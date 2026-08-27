"""Bedrock provider -- Converse API over boto3, additive next to OpenRouter (D-022).

Exists to serve both reader arms through one wire format (state-of-play.md, "Next, in order"
#1): arm A is Claude Haiku 4.5, and any second Bedrock vendor (Nova, Llama) reader arm B might
use later goes through the exact same translation in this file, because Converse is one API
across every vendor Bedrock hosts. No API key: Bedrock is IAM-authenticated over whatever boto3's
default credential chain resolves -- the SSO profile locally, an execution role once deployed
(docs/ops/aws-infrastructure.md) -- so `resolve_api_key()` and `openrouter.py` stay exactly as
they are. Not a replacement; D-022 calls the Bedrock provider "additive".

Four things are load-bearing, in the order they will bite someone:

* **The `us.` inference-profile prefix is per-vendor, not universal.** Anthropic models on
  Bedrock are published as inference profiles, not on-demand foundation models: the bare
  `anthropic.claude-...` id fails with "on-demand throughput isn't supported" (verified,
  `tools/aws_probe.py`). Amazon Nova and Meta Llama are the opposite -- they ARE on-demand and
  take the bare id, so prefixing them fails just as hard the other way. `normalize_model_id`
  branches on the vendor for exactly this reason rather than applying one rule to every id.

* **Default model is Haiku 4.5, never Sonnet (D-025, 2026-08-25).** `us.anthropic.claude-
  haiku-4-5-20251001-v1:0` does both the reader's and the investigator's job now. Sonnet 4.5
  needs a one-time Anthropic use-case/EUA form on this account and returns
  `ResourceNotFoundException` until it is filed -- nothing in this module reaches for it, ever.

* **Cost is COMPUTED, not charged (G1, docs/architecture/infrastructure.md#L447).** Converse
  returns `usage.inputTokens` / `usage.outputTokens` only -- no dollar figure the way
  OpenRouter's `usage: {include: true}` returns one (see that module's own docstring). `_cost`
  prices those tokens from `PRICE_PER_1M_TOKENS`, a small hand-checked table, and every figure
  it produces is a projection from a price list, not measured spend. Label it "computed from
  published prices" wherever it is surfaced -- README, sweep output, the demo -- never
  "charged". A model id absent from the table returns `cost_usd=0.0`, explicitly, rather than a
  guessed number: a number labelled wrong is worse than a number missing.

* **The boto3 client is built on first use, never at import or construction.** boto3 is an
  optional dependency (`[project.optional-dependencies] aws`, pyproject.toml) precisely so a
  fresh `uv sync` and the test suite stay boto3-free -- importing this module, or constructing
  `BedrockProvider` / `LazyBedrockProvider`, must never require it to be installed. Only calling
  `complete()` does, and even then only when no client was injected (tests inject one, and so
  never touch boto3 at all). A missing boto3 raises `MissingBoto3` with an actionable message
  rather than a bare `ModuleNotFoundError` from inside a botocore stack frame.

Converse translation runs both ways, and neither direction is a relabelling of OpenRouter's:
OpenAI-shaped `messages` (role/content, plus `tool_calls` / `tool_call_id`) become Converse's
`messages` (content blocks, `toolUse` / `toolResult`) and a separate top-level `system`; the
reply comes back as this repo's `Completion`, with `tool_calls` as `ToolCall(id, name,
arguments: dict)` exactly like every other provider returns them -- so `agent/investigator.py`
cannot tell which provider it is talking to, which is the whole point of `LLMProvider`.
"""

from __future__ import annotations

import json
import time
from typing import Any

from .base import (
    DEFAULT_MODEL,
    Completion,
    Message,
    ModelConfig,
    ProviderError,
    ToolCall,
    ToolSpec,
    Usage,
    env,
)

DEFAULT_REGION = "us-east-1"  # every model ARN, `us.` profile and price in the docs is this region

# D-025, 2026-08-25: one model for both jobs. Sonnet 4.5 needs a one-time Anthropic use-case/EUA
# form on this account and is not used anywhere in this module -- see the module docstring.
DEFAULT_BEDROCK_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

