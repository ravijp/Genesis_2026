"""OpenRouter provider — the only place in the codebase that touches the network.

OpenRouter is an OpenAI-compatible gateway, so the wire format here is chat/completions with
`tools`, not the Anthropic Messages API; the model *behind* it is named by an OpenRouter model
id (`anthropic/claude-sonnet-4.5` by default, overridable with `EARSHOT_OPENROUTER_MODEL`).

Two things are load-bearing for the submission and neither is decoration:

* **Real cost accounting.** `usage: {include: true}` makes OpenRouter return the actual `cost`
  it charged alongside token counts, so "cost per 1,000 conversations" is measured rather than
  projected from a price list.
* **The key never appears anywhere.** It is read from env or a file, stripped, held in memory,
  and sent in one header. It is not logged, not printed, not put in the cache key, and not in
  any error message — an API key in a committed artifact would be a self-inflicted wound.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx

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

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_KEY_PATH = "C:/tmp/openrouterAPIKey.txt"
MAX_ATTEMPTS = 3
RETRY_STATUS = frozenset({408, 409, 429, 500, 502, 503, 504, 520, 524})


class MissingAPIKey(ProviderError):
    pass


def resolve_api_key() -> str:
    """env var -> env-named file -> default path. Whitespace stripped, never echoed."""
    inline = env("OPENROUTER_API_KEY")
    if inline:
        return inline

    path = Path(env("OPENROUTER_API_KEY_FILE") or DEFAULT_KEY_PATH)
    if path.is_file():
        key = path.read_text(encoding="utf-8").strip()
        if key:
            return key

    raise MissingAPIKey(
        "no OpenRouter key: set EARSHOT_OPENROUTER_API_KEY, or EARSHOT_OPENROUTER_API_KEY_FILE, or "
        f"place one at {DEFAULT_KEY_PATH}. The offline provider needs no key at all."
    )


def _wire_messages(messages: list[Message]) -> list[dict[str, Any]]:
    """Serialise tool-call arguments to JSON strings, which is what the wire format wants.

    Internally arguments stay as dicts so the cache key is stable under key ordering.
    """
    out: list[dict[str, Any]] = []
    for message in messages:
        wire = dict(message)
        calls = wire.get("tool_calls")
        if calls:
            wire["tool_calls"] = [
                {
                    "id": call["id"],
                    "type": "function",
                    "function": {
                        "name": call["function"]["name"],
                        "arguments": json.dumps(call["function"]["arguments"], sort_keys=True)
                        if isinstance(call["function"]["arguments"], dict)
                        else call["function"]["arguments"],
                    },
                }
                for call in calls
            ]
        out.append(wire)
    return out


def _parse_tool_calls(raw: list[dict[str, Any]] | None) -> tuple[ToolCall, ...]:
    calls: list[ToolCall] = []
    for i, call in enumerate(raw or []):
        fn = call.get("function") or {}
        arguments = fn.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments or "{}")
            except json.JSONDecodeError:
                # A malformed argument blob is a tool-call failure, not a crash: hand the
                # loop an empty dict and let schema validation on the tool side report it.
                arguments = {}
        calls.append(
            ToolCall(
                id=call.get("id") or f"call_{i}",
                name=fn.get("name", ""),
                arguments=arguments if isinstance(arguments, dict) else {},
            )
        )
    return tuple(calls)


class OpenRouterProvider:
    """Chat-completions client with bounded retry. One request per `complete()`."""

    name = "openrouter"

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str = ENDPOINT,
        timeout: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key or resolve_api_key()
        self._endpoint = endpoint
        self._client = client or httpx.Client(
            timeout=httpx.Timeout(timeout, connect=10.0),
            headers={
                # Attribution headers OpenRouter uses for its dashboards. Harmless, and they
                # make the spend on this project identifiable after the fact.
                "HTTP-Referer": "https://github.com/ravijp/Genesis_2026",
                "X-Title": "ear-on-every-call",
            },
        )

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion:
        payload: dict[str, Any] = {
            "model": model_cfg.model or env("OPENROUTER_MODEL") or DEFAULT_MODEL,
            "messages": _wire_messages(messages),
            "temperature": model_cfg.temperature,
            "max_tokens": model_cfg.max_tokens,
            "usage": {"include": True},  # returns real spend, not an estimate
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        started = time.perf_counter()
        data = self._post(payload)
        latency_ms = (time.perf_counter() - started) * 1000.0

        choices = data.get("choices") or []
        if not choices:
            raise ProviderError(f"OpenRouter returned no choices: {data.get('error')}")
        message = choices[0].get("message") or {}
        usage = data.get("usage") or {}

        return Completion(
            content=message.get("content") or "",
            tool_calls=_parse_tool_calls(message.get("tool_calls")),
            usage=Usage(
                prompt_tokens=int(usage.get("prompt_tokens", 0) or 0),
                completion_tokens=int(usage.get("completion_tokens", 0) or 0),
            ),
            latency_ms=round(latency_ms, 1),
            cost_usd=float(usage.get("cost", 0.0) or 0.0),
            model=data.get("model") or payload["model"],
        )

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        last: str = "no attempt made"
        for attempt in range(MAX_ATTEMPTS):
            if attempt:
                time.sleep(2.0**attempt)  # 2s, 4s — bounded, and no jitter to keep runs comparable
            try:
                response = self._client.post(
                    self._endpoint,
                    json=payload,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
            except httpx.HTTPError as exc:
                last = f"transport error: {type(exc).__name__}"
                continue

            if response.status_code in RETRY_STATUS:
                last = f"HTTP {response.status_code}"
                continue
            if response.status_code >= 400:
                # Truncated: a provider error body can be long, and it is not worth the tokens.
                raise ProviderError(f"HTTP {response.status_code}: {response.text[:300]}")
            try:
                return response.json()
            except ValueError:
                last = "response was not JSON"

        raise ProviderError(f"OpenRouter failed after {MAX_ATTEMPTS} attempts ({last})")

    def close(self) -> None:
        self._client.close()


class LazyOpenRouterProvider:
    """Same surface as `OpenRouterProvider`, but the client is built on first use.

    Replay never touches the network, so a replay run must not need a key to get as far as the
    cache. Building the real client eagerly makes a keyless replay fail on a key it would never
    have used.
    """

    name = "openrouter"

    def __init__(self) -> None:
        self._inner: OpenRouterProvider | None = None

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion:
        if self._inner is None:
            self._inner = OpenRouterProvider()
        return self._inner.complete(messages, tools, model_cfg)
