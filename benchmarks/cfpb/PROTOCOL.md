# AT-43 — pre-registration

**Frozen 2026-08-09, before any narrative was read.** Everything in §1–§7 was decided in advance.
§8 is the only section written after seeing a result, and it may not change §1–§7.

**Disclosure of what the author had seen when freezing this.** Aggregate counts only — the `product`,
`issue` and `has_narrative` bucket counts reproduced in §2, obtained from `size=0` API queries. No
narrative text of any kind. The counts in §2 were copy-pasted from the output of those queries in the
same session, per the project's rule that a number may not enter a document any other way.

**Disclosure of contamination.** The author of this protocol and of the gold marks has read
`src/earshot/extract_lexicon.py` — the extractor's cue vocabulary — earlier in the same session. This
cannot be undone and is not claimed to be. §5 states what is done to bound it and what remains
uncontrolled.

---

## 1. The question, and the grain it is asked at

`src/earshot/evals.py:198-200` keys extraction on `(conversation_id, signal_type)`. The published
synthetic recall of **0.681 (496 / 728)** therefore answers exactly one question:

> Did the extractor fire the correct signal type *somewhere in this document*?

Not spans, not counts, not confidence calibration. The CFPB benchmark asks the **identical** question,
because asking a different one and putting the two numbers side by side is the defect
`working-agreements.md` §1 calls out — two numbers that sound comparable and are not is worse than one
number.

So: one CFPB narrative = one document, marked with the subset of the four `SignalType` values it
expresses. `{churn_intent, financial_distress, complaint_escalation, life_event}`.

**Metrics, all reported per panel and per signal type, always with integers:**

- `strict_recall` **(primary)** = gold-positive `(document, type)` pairs the extractor fired the *same
  type* on / gold-positive pairs. Identical to the question `evals.py` asks.
- `any_type_recall` **(declared secondary)** = documents the extractor fired *anything* on / documents
  the gold marked positive for *anything*.
- `false_positive_rate` = extractor firings on gold-**negative** pairs / gold-negative pairs
- Panels are **never pooled.** A rate computed across a uniform panel and an enriched panel describes
  neither population.

The secondary metric is declared now, in advance, because of one **known taxonomy disagreement**: our
extractor files job loss under `financial_distress` (cue `f-job`), while a marker working from the
construct definitions records it as a `life_event` — and as distress too, when the money consequence is
stated. Where those diverge, strict recall records a miss even though the reader saw the sentence. The
gap between the two numbers is the size of that class of disagreement, and it separates *"the reader
did not see it"* from *"the reader saw it and called it something else"* — different defects with
different fixes, which one pooled number hides.

`MARKING-GUIDE.md` is deliberately **not** adjusted to match the extractor's taxonomy. Doing so would
be authoring the answer key from the tool under test, which is the exact objection AT-43 exists to
close.

## 2. Sampling frame — metadata only, never text

Filtering on words our own lexicon knows would guarantee the answer. That is the demo tautology in
`working-agreements.md` §3. So sampling touches CFPB's own metadata fields only — `product`, `issue`,
`date_received`, `has_narrative` — and never the narrative.

**Pinned window: `date_received` 2025-01-01 to 2025-12-31.** A complete calendar year, recent, and
closed — so it is not churning under a live re-index.

**A restriction that must be published, not buried.** A genuinely uniform draw from all 2025
narratives is **74.7% credit-reporting disputes** (912,757 of 1,222,052). Those are letters about
credit bureaux, not conversations between a bank and its own customer, and this entry does not claim
to read them. Drawing uniformly over that population would measure a genre nobody claimed, so the
frame is restricted — **by product metadata, declared in advance** — to complaints a retail bank's own
customer makes about their own account:

| Product (included) | 2025 narratives |
|---|---|
| Checking or savings account | 51,448 |
| Credit card | 41,517 |
| Mortgage | 14,029 |
| Vehicle loan or lease | 11,685 |
| Student loan | 10,874 |
| Payday loan, title loan, personal loan, or advance loan | 7,805 |
| Prepaid card | 3,822 |
| **Frame total** | **141,180** |

Excluded, with reasons: *Credit reporting or other personal consumer reports* (912,757) — a dispute
with a bureau, not a bank conversation; *Debt collection* (100,609) — usually a third-party collector,
not the bank's own customer relationship; *Money transfer, virtual currency, or money service*
(64,861) — payment apps and crypto rather than a banking relationship; *Debt or credit management*
(2,645) — debt-settlement firms.

