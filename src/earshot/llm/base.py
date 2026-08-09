"""Provider contract for the investigator: messages in, one completion out.

Deliberately small. The loop in `agent/investigator.py` owns planning, budget and validation;
a provider only has to turn a message list into a `Completion`. That keeps the offline provider
honest — it cannot quietly acquire capabilities the real model does not have — and it keeps the
cost and latency accounting in one place, because every provider fills the same fields.

Nothing here may import the corpus side (see tests/test_separation.py).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Protocol

Message = dict[str, Any]  # OpenAI-shaped: role/content, plus tool_calls or tool_call_id
ToolSpec = dict[str, Any]  # OpenAI-shaped function tool spec

DEFAULT_MODEL = "anthropic/claude-sonnet-4.5"


def env(name: str, default: str = "") -> str:
    """Read `EARSHOT_<name>`, falling back to the older `EAR_<name>`.

    The package was renamed mid-build. Honouring both spellings means an existing shell profile
    or CI secret does not silently stop working — and a silently unread API key looks exactly
    like a broken client.
    """
    return (
        os.environ.get(f"EARSHOT_{name}") or os.environ.get(f"EAR_{name}") or default
    ).strip()


@dataclass(frozen=True)
class ModelConfig:
    model: str = DEFAULT_MODEL
    temperature: float = 0.0  # judgment should be reproducible, not creative
    max_tokens: int = 1500


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class Completion:
    content: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    usage: Usage = field(default_factory=Usage)
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    model: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "tool_calls": [
                {"id": c.id, "name": c.name, "arguments": c.arguments} for c in self.tool_calls
            ],
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
            },
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "model": self.model,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Completion:
        usage = payload.get("usage") or {}
        return cls(
            content=payload.get("content", "") or "",
            tool_calls=tuple(
                ToolCall(id=c["id"], name=c["name"], arguments=c.get("arguments") or {})
                for c in payload.get("tool_calls") or []
            ),
            usage=Usage(
                prompt_tokens=int(usage.get("prompt_tokens", 0)),
                completion_tokens=int(usage.get("completion_tokens", 0)),
            ),
            latency_ms=float(payload.get("latency_ms", 0.0)),
            cost_usd=float(payload.get("cost_usd", 0.0)),
            model=payload.get("model", "") or "",
        )


class LLMProvider(Protocol):
    """Implemented by the offline rule provider, OpenRouter, and the caching wrapper."""

    name: str

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion: ...


class ProviderError(RuntimeError):
    """Provider could not produce a completion. The loop degrades rather than crashing."""


def assistant_message(completion: Completion) -> Message:
    """Render a completion back into the transcript the next request replays."""
    message: Message = {"role": "assistant", "content": completion.content or ""}
    if completion.tool_calls:
        message["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.name, "arguments": call.arguments},
            }
            for call in completion.tool_calls
        ]
    return message
