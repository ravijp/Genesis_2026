"""The investigator's tools: plain functions over a `ToolContext`, no LLM import anywhere.

Three properties, each there for a reason:

1. **Pure and synchronous.** Every tool is `(ctx, args) -> result`, so the whole surface is
   unit-testable with no network and no model — see `tests/test_tools.py`. A tool that needed a
   client to test would not get tested.
2. **Schemas are derived, never typed twice.** `.spec()` renders the OpenAI function schema from
   the pydantic args model, so the wire contract cannot drift from the validation the tool
   actually performs. Hand-written JSON schemas rot silently.
3. **The context carries primitives, not truth.** The caller assembles `ToolContext` and passes
   `risk_signal` down as a number. Nothing here can reach an outcome, a stratum, or a seeded
   signal — `tests/test_separation.py` covers this file by glob and will fail if that changes.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..core.accounts import (
    WINDOW_DAYS,
    PriorCase,
    Transaction,
    account_snapshot,
    generate_history,
    synthesize_prior_cases,
)
from ..memory import ScoreBreakdown
from ..schema import Conversation


class ToolError(RuntimeError):
    """A tool was called with arguments that do not resolve. Reported to the model, not raised."""


@dataclass(frozen=True)
class ToolContext:
    """Everything the tools may see about one customer. Assembled by the caller.

    `risk_signal` is a generative parameter (it drives synthetic transactions the way real
    financial stress drives real ones). It is named `risk_signal`, not `latent_risk`, on
    purpose: `CustomerTruth.latent_risk` (see `schema.py`) is the answer-key-adjacent field this
    context must never carry, and the two now have different names so that `risk_signal =
    truth.latent_risk` reads as the error it would be. The outcome — whether this customer
    actually churned or defaulted — is deliberately absent and must stay absent.
    """

    customer_id: str
    as_of_day: int
    seed: int
    risk_signal: float
    signal_type: str
    score: float
    threshold: float
    conversations: tuple[Conversation, ...] = ()
    breakdown: ScoreBreakdown | None = None
    prior_cases: tuple[PriorCase, ...] | None = None
    _txn_cache: dict[int, list[Transaction]] = field(default_factory=dict, repr=False)

    def transactions(self, window_days: int = WINDOW_DAYS) -> list[Transaction]:
        """Memoised so repeated tool calls inside one investigation see one consistent account."""
        if window_days not in self._txn_cache:
            self._txn_cache[window_days] = generate_history(
                self.customer_id, self.risk_signal, self.seed, self.as_of_day, window_days
            )
        return self._txn_cache[window_days]

    def cases(self) -> tuple[PriorCase, ...]:
        if self.prior_cases is not None:
            return self.prior_cases
        return synthesize_prior_cases(
            self.customer_id, self.risk_signal, self.seed, self.as_of_day
        )


# --- result / argument models ------------------------------------------------------


class LedgerEntryView(BaseModel):
    conversation_id: str
    turn_index: int
    day: int
    channel: str
    quote: str
    confidence: float
    contribution_now: float
    score_at_write: float
    score_now: float
    load_bearing: bool


class LedgerSummaryArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_entries: int = Field(
        default=20, ge=1, le=50, description="Cap on evidence-chain entries returned."
    )


class LedgerSummaryResult(BaseModel):
    customer_id: str
    signal_type: str
    score: float
    threshold: float
    as_of_day: int
    n_conversations: int
    conversation_ids: list[str]
    entries: list[LedgerEntryView]


class GetConversationArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str = Field(
        description="Conversation id, e.g. CUST-0007-C2. Ids come from get_ledger_summary."
    )


class TurnView(BaseModel):
    index: int
    speaker: str
    text: str


class ConversationResult(BaseModel):
    conversation_id: str
    customer_id: str
    channel: str
    day: int
    turns: list[TurnView]


class GetTransactionsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    window_days: int = Field(
        default=WINDOW_DAYS, ge=7, le=WINDOW_DAYS, description="Days of history ending today."
    )
    category: str | None = Field(
        default=None,
        description=(
            "Optional filter: salary, housing, utilities, groceries, transport, "
            "discretionary, fees, transfer, savings."
        ),
    )
    max_rows: int = Field(default=20, ge=1, le=60, description="Cap on individual rows returned.")


class TransactionRow(BaseModel):
    day: int
    description: str
    category: str
    amount: float
    balance_after: float


class MonthBucket(BaseModel):
    from_day: int
    to_day: int
    credits: float
    debits: float
    closing_balance: float


class TransactionsResult(BaseModel):
    customer_id: str
    window_days: int
    from_day: int
    to_day: int
    opening_balance: float
    closing_balance: float
    lowest_balance: float
    total_credits: float
    total_debits: float
    net_by_category: dict[str, float]
    by_month: list[MonthBucket]
    n_matching: int
    rows: list[TransactionRow]


class AccountStateArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    window_days: int = Field(
        default=WINDOW_DAYS, ge=7, le=WINDOW_DAYS, description="Window the summary is computed over."
    )


class AccountStateResult(BaseModel):
    customer_id: str
    as_of_day: int
    product: str
    tenure_months: int
    current_balance: float
    overdraft_limit: float
    days_in_overdraft: int
    lowest_balance: float
    balance_trend: float
    salary_credits: int
    expected_salary_credits: int
    median_salary_credit: float
    salary_change_pct: float
    returned_direct_debits: int
    fee_charges: int
    essential_spend: float
    discretionary_spend: float
    savings_balance: float


class PriorCasesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=5, ge=1, le=20, description="Maximum prior cases to return.")


class PriorCaseView(BaseModel):
    case_id: str
    opened_on_day: int
    signal_type: str
    owning_team: str
    resolution: str
    note: str


class PriorCasesResult(BaseModel):
    customer_id: str
    count: int
    cases: list[PriorCaseView]


# --- the tools ---------------------------------------------------------------------


def get_ledger_summary(ctx: ToolContext, args: LedgerSummaryArgs) -> LedgerSummaryResult:
    """The evidence chain that opened this case, with then-vs-now contribution per quote."""
    entries: list[LedgerEntryView] = []
    breakdown = ctx.breakdown
    if breakdown is not None:
        ordered = sorted(breakdown.entries, key=lambda e: e.signal.day)
        for entry in ordered[: args.max_entries]:
            entries.append(
                LedgerEntryView(
                    conversation_id=entry.signal.conversation_id,
                    turn_index=entry.signal.turn_index,
                    day=entry.signal.day,
                    channel=entry.signal.channel.value,
                    quote=entry.signal.evidence_quote.strip(),
                    confidence=round(entry.signal.confidence, 4),
                    contribution_now=round(entry.contribution_now, 4),
                    score_at_write=round(entry.score_at_write, 4),
                    score_now=round(entry.score_now, 4),
                    load_bearing=entry.is_load_bearing(ctx.threshold),
                )
            )

    return LedgerSummaryResult(
        customer_id=ctx.customer_id,
        signal_type=ctx.signal_type,
        score=round(ctx.score, 4),
        threshold=round(ctx.threshold, 4),
        as_of_day=ctx.as_of_day,
        n_conversations=len({e.conversation_id for e in entries}),
        conversation_ids=[c.conversation_id for c in ctx.conversations],
        entries=entries,
    )


def get_conversation(ctx: ToolContext, args: GetConversationArgs) -> ConversationResult:
    """Full transcript of one conversation, so a quote can be checked in context."""
    for conversation in ctx.conversations:
        if conversation.conversation_id == args.conversation_id:
            return ConversationResult(
                conversation_id=conversation.conversation_id,
                customer_id=conversation.customer_id,
                channel=conversation.channel.value,
                day=conversation.day,
                turns=[
                    TurnView(index=t.index, speaker=t.speaker, text=t.text)
                    for t in conversation.turns
                ],
            )
    known = ", ".join(c.conversation_id for c in ctx.conversations) or "none"
    raise ToolError(f"unknown conversation_id {args.conversation_id!r}. Available: {known}")


def get_transactions(ctx: ToolContext, args: GetTransactionsArgs) -> TransactionsResult:
    """Account activity that either corroborates or refutes what was said on the call."""
    txns = ctx.transactions(args.window_days)
    from_day = ctx.as_of_day - args.window_days + 1

    opening = round(txns[0].balance_after - txns[0].amount, 2) if txns else 0.0
    closing = txns[-1].balance_after if txns else opening

    net_by_category: dict[str, float] = {}
    for t in txns:
        net_by_category[t.category] = round(net_by_category.get(t.category, 0.0) + t.amount, 2)

    buckets: list[MonthBucket] = []
    span = max(1, args.window_days // 3)
    for i in range(3):
        lo = from_day + i * span
        hi = ctx.as_of_day if i == 2 else lo + span - 1
        window = [t for t in txns if lo <= t.day <= hi]
        buckets.append(
            MonthBucket(
                from_day=lo,
                to_day=hi,
                credits=round(sum(t.amount for t in window if t.amount > 0), 2),
                debits=round(sum(-t.amount for t in window if t.amount < 0), 2),
                closing_balance=window[-1].balance_after if window else closing,
            )
        )

    matching = [t for t in txns if args.category is None or t.category == args.category]
    # Rows are a sample, not the ledger: everything unusual (fees, returned debits, salary) plus
    # the largest movements. A full 90-day dump would cost more tokens than it is worth.
    notable = [t for t in matching if t.category in ("fees", "salary") or "RETURNED" in t.description]
    rest = sorted(
        (t for t in matching if t not in notable), key=lambda t: -abs(t.amount)
    )
    rows = sorted(notable + rest[: max(0, args.max_rows - len(notable))], key=lambda t: t.day)

    return TransactionsResult(
        customer_id=ctx.customer_id,
        window_days=args.window_days,
        from_day=from_day,
        to_day=ctx.as_of_day,
        opening_balance=opening,
        closing_balance=closing,
        lowest_balance=round(min((t.balance_after for t in txns), default=opening), 2),
        total_credits=round(sum(t.amount for t in txns if t.amount > 0), 2),
        total_debits=round(sum(-t.amount for t in txns if t.amount < 0), 2),
        net_by_category=net_by_category,
        by_month=buckets,
        n_matching=len(matching),
        rows=[
            TransactionRow(
                day=t.day,
                description=t.description,
                category=t.category,
                amount=t.amount,
                balance_after=t.balance_after,
            )
            for t in rows[: args.max_rows]
        ],
    )


def get_account_state(ctx: ToolContext, args: AccountStateArgs) -> AccountStateResult:
    """The account screen a servicing agent would have open while reading the case."""
    snapshot = account_snapshot(
        ctx.customer_id,
        ctx.risk_signal,
        ctx.seed,
        ctx.as_of_day,
        args.window_days,
        transactions=ctx.transactions(args.window_days),
    )
    return AccountStateResult(**vars(snapshot))


def get_prior_cases(ctx: ToolContext, args: PriorCasesArgs) -> PriorCasesResult:
    """What a human already decided about this customer. Stops us re-opening settled cases."""
    cases = ctx.cases()[: args.limit]
    return PriorCasesResult(
        customer_id=ctx.customer_id,
        count=len(cases),
        cases=[
            PriorCaseView(
                case_id=c.case_id,
                opened_on_day=c.opened_on_day,
                signal_type=c.signal_type,
                owning_team=c.owning_team,
                resolution=c.resolution,
                note=c.note,
            )
            for c in cases
        ],
    )


# --- registry ----------------------------------------------------------------------


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    result_model: type[BaseModel]
    fn: Callable[[ToolContext, Any], BaseModel]

    def spec(self) -> dict[str, Any]:
        """OpenAI-style function schema, derived from the pydantic model. Never hand-written."""
        schema = self.args_model.model_json_schema()
        schema.pop("title", None)
        schema["additionalProperties"] = False
        schema.setdefault("properties", {})
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }

    def run(self, ctx: ToolContext, raw_args: dict[str, Any] | None = None) -> dict[str, Any]:
        args = self.args_model.model_validate(raw_args or {})
        return self.fn(ctx, args).model_dump()


TOOLS: tuple[Tool, ...] = (
    Tool(
        name="get_ledger_summary",
        description=(
            "Read the standing signal ledger for this customer: the score, the threshold it "
            "crossed, and every retained quote with what it contributed when it arrived versus "
            "what it supports now. Start here."
        ),
        args_model=LedgerSummaryArgs,
        result_model=LedgerSummaryResult,
        fn=get_ledger_summary,
    ),
    Tool(
        name="get_conversation",
        description=(
            "Fetch the full transcript of one conversation by id, with turn indices, so a quote "
            "can be read in context and checked for who it was actually about."
        ),
        args_model=GetConversationArgs,
        result_model=ConversationResult,
        fn=get_conversation,
    ),
    Tool(
        name="get_transactions",
        description=(
            "Current-account transactions over the last 90 days with per-category and per-month "
            "totals. Use it to corroborate or refute what the customer said."
        ),
        args_model=GetTransactionsArgs,
        result_model=TransactionsResult,
        fn=get_transactions,
    ),
    Tool(
        name="get_account_state",
        description=(
            "Summary account state: balance, overdraft use, salary-credit regularity, returned "
            "direct debits, fees, and essential versus discretionary spend."
        ),
        args_model=AccountStateArgs,
        result_model=AccountStateResult,
        fn=get_account_state,
    ),
    Tool(
        name="get_prior_cases",
        description=(
            "Cases already raised on this customer and how a human resolved them. Check before "
            "recommending anything a team has already done or explicitly dismissed."
        ),
        args_model=PriorCasesArgs,
        result_model=PriorCasesResult,
        fn=get_prior_cases,
    ),
)

TOOLS_BY_NAME: dict[str, Tool] = {tool.name: tool for tool in TOOLS}


def tool_specs() -> list[dict[str, Any]]:
    return [tool.spec() for tool in TOOLS]


def _normalise(text: str) -> str:
    return " ".join(text.split()).casefold()


# A citation has to carry enough of the turn to be checkable by a person reading the case. Below
# this it is not evidence: `""` is a substring of every turn, and so is a single letter.
MIN_QUOTE_WORDS = 4


def unresolved_evidence(ctx: ToolContext, refs: list[Any]) -> list[str]:
    """Which of these citations do NOT resolve against the corpus?

    Empty list means every reference points at a real turn and quotes a contiguous run of at
    least `MIN_QUOTE_WORDS` of its words. This is the groundedness check the architecture
    promises. It lives in code the eval can call rather than inside the loop, so a first-attempt
    failure rate can be measured; the loop itself rejects and retries, so a decision that
    survives to the caller always resolves.

    Three things a plain substring test certifies that are not evidence, all closed here:

    * **The empty string is a substring of every turn.** A whitespace-only quote passed, so a
      decision could cite a real turn containing none of its words and be called verbatim.
    * **So is a single character.** A quote has to carry enough of the turn that a reviewer can
      check it, which is a floor in WORDS, not characters.
    * **A substring can invert the sentence it came from.** "I don't use half of what I'm paying
      for" contains "use half of what I'm paying for", which says the opposite. Requiring word
      boundaries does not fix meaning-inversion in general, but it stops the mid-word splicing
      that makes it trivial, and the floor makes a dropped leading negation visible in the case
      file because the surrounding words come with it.
    """
    by_id = {c.conversation_id: c for c in ctx.conversations}
    problems: list[str] = []
    for ref in refs:
        conversation = by_id.get(ref.conversation_id)
        if conversation is None:
            problems.append(f"{ref.conversation_id}: not a conversation for this customer")
            continue
        turn = next((t for t in conversation.turns if t.index == ref.turn_index), None)
        if turn is None:
            problems.append(
                f"{ref.conversation_id} turn {ref.turn_index}: no such turn "
                f"(valid 0-{len(conversation.turns) - 1})"
            )
            continue
        quote_words = _normalise(ref.quote).split()
        if len(quote_words) < MIN_QUOTE_WORDS:
            problems.append(
                f"{ref.conversation_id} turn {ref.turn_index}: quote is {len(quote_words)} "
                f"word(s); cite at least {MIN_QUOTE_WORDS} consecutive words of the turn"
            )
            continue
        turn_words = _normalise(turn.text).split()
        # Word-sequence containment, not substring: a substring test matches mid-word and lets a
        # citation start or end inside a token.
        if not any(
            turn_words[i : i + len(quote_words)] == quote_words
            for i in range(len(turn_words) - len(quote_words) + 1)
        ):
            problems.append(
                f"{ref.conversation_id} turn {ref.turn_index}: quote is not verbatim from "
                f"that turn"
            )
    return problems
