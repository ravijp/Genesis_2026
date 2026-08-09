"""Tests for the multi-seed harness.

Everything published comes through `sweep.py`, so it carries the most coverage in the suite:
the sign test against hand computation, the pairing, and the invariants the multi-seed
comparison depends on — equal budgets, matching denominators, determinism.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from earshot.config import DEFAULT
from earshot.sweep import ArmSample, paired_record, sign_test_p, sweep

SMALL = replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=150))
SEEDS = [20260809, 20260810, 20260811]


def _sample(arm: str, seed: int, recall: float, diffuse: float = 0.0) -> ArmSample:
    return ArmSample(
        arm=arm, seed=seed, recall=recall, hits=0, outcomes=0, flagged=0,
        diffuse_recall=diffuse,
    )


# --- the sign test -----------------------------------------------------------------
@pytest.mark.parametrize(
    ("wins", "losses", "expected"),
    [
        (8, 0, 0.0078),   # the headline shape
        (0, 8, 0.0078),   # symmetric
        (1, 8, 0.0391),
        (5, 5, 1.0),
        (0, 0, 1.0),      # all ties -> no evidence either way
        (3, 4, 1.0),
    ],
)
def test_sign_test_matches_hand_computation(wins: int, losses: int, expected: float) -> None:
    assert sign_test_p(wins, losses) == pytest.approx(expected, abs=1e-4)


def test_sign_test_never_exceeds_one() -> None:
    """The two-sided doubling can overshoot without the clamp."""
    for wins in range(6):
        for losses in range(6):
            assert 0.0 <= sign_test_p(wins, losses) <= 1.0


# --- pairing -----------------------------------------------------------------------
def test_pairing_is_on_seed_not_on_position() -> None:
    """Comparing sorted lists instead of matched seeds would silently change the answer."""
    by_arm = {
        "a": [_sample("a", 1, 0.10), _sample("a", 2, 0.30)],
        "b": [_sample("b", 2, 0.20), _sample("b", 1, 0.40)],  # deliberately out of order
    }
    # seed 1: 0.10 vs 0.40 -> loss. seed 2: 0.30 vs 0.20 -> win.
    assert paired_record(by_arm, "a", "b") == (1, 1, 0)


def test_pairing_ignores_seeds_present_in_only_one_arm() -> None:
    by_arm = {
        "a": [_sample("a", 1, 0.5), _sample("a", 9, 0.9)],
        "b": [_sample("b", 1, 0.4)],
    }
    assert paired_record(by_arm, "a", "b") == (1, 0, 0)


def test_pairing_can_use_a_metric_other_than_recall() -> None:
    """The pre-registered headline is a diffuse-stratum comparison, so pairing has to work on
    a metric other than overall recall or the published number is unreproducible."""
    by_arm = {
        "a": [_sample("a", 1, recall=0.9, diffuse=0.1)],
        "b": [_sample("b", 1, recall=0.1, diffuse=0.9)],
    }
    assert paired_record(by_arm, "a", "b", metric="recall") == (1, 0, 0)
    assert paired_record(by_arm, "a", "b", metric="diffuse_recall") == (0, 1, 0)


# --- the sweep itself --------------------------------------------------------------
@pytest.fixture(scope="module")
def swept():
    return sweep(SMALL, SEEDS, budget=0.10)


EXPECTED_ARMS = {
    "stateless-max",
    "stateless-top2",
    "dumb-ledger",
    "long-context-3",
    "full-ledger",
    "hybrid",
}


def test_every_arm_runs_on_every_seed(swept) -> None:
    summaries, by_arm = swept
    assert set(summaries) == EXPECTED_ARMS, f"arm roster changed: {sorted(summaries)}"
    for arm, samples in by_arm.items():
        assert sorted(s.seed for s in samples) == SEEDS, f"{arm} dropped a seed"


def test_published_integers_are_counted_not_recovered_from_a_rate() -> None:
    """The integers beside every published rate must be the ones that PRODUCED it.

    Recovering them as `round(rate * denominator)` yields something that looks like a count,
    reads like a count, and silently stops being one as soon as the rate is rounded or the two
    denominators drift apart. Here the counts are compared against a direct intersection of the
    flagged set with the outcome set.
    """
    from earshot.arms import run_all_arms
    from earshot.corpus import generate
    from earshot.evals import evaluate_arm
    from earshot.extract import OfflineLexiconExtractor, extract_all
    from earshot.schema import Outcome, Stratum

    run = replace(SMALL, seed=SEEDS[0])
    corpus = generate(run)
    signals = extract_all(OfflineLexiconExtractor(), corpus.conversations)
    outcome_ids = {c.customer_id for c in corpus.customers if c.outcome is not Outcome.NONE}
    diffuse_ids = {
        c.customer_id
        for c in corpus.customers
        if c.outcome is not Outcome.NONE and c.stratum is Stratum.DIFFUSE
    }
    assert outcome_ids and diffuse_ids, "nothing to count against"

    for arm in run_all_arms(signals, run.scoring).values():
        result = evaluate_arm(corpus, arm, 0.10)
        scores = {c.customer_id: 0.0 for c in corpus.customers}
        scores.update(arm.scores())
        k = max(1, round(0.10 * len(scores)))
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        flagged = {cid for cid, s in ranked[:k] if s > 0}

        assert result.n_hits == len(flagged & outcome_ids), f"{arm.arm}: overall count"
        assert result.n_outcomes == len(outcome_ids), f"{arm.arm}: overall denominator"
        assert result.stratum_hits["diffuse"] == len(flagged & diffuse_ids), (
            f"{arm.arm}: diffuse count"
        )
        assert result.stratum_outcomes["diffuse"] == len(diffuse_ids)


def test_the_strongest_per_call_baseline_is_not_a_copy_of_the_weakest(swept) -> None:
    """`stateless-top2` exists to be a hard opponent, so it must actually differ from `max`.

    An arm that silently collapses into another arm turns a comparison into a tautology, which
    is what happened to `long-context` when its window never bound.
    """
    _, by_arm = swept
    max_scores = {(s.seed, s.arm): s for s in by_arm["stateless-max"]}
    differing = sum(
        1
        for s in by_arm["stateless-top2"]
        if s.diffuse_recall != max_scores[(s.seed, "stateless-max")].diffuse_recall
    )
    assert differing, (
        "stateless-top2 scored identically to stateless-max on every seed — it has collapsed "
        "into the arm it is supposed to be a stronger version of"
    )


def test_pooled_recall_is_over_customers_not_a_mean_of_rates(swept) -> None:
    """Averaging per-seed rates weights a small seed the same as a large one."""
    summaries, by_arm = swept
    for arm, summary in summaries.items():
        hits = sum(s.hits for s in by_arm[arm])
        outcomes = sum(s.outcomes for s in by_arm[arm])
        assert summary.total_hits == hits
        assert summary.total_outcomes == outcomes
        if outcomes:
            assert summary.pooled_recall == pytest.approx(hits / outcomes)


def test_every_rate_carries_its_denominator(swept) -> None:
    """A rate without its integers hides its own sample size."""
    _, by_arm = swept
    for samples in by_arm.values():
        for s in samples:
            assert s.outcomes > 0
            assert s.diffuse_outcomes > 0
            assert 0 <= s.hits <= s.outcomes
            assert 0 <= s.diffuse_hits <= s.diffuse_outcomes


def test_the_denominators_are_identical_across_arms(swept) -> None:
    """All arms see the same customers, so a differing denominator means a filtering bug."""
    _, by_arm = swept
    for seed in SEEDS:
        outcomes = {
            arm: next(s.outcomes for s in samples if s.seed == seed)
            for arm, samples in by_arm.items()
        }
        assert len(set(outcomes.values())) == 1, f"seed {seed} denominators differ: {outcomes}"


def test_equal_alert_budget_flags_the_same_count_for_every_arm(swept) -> None:
    """The fairness mechanism of the whole experiment."""
    _, by_arm = swept
    for seed in SEEDS:
        flagged = {
            arm: next(s.flagged for s in samples if s.seed == seed)
            for arm, samples in by_arm.items()
        }
        assert len(set(flagged.values())) == 1, f"seed {seed} budgets differ: {flagged}"


def test_the_sweep_is_deterministic() -> None:
    """Same seeds, same numbers — otherwise nothing published is reproducible."""
    first, _ = sweep(SMALL, SEEDS[:2], budget=0.10)
    second, _ = sweep(SMALL, SEEDS[:2], budget=0.10)
    assert {k: v.pooled_recall for k, v in first.items()} == {
        k: v.pooled_recall for k, v in second.items()
    }
