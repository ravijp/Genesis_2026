"""The reviewer API: routing, the one write, and the guarantees a client-facing surface carries.

Fake DynamoDB and fake S3, so this runs the real routing and the real stores with no AWS.

Four claims are load-bearing rather than incidental, and each has a test that would fail loudly:

* **no answer key leaves the API** — every response body is scanned for ground-truth field names;
* **no endpoint contacts anyone** — the route table is asserted against, because HITL in this
  system is enforced by the absence of an outbound surface, not by a check somewhere;
* **a review never mutates evidence** — Q3 in infrastructure.md is answered "only annotate";
* **an unexpected error returns no stack trace** — a traceback in a body names the tables.
"""

from __future__ import annotations

import json

import pytest
from test_investigate_handler import conversations, signals
from test_stores import FakeTable
from test_transcripts import FakeS3

from earshot.aws import api as api_mod
from earshot.aws.api import ApiError, ReviewerApi, handler, route
from earshot.aws.stores import CaseStore, LedgerStore, ReviewStore
from earshot.aws.transcripts import TranscriptArchive
from earshot.memory import SignalLedger
from earshot.schema import SignalType

ANSWER_KEY_FIELDS = {
    "stratum",
    "outcome",
    "outcome_day",
    "latent_risk",
    "financial_state",
    "seeded",
    "seeded_signals",
    "lead_days",
}


def _keys(obj) -> set[str]:
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in _keys(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in _keys(v)}
    return set()


@pytest.fixture
def api():
    """One customer, three conversations, one open case — the smallest world all six endpoints
    have something to say about."""
    case_table, review_table, ledger_table, s3 = FakeTable(), FakeTable(), FakeTable(), FakeS3()

    ledger_store = LedgerStore("ledger", table=ledger_table)
    ledger_store.append_all(signals())
    archive = TranscriptArchive("dev", s3=s3)
    for conversation in conversations():
        archive.put(conversation)

    ledger = SignalLedger()
    ledger.extend(ledger_store.load("C1"))
    opened = ledger.open_case("C1", SignalType.FINANCIAL_DISTRESS, 0.3)
    assert opened is not None
    case_store = CaseStore("cases", table=case_table)
    case_id = case_store.put_case(
        opened,
        threshold=0.3,
        now=ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 70),
        decision={"verdict": "genuine", "owning_team": "collections", "confidence": 0.7},
        trace={"cost_usd": 0.01, "account_data": "synthetic"},
    )

    built = ReviewerApi(
        case_store,
        ReviewStore("reviews", table=review_table),
        ledger_store,
        archive,
        threshold=0.3,
    )
    return built, case_id


# ---- the five reads --------------------------------------------------------------------------


def test_the_queue_returns_rows_not_whole_cases(api) -> None:
    """A queue of 200 cases each carrying its evidence chain and model trace is megabytes of JSON
    to render a table."""
    built, case_id = api
    status, payload = route(built, "GET", "/cases")

    assert status == 200
    assert payload["count"] == 1 and payload["truncated"] is False
    row = payload["cases"][0]
    assert row["case_id"] == case_id
    assert row["verdict"] == "genuine" and row["n_evidence"] == 3
    assert "evidence" not in row and "trace" not in row


def test_the_queue_says_when_it_is_truncated(api) -> None:
    """A page that returned exactly `limit` rows must not read as "that is all of them"."""
    built, _ = api
    _, payload = route(built, "GET", "/cases", {"limit": "1"})
    assert payload["truncated"] is True


def test_a_bad_limit_is_a_400_not_a_500(api) -> None:
    built, _ = api
    with pytest.raises(ApiError) as caught:
        route(built, "GET", "/cases", {"limit": "9000"})
    assert caught.value.status == 400
    with pytest.raises(ApiError) as caught:
        route(built, "GET", "/cases", {"limit": "banana"})
    assert caught.value.status == 400


def test_one_case_comes_back_with_the_retro_fields_the_ui_renders(api) -> None:
    built, case_id = api
    status, case = route(built, "GET", f"/cases/{case_id}")

    assert status == 200
    assert case["score_at_open"] and case["opened_on_day"] is not None
    for row in case["evidence"]:
        assert {"score_at_write", "score_now", "retro_delta", "load_bearing"} <= set(row)


