"""DynamoDB persistence for the signal ledger, the case queue and the review audit trail.

Three tables, one convention: everything here is a load/persist BOUNDARY, never a second
scorer. `SignalLedger.score()` and `_raw()` (memory.py) are the only place a customer's risk
number is ever computed, online or offline, and nothing in this module reimplements so much
as the decay curve. `LedgerStore.load_ledger()` reads raw signals off DynamoDB, hands them to
an ordinary in-memory `SignalLedger`, and the caller scores it exactly as `cli.py` already
does. If a change here ever needs to know what `_raw()` returns, that change belongs in
memory.py instead.

boto3 is imported lazily, inside `_resolve_table()`, and reached only when a caller asks for a
REAL table (no `table=` override). `earshot[aws]` is an optional dependency
(`[project.optional-dependencies] aws` in pyproject.toml), not a base one -- specifically so a
laptop `uv sync` and the product test suite stay boto3-free (see `aws/__init__.py`'s
docstring). Every class below can be constructed against an injected fake table with boto3
absent from the environment entirely, which is exactly what `tests/test_stores.py` does.

Table design is `docs/architecture/infrastructure.md` S1.6, reproduced here as the one place
key layout can drift from that document if someone edits only one of them:

    LEDGER   PK  CUST#<customer_id>          SK  SIG#<day>#<conversation_id>#<signal_type>
    CASES    PK  CASE#<case_id>               (simple key -- the ranked queue lives entirely
                                                on the GSI below, not on the base table)
             GSI PK  QUEUE#<status>           SK  <zero-padded score>
    REVIEWS  PK  CASE#<case_id>               SK  REVIEW#<iso-timestamp>#<review_id>

DynamoDB has no float type -- `put_item` raises the moment it meets a bare Python float
anywhere in the item, nested or not. `_floats_to_decimal` / `_decimals_to_float` convert at the
boundary via `Decimal(str(x))`, never `Decimal(x)` directly: `str()` on a float is the shortest
decimal string that parses back to the identical bits (Python's float-repr algorithm, since
3.1), so the round trip is exact. `Decimal(x)` instead reproduces float's own binary
imprecision as 50-plus spurious digits.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from ..config import ScoringConfig
from ..memory import SignalLedger
from ..schema import Case, Channel, ExtractedSignal, LedgerEntry, SignalType

REGION = "us-east-1"
STAGES = ("dev", "demo")

# Fixed-width zero-padding so DynamoDB's byte-wise string sort matches numeric sort. Neither
# width is a correctness dependency inside this module -- `SignalLedger.extend()` re-sorts on
# load regardless of SK order, and `CaseStore` always ranks via the GSI Query, never by parsing
# the padded string back into a number. Both exist purely so a console scan, or a future range
# query on either key, reads in the order a human expects.
_DAY_WIDTH = 6
_SCORE_WIDTH = 8  # "0." + 6 fractional digits; score is a saturating function into [0, 1)


def table_name(stage: str, kind: str) -> str:
    """`earshot-<stage>-<kind>` -- the one place this format is spelled out. `tools/provision.py`
    imports this so the tables it creates can never drift from the names these classes read."""
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}, got {stage!r}")
    return f"earshot-{stage}-{kind}"


# ---- CreateTable shapes, shared with tools/provision.py so schema lives in exactly one place --

LEDGER_KEY_SCHEMA = [
    {"AttributeName": "pk", "KeyType": "HASH"},
    {"AttributeName": "sk", "KeyType": "RANGE"},
]
LEDGER_ATTRIBUTE_DEFINITIONS = [
    {"AttributeName": "pk", "AttributeType": "S"},
    {"AttributeName": "sk", "AttributeType": "S"},
]

CASES_KEY_SCHEMA = [{"AttributeName": "pk", "KeyType": "HASH"}]
CASES_ATTRIBUTE_DEFINITIONS = [
    {"AttributeName": "pk", "AttributeType": "S"},
    {"AttributeName": "gsi1pk", "AttributeType": "S"},
    {"AttributeName": "gsi1sk", "AttributeType": "S"},
]
CASES_GSI_NAME = "queue-index"
CASES_GLOBAL_SECONDARY_INDEXES = [
    {
        "IndexName": CASES_GSI_NAME,
        "KeySchema": [
            {"AttributeName": "gsi1pk", "KeyType": "HASH"},
            {"AttributeName": "gsi1sk", "KeyType": "RANGE"},
        ],
        "Projection": {"ProjectionType": "ALL"},
    }
]

REVIEWS_KEY_SCHEMA = [
    {"AttributeName": "pk", "KeyType": "HASH"},
    {"AttributeName": "sk", "KeyType": "RANGE"},
]
REVIEWS_ATTRIBUTE_DEFINITIONS = [
    {"AttributeName": "pk", "AttributeType": "S"},
    {"AttributeName": "sk", "AttributeType": "S"},
]

# One row per table, consumed by provision.py's create loop. NEVER add a "ttl" entry for any of
# these three -- see LedgerStore's docstring. There is deliberately no such field to set, on any
# of the three tables (the task that asked for this module was explicit that none of the three
# carry a TTL, not just the ledger).
TABLE_SPECS: dict[str, dict[str, Any]] = {
    "ledger": {
        "key_schema": LEDGER_KEY_SCHEMA,
        "attribute_definitions": LEDGER_ATTRIBUTE_DEFINITIONS,
        "gsi": None,
    },
    "cases": {
        "key_schema": CASES_KEY_SCHEMA,
        "attribute_definitions": CASES_ATTRIBUTE_DEFINITIONS,
        "gsi": CASES_GLOBAL_SECONDARY_INDEXES,
    },
    "reviews": {
        "key_schema": REVIEWS_KEY_SCHEMA,
        "attribute_definitions": REVIEWS_ATTRIBUTE_DEFINITIONS,
        "gsi": None,
    },
}


# ---- wire-format helpers, shared by all three stores ---------------------------------------


def _to_decimal(x: float) -> Decimal:
    return Decimal(str(x))


def _floats_to_decimal(obj: Any) -> Any:
    """Recurse through a dict/list so a whole item -- including the evidence list and the
    opaque `decision`/`trace` blobs, whose exact shape this module does not know -- can go
    straight into `put_item` without a second, shape-specific converter per caller."""
    if isinstance(obj, float):
        return _to_decimal(obj)
    if isinstance(obj, dict):
        return {k: _floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_floats_to_decimal(v) for v in obj]
    return obj


def _decimals_to_float(obj: Any) -> Any:
    """The inverse, applied on read. Also what makes a read item JSON-serialisable again --
    `Decimal` is not, and a reviewer API will want to hand one of these back as JSON untouched."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _decimals_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimals_to_float(v) for v in obj]
    return obj


