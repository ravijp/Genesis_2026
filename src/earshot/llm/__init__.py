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
from .bedrock import (
    DEFAULT_BEDROCK_MODEL,
    BedrockProvider,
    LazyBedrockProvider,
    MissingBoto3,
    normalize_model_id,
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
    "DEFAULT_BEDROCK_MODEL",
    "DEFAULT_MODEL",
    "BedrockProvider",
    "CacheMiss",
    "CachingProvider",
    "Completion",
    "LLMProvider",
    "LazyBedrockProvider",
    "LazyOpenRouterProvider",
    "Message",
    "MissingAPIKey",
    "MissingBoto3",
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
    "normalize_model_id",
    "resolve_api_key",
]
