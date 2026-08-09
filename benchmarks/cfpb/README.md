# AT-43 — benchmarking the extractor on real CFPB complaint narratives

**Self-contained and replicable.** Everything needed to reproduce this benchmark from nothing is in
this folder: the pre-registered protocol, the marking guide, one script per step, the committed
inputs and outputs, and a log of every command that was run against the live API.

The question it answers is the most likely technical objection to this entry on 2026-09-07:

> *Your reader only works because it is reading prose you wrote yourself.*

We run the **existing, unmodified** extractor (`src/earshot/extract.py` + `extract_lexicon.py`) over
real, public-domain consumer complaint narratives from the CFPB Consumer Complaint Database, scored
against a hand-marked gold set, and publish the number with its denominator beside the synthetic one.

---

## Replicate it

Requires the repo's normal environment (`uv sync` at the repo root). Steps are numbered and must run
in order. Every script writes to `out/` and appends to `RUNLOG.md`.

```bash
uv run python benchmarks/cfpb/steps/01_frame.py     # frame counts via the search API (cross-check)
uv run python benchmarks/cfpb/steps/02_download.py  # bulk archive, ~1.3 GB, checksummed
uv run python benchmarks/cfpb/steps/03_filter.py    # stream the archive -> the 2025 frame
uv run python benchmarks/cfpb/steps/04_draw.py      # seeded draw of Panel A + Panel B
uv run python benchmarks/cfpb/steps/05_score.py     # extractor vs gold marks -> the numbers
```

**A second reader arm** (PROTOCOL.md §9, added 2026-08-10). `src/earshot/extract.py` defines an
`Extractor` protocol; the numbers above measure `OfflineLexiconExtractor`, the keyless 26-regex
fallback. The model reader is the protocol's other implementation, and it is scored on the same 150
documents, the same gold marks and the same `(document, type)` grain by the same script:

```bash
EARSHOT_OPENROUTER_API_KEY=... \
  uv run python benchmarks/cfpb/steps/05_score.py --extractor model 2026-08-DD
```

It prints both readers side by side with their integers, writes `out/results-model.json` (leaving
`out/results.json` alone), and records every response into `artifacts/cache/extractor.jsonl` so the
run replays afterwards with `EARSHOT_CACHE_MODE=replay` and no key. **It has never been run** — no
key existed in the environment it was built in, and no figure for it exists anywhere in this repo.

Steps 01–02 need network; 03–05 are entirely local. The bulk archive and the extracted frame live
**outside the repo** (default `c:/tmp/ccdb`, override with `CCDB_DIR`) because they are large; what is
committed is their SHA-256, the 150 drawn documents, and the results. So **step 05 alone reproduces
every published number with no network and no large download** — which is also how a judge in a room
with no wifi replays it.

**Why bulk rather than the API.** The draw has to be exactly uniform over the frame, which means
indexing into a complete, stable list. The search API cannot supply one: its `frm` paging is capped
(a 2,198-record day yields only the first 1,000 distinct records) and its result ordering is not
stable across re-indexes. Both failures return a prefix of a bucket and *look* like success. Step 01
is kept because it now serves as an independent cross-check — the API's frame total against the
archive's, reached by two different paths.

---

## What is in here

| Path | What |
|---|---|
| `PROTOCOL.md` | **The pre-registration.** Sampling frame, panel design, wrapping rule, interpretation thresholds, freeze rules. Committed *before* any narrative was read. |
| `MARKING-GUIDE.md` | How a narrative gets marked, derived from the construct definitions and not from the extractor's cues. Committed *before* any narrative was read. |
| `steps/*.py` | One script per step. Each logs its exact API URLs, response counts, and output hashes. |
| `out/` | Generated, committed: the frame, day counts, the drawn sample, the gold marks, the results. `results-model.json` appears here the first time the model arm is run. |
| `RUNLOG.md` | Append-only log of every run: command, date, key counts, output SHA-256. |

## Reading order for a reviewer

1. `PROTOCOL.md` — what was decided in advance, and what the number is allowed to mean
2. `MARKING-GUIDE.md` — the marking scheme, with its known weaknesses stated
3. `RUNLOG.md` — what was actually run, and when
4. `out/results.json` and the results table in `PROTOCOL.md` §8

## Data provenance and licence

CFPB Consumer Complaint Database, `_meta.license: CC0`. Narratives are published by the CFPB only
with the consumer's opt-in consent and are scrubbed of personal information by the CFPB before
publication (redactions appear as `XXXX`). No client data of any kind is involved. Portal:
<https://www.consumerfinance.gov/data-research/consumer-complaints/> · API:
`https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/` · data-use policy:
<https://www.consumerfinance.gov/complaint/data-use/> (all accessed 2026-08-09).
