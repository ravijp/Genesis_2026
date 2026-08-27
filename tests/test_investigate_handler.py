"""The investigate handler: a crossing off the queue becomes a persisted case.

Fake DynamoDB, fake S3, and the **offline rule-engine provider** -- so this runs the real path with
no AWS, no key and no spend. The offline provider's verdicts are a floor, not a result; what is
under test here is the wiring around the loop, not the model's judgment.

The claims worth pinning:

* the score in the case is **recomputed from the ledger**, not the one the queue message carried
  (a conversation can land between the crossing and this run);
* nothing here scores -- the number equals an ordinary `SignalLedger`'s;
* a missing transcript archive fails loudly rather than producing a case that says "insufficient
  evidence" about a customer with plenty;
* the persisted case is the same shape `case_record()` writes to disk, and carries the retro
  fields the reviewer UI reads;
* re-investigating the same crossing overwrites one case rather than forking the queue.
"""

from __future__ import annotations

import json

import pytest
from test_stores import FakeTable
from test_transcripts import FakeS3

from earshot.aws import investigate as inv_mod
from earshot.aws.investigate import (
    COST_CAP_PER_CASE_USD,
    CrossingError,
    Investigator,
    handler,
    parse_crossing,
)
from earshot.aws.stores import CaseStore, LedgerStore
from earshot.aws.transcripts import TranscriptArchive
from earshot.config import ScoringConfig
from earshot.llm.offline import OfflineProvider
from earshot.memory import SignalLedger
from earshot.schema import Channel, Conversation, ExtractedSignal, SignalType, Turn

QUOTES = {
    "K0": "Money has been really tight since the hours were cut.",
    "K1": "I had to put the council tax on a credit card this month.",
    "K2": "We're behind on the rent and I don't know what to do.",
}


def conversations() -> tuple[Conversation, ...]:
    return tuple(
        Conversation(
            conversation_id=cid,
            customer_id="C1",
            channel=channel,
            day=day,
            turns=(
                Turn(0, "agent", "Thanks for calling."),
                Turn(1, "customer", QUOTES[cid]),
                Turn(2, "agent", "Noted."),
            ),
        )
        for cid, day, channel in (
            ("K0", 10, Channel.CALL),
            ("K1", 40, Channel.CHAT),
            ("K2", 70, Channel.COMPLAINT),
        )
    )


def signals() -> list[ExtractedSignal]:
    return [
        ExtractedSignal(
            customer_id="C1",
            conversation_id=c.conversation_id,
            signal_type=SignalType.FINANCIAL_DISTRESS,
            confidence=0.45,
            evidence_quote=QUOTES[c.conversation_id],
            turn_index=1,
            day=c.day,
            channel=c.channel,
        )
        for c in conversations()
    ]


def build(threshold: float = 0.3, *, archive_transcripts: bool = True):
    """A wired `Investigator` over fakes. Returns `(investigator, ledger_table, case_table, s3)`."""
    ledger_table, case_table, s3 = FakeTable(), FakeTable(), FakeS3()
    ledger_store = LedgerStore("ledger", table=ledger_table)
    ledger_store.append_all(signals())
    archive = TranscriptArchive("dev", s3=s3)
    if archive_transcripts:
        for conversation in conversations():
            archive.put(conversation)
    investigator = Investigator(
        OfflineProvider(),
        ledger_store,
        CaseStore("cases", table=case_table),
        archive,
    )
    return investigator, ledger_table, case_table, s3


def local_score(ledger_table: FakeTable, as_of_day: int = 70) -> float:
    """What an ordinary in-memory `SignalLedger` says, from the same stored signals."""
    ledger = SignalLedger(ScoringConfig())
    ledger.extend(LedgerStore("ledger", table=ledger_table).load("C1"))
    return ledger.score("C1", SignalType.FINANCIAL_DISTRESS, as_of_day).score


# ---- parsing ------------------------------------------------------------------------------------


def test_a_crossing_missing_its_coordinates_is_rejected() -> None:
    with pytest.raises(CrossingError, match="missing"):
        parse_crossing({"customer_id": "C1"})


