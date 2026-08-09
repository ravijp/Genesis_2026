"""Synthetic corpus generation: plan first, prose second.

Two properties matter more than realism here:

1. **Strata are generative.** A customer's stratum is decided by the Dirichlet concentration
   used to split their arc's evidence mass, NOT by asking whether some baseline can detect
   them. Defining a stratum by reference to a baseline's decision function, or regenerating
   arcs that baseline catches, would be selection on the dependent variable. Whether an arm
   can detect a DIFFUSE arc is a *measured result*, not a construction.

2. **Outcomes are drawn stochastically from latent risk.** Nobody is handed the answer, so
   outcome prediction is a genuine prediction task rather than a lookup on the answer key.

No third-party dependencies: Dirichlet is sampled via normalised Gamma draws from `random`.
"""

from __future__ import annotations

import random

from .config import CorpusConfig, RunConfig
from .corpus_lexicon import (
    BY_TYPE,
    CLOSINGS,
    DECOYS_ACCUMULATOR,
    DECOYS_EXTRACTOR,
    FILLER_AGENT,
    FILLER_CUSTOMER,
    OPENINGS,
    Fragment,
)
from .schema import (
    Channel,
    Conversation,
    Corpus,
    CustomerTruth,
    Outcome,
    SeededSignal,
    SignalType,
    Stratum,
    Turn,
)

_TRAJECTORY_CHOICES = (
    SignalType.CHURN_INTENT,
    SignalType.FINANCIAL_DISTRESS,
    SignalType.COMPLAINT_ESCALATION,
    SignalType.LIFE_EVENT,
)


def _dirichlet(rng: random.Random, alpha: float, k: int) -> list[float]:
    draws = [rng.gammavariate(alpha, 1.0) for _ in range(k)]
    total = sum(draws) or 1.0
    return [d / total for d in draws]


def _pick_stratum(rng: random.Random, cfg: CorpusConfig) -> Stratum:
    names, weights = zip(*cfg.stratum_weights.items())
    return Stratum(rng.choices(names, weights=weights, k=1)[0])


def _nearest_fragment(
    pool: tuple[Fragment, ...], target: float, used: set[str]
) -> Fragment | None:
    """Pick the fragment whose intrinsic loudness best matches the mass allocated here."""
    candidates = [f for f in pool if f.fragment_id not in used] or list(pool)
    if not candidates:
        return None
    return min(candidates, key=lambda f: (abs(f.strength - target), f.fragment_id))


def _apply_asr_noise(rng: random.Random, text: str, rate: float) -> str:
    """Transcription is never clean. Drop or mangle the occasional word."""
    if rate <= 0:
        return text
    words = text.split()
    out: list[str] = []
    for w in words:
        if rng.random() < rate:
            if rng.random() < 0.5:
                continue  # dropped word
            out.append(w[:-1] + "-")  # clipped word
        else:
            out.append(w)
    return " ".join(out) or text


def _render_conversation(
    rng: random.Random,
    cfg: CorpusConfig,
    conversation_id: str,
    customer_id: str,
    channel: Channel,
    day: int,
    plant: Fragment | None,
) -> tuple[Conversation, int | None]:
    """Build turns around an optional planted fragment. Returns (conversation, plant turn index)."""
    turns: list[Turn] = []
    idx = 0
    if channel != Channel.COMPLAINT:
        turns.append(Turn(idx, "agent", rng.choice(OPENINGS)))
        idx += 1

    n_filler = rng.randint(*cfg.filler_turns)
    # Where the planted line lands. Never first, never last -- a signal buried mid-call is
    # the realistic case and the one sampling-based QA misses.
    plant_at = rng.randint(1, max(1, n_filler - 1)) if plant else -1

    plant_turn_index: int | None = None
    for i in range(n_filler):
        if i == plant_at and plant is not None:
            text = _apply_asr_noise(rng, plant.text, cfg.asr_error_rate)
            turns.append(Turn(idx, "customer", text))
            plant_turn_index = idx
            idx += 1
            turns.append(Turn(idx, "agent", rng.choice(FILLER_AGENT)))
            idx += 1
            continue
        turns.append(
            Turn(idx, "customer", _apply_asr_noise(rng, rng.choice(FILLER_CUSTOMER), cfg.asr_error_rate))
        )
        idx += 1
        if rng.random() < 0.75:
            turns.append(Turn(idx, "agent", rng.choice(FILLER_AGENT)))
            idx += 1

    if channel != Channel.COMPLAINT:
        turns.append(Turn(idx, "agent", rng.choice(CLOSINGS)))

    return (
        Conversation(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            day=day,
            turns=tuple(turns),
        ),
        plant_turn_index,
    )


