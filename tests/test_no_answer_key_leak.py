"""Statistical proof that the agent's tools cannot recover the answer key.

`test_separation.py` guards IMPORTS, and an import guard is blind to the more dangerous leak:
a ground-truth field handed to the tools as a plain float. `latent_risk > 0` is a lossless
encoding of `Stratum`, no import is involved, nothing fails, and an agent can separate decoys
from real arcs off the account tool without reading a word.

These tests guard the DATA. A value that correlates with the answer is fine; a value that
recovers it is not.
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
    """One identifier in cli.py decides whether the answer key is reachable from the tools, and
    no other test in the suite would notice it changing."""
    import inspect

    from earshot import cli

    source = inspect.getsource(cli._context)
    assert "truth.financial_state" in source, (
        "the ToolContext no longer receives financial_state -- if it has been switched back to "
        "latent_risk, the answer key is reachable from the agent's tools again"
    )
    assert "truth.latent_risk" not in source, "latent_risk is being passed into ToolContext"


def test_the_agents_tools_are_fed_financial_state_not_latent_risk() -> None:
    """The behavioural counterpart to the string check above, and the one that actually holds.

    A string match on `_context`'s source is a tripwire, not a guarantee. `getattr(truth,
    "latent_" + "risk")` hands the agent the answer key while leaving both spellings the check
    looks for exactly as they were, and the whole suite stays green -- which is the state A6
    ("a static guard cannot be complete, so back it with a behavioural one") exists to forbid.

    What cannot be spelled around is the tool output. So this builds a real `ToolContext`
    through `cli._context` and asks `get_account_state` -- the tool that turns the risk figure
    into a whole account profile -- what it returns.

    The counterfactual is built by poisoning the CORPUS, not the context: a copy in which the
    subject's `financial_state` has been overwritten with their `latent_risk`, run through the
    same `_context`. If `_context` reads `financial_state`, the two snapshots differ. If it
    reaches for `latent_risk` by any spelling, they are byte-identical, because the poisoned
    copy left that field alone. The first assertion pins which value crosses; the second is
    what fails when the answer key does.
    """
    from dataclasses import replace as dc_replace

    from earshot.agent.tools import AccountStateArgs, get_account_state
    from earshot.cli import _context
    from earshot.core.accounts import account_snapshot
    from earshot.memory import ScoreBreakdown
    from earshot.schema import SignalType

    # A customer whose two risk figures are far enough apart that the synthetic account
    # generator draws visibly different histories from them -- otherwise the test cannot tell
    # the two wirings apart and would pass either way.
    subject = next(
        c
        for c in CORPUS.customers
        if abs(c.financial_state - c.latent_risk) > 0.2
        and CORPUS.conversations_for(c.customer_id)
    )
    as_of = max(c.day for c in CORPUS.conversations_for(subject.customer_id))
    breakdown = ScoreBreakdown(
        customer_id=subject.customer_id,
        signal_type=SignalType.FINANCIAL_DISTRESS,
        score=0.7,
        as_of_day=as_of,
    )
    args = AccountStateArgs()

    honest = get_account_state(
        _context(CORPUS, subject.customer_id, breakdown, 0.5, CORPUS.seed), args
    )
    expected = account_snapshot(
        subject.customer_id, subject.financial_state, CORPUS.seed, as_of, args.window_days
    )
    assert honest.current_balance == expected.current_balance, (
        "the account tool is not deriving its state from financial_state"
    )

    poisoned_corpus = dc_replace(
        CORPUS,
        customers=tuple(
            dc_replace(c, financial_state=c.latent_risk)
            if c.customer_id == subject.customer_id
            else c
            for c in CORPUS.customers
        ),
    )
    leaked = get_account_state(
        _context(poisoned_corpus, subject.customer_id, breakdown, 0.5, CORPUS.seed), args
    )
    assert honest != leaked, (
        "the agent's account tool returns the same state whether the customer's financial_state "
        "is their own or their latent_risk -- so _context is reaching for latent_risk, and the "
        "tools can recover Stratum without reading a word"
    )


def _snapshot_fields() -> list[str]:
    """Discovered, not listed. A hand-written list can name a field that does not exist on
    `AccountSnapshot`; `getattr(..., default)` then returns a constant, the check below skips
    it as "near-constant", and a distress-correlated value the agent reads goes unguarded."""
    import dataclasses

    from earshot.core.accounts import AccountSnapshot

    return sorted(
        f.name for f in dataclasses.fields(AccountSnapshot)
        if f.type in ("float", "int", float, int)
    )


def test_snapshot_field_discovery_is_not_empty() -> None:
    assert len(_snapshot_fields()) >= 3, (
        f"discovery found {_snapshot_fields()} — the per-field leak check covers nothing"
    )


@pytest.mark.parametrize("field", _snapshot_fields())
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
        # No default: a missing field must raise, not silently become a constant that then
        # gets skipped as "near-constant".
        return float(getattr(snap, field) or 0.0)

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


def test_the_reviewer_consoles_account_header_uses_financial_state_not_latent_risk() -> None:
    """The console's customer-360 header is a second door onto the account tools. Pin which key
    opens it.

    `account_snapshot()` takes a risk figure and derives a whole account profile from it. Handed
    `latent_risk` it becomes an oracle: that value is a function of how much evidence was planted
    in the customer's conversations, so a reader of the header recovers `Stratum` without reading
    a word. Handed `financial_state` it does not, and the tests above are what prove that.

    This asserts the wiring rather than the statistics, because the statistics are already proved
    above and would pass either way on a small sample. It is a behavioural pin: `stream_inputs`'
    `account_for` must produce exactly what `financial_state` produces and exactly not what
    `latent_risk` produces. That distinction is the one this repo has already got wrong once.
    """
    from earshot.cli import stream_inputs
    from earshot.core.accounts import account_snapshot
    from earshot.tenants import DEFAULT_TENANT

    t = DEFAULT_TENANT
    corpus = generate(t.run)
    _conversations, _context_for, account_for = stream_inputs(t)

    # A customer whose two risk figures actually differ, or the test cannot tell them apart.
    subject = next(
        c for c in corpus.customers if abs(c.financial_state - c.latent_risk) > 0.05
    )
    as_of = 170
    got = account_for(subject.customer_id, as_of)
    assert got is not None
    assert got["source"] == "synthetic", "the header must stamp itself as synthetic"

    from_financial = account_snapshot(
        subject.customer_id, subject.financial_state, t.run.seed, as_of
    )
    from_latent = account_snapshot(
        subject.customer_id, subject.latent_risk, t.run.seed, as_of
    )
    assert got["snapshot"]["current_balance"] == from_financial.current_balance, (
        "the console header is not derived from financial_state"
    )
    assert from_financial != from_latent, (
        "the two risk figures produced an identical snapshot for this customer, so this test "
        "cannot distinguish them -- pick a customer whose figures differ more"
    )
    assert got["snapshot"]["current_balance"] != from_latent.current_balance, (
        "the console header is derived from latent_risk, which encodes the answer key"
    )


def test_the_account_header_carries_no_answer_key_field() -> None:
    """A structural check on top of the statistical one: no field is even named after the key."""
    from earshot.cli import stream_inputs
    from earshot.stream import ANSWER_KEY_FIELDS, _all_keys
    from earshot.tenants import DEFAULT_TENANT

    _conversations, _context_for, account_for = stream_inputs(DEFAULT_TENANT)
    payload = account_for("CUST-0000", 170)
    leaked = _all_keys(payload) & ANSWER_KEY_FIELDS
    assert not leaked, f"the console header carries {sorted(leaked)}"
