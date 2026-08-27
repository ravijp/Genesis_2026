"""The transcript wire format, and the S3 archive that keeps transcripts after ingest.

Two things live here because they are one concern: the JSON shape a transcript arrives in, and
where that JSON is kept afterwards. `ingest.py` parses and writes; `investigate.py` reads back.
Neither owns the format, so neither can quietly change it for the other.

**Why an archive at all.** The ledger stores signals, not conversations -- one quote and its
coordinates, never the surrounding turns. The investigator's `get_conversation` tool needs the
whole transcript, and `unresolved_evidence()` rejects any decision whose citations do not resolve
against one. Without this archive the deployed investigator would reject every decision it made
and burn its retry budget doing it. Locally the corpus object supplies transcripts; in deployment
this does.

**Write-once, honestly degraded.** `docs/architecture/infrastructure.md` A.1 line 13 specifies S3
Object Lock in compliance mode on the evidence archive -- that is how never-discard becomes
auditable rather than asserted. Object Lock must be enabled **at bucket creation** and the one
bucket this account can use (`s3://agentic-trio`) was created without it, verified, unchangeable
without an AWS Support case. So the guarantee here degrades to a **conditional put**
(`IfNoneMatch="*"`): the first write of a key wins and every redelivery is refused by S3 itself.
That stops overwrite-by-accident and overwrite-by-redelivery. It does **not** stop a deliberate
delete by a principal holding `s3:DeleteObject`, which is what Object Lock would have stopped.
Say the smaller thing on stage.

**The ledger's own A6 guarantee is unaffected and must not be merged with this one.** That is
DynamoDB: no TTL, no delete permission, and `LedgerStore` has no delete method at all.
"""

from __future__ import annotations

import json
from typing import Any

from ..schema import Channel, Conversation, Turn

REGION = "us-east-1"

# The one bucket this account can write to. `earshot-evidence` and `earshot-artifacts` from A.1
# need `s3:CreateBucket`, which is denied, so both live as prefixes inside this one (D-024).
DEFAULT_BUCKET = "agentic-trio"
EVIDENCE_PREFIX = "evidence"

# Zero-padded so a prefix listing returns a customer's conversations in day order, which is the
# order an evidence chain is read in. Matches `stores._DAY_WIDTH` by intent, not by import: these
# are two different key spaces and coupling them would be a false economy.
_DAY_WIDTH = 6


class TranscriptError(ValueError):
    """A payload that cannot be turned into a `Conversation`. Fails that record alone."""


def parse_conversation(payload: Any) -> Conversation:
    """Strict parse of one transcript message. Rejects rather than defaults.

    A missing `day` defaulted to 0 would place every signal at the corpus epoch and decay it to
    nothing, which reads on a dashboard as "the ledger does not work" rather than as bad input. So
    every field a score depends on is required, and an unknown channel is an error rather than a
    fallback -- `Channel` is a closed set, and adding to it is a change to the model, not something
    a queue producer gets to do in a payload.
    """
    if not isinstance(payload, dict):
        raise TranscriptError(f"transcript must be a JSON object, got {type(payload).__name__}")
    missing = {"conversation_id", "customer_id", "channel", "day", "turns"} - set(payload)
    if missing:
        raise TranscriptError(f"transcript is missing {sorted(missing)}")
    try:
        channel = Channel(payload["channel"])
    except ValueError as exc:
        known = ", ".join(c.value for c in Channel)
        raise TranscriptError(f"unknown channel {payload['channel']!r}; known: {known}") from exc
    day = payload["day"]
    if isinstance(day, bool) or not isinstance(day, int):
        raise TranscriptError(f"day must be an integer, got {day!r}")
    raw_turns = payload["turns"]
    if not isinstance(raw_turns, list) or not raw_turns:
        raise TranscriptError("turns must be a non-empty list")
    turns = []
    for i, turn in enumerate(raw_turns):
        if not isinstance(turn, dict) or "speaker" not in turn or "text" not in turn:
            raise TranscriptError(f"turn {i} must be an object with 'speaker' and 'text'")
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


