"""Queue provisioning, and the cross-file coupling that broke it.

On 2026-09-02 both SQS -> Lambda event source mappings failed to create against the live account:

    InvalidParameterValueException
    Queue visibility timeout: 30 seconds is less than Function timeout: 60 seconds

`provision.py` set no `VisibilityTimeout`, so both queues sat at the SQS default of 30s, while the
function timeouts that constrain it lived in `deploy.py` with nothing connecting the two files.
`test_every_consumed_queue_tolerates_its_consumers_timeout` is the test that would have caught
that, and it keeps catching it if someone raises a Lambda timeout.

The rest cover the second half of the same bug: `_ensure_queue` was create-only, so on an account
where the queues already existed a corrected desired value would have been *silently inert* --
the tool printing SKIP while the defect survived. A stub records every call, so "did it write?" is
asserted rather than inferred. Nothing here touches AWS.
"""

from __future__ import annotations

import json
from typing import Any

import deploy
import provision
import pytest


class FakeSqs:
    """Records every call. `attributes` is the live queue state, as SQS returns it: all strings."""

    def __init__(self, attributes: dict[str, str] | None = None, exists: bool = True) -> None:
        self.attributes = dict(attributes or {})
        self.exists = exists
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get_queue_url(self, **kwargs: Any) -> dict[str, str]:
        self.calls.append(("get_queue_url", kwargs))
        if not self.exists:
            raise _absent()
        return {"QueueUrl": f"https://sqs.test/{kwargs['QueueName']}"}

    def get_queue_attributes(self, **kwargs: Any) -> dict[str, dict[str, str]]:
        self.calls.append(("get_queue_attributes", kwargs))
        asked = kwargs["AttributeNames"]
        return {"Attributes": {k: v for k, v in self.attributes.items() if k in asked}}

    def set_queue_attributes(self, **kwargs: Any) -> dict:
        self.calls.append(("set_queue_attributes", kwargs))
        self.attributes.update(kwargs["Attributes"])
        return {}

    def create_queue(self, **kwargs: Any) -> dict[str, str]:
        self.calls.append(("create_queue", kwargs))
        return {"QueueUrl": f"https://sqs.test/{kwargs['QueueName']}"}

    def names_called(self) -> list[str]:
        return [name for name, _ in self.calls]


def _absent() -> Exception:
    exc = Exception("nope")
    exc.response = {  # type: ignore[attr-defined]
        "Error": {
            "Code": "AWS.SimpleQueueService.NonExistentQueue",
            "Message": "The specified queue does not exist.",
        }
    }
    return exc


@pytest.fixture(autouse=True)
def _clear_rows():
    provision._rows.clear()
    yield
    provision._rows.clear()


def _plan_queues(stage: str) -> dict[str, dict[str, str]]:
    """What `_provision_queues` would configure, per queue name.

    Driven through the real function rather than restating its intent, so the assertions above are
    about the shipped plan and not about a second description of it.
    """
    planned: dict[str, dict[str, str]] = {}

    class PlanningSqs:
        def get_queue_url(self, **kw):
            name = kw["QueueName"]
            if name not in planned:
                raise _absent()
            return {"QueueUrl": f"https://sqs.test/{name}"}

        def get_queue_attributes(self, **kw):
            name = kw["QueueUrl"].rsplit("/", 1)[-1]
            asked = kw["AttributeNames"]
            attrs = dict(planned.get(name, {}))
            attrs["QueueArn"] = f"arn:aws:sqs:us-east-1:1:{name}"
            if asked == ["QueueArn"]:
                return {"Attributes": {"QueueArn": attrs["QueueArn"]}}
            return {"Attributes": {k: v for k, v in attrs.items() if k in asked}}

        def create_queue(self, **kw):
            planned[kw["QueueName"]] = dict(kw.get("Attributes") or {})
            return {"QueueUrl": f"https://sqs.test/{kw['QueueName']}"}

        def set_queue_attributes(self, **kw):
            planned[kw["QueueUrl"].rsplit("/", 1)[-1]].update(kw["Attributes"])
            return {}

    provision._provision_queues(PlanningSqs(), stage, False)
    return planned


def _results() -> list[str]:
    return [result for _, _, result in provision._rows]


# ---- the coupling ---------------------------------------------------------------------------


def test_every_consumed_queue_tolerates_its_consumers_timeout() -> None:
    """The property, not the number. AWS refuses a mapping whose queue visibility timeout is below
    the consuming function's timeout, so this must hold for every queue-backed function in
    `deploy.FUNCTIONS` -- including one added later, or one whose timeout is raised."""
    timeouts = provision.visibility_timeouts("dev")
    consumed = {k: v for k, v in deploy.FUNCTIONS.items() if v.get("queue")}
    assert consumed, "no queue-backed functions found; the derivation has nothing to check"
    for kind, spec in consumed.items():
        queue = f"earshot-dev-{spec['queue']}"
        assert queue in timeouts, f"{kind} consumes {queue} and no visibility timeout is derived"
        assert timeouts[queue] >= spec["timeout"], (
            f"{queue} visibility {timeouts[queue]}s is below {kind}'s timeout {spec['timeout']}s "
            "-- AWS will refuse the event source mapping"
        )


