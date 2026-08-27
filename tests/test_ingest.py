"""The ingest handler, end to end, with no AWS and no model.

`FakeTable` (from `test_stores.py`) is the same fake DynamoDB the store tests use, so the path
under test here is the real one: extract -> conditional append -> reload -> `SignalLedger` ->
threshold. Nothing is stubbed between the handler and the scorer, which is the only way a test can
catch the failure this module is written against -- a second scorer appearing on the deployed path.

The tests that matter are the design claims, on the deployed path rather than on the laptop one:

* a sub-threshold signal is RETAINED and still summable (never-discard, the design inversion);
* two conversations cross where neither alone would (accumulation);
* the online score equals what `memory.py` computes locally, bit for bit (no second scorer);
* SQS at-least-once redelivery changes nothing (idempotency);
* one poison record fails alone (batch isolation).
"""

from __future__ import annotations

import json

import pytest
from test_stores import FakeTable

from earshot.aws import ingest as ingest_mod
from earshot.aws.ingest import (
    IngestError,
    Ingestor,
    QueuePublisher,
    handler,
    parse_conversation,
)
from earshot.aws.stores import LedgerStore
from earshot.config import ScoringConfig
from earshot.extract import OfflineLexiconExtractor
from earshot.memory import SignalLedger
from earshot.schema import Channel, Conversation, Turn

# Two turns the offline lexicon actually fires on (`c-close`, `c-rival` in extract_lexicon.py). A
# test built on text the extractor ignores passes for the wrong reason and proves nothing.
FIRES_ONCE = "I want to close my account, this has gone on long enough"
FIRES_AGAIN = "I have been comparing rates at another bank all week"


