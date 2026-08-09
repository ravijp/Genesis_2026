"""Every tool, in memory, with zero network and zero model.

The separation test proves the tools *cannot* import the answer key. These prove they do not
leak it by another route, and that the account they synthesise is informative without being a
readout of latent risk — which is the difference between an eval and a demo.
"""

from __future__ import annotations

import json
import statistics

import pytest
from pydantic import ValidationError

from earshot.agent.schemas import EvidenceRef
from earshot.agent.tools import (
    TOOLS,
    TOOLS_BY_NAME,
    AccountStateArgs,
    GetConversationArgs,
    GetTransactionsArgs,
    LedgerSummaryArgs,
    PriorCasesArgs,
    ToolContext,
    ToolError,
    get_account_state,
    get_conversation,
    get_ledger_summary,
    get_prior_cases,
    get_transactions,
    tool_specs,
    unresolved_evidence,
)
from earshot.core.accounts import account_snapshot, generate_history
from earshot.memory import SignalLedger
from earshot.schema import Channel, Conversation, ExtractedSignal, SignalType, Turn

SEED = 4242


def conversation(cid: str, day: int, quote: str, channel: Channel = Channel.CALL) -> Conversation:
    return Conversation(
        conversation_id=cid,
        customer_id="C1",
        channel=channel,
        day=day,
        turns=(
            Turn(0, "agent", "Thanks for calling, how can I help?"),
            Turn(1, "customer", quote),
            Turn(2, "agent", "Understood, let me note that."),
        ),
    )


def signal(cid: str, day: int, quote: str, channel: Channel = Channel.CALL) -> ExtractedSignal:
    return ExtractedSignal(
        customer_id="C1",
        conversation_id=cid,
        signal_type=SignalType.FINANCIAL_DISTRESS,
        confidence=0.4,
        evidence_quote=quote,
        turn_index=1,
        day=day,
        channel=channel,
    )


@pytest.fixture
def ctx() -> ToolContext:
    quotes = {
        "K0": "Money has been really tight since the hours were cut.",
        "K1": "I had to put the council tax on a credit card this month.",
        "K2": "We're behind on the rent and I don't know what to do.",
    }
    conversations = tuple(
        conversation(cid, day, quotes[cid], channel)
        for cid, day, channel in (
            ("K0", 10, Channel.CALL),
            ("K1", 40, Channel.CHAT),
            ("K2", 70, Channel.COMPLAINT),
        )
    )
    ledger = SignalLedger()
    ledger.extend([signal(c.conversation_id, c.day, quotes[c.conversation_id], c.channel)
                   for c in conversations])
    breakdown = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 70)
    return ToolContext(
        customer_id="C1",
        as_of_day=70,
        seed=SEED,
        latent_risk=0.7,
        signal_type=SignalType.FINANCIAL_DISTRESS.value,
        score=breakdown.score,
        threshold=0.5,
        conversations=conversations,
        breakdown=breakdown,
    )


# --- specs -------------------------------------------------------------------------


def test_specs_are_openai_shaped_and_derived_from_the_models() -> None:
    for tool in TOOLS:
        spec = tool.spec()
        assert spec["type"] == "function"
        assert spec["function"]["name"] == tool.name
        assert spec["function"]["description"]
        params = spec["function"]["parameters"]
        assert params["additionalProperties"] is False
        # Derived, not hand-written: the property set must equal the pydantic field set.
        assert set(params["properties"]) == set(tool.args_model.model_fields)


def test_every_spec_is_json_serialisable() -> None:
    json.dumps(tool_specs())


# --- the five tools ----------------------------------------------------------------


def test_ledger_summary_returns_the_whole_evidence_chain(ctx: ToolContext) -> None:
    result = get_ledger_summary(ctx, LedgerSummaryArgs())
    assert result.customer_id == "C1"
    assert result.n_conversations == 3
    assert len(result.entries) == 3
    assert [e.day for e in result.entries] == [10, 40, 70]
    # Retro re-scoring must be visible to the agent -- it is the reason the case exists.
    assert result.entries[0].score_at_write < result.entries[0].score_now


def test_ledger_summary_respects_max_entries(ctx: ToolContext) -> None:
    assert len(get_ledger_summary(ctx, LedgerSummaryArgs(max_entries=1)).entries) == 1


def test_get_conversation_returns_turns_with_indices(ctx: ToolContext) -> None:
    result = get_conversation(ctx, GetConversationArgs(conversation_id="K1"))
    assert result.channel == "chat"
    assert [t.index for t in result.turns] == [0, 1, 2]
    assert "council tax" in result.turns[1].text


def test_get_conversation_rejects_an_unknown_id(ctx: ToolContext) -> None:
    with pytest.raises(ToolError) as exc:
        get_conversation(ctx, GetConversationArgs(conversation_id="NOPE"))
    assert "K0" in str(exc.value)  # tells the model what it could have asked for


def test_transactions_are_bounded_and_internally_consistent(ctx: ToolContext) -> None:
    result = get_transactions(ctx, GetTransactionsArgs(max_rows=12))
    assert result.to_day == ctx.as_of_day
    assert result.from_day == ctx.as_of_day - 89
    assert len(result.rows) <= 12
    assert len(result.by_month) == 3
    assert result.total_credits > 0 and result.total_debits > 0
    assert result.rows == sorted(result.rows, key=lambda r: r.day)


