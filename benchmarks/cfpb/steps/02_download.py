"""Step 02 — download the CFPB bulk complaint archive and checksum it.

Why bulk rather than the search API. The draw has to be exactly uniform over the frame, which
means indexing into a complete, stable list. The public search API cannot supply that: its `frm`
paging is capped (a 2,198-record day yields only the first 1,000 distinct records) and its result
ordering is not stable across re-indexes. Both failures are silent -- they return a prefix of a
bucket and look like success. Sampling from a local, complete, checksummed file removes the whole
class of problem, and gives a reviewer one artifact to verify instead of several hundred requests
to trust.

The archive lands OUTSIDE the repository (default `c:/tmp/ccdb`), because it is ~1.3 GB. What
gets committed is its SHA-256, so a replication can prove it read the same bytes.

    uv run python benchmarks/cfpb/steps/02_download.py [run-date] [dest-dir]
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import log, write_json  # noqa: E402

URL = "https://files.consumerfinance.gov/ccdb/complaints.csv.zip"
DEFAULT_DEST = Path("c:/tmp/ccdb")
CHUNK = 1 << 20


def download(dest: Path) -> tuple[Path, int, str]:
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / "complaints.csv.zip"

    with urllib.request.urlopen(URL, timeout=120) as resp:
        declared = int(resp.headers["Content-Length"])
        last_modified = resp.headers.get("Last-Modified")
        if target.exists() and target.stat().st_size == declared:
            print(f"already present at {target} ({declared:,} bytes) — skipping download")
        else:
            print(f"downloading {declared:,} bytes -> {target}")
            got = 0
            with target.open("wb") as fh:
                while chunk := resp.read(CHUNK):
                    fh.write(chunk)
                    got += len(chunk)
                    if got % (64 * CHUNK) < CHUNK:
                        pct = 100 * got / declared
                        print(f"  {got / 1e9:.2f} / {declared / 1e9:.2f} GB ({pct:.1f}%)", flush=True)
            if got != declared:
                raise SystemExit(f"truncated download: {got:,} of {declared:,} bytes")

    size = target.stat().st_size
    if size != declared:
        raise SystemExit(f"size on disk {size:,} != Content-Length {declared:,}")

    digest = hashlib.sha256()
    with target.open("rb") as fh:
        while chunk := fh.read(CHUNK):
            digest.update(chunk)
    return target, size, digest.hexdigest()


def main() -> None:
    run_date = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(os.environ.get("CCDB_DIR", DEFAULT_DEST))
    target, size, sha = download(dest)

    write_json("source_archive.json", {
        "run_date": run_date, "url": URL, "path": str(target),
        "bytes": size, "sha256": sha,
    })
    log("02_download", run_date, [
        f"source `{URL}`",
        f"**{size:,} bytes**, sha256 `{sha}`",
        f"stored outside the repo at `{target}` — only the checksum is committed",
    ])


if __name__ == "__main__":
    main()
