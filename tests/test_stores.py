"""Unit tests for `earshot.aws.stores` against a hand-rolled fake DynamoDB table.

No boto3, no botocore, no network, no credentials, anywhere in this file -- `FakeTable` mimics
just enough of the boto3 Table resource surface (put_item/get_item/update_item/query, and the
duck-typed `.response["Error"]["Code"]` shape `put_item` raises on a conditional-check failure)
for `stores.py` to run against unmodified. That is the point: this file proves the adapters
work correctly using the SAME code path a real deployment uses, without ever touching AWS. The
236 tests this repo already had must keep running with no AWS access, and this file adds to
that count rather than narrowing it.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from earshot.aws import stores
from earshot.aws.stores import CaseStore, LedgerStore, ReviewStore, evidence_chain, evidence_item
from earshot.config import ScoringConfig
from earshot.memory import SignalLedger
from earshot.schema import Channel, ExtractedSignal, SignalType


# ---- the fake table -------------------------------------------------------------------------


class _FakeConditionalCheckFailed(Exception):
    """Shaped like botocore's ClientError -- `.response["Error"]["Code"]` -- which is exactly
    what `stores._is_conditional_check_failure` duck-types against. Nothing in this class, or
    anywhere else in this file, imports botocore."""

    def __init__(self) -> None:
        super().__init__("ConditionalCheckFailedException")
        self.response = {"Error": {"Code": "ConditionalCheckFailedException"}}


class FakeTable:
    """A minimal stand-in for a boto3 DynamoDB Table resource: enough of put_item / get_item /
    update_item / query (plain partition query and GSI query alike) for every method in
    `stores.py` to run unmodified. `page_size`, when set, splits a partition query into pages of
    that size and returns `LastEvaluatedKey`, so `LedgerStore.load()`'s pagination loop has
    something real to walk.
    """

    def __init__(self, page_size: int | None = None) -> None:
        self.items: dict[tuple, dict] = {}
        self.page_size = page_size
        self.put_calls = 0

    @staticmethod
    def _key(d: dict) -> tuple:
        return (d["pk"], d["sk"]) if "sk" in d else (d["pk"],)

    def put_item(self, Item: dict, ConditionExpression: str | None = None) -> dict:
        self.put_calls += 1
        key = self._key(Item)
        if ConditionExpression == "attribute_not_exists(sk)" and key in self.items:
            raise _FakeConditionalCheckFailed()
        self.items[key] = dict(Item)
        return {}

    def get_item(self, Key: dict) -> dict:
        item = self.items.get(self._key(Key))
        return {"Item": dict(item)} if item is not None else {}

    def update_item(
        self,
        Key: dict,
        UpdateExpression: str,
        ExpressionAttributeNames: dict,
        ExpressionAttributeValues: dict,
    ) -> dict:
        item = self.items[self._key(Key)]
        # Only the one shape CaseStore.update_status ever sends -- not a general expression
        # evaluator, deliberately, since that is not what this module needs to prove.
        assert UpdateExpression == "SET #s = :status, gsi1pk = :gsi1pk"
        item[ExpressionAttributeNames["#s"]] = ExpressionAttributeValues[":status"]
        item["gsi1pk"] = ExpressionAttributeValues[":gsi1pk"]
        return {}

    def query(
        self,
        KeyConditionExpression: str,
        ExpressionAttributeValues: dict,
        IndexName: str | None = None,
        ScanIndexForward: bool = True,
        Limit: int | None = None,
        ExclusiveStartKey: dict | None = None,
    ) -> dict:
        if IndexName is not None:
            qp = ExpressionAttributeValues[":qp"]
            matches = sorted(
                (dict(i) for i in self.items.values() if i.get("gsi1pk") == qp),
                key=lambda i: i["gsi1sk"],
                reverse=not ScanIndexForward,
            )
            if Limit is not None:
                matches = matches[:Limit]
            return {"Items": matches}

        pk = ExpressionAttributeValues[":pk"]
        matches = sorted(
            (dict(i) for i in self.items.values() if i["pk"] == pk),
            key=lambda i: i.get("sk", ""),
        )
        start = 0
        if ExclusiveStartKey is not None:
            start_sk = ExclusiveStartKey["sk"]
            start = next(i for i, m in enumerate(matches) if m["sk"] == start_sk) + 1
        page = matches[start:]
        resp: dict = {}
        if self.page_size is not None and len(page) > self.page_size:
            page = page[: self.page_size]
            resp["LastEvaluatedKey"] = {"pk": pk, "sk": page[-1]["sk"]}
        resp["Items"] = page
        return resp


def sig(
    day: int,
    conversation: str,
    confidence: float = 0.3,
    customer_id: str = "C1",
    signal_type: SignalType = SignalType.FINANCIAL_DISTRESS,
    channel: Channel = Channel.CALL,
    turn_index: int = 1,
    cue_id: str = "cue.x",
) -> ExtractedSignal:
    return ExtractedSignal(
        customer_id=customer_id,
        conversation_id=conversation,
        signal_type=signal_type,
        confidence=confidence,
        evidence_quote="the customer said something relevant here",
        turn_index=turn_index,
        day=day,
        channel=channel,
        cue_id=cue_id,
    )


# ---- boto3 stays out of this file, structurally, not by promise -----------------------------


def test_module_never_imports_boto3_at_module_level() -> None:
    """Belt and braces on top of the standalone `python -c "import earshot.aws.stores"` check:
    `boto3` must appear only inside `_resolve_table`, never as a top-level statement, or a
    laptop `uv sync` (no `aws` extra) breaks on importing this module at all."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(stores))
    for node in tree.body:  # module-level statements only -- not inside any function
        if isinstance(node, ast.Import):
            assert not any(a.name == "boto3" for a in node.names), (
                "boto3 imported at module level -- this breaks a boto3-free `uv sync`"
            )
        if isinstance(node, ast.ImportFrom):
            assert node.module != "boto3"


