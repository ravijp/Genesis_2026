"""The end-to-end feeder, and the two ways it could lie.

`tools/feed.py` publishes a tenant's book to the deployed FIFO queue and then asserts the result
against the local pipeline. Two failure modes make it worse than useless:

1. **It could put the answer key on the wire.** `predict()` needs `cli.stream_inputs`, so this
   process holds the corpus. `wire_payload()` is the boundary.
2. **It could report success regardless.** A verifier that cannot fail is the `timeout ... | tail`
   mistake again (`docs/ops/handover.md`): a wrapper that hid an exit code turned a truncated run
   into a clean one, twice. So every `verify()` branch is tested for the failing direction, not
   just the passing one.

Nothing here touches AWS. The prediction runs the real generator, the real lexicon and the real
`SignalLedger`, because that is exactly what it must agree with.
"""

from __future__ import annotations

import json

import feed
import pytest

from earshot.aws.ingest import DEFAULT_THRESHOLD
from earshot.cli import stream_inputs
from earshot.schema import Channel, Conversation, Turn
from earshot.tenants import NORTHWIND

# Every field any ground-truth object carries that must never reach a queue. Named here rather
# than imported so this test keeps failing if someone renames one and misses a call site.
ANSWER_KEY_FIELDS = ("stratum", "outcome", "latent_risk", "trajectory", "planted", "financial_state")


@pytest.fixture(scope="module")
def conversations() -> list[Conversation]:
    convs, _context_for, _account_for = stream_inputs(NORTHWIND)
    return list(convs)


def _conversation(**overrides) -> Conversation:
    base = {
        "conversation_id": "C-1",
        "customer_id": "CUST-0001",
        "channel": Channel.CHAT,
        "day": 3,
        "turns": (Turn(index=0, speaker="customer", text="hello"),),
    }
    return Conversation(**{**base, **overrides})


# ---- the wire is the boundary ---------------------------------------------------------------


def test_the_payload_carries_exactly_the_fields_the_parser_requires() -> None:
    """More would be a leak; fewer is a `TranscriptError` on the deployed side."""
    assert set(feed.wire_payload(_conversation())) == feed.WIRE_KEYS


def test_no_answer_key_field_reaches_the_wire(conversations) -> None:
    """The real corpus, not a fixture: the generator's conversations are the ones that would carry
    a leaked field, and a hand-built object would prove nothing about them."""
    for conversation in conversations[:40]:
        payload = feed.wire_payload(conversation)
        flat = repr(payload)
        for banned in ANSWER_KEY_FIELDS:
            assert banned not in payload, f"{banned} is a key on the wire"
            assert f"'{banned}'" not in flat, f"{banned} appears nested in the payload"


def test_the_payload_survives_the_deployed_parser_unchanged(conversations) -> None:
    """Round-trip through the real `parse_conversation`. A lost turn index breaks every evidence
    citation, which resolves by (conversation_id, turn_index)."""
    from earshot.aws.transcripts import parse_conversation

    for conversation in conversations[:25]:
        parsed = parse_conversation(feed.wire_payload(conversation))
        assert parsed.conversation_id == conversation.conversation_id
        assert parsed.customer_id == conversation.customer_id
        assert parsed.day == conversation.day
        assert parsed.channel == conversation.channel
        assert [(t.index, t.speaker, t.text) for t in parsed.turns] == [
            (t.index, t.speaker, t.text) for t in conversation.turns
        ]


# ---- ordering, which the whole claim depends on ---------------------------------------------


def test_each_customers_conversations_are_grouped_in_day_order(conversations) -> None:
    """Accumulation is order-dependent: a signal must be on the ledger before a later
    conversation can be re-scored against it."""
    grouped = feed.by_customer(conversations)
    assert grouped, "no customers grouped"
    for customer_id, convs in grouped.items():
        days = [c.day for c in convs]
        assert days == sorted(days), f"{customer_id} is out of day order"
        assert {c.customer_id for c in convs} == {customer_id}
    assert sum(len(v) for v in grouped.values()) == len(conversations)


def test_no_customer_exceeds_the_sqs_batch_limit(conversations) -> None:
    """`send()` puts one customer in one batch, and SQS caps a batch at 10. A tenant tuned to
    more conversations per customer must fail loudly there, so this is the early warning."""
    for customer_id, convs in feed.by_customer(conversations).items():
        assert len(convs) <= 10, f"{customer_id} has {len(convs)} conversations; batch max is 10"


# ---- the prediction -------------------------------------------------------------------------


def test_the_prediction_counts_every_conversation_and_customer(conversations) -> None:
    prediction = feed.predict(conversations, DEFAULT_THRESHOLD)
    assert prediction.conversations == len(conversations)
    assert prediction.customers == len(feed.by_customer(conversations))


def test_a_crossing_scores_at_or_above_the_threshold(conversations) -> None:
    prediction = feed.predict(conversations, DEFAULT_THRESHOLD)
    for _customer, _conversation, score, _signal_type, _as_of in prediction.enqueues:
        assert score >= DEFAULT_THRESHOLD


def test_one_case_per_crossing_customer_not_per_crossing() -> None:
    """`case_record.make_case_id` keys on the first crossing day, so a customer who crosses again
    overwrites one case rather than adding one."""
    prediction = feed.Prediction()
    prediction.enqueues = [
        ("CUST-1", "C-1", 0.7, "financial_distress", 10),
        ("CUST-1", "C-2", 0.8, "financial_distress", 20),
        ("CUST-2", "C-3", 0.9, "complaint_risk", 30),
    ]
    assert len(prediction.enqueues) == 3
    assert prediction.cases == 2
    assert prediction.crossing_customers == {"CUST-1", "CUST-2"}


