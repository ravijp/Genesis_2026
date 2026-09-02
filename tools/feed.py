"""Push one tenant's book through the DEPLOYED pipeline, and check the result against the local
answer.

    uv run --with boto3 python tools/feed.py --stage dev                  # predict + dry-run
    uv run --with boto3 python tools/feed.py --stage dev --no-dry-run     # send, then observe
    uv run --with boto3 python tools/feed.py --stage dev --observe-only   # just read the state

**Why this exists.** Until today the deployed path was permissioned but unconsumed: three Lambdas,
three queues, three empty tables, and nothing had ever travelled between them. `earshot run` and
`earshot sweep` prove the *idea* locally; they prove nothing about the infrastructure. Feasibility
and production readiness is 25 of the 100 rubric points, and a diagram scores none of it.

**It predicts before it sends, and exits non-zero if the deployment disagrees.** The local ledger
is the answer key for the deployed one: `memory.py` is the only scorer in this codebase, and
`aws/ingest.py` delegates to it rather than reimplementing it. So the number of ledger writes, the
number of crossings, and the identity and score of every crossing customer are all knowable before
a single message is sent. Asserting them afterwards is what turns "it ran" into "it ran and agreed
with the local pipeline to six decimal places". A tool that printed a green summary either way
would be the same mistake as the `timeout ... | tail` wrapper that turned a truncated run into a
clean one (`docs/ops/handover.md`).

**This file is ON the separation-guarded surface, and it stays there.** `tests/test_separation.py`
globs `tools/` as well as the package, and `_TOOLS_EVALUATION_SIDE` is capped at three entries that
are all taken -- so this module is scanned like any other. It passes for the same structural reason
`stream.py` does: `predict()` gets its conversations from `cli.stream_inputs()`, which is the
sanctioned seam. Nothing here imports `corpus` or names a ground-truth type, so the guard's four
nets have nothing to catch. **Do not "fix" this by asking for an exemption** -- the exemption list
is for harnesses that score against the answer key, and this one does not: it compares a deployed
ledger to a local ledger, and neither side knows the truth.

What crosses to AWS is narrower still, and `wire_payload()` enforces that by construction: the five
fields `aws/transcripts.parse_conversation` requires, built from named attributes, key set
asserted. A payload cannot pick up `stratum`, `outcome` or `latent_risk` from someone spreading a
dataclass into it.

**Ordering is the point, not a detail.** The claim is accumulation: a sub-threshold signal in
conversation 1 still counts in conversation 3. That only reproduces if one customer's
conversations arrive in day order, which is why the queue is FIFO and `MessageGroupId` is the
customer id. Each customer's conversations go in one batch, in ascending day order; different
customers are independent groups and may interleave freely, which is the parallelism.

`MessageDeduplicationId` is the conversation id, because content-based deduplication is off on
that queue (`tools/provision.py`). A second feed of the same book is therefore a no-op inside
SQS's 5-minute dedup window, and a no-op on the ledger after it (`LedgerStore.append` writes
conditional on `attribute_not_exists(sk)`) -- so re-running this tool is safe, and the duplicate
count it reports is the A7 metric rather than an error.

**What `verify()` checks is re-feed-stable, and that is deliberate.** Ledger count, case count, DLQ
depth and `GET /cases` all land on the same values whether this is the first feed or the fifth.
`Crossings` and `Investigations` do NOT: `predict()` models a ledger that starts empty, but on a
re-feed the ledger is already complete, so every one of a crossing customer's conversations sees a
crossing state rather than only the one that first reached the threshold. Measured on 2026-09-02:
the first feed produced 1 crossing, the second produced 4 -- CUST-0006 has four conversations, and
the second time round all four crossed. That is `aws/ingest.py`'s documented behaviour ("a crossing
that stays crossed re-investigates") and it does not multiply cases, because
`case_record.make_case_id` keys on the first crossing day. Do not add a crossings-equal-prediction
assertion here: it would be correct on a clean stage and wrong on every rerun.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from earshot.aws.ingest import DEFAULT_THRESHOLD
from earshot.aws.stores import REGION, STAGES, table_name
from earshot.cli import stream_inputs
from earshot.config import ScoringConfig
from earshot.extract import OfflineLexiconExtractor
from earshot.memory import SignalLedger
from earshot.schema import Conversation
from earshot.tenants import BY_ID, DEFAULT_TENANT

# Exactly the fields `aws/transcripts.parse_conversation` requires, and nothing else. Asserted
# rather than trusted: this process is holding the corpus, so the wire is the boundary.
WIRE_KEYS = frozenset({"conversation_id", "customer_id", "channel", "day", "turns"})

_rows: list[tuple[str, str, str]] = []


def _record(resource: str, action: str, result: str) -> None:
    _rows.append((resource, action, result))
    print(f"  {action:<9} {resource:<40} {result}")


@dataclass
class Prediction:
    """What the local pipeline says the deployed one must produce."""

    conversations: int = 0
    customers: int = 0
    ledger_writes: int = 0
    # (customer_id, conversation_id, score, signal_type, as_of_day) per crossing, in order.
    enqueues: list[tuple[str, str, float, str, int]] = field(default_factory=list)

    @property
    def crossing_customers(self) -> set[str]:
        return {e[0] for e in self.enqueues}

    @property
    def cases(self) -> int:
        """One case per crossing CUSTOMER, not per crossing. `case_record.make_case_id` keys on
        the first crossing day, so a customer who crosses again overwrites one case."""
        return len(self.crossing_customers)


def wire_payload(conversation: Conversation) -> dict[str, Any]:
    """One transcript, as the queue carries it. Named fields only -- see the module docstring."""
    payload = {
        "conversation_id": conversation.conversation_id,
        "customer_id": conversation.customer_id,
        "channel": conversation.channel.value,
        "day": conversation.day,
        "turns": [
            {"index": t.index, "speaker": t.speaker, "text": t.text} for t in conversation.turns
        ],
    }
    extra = set(payload) - WIRE_KEYS
    if extra:  # unreachable while the dict above is literal, and that is the point of asserting
        raise AssertionError(f"transcript payload carries non-wire fields: {sorted(extra)}")
    return payload


def by_customer(conversations: list[Conversation]) -> dict[str, list[Conversation]]:
    """Grouped, and each group sorted by day. Accumulation is order-dependent."""
    grouped: dict[str, list[Conversation]] = defaultdict(list)
    for conversation in conversations:
        grouped[conversation.customer_id].append(conversation)
    return {cid: sorted(convs, key=lambda c: c.day) for cid, convs in sorted(grouped.items())}


def predict(conversations: list[Conversation], threshold: float) -> Prediction:
    """Run the same ledger, the same extractor and the same threshold locally.

    Deliberately a re-implementation of `Ingestor.ingest`'s *sequence* rather than a call into it:
    `Ingestor` needs a `LedgerStore`, and pointing this at DynamoDB would make the prediction a
    reading of the thing it is supposed to be checking. The scoring itself is not reimplemented --
    `SignalLedger.best()` is the same call the handler makes.
    """
    scoring = ScoringConfig()
    extractor = OfflineLexiconExtractor()
    prediction = Prediction(conversations=len(conversations))
    grouped = by_customer(conversations)
    prediction.customers = len(grouped)
    for customer_id, convs in grouped.items():
        # One ledger per customer, because that is what `LedgerStore.load_ledger` returns.
        ledger = SignalLedger(scoring)
        for conversation in convs:
            for signal in extractor.extract(conversation):
                ledger.append(signal)
                prediction.ledger_writes += 1
            known = ledger.signals(customer_id)
            # `ingest.py`: today is the latest day ON THE LEDGER, not this message's day, so an
            # out-of-order arrival cannot decay evidence that has not aged.
            as_of_day = max([conversation.day] + [s.day for s in known])
            breakdown = ledger.best(customer_id, as_of_day)
            if breakdown.entries and breakdown.score >= threshold:
                prediction.enqueues.append(
                    (
                        customer_id,
                        conversation.conversation_id,
                        breakdown.score,
                        breakdown.signal_type.value,
                        as_of_day,
                    )
                )
    return prediction


def send(sqs: Any, queue_url: str, grouped: dict[str, list[Conversation]], dry_run: bool) -> int:
    """One batch per customer, in day order. Returns the number of messages accepted.

    One customer per batch is not required -- FIFO groups are independent -- but it makes the
    ordering that accumulation depends on obvious from the call rather than inferred from SQS's
    batch semantics, and no customer here has more than the 10-entry batch limit.
    """
    sent = 0
    for customer_id, convs in grouped.items():
        entries = [
            {
                "Id": str(i),
                "MessageBody": json.dumps(wire_payload(c)),
                # Per-customer ordering. Different customers are different groups and interleave.
                "MessageGroupId": customer_id,
                # Content-based dedup is off on this queue, so the producer must supply this.
                # The conversation id makes a re-feed a no-op rather than a double-count.
                "MessageDeduplicationId": c.conversation_id,
            }
            for i, c in enumerate(convs)
        ]
        if len(entries) > 10:
            raise AssertionError(f"{customer_id} has {len(entries)} conversations; batch max is 10")
        if dry_run:
            sent += len(entries)
            continue
        response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
        failed = response.get("Failed") or []
        if failed:
            for f in failed:
                _record(f"sqs:{customer_id}", "SEND", f"FAILED {f.get('Code')} {f.get('Message')}")
        sent += len(response.get("Successful") or [])
    return sent


def send_poison(sqs: Any, queue_url: str, count: int, dry_run: bool) -> int:
    """Publish deliberately malformed transcripts, to prove the failure path actually works.

    Six alarms existed for a week and not one had ever transitioned to ALARM, so every threshold
    was reasoned rather than observed. One bad record exercises four things at once: the `Failed`
    EMF metric, the `earshot-dev-ingest-failures` alarm crossing (`Failed >= 1`, Sum over 300s),
    `batchItemFailures` isolating the bad record from its healthy neighbours, and the transcripts
    DLQ -- which did not exist before 2026-09-03.

    **Safe by construction, and each part matters.** The payload is missing required fields, so
    `parse_conversation` raises before anything is archived or scored -- nothing reaches the ledger.
    `MessageGroupId` is a throwaway, NOT a customer id, because a FIFO group is ordered and a poison
    message blocks its own group: putting this on a real customer's group would stall that
    customer's stream for as long as the retries last. With `maxReceiveCount` 3 and a 360s
    visibility timeout it retries for ~18 minutes and then moves to the DLQ, rather than the 4 days
    it would have taken before that queue had one.
    """
    group = f"POISON-TEST-{int(time.time())}"
    entries = [
        {
            "Id": str(i),
            # Missing `customer_id`, `channel`, `day` and `turns`. `parse_conversation` rejects
            # rather than defaulting, which is the property being exercised.
            "MessageBody": json.dumps({"conversation_id": f"{group}-{i}", "malformed": True}),
            "MessageGroupId": group,
            "MessageDeduplicationId": f"{group}-{i}",
        }
        for i in range(count)
    ]
    if dry_run:
        _record("sqs:poison", "SEND", f"DRY-RUN -- would publish {count} malformed message(s)")
        return count
    response = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
    sent = len(response.get("Successful") or [])
    _record("sqs:poison", "SEND", f"published {sent} malformed message(s) as group {group}")
    return sent


def alarm_states(cw: Any, stage: str) -> list[tuple[str, str]]:
    """Every earshot alarm and its state, so "it fired" is read off AWS rather than asserted."""
    try:
        alarms = cw.describe_alarms(AlarmNamePrefix=f"earshot-{stage}-")["MetricAlarms"]
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record("cloudwatch:alarms", "CHECK", f"FAILED {type(exc).__name__}")
        return []
    return sorted((a["AlarmName"], a["StateValue"]) for a in alarms)


def _count(ddb: Any, table: str) -> int | None:
    """`Select=COUNT` rather than `describe_table`'s ItemCount, which AWS refreshes roughly every
    six hours and would report 0 long after a feed landed."""
    try:
        total, kwargs = 0, {"TableName": table, "Select": "COUNT"}
        while True:
            page = ddb.scan(**kwargs)
            total += page["Count"]
            if not page.get("LastEvaluatedKey"):
                return total
            kwargs["ExclusiveStartKey"] = page["LastEvaluatedKey"]
    except Exception as exc:  # noqa: BLE001 - "cannot read" is a result, not a crash
        _record(f"dynamodb:{table}", "COUNT", f"FAILED {type(exc).__name__}")
        return None


def _queue_depth(sqs: Any, url: str) -> tuple[int, int]:
    attrs = sqs.get_queue_attributes(
        QueueUrl=url,
        AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
    )["Attributes"]
    return (
        int(attrs["ApproximateNumberOfMessages"]),
        int(attrs["ApproximateNumberOfMessagesNotVisible"]),
    )


def get_cases(lam: Any, stage: str) -> dict[str, Any] | None:
    """`GET /cases` through the real handler and the real table.

    Invoked rather than fetched over the Function URL: the URL is `AuthType=AWS_IAM` and signing it
    is a separate open question (the reviewer UI cannot). This exercises the same handler, routing
    and DynamoDB read; only the HTTP and IAM hop is skipped, and saying so is the honest framing.
    """
    event = {"rawPath": "/cases", "requestContext": {"http": {"method": "GET"}}}
    try:
        raw = lam.invoke(
            FunctionName=f"earshot-{stage}-api",
            Payload=json.dumps(event).encode(),
        )["Payload"].read()
        envelope = json.loads(raw)
        status = envelope.get("statusCode")
        body = json.loads(envelope.get("body") or "{}")
        _record(f"lambda:earshot-{stage}-api", "GET", f"/cases -> {status}")
        return {"status": status, "body": body}
    except Exception as exc:  # noqa: BLE001 - reported as a row, not a crash
        _record(f"lambda:earshot-{stage}-api", "GET", f"FAILED {type(exc).__name__}: {exc}")
        return None


def observe(
    ddb: Any, sqs: Any, lam: Any, stage: str, prediction: Prediction, settle: int
) -> dict[str, Any]:
    """Wait for both queues to drain, then read the end state.

    Bounded by a deadline and reported either way. A poll loop that gives up silently is how a
    half-finished run gets written down as a finished one.
    """
    transcripts = sqs.get_queue_url(QueueName=f"earshot-{stage}-transcripts.fifo")["QueueUrl"]
    investigations = sqs.get_queue_url(QueueName=f"earshot-{stage}-investigations")["QueueUrl"]
    deadline = time.monotonic() + settle
    drained = False
    while time.monotonic() < deadline:
        t_visible, t_flight = _queue_depth(sqs, transcripts)
        i_visible, i_flight = _queue_depth(sqs, investigations)
        if t_visible == t_flight == i_visible == i_flight == 0:
            drained = True
            break
        time.sleep(5)
    t_visible, t_flight = _queue_depth(sqs, transcripts)
    i_visible, i_flight = _queue_depth(sqs, investigations)
    _record(
        f"sqs:earshot-{stage}-transcripts.fifo",
        "DRAIN",
        f"{t_visible} waiting, {t_flight} in flight",
    )
    _record(
        f"sqs:earshot-{stage}-investigations",
        "DRAIN",
        f"{i_visible} waiting, {i_flight} in flight",
    )
    if not drained:
        _record("sqs:both", "DRAIN", f"FAILED not empty after {settle}s -- state below is partial")
    dlq_visible, _ = _queue_depth(
        sqs, sqs.get_queue_url(QueueName=f"earshot-{stage}-investigations-dlq")["QueueUrl"]
    )
    _record(f"sqs:earshot-{stage}-investigations-dlq", "CHECK", f"{dlq_visible} messages")

    ledger = _count(ddb, table_name(stage, "ledger"))
    cases = _count(ddb, table_name(stage, "cases"))
    _record(f"dynamodb:{table_name(stage, 'ledger')}", "COUNT", f"{ledger} entries")
    _record(f"dynamodb:{table_name(stage, 'cases')}", "COUNT", f"{cases} cases")
    api = get_cases(lam, stage)
    return {
        "drained": drained,
        "dlq": dlq_visible,
        "ledger": ledger,
        "cases": cases,
        "api": api,
        "prediction": prediction,
    }


def verify(state: dict[str, Any], *, strict: bool = True) -> list[str]:
    """Deployed reality against the local answer key. Returns the failures, empty if it agrees.

    `strict=False` when the DEPLOYED reader is a model. Then exact equality is the wrong contract
    and asserting it would manufacture a failure: `predict()` runs the offline lexicon, a model
    reads differently by design, and a model is not deterministic even against itself. What still
    has to hold is structural -- the queues drained, nothing reached the DLQ, the reader found
    something, the API answers, and every case it serves is genuinely at or above the online cut.
    Reporting those honestly beats reporting a green equality that was never meaningful.
    """
    prediction: Prediction = state["prediction"]
    failures = []
    if not strict:
        if state["ledger"] is not None and state["ledger"] <= 0:
            failures.append("the ledger is empty -- the deployed reader found nothing at all")
        if state["dlq"]:
            failures.append(f"{state['dlq']} message(s) on the DLQ -- something failed three times")
        if not state["drained"]:
            failures.append("queues did not drain inside the settle window")
        api = state["api"]
        if api is None:
            failures.append("GET /cases did not answer")
        elif api["status"] != 200:
            failures.append(f"GET /cases returned {api['status']}")
        else:
            for case in api["body"].get("cases") or []:
                if not isinstance(case, dict):
                    continue
                score, cut = case.get("score"), case.get("threshold")
                if score is None or cut is None:
                    failures.append(f"case {case.get('case_id')} carries no score or threshold")
                elif score < cut:
                    failures.append(
                        f"case {case.get('case_id')} scores {score} below its own cut {cut}"
                    )
        return failures
    if state["ledger"] is not None and state["ledger"] != prediction.ledger_writes:
        failures.append(
            f"ledger holds {state['ledger']} entries, local pipeline wrote "
            f"{prediction.ledger_writes}"
        )
    if state["cases"] is not None and state["cases"] != prediction.cases:
        failures.append(f"cases table holds {state['cases']}, local pipeline crossed "
                        f"{prediction.cases} customer(s)")
    if state["dlq"]:
        failures.append(f"{state['dlq']} message(s) on the DLQ -- something failed three times")
    api = state["api"]
    if api is None:
        failures.append("GET /cases did not answer")
    elif api["status"] != 200:
        failures.append(f"GET /cases returned {api['status']}")
    else:
        served = api["body"].get("cases") or api["body"].get("items") or []
        if len(served) != prediction.cases:
            failures.append(f"GET /cases served {len(served)} case(s), expected {prediction.cases}")
        served_customers = {c.get("customer_id") for c in served if isinstance(c, dict)}
        missing = prediction.crossing_customers - served_customers
        if missing:
            failures.append(f"crossing customers absent from GET /cases: {sorted(missing)}")
    if not state["drained"]:
        failures.append("queues did not drain inside the settle window")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Feed one tenant's book through the deployed pipeline and verify the result."
    )
    parser.add_argument("--stage", choices=STAGES, default="dev")
    parser.add_argument("--tenant", choices=sorted(BY_ID), default=DEFAULT_TENANT.tenant_id)
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="default: on. Pass --no-dry-run to actually publish to SQS.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="the ONLINE cut, and it must match the deployed EARSHOT_THRESHOLD or the prediction "
        "is against a different system than the one being fed",
    )
    parser.add_argument(
        "--observe-only",
        action="store_true",
        help="read the deployed state and verify it, without sending anything",
    )
    parser.add_argument(
        "--deployed-reader",
        choices=("offline", "bedrock"),
        default="offline",
        help="which reader the DEPLOYED ingest handler is running (EARSHOT_EXTRACTOR). Must match, "
        "or the local prediction is against a different system than the one being fed. `bedrock` "
        "relaxes the equality checks to structural ones -- see `verify`.",
    )
    parser.add_argument(
        "--poison",
        type=int,
        default=0,
        help="publish N malformed transcripts INSTEAD of the book, to prove the failure path and "
        "the ingest-failures alarm actually fire. Safe: its own throwaway message group, and the "
        "DLQ catches it after 3 attempts.",
    )
    parser.add_argument(
        "--settle",
        type=int,
        default=180,
        help="seconds to wait for both queues to drain before reading the end state",
    )
    args = parser.parse_args()

    tenant = BY_ID[args.tenant]
    conversations, _context_for, _account_for = stream_inputs(tenant)
    grouped = by_customer(list(conversations))
    prediction = predict(list(conversations), args.threshold)

    print(f"FEED    stage={args.stage}  tenant={tenant.tenant_id}  region={REGION}  "
          f"dry_run={args.dry_run}")
    print(f"        threshold={args.threshold}  extractor=offline (the deployed default; keyless)")
    print("\nLocal prediction -- what the deployed pipeline must reproduce")
    print(f"  {prediction.conversations} conversations across {prediction.customers} customers")
    print(f"  {prediction.ledger_writes} ledger writes")
    print(f"  {len(prediction.enqueues)} crossing(s) -> {prediction.cases} case(s)")
    for customer_id, conversation_id, score, signal_type, as_of_day in prediction.enqueues:
        print(f"    {customer_id} crosses on {conversation_id}: score={score:.6f} "
              f"type={signal_type} as_of_day={as_of_day}")

    import boto3  # noqa: PLC0415 -- the AWS path is the whole point; keep the import at the edge
    from botocore.config import Config  # noqa: PLC0415 -- same reason

    # boto3 defaults to a 60s connect timeout with retries behind it, so an unreachable endpoint
    # hangs for minutes and reads as a slow run rather than a broken one. On 2026-09-03 that cost
    # ~10 minutes of wall clock across a handful of calls before anyone questioned the network.
    timeouts = Config(connect_timeout=8, read_timeout=20, retries={"max_attempts": 3})
    sqs = boto3.client("sqs", region_name=REGION, config=timeouts)
    ddb = boto3.client("dynamodb", region_name=REGION, config=timeouts)
    lam = boto3.client("lambda", region_name=REGION, config=timeouts)
    cw = boto3.client("cloudwatch", region_name=REGION, config=timeouts)

    print(f"\n  {'ACTION':<9} {'RESOURCE':<40} RESULT\n")
    if args.poison:
        # The failure path, not the happy one. Verification is different in kind: nothing should
        # reach the ledger, and an alarm should cross -- so `verify()` does not apply here.
        queue_url = sqs.get_queue_url(QueueName=f"earshot-{args.stage}-transcripts.fifo")[
            "QueueUrl"
        ]
        if args.dry_run:
            # Deliberately before any CloudWatch read: a preview that needs a reachable endpoint
            # to say what it would do is not much of a preview.
            send_poison(sqs, queue_url, args.poison, args.dry_run)
            print("\nDRY-RUN -- nothing was published. Pass --no-dry-run to send it.")
            return 0
        for name, state in alarm_states(cw, args.stage):
            _record(f"cloudwatch:{name}", "BEFORE", state)
        send_poison(sqs, queue_url, args.poison, args.dry_run)
        print(f"\n  waiting up to {args.settle}s for the alarm to evaluate "
              f"(Failed >= 1, Sum over a 300s period)...")
        deadline = time.monotonic() + args.settle
        fired: list[tuple[str, str]] = []
        while time.monotonic() < deadline:
            fired = [(n, st) for n, st in alarm_states(cw, args.stage) if st == "ALARM"]
            if fired:
                break
            time.sleep(15)
        for name, state in alarm_states(cw, args.stage):
            _record(f"cloudwatch:{name}", "AFTER", state)
        print("\n" + "-" * 78)
        if fired:
            print(f"ALARM CROSSED: {', '.join(n for n, _ in fired)} -- a threshold that was "
                  "reasoned is now observed.")
            return 0
        print(f"No alarm reached ALARM inside {args.settle}s. `Failed` is a Sum over a 300s "
              "period, so this may simply be too early. Check the metric in CloudWatch before "
              "concluding the alarm is broken.")
        return 1

    if not args.observe_only:
        queue_url = sqs.get_queue_url(QueueName=f"earshot-{args.stage}-transcripts.fifo")[
            "QueueUrl"
        ]
        sent = send(sqs, queue_url, grouped, args.dry_run)
        verb = "DRY-RUN -- would publish" if args.dry_run else "published"
        _record(f"sqs:earshot-{args.stage}-transcripts.fifo", "SEND",
                f"{verb} {sent} message(s) in {len(grouped)} group(s)")
        if args.dry_run:
            print("\nDRY-RUN -- nothing was published. Pass --no-dry-run to feed the pipeline.")
            return 0

    state = observe(ddb, sqs, lam, args.stage, prediction, args.settle)
    strict = args.deployed_reader == "offline"
    failures = verify(state, strict=strict)
    print("\n" + "-" * 78)
    if failures:
        print(f"DISAGREES with the local pipeline -- {len(failures)} finding(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    if strict:
        print("AGREES with the local pipeline: ledger, cases and GET /cases match the prediction.")
    else:
        print(f"deployed reader = {args.deployed_reader}; the local prediction above is the "
              "OFFLINE lexicon's and is NOT the expected answer here -- it is the baseline this "
              "run is meant to differ from. Structural checks passed: queues drained, DLQ empty, "
              "the reader wrote to the ledger, and every case served is at or above its own cut.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