ANTHROPIC_PREFIX = "anthropic."
US_PREFIX = "us."

MAX_ATTEMPTS = 3  # same bound as openrouter.py's MAX_ATTEMPTS

# Bedrock's overload/throttle signals, per the task brief this module was built against. Anything
# else -- a bad request, a missing model, an auth failure -- is wrong to retry and is raised
# immediately instead: retrying a validation error three times just triples the wait before the
# same error is reported.
RETRYABLE_CODES = frozenset(
    {"ThrottlingException", "ModelTimeoutException", "ServiceUnavailableException"}
)

# Published on-demand list prices, us-east-1, $ per 1,000,000 tokens -- checked 2026-08-25.
# Bedrock prices each vendor's models independently of that vendor's own first-party API rates
# (G1), so these are NOT copied from anywhere else in the repo and must be reverified before
# being requoted elsewhere. Keyed on the BARE model id (no `us.` prefix) so a lookup succeeds
# whether or not the inference-profile prefix was applied to the request -- see
# `_price_lookup_key`.
#
# A model id absent from this table gets cost_usd=0.0 from `_cost`, explicitly, never a guessed
# price -- do not add an entry here without a citable source and today's date in this comment.
PRICE_PER_1M_TOKENS: dict[str, tuple[float, float]] = {
    # model id                                       : (input $/1M, output $/1M)
    "anthropic.claude-haiku-4-5-20251001-v1:0": (1.00, 5.00),
    "amazon.nova-lite-v1:0": (0.06, 0.24),
    "amazon.nova-micro-v1:0": (0.035, 0.14),
    "meta.llama3-8b-instruct-v1:0": (0.30, 0.60),
}


class MissingBoto3(ProviderError):
    """boto3 is not installed. Raised only when a provider is actually used -- see module docstring."""


# -- model id handling ------------------------------------------------------------------------


def normalize_model_id(model_id: str) -> str:
    """Add the `us.` inference-profile prefix Anthropic models require on Bedrock.

    Verified empirically (`tools/aws_probe.py`): the bare `anthropic.claude-...` foundation-model
    id fails with "on-demand throughput isn't supported" -- Anthropic models on Bedrock are
    published as inference profiles, not on-demand models, and only the `us.`-prefixed profile id
    is invocable. Amazon Nova (`amazon.nova-*`) and Meta Llama (`meta.llama3-*`) are the opposite:
    they ARE on-demand and take the bare id, so the prefix is added only for the vendor that
    needs it, never unconditionally. Idempotent: an already-prefixed id passes through unchanged.
    """
    if model_id.startswith(ANTHROPIC_PREFIX) and not model_id.startswith(US_PREFIX):
        return f"{US_PREFIX}{model_id}"
    return model_id


def _resolve_model(model_cfg: ModelConfig) -> str:
    """The model id to invoke, normalised for Bedrock.

    `ModelConfig.model` defaults to `base.DEFAULT_MODEL` ("anthropic/claude-sonnet-4.5") --
    OpenRouter's slash-form id, meaningless to Bedrock's Converse API. A caller that swaps
    `OpenRouterProvider` for this provider without also overriding `model_cfg.model` would
    otherwise send that id straight to `converse()` and get a validation error instead of a
    completion. Treating the base default as "no Bedrock model requested" and substituting ours
    is what makes Haiku 4.5 the actual default here (module docstring), not an unreachable one.
    """
    requested = model_cfg.model
    if not requested or requested == DEFAULT_MODEL:
        requested = env("BEDROCK_MODEL") or DEFAULT_BEDROCK_MODEL
    return normalize_model_id(requested)


# -- cost ---------------------------------------------------------------------------------------


def _price_lookup_key(model_id: str) -> str:
    return model_id[len(US_PREFIX) :] if model_id.startswith(US_PREFIX) else model_id


