"""The decision contract. Strict by construction, because "evidence is mandatory" has to be
mechanical rather than aspirational.

Two rules are enforced here and nowhere else:

* **At least one evidence reference.** `min_length=1` on `evidence` means a decision with no
  citation cannot be constructed at all — the failure happens at parse time and is counted as a
  schema repair. This is the answer to hallucinated justification.
* **No extra fields.** `extra="forbid"` stops a model inventing a `risk_score` or a
  `probability_of_churn` that then leaks into a report as though the system computed it.

Resolution of a reference against the corpus is *not* done here — the schema has no access to
conversations. That check lives in `tools.unresolved_evidence` and is applied by the loop.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Verdict = Literal["genuine", "false_alarm", "insufficient_evidence"]
OwningTeam = Literal["retention", "collections", "vulnerability", "complaints", "none"]


class EvidenceRef(BaseModel):
    """A pointer into a real conversation turn. Must be quotable, and must resolve."""

    model_config = ConfigDict(extra="forbid")

    conversation_id: str = Field(min_length=1)
    turn_index: int = Field(ge=0)
    quote: str = Field(min_length=1)


class InvestigationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1)
    verdict: Verdict
    owning_team: OwningTeam
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=1)
    recommended_action: str = Field(min_length=1)
    # Asked for explicitly because a decision that cannot be falsified is not a decision. It is
    # also the field a reviewer uses to decide what to check first.
    what_would_change_my_mind: str = Field(min_length=1)
    evidence: list[EvidenceRef] = Field(min_length=1)


def decision_schema_text() -> str:
    """The schema as the prompt shows it to the model. Generated, never hand-written."""
    import json

    return json.dumps(InvestigationDecision.model_json_schema(), indent=2)