def test_the_ledger_view_shows_every_signal_family_not_only_the_winner(api) -> None:
    """A reviewer looking at a churn case needs to see the distress score sitting under it. A UI
    that only ever shows the top family hides the accumulation the system is about."""
    built, _ = api
    status, payload = route(built, "GET", "/customers/C1/ledger")

    assert status == 200
    assert payload["signal_type"] in payload["by_signal_type"]
    assert payload["score"] == payload["by_signal_type"][payload["signal_type"]]
    assert payload["crossed"] is True
    assert len(payload["evidence"]) == 3


def test_the_ledger_score_is_memory_pys_not_a_second_one(api) -> None:
    built, _ = api
    _, payload = route(built, "GET", "/customers/C1/ledger")

    local = SignalLedger()
    local.extend(built.ledger_store.load("C1"))
    assert payload["score"] == local.best("C1", payload["as_of_day"]).score


def test_a_transcript_can_be_read_behind_a_quote(api) -> None:
    built, _ = api
    status, payload = route(built, "GET", "/customers/C1/conversations/K1")
    assert status == 200
    assert payload["turns"][1]["text"].startswith("I had to put the council tax")


def test_missing_things_are_404s_that_name_what_is_missing(api) -> None:
    built, _ = api
    for method, path in [
        ("GET", "/cases/NOPE"),
        ("GET", "/cases/NOPE/reviews"),
        ("GET", "/customers/NOBODY/ledger"),
        ("GET", "/customers/C1/conversations/NOPE"),
        ("GET", "/nonsense"),
    ]:
        with pytest.raises(ApiError) as caught:
            route(built, method, path)
        assert caught.value.status == 404, path


# ---- the one write ---------------------------------------------------------------------------


def test_a_review_annotates_and_never_touches_the_evidence(api) -> None:
    """Q3 in infrastructure.md — reduce the score, suppress the customer, or only annotate — is
    answered here as "only annotate", and this is what holds it."""
    built, case_id = api
    _, before = route(built, "GET", f"/cases/{case_id}")

    status, payload = route(
        built,
        "POST",
        f"/cases/{case_id}/reviews",
        body={"action": "dismiss", "reviewer": "amara", "reason": "already in collections"},
    )
    assert status == 201 and payload["status"] == "dismissed"

    _, after = route(built, "GET", f"/cases/{case_id}")
    assert after["evidence"] == before["evidence"]
    assert after["score"] == before["score"]
    assert after["status"] == "dismissed"

    _, reviews = route(built, "GET", f"/cases/{case_id}/reviews")
    assert reviews["count"] == 1
    assert reviews["reviews"][0]["reviewer"] == "amara"


def test_a_dismissed_case_leaves_the_open_queue_and_appears_in_the_other(api) -> None:
    built, case_id = api
    route(
        built,
        "POST",
        f"/cases/{case_id}/reviews",
        body={"action": "dismiss", "reviewer": "amara", "reason": "duplicate of AT-12"},
    )
    _, open_queue = route(built, "GET", "/cases", {"status": "open"})
    _, dismissed = route(built, "GET", "/cases", {"status": "dismissed"})
    assert open_queue["count"] == 0
    assert [c["case_id"] for c in dismissed["cases"]] == [case_id]


@pytest.mark.parametrize(
    "body, why",
    [
        ({"reviewer": "amara"}, "no action"),
        ({"action": "delete", "reviewer": "amara"}, "an action outside the closed set"),
        ({"action": "approve"}, "an anonymous entry in an audit trail"),
        ({"action": "approve", "reviewer": "   "}, "a whitespace reviewer"),
        ({"action": "dismiss", "reviewer": "amara"}, "a dismissal with no reason"),
    ],
)
def test_a_review_that_would_be_useless_later_is_refused_now(api, body: dict, why: str) -> None:
    built, case_id = api
    with pytest.raises(ApiError) as caught:
        route(built, "POST", f"/cases/{case_id}/reviews", body=body)
    assert caught.value.status == 400, why


def test_a_free_text_status_cannot_create_a_queue_nothing_lists(api) -> None:
    """`update_status` writes straight into the GSI partition key, so the action set is closed."""
    assert set(api_mod.ACTIONS) == {"approve", "dismiss", "route"}


