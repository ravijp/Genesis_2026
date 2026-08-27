"""The ingest handler: one conversation in, a re-scored ledger and maybe an investigation out.

    SQS record -> Conversation -> extract() -> LedgerStore.append() -> re-score -> threshold

**This module does not score anything.** It loads, delegates to an unchanged `SignalLedger`, and
persists. `memory.py` is the only scorer in this codebase, online or offline, and the one thing
this architecture forbids is a second one appearing on the deployed path where nobody compares it
to the local one. Every number below comes back from `SignalLedger.best()`.

Four properties, each bought with a reason:

1. **Redelivery is a no-op, not an error.** `LedgerStore.append()` writes conditional on
   `attribute_not_exists(sk)`, so SQS's at-least-once delivery cannot double-count a signal. The
   duplicate count is returned rather than swallowed -- it is the A7 duplicate metric.
2. **One bad record fails alone.** The handler returns `batchItemFailures`, so a malformed
   transcript retries and eventually reaches the DLQ while its healthy neighbours commit. Raising
   instead would redeliver the whole batch and re-run every extraction in it.
3. **Keyless by default.** The extractor is the offline lexicon unless `EARSHOT_EXTRACTOR=bedrock`
   says otherwise, chosen by an explicit `if`/`elif` -- `aws/__init__.py` forbids dynamic imports
   on the guarded surface, so there is no registry lookup here and there must never be one.
4. **Nothing here can see the answer key.** It reads a transcript off a queue; there is no corpus
   import and no truth object anywhere in the module. `tests/test_separation.py` covers this file
   by glob.

**The deployed threshold is a fixed cut, and it is NOT the local one.** `cli.py:_queue` derives its
threshold from a review budget over a whole population -- the 10% of customers a review team can
work today. A streaming handler has no population snapshot to rank against, so the online cut is a
constant (`EARSHOT_THRESHOLD`, default `DEFAULT_THRESHOLD`). The two are different quantities and
will not agree: a customer can cross online and rank out of the local queue, or the reverse. Say so
rather than implying one threshold governs both.

**A crossing that stays crossed re-investigates.** Every later conversation that leaves the
customer above the cut enqueues again, because re-reading old evidence in light of new is the
claim the entry rests on. It is bounded by conversation volume, not by anything clever, and it
costs one investigation each time. It does not multiply *cases*: `case_record.make_case_id` keys on
the first crossing day, so re-investigation overwrites one case rather than growing the queue.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from typing import Any

from ..config import ScoringConfig
from ..extract import Extractor, OfflineLexiconExtractor
from ..schema import Channel, Conversation, Turn
from .stores import REGION, LedgerStore, table_name

# The online cut. Deliberately a constant rather than a budget -- see the module docstring.
DEFAULT_THRESHOLD = 0.60

DEFAULT_STAGE = "dev"


class IngestError(ValueError):
    """A record that cannot be turned into a `Conversation`. Fails that record alone."""


def parse_conversation(payload: Any) -> Conversation:
    """Strict parse of one transcript message. Rejects rather than defaults.

    A missing `day` defaulted to 0 would place every signal at the corpus epoch and decay it to
    nothing, which reads on a dashboard as "the ledger does not work" rather than as bad input. So
    every field a score depends on is required, and an unknown channel is an error rather than a
    fallback -- `Channel` is a closed set, and adding to it is a change to the model, not something
    a queue producer gets to do in a payload.
    """
    if not isinstance(payload, dict):
        raise IngestError(f"transcript must be a JSON object, got {type(payload).__name__}")
    missing = {"conversation_id", "customer_id", "channel", "day", "turns"} - set(payload)
    if missing:
        raise IngestError(f"transcript is missing {sorted(missing)}")
    try:
        channel = Channel(payload["channel"])
    except ValueError as exc:
        known = ", ".join(c.value for c in Channel)
        raise IngestError(f"unknown channel {payload['channel']!r}; known: {known}") from exc
    day = payload["day"]
    if isinstance(day, bool) or not isinstance(day, int):
        raise IngestError(f"day must be an integer, got {day!r}")
    raw_turns = payload["turns"]
    if not isinstance(raw_turns, list) or not raw_turns:
        raise IngestError("turns must be a non-empty list")
    turns = []
    for i, turn in enumerate(raw_turns):
        if not isinstance(turn, dict) or "speaker" not in turn or "text" not in turn:
            raise IngestError(f"turn {i} must be an object with 'speaker' and 'text'")
        # The producer's index wins when it gives one: evidence citations resolve by
        # (conversation_id, turn_index), so re-indexing a turn breaks every quote citing it.
        turns.append(
            Turn(
                index=int(turn.get("index", i)),
                speaker=str(turn["speaker"]),
                text=str(turn["text"]),
            )
        )
    return Conversation(
        conversation_id=str(payload["conversation_id"]),
        customer_id=str(payload["customer_id"]),
        channel=channel,
        day=day,
        turns=tuple(turns),
    )


@dataclass(frozen=True)
class IngestResult:
    """What one conversation did to one customer's standing ledger.

    `duplicates` is not an error count. It is how often SQS delivered a signal already on the
    ledger -- the A7 metric, which the conditional write is what makes harmless.
    """

    conversation_id: str
    customer_id: str
    extracted: int
    written: int
    duplicates: int
    signal_type: str | None
    score: float
    threshold: float
    crossed: bool
    as_of_day: int
    enqueued: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "customer_id": self.customer_id,
            "extracted": self.extracted,
            "written": self.written,
            "duplicates": self.duplicates,
            "signal_type": self.signal_type,
            "score": round(self.score, 6),
            "threshold": self.threshold,
            "crossed": self.crossed,
            "as_of_day": self.as_of_day,
            "enqueued": self.enqueued,
        }


class QueuePublisher:
    """`send_message` on the investigations queue, with the boto3 client built on first use.

    Lazy for the same reason `stores._resolve_table` is: `earshot[aws]` is optional, and a test
    injects a fake `sqs` so the whole ingest path runs with boto3 absent from the environment.
    """

    def __init__(
        self, queue_url: str, *, region_name: str = REGION, sqs: Any | None = None
    ) -> None:
        self.queue_url = queue_url
        self._region = region_name
        self._sqs = sqs

    @property
    def client(self) -> Any:
        if self._sqs is None:
            import boto3  # noqa: PLC0415 -- deliberately lazy; see the class docstring

            self._sqs = boto3.client("sqs", region_name=self._region)
        return self._sqs

    def publish(self, body: dict[str, Any]) -> None:
        self.client.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(body))


class Ingestor:
    """The ingest path as an object, so every collaborator is injectable and `handler` is a thin
    wrapper rather than the only way to run this code."""

    def __init__(
        self,
        extractor: Extractor,
        ledger_store: LedgerStore,
        *,
        threshold: float = DEFAULT_THRESHOLD,
        publisher: QueuePublisher | None = None,
        scoring: ScoringConfig | None = None,
    ) -> None:
        self.extractor = extractor
        self.store = ledger_store
        self.threshold = threshold
        self.publisher = publisher
        self.scoring = scoring or ScoringConfig()

    def ingest(self, conversation: Conversation) -> IngestResult:
        signals = self.extractor.extract(conversation)
        written, duplicates = self.store.append_all(signals)

        # Re-scored from what DynamoDB holds, not from the signals just extracted. That is the
        # whole point of the ledger: accumulation is over everything ever heard, and this handler
        # only ever saw one conversation.
        ledger = self.store.load_ledger(conversation.customer_id, self.scoring)
        known = ledger.signals(conversation.customer_id)
        # A conversation can arrive out of order, so "today" is the latest day on the ledger, not
        # this message's day. Scoring as of an older day would decay evidence that has not aged.
        as_of_day = max([conversation.day] + [s.day for s in known])
        breakdown = ledger.best(conversation.customer_id, as_of_day)
        crossed = bool(breakdown.entries) and breakdown.score >= self.threshold

        result = IngestResult(
            conversation_id=conversation.conversation_id,
            customer_id=conversation.customer_id,
            extracted=len(signals),
            written=written,
            duplicates=duplicates,
            signal_type=breakdown.signal_type.value if breakdown.entries else None,
            score=breakdown.score,
            threshold=self.threshold,
            crossed=crossed,
            as_of_day=as_of_day,
        )
        if crossed and self.publisher is not None:
            # The crossing's coordinates only. The investigate handler reloads the ledger from
            # DynamoDB itself, so putting the evidence chain on the wire would ship a second,
            # staler copy of the same truth.
            self.publisher.publish(
                {
                    "customer_id": conversation.customer_id,
                    "signal_type": breakdown.signal_type.value,
                    "score": round(breakdown.score, 6),
                    "threshold": self.threshold,
                    "as_of_day": as_of_day,
                    "triggered_by_conversation": conversation.conversation_id,
                }
            )
            result = replace(result, enqueued=True)
        return result


# ---- Lambda entrypoint -------------------------------------------------------------------------


def _extractor_from_env() -> Extractor:
    """Explicit `if`/`elif`, never a registry: `aws/__init__.py` forbids dynamic imports on the
    guarded surface, and a lookup table is exactly how a corpus-side reader would one day come to
    be selected by a string in an environment variable."""
    name = os.environ.get("EARSHOT_EXTRACTOR", "offline")
    if name == "offline":
        return OfflineLexiconExtractor()
    if name == "bedrock":
        from ..extract_model import ModelExtractor  # noqa: PLC0415 -- keeps cold start keyless
        from ..llm.bedrock import BedrockProvider  # noqa: PLC0415

        return ModelExtractor(BedrockProvider())
    raise IngestError(f"unknown EARSHOT_EXTRACTOR {name!r}; known: offline, bedrock")


def build_ingestor() -> Ingestor:
    """Assembled from the environment. Called once per container, not once per record."""
    stage = os.environ.get("EARSHOT_STAGE", DEFAULT_STAGE)
    queue_url = os.environ.get("EARSHOT_INVESTIGATIONS_QUEUE_URL")
    return Ingestor(
        _extractor_from_env(),
        LedgerStore(table_name(stage, "ledger")),
        threshold=float(os.environ.get("EARSHOT_THRESHOLD", DEFAULT_THRESHOLD)),
        publisher=QueuePublisher(queue_url) if queue_url else None,
    )


_INGESTOR: Ingestor | None = None


def handler(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
    """SQS batch entrypoint. Returns `batchItemFailures` so a poison record fails alone.

    Never raises. A raised exception fails the whole batch, which redelivers every healthy
    conversation in it and re-runs their extractions -- with a model reader, real money spent to
    punish one malformed neighbour.
    """
    global _INGESTOR
    if _INGESTOR is None:
        _INGESTOR = build_ingestor()

    failures: list[dict[str, str]] = []
    for record in event.get("Records", []):
        message_id = record.get("messageId", "")
        try:
            conversation = parse_conversation(json.loads(record["body"]))
            result = _INGESTOR.ingest(conversation)
        except Exception as exc:  # noqa: BLE001 -- the contract is "this record failed", not why
            # Structured and one line: a CloudWatch Insights query on `event=ingest.failed` is the
            # only practical way to find a poison message in a busy log group.
            print(
                json.dumps(
                    {"event": "ingest.failed", "messageId": message_id, "error": str(exc)}
                )
            )
            failures.append({"itemIdentifier": message_id})
            continue
        print(json.dumps({"event": "ingest.ok", **result.to_dict()}))
    return {"batchItemFailures": failures}
