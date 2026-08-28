
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

### 05_score (model arm) — 2026-08-28
- **a second reader arm, PROTOCOL.md section 9** — no published figure was touched, and `out/results.json` was not rewritten. Wrapping: sentence.
- offline-lexicon: **strict recall 0.0357 (4 / 112)**
- offline-lexicon: any-type recall 0.0964 (8 / 83)
- offline-lexicon: false-positive rate 0.0205 (10 / 488)
- offline-lexicon: per type — churn_intent: recall 0.3077 (4 / 13), fp 0.0292 (4 / 137)
- offline-lexicon: per type — financial_distress: recall 0.0 (0 / 21), fp 0.0465 (6 / 129)
- offline-lexicon: per type — complaint_escalation: recall 0.0 (0 / 67), fp 0.0 (0 / 83)
- offline-lexicon: per type — life_event: recall 0.0 (0 / 11), fp 0.0 (0 / 139)
- offline-lexicon: per panel — A: recall 0.0244 (2 / 82) over 100 docs
- offline-lexicon: per panel — B/churn_intent: recall 0.0833 (1 / 12) over 17 docs
- offline-lexicon: per panel — B/complaint_escalation: recall 0.125 (1 / 8) over 16 docs
- offline-lexicon: per panel — B/financial_distress: recall 0.0 (0 / 10) over 17 docs
- model:anthropic/claude-sonnet-4.5@extractor/v1: **strict recall 0.8214 (92 / 112)**
- model:anthropic/claude-sonnet-4.5@extractor/v1: any-type recall 0.9759 (81 / 83)
- model:anthropic/claude-sonnet-4.5@extractor/v1: false-positive rate 0.1598 (78 / 488)
- model:anthropic/claude-sonnet-4.5@extractor/v1: per type — churn_intent: recall 0.3846 (5 / 13), fp 0.0146 (2 / 137)
- model:anthropic/claude-sonnet-4.5@extractor/v1: per type — financial_distress: recall 0.8571 (18 / 21), fp 0.0543 (7 / 129)
- model:anthropic/claude-sonnet-4.5@extractor/v1: per type — complaint_escalation: recall 0.9701 (65 / 67), fp 0.8072 (67 / 83)
- model:anthropic/claude-sonnet-4.5@extractor/v1: per type — life_event: recall 0.3636 (4 / 11), fp 0.0144 (2 / 139)
- model:anthropic/claude-sonnet-4.5@extractor/v1: per panel — A: recall 0.8293 (68 / 82) over 100 docs
- model:anthropic/claude-sonnet-4.5@extractor/v1: per panel — B/churn_intent: recall 0.8333 (10 / 12) over 17 docs
- model:anthropic/claude-sonnet-4.5@extractor/v1: per panel — B/complaint_escalation: recall 0.75 (6 / 8) over 16 docs
- model:anthropic/claude-sonnet-4.5@extractor/v1: per panel — B/financial_distress: recall 0.8 (8 / 10) over 17 docs
- model telemetry — conversations: 150
- model telemetry — model_calls: 150
- model telemetry — prompt_tokens: 188710
- model telemetry — completion_tokens: 11948
- model telemetry — cost_usd: 0.24845
- model telemetry — cost_per_1000_conversations: 1.6563
- model telemetry — p50_latency_ms: 1244.4
- model telemetry — p95_latency_ms: 2212.0
- model telemetry — emitted_signals: 170
- model telemetry — unparsable_replies: 0
- model telemetry — dropped_unknown_type: 0
- model telemetry — dropped_not_verbatim: 5
- model telemetry — dropped_quote_too_short: 1
- model telemetry — dropped_not_customer_turn: 0
- model telemetry — dropped_below_floor: 0
- model telemetry — relocated_quotes: 4
- `out/results-model.json` sha256 `6daf4923974c073714d1d3880d704ea92615cc6678772b423b7707904cd535f8`