def test_an_unknown_signal_family_fails_the_record_with_a_readable_message() -> None:
    with pytest.raises(CrossingError, match="unknown signal_type"):
        parse_crossing({"customer_id": "C1", "signal_type": "vibes", "threshold": 0.3})


def test_the_message_score_is_optional_because_it_is_not_trusted() -> None:
    crossing = parse_crossing(
        {"customer_id": "C1", "signal_type": "financial_distress", "threshold": 0.3}
    )
    assert crossing["reported_score"] is None
    assert crossing["signal_type"] is SignalType.FINANCIAL_DISTRESS


# ---- the context assembled from storage ----------------------------------------------------------


def test_the_context_is_built_from_the_ledger_and_the_archive_not_from_the_message() -> None:
    investigator, ledger_table, _, _ = build()
    ctx = investigator.context("C1", SignalType.FINANCIAL_DISTRESS, threshold=0.3)

    assert ctx.as_of_day == 70
    assert [c.conversation_id for c in ctx.conversations] == ["K0", "K1", "K2"]
    assert ctx.score == local_score(ledger_table), "the handler is scoring, not delegating"
    assert ctx.breakdown is not None and len(ctx.breakdown.entries) == 3


def test_the_synthetic_account_risk_is_stable_across_processes() -> None:
    """`hash()` is salted per process, so the same customer would get a different synthetic
    account on every cold start and two investigations would disagree about their transactions."""
    first = inv_mod._synthetic_risk("CUST-0007")
    assert first == inv_mod._synthetic_risk("CUST-0007")
    assert first != inv_mod._synthetic_risk("CUST-0008")
    assert 0.0 <= first < 1.0


def test_a_customer_with_no_archived_transcripts_fails_loudly() -> None:
    """With no transcripts every citation is unresolvable: the loop would spend its whole retry
    budget rejecting its own decisions and land a case reading "insufficient evidence" about a
    customer who has plenty. The DLQ is the right destination, and the error names the cause."""
    investigator, _, _, _ = build(archive_transcripts=False)
    with pytest.raises(CrossingError, match="no archived transcripts"):
        investigator.context("C1", SignalType.FINANCIAL_DISTRESS, threshold=0.3)


def test_a_customer_with_no_ledger_entries_fails_loudly() -> None:
    investigator, _, _, _ = build()
    with pytest.raises(CrossingError, match="no ledger entries"):
        investigator.context("C-NOBODY", SignalType.FINANCIAL_DISTRESS, threshold=0.3)


# ---- the persisted case ---------------------------------------------------------------------------


def test_a_crossing_becomes_a_case_the_reviewer_ui_can_render() -> None:
    investigator, ledger_table, case_table, _ = build(threshold=0.3)
    logged = investigator.run("C1", SignalType.FINANCIAL_DISTRESS, 0.3)

    assert logged["event"] == "investigate.ok"
    case = CaseStore("cases", table=case_table).get_case(logged["case_id"])
    assert case is not None
    assert case["customer_id"] == "C1"
    assert case["signal_type"] == "financial_distress"
    assert case["score"] == local_score(ledger_table)
    assert case["threshold"] == 0.3
    assert case["status"] == "open"
    assert case["decision"]["verdict"]
    for row in case["evidence"]:
        assert {"score_at_write", "score_now", "retro_delta", "load_bearing"} <= set(row)


def test_the_case_says_its_account_data_is_synthetic() -> None:
    """There is no bank core feed behind this. A reviewer UI must be able to label the account
    panel rather than presenting a hash-derived transaction history as a record."""
    investigator, _, case_table, _ = build()
    logged = investigator.run("C1", SignalType.FINANCIAL_DISTRESS, 0.3)
    case = CaseStore("cases", table=case_table).get_case(logged["case_id"])
    assert case["trace"]["account_data"] == inv_mod.SYNTHETIC_ACCOUNT_MARKER


