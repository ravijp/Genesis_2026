"""Layer 2: the investigator agent — loop, tools, decision schema, prompt loading.

No module in this package may import the corpus generator or a ground-truth type. The tools see
`latent_risk` and a seed; they never see an outcome. See `tests/test_separation.py`.
"""

from __future__ import annotations

from .investigator import (
    MAX_SCHEMA_RETRIES,
    MAX_STEPS,
    InvestigationTrace,
    StepRecord,
    investigate,
)
from .prompts import investigator_prompts, load_prompt, prompt, render
from .schemas import EvidenceRef, InvestigationDecision, OwningTeam, Verdict
from .tools import TOOLS, TOOLS_BY_NAME, Tool, ToolContext, ToolError, tool_specs, unresolved_evidence

__all__ = [
    "MAX_SCHEMA_RETRIES",
    "MAX_STEPS",
    "TOOLS",
    "TOOLS_BY_NAME",
    "EvidenceRef",
    "InvestigationDecision",
    "InvestigationTrace",
    "OwningTeam",
    "StepRecord",
    "Tool",
    "ToolContext",
    "ToolError",
    "Verdict",
    "investigate",
    "investigator_prompts",
    "load_prompt",
    "prompt",
    "render",
    "tool_specs",
    "unresolved_evidence",
]
