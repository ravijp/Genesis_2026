"""AT-58's scorer: does a routed team get graded correctly against the seeded trajectory?

Mirrors `tests/test_verdict_accuracy.py`: what needs a model (the investigation itself) is not
tested here. What is testable is the part the first draft of a sibling tool got wrong once
already — scoring against a value the schema does not permit, silently favouring the agent —
so every test here is a PROPERTY of the scoring, never a label a constant-returning stub could
satisfy.
"""

from __future__ import annotations

from typing import get_args

import pytest
import routing_accuracy as ra

from earshot.agent.schemas import InvestigationDecision
from earshot.core.accounts import synthesize_prior_cases
from earshot.schema import TRAJECTORY_TEAM
from earshot.tenants import CANONICAL_TEAMS


def test_trajectory_team_matches_the_schema_it_hoists_from() -> None:
    """`TRAJECTORY_TEAM` is the ONE map -- pinned against `SignalType` and `CANONICAL_TEAMS`
    directly, so a fifth signal family or a renamed team cannot silently drift out of step with
    either side that reads it (`core/accounts.py`'s prior-case generator, this scorer)."""
    from earshot.schema import SignalType

    assert set(TRAJECTORY_TEAM) == {t.value for t in SignalType}
    assert set(TRAJECTORY_TEAM.values()) == set(CANONICAL_TEAMS)


def test_prior_case_generator_and_the_scorer_read_the_same_map() -> None:
    """`core/accounts.py`'s synthetic prior-case history used to carry its OWN copy of the
    family->team map. Every prior case it generates must agree with `TRAJECTORY_TEAM`, the one
    this scorer also reads -- if they ever diverge again, this catches it directly rather than
    leaving the two silently disagreeing about what "correct" means."""
    seen_any = False
    for i in range(200):
        cases = synthesize_prior_cases(f"CUST-{i:04d}", risk_signal=0.9, seed=1, as_of_day=400)
        for case in cases:
            seen_any = True
            assert case.owning_team == TRAJECTORY_TEAM[case.signal_type]
    assert seen_any, "no prior cases were generated across 200 customers at a high risk_signal"


def test_owning_team_vocabulary_matches_the_schema() -> None:
    """Pinned against `InvestigationDecision.owning_team`'s annotation rather than a list
    written here, so the two cannot drift -- same rationale as AT-57's VERDICTS pin."""
    permitted = set(get_args(InvestigationDecision.model_fields["owning_team"].annotation))
    assert set(ra.OWNING_TEAMS) == permitted


def test_an_owning_team_outside_the_schema_is_refused_loudly() -> None:
    with pytest.raises(ValueError, match="unknown owning_team"):
        ra._score("churn_intent", "sales")


@pytest.mark.parametrize(
    "trajectory, routed_team, expected",
    [
        ("churn_intent", "retention", "correct"),
        ("financial_distress", "collections", "correct"),
        ("complaint_escalation", "complaints", "correct"),
        ("life_event", "vulnerability", "correct"),
        ("churn_intent", "collections", "wrong"),
        ("churn_intent", "vulnerability", "wrong"),
        ("churn_intent", "none", "declined"),
        ("life_event", "none", "declined"),
    ],
)
def test_the_three_trajectory_present_buckets(trajectory: str, routed_team: str, expected: str) -> None:
    assert ra._score(trajectory, routed_team) == expected


@pytest.mark.parametrize("routed_team", [*CANONICAL_TEAMS, "none"])
def test_a_trajectory_none_customer_is_always_unscored(routed_team: str) -> None:
    """No seeded trajectory means no correct team exists. Routing right, wrong or not at all
    must all read the same way: there is nothing here that could have been correct."""
    assert ra._score(None, routed_team) == "unscored"


def test_unscored_is_never_one_of_the_three_scored_buckets() -> None:
    """A test that would pass with the trajectory-None branch deleted is worse than no test --
    this fails if `unscored` ever collides with `correct`/`wrong`/`declined`."""
    scored_buckets = {ra._score(t, team) for t in TRAJECTORY_TEAM for team in ra.OWNING_TEAMS}
    none_bucket = {ra._score(None, team) for team in ra.OWNING_TEAMS}
    assert none_bucket == {"unscored"}
    assert not none_bucket & scored_buckets


