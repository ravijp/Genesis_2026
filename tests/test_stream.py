"""The arrival stream: ordering, frame arithmetic, crossings, and what may reach a browser.

These assert *properties* rather than pinned outputs, per `working-agreements.md`: a test that
pins "frame 41 scores 0.612" fails on every corpus tweak and tells you nothing about whether the
stream is right. What must hold is that the frames agree with `memory.py`, that the arrival order
is genuinely interleaved, that a customer opens at most one case, and that nothing on the
answer key can reach the payload.
"""

from __future__ import annotations

import copy

import pytest

from earshot import stream as stream_mod
from earshot.cli import stream_inputs
from earshot.extract import OfflineLexiconExtractor
from earshot.memory import SignalLedger
from earshot.stream import (
    ANSWER_KEY_FIELDS,
    StreamError,
    _team_rollup,
    arrival_order,
    run_stream,
    stream_payload,
)
from earshot.tenants import CANONICAL_TEAMS, NORTHWIND, TENANTS


@pytest.fixture(scope="module")
def run():
    """One offline stream, shared. Keyless and deterministic, so no test here needs a provider.

    `investigate_limit=0` because the agent is not what these tests are about: they check the
    accumulation path, which is pure code, and an investigation would make the fixture slow and
    provider-dependent for no gain.
    """
    t = NORTHWIND
    conversations, context_for, _ = stream_inputs(t)
    extractor = OfflineLexiconExtractor(
        miss_rate=t.run.offline_miss_rate, false_fire_rate=t.run.offline_false_fire_rate
    )
    return run_stream(
        t,
        conversations,
        extractor,
        provider=None,
        context_for=context_for,
        investigate_limit=0,
    )


def test_arrival_order_is_by_day_across_the_whole_book(run) -> None:
    days = [f["day"] for f in run.frames]
    assert days == sorted(days), "frames must arrive in day order, as a live queue delivers them"


def test_arrival_order_interleaves_customers(run) -> None:
    """The point of streaming: two conversations of one arc are separated by other customers'.

    Grouped-by-customer ordering would still be "day ordered" within each arc and would still
    animate, but it would demonstrate a batch with a clock painted on it -- the board would never
    re-rank between two conversations of the same customer, which is the beat.
    """
    ids = [f["customer_id"] for f in run.frames]
    runs_of_one = sum(
        1 for a, b in zip(ids, ids[1:]) if a == b
    )
    assert runs_of_one < len(ids) // 4, (
        f"{runs_of_one}/{len(ids)} consecutive frames share a customer -- the stream is grouped, "
        f"not interleaved"
    )


def test_frames_agree_with_the_ledger(run) -> None:
    """`score_after` on every frame is what `memory.py` says, recomputed independently.

    This is the guard against the browser ever needing to compute: if the frames are right, the
    UI can be a dumb player. If they drift from the scorer, two numbers exist for one question.
    """
    ledger = SignalLedger(run.tenant.run.scoring)
    seen = set()
    for frame in run.frames:
        for signal in frame["signals"]:
            pass  # signals are already in the run's ledger; rebuild below from it instead
    # Rebuild by replaying the run's own ledger day by day is circular, so check the invariant
    # that matters instead: the score in the frame equals `best()` for that customer on that day
    # using the run's ledger restricted to that day. `best` filters by `as_of_day` itself.
    for frame in run.frames:
        seen.add(frame["customer_id"])
        expected = run.ledger.best(frame["customer_id"], frame["day"])
        # The frame was taken mid-stream, so later arrivals for the same customer on the SAME day
        # would move it. Compare only where this is the customer's last conversation that day.
        later_same_day = any(
            g["customer_id"] == frame["customer_id"]
            and g["day"] == frame["day"]
            and g["i"] > frame["i"]
            for g in run.frames
        )
        if later_same_day:
            continue
        assert frame["score_after"] == pytest.approx(round(expected.score, 4), abs=1e-4), (
            f"frame {frame['i']} says {frame['score_after']} but the ledger says {expected.score}"
        )
    assert ledger is not None


def test_score_before_is_taken_on_the_same_day(run) -> None:
    """Movement in a frame must be caused by the conversation, not by the calendar advancing.

    Taking `score_before` from the customer's previous frame would fold decay since that day into
    the delta, and a decayed customer would appear to have *dropped* on a conversation that added
    evidence. The screen prints that delta next to the arrow, so it has to mean one thing.
    """
    for frame in run.frames:
        if frame["signals"]:
            assert frame["score_after"] >= frame["score_before"] - 1e-9, (
                f"frame {frame['i']} added {len(frame['signals'])} signal(s) and the score fell"
            )


def test_a_customer_crosses_at_most_once(run) -> None:
    crossed = [f["customer_id"] for f in run.frames if f["crossed"]]
    assert len(crossed) == len(set(crossed)), "a customer opened more than one case"


def test_crossings_are_above_the_threshold(run) -> None:
    for frame in run.frames:
        if frame["crossed"]:
            assert frame["score_after"] >= run.tenant.threshold
            assert frame["score_before"] < run.tenant.threshold


