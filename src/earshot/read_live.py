"""Reading a conversation **as it happens**: the model called again at each customer turn.

**What this is for.** `extract_model.ModelExtractor` reads a finished transcript in one call. That
is right for the ledger and wrong for a demo, because it hides the thing worth seeing: a belief
forming. A reader that has heard six turns thinks nothing is wrong. Three turns later it reports
financial distress at 0.55. By the end it is at 0.78 and has moved its citation to a better line.
That sequence is the product working, and one call per conversation makes it invisible.

**The cadence is customer turns, because that is where signals live.** The agent's turns are
scripted service language; a signal is something the *customer* says. So the model is re-asked
after each customer turn, never closer together than `MIN_STRIDE` turns, and always once at the
end. A 17-turn conversation with nine customer turns costs about nine calls -- but each prefix is
shorter than the whole, so it is well under nine times a single read, and `narration_cost_usd`
reports what it actually was rather than a multiple.

**The last step is the batch read, exactly.** The final prefix is the whole transcript, so its
request is byte-identical to what `ModelExtractor.extract()` would send. Under a content-addressed
cache the two are the same entry: whichever runs first pays and the other is free. That is not an
optimisation, it is the guarantee that **narration cannot disagree with the ledger** -- the belief
shown at the end of the animation is the belief that was appended.

**Narration telemetry is kept apart from the reader's, deliberately.** `ExtractionTelemetry
.conversations` is the denominator of the published cost-per-1,000-conversations figure. Counting
nine prefix reads as nine conversations would divide the same money by nine times the work and
report a cost per conversation that is a fiction. So a narration pass takes its **own** extractor
instance and its own counters, and the two numbers are reported side by side and named apart.

**It never touches the ledger.** Nothing here appends, scores or thresholds. It produces a
sequence of beliefs for a screen to animate; `stream.py` feeds the ledger from the reader, as
before.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Any

from .extract import Extractor
from .schema import Conversation, ExtractedSignal

# Never re-ask the model on two consecutive turns. Back-to-back customer turns are usually one
# thought split across two lines, and a read between them costs a call to show a delta of zero.
MIN_STRIDE = 2

# The speaker whose words can carry a signal. The prompt already says a family belongs to the
# customer's own situation and never to the agent asking about it; this picks the read points to
# match, so the cadence and the prompt agree about where evidence comes from.
CUSTOMER = "customer"

# How much a confidence must move before it is called a change rather than noise. Two reads of an
# unchanged belief can differ in the third decimal, and a screen that flags that as "firmer" is
# animating rounding error.
CONFIDENCE_EPSILON = 0.02


@dataclass(frozen=True)
class ReadStep:
    """What the reader believed after hearing the first `turns_seen` turns."""

    step: int
    up_to_turn: int
    turns_seen: int
    signals: tuple[ExtractedSignal, ...]
    latency_ms: float
    cost_usd: float
    # What moved since the previous step, as signal-family names. Computed here rather than in the
    # browser: it is a comparison of two model outputs, and the browser's job is to animate a
    # decision, never to make one.
    appeared: tuple[str, ...] = ()
    firmed: tuple[str, ...] = ()
    faded: tuple[str, ...] = ()
    withdrawn: tuple[str, ...] = ()
    requoted: tuple[str, ...] = ()

    @property
    def changed(self) -> bool:
        return bool(
            self.appeared or self.firmed or self.faded or self.withdrawn or self.requoted
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "up_to_turn": self.up_to_turn,
            "turns_seen": self.turns_seen,
            "signals": [
                {
                    "signal_type": s.signal_type.value,
                    "confidence": round(s.confidence, 3),
                    "turn_index": s.turn_index,
                    "quote": s.evidence_quote,
                }
                for s in self.signals
            ],
            "latency_ms": round(self.latency_ms, 1),
            "cost_usd": round(self.cost_usd, 6),
            "appeared": list(self.appeared),
            "firmed": list(self.firmed),
            "faded": list(self.faded),
            "withdrawn": list(self.withdrawn),
            "requoted": list(self.requoted),
            "changed": self.changed,
        }


def read_points(conversation: Conversation, min_stride: int = MIN_STRIDE) -> list[int]:
    """The turn positions at which to re-ask the model, as counts of turns heard so far.

    After each customer turn, never closer than `min_stride`, and always once at the very end so
    the final step is the whole transcript. Returns counts (1-based lengths), not turn indices,
    because that is what slicing needs and an off-by-one here silently shortens every prefix.
    """
    points: list[int] = []
    for position, turn in enumerate(conversation.turns, start=1):
        if str(turn.speaker).lower() != CUSTOMER:
            continue
        if points and position - points[-1] < min_stride:
            continue
        points.append(position)
    total = len(conversation.turns)
    if not points or points[-1] != total:
        points.append(total)
    return points


def _by_family(signals: Sequence[ExtractedSignal]) -> dict[str, ExtractedSignal]:
    return {s.signal_type.value: s for s in signals}


def _diff(
    previous: Sequence[ExtractedSignal], current: Sequence[ExtractedSignal]
) -> dict[str, tuple[str, ...]]:
    """How the reader's belief moved between two steps, by signal family.

    Five distinct movements, because they mean different things on screen and lumping them into
    "changed" throws away the interesting one. A model that *withdraws* a signal after hearing
    more is behaving well; a model that keeps a signal but moves its citation has found better
    evidence for the same claim. Both are worth showing and neither is a confidence change.
    """
    before, after = _by_family(previous), _by_family(current)
    appeared = tuple(sorted(set(after) - set(before)))
    withdrawn = tuple(sorted(set(before) - set(after)))
    firmed, faded, requoted = [], [], []
    for family in sorted(set(before) & set(after)):
        delta = after[family].confidence - before[family].confidence
        if delta > CONFIDENCE_EPSILON:
            firmed.append(family)
        elif delta < -CONFIDENCE_EPSILON:
            faded.append(family)
        if after[family].turn_index != before[family].turn_index:
            requoted.append(family)
    return {
        "appeared": appeared,
        "withdrawn": withdrawn,
        "firmed": tuple(firmed),
        "faded": tuple(faded),
        "requoted": tuple(requoted),
    }


def read_turn_by_turn(
    extractor: Extractor,
    conversation: Conversation,
    *,
    min_stride: int = MIN_STRIDE,
) -> list[ReadStep]:
    """Call the reader once per read point, on the transcript heard so far.

    The extractor is called through its ordinary `extract()`, on a `Conversation` truncated to the
    prefix -- so the model is given no hint that it is mid-call and cannot behave differently
    because of it. What it sees at step 3 is exactly what it would see if the customer had hung up
    after turn 9.
    """
    steps: list[ReadStep] = []
    previous: tuple[ExtractedSignal, ...] = ()
    spent, elapsed = _telemetry(extractor)

    for step, upto in enumerate(read_points(conversation, min_stride)):
        prefix = replace(conversation, turns=tuple(conversation.turns[:upto]))
        signals = tuple(extractor.extract(prefix))
        spent_after, elapsed_after = _telemetry(extractor)
        movement = _diff(previous, signals)
        steps.append(
            ReadStep(
                step=step,
                up_to_turn=conversation.turns[upto - 1].index,
                turns_seen=upto,
                signals=signals,
                latency_ms=elapsed_after - elapsed,
                cost_usd=spent_after - spent,
                **movement,
            )
        )
        previous = signals
        spent, elapsed = spent_after, elapsed_after
    return steps


def _telemetry(extractor: Extractor) -> tuple[float, float]:
    """`(cost_usd, total_latency_ms)` so far, or zeros for the keyless lexicon.

    Snapshot-and-diff against the reader's own counters rather than a second tally kept here: two
    counters for one quantity is how a screen ends up disagreeing with a manifest.
    """
    telemetry = getattr(extractor, "telemetry", None)
    if telemetry is None:
        return 0.0, 0.0
    return telemetry.cost_usd, sum(telemetry.latencies_ms)


def narrate(
    extractor: Extractor,
    conversations: Sequence[Conversation],
    *,
    min_stride: int = MIN_STRIDE,
) -> dict[str, list[dict[str, Any]]]:
    """Turn-by-turn reads for a chosen handful of conversations, keyed by conversation id.

    A *handful* on purpose. Narrating the whole book multiplies the read cost by the number of
    customer turns for a screen that shows one conversation at a time, and a demo that quietly
    spends nine times its stated figure is the kind of number this repo exists not to publish.
    The caller picks which conversations matter -- in practice the ones that open cases -- and
    `stream_payload` records how many were narrated against how many were not.
    """
    return {
        conversation.conversation_id: [
            step.to_dict() for step in read_turn_by_turn(extractor, conversation, min_stride=min_stride)
        ]
        for conversation in conversations
    }


def narration_totals(reads: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """What the narration pass cost, reported apart from the reader's own figures.

    Named `narration_*` everywhere it appears. It is the cost of *showing the working*, not the
    cost of reading the book, and a single blended number would misstate both.
    """
    steps = [step for series in reads.values() for step in series]
    changes = [step for step in steps if step["changed"]]
    return {
        "conversations_narrated": len(reads),
        "narration_calls": len(steps),
        "narration_cost_usd": round(sum(step["cost_usd"] for step in steps), 6),
        # How often re-asking actually changed the answer. If this is near zero the whole
        # turn-by-turn idea is decoration, and the number that says so is on the screen.
        "steps_that_changed_the_read": len(changes),
    }
