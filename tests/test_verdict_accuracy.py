"""AT-57's scorer: the part that decides what "correct" means.

The measurement itself needs a model. What is testable here is the scoring, and it is exactly where
the first draft was wrong: it scored against `false_positive`, which `agent/schemas.py` does not
permit, so every correct dismissal would have been counted as an error — silently, and in the
direction that flatters nobody but is still wrong.
"""

from __future__ import annotations

import pytest
import verdict_accuracy as va

from earshot.agent.schemas import InvestigationDecision


def test_the_scorer_only_accepts_verdicts_the_schema_permits() -> None:
    """Scoring for a value the model can never emit fails silently. Pinned against the schema
    rather than against a list written here, so the two cannot drift."""
    from typing import get_args

    permitted = set(get_args(InvestigationDecision.model_fields["verdict"].annotation))
    assert set(va.VERDICTS) == permitted


def test_a_verdict_outside_the_schema_is_refused_loudly() -> None:
    with pytest.raises(ValueError, match="unknown verdict"):
        va.score_verdict("false_positive", has_outcome=False)


@pytest.mark.parametrize(
    "verdict, has_outcome, expected",
    [
        ("genuine", True, "caught"),
        ("false_alarm", True, "missed"),
        ("insufficient_evidence", True, "missed"),
        ("false_alarm", False, "dismissed"),
        ("genuine", False, "escalated_anyway"),
        ("insufficient_evidence", False, "escalated_anyway"),
    ],
)
def test_the_four_buckets(verdict: str, has_outcome: bool, expected: str) -> None:
    assert va.score_verdict(verdict, has_outcome) == expected


def test_abstaining_is_wrong_on_both_arms() -> None:
    """`insufficient_evidence` is an honest answer and a useless one for a reviewer. Folding it
    into "not a false alarm" would let a model that never commits score well."""
    assert va.score_verdict("insufficient_evidence", True) == "missed"
    assert va.score_verdict("insufficient_evidence", False) == "escalated_anyway"


def test_the_result_names_never_collide_with_the_verdict_names() -> None:
    """The first run printed `verdict=genuine  false_alarm` in adjacent columns, where the second
    word was the RESULT and read as a verdict. A reader should not have to know which column is
    which."""
    results = {
        va.score_verdict(v, o) for v in va.VERDICTS for o in (True, False)
    }
    assert not results & set(va.VERDICTS)


def test_the_percentile_is_nearest_rank_and_reports_a_real_observation() -> None:
    """At ten cases an interpolated p95 reports a latency no case actually had."""
    values = [10.0, 20.0, 30.0, 40.0]
    assert va._percentile(values, 0.5) in values
    assert va._percentile(values, 0.95) == 40.0
    assert va._percentile([], 0.5) == 0.0