def test_the_derivation_names_every_stage_the_same_way() -> None:
    """A stage-mismatched key would raise `KeyError` inside `_provision_queues` rather than
    producing a wrong queue, but only for a stage nobody tested."""
    for stage in provision.STAGES:
        derived = provision.visibility_timeouts(stage)
        assert derived, f"stage {stage} derived no visibility timeouts"
        assert all(name.startswith(f"earshot-{stage}-") for name in derived)


def test_a_queue_with_no_consumer_gets_no_derived_timeout() -> None:
    """The DLQ has no entry in `deploy.FUNCTIONS`, so it must not appear here -- a derived value
    for it would be invented, not required."""
    assert "earshot-dev-investigations-dlq" not in provision.visibility_timeouts("dev")


# ---- dead-letter coverage -------------------------------------------------------------------


def test_every_consumed_queue_has_a_dead_letter_target() -> None:
    """The transcripts queue had none until 2026-09-03, while `aws/ingest.py` documented that a
    malformed transcript "eventually reaches the DLQ". On a FIFO queue the consequence is not a
    lost message but a stalled customer: the group is ordered, so a poison transcript blocks every
    later conversation for that customer for the full retention period."""
    planned = _plan_queues("dev")
    consumed = {f"earshot-dev-{spec['queue']}" for spec in deploy.FUNCTIONS.values() if spec.get("queue")}
    assert consumed, "no queue-backed functions found"
    for name in consumed:
        attrs = planned[name]
        assert "RedrivePolicy" in attrs, f"{name} is consumed by a Lambda and has no DLQ"
        policy = json.loads(attrs["RedrivePolicy"])
        assert policy["maxReceiveCount"] == provision.MAX_RECEIVE_COUNT
        assert policy["deadLetterTargetArn"].endswith("-dlq") or policy[
            "deadLetterTargetArn"
        ].endswith("-dlq.fifo")


def test_a_fifo_queues_dead_letter_target_is_itself_fifo() -> None:
    """AWS refuses a standard DLQ for a FIFO source. Getting this wrong fails at provision time,
    but only for whoever runs it against a fresh account."""
    planned = _plan_queues("dev")
    for name, attrs in planned.items():
        if attrs.get("FifoQueue") != "true":
            continue
        policy = attrs.get("RedrivePolicy")
        if not policy:
            continue  # a DLQ itself has no onward target
        target = json.loads(policy)["deadLetterTargetArn"]
        assert target.endswith(".fifo"), f"{name} is FIFO and points at a non-FIFO DLQ {target}"
        assert planned[target.rsplit(":", 1)[-1]]["FifoQueue"] == "true"


def test_a_dlq_is_not_itself_consumed_by_a_lambda() -> None:
    """A DLQ wired to the handler that rejected the message is an infinite loop with extra steps."""
    consumed = {f"earshot-dev-{spec['queue']}" for spec in deploy.FUNCTIONS.values() if spec.get("queue")}
    assert not any(name.endswith(("-dlq", "-dlq.fifo")) for name in consumed)


def test_teardown_removes_every_queue_provisioning_creates() -> None:
    """A DLQ left behind after teardown blocks the next `create_queue` on a name that AWS still
    holds for 60 seconds, and reads as a permissions problem."""
    import inspect

    source = inspect.getsource(provision._teardown)
    for name in _plan_queues("dev"):
        stem = name.replace("earshot-dev-", "").replace(".fifo", "")
        assert stem in source, f"{name} is created by provisioning and never torn down"


# ---- reconciliation -------------------------------------------------------------------------


def test_an_existing_queue_at_the_sqs_default_is_corrected() -> None:
    """The 2026-09-02 state exactly: the queue exists, at 30s, and must be repaired rather than
    skipped."""
    sqs = FakeSqs({"VisibilityTimeout": "30"})
    provision._ensure_queue(
        sqs, "earshot-dev-investigations", False, attributes={"VisibilityTimeout": "1800"}
    )
    assert "set_queue_attributes" in sqs.names_called()
    assert sqs.attributes["VisibilityTimeout"] == "1800"
    assert any("VisibilityTimeout 30 -> 1800" in r for r in _results()), _results()


def test_a_queue_already_correct_is_not_rewritten() -> None:
    """An idempotent tool must be readable as idempotent: a run that changes nothing must issue no
    write at all, not a harmless one."""
    sqs = FakeSqs({"VisibilityTimeout": "1800"})
    provision._ensure_queue(
        sqs, "earshot-dev-investigations", False, attributes={"VisibilityTimeout": "1800"}
    )
    assert "set_queue_attributes" not in sqs.names_called()
    assert _results() == ["already exists, attributes match"]


