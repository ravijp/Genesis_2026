"""Shared plumbing for the AT-43 CFPB benchmark steps.

Every API call goes through `api()` so that the exact URL, the response size and the record
count are logged. Every artifact goes through `write_json()` so that it is hashed. The point is
that a reviewer can reconstruct what was fetched and when without taking anyone's word for it.

Nothing in this folder imports the corpus generator or a ground-truth type; the benchmark reads
real text and a hand-marked gold set, and never touches the synthetic answer key.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"

# --- the pre-registered sampling frame (PROTOCOL.md section 2) -----------------------------
# Retail-banking products only: complaints a bank's own customer makes about their own account.
# Credit reporting, debt collection, money transfer and debt-management are excluded, with
# reasons, in the protocol. Changing this list invalidates the pre-registration.
FRAME_PRODUCTS: tuple[str, ...] = (
    "Checking or savings account",
    "Credit card",
    "Mortgage",
    "Vehicle loan or lease",
    "Student loan",
    "Payday loan, title loan, personal loan, or advance loan",
    "Prepaid card",
)
WINDOW_MIN = "2025-01-01"
WINDOW_MAX = "2025-12-31"

# Date-based, matching the convention `earshot sweep` uses for its seed base.
SEED = 20260809

PANEL_A_N = 100
PANEL_B_STRATA: tuple[tuple[str, tuple[str, ...], int], ...] = (
    (
        "financial_distress",
        (
            "Problem caused by your funds being low",
            "Struggling to pay mortgage",
            "Struggling to repay your loan",
            "Struggling to pay your loan",
        ),
        17,
    ),
    ("churn_intent", ("Closing an account", "Closing your account"), 17),
    (
        "complaint_escalation",
        ("Problem with a company's investigation into an existing problem",),
        16,
    ),
    # life_event has no CFPB metadata handle at all -- no bucket for bereavement, divorce,
    # redundancy or new parenthood. Its denominator comes from natural occurrence only. This
    # absence is pre-registered rather than discovered; see PROTOCOL.md section 3.
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "out"
RUNLOG = ROOT / "RUNLOG.md"

_CALL_COUNT = 0


def frame_params() -> list[tuple[str, str]]:
    """The frame filter, identical everywhere it is used."""
    return [
        ("has_narrative", "true"),
        ("date_received_min", WINDOW_MIN),
        ("date_received_max", WINDOW_MAX),
    ] + [("product", p) for p in FRAME_PRODUCTS]


def api(params: list[tuple[str, str]], *, retries: int = 4, pause: float = 0.25) -> dict[str, Any]:
    """One CFPB API call. Retries on transport errors; raises with the URL on give-up.

    The URL is returned to the caller inside the payload under `_url` so a log line can quote
    the exact request rather than a description of it.
    """
    global _CALL_COUNT
    url = BASE + "?" + urllib.parse.urlencode(params)
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            _CALL_COUNT += 1
            time.sleep(pause)  # deliberate: this is a public service, not a private endpoint
            payload["_url"] = url
            return payload
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"CFPB API failed after {retries} attempts: {url}") from last


def call_count() -> int:
    return _CALL_COUNT


def total_for(params: list[tuple[str, str]]) -> int:
    """`hits.total.value` for a filter, via a size=0 query."""
    payload = api([("size", "0"), *params])
    return int(payload["hits"]["total"]["value"])


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, obj: Any) -> tuple[Path, str]:
    """Write an artifact to out/ with stable formatting, and return its path and hash.

    `sort_keys` and a fixed separator make the file byte-identical across runs that produce the
    same data, so a diff means the data changed rather than the serialiser did.
    """
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path, sha256_of(path)


def read_json(name: str) -> Any:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def log(step: str, run_date: str, lines: list[str]) -> None:
    """Append a run record to RUNLOG.md.

    Append-only and dated. `run_date` is passed in rather than read from the clock so a replay
    can state the date it is replaying, and so nothing here depends on wall-clock time.
    """
    block = [f"\n### {step} — {run_date}\n"]
    block += [f"- {line}\n" for line in lines]
    with RUNLOG.open("a", encoding="utf-8") as fh:
        fh.writelines(block)
    for line in block:
        print(line.rstrip())
