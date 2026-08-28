"""The model reader's guarantees, proved against a stub provider rather than a real model.

There is no key in this environment and there may not be one in a judging room either, so every
property below is pinned with a deterministic in-memory provider. What that buys is the shape of
the contract: stateless per conversation, verbatim quotes or nothing, the same grain the offline
path emits at, and a keyless path that fails with an explanation instead of a traceback.

What it does not buy is accuracy. No test here says anything about how well a model reads, and
no number for that exists anywhere in this repository until one keyed run produces it.
"""

from __future__ import annotations

import json

import pytest

from earshot.extract import CONFIDENCE_FLOOR, OfflineLexiconExtractor
from earshot.extract_model import (
    ExtractionTelemetry,
    ModelExtractor,
    extractor_cache_path,
    extractor_prompts,
    model_extractor,
)
from earshot.llm.base import Completion, ModelConfig, ProviderError, Usage
from earshot.llm.cache import CacheMiss, CachingProvider, ResponseCache
from earshot.schema import Channel, Conversation, ExtractedSignal, SignalType, Turn

QUOTE = "things have been really tight since my hours got cut"
SECOND = "I might just close the account and move somewhere else"


def conversation(
    conversation_id: str = "K1", customer_id: str = "C1", day: int = 12
) -> Conversation:
    return Conversation(
        conversation_id=conversation_id,
        customer_id=customer_id,
        channel=Channel.CHAT,
        day=day,
        turns=(
            Turn(0, "agent", "Thanks for getting in touch, how can I help?"),
            Turn(1, "customer", f"Honestly {QUOTE}."),
            Turn(2, "agent", "I'm sorry to hear that."),
            Turn(3, "customer", f"{SECOND}, I don't know yet."),
        ),
    )


class StubProvider:
    """Deterministic, in-memory, no network. Records every request it was handed."""

    name = "stub"

    def __init__(
        self,
        replies: list[str],
        *,
        cost: float = 0.0,
        latency: float = 0.0,
        model: str = "stub-model",
    ) -> None:
        self.replies = list(replies)
        self.cost = cost
        self.latency = latency
        # Settable, because the served model is a property of the ANSWER: a provider is free to
        # substitute one (bedrock.py does), and a run that changed model halfway has to be able
        # to say so.
        self.model = model
        self.requests: list[list[dict]] = []

    def complete(self, messages, tools, model_cfg) -> Completion:
        self.requests.append(json.loads(json.dumps(messages)))
        content = self.replies.pop(0) if self.replies else "{}"
        return Completion(
            content=content,
            usage=Usage(prompt_tokens=100, completion_tokens=20),
            latency_ms=self.latency,
            cost_usd=self.cost,
            model=self.model,
        )


def reply(*signals: dict) -> str:
    return json.dumps({"signals": list(signals)})


def distress(turn_index: int = 1, quote: str = QUOTE, confidence: float = 0.55) -> dict:
    return {
        "signal_type": "financial_distress",
        "turn_index": turn_index,
        "confidence": confidence,
        "evidence_quote": quote,
    }


def build(replies: list[str], **kwargs) -> tuple[ModelExtractor, StubProvider]:
    provider = StubProvider(replies, **kwargs)
    return ModelExtractor(provider, model_cfg=ModelConfig(model="stub-model")), provider


# --- statelessness ------------------------------------------------------------------------


def test_the_prompt_carries_nothing_that_identifies_the_customer() -> None:
    """The load-bearing property of the whole experiment.

    Every arm shares one extraction stream, so if the reader could see who it was reading, the
    thing the memory ablation removes would leak into the thing it holds constant. The strongest
    form of that guarantee is that the model is never told: no customer id, no conversation id,
    no day.
    """
    extractor, provider = build([reply()])
    conv = conversation(conversation_id="ZZ-9", customer_id="CUST-4242", day=137)
    extractor.extract(conv)

    blob = json.dumps(provider.requests[0])
    assert "CUST-4242" not in blob, "the reader was told which customer it is reading"
    assert "ZZ-9" not in blob, "the reader was told which conversation it is reading"
    assert "137" not in blob, "the reader was told where in the arc it is"


