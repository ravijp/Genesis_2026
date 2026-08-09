"""Marking utility — show documents for marking, and validate a finished mark set.

Not a numbered pipeline step: it is the tool used to PRODUCE `out/gold.jsonl` (step 04b, by hand)
and to check the result before step 05 is allowed to score it.

    uv run python benchmarks/cfpb/steps/mark.py show 0 25          # documents to mark
    uv run python benchmarks/cfpb/steps/mark.py show 0 25 --ids    # ids only, no text
    uv run python benchmarks/cfpb/steps/mark.py validate           # check out/gold.jsonl
    uv run python benchmarks/cfpb/steps/mark.py validate --file out/gold_second.jsonl
    uv run python benchmarks/cfpb/steps/mark.py agree out/gold.jsonl out/gold_second.jsonl

`show` deliberately hides the panel and stratum of each document. A marker who knows a document
was drawn from the "Struggling to pay your loan" bucket is being told the answer before reading
it, and Panel B would mark higher than it should for that reason alone.

`validate` enforces the parts of MARKING-GUIDE.md that a machine can check: every sampled document
marked exactly once, every mark a known signal type, and -- the one that matters -- every positive
mark carrying a span that occurs VERBATIM in that document's narrative. A quote that is not in the
text is either a transcription slip or an invented one, and neither belongs in an answer key.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import OUT, SEED  # noqa: E402

from earshot.schema import SignalType  # noqa: E402

TYPES = {t.value for t in SignalType}


def load_sample() -> list[dict]:
    path = OUT / "sample.jsonl"
    if not path.exists():
        raise SystemExit(f"{path} is missing — run 04_draw.py first")
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def load_marks(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path} is missing")
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def normalise(text: str) -> str:
    """Whitespace-insensitive comparison, so a span that wraps a line still matches."""
    return " ".join(text.split()).lower()


def cmd_show(argv: list[str]) -> None:
    docs = load_sample()
    start = int(argv[0]) if argv else 0
    end = int(argv[1]) if len(argv) > 1 else min(start + 25, len(docs))
    ids_only = "--ids" in argv
    docs.sort(key=lambda d: int(d["complaint_id"]))
    for i, doc in enumerate(docs[start:end], start=start):
        cid = doc["complaint_id"]
        if ids_only:
            print(f"{i}\t{cid}")
            continue
        # Panel, stratum and issue are withheld on purpose -- see the module docstring.
        print(f"\n{'=' * 78}\n[{i}] complaint_id {cid}  ({doc['product']}, {doc['date_received']})\n{'=' * 78}")
        print(doc["complaint_what_happened"])
    if not ids_only:
        print(f"\n{'=' * 78}\nshown {start}..{end - 1} of {len(docs)}")


SECOND_MARKER_N = 30


def second_marker_ids() -> list[str]:
    """The documents the second marker double-marks, chosen deterministically.

    Derived from the run seed rather than picked, so which 30 get double-marked is not a choice
    anyone made after seeing the marks. Offset by 1 from the draw seed so it is a different
    stream from the one that selected the sample.
    """
    import random

    ids = sorted((d["complaint_id"] for d in load_sample()), key=int)
    return sorted(random.Random(SEED + 1).sample(ids, SECOND_MARKER_N), key=int)


def cmd_second_set(argv: list[str]) -> None:
    docs = {d["complaint_id"]: d for d in load_sample()}
    chosen = second_marker_ids()
    if "--ids" in argv:
        print("\n".join(chosen))
        return
    for i, cid in enumerate(chosen):
        doc = docs[cid]
        # Panel, stratum and issue withheld -- see the module docstring.
        print(f"\n{'=' * 78}\n[{i}] complaint_id {cid}  ({doc['product']}, {doc['date_received']})\n{'=' * 78}")
        print(doc["complaint_what_happened"])
    print(f"\n{'=' * 78}\n{len(chosen)} documents for independent second marking")


def cmd_validate(argv: list[str]) -> None:
    path = Path(argv[argv.index("--file") + 1]) if "--file" in argv else OUT / "gold.jsonl"
    docs = {d["complaint_id"]: d for d in load_sample()}
    marks = load_marks(path)
    problems: list[str] = []

    seen: set[str] = set()
    for row in marks:
        cid = str(row.get("complaint_id", ""))
        if cid in seen:
            problems.append(f"{cid}: marked more than once")
        seen.add(cid)
        if cid not in docs:
            problems.append(f"{cid}: not in the sample")
            continue
        marked = row.get("marks", {})
        unknown = set(marked) - TYPES
        if unknown:
            problems.append(f"{cid}: unknown signal type(s) {sorted(unknown)}")
        if set(marked) != TYPES:
            problems.append(f"{cid}: must carry all four types, missing {sorted(TYPES - set(marked))}")
        haystack = normalise(docs[cid]["complaint_what_happened"])
        spans = row.get("spans", {})
        for t, present in marked.items():
            if not present:
                continue
            span = (spans.get(t) or "").strip()
            if not span:
                problems.append(f"{cid}/{t}: marked positive with no span — a mark without a span is not a mark")
            elif normalise(span) not in haystack:
                problems.append(f"{cid}/{t}: span is not verbatim in the narrative: {span[:70]!r}")
        for t, span in spans.items():
            if span and not marked.get(t):
                problems.append(f"{cid}/{t}: span given for a type marked negative")

    subset = len(seen) < len(docs)
    missing = set(docs) - seen
    if missing and not subset:
        problems.append(f"{len(missing)} sampled documents unmarked")

    counts = {t: sum(1 for r in marks if r.get("marks", {}).get(t)) for t in sorted(TYPES)}
    print(f"file: {path}")
    print(f"documents marked: {len(seen)} of {len(docs)}" + ("  (subset — second marker)" if subset else ""))
    print("positives per type: " + " · ".join(f"{t} {c}" for t, c in counts.items()))
    print(f"documents with at least one mark: {sum(1 for r in marks if any(r.get('marks', {}).values()))}")
    if problems:
        print(f"\n{len(problems)} PROBLEM(S):")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print("\nOK — every positive mark carries a span that occurs verbatim in its narrative.")


def cmd_agree(argv: list[str]) -> None:
    """Cohen's kappa per type, over the documents both files mark."""
    a = {str(r["complaint_id"]): r["marks"] for r in load_marks(Path(argv[0]))}
    b = {str(r["complaint_id"]): r["marks"] for r in load_marks(Path(argv[1]))}
    shared = sorted(set(a) & set(b))
    # --restrict narrows the comparison to a named set of documents. It exists so the
    # UNCONTAMINATED subset can be reported by command rather than by assertion: the first
    # marker read the second marker's summary partway through marking, so agreement over
    # documents marked after that point is not independent. See PROTOCOL.md section 5a.
    if "--restrict" in argv:
        keep = {x.strip() for x in argv[argv.index("--restrict") + 1].split(",") if x.strip()}
        missing = keep - set(shared)
        if missing:
            raise SystemExit(f"--restrict names documents not double-marked: {sorted(missing)}")
        shared = [c for c in shared if c in keep]
        print(f"restricted to {len(shared)} of {len(set(a) & set(b))} double-marked documents")
    if not shared:
        raise SystemExit("the two mark sets share no documents")

    print(f"double-marked documents: {len(shared)}\n")
    disagreements: list[str] = []
    for t in sorted(TYPES):
        n11 = sum(1 for c in shared if a[c].get(t) and b[c].get(t))
        n00 = sum(1 for c in shared if not a[c].get(t) and not b[c].get(t))
        n10 = sum(1 for c in shared if a[c].get(t) and not b[c].get(t))
        n01 = sum(1 for c in shared if not a[c].get(t) and b[c].get(t))
        n = len(shared)
        po = (n11 + n00) / n
        pe = ((n11 + n10) * (n11 + n01) + (n00 + n01) * (n00 + n10)) / (n * n)
        kappa = (po - pe) / (1 - pe) if pe != 1 else None
        k = "undefined (one marker never used this type)" if kappa is None else f"{kappa:.3f}"
        print(f"{t:<24} kappa {k:>10}   agree {n11 + n00}/{n}   both+ {n11}  A-only {n10}  B-only {n01}")
        disagreements += [f"{c}/{t}: A={bool(a[c].get(t))} B={bool(b[c].get(t))}"
                          for c in shared if bool(a[c].get(t)) != bool(b[c].get(t))]

    print(f"\n{len(disagreements)} disagreement(s) to adjudicate in writing:")
    for d in disagreements:
        print(f"  - {d}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd, argv = sys.argv[1], sys.argv[2:]
    if cmd == "show":
        cmd_show(argv)
    elif cmd == "validate":
        cmd_validate(argv)
    elif cmd == "second-set":
        cmd_second_set(argv)
    elif cmd == "agree":
        cmd_agree(argv)
    else:
        raise SystemExit(f"unknown command {cmd!r}\n{__doc__}")


if __name__ == "__main__":
    main()
