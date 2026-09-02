"""Idempotent boto3 provisioning for earshot's DynamoDB tables and SQS queues.

CDK is unusable on this account: `cdk bootstrap` needs `s3:CreateBucket`, `iam:CreateRole` and
`ecr:CreateRepository`, all three denied (D-024, docs/ops/decisions.md). This script IS the
infrastructure-as-code for the resources we CAN create -- three DynamoDB tables and three SQS
queues, matching `src/earshot/aws/stores.py` and `docs/architecture/infrastructure.md` S1.6 /
Appendix A rows 9-11 and 15/17. Resources we cannot create (ECR, new S3 buckets, IAM roles, a
CodeBuild project) are printed as PARKED rows -- named, with what is needed and from whom --
rather than attempted and failed.

Re-running this script is always safe: every action checks live AWS state first (`describe_table`
/ `get_queue_url`) and only acts on the gap between that and the desired state, so a second run
against an already-provisioned stage reports SKIP everywhere and changes nothing.

    uv run --with boto3 python tools/provision.py --stage dev              # dry-run (default)
    uv run --with boto3 python tools/provision.py --stage dev --no-dry-run # actually create
    uv run --with boto3 python tools/provision.py --stage dev --teardown --no-dry-run

Dry-run is the DEFAULT and must be turned off explicitly with `--no-dry-run`, because this
script's other mode writes to a real, billed AWS account. `--teardown` never deletes the ledger
table, with or without `--no-dry-run` -- there is no code path in this file that can call
`delete_table` on it. See `LedgerStore`'s docstring for the same rule on the read/write side.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import deploy
from earshot.aws.stores import REGION, STAGES, TABLE_SPECS, table_name

# D-024's unlock: the one execution role every Lambda passes, since none of the three per-
# function roles Appendix A rows 6-8 wanted can be created. Named here only so the PARKED
# explanation below is concrete rather than vague about what "the existing role" refers to.
LEDGER_LAMBDA_ROLE_ARN = "arn:aws:iam::859430413223:role/zenon-poc-lambda-execution"

# AWS refuses an event source mapping whose queue visibility timeout is below the consuming
# function's timeout, and recommends 6x it so a partially-failed batch has room to retry inside
# one visibility window.
#
# The multiple is applied to `deploy.FUNCTIONS` rather than written here as a second number,
# because the two numbers living in two files with nothing connecting them is the actual bug:
# on 2026-09-02 both mappings failed to create, because this script left both queues at the SQS
# default of 30s while the functions it never looked at were set to 60s and 300s. Raising a
# Lambda timeout in `deploy.py` now raises the queue's visibility timeout with it.
#
# Accepted consequence: `maxReceiveCount` is 3 on the investigations queue, so a longer
# visibility timeout also means a poison message takes proportionally longer to reach the DLQ.
VISIBILITY_MULTIPLE = 6


def visibility_timeouts(stage: str) -> dict[str, int]:
    """Queue name -> the `VisibilityTimeout` its consumer's own timeout demands.

    Keyed by queue rather than by function because that is how SQS is addressed, and because a
    queue with no consumer in `deploy.FUNCTIONS` (the DLQ) correctly gets no entry.
    """
    return {
        f"earshot-{stage}-{spec['queue']}": int(spec["timeout"]) * VISIBILITY_MULTIPLE
        for spec in deploy.FUNCTIONS.values()
        if spec.get("queue")
    }

Row = tuple[str, str, str]  # resource, action, result
_rows: list[Row] = []


def _record(resource: str, action: str, result: str) -> None:
    _rows.append((resource, action, result))
    print(f"  {action:8} {resource:44} {result}")


def _error_code(exc: Exception) -> str:
    """Duck-typed against botocore's error shape -- see `stores.py`'s identical helper. Kept as
    its own copy here rather than imported: this script is standalone tooling, not part of the
    guarded package surface, and has no other reason to depend on `earshot.aws.stores`'s
    private helpers."""
    return getattr(exc, "response", {}).get("Error", {}).get("Code", "") or type(exc).__name__


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


# ---- DynamoDB ------------------------------------------------------------------------------


def _table_exists(ddb: Any, name: str) -> bool:
    try:
        ddb.describe_table(TableName=name)
        return True
    except Exception as exc:  # noqa: BLE001 - re-raised unless it is "does not exist"
        if _error_code(exc) == "ResourceNotFoundException":
            return False
        raise


# Six attempts with 1.5x backoff from 5s is a little over two minutes -- longer than any
# observed backups-subsystem lag, and short enough that a genuinely broken run still ends.
_PITR_ATTEMPTS = 6


def _ensure_pitr(ddb: Any, name: str, dry_run: bool) -> None:
    """Checked and converged on EVERY run, whether the table pre-existed or was just created --
    idempotent means "ensure this state", not just "ensure existence"."""
    try:
        backups = ddb.describe_continuous_backups(TableName=name)["ContinuousBackupsDescription"]
        status = backups["PointInTimeRecoveryDescription"]["PointInTimeRecoveryStatus"]
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"dynamodb:{name}:pitr", "CHECK", f"FAILED {_error_detail(exc)}")
        return
    if status == "ENABLED":
        _record(f"dynamodb:{name}:pitr", "SKIP", "already on")
        return
    if dry_run:
        _record(f"dynamodb:{name}:pitr", "ENABLE", "DRY-RUN -- would enable point-in-time recovery")
        return
    # A freshly created table is ACTIVE (the `table_exists` waiter checks exactly that) several
    # seconds before its continuous-backups subsystem is, and DynamoDB reports the gap as
    # `ContinuousBackupsUnavailableException`. Found the hard way on 2026-08-28: the first real
    # run created all three tables and left all three with PITR DISABLED, and the failure reads
    # like a permission problem. Retry that one code, and only that one -- an AccessDenied here
    # must still fail on the first attempt rather than after a minute of pointless waiting.
    delay = 5.0
    for attempt in range(1, _PITR_ATTEMPTS + 1):
        try:
            ddb.update_continuous_backups(
                TableName=name,
                PointInTimeRecoverySpecification={"PointInTimeRecoveryEnabled": True},
            )
            suffix = "" if attempt == 1 else f" (after {attempt} attempts)"
            _record(f"dynamodb:{name}:pitr", "ENABLE", f"enabled{suffix}")
            return
        except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
            code = _error_code(exc)
            if code != "ContinuousBackupsUnavailableException" or attempt == _PITR_ATTEMPTS:
                _record(f"dynamodb:{name}:pitr", "ENABLE", f"FAILED {code}")
                return
            time.sleep(delay)
            delay *= 1.5


def _provision_tables(ddb: Any, stage: str, dry_run: bool) -> None:
    print("\nDynamoDB tables (on-demand, PITR on, NO TTL -- ledger/cases/reviews alike)")
    for kind, spec in TABLE_SPECS.items():
        name = table_name(stage, kind)
        if _table_exists(ddb, name):
            _record(f"dynamodb:{name}", "SKIP", "already exists")
        elif dry_run:
            _record(f"dynamodb:{name}", "CREATE", "DRY-RUN -- would create")
            # Nothing exists to describe, so a PITR check here reports FAILED
            # TableNotFoundException and reads as a permission problem. State the intent instead.
            _record(f"dynamodb:{name}:pitr", "ENABLE", "DRY-RUN -- would enable after create")
            continue
        else:
            try:
                kwargs: dict[str, Any] = {
                    "TableName": name,
                    "BillingMode": "PAY_PER_REQUEST",
                    "KeySchema": spec["key_schema"],
                    "AttributeDefinitions": spec["attribute_definitions"],
                }
                if spec["gsi"]:
                    kwargs["GlobalSecondaryIndexes"] = spec["gsi"]
                ddb.create_table(**kwargs)
                ddb.get_waiter("table_exists").wait(
                    TableName=name, WaiterConfig={"Delay": 2, "MaxAttempts": 20}
                )
                _record(f"dynamodb:{name}", "CREATE", "created")
            except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
                _record(f"dynamodb:{name}", "CREATE", f"FAILED {_error_detail(exc)}")
                continue  # PITR would fail too with nothing to point at; move to the next table
        _ensure_pitr(ddb, name, dry_run)


def _teardown_table(ddb: Any, name: str, dry_run: bool) -> None:
    if not _table_exists(ddb, name):
        _record(f"dynamodb:{name}", "SKIP", "already absent")
        return
    if dry_run:
        _record(f"dynamodb:{name}", "DELETE", "DRY-RUN -- would delete")
        return
    try:
        ddb.delete_table(TableName=name)
        _record(f"dynamodb:{name}", "DELETE", "deleted")
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"dynamodb:{name}", "DELETE", f"FAILED {_error_detail(exc)}")


# ---- SQS -----------------------------------------------------------------------------------


# SQS reports a missing queue with the wire code `AWS.SimpleQueueService.NonExistentQueue`, while
# botocore names the exception class `QueueDoesNotExist`. Matching only the class name let a
# perfectly normal "not created yet" escape as a crash on the first real dry-run.
_QUEUE_ABSENT = frozenset({"AWS.SimpleQueueService.NonExistentQueue", "QueueDoesNotExist"})


def _queue_url(sqs: Any, name: str) -> str | None:
    try:
        return sqs.get_queue_url(QueueName=name)["QueueUrl"]
    except Exception as exc:  # noqa: BLE001 - re-raised unless it is "does not exist"
        if _error_code(exc) in _QUEUE_ABSENT or type(exc).__name__ in _QUEUE_ABSENT:
            return None
        raise


# `FifoQueue` is fixed at creation -- SQS rejects it in `set_queue_attributes`, and a queue cannot
# be converted between standard and FIFO. Excluded from reconciliation so an existing FIFO queue
# does not report a diff on every run that no run can ever close.
_IMMUTABLE_ATTRIBUTES = frozenset({"FifoQueue"})

# AWS re-serialises these, so key order and whitespace differ from what we sent. Compared as
# parsed JSON: a string compare reports drift on every run and rewrites an identical policy
# forever, which reads in the output exactly like a real change.
_JSON_ATTRIBUTES = frozenset({"Policy", "RedrivePolicy", "RedriveAllowPolicy"})


def _attribute_matches(name: str, live: str | None, wanted: Any) -> bool:
    if live is None:
        return False
    if name in _JSON_ATTRIBUTES:
        try:
            return json.loads(live) == json.loads(str(wanted))
        except ValueError:
            return False
    # Every SQS attribute comes back as a string. `"30" != 30`, so an int on our side would
    # report a diff forever and set the same value on every run.
    return live == str(wanted)


def _reconcile_queue(
    sqs: Any,
    name: str,
    url: str,
    attributes: dict[str, str],
    dry_run: bool,
    *,
    unevaluated: str = "",
) -> None:
    """Correct an existing queue's mutable attributes.

    Create-if-missing is not enough. On 2026-09-02 both queues on this account already existed at
    the SQS default visibility timeout, so changing the desired value alone would have been
    silently inert -- the tool reporting SKIP while the bug it was meant to fix survived. That is
    a worse failure than an error, because it looks like success.
    """
    wanted = {k: v for k, v in attributes.items() if k not in _IMMUTABLE_ATTRIBUTES}
    if not wanted:
        _record(f"sqs:{name}", "SKIP", "already exists")
        return
    try:
        live = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=sorted(wanted))["Attributes"]
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"sqs:{name}", "CHECK", f"FAILED {_error_detail(exc)}")
        return
    drift = {k: v for k, v in wanted.items() if not _attribute_matches(k, live.get(k), v)}
    if not drift:
        # `unevaluated` names an attribute this run could not compare -- in a dry-run the redrive
        # policy needs a DLQ ARN that does not exist yet. Saying "attributes match" flat would
        # contradict the WIRE row printed just above it, which is the dry-run under-reporting its
        # own plan (the same defect `deploy.py` had, fixed 2026-09-02).
        note = f"already exists, attributes match ({unevaluated} not evaluated)" if unevaluated             else "already exists, attributes match"
        _record(f"sqs:{name}", "SKIP", note)
        return
    changed = ", ".join(f"{k} {live.get(k, '(unset)')} -> {v}" for k, v in sorted(drift.items()))
    if dry_run:
        _record(f"sqs:{name}", "UPDATE", f"DRY-RUN -- would set {changed}")
        return
    try:
        sqs.set_queue_attributes(QueueUrl=url, Attributes={k: str(v) for k, v in drift.items()})
        _record(f"sqs:{name}", "UPDATE", changed)
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"sqs:{name}", "UPDATE", f"FAILED {_error_detail(exc)}")


def _ensure_queue(
    sqs: Any, name: str, dry_run: bool, *, attributes: dict[str, str], unevaluated: str = ""
) -> str | None:
    """Create-if-missing, and repair-if-drifted. Returns the queue URL if the queue exists or was
    just created; `None` only in dry-run, when nothing was actually created and there is no URL to
    hand back."""
    url = _queue_url(sqs, name)
    if url is not None:
        _reconcile_queue(sqs, name, url, attributes, dry_run, unevaluated=unevaluated)
        return url
    if dry_run:
        _record(f"sqs:{name}", "CREATE", "DRY-RUN -- would create")
        return None
    try:
        url = sqs.create_queue(QueueName=name, Attributes=attributes)["QueueUrl"]
        _record(f"sqs:{name}", "CREATE", "created")
        return url
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"sqs:{name}", "CREATE", f"FAILED {_error_detail(exc)}")
        return None


# Three delivery attempts before a message is set aside, on both queues.
#
# On the FIFO transcripts queue this bound is doing more work than it looks. A FIFO message group
# is ordered, so a poison transcript blocks its OWN customer's entire stream until it is either
# accepted or moved aside -- and until 2026-09-03 that queue had no DLQ at all, so the answer was
# "neither": it retried for the full 4-day retention period, stalling that customer and
# re-invoking ingest every visibility window. Under `EARSHOT_EXTRACTOR=bedrock` each of those
# retries is a paid model call, and `llm/budget.py` cannot stop it, because every retry is a fresh
# invocation with a fresh budget.
#
# 3 attempts x the 360s visibility timeout is about 18 minutes of head-of-line blocking for one
# customer, then the group moves on. That is the trade: enough attempts to ride out a transient
# DynamoDB or S3 blip, few enough that a malformed transcript cannot hold a stream hostage.
MAX_RECEIVE_COUNT = 3


def _dlq_arn(sqs: Any, url: str) -> str:
    return sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueArn"])["Attributes"][
        "QueueArn"
    ]


def _redrive(dlq_arn: str) -> str:
    return json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": MAX_RECEIVE_COUNT})


def _provision_queues(sqs: Any, stage: str, dry_run: bool) -> None:
    print("\nSQS -- transcript ingest bus (FIFO) + investigation queue, each with its own DLQ")
    visibility = visibility_timeouts(stage)

    # A FIFO queue's dead-letter target must itself be FIFO, so this is its own queue rather than
    # one bucket shared with the investigations DLQ.
    transcripts_dlq = f"earshot-{stage}-transcripts-dlq.fifo"
    transcripts_dlq_url = _ensure_queue(
        sqs, transcripts_dlq, dry_run,
        attributes={"FifoQueue": "true", "ContentBasedDeduplication": "false"},
    )

    transcripts = f"earshot-{stage}-transcripts.fifo"
    transcripts_attrs = {
        "FifoQueue": "true",
        "ContentBasedDeduplication": "false",
        "VisibilityTimeout": str(visibility[transcripts]),
    }
    if transcripts_dlq_url is not None:
        transcripts_attrs["RedrivePolicy"] = _redrive(_dlq_arn(sqs, transcripts_dlq_url))
    elif dry_run:
        _record(f"sqs:{transcripts}", "WIRE",
                "DRY-RUN -- would wire a redrive policy to the FIFO DLQ above")
    else:
        _record(f"sqs:{transcripts}", "WIRE",
                "FAILED -- FIFO DLQ was not created, cannot wire a redrive policy")
    _ensure_queue(
        sqs, transcripts, dry_run, attributes=transcripts_attrs,
        unevaluated="" if "RedrivePolicy" in transcripts_attrs else "RedrivePolicy",
    )
    print("    (MessageGroupId=customer_id is set per-message by producers, not a queue "
          "attribute -- nothing to provision for it; content-based dedup is off, so producers "
          "must set MessageDeduplicationId themselves)")

    dlq_name = f"earshot-{stage}-investigations-dlq"
    dlq_url = _ensure_queue(sqs, dlq_name, dry_run, attributes={})

    inv_name = f"earshot-{stage}-investigations"
    if dlq_url is None:
        if dry_run:
            _record(f"sqs:{inv_name}", "CREATE",
                     "DRY-RUN -- would create with a redrive policy to the DLQ above")
        else:
            _record(f"sqs:{inv_name}", "CREATE",
                     "FAILED -- DLQ was not created, cannot wire a redrive policy")
        return
    _ensure_queue(
        sqs, inv_name, dry_run,
        attributes={
            "RedrivePolicy": _redrive(_dlq_arn(sqs, dlq_url)),
            "VisibilityTimeout": str(visibility[inv_name]),
        },
    )


def _teardown_queue(sqs: Any, name: str, dry_run: bool) -> None:
    url = _queue_url(sqs, name)
    if url is None:
        _record(f"sqs:{name}", "SKIP", "already absent")
        return
    if dry_run:
        _record(f"sqs:{name}", "DELETE", "DRY-RUN -- would delete")
        return
    try:
        sqs.delete_queue(QueueUrl=url)
        _record(f"sqs:{name}", "DELETE", "deleted")
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"sqs:{name}", "DELETE", f"FAILED {_error_detail(exc)}")


# ---- teardown, and the one resource it refuses ----------------------------------------------


def _teardown(ddb: Any, sqs: Any, stage: str, dry_run: bool) -> None:
    # The ledger is NEVER deleted by this tool -- teardown or not, dry-run or not. There is no
    # call to delete_table on it anywhere below; this line only makes that refusal visible.
    ledger_name = table_name(stage, "ledger")
    _record(f"dynamodb:{ledger_name}", "REFUSE", "never deleted by this tool (A6, never-discard)")

    print("\nDynamoDB -- cases + reviews (ledger refused above)")
    for kind in ("cases", "reviews"):
        _teardown_table(ddb, table_name(stage, kind), dry_run)

    print("\nSQS")
    # Source queues before their dead-letter targets, so a DLQ is never deleted out from under a
    # redrive policy that still names it.
    for name in (
        f"earshot-{stage}-transcripts.fifo",
        f"earshot-{stage}-transcripts-dlq.fifo",
        f"earshot-{stage}-investigations",
        f"earshot-{stage}-investigations-dlq",
    ):
        _teardown_queue(sqs, name, dry_run)


# ---- the resources we know we cannot create -------------------------------------------------


def _print_parked() -> None:
    """Named per the CONTEXT this script was built under: ECR, a new S3 bucket, IAM roles and a
    CodeBuild project are all denied on this account (D-024, docs/ops/decisions.md). Printed as
    a fixed, informational list rather than attempted -- we already know, from `aws_probe.py`,
    that the API calls fail, so there is nothing to gain by re-discovering that here on every
    run."""
    print("\nPARKED -- known permission gaps, not attempted (D-024, docs/ops/decisions.md)")
    parked = [
        (
            "ecr:earshot",
            "needs ecr:CreateRepository, from an account admin -- worked around: Lambda "
            "deploy artifacts are ZIPs on s3://agentic-trio, not container images, so this "
            "repo is not on the critical path today",
        ),
        (
            "s3:earshot-evidence / earshot-artifacts",
            "needs s3:CreateBucket, from an account admin -- worked around: both live as "
            "prefixes inside the one bucket we have, s3://agentic-trio, so Object Lock "
            "write-once on the evidence prefix is unavailable until this is granted",
        ),
        (
            "iam:ingest / investigate / api execution roles",
            f"needs iam:CreateRole, from an account admin -- worked around: all three "
            f"Lambdas pass the existing {LEDGER_LAMBDA_ROLE_ARN} (D-024); per-function least "
            f"privilege is target-state, not built",
        ),
        (
            "codebuild:earshot-build",
            "needs an IAM service role for CodeBuild to assume -- the only role we can pass "
            "is scoped to Lambda's trust policy, not CodeBuild's, so this is blocked by the "
            "same gap as the row above, not a separate one. No workaround yet (W9)",
        ),
    ]
    for resource, need in parked:
        _record(resource, "PARK", need)


# ---- CLI -------------------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="provision.py",
        description="Idempotent boto3 provisioning for earshot's DynamoDB tables and SQS "
        "queues (docs/architecture/infrastructure.md S1.6, Appendix A). CDK is unusable on "
        "this account (D-024) -- this script IS the infrastructure-as-code.",
    )
    parser.add_argument("--stage", choices=STAGES, required=True, help="table/queue namespace")
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="print the plan without creating or deleting anything (default: on, i.e. safe). "
        "Pass --no-dry-run to actually touch AWS.",
    )
    parser.add_argument(
        "--teardown",
        action="store_true",
        help="delete the cases/reviews tables and all three queues instead of creating them. "
        "NEVER deletes the ledger table, with or without this flag.",
    )
    args = parser.parse_args()  # --help exits here; nothing below runs, so no boto3 is needed

    try:
        import boto3
    except ImportError:
        print(
            "boto3 missing. Run: uv run --with boto3 python tools/provision.py ...",
            file=sys.stderr,
        )
        return 2

    ddb = boto3.client("dynamodb", region_name=REGION)
    sqs = boto3.client("sqs", region_name=REGION)

    mode = "TEARDOWN" if args.teardown else "PROVISION"
    print(f"\n{mode}  stage={args.stage}  region={REGION}  dry_run={args.dry_run}")
    print(f"  {'ACTION':8} {'RESOURCE':44} RESULT")

    if args.teardown:
        _teardown(ddb, sqs, args.stage, args.dry_run)
    else:
        _provision_tables(ddb, args.stage, args.dry_run)
        _provision_queues(sqs, args.stage, args.dry_run)
    _print_parked()

    failed = [r for r in _rows if r[2].startswith("FAILED")]
    print(f"\n{'-' * 78}")
    print(f"{len(_rows)} rows: {len(_rows) - len(failed)} ok, {len(failed)} failed")
    if args.dry_run:
        print("DRY-RUN -- nothing was created, deleted or changed. Pass --no-dry-run to act.")
    if failed:
        print("\nFAILED:")
        for resource, action, result in failed:
            print(f"  {action:8} {resource:44} {result}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
