"""The persisted case: one shape for disk and DynamoDB, retro fields intact, no answer key.

W1 was "`cli.py` throws the case fields away". The fix is a shared serializer, so the tests that
matter are not "does the dict have keys" but the three properties the fix exists to buy:

1. **No drift.** The artifact on disk and the `CASES` item carry the same case fields. Two
   serializers is how a reviewer screen renders a retro delta from one source and a blank column
   from the other, and that failure shows up on stage, not in CI.
2. **The retro fields survive.** `score_at_write` vs `score_now` per quote, and `load_bearing`,
   are the entire retro re-score beat. They are read off `memory.py`'s entries, never recomputed.
3. **No ground truth reaches the record.** This dict goes behind a client-facing screen.

No boto3 anywhere in this file; `CaseStore` runs against `test_stores.FakeTable`.
"""

from __future__ import annotations

import json

from earshot.aws import stores
from earshot.aws.stores import CaseStore
from earshot.case_record import case_record, make_case_id
from earshot.memory import SignalLedger
from earshot.schema import SignalType

from test_stores import FakeTable, sig

# Answer-key fields. `tests/test_separation.py` stops the extractor from importing the corpus;
# this stops the corpus's own vocabulary from arriving on a reviewer's screen by a different
# route — a persisted case built from a truth object.
ANSWER_KEY_FIELDS = {
    "stratum",
    "outcome",
    "outcome_day",
    "latent_risk",
    "financial_state",
    "seeded",
    "seeded_signals",
    "lead_days",
}


def _case(threshold: float = 0.05):
    """A customer who crosses on the first conversation and then keeps accumulating — the shape
    the retro beat is about. Returns `(opened, now)`: the crossing, and the customer today."""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    opened = ledger.open_case("C1", SignalType.FINANCIAL_DISTRESS, threshold)
    now = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 40)
    assert opened is not None
    assert len(opened.evidence) < len(now.entries), (
        "the fixture no longer accumulates after the case opens, so nothing below can tell a "
        "frozen evidence chain from a current one"
    )
    return opened, now


def _keys(obj) -> set[str]:
    """Every key at every depth — an answer-key field nested inside `evidence` or `trace` is
    just as exposed as one at the top level."""
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in _keys(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in _keys(v)}
    return set()


def test_the_disk_record_and_the_dynamodb_item_carry_the_same_case_fields() -> None:
    """The one property that makes the split safe. If `put_case` ever grows a readable field
    `case_record()` does not produce, this fails — which is the moment to move it into
    `case_record()` rather than to relax this test."""
    opened, now = _case()
    on_disk = case_record(opened, threshold=0.05, now=now)

    store = CaseStore("t", table=FakeTable())
    case_id = store.put_case(opened, threshold=0.05, now=now)
    in_dynamo = store.get_case(case_id)

    # pk/gsi1pk/gsi1sk are DynamoDB key attributes and belong only to the store.
    keys_only = {"pk", "gsi1pk", "gsi1sk"}
    assert set(in_dynamo) - keys_only == set(on_disk), (
        "the case shape has drifted between the artifact and the table"
    )
    for field, value in on_disk.items():
        assert in_dynamo[field] == value, f"{field} differs between disk and DynamoDB"


def test_the_record_is_json_serialisable_as_written() -> None:
    """`cli.py` writes it with `json.dumps`. A stray enum or dataclass in here is a crash at the
    end of a run that already spent the model budget."""
    opened, now = _case()
    record = case_record(opened, threshold=0.05, now=now)
    assert json.loads(json.dumps(record))["signal_type"] == "financial_distress"


def test_every_quote_carries_its_then_and_now_score() -> None:
    """The retro re-score beat, straight off `memory.py` — nothing here recomputes a score."""
    opened, now = _case()
    record = case_record(opened, threshold=0.05, now=now)
    by_day = {row["day"]: row for row in record["evidence"]}

    assert [row["day"] for row in record["evidence"]] == [0, 20, 40], (
        "the chain is not the customer's whole history, oldest first — a chain frozen at the "
        "opening day is the failure this record exists to prevent"
    )
    for entry in now.entries:
        row = by_day[entry.signal.day]
        assert row["score_at_write"] == entry.score_at_write
        assert row["score_now"] == entry.score_now
        assert row["retro_delta"] == entry.retro_delta
        assert row["load_bearing"] == entry.is_load_bearing(0.05)

    earliest = by_day[0]
    assert earliest["score_now"] != earliest["score_at_write"], (
        "the earliest quote scores the same then as now, so this corpus cannot demonstrate the "
        "retro beat and the test above is passing vacuously"
    )


def test_no_answer_key_field_reaches_the_persisted_case() -> None:
    opened, now = _case()
    record = case_record(
        opened,
        threshold=0.05,
        now=now,
        decision={"verdict": "escalate", "confidence": 0.8},
        trace={"cost_usd": 0.01},
    )
    leaked = _keys(record) & ANSWER_KEY_FIELDS
    assert not leaked, f"answer-key fields on a client-facing record: {sorted(leaked)}"


def test_the_two_scores_are_named_apart_and_the_queue_ranks_on_today() -> None:
    """Under decay a case's crossing-day score and its score today differ. One field for both is
    how a faded case keeps its opening-day seat at the top of the reviewer's queue."""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    # A threshold this customer only reaches on their last conversation, so nothing arrives
    # afterwards and decay alone moves the score. At 0.05 they cross on day 0 and the three
    # signals that follow outweigh the decay, which is the opposite case.
    opened = ledger.open_case("C1", SignalType.FINANCIAL_DISTRESS, 0.3)
    assert opened is not None and opened.opened_on_day == 40
    faded = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 400)
    assert faded.score < opened.score, "decay is not fading this customer; the test is vacuous"

    record = case_record(opened, threshold=0.3, now=faded)
    assert record["score"] == faded.score
    assert record["score_at_open"] == opened.score
    assert record["opened_on_day"] == opened.opened_on_day
    assert record["as_of_day"] == 400

    table = FakeTable()
    store = CaseStore("t", table=table)
    store.put_case(opened, threshold=0.3, now=faded)
    item = next(iter(table.items.values()))
    assert item["gsi1sk"] == stores._padded_score(faded.score)
    assert item["gsi1sk"] < stores._padded_score(opened.score), (
        "a faded case still sorts at its opening-day seat in the reviewer's queue"
    )


def test_a_record_built_without_a_current_score_still_reads_as_a_whole_case() -> None:
    """A caller holding only an opened case — the ingest handler's first write, before any
    re-score — must still produce a well-formed record."""
    opened, _ = _case()
    record = case_record(opened, threshold=0.05)
    assert record["score"] == record["score_at_open"] == opened.score
    assert record["as_of_day"] == record["opened_on_day"]
    assert [row["day"] for row in record["evidence"]] == [e.signal.day for e in opened.evidence]
    assert record["status"] == "open"


def test_the_case_id_is_the_crossing_not_the_run() -> None:
    """Re-investigating the same crossing must overwrite one case, not fork the queue."""
    opened, now = _case()
    first = case_record(opened, threshold=0.05)["case_id"]
    second = case_record(opened, threshold=0.05, now=now)["case_id"]
    expected = make_case_id("C1", SignalType.FINANCIAL_DISTRESS, opened.opened_on_day)
    assert first == second == expected
    assert first == CaseStore.make_case_id(
        "C1", SignalType.FINANCIAL_DISTRESS, opened.opened_on_day
    ), "the store and the disk path derive different ids for the same crossing"
