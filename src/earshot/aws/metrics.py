"""Observability by printing — CloudWatch Embedded Metric Format (W11).

**Why EMF and not `PutMetricData`.** An API call per metric costs money, adds latency to the hot
path, needs `cloudwatch:PutMetricData` on the execution role (which it does not have, and which is
not worth a second IT ask), and fails independently of the work it is measuring. EMF is a JSON line
on stdout: the Lambda log driver extracts the metrics, and a handler that cannot reach CloudWatch
still leaves a complete record in its own log group. The metric and the log line are the same
object, so they can never disagree about what happened.

**One line does both jobs.** `emit()` prints a record that CloudWatch reads as metrics and a human
reads as a structured log. `event` stays on every line so the existing Insights queries
(`event="ingest.failed"`) keep working — the handlers used to print bare JSON and this is a strict
superset of that.

**What is a metric and what is a property.** Anything you would alarm on or graph is a metric;
anything you would filter or grep by is a property. `customer_id` is a property, never a dimension:
a dimension with unbounded cardinality creates one CloudWatch metric per customer and a bill that
grows with the portfolio. `DIMENSIONS` is deliberately tiny for the same reason.

**Alarms target EventBridge, not SNS.** There is no SNS on this account (`docs/ops/progress.md`),
so the alarm path is CloudWatch alarm → EventBridge rule → Lambda. That is a deployment concern and
not this module's, but it is why nothing here tries to notify anyone.
"""

from __future__ import annotations

import json
import os
from typing import Any

NAMESPACE = "Earshot"

# The unit strings CloudWatch accepts. Spelled out rather than passed as free text: a typo makes
# CloudWatch silently drop the metric, and a metric that is silently absent looks exactly like a
# system that is quietly healthy.
COUNT = "Count"
MILLISECONDS = "Milliseconds"
NONE = "None"


def _stage() -> str:
    return os.environ.get("EARSHOT_STAGE", "dev")


def emf(
    event: str,
    metrics: dict[str, tuple[float, str]],
    *,
    dimensions: dict[str, str] | None = None,
    properties: dict[str, Any] | None = None,
    namespace: str = NAMESPACE,
    timestamp_ms: int | None = None,
) -> dict[str, Any]:
    """Build one EMF record. Pure, so the shape is testable without capturing stdout.

    `metrics` maps name -> (value, unit). `timestamp_ms` is accepted so a test can pin it; in
    production it is omitted and CloudWatch stamps the record with the log event's own time, which
    is more truthful than a clock this process read at a slightly different moment.
    """
    dimensions = {"Stage": _stage(), **(dimensions or {})}
    directive: dict[str, Any] = {
        "CloudWatchMetrics": [
            {
                "Namespace": namespace,
                # One dimension SET, not one per key: CloudWatch multiplies dimension sets into
                # separate metrics, and three sets of the same counter is three times the bill for
                # the same information.
                "Dimensions": [sorted(dimensions)],
                "Metrics": [
                    {"Name": name, "Unit": unit} for name, (_, unit) in sorted(metrics.items())
                ],
            }
        ]
    }
    if timestamp_ms is not None:
        directive["Timestamp"] = timestamp_ms

    record: dict[str, Any] = {"_aws": directive, "event": event}
    record.update(dimensions)
    record.update({name: value for name, (value, _) in metrics.items()})
    for key, value in (properties or {}).items():
        # A property must never silently overwrite a metric -- the record would still be valid
        # JSON and CloudWatch would extract a string where a number was declared, dropping the
        # datapoint without an error anywhere.
        if key in record:
            raise ValueError(f"property {key!r} collides with a metric or dimension")
        record[key] = value
    return record


def emit(
    event: str,
    metrics: dict[str, tuple[float, str]],
    *,
    dimensions: dict[str, str] | None = None,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """`emf()` on stdout, which is all a Lambda has to do. Returns the record so a caller can
    assert on it."""
    record = emf(event, metrics, dimensions=dimensions, properties=properties)
    print(json.dumps(record, default=str))
    return record