def to_payload(conversation: Conversation) -> dict[str, Any]:
    """The inverse of `parse_conversation`, so a round trip through S3 is lossless. A test asserts
    that both directions agree; an archive that cannot reproduce the turn indices it was given
    would break every citation that resolves against it."""
    return {
        "conversation_id": conversation.conversation_id,
        "customer_id": conversation.customer_id,
        "channel": conversation.channel.value,
        "day": conversation.day,
        "turns": [
            {"index": t.index, "speaker": t.speaker, "text": t.text} for t in conversation.turns
        ],
    }


def transcript_key(stage: str, conversation: Conversation) -> str:
    """`evidence/<stage>/<customer_id>/<padded day>-<conversation_id>.json`.

    Customer-first so one `list_objects_v2` prefix call returns exactly the conversations an
    investigation needs and nothing else -- the investigator reads one customer at a time, always.
    """
    return (
        f"{EVIDENCE_PREFIX}/{stage}/{conversation.customer_id}/"
        f"{conversation.day:0{_DAY_WIDTH}d}-{conversation.conversation_id}.json"
    )


class TranscriptArchive:
    """S3 persistence for raw transcripts. The boto3 client is built on first use, and a fake one
    can be injected -- so every test in this repo runs the real code path with boto3 absent."""

    def __init__(
        self,
        stage: str,
        *,
        bucket: str = DEFAULT_BUCKET,
        region_name: str = REGION,
        s3: Any | None = None,
    ) -> None:
        self.stage = stage
        self.bucket = bucket
        self._region = region_name
        self._s3 = s3
        self.refused_overwrites = 0

    @property
    def client(self) -> Any:
        if self._s3 is None:
            import boto3  # noqa: PLC0415 -- deliberately lazy; `earshot[aws]` is optional

            self._s3 = boto3.client("s3", region_name=self._region)
        return self._s3

    def put(self, conversation: Conversation) -> bool:
        """Archive one transcript. Returns `False` -- a no-op, not an error -- if the key already
        exists, which is what SQS redelivery looks like from here.

        `IfNoneMatch="*"` makes S3 itself refuse the second write, so two concurrent ingests of
        the same conversation cannot race: one wins, the other is told it lost. Doing this with a
        read-then-write instead would have a window between the two.
        """
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=transcript_key(self.stage, conversation),
                Body=json.dumps(to_payload(conversation)).encode("utf-8"),
                ContentType="application/json",
                IfNoneMatch="*",
            )
        except Exception as exc:  # noqa: BLE001 -- duck-typed on the wire code, see below
            if _is_precondition_failure(exc):
                self.refused_overwrites += 1
                return False
            raise
        return True

    def load(self, customer_id: str) -> tuple[Conversation, ...]:
        """Every archived conversation for one customer, oldest first.

        Paginated by hand rather than with a paginator: `list_objects_v2` truncates at 1,000 keys
        and a customer with more conversations than that would silently investigate a prefix of
        their own history -- the kind of bug that only appears in production and looks like the
        model missing evidence.
        """
        prefix = f"{EVIDENCE_PREFIX}/{self.stage}/{customer_id}/"
        keys: list[str] = []
        token: str | None = None
        while True:
            kwargs: dict[str, Any] = {"Bucket": self.bucket, "Prefix": prefix}
            if token:
                kwargs["ContinuationToken"] = token
            page = self.client.list_objects_v2(**kwargs)
            keys.extend(obj["Key"] for obj in page.get("Contents", []))
            if not page.get("IsTruncated"):
                break
            token = page.get("NextContinuationToken")
            if not token:
                break

        conversations = []
        for key in sorted(keys):
            body = self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()
            conversations.append(parse_conversation(json.loads(body)))
        return tuple(sorted(conversations, key=lambda c: (c.day, c.conversation_id)))


def _is_precondition_failure(exc: Exception) -> bool:
    """Duck-typed against botocore's error shape, the same way `stores._is_conditional_check_failure`
    is, so this module never imports botocore. S3 reports a failed `IfNoneMatch` as
    `PreconditionFailed` (HTTP 412); some paths surface it as `ConditionalRequestConflict` (409)
    when two writers race, which is the same answer to the same question: someone else got there
    first."""
    response = getattr(exc, "response", None)
    code = ""
    if isinstance(response, dict):
        code = str(response.get("Error", {}).get("Code", ""))
    return code in {"PreconditionFailed", "ConditionalRequestConflict"} or (
        type(exc).__name__ in {"PreconditionFailed", "ConditionalRequestConflict"}
    )