def test_reading_one_conversation_is_unaffected_by_what_came_before() -> None:
    """Same conversation, same request, whatever the reader has already seen."""
    first, second = conversation("A", "C1", 1), conversation("B", "C2", 90)

    with_history, provider_a = build([reply(distress()), reply(distress())])
    with_history.extract(first)
    after = with_history.extract(second)

    alone, provider_b = build([reply(distress())])
    fresh = alone.extract(second)

    assert provider_a.requests[1] == provider_b.requests[0], (
        "the request for a conversation changed depending on what the reader had read before"
    )
    assert after == fresh


# --- verbatim quotes ----------------------------------------------------------------------


def test_a_quote_that_is_not_in_the_conversation_is_dropped() -> None:
    extractor, _ = build([reply(distress(quote="money has been a real struggle lately"))])
    assert extractor.extract(conversation()) == []
    assert extractor.telemetry.dropped_not_verbatim == 1


def test_a_paraphrase_of_a_real_turn_is_dropped() -> None:
    """Near-misses are the dangerous case: a tidied quote reads as genuine in a case file."""
    tidied = QUOTE.replace("things have been really tight", "things have been very tight")
    extractor, _ = build([reply(distress(quote=tidied))])
    assert extractor.extract(conversation()) == []
    assert extractor.telemetry.dropped_not_verbatim == 1


@pytest.mark.parametrize("quote", ["", "   ", "I", "tight", "since my hours"])
def test_a_quote_too_short_to_check_is_not_evidence(quote: str) -> None:
    """The empty string and a single character are substrings of every turn.

    `agent/tools.py` closed exactly this on the case-file side; a reader that certifies a
    one-word citation as verbatim rebuilds the same hole one file away.
    """
    extractor, _ = build([reply(distress(quote=quote))])
    assert extractor.extract(conversation()) == []
    assert extractor.telemetry.dropped_quote_too_short == 1


def test_the_quote_floor_is_the_same_one_the_case_file_enforces() -> None:
    from earshot.agent.tools import MIN_QUOTE_WORDS as CASE_FILE_FLOOR
    from earshot.extract_model import MIN_QUOTE_WORDS as READER_FLOOR

    assert READER_FLOOR == CASE_FILE_FLOOR, (
        "the reader and the case file disagree about how much of a turn a citation must carry"
    )


def test_every_emitted_quote_is_a_substring_of_the_turn_it_names() -> None:
    """The property, asserted over the output rather than over the parser's intentions."""
    conv = conversation()
    extractor, _ = build([reply(distress(), {"signal_type": "churn_intent", "turn_index": 3,
                                            "confidence": 0.7, "evidence_quote": SECOND})])
    signals = extractor.extract(conv)
    by_index = {t.index: t for t in conv.turns}

    assert len(signals) == 2
    for signal in signals:
        assert signal.evidence_quote in by_index[signal.turn_index].text
        assert by_index[signal.turn_index].speaker == "customer"


def test_a_verbatim_quote_cited_against_the_wrong_turn_is_re_pointed() -> None:
    """Mis-numbering a row is a different defect from inventing text, and is recoverable."""
    extractor, _ = build([reply(distress(turn_index=0))])
    (signal,) = extractor.extract(conversation())
    assert signal.turn_index == 1, "the signal kept an index whose turn does not contain the quote"
    assert extractor.telemetry.relocated_quotes == 1


def test_the_agent_is_never_cited_as_evidence() -> None:
    """An agent's words are not a customer signal, however verbatim they are."""
    extractor, _ = build([reply(distress(turn_index=2, quote="I'm sorry to hear that"))])
    assert extractor.extract(conversation()) == []
    assert extractor.telemetry.dropped_not_customer_turn == 1
    assert extractor.telemetry.dropped_not_verbatim == 0, (
        "misattributing real words was counted as inventing them"
    )


# --- shape of the output ------------------------------------------------------------------


def test_output_is_an_extracted_signal_with_the_offline_path_s_fields() -> None:
    conv = conversation()
    extractor, _ = build([reply(distress())])
    (signal,) = extractor.extract(conv)

    assert isinstance(signal, ExtractedSignal)
    assert signal.customer_id == conv.customer_id
    assert signal.conversation_id == conv.conversation_id
    assert signal.signal_type is SignalType.FINANCIAL_DISTRESS
    assert signal.day == conv.day
    assert signal.channel is conv.channel
    assert signal.cue_id, "no cue id, so an error analysis cannot tell readers apart"


