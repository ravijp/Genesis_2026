"""The reviewer API: five reads for the three screens, and one write for the audit trail.

    GET  /cases?status=open&limit=50                  the ranked queue          (screen 1)
    GET  /cases/{case_id}                             one case, evidence chain  (screen 2)
    GET  /cases/{case_id}/reviews                     who did what, and why     (screen 3)
    GET  /customers/{customer_id}/ledger              the standing ledger, re-scored now
    GET  /customers/{customer_id}/conversations/{id}  the transcript behind a quote
    POST /cases/{case_id}/reviews                     record a reviewer action

**One write, and it cannot touch evidence.** `POST .../reviews` appends to `ReviewStore` and moves
the case's status; it never edits a case's score or its evidence chain. Infrastructure.md S1.6 is
explicit that a write-back mutating the case in place destroys the audit trail on the one table a
regulator would ask for, and `CaseStore.update_status` is built so that it structurally cannot.
Q3 -- should a dismissal reduce the score, suppress the customer, or only annotate -- is answered
here the same way: **only annotate.**

**There is no outbound contact surface, and its absence is the control.** No endpoint emails,
calls, texts or messages a customer, and none queues anything that would. HITL is enforced by
there being nothing to enforce it against. If an endpoint that contacts anyone is ever added, that
guarantee is gone and the entry's claim goes with it.

**Nothing here can return an answer key.** Cases are read back exactly as `case_record()` wrote
them (no `stratum`, `outcome` or `latent_risk`), the ledger view is serialized by the same
`evidence_chain()` the case uses, and no endpoint reaches the corpus.
`tests/test_separation.py` covers this file by glob and `tests/test_api.py` scans every response
body for answer-key field names.

**Errors are JSON with a status, never a stack trace.** A 500 whose body is a traceback tells an
attacker the table names and tells a reviewer nothing.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import unquote

from ..case_record import evidence_chain
from ..config import ScoringConfig
from .ingest import DEFAULT_THRESHOLD
from .stores import CaseStore, LedgerStore, ReviewStore, table_name
from .transcripts import TranscriptArchive

DEFAULT_STAGE = "dev"
MAX_QUEUE_LIMIT = 200

# What a reviewer can do with a case. A closed set: `update_status` writes straight into the GSI
# partition key, so a free-text status would silently create a queue nothing lists.
ACTIONS: dict[str, str] = {
    "approve": "approved",
    "dismiss": "dismissed",
    "route": "routed",
}


class ApiError(Exception):
    """An HTTP error with a status. Anything else becomes a 500 with no detail in the body."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