class FakeSQS:
    """`send_message` and nothing else -- the only SQS call this module makes."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send_message(self, QueueUrl: str, MessageBody: str) -> dict:  # noqa: N803 -- boto3 casing
        self.sent.append({"QueueUrl": QueueUrl, "MessageBody": MessageBody})
        return {"MessageId": f"m{len(self.sent)}"}


def convo(conversation_id: str, day: int, text: str, customer_id: str = "CUST-1") -> Conversation:
    return Conversation(
        conversation_id=conversation_id,
        customer_id=customer_id,
        channel=Channel.CALL,
        day=day,
        turns=(Turn(index=0, speaker="customer", text=text),),
    )


def build(threshold: float = 0.6, table: FakeTable | None = None):
    """An `Ingestor` over a fake table and a fake queue. Returns `(ingestor, table, sqs)`."""
    table = table or FakeTable()
    sqs = FakeSQS()
    ingestor = Ingestor(
        OfflineLexiconExtractor(),
        LedgerStore("t", table=table),
        threshold=threshold,
        publisher=QueuePublisher("https://sqs.invalid/q", sqs=sqs),
    )
    return ingestor, table, sqs


# ---- parsing: reject, never default -------------------------------------------------------------


def test_a_transcript_missing_a_scoring_field_is_rejected_not_defaulted() -> None:
    """`day` defaulted to 0 would place the signal at the corpus epoch and decay it to nothing --
    a wrong answer that looks like a working system."""
    with pytest.raises(IngestError, match="missing"):
        parse_conversation({"conversation_id": "C1", "customer_id": "X", "channel": "call"})


@pytest.mark.parametrize(
    "payload, match",
    [
        ({"channel": "carrier-pigeon"}, "unknown channel"),
        ({"day": "12"}, "day must be an integer"),
        ({"day": True}, "day must be an integer"),
        ({"turns": []}, "non-empty"),
        ({"turns": [{"speaker": "customer"}]}, "turn 0"),
    ],
)
def test_a_malformed_field_names_itself(payload: dict, match: str) -> None:
    base = {
        "conversation_id": "C1",
        "customer_id": "X",
        "channel": "call",
        "day": 3,
        "turns": [{"speaker": "customer", "text": "hello"}],
    }
    with pytest.raises(IngestError, match=match):
        parse_conversation({**base, **payload})


def test_the_producers_turn_index_wins_over_position() -> None:
    """Evidence citations resolve by `(conversation_id, turn_index)`, so re-indexing a turn breaks
    every quote that cites it."""
    parsed = parse_conversation(
        {
            "conversation_id": "C1",
            "customer_id": "X",
            "channel": "chat",
            "day": 3,
            "turns": [{"index": 7, "speaker": "customer", "text": "hello"}],
        }
    )
    assert parsed.turns[0].index == 7
    assert parsed.channel is Channel.CHAT


# ---- the design claims, on the deployed path -----------------------------------------------------


def test_a_sub_threshold_signal_is_retained_and_still_counts_later() -> None:
    """Never-discard, asserted where it is easiest to lose it. The first conversation does not
    cross, and the handler must still have written it -- so the second conversation scores against
    both, not against itself."""
    ingestor, table, sqs = build(threshold=0.6)

    first = ingestor.ingest(convo("C1", day=0, text=FIRES_ONCE))
    assert first.extracted == 1 and first.written == 1
    assert not first.crossed, "the fixture crosses on one conversation; nothing below is testable"
    assert not sqs.sent

    second = ingestor.ingest(convo("C2", day=10, text=FIRES_AGAIN))
    assert second.score > first.score, (
        "the second conversation scored as if the first had been discarded -- this is the "
        "never-discard inversion the entry rests on"
    )
    assert len(LedgerStore("t", table=table).load("CUST-1")) == 2


def test_two_conversations_cross_where_neither_alone_would() -> None:
    """Accumulation, on the deployed path. The cut sits above either conversation on its own
    (0.270 and 0.146) and below the two together (0.459) — so a crossing here is the accumulation
    doing work, not one loud call."""
    threshold = 0.35
    alone, _, _ = build(threshold=threshold)
    assert not alone.ingest(convo("C2", day=10, text=FIRES_AGAIN)).crossed, (
        "the second conversation crosses on its own; this test would prove nothing"
    )

    ingestor, _, sqs = build(threshold=threshold)
    first = ingestor.ingest(convo("C1", day=0, text=FIRES_ONCE))
    assert not first.crossed and first.score < threshold

    second = ingestor.ingest(convo("C2", day=10, text=FIRES_AGAIN))
    assert second.crossed and second.enqueued
    assert len(sqs.sent) == 1


def test_the_online_score_is_memory_pys_score_not_a_second_one() -> None:
    """The one thing this architecture forbids is a second scorer on the deployed path. The
    handler's number must equal an ordinary in-memory `SignalLedger` over the same signals."""
    ingestor, table, _ = build(threshold=0.9)
    ingestor.ingest(convo("C1", day=0, text=FIRES_ONCE))
    result = ingestor.ingest(convo("C2", day=10, text=FIRES_AGAIN))

    local = SignalLedger(ScoringConfig())
    local.extend(LedgerStore("t", table=table).load("CUST-1"))
    assert result.score == local.best("CUST-1", result.as_of_day).score
    assert result.signal_type == local.best("CUST-1", result.as_of_day).signal_type.value


def test_an_out_of_order_conversation_does_not_age_evidence_that_has_not_aged() -> None:
    """Scoring as of the message's own day would decay the ledger back to an earlier date."""
    ingestor, _, _ = build(threshold=0.9)
    ingestor.ingest(convo("C2", day=100, text=FIRES_ONCE))
    late_arrival = ingestor.ingest(convo("C1", day=5, text=FIRES_AGAIN))
    assert late_arrival.as_of_day == 100


# ---- idempotency: SQS delivers at least once -----------------------------------------------------


def test_redelivery_of_the_same_conversation_changes_nothing() -> None:
    ingestor, table, _ = build(threshold=0.9)
    first = ingestor.ingest(convo("C1", day=0, text=FIRES_ONCE))
    again = ingestor.ingest(convo("C1", day=0, text=FIRES_ONCE))

    assert first.written == 1 and first.duplicates == 0
    assert again.written == 0 and again.duplicates == 1, (
        "a redelivered conversation was written twice -- the conditional append is not holding"
    )
    assert again.score == first.score
    assert len(LedgerStore("t", table=table).load("CUST-1")) == 1


