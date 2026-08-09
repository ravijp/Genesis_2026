"""Evaluation harness.

Two properties hold everything else up, and neither survives being "simplified" away:

**Equal alert budget, not a shared threshold.** An accumulating sum and a per-conversation max
do not live on the same scale, so cutting both at the same number is a gift to the accumulator.
Instead each arm is cut at *its own* threshold chosen so that all arms flag the same number of
customers -- which is also the real operating constraint, since a review team has fixed capacity.

**Detectability is measured, never enforced.** `corpus_diagnostics` reports what share of each
stratum each arm actually catches, and has no power to change the corpus. Regenerating arcs a
baseline manages to detect would be selection on the dependent variable, so detectability is a
diagnostic here and nothing more.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from .arms import ArmResult
from .schema import Corpus, ExtractedSignal, Outcome, SeededSignal, Stratum

DEFAULT_BUDGETS = (0.01, 0.02, 0.05, 0.10)
LEAD_HORIZONS = (0, 7, 14, 30, 60)


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if q <= 0:
        return ordered[0]
    if q >= 1:
        return ordered[-1]
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[idx]


@dataclass
class BudgetResult:
    arm: str
    budget: float
    threshold: float
    n_flagged: int
    recall: float
    precision: float
    median_lead_days: float | None
    recall_by_stratum: dict[str, float] = field(default_factory=dict)
    lead_survival: dict[int, float] = field(default_factory=dict)
    # The integers the rates were computed FROM. Carried rather than recovered downstream:
    # multiplying a rounded rate back by its denominator looks like a count and is not one,
    # and it goes silently wrong the moment the two denominators stop matching.
    n_hits: int = 0
    n_outcomes: int = 0
    stratum_hits: dict[str, int] = field(default_factory=dict)
    stratum_outcomes: dict[str, int] = field(default_factory=dict)
    # Who this arm actually alerted on. Anything asking "would the baseline have caught them?"
    # must ask THIS set, not `score >= threshold`: arms produce large tie clusters at the cut,
    # and a threshold comparison silently answers for the whole cluster rather than for the K
    # customers the budget really buys.
    #
    # A SORTED TUPLE, not a set: run artifacts are serialised with `default=str`, and a set
    # stringifies in hash order, so two identical runs would write different files and the
    # bit-for-bit reproducibility claim would be false.
    flagged_ids: tuple[str, ...] = ()
    # How well-defined this arm's ranking is. An arm with few distinct scores has a large tie
    # cluster sitting at the cut, so part of its alert queue is chosen by the `customer_id`
    # tie-break rather than by evidence. Published, because it is the difference between a
    # comparison that means something and one that is partly alphabetical.
    n_distinct_scores: int = 0
    n_tie_decided: int = 0


def _outcome_customers(corpus: Corpus) -> dict[str, int | None]:
    return {
        c.customer_id: c.outcome_day
        for c in corpus.customers
        if c.outcome is not Outcome.NONE
    }


def evaluate_arm(
    corpus: Corpus, arm: ArmResult, budget: float
) -> BudgetResult:
    # Every customer gets a score, including those the extractor found nothing for -- omitting
    # them would quietly inflate precision.
    scores = {c.customer_id: 0.0 for c in corpus.customers}
    scores.update(arm.scores())

    # TRUE equal alert budget: rank and take the top K, rather than thresholding on a
    # quantile. Thresholding looks equivalent and is not — arms produce heavily tied scores
    # (every customer whose only evidence is one cue of the same weight scores identically),
    # so a `>=` cut sweeps in the whole tie cluster and the arms end up flagging wildly
    # different numbers of customers at the same nominal budget, which is not a comparison at
    # all. Ties are broken deterministically by customer_id.
    k = max(1, round(budget * len(scores)))
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    flagged = {cid for cid, s in ranked[:k] if s > 0}
    threshold = min((scores[cid] for cid in flagged), default=1.0)
    outcomes = _outcome_customers(corpus)
    truth_by_id = {c.customer_id: c for c in corpus.customers}

    # How many of the issued alerts sit exactly on the cut. Compared below against how many
    # customers in the whole portfolio sit there: if they are equal, the tie cluster fitted
    # inside the budget and nothing was decided by the tie-break.
    _at_cut_flagged = sum(1 for cid in flagged if scores[cid] == threshold and scores[cid] > 0)

    hits = flagged & set(outcomes)
    recall = len(hits) / len(outcomes) if outcomes else 0.0
    precision = len(hits) / len(flagged) if flagged else 0.0

    leads: list[int] = []
    for cid in hits:
        outcome_day = outcomes[cid]
        timeline = arm.timelines.get(cid)
        if outcome_day is None or timeline is None:
            continue
        crossed = timeline.first_crossing(threshold)
        if crossed is not None:
            leads.append(outcome_day - crossed)

    survival = {
        d: (sum(1 for lead in leads if lead >= d) / len(outcomes) if outcomes else 0.0)
        for d in LEAD_HORIZONS
    }

    by_stratum: dict[str, float] = {}
    stratum_hits: dict[str, int] = {}
    stratum_outcomes: dict[str, int] = {}
    for stratum in Stratum:
        members = [c.customer_id for c in corpus.customers if c.stratum is stratum]
        if not members:
            continue
        # For decoy and null strata, "recall" would be meaningless -- report the FLAG RATE
        # instead, which is the false-positive rate we actually care about there.
        relevant = [cid for cid in members if truth_by_id[cid].outcome is not Outcome.NONE]
        if stratum in (Stratum.DECOY_EXTRACTOR, Stratum.DECOY_ACCUMULATOR, Stratum.NULL):
            by_stratum[f"{stratum.value} (flag rate)"] = len(
                [cid for cid in members if cid in flagged]
            ) / len(members)
        elif relevant:
            caught = len([cid for cid in relevant if cid in flagged])
            by_stratum[stratum.value] = caught / len(relevant)
            stratum_hits[stratum.value] = caught
            stratum_outcomes[stratum.value] = len(relevant)

    return BudgetResult(
        arm=arm.arm,
        budget=budget,
        threshold=round(threshold, 4),
        n_flagged=len(flagged),
        recall=round(recall, 4),
        precision=round(precision, 4),
        median_lead_days=round(statistics.median(leads), 1) if leads else None,
        recall_by_stratum={k: round(v, 4) for k, v in sorted(by_stratum.items())},
        lead_survival={d: round(v, 4) for d, v in survival.items()},
        n_hits=len(hits),
        n_outcomes=len(outcomes),
        flagged_ids=tuple(sorted(flagged)),
        n_distinct_scores=len(set(scores.values())),
        # Alerts the score could not decide. Zero unless the tie cluster at the cut is genuinely
        # LARGER than the room left in the queue: `threshold` is the lowest flagged score, so
        # that customer always equals it and a plain `len(flagged) - count(> threshold)` reports
        # at least one arbitrary slot for every arm, always. That floor is what made an arm with
        # a perfectly well-separated ranking read as 0.7% arbitrary rather than 0.0%.
        n_tie_decided=(
            _at_cut_flagged
            if (
                sum(1 for s in scores.values() if s == threshold and s > 0) > _at_cut_flagged
            )
            else 0
        ),
        stratum_hits=dict(sorted(stratum_hits.items())),
        stratum_outcomes=dict(sorted(stratum_outcomes.items())),
    )


def evaluate_all(
    corpus: Corpus, arms: dict[str, ArmResult], budgets: tuple[float, ...] = DEFAULT_BUDGETS
) -> list[BudgetResult]:
    return [
        evaluate_arm(corpus, arm, budget) for budget in budgets for arm in arms.values()
    ]


# --- honesty diagnostics ---------------------------------------------------------


def extraction_fidelity(
    seeded: tuple[SeededSignal, ...], extracted: list[ExtractedSignal]
) -> dict[str, float | int]:
    """How good is the extractor, really? Published, never hidden.

    'It misses N% of planted signals, it is the WEAKER arm, and the memory delta holds anyway'
    is a stronger position than a matcher that scores itself perfectly.
    """
    found = {(s.conversation_id, s.signal_type) for s in extracted}
    genuine = [s for s in seeded if not s.is_decoy]
    caught = [s for s in genuine if (s.conversation_id, s.signal_type) in found]

    planted_keys = {(s.conversation_id, s.signal_type) for s in seeded}
    unplanted = [s for s in extracted if (s.conversation_id, s.signal_type) not in planted_keys]

    decoys = [s for s in seeded if s.is_decoy]
    decoys_fired = [s for s in decoys if (s.conversation_id, s.signal_type) in found]

    # The two decoy families are aimed at different components and a firing means the opposite
    # thing in each, so pooling them averages a success and a failure into one uninterpretable
    # rate. Extractor decoys are lookalikes: firing is a mistake. Accumulator decoys are
    # GENUINE weak signals that never amount to anything: firing is correct, and what is being
    # tested is whether the ledger goes on to over-accumulate them.
    def _split(is_extractor_decoy: bool) -> tuple[int, int]:
        family = [s for s in decoys if (s.decoy_kind == "extractor") is is_extractor_decoy]
        fired = [s for s in family if (s.conversation_id, s.signal_type) in found]
        return len(fired), len(family)

    extractor_fired, extractor_n = _split(True)
    accumulator_fired, accumulator_n = _split(False)

    return {
        "planted_genuine": len(genuine),
        "extraction_recall": round(len(caught) / len(genuine), 4) if genuine else 0.0,
        "measured_miss_rate": round(1 - len(caught) / len(genuine), 4) if genuine else 0.0,
        "unplanted_extractions": len(unplanted),
        "decoys_planted": len(decoys),
        "decoy_fire_rate": round(len(decoys_fired) / len(decoys), 4) if decoys else 0.0,
        "extractor_decoys_planted": extractor_n,
        "extractor_decoy_fire_rate": (
            round(extractor_fired / extractor_n, 4) if extractor_n else 0.0
        ),
        "accumulator_decoys_planted": accumulator_n,
        "accumulator_decoy_fire_rate": (
            round(accumulator_fired / accumulator_n, 4) if accumulator_n else 0.0
        ),
    }


def corpus_diagnostics(corpus: Corpus, arms: dict[str, ArmResult]) -> dict[str, object]:
    """Reported, never enforced. Shows how the generated strata actually behaved."""
    counts: dict[str, int] = {}
    for c in corpus.customers:
        counts[c.stratum.value] = counts.get(c.stratum.value, 0) + 1

    outcomes = sum(1 for c in corpus.customers if c.outcome is not Outcome.NONE)
    conv_per_customer = [
        len(corpus.conversations_for(c.customer_id)) for c in corpus.customers
    ]

    # Volume confound check: does the full ledger just reward talkative
    # customers? If score tracks conversation count, the "memory" is only "more text".
    full = arms.get("full-ledger")
    volume_correlation = None
    if full:
        scores = full.scores()
        pairs = [
            (len(corpus.conversations_for(c.customer_id)), scores.get(c.customer_id, 0.0))
            for c in corpus.customers
        ]
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        if len(set(xs)) > 1 and len(set(ys)) > 1:
            volume_correlation = round(statistics.correlation(xs, ys), 4)

    return {
        "n_customers": len(corpus.customers),
        "n_conversations": len(corpus.conversations),
        "n_seeded_signals": len(corpus.seeded),
        "stratum_counts": dict(sorted(counts.items())),
        "outcome_rate": round(outcomes / len(corpus.customers), 4) if corpus.customers else 0.0,
        "mean_conversations_per_customer": round(statistics.mean(conv_per_customer), 2)
        if conv_per_customer
        else 0.0,
        "score_vs_volume_correlation": volume_correlation,
    }