# ---- key construction -------------------------------------------------------------------------


def test_table_name_is_namespaced_per_stage() -> None:
    assert stores.table_name("dev", "ledger") == "earshot-dev-ledger"
    assert stores.table_name("demo", "cases") == "earshot-demo-cases"
    assert stores.table_name("dev", "reviews") == "earshot-dev-reviews"


def test_table_name_rejects_an_unknown_stage() -> None:
    with pytest.raises(ValueError):
        stores.table_name("prod", "ledger")


def test_ledger_key_shape_matches_infrastructure_md() -> None:
    """PK = CUST#<customer_id>, SK = SIG#<day>#<conversation_id>#<signal_type> -- infra.md S1.6,
    verified against the literal item a real `put_item` call would send."""
    table = FakeTable()
    store = LedgerStore("t", table=table)
    store.append(sig(day=7, conversation="CONV-9", signal_type=SignalType.CHURN_INTENT))

    (item,) = table.items.values()
    assert item["pk"] == "CUST#C1"
    assert item["sk"] == "SIG#000007#CONV-9#churn_intent"


def test_case_id_is_deterministic_for_the_same_crossing() -> None:
    cid = CaseStore.make_case_id("C1", SignalType.FINANCIAL_DISTRESS, opened_on_day=42)
    assert cid == CaseStore.make_case_id("C1", SignalType.FINANCIAL_DISTRESS, opened_on_day=42)
    # A different day is a different crossing, and must be a different id.
    assert cid != CaseStore.make_case_id("C1", SignalType.FINANCIAL_DISTRESS, opened_on_day=43)


# ---- the conditional write: a duplicate delivery is a no-op ---------------------------------


