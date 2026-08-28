"""The investigate handler: a crossing off the queue becomes a case file with cited evidence.

    SQS record -> LedgerStore -> SignalLedger -> TranscriptArchive -> investigate() -> CaseStore

**The loop is unchanged.** `agent/investigator.py` already enforces max 6 steps, max 2 retries, a
pre-flight cost cap, a tool-output cap, and a contract that it always returns a decision and never
raises (A9). This module assembles a `ToolContext` and calls it. Nothing here re-implements a step
limit, a retry, or a scoring rule -- if a change needs to alter how the agent reasons, it belongs
in `agent/`, where the tests for it are.

**Two things this handler must not do, both easy to reach for:**

1. **Score anything.** `LedgerStore.load_ledger()` returns an ordinary `SignalLedger` and
   `.best()` is the answer. A second scorer on the deployed path is the failure this whole
   architecture is arranged to prevent.
2. **Trust the message's score.** The queue message carries the score ingest computed, and by the
   time this runs another conversation may have landed. So the score is **recomputed from the
   ledger** and the message's copy is used only to detect that drift, never as the number of
   record. A case file quoting a stale score is a case file a reviewer cannot reconcile.

**The account tools are synthetic, and the case says so.** `core/accounts.py` derives transactions
and prior cases from `(customer_id, latent_risk, seed, as_of_day)`. Locally `latent_risk` is the
corpus's `financial_state`; in deployment there is no bank core feed to read, so the handler draws
it deterministically from the customer id (`_synthetic_risk`) -- fiction, stable per customer,
derived from nothing real. The alternative, one constant for everybody, makes every account
identical, which is a worse thing to put on a screen than a labelled synthetic one. Every case this
handler writes carries `account_data: "synthetic"` so no reviewer UI can present it as a bank
record. **When a real feed exists, this is the seam it replaces.**

**No answer key can reach here.** `latent_risk` is drawn from a hash of the customer id, not from a
truth object; there is no corpus import, and `tests/test_separation.py` covers this file by glob.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from ..agent import ToolContext, investigate
from ..case_record import make_case_id
from ..config import ScoringConfig
from ..llm.base import LLMProvider
from ..schema import SignalType
from .metrics import COUNT, MILLISECONDS, NONE, emit
from .stores import CaseStore, LedgerStore, table_name
from .transcripts import TranscriptArchive, TranscriptError

# Ceiling on model spend for one case. Mirrors `cli.py:COST_CAP_PER_CASE_USD` -- deliberately a
# copy rather than an import, because `cli.py` pulls in the corpus and this module may not.
# `tests/test_investigate_handler.py` asserts the two numbers agree, so the duplication is checked
# rather than hoped for.
COST_CAP_PER_CASE_USD = 0.25

DEFAULT_STAGE = "dev"

# What the ledger records for a customer whose account we cannot see. Never a measurement.
SYNTHETIC_ACCOUNT_MARKER = "synthetic"


class CrossingError(ValueError):
    """A queue message that is not a usable crossing. Fails that record alone."""


def _synthetic_risk(customer_id: str) -> float:
    """A stable, meaningless number in [0, 1) for a customer with no bank feed behind them.

    SHA-256 rather than `hash()`: Python's string hash is salted per process, so the same customer
    would get a different synthetic account on every cold start and two investigations of one
    customer would disagree about their transactions.
    """
    digest = hashlib.sha256(customer_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def parse_crossing(payload: Any) -> dict[str, Any]:
    """Strict parse of one investigations-queue message, as published by `ingest.Ingestor`.

    `score` is accepted and deliberately not trusted -- see the module docstring. `signal_type` is
    validated against the enum here rather than deep inside the context assembly, because a typo
    in a producer's payload should fail this record with a readable message, not surface as an
    investigation into a signal family that does not exist.
    """
    if not isinstance(payload, dict):
        raise CrossingError(f"crossing must be a JSON object, got {type(payload).__name__}")
    missing = {"customer_id", "signal_type", "threshold"} - set(payload)
    if missing:
        raise CrossingError(f"crossing is missing {sorted(missing)}")
    try:
        signal_type = SignalType(payload["signal_type"])
    except ValueError as exc:
        known = ", ".join(s.value for s in SignalType)
        raise CrossingError(
            f"unknown signal_type {payload['signal_type']!r}; known: {known}"
        ) from exc
    return {
        "customer_id": str(payload["customer_id"]),
        "signal_type": signal_type,
        "threshold": float(payload["threshold"]),
        "reported_score": float(payload["score"]) if "score" in payload else None,
    }


class Investigator:
    """The investigate path as an object, so every collaborator is injectable and `handler` is a
    thin wrapper rather than the only way to run this code."""

    def __init__(
        self,
        provider: LLMProvider,
        ledger_store: LedgerStore,
        case_store: CaseStore,
        archive: TranscriptArchive,
        *,
        cost_cap_usd: float | None = COST_CAP_PER_CASE_USD,
        scoring: ScoringConfig | None = None,
    ) -> None:
        self.provider = provider
        self.ledger_store = ledger_store
        self.case_store = case_store
        self.archive = archive
        self.cost_cap_usd = cost_cap_usd
        self.scoring = scoring or ScoringConfig()

    def context(self, customer_id: str, signal_type: SignalType, threshold: float) -> ToolContext:
        """Assemble the agent's view of one customer from DynamoDB and S3.

        The local equivalent is `cli.py:_context`, which reads the same fields off a corpus truth
        object. The two must stay the same shape: an investigator that sees a different context in
        deployment than in evaluation has an accuracy number that means nothing.
        """
        ledger = self.ledger_store.load_ledger(customer_id, self.scoring)
        signals = ledger.signals(customer_id)
        if not signals:
            raise CrossingError(f"no ledger entries for {customer_id}; nothing to investigate")
        as_of_day = max(s.day for s in signals)
        breakdown = ledger.score(customer_id, signal_type, as_of_day)
        conversations = self.archive.load(customer_id)
        if not conversations:
            # Failing loudly beats investigating: with no transcripts every citation is
            # unresolvable, the loop spends its whole retry budget rejecting its own decisions,
            # and the case that lands says "insufficient evidence" about a customer who has
            # plenty. The DLQ is the right place for this, and it names the real cause.
            raise CrossingError(
                f"no archived transcripts for {customer_id}; every citation would be "
                f"unresolvable (see aws/transcripts.py)"
            )
        return ToolContext(
            customer_id=customer_id,
            as_of_day=as_of_day,
            seed=0,  # the account synthesiser's stream selector; the customer id carries identity
            latent_risk=_synthetic_risk(customer_id),
            signal_type=signal_type.value,
            score=breakdown.score,
            threshold=threshold,
            conversations=conversations,
            breakdown=breakdown,
        )

    def run(
        self,
        customer_id: str,
        signal_type: SignalType,
        threshold: float,
        *,
        reported_score: float | None = None,
    ) -> dict[str, Any]:
        """One crossing in, one persisted case out. Returns the log record, not the case."""
        ctx = self.context(customer_id, signal_type, threshold)
        decision, trace = investigate(ctx, self.provider, cost_cap_usd=self.cost_cap_usd)

        ledger = self.ledger_store.load_ledger(customer_id, self.scoring)
        opened = ledger.open_case(customer_id, signal_type, threshold)
        breakdown = ctx.breakdown
        if opened is None:
            # The customer no longer clears the cut anywhere on their timeline -- decay, or a
            # threshold raised since the message was enqueued. Do not invent a crossing to hang
            # the case on; drop it and say why. The ledger keeps every signal regardless.
            return {
                "event": "investigate.no_longer_crossing",
                "customer_id": customer_id,
                "signal_type": signal_type.value,
                "score": round(breakdown.score, 6) if breakdown else None,
                "threshold": threshold,
            }

        case_id = self.case_store.put_case(
            opened,
            threshold=threshold,
            now=breakdown,
            decision=decision.model_dump(),
            trace={**trace.to_dict(), "account_data": SYNTHETIC_ACCOUNT_MARKER},
        )
        return {
            "event": "investigate.ok",
            "case_id": case_id,
            "customer_id": customer_id,
            "signal_type": signal_type.value,
            "score": round(ctx.score, 6),
            "threshold": threshold,
            # Named `score_when_enqueued` rather than `score`: the two differ whenever a
            # conversation landed between the crossing and this run, and the recomputed one is
            # the number of record.
            "score_when_enqueued": reported_score,
            "score_drifted": reported_score is not None
            and round(reported_score, 6) != round(ctx.score, 6),
            "cost_usd": trace.cost_usd,
            # Model time, not wall clock. In replay the two differ by ~50x, and one number
            # labelled neither is how "2 investigations in 1.2s" ends up beside a per-case 33s.
            "latency_ms": trace.latency_ms,
            "model_calls": trace.model_calls,
            "stopped_because": trace.stopped_because,
            "evidence_repairs": trace.evidence_repairs,
        }


# ---- Lambda entrypoint -------------------------------------------------------------------------


def _provider_from_env() -> LLMProvider:
    """Explicit `if`/`elif`, never a registry -- `aws/__init__.py` forbids dynamic imports on the
    guarded surface. `offline` is a rule engine, not a model: it exists so the deployed path can be
    smoke-tested with no Bedrock access and no spend, and its verdicts are a floor, not a result."""
    name = os.environ.get("EARSHOT_PROVIDER", "bedrock")
    if name == "bedrock":
        from ..llm.bedrock import BedrockProvider  # noqa: PLC0415 -- keeps cold start keyless

        return BedrockProvider()
    if name == "offline":
        from ..llm.offline import OfflineProvider  # noqa: PLC0415

        return OfflineProvider()
    raise CrossingError(f"unknown EARSHOT_PROVIDER {name!r}; known: bedrock, offline")


def build_investigator() -> Investigator:
    """Assembled from the environment. Called once per container, not once per record."""
    stage = os.environ.get("EARSHOT_STAGE", DEFAULT_STAGE)
    return Investigator(
        _provider_from_env(),
        LedgerStore(table_name(stage, "ledger")),
        CaseStore(table_name(stage, "cases")),
        TranscriptArchive(stage),
        cost_cap_usd=float(os.environ.get("EARSHOT_COST_CAP_USD", COST_CAP_PER_CASE_USD)),
    )


_INVESTIGATOR: Investigator | None = None


def handler(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
    """SQS batch entrypoint. Returns `batchItemFailures` so a poison record fails alone.

    Batch size should be 1 in the event-source mapping: an investigation is the expensive unit of
    work here, and a batch of ten that times out on the tenth redelivers the nine already paid for.
    The handler is written to survive a larger batch anyway, because an event-source mapping is a
    console setting and console settings drift.
    """
    global _INVESTIGATOR
    if _INVESTIGATOR is None:
        _INVESTIGATOR = build_investigator()

    failures: list[dict[str, str]] = []
    for record in event.get("Records", []):
        message_id = record.get("messageId", "")
        try:
            crossing = parse_crossing(json.loads(record["body"]))
            logged = _INVESTIGATOR.run(
                crossing["customer_id"],
                crossing["signal_type"],
                crossing["threshold"],
                reported_score=crossing["reported_score"],
            )
        except Exception as exc:  # noqa: BLE001 -- the contract is "this record failed", not why
            emit(
                "investigate.failed",
                {"Failed": (1, COUNT)},
                properties={
                    "messageId": message_id,
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )
            failures.append({"itemIdentifier": message_id})
            continue
        _emit_investigation(logged)
    return {"batchItemFailures": failures}


def _emit_investigation(logged: dict[str, Any]) -> None:
    """One EMF line per investigation.

    `stopped_because` is a DIMENSION here and nowhere else: its cardinality is bounded by the
    loop's own exit reasons, and the distribution across them is the most diagnostic number this
    system produces. A shift toward `cost_cap` or `max_steps` is the agent degrading, and it moves
    before any accuracy metric does.
    """
    if logged["event"] != "investigate.ok":
        emit(
            logged["event"],
            {"NoLongerCrossing": (1, COUNT)},
            properties={k: v for k, v in logged.items() if k != "event"},
        )
        return
    emit(
        "investigate.ok",
        {
            "Investigated": (1, COUNT),
            "CostUsd": (round(logged.get("cost_usd") or 0.0, 6), NONE),
            "ModelCalls": (logged.get("model_calls") or 0, COUNT),
            # First-attempt failures, not post-retry ones: a decision whose citations do not
            # resolve is rejected inside the loop, so this is the groundedness signal AT-57 asks
            # for. Taken off the returned decision it would be a structural zero.
            "EvidenceRepairs": (logged.get("evidence_repairs") or 0, COUNT),
            "ScoreDrifted": (1 if logged.get("score_drifted") else 0, COUNT),
            "LatencyMs": (round(logged.get("latency_ms") or 0.0, 3), MILLISECONDS),
        },
        dimensions={"StoppedBecause": str(logged.get("stopped_because") or "unknown")},
        properties={
            k: v
            for k, v in logged.items()
            if k
            not in {
                "event",
                "cost_usd",
                "model_calls",
                "evidence_repairs",
                "score_drifted",
                "latency_ms",
                "stopped_because",
            }
        },
    )


__all__ = [
    "COST_CAP_PER_CASE_USD",
    "CrossingError",
    "Investigator",
    "SYNTHETIC_ACCOUNT_MARKER",
    "TranscriptError",
    "build_investigator",
    "handler",
    "make_case_id",
    "parse_crossing",
]