The claim this frame supports is therefore **"uniform within retail-banking complaint narratives"**,
never "uniform over CFPB". Any published sentence says so.

## 3. Two panels, 150 documents

| Panel | n | Draw | What it is for |
|---|---|---|---|
| **A — prevalence** | 100 | Exactly uniform over the 141,180-document frame, seeded | The honest false-positive rate, and the true base rate of our four constructs in unselected complaints |
| **B — recall** | 50 | Enriched by `issue` bucket only (below), seeded | Recall with a denominator worth quoting |

Panel A alone would yield a handful of positives per type, and a recall over n≈5 is exactly the defect
`working-agreements.md` §1 exists to prevent. Panel B buys a usable denominator; the price is that it
is a stacked deck, so **the enrichment factor is computed from Panel A and published beside it.**

**Panel B strata, chosen from `issue` buckets measured within the frame (64 buckets, summing to
141,180):**

| Target type | `issue` buckets | Bucket size | n drawn |
|---|---|---|---|
| `financial_distress` | Problem caused by your funds being low · Struggling to pay mortgage · Struggling to repay your loan · Struggling to pay your loan | 9,338 · 3,159 · 2,287 · 1,392 | 17 |
| `churn_intent` | Closing an account · Closing your account | 6,149 · 3,543 | 17 |
| `complaint_escalation` | Problem with a company's investigation into an existing problem | 3,069 | 16 |
| `life_event` | **none exists** | — | 0 |

Three things about this table are pre-registered *as expectations*, so they cannot be presented as
discoveries afterwards:

1. **An `issue` bucket is a label, not a mark.** It says what the complaint was filed under, not what
   language it contains. The gold mark decides; the bucket only raises the odds of finding one.
2. **"Closing an account" will frequently be the *bank* closing the customer's account** — a
   de-banking complaint, which is the opposite of churn intent. We expect the churn stratum to convert
   poorly, and that is a finding about CFPB metadata, not about our reader.
3. **`life_event` has no metadata handle at all.** CFPB has no bucket for bereavement, divorce,
   redundancy or new parenthood. Its recall rests on whatever appears naturally across both panels. If
   its denominator is small, it is **reported as small** and never pooled into a headline rate.

**Draw mechanism, exactly uniform and reproducible.** The frame is extracted from the **bulk
archive** (`complaints.csv.zip`, checksummed and committed as a SHA-256), sorted into one canonical
order by numeric `complaint_id`, and indexed into by a seeded RNG. Uniformity is therefore arithmetic
over a complete local file, and depends on nothing about how a service pages or orders results. Seed,
drawn indices and the resulting `complaint_id` list are all committed, so the draw is checkable years
later even as CFPB re-indexes.

## 2a. Amendment log

Changes made to this pre-registration after it was frozen. Recorded rather than silently rewritten;
**both entries below were made before any narrative text was read**, so neither could have been
chosen to steer a result.

- **2026-08-09 — the draw moved from the search API to the bulk archive.** As frozen, §3 sampled by
  fetching one day at a time from the search API. Two API limits then fired, both caught by the
  scripts' own guards rather than discovered afterwards: a whole-bucket fetch returned 2,000 of a
  2,198-record day, and `frm` paging returned only 1,000 distinct records for that same day. Both
  failures return a *prefix* of a bucket and look like success, which would have made the draw
  silently non-uniform. Sampling from the complete local archive removes the entire class of problem.
  The frame definition, panel sizes, strata and seed are **unchanged**; only the access path changed.
  Step 01 is kept precisely because it is now an *independent* cross-check — the API's frame total
  against the archive's, obtained two different ways.
- **2026-08-09 — a secondary metric was declared** (`any_type_recall`, §1) and a secondary run
  variant added (raw lexicon with the simulated rates off, §4). Both are additions; neither changes
  the primary measurement or the §6 thresholds.

## 4. Wrapping — a decision that moves the number, fixed in advance

The extractor reads `turn.speaker == "customer"` turns, and applies dampeners **per turn**
(`extract.py:71-73`). Wrapping a 900-word narrative as one turn therefore lets a single "my brother"
anywhere in the document damp *every* cue in the document.

- **Primary, pre-registered: sentence-per-turn.** Closest to the per-utterance grain the extractor was
  designed for. Sentence split is a plain regex on `.?!` boundaries with abbreviation guards, applied
  identically to every document, and it is committed code — not a judgement call per narrative.
