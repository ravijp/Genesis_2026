"""The four arms of the experiment (BUILD-PLAN §3.1).

v1 compared two arms and the eval review judged it circular and unfair. The ladder is now:

  1. stateless-max    -- each conversation scored alone; customer score = running max.
                         Stated honestly: ANY customer-level score implies an aggregator, so
                         even this arm has a trivial memory. There is no such thing as a truly
                         stateless customer-level baseline, and pretending otherwise is a
                         strawman.
  2. dumb-ledger      -- unweighted count of signals. No decay, no corroboration, no channel
                         weighting, no confidence weighting. THIS IS THE HONEST ARM: if it ties
                         the full ledger, every mechanism in memory.py is decoration and the
                         technical-depth claim is unearned. Better to learn that here than on
                         stage.
  3. long-context-N   -- the last N conversations pooled and read together, with no accumulation
                         math. This approximates dropping N transcripts into one long prompt,
                         which is the alternative a judge will actually raise. APPROXIMATION,
                         stated: with a real model this arm would re-read raw text; here it
                         pools the same extracted signals without decay or corroboration. It
                         flatters the ledger slightly less than a real long-context run would
                         on short histories, and slightly more on long ones.
  4. full-ledger      -- decay + corroboration + cross-channel + escalation + retro re-scoring.

Every arm runs through the SAME SignalLedger code path with a different ScoringConfig, so the
ablation is structurally fair rather than fair-by-assertion.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .config import ScoringConfig
from .memory import SignalLedger
from .schema import ExtractedSignal, SignalType

LONG_CONTEXT_WINDOW = 10


@dataclass
class ArmTimeline:
    """Per-customer score trajectory: the running score after each signal-bearing conversation."""

    customer_id: str
    points: list[tuple[int, float]] = field(default_factory=list)  # (day, score)

    def final(self) -> float:
        return max((s for _, s in self.points), default=0.0)

    def first_crossing(self, threshold: float) -> int | None:
        for day, score in sorted(self.points):
            if score >= threshold:
                return day
        return None


@dataclass
class ArmResult:
    arm: str
    timelines: dict[str, ArmTimeline]

    def scores(self) -> dict[str, float]:
        return {cid: t.final() for cid, t in self.timelines.items()}


def _stateless_config(base: ScoringConfig) -> ScoringConfig:
    return replace(
        base,
        decay_enabled=False,
        corroboration_enabled=False,
        cross_channel_enabled=False,
        escalation_enabled=False,
    )


def _dumb_config(base: ScoringConfig) -> ScoringConfig:
    return replace(
        base,
        decay_enabled=False,
        corroboration_enabled=False,
        cross_channel_enabled=False,
        escalation_enabled=False,
        confidence_weighting=False,
    )


def _run(
    signals: list[ExtractedSignal],
    cfg: ScoringConfig,
    *,
    window: int | None = None,
    per_conversation: bool = False,
) -> dict[str, ArmTimeline]:
    by_customer: dict[str, list[ExtractedSignal]] = {}
    for s in signals:
        by_customer.setdefault(s.customer_id, []).append(s)

    timelines: dict[str, ArmTimeline] = {}
    for customer_id, sigs in by_customer.items():
        timeline = ArmTimeline(customer_id)
        days = sorted({s.day for s in sigs})
        for day in days:
            visible = [s for s in sigs if s.day <= day]
            if window is not None:
                recent_conversations = sorted({s.conversation_id for s in visible})[-window:]
                visible = [s for s in visible if s.conversation_id in set(recent_conversations)]

            best = 0.0
            types = {s.signal_type for s in visible}
            for signal_type in sorted(types, key=lambda t: t.value):
                subset = [s for s in visible if s.signal_type is signal_type]
                if per_conversation:
                    # Score each conversation independently, then take the max -- the
                    # "score it and archive it" behaviour we are ablating against.
                    for conversation_id in sorted({s.conversation_id for s in subset}):
                        one = [s for s in subset if s.conversation_id == conversation_id]
                        ledger = SignalLedger(cfg)
                        ledger.extend(one)
                        best = max(best, ledger.score(customer_id, signal_type, one[0].day).score)
                else:
                    ledger = SignalLedger(cfg)
                    ledger.extend(subset)
                    best = max(best, ledger.score(customer_id, signal_type, day).score)
            timeline.points.append((day, best))
        timelines[customer_id] = timeline
    return timelines


def _hybrid(
    stateless: dict[str, ArmTimeline], ledger: dict[str, ArmTimeline]
) -> dict[str, ArmTimeline]:
    """Commodity per-call detection OR accumulation — whichever fires first.

    This is the arm the first 400-customer run argued for, and it is what the submission
    actually describes: "It adds a memory on top of tools banks already run, rather than
    replacing them." Running the ledger *instead of* per-call detection loses concentrated
    arcs (one loud conversation), because accumulation dilutes a single decisive signal.
    Running it *alongside* keeps both. Replacing the incumbent was never the pitch.

    Combined on RANK, not on raw score. A first attempt took `max()` of the two raw scores and
    came back byte-identical to the ledger arm: the ledger's saturation puts its scores
    uniformly above the stateless arm's, so the max was never the stateless one. The two arms
    are not on a common scale — the same incommensurability that makes a shared threshold
    unfair. Mapping each arm's score to its percentile *within that arm* fixes it, and is the
    cheap stand-in for the dev-split probability calibration in BUILD-PLAN §3.2.
    """

    def percentiler(timelines: dict[str, ArmTimeline]):
        finals = sorted(t.final() for t in timelines.values())

        def pct(score: float) -> float:
            if not finals or score <= 0:
                return 0.0
            lo, hi = 0, len(finals)
            while lo < hi:  # count of finals strictly below `score`
                mid = (lo + hi) // 2
                if finals[mid] < score:
                    lo = mid + 1
                else:
                    hi = mid
            return lo / len(finals)

        return pct

    pct_stateless = percentiler(stateless)
    pct_ledger = percentiler(ledger)

    out: dict[str, ArmTimeline] = {}
    for customer_id in set(stateless) | set(ledger):
        a = dict(stateless.get(customer_id, ArmTimeline(customer_id)).points)
        b = dict(ledger.get(customer_id, ArmTimeline(customer_id)).points)
        days = sorted(set(a) | set(b))
        out[customer_id] = ArmTimeline(
            customer_id,
            [
                (d, max(pct_stateless(a.get(d, 0.0)), pct_ledger(b.get(d, 0.0))))
                for d in days
            ],
        )
    return out


def run_all_arms(
    signals: list[ExtractedSignal], cfg: ScoringConfig | None = None
) -> dict[str, ArmResult]:
    base = cfg or ScoringConfig()
    stateless = _run(signals, _stateless_config(base), per_conversation=True)
    full = _run(signals, base)
    return {
        "stateless-max": ArmResult("stateless-max", stateless),
        "dumb-ledger": ArmResult("dumb-ledger", _run(signals, _dumb_config(base))),
        f"long-context-{LONG_CONTEXT_WINDOW}": ArmResult(
            f"long-context-{LONG_CONTEXT_WINDOW}",
            _run(signals, _stateless_config(base), window=LONG_CONTEXT_WINDOW),
        ),
        "full-ledger": ArmResult("full-ledger", full),
        "hybrid": ArmResult("hybrid", _hybrid(stateless, full)),
    }


def mechanism_ablations(
    signals: list[ExtractedSignal], cfg: ScoringConfig | None = None
) -> dict[str, ArmResult]:
    """Each mechanism switched off one at a time, against the full ledger.

    Answers "which of these actually earns its place" -- and BUILD-PLAN §7 says cross-channel
    and escalation only survive to the demo if this says they do.
    """
    base = cfg or ScoringConfig()
    variants = {
        "no-decay": replace(base, decay_enabled=False),
        "no-corroboration": replace(base, corroboration_enabled=False),
        "no-cross-channel": replace(base, cross_channel_enabled=False),
        "no-escalation": replace(base, escalation_enabled=False),
        "no-confidence-weighting": replace(base, confidence_weighting=False),
    }
    return {name: ArmResult(name, _run(signals, variant)) for name, variant in variants.items()}


def demo_ledger(signals: list[ExtractedSignal], cfg: ScoringConfig | None = None) -> SignalLedger:
    """A fully-populated ledger for narrating a single customer on screen."""
    ledger = SignalLedger(cfg or ScoringConfig())
    ledger.extend(signals)
    return ledger


__all__ = [
    "ArmResult",
    "ArmTimeline",
    "LONG_CONTEXT_WINDOW",
    "SignalType",
    "demo_ledger",
    "mechanism_ablations",
    "run_all_arms",
]