def _is_conditional_check_failure(exc: Exception) -> bool:
    """Duck-typed against botocore's error shape (`code = e.response["Error"]["Code"]`) -- the
    same pattern `tools/aws_probe.py` already uses -- so this module never has to import
    `botocore.exceptions.ClientError` just to catch one error code, lazily or otherwise."""
    code = getattr(exc, "response", {}).get("Error", {}).get("Code", "")
    return code == "ConditionalCheckFailedException"


def _resolve_table(table_name_: str, region_name: str, table: Any | None) -> Any:
    """The only place in this module that can import boto3. Reached exclusively when a caller
    wants a REAL table and did not inject one -- so `import earshot.aws.stores` alone, and
    every test in `test_stores.py`, never needs boto3 installed at all."""
    if table is not None:
        return table
    import boto3

    return boto3.resource("dynamodb", region_name=region_name).Table(table_name_)


# ---- Ledger ----------------------------------------------------------------------------------


def _customer_pk(customer_id: str) -> str:
    return f"CUST#{customer_id}"


def _signal_sk(day: int, conversation_id: str, signal_type: SignalType | str) -> str:
    st = signal_type.value if isinstance(signal_type, SignalType) else signal_type
    return f"SIG#{day:0{_DAY_WIDTH}d}#{conversation_id}#{st}"


def _signal_to_item(signal: ExtractedSignal) -> dict[str, Any]:
    return {
        "pk": _customer_pk(signal.customer_id),
        "sk": _signal_sk(signal.day, signal.conversation_id, signal.signal_type),
        "customer_id": signal.customer_id,
        "conversation_id": signal.conversation_id,
        "signal_type": signal.signal_type.value,
        "confidence": signal.confidence,
        "evidence_quote": signal.evidence_quote,
        "turn_index": signal.turn_index,
        "day": signal.day,
        "channel": signal.channel.value,
        "cue_id": signal.cue_id,
    }