def test_one_signal_per_type_per_conversation_keeping_the_strongest() -> None:
    """`evals.py` keys extraction on (conversation_id, signal_type). Two readers scored at
    different grains are not comparable, so this matches the offline path exactly."""
    extractor, _ = build([reply(distress(confidence=0.4),
                                distress(turn_index=3, quote=SECOND, confidence=0.9))])
    signals = extractor.extract(conversation())
    assert len(signals) == 1
    assert signals[0].confidence == 0.9


def test_the_confidence_floor_is_the_same_one_the_offline_path_applies() -> None:
    extractor, _ = build([reply(distress(confidence=CONFIDENCE_FLOOR - 0.01))])
    assert extractor.extract(conversation()) == []
    assert extractor.telemetry.dropped_below_floor == 1


def test_an_unknown_signal_type_is_dropped_rather_than_invented() -> None:
    extractor, _ = build([reply({"signal_type": "fraud_risk", "turn_index": 1,
                                 "confidence": 0.8, "evidence_quote": QUOTE})])
    assert extractor.extract(conversation()) == []
    assert extractor.telemetry.dropped_unknown_type == 1


@pytest.mark.parametrize(
    "content",
    ["not json at all", "", "{}", '{"signals": "financial_distress"}'],
)
def test_an_unusable_reply_yields_no_signals_and_is_counted(content: str) -> None:
    extractor, _ = build([content])
    assert extractor.extract(conversation()) == []
    assert extractor.telemetry.unparsable_replies == 1


def test_a_fenced_reply_is_still_read() -> None:
    extractor, _ = build([f"```json\n{reply(distress())}\n```"])
    assert len(extractor.extract(conversation())) == 1


def test_a_provider_failure_is_raised_rather_than_read_as_an_empty_conversation() -> None:
    """A key or network failure that returns [] reports a recall of zero that looks exactly like
    a reader which found nothing. It has to be loud."""

    class Broken:
        name = "broken"

        def complete(self, messages, tools, model_cfg):
            raise ProviderError("no key")

    with pytest.raises(ProviderError):
        ModelExtractor(Broken()).extract(conversation())


# --- cost and latency ---------------------------------------------------------------------


def test_cost_and_latency_are_captured_per_call() -> None:
    """Cost per 1,000 conversations is a named deliverable; this is where it comes from."""
    extractor, _ = build([reply(distress()), reply()], cost=0.002, latency=300.0)
    extractor.extract(conversation("A"))
    extractor.extract(conversation("B"))

    telemetry = extractor.telemetry
    assert telemetry.conversations == 2
    assert telemetry.model_calls == 2
    assert telemetry.prompt_tokens == 200
    assert telemetry.cost_usd == pytest.approx(0.004)
    assert telemetry.cost_per_1000_conversations == pytest.approx(2.0)
    assert telemetry.p50_latency_ms == 300.0
    assert telemetry.p95_latency_ms == 300.0
    assert telemetry.to_dict()["emitted_signals"] == 1


def test_percentiles_report_a_latency_some_call_actually_had() -> None:
    telemetry = ExtractionTelemetry(conversations=4, latencies_ms=[100.0, 200.0, 300.0, 4000.0])
    assert telemetry.p50_latency_ms in (100.0, 200.0)
    assert telemetry.p95_latency_ms == 4000.0
    assert telemetry.cost_per_1000_conversations == 0.0, "unpaid calls must not report a cost"


# --- keyless behaviour --------------------------------------------------------------------


def test_build_extractor_defaults_to_the_offline_lexicon() -> None:
    import earshot.cli as cli
    from earshot.config import DEFAULT

    assert isinstance(cli.build_extractor("offline", DEFAULT), OfflineLexiconExtractor)


