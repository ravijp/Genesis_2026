"""Extraction: conversation in, signals out. Stateless by construction.

Provider contract. Every provider sees one conversation and nothing else --
no customer history, no ledger, no ground truth. That statelessness is what makes the memory
ablation meaningful: all four arms share the identical extraction stream, so the only thing
that varies between them is what happens *after* extraction.

`OfflineLexiconExtractor` is the provider that ships first. It is deliberately the weaker
arm: it misses fragments whose phrasing its cues don't cover, and it fires on
decoys its dampeners don't catch. Its measured miss rate is published rather than hidden --
"it misses N% of planted signals and the memory delta holds anyway" is a stronger position
than a matcher that scores itself perfectly.

This module MUST NOT import corpus_lexicon or any ground-truth type. See tests/test_separation.py.
"""

from __future__ import annotations

import hashlib
from typing import Protocol

from .extract_lexicon import COMPILED_CUES, COMPILED_DAMPENERS
from .schema import Conversation, ExtractedSignal

CONFIDENCE_FLOOR = 0.20


class Extractor(Protocol):
    """Implemented by the offline provider now, and by Claude / the comparison model later."""

    name: str

    def extract(self, conversation: Conversation) -> list[ExtractedSignal]: ...


def _stable_uniform(*parts: str) -> float:
    """Deterministic pseudo-random in [0,1) from stable inputs.

    Used instead of `random` so that a conversation's simulated extractor imperfection is
    identical no matter what order conversations are processed in, and reproduces exactly
    across runs and machines.
    """
    digest = hashlib.sha256("|".join(parts).encode()).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


class OfflineLexiconExtractor:
    """Cue-and-dampener extractor. No model, no keys, no network."""

    name = "offline-lexicon"

    def __init__(self, miss_rate: float = 0.0, false_fire_rate: float = 0.0) -> None:
        # Both default to zero so the *natural* error profile (uncovered phrasings, dampeners
        # that don't catch every decoy) is what you get unless imperfection is dialled in
        # deliberately for robustness testing. Whatever is configured, the eval reports the
        # MEASURED extraction recall, never the configured knob.
        self.miss_rate = miss_rate
        self.false_fire_rate = false_fire_rate

    def extract(self, conversation: Conversation) -> list[ExtractedSignal]:
        found: list[ExtractedSignal] = []
        for turn in conversation.turns:
            if turn.speaker != "customer":
                continue
            for cue, pattern in COMPILED_CUES:
                match = pattern.search(turn.text)
                if not match:
                    continue

                confidence = cue.weight
                for damp_pattern, multiplier in COMPILED_DAMPENERS:
                    if damp_pattern.search(turn.text):
                        confidence *= multiplier
                if confidence < CONFIDENCE_FLOOR:
                    continue

                # Simulated recall failure, deterministic per (conversation, turn, cue).
                if self.miss_rate > 0 and _stable_uniform(
                    conversation.conversation_id, str(turn.index), cue.cue_id, "miss"
                ) < self.miss_rate:
                    continue

                found.append(
                    ExtractedSignal(
                        customer_id=conversation.customer_id,
                        conversation_id=conversation.conversation_id,
                        signal_type=cue.signal_type,
                        confidence=round(confidence, 4),
                        evidence_quote=turn.text,
                        turn_index=turn.index,
                        day=conversation.day,
                        channel=conversation.channel,
                        cue_id=cue.cue_id,
                    )
                )

        # Simulated spurious firing, applied ONCE PER CONVERSATION rather than per turn.
        # Per-turn was a modelling error: it multiplied by turn count, so a 12-turn call drew
        # ~1 false signal and the noise swamped the corpus (114 unplanted extractions across
        # 221 conversations on the first run). A real extractor's error rate is per document.
        customer_turns = [t for t in conversation.turns if t.speaker == "customer"]
        if (
            self.false_fire_rate > 0
            and customer_turns
            and _stable_uniform(conversation.conversation_id, "ff") < self.false_fire_rate
        ):
            pick = customer_turns[
                int(_stable_uniform(conversation.conversation_id, "where") * len(customer_turns))
            ]
            cue = COMPILED_CUES[
                int(_stable_uniform(conversation.conversation_id, "which") * len(COMPILED_CUES))
            ][0]
            found.append(
                ExtractedSignal(
                    customer_id=conversation.customer_id,
                    conversation_id=conversation.conversation_id,
                    signal_type=cue.signal_type,
                    confidence=round(CONFIDENCE_FLOOR + 0.15, 4),
                    evidence_quote=pick.text,
                    turn_index=pick.index,
                    day=conversation.day,
                    channel=conversation.channel,
                    cue_id=f"{cue.cue_id}:false-fire",
                )
            )

        # One signal per (conversation, type): keep the most confident. Repetition inside a
        # single conversation is not corroboration -- that distinction belongs to the ledger.
        best: dict[str, ExtractedSignal] = {}
        for sig in found:
            key = sig.signal_type.value
            if key not in best or sig.confidence > best[key].confidence:
                best[key] = sig
        return sorted(best.values(), key=lambda s: (s.signal_type.value, s.turn_index))


def extract_all(extractor: Extractor, conversations: tuple[Conversation, ...]) -> list[ExtractedSignal]:
    out: list[ExtractedSignal] = []
    for conv in sorted(conversations, key=lambda c: (c.day, c.conversation_id)):
        out.extend(extractor.extract(conv))
    return out