def _item_to_signal(item: dict[str, Any]) -> ExtractedSignal:
    return ExtractedSignal(
        customer_id=item["customer_id"],
        conversation_id=item["conversation_id"],
        signal_type=SignalType(item["signal_type"]),
        confidence=float(item["confidence"]),
        evidence_quote=item["evidence_quote"],
        turn_index=int(item["turn_index"]),
        day=int(item["day"]),
        channel=Channel(item["channel"]),
        cue_id=item.get("cue_id", ""),
    )


class LedgerStore:
    """DynamoDB persistence for the append-only signal ledger. Load/persist only -- every
    number `SignalLedger.score()` returns comes from handing this class's output to an
    unmodified `SignalLedger`, never from arithmetic written in this file.

    **There is no delete method on this class, and there must never be one.** A6 in
    infrastructure.md requires never-discard to be a permission boundary, not a convention:
    this is the code-level half (no method exists to call), and the other half is that no IAM
    role in the deployed system is ever granted `dynamodb:DeleteItem` on this table. No method
    here writes a TTL attribute, and `provision.py` never enables TTL on the table this class
    points at, for the identical reason -- a sub-threshold signal that quietly ages out is
    exactly as gone as one a bug deletes. If a future change adds delete, expire or archive
    here, it has broken the one invariant this whole architecture exists to preserve. Don't.

    **Idempotency (A7).** At-least-once delivery means one conversation can be re-ingested.
    `_raw()` (memory.py) sums per signal, so a duplicate append would inflate a customer's
    score permanently -- and never-discard means nothing downstream ever removes the excess.
    `append()` makes every write conditional on no item already existing at
    `(customer_id, day, conversation_id, signal_type)`; a duplicate delivery is a `put_item`
    that fails its condition and changes nothing. `duplicate_deliveries` is the running count of
    exactly that failure -- Appendix A's alarm target, and F1's containment.

    There is deliberately no batch-append. `BatchWriteItem` cannot carry a per-item
    `ConditionExpression`, so a batch path would silently drop the idempotency guarantee every
    single write gets through `append()`. `append_all()` below is a plain Python loop over
    individual conditional writes, not a batch call, for exactly this reason.
    """

    def __init__(
        self, table_name: str, *, region_name: str = REGION, table: Any | None = None
    ) -> None:
        self.table_name = table_name
        self._table = _resolve_table(table_name, region_name, table)
        self._duplicate_count = 0

    @property
    def duplicate_deliveries(self) -> int:
        return self._duplicate_count

    def append(self, signal: ExtractedSignal) -> bool:
        """Persist one signal. Returns `False` -- a no-op, not an error -- if this exact
        `(customer, day, conversation, signal_type)` was already written; `True` if this call
        is the one that wrote it."""
        item = _floats_to_decimal(_signal_to_item(signal))
        try:
            self._table.put_item(Item=item, ConditionExpression="attribute_not_exists(sk)")
            return True
        except Exception as exc:  # noqa: BLE001 - re-raised unless it is the one code we handle
            if _is_conditional_check_failure(exc):
                self._duplicate_count += 1
                return False
            raise

    def append_all(self, signals: list[ExtractedSignal]) -> tuple[int, int]:
        """`append()` looped, never `BatchWriteItem` -- see the class docstring. Returns
        `(written, duplicates)` for THIS call, independent of the running total."""
        written = duplicates = 0
        for s in signals:
            if self.append(s):
                written += 1
            else:
                duplicates += 1
        return written, duplicates

    def load(self, customer_id: str) -> list[ExtractedSignal]:
        """Every signal ever recorded for this customer. Order is whatever DynamoDB returns --
        `load_ledger()` (and `SignalLedger.extend()` beneath it) sorts by
        `(day, conversation_id, turn_index)` before appending, so callers never need to care."""
        items: list[dict[str, Any]] = []
        kwargs: dict[str, Any] = {
            "KeyConditionExpression": "pk = :pk",
            "ExpressionAttributeValues": {":pk": _customer_pk(customer_id)},
        }
        while True:
            resp = self._table.query(**kwargs)
            items.extend(resp.get("Items", []))
            last_key = resp.get("LastEvaluatedKey")
            if not last_key:
                break
            kwargs["ExclusiveStartKey"] = last_key
        return [_item_to_signal(item) for item in items]

    def load_ledger(self, customer_id: str, cfg: ScoringConfig | None = None) -> SignalLedger:
        """The entire load boundary: read this customer's raw signals, hand them to a fresh,
        UNCHANGED `SignalLedger`. Scoring from here on is memory.py's job -- call `.score()` or
        `.best()` on the object this returns, exactly as `cli.py` already does."""
        ledger = SignalLedger(cfg)
        ledger.extend(self.load(customer_id))
        return ledger