### 05_score (model arm) — 2026-08-28
- **a second reader arm, PROTOCOL.md section 9** — no published figure was touched, and `out/results.json` was not rewritten. Wrapping: sentence.
- offline-lexicon: **strict recall 0.0357 (4 / 112)**
- offline-lexicon: any-type recall 0.0964 (8 / 83)
- offline-lexicon: false-positive rate 0.0205 (10 / 488)
- offline-lexicon: per type — churn_intent: recall 0.3077 (4 / 13), fp 0.0292 (4 / 137)
- offline-lexicon: per type — financial_distress: recall 0.0 (0 / 21), fp 0.0465 (6 / 129)
- offline-lexicon: per type — complaint_escalation: recall 0.0 (0 / 67), fp 0.0 (0 / 83)
- offline-lexicon: per type — life_event: recall 0.0 (0 / 11), fp 0.0 (0 / 139)
- offline-lexicon: per panel — A: recall 0.0244 (2 / 82) over 100 docs
- offline-lexicon: per panel — B/churn_intent: recall 0.0833 (1 / 12) over 17 docs
- offline-lexicon: per panel — B/complaint_escalation: recall 0.125 (1 / 8) over 16 docs
- offline-lexicon: per panel — B/financial_distress: recall 0.0 (0 / 10) over 17 docs
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: **strict recall 0.8214 (92 / 112)**
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: any-type recall 0.9759 (81 / 83)
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: false-positive rate 0.1598 (78 / 488)
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per type — churn_intent: recall 0.3846 (5 / 13), fp 0.0146 (2 / 137)
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per type — financial_distress: recall 0.8571 (18 / 21), fp 0.0543 (7 / 129)
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per type — complaint_escalation: recall 0.9701 (65 / 67), fp 0.8072 (67 / 83)
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per type — life_event: recall 0.3636 (4 / 11), fp 0.0144 (2 / 139)
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per panel — A: recall 0.8293 (68 / 82) over 100 docs
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per panel — B/churn_intent: recall 0.8333 (10 / 12) over 17 docs
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per panel — B/complaint_escalation: recall 0.75 (6 / 8) over 16 docs
- model:us.anthropic.claude-haiku-4-5-20251001-v1:0@extractor/v1: per panel — B/financial_distress: recall 0.8 (8 / 10) over 17 docs
- model telemetry — conversations: 150
- model telemetry — model_calls: 150
- model telemetry — served_model: us.anthropic.claude-haiku-4-5-20251001-v1:0
- model telemetry — prompt_tokens: 188710
- model telemetry — completion_tokens: 11948
- model telemetry — cost_usd: 0.24845
- model telemetry — cost_per_1000_conversations: 1.6563
- model telemetry — p50_latency_ms: 1244.4
- model telemetry — p95_latency_ms: 2212.0
- model telemetry — emitted_signals: 170
- model telemetry — unparsable_replies: 0
- model telemetry — dropped_unknown_type: 0
- model telemetry — dropped_not_verbatim: 5
- model telemetry — dropped_quote_too_short: 1
- model telemetry — dropped_not_customer_turn: 0
- model telemetry — dropped_below_floor: 0
- model telemetry — relocated_quotes: 4
- `out/results-model.json` sha256 `1770692e08e86db6fa364ac882bff261d56b306257d823e18b1de225ce65b9a7`

### correction to the two 05_score (model arm) entries above — 2026-08-28

This log is append-only, so both entries stand as written and are corrected here instead.

- **The first entry names the wrong model.** It says
  `model:anthropic/claude-sonnet-4.5@extractor/v1`. Every one of its 150 calls was served by
  `us.anthropic.claude-haiku-4-5-20251001-v1:0`. `ModelExtractor.name` was built from the
  *requested* `model_cfg.model`, and `bedrock.py` substitutes its own default for
  `base.DEFAULT_MODEL` — an OpenRouter slash-form id meaningless to Converse — by design and
  documented in that module. Nothing between the two noticed. Fixed at the source: the reader is
  now named after the model that answered (`ExtractionTelemetry.served_model`), which is recorded
  per call and would show `a+b` if a run ever changed model halfway.
- **The measurement itself is unaffected, and this is checkable rather than asserted.** The second
  entry is the identical run replayed from `artifacts/cache/extractor.jsonl` with
  `EARSHOT_CACHE_MODE=replay` and no credentials. Every figure is identical to the first —
  0.8214 (92 / 112) strict, 0.9759 (81 / 83) any-type, 0.1598 (78 / 488) false positive,
  $0.24845 over 150 conversations, p50 1244.4 ms, p95 2212.0 ms. Only the arm label and the new
  `served_model` field differ, which is exactly what a labelling fix should change.
- **The corrected artifact is `out/results-model.json` sha256
  `1770692e08e86db6fa364ac882bff261d56b306257d823e18b1de225ce65b9a7`.** The first run's artifact
  (`6daf4923...`) was overwritten by the replay; its content is recoverable from this log and from
  git, and it differed only in the two fields named above.
- **Nothing published moved.** `out/results.json` — PROTOCOL.md section 8's offline figure — was
  not rewritten by either run, and the offline arm reproduced 0.0357 (4 / 112) both times.

**Why this is written down rather than quietly fixed.** A published number carrying the wrong model
name is the defect `docs/ops/working-agreements.md` section 1 exists for: two figures that sound
comparable and are not. The first keyed run in this project's history got the number right and the
label wrong, and the label is half of what makes a number mean anything.
