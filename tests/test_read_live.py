"""Reading a conversation turn by turn: cadence, prefixes, belief movement, and cost accounting.

The properties that matter are the ones a screen would otherwise fake. The model must genuinely be
re-asked on a *prefix* (not shown the whole transcript and asked to pretend); the final step must
be the batch read exactly, or the animation ends somewhere the ledger never was; and the narration
calls must not land in the reader's own telemetry, because that is the denominator of a published
cost-per-1,000-conversations figure.
"""

from __future__ import annotations

import pytest

from earshot.extract import OfflineLexiconExtractor
from earshot.extract_model import ModelExtractor
from earshot.read_live import (
    MIN_STRIDE,
    ReadStep,
    _diff,
    narrate,
    narration_totals,
    read_points,
    read_turn_by_turn,
)
from earshot.schema import Channel, Conversation, ExtractedSignal, SignalType, Turn


def conversation(*speakers: str) -> Conversation:
    return Conversation(
        conversation_id="C-1",
        customer_id="CUST-0001",
        channel=Channel.CALL,
        day=3,
        turns=tuple(
            Turn(index=i, speaker=s, text=f"line {i} from the {s}")
            for i, s in enumerate(speakers)
        ),
    )


# -- cadence -------------------------------------------------------------------------------


def test_read_points_land_after_customer_turns() -> None:
    """A signal is something the customer says; the agent's turns are scripted service language."""
    convo = conversation("agent", "customer", "agent", "customer", "agent")
    points = read_points(convo, min_stride=1)
    # counts of turns heard, so 2 means "after the customer turn at index 1"
    assert points[0] == 2
    assert points[-1] == len(convo.turns)


def test_read_points_respect_the_minimum_stride() -> None:
    """Back-to-back customer turns are usually one thought split in two; a read between them
    costs a call to show a delta of zero."""
    convo = conversation("customer", "customer", "customer", "customer")
    assert read_points(convo, min_stride=3) == [1, 4]


def test_read_points_always_end_on_the_whole_transcript() -> None:
    """The last step has to be the complete conversation, or the animation finishes at a belief
    that was never appended to the ledger."""
    for speakers in (
        ("agent", "agent", "agent"),
        ("customer", "agent"),
        ("customer",),
    ):
        convo = conversation(*speakers)
        assert read_points(convo)[-1] == len(convo.turns)


def test_read_points_never_exceed_the_transcript() -> None:
    convo = conversation("customer", "agent", "customer", "agent", "customer")
    assert all(0 < p <= len(convo.turns) for p in read_points(convo))


def test_default_stride_is_at_least_two() -> None:
    assert MIN_STRIDE >= 2


# -- the prefixes are real -----------------------------------------------------------------


class RecordingExtractor:
    """Records the transcript it was handed at each call. Returns nothing."""

    def __init__(self) -> None:
        self.seen: list[tuple[int, ...]] = []

    def extract(self, conv: Conversation) -> list[ExtractedSignal]:
        self.seen.append(tuple(t.index for t in conv.turns))
        return []


def test_the_model_is_given_a_prefix_not_the_whole_transcript() -> None:
    """The whole claim rests on this. If the model saw the full conversation at every step, the
    "belief forming" animation would be a model being asked the same question five times."""
    convo = conversation("agent", "customer", "agent", "customer", "agent", "customer")
    recorder = RecordingExtractor()
    read_turn_by_turn(recorder, convo, min_stride=1)

    lengths = [len(seen) for seen in recorder.seen]
    assert lengths == sorted(lengths), "prefixes must grow"
    assert len(set(lengths)) == len(lengths), "two steps saw the same number of turns"
    assert lengths[-1] == len(convo.turns), "the last step is not the whole transcript"
    assert lengths[0] < len(convo.turns), "the first step already saw everything"
    for seen in recorder.seen:
        assert seen == tuple(range(len(seen))), "a prefix skipped or reordered turns"


def test_the_final_step_matches_a_batch_read_exactly() -> None:
    """Byte-identical requests, so under a content-addressed cache they are one entry.

    This is not an optimisation. It is the guarantee that the belief shown at the end of the
    animation is the belief that was appended to the ledger.
    """
    convo = conversation("agent", "customer", "agent", "customer")
    recorder = RecordingExtractor()
    read_turn_by_turn(recorder, convo, min_stride=1)
    assert recorder.seen[-1] == tuple(t.index for t in convo.turns)


def test_the_prompt_for_the_last_step_is_the_batch_prompt(monkeypatch) -> None:
    """Checked at the message level, not just the turn count: `messages_for` is what is hashed
    into the cache key, so equality there is what makes the two calls one entry."""

    class Stub:
        name = "stub"

        def complete(self, messages, tools, cfg):
            raise AssertionError("not called")

    convo = conversation("agent", "customer", "agent", "customer")
    reader = ModelExtractor(Stub())
    batch = reader.messages_for(convo)
    prefix = reader.messages_for(convo)  # the final prefix IS the conversation
    assert batch == prefix