# ---- Cases -------------------------------------------------------------------------------------


def _padded_score(score: float) -> str:
    """DynamoDB sorts the GSI's string range key byte-wise, so an unpadded `str(score)` would
    put "0.9" before "0.85" -- fixed-width zero-padding is what makes that order match numeric
    order. Six fractional digits is well past the precision `ScoringConfig.saturation` ever
    produces (scores live in [0, 1))."""
    return f"{score:0{_SCORE_WIDTH}.6f}"


def evidence_item(entry: LedgerEntry, threshold: float) -> dict[str, Any]:
    """One evidence-chain row from an UNCHANGED `memory.LedgerEntry`. Every number below --
    `contribution_at_write/now`, `score_at_write/now`, `retro_delta`, `load_bearing` -- is read
    directly off the entry `memory.score()` already computed; nothing here recomputes any of
    it. `threshold` is required because `is_load_bearing()` takes it as an argument: memory.py
    never stores a load-bearing bit on the entry itself, since the answer depends on which
    threshold is asked about."""
    s = entry.signal
    return {
        "conversation_id": s.conversation_id,
        "day": s.day,
        "channel": s.channel.value,
        "signal_type": s.signal_type.value,
        "evidence_quote": s.evidence_quote,
        "confidence": s.confidence,
        "turn_index": s.turn_index,
        "cue_id": s.cue_id,
        "contribution_at_write": entry.contribution_at_write,
        "contribution_now": entry.contribution_now,
        "score_at_write": entry.score_at_write,
        "score_now": entry.score_now,
        "retro_delta": entry.retro_delta,
        "load_bearing": entry.is_load_bearing(threshold),
    }


def evidence_chain(entries: list[LedgerEntry], threshold: float) -> list[dict[str, Any]]:
    """`evidence_item()` for a whole case, oldest first -- the order the retro re-score prints
    in (`cli.py`'s `RETRO RE-SCORE` block) and the order a reviewer reads an evidence chain in."""
    return [evidence_item(e, threshold) for e in sorted(entries, key=lambda e: e.signal.day)]


