"""All tunable parameters live here. No magic numbers in logic modules.

Every value in ScoringConfig is ablatable and sweepable. The sensitivity sweep exists to
discover that the memory advantage is a tuning artifact, so these must be data, not literals
buried in the scorer.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from .schema import SignalType


@dataclass(frozen=True)
class CorpusConfig:
    n_customers: int = 10
    conversations_per_customer: tuple[int, int] = (2, 5)
    horizon_days: int = 180
    # Stratum mix. Deliberately includes both decoy kinds; v1 only had extractor-targeted ones.
    stratum_weights: dict[str, float] = field(
        default_factory=lambda: {
            "concentrated": 0.25,
            "diffuse": 0.30,
            "decoy_extractor": 0.15,
            "decoy_accumulator": 0.10,
            "null": 0.20,
        }
    )
    # Dirichlet concentration: low alpha -> mass piles into one conversation (CONCENTRATED),
    # high alpha -> mass spreads evenly (DIFFUSE). Strata are labelled from THIS, not from
    # what any arm can detect.
    alpha_concentrated: float = 0.35
    alpha_diffuse: float = 6.0
    total_arc_mass: tuple[float, float] = (0.55, 1.0)
    # Outcomes are drawn stochastically from latent risk so prediction is a real task.
    # Calibrated to a plausible retail-banking portfolio: ~3% background attrition, rising to
    # ~20% for the highest-risk arcs. The first run used gain=0.75, which produced a 33%
    # portfolio outcome rate -- unrealistic, and it made precision meaningless because a third
    # of every random sample was a true positive.
    outcome_base_rate: float = 0.03
    outcome_risk_gain: float = 0.18
    filler_turns: tuple[int, int] = (4, 12)
    asr_error_rate: float = 0.02


@dataclass(frozen=True)
class ScoringConfig:
    # Half-life in days, per signal type. A job loss two years ago is not live risk.
    half_life_days: dict[str, float] = field(
        default_factory=lambda: {
            SignalType.CHURN_INTENT.value: 120.0,
            SignalType.FINANCIAL_DISTRESS.value: 200.0,
            SignalType.COMPLAINT_ESCALATION.value: 90.0,
            SignalType.LIFE_EVENT.value: 300.0,
        }
    )
    # Independent signals in DIFFERENT conversations reinforce super-additively.
    # Repetition inside one conversation does not.
    corroboration_bonus: float = 0.35
    cross_channel_bonus: float = 0.20
    escalation_bonus: float = 0.25
    confidence_weighting: bool = True
    decay_enabled: bool = True
    corroboration_enabled: bool = True
    cross_channel_enabled: bool = True
    escalation_enabled: bool = True
    # Squashing keeps scores in [0,1) so arms are comparable after calibration.
    #
    # Readability only. At 1.6 a five-signal arc reached 0.983 by its third conversation and
    # 1.000 by its fifth, which is useless on a reviewer's screen.
    #
    # Recorded because the first diagnosis was WRONG and the mistake is worth not repeating:
    # this value cannot change any equal-alert-budget result. 1-exp(-kx) is strictly monotonic
    # in x, so every k induces the identical customer ranking. Changing 1.6 -> 0.35 moved every
    # recall/precision figure by exactly zero. If the ledger under-performs, saturation is not
    # the reason -- look at decay and escalation, which the mechanism ablation implicates.
    saturation: float = 0.35


@dataclass(frozen=True)
class RunConfig:
    seed: int = 20260809
    corpus: CorpusConfig = field(default_factory=CorpusConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    # Extractor honesty knobs: the offline provider is deliberately
    # imperfect and its miss rate is measured and published, never hidden.
    offline_miss_rate: float = 0.22
    offline_false_fire_rate: float = 0.08

    def hash(self) -> str:
        blob = json.dumps(asdict(self), sort_keys=True, default=str).encode()
        return hashlib.sha256(blob).hexdigest()[:12]


DEFAULT = RunConfig()