def test_error_kind_matches_the_ledgers_dominant_signal_or_neither() -> None:
    assert ra._error_kind(routed_team="collections", dominant_team="collections") == "matched_dominant_signal"
    assert ra._error_kind(routed_team="collections", dominant_team="vulnerability") == "matched_neither"


def _row(trajectory: str | None, routed_team: str, dominant_signal: str, confidence: float = 0.5) -> dict:
    """A row shaped exactly like `score_cases` produces, built by hand so `summarize()` can be
    tested without generating a corpus."""
    bucket = ra._score(trajectory, routed_team)
    dominant_team = TRAJECTORY_TEAM[dominant_signal]
    correct_team = TRAJECTORY_TEAM[trajectory] if trajectory is not None else None
    error_kind = ra._error_kind(routed_team, dominant_team) if bucket == "wrong" else None
    return {
        "customer_id": "CUST-TEST",
        "trajectory": trajectory,
        "correct_team": correct_team,
        "dominant_signal": dominant_signal,
        "dominant_team": dominant_team,
        "routed_team": routed_team,
        "confidence": confidence,
        "bucket": bucket,
        "error_kind": error_kind,
    }


def test_a_trajectory_none_customer_never_enters_the_accuracy_denominator() -> None:
    """The load-bearing property: `with_trajectory.n` -- the accuracy denominator -- must count
    only customers a route could have been right about, however many trajectory-None customers
    are in the batch and however they were routed."""
    rows = [
        _row("churn_intent", "retention", dominant_signal="churn_intent"),
        _row(None, "retention", dominant_signal="churn_intent"),  # routed anyway
        _row(None, "none", dominant_signal="life_event"),  # declined
        _row(None, "collections", dominant_signal="financial_distress"),  # routed anyway
    ]
    summary = ra.summarize(rows)
    assert summary["with_trajectory"]["n"] == 1
    assert summary["without_trajectory"]["n"] == 3
    assert summary["without_trajectory"]["routed_anyway"] == 2
    assert summary["without_trajectory"]["declined"] == 1


def test_summarize_splits_correct_wrong_declined() -> None:
    rows = [
        _row("churn_intent", "retention", dominant_signal="churn_intent"),  # correct
        _row("churn_intent", "collections", dominant_signal="financial_distress"),  # wrong, matches dominant
        _row("churn_intent", "vulnerability", dominant_signal="churn_intent"),  # wrong, matches neither
        _row("life_event", "none", dominant_signal="life_event"),  # declined
    ]
    summary = ra.summarize(rows)
    assert summary["with_trajectory"] == {"n": 4, "correct": 1, "wrong": 2, "declined": 1}
    assert summary["wrong_error_kind"] == {
        "matched_dominant_signal": 1, "matched_neither": 1, "total_wrong": 2,
    }


def test_confusion_matrix_has_every_team_and_zero_is_not_omitted() -> None:
    rows = [_row("churn_intent", "retention", dominant_signal="churn_intent")]
    matrix = ra.summarize(rows)["confusion_matrix"]
    assert set(matrix) == set(CANONICAL_TEAMS)
    for truth_team in CANONICAL_TEAMS:
        assert set(matrix[truth_team]) == {*CANONICAL_TEAMS, "none"}
    assert matrix["retention"]["retention"] == 1  # churn_intent's correct team is retention
    assert matrix["collections"]["retention"] == 0  # zero counts are present, not omitted


def test_config_hash_mismatch_aborts_loudly() -> None:
    """Scoring against a corpus that is not the one the artifact's investigations actually saw
    is not a wrong measurement, it is a confident one. Must refuse rather than proceed."""
    fake_manifest = {
        "seed": 20260809,
        "config_hash": "0000not-a-real-hash",
        "population": {"customers": 400},
    }
    with pytest.raises(SystemExit, match="config hash mismatch"):
        ra.rebuild_queue(fake_manifest)


def test_matching_config_hash_does_not_abort() -> None:
    """The positive case for the same guard: the default config at customers=400 is what
    `verdict_accuracy.py` runs with by default, so rebuilding it must reproduce its own hash."""
    from dataclasses import replace

    from earshot.config import DEFAULT

    run = replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=50))
    real_manifest = {
        "seed": run.seed,
        "config_hash": run.hash(),
        "population": {"customers": 50},
    }
    corpus, _, cut, _ = ra.rebuild_queue(real_manifest)
    assert corpus.customers
    assert isinstance(cut, list)
