"""Step 04 — score the UNMODIFIED extractor against the hand-marked gold set.

Offline and deterministic: no network, no keys. Given `out/sample.jsonl` and `out/gold.jsonl`,
this reproduces every published AT-43 number.

What is computed, all with integers beside every rate (PROTOCOL.md section 1):

  strict_recall     primary. Extractor fired the SAME type the gold marks. Identical to the
                    question src/earshot/evals.py:198-200 asks of the synthetic corpus.
  any_type_recall   declared secondary. Fired anything on a document marked anything. The gap
                    against strict is the size of the known taxonomy disagreement over job loss.
  fp_rate           fired on a gold-NEGATIVE (document, type) pair.

Four runs, all published: {sentence-per-turn, whole-document} x {configured rates, raw lexicon}.
Sentence-per-turn with configured rates is the pre-registered primary, because the published
synthetic 0.681 was measured with those same configured rates. Wrapping matters because dampeners
apply per turn (src/earshot/extract.py:71-73), so a whole narrative as one turn lets a single
"my brother" damp every cue in the document.

    uv run python benchmarks/cfpb/steps/04_score.py [run-date]
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import OUT, log, write_json  # noqa: E402

from earshot.config import RunConfig  # noqa: E402
from earshot.extract import OfflineLexiconExtractor  # noqa: E402
from earshot.extract_lexicon import CUES  # noqa: E402
from earshot.schema import Channel, Conversation, SignalType, Turn  # noqa: E402

TYPES = tuple(SignalType)

# Protected so a full stop inside them is not read as a sentence boundary. Deliberately short:
# this is a splitter, not a tokeniser, and every narrative gets the identical treatment.
_ABBREV = ("Mr", "Mrs", "Ms", "Dr", "Inc", "Co", "Corp", "Ltd", "Jr", "Sr", "St", "Ave",
           "No", "vs", "etc", "approx", "Dept", "Acct", "Apt")

# A sentinel that cannot occur in CFPB narrative text, so a protected full stop survives the
# split and is restored afterwards. A plain ASCII token rather than a control character: control
# characters are invisible in a diff, which makes a bug here impossible to review.
_DOT = "@@DOT@@"

_ABBREV_RE = re.compile(r"\b(" + "|".join(_ABBREV) + r")\.", re.IGNORECASE)
# Whole initialisms -- U.S., U.S.A., F.B.I. Matching the run and protecting every stop inside it
# is what keeps the TRAILING stop from being read as a sentence end; a lookahead form protects
# every stop except the last one, which splits "the U.S. branch" in two.
_INITIALS_RE = re.compile(r"\b(?:[A-Z]\.){2,}")
_SENT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    """Plain, uniform sentence split. Applied identically to every document."""
    protected = _ABBREV_RE.sub(lambda m: m.group(1) + _DOT, text)
    protected = _INITIALS_RE.sub(lambda m: m.group(0).replace(".", _DOT), protected)
    parts: list[str] = []
    for line in protected.replace("\r\n", "\n").split("\n"):
        parts.extend(_SENT_RE.split(line))
    return [s for s in (p.replace(_DOT, ".").strip() for p in parts) if s]


def as_conversation(doc: dict, *, wrapping: str) -> Conversation:
    text = doc["complaint_what_happened"]
    chunks = split_sentences(text) if wrapping == "sentence" else [text.strip()]
    return Conversation(
        conversation_id=str(doc["complaint_id"]),
        customer_id=str(doc["complaint_id"]),
        channel=Channel.COMPLAINT,
        day=0,
        turns=tuple(Turn(index=i, speaker="customer", text=c) for i, c in enumerate(chunks)),
    )


def score(docs: list[dict], gold: dict[str, set[str]], *, wrapping: str, rates: str) -> dict:
    cfg = RunConfig()
    extractor = (
        OfflineLexiconExtractor(miss_rate=cfg.offline_miss_rate,
                                false_fire_rate=cfg.offline_false_fire_rate)
        if rates == "configured"
        else OfflineLexiconExtractor()
    )

    per_type: dict[str, dict[str, int]] = {
        t.value: {"tp": 0, "fn": 0, "fp": 0, "tn": 0} for t in TYPES
    }
    per_panel: dict[str, dict[str, int]] = {}
    cue_fires: dict[str, int] = {}
    any_num = any_den = 0

    for doc in docs:
        cid = str(doc["complaint_id"])
        panel = doc["panel"] if doc["panel"] == "A" else f"B/{doc['stratum']}"
        signals = extractor.extract(as_conversation(doc, wrapping=wrapping))
        fired = {s.signal_type.value for s in signals}
        for s in signals:
            cue_fires[s.cue_id] = cue_fires.get(s.cue_id, 0) + 1

        marked = gold.get(cid, set())
        bucket = per_panel.setdefault(panel, {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "docs": 0})
        bucket["docs"] += 1
        for t in TYPES:
            key = ("tp" if (t.value in marked and t.value in fired)
                   else "fn" if t.value in marked
                   else "fp" if t.value in fired
                   else "tn")
            per_type[t.value][key] += 1
            bucket[key] += 1

        if marked:
            any_den += 1
            any_num += 1 if fired else 0

    def rate(num: int, den: int) -> float | None:
        return round(num / den, 4) if den else None

    totals = {k: sum(v[k] for v in per_type.values()) for k in ("tp", "fn", "fp", "tn")}
    return {
        "wrapping": wrapping,
        "rates": rates,
        "documents": len(docs),
        "strict_recall": rate(totals["tp"], totals["tp"] + totals["fn"]),
        "strict_recall_integers": f"{totals['tp']} / {totals['tp'] + totals['fn']}",
        "any_type_recall": rate(any_num, any_den),
        "any_type_recall_integers": f"{any_num} / {any_den}",
        "fp_rate": rate(totals["fp"], totals["fp"] + totals["tn"]),
        "fp_rate_integers": f"{totals['fp']} / {totals['fp'] + totals['tn']}",
        "by_type": {
            t: {**v,
                "recall": rate(v["tp"], v["tp"] + v["fn"]),
                "recall_integers": f"{v['tp']} / {v['tp'] + v['fn']}",
                "fp_rate": rate(v["fp"], v["fp"] + v["tn"]),
                "fp_rate_integers": f"{v['fp']} / {v['fp'] + v['tn']}"}
            for t, v in per_type.items()
        },
        "by_panel": {
            p: {**v,
                "recall": rate(v["tp"], v["tp"] + v["fn"]),
                "recall_integers": f"{v['tp']} / {v['tp'] + v['fn']}"}
            for p, v in sorted(per_panel.items())
        },
        "cue_fires": dict(sorted(cue_fires.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def main() -> None:
    run_date = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    sample_path, gold_path = OUT / "sample.jsonl", OUT / "gold.jsonl"
    if not gold_path.exists():
        raise SystemExit(
            "out/gold.jsonl is missing. The gold marks must exist, and must have been committed, "
            "BEFORE this runs — see PROTOCOL.md section 5."
        )
    docs = [json.loads(x) for x in sample_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    gold: dict[str, set[str]] = {}
    for line in gold_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        gold[str(row["complaint_id"])] = {k for k, v in row["marks"].items() if v}

    missing = {str(d["complaint_id"]) for d in docs} - set(gold)
    if missing:
        raise SystemExit(f"{len(missing)} sampled documents have no gold mark: {sorted(missing)[:5]}")

    runs = {
        f"{w}-{r}": score(docs, gold, wrapping=w, rates=r)
        for w in ("sentence", "document") for r in ("configured", "raw")
    }
    primary = runs["sentence-configured"]

    results = {
        "run_date": run_date,
        "primary_run": "sentence-configured",
        "synthetic_comparator": {
            "extraction_recall": 0.681, "integers": "496 / 728",
            "source": "artifacts/runs/pinned/, quoted in README.md — a single-dataset diagnostic",
        },
        "runs": runs,
    }
    _, digest = write_json("results.json", results)

    lines = [
        f"primary (sentence-per-turn, configured rates): **strict recall "
        f"{primary['strict_recall']} ({primary['strict_recall_integers']})**",
        f"any-type recall {primary['any_type_recall']} ({primary['any_type_recall_integers']})",
        f"false-positive rate {primary['fp_rate']} ({primary['fp_rate_integers']})",
    ]
    lines += [
        f"per type — {t}: recall {v['recall']} ({v['recall_integers']}), "
        f"fp {v['fp_rate']} ({v['fp_rate_integers']})"
        for t, v in primary["by_type"].items()
    ]
    lines += [
        f"per panel — {p}: recall {v['recall']} ({v['recall_integers']}) over {v['docs']} docs"
        for p, v in primary["by_panel"].items()
    ]
    lines += [
        f"sensitivity — {k}: strict {v['strict_recall']} ({v['strict_recall_integers']})"
        for k, v in runs.items() if k != "sentence-configured"
    ]
    never_fired = [c.cue_id for c in CUES if c.cue_id not in primary["cue_fires"]]
    lines.append(
        f"cues that never fired on real prose: **{len(never_fired)} of {len(CUES)}** — "
        + (", ".join(never_fired) if never_fired else "none")
    )
    lines.append(f"`out/results.json` sha256 `{digest}`")
    log("04_score", run_date, lines)


if __name__ == "__main__":
    main()