# ---- the guarantees a client-facing surface carries ----------------------------------------------


def test_no_response_body_carries_an_answer_key_field(api) -> None:
    built, case_id = api
    route(
        built,
        "POST",
        f"/cases/{case_id}/reviews",
        body={"action": "route", "reviewer": "amara", "reason": "to collections"},
    )
    bodies = [
        route(built, "GET", "/cases", {"status": "routed"})[1],
        route(built, "GET", f"/cases/{case_id}")[1],
        route(built, "GET", f"/cases/{case_id}/reviews")[1],
        route(built, "GET", "/customers/C1/ledger")[1],
        route(built, "GET", "/customers/C1/conversations/K0")[1],
    ]
    leaked = _keys(bodies) & ANSWER_KEY_FIELDS
    assert not leaked, f"answer-key fields on a client-facing API: {sorted(leaked)}"


def test_there_is_no_endpoint_that_contacts_anyone(api) -> None:
    """HITL here is enforced by the absence of an outbound surface, not by a check somewhere. If
    this test has to change, the entry's central safety claim has changed with it."""
    built, case_id = api
    for path in [
        f"/cases/{case_id}/contact",
        f"/cases/{case_id}/notify",
        f"/cases/{case_id}/email",
        "/customers/C1/message",
        "/outreach",
    ]:
        for method in ("GET", "POST"):
            with pytest.raises(ApiError) as caught:
                route(built, method, path, body={"reviewer": "amara", "action": "approve"})
            assert caught.value.status == 404, f"{method} {path} routed somewhere"


# ---- the Lambda entrypoint -----------------------------------------------------------------------


@pytest.fixture
def wired(api, monkeypatch):
    built, case_id = api
    monkeypatch.setattr(api_mod, "_API", built)
    monkeypatch.delenv("EARSHOT_ALLOWED_ORIGIN", raising=False)
    return built, case_id


def _event(method: str, path: str, body: str | None = None, query: dict | None = None) -> dict:
    return {
        "requestContext": {"http": {"method": method}},
        "rawPath": path,
        "queryStringParameters": query,
        "body": body,
    }


def test_the_handler_serves_the_queue_as_json(wired) -> None:
    response = handler(_event("GET", "/cases"))
    assert response["statusCode"] == 200
    assert response["headers"]["content-type"] == "application/json"
    assert json.loads(response["body"])["count"] == 1


def test_the_handler_turns_an_api_error_into_its_status(wired) -> None:
    assert handler(_event("GET", "/cases/NOPE"))["statusCode"] == 404
    assert handler(_event("GET", "/cases", query={"limit": "0"}))["statusCode"] == 400


def test_a_malformed_body_is_a_400_not_a_crash(wired) -> None:
    _, case_id = wired
    response = handler(_event("POST", f"/cases/{case_id}/reviews", body="{not json"))
    assert response["statusCode"] == 400
    assert "invalid JSON" in json.loads(response["body"])["error"]


def test_an_unexpected_error_returns_no_stack_trace(wired, capsys) -> None:
    """A traceback in a response body names the tables. It goes to the log, not to the client."""
    built, _ = wired

    def boom(*_args, **_kwargs):
        raise RuntimeError("dynamodb table earshot-dev-cases is on fire")

    built.cases.list_queue = boom  # type: ignore[method-assign]
    response = handler(_event("GET", "/cases"))

    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"error": "internal error"}
    assert "on fire" not in response["body"]
    assert "api.error" in capsys.readouterr().out


def test_cors_is_off_unless_an_origin_is_configured(wired, monkeypatch) -> None:
    """Defaulting to `*` would publish a reviewer's case queue to any page a browser loads."""
    assert "Access-Control-Allow-Origin" not in handler(_event("GET", "/cases"))["headers"]

    monkeypatch.setenv("EARSHOT_ALLOWED_ORIGIN", "https://reviewer.example")
    headers = handler(_event("GET", "/cases"))["headers"]
    assert headers["Access-Control-Allow-Origin"] == "https://reviewer.example"


def test_a_preflight_is_answered_without_touching_a_store(wired) -> None:
    assert handler(_event("OPTIONS", "/cases"))["statusCode"] == 204
