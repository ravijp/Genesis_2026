"""Core data types for the conversation signal layer.

Design note (BUILD-PLAN Rule 1): ground truth is authored *before* the prose. `SeededSignal`
is the answer key and is produced by the corpus planner; `ExtractedSignal` is what an
extractor believes it found. They are deliberately separate types so nothing downstream can
confuse one for the other, and so the eval can only ever compare them explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Channel(str, Enum):
    CALL = "call"
    CHAT = "chat"
    COMPLAINT = "complaint"


class SignalType(str, Enum):
    CHURN_INTENT = "churn_intent"
    FINANCIAL_DISTRESS = "financial_distress"
    COMPLAINT_ESCALATION = "complaint_escalation"
    LIFE_EVENT = "life_event"


class Stratum(str, Enum):
    """Labelled from *generation parameters*, never from what a baseline can detect.

    BUILD-PLAN §3: v1 defined these by reference to the baseline's decision function, which
    made the headline result circular. Concentrated evidence mass -> CONCENTRATED; diffuse
    mass -> DIFFUSE. Whether an arm can actually detect them is measured, not assumed.
    """

    CONCENTRATED = "concentrated"  # most evidence mass in one conversation
    DIFFUSE = "diffuse"  # evidence mass spread thin across the arc
    DECOY_EXTRACTOR = "decoy_extractor"  # looks like a signal, isn't one
    DECOY_ACCUMULATOR = "decoy_accumulator"  # real weak signals that corroborate, no outcome
    NULL = "null"  # no trajectory at all


class Outcome(str, Enum):
    NONE = "none"
    CHURNED = "churned"
    DELINQUENT = "delinquent"


@dataclass(frozen=True)
class Turn:
    index: int
    speaker: str  # "customer" | "agent" | "system"
    text: str


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    customer_id: str
    channel: Channel
    day: int  # days since corpus epoch
    turns: tuple[Turn, ...]

    def text(self) -> str:
        return "\n".join(f"{t.speaker}: {t.text}" for t in self.turns)

    def customer_text(self) -> str:
        return "\n".join(t.text for t in self.turns if t.speaker == "customer")


@dataclass(frozen=True)
class SeededSignal:
    """Answer key. Written by the planner before any prose exists."""

    customer_id: str
    conversation_id: str
    signal_type: SignalType
    mass: float  # evidence mass assigned by the Dirichlet split; the arc's "true" strength here
    turn_index: int
    fragment_id: str  # which corpus fragment was planted, for provenance
    is_decoy: bool = False


@dataclass(frozen=True)
class ExtractedSignal:
    """What an extractor believes it found. Never compared to the key implicitly."""

    customer_id: str
    conversation_id: str
    signal_type: SignalType
    confidence: float
    evidence_quote: str
    turn_index: int
    day: int
    channel: Channel = Channel.CALL  # carried so the ledger can weight cross-channel corroboration
    cue_id: str = ""  # which extractor cue fired, for error analysis


@dataclass(frozen=True)
class CustomerTruth:
    customer_id: str
    stratum: Stratum
    trajectory: SignalType | None
    outcome: Outcome
    outcome_day: int | None  # None when Outcome.NONE
    latent_risk: float  # the probability the outcome was drawn from

    # What the customer's account actually looks like, which is NOT the same thing as how much
    # they talked about it. Kept separate because conflating them made the account tool an
    # oracle: `latent_risk` is a function of how much evidence was planted in conversations,
    # so a tool reading it could recover the stratum -- the answer key -- without reading a
    # word. Financial state correlates with risk, loosely, and is drawn for every customer
    # from one common distribution so the populations genuinely overlap.
    financial_state: float = 0.0


@dataclass(frozen=True)
class Corpus:
    customers: tuple[CustomerTruth, ...]
    conversations: tuple[Conversation, ...]
    seeded: tuple[SeededSignal, ...]
    seed: int
    config_hash: str

    def conversations_for(self, customer_id: str) -> list[Conversation]:
        return sorted(
            (c for c in self.conversations if c.customer_id == customer_id), key=lambda c: c.day
        )


@dataclass
class LedgerEntry:
    """One extracted signal, retained forever.

    BUILD-PLAN Rule 3 (never-discard): sub-threshold signals are *retained and stay summable*.
    This is the design inversion against reconcile-to-current-truth. Nothing in this codebase
    may delete or supersede a ledger entry.

    Rule 4 (retro re-scoring) needs care, because the obvious formulation is false. The
    leave-one-out *marginal* contribution of any single signal necessarily SHRINKS as evidence
    accumulates — the score function is concave, so later signals push everything into
    diminishing returns. Claiming "this quote is worth more marginal points now" would be
    mathematically wrong, and a technical judge would catch it.

    What actually changes retroactively is the **interpretation**: the same conversation that
    supported a "no action" verdict when it arrived now sits inside an evidence chain that
    crosses threshold. So retro re-scoring is expressed two honest ways:

      * `retro_delta` — how much the customer's total picture has moved since this evidence
        landed (`score_now - score_at_write`), which is what "we re-read March in light of
        July" actually means;
      * `is_load_bearing()` — whether removing this quote would drop the case back below
        threshold. That is the question a compliance officer asks, and it is auditable.
    """

    signal: ExtractedSignal
    contribution_at_write: float = 0.0  # marginal value on the day it arrived
    contribution_now: float = 0.0  # marginal value today (expected to be smaller)
    score_at_write: float = 0.0  # customer's total score that day, on evidence known then
    score_now: float = 0.0  # customer's total score today

    @property
    def retro_delta(self) -> float:
        """How much this evidence's supported conclusion has moved since it landed."""
        return self.score_now - self.score_at_write

    def is_load_bearing(self, threshold: float) -> bool:
        """Would the case collapse without this quote?"""
        return self.score_now >= threshold and (self.score_now - self.contribution_now) < threshold


@dataclass
class Case:
    """Emitted when a customer's score crosses threshold. Carries the whole evidence chain."""

    customer_id: str
    signal_type: SignalType
    score: float
    opened_on_day: int
    opened_by_conversation: str
    evidence: list[LedgerEntry] = field(default_factory=list)

    def lead_days(self, outcome_day: int | None) -> int | None:
        if outcome_day is None:
            return None
        return outcome_day - self.opened_on_day
