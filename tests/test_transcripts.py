"""The transcript wire format and the S3 evidence archive, against a hand-rolled fake S3.

No boto3, no botocore, no network, no credentials. `FakeS3` mimics the four calls this module
makes -- `put_object` (including the `IfNoneMatch` precondition), `list_objects_v2` with real
truncation, and `get_object` -- so `transcripts.py` runs unmodified against it.

The archive exists because the ledger stores signals, not conversations, and the investigator's
citations resolve against whole transcripts. So the tests that matter are: a round trip is lossless
(a lost turn index breaks every citation that names it), a redelivery cannot overwrite, and a
customer with more than one page of history is read in full rather than truncated at page one.
"""

from __future__ import annotations

import io
import json

import pytest

from earshot.aws.transcripts import (
    TranscriptArchive,
    TranscriptError,
    parse_conversation,
    to_payload,
    transcript_key,
)
from earshot.schema import Channel, Conversation, Turn


class _FakePreconditionFailed(Exception):
    """Shaped like botocore's ClientError -- `.response["Error"]["Code"]` -- which is what
    `transcripts._is_precondition_failure` duck-types against."""

    def __init__(self) -> None:
        super().__init__("PreconditionFailed")
        self.response = {"Error": {"Code": "PreconditionFailed"}}


class FakeS3:
    """Enough of the S3 client for `TranscriptArchive`. `page_size` splits a listing so the
    pagination loop has something real to walk."""

    def __init__(self, page_size: int | None = None) -> None:
        self.objects: dict[str, bytes] = {}
        self.page_size = page_size
        self.put_calls = 0

    def put_object(
        self,
        Bucket: str,  # noqa: N803 -- boto3 casing
        Key: str,  # noqa: N803
        Body: bytes,  # noqa: N803
        ContentType: str = "",  # noqa: N803
        IfNoneMatch: str | None = None,  # noqa: N803
    ) -> dict:
        self.put_calls += 1
        if IfNoneMatch == "*" and Key in self.objects:
            raise _FakePreconditionFailed()
        self.objects[Key] = Body
        return {"ETag": '"x"'}

    def list_objects_v2(
        self,
        Bucket: str,  # noqa: N803
        Prefix: str = "",  # noqa: N803
        ContinuationToken: str | None = None,  # noqa: N803
    ) -> dict:
        keys = sorted(k for k in self.objects if k.startswith(Prefix))
        start = int(ContinuationToken) if ContinuationToken else 0
        page = keys[start:] if self.page_size is None else keys[start : start + self.page_size]
        end = start + len(page)
        out: dict = {"Contents": [{"Key": k} for k in page]}
        if end < len(keys):
            out["IsTruncated"] = True
            out["NextContinuationToken"] = str(end)
        return out

    def get_object(self, Bucket: str, Key: str) -> dict:  # noqa: N803
        return {"Body": io.BytesIO(self.objects[Key])}


def convo(conversation_id: str, day: int, customer_id: str = "CUST-1") -> Conversation:
    return Conversation(
        conversation_id=conversation_id,
        customer_id=customer_id,
        channel=Channel.CALL,
        day=day,
        turns=(
            Turn(index=0, speaker="agent", text="Thanks for calling."),
            Turn(index=1, speaker="customer", text="Money is tight since my hours were cut."),
        ),
    )


# ---- the wire format ------------------------------------------------------------------------


def test_a_transcript_round_trips_through_the_payload_form() -> None:
    """`to_payload` then `parse_conversation` must give back the same conversation. A lost turn
    index breaks every citation that resolves by `(conversation_id, turn_index)`."""
    original = convo("C1", day=12)
    assert parse_conversation(to_payload(original)) == original


def test_the_archive_round_trips_a_conversation_unchanged() -> None:
    s3 = FakeS3()
    archive = TranscriptArchive("dev", s3=s3)
    original = convo("C1", day=12)
    assert archive.put(original) is True
    assert archive.load("CUST-1") == (original,)


def test_the_key_sorts_by_day_within_a_customer() -> None:
    """A prefix listing returns keys byte-wise, so the day has to be zero-padded for a customer's
    history to come back in the order an evidence chain is read in."""
    keys = [transcript_key("dev", convo(f"C{d}", day=d)) for d in (5, 40, 300)]
    assert keys == sorted(keys)
    assert all(k.startswith("evidence/dev/CUST-1/") for k in keys)


