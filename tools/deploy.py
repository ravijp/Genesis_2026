"""Build one zip and deploy the three Lambda handlers from it. Idempotent, dry-run by default.

CDK cannot be used on this account (D-024: `cdk bootstrap` needs `s3:CreateBucket`,
`iam:CreateRole` and `ecr:CreateRepository`, all denied), so this is the deploy path. Same shape as
`tools/provision.py` -- prints one row per action, converges on every run, and says exactly what it
would do before it does anything.

    uv run --extra aws python tools/deploy.py --stage dev              # dry run
    uv run --extra aws python tools/deploy.py --stage dev --no-dry-run

**One zip, three functions.** The handlers share a package, a prompt tree and a dependency set, so
building three artifacts would be three chances for them to differ. The zip's SHA-256 goes in its S3
key and in every function's description, which makes "are all three running the same code?" a thing
you can read off the console rather than infer.

**No new IAM role.** All three pass the existing `zenon-poc-lambda-execution` (D-024). Per-function
least privilege is target-state and is honestly not built.

**boto3 is not vendored.** The Lambda Python runtime ships it. `pydantic` and `httpx` are not, so
they are installed into the build directory -- **cross-compiled for manylinux cp313**, because
`pydantic-core` is a compiled extension and a plain install on a Windows laptop vendors a `.pyd`
that dies at import inside a Linux Lambda. `earshot[aws]` stays optional for exactly this reason:
the laptop suite must run boto3-free.

**Deployed keyless first.** Both `EARSHOT_EXTRACTOR` and `EARSHOT_PROVIDER` default to `offline`
here, so the first deploy proves the plumbing without spending anything. Flipping either to
`bedrock` is a configuration update, not a redeploy -- `--extractor` / `--provider`.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from earshot.aws.stores import REGION, STAGES

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "lambda"
BUCKET = "agentic-trio"
KEY_PREFIX = "artifacts/lambda"

# The one role this account lets us pass. It trusts lambda.amazonaws.com; it does NOT trust
# codebuild.amazonaws.com, which is why W9 is still blocked on IT (D-024).
ROLE_ARN = "arn:aws:iam::859430413223:role/zenon-poc-lambda-execution"

RUNTIME = "python3.13"

# Not vendored: boto3/botocore (in the runtime). Vendored: everything `import earshot` reaches.
VENDORED = ("pydantic>=2.11", "httpx>=0.28")

FUNCTIONS: dict[str, dict[str, Any]] = {
    "ingest": {
        "handler": "earshot.aws.ingest.handler",
        # One conversation, one extraction. 60s is generous even with a model reader.
        "timeout": 60,
        "memory": 1024,
        "queue": "transcripts.fifo",
        "batch_size": 10,
    },
    "investigate": {
        "handler": "earshot.aws.investigate.handler",
        # A multi-turn tool loop: up to 6 model calls. Well inside Lambda's 15-minute ceiling,
        # which is the A9 argument for Lambda over Fargate in the first place.
        "timeout": 300,
        "memory": 1024,
        "queue": "investigations",
        # ONE. An investigation is the expensive unit here, and a batch of ten that times out on
        # the tenth redelivers the nine already paid for.
        "batch_size": 1,
    },
    "api": {
        "handler": "earshot.aws.api.handler",
        "timeout": 30,
        "memory": 512,
        "queue": None,
        "batch_size": None,
    },
}

_ROWS: list[tuple[str, str, str]] = []


def _record(resource: str, action: str, result: str) -> None:
    _ROWS.append((resource, action, result))
    print(f"  {action:<8} {resource:<44} {result}")


def _error_code(exc: Exception) -> str:
    """Duck-typed on botocore's error shape so this file never imports botocore."""
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        code = response.get("Error", {}).get("Code")
        if code:
            return str(code)
    return type(exc).__name__


def _error_detail(exc: Exception) -> str:
    """The AWS error code *and* its message, for a row a human can act on.

    `_error_code` alone is why 2026-09-02's event source mapping failure read as a bare
    `InvalidParameterValueException`. The message said exactly what was wrong -- "Queue visibility
    timeout: 30 seconds is less than Function timeout: 60 seconds" -- and discarding it cost a
    diagnostic round-trip against the live account. Control-flow callers still compare
    `_error_code`; only the reported rows use this.
    """
    code = _error_code(exc)
    response = getattr(exc, "response", None)
    message = ""
    if isinstance(response, dict):
        message = str(response.get("Error", {}).get("Message", "") or "")
    message = " ".join((message or str(exc)).split())
    if not message or message == code:
        return code
    if len(message) > 160:
        message = message[:157] + "..."
    return f"{code}: {message}"