def test_duplicate_delivery_is_a_no_op_not_a_second_entry() -> None:
    """A7: at-least-once delivery means the same conversation can arrive twice. The second
    `append()` must change nothing and must not raise."""
    store = LedgerStore("t", table=FakeTable())
    s = sig(day=10, conversation="K1")

    assert store.append(s) is True
    assert store.append(s) is False  # exact same (customer, day, conversation, type)

    assert len(store.load("C1")) == 1
    assert store.duplicate_deliveries == 1


def test_duplicate_delivery_count_only_increments_on_the_duplicate() -> None:
    store = LedgerStore("t", table=FakeTable())
    store.append(sig(day=0, conversation="A"))
    store.append(sig(day=10, conversation="B"))  # a genuinely different entry, not a duplicate
    assert store.duplicate_deliveries == 0
    store.append(sig(day=0, conversation="A"))  # now repeat the first one
    assert store.duplicate_deliveries == 1
    assert len(store.load("C1")) == 2


def test_two_different_signal_types_from_one_conversation_are_not_duplicates() -> None:
    """The idempotency key is (customer, day, conversation, signal_type) -- infra.md's own open
    question Q2. Two distinct types from the same conversation are two distinct SKs and both
    must be kept, never collapsed."""
    store = LedgerStore("t", table=FakeTable())
    store.append(sig(day=5, conversation="K1", signal_type=SignalType.CHURN_INTENT))
    store.append(sig(day=5, conversation="K1", signal_type=SignalType.LIFE_EVENT))
    assert store.duplicate_deliveries == 0
    assert len(store.load("C1")) == 2


def test_append_all_reports_written_and_duplicates_for_this_call_only() -> None:
    store = LedgerStore("t", table=FakeTable())
    store.append(sig(day=0, conversation="A"))  # pre-existing, before append_all runs

    written, duplicates = store.append_all(
        [sig(day=0, conversation="A"), sig(day=10, conversation="B"), sig(day=20, conversation="C")]
    )
    assert (written, duplicates) == (2, 1)
    assert len(store.load("C1")) == 3


# ---- the ledger adapter has no delete path, structurally -------------------------------------


def test_ledger_store_has_no_delete_method() -> None:
    """Never-discard must be structural, not conventional (A6) -- there must be no method on
    this class whose name even suggests deletion, expiry or archival."""
    surface = {name for name in dir(LedgerStore) if not name.startswith("__")}
    banned = ("delete", "expire", "archive", "ttl")
    assert not any(word in name.lower() for name in surface for word in banned), (
        f"LedgerStore exposes a deletion-shaped method: {sorted(surface)}"
    )


def test_review_store_has_no_update_or_delete_method() -> None:
    """An audit trail that can be edited after the fact is not an audit trail (S1.6, Reviews)."""
    surface = {name for name in dir(ReviewStore) if not name.startswith("__")}
    assert not any(
        word in name.lower() for name in surface for word in ("delete", "update", "expire")
    ), f"ReviewStore exposes a mutating method: {sorted(surface)}"


# ---- Decimal/float round-tripping without precision loss -------------------------------------


@pytest.mark.parametrize(
    "value",
    [0.0, 1.0, 0.1, 0.3, 0.07, 0.123456789, 1 / 3, 0.35 ** 3, 0.9999999999999999],
)
def test_decimal_round_trip_is_exact(value: float) -> None:
    """`Decimal(str(x))`, never `Decimal(x)` -- the whole reason this helper exists rather than
    a bare `Decimal(x)` call at each write site."""
    decimal_value = stores._to_decimal(value)
    assert float(decimal_value) == value


def test_floats_to_decimal_round_trips_a_nested_structure() -> None:
    original = {
        "score": 0.729401,
        "evidence": [
            {"confidence": 0.31, "contribution_now": 0.0142},
            {"confidence": 0.885, "contribution_now": 0.0},
        ],
        "trace": {"cost_usd": 0.0432, "steps": [{"latency_ms": 812.5}]},
        "label": "unchanged",
        "count": 3,
        "flag": True,
    }
    wire = stores._floats_to_decimal(original)
    # Nothing that reaches DynamoDB may still be a bare float -- put_item would reject it.
    assert not _contains_float(wire)
    back = stores._decimals_to_float(wire)
    assert back == original