def test_an_unreachable_threshold_predicts_no_crossings(conversations) -> None:
    """Guards against a prediction that always finds something, which would agree with a broken
    deployment as readily as a working one."""
    assert feed.predict(conversations, 1.01).enqueues == []


def test_lowering_the_threshold_can_only_add_crossing_customers(conversations) -> None:
    """Monotonicity. Note it is *customers* that behave monotonically, not enqueues: at threshold
    0.0 a customer with any signal re-crosses on every later conversation, so the enqueue count
    can exceed the ledger-write count. That is the handler's documented behaviour -- a crossing
    that stays crossed re-investigates -- and not a miscount."""
    low = feed.predict(conversations, 0.0)
    high = feed.predict(conversations, DEFAULT_THRESHOLD)
    assert low.enqueues, "no crossings at threshold 0.0, so the extractor found nothing"
    assert high.crossing_customers <= low.crossing_customers
    assert low.ledger_writes == high.ledger_writes, "the threshold must not change what is written"


def test_every_crossing_customer_has_at_least_one_ledger_write(conversations) -> None:
    """A crossing with no evidence behind it would mean `best()` scored an empty chain."""
    low = feed.predict(conversations, 0.0)
    assert len(low.crossing_customers) <= low.ledger_writes


# ---- the verifier must be able to fail ------------------------------------------------------


def _state(**overrides) -> dict:
    prediction = feed.Prediction(conversations=130, customers=44, ledger_writes=34)
    prediction.enqueues = [("CUST-0006", "CUST-0006-C3", 0.652662, "financial_distress", 94)]
    base = {
        "drained": True,
        "dlq": 0,
        "ledger": 34,
        "cases": 1,
        "api": {"status": 200, "body": {"cases": [{"customer_id": "CUST-0006"}]}},
        "prediction": prediction,
    }
    return {**base, **overrides}


def test_a_matching_deployment_produces_no_findings() -> None:
    assert feed.verify(_state()) == []


@pytest.mark.parametrize(
    ("override", "expected"),
    [
        ({"ledger": 33}, "ledger holds 33"),
        ({"cases": 0}, "cases table holds 0"),
        ({"dlq": 2}, "2 message(s) on the DLQ"),
        ({"drained": False}, "did not drain"),
        ({"api": None}, "did not answer"),
        ({"api": {"status": 500, "body": {}}}, "returned 500"),
        ({"api": {"status": 200, "body": {"cases": []}}}, "served 0 case(s)"),
        (
            {"api": {"status": 200, "body": {"cases": [{"customer_id": "CUST-9999"}]}}},
            "absent from GET /cases",
        ),
    ],
)
def test_every_disagreement_is_reported(override: dict, expected: str) -> None:
    """One parametrised case per branch of `verify()`. A verifier with an unreachable failure
    branch is indistinguishable from one that always passes."""
    failures = feed.verify(_state(**override))
    assert failures, f"{override} produced no finding"
    assert any(expected in f for f in failures), failures


def test_an_unreadable_table_is_not_silently_treated_as_a_match() -> None:
    """`_count` returns None when the scan fails. That must not read as agreement -- but it also
    must not invent a count, so the honest behaviour is to skip that check and let the API and
    drain checks carry the verdict."""
    failures = feed.verify(_state(ledger=None, cases=None))
    assert failures == [], "the API and drain checks still passed, so there is nothing to report"
    failures = feed.verify(_state(ledger=None, cases=None, api={"status": 500, "body": {}}))
    assert any("returned 500" in f for f in failures)


# ---- the failure path ------------------------------------------------------------------------


def test_a_poison_payload_is_rejected_by_the_deployed_parser() -> None:
    """`--poison` is only a useful alarm test if the payload really does fail, and fails at the
    parse step -- before anything is archived or written to the ledger."""
    from earshot.aws.transcripts import TranscriptError, parse_conversation

    sent: list[dict] = []

    class Recorder:
        def send_message_batch(self, **kw):
            sent.extend(kw["Entries"])
            return {"Successful": kw["Entries"], "Failed": []}

    feed.send_poison(Recorder(), "https://sqs.test/q", 2, dry_run=False)
    assert len(sent) == 2
    for entry in sent:
        with pytest.raises(TranscriptError):
            parse_conversation(json.loads(entry["MessageBody"]))


def test_poison_never_borrows_a_real_customers_message_group() -> None:
    """A FIFO group is ordered, so a poison message blocks its own group until it is set aside.
    On a real customer's group that stalls their whole stream for the length of the retries."""
    sent: list[dict] = []

    class Recorder:
        def send_message_batch(self, **kw):
            sent.extend(kw["Entries"])
            return {"Successful": kw["Entries"], "Failed": []}

    feed.send_poison(Recorder(), "https://sqs.test/q", 3, dry_run=False)
    groups = {e["MessageGroupId"] for e in sent}
    assert len(groups) == 1
    group = groups.pop()
    assert group.startswith("POISON-TEST-")
    assert not group.startswith("CUST-")
    # Distinct dedup ids, or SQS collapses the batch into one message and the test proves nothing.
    assert len({e["MessageDeduplicationId"] for e in sent}) == 3


def test_a_poison_dry_run_publishes_nothing() -> None:
    class Exploding:
        def send_message_batch(self, **kw):
            raise AssertionError("a dry run must not publish")

    assert feed.send_poison(Exploding(), "https://sqs.test/q", 1, dry_run=True) == 1