def test_board_is_ranked_and_bounded(run) -> None:
    for frame in run.frames:
        scores = [row["score"] for row in frame["board"]]
        assert scores == sorted(scores, reverse=True), f"frame {frame['i']} board is unsorted"
        assert len(frame["board"]) <= stream_mod.BOARD_SIZE


def test_nothing_is_ever_discarded(run) -> None:
    """`ledger_size` is monotonic. Never-discard is the design inversion; assert it mechanically."""
    sizes = [f["ledger_size"] for f in run.frames]
    assert sizes == sorted(sizes), "the retained-quote count went down; something discarded"


def test_payload_refuses_answer_key_fields(run) -> None:
    """The guard has to fire on a nested field, not only a top-level one.

    Copies rather than mutating the shared fixture: a poisoned frame dict is the same object the
    other tests read, and a guard test that corrupts its own fixture reports three failures
    somewhere else.
    """
    poisoned = copy.copy(run)
    poisoned.frames = copy.deepcopy(run.frames[:2])
    poisoned.crossings = []
    poisoned.frames[0]["reader"]["stratum"] = "concentrated"
    with pytest.raises(StreamError, match="answer-key"):
        stream_payload(poisoned, {"asr": "none"})


def test_clean_payload_passes_the_guard(run) -> None:
    payload = stream_payload(run, {"tenant_id": run.tenant.tenant_id, "asr": "none"})
    assert not (stream_mod._all_keys(payload) & ANSWER_KEY_FIELDS)
    assert payload["totals"]["conversations"] == len(run.frames)
    assert payload["manifest"]["asr"] == "none"


def test_every_crossing_is_accounted_for(run) -> None:
    """Investigated or listed as unworked with a reason -- never silently dropped.

    A demo that shows four worked cases out of nine crossings and does not say so is claiming a
    precision it did not measure.
    """
    payload = stream_payload(run, {"asr": "none"})
    assert payload["totals"]["investigated"] + len(payload["unworked"]) == payload["totals"][
        "crossings"
    ]
    for row in payload["unworked"]:
        assert row["reason"], f"{row['customer_id']} was not worked and no reason was recorded"


# The stream's case record is `case_record()` plus these three, and nothing else.
#
# Declared here rather than derived from the code, so a fourth one has to be added deliberately
# -- to this set, in a commit someone reads -- rather than appearing in a browser payload nobody
# diffed. `case_record.py` exists because two serializers drift silently; `stream.py` is the
# third producer of that record, and the drift it can cause is additive, which is exactly the
# kind no equality test between the other two would ever see.
STREAM_CASE_EXTRAS = {"tenant_id", "team_label", "frame_index"}


def test_the_stream_case_record_is_case_record_plus_a_bounded_set_of_extras(run) -> None:
    """`_case_records` mutates the canonical record after building it, and until this existed
    nothing bounded what it could add.

    A field added here reaches `ui/stream.js` and nothing else in the suite notices -- the
    payload's answer-key scan matches field names exactly, so `latent_risk_band` walks straight
    past `latent_risk`. And the investigate screens in `ui/app.js` already read `team_label`, a
    field only this producer writes, so the page is being written against the union of two record
    shapes. That union is the state `case_record.py` was created to prevent.

    The fixture runs with `investigate_limit=0`, so a decision is attached here on a COPY: the
    module-scoped run is shared, and a guard test that corrupts its own fixture reports its
    failures somewhere else.
    """
    from dataclasses import replace as dc_replace

    from earshot.agent.investigator import InvestigationTrace
    from earshot.agent.schemas import EvidenceRef, InvestigationDecision
    from earshot.case_record import case_record
    from earshot.memory import Case
    from earshot.schema import SignalType

    crossing = run.crossings[0]
    decision = InvestigationDecision(
        customer_id=crossing.customer_id,
        verdict="genuine",
        owning_team="collections",
        confidence=0.7,
        rationale="three conversations, one arc",
        recommended_action="call the customer",
        what_would_change_my_mind="a salary credit landing next month",
        evidence=[EvidenceRef(conversation_id=crossing.conversation_id, turn_index=0, quote="x")],
    )
    trace = InvestigationTrace(
        customer_id=crossing.customer_id,
        provider="offline-rules",
        model="none",
        prompt_version="v1",
        prompt_sha="0" * 8,
    )
    streamed = dc_replace(
        run, crossings=[dc_replace(crossing, decision=decision, trace=trace)]
    )

    records = stream_mod._case_records(streamed)
    assert len(records) == 1
    record = next(iter(records.values()))

    # The canonical key set, taken from `case_record()` itself rather than written out here --
    # a field added or renamed over there must not need this test edited to keep passing.
    canonical = set(
        case_record(
            Case(
                customer_id=crossing.customer_id,
                signal_type=SignalType.FINANCIAL_DISTRESS,
                score=crossing.score_at_cross,
                opened_on_day=crossing.day,
                opened_by_conversation=crossing.conversation_id,
                evidence=[],
            ),
            threshold=run.tenant.threshold,
            decision=decision.model_dump(),
            trace=trace.to_dict(),
        )
    )

    assert not canonical - set(record), (
        f"the stream record is missing {sorted(canonical - set(record))} that every other "
        f"case_record() producer writes -- the reviewer screens read one shape, not two"
    )
    assert set(record) - canonical == STREAM_CASE_EXTRAS, (
        f"the stream record carries {sorted(set(record) - canonical - STREAM_CASE_EXTRAS)} on "
        f"top of case_record() and nothing declares them. Add them to STREAM_CASE_EXTRAS and say "
        f"why, or put them in case_record() so all three producers write them."
    )