def test_an_int_on_our_side_does_not_look_like_drift() -> None:
    """SQS returns every attribute as a string. `"1800" != 1800` would report drift forever and
    write the same value on every run."""
    sqs = FakeSqs({"VisibilityTimeout": "1800"})
    provision._ensure_queue(
        sqs, "earshot-dev-investigations", False, attributes={"VisibilityTimeout": 1800}
    )
    assert "set_queue_attributes" not in sqs.names_called()


def test_a_reserialised_redrive_policy_does_not_look_like_drift() -> None:
    """AWS returns `RedrivePolicy` re-serialised, so key order differs from what we sent. A string
    compare would rewrite an identical policy on every run and print it as a change."""
    ours = json.dumps({"deadLetterTargetArn": "arn:aws:sqs:us-east-1:1:dlq", "maxReceiveCount": 3})
    theirs = json.dumps({"maxReceiveCount": 3, "deadLetterTargetArn": "arn:aws:sqs:us-east-1:1:dlq"})
    assert ours != theirs, "the two serialisations must differ, or this test proves nothing"
    sqs = FakeSqs({"RedrivePolicy": theirs})
    provision._ensure_queue(
        sqs, "earshot-dev-investigations", False, attributes={"RedrivePolicy": ours}
    )
    assert "set_queue_attributes" not in sqs.names_called()


def test_the_immutable_fifo_flag_is_never_reconciled() -> None:
    """`FifoQueue` cannot be set after creation. Reconciling it would report a diff on every run
    that no run can close, and the write would be rejected."""
    sqs = FakeSqs({"VisibilityTimeout": "360", "ContentBasedDeduplication": "false"})
    provision._ensure_queue(
        sqs, "earshot-dev-transcripts.fifo", False,
        attributes={
            "FifoQueue": "true",
            "ContentBasedDeduplication": "false",
            "VisibilityTimeout": "360",
        },
    )
    asked = [kw for name, kw in sqs.calls if name == "get_queue_attributes"]
    assert asked and "FifoQueue" not in asked[0]["AttributeNames"]
    assert "set_queue_attributes" not in sqs.names_called()


def test_a_dry_run_reports_the_change_and_writes_nothing() -> None:
    sqs = FakeSqs({"VisibilityTimeout": "30"})
    provision._ensure_queue(
        sqs, "earshot-dev-investigations", True, attributes={"VisibilityTimeout": "1800"}
    )
    assert "set_queue_attributes" not in sqs.names_called()
    assert "create_queue" not in sqs.names_called()
    assert sqs.attributes["VisibilityTimeout"] == "30"
    assert any(r.startswith("DRY-RUN -- would set") for r in _results()), _results()


def test_a_dry_run_against_a_missing_queue_creates_nothing() -> None:
    sqs = FakeSqs(exists=False)
    url = provision._ensure_queue(
        sqs, "earshot-dev-investigations", True, attributes={"VisibilityTimeout": "1800"}
    )
    assert url is None
    assert "create_queue" not in sqs.names_called()


def test_a_missing_queue_is_created_with_the_visibility_timeout_set() -> None:
    """Creating it with the attribute is what makes a fresh account correct on the first run,
    rather than correct only after a second reconciling run."""
    sqs = FakeSqs(exists=False)
    provision._ensure_queue(
        sqs, "earshot-dev-investigations", False, attributes={"VisibilityTimeout": "1800"}
    )
    created = [kw for name, kw in sqs.calls if name == "create_queue"]
    assert created and created[0]["Attributes"]["VisibilityTimeout"] == "1800"


# ---- error reporting ------------------------------------------------------------------------


def test_a_failure_row_carries_the_aws_message_not_just_the_code() -> None:
    """`InvalidParameterValueException` on its own is what cost a diagnostic round-trip against
    the live account. The message said exactly what was wrong."""
    exc = Exception("boom")
    exc.response = {  # type: ignore[attr-defined]
        "Error": {
            "Code": "InvalidParameterValueException",
            "Message": "Queue visibility timeout: 30 seconds is less than Function timeout: 60 seconds",
        }
    }
    detail = provision._error_detail(exc)
    assert detail.startswith("InvalidParameterValueException: ")
    assert "30 seconds is less than Function timeout: 60 seconds" in detail


def test_error_detail_is_bounded_so_a_row_stays_readable() -> None:
    exc = Exception("boom")
    exc.response = {"Error": {"Code": "ThrottlingException", "Message": "x" * 500}}  # type: ignore[attr-defined]
    assert len(provision._error_detail(exc)) < 200


def test_error_code_still_answers_the_control_flow_question() -> None:
    """`_queue_url` compares `_error_code` against `_QUEUE_ABSENT`. Adding the message must not
    have changed that contract, or a missing queue starts raising instead of returning None."""
    assert provision._error_code(_absent()) in provision._QUEUE_ABSENT
    sqs = FakeSqs(exists=False)
    assert provision._queue_url(sqs, "earshot-dev-investigations") is None


def test_an_exception_with_no_botocore_shape_still_reports_something() -> None:
    detail = provision._error_detail(RuntimeError("credentials not found"))
    assert "credentials not found" in detail or "RuntimeError" in detail
