"""The live path, replayable: conversations arriving in wall-clock order, one frame each.

**What this is for.** Every other command in this repo answers a batch question -- generate a
corpus, score it, rank it, investigate the top of the queue. That hides the one thing the entry is
actually about, which is *accumulation over time*: a customer who says something faint in March,
something else in May, and crosses in July. `run_stream()` walks conversations in **global day
order across the whole book**, exactly as a production queue would deliver them, and records what
the system knew after each one.

**The output is a frame timeline, and the browser only plays it back.** Every score, delta and
crossing in a frame is computed here by `memory.py` -- the one scorer in this system. The UI reads
frames and animates them. It does not re-derive a number, because the moment a browser starts
scoring there are two scorers and they will disagree on stage.

**Honesty, stated where it is implemented rather than only in a caption.**

* There is **no speech recognition anywhere in this system.** A frame carries text that was
  generated as text. What the replay reproduces faithfully is the *arrival pattern* -- order,
  spacing, channel mix -- not an audio pipeline. `manifest.asr` says `"none"` on every run and
  the UI prints it.
* The threshold is a **fixed cut**, per tenant, mirroring `aws/ingest.py`. A streaming consumer
  sees one conversation at a time and has no population to rank against, so the budget-derived
  threshold in `cli._queue` cannot apply here. The two disagree about who crossed. That is a
  property of streaming, not a bug, and both numbers are labelled.
* The investigation runs **at the crossing**, on the evidence known then -- that is what a live
  consumer does. The case *record* is then built at the end of the stream with the customer's
  current breakdown, so `score_at_open` and `score` are two different moments, the same split
  `case_record.py` already enforces. Taking both from the crossing would freeze the retro chain
  on opening day and empty the beat for every customer who kept talking.

**This module cannot see the answer key, structurally.** It does not generate the corpus and it
does not build the agent's context -- both are handed in by `cli.py`, which is the one module
already exempted from the separation guard for exactly this reason. So `stream.py` sits on the
guarded surface with every other reader (`tests/test_separation.py` discovers it by glob), and it
could not reach `stratum`, `outcome` or `latent_risk` even if a future edit tried to: it never
holds the object they live on. `stream_payload()` asserts the same thing again at the boundary,
and `tools/stream_fixture.py` a third time before anything reaches a browser.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from .agent import InvestigationDecision, InvestigationTrace, ToolContext, investigate
from .aws.transcripts import to_payload
from .case_record import case_record
from .extract import Extractor
from .memory import ScoreBreakdown, SignalLedger
from .schema import Case, Conversation, SignalType
from .tenants import CANONICAL_TEAMS, Tenant

# How the caller turns a crossing into the agent's view of that customer. Supplied rather than
# built here: assembling a `ToolContext` needs the customer's financial state, which lives on the
# corpus side. Keeping the factory outside is what lets this module stay on the guarded surface.
ContextFactory = Callable[[str, ScoreBreakdown, float], ToolContext]

# How many customers the live board shows. A leaderboard is only legible if it fits on a screen
# beside the transcript, and the beat being demonstrated is re-ranking, not enumeration.
BOARD_SIZE = 8

# Ceiling on model spend for a single streamed investigation. Same value as `cli`, deliberately:
# a cap that differs by entrypoint is a cap someone can route around.
COST_CAP_PER_CASE_USD = 0.25

# Answer-key fields. Checked here as well as in `tools/stream_fixture.py` and the tests, because
# this module is the one place that holds a `Corpus` and a browser payload in the same scope.
ANSWER_KEY_FIELDS = frozenset(
    {
        "stratum",
        "outcome",
        "outcome_day",
        "latent_risk",
        "financial_state",
        "seeded",
        "seeded_signals",
        "lead_days",
        "trajectory",
    }
)


class StreamError(RuntimeError):
    """Something makes the stream unrunnable. Named, not a traceback."""


@dataclass
class Crossing:
    """A customer clearing the threshold, and what the agent made of it at that moment."""

    customer_id: str
    signal_type: SignalType
    day: int
    frame_index: int
    conversation_id: str
    score_at_cross: float
    decision: InvestigationDecision | None = None
    trace: InvestigationTrace | None = None
    # Why no agent ran, when none did. A blank case on screen must say which of "the budget was
    # spent" and "the provider failed" happened, or a demo answers the question wrongly.
    skipped: str | None = None


@dataclass
class StreamRun:
    tenant: Tenant
    ledger: SignalLedger
    final_day: int = 0
    frames: list[dict[str, Any]] = field(default_factory=list)
    crossings: list[Crossing] = field(default_factory=list)
    conversations: dict[str, dict[str, Any]] = field(default_factory=dict)
    reader_cost_usd: float = 0.0
    investigation_cost_usd: float = 0.0
    elapsed_seconds: float = 0.0


def arrival_order(conversations: Sequence[Conversation]) -> list[Conversation]:
    """Every conversation in the book, in the order a live queue would deliver them.

    Sorted by day across ALL customers, not grouped by customer. That interleaving is the whole
    point: it is what makes the board re-rank between two conversations of the same arc, and it
    is the difference between demonstrating a stream and demonstrating a batch with a timer on it.
    """
    return sorted(conversations, key=lambda c: (c.day, c.conversation_id))


def _reader_snapshot(extractor: Extractor) -> tuple[float, float, int]:
    """`(cost_usd, latency_ms_total, model_calls)` so far, or zeros for a keyless extractor.

    Snapshot-and-diff rather than a per-call hook: `ExtractionTelemetry` is the measured record
    the published cost-per-1,000 figure comes from, and a second counter maintained here could
    disagree with it. Diffing the one that is already authoritative cannot.
    """
    telemetry = getattr(extractor, "telemetry", None)
    if telemetry is None:
        return 0.0, 0.0, 0
    return telemetry.cost_usd, sum(telemetry.latencies_ms), telemetry.model_calls


def _board(
    ledger: SignalLedger, seen: list[str], day: int, threshold: float, opened: dict[str, str]
) -> list[dict[str, Any]]:
    """The ranked board as of `day`: who a reviewer would look at right now.

    Recomputed over every customer heard so far, not incrementally patched. Under decay every
    score moves when the day advances, including the scores of customers who said nothing --
    which is exactly the behaviour worth showing, and an incremental update would miss it.
    """
    rows = []
    for customer_id in seen:
        breakdown = ledger.best(customer_id, day)
        if breakdown.score <= 0:
            continue
        rows.append(
            {
                "customer_id": customer_id,
                "signal_type": breakdown.signal_type.value,
                "score": round(breakdown.score, 4),
                "n_entries": len(breakdown.entries),
                "case_id": opened.get(customer_id),
                "state": "case" if customer_id in opened
                else "over" if breakdown.score >= threshold
                else "watch",
            }
        )
    rows.sort(key=lambda r: (-r["score"], r["customer_id"]))
    return rows[:BOARD_SIZE]


def run_stream(
    t: Tenant,
    conversations: Sequence[Conversation],
    extractor: Extractor,
    provider: Any,
    *,
    context_for: ContextFactory,
    investigate_limit: int | None = None,
    on_frame: Callable[[dict[str, Any]], None] | None = None,
    on_investigated: Callable[[Crossing], None] | None = None,
) -> StreamRun:
    """Walk one tenant's book in arrival order and record a frame per conversation.

    `on_frame` and `on_investigated` are called as each completes, which is what `--serve` pushes
    to a browser. Batch callers pass neither and read `run.frames` at the end; there is one code
    path either way, so the live server and the recorded replay cannot drift about what a frame is.
    """
    started = time.time()
    limit = t.investigate if investigate_limit is None else investigate_limit
    ordered = arrival_order(conversations)
    if not ordered:
        raise StreamError(f"{t.tenant_id} has no conversations to stream")
    ledger = SignalLedger(t.run.scoring)
    run = StreamRun(
        tenant=t, ledger=ledger, final_day=max(c.day for c in ordered)
    )

    seen: list[str] = []
    opened: dict[str, str] = {}
    pending: list[Crossing] = []

    for index, conversation in enumerate(ordered):
        customer_id = conversation.customer_id
        day = conversation.day
        cost_before, latency_before, calls_before = _reader_snapshot(extractor)

        # The score the system held for this customer the instant before this conversation
        # landed, on this day -- so any movement in the frame is caused by this conversation and
        # not by the calendar advancing. Comparing against a score taken on an earlier day would
        # attribute decay to the arrival.
        before = ledger.best(customer_id, day) if customer_id in seen else None

        signals = extractor.extract(conversation)
        for signal in sorted(signals, key=lambda s: (s.turn_index,)):
            ledger.append(signal)

        if customer_id not in seen:
            seen.append(customer_id)
        after = ledger.best(customer_id, day)

        cost_after, latency_after, calls_after = _reader_snapshot(extractor)
        run.reader_cost_usd += cost_after - cost_before
        read_calls = calls_after - calls_before

        crossed = (
            after.score >= t.threshold
            and customer_id not in opened
            and (before is None or before.score < t.threshold)
        )
        crossing: Crossing | None = None
        if crossed:
            case_id = f"{customer_id}:{after.signal_type.value}:{after.as_of_day}"
            opened[customer_id] = case_id
            crossing = Crossing(
                customer_id=customer_id,
                signal_type=after.signal_type,
                day=day,
                frame_index=index,
                conversation_id=conversation.conversation_id,
                score_at_cross=round(after.score, 4),
            )
            pending.append(crossing)

        run.conversations[conversation.conversation_id] = to_payload(conversation)
        frame = {
            "i": index,
            "day": day,
            "conversation_id": conversation.conversation_id,
            "customer_id": customer_id,
            "channel": conversation.channel.value,
            "n_turns": len(conversation.turns),
            "signals": [
                {
                    "signal_type": s.signal_type.value,
                    "confidence": round(s.confidence, 3),
                    "turn_index": s.turn_index,
                    "quote": s.evidence_quote,
                }
                for s in sorted(signals, key=lambda s: s.turn_index)
            ],
            "signal_type": after.signal_type.value if after.score > 0 else None,
            "score_before": round(before.score, 4) if before is not None else 0.0,
            "score_after": round(after.score, 4),
            "n_entries": len(after.entries),
            "ledger_size": sum(len(ledger.signals(c)) for c in seen),
            "customers_seen": len(seen),
            "crossed": crossed,
            "case_id": opened.get(customer_id) if crossed else None,
            # Per-conversation read cost and latency, from the reader's own telemetry. Zero and
            # absent for the keyless lexicon, which is honest: a regex costs nothing and a screen
            # that showed a made-up figure for it would be inventing evidence of spend.
            "reader": {
                "model_calls": read_calls,
                "cost_usd": round(cost_after - cost_before, 6),
                "latency_ms": round(latency_after - latency_before, 1),
            },
            "board": _board(ledger, seen, day, t.threshold, opened),
        }
        run.frames.append(frame)
        if on_frame is not None:
            on_frame(frame)

    # -- the agent, at each crossing, in arrival order, up to the tenant's budget ---------------
    #
    # Deliberately after the walk rather than inside it. The scoring above is pure code and takes
    # milliseconds; an investigation takes ~20 seconds and would otherwise stall the stream a
    # judge is watching. The caller's `context_for` cuts the transcripts at the crossing day, so
    # each agent still sees what a live consumer would have handed it and nothing that arrived
    # later.
    for crossing in pending[:limit]:
        breakdown = ledger.score(crossing.customer_id, crossing.signal_type, crossing.day)
        ctx = context_for(crossing.customer_id, breakdown, t.threshold)
        try:
            decision, trace = investigate(ctx, provider, cost_cap_usd=COST_CAP_PER_CASE_USD)
        except Exception as exc:  # provider failure, spend ceiling, malformed reply
            crossing.skipped = f"{type(exc).__name__}: {exc}"
            if on_investigated is not None:
                on_investigated(crossing)
            continue
        crossing.decision = decision
        crossing.trace = trace
        run.investigation_cost_usd += trace.cost_usd
        if on_investigated is not None:
            on_investigated(crossing)
    for crossing in pending[limit:]:
        crossing.skipped = f"beyond this tenant's investigation budget of {limit}"

    run.crossings = pending
    run.elapsed_seconds = time.time() - started
    return run


def _case_records(run: StreamRun) -> dict[str, dict[str, Any]]:
    """One case record per investigated crossing, built at the end of the stream.

    Two moments, kept apart, the same way `cli._case_record` keeps them: `opened` supplies the
    crossing facts (`opened_on_day`, `opened_by_conversation`, `score_at_open`) and `now` supplies
    the customer as they stand at the end of the book -- current score, and the whole evidence
    chain including everything that landed after the case opened. That second half is what the
    retro screen renders; taking it from the crossing would leave the beat empty.
    """
    t = run.tenant
    final_day = run.final_day
    records: dict[str, dict[str, Any]] = {}
    for crossing in run.crossings:
        if crossing.decision is None or crossing.trace is None:
            continue
        now = run.ledger.score(crossing.customer_id, crossing.signal_type, final_day)
        opened = run.ledger.open_case(crossing.customer_id, crossing.signal_type, t.threshold)
        if opened is None:
            # Reachable only if the current score clears the cut while no point on the timeline
            # ever did. Under decay that cannot happen; this guards a future scoring change.
            opened = Case(
                customer_id=crossing.customer_id,
                signal_type=crossing.signal_type,
                score=crossing.score_at_cross,
                opened_on_day=crossing.day,
                opened_by_conversation=crossing.conversation_id,
                evidence=list(now.entries),
            )
        record = case_record(
            opened,
            threshold=t.threshold,
            now=now,
            decision=crossing.decision.model_dump(),
            trace=crossing.trace.to_dict(),
        )
        record["tenant_id"] = t.tenant_id
        # The local name for the canonical routing slot. Added here rather than in the browser so
        # the mapping is applied once, server-side, and a screenshot cannot show a team name the
        # tenant profile does not actually define.
        record["team_label"] = t.team_label(crossing.decision.owning_team)
        record["frame_index"] = crossing.frame_index
        records[record["case_id"]] = record
    return records


def _team_rollup(records: dict[str, dict[str, Any]], t: Tenant) -> list[dict[str, Any]]:
    """Cases per routing destination -- the "which team picks this up" view.

    Every canonical slot is listed even at zero. A rollup that hides empty teams reads as "this
    tenant has three teams", and the absence of routing to one of them is itself a finding: it is
    how AT-57's non-discrimination shows up on a dashboard.
    """
    counts: dict[str, int] = {slot: 0 for slot in CANONICAL_TEAMS}
    unrouted = 0
    for record in records.values():
        slot = (record.get("decision") or {}).get("owning_team")
        if slot in counts:
            counts[slot] += 1
        else:
            unrouted += 1
    rows = [
        {"team": slot, "label": t.team_label(slot), "cases": counts[slot]}
        for slot in CANONICAL_TEAMS
    ]
    if unrouted:
        rows.append({"team": "none", "label": t.team_label(None), "cases": unrouted})
    return rows


def _all_keys(obj: Any) -> set[str]:
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in _all_keys(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in _all_keys(v)}
    return set()


def stream_payload(run: StreamRun, manifest: dict[str, Any]) -> dict[str, Any]:
    """The whole run, in the shape the browser reads. Refuses to leak the answer key."""
    t = run.tenant
    records = _case_records(run)
    investigated = len(records)
    crossings = len(run.crossings)
    payload = {
        "manifest": manifest,
        "tenant": t.public(),
        "frames": run.frames,
        "cases": records,
        "conversations": run.conversations,
        "teams": _team_rollup(records, t),
        "totals": {
            "customers": len({f["customer_id"] for f in run.frames}),
            "conversations": len(run.frames),
            "signals": sum(len(f["signals"]) for f in run.frames),
            "crossings": crossings,
            "investigated": investigated,
            # Named "not investigated" rather than omitted. A demo that shows 4 cases from 11
            # crossings and does not say so is claiming a precision it did not measure.
            "not_investigated": crossings - investigated,
            "horizon_days": max((f["day"] for f in run.frames), default=0),
            "reader_cost_usd": round(run.reader_cost_usd, 6),
            "investigation_cost_usd": round(run.investigation_cost_usd, 6),
            "total_cost_usd": round(run.reader_cost_usd + run.investigation_cost_usd, 6),
            "elapsed_seconds": round(run.elapsed_seconds, 2),
        },
        # Why each crossing does or does not have a case behind it. On screen next to the queue,
        # so "only four were investigated" is visible rather than inferable.
        "unworked": [
            {
                "customer_id": c.customer_id,
                "day": c.day,
                "signal_type": c.signal_type.value,
                "score": c.score_at_cross,
                "reason": c.skipped,
            }
            for c in run.crossings
            if c.decision is None
        ],
    }
    leaked = _all_keys(payload) & ANSWER_KEY_FIELDS
    if leaked:
        raise StreamError(f"answer-key fields would reach the browser: {sorted(leaked)}")
    return payload