- **Sensitivity check, also published: whole-document-as-one-turn.** If the two differ materially,
  that is a real property of the extractor and it goes in the write-up.

Both runs use the *same* configured `offline_miss_rate` and `offline_false_fire_rate` as the pipeline
that produced the published synthetic number, so the comparison is like-for-like.

CFPB redactions (`XXXX`) are left **exactly as published**. Repairing them would be editing the test
set.

## 5. Marking — the protocol, and what it does not fix

- `MARKING-GUIDE.md` is written and committed **before** the sample is drawn, and derives each
  construct from `src/earshot/schema.py` and the submitted brief — from what the construct *means*,
  never from what our cues match. Its worked examples are invented, not taken from the sample.
- All 150 documents are marked **before the extractor is run even once**. Ordering is proved by commit
  sequence: marks land in one commit, the first extractor run in a later one, and `out/results.json`
  records the SHA-256 of the gold file it scored.
- Every positive mark cites the verbatim span that triggered it, so a reviewer can disagree with a
  specific string rather than with a verdict.
- **Second marker:** a separate Opus instance blind-marks a random 30 of the 150 from
  `MARKING-GUIDE.md` alone, without the extractor's lexicon and without the first marker's marks.
  Cohen's κ is reported and every disagreement is adjudicated in writing before either mark set meets
  the extractor.

**What this does not fix, stated rather than managed:**

- The first marker has read the extractor's cue vocabulary (see the disclosure above).
- The second marker is a **model instance, not a second human.** AT-43's acceptance criterion asks for
  a second person. This is a documented substitution and every published sentence says
  "second-marked by an independent model instance", never "independently verified by a second
  reviewer". Ravi selected this option knowingly on 2026-08-09 to avoid blocking the measurement; a
  human re-mark of the same 30 before 2026-09-07 would upgrade the claim.
- The second marker runs with repo file access and cannot be truly sandboxed from
  `extract_lexicon.py`. It is instructed not to open it, and its returned rationales are checked for
  cue-shaped language. That is a mitigation, not a guarantee.

## 6. Interpretation, fixed now so it cannot be chosen later

Panel B **strict** recall, sentence-wrapped, against the published synthetic **0.681 (496 / 728)**:

| Result | Reading | Consequence |
|---|---|---|
| **≥ 0.50** | The reader holds up on real language | Work 3 (regrounding the corpus lexicon in CFPB phrasing) is **not needed**. Publish the pair; go to the reviewer queue. |
| **0.30 – 0.50** | Partial | Publish the per-cue fire table. That table *is* the input to work 3 if it is ever run. |
| **< 0.30** | Collapse | Work 3 has a measured reason rather than a speculative one, and moves ahead of the queue UI. |

**The strict/any-type gap routes the follow-up work, and that routing is fixed now.** A low strict
recall with a *high* any-type recall means the reader finds the sentences and mislabels them — a
taxonomy problem, fixed by moving cues between types, and **not** a reason to reground the corpus
lexicon. A low strict recall with an equally low any-type recall means the reader genuinely cannot see
real phrasing, which is what work 3 exists for. Only the second reading sends work 3 ahead of the
reviewer queue.

**A gap between the synthetic and CFPB numbers is expected and is not, by itself, a failure.** On synthetic data a
"planted signal" is a fragment drawn from a pool the cues partly cover by construction; on CFPB a mark
is *any* expression of the construct, including phrasings no cue was ever written for. The synthetic
number is an easier question. This sentence is here so it cannot be written for the first time after
seeing a disappointing result.

**Genre mismatch is a live alternative explanation, declared now.** CFPB narratives are written,
retrospective, third-party-scrubbed, and every one is already an escalation to a regulator. The
extractor was built for spoken call turns and live chat. A low number may measure genre rather than
reading quality. The per-cue fire table is what distinguishes the two, so it is published either way.

## 7. Freeze rules

- **No edits to `extract_lexicon.py` or `extract.py` until this benchmark publishes.** Otherwise the
  benchmark becomes tuning — `working-agreements.md` §1, "never tune until it wins".
- **n is fixed at 150.** No adding documents after seeing results, no re-drawing, no discarding a
  narrative for being unfair.
- Nothing here touches anything upstream of a published figure. `RECALL_BAND` and every synthetic
  number are untouched.
- Any number that appears in §8 or in `README.md` is copy-pasted from the output of a script in
  `steps/`, in the session that wrote it.

## 8. Results

*Not yet run. This section stays empty until steps 01–04 have executed.*