def test_transactions_can_be_filtered_by_category(ctx: ToolContext) -> None:
    salary = get_transactions(ctx, GetTransactionsArgs(category="salary"))
    assert salary.n_matching >= 1
    assert {r.category for r in salary.rows} == {"salary"}


def test_account_state_matches_the_transactions_the_agent_can_see(ctx: ToolContext) -> None:
    account = get_account_state(ctx, AccountStateArgs())
    txns = get_transactions(ctx, GetTransactionsArgs(max_rows=60))
    assert account.current_balance == txns.closing_balance
    assert account.lowest_balance == txns.lowest_balance
    assert account.expected_salary_credits == 3


def test_prior_cases_are_deterministic_and_capped(ctx: ToolContext) -> None:
    first = get_prior_cases(ctx, PriorCasesArgs(limit=2))
    second = get_prior_cases(ctx, PriorCasesArgs(limit=2))
    assert first == second
    assert first.count <= 2


def test_tools_run_through_the_registry_with_raw_json_arguments(ctx: ToolContext) -> None:
    """The path a model call actually takes: a dict of arguments off the wire, in; JSON, out."""
    calls = {
        "get_ledger_summary": {},
        "get_transactions": {},
        "get_account_state": {},
        "get_prior_cases": {},
        "get_conversation": {"conversation_id": "K0"},
    }
    assert set(calls) == set(TOOLS_BY_NAME), "a tool was added without a test"
    for name, args in calls.items():
        json.dumps(TOOLS_BY_NAME[name].run(ctx, args), default=str)
    assert TOOLS_BY_NAME["get_conversation"].run(ctx, calls["get_conversation"])[
        "conversation_id"
    ] == "K0"


def test_registry_rejects_arguments_the_schema_forbids(ctx: ToolContext) -> None:
    with pytest.raises(ValidationError):
        TOOLS_BY_NAME["get_transactions"].run(ctx, {"window_days": 9999})
    with pytest.raises(ValidationError):
        TOOLS_BY_NAME["get_transactions"].run(ctx, {"not_a_field": 1})


# --- the honesty properties --------------------------------------------------------


def test_no_tool_result_mentions_an_outcome(ctx: ToolContext) -> None:
    """A tool that surfaced churn/default status would hand the agent the answer key."""
    blob = " ".join(
        json.dumps(TOOLS_BY_NAME[name].run(ctx, args), default=str).lower()
        for name, args in (
            ("get_ledger_summary", {}),
            ("get_transactions", {}),
            ("get_account_state", {}),
            ("get_prior_cases", {}),
            ("get_conversation", {"conversation_id": "K0"}),
        )
    )
    for forbidden in ("outcome", "churned", "delinquent", "latent_risk", "stratum"):
        assert forbidden not in blob, f"tool output leaks {forbidden!r}"


def test_transactions_are_deterministic_for_a_given_seed() -> None:
    a = generate_history("C1", 0.6, SEED, 120)
    b = generate_history("C1", 0.6, SEED, 120)
    assert a == b
    assert generate_history("C1", 0.6, SEED + 1, 120) != a


def _markers(snapshot) -> int:
    return sum(
        (
            snapshot.days_in_overdraft >= 14,
            snapshot.salary_credits < snapshot.expected_salary_credits,
            snapshot.returned_direct_debits >= 1,
            snapshot.balance_trend <= -250,
            snapshot.salary_change_pct <= -20,
        )
    )


def test_higher_latent_risk_shifts_the_account_but_does_not_determine_it() -> None:
    """Informative but ambiguous. If this test ever fails in the 'too clean' direction, the
    investigator's job has become a threshold check and the eval measures nothing."""
    low = [_markers(account_snapshot(f"C{i:04d}", 0.05, SEED, 150)) for i in range(150)]
    high = [_markers(account_snapshot(f"C{i:04d}", 0.85, SEED, 150)) for i in range(150)]

    assert statistics.mean(high) > statistics.mean(low) + 0.5, "transactions carry no signal"
    # The overlap is the point: some calm customers look bad and some stressed ones look fine.
    assert sum(m >= 2 for m in low) / len(low) > 0.05, "no low-risk customer ever looks bad"
    assert sum(m == 0 for m in high) / len(high) > 0.05, "every high-risk customer looks bad"


# --- evidence resolution -----------------------------------------------------------


def test_evidence_resolves_only_against_real_turns(ctx: ToolContext) -> None:
    good = EvidenceRef(
        conversation_id="K2", turn_index=1, quote="We're behind on the rent"
    )
    assert unresolved_evidence(ctx, [good]) == []

    bad = [
        EvidenceRef(conversation_id="NOPE", turn_index=1, quote="anything"),
        EvidenceRef(conversation_id="K2", turn_index=99, quote="anything"),
        EvidenceRef(conversation_id="K2", turn_index=1, quote="a quote nobody ever said"),
    ]
    problems = unresolved_evidence(ctx, bad)
    assert len(problems) == 3
    assert "not a conversation" in problems[0]
    assert "no such turn" in problems[1]
    assert "verbatim" in problems[2]
