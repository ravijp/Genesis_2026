"""Statistical proof that the agent's tools cannot recover the answer key.

`test_separation.py` guards IMPORTS. It cannot see the leak that actually happened: a
ground-truth field was handed to the tools as a plain float, and `latent_risk > 0` was a
lossless encoding of `Stratum`. No import was involved, so nothing failed, and the offline
agent was separating decoys from real arcs off the account tool alone.

These tests guard the DATA. They are the ones that would have caught it.
"""

from __future__ import annotations

import statistics
from dataclasses import replace

import pytest

from earshot.config import DEFAULT
from earshot.corpus import generate
from earshot.schema import Outcome, Stratum

N = 1200
CORPUS = generate(replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=N)))
ARC_STRATA = (Stratum.CONCENTRATED, Stratum.DIFFUSE)


def _best_threshold_accuracy(positive: list[float], negative: list[float]) -> float:
    """How well can a single cut on this value recover the label? 1.0 means it IS the label."""
    if not positive or not negative:
        return 1.0
    total = len(positive) + len(negative)
    best = 0.0
    for t in sorted(set(positive + negative)):
        correct = sum(1 for x in positive if x >= t) + sum(1 for x in negative if x < t)
        best = max(best, correct / total)
    return best


def _split(getter):
    arc = [getter(c) for c in CORPUS.customers if c.stratum in ARC_STRATA]
    other = [getter(c) for c in CORPUS.customers if c.stratum not in ARC_STRATA]
    return arc, other


def _base_rate() -> float:
    arc = sum(1 for c in CORPUS.customers if c.stratum in ARC_STRATA)
    return max(arc, len(CORPUS.customers) - arc) / len(CORPUS.customers)


def test_the_value_handed_to_tools_is_not_the_answer_key() -> None:
    """`financial_state` is what ToolContext receives. It must not encode Stratum.

    Guard band: base rate + 0.25. Wide on purpose -- a distressed customer genuinely should
    look somewhat worse financially, so perfect independence would be unrealistic. What must
    not happen is near-perfect recovery.
    """
    arc, other = _split(lambda c: c.financial_state)
    accuracy = _best_threshold_accuracy(arc, other)
    ceiling = _base_rate() + 0.25
    assert accuracy < ceiling, (
        f"a single threshold on financial_state recovers Stratum with accuracy {accuracy:.3f} "
        f"(base rate {_base_rate():.3f}). The account tool is an oracle for the answer key."
    )


def test_latent_risk_is_still_revealing_and_therefore_must_never_reach_a_tool() -> None:
    """The counter-example, pinned deliberately.

    `latent_risk` IS close to the answer key -- it is derived from how much evidence was
    planted. That is fine, because nothing on the decision path may see it. This test exists so
    that if someone ever wires `latent_risk` back into `ToolContext`, the reason it is
    forbidden is written down right here and cannot be mistaken for over-caution.
    """
    arc, other = _split(lambda c: c.latent_risk)
    assert _best_threshold_accuracy(arc, other) > 0.90


def test_tool_context_is_not_constructed_from_latent_risk() -> None:
    """Reverting one token in cli.py reopened the leak with every other test still green."""
    import inspect

    from earshot import cli

    source = inspect.getsource(cli._context)
    assert "truth.financial_state" in source, (
        "the ToolContext no longer receives financial_state -- if it has been switched back to "
        "latent_risk, the answer key is reachable from the agent's tools again"
    )
    assert "truth.latent_risk" not in source, "latent_risk is being passed into ToolContext"


@pytest.mark.parametrize("field", ["balance_trend", "days_in_overdraft", "returned_payments"])
def test_account_features_do_not_separate_the_populations(field: str) -> None:
    """The individual signals the agent reads must overlap between the two populations.

    A field whose distributions barely overlap is a back door even if no single threshold is
    perfect, because a model can combine several of them.
    """
    from earshot.core.accounts import account_snapshot

    def value(customer) -> float:
        snap = account_snapshot(
            customer.customer_id, customer.financial_state, CORPUS.seed, as_of_day=180
        )
        return float(getattr(snap, field, 0.0) or 0.0)

    sample = CORPUS.customers[:400]
    arc = [value(c) for c in sample if c.stratum in ARC_STRATA]
    other = [value(c) for c in sample if c.stratum not in ARC_STRATA]
    if len(set(arc + other)) < 3:
        pytest.skip(f"{field} is near-constant in this corpus")
    accuracy = _best_threshold_accuracy(arc, other)
    assert accuracy < _base_rate() + 0.25, (
        f"{field} alone recovers Stratum at {accuracy:.3f} vs base {_base_rate():.3f}"
    )


def test_outcome_is_not_recoverable_from_financial_state() -> None:
    """Predicting the outcome is the agent's job. It must not be readable off one number."""
    churned = [c.financial_state for c in CORPUS.customers if c.outcome is not Outcome.NONE]
    fine = [c.financial_state for c in CORPUS.customers if c.outcome is Outcome.NONE]
    if not churned:
        pytest.skip("no outcomes in this corpus")
    # Means may differ -- that is real signal -- but the distributions must overlap heavily.
    overlap_lo = max(min(churned), min(fine))
    overlap_hi = min(max(churned), max(fine))
    assert overlap_hi > overlap_lo, "financial_state ranges do not overlap between outcomes"
    spread = statistics.pstdev(churned + fine)
    gap = abs(statistics.mean(churned) - statistics.mean(fine))
    assert gap < spread, (
        f"financial_state separates outcomes too cleanly: means differ by {gap:.3f} against a "
        f"spread of {spread:.3f}"
    )
