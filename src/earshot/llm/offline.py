"""Offline provider: a valid decision with no key, no network, and no pretence.

This exists so the whole product runs for someone with no credentials and no wifi. It is
**not** a stand-in for model judgment, and it says so in its own output rather than leaving a
reader to assume a model was involved.

What it does: walks a fixed tool plan, then applies a crude scoring rule over what the tools
returned. What it cannot do: read the conversations, weigh ambiguity, notice that a returned
direct debit lands the week after a bereavement, or explain itself in language a reviewer would
recognise. Its confidence is capped at 0.75 for that reason, it reports zero tokens and zero
cost because no model ran, and its verdicts are reported in the eval as the offline arm — never
folded in with real-model numbers.

Constrained deliberately: the honest baseline is the one that makes the
model's contribution measurable.
"""

from __future__ import annotations

import json
import time
from typing import Any

from .base import Completion, Message, ModelConfig, ToolCall, ToolSpec, Usage

# Fixed plan: evidence chain first, then corroboration, then history. A real agent chooses;
# this one does not, and the trace makes that visible.
PLAN = (
    "get_ledger_summary",
    "get_transactions",
    "get_account_state",
    "get_prior_cases",
)

TEAM_BY_SIGNAL = {
    "churn_intent": "retention",
    "financial_distress": "collections",
    "complaint_escalation": "complaints",
    "life_event": "vulnerability",
}

ACTION_BY_TEAM = {
    "retention": "Queue for a retention call before the next renewal date; do not discount blind.",
    "collections": "Offer a pre-arrears affordability conversation; suppress automated chasing.",
    "complaints": "Escalate to a complaints handler with the full evidence chain attached.",
    "vulnerability": "Flag for a vulnerability-trained agent; apply support measures, not sales.",
    "none": "No action. Leave the signals in the ledger to be re-scored next batch.",
}


class OfflineProvider:
    """Deterministic, rule-based, and openly worse than a model. That is the point."""

    name = "offline-rules"

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion:
        started = time.perf_counter()
        results = _tool_results(messages)
        available = {spec.get("function", {}).get("name") for spec in tools}

        for tool_name in PLAN:
            if tool_name in available and tool_name not in results:
                return Completion(
                    tool_calls=(ToolCall(id=f"offline-{tool_name}", name=tool_name, arguments={}),),
                    usage=Usage(),  # no model ran; reporting a token estimate would be a lie
                    latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
                    cost_usd=0.0,
                    model=self.name,
                )

        decision = _decide(results)
        return Completion(
            content=json.dumps(decision, indent=2),
            usage=Usage(),
            latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
            cost_usd=0.0,
            model=self.name,
        )


def _tool_results(messages: list[Message]) -> dict[str, dict[str, Any]]:
    """Latest parsed payload per tool name, from the transcript so far."""
    out: dict[str, dict[str, Any]] = {}
    for message in messages:
        if message.get("role") != "tool":
            continue
        name = message.get("name") or ""
        try:
            payload = json.loads(message.get("content") or "{}")
        except json.JSONDecodeError:
            payload = {}
        if name:
            out[name] = payload if isinstance(payload, dict) else {"value": payload}
    return out


def _markers(account: dict[str, Any]) -> list[str]:
    """Account-side corroboration. Each marker is weak; the rule only counts them."""
    found: list[str] = []
    if int(account.get("days_in_overdraft", 0)) >= 14:
        found.append(f"{account['days_in_overdraft']} days in overdraft")
    expected = int(account.get("expected_salary_credits", 0))
    credits = int(account.get("salary_credits", 0))
    if expected and credits < expected:
        found.append(f"{credits} of {expected} expected salary credits")
    if int(account.get("returned_direct_debits", 0)) >= 1:
        found.append(f"{account['returned_direct_debits']} returned direct debit(s)")
    if float(account.get("balance_trend", 0.0)) <= -250.0:
        found.append(f"balance down {abs(float(account['balance_trend'])):.0f} over the window")
    if float(account.get("salary_change_pct", 0.0)) <= -20.0:
        found.append(f"income down {abs(float(account['salary_change_pct'])):.0f}%")
    return found


def _decide(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ledger = results.get("get_ledger_summary", {})
    account = results.get("get_account_state", {})
    prior = results.get("get_prior_cases", {})

    signal_type = str(ledger.get("signal_type", ""))
    conversations = int(ledger.get("n_conversations", 0))
    entries = [e for e in ledger.get("entries", []) if isinstance(e, dict)]
    markers = _markers(account)
    n = len(markers)

    already_handled = any(
        case.get("signal_type") == signal_type and case.get("resolution") == "resolved"
        for case in prior.get("cases", [])
        if isinstance(case, dict)
    )

    if n >= 2:
        verdict = "genuine"
    elif n == 1 and conversations >= 3:
        verdict = "genuine"
    elif n == 0 and (conversations <= 2 or already_handled):
        verdict = "false_alarm"
    else:
        verdict = "insufficient_evidence"

    team = "none" if verdict != "genuine" else TEAM_BY_SIGNAL.get(signal_type, "none")
    confidence = min(0.75, 0.30 + 0.11 * n + 0.04 * max(0, conversations - 1))

    evidence = [
        {
            "conversation_id": entry.get("conversation_id", ""),
            "turn_index": int(entry.get("turn_index", 0)),
            "quote": entry.get("quote", ""),
        }
        for entry in sorted(entries, key=lambda e: -float(e.get("contribution_now", 0.0)))[:2]
        if entry.get("conversation_id") and entry.get("quote")
    ]

    corroboration = ", ".join(markers) if markers else "no account-side corroboration"
    rationale = (
        f"Rule-based offline provider (no model call). The ledger holds {len(entries)} "
        f"{signal_type or 'signal'} entries across {conversations} conversation(s), scoring "
        f"{float(ledger.get('score', 0.0)):.3f} against a {float(ledger.get('threshold', 0.0)):.3f} "
        f"threshold. Account check found {corroboration}. "
        f"{'Prior case on this family was already resolved. ' if already_handled else ''}"
        f"Counting {n} corroborating marker(s) gives '{verdict}'. No natural-language reading "
        f"of the conversations was performed."
    )

    return {
        "customer_id": ledger.get("customer_id", ""),
        "verdict": verdict,
        "owning_team": team,
        "confidence": round(confidence, 2),
        "rationale": rationale,
        "recommended_action": ACTION_BY_TEAM[team],
        "what_would_change_my_mind": (
            "A reading of the quoted turns showing the remark was about someone else, or a "
            "salary credit landing on schedule next cycle, would drop this to a false alarm. "
            "A second returned direct debit would raise it."
        ),
        "evidence": evidence,
    }
