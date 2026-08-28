"""The alarm set, as data.

`tools/alarms.py` builds `put_metric_alarm` kwargs and then calls AWS. Only the first half is
testable here, and per `docs/ops/handover.md` a green stub test is not proof — the API calls have
been dry-run against the live account and nothing has been created yet.

What these do check is the part that is wrong in a way nobody notices: an alarm on a metric no
handler emits is permanently INSUFFICIENT_DATA and silently guards nothing, and an alarm that goes
red every quiet night trains people to ignore the whole set.
"""

from __future__ import annotations

import alarms
import pytest

from earshot.aws.metrics import NAMESPACE

STAGES = ("dev", "demo")

# Every metric name the handlers actually emit, from aws/{ingest,investigate,api}.py.
EMITTED = {
    "Ingested",
    "SignalsWritten",
    "DuplicateDeliveries",
    "Crossings",
    "Investigations",
    "LedgerScore",
    "Failed",
    "Investigated",
    "CostUsd",
    "ModelCalls",
    "EvidenceRepairs",
    "ScoreDrifted",
    "LatencyMs",
    "NoLongerCrossing",
    "ServerError",
}


@pytest.fixture
def specs() -> list[dict]:
    return alarms.alarm_specs("dev")


def test_every_alarm_on_our_namespace_watches_a_metric_a_handler_emits(specs) -> None:
    """An alarm on a metric nothing writes sits in INSUFFICIENT_DATA forever and guards nothing,
    while looking on a dashboard exactly like an alarm that is fine."""
    for spec in specs:
        if spec["Namespace"] != NAMESPACE:
            continue  # AWS/SQS metrics are emitted by SQS, not by us
        assert spec["MetricName"] in EMITTED, f"{spec['AlarmName']} watches a phantom metric"


def test_the_sqs_alarms_name_queues_provision_actually_creates(specs) -> None:
    from earshot.aws.stores import table_name  # noqa: F401 -- same naming convention, dev stage

    expected = {"earshot-dev-investigations-dlq", "earshot-dev-transcripts.fifo"}
    named = {
        dim["Value"]
        for spec in specs
        if spec["Namespace"] == "AWS/SQS"
        for dim in spec["Dimensions"]
        if dim["Name"] == "QueueName"
    }
    assert named == expected


def test_nothing_is_quiet_enough_to_alarm_on_missing_data(specs) -> None:
    """A queue with nothing in it is quiet, not broken. An alarm that goes red every night at 3am
    teaches people that red means nothing, which is worse than having no alarm."""
    for spec in specs:
        assert spec["TreatMissingData"] == "notBreaching", spec["AlarmName"]


def test_every_alarm_explains_itself(specs) -> None:
    """The description is what someone reads at 2am, and it is the only context an alarm carries
    into a console that knows nothing about this repository."""
    for spec in specs:
        assert len(spec["AlarmDescription"]) > 60, spec["AlarmName"]


def test_alarm_names_are_stage_scoped_and_unique(specs) -> None:
    """dev and demo share a namespace and a console. An unprefixed name means a demo run silently
    reconfigures the dev alarm."""
    names = [spec["AlarmName"] for spec in specs]
    assert len(names) == len(set(names))
    assert all(name.startswith("earshot-dev-") for name in names)
    assert all(
        spec["AlarmName"].startswith("earshot-demo-") for spec in alarms.alarm_specs("demo")
    )


def test_the_cost_alarm_fires_below_the_per_case_cap(specs) -> None:
    """It exists to catch the average creeping toward the cap. Set at or above the cap it could
    only fire after the cap had already stopped the run, which is a report and not a warning."""
    from earshot.aws.investigate import COST_CAP_PER_CASE_USD

    cost = next(s for s in specs if s["MetricName"] == "CostUsd")
    assert cost["Threshold"] < COST_CAP_PER_CASE_USD
    assert cost["Statistic"] == "Average"


def test_the_set_stays_small_enough_that_someone_reads_it(specs) -> None:
    """An alarm nobody acts on is worse than no alarm. This is a judgement, pinned so that growing
    the set is a decision rather than an accretion."""
    assert len(specs) <= 8


def test_the_specs_are_valid_put_metric_alarm_kwargs(specs) -> None:
    required = {
        "AlarmName",
        "Namespace",
        "MetricName",
        "Statistic",
        "Period",
        "EvaluationPeriods",
        "Threshold",
        "ComparisonOperator",
    }
    valid_ops = {
        "GreaterThanThreshold",
        "GreaterThanOrEqualToThreshold",
        "LessThanThreshold",
        "LessThanOrEqualToThreshold",
    }
    for spec in specs:
        assert required <= set(spec), f"{spec['AlarmName']} is missing {required - set(spec)}"
        assert spec["ComparisonOperator"] in valid_ops
        assert spec["Period"] % 60 == 0, "CloudWatch periods are whole minutes above 60s"