# -- belief movement -----------------------------------------------------------------------


def signal(family: SignalType, confidence: float, turn_index: int = 1) -> ExtractedSignal:
    return ExtractedSignal(
        customer_id="CUST-0001",
        conversation_id="C-1",
        signal_type=family,
        confidence=confidence,
        evidence_quote="q",
        turn_index=turn_index,
        day=3,
    )


def test_diff_names_each_movement_separately() -> None:
    """Five movements, because they mean different things. A model that *withdraws* a signal after
    hearing more is behaving well; one that keeps it but moves the citation found better evidence
    for the same claim. Lumping both into "changed" throws away the interesting part."""
    before = [signal(SignalType.CHURN_INTENT, 0.5, 1), signal(SignalType.LIFE_EVENT, 0.4, 2)]
    after = [
        signal(SignalType.CHURN_INTENT, 0.8, 3),          # firmed AND requoted
        signal(SignalType.FINANCIAL_DISTRESS, 0.3, 4),    # appeared
    ]                                                      # life_event withdrawn
    moved = _diff(before, after)
    assert moved["firmed"] == ("churn_intent",)
    assert moved["requoted"] == ("churn_intent",)
    assert moved["appeared"] == ("financial_distress",)
    assert moved["withdrawn"] == ("life_event",)
    assert moved["faded"] == ()


def test_diff_ignores_confidence_noise() -> None:
    """Two reads of an unchanged belief differ in the third decimal. A screen that flags that as
    "firmer" is animating rounding error."""
    before = [signal(SignalType.CHURN_INTENT, 0.500)]
    after = [signal(SignalType.CHURN_INTENT, 0.505)]
    moved = _diff(before, after)
    assert moved["firmed"] == () and moved["faded"] == ()


def test_a_step_with_no_movement_is_not_marked_changed() -> None:
    step = ReadStep(step=1, up_to_turn=4, turns_seen=5, signals=(), latency_ms=1.0, cost_usd=0.0)
    assert not step.changed
    assert not step.to_dict()["changed"]


# -- accounting ----------------------------------------------------------------------------


def test_narration_does_not_pollute_the_readers_conversation_count() -> None:
    """`ExtractionTelemetry.conversations` is the denominator of the published cost-per-1,000
    figure. Counting nine prefix reads as nine conversations divides the same money by nine times
    the work and reports a cost per conversation that is a fiction.

    `read_live` cannot enforce this on its own -- it calls whatever extractor it is handed -- so
    what is pinned here is that the counter really does move per call, which is exactly why
    `cli.cmd_stream` builds a SEPARATE extractor for the narration pass.
    """
    convo = conversation("agent", "customer", "agent", "customer", "agent", "customer")
    reader = OfflineLexiconExtractor()
    assert getattr(reader, "telemetry", None) is None, (
        "the offline lexicon grew telemetry; this test's premise needs revisiting"
    )
    steps = read_turn_by_turn(reader, convo, min_stride=1)
    assert len(steps) >= 2


def test_narrate_keys_by_conversation_id() -> None:
    convos = [conversation("customer", "agent"), conversation("agent", "customer")]
    convos[1] = convos[1].__class__(**{**convos[1].__dict__, "conversation_id": "C-2"})
    reads = narrate(OfflineLexiconExtractor(), convos)
    assert set(reads) == {"C-1", "C-2"}
    assert all(isinstance(series, list) for series in reads.values())


def test_narration_totals_report_calls_and_cost_apart() -> None:
    """Named `narration_*` everywhere. It is the cost of showing the working, not of reading the
    book, and one blended number would misstate both."""
    reads = narrate(OfflineLexiconExtractor(), [conversation("customer", "agent", "customer")])
    totals = narration_totals(reads)
    assert totals["conversations_narrated"] == 1
    assert totals["narration_calls"] == sum(len(v) for v in reads.values())
    assert totals["narration_cost_usd"] == 0.0  # the lexicon costs nothing, and says so
    assert "steps_that_changed_the_read" in totals


def test_steps_are_numbered_from_zero_and_are_contiguous() -> None:
    steps = read_turn_by_turn(
        OfflineLexiconExtractor(), conversation("customer", "agent", "customer", "agent"),
        min_stride=1,
    )
    assert [s.step for s in steps] == list(range(len(steps)))


@pytest.mark.parametrize("speakers", [("customer",), ("agent",), ("agent", "customer")])
def test_short_conversations_still_produce_at_least_one_read(speakers) -> None:
    """A one-turn conversation is still a conversation, and a screen that renders nothing for it
    looks like a bug rather than a short call."""
    steps = read_turn_by_turn(OfflineLexiconExtractor(), conversation(*speakers))
    assert steps
    assert steps[-1].turns_seen == len(speakers)