def test_a_payload_that_is_not_a_transcript_is_rejected() -> None:
    with pytest.raises(TranscriptError, match="missing"):
        parse_conversation({"conversation_id": "C1"})
    with pytest.raises(TranscriptError, match="JSON object"):
        parse_conversation([1, 2, 3])


# ---- write-once, degraded to a conditional put ------------------------------------------------


def test_a_second_write_of_the_same_key_is_refused_not_silently_applied() -> None:
    """Object Lock is unavailable on this bucket (created without it, unchangeable), so write-once
    degrades to `IfNoneMatch="*"`. The first write wins; a redelivery is told it lost."""
    s3 = FakeS3()
    archive = TranscriptArchive("dev", s3=s3)
    original = convo("C1", day=12)

    assert archive.put(original) is True
    assert archive.put(original) is False, "a redelivery overwrote the archived transcript"
    assert archive.refused_overwrites == 1
    assert archive.load("CUST-1") == (original,)


def test_a_conditional_put_is_actually_requested() -> None:
    """The guarantee is the precondition, not our own read-then-write. If the flag stops being
    sent, the fake's refusal above becomes theatre and this is the test that notices."""
    calls: list[dict] = []

    class Recording(FakeS3):
        def put_object(self, **kwargs):  # type: ignore[override]
            calls.append(kwargs)
            return super().put_object(**kwargs)

    TranscriptArchive("dev", s3=Recording()).put(convo("C1", day=1))
    assert calls[0]["IfNoneMatch"] == "*"


def test_an_error_that_is_not_a_precondition_failure_still_raises() -> None:
    """Swallowing every S3 error would turn "the bucket is gone" into "already archived"."""

    class Broken(FakeS3):
        def put_object(self, **kwargs):  # type: ignore[override]
            exc = Exception("AccessDenied")
            exc.response = {"Error": {"Code": "AccessDenied"}}  # type: ignore[attr-defined]
            raise exc

    with pytest.raises(Exception, match="AccessDenied"):
        TranscriptArchive("dev", s3=Broken()).put(convo("C1", day=1))


# ---- reading a customer's history --------------------------------------------------------------


def test_a_customer_with_more_than_one_page_of_history_is_read_in_full() -> None:
    """`list_objects_v2` truncates at 1,000 keys. A handler that stopped at page one would
    investigate a prefix of the customer's history and look like the model missing evidence."""
    s3 = FakeS3(page_size=2)
    archive = TranscriptArchive("dev", s3=s3)
    for day in range(7):
        archive.put(convo(f"C{day}", day=day))

    loaded = archive.load("CUST-1")
    assert len(loaded) == 7
    assert [c.day for c in loaded] == list(range(7))


def test_one_customers_prefix_never_returns_anothers() -> None:
    s3 = FakeS3()
    archive = TranscriptArchive("dev", s3=s3)
    archive.put(convo("C1", day=1, customer_id="CUST-1"))
    archive.put(convo("C2", day=1, customer_id="CUST-2"))

    assert [c.customer_id for c in archive.load("CUST-1")] == ["CUST-1"]


def test_a_customer_with_nothing_archived_reads_empty_rather_than_raising() -> None:
    assert TranscriptArchive("dev", s3=FakeS3()).load("CUST-404") == ()


def test_stages_do_not_read_each_others_transcripts() -> None:
    s3 = FakeS3()
    TranscriptArchive("dev", s3=s3).put(convo("C1", day=1))
    assert TranscriptArchive("demo", s3=s3).load("CUST-1") == ()


def test_what_is_stored_is_json_a_human_can_read() -> None:
    """The evidence archive is the artifact a regulator would be handed. An opaque blob there
    would be worth nothing, whatever the retention policy says."""
    s3 = FakeS3()
    TranscriptArchive("dev", s3=s3).put(convo("C1", day=12))
    stored = json.loads(next(iter(s3.objects.values())).decode("utf-8"))
    assert stored["conversation_id"] == "C1"
    assert stored["turns"][1]["text"].startswith("Money is tight")
