"""The eight comparison arms, and what each one is for.

  1. stateless-max    -- each conversation scored alone; customer score = running max. The
                         incumbent shape: score it and archive it. Stated honestly, ANY
                         customer-level score implies an aggregator, so even this arm has a
                         trivial memory. There is no truly stateless customer-level baseline,
                         and claiming one would be a strawman.
  2. stateless-top2   -- the same per-conversation scores, summed over the two loudest calls
                         instead of the single loudest. The STRONGEST fair per-call baseline:
                         it needs two floats per customer, no ledger, no decay, no retro
                         re-scoring. It exists because "max" alone is a weak opponent on arcs
                         built to have no loud call, so beating it would show only that one
                         number is worse than two. Whatever the ledger claims over this arm is
                         what accumulation actually buys.
  3. stateless-top3   -- as top2, over the three loudest calls. Bounds how much of top2's
                         strength is just "more than one number" rather than the specific two.
  4. windowN-top2     -- only the last N conversations exist, and only the two loudest of those
                         count. Strictly less state than a ledger and the HARDEST opponent it
                         has: at 30 seeds it holds the ledger to a tie on concentrated arcs and
                         beats it on the pre-registered thin-evidence stratum. Shipped rather
                         than described, because an opponent you only describe is one you have
                         not really run.
  5. dumb-ledger      -- unweighted count of signals. No decay, no corroboration, no channel
                         weighting, no confidence weighting. The floor the full ledger has to
                         clear: if it ties the full ledger, every mechanism in memory.py is
                         decoration.
  6. long-context-N   -- the last N conversations pooled and read together, with no
                         accumulation math. Approximates dropping N transcripts into one long
                         prompt, which is the obvious alternative to a ledger. It is an
                         APPROXIMATION: a real long-context run re-reads raw text, whereas
                         this pools the same extracted signals without decay or corroboration.
                         That flatters the ledger slightly less than a real long-context run
                         would on short histories, and slightly more on long ones.
  7. full-ledger      -- decay + corroboration + cross-channel + escalation + retro re-scoring.
  8. hybrid           -- stateless-max OR full-ledger, whichever fires first, combined on rank.
                         A memory added on top of the per-call detection a bank already runs,
                         rather than a replacement for it.

Arms 1-5 run through the SAME SignalLedger code path with a different ScoringConfig, so the
ablation is structurally fair rather than fair-by-assertion. Arms 1 and 2 differ only in how
many per-conversation scores the customer-level number may see.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .config import ScoringConfig
from .memory import SignalLedger
from .schema import ExtractedSignal, SignalType

# Must be smaller than a typical customer's conversation count or the window never binds and
# this arm silently collapses into the confidence-weighted dumb ledger, scoring identically to
# it at every budget. Against `conversations_per_customer = (2, 5)` it binds for roughly one
# customer in six -- enough that the arm is not a copy of another, and a reason to widen the
# corpus rather than to trust this arm as a long-context proxy.
LONG_CONTEXT_WINDOW = 3


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
    top_n: int | None = None,
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
                # Ordered by DAY, not by conversation id. Ids sort lexicographically, so from ten
                # conversations on "C9" sorts above "C10" and the window silently selects the
                # wrong transcripts -- which is invisible at the shipped 2-5 conversations and
                # wrong exactly where we are heading next.
                by_day = sorted({(s.day, s.conversation_id) for s in visible})[-window:]
                recent = {cid for _, cid in by_day}
                visible = [s for s in visible if s.conversation_id in recent]

            best = 0.0
            types = {s.signal_type for s in visible}
            for signal_type in sorted(types, key=lambda t: t.value):
                subset = [s for s in visible if s.signal_type is signal_type]
                if per_conversation:
                    # Score each conversation independently -- the "score it and archive it"
                    # behaviour we are ablating against. `top_n` chooses how many of those
                    # independent scores the customer-level number is allowed to see: 1 is a
                    # running max, 2 keeps the two loudest calls.
                    per_conv: list[float] = []
                    for conversation_id in sorted({s.conversation_id for s in subset}):
                        one = [s for s in subset if s.conversation_id == conversation_id]
                        ledger = SignalLedger(cfg)
                        ledger.extend(one)
                        per_conv.append(ledger.score(customer_id, signal_type, one[0].day).score)
                    if top_n is None:
                        best = max([best, *per_conv])
                    else:
                        best = max(best, sum(sorted(per_conv, reverse=True)[:top_n]))
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

    A memory added on top of the per-call detection a bank already runs. Running the ledger
    *instead of* per-call detection loses concentrated arcs — one loud conversation — because
    accumulation dilutes a single decisive signal. Running it *alongside* keeps both.

    Combined on RANK, not on raw score, because the two arms are not on a common scale: the
    same incommensurability that makes a shared threshold unfair between them. Saturation puts
    the ledger's scores uniformly above the stateless arm's, so a `max()` of raw scores would
    always pick the ledger and the hybrid would be the ledger arm under another name. Mapping
    each arm's score to its percentile *within that arm* is what makes the two comparable, and
    it is a cheap stand-in for dev-split probability calibration, which is not built.
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
        "stateless-top2": ArmResult(
            "stateless-top2",
            _run(signals, _stateless_config(base), per_conversation=True, top_n=2),
        ),
        "stateless-top3": ArmResult(
            "stateless-top3",
            _run(signals, _stateless_config(base), per_conversation=True, top_n=3),
        ),
        # Bounded memory: only the last three conversations exist, and only the two loudest of
        # those count. Strictly less state than a ledger, and the hardest opponent the ledger
        # has -- which is why it is shipped rather than described.
        f"window{LONG_CONTEXT_WINDOW}-top2": ArmResult(
            f"window{LONG_CONTEXT_WINDOW}-top2",
            _run(
                signals,
                _stateless_config(base),
                per_conversation=True,
                top_n=2,
                window=LONG_CONTEXT_WINDOW,
            ),
        ),
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

    Answers "which of these actually earns its place". Cross-channel
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