def _cost(model_id: str, usage: Usage) -> float:
    """Computed from `PRICE_PER_1M_TOKENS`, never charged -- see the module docstring's G1 note.

    Bedrock's Converse response carries token counts only. Every dollar figure this returns is a
    projection from the price table's list prices, not measured spend, and must be labelled
    "computed from published prices" wherever it is surfaced -- not "charged".
    """
    prices = PRICE_PER_1M_TOKENS.get(_price_lookup_key(model_id))
    if prices is None:
        return 0.0
    price_in, price_out = prices
    cost = (usage.prompt_tokens / 1_000_000.0) * price_in
    cost += (usage.completion_tokens / 1_000_000.0) * price_out
    return round(cost, 6)


# -- OpenAI-shaped messages/tools -> Converse ----------------------------------------------------


def _text(content: Any) -> str:
    """Every message in this codebase carries a plain string; anything else is coerced rather
    than sent to Converse as the wrong JSON type."""
    if isinstance(content, str):
        return content
    return "" if content is None else str(content)


def _append_turn(converse: list[dict[str, Any]], role: str, blocks: list[dict[str, Any]]) -> None:
    """Append content blocks, merging into the previous turn if it was the same Converse role.

    Converse rejects two consecutive messages of the same role ("messages must alternate between
    user and assistant"). `investigator.py` appends one `{"role": "tool", ...}` message PER call
    when a step makes several tool calls at once, and every one of them maps to a `toolResult`
    block on a Converse USER turn -- naively translating each into its own message would emit N
    consecutive user turns for N tool calls in one step. Merging is written generally, keyed on
    the Converse role rather than special-cased to "tool", so any other accidental same-role run
    is just as safe.
    """
    if converse and converse[-1]["role"] == role:
        converse[-1]["content"].extend(blocks)
    else:
        converse.append({"role": role, "content": list(blocks)})


def _wire_messages(messages: list[Message]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """OpenAI-shaped messages -> (Converse `system` blocks, Converse `messages`).

    Three shape differences from the OpenAI wire format, all load-bearing:

    - Converse has no per-message "system" role; every "system" message is hoisted into the
      separate top-level `system` parameter, in order. The codebase only ever sends one today
      (always `messages[0]`), but nothing here assumes that.
    - Converse represents a tool call as a `toolUse` block on an ASSISTANT turn and its result as
      a `toolResult` block on the FOLLOWING USER turn -- there is no dedicated "tool" role, so a
      `{"role": "tool", ...}` message becomes a one-block user turn (merged with any neighbours
      by `_append_turn`).
    - An assistant turn whose only content is a tool call has an EMPTY `content` string
      (`assistant_message()` in base.py sets `content: completion.content or ""`). Converse
      rejects an empty `text` content block outright, so the text block is omitted rather than
      sent empty -- only added when there is something to say.
    """
    system_blocks: list[dict[str, Any]] = []
    converse: list[dict[str, Any]] = []

    for message in messages:
        role = message.get("role")

        if role == "system":
            text = _text(message.get("content"))
            if text:
                system_blocks.append({"text": text})
            continue

        if role == "tool":
            block = {
                "toolResult": {
                    "toolUseId": message.get("tool_call_id", ""),
                    "content": [{"text": _text(message.get("content"))}],
                }
            }
            _append_turn(converse, "user", [block])
            continue

        if role == "assistant":
            blocks: list[dict[str, Any]] = []
            text = _text(message.get("content"))
            if text:
                blocks.append({"text": text})
            for call in message.get("tool_calls") or []:
                fn = call.get("function") or {}
                arguments = fn.get("arguments")
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}
                blocks.append(
                    {
                        "toolUse": {
                            "toolUseId": call.get("id", ""),
                            "name": fn.get("name", ""),
                            "input": arguments if isinstance(arguments, dict) else {},
                        }
                    }
                )
            if not blocks:
                # Degenerate case that should not arise from this codebase's own callers (an
                # assistant turn with neither text nor a tool call) -- a placeholder beats a
                # Converse validation error for a completion that was already paid for.
                blocks.append({"text": " "})
            _append_turn(converse, "assistant", blocks)
            continue

        # "user", or anything else -- treated as user content.
        _append_turn(converse, "user", [{"text": _text(message.get("content"))}])

    return system_blocks, converse