def test_the_shipped_command_never_builds_a_network_reader_unless_asked(
    monkeypatch, tmp_path, capsys
) -> None:
    """D-004, asserted on the command someone actually runs rather than on a flag's default.

    If `--extractor` ever defaulted to `model`, or if some other path started reaching for a
    reader, `build_extractor` would be called here and this would fail. A test that only read
    the parser default would pass with the wiring pointed anywhere.
    """
    monkeypatch.setenv("EARSHOT_ARTIFACTS", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["earshot", "run", "--customers", "60"])

    import importlib

    import earshot.cli as cli_module

    cli = importlib.reload(cli_module)
    monkeypatch.setattr(
        cli, "build_extractor", lambda *a, **k: pytest.fail(f"reached for a reader: {a}")
    )

    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "offline provider" in out
    assert "MODEL READER" not in out


def test_asking_for_the_model_reader_without_a_key_exits_1_with_an_explanation(
    monkeypatch, tmp_path, capsys
) -> None:
    """The command has to say what is wrong and what still works, not raise MissingAPIKey.

    Pinned to OpenRouter explicitly. The default provider became Bedrock when D-022 retired the
    OpenRouter key, and Bedrock's credentials come from the environment rather than from a
    variable a test can delete — so this keeps testing the message, not the default.
    """
    monkeypatch.setenv("EARSHOT_LLM", "openrouter")
    monkeypatch.setenv("EARSHOT_ARTIFACTS", str(tmp_path))
    monkeypatch.delenv("EARSHOT_OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("EAR_OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("EARSHOT_OPENROUTER_API_KEY_FILE", str(tmp_path / "absent.txt"))
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "record")
    monkeypatch.setattr(
        "sys.argv", ["earshot", "run", "--extractor", "model", "--customers", "50"]
    )

    import importlib

    import earshot.cli as cli_module

    assert importlib.reload(cli_module).main() == 1
    err = capsys.readouterr().err
    assert "EARSHOT_OPENROUTER_API_KEY" in err
    assert "--extractor offline" in err, "the message does not say what still works"


def test_the_extractor_flag_is_refused_on_commands_that_do_not_take_one(
    monkeypatch, tmp_path
) -> None:
    """`demo` is the no-wifi artefact and `investigate` selects its provider separately.
    Accepting the flag and ignoring it is how a run silently measures something else."""
    monkeypatch.setenv("EARSHOT_ARTIFACTS", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["earshot", "demo", "--extractor", "model"])

    import importlib

    import earshot.cli as cli_module

    with pytest.raises(SystemExit) as exc:
        importlib.reload(cli_module).main()
    assert exc.value.code == 2


def test_no_key_fails_with_an_explanation_not_a_traceback(monkeypatch) -> None:
    monkeypatch.setenv("EARSHOT_LLM", "openrouter")
    monkeypatch.delenv("EARSHOT_OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("EAR_OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("EARSHOT_OPENROUTER_API_KEY_FILE", "/nonexistent/key.txt")
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "record")

    with pytest.raises(ProviderError) as exc:
        model_extractor()
    assert "EARSHOT_OPENROUTER_API_KEY" in str(exc.value)