def function_name(stage: str, kind: str) -> str:
    return f"earshot-{stage}-{kind}"


# ---- build ---------------------------------------------------------------------------------


def build_zip(dry_run: bool) -> tuple[Path, str]:
    """Install the vendored deps, copy the package and the prompts, zip it. Returns (path, sha).

    Deterministic on purpose: every entry is written with a fixed timestamp, so the same source
    tree produces the same SHA-256 and a redeploy of unchanged code is visibly a no-op rather than
    a new artifact with a new name.
    """
    zip_path = ROOT / "build" / "earshot-lambda.zip"
    if dry_run:
        _record("build:earshot-lambda.zip", "BUILD", "DRY-RUN -- would build from src/ + prompts/")
        return zip_path, "dry-run"

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    # CROSS-PLATFORM, and this is not optional. `pydantic-core` is a compiled extension, so a
    # plain install on this Windows laptop vendors a `.pyd` into a Linux Lambda and the function
    # dies at import with `ModuleNotFoundError: pydantic_core._pydantic_core`. `--python-platform`
    # plus `--only-binary` forces manylinux cp313 wheels and fails loudly rather than quietly
    # building the wrong thing from source.
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv not on PATH; it is what builds the deployment artifact")
    result = subprocess.run(
        [
            uv, "pip", "install",
            "--target", str(BUILD),
            "--python-platform", "x86_64-manylinux2014",
            "--python-version", "3.13",
            "--only-binary", ":all:",
            *VENDORED,
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError("dependency install failed: " + result.stderr.strip())
    shutil.copytree(ROOT / "src" / "earshot", BUILD / "earshot")
    # At the zip ROOT, not inside the package: Lambda's cwd is /var/task, so `prompt_files
    # .prompts_root()`'s `Path("prompts")` branch resolves. `EARSHOT_PROMPTS` is also set on every
    # function, so this does not depend on cwd staying what it is today.
    shutil.copytree(ROOT / "prompts", BUILD / "prompts")

    for junk in list(BUILD.rglob("__pycache__")) + list(BUILD.rglob("*.dist-info")):
        shutil.rmtree(junk, ignore_errors=True)

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(BUILD.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(str(path.relative_to(BUILD)).replace("\\", "/"))
                info.date_time = (2026, 1, 1, 0, 0, 0)
                info.external_attr = 0o644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())

    sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()[:12]
    size_mb = zip_path.stat().st_size / 1_000_000
    _record("build:earshot-lambda.zip", "BUILD", f"{size_mb:.1f} MB, sha {sha}")
    return zip_path, sha


def upload(s3: Any, zip_path: Path, sha: str, dry_run: bool) -> str:
    key = f"{KEY_PREFIX}/earshot-{sha}.zip"
    if dry_run:
        _record(f"s3:{key}", "UPLOAD", f"DRY-RUN -- would upload to s3://{BUCKET}")
        return key
    try:
        s3.put_object(Bucket=BUCKET, Key=key, Body=zip_path.read_bytes())
        _record(f"s3:{key}", "UPLOAD", f"uploaded to s3://{BUCKET}")
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"s3:{key}", "UPLOAD", f"FAILED {_error_detail(exc)}")
    return key


# ---- functions -----------------------------------------------------------------------------


def _env(stage: str, kind: str, sqs: Any, extractor: str, provider: str, threshold: float) -> dict:
    env = {
        "EARSHOT_STAGE": stage,
        # Explicit rather than relying on Lambda's cwd being /var/task. A prompt loaded from the
        # wrong place would change `prompt_sha`, and the sha is what ties a decision to the text
        # that produced it.
        "EARSHOT_PROMPTS": "/var/task/prompts",
        "EARSHOT_THRESHOLD": str(threshold),
    }
    if kind == "ingest":
        env["EARSHOT_EXTRACTOR"] = extractor
        url = _queue_url(sqs, f"earshot-{stage}-investigations")
        if url:
            env["EARSHOT_INVESTIGATIONS_QUEUE_URL"] = url
    if kind == "investigate":
        env["EARSHOT_PROVIDER"] = provider
    return env


def _queue_url(sqs: Any, name: str) -> str | None:
    try:
        return sqs.get_queue_url(QueueName=name)["QueueUrl"]
    except Exception:  # noqa: BLE001 - absent is an answer, not an error
        return None


def _queue_arn(sqs: Any, name: str) -> str | None:
    url = _queue_url(sqs, name)
    if url is None:
        return None
    try:
        return sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueArn"])["Attributes"][
            "QueueArn"
        ]
    except Exception:  # noqa: BLE001
        return None


