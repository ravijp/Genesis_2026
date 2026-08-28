"""Content-addressed response cache — the thing that makes the demo survive a room with no wifi.

Keyed on sha256 of (model, prompt sha, messages, tools). The prompt sha is in the key on purpose:
editing `prompts/investigator/v1/system.md` must invalidate every cached response, otherwise a
replayed demo would show answers produced by a prompt that no longer exists in the repo.

Modes come from `EARSHOT_CACHE_MODE`:

    record  — serve hits, call the provider on a miss and append the response (default)
    replay  — serve hits, RAISE on a miss. No network is possible in this mode, which is the
              guarantee the committed cache is supposed to give.
    off     — bypass entirely

The file is jsonl so it appends cleanly and diffs readably in review.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .base import Completion, LLMProvider, Message, ModelConfig, ProviderError, ToolSpec, env

DEFAULT_CACHE_PATH = Path("artifacts/cache/investigator-demo.jsonl")
CACHE_DIR = DEFAULT_CACHE_PATH.parent
MODES = ("record", "replay", "off")


class CacheMiss(ProviderError):
    """Replay mode asked for something that was never recorded."""


def cache_mode(default: str = "record") -> str:
    mode = env("CACHE_MODE", default).lower() or default
    return mode if mode in MODES else default


def cache_path(provider: str | None = None) -> Path:
    """Where a provider's recorded responses live.

    **One file per provider, and that is a correctness boundary rather than tidiness.**
    `investigator-demo.jsonl` holds the two live Sonnet 4.5 investigations whose cost and latency
    the README quotes, and `tests/test_agent.py` asserts it contains those and nothing else. On
    2026-08-28 the first keyed Bedrock runs appended Haiku 4.5 completions straight into it and
    that test caught them. A shared file means any run of any model is one command away from
    editing a pinned artifact.

    `$EARSHOT_CACHE_PATH` still wins outright, so an explicit path is never second-guessed.
    """
    explicit = env("CACHE_PATH")
    if explicit:
        return Path(explicit)
    if not provider or provider.startswith("openrouter"):
        # The historical default. The two pinned investigations were recorded through OpenRouter,
        # so it keeps the filename they were committed under.
        return DEFAULT_CACHE_PATH
    # `bedrock+cache:record+cap:$5.00` -> `bedrock`. The decorations describe this process, not
    # the recording, and putting them in a filename would fragment the cache by cache mode.
    stem = provider.split("+")[0].replace("/", "-")
    return CACHE_DIR / f"investigator-{stem}.jsonl"


class ResponseCache:
    def __init__(self, path: Path | None = None, mode: str | None = None) -> None:
        self.path = cache_path() if path is None else path
        self.mode = mode or cache_mode()
        self._entries: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.mode == "off" or not self.path.is_file():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue  # a half-written line must not take the demo down
            key = record.get("key")
            if key:
                self._entries[key] = record.get("completion") or {}

    @staticmethod
    def key(
        model: str, prompt_sha: str, messages: list[Message], tools: list[ToolSpec]
    ) -> str:
        blob = json.dumps(
            {"model": model, "prompt_sha": prompt_sha, "messages": messages, "tools": tools},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Completion | None:
        payload = self._entries.get(key)
        return Completion.from_dict(payload) if payload is not None else None

    def put(self, key: str, completion: Completion) -> None:
        if self.mode == "off":
            return
        self._entries[key] = completion.to_dict()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"key": key, "completion": completion.to_dict()}) + "\n")

    def __len__(self) -> int:
        return len(self._entries)


class CachingProvider:
    """Wraps any provider. Identical `LLMProvider` surface, so the loop cannot tell."""

    def __init__(
        self, inner: LLMProvider, prompt_sha: str, cache: ResponseCache | None = None
    ) -> None:
        self.inner = inner
        self.prompt_sha = prompt_sha
        # `is None`, not `or`: `ResponseCache` defines `__len__`, so an empty cache is falsy
        # and `cache or ResponseCache()` would discard a caller's replay-mode cache and let a
        # run that must not touch the network reach for it.
        self.cache = ResponseCache() if cache is None else cache
        self.name = f"{inner.name}+cache:{self.cache.mode}"
        self.hits = 0
        self.misses = 0

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion:
        if self.cache.mode == "off":
            return self.inner.complete(messages, tools, model_cfg)

        key = ResponseCache.key(model_cfg.model, self.prompt_sha, messages, tools)
        cached = self.cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached

        self.misses += 1
        if self.cache.mode == "replay":
            raise CacheMiss(
                f"cache miss in replay mode (key {key[:12]}…, {len(self.cache)} entries in "
                f"{self.cache.path}). Re-record with EARSHOT_CACHE_MODE=record, or run the offline "
                f"provider."
            )

        completion = self.inner.complete(messages, tools, model_cfg)
        self.cache.put(key, completion)
        return completion