def test_replay_needs_no_key_and_reports_a_miss_instead_of_reaching_the_network(
    monkeypatch, tmp_path
) -> None:
    """The keyless replay path, on a cache under tmp_path.

    A test must never construct a cache without a path: the default mode is `record`, and the
    default path is a committed artifact whose contents and cost are pinned by another test.
    """
    monkeypatch.delenv("EARSHOT_OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("EAR_OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("EARSHOT_OPENROUTER_API_KEY_FILE", "/nonexistent/key.txt")
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")

    extractor = model_extractor(cache=ResponseCache(tmp_path / "cache.jsonl", "replay"))
    with pytest.raises(CacheMiss):
        extractor.extract(conversation())


# --- the model that actually answered -----------------------------------------------------------


def test_the_reader_is_named_after_the_model_that_answered() -> None:
    """The first keyed CFPB run was logged as `anthropic/claude-sonnet-4.5` when all 150 of its
    calls were served by Haiku 4.5: `bedrock.py` substitutes its own default for the OpenRouter
    slash-form id, by design, and the name was built from the request. A published number carrying
    the wrong model name is worse than one carrying no name at all."""
    reader = ModelExtractor(StubProvider([json.dumps({"signals": []})], model="served-model-9"))
    assert "served-model-9" not in reader.name, "named after a call that has not happened yet"

    reader.extract(conversation())
    assert reader.name == "model:served-model-9@extractor/v1"
    assert reader.telemetry.to_dict()["served_model"] == "served-model-9"


def test_a_run_that_changed_model_halfway_says_so_rather_than_averaging_it_away() -> None:
    """Two models behind one recall figure is a finding, not a formatting problem."""
    provider = StubProvider(
        [json.dumps({"signals": []}), json.dumps({"signals": []})], model="first"
    )
    reader = ModelExtractor(provider)
    reader.extract(conversation())
    provider.model = "second"
    reader.extract(conversation())

    assert reader.telemetry.served_model == "first+second"
    assert reader.name == "model:first+second@extractor/v1"


# --- which provider the reader actually reaches for -------------------------------------------


def test_the_default_reader_is_bedrock(monkeypatch, tmp_path) -> None:
    """D-022 retired the OpenRouter key and moved every arm to Bedrock. The reader defaulting to
    OpenRouter anyway is why no keyed run was possible until 2026-08-28 — the provider existed and
    nothing could select it."""
    monkeypatch.delenv("EARSHOT_LLM", raising=False)
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")

    reader = model_extractor(cache=ResponseCache(tmp_path / "cache.jsonl", "replay"))
    assert "bedrock" in reader.provider.name


def test_the_reader_honours_an_explicit_provider(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")
    reader = model_extractor(
        "openrouter", cache=ResponseCache(tmp_path / "cache.jsonl", "replay")
    )
    assert "openrouter" in reader.provider.name


def test_an_unknown_provider_is_refused_by_name(monkeypatch, tmp_path) -> None:
    """A typo in `$EARSHOT_LLM` must not fall through to a default and silently measure something
    else — the whole point of naming the provider in every manifest."""
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")
    with pytest.raises(ValueError, match="unknown provider"):
        model_extractor("clawed", cache=ResponseCache(tmp_path / "cache.jsonl", "replay"))


def test_a_recorded_read_replays_with_no_provider_available(tmp_path) -> None:
    """One keyed run records; every later run replays. The pattern the measurement depends on."""
    path = tmp_path / "cache.jsonl"
    _, _, sha = extractor_prompts()

    live, _ = build([reply(distress())], cost=0.003, latency=250.0)
    recorder = CachingProvider(live.provider, sha, ResponseCache(path, "record"))
    recorded = ModelExtractor(recorder, model_cfg=ModelConfig(model="stub-model")).extract(
        conversation()
    )

    class Dead:
        name = "dead"

        def complete(self, messages, tools, model_cfg):
            raise AssertionError("replay reached the provider")

    replayer = CachingProvider(Dead(), sha, ResponseCache(path, "replay"))
    replayed = ModelExtractor(replayer, model_cfg=ModelConfig(model="stub-model")).extract(
        conversation()
    )
    assert replayed == recorded


def test_the_reader_does_not_record_into_the_investigators_committed_cache() -> None:
    """`artifacts/cache/investigator-demo.jsonl` is pinned to the two live investigations and
    the exact dollars they cost. Extraction traffic must not land in it."""
    from earshot.llm.cache import DEFAULT_CACHE_PATH

    assert extractor_cache_path() != DEFAULT_CACHE_PATH


# --- prompts ------------------------------------------------------------------------------


def test_prompts_are_versioned_files_so_a_prompt_change_is_a_reviewable_diff() -> None:
    system, task, combined = extractor_prompts()
    assert system.version == "v1" and task.version == "v1"
    assert system.sha256 != task.sha256
    assert len(combined) == 64

    extractor, _ = build([reply()])
    assert extractor.prompt_sha == combined
    assert extractor.prompt_version == "v1"


def test_the_prompt_sha_is_in_the_cache_key_so_an_edited_prompt_invalidates_a_replay(
    tmp_path,
) -> None:
    cache = ResponseCache(tmp_path / "cache.jsonl", "record")
    stub = StubProvider([reply(distress()), reply(distress())])
    messages = ModelExtractor(stub).messages_for(conversation())

    a = CachingProvider(stub, "sha-one", cache)
    b = CachingProvider(stub, "sha-two", cache)
    a.complete(messages, [], ModelConfig())
    b.complete(messages, [], ModelConfig())
    assert a.hits == 0 and b.hits == 0, "a different prompt served a response recorded under the old one"
