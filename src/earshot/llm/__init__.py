"""Model access: one provider contract, three implementations, zero required keys.

`OfflineProvider` is what ships by default. OpenRouter is strictly additive, and
`CachingProvider` turns a recorded run into a replayable one.
"""

from __future__ import annotations

from .base import (
    DEFAULT_MODEL,
    Completion,
    LLMProvider,
    Message,
    ModelConfig,
    ProviderError,
    ToolCall,
    ToolSpec,
    Usage,
    assistant_message,
)
from .cache import CacheMiss, CachingProvider, ResponseCache, cache_mode, cache_path
from .offline import OfflineProvider
from .openrouter import (
    LazyOpenRouterProvider,
    MissingAPIKey,
    OpenRouterProvider,
    resolve_api_key,
)

__all__ = [
    "DEFAULT_MODEL",
    "CacheMiss",
    "CachingProvider",
    "Completion",
    "LLMProvider",
    "LazyOpenRouterProvider",
    "Message",
    "MissingAPIKey",
    "ModelConfig",
    "OfflineProvider",
    "OpenRouterProvider",
    "ProviderError",
    "ResponseCache",
    "ToolCall",
    "ToolSpec",
    "Usage",
    "assistant_message",
    "cache_mode",
    "cache_path",
    "resolve_api_key",
]
