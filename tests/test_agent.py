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


def _context(latent_risk: float = 0.8) -> ToolContext:
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
        latent_risk=latent_risk,
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


def test_the_committed_cache_covers_the_documented_replay_invocation() -> None:
    """The README names one exact replay command; the cache has to actually cover it.

    A cache that covers fewer investigations than the documented `--limit` puts a
    `provider_error` on screen at the gate, which is what happened before this test existed.
    """
    from earshot.llm.cache import ResponseCache

    cache = ResponseCache(mode="replay")
    assert len(cache) >= 10, (
        f"the committed cache holds {len(cache)} completions — the documented replay command "
        f"(--customers 200 --limit 2) needs the responses for two full investigations"
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
    ctx = _context(latent_risk=0.9)
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
        risk: investigate(_context(latent_risk=risk), OfflineProvider())[0].verdict
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
