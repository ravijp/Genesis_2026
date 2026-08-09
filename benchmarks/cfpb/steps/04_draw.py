"""Step 04 — draw Panel A (uniform) and Panel B (issue-enriched) from the local frame.

Sampling from a complete local file, so uniformity is arithmetic rather than a property of an
API's paging behaviour. The frame is sorted by numeric `complaint_id` into one canonical order;
a seeded RNG picks distinct indices into it; those rows are the sample. Nothing depends on
result ordering, request timing, or how many records a service will return per page.

Panel B is drawn from the same canonical order, restricted to the `issue` buckets each stratum
declares. A row already taken by Panel A is skipped and replaced by walking forward through the
same seeded index stream, so the replacement rule is fixed in advance and cannot be used to steer
the sample. Every replacement is recorded.

    uv run python benchmarks/cfpb/steps/04_draw.py [run-date] [dest-dir]
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    OUT,
    PANEL_A_N,
    PANEL_B_STRATA,
    SEED,
    log,
    read_json,
    write_json,
)

DEFAULT_DEST = Path("c:/tmp/ccdb")


def take(pool: list[dict], n: int, rng: random.Random, taken: set[str],
         panel: str, stratum: str | None) -> tuple[list[dict], list[dict]]:
    """Pick `n` unused rows from `pool`, recording any skipped as replacements."""
    if n > len(pool):
        raise SystemExit(f"{panel}/{stratum}: asked for {n} from a pool of {len(pool)}")
    order = rng.sample(range(len(pool)), min(len(pool), n * 4))
    picked, replacements = [], []
    for idx in order:
        if len(picked) == n:
            break
        row = pool[idx]
        cid = row["complaint_id"]
        if cid in taken:
            replacements.append({"index": idx, "complaint_id": cid,
                                 "reason": "already drawn into another panel"})
            continue
        taken.add(cid)
        picked.append({**row, "panel": panel, "stratum": stratum, "draw_index": idx})
    if len(picked) != n:
        raise SystemExit(f"{panel}/{stratum}: only {len(picked)} of {n} drawn")
    return picked, replacements


def main() -> None:
    run_date = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(os.environ.get("CCDB_DIR", DEFAULT_DEST))
    frame_file = dest / "frame_2025.jsonl"
    if not frame_file.exists():
        raise SystemExit(f"{frame_file} is missing — run 03_filter.py first")

    rows = [json.loads(x) for x in frame_file.read_text(encoding="utf-8").splitlines() if x.strip()]
    # One canonical order, independent of how the file happened to be written.
    rows.sort(key=lambda r: int(r["complaint_id"]))
    local = read_json("frame_local.json")
    if len(rows) != local["frame_rows"]:
        raise SystemExit(f"frame file holds {len(rows)} rows, frame_local.json says {local['frame_rows']}")

    rng = random.Random(SEED)
    taken: set[str] = set()
    manifest: dict = {"seed": SEED, "run_date": run_date,
                      "frame_rows": len(rows), "panels": {}}

    a_rows, a_repl = take(rows, PANEL_A_N, rng, taken, "A", None)
    manifest["panels"]["A"] = {"n": len(a_rows), "pool": len(rows), "replacements": a_repl,
                               "complaint_ids": [r["complaint_id"] for r in a_rows]}
    print(f"Panel A: {len(a_rows)} drawn from {len(rows):,}")

    sample = list(a_rows)
    for target, buckets, n in PANEL_B_STRATA:
        pool = [r for r in rows if r["issue"] in set(buckets)]
        b_rows, b_repl = take(pool, n, rng, taken, "B", target)
        sample += b_rows
        manifest["panels"][f"B/{target}"] = {
            "n": len(b_rows), "pool": len(pool), "issue_buckets": list(buckets),
            "replacements": b_repl, "complaint_ids": [r["complaint_id"] for r in b_rows]}
        print(f"Panel B/{target}: {len(b_rows)} drawn from pool {len(pool):,}, "
              f"{len(b_repl)} replacements")

    ids = [r["complaint_id"] for r in sample]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate complaint_id across panels — the overlap guard failed")

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "sample.jsonl"
    path.write_text(
        "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in sample),
        encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest["total_drawn"] = len(sample)
    manifest["sample_sha256"] = digest
    _, mdigest = write_json("draw_manifest.json", manifest)

    lengths = sorted(len(r["complaint_what_happened"]) for r in sample)
    log("04_draw", run_date, [
        f"seed **{SEED}**, drawn **{len(sample)}** documents from a local frame of {len(rows):,} "
        f"(Panel A {len(a_rows)}, Panel B {len(sample) - len(a_rows)})",
        "panel pools: " + " · ".join(f"{k} {v['pool']:,}" for k, v in manifest["panels"].items()),
        "replacements: " + " · ".join(
            f"{k} {len(v['replacements'])}" for k, v in manifest["panels"].items()),
        f"narrative length chars: min {lengths[0]}, median {lengths[len(lengths) // 2]}, "
        f"max {lengths[-1]}",
        f"all {len(ids)} complaint_ids distinct",
        f"`out/sample.jsonl` sha256 `{digest}`",
        f"`out/draw_manifest.json` sha256 `{mdigest}`",
    ])
    print("\nNarrative text is deliberately not printed here. Marking is step 04b, after commit.")


if __name__ == "__main__":
    main()
