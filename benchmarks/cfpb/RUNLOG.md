
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

### 04_score — 2026-08-09
- primary (sentence-per-turn, configured rates): **strict recall 0.0357 (4 / 112)**
- any-type recall 0.0964 (8 / 83)
- false-positive rate 0.0205 (10 / 488)
- per type — churn_intent: recall 0.3077 (4 / 13), fp 0.0292 (4 / 137)
- per type — financial_distress: recall 0.0 (0 / 21), fp 0.0465 (6 / 129)
- per type — complaint_escalation: recall 0.0 (0 / 67), fp 0.0 (0 / 83)
- per type — life_event: recall 0.0 (0 / 11), fp 0.0 (0 / 139)
- per panel — A: recall 0.0244 (2 / 82) over 100 docs
- per panel — B/churn_intent: recall 0.0833 (1 / 12) over 17 docs
- per panel — B/complaint_escalation: recall 0.125 (1 / 8) over 16 docs
- per panel — B/financial_distress: recall 0.0 (0 / 10) over 17 docs
- sensitivity — sentence-raw: strict 0.0357 (4 / 112)
- sensitivity — document-configured: strict 0.0357 (4 / 112)
- sensitivity — document-raw: strict 0.0357 (4 / 112)
- cues that never fired on real prose: **24 of 26** — c-move, c-switch, c-shop, c-exit-fee, c-dormant, c-notice, f-cant-pay, f-job, f-hours, f-tight, f-credit, f-late, f-date, f-bounce, f-juggle, f-payday, e-nth, e-callback, e-before, e-ref, l-bereave, l-separate, l-move, l-statpay
- `out/results.json` sha256 `4e47be33d367b6ac502436d6db77457db95fc1c5e661349501635288039f2985`

### correction to the 05_score entry above — 2026-08-09

Append-only, so the entry stands and is corrected here.

- It is headed `04_score` because the script still carried its pre-renumber label. The run itself is
  `steps/05_score.py`; the label is now fixed.
- **Strict recall is identical (4 / 112) across all four run variants, and that is a coincidence of
  small numbers, not a bug.** The variants genuinely differ: false positives are 10, 5, 11 and 5 for
  sentence-configured, sentence-raw, document-configured and document-raw. Every true positive comes
  from one cue (`c-close`), which survives the simulated miss-rate draw in both configured runs, so
  the recall numerator does not move while the FP numerator does.
- Most false positives in the *configured* runs are `:false-fire` entries — noise injected by
  `offline_false_fire_rate=0.08`, not cue matches on real text. Against real prose the genuine cue
  firings are only `c-close` (6), `c-rival` (1-2) and `c-move` (0-1).

### 05_score — 2026-08-10 — regression check after the script grew a second arm

Not a new measurement. `05_score.py` was refactored so a reader can be passed in (PROTOCOL.md
§9), and this run checks the refactor moved nothing. Command:
`uv run python benchmarks/cfpb/steps/05_score.py 2026-08-10`.

- primary (sentence-per-turn, configured rates): **strict recall 0.0357 (4 / 112)** — identical
- any-type recall 0.0964 (8 / 83), false-positive rate 0.0205 (10 / 488) — identical
- per type — churn_intent 0.3077 (4 / 13) · financial_distress 0.0 (0 / 21) ·
  complaint_escalation 0.0 (0 / 67) · life_event 0.0 (0 / 11) — identical
- all three sensitivity variants: strict 0.0357 (4 / 112) — identical
- cues that never fired: **24 of 26** — identical
- `out/results.json` was regenerated and differed from the committed file in exactly one field,
  `run_date`, so it was **restored to the 2026-08-09 version**. The published artifact keeps the
  date it was published on; nothing in it is re-dated by a regression run.
- The model arm has **not** been run. It needs a key, there is none in this environment, and no
  figure for it exists anywhere.