def deploy_function(
    lam: Any,
    sqs: Any,
    stage: str,
    kind: str,
    spec: dict[str, Any],
    key: str,
    sha: str,
    *,
    extractor: str,
    provider: str,
    threshold: float,
    dry_run: bool,
) -> None:
    name = function_name(stage, kind)
    env = _env(stage, kind, sqs, extractor, provider, threshold)
    exists = True
    try:
        lam.get_function(FunctionName=name)
    except Exception as exc:  # noqa: BLE001
        if _error_code(exc) != "ResourceNotFoundException":
            _record(f"lambda:{name}", "CHECK", f"FAILED {_error_detail(exc)}")
            return
        exists = False

    if dry_run:
        _record(f"lambda:{name}", "UPDATE" if exists else "CREATE", "DRY-RUN")
        # Fall through to the mapping preview rather than returning. Queue wiring is the one step
        # here that is not idempotent-by-inspection, so a dry-run that hides it previews the least
        # of what a real run does.
        if spec["queue"]:
            _ensure_mapping(lam, sqs, stage, name, spec, dry_run, exists=exists)
        return

    common = {
        "Role": ROLE_ARN,
        "Handler": spec["handler"],
        "Runtime": RUNTIME,
        "Timeout": spec["timeout"],
        "MemorySize": spec["memory"],
        "Environment": {"Variables": env},
        # The zip's own hash, so "are all three running the same code?" is readable, not inferred.
        "Description": f"Ear on Every Call {kind} ({stage}) - zip sha {sha}",
    }
    try:
        if exists:
            lam.update_function_code(FunctionName=name, S3Bucket=BUCKET, S3Key=key, Publish=True)
            lam.get_waiter("function_updated_v2").wait(FunctionName=name)
            lam.update_function_configuration(FunctionName=name, **common)
            lam.get_waiter("function_updated_v2").wait(FunctionName=name)
            _record(f"lambda:{name}", "UPDATE", "code + config updated")
        else:
            lam.create_function(
                FunctionName=name, Code={"S3Bucket": BUCKET, "S3Key": key}, Publish=True, **common
            )
            lam.get_waiter("function_active_v2").wait(FunctionName=name)
            _record(f"lambda:{name}", "CREATE", "created")
    except Exception as exc:  # noqa: BLE001
        _record(f"lambda:{name}", "UPDATE" if exists else "CREATE", f"FAILED {_error_detail(exc)}")
        return

    if spec["queue"]:
        _ensure_mapping(lam, sqs, stage, name, spec, dry_run, exists=True)


def _ensure_mapping(
    lam: Any,
    sqs: Any,
    stage: str,
    name: str,
    spec: dict[str, Any],
    dry_run: bool,
    *,
    exists: bool,
) -> None:
    """Wire the queue to the function. Idempotent: an existing mapping is left alone rather than
    recreated, because deleting one drops in-flight messages.

    `exists` says whether the function is already deployed. Only a dry-run can be called with
    `exists=False`, and it must not ask Lambda to list mappings for a function that is not there
    yet -- that raises, and a preview reporting FAILED for a resource it is about to create reads
    as a blocker when it is not one.
    """
    queue_name = f"earshot-{stage}-{spec['queue']}"
    arn = _queue_arn(sqs, queue_name)
    if arn is None:
        _record(f"mapping:{queue_name}", "WIRE", "FAILED queue not found -- run provision.py first")
        return
    if not exists:
        _record(f"mapping:{queue_name}", "WIRE", f"DRY-RUN -- would wire to {name} after create")
        return
    try:
        existing = lam.list_event_source_mappings(FunctionName=name, EventSourceArn=arn)
        if existing.get("EventSourceMappings"):
            _record(f"mapping:{queue_name}", "SKIP", f"already wired to {name}")
            return
        if dry_run:
            _record(f"mapping:{queue_name}", "WIRE", f"DRY-RUN -- would wire to {name}")
            return
        lam.create_event_source_mapping(
            FunctionName=name,
            EventSourceArn=arn,
            BatchSize=spec["batch_size"],
            # Without this, `batchItemFailures` in the handler's return value is IGNORED and a
            # single poison record redelivers the whole batch -- the exact behaviour both handlers
            # are written to avoid.
            FunctionResponseTypes=["ReportBatchItemFailures"],
        )
        _record(f"mapping:{queue_name}", "WIRE", f"wired to {name}, batch {spec['batch_size']}")
    except Exception as exc:  # noqa: BLE001
        _record(f"mapping:{queue_name}", "WIRE", f"FAILED {_error_detail(exc)}")


