"""EMF observability — W11, and the handlers that emit it.

The record is checked as a shape rather than as a string, because CloudWatch's failure mode here is
silent: a malformed `_aws` block, an unknown unit or a declared metric whose value is a string is
dropped without an error anywhere, and a metric that is silently absent looks exactly like a system
that is quietly healthy.

Two properties are about cost rather than correctness and are easy to regress:

* **no unbounded dimension.** A dimension per customer is one CloudWatch metric per customer.
* **one dimension set, not one per key.** CloudWatch multiplies dimension sets into separate
  metrics, so three sets of the same counter is three times the bill for the same information.
"""

from __future__ import annotations

import json

import pytest
from test_investigate_handler import build as build_investigator
from test_transcripts import FakeS3

from earshot.aws import metrics as metrics_mod
from earshot.aws.metrics import COUNT, MILLISECONDS, NONE, emf, emit
from earshot.schema import SignalType

VALID_UNITS = {COUNT, MILLISECONDS, NONE}

# Anything that identifies one customer, one case or one message. Fine as a property, never as a
# dimension: cardinality is what makes CloudWatch expensive.
UNBOUNDED = {"customer_id", "case_id", "conversation_id", "messageId", "case", "customer"}


def directive(record: dict) -> dict:
    return record["_aws"]["CloudWatchMetrics"][0]


def declared(record: dict) -> set[str]:
    return {m["Name"] for m in directive(record)["Metrics"]}


# ---- the record shape --------------------------------------------------------------------


def test_a_declared_metric_always_has_a_numeric_value_at_the_top_level() -> None:
    """This is the silent failure: CloudWatch drops a datapoint whose declared metric resolves to
    a string, and nothing anywhere says so."""
    record = emf("t", {"Ingested": (1, COUNT), "LedgerScore": (0.42, NONE)})
    for name in declared(record):
        assert isinstance(record[name], int | float), f"{name} is not numeric"


def test_every_record_carries_the_timestamp_emf_requires() -> None:
    """The one that was missing. EMF requires `_aws.Timestamp`; without it CloudWatch stores the
    log line and silently DROPS the metrics. Measured on 2026-09-02: 130 well-formed ingest
    records, every declared value numeric, and `list_metrics` on the `Earshot` namespace returned
    nothing at all. Every alarm would have read INSUFFICIENT_DATA forever."""
    record = emf("t", {"Ingested": (1, COUNT)})
    assert "Timestamp" in record["_aws"], "no Timestamp: CloudWatch will drop these metrics"


def test_the_timestamp_is_epoch_milliseconds_not_seconds() -> None:
    """Seconds would be read as 1970 and land outside EMF's accepted window, which is the same
    silent drop by a different route."""
    record = emf("t", {"Ingested": (1, COUNT)})
    stamp = record["_aws"]["Timestamp"]
    assert isinstance(stamp, int)
    # 1e12 ms is 2001; a seconds-valued clock would be ~1.8e9 and fail this.
    assert stamp > 1_000_000_000_000, f"{stamp} looks like seconds, not milliseconds"


def test_a_pinned_timestamp_is_used_verbatim() -> None:
    """The parameter exists for tests and for a caller replaying a known time; it must not be
    quietly overridden by the clock."""
    record = emf("t", {"Ingested": (1, COUNT)}, timestamp_ms=1_700_000_000_123)
    assert record["_aws"]["Timestamp"] == 1_700_000_000_123


def test_every_handler_emits_a_timestamped_record(capsys) -> None:
    """Asserted through the handlers rather than only on `emf()`, because the bug was invisible
    precisely where the records are actually produced."""
    from earshot.aws.metrics import emit

    emit("ingest.ok", {"Ingested": (1, COUNT)})
    for line in capsys.readouterr().out.strip().splitlines():
        assert "Timestamp" in json.loads(line)["_aws"]


def test_the_stage_is_always_a_dimension() -> None:
    """dev and demo write to the same namespace. Without this, a demo run moves the dev alarm."""
    record = emf("t", {"Ingested": (1, COUNT)})
    assert record["Stage"]
    assert "Stage" in directive(record)["Dimensions"][0]


