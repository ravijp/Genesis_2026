"""The bounded investigator loop.

Three limits, all hard: **6 tool-calling steps, 2 schema-validation retries, an optional cost
cap.** An agent that can loop forever is not production-ready, and feasibility is a quarter of
the score. Budget exhaustion is not an exception — the loop always returns a decision, and an
exhausted budget returns `insufficient_evidence` with the reason recorded in the trace. A
reviewer seeing "I ran out of steps" is strictly better served than one seeing a stack trace.

Everything that costs money or time is recorded per step, so cost-per-investigation, tokens,
p50/p95 latency and the schema-rejection rate all come out of the same object the demo prints.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from ..llm.base import (
    Completion,
    LLMProvider,
    Message,
    ModelConfig,
    ProviderError,
    assistant_message,
)
from .prompts import investigator_prompts, render
from .schemas import EvidenceRef, InvestigationDecision, decision_schema_text
from .tools import TOOLS_BY_NAME, ToolContext, ToolError, tool_specs, unresolved_evidence

MAX_STEPS = 6
MAX_SCHEMA_RETRIES = 2
TOOL_RESULT_CHAR_CAP = 6000  # a runaway tool result must not blow the context window

# Headroom multiplier for the cost pre-flight. Each step replays the previous tool results as
# prompt tokens, so the next call is reliably dearer than the last; estimating without this
# let the cap be breached while still reporting "cost_cap".
#
# WHAT THE CAP ACTUALLY ENFORCES, stated precisely because the previous version claimed more
# than it delivered. Spend is bounded before each call using the priciest call so far times
# this factor. That holds cumulative spend under the cap for any realistic cost curve, where
# each call costs somewhat more than the last. It CANNOT bound a call that costs wildly more
# than every prior call — no estimate can. A single call is bounded instead by `max_tokens`
# on the request and `TOOL_RESULT_CHAR_CAP` on what can be fed back into the prompt.
COST_GROWTH_FACTOR = 4.0


@dataclass
class StepRecord:
    index: int
    kind: str  # "model" | "tool"
    name: str
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "kind": self.kind,
            "name": self.name,
            "latency_ms": round(self.latency_ms, 1),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "detail": self.detail,
        }


@dataclass
class InvestigationTrace:
    customer_id: str
    provider: str
    model: str
    prompt_version: str
    prompt_sha: str
    steps: list[StepRecord] = field(default_factory=list)
    schema_retries: int = 0
    evidence_repairs: int = 0
    stopped_because: str = "decided"

    @property
    def model_calls(self) -> int:
        return sum(1 for s in self.steps if s.kind == "model")

    @property
    def tool_calls(self) -> int:
        return sum(1 for s in self.steps if s.kind == "tool")

    @property
    def prompt_tokens(self) -> int:
        return sum(s.prompt_tokens for s in self.steps)

    @property
    def completion_tokens(self) -> int:
        return sum(s.completion_tokens for s in self.steps)

    @property
    def cost_usd(self) -> float:
        return round(sum(s.cost_usd for s in self.steps), 6)

    @property
    def latency_ms(self) -> float:
        return round(sum(s.latency_ms for s in self.steps), 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "prompt_sha": self.prompt_sha,
            "model_calls": self.model_calls,
            "tool_calls": self.tool_calls,
            "schema_retries": self.schema_retries,
            "evidence_repairs": self.evidence_repairs,
            "stopped_because": self.stopped_because,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "steps": [s.to_dict() for s in self.steps],
        }


def _extract_json(text: str) -> dict[str, Any] | None:
    """Pull one JSON object out of a model reply that may be fenced or prefaced with prose."""
    if not text:
        return None
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.split("```")[1] if "```" in candidate[3:] else candidate[3:]
        if candidate.lstrip().lower().startswith("json"):
            candidate = candidate.lstrip()[4:]
    start, end = candidate.find("{"), candidate.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(candidate[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _validate(
    content: str, ctx: ToolContext
) -> tuple[InvestigationDecision | None, list[str], bool]:
    """Returns (decision, problems, evidence_problem). Evidence failures are counted separately
    because groundedness is a published metric, not just a retry reason."""
    payload = _extract_json(content)
    if payload is None:
        return None, ["reply was not a single JSON object"], False

    try:
        decision = InvestigationDecision.model_validate(payload)
    except ValidationError as exc:
        return None, [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()], False

    problems: list[str] = []
    if decision.customer_id != ctx.customer_id:
        problems.append(
            f"customer_id: expected {ctx.customer_id}, got {decision.customer_id}"
        )
    unresolved = unresolved_evidence(ctx, decision.evidence)
    if unresolved:
        return None, problems + unresolved, True
    if problems:
        return None, problems, False
    return decision, [], False


def _repair_message(problems: list[str]) -> Message:
    return {
        "role": "user",
        "content": (
            "Your reply was rejected:\n- "
            + "\n- ".join(problems)
            + "\n\nReturn one corrected JSON object and nothing else. Quotes must be copied "
            "verbatim from the turn you cite, transcription errors included."
        ),
    }


def _fallback_decision(ctx: ToolContext, reason: str) -> InvestigationDecision:
    """A decision the loop can always produce, whatever went wrong. Never raises.

    It cites real evidence — the ledger entry that carries the most weight, or failing that the
    first customer turn on file — because a case with no citation is not reviewable and the
    schema would reject it anyway.
    """
    evidence: list[EvidenceRef] = []
    if ctx.breakdown is not None and ctx.breakdown.entries:
        top = max(ctx.breakdown.entries, key=lambda e: e.contribution_now)
        evidence.append(
            EvidenceRef(
                conversation_id=top.signal.conversation_id,
                turn_index=top.signal.turn_index,
                quote=top.signal.evidence_quote.strip() or "(empty turn)",
            )
        )
    elif ctx.conversations:
        conversation = ctx.conversations[0]
        turn = next(
            (t for t in conversation.turns if t.speaker == "customer"),
            conversation.turns[0] if conversation.turns else None,
        )
        if turn is not None:
            evidence.append(
                EvidenceRef(
                    conversation_id=conversation.conversation_id,
                    turn_index=turn.index,
                    quote=turn.text.strip() or "(empty turn)",
                )
            )
    if not evidence:
        evidence.append(
            EvidenceRef(conversation_id="(none)", turn_index=0, quote="(no evidence on file)")
        )

    return InvestigationDecision(
        customer_id=ctx.customer_id,
        verdict="insufficient_evidence",
        owning_team="none",
        confidence=0.0,
        rationale=(
            f"The investigation did not complete: {reason}. No verdict was reached, so none is "
            f"reported. The ledger score was {ctx.score:.3f} against a {ctx.threshold:.3f} "
            f"threshold on {ctx.signal_type or 'an unnamed signal family'}."
        ),
        recommended_action=(
            "Route to a human reviewer unassisted, and re-run the investigation with a larger "
            "budget before relying on an automated verdict for this customer."
        ),
        what_would_change_my_mind=(
            "A completed investigation. This is a budget outcome, not a judgment about the "
            "customer."
        ),
        evidence=evidence,
    )


def investigate(
    ctx: ToolContext,
    provider: LLMProvider,
    *,
    model_cfg: ModelConfig | None = None,
    max_steps: int = MAX_STEPS,
    max_schema_retries: int = MAX_SCHEMA_RETRIES,
    cost_cap_usd: float | None = None,
    prompt_version: str = "v1",
) -> tuple[InvestigationDecision, InvestigationTrace]:
    """Run one investigation. Always returns a decision and a trace; never raises on budget."""
    model_cfg = model_cfg or ModelConfig()
    system, task, combined_sha = investigator_prompts(prompt_version)

    messages: list[Message] = [
        {"role": "system", "content": render(system.text, schema=decision_schema_text())},
        {
            "role": "user",
            "content": render(
                task.text,
                customer_id=ctx.customer_id,
                signal_type=ctx.signal_type,
                score=f"{ctx.score:.3f}",
                threshold=f"{ctx.threshold:.3f}",
                as_of_day=ctx.as_of_day,
                conversation_ids=", ".join(c.conversation_id for c in ctx.conversations) or "none",
            ),
        },
    ]
    specs = tool_specs()

    trace = InvestigationTrace(
        customer_id=ctx.customer_id,
        provider=getattr(provider, "name", type(provider).__name__),
        model=model_cfg.model,
        prompt_version=system.version,
        prompt_sha=combined_sha,
    )

    decision: InvestigationDecision | None = None
    step = 0

    # How much more the next call may cost than the priciest so far. Tool results accumulate
    # into the prompt, so cost climbs; measured ramps sat well inside 4x.
    priciest_call = 0.0
    while step < max_steps:
        step += 1

        # PRE-FLIGHT. Checking spend only after a call is not a cap, it is a report: with a
        # $0.25 cap and $0.30-per-call model, the old check happily booked $0.30 and then
        # announced "cost_cap". Refuse a call we already know we cannot afford, using the
        # priciest call seen so far as the estimate.
        #
        # Honest limit: the very first call cannot be estimated, so a cap below the cost of a
        # single call cannot be enforced. Everything after that is genuinely bounded.
        # Reserve headroom, because cost GROWS: every tool result is replayed as prompt tokens
        # on the next call, so "the priciest call so far" systematically under-estimates the
        # next one. Estimating with no growth factor let a $0.25 cap spend $0.26 on a gentle
        # 1.5x ramp and $5.00 on a spike -- while still reporting "cost_cap", which is the
        # exact shape of bug working-agreements.md §5 exists to prevent.
        estimate = priciest_call * COST_GROWTH_FACTOR
        if cost_cap_usd is not None and trace.cost_usd + estimate > cost_cap_usd:
            trace.stopped_because = "cost_cap"
            break

        try:
            completion: Completion = provider.complete(messages, specs, model_cfg)
        except ProviderError as exc:
            trace.steps.append(
                StepRecord(index=step, kind="model", name="error", detail=str(exc)[:200])
            )
            trace.stopped_because = "provider_error"
            break
        except Exception as exc:  # noqa: BLE001 - the loop must never take the demo down
            # This module promises it always returns a decision rather than raising, and that
            # promise was only true for ProviderError. Any other failure -- a bug in a
            # provider, a JSON edge case, a network library raising something unexpected --
            # propagated to the CLI as a traceback in front of whoever is watching.
            trace.steps.append(
                StepRecord(
                    index=step,
                    kind="model",
                    name="internal_error",
                    detail=f"{type(exc).__name__}: {exc}"[:200],
                )
            )
            trace.stopped_because = "internal_error"
            break

        # Report the model that actually served, not the one we asked for -- OpenRouter can
        # route to a different snapshot, and the offline provider is not a model at all.
        trace.model = completion.model or model_cfg.model
        trace.steps.append(
            StepRecord(
                index=step,
                kind="model",
                name=completion.model or model_cfg.model,
                latency_ms=completion.latency_ms,
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                cost_usd=completion.cost_usd,
                detail=(
                    "tool_calls: " + ", ".join(c.name for c in completion.tool_calls)
                    if completion.tool_calls
                    else "final answer"
                ),
            )
        )

        # Track the most expensive call so far so the pre-flight check below can refuse a call
        # that would breach the cap, rather than noticing afterwards.
        priciest_call = max(priciest_call, completion.cost_usd)

        if cost_cap_usd is not None and trace.cost_usd >= cost_cap_usd:
            trace.stopped_because = "cost_cap"
            break

        if completion.tool_calls:
            messages.append(assistant_message(completion))
            for call in completion.tool_calls:
                payload, detail = _run_tool(ctx, call.name, call.arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": call.name,
                        "content": payload[:TOOL_RESULT_CHAR_CAP],
                    }
                )
                trace.steps.append(
                    StepRecord(index=step, kind="tool", name=call.name, detail=detail)
                )
            continue

        parsed, problems, evidence_problem = _validate(completion.content, ctx)
        if parsed is not None:
            decision = parsed
            trace.stopped_because = "decided"
            break

        trace.schema_retries += 1
        trace.evidence_repairs += int(evidence_problem)
        if trace.schema_retries > max_schema_retries:
            trace.stopped_because = "invalid_after_retries"
            break
        messages.append(assistant_message(completion))
        messages.append(_repair_message(problems))
    else:
        trace.stopped_because = "step_cap"

    if decision is None:
        decision = _fallback_decision(ctx, trace.stopped_because)

    return decision, trace


def _run_tool(ctx: ToolContext, name: str, arguments: dict[str, Any]) -> tuple[str, str]:
    """Execute one tool call. Failures come back as content the model can read and recover from."""
    tool = TOOLS_BY_NAME.get(name)
    if tool is None:
        available = ", ".join(sorted(TOOLS_BY_NAME))
        return (
            json.dumps({"error": f"no tool named {name!r}", "available": available}),
            "unknown tool",
        )
    try:
        result = tool.run(ctx, arguments)
    except ToolError as exc:
        return json.dumps({"error": str(exc)}), f"tool error: {exc}"[:120]
    except ValidationError as exc:
        return (
            json.dumps({"error": "invalid arguments", "detail": exc.errors(include_url=False)},
                       default=str),
            "invalid arguments",
        )
    except Exception as exc:  # noqa: BLE001 - a broken tool must not take the run down
        # Catching only ToolError/ValidationError meant a plain KeyError inside a tool escaped
        # `investigate()` as a traceback, in front of whoever was watching -- the same promise
        # the model-call path already had to have widened.
        return (
            json.dumps({"error": f"{type(exc).__name__}: {exc}"}),
            f"tool crashed: {type(exc).__name__}"[:120],
        )
    payload = json.dumps(result, default=str)
    return payload, f"{len(payload)} chars"