class ReviewerApi:
    """The API as an object, so every store is injectable and `handler` is a thin wrapper."""

    def __init__(
        self,
        case_store: CaseStore,
        review_store: ReviewStore,
        ledger_store: LedgerStore,
        archive: TranscriptArchive,
        *,
        threshold: float = DEFAULT_THRESHOLD,
        scoring: ScoringConfig | None = None,
    ) -> None:
        self.cases = case_store
        self.reviews = review_store
        self.ledger_store = ledger_store
        self.archive = archive
        self.threshold = threshold
        self.scoring = scoring or ScoringConfig()

    # -- reads ---------------------------------------------------------------------------

    def list_queue(self, status: str = "open", limit: int = 50) -> dict[str, Any]:
        """The ranked queue, highest current score first. One GSI query, no scan."""
        if limit < 1 or limit > MAX_QUEUE_LIMIT:
            raise ApiError(400, f"limit must be between 1 and {MAX_QUEUE_LIMIT}")
        cases = self.cases.list_queue(status, limit=limit)
        return {
            "status": status,
            "count": len(cases),
            # The denominator a reviewer is looking at, not a rate. `count` is what this page
            # returned and `limit` is what it asked for; a truncated queue must be visible as
            # truncated rather than reading as "that is all of them".
            "limit": limit,
            "truncated": len(cases) == limit,
            "cases": [_queue_row(case) for case in cases],
        }

    def get_case(self, case_id: str) -> dict[str, Any]:
        case = self.cases.get_case(case_id)
        if case is None:
            raise ApiError(404, f"no case {case_id}")
        return case

    def list_reviews(self, case_id: str) -> dict[str, Any]:
        """Every action on this case, oldest first. Returns an empty list for a case nobody has
        touched -- and 404s for a case that does not exist, because those are different answers."""
        self.get_case(case_id)
        reviews = self.reviews.list_reviews(case_id)
        return {"case_id": case_id, "count": len(reviews), "reviews": reviews}

    def get_ledger(self, customer_id: str) -> dict[str, Any]:
        """The standing ledger, re-scored as of the customer's latest signal.

        This is the accumulation screen: every quote ever heard, what it supported when it landed
        and what it supports now. Scored by an unchanged `SignalLedger` -- this module, like every
        other one outside `memory.py`, does not compute a score.
        """
        ledger = self.ledger_store.load_ledger(customer_id, self.scoring)
        signals = ledger.signals(customer_id)
        if not signals:
            raise ApiError(404, f"no ledger entries for {customer_id}")
        as_of_day = max(s.day for s in signals)
        breakdown = ledger.best(customer_id, as_of_day)
        return {
            "customer_id": customer_id,
            "as_of_day": as_of_day,
            "signal_type": breakdown.signal_type.value,
            "score": breakdown.score,
            "threshold": self.threshold,
            "crossed": breakdown.score >= self.threshold,
            "n_signals": len(signals),
            # Every family, not only the top one: a reviewer looking at a churn case needs to see
            # the distress score sitting under it, and a UI that only ever shows the winner hides
            # exactly the accumulation this system is about.
            "by_signal_type": {
                st.value: ledger.score(customer_id, st, as_of_day).score
                for st in sorted({s.signal_type for s in signals}, key=lambda t: t.value)
            },
            "evidence": evidence_chain(breakdown.entries, self.threshold),
        }

    def get_conversation(self, customer_id: str, conversation_id: str) -> dict[str, Any]:
        """The transcript behind a quote, so a reviewer can read it in context rather than
        trusting the fragment the model chose to cite."""
        for conversation in self.archive.load(customer_id):
            if conversation.conversation_id == conversation_id:
                return {
                    "conversation_id": conversation.conversation_id,
                    "customer_id": conversation.customer_id,
                    "channel": conversation.channel.value,
                    "day": conversation.day,
                    "turns": [
                        {"index": t.index, "speaker": t.speaker, "text": t.text}
                        for t in conversation.turns
                    ],
                }
        raise ApiError(404, f"no conversation {conversation_id} for {customer_id}")

    # -- the one write --------------------------------------------------------------------

    def add_review(self, case_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Append a reviewer action and move the case's status. Never touches the evidence."""
        self.get_case(case_id)
        action = str(body.get("action", ""))
        if action not in ACTIONS:
            raise ApiError(400, f"action must be one of {sorted(ACTIONS)}")
        reviewer = str(body.get("reviewer", "")).strip()
        if not reviewer:
            # An anonymous entry in an audit trail is not an audit trail.
            raise ApiError(400, "reviewer is required")
        reason = str(body.get("reason", ""))
        if action == "dismiss" and not reason.strip():
            # The dismissals are the rows anyone will actually want to read later.
            raise ApiError(400, "a dismissal must carry a reason")

        review = self.reviews.put_review(
            case_id, reviewer=reviewer, action=action, reason=reason
        )
        self.cases.update_status(case_id, ACTIONS[action])
        return {"case_id": case_id, "status": ACTIONS[action], "review": review}


def _queue_row(case: dict[str, Any]) -> dict[str, Any]:
    """The ranked list shows a row, not a whole case: a queue of 200 cases each carrying its full
    evidence chain and model trace is megabytes of JSON to render a table."""
    decision = case.get("decision") or {}
    return {
        "case_id": case.get("case_id"),
        "customer_id": case.get("customer_id"),
        "signal_type": case.get("signal_type"),
        "score": case.get("score"),
        "score_at_open": case.get("score_at_open"),
        "threshold": case.get("threshold"),
        "opened_on_day": case.get("opened_on_day"),
        "as_of_day": case.get("as_of_day"),
        "status": case.get("status"),
        "n_evidence": len(case.get("evidence") or []),
        "verdict": decision.get("verdict"),
        "owning_team": decision.get("owning_team"),
        "confidence": decision.get("confidence"),
    }


# ---- routing -------------------------------------------------------------------------------------


def route(
    api: ReviewerApi,
    method: str,
    path: str,
    query: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Match a request to a handler. Separate from `handler` so every route is testable without
    constructing an API Gateway event, and so the event shape can change without touching this."""
    query = query or {}
    parts = [unquote(p) for p in path.strip("/").split("/") if p]

    if method == "GET" and parts == ["health"]:
        return 200, {"ok": True}

    if parts and parts[0] == "cases":
        if method == "GET" and len(parts) == 1:
            limit = _int_param(query, "limit", 50)
            return 200, api.list_queue(query.get("status", "open"), limit)
        if method == "GET" and len(parts) == 2:
            return 200, api.get_case(parts[1])
        if len(parts) == 3 and parts[2] == "reviews":
            if method == "GET":
                return 200, api.list_reviews(parts[1])
            if method == "POST":
                return 201, api.add_review(parts[1], body or {})

    if parts and parts[0] == "customers" and len(parts) >= 2:
        if method == "GET" and len(parts) == 3 and parts[2] == "ledger":
            return 200, api.get_ledger(parts[1])
        if method == "GET" and len(parts) == 4 and parts[2] == "conversations":
            return 200, api.get_conversation(parts[1], parts[3])

    raise ApiError(404, f"no route for {method} {path}")


def _int_param(query: dict[str, str], name: str, default: int) -> int:
    raw = query.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ApiError(400, f"{name} must be an integer, got {raw!r}") from exc


# ---- Lambda entrypoint -------------------------------------------------------------------------


def build_api() -> ReviewerApi:
    """Assembled from the environment. Called once per container, not once per request."""
    stage = os.environ.get("EARSHOT_STAGE", DEFAULT_STAGE)
    return ReviewerApi(
        CaseStore(table_name(stage, "cases")),
        ReviewStore(table_name(stage, "reviews")),
        LedgerStore(table_name(stage, "ledger")),
        TranscriptArchive(stage),
        threshold=float(os.environ.get("EARSHOT_THRESHOLD", DEFAULT_THRESHOLD)),
    )


_API: ReviewerApi | None = None


def _cors_headers() -> dict[str, str]:
    """Only when an origin is configured. Defaulting to `*` would publish a reviewer's case queue
    to any page a browser happens to load, and a default nobody set is a default nobody reviews."""
    origin = os.environ.get("EARSHOT_ALLOWED_ORIGIN")
    if not origin:
        return {}
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "content-type",
    }


def _response(status: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json", **_cors_headers()},
        "body": json.dumps(payload, default=str),
    }


def handler(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
    """API Gateway HTTP API (payload format 2.0) entrypoint. Never raises, never leaks a trace."""
    global _API
    if _API is None:
        _API = build_api()

    http = (event.get("requestContext") or {}).get("http") or {}
    method = str(http.get("method") or event.get("httpMethod") or "GET").upper()
    path = str(event.get("rawPath") or event.get("path") or "/")

    if method == "OPTIONS":
        return _response(204, {})

    raw_body = event.get("body")
    try:
        body = json.loads(raw_body) if raw_body else {}
        if not isinstance(body, dict):
            raise ApiError(400, "body must be a JSON object")
    except json.JSONDecodeError as exc:
        return _response(400, {"error": f"invalid JSON body: {exc}"})
    except ApiError as exc:
        return _response(exc.status, {"error": exc.message})

    try:
        status, payload = route(
            _API, method, path, event.get("queryStringParameters") or {}, body
        )
    except ApiError as exc:
        return _response(exc.status, {"error": exc.message})
    except Exception as exc:  # noqa: BLE001 -- a trace in a response body is an information leak
        print(json.dumps({"event": "api.error", "path": path, "error": f"{type(exc).__name__}"}))
        return _response(500, {"error": "internal error"})
    return _response(status, payload)


__all__ = [
    "ACTIONS",
    "ApiError",
    "ReviewerApi",
    "build_api",
    "handler",
    "route",
]