def test_the_score_of_record_is_recomputed_and_drift_is_reported_not_hidden() -> None:
    """A conversation can land between the crossing and this run. The case must carry the current
    score, and the log must say the enqueued one disagreed rather than quietly discarding it."""
    investigator, ledger_table, case_table, _ = build()
    stale = 0.01

    logged = investigator.run(
        "C1", SignalType.FINANCIAL_DISTRESS, 0.3, reported_score=stale
    )
    assert logged["score"] == round(local_score(ledger_table), 6)
    assert logged["score_when_enqueued"] == stale
    assert logged["score_drifted"] is True

    case = CaseStore("cases", table=case_table).get_case(logged["case_id"])
    assert case["score"] != stale


def test_re_investigating_the_same_crossing_overwrites_one_case() -> None:
    """Otherwise every new conversation on an already-crossed customer forks a fresh case and the
    reviewer's queue grows with duplicates of one situation."""
    investigator, _, case_table, _ = build()
    first = investigator.run("C1", SignalType.FINANCIAL_DISTRESS, 0.3)
    second = investigator.run("C1", SignalType.FINANCIAL_DISTRESS, 0.3)

    assert first["case_id"] == second["case_id"]
    assert len(CaseStore("cases", table=case_table).list_queue("open")) == 1


def test_a_customer_who_no_longer_crosses_produces_no_case() -> None:
    """Decay, or a threshold raised since the message was enqueued. Do not invent a crossing to
    hang a case on -- and say why in the log rather than failing silently."""
    investigator, _, case_table, _ = build()
    logged = investigator.run("C1", SignalType.FINANCIAL_DISTRESS, threshold=0.99)

    assert logged["event"] == "investigate.no_longer_crossing"
    assert "case_id" not in logged
    assert CaseStore("cases", table=case_table).list_queue("open") == []


def test_the_deployed_cost_cap_matches_the_local_one() -> None:
    """The constant is duplicated rather than imported, because `cli.py` pulls in the corpus and
    this module may not. Duplication that is checked is fine; duplication that is hoped for is not."""
    from earshot.cli import COST_CAP_PER_CASE_USD as local_cap

    assert COST_CAP_PER_CASE_USD == local_cap


# ---- the Lambda entrypoint --------------------------------------------------------------------------


@pytest.fixture
def wired(monkeypatch):
    investigator, ledger_table, case_table, s3 = build()
    monkeypatch.setattr(inv_mod, "_INVESTIGATOR", investigator)
    return investigator, ledger_table, case_table, s3


def _event(*bodies: tuple[str, str]) -> dict:
    return {"Records": [{"messageId": mid, "body": body} for mid, body in bodies]}


def _crossing(threshold: float = 0.3) -> str:
    return json.dumps(
        {
            "customer_id": "C1",
            "signal_type": "financial_distress",
            "score": 0.5,
            "threshold": threshold,
            "as_of_day": 70,
            "triggered_by_conversation": "K2",
        }
    )


def test_the_handler_investigates_a_crossing_and_persists_it(wired, capsys) -> None:
    _, _, case_table, _ = wired
    assert handler(_event(("m1", _crossing()))) == {"batchItemFailures": []}

    logged = [json.loads(li) for li in capsys.readouterr().out.splitlines() if li.startswith("{")]
    assert logged[0]["event"] == "investigate.ok"
    assert CaseStore("cases", table=case_table).get_case(logged[0]["case_id"]) is not None


def test_one_poison_crossing_fails_alone(wired) -> None:
    response = handler(_event(("good", _crossing()), ("poison", "{not json")))
    assert response == {"batchItemFailures": [{"itemIdentifier": "poison"}]}


def test_a_crossing_for_an_unknown_customer_reaches_the_dlq_rather_than_crashing(wired) -> None:
    body = json.dumps(
        {"customer_id": "C-NOBODY", "signal_type": "financial_distress", "threshold": 0.3}
    )
    assert handler(_event(("m1", body))) == {"batchItemFailures": [{"itemIdentifier": "m1"}]}


def test_an_empty_batch_is_a_no_op(wired) -> None:
    assert handler({"Records": []}) == {"batchItemFailures": []}