def _wire_tools(tools: list[ToolSpec]) -> list[dict[str, Any]]:
    """OpenAI-style `{"type": "function", "function": {...}}` specs -> Converse `toolConfig.tools`.

    `Tool.spec()` (agent/tools.py) is the only producer of `ToolSpec` in this repo and always
    emits that shape, with `parameters` holding a pydantic-derived JSON schema; Converse wants
    the identical schema under `toolSpec.inputSchema.json` instead.
    """
    wired: list[dict[str, Any]] = []
    for spec in tools:
        fn = spec.get("function") or {}
        wired.append(
            {
                "toolSpec": {
                    "name": fn.get("name", ""),
                    "description": fn.get("description", ""),
                    "inputSchema": {"json": fn.get("parameters") or {"type": "object"}},
                }
            }
        )
    return wired


# -- Converse -> Completion -----------------------------------------------------------------


def _parse_response(model_id: str, response: dict[str, Any], latency_ms: float) -> Completion:
    """Converse's response shape -> this repo's `Completion`.

    `toolUse.input` comes back from boto3 already deserialised -- Converse types it as a JSON
    `Document`, which boto3 turns into a native dict, unlike OpenRouter's OpenAI-shaped wire
    format where `function.arguments` is a JSON *string* `_parse_tool_calls` has to `json.loads`.
    Guarded anyway in case a stub, or a future botocore version, hands back a string instead.

    Bedrock never echoes a "model" field the way OpenRouter's response body does -- Converse
    always serves exactly the model that was asked for, so the resolved, normalised request id
    is what `Completion.model` carries.
    """
    message = (response.get("output") or {}).get("message") or {}
    blocks = message.get("content") or []

    text = "".join(b["text"] for b in blocks if isinstance(b, dict) and "text" in b)

    tool_calls: list[ToolCall] = []
    for i, block in enumerate(blocks):
        if not isinstance(block, dict) or "toolUse" not in block:
            continue
        tool_use = block.get("toolUse") or {}
        arguments = tool_use.get("input")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}
        tool_calls.append(
            ToolCall(
                id=tool_use.get("toolUseId") or f"call_{i}",
                name=tool_use.get("name", ""),
                arguments=arguments if isinstance(arguments, dict) else {},
            )
        )

    usage_raw = response.get("usage") or {}
    usage = Usage(
        prompt_tokens=int(usage_raw.get("inputTokens", 0) or 0),
        completion_tokens=int(usage_raw.get("outputTokens", 0) or 0),
    )

    return Completion(
        content=text,
        tool_calls=tuple(tool_calls),
        usage=usage,
        latency_ms=round(latency_ms, 1),
        cost_usd=_cost(model_id, usage),
        model=model_id,
    )


# -- boto3, deferred ------------------------------------------------------------------------


def _import_boto3() -> Any:
    """Deferred so importing this module, or constructing a provider, never requires boto3."""
    try:
        import boto3
    except ImportError as exc:
        raise MissingBoto3(
            "boto3 is not installed. Install the aws extra: `uv sync --extra aws` (or `pip "
            "install 'ear-on-every-call[aws]'`). The offline and OpenRouter providers need "
            "neither boto3 nor AWS credentials."
        ) from exc
    return boto3


def _error_code(exc: Exception) -> str:
    """AWS error code off a botocore `ClientError`, by duck typing rather than `isinstance`.

    Same pattern `tools/aws_probe.py`'s `probe()` already uses: `getattr(e, "response",
    {}).get("Error", {}).get("Code", "")`. Deliberate, not a shortcut -- `botocore.exceptions.
    ClientError` is only importable when boto3 is, and this module (and the test suite that
    stubs its client) must keep working with neither installed, so nothing here ever imports the
    real exception type.
    """
    response = getattr(exc, "response", None)
    if not isinstance(response, dict):
        return ""
    return (response.get("Error") or {}).get("Code", "")


# -- providers ------------------------------------------------------------------------------


