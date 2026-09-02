"""CloudWatch alarms over the EMF metrics the handlers emit. Idempotent, dry-run by default.

    uv run --extra aws python tools/alarms.py --stage dev
    uv run --extra aws python tools/alarms.py --stage dev --no-dry-run

Separate from `provision.py` because these depend on the handlers being deployed and emitting,
where tables and queues do not. Same conventions: one row per action, converges on every run, says
what it would do before doing it.

**Nothing pages anyone, and that is stated rather than implied.** A CloudWatch alarm action can
target SNS, EC2, Auto Scaling or Systems Manager. There is no SNS on this account
(`docs/ops/progress.md`), so these alarms are created with **no actions at all**: they go RED in the
console and on a dashboard, and no human is woken. The intended routing is EventBridge's
`CloudWatch Alarm State Change` event to a notifier Lambda, which does not exist — and building one
would be the first outbound contact surface in a system whose HITL guarantee is that there is none
(`aws/api.py`). An operator-facing notifier is not a customer-facing one, so this is a gap to close
deliberately, not a rule to break accidentally. Until then: **the alarms are visible, not
actionable.**

**An alarm on a metric that has never been emitted is not an error.** It sits in INSUFFICIENT_DATA
until the first datapoint, which is the correct state for a system that has not run yet.
`TreatMissingData` is `notBreaching` throughout: a queue with nothing in it is quiet, not broken,
and an alarm that goes red every night at 3am trains people to ignore it.

**Not verified against the account.** `cloudwatch:PutMetricAlarm` has never been exercised here.
The specs below are unit-tested (`tests/test_alarms.py`); the API calls are not, and per
`docs/ops/handover.md` a green stub test is not proof. Run the dry-run first and read the rows.
"""

from __future__ import annotations

import argparse
from typing import Any

from earshot.aws.metrics import NAMESPACE
from earshot.aws.stores import REGION, STAGES

# `COST_CAP_PER_CASE_USD * 0.8`, derived rather than typed. The per-case cap already stops one
# runaway investigation; this catches the AVERAGE creeping toward it, which is the shape of a
# prompt or a model getting more expensive without anyone deciding that it should.
#
# It was a literal 0.20 until 2026-08-29. When the cap was re-derived from 50 keyed cases and fell
# to $0.10, this stayed at $0.20 — an alarm set at twice the cap, which could only ever have fired
# after the cap had already stopped the run. A test caught it. Deriving it removes the chance of a
# repeat, and the test stays because a derivation can still be wrong.
from earshot.aws.investigate import COST_CAP_PER_CASE_USD

COST_WARN_USD = round(COST_CAP_PER_CASE_USD * 0.8, 4)


def alarm_specs(stage: str) -> list[dict[str, Any]]:
    """Every alarm, as plain data, so the set is reviewable and testable without AWS.

    Each entry is a `put_metric_alarm` kwargs dict. Deliberately few: an alarm nobody acts on is
    worse than no alarm, because it teaches people that red means nothing.
    """
    dims = [{"Name": "Stage", "Value": stage}]
    return [
        {
            "AlarmName": f"earshot-{stage}-ingest-failures",
            "AlarmDescription": (
                "A transcript could not be ingested. Handled per-record (batchItemFailures), so "
                "the batch still committed -- but three of these on one message means the DLQ."
            ),
            "Namespace": NAMESPACE,
            "MetricName": "Failed",
            "Dimensions": dims,
            "Statistic": "Sum",
            "Period": 300,
            "EvaluationPeriods": 1,
            "Threshold": 1,
            "ComparisonOperator": "GreaterThanOrEqualToThreshold",
            "TreatMissingData": "notBreaching",
        },
        {
            "AlarmName": f"earshot-{stage}-api-errors",
            "AlarmDescription": (
                "The reviewer API returned a 500. The response body carries no detail on purpose, "
                "so the log line behind this alarm is the only place the cause exists."
            ),
            "Namespace": NAMESPACE,
            "MetricName": "ServerError",
            "Dimensions": dims,
            "Statistic": "Sum",
            "Period": 300,
            "EvaluationPeriods": 1,
            "Threshold": 1,
            "ComparisonOperator": "GreaterThanOrEqualToThreshold",
            "TreatMissingData": "notBreaching",
        },
        {
            "AlarmName": f"earshot-{stage}-cost-per-investigation",
            "AlarmDescription": (
                f"Average model spend per investigation above ${COST_WARN_USD:.2f}. The per-case "
                "cap stops one runaway; this catches the average creeping toward it, which is what "
                "a more expensive prompt or model looks like before anyone notices."
            ),
            "Namespace": NAMESPACE,
            "MetricName": "CostUsd",
            "Dimensions": dims,
            "Statistic": "Average",
            "Period": 3600,
            "EvaluationPeriods": 1,
            "Threshold": COST_WARN_USD,
            "ComparisonOperator": "GreaterThanThreshold",
            "TreatMissingData": "notBreaching",
        },
        {
            "AlarmName": f"earshot-{stage}-evidence-repairs",
            "AlarmDescription": (
                "Decisions whose citations did not resolve on the first attempt. This is the AT-57 "
                "groundedness signal: the loop repairs them, so accuracy looks fine while the "
                "model's honesty degrades underneath it."
            ),
            "Namespace": NAMESPACE,
            "MetricName": "EvidenceRepairs",
            "Dimensions": dims,
            "Statistic": "Sum",
            "Period": 3600,
            "EvaluationPeriods": 1,
            "Threshold": 5,
            "ComparisonOperator": "GreaterThanThreshold",
            "TreatMissingData": "notBreaching",
        },
        {
            "AlarmName": f"earshot-{stage}-investigations-dlq",
            "AlarmDescription": (
                "Anything in the investigations DLQ. A message reaches it after three failed "
                "receives, so one message here is a poison crossing nobody has looked at."
            ),
            "Namespace": "AWS/SQS",
            "MetricName": "ApproximateNumberOfMessagesVisible",
            "Dimensions": [
                {"Name": "QueueName", "Value": f"earshot-{stage}-investigations-dlq"}
            ],
            "Statistic": "Maximum",
            "Period": 300,
            "EvaluationPeriods": 1,
            "Threshold": 0,
            "ComparisonOperator": "GreaterThanThreshold",
            "TreatMissingData": "notBreaching",
        },
        {
            "AlarmName": f"earshot-{stage}-ingest-lag",
            "AlarmDescription": (
                "Oldest unprocessed transcript older than 15 minutes. The entry's claim is that a "
                "conversation re-scores the ledger within seconds; this is the number that would "
                "falsify it."
            ),
            "Namespace": "AWS/SQS",
            "MetricName": "ApproximateAgeOfOldestMessage",
            "Dimensions": [
                {"Name": "QueueName", "Value": f"earshot-{stage}-transcripts.fifo"}
            ],
            "Statistic": "Maximum",
            "Period": 300,
            "EvaluationPeriods": 1,
            "Threshold": 900,
            "ComparisonOperator": "GreaterThanThreshold",
            "TreatMissingData": "notBreaching",
        },
    ]