def generate(run: RunConfig | None = None) -> Corpus:
    run = run or RunConfig()
    cfg = run.corpus
    rng = random.Random(run.seed)

    customers: list[CustomerTruth] = []
    conversations: list[Conversation] = []
    seeded: list[SeededSignal] = []

    for n in range(cfg.n_customers):
        customer_id = f"CUST-{n:04d}"
        stratum = _pick_stratum(rng, cfg)
        k = rng.randint(*cfg.conversations_per_customer)

        # Conversation days, spread over the horizon and always ordered.
        days = sorted(rng.sample(range(cfg.horizon_days), k)) if k <= cfg.horizon_days else list(
            range(k)
        )
        # Channel mix: arcs that cross channels are the interesting ones, so bias toward variety.
        channels = [rng.choice(list(Channel)) for _ in range(k)]

        trajectory: SignalType | None = None
        latent_risk = 0.0
        plants: list[Fragment | None] = [None] * k

        if stratum in (Stratum.CONCENTRATED, Stratum.DIFFUSE):
            trajectory = rng.choice(_TRAJECTORY_CHOICES)
            total_mass = rng.uniform(*cfg.total_arc_mass)
            alpha = (
                cfg.alpha_concentrated
                if stratum is Stratum.CONCENTRATED
                else cfg.alpha_diffuse
            )
            shares = _dirichlet(rng, alpha, k)
            pool = BY_TYPE[trajectory]
            used: set[str] = set()
            for i, share in enumerate(shares):
                # Mass allocated to this conversation, expressed on the fragment strength scale.
                allocated = min(1.0, share * total_mass * k / max(1, k) * (1.0 if k == 1 else 1.6))
                frag = _nearest_fragment(pool, allocated, used)
                if frag is not None:
                    used.add(frag.fragment_id)
                    plants[i] = frag
            latent_risk = total_mass

        elif stratum is Stratum.DECOY_EXTRACTOR:
            trajectory = None
            for i in range(k):
                if rng.random() < 0.6:
                    plants[i] = rng.choice(DECOYS_EXTRACTOR)

        elif stratum is Stratum.DECOY_ACCUMULATOR:
            # Genuine weak signals that corroborate across time and channel -- and go nowhere.
            # Their whole job is to punish an over-eager accumulator. latent_risk stays 0.
            trajectory = None
            for i in range(k):
                plants[i] = rng.choice(DECOYS_ACCUMULATOR)

        # NULL: plants stay empty.

        # Latent risk for the customers who are NOT on a distress arc. Real customers who are
        # fine still carry some risk, and it must OVERLAP the bottom of the distressed range.
        #
        # Leaving this at 0.0 would make `latent_risk > 0` a lossless readout of `Stratum` --
        # an answer-key field. Tools take latent risk as a plain float, so no import guard
        # would see it, and an agent could separate decoys from real arcs off the account tool
        # without reading a word of conversation.
        if stratum not in (Stratum.CONCENTRATED, Stratum.DIFFUSE):
            latent_risk = rng.betavariate(2.0, 3.5) * 0.75

        # Financial state: mostly idiosyncratic, only loosely tied to conversational risk.
        # The 0.35 weight is what keeps the account tool useful (a distressed customer really
        # is more likely to look distressed) without making it decisive on its own.
        financial_state = min(
            1.0, max(0.0, 0.35 * latent_risk + 0.65 * rng.betavariate(2.2, 2.6))
        )

        # Outcome drawn from latent risk. Decoy-accumulator and null customers sit at the
        # base rate, so a few of them churn by chance -- as they would in a real portfolio.
        p_outcome = min(0.95, cfg.outcome_base_rate + cfg.outcome_risk_gain * latent_risk)
        outcome, outcome_day = Outcome.NONE, None
        if rng.random() < p_outcome:
            outcome = (
                Outcome.CHURNED
                if (trajectory is SignalType.CHURN_INTENT or trajectory is None)
                else Outcome.DELINQUENT
            )
            outcome_day = days[-1] + rng.randint(10, 60)

        for i in range(k):
            conversation_id = f"{customer_id}-C{i}"
            conv, plant_turn = _render_conversation(
                rng, cfg, conversation_id, customer_id, channels[i], days[i], plants[i]
            )
            conversations.append(conv)
            frag = plants[i]
            if frag is not None and plant_turn is not None:
                seeded.append(
                    SeededSignal(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        signal_type=frag.signal_type,
                        mass=frag.strength,
                        turn_index=plant_turn,
                        fragment_id=frag.fragment_id,
                        is_decoy=stratum
                        in (Stratum.DECOY_EXTRACTOR, Stratum.DECOY_ACCUMULATOR),
                    )
                )

        customers.append(
            CustomerTruth(
                customer_id=customer_id,
                stratum=stratum,
                trajectory=trajectory,
                outcome=outcome,
                outcome_day=outcome_day,
                latent_risk=latent_risk,
                financial_state=financial_state,
            )
        )

    return Corpus(
        customers=tuple(customers),
        conversations=tuple(conversations),
        seeded=tuple(seeded),
        seed=run.seed,
        config_hash=run.hash(),
    )
