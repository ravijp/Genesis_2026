"""The agent's guarantees: a strict decision contract, a loop that always terminates, and an
offline path that produces a valid case file with no key and no network.

These are the claims a judge would poke at first — "what happens when the model loops?", "what
stops it inventing a quote?" — so they are pinned here rather than argued in prose.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from earshot.agent.investigator import MAX_STEPS, investigate
from earshot.agent.prompts import investigator_prompts, load_prompt, render
from earshot.agent.schemas import EvidenceRef, InvestigationDecision
from earshot.agent.tools import ToolContext, tool_specs
from earshot.llm.base import Completion, ModelConfig, ProviderError, ToolCall, Usage
from earshot.llm.cache import CacheMiss, CachingProvider, ResponseCache
from earshot.llm.offline import OfflineProvider
from earshot.memory import SignalLedger
from earshot.schema import Channel, Conversation, ExtractedSignal, SignalType, Turn

QUOTES = {
    "K0": "Money has been really tight since the hours were cut.",
    "K1": "I had to put the council tax on a credit card this month.",
    "K2": "We're behind on the rent and I don't know what to do.",
}


def _context(risk_signal: float = 0.8) -> ToolContext:
    conversations = tuple(
        Conversation(
            conversation_id=cid,
            customer_id="C1",
            channel=channel,
            day=day,
            turns=(
                Turn(0, "agent", "Thanks for calling."),
                Turn(1, "customer", QUOTES[cid]),
                Turn(2, "agent", "Noted."),
            ),
        )
        for cid, day, channel in (
            ("K0", 10, Channel.CALL),
            ("K1", 40, Channel.CHAT),
            ("K2", 70, Channel.COMPLAINT),
        )
    )
    ledger = SignalLedger()
    ledger.extend(
        [
            ExtractedSignal(
                customer_id="C1",
                conversation_id=c.conversation_id,
                signal_type=SignalType.FINANCIAL_DISTRESS,
                confidence=0.45,
                evidence_quote=QUOTES[c.conversation_id],
                turn_index=1,
                day=c.day,
                channel=c.channel,
            )
            for c in conversations
        ]
    )
    breakdown = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 70)
    return ToolContext(
        customer_id="C1",
        as_of_day=70,
        seed=7,
        risk_signal=risk_signal,
        signal_type=SignalType.FINANCIAL_DISTRESS.value,
        score=breakdown.score,
        threshold=0.5,
        conversations=conversations,
        breakdown=breakdown,
    )


VALID_DECISION = {
    "customer_id": "C1",
    "verdict": "genuine",
    "owning_team": "collections",
    "confidence": 0.7,
    "rationale": "Three conversations agree and the account corroborates.",
    "recommended_action": "Pre-arrears affordability call.",
    "what_would_change_my_mind": "A salary credit landing on schedule next cycle.",
    "evidence": [
        {"conversation_id": "K2", "turn_index": 1, "quote": "We're behind on the rent"}
    ],
}


# --- the decision contract ---------------------------------------------------------


def test_schema_accepts_a_well_formed_decision() -> None:
    decision = InvestigationDecision.model_validate(VALID_DECISION)
    assert decision.verdict == "genuine"


def test_schema_rejects_a_decision_with_no_evidence() -> None:
    """An unquotable claim must be impossible to construct, not merely discouraged."""
    payload = dict(VALID_DECISION, evidence=[])
    with pytest.raises(ValidationError):
        InvestigationDecision.model_validate(payload)


def test_schema_rejects_empty_quotes_and_negative_turns() -> None:
    with pytest.raises(ValidationError):
        EvidenceRef(conversation_id="K0", turn_index=1, quote="")
    with pytest.raises(ValidationError):
        EvidenceRef(conversation_id="", turn_index=1, quote="something")
    with pytest.raises(ValidationError):
        EvidenceRef(conversation_id="K0", turn_index=-1, quote="something")


def test_schema_forbids_invented_fields_and_out_of_range_confidence() -> None:
    with pytest.raises(ValidationError):
        InvestigationDecision.model_validate(dict(VALID_DECISION, probability_of_churn=0.9))
    with pytest.raises(ValidationError):
        InvestigationDecision.model_validate(dict(VALID_DECISION, confidence=1.4))
    with pytest.raises(ValidationError):
        InvestigationDecision.model_validate(dict(VALID_DECISION, owning_team="marketing"))


# --- stub providers ----------------------------------------------------------------


class _Stub:
    """Replays a fixed script. `complete` ignores the transcript, which is the point: these
    tests are about the loop's control flow, not about anyone's judgment."""

    def __init__(self, name: str, replies: list[Completion], repeat_last: bool = True) -> None:
        self.name = name
        self._replies = replies
        self._repeat_last = repeat_last
        self.calls = 0

    def complete(self, messages, tools, model_cfg) -> Completion:
        self.calls += 1
        if self.calls <= len(self._replies):
            return self._replies[self.calls - 1]
        if self._repeat_last and self._replies:
            return self._replies[-1]
        raise ProviderError("script exhausted")


def _tool_reply(name: str = "get_ledger_summary", **kwargs) -> Completion:
    return Completion(
        tool_calls=(ToolCall(id=f"c{name}", name=name, arguments={}),),
        model="stub",
        **kwargs,
    )


def _text_reply(text: str, **kwargs) -> Completion:
    return Completion(content=text, model="stub", **kwargs)


# --- the loop ----------------------------------------------------------------------


def test_loop_terminates_at_the_step_cap_and_still_emits_a_decision() -> None:
    """A provider that never stops calling tools must not hang the batch."""
    provider = _Stub("looper", [_tool_reply()])
    decision, trace = investigate(_context(), provider)

    assert provider.calls == MAX_STEPS
    assert trace.model_calls == MAX_STEPS
    assert trace.stopped_because == "step_cap"
    assert decision.verdict == "insufficient_evidence"
    assert decision.owning_team == "none"
    assert decision.confidence == 0.0
    # Even the give-up path cites something real, or it would not be reviewable.
    assert decision.evidence and decision.evidence[0].conversation_id in QUOTES


def test_loop_honours_a_lower_step_cap() -> None:
    _, trace = investigate(_context(), _Stub("looper", [_tool_reply()]), max_steps=2)
    assert trace.model_calls == 2
    assert trace.stopped_because == "step_cap"


def test_a_good_first_answer_ends_the_loop_immediately() -> None:
    provider = _Stub("oneshot", [_text_reply(json.dumps(VALID_DECISION))])
    decision, trace = investigate(_context(), provider)

    assert trace.model_calls == 1
    assert trace.stopped_because == "decided"
    assert decision.verdict == "genuine"
    assert trace.schema_retries == 0


def test_a_fenced_json_reply_with_preamble_still_parses() -> None:
    reply = "Here is my decision:\n```json\n" + json.dumps(VALID_DECISION) + "\n```"
    decision, trace = investigate(_context(), _Stub("chatty", [_text_reply(reply)]))
    assert trace.stopped_because == "decided"
    assert decision.verdict == "genuine"


def test_malformed_json_is_retried_at_most_twice_then_degrades() -> None:
    provider = _Stub("babbler", [_text_reply("I think this customer is fine, honestly.")])
    decision, trace = investigate(_context(), provider)

    assert trace.schema_retries == 3  # two retries, then the third rejection stops it
    assert trace.stopped_because == "invalid_after_retries"
    assert decision.verdict == "insufficient_evidence"


def test_unresolvable_evidence_is_rejected_and_counted() -> None:
    """The groundedness guarantee: a quote nobody said cannot reach a reviewer."""
    invented = dict(
        VALID_DECISION,
        evidence=[{"conversation_id": "K0", "turn_index": 1, "quote": "I am closing my account"}],
    )
    provider = _Stub("fabricator", [_text_reply(json.dumps(invented))])
    decision, trace = investigate(_context(), provider)

    assert trace.evidence_repairs >= 1
    assert trace.stopped_because == "invalid_after_retries"
    assert decision.verdict == "insufficient_evidence"


@pytest.mark.parametrize(
    ("label", "quote"),
    [
        ("whitespace only", "   \t\n  "),
        ("empty", ""),
        ("single space", " "),
        ("non-breaking space", "\xa0"),
        ("single character", "M"),
        ("one word", "Money"),
        ("three words", "Money has been"),
        ("mid-word fragment", "oney has been really"),
        ("ends mid-word", "Money has been rea"),
    ],
)
def test_a_citation_that_is_not_evidence_does_not_resolve(label: str, quote: str) -> None:
    """The substring test certified all of these as "verbatim".

    `""` is a substring of every turn, and so is any single letter — so a decision could cite a
    real turn while quoting none of its words and pass the groundedness check. A citation has to
    carry enough consecutive words for a reviewer to check it against the transcript.
    """
    from earshot.agent.tools import unresolved_evidence

    ctx = _context()
    ref = EvidenceRef(conversation_id="K0", turn_index=1, quote=quote or " ")
    assert unresolved_evidence(ctx, [ref]), (
        f"{label!r} was accepted as a verbatim citation of "
        f"{QUOTES['K0']!r} — that is not evidence"
    )


def test_a_real_multi_word_quote_still_resolves() -> None:
    """The floor must not reject honest citations: a genuine span of the turn still passes."""
    from earshot.agent.tools import unresolved_evidence

    ctx = _context()
    assert (
        unresolved_evidence(
            ctx,
            [EvidenceRef(conversation_id="K0", turn_index=1, quote="tight since the hours were")],
        )
        == []
    )
    # Case and internal whitespace are still forgiven — a model retyping a quote should not fail
    # on capitalisation.
    assert (
        unresolved_evidence(
            ctx,
            [EvidenceRef(conversation_id="K0", turn_index=1, quote="TIGHT   since the HOURS were")],
        )
        == []
    )


def test_unresolved_refs_on_a_returned_decision_are_zero_by_construction() -> None:
    """Why groundedness is reported as first-attempt repairs and never as a post-hoc count.

    The loop rejects any decision whose citations do not resolve, so counting unresolved refs on
    what the loop RETURNS yields zero however badly the provider behaves. A reader sees that zero
    as a measurement of honesty; it is a measurement of the rejection that already happened. The
    signal that carries information is `evidence_repairs`.
    """
    from earshot.agent.tools import unresolved_evidence

    invented = dict(
        VALID_DECISION,
        evidence=[{"conversation_id": "K0", "turn_index": 1, "quote": "I am closing my account"}],
    )
    ctx = _context()
    provider = _Stub("always-fabricates", [_text_reply(json.dumps(invented))])
    decision, trace = investigate(ctx, provider)

    # The provider fabricated every citation it produced...
    assert trace.evidence_repairs >= 1
    # ...yet the returned decision resolves cleanly, so the post-hoc count reports perfection.
    assert unresolved_evidence(ctx, decision.evidence) == []


class _Exploding:
    """A provider that fails the test if the loop reaches it. Replay must never call out."""

    name = "must-not-be-called"

    def complete(self, messages, tools, model_cfg):
        raise AssertionError("replay mode reached the inner provider")


def test_replay_never_reaches_the_inner_provider(tmp_path) -> None:
    """The no-wifi guarantee for the demo: a cache hit must not touch the network at all.

    The committed cache is what stands between a judging room with no wifi and a dead demo, so
    "replay mode serves from disk" has to be mechanical rather than believed. The cache is
    written under `tmp_path`: a test that records into the real cache file would append junk
    completions to the artifact the demo replays from.
    """
    from earshot.llm.cache import CachingProvider, ResponseCache

    cache = ResponseCache(path=tmp_path / "cache.jsonl", mode="record")
    provider = CachingProvider(_Exploding(), prompt_sha="abc", cache=cache)
    key = ResponseCache.key("m", "abc", [{"role": "user", "content": "hi"}], [])
    cache.put(key, Completion(content="{}", model="m"))

    cache.mode = "replay"
    served = provider.complete([{"role": "user", "content": "hi"}], [], ModelConfig(model="m"))
    assert served.content == "{}"
    assert provider.hits == 1


def test_replay_reports_a_miss_instead_of_falling_through_to_the_network(tmp_path) -> None:
    """A cache miss in replay mode must fail loudly, not quietly go online with an invalid key."""
    from earshot.llm.cache import CacheMiss, CachingProvider, ResponseCache

    provider = CachingProvider(
        _Exploding(),
        prompt_sha="abc",
        cache=ResponseCache(path=tmp_path / "cache.jsonl", mode="replay"),
    )
    with pytest.raises(CacheMiss):
        provider.complete(
            [{"role": "user", "content": "never recorded"}], [], ModelConfig(model="m")
        )


def test_the_bedrock_cache_holds_only_bedrock_completions() -> None:
    """One cache file per provider, and this is what enforces it.

    Until 2026-08-28 every provider shared `investigator-demo.jsonl`, and the first keyed Bedrock
    runs appended Haiku 4.5 completions into the file holding the two pinned Sonnet investigations
    the README quotes. The test above caught it. This is the same guard from the other side: a
    stray OpenRouter or offline run must not land here either.
    """
    import json

    from earshot.llm.cache import cache_path

    path = cache_path("bedrock")
    if not path.is_file():
        pytest.skip("no Bedrock cache recorded in this checkout")
    entries = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    models = {e.get("completion", e).get("model") for e in entries}
    assert models == {"us.anthropic.claude-haiku-4-5-20251001-v1:0"}, (
        f"the Bedrock cache carries completions from {sorted(models)}"
    )


def test_the_committed_cache_is_exactly_the_two_live_investigations() -> None:
    """The cache is committed evidence, so its contents are pinned rather than assumed.

    Running `earshot investigate` in the default record mode appends to this file, so it is one
    stray command away from carrying offline junk beside the two real Sonnet 4.5 runs whose cost
    and latency the README quotes.
    """
    import json

    from earshot.llm.cache import cache_path

    entries = [
        json.loads(line)
        for line in cache_path().read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    models = {e.get("completion", e).get("model") for e in entries}
    assert models == {"anthropic/claude-sonnet-4.5"}, (
        f"the committed cache carries completions from {sorted(models)} — it must hold only the "
        f"two live Sonnet 4.5 investigations the README quotes"
    )
    total = sum(e.get("completion", e).get("cost_usd", 0.0) for e in entries)
    assert abs(total - 0.1855) < 0.001, f"committed cache cost drifted to ${total:.4f}"
    # Exact, not >=: a duplicate or a zero-cost re-record leaves both the model set and the
    # cost sum unchanged, so only the count catches it.
    assert len(entries) == 10, (
        f"the committed cache holds {len(entries)} completions, not the 10 that make up the two "
        f"live investigations — something has been appended to it"
    )


# `test_the_committed_cache_covers_the_documented_replay_invocation` stood here and asserted only
# `len(cache) >= 10` — a count, never a key — so it stayed green through the exact failure it was
# written to catch: the README's replay command (`--provider openrouter --customers 200 --limit 2`)
# cache-misses today, because the investigator prompt changed twice after the cache was recorded
# (`7229b70`, `80c0914`) and the cache key includes `prompt_sha`. Verified 2026-08-28 by running the
# command as documented: both cases print `provider_error`. Deleted along with the README claim
# (D-025 also dropped Sonnet) rather than rewritten, because there is nothing left to guard — the
# README no longer tells anyone to run that command. The two tests above still pin the cache's
# *contents* (model, cost, count); that guard is real and stays.


@pytest.mark.parametrize("junk", [None, {"content": "{}"}, "a bare string", 42])
def test_a_provider_returning_the_wrong_type_degrades_instead_of_raising(junk) -> None:
    """"The loop always returns a decision" has to hold for a broken provider too.

    Reading `.model` off the reply sat outside the exception guard, so a provider returning None,
    a dict or a string raised AttributeError straight past a loop whose entire contract is that
    it never does.
    """

    class _WrongType:
        name = "wrong-type"

        def complete(self, messages, tools, model_cfg):
            return junk

    decision, trace = investigate(_context(), _WrongType())
    assert decision.verdict == "insufficient_evidence"
    assert trace.stopped_because == "internal_error"


def test_a_non_finite_cost_cannot_slip_past_the_cap_or_into_the_manifest() -> None:
    """NaN compares False against every bound, so it defeats the cap and breaks the artifact.

    `nan > cap` is False, so the pre-flight waves it through; `json.dumps(nan)` then produces
    output that is not valid JSON, which is how a run manifest stops being loadable.
    """
    import json
    import math

    provider = _Stub(
        "nan-cost",
        [_text_reply(json.dumps(VALID_DECISION), cost_usd=float("nan"))],
    )
    decision, trace = investigate(_context(), provider, cost_cap_usd=0.25)

    assert math.isfinite(trace.cost_usd), "a non-finite cost reached the trace"
    json.dumps(trace.to_dict())  # would raise ValueError on NaN
    assert decision.verdict == "genuine"


def test_a_valid_decision_is_kept_even_if_that_call_crossed_the_cap() -> None:
    """The cap stops the NEXT call. Discarding an answer already paid for buys nothing."""
    expensive = _Stub(
        "valid-but-expensive",
        [_text_reply(json.dumps(VALID_DECISION), cost_usd=99.0)],
    )
    decision, trace = investigate(_context(), expensive, cost_cap_usd=0.25)

    assert decision.verdict == "genuine", (
        f"the loop paid ${trace.cost_usd} for a valid decision and then threw it away "
        f"(stopped_because={trace.stopped_because})"
    )


def test_tool_calls_are_bounded_per_step_not_just_model_calls() -> None:
    """"Six steps" bounded model calls while tool executions and prompt growth were unbounded."""
    from earshot.agent.investigator import MAX_TOOL_CALLS_PER_STEP

    fan_out = Completion(
        tool_calls=tuple(
            ToolCall(id=f"c{i}", name="get_ledger_summary", arguments={}) for i in range(500)
        ),
        model="stub",
    )
    _, trace = investigate(_context(), _Stub("fan-out", [fan_out]))

    assert trace.tool_calls <= MAX_STEPS * MAX_TOOL_CALLS_PER_STEP, (
        f"{trace.tool_calls} tools ran from {trace.model_calls} model calls — the step cap does "
        f"not bound tool execution"
    )


def test_a_repaired_answer_is_accepted_on_the_second_attempt() -> None:
    provider = _Stub(
        "self-correcting",
        [_text_reply("not json at all"), _text_reply(json.dumps(VALID_DECISION))],
        repeat_last=False,
    )
    decision, trace = investigate(_context(), provider)

    assert trace.schema_retries == 1
    assert trace.stopped_because == "decided"
    assert decision.verdict == "genuine"


def test_cost_cap_is_a_cap_not_a_report() -> None:
    """A cap that notices the overspend afterwards is not a cap.

    Assert the money, not the label: `stopped_because == "cost_cap"` is equally true of a loop
    that booked the spend and then complained about it. What has to hold is that the loop
    refuses a call it already knows it cannot afford.
    """
    expensive = _tool_reply(cost_usd=0.20, usage=Usage(prompt_tokens=1000, completion_tokens=50))
    decision, trace = investigate(_context(), _Stub("pricey", [expensive]), cost_cap_usd=0.25)

    assert trace.stopped_because == "cost_cap"
    assert trace.cost_usd <= 0.25, f"spent {trace.cost_usd} against a 0.25 cap"
    assert decision.verdict == "insufficient_evidence"


def test_cost_cap_holds_when_each_call_costs_more_than_the_last() -> None:
    """The realistic shape: tool results accumulate into the prompt, so cost climbs.

    A constant-cost stub is the one shape even a naive estimator gets right, so it proves
    nothing on its own. This ramps 1.5x per call.
    """

    class Ramp:
        name = "ramp"

        def __init__(self) -> None:
            self.calls = 0

        def complete(self, *args, **kwargs):  # noqa: ANN002, ANN003
            self.calls += 1
            return _tool_reply(
                cost_usd=0.02 * (1.5**self.calls),
                usage=Usage(prompt_tokens=100, completion_tokens=10),
            )

    _, trace = investigate(_context(), Ramp(), cost_cap_usd=0.25)
    assert trace.cost_usd <= 0.25, f"spent {trace.cost_usd:.4f} against a 0.25 cap"


def test_a_single_unbounded_call_can_still_breach_the_cap() -> None:
    """Documents the honest limit rather than pretending it does not exist.

    Two cheap calls followed by one enormously expensive one defeats any pre-flight estimate.
    A single call is bounded by max_tokens and TOOL_RESULT_CHAR_CAP, not by the cost cap. If
    someone later claims the cap is absolute, this test is the counter-example.
    """

    class Spike:
        name = "spike"

        def __init__(self) -> None:
            self.costs = [0.001, 0.001, 5.00]
            self.calls = 0

        def complete(self, *args, **kwargs):  # noqa: ANN002, ANN003
            cost = self.costs[min(self.calls, len(self.costs) - 1)]
            self.calls += 1
            return _tool_reply(
                cost_usd=cost, usage=Usage(prompt_tokens=100, completion_tokens=10)
            )

    _, trace = investigate(_context(), Spike(), cost_cap_usd=0.25)
    assert trace.cost_usd > 0.25
    assert trace.stopped_because == "cost_cap"


def test_a_tool_that_crashes_does_not_take_the_run_down() -> None:
    """Whatever a tool raises comes back as content the model can read. A tool that raises
    something other than ToolError or ValidationError must not escape as a traceback."""
    import earshot.agent.investigator as inv

    class Exploding:
        name = "get_ledger_summary"

        def run(self, ctx, arguments):  # noqa: ANN001, ARG002
            raise KeyError("internal")

    original = dict(inv.TOOLS_BY_NAME)
    inv.TOOLS_BY_NAME["get_ledger_summary"] = Exploding()
    try:
        payload, detail = inv._run_tool(_context(), "get_ledger_summary", {})
    finally:
        inv.TOOLS_BY_NAME.clear()
        inv.TOOLS_BY_NAME.update(original)

    assert "KeyError" in payload
    assert "crashed" in detail


def test_a_provider_failure_degrades_instead_of_raising() -> None:
    provider = _Stub("broken", [], repeat_last=False)
    decision, trace = investigate(_context(), provider)

    assert trace.stopped_because == "provider_error"
    assert decision.verdict == "insufficient_evidence"


def test_unknown_tool_calls_come_back_as_readable_errors() -> None:
    provider = _Stub("confused", [_tool_reply("get_credit_score")])
    _, trace = investigate(_context(), provider, max_steps=2)
    tool_steps = [s for s in trace.steps if s.kind == "tool"]
    assert tool_steps and tool_steps[0].detail == "unknown tool"


def test_trace_totals_add_up() -> None:
    reply = _tool_reply(cost_usd=0.01, latency_ms=12.5, usage=Usage(10, 5))
    _, trace = investigate(_context(), _Stub("meter", [reply]), max_steps=3)
    assert trace.model_calls == 3
    assert trace.prompt_tokens == 30
    assert trace.completion_tokens == 15
    assert trace.cost_usd == pytest.approx(0.03)
    assert trace.latency_ms == pytest.approx(37.5)
    assert json.dumps(trace.to_dict())


# --- the offline path, end to end --------------------------------------------------


def test_offline_provider_produces_a_valid_decision_with_no_network() -> None:
    ctx = _context(risk_signal=0.9)
    decision, trace = investigate(ctx, OfflineProvider())

    assert trace.stopped_because == "decided"
    assert trace.tool_calls >= 3, "the offline provider must actually use its tools"
    assert decision.customer_id == "C1"
    assert decision.verdict in ("genuine", "false_alarm", "insufficient_evidence")
    assert decision.evidence
    # Round-trips through the schema, so the case file the CLI writes is always valid.
    InvestigationDecision.model_validate(decision.model_dump())


def test_offline_provider_cites_only_evidence_that_resolves() -> None:
    from earshot.agent.tools import unresolved_evidence

    ctx = _context()
    decision, _ = investigate(ctx, OfflineProvider())
    assert unresolved_evidence(ctx, decision.evidence) == []


def test_offline_provider_is_honest_about_being_a_rule_engine() -> None:
    decision, trace = investigate(_context(), OfflineProvider())
    assert trace.model == "offline-rules"
    assert trace.cost_usd == 0.0
    assert trace.prompt_tokens == 0, "no model ran; a token estimate here would be fiction"
    assert "no model call" in decision.rationale.lower()
    assert decision.confidence <= 0.75


def test_offline_provider_is_deterministic() -> None:
    first, _ = investigate(_context(), OfflineProvider())
    second, _ = investigate(_context(), OfflineProvider())
    assert first.model_dump() == second.model_dump()


def test_offline_verdict_moves_with_the_account_evidence() -> None:
    """If the account said nothing, the rule engine would be a coin flip on the ledger alone."""
    verdicts = {
        risk: investigate(_context(risk_signal=risk), OfflineProvider())[0].verdict
        for risk in (0.0, 0.95)
    }
    assert len(set(verdicts.values())) == 2, verdicts


# --- prompts and cache -------------------------------------------------------------


def test_prompts_load_with_a_version_and_a_sha() -> None:
    text, version, sha = load_prompt("system")
    assert version == "v1"
    assert len(sha) == 64
    assert "Evidence is mandatory" in text

    system, task, combined = investigator_prompts()
    assert combined != system.sha256 != task.sha256
    assert "{{customer_id}}" in task.text


def test_render_fills_slots_without_touching_json_braces() -> None:
    out = render('{{a}} and {"k": 1}', a="x")
    assert out == 'x and {"k": 1}'


def test_cache_records_then_replays_with_no_provider_available(tmp_path) -> None:
    """This is the wifi-free demo, in a test."""
    path = tmp_path / "cache.jsonl"
    recorded = Completion(content="hello", model="m", usage=Usage(3, 4), cost_usd=0.002)
    inner = _Stub("once", [recorded], repeat_last=False)

    recorder = CachingProvider(inner, "sha", ResponseCache(path, "record"))
    first = recorder.complete([{"role": "user", "content": "hi"}], tool_specs(), ModelConfig())
    assert first.content == "hello"

    # A fresh cache object, a provider that would now raise, and replay mode.
    replayer = CachingProvider(
        _Stub("dead", [], repeat_last=False), "sha", ResponseCache(path, "replay")
    )
    replayed = replayer.complete([{"role": "user", "content": "hi"}], tool_specs(), ModelConfig())
    assert replayed.content == "hello"
    assert replayed.cost_usd == 0.002
    assert replayer.hits == 1


def test_replay_mode_fails_loudly_on_a_miss(tmp_path) -> None:
    provider = CachingProvider(
        _Stub("dead", [], repeat_last=False), "sha", ResponseCache(tmp_path / "c.jsonl", "replay")
    )
    with pytest.raises(CacheMiss):
        provider.complete([{"role": "user", "content": "unseen"}], [], ModelConfig())


def test_cache_key_changes_when_the_prompt_changes() -> None:
    messages = [{"role": "user", "content": "hi"}]
    a = ResponseCache.key("m", "sha-a", messages, [])
    b = ResponseCache.key("m", "sha-b", messages, [])
    assert a != b, "editing a prompt must invalidate its recorded responses"

def test_the_cost_cap_clears_a_full_length_loop_but_still_binds() -> None:
    """The cap has to survive an honest worst case and still stop a runaway. Both directions.

    It was $0.25 until 2026-08-29, derived from two Sonnet 4.5 investigations at $0.089 and
    $0.097. Sonnet was dropped by D-025, and against measured Haiku that cap sat at 6.8x the
    worst of 50 keyed cases: it never bound once, so it was a comment with a number in it rather
    than a ceiling. D-025 said the honest move was to re-derive it from a real Bedrock run.

    This ties the cap to `MAX_STEPS` rather than to a literal, because the two are one decision.
    Raising the step budget without revisiting the cap would let an honest maximum-length loop
    trip a guard meant for runaways — which reads to a reviewer exactly like a broken agent.
    """
    from earshot.agent.investigator import MAX_STEPS
    from earshot.cli import COST_CAP_PER_CASE_USD, MEASURED_COST_PER_MODEL_CALL_USD

    full_loop = MAX_STEPS * MEASURED_COST_PER_MODEL_CALL_USD
    assert COST_CAP_PER_CASE_USD > full_loop, (
        f"a full {MAX_STEPS}-step loop costs about ${full_loop:.4f} at the measured per-call "
        f"rate, which the ${COST_CAP_PER_CASE_USD} cap would cut off mid-case"
    )
    # And it must still be able to bind. A cap far above any reachable cost cannot stop anything.
    assert COST_CAP_PER_CASE_USD < 5 * full_loop, (
        f"${COST_CAP_PER_CASE_USD} is more than 5x a maximum-length loop (${full_loop:.4f}); a "
        f"ceiling that cannot be reached is not a ceiling"
    )


def test_every_entrypoint_shares_one_cost_cap() -> None:
    """A cap that differs by entrypoint is a cap someone can route around.

    `stream.py` said exactly that in a comment -- "Same value as `cli`, deliberately" -- while
    carrying 0.25 against cli's 0.10, for as long as both existed. Nothing caught it: the test
    above pins the cap against a full-length loop, but only ever imported `cli`'s copy, so the
    streamed entrypoint ran at 2.5x the ceiling every other path enforced.

    The three cannot be collapsed into one import -- `cli` imports `stream`, so `stream` importing
    `cli` is circular -- which is precisely why they need pinning together here instead.
    """
    from earshot.aws.investigate import COST_CAP_PER_CASE_USD as aws_cap
    from earshot.cli import COST_CAP_PER_CASE_USD as cli_cap
    from earshot.stream import COST_CAP_PER_CASE_USD as stream_cap

    assert cli_cap == stream_cap == aws_cap, (
        f"the per-case cost cap differs by entrypoint: cli=${cli_cap}, stream=${stream_cap}, "
        f"aws=${aws_cap}. Whichever is highest is the one a runaway will find."
    )