def _contains_float(obj) -> bool:
    if isinstance(obj, float):
        return True
    if isinstance(obj, dict):
        return any(_contains_float(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_contains_float(v) for v in obj)
    return False


def test_ledger_round_trip_through_a_fake_table_preserves_confidence_exactly() -> None:
    """The end-to-end path a real deployment uses: append through the public API, load back
    through the public API, and the float that comes out must be bit-identical to the one that
    went in -- not merely close."""
    store = LedgerStore("t", table=FakeTable())
    original = sig(day=3, conversation="K1", confidence=0.123456789)
    store.append(original)

    (loaded,) = store.load("C1")
    assert loaded.confidence == original.confidence
    assert loaded == original  # every field, not just confidence


def test_ledger_load_paginates_across_multiple_query_pages() -> None:
    """`LastEvaluatedKey` must be followed until DynamoDB stops returning one -- a customer
    with more entries than fit in one page is exactly the case never-discard guarantees will
    eventually happen."""
    store = LedgerStore("t", table=FakeTable(page_size=2))
    signals = [sig(day=d, conversation=f"K{d}") for d in range(0, 50, 5)]  # 10 entries
    for s in signals:
        store.append(s)

    loaded = store.load("C1")
    assert len(loaded) == len(signals)
    assert {s.conversation_id for s in loaded} == {s.conversation_id for s in signals}


# ---- scoring is delegated to the unchanged SignalLedger, never reimplemented -----------------


def test_stores_module_does_not_import_the_scoring_machinery() -> None:
    """`_raw()` (memory.py) is built on `math.exp`. If `stores.py` ever needs `math` itself,
    something in this file has started recomputing a score instead of persisting one."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(stores))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    assert "math" not in modules, "stores.py imports math -- it should only ever call memory.py"


def test_load_ledger_reproduces_the_identical_score_memory_py_computes_in_process() -> None:
    """The load boundary: persist a set of signals, read them back into a fresh SignalLedger via
    `load_ledger()`, and score it. The result must be bit-for-bit identical to scoring the SAME
    signals in an ordinary in-process SignalLedger that never touched DynamoDB at all -- proof
    that persistence changes nothing about what memory.py computes."""
    cfg = ScoringConfig()
    signals = [
        sig(day=0, conversation="A", confidence=0.4),
        sig(day=20, conversation="B", confidence=0.5, channel=Channel.COMPLAINT),
        sig(day=45, conversation="C", confidence=0.6),
    ]

    direct = SignalLedger(cfg)
    direct.extend(signals)
    direct_breakdown = direct.score("C1", SignalType.FINANCIAL_DISTRESS, 45)

    store = LedgerStore("t", table=FakeTable())
    for s in signals:
        store.append(s)
    via_store = store.load_ledger("C1", cfg)
    store_breakdown = via_store.score("C1", SignalType.FINANCIAL_DISTRESS, 45)

    assert store_breakdown.score == direct_breakdown.score
    direct_by_day = {e.signal.day: e for e in direct_breakdown.entries}
    for entry in store_breakdown.entries:
        d = direct_by_day[entry.signal.day]
        assert entry.contribution_now == d.contribution_now
        assert entry.contribution_at_write == d.contribution_at_write
        assert entry.score_at_write == d.score_at_write
        assert entry.retro_delta == d.retro_delta


def test_evidence_item_reads_memory_py_numbers_without_recomputing_them() -> None:
    """`evidence_item()` must be a pure read of a `LedgerEntry`'s own fields/property/method --
    never a second formula. Constructed independently here (a plain SignalLedger, no store
    involved) so this test cannot pass merely because the store round-trip above already
    passed."""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    breakdown = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 40)
    threshold = breakdown.score - 0.01  # every entry load-bearing at this cut (test_memory.py)

    for entry in breakdown.entries:
        item = evidence_item(entry, threshold)
        assert item["contribution_at_write"] == entry.contribution_at_write
        assert item["contribution_now"] == entry.contribution_now
        assert item["score_at_write"] == entry.score_at_write
        assert item["score_now"] == entry.score_now
        assert item["retro_delta"] == entry.retro_delta
        assert item["load_bearing"] == entry.is_load_bearing(threshold)


def test_evidence_chain_is_ordered_oldest_first() -> None:
    ledger = SignalLedger()
    ledger.extend([sig(40, "C"), sig(0, "A"), sig(20, "B")])  # appended out of day order
    breakdown = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 40)
    chain = evidence_chain(breakdown.entries, threshold=0.0)
    assert [row["day"] for row in chain] == [0, 20, 40]


# ---- CaseStore: the ranked queue and the status/evidence split -------------------------------


def test_put_case_persists_what_cli_py_currently_discards() -> None:
    """score, signal_type, threshold and the retro fields -- infra.md S1.6's own list of what
    `cli.py` throws away today."""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    threshold = 0.05
    case = ledger.open_case("C1", SignalType.FINANCIAL_DISTRESS, threshold)
    assert case is not None

    store = CaseStore("t", table=FakeTable())
    case_id = store.put_case(case, threshold=threshold)

    read = store.get_case(case_id)
    assert read["customer_id"] == "C1"
    assert read["signal_type"] == "financial_distress"
    assert read["score"] == case.score
    assert read["threshold"] == threshold
    assert len(read["evidence"]) == len(case.evidence)
    assert all("score_now" in row and "load_bearing" in row for row in read["evidence"])


def test_put_case_carries_decision_and_trace_when_supplied() -> None:
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    case = ledger.open_case("C1", SignalType.FINANCIAL_DISTRESS, 0.05)
    assert case is not None

    store = CaseStore("t", table=FakeTable())
    decision = {"verdict": "escalate", "confidence": 0.81}
    trace = {"cost_usd": 0.0421, "model_calls": 3, "steps": [{"latency_ms": 120.5}]}
    case_id = store.put_case(case, threshold=0.05, decision=decision, trace=trace)

    read = store.get_case(case_id)
    assert read["decision"] == decision
    assert read["trace"] == trace


def test_update_status_moves_the_case_between_queues_without_touching_evidence() -> None:
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    case = ledger.open_case("C1", SignalType.FINANCIAL_DISTRESS, 0.05)
    assert case is not None

    store = CaseStore("t", table=FakeTable())
    case_id = store.put_case(case, threshold=0.05)
    before = store.get_case(case_id)

    store.update_status(case_id, "dismissed")
    after = store.get_case(case_id)

    assert after["status"] == "dismissed"
    assert after["evidence"] == before["evidence"], "a status change must never touch evidence"
    assert after["score"] == before["score"]

    assert store.list_queue("open") == []
    assert [c["case_id"] for c in store.list_queue("dismissed")] == [case_id]


def test_list_queue_ranks_highest_score_first() -> None:
    table = FakeTable()
    store = CaseStore("t", table=table)
    low = SignalLedger()
    low.extend([sig(0, "A", confidence=0.1, customer_id="LOW")])
    high = SignalLedger()
    high.extend([sig(0, "A", confidence=0.9, customer_id="HIGH")])

    low_case = low.open_case("LOW", SignalType.FINANCIAL_DISTRESS, 0.0)
    high_case = high.open_case("HIGH", SignalType.FINANCIAL_DISTRESS, 0.0)
    assert low_case is not None and high_case is not None
    assert high_case.score > low_case.score

    store.put_case(low_case, threshold=0.0, case_id="low")
    store.put_case(high_case, threshold=0.0, case_id="high")

    ranked = store.list_queue("open")
    assert [c["case_id"] for c in ranked] == ["high", "low"]


# ---- ReviewStore: append-only audit ------------------------------------------------------------


def test_put_review_then_list_reviews_round_trips() -> None:
    store = ReviewStore("t", table=FakeTable())
    store.put_review(
        "case-1", reviewer="alice@bank.example", action="dismissed", reason="known dispute",
        review_id="r1", at="2026-08-25T10:00:00+00:00",
    )
    reviews = store.list_reviews("case-1")
    assert len(reviews) == 1
    assert reviews[0]["reviewer"] == "alice@bank.example"
    assert reviews[0]["action"] == "dismissed"


def test_reviews_accumulate_rather_than_overwrite() -> None:
    """Two actions on the same case are two rows, never one row updated in place -- an audit
    trail that can lose its first entry is not an audit trail."""
    store = ReviewStore("t", table=FakeTable())
    store.put_review(
        "case-1", reviewer="alice", action="opened", review_id="r1",
        at="2026-08-25T09:00:00+00:00",
    )
    store.put_review(
        "case-1", reviewer="bob", action="dismissed", review_id="r2",
        at="2026-08-25T10:00:00+00:00",
    )
    reviews = store.list_reviews("case-1")
    assert len(reviews) == 2
    assert [r["at"] for r in reviews] == sorted(r["at"] for r in reviews), "must read oldest-first"


def test_put_review_generates_an_id_and_timestamp_when_not_supplied() -> None:
    store = ReviewStore("t", table=FakeTable())
    row = store.put_review("case-1", reviewer="alice", action="approved")
    assert row["review_id"]
    assert row["at"]
    assert store.list_reviews("case-1") == [row]


# ---- table schema sanity: what provision.py actually builds from ------------------------------


def test_table_specs_cover_exactly_the_three_tables_with_no_ttl_field() -> None:
    assert set(stores.TABLE_SPECS) == {"ledger", "cases", "reviews"}
    for kind, spec in stores.TABLE_SPECS.items():
        assert "ttl" not in spec, f"{kind} spec carries a ttl field -- none of these three may"


def test_only_cases_carries_a_gsi() -> None:
    assert stores.TABLE_SPECS["ledger"]["gsi"] is None
    assert stores.TABLE_SPECS["reviews"]["gsi"] is None
    assert stores.TABLE_SPECS["cases"]["gsi"] is not None
    (gsi,) = stores.TABLE_SPECS["cases"]["gsi"]
    assert gsi["IndexName"] == stores.CASES_GSI_NAME


def test_region_and_stage_defaults_are_the_provisioned_account() -> None:
    """Not a network check -- just pinning the constants `provision.py` and every store share
    against the live account recorded in docs/ops/aws-infrastructure.md."""
    assert stores.REGION == "us-east-1"
    assert stores.STAGES == ("dev", "demo")


# ---- construction never needs boto3 when a table is injected ---------------------------------


def test_stores_construct_with_an_injected_table_and_no_region_call() -> None:
    """Every class takes `table=` precisely so a caller -- production code with a real boto3
    resource, or this test file with a fake one -- never has to touch `_resolve_table`'s lazy
    `import boto3` line at all."""
    fake = FakeTable()
    assert LedgerStore("t", table=fake).table_name == "t"
    assert CaseStore("t", table=fake).table_name == "t"
    assert ReviewStore("t", table=fake).table_name == "t"


def test_scoring_config_can_be_ablated_through_the_load_boundary() -> None:
    """The load boundary must not silently pin a config -- `load_ledger` takes one, and an
    ablated config (as the mechanism-ablation arms use) must reach `score()` unchanged."""
    plain_cfg = replace(ScoringConfig(), decay_enabled=False)
    store = LedgerStore("t", table=FakeTable())
    store.append(sig(day=0, conversation="A"))

    ledger = store.load_ledger("C1", plain_cfg)
    fresh = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 0).score
    stale = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 900).score
    assert stale == fresh, "decay_enabled=False did not reach memory.py through the store"
