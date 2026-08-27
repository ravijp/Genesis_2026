"""The persisted shape of one case: what a reviewer screen reads, and nothing else.

**Why this is its own module rather than living in `aws/stores.py`, where it started.** The
local artifact `earshot investigate` writes to disk and the DynamoDB `CASES` item have to carry
the *same* case fields. Two serializers drift, and the drift does not show up as a test
failure — it shows up as a reviewer screen that renders a retro delta from DynamoDB and a blank
column from the artifact, on stage. So there is one function, `case_record()`, and both paths
call it. `CaseStore.put_case()` adds only the three DynamoDB key attributes on top of it.

It is also boto3-free by construction, which is what lets `cli.py` — the keyless laptop path —
share it (`earshot[aws]` is optional and must stay optional). `aws/stores.py` re-exports
`evidence_item` and `evidence_chain`, so nothing that already imports them from there changes.

**Nothing here computes a score.** Every number is read straight off a `LedgerEntry` that
`memory.score()` already filled in. `memory.py` is the only scorer in this codebase, online or
offline; see `evidence_item`.

**A case is two moments, and the record carries both.** `memory.open_case()` describes the
crossing: `opened_on_day`, `opened_by_conversation`, and the score *then*. A `ScoreBreakdown`
describes the customer *now*: the score today and the whole evidence chain, earlier quotes
included. They are separate arguments here because merging them loses one or the other, and
both losses are silent:

  * take the score from the crossing and the queue ranks a faded case at its opening-day seat
    forever, which is not the question `cli.py:_queue` asks ("who should someone look at
    today");
  * take the evidence from the crossing and the retro chain is frozen at the day the case
    opened — so the "we re-read March in light of July" beat renders empty for precisely the
    customers who kept accumulating, which are the ones the whole entry is about.

So `score`/`as_of_day`/`evidence` come from `now`, and `score_at_open`/`opened_on_day`/
`opened_by_conversation` come from `case`.

**No ground truth may appear in this record.** `stratum`, `outcome`, `latent_risk` and
`financial_state` are answer-key fields; this dict goes behind a client-facing screen.
`tests/test_case_record.py` asserts their absence by name, and `tests/test_separation.py`
covers this file by glob.
"""

from __future__ import annotations

from typing import Any

from .memory import ScoreBreakdown
from .schema import Case, LedgerEntry, SignalType

# Zero-padded so a case id sorts by day in a console scan. Not a correctness dependency —
# nothing parses the day back out of a case id — but ids are read by humans in support tickets.
DAY_WIDTH = 6


def make_case_id(customer_id: str, signal_type: SignalType | str, opened_on_day: int) -> str:
    """`memory.Case` carries no id: it identifies a crossing by
    `(customer_id, signal_type, opened_on_day)`. This turns that triple into one id
    deterministically, so re-investigating the same crossing overwrites the same case rather
    than forking the reviewer's queue."""
    st = signal_type.value if isinstance(signal_type, SignalType) else signal_type
    return f"{customer_id}#{st}#{opened_on_day:0{DAY_WIDTH}d}"


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


def case_record(
    case: Case,
    *,
    threshold: float,
    now: ScoreBreakdown | None = None,
    case_id: str | None = None,
    status: str = "open",
    decision: dict[str, Any] | None = None,
    trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The canonical persisted case, ready for `json.dumps` or for `put_item`.

    `now` is the customer's CURRENT breakdown — `SignalLedger.score()` or `.best()` as of today
    — and supplies the score, the as-of day and the evidence chain. It defaults to the crossing
    itself, so a caller holding only a freshly opened case still gets a well-formed record; pass
    it whenever a current breakdown is in hand, which is every case a reviewer sees.

    `decision` / `trace` are the plain dicts `InvestigationDecision.model_dump()` and
    `InvestigationTrace.to_dict()` already produce. Both are treated as opaque here; this
    module never reaches inside them.
    """
    score = case.score if now is None else now.score
    as_of_day = case.opened_on_day if now is None else now.as_of_day
    evidence = case.evidence if now is None else now.entries
    record: dict[str, Any] = {
        "case_id": case_id or make_case_id(case.customer_id, case.signal_type, case.opened_on_day),
        "customer_id": case.customer_id,
        "signal_type": case.signal_type.value,
        # The queue ranks on this one. See the module docstring on the two moments.
        "score": score,
        "score_at_open": case.score,
        "threshold": threshold,
        "opened_on_day": case.opened_on_day,
        "as_of_day": as_of_day,
        "opened_by_conversation": case.opened_by_conversation,
        "evidence": evidence_chain(evidence, threshold),
        "status": status,
    }
    if decision is not None:
        record["decision"] = decision
    if trace is not None:
        record["trace"] = trace
    return record