def ensure_function_url(lam: Any, stage: str, dry_run: bool) -> None:
    """A Function URL for the reviewer API, so the SPA has something to call without API Gateway.

    `AuthType=AWS_IAM`, not `NONE`: an unauthenticated URL puts a bank's case queue on the public
    internet, and "it is only a POC" is how that ships. The SPA signs with SigV4, or a reviewer
    reaches it through the console.
    """
    name = function_name(stage, "api")
    try:
        lam.get_function_url_config(FunctionName=name)
        _record(f"url:{name}", "SKIP", "already configured")
        return
    except Exception as exc:  # noqa: BLE001
        if _error_code(exc) != "ResourceNotFoundException":
            _record(f"url:{name}", "CHECK", f"FAILED {_error_detail(exc)}")
            return
    if dry_run:
        _record(f"url:{name}", "CREATE", "DRY-RUN -- would create (AuthType=AWS_IAM)")
        return
    try:
        url = lam.create_function_url_config(FunctionName=name, AuthType="AWS_IAM")["FunctionUrl"]
        _record(f"url:{name}", "CREATE", url)
    except Exception as exc:  # noqa: BLE001
        _record(f"url:{name}", "CREATE", f"FAILED {_error_detail(exc)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one zip and deploy the three earshot Lambda handlers from it."
    )
    parser.add_argument("--stage", choices=STAGES, required=True)
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="default: on. Pass --no-dry-run to actually create or update anything.",
    )
    parser.add_argument(
        "--extractor",
        choices=("offline", "bedrock"),
        default="offline",
        help="the reader the ingest handler uses. Default offline: costs nothing.",
    )
    parser.add_argument(
        "--provider",
        choices=("offline", "bedrock"),
        default="offline",
        help="the investigator's model. Default offline: a rule engine, and its verdicts are a "
        "floor, not a result.",
    )
    parser.add_argument("--threshold", type=float, default=0.60, help="the online cut (D-027)")
    args = parser.parse_args()

    import boto3  # noqa: PLC0415 -- the whole script is the AWS path; keep the import at the edge

    lam = boto3.client("lambda", region_name=REGION)
    s3 = boto3.client("s3", region_name=REGION)
    sqs = boto3.client("sqs", region_name=REGION)

    print(f"DEPLOY  stage={args.stage}  region={REGION}  dry_run={args.dry_run}")
    print(f"        extractor={args.extractor}  provider={args.provider}  "
          f"threshold={args.threshold}")
    print(f"  {'ACTION':<8} {'RESOURCE':<44} RESULT\n")

    zip_path, sha = build_zip(args.dry_run)
    key = upload(s3, zip_path, sha, args.dry_run)

    print("\nLambda functions (one zip, three handlers, the existing role passed -- D-024)")
    for kind, spec in FUNCTIONS.items():
        deploy_function(
            lam, sqs, args.stage, kind, spec, key, sha,
            extractor=args.extractor, provider=args.provider, threshold=args.threshold,
            dry_run=args.dry_run,
        )

    print("\nReviewer API endpoint")
    ensure_function_url(lam, args.stage, args.dry_run)

    failed = [row for row in _ROWS if "FAILED" in row[2]]
    print("\n" + "-" * 78)
    print(f"{len(_ROWS)} rows: {len(_ROWS) - len(failed)} ok, {len(failed)} failed")
    if failed:
        print("\nFAILED:")
        for resource, action, result in failed:
            print(f"  {action:<8} {resource:<44} {result}")
    if args.dry_run:
        print("\nDRY-RUN -- nothing was built, uploaded or changed. Pass --no-dry-run to act.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
