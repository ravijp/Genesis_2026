
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