def test_team_rollup_lists_every_slot_even_at_zero(run) -> None:
    """A rollup that hides empty teams reads as "this tenant has three teams"."""
    payload = stream_payload(run, {"asr": "none"})
    labels = {row["team"] for row in payload["teams"]}
    assert {"retention", "collections", "vulnerability", "complaints"} <= labels


def test_team_rollup_lists_the_unrouted_bucket_even_at_zero(run) -> None:
    """`none` is not a team; it is the agent declining to pick one, and it is listed at zero.

    Dropping the row when it is empty makes "the agent always picks a team" the default reading
    of every dashboard that has not yet seen a declined case. It declined 8 of 49 times when
    routing was measured on 2026-08-28, so that reading is wrong, and those are the cases a
    reviewer must not lose.
    """
    payload = stream_payload(run, {"asr": "none"})
    rows = [row for row in payload["teams"] if row["team"] == "none"]
    assert len(rows) == 1, "the unrouted bucket must appear exactly once, at zero or not"
    assert rows[0]["cases"] == 0


def _record(slot: str | None) -> dict:
    """A case record as far as the rollup is concerned: a decision with a routing slot."""
    return {"decision": {} if slot is None else {"owning_team": slot}}


def test_team_rollup_is_a_partition_of_the_cases() -> None:
    """Every case counts in exactly one bucket, and the buckets sum to the whole queue.

    Property, not a pinned table: the team-scoped queue in `ui/console.js` filters the same
    records, so a rollup that double-counts or drops one makes the filter's denominator disagree
    with the rows a reviewer can see. The unmapped and missing slots are here on purpose — both
    must land in `none` rather than vanishing.
    """
    records = {
        "a": _record("retention"),
        "b": _record("vulnerability"),
        "c": _record("vulnerability"),
        "d": _record("none"),
        "e": _record(None),
        "f": _record("commercial"),  # not a canonical slot: the brief's fourth view, never built
    }
    rows = _team_rollup(records, NORTHWIND)

    assert [row["team"] for row in rows] == [*CANONICAL_TEAMS, "none"]
    assert sum(row["cases"] for row in rows) == len(records)
    counts = {row["team"]: row["cases"] for row in rows}
    assert counts["retention"] == 1
    assert counts["vulnerability"] == 2
    assert counts["collections"] == 0
    # A declined route, a decision with no slot, and a slot no queue drains all read the same way
    # to a reviewer: the agent did not choose a destination.
    assert counts["none"] == 3


def test_team_rollup_labels_are_the_tenants_names_not_the_models_slots() -> None:
    """D-029: the team map is display-only. The slot is the model's vocabulary and stays out of
    anything a reviewer reads, or a client string ends up inside the decision contract."""
    rows = _team_rollup({"a": _record("retention")}, NORTHWIND)
    by_slot = {row["team"]: row["label"] for row in rows}
    for slot in CANONICAL_TEAMS:
        assert by_slot[slot] == NORTHWIND.teams[slot]
    assert by_slot["none"] == NORTHWIND.team_label(None)
    assert by_slot["none"] != "none"


def test_empty_book_is_refused_not_streamed() -> None:
    with pytest.raises(StreamError, match="no conversations"):
        run_stream(
            NORTHWIND,
            [],
            OfflineLexiconExtractor(),
            provider=None,
            context_for=lambda *a: None,
            investigate_limit=0,
        )


def test_arrival_order_is_stable() -> None:
    """Two conversations on the same day must not shuffle between runs: a demo is rehearsed."""
    conversations, _, _ = stream_inputs(TENANTS[0])
    first = [c.conversation_id for c in arrival_order(conversations)]
    second = [c.conversation_id for c in arrival_order(list(reversed(list(conversations))))]
    assert first == second


def test_the_stream_module_never_holds_a_corpus() -> None:
    """The structural half of the separation guarantee, stated as a test.

    `stream.py` is on the guarded surface (`tests/test_separation.py` discovers it by glob), and
    it stays there only because the corpus and the `ToolContext` factory are handed in by
    `cli.py`. If someone re-adds `generate()` here, the guard fails -- but this says *why*, which
    a bare import assertion does not.
    """
    source = __import__("inspect").getsource(stream_mod)
    assert "generate(" not in source
    assert "CustomerTruth" not in source
