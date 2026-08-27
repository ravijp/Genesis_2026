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
from typing import Any

from earshot.aws.stores import REGION, STAGES, TABLE_SPECS, table_name

# D-024's unlock: the one execution role every Lambda passes, since none of the three per-
# function roles Appendix A rows 6-8 wanted can be created. Named here only so the PARKED
# explanation below is concrete rather than vague about what "the existing role" refers to.
LEDGER_LAMBDA_ROLE_ARN = "arn:aws:iam::859430413223:role/zenon-poc-lambda-execution"

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


# ---- DynamoDB ------------------------------------------------------------------------------


def _table_exists(ddb: Any, name: str) -> bool:
    try:
        ddb.describe_table(TableName=name)
        return True
    except Exception as exc:  # noqa: BLE001 - re-raised unless it is "does not exist"
        if _error_code(exc) == "ResourceNotFoundException":
            return False
        raise


def _ensure_pitr(ddb: Any, name: str, dry_run: bool) -> None:
    """Checked and converged on EVERY run, whether the table pre-existed or was just created --
    idempotent means "ensure this state", not just "ensure existence"."""
    try:
        backups = ddb.describe_continuous_backups(TableName=name)["ContinuousBackupsDescription"]
        status = backups["PointInTimeRecoveryDescription"]["PointInTimeRecoveryStatus"]
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"dynamodb:{name}:pitr", "CHECK", f"FAILED {_error_code(exc)}")
        return
    if status == "ENABLED":
        _record(f"dynamodb:{name}:pitr", "SKIP", "already on")
        return
    if dry_run:
        _record(f"dynamodb:{name}:pitr", "ENABLE", "DRY-RUN -- would enable point-in-time recovery")
        return
    try:
        ddb.update_continuous_backups(
            TableName=name,
            PointInTimeRecoverySpecification={"PointInTimeRecoveryEnabled": True},
        )
        _record(f"dynamodb:{name}:pitr", "ENABLE", "enabled")
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"dynamodb:{name}:pitr", "ENABLE", f"FAILED {_error_code(exc)}")


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
                _record(f"dynamodb:{name}", "CREATE", f"FAILED {_error_code(exc)}")
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
        _record(f"dynamodb:{name}", "DELETE", f"FAILED {_error_code(exc)}")


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


def _ensure_queue(sqs: Any, name: str, dry_run: bool, *, attributes: dict[str, str]) -> str | None:
    """Create-if-missing. Returns the queue URL if the queue exists or was just created; `None`
    only in dry-run, when nothing was actually created and there is no URL to hand back."""
    url = _queue_url(sqs, name)
    if url is not None:
        _record(f"sqs:{name}", "SKIP", "already exists")
        return url
    if dry_run:
        _record(f"sqs:{name}", "CREATE", "DRY-RUN -- would create")
        return None
    try:
        url = sqs.create_queue(QueueName=name, Attributes=attributes)["QueueUrl"]
        _record(f"sqs:{name}", "CREATE", "created")
        return url
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"sqs:{name}", "CREATE", f"FAILED {_error_code(exc)}")
        return None


def _provision_queues(sqs: Any, stage: str, dry_run: bool) -> None:
    print("\nSQS -- transcript ingest bus (FIFO) + investigation queue with a DLQ")
    transcripts = f"earshot-{stage}-transcripts.fifo"
    _ensure_queue(
        sqs, transcripts, dry_run,
        attributes={"FifoQueue": "true", "ContentBasedDeduplication": "false"},
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
    dlq_arn = sqs.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=["QueueArn"])
    dlq_arn = dlq_arn["Attributes"]["QueueArn"]
    redrive = json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": 3})
    _ensure_queue(sqs, inv_name, dry_run, attributes={"RedrivePolicy": redrive})


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
        _record(f"sqs:{name}", "DELETE", f"FAILED {_error_code(exc)}")


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
    for name in (
        f"earshot-{stage}-transcripts.fifo",
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