class CaseStore:
    """DynamoDB persistence for the reviewer's ranked case queue -- what S1.6 says `cli.py`
    currently throws away: `ctx.score`, `ctx.signal_type`, `ctx.threshold`, and the retro
    fields `memory.score()` computes (`score_at_write/now`, `contribution_at_write/now`,
    `load_bearing`). Without this table none of the three reviewer-UI beats -- ranked list,
    evidence chain, retro re-score -- has anything to read from disk.

    The base table has a SIMPLE primary key, `pk = CASE#<case_id>` only. The ranked queue is
    served entirely off the GSI (`gsi1pk = QUEUE#<status>`, `gsi1sk = <padded score>`) --
    DynamoDB lets a GSI's key attributes be any ordinary top-level attributes on the item,
    independent of the base table's own key schema, so no sort key is needed on the base table
    at all.

    `memory.Case` carries no `case_id` -- it identifies a crossing by
    `(customer_id, signal_type, opened_on_day)` instead. `make_case_id` turns that triple into
    one deterministically, so re-investigating the same crossing overwrites the same case
    rather than forking the queue; pass an explicit `case_id` to `put_case` for any other
    identity scheme a caller prefers.

    `update_status` touches ONLY the status/GSI attributes, never the score or evidence. Q3 in
    infrastructure.md asks whether a dismissal should reduce the score, suppress the customer,
    or only annotate; this class answers "only annotate" by construction -- mutating a case's
    evidence in place is exactly what S1.6's own Reviews section calls out as destroying the
    audit trail. The "who dismissed and why" record belongs in `ReviewStore`, never here.
    """

    def __init__(
        self, table_name: str, *, region_name: str = REGION, table: Any | None = None
    ) -> None:
        self.table_name = table_name
        self._table = _resolve_table(table_name, region_name, table)

    @staticmethod
    def make_case_id(customer_id: str, signal_type: SignalType | str, opened_on_day: int) -> str:
        st = signal_type.value if isinstance(signal_type, SignalType) else signal_type
        return f"{customer_id}#{st}#{opened_on_day:0{_DAY_WIDTH}d}"

    def put_case(
        self,
        case: Case,
        *,
        threshold: float,
        case_id: str | None = None,
        status: str = "open",
        decision: dict[str, Any] | None = None,
        trace: dict[str, Any] | None = None,
    ) -> str:
        """Persist one `memory.Case`, evidence chain and all. `threshold` is required because
        `is_load_bearing()` needs it (see `evidence_item`) -- pass the same threshold the case
        was opened against. `decision`/`trace` are the plain dicts `InvestigationDecision
        .model_dump()` / `InvestigationTrace.to_dict()` already produce (see `cli.py`'s
        `_print_case`); this module treats both as opaque and only ever converts their floats.

        Returns the case_id actually written, so a caller that let this method derive one via
        `make_case_id` still has it for `update_status` or `ReviewStore`.
        """
        case_id = case_id or self.make_case_id(
            case.customer_id, case.signal_type, case.opened_on_day
        )
        item: dict[str, Any] = {
            "pk": f"CASE#{case_id}",
            "case_id": case_id,
            "customer_id": case.customer_id,
            "signal_type": case.signal_type.value,
            "score": case.score,
            "threshold": threshold,
            "opened_on_day": case.opened_on_day,
            "opened_by_conversation": case.opened_by_conversation,
            "evidence": evidence_chain(case.evidence, threshold),
            "status": status,
            "gsi1pk": f"QUEUE#{status}",
            "gsi1sk": _padded_score(case.score),
        }
        if decision is not None:
            item["decision"] = decision
        if trace is not None:
            item["trace"] = trace
        self._table.put_item(Item=_floats_to_decimal(item))
        return case_id

    def get_case(self, case_id: str) -> dict[str, Any] | None:
        resp = self._table.get_item(Key={"pk": f"CASE#{case_id}"})
        item = resp.get("Item")
        return _decimals_to_float(item) if item is not None else None

    def update_status(self, case_id: str, status: str) -> None:
        """Move a case between queues without touching its evidence chain -- see the class
        docstring for why that split is deliberate."""
        self._table.update_item(
            Key={"pk": f"CASE#{case_id}"},
            UpdateExpression="SET #s = :status, gsi1pk = :gsi1pk",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": status, ":gsi1pk": f"QUEUE#{status}"},
        )

    def list_queue(self, status: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """The ranked queue: highest score first, the reviewer's priority order.
        `ScanIndexForward=False` reverses the GSI's ascending sort on the padded score string."""
        resp = self._table.query(
            IndexName=CASES_GSI_NAME,
            KeyConditionExpression="gsi1pk = :qp",
            ExpressionAttributeValues={":qp": f"QUEUE#{status}"},
            ScanIndexForward=False,
            Limit=limit,
        )
        return [_decimals_to_float(item) for item in resp.get("Items", [])]


# ---- Reviews -----------------------------------------------------------------------------------


class ReviewStore:
    """Append-only audit of reviewer actions: who approved, dismissed or routed a case, when,
    and why. S1.6 gives Ledger and Cases an explicit key design and does not give Reviews one;
    this follows the same idiom as the ledger -- one partition per case, a sort key that encodes
    time so every write lands at a new key and nothing already written is ever touched again.
    There is no update or delete method, on purpose: S1.6 calls this "the one table a regulator
    would ask for", and a table that can be edited after the fact is not an audit trail.
    """

    def __init__(
        self, table_name: str, *, region_name: str = REGION, table: Any | None = None
    ) -> None:
        self.table_name = table_name
        self._table = _resolve_table(table_name, region_name, table)

    def put_review(
        self,
        case_id: str,
        *,
        reviewer: str,
        action: str,
        reason: str = "",
        review_id: str | None = None,
        at: str | None = None,
    ) -> dict[str, Any]:
        """Record one reviewer action. `at` defaults to now (UTC, ISO-8601) and `review_id` to a
        fresh UUID; both are accepted as arguments so a caller can make a write reproducible in
        a test."""
        at = at or datetime.now(timezone.utc).isoformat()
        review_id = review_id or uuid.uuid4().hex
        item = {
            "pk": f"CASE#{case_id}",
            "sk": f"REVIEW#{at}#{review_id}",
            "case_id": case_id,
            "review_id": review_id,
            "reviewer": reviewer,
            "action": action,
            "reason": reason,
            "at": at,
        }
        self._table.put_item(Item=item)
        return item

    def list_reviews(self, case_id: str) -> list[dict[str, Any]]:
        """Every review action on this case, oldest first (the SK's timestamp prefix sorts
        chronologically)."""
        resp = self._table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": f"CASE#{case_id}"},
        )
        return resp.get("Items", [])
