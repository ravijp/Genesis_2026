"""The per-customer signal ledger and the re-scorer. Pure code, no model calls.

Two mechanics:

**Never-discard.** Nothing here deletes or supersedes an entry. Customer memory that reconciles
to *current truth* -- new observations overwrite old ones -- is right for personalization and
structurally wrong for risk, because three faint distress signals must sum rather than
overwrite. `append()` is the only mutator and it only ever grows the ledger.

**Retro re-scoring.** Every entry carries what it contributed *when it was written* and what it
contributes *now*. A signal correctly scored "no action" in March is re-read in July:
conversation #3 changes the interpretation of #1 and #2. `retro_delta` is that change, and it
is the thing that goes on screen in the demo.

Contribution is leave-one-out marginal: the score with this entry minus the score without it.
That makes the evidence chain auditable -- a compliance officer can ask what any single quote
was worth, and get a number rather than a vibe.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field, replace

from .config import ScoringConfig
from .schema import Case, ExtractedSignal, LedgerEntry, SignalType


@dataclass
class ScoreBreakdown:
    customer_id: str
    signal_type: SignalType
    score: float
    as_of_day: int
    entries: list[LedgerEntry] = field(default_factory=list)

    def top_evidence(self, n: int = 3) -> list[LedgerEntry]:
        return sorted(self.entries, key=lambda e: -e.contribution_now)[:n]


def _decay(age_days: int, half_life: float, enabled: bool) -> float:
    if not enabled or half_life <= 0:
        return 1.0
    return 0.5 ** (max(0, age_days) / half_life)


def _escalating(signals: list[ExtractedSignal]) -> bool:
    """Accelerating recurrence: the same issue coming back faster than it used to.

    Deliberately distinct from corroboration (which just counts distinct conversations) so the
    per-mechanism ablation can tell them apart.
    """
    days = sorted({s.day for s in signals})
    if len(days) < 3:
        return False
    gaps = [b - a for a, b in zip(days, days[1:])]
    return gaps[-1] < gaps[0]


class SignalLedger:
    """Append-only per-customer signal store."""

    def __init__(self, cfg: ScoringConfig | None = None) -> None:
        self.cfg = cfg or ScoringConfig()
        self._entries: dict[str, list[LedgerEntry]] = defaultdict(list)

    # -- writes ------------------------------------------------------------------
    def append(self, signal: ExtractedSignal) -> LedgerEntry:
        entry = LedgerEntry(signal=signal)
        self._entries[signal.customer_id].append(entry)
        return entry

    def extend(self, signals: list[ExtractedSignal]) -> None:
        for s in sorted(signals, key=lambda s: (s.day, s.conversation_id, s.turn_index)):
            self.append(s)

    # -- reads -------------------------------------------------------------------
    def customers(self) -> list[str]:
        return sorted(self._entries)

    def signals(
        self, customer_id: str, signal_type: SignalType | None = None, as_of_day: int | None = None
    ) -> list[ExtractedSignal]:
        out = [e.signal for e in self._entries.get(customer_id, [])]
        if signal_type is not None:
            out = [s for s in out if s.signal_type is signal_type]
        if as_of_day is not None:
            out = [s for s in out if s.day <= as_of_day]
        return out

    # -- the re-scorer -----------------------------------------------------------
    def _raw(self, signals: list[ExtractedSignal], as_of_day: int) -> float:
        if not signals:
            return 0.0
        cfg = self.cfg
        half_life = cfg.half_life_days.get(signals[0].signal_type.value, 120.0)

        base = 0.0
        for s in signals:
            weight = s.confidence if cfg.confidence_weighting else 1.0
            base += weight * _decay(as_of_day - s.day, half_life, cfg.decay_enabled)

        multiplier = 1.0
        if cfg.corroboration_enabled:
            # Independent conversations reinforce. Repetition inside one conversation does not
            # -- the extractor already collapsed those to one signal per (conversation, type).
            n_conversations = len({s.conversation_id for s in signals})
            multiplier *= 1.0 + cfg.corroboration_bonus * (n_conversations - 1)
        if cfg.cross_channel_enabled:
            n_channels = len({s.channel for s in signals})
            multiplier *= 1.0 + cfg.cross_channel_bonus * (n_channels - 1)
        if cfg.escalation_enabled and _escalating(signals):
            multiplier *= 1.0 + cfg.escalation_bonus

        return 1.0 - math.exp(-cfg.saturation * base * multiplier)

    def score(
        self, customer_id: str, signal_type: SignalType, as_of_day: int
    ) -> ScoreBreakdown:
        # COPIES, never the stored entries: scoring must not mutate the ledger. `score()`
        # writes contribution and score fields onto the entries it returns, and `timeline()`
        # materialises one breakdown per day before anyone reads any of them. Hand back the
        # stored objects and every earlier breakdown ends up carrying the final day's numbers,
        # so `Case.evidence` -- the auditable chain, and the input to `is_load_bearing()` --
        # reports the wrong as-of-day contributions.
        live = [
            replace(e)
            for e in self._entries.get(customer_id, [])
            if e.signal.signal_type is signal_type and e.signal.day <= as_of_day
        ]
        total = self._raw([e.signal for e in live], as_of_day)

        for entry in live:
            others_now = [e.signal for e in live if e is not entry]
            entry.contribution_now = total - self._raw(others_now, as_of_day)
            entry.score_now = total

            # What was known on the day this entry arrived, and what it was worth then.
            at_write_day = entry.signal.day
            known_then = [e for e in live if e.signal.day <= at_write_day]
            then_total = self._raw([e.signal for e in known_then], at_write_day)
            then_others = [e.signal for e in known_then if e is not entry]
            entry.score_at_write = then_total
            entry.contribution_at_write = then_total - self._raw(then_others, at_write_day)

        return ScoreBreakdown(
            customer_id=customer_id,
            signal_type=signal_type,
            score=total,
            as_of_day=as_of_day,
            entries=live,
        )

    def best(self, customer_id: str, as_of_day: int) -> ScoreBreakdown:
        """Highest-scoring signal family for this customer, as of a date."""
        present = {s.signal_type for s in self.signals(customer_id, as_of_day=as_of_day)}
        if not present:
            return ScoreBreakdown(customer_id, SignalType.CHURN_INTENT, 0.0, as_of_day)
        return max(
            (self.score(customer_id, st, as_of_day) for st in sorted(present, key=lambda t: t.value)),
            key=lambda b: b.score,
        )

    def timeline(self, customer_id: str, signal_type: SignalType) -> list[ScoreBreakdown]:
        """Score after each conversation that carried a signal. This is the demo."""
        days = sorted({s.day for s in self.signals(customer_id, signal_type)})
        return [self.score(customer_id, signal_type, d) for d in days]

    def open_case(
        self, customer_id: str, signal_type: SignalType, threshold: float
    ) -> Case | None:
        """First day the running score crosses. Carries the whole evidence chain."""
        for breakdown in self.timeline(customer_id, signal_type):
            if breakdown.score >= threshold:
                latest = max(breakdown.entries, key=lambda e: e.signal.day)
                return Case(
                    customer_id=customer_id,
                    signal_type=signal_type,
                    score=breakdown.score,
                    opened_on_day=breakdown.as_of_day,
                    opened_by_conversation=latest.signal.conversation_id,
                    evidence=list(breakdown.entries),
                )
        return None