class BedrockProvider:
    """Converse-API client with bounded retry. One request per `complete()`.

    The boto3 client is built lazily, in `_client()`, on the first call that needs it -- never
    in `__init__` -- so constructing this class costs nothing and needs nothing (module
    docstring). Pass `client=` (any object exposing `.converse(**kwargs)`) to bypass boto3
    entirely, which is how the test suite stubs it with zero network and zero credentials.
    """

    name = "bedrock"

    def __init__(
        self,
        *,
        region: str | None = None,
        client: Any = None,
        max_attempts: int = MAX_ATTEMPTS,
    ) -> None:
        self._region = region or env("BEDROCK_REGION") or DEFAULT_REGION
        self._injected_client = client
        self._boto_client: Any = None
        self._max_attempts = max_attempts

    def _client(self) -> Any:
        if self._boto_client is None:
            if self._injected_client is not None:
                self._boto_client = self._injected_client
            else:
                boto3 = _import_boto3()
                from botocore.config import Config  # boto3 import above guarantees this exists

                self._boto_client = boto3.client(
                    "bedrock-runtime",
                    region_name=self._region,
                    # max_attempts=1: botocore's OWN retry-on-throttle must not run underneath
                    # ours -- two nested retry loops turn one bounded, predictable policy into
                    # an unbounded one, and this provider's retry loop is the one this repo can
                    # actually see and test.
                    config=Config(retries={"max_attempts": 1}),
                )
        return self._boto_client

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion:
        model_id = _resolve_model(model_cfg)
        system, converse_messages = _wire_messages(messages)

        request: dict[str, Any] = {
            "modelId": model_id,
            "messages": converse_messages,
            "inferenceConfig": {
                "maxTokens": model_cfg.max_tokens,
                "temperature": model_cfg.temperature,
            },
        }
        if system:
            request["system"] = system
        if tools:
            # No explicit toolChoice: not every Converse-compatible model accepts one (some
            # reject "any"/"tool" outright), and every vendor this provider targets -- Anthropic,
            # Nova, Llama -- already defaults to "auto" the moment toolConfig.tools is present.
            request["toolConfig"] = {"tools": _wire_tools(tools)}

        started = time.perf_counter()
        response = self._invoke(request)
        latency_ms = (time.perf_counter() - started) * 1000.0

        return _parse_response(model_id, response, latency_ms)

    def _invoke(self, request: dict[str, Any]) -> dict[str, Any]:
        client = self._client()
        last = "no attempt made"
        for attempt in range(self._max_attempts):
            if attempt:
                time.sleep(2.0**attempt)  # 2s, 4s -- same bounded backoff as openrouter.py
            try:
                return client.converse(**request)
            except Exception as exc:  # noqa: BLE001 -- narrowed immediately below by error shape
                code = _error_code(exc)
                if code not in RETRYABLE_CODES:
                    raise ProviderError(
                        f"Bedrock {code or type(exc).__name__}: {str(exc)[:300]}"
                    ) from exc
                last = f"{code} (attempt {attempt + 1})"

        raise ProviderError(f"Bedrock failed after {self._max_attempts} attempts ({last})")


class LazyBedrockProvider:
    """Same surface as `BedrockProvider`, but construction is deferred to first use.

    Mirrors `LazyOpenRouterProvider` (openrouter.py) precisely, per the task this module was
    built against. `BedrockProvider` is already lazy about the boto3 CLIENT (`_client()` builds
    it on first `complete()`, not in `__init__`); this second layer defers building the PROVIDER
    itself, so a future factory that branches on cache mode -- the way `model_extractor()` does
    today for OpenRouter (`LazyOpenRouterProvider() if mode == "replay" else OpenRouterProvider()`)
    -- has the identical no-op-until-called provider ready to reach for.
    """

    name = "bedrock"

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = kwargs
        self._inner: BedrockProvider | None = None

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion:
        if self._inner is None:
            self._inner = BedrockProvider(**self._kwargs)
        return self._inner.complete(messages, tools, model_cfg)
