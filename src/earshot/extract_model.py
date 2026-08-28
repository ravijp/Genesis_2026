"""The model-backed extractor: the reader this entry actually describes.

`OfflineLexiconExtractor` is a 26-regex keyless fallback and everything published about
extraction so far measures it. This module is the other implementation of the same `Extractor`
protocol -- a model reads the turns and reports what it found. Both emit `ExtractedSignal` with
the same fields at the same grain, so `evals.py` and the CFPB scorer can put them side by side
without either changing the question it asks.

Three properties are load-bearing, in this order.

**Stateless, and provably so.** One conversation goes into the prompt and nothing else -- no
customer id, no day, no prior signals, no ledger. The memory ablation compares arms that share
one extraction stream, so a reader that saw history would leak the ablated thing into the thing
held constant and every arm comparison in the repo would stop meaning anything. The prompt is
built from `conversation.turns` and the channel alone, which is what makes the property testable
rather than asserted: the model literally cannot tell which customer it is reading.

**It never sees the answer key.** The prompt states what each signal family *means* in retail
banking. It was written without opening `corpus_lexicon.py`, and it deliberately does not
restate `extract_lexicon.py`'s regexes in prose or the CFPB marking guide's rules -- either
would fit the reader to a set it is about to be scored on. Disclosure, in the register
`benchmarks/cfpb/PROTOCOL.md` uses: the author had read the offline cue vocabulary earlier in
the same session, which cannot be undone and is not claimed to be.

**A quote is verbatim or the signal is dropped.** A citation that does not appear character for
character in the turn it names is a fabrication, and a fabricated quote in a case file is worse
than a missed signal. Signals that fail that check never leave `extract()`; the count is carried
in `ExtractionTelemetry` so the rate is measurable instead of invisible.

Cost and latency come back from the provider on every call and are accumulated here, which is
what makes cost per 1,000 conversations a measured figure rather than a projection.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Any

from .extract import CONFIDENCE_FLOOR
from .llm.base import Completion, LLMProvider, Message, ModelConfig, env, first_json_object
from .prompt_files import DEFAULT_VERSION, Prompt, pair_sha, prompt, render
from .schema import Conversation, ExtractedSignal, SignalType, Turn

FAMILY = "extractor"

# Small: the reply is a short JSON object, never prose. A large ceiling here would only buy the
# model room to ramble before the object, which the parser then has to survive anyway.
DEFAULT_MAX_TOKENS = 900

# The same floor `agent/tools.py` puts under a case file's citations, and for the same reason: a
# plain substring test certifies the empty string and a single character, both of which appear in
# every turn. A quote has to carry enough of the turn that a reviewer can check it. Held in step
# with the agent's constant by a test rather than by an import across layers.
MIN_QUOTE_WORDS = 4

_VALID_TYPES = {t.value: t for t in SignalType}


def extractor_prompts(version: str = DEFAULT_VERSION) -> tuple[Prompt, Prompt, str]:
    """System prompt, task template, and a combined sha covering both."""
    system = prompt(FAMILY, "system", version)
    task = prompt(FAMILY, "task", version)
    return system, task, pair_sha(system, task)


@dataclass
class ExtractionTelemetry:
    """What one extraction pass cost, and how often the reader had to be corrected.

    The drop counters are here rather than in a log because they are the honest error profile of
    a model reader, and a number nobody prints is a number nobody checks. `not_verbatim` in
    particular is the anti-fabrication rate: how often the model cited words that were not in
    the turn it named.
    """

    conversations: int = 0
    model_calls: int = 0
    # Every DISTINCT model id the provider actually returned. A list, not a single field, because
    # a run that silently changed model halfway is exactly the thing worth surfacing rather than
    # averaging away -- and because the requested id and the served id are routinely different:
    # `bedrock.py` substitutes its own default for `base.DEFAULT_MODEL`, which is an OpenRouter
    # slash-form id meaningless to Converse.
    served_models: list[str] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    latencies_ms: list[float] = field(default_factory=list)
    unparsable_replies: int = 0
    dropped_unknown_type: int = 0
    dropped_not_verbatim: int = 0
    dropped_quote_too_short: int = 0
    dropped_not_customer_turn: int = 0
    dropped_below_floor: int = 0
    relocated_quotes: int = 0
    emitted_signals: int = 0

    def _percentile(self, q: float) -> float:
        """Nearest-rank percentile. No interpolation: with a handful of calls an interpolated
        p95 reports a latency no call actually had."""
        if not self.latencies_ms:
            return 0.0
        ordered = sorted(self.latencies_ms)
        rank = max(1, math.ceil(q * len(ordered)))
        return round(ordered[rank - 1], 1)

    @property
    def p50_latency_ms(self) -> float:
        return self._percentile(0.50)

    @property
    def p95_latency_ms(self) -> float:
        return self._percentile(0.95)

    @property
    def served_model(self) -> str:
        """What actually answered. Empty before the first call; `a+b` if a run used more than
        one, which is a finding and not a formatting problem."""
        return "+".join(self.served_models)

    def record_model(self, model: str) -> None:
        if model and model not in self.served_models:
            self.served_models.append(model)

    @property
    def cost_per_1000_conversations(self) -> float:
        """Measured spend scaled to 1,000 conversations. Zero when nothing was paid for --
        a cache replay reports the cost of the ORIGINAL calls, and a stub reports nothing."""
        if not self.conversations:
            return 0.0
        return round(1000.0 * self.cost_usd / self.conversations, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversations": self.conversations,
            "model_calls": self.model_calls,
            "served_model": self.served_model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "cost_per_1000_conversations": self.cost_per_1000_conversations,
            "p50_latency_ms": self.p50_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "emitted_signals": self.emitted_signals,
            "unparsable_replies": self.unparsable_replies,
            "dropped_unknown_type": self.dropped_unknown_type,
            "dropped_not_verbatim": self.dropped_not_verbatim,
            "dropped_quote_too_short": self.dropped_quote_too_short,
            "dropped_not_customer_turn": self.dropped_not_customer_turn,
            "dropped_below_floor": self.dropped_below_floor,
            "relocated_quotes": self.relocated_quotes,
        }


# first_json_object now lives in llm/base.py -- see the note there.
class ModelExtractor:
    """A model reading one conversation at a time. Same protocol as the offline lexicon."""

    def __init__(
        self,
        provider: LLMProvider,
        *,
        model_cfg: ModelConfig | None = None,
        prompt_version: str = DEFAULT_VERSION,
    ) -> None:
        self.provider = provider
        self.model_cfg = model_cfg or ModelConfig(max_tokens=DEFAULT_MAX_TOKENS)
        system, task, combined = extractor_prompts(prompt_version)
        self.prompt_version = system.version
        self.prompt_sha = combined
        self._system = system.text
        self._task = task.text
        # Names the reader AND the prompt behind it. Two runs of the same model under different
        # prompt versions are different readers, and a manifest that cannot tell them apart
        # cannot support a comparison.
        self.requested_model = self.model_cfg.model
        self.telemetry = ExtractionTelemetry()

    @property
    def name(self) -> str:
        """Named after the model that ANSWERED, falling back to the one requested before any call
        has been made.

        This was `model_cfg.model` until 2026-08-28, and the first keyed CFPB run was therefore
        logged as `anthropic/claude-sonnet-4.5` when all 150 of its calls were served by Haiku
        4.5 -- `bedrock.py` substitutes its own default for the OpenRouter-form id, by design and
        documented, and nothing downstream noticed. A published number carrying the wrong model
        name is the defect `working-agreements.md` section 1 is about, so the name follows the
        provider's answer now.
        """
        served = self.telemetry.served_model
        return f"model:{served or self.requested_model}@{FAMILY}/{self.prompt_version}"

    # -- the protocol ---------------------------------------------------------------

    def extract(self, conversation: Conversation) -> list[ExtractedSignal]:
        """One conversation in, signals out. Sees nothing about the customer beyond these turns.

        A provider failure propagates. It is nearly always systemic -- no key, no network, a
        model id that does not exist -- and `OpenRouterProvider` has already retried three times
        by the time one reaches here. Swallowing it would report a recall of zero that looks
        exactly like a reader that found nothing.
        """
        messages = self.messages_for(conversation)
        completion = self.provider.complete(messages, [], self.model_cfg)

        self.telemetry.conversations += 1
        if isinstance(completion, Completion):
            self.telemetry.model_calls += 1
            self.telemetry.record_model(completion.model)
            self.telemetry.prompt_tokens += completion.usage.prompt_tokens
            self.telemetry.completion_tokens += completion.usage.completion_tokens
            if math.isfinite(completion.cost_usd):
                self.telemetry.cost_usd += completion.cost_usd
            self.telemetry.latencies_ms.append(completion.latency_ms)
        else:
            self.telemetry.unparsable_replies += 1
            return []

        payload = first_json_object(completion.content)
        raw = payload.get("signals") if isinstance(payload, dict) else None
        if not isinstance(raw, list):
            self.telemetry.unparsable_replies += 1
            return []

        found: list[ExtractedSignal] = []
        for item in raw:
            signal = self._build(conversation, item)
            if signal is not None:
                found.append(signal)

        # One signal per (conversation, type), keeping the most confident -- identical to the
        # offline path, because `evals.py` keys extraction on exactly that pair and two readers
        # scored at different grains are not comparable.
        best: dict[str, ExtractedSignal] = {}
        for sig in found:
            key = sig.signal_type.value
            if key not in best or sig.confidence > best[key].confidence:
                best[key] = sig
        out = sorted(best.values(), key=lambda s: (s.signal_type.value, s.turn_index))
        self.telemetry.emitted_signals += len(out)
        return out

    # -- prompt construction --------------------------------------------------------

    def messages_for(self, conversation: Conversation) -> list[Message]:
        """The exact request for one conversation.

        Public because statelessness is only worth what a test can check: this returns the whole
        of what the model is told, so a test can assert that it carries no customer id, no day,
        and nothing from any other conversation.
        """
        transcript = "\n".join(
            f"[{turn.index}] {turn.speaker}: {turn.text}" for turn in conversation.turns
        )
        return [
            {"role": "system", "content": self._system},
            {
                "role": "user",
                "content": render(
                    self._task, channel=conversation.channel.value, transcript=transcript
                ),
            },
        ]

    # -- validation -----------------------------------------------------------------

    def _build(self, conversation: Conversation, item: Any) -> ExtractedSignal | None:
        if not isinstance(item, dict):
            self.telemetry.dropped_unknown_type += 1
            return None

        signal_type = _VALID_TYPES.get(str(item.get("signal_type", "")).strip().lower())
        if signal_type is None:
            self.telemetry.dropped_unknown_type += 1
            return None

        quote = item.get("evidence_quote")
        if not isinstance(quote, str):
            self.telemetry.dropped_not_verbatim += 1
            return None
        quote = quote.strip()
        if len(quote.split()) < MIN_QUOTE_WORDS:
            # Counted apart from a fabrication. The words may well be in the turn; there are just
            # not enough of them for a reviewer to check anything, and "" and "a" are in every turn.
            self.telemetry.dropped_quote_too_short += 1
            return None

        turn = self._locate(conversation, item.get("turn_index"), quote)
        if turn is None:
            return None

        confidence = _as_confidence(item.get("confidence"))
        if confidence < CONFIDENCE_FLOOR:
            self.telemetry.dropped_below_floor += 1
            return None

        start = turn.text.find(quote)
        return ExtractedSignal(
            customer_id=conversation.customer_id,
            conversation_id=conversation.conversation_id,
            signal_type=signal_type,
            confidence=round(confidence, 4),
            # Sliced out of the turn rather than copied from the reply, so what is emitted is
            # verbatim by construction and not merely by assertion.
            evidence_quote=turn.text[start : start + len(quote)],
            turn_index=turn.index,
            day=conversation.day,
            channel=conversation.channel,
            cue_id=f"{FAMILY}/{self.prompt_version}:{signal_type.value}",
        )

    def _locate(
        self, conversation: Conversation, claimed: Any, quote: str
    ) -> Turn | None:
        """The customer turn this quote is actually in, or None.

        A cited index that holds the quote is taken as given. A cited index that does not is not
        fatal on its own -- models mis-number rows more often than they invent text -- so the
        quote is searched for across the customer turns and the signal is re-pointed at the turn
        that really contains it. Only when no customer turn contains it is the signal dropped.
        """
        by_index = {turn.index: turn for turn in conversation.turns}
        customer_turns = [t for t in conversation.turns if t.speaker == "customer"]

        if isinstance(claimed, bool):
            claimed = None
        if isinstance(claimed, int) or (isinstance(claimed, str) and claimed.isdigit()):
            turn = by_index.get(int(claimed))
            if turn is not None and turn.speaker == "customer" and quote in turn.text:
                return turn

        for turn in customer_turns:
            if quote in turn.text:
                self.telemetry.relocated_quotes += 1
                return turn

        # Present, but in something the customer did not say. Counted apart from a fabrication:
        # the reader found real words and attributed them to the wrong speaker, which is a
        # different defect from inventing them.
        if any(quote in turn.text for turn in conversation.turns):
            self.telemetry.dropped_not_customer_turn += 1
        else:
            self.telemetry.dropped_not_verbatim += 1
        return None


def _as_confidence(value: Any) -> float:
    """Anything unusable reads as the floor, not as zero and not as a crash.

    A model that omits `confidence` has still reported a signal; discarding it for a missing
    field would silently convert a formatting slip into a miss.
    """
    try:
        conf = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return CONFIDENCE_FLOOR
    if not math.isfinite(conf):
        return CONFIDENCE_FLOOR
    return min(1.0, max(0.0, conf))


# -- construction ------------------------------------------------------------------------


DEFAULT_EXTRACTOR_CACHE = Path("artifacts/cache/extractor.jsonl")


def extractor_cache_path(model_id: str | None = None) -> Path:
    """Where model reads are recorded. Deliberately NOT the investigator's cache file, and
    deliberately NOT one file for every model.

    `artifacts/cache/investigator-demo.jsonl` is pinned by a test to the two committed live
    investigations and the exact dollars they cost; appending extraction traffic to it would
    break that pin and blur two different measurements into one file.

    **One file per model, for the same reason `llm.cache.cache_path` keeps one per provider.**
    The committed `extractor.jsonl` holds the Haiku 4.5 reads behind this repo's published
    reader numbers -- 0.8214 strict recall (92 / 112), $1.6563 per 1,000, p50 1,244 ms -- and a
    judge replays them from it with no key. A second reader arm (Nova Lite, Llama 3 8B) run
    through the same default path would append a different model's completions into that file:
    the keys would not collide, so nothing would break loudly, and the cache behind a published
    figure would quietly hold two models. That is the failure that already happened once on the
    investigator side, when the first keyed Bedrock run appended Haiku completions into the
    pinned Sonnet file.

    The default model keeps the historical filename, because that file is committed and the
    published numbers replay from it -- renaming it would break reproduction for a reader who
    has done nothing wrong. Every other model gets its own.

    `$EARSHOT_EXTRACTOR_CACHE_PATH` still wins outright, so an explicit path is never
    second-guessed.
    """
    explicit = env("EXTRACTOR_CACHE_PATH")
    if explicit:
        return Path(explicit)
    from .llm.bedrock import DEFAULT_BEDROCK_MODEL, normalize_model_id

    requested = model_id or env("BEDROCK_MODEL")
    if not requested or normalize_model_id(requested) == DEFAULT_BEDROCK_MODEL:
        return DEFAULT_EXTRACTOR_CACHE
    # `amazon.nova-lite-v1:0` -> `extractor-amazon-nova-lite-v1-0.jsonl`. Slugged because `:` is
    # not a legal Windows filename character -- a lesson this repo paid for on 2026-08-28, when
    # an artifact write raised OSError after a $1.50 run had already printed its results.
    slug = re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", requested)).strip("-")
    return DEFAULT_EXTRACTOR_CACHE.with_name(f"extractor-{slug}.jsonl")


def _requested_model(model_cfg: ModelConfig | None) -> str | None:
    """The model this reader will actually ask for, or None to mean "whatever the default is".

    `ModelConfig.model` carries OpenRouter's slash-form default when nothing was chosen, which
    Bedrock treats as "no model requested" (`bedrock._model_id`). Passing that through as if it
    were a real selection would give the default model a cache file named after a model it is
    not, so the same "is this actually a choice?" test is applied here.
    """
    from .llm.base import DEFAULT_MODEL

    requested = getattr(model_cfg, "model", None)
    return None if not requested or requested == DEFAULT_MODEL else requested


def model_extractor(
    provider_name: str | None = None,
    *,
    prompt_version: str = DEFAULT_VERSION,
    model_cfg: ModelConfig | None = None,
    cache=None,
) -> ModelExtractor:
    """The model reader, wrapped in the response cache.

    `provider_name` defaults to `$EARSHOT_LLM` and then to Bedrock (D-022 retired the OpenRouter
    key). Selection itself lives in `llm/select.py` so the reader, the CLI and the two Lambda
    handlers cannot drift about what "the model" means -- which they had, leaving the reader
    unable to reach the only provider this account has credentials for.

    One keyed run records every completion; every later run replays it with
    `EARSHOT_CACHE_MODE=replay` and no key at all. That is the same record-then-replay path the
    two committed live investigations use, and it is what lets a measurement be reproduced in a
    room with no wifi.

    In replay mode the network client is never constructed, so no credentials are required to get
    here. In record mode it is built eagerly and fails immediately -- on conversation zero rather
    than on conversation one, halfway through a run that has already spent money.
    """
    from .llm import ResponseCache, build_provider, cache_mode

    _, _, combined_sha = extractor_prompts(prompt_version)
    provider = build_provider(
        provider_name,
        combined_sha,
        cache=(
            None
            if cache_mode() == "off"
            else (
                ResponseCache(path=extractor_cache_path(_requested_model(model_cfg)))
                if cache is None
                else cache
            )
        ),
    )
    return ModelExtractor(provider, model_cfg=model_cfg, prompt_version=prompt_version)