def test_the_enqueued_message_carries_the_crossing_and_not_the_evidence() -> None:
    """The investigate handler reloads the ledger itself, so a chain on the wire would be a
    second, staler copy of the same truth -- and quotes on a queue are customer speech in a place
    nothing audits."""
    ingestor, _, sqs = build(threshold=0.1)
    ingestor.ingest(convo("C1", day=0, text=FIRES_ONCE))

    body = json.loads(sqs.sent[0]["MessageBody"])
    assert set(body) == {
        "customer_id",
        "signal_type",
        "score",
        "threshold",
        "as_of_day",
        "triggered_by_conversation",
    }
    assert "evidence" not in body and "quote" not in json.dumps(body)


def test_no_queue_configured_means_no_enqueue_not_a_crash() -> None:
    """A stage without an investigations queue still ingests and still re-scores; it just cannot
    escalate. That is a degraded mode, not a failure."""
    ingestor = Ingestor(
        OfflineLexiconExtractor(), LedgerStore("t", table=FakeTable()), threshold=0.1
    )
    result = ingestor.ingest(convo("C1", day=0, text=FIRES_ONCE))
    assert result.crossed and not result.enqueued


def test_a_conversation_with_nothing_in_it_is_not_an_error() -> None:
    ingestor, _, sqs = build()
    result = ingestor.ingest(convo("C1", day=0, text="thanks very much, that is all sorted"))
    assert result.extracted == 0 and result.score == 0.0
    assert result.signal_type is None and not result.crossed and not sqs.sent


# ---- the Lambda entrypoint ------------------------------------------------------------------------


def _sqs_event(*bodies: tuple[str, str]) -> dict:
    return {"Records": [{"messageId": mid, "body": body} for mid, body in bodies]}


def _transcript(conversation_id: str, day: int, text: str) -> str:
    return json.dumps(
        {
            "conversation_id": conversation_id,
            "customer_id": "CUST-1",
            "channel": "call",
            "day": day,
            "turns": [{"index": 0, "speaker": "customer", "text": text}],
        }
    )


@pytest.fixture
def wired(monkeypatch):
    """`handler` against an injected ingestor. The module caches one per container, so the cache
    is what a test has to replace -- and it is reset afterwards so no test leaks into the next."""
    ingestor, table, sqs = build(threshold=0.1)
    monkeypatch.setattr(ingest_mod, "_INGESTOR", ingestor)
    return ingestor, table, sqs


def test_one_poison_record_fails_alone(wired, capsys) -> None:
    """Raising instead would redeliver the whole batch and re-run every extraction in it -- with a
    model reader, real money spent to punish one malformed neighbour."""
    _, table, _ = wired
    response = handler(
        _sqs_event(
            ("good-1", _transcript("C1", 0, FIRES_ONCE)),
            ("poison", "{not json"),
            ("good-2", _transcript("C2", 10, FIRES_AGAIN)),
        )
    )

    assert response == {"batchItemFailures": [{"itemIdentifier": "poison"}]}
    assert len(LedgerStore("t", table=table).load("CUST-1")) == 2, (
        "the healthy records in the batch did not commit"
    )
    logged = [json.loads(li) for li in capsys.readouterr().out.splitlines() if li.startswith("{")]
    assert {"ingest.ok", "ingest.failed"} == {li["event"] for li in logged}


def test_a_record_that_is_valid_json_but_not_a_transcript_fails_alone(wired) -> None:
    response = handler(_sqs_event(("bad-shape", json.dumps({"hello": "world"}))))
    assert response == {"batchItemFailures": [{"itemIdentifier": "bad-shape"}]}


def test_an_empty_batch_is_a_no_op(wired) -> None:
    assert handler({"Records": []}) == {"batchItemFailures": []}
