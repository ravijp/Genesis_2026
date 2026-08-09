
### 01_frame — 2026-08-09
- CFPB `_meta.last_updated` **2026-08-09T12:00:00-05:00**, licence `CC0`
- all narrative complaints in window: **1,222,052**
- frame (7 retail-banking products): **141,180** (11.6% of all narratives in window)
- per-product parts sum to 141,180 — matches the frame total
- issue buckets within frame: **64**, summing to 141,180
- Panel B pools: financial_distress 16,176 (draw 17) · churn_intent 9,692 (draw 17) · complaint_escalation 3,069 (draw 16)
- API calls: 14
- `out/frame.json` sha256 `e0f7613aeb8a3d32638be399c3b35319a0f23a5f25b9de27035fd2ecbaa9d164`

### 02_day_counts — 2026-08-09
- counted **365** days; they sum to **141,180**, matching `frame.json`
- busiest day 2025-01-17 at 3,728 records — one request fetches a whole day, so no paging limit is approached
- Panel B strata counted by month: financial_distress 16,176 · churn_intent 9,692 · complaint_escalation 3,069
- API calls this run: 151
- `out/day_counts.json` sha256 `9d8772aab7dfcf469f822c0057f89d65305395935810bc0e04cb13668665fca7`

### correction to 02_day_counts — 2026-08-09

This log is append-only, so the entry above stands as written and is corrected here instead.

- **"one request fetches a whole day, so no paging limit is approached" was wrong.** A whole-bucket
  fetch of 2025-01-16 returned 2,000 of 2,198 records, and `frm` paging returned only 1,000 distinct
  records for the same day. Both were caught by the draw script's own guards, which is the only
  reason the sample was not silently drawn from a prefix of each bucket.
- Consequence: the day-count approach was abandoned entirely. `02_day_counts.py`, `03_draw.py` and
  `out/day_counts.json` were removed; the draw now reads the bulk archive. See `PROTOCOL.md` §2a.
- The 365 day counts did agree with the frame total (141,180) before being discarded, so the
  arithmetic was sound; it was the retrieval that could not be trusted.

### 02_download — 2026-08-09
- source `https://files.consumerfinance.gov/ccdb/complaints.csv.zip`
- **1,411,120,769 bytes**, sha256 `e6183856f536ad4bba3744129efbe2bb4172cf1d150511d9a061259cbc30b02e`
- stored outside the repo at `c:\tmp\ccdb\complaints.csv.zip` — only the checksum is committed

### 03_filter — 2026-08-09
- scanned **16,996,406** rows in the bulk archive
- frame rows kept: **141,180** (search API independently reported 141,180; delta +0, 0.000%)
- per product: Checking or savings account 51,448 · Credit card 41,517 · Mortgage 14,029 · Vehicle loan or lease 11,685 · Student loan 10,874 · Payday loan, title loan, personal loan, or advance loan 7,805 · Prepaid card 3,822
- issue buckets present: 64
- `frame_2025.jsonl` sha256 `230cfb619823629633b71152c5c2f4e2d02efbe30ae0bf051479367f2451ccf5` (kept outside the repo)
- `out/frame_local.json` sha256 `08355779ac83a88b34106778155a4010f0256108495aae960e26d4217c1287a7`

### 04_draw — 2026-08-09
- seed **20260809**, drawn **150** documents from a local frame of 141,180 (Panel A 100, Panel B 50)
- panel pools: A 141,180 · B/financial_distress 16,176 · B/churn_intent 9,692 · B/complaint_escalation 3,069
- replacements: A 0 · B/financial_distress 0 · B/churn_intent 0 · B/complaint_escalation 0
- narrative length chars: min 67, median 921, max 4993
- all 150 complaint_ids distinct
- `out/sample.jsonl` sha256 `dc5b1e49625e35272142da8bb2fdefbdbd59303836b06bbc9b8a74f205951c1d`
- `out/draw_manifest.json` sha256 `af13e836e075df980c5616b727c32a68ec3634499f1c3f0abbeae08526370cbd`
