"""Step 03 — stream the bulk archive and extract the pre-registered frame.

Reads `complaints.csv.zip` without expanding it, keeps only rows matching the frame declared in
PROTOCOL.md section 2 (2025, seven retail-banking products, non-empty narrative), and writes them
to a local JSONL beside the archive -- outside the repo, because it is a few hundred MB.

The committed output is `out/frame_local.json`: counts only, no text. It carries a real
cross-check -- the row count found here against the 141,180 the search API reported independently
in step 01. Two different access paths agreeing is worth more than either one asserting.

    uv run python benchmarks/cfpb/steps/03_filter.py [run-date] [dest-dir]
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import os
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import FRAME_PRODUCTS, WINDOW_MAX, WINDOW_MIN, log, read_json, write_json  # noqa: E402

DEFAULT_DEST = Path("c:/tmp/ccdb")

# CSV header -> the field name used downstream. The bulk export uses human-readable headers while
# the search API uses snake_case; this mapping is the only place that difference lives.
COLUMNS = {
    "Complaint ID": "complaint_id",
    "Date received": "date_received",
    "Product": "product",
    "Sub-product": "sub_product",
    "Issue": "issue",
    "Sub-issue": "sub_issue",
    "Company": "company",
    "State": "state",
    "Submitted via": "submitted_via",
    "Tags": "tags",
    "Company response to consumer": "company_response",
    "Timely response?": "timely",
    "Consumer complaint narrative": "complaint_what_happened",
}


def main() -> None:
    run_date = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(os.environ.get("CCDB_DIR", DEFAULT_DEST))
    archive = dest / "complaints.csv.zip"
    if not archive.exists():
        raise SystemExit(f"{archive} is missing — run 02_download.py first")

    out_path = dest / "frame_2025.jsonl"
    products = set(FRAME_PRODUCTS)
    per_product: Counter[str] = Counter()
    per_issue: Counter[str] = Counter()
    kept = scanned = 0
    # Deliberately unbounded field size: some narratives are very long, and csv's default limit
    # raises mid-file, which would truncate the frame silently if it were caught and ignored.
    csv.field_size_limit(1 << 31)

    with zipfile.ZipFile(archive) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(members) != 1:
            raise SystemExit(f"expected exactly one CSV in the archive, found {members}")
        member = members[0]
        print(f"reading {member} from {archive}")

        with zf.open(member) as raw:
            stream = io.TextIOWrapper(raw, encoding="utf-8", newline="")
            reader = csv.DictReader(stream)
            missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise SystemExit(
                    f"the archive is missing expected columns {missing}. Found: {reader.fieldnames}"
                )
            with out_path.open("w", encoding="utf-8") as fh:
                for row in reader:
                    scanned += 1
                    if scanned % 2_000_000 == 0:
                        print(f"  scanned {scanned:,}, kept {kept:,}", flush=True)
                    date = row["Date received"]
                    if not (WINDOW_MIN <= date <= WINDOW_MAX):
                        continue
                    if row["Product"] not in products:
                        continue
                    narrative = (row["Consumer complaint narrative"] or "").strip()
                    if not narrative:
                        continue
                    rec = {v: (row[k] or "").strip() for k, v in COLUMNS.items()}
                    rec["complaint_what_happened"] = narrative
                    fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
                    per_product[rec["product"]] += 1
                    per_issue[rec["issue"]] += 1
                    kept += 1

    digest = hashlib.sha256()
    with out_path.open("rb") as fh:
        while chunk := fh.read(1 << 20):
            digest.update(chunk)

    api_total = read_json("frame.json")["frame_total"]
    delta = kept - api_total
    # A few hours separate the bulk export from the API index, so exact equality is not expected.
    # A LARGE gap means the filter is wrong, which would invalidate the frame.
    if abs(delta) > 0.01 * api_total:
        raise SystemExit(
            f"local frame {kept:,} vs search API {api_total:,} — a {delta:+,} gap is too large to "
            f"be re-index drift. The filter does not select what PROTOCOL.md section 2 declares."
        )

    _, cdigest = write_json("frame_local.json", {
        "run_date": run_date,
        "rows_scanned": scanned,
        "frame_rows": kept,
        "api_frame_total": api_total,
        "delta_vs_api": delta,
        "per_product": dict(per_product.most_common()),
        "per_issue": dict(per_issue.most_common()),
        "frame_file": str(out_path),
        "frame_file_sha256": digest.hexdigest(),
    })

    log("03_filter", run_date, [
        f"scanned **{scanned:,}** rows in the bulk archive",
        f"frame rows kept: **{kept:,}** (search API independently reported {api_total:,}; "
        f"delta {delta:+,}, {abs(delta) / api_total:.3%})",
        "per product: " + " · ".join(f"{k} {v:,}" for k, v in per_product.most_common()),
        f"issue buckets present: {len(per_issue)}",
        f"`{out_path.name}` sha256 `{digest.hexdigest()}` (kept outside the repo)",
        f"`out/frame_local.json` sha256 `{cdigest}`",
    ])


if __name__ == "__main__":
    main()