_ROWS: list[tuple[str, str, str]] = []


def _record(resource: str, action: str, result: str) -> None:
    _ROWS.append((resource, action, result))
    print(f"  {action:<8} {resource:<44} {result}")


def _error_code(exc: Exception) -> str:
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


def _exists(cw: Any, name: str) -> bool:
    found = cw.describe_alarms(AlarmNames=[name]).get("MetricAlarms", [])
    return bool(found)


def main() -> int:
    parser = argparse.ArgumentParser(description="CloudWatch alarms over earshot's EMF metrics")
    parser.add_argument("--stage", choices=STAGES, required=True)
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="default: on. Pass --no-dry-run to create or update anything.",
    )
    args = parser.parse_args()

    import boto3  # noqa: PLC0415 -- the whole script is the AWS path

    cw = boto3.client("cloudwatch", region_name=REGION)

    print(f"ALARMS  stage={args.stage}  region={REGION}  dry_run={args.dry_run}")
    print(f"  {'ACTION':<8} {'RESOURCE':<44} RESULT\n")
    print("CloudWatch alarms (no actions -- see the module docstring: nothing pages anyone)")

    for spec in alarm_specs(args.stage):
        name = spec["AlarmName"]
        try:
            exists = _exists(cw, name)
        except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
            _record(f"cloudwatch:{name}", "CHECK", f"FAILED {_error_detail(exc)}")
            continue
        if args.dry_run:
            _record(f"cloudwatch:{name}", "UPDATE" if exists else "CREATE", "DRY-RUN")
            continue
        try:
            # `put_metric_alarm` is create-or-replace, so converging is the same call either way.
            # ActionsEnabled=False as well as no actions: belt and braces against someone adding
            # an SNS topic later and being surprised at 3am.
            cw.put_metric_alarm(ActionsEnabled=False, **spec)
            _record(f"cloudwatch:{name}", "UPDATE" if exists else "CREATE", "ok")
        except Exception as exc:  # noqa: BLE001
            _record(f"cloudwatch:{name}", "UPDATE" if exists else "CREATE", f"FAILED {_error_detail(exc)}")

    print("\nPARKED -- deliberate gaps, not oversights")
    _record(
        "sns:earshot-alerts",
        "PARK",
        "no SNS on this account; alarms are visible in the console and page nobody",
    )
    _record(
        "events:alarm-state-change -> notifier",
        "PARK",
        "needs a notifier Lambda that does not exist. An operator notifier is not a customer "
        "contact surface, but it is the first thing that would look like one -- build it "
        "deliberately (see aws/api.py on why absence is the control)",
    )

    failed = [row for row in _ROWS if "FAILED" in row[2]]
    print("\n" + "-" * 78)
    print(f"{len(_ROWS)} rows: {len(_ROWS) - len(failed)} ok, {len(failed)} failed")
    if args.dry_run:
        print("\nDRY-RUN -- nothing was created or changed. Pass --no-dry-run to act.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