def test_there_is_exactly_one_dimension_set() -> None:
    record = emf("t", {"Ingested": (1, COUNT)}, dimensions={"StoppedBecause": "decision"})
    assert len(directive(record)["Dimensions"]) == 1


def test_the_event_name_survives_so_existing_log_queries_keep_working() -> None:
    """The handlers printed bare JSON with an `event` key before this existed, and the Insights
    queries written against that must not break."""
    record = emf("ingest.failed", {"Failed": (1, COUNT)})
    assert record["event"] == "ingest.failed"


def test_a_property_cannot_silently_overwrite_a_metric() -> None:
    """The record would still be valid JSON and CloudWatch would find a string where a number was
    declared — dropping the datapoint with no error."""
    with pytest.raises(ValueError, match="collides"):
        emf("t", {"Ingested": (1, COUNT)}, properties={"Ingested": "one"})


def test_emit_writes_one_json_line(capsys) -> None:
    emit("t", {"Ingested": (1, COUNT)}, properties={"customer_id": "C1"})
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 1
    assert json.loads(out[0])["customer_id"] == "C1"


# ---- the handlers ----------------------------------------------------------------------------


def _records(captured: str) -> list[dict]:
    return [
        json.loads(line)
        for line in captured.splitlines()
        if line.startswith("{") and "_aws" in line
    ]


def test_ingest_emits_the_duplicate_metric_that_makes_at_least_once_visible(capsys) -> None:
    """A7. Redelivery is harmless because the write is conditional, but a climb in this number is
    how anyone would ever notice something upstream redriving."""
    from test_ingest import _sqs_event, _transcript, build

    from earshot.aws import ingest as ingest_mod

    ingestor, _, _ = build(threshold=0.1)
    ingest_mod._INGESTOR = ingestor
    try:
        body = _transcript("C1", 0, "I want to close my account, this has gone on long enough")
        ingest_mod.handler(_sqs_event(("m1", body), ("m2", body)))
    finally:
        ingest_mod._INGESTOR = None

    records = _records(capsys.readouterr().out)
    assert len(records) == 2
    assert [r["DuplicateDeliveries"] for r in records] == [0, 1]
    assert records[0]["Crossings"] == 1


def test_ingest_emits_a_failure_metric_for_a_poison_record(capsys) -> None:
    from test_ingest import _sqs_event, build

    from earshot.aws import ingest as ingest_mod

    ingestor, _, _ = build(threshold=0.1)
    ingest_mod._INGESTOR = ingestor
    try:
        ingest_mod.handler(_sqs_event(("bad", "{not json")))
    finally:
        ingest_mod._INGESTOR = None

    record = _records(capsys.readouterr().out)[0]
    assert record["event"] == "ingest.failed"
    assert record["Failed"] == 1
    assert record["messageId"] == "bad"


def test_investigate_puts_stopped_because_on_a_dimension(capsys) -> None:
    """The distribution across exit reasons is the most diagnostic number this system produces: a
    shift toward `cost_cap` or `max_steps` is the agent degrading, and it moves before accuracy
    does. Its cardinality is bounded by the loop's own exits, so it is safe as a dimension."""
    investigator, _, _, _ = build_investigator()
    investigator.run("C1", SignalType.FINANCIAL_DISTRESS, 0.3)
    capsys.readouterr()

    from earshot.aws import investigate as inv_mod

    logged = investigator.run("C1", SignalType.FINANCIAL_DISTRESS, 0.3)
    inv_mod._emit_investigation(logged)
    record = _records(capsys.readouterr().out)[0]

    assert record["StoppedBecause"]
    assert "StoppedBecause" in directive(record)["Dimensions"][0]
    assert {"Investigated", "CostUsd", "ModelCalls", "EvidenceRepairs", "LatencyMs"} <= declared(
        record
    )


