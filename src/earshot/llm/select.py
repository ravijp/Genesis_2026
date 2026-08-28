"""Choosing a provider, in one place, with an explicit `if`/`elif` and no registry.

Three call sites used to each decide this for themselves — `cli.py:_provider`, `extract_model
.model_extractor`, and the two Lambda handlers — and they had drifted: after D-022 dropped the
OpenRouter key and moved both arms to Bedrock, the reader could still only be built on OpenRouter.
A keyed run was impossible for a reason nobody had written down. So the choice lives here now, and
the cache-mode handling comes with it rather than being re-derived per caller.

**Explicit `if`/`elif`, never a lookup table.** `aws/__init__.py` forbids dynamic imports on the
guarded surface, and a registry keyed by an environment variable is exactly how a corpus-side
implementation would one day get selected by a string. The imports are lazy per branch so a
keyless laptop never imports boto3 and a Lambda never imports httpx it will not use.

**Cache mode is the same for every provider, and it is not a detail.**

  * `record` — live calls, every completion written to the cache. This is the mode that spends.
  * `replay` — the cache serves and the network client is never constructed, so no key and no
    credentials are needed. This is what lets a measurement be reproduced in a room with no wifi.
  * `off` — live calls, nothing recorded. Debugging only.

The offline rule engine is **never** wrapped in the cache. It is already deterministic, and
wrapping it would let `EARSHOT_CACHE_MODE=replay` turn a cache miss into a failure on the one path
that must never need anything. For the same reason it is never wrapped in the spend ceiling: it
cannot spend.

**Layering, and it is load-bearing:** `CappedProvider(CachingProvider(live))`. The ceiling sits
OUTSIDE the cache, so a replayed response costs nothing and does not count against it — which is
correct, because replay spends no money. Inverting the two would make a keyless replay run
exhaustible, which is the one thing that must never happen.
"""

from __future__ import annotations

import os

from .base import LLMProvider
from .budget import CappedProvider, SpendCeiling, spend_cap_usd
from .cache import CachingProvider, ResponseCache, cache_mode, cache_path

# Bedrock, because D-022 retired the OpenRouter key and every arm now runs through Bedrock. A
# caller that still wants OpenRouter has to say so, which is the right way round: the default
# should be the thing the project actually has credentials for.
DEFAULT_LLM = "bedrock"

PROVIDERS = ("offline", "bedrock", "openrouter")


def llm_name(name: str | None = None) -> str:
    """`name`, else `$EARSHOT_LLM`, else `bedrock`."""
    return name or os.environ.get("EARSHOT_LLM") or DEFAULT_LLM


def build_provider(
    name: str | None = None,
    prompt_sha: str = "",
    *,
    cache: ResponseCache | None = None,
    ceiling: SpendCeiling | None = None,
    cap_usd: float | None = None,
) -> LLMProvider:
    """One provider, wired for the current cache mode and the spend ceiling.

    `prompt_sha` goes into the cache key, so a prompt edit invalidates recorded responses instead
    of silently replaying answers to a question that is no longer being asked.

    `ceiling` lets several providers share one budget (a sweep runs a reader and an investigator);
    omit it and each provider gets its own, from `cap_usd` or `$EARSHOT_SPEND_CAP_USD`.
    """
    resolved = llm_name(name)
    mode = cache_mode()

    if resolved == "offline":
        from .offline import OfflineProvider  # noqa: PLC0415 -- lazy per branch, see the docstring

        return OfflineProvider()

    def capped(provider: LLMProvider) -> LLMProvider:
        budget = ceiling if ceiling is not None else SpendCeiling(spend_cap_usd(cap_usd))
        return provider if budget.cap_usd is None else CappedProvider(provider, budget)

    def recorded(inner: LLMProvider) -> LLMProvider:
        # A cache file per provider. Sharing one is how a Bedrock run appended Haiku completions
        # into the pinned Sonnet demo cache on 2026-08-28 -- caught by a test, not by review.
        store = cache if cache is not None else ResponseCache(path=cache_path(resolved))
        return CachingProvider(inner, prompt_sha, cache=store)

    if resolved == "bedrock":
        from .bedrock import BedrockProvider, LazyBedrockProvider  # noqa: PLC0415

        if mode == "off":
            return capped(BedrockProvider())
        # Replay must not need credentials, so the live client is only constructed if something
        # actually misses. Record builds it eagerly: failing on conversation zero beats failing on
        # conversation one, halfway through a run that has already spent money.
        inner = LazyBedrockProvider() if mode == "replay" else BedrockProvider()
        return capped(recorded(inner))

    if resolved == "openrouter":
        from .openrouter import LazyOpenRouterProvider, OpenRouterProvider  # noqa: PLC0415

        if mode == "off":
            return capped(OpenRouterProvider())
        inner = LazyOpenRouterProvider() if mode == "replay" else OpenRouterProvider()
        return capped(recorded(inner))

    raise ValueError(f"unknown provider {resolved!r}; known: {', '.join(PROVIDERS)}")