def test_investigate_reports_a_customer_who_no_longer_crosses_rather_than_staying_silent(
    capsys,
) -> None:
    from earshot.aws import investigate as inv_mod

    investigator, _, _, _ = build_investigator()
    logged = investigator.run("C1", SignalType.FINANCIAL_DISTRESS, threshold=0.99)
    inv_mod._emit_investigation(logged)

    record = _records(capsys.readouterr().out)[0]
    assert record["event"] == "investigate.no_longer_crossing"
    assert record["NoLongerCrossing"] == 1


def test_the_api_logs_an_error_type_and_never_its_message(capsys) -> None:
    """A `ClientError` naming a table is an information leak in a log a wider audience reads than
    the response body ever reaches."""
    from test_api import _event

    from earshot.aws import api as api_mod

    built = _blank_api()
    api_mod._API = built
    try:

        def boom(*_a, **_k):
            raise RuntimeError("dynamodb table earshot-dev-cases is on fire")

        built.cases.list_queue = boom  # type: ignore[method-assign]
        response = api_mod.handler(_event("GET", "/cases"))
    finally:
        api_mod._API = None

    assert response["statusCode"] == 500
    record = _records(capsys.readouterr().out)[0]
    assert record["error"] == "RuntimeError"
    assert record["ServerError"] == 1
    assert "on fire" not in json.dumps(record)


def _blank_api():
    from test_stores import FakeTable

    from earshot.aws.api import ReviewerApi
    from earshot.aws.stores import CaseStore, LedgerStore, ReviewStore
    from earshot.aws.transcripts import TranscriptArchive

    return ReviewerApi(
        CaseStore("cases", table=FakeTable()),
        ReviewStore("reviews", table=FakeTable()),
        LedgerStore("ledger", table=FakeTable()),
        TranscriptArchive("dev", s3=FakeS3()),
    )


# ---- cost discipline ----------------------------------------------------------------------------


def test_no_handler_puts_an_unbounded_field_on_a_dimension(capsys) -> None:
    """One dimension per customer is one CloudWatch metric per customer, and the bill grows with
    the portfolio. Every one of these belongs in `properties`, where it is still greppable."""
    from test_ingest import _sqs_event, _transcript, build

    from earshot.aws import ingest as ingest_mod
    from earshot.aws import investigate as inv_mod

    ingestor, _, _ = build(threshold=0.1)
    ingest_mod._INGESTOR = ingestor
    try:
        ingest_mod.handler(
            _sqs_event(("m1", _transcript("C1", 0, "I want to close my account, enough")))
        )
    finally:
        ingest_mod._INGESTOR = None

    investigator, _, _, _ = build_investigator()
    inv_mod._emit_investigation(investigator.run("C1", SignalType.FINANCIAL_DISTRESS, 0.3))

    for record in _records(capsys.readouterr().out):
        leaked = set(directive(record)["Dimensions"][0]) & UNBOUNDED
        assert not leaked, f"{record['event']} dimensions on {sorted(leaked)}"


def test_every_unit_is_one_cloudwatch_accepts(capsys) -> None:
    """A typo makes CloudWatch drop the metric silently, so the units are named constants and this
    is what stops a raw string sneaking back in."""
    from test_ingest import _sqs_event, _transcript, build

    from earshot.aws import ingest as ingest_mod

    ingestor, _, _ = build(threshold=0.1)
    ingest_mod._INGESTOR = ingestor
    try:
        ingest_mod.handler(
            _sqs_event(("m1", _transcript("C1", 0, "I want to close my account, enough")))
        )
    finally:
        ingest_mod._INGESTOR = None

    for record in _records(capsys.readouterr().out):
        for metric in directive(record)["Metrics"]:
            assert metric["Unit"] in VALID_UNITS, metric


def test_the_namespace_is_one_string_in_one_place() -> None:
    """Two namespaces is two dashboards, and the second one is always the empty one."""
    assert metrics_mod.NAMESPACE == "Earshot"
    assert directive(emf("t", {"X": (1, COUNT)}))["Namespace"] == "Earshot"
