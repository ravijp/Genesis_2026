# AT-43 — pre-registration

> **Dated note, added 2026-08-31. Nothing below this note has been altered.**
> This protocol cites a synthetic recall of **0.681 (496 / 728)** as the comparison point for the
> CFPB figures (§2, §8, §9). **That figure was measured on a corpus that has since been rebuilt
> twice** — pools widened 2026-08-30, then Phase C's realism rebuild on 2026-08-31 — and it is no
> longer what the shipping corpus produces. The same measurement today reads **0.2285 (617 / 2,700)**
> at n=1,500. The CFPB numbers themselves are unaffected: they are scored against an external,
> unchanged gold set of 150 public narratives and do not touch our corpus. Only the synthetic
> comparison point moved. **`README.md` is the source of record for current numbers.**
>
> This note is additive by design. §1–§7 were frozen before any narrative was read and correcting a
> stale cross-reference inside them would destroy the only thing pre-registration is worth.

**Frozen 2026-08-09, before any narrative was read.** §1–§7 were decided in advance and none of them
has been altered since.

Three sections were added afterwards and are marked as such rather than folded into the frozen text:
**§2a** (amendment log — both entries made before any narrative was read), **§5a** (a contamination
disclosure about the second marker), and **§6a** (a defect found in the marking guide while marking).
**§8** is the results, written after seeing them, and **§9** adds a second reader arm on 2026-08-10.
None of these may change §1–§7, and none does.

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

## 5a. Contamination of the second-marker comparison — disclosed, not managed

**The first marker read the second marker's summary report partway through marking.** It arrived as a
completion notification after 66 of 150 documents had been marked, and it named specific
`complaint_id`s together with the second marker's verdicts on them. Nine of the still-unmarked
documents were among those named.

This is a process failure by the first marker and it is not repairable after the fact. What it means:

- Agreement over the **10** double-marked documents that were marked *before* the report was read is
  independent. Reproduce it with
  `mark.py agree out/gold.jsonl out/gold_second.jsonl --restrict <the 10 ids>`.
- Agreement over the full **30** is **not** independent, and is quoted only with this label attached.

Both are published in §8. The contaminated figure is the higher one, which is exactly why it cannot be
the headline.

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

## 6a. A defect in the marking guide, found during marking

`MARKING-GUIDE.md` §2.3 has a **headline and a bullet list that disagree**. The headline marks "a
problem the customer has raised before and that is still unresolved"; the bullets require an explicit
count, a case reference, a missed callback, a closed complaint, or department ping-pong. Several
documents satisfy the headline and no bullet. Both markers hit this independently.

The first marker read the bullets as near-exhaustive and marked single-contact-with-no-answer as FALSE
(`13467477`, `14812570`, `15401666`, `15339554`, `14947106`, `17832509`, `17201348`). The second
marker read the headline as governing and marked at least `17201348` TRUE. The guide also does not say
what to do when the customer contacted the firm once and received **no answer at all** — its exclusion
only covers being "dissatisfied with the answer".

**Adjudication of the single disagreement (`17201348`): the first marker's FALSE stands** — not
because it is more defensible in isolation, but because six other documents were marked the same way
and changing one would make the gold set internally inconsistent. Per §5 of the guide, where no rule
resolves a disagreement the rule was missing, so this is recorded as a limitation rather than patched
after seeing the result. It does not affect the headline: escalation recall is 0 either way.

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

Run `2026-08-09` via `steps/05_score.py`; primary variant is sentence-per-turn with configured rates.
Every figure below is copy-pasted from that command's output. `out/results.json` carries the rest.

### The headline

| | CFPB (real) | synthetic (published) |
|---|---|---|
| **strict recall** | **0.0357 — 4 / 112** | 0.681 — 496 / 728 |
| any-type recall (secondary) | 0.0964 — 8 / 83 | — |
| false-positive rate | 0.0205 — 10 / 488 | — |

**This is the "collapse" band of §6 (< 0.30), by a wide margin.** The pre-registered consequence
follows automatically: work 3 — regrounding the corpus lexicon in real phrasing — now has a measured
reason rather than a speculative one, and moves ahead of the reviewer queue.

### Per type, with denominators

| signal type | recall | integers | fp rate | integers |
|---|---|---|---|---|
| `churn_intent` | 0.3077 | 4 / 13 | 0.0292 | 4 / 137 |
| `financial_distress` | 0.000 | 0 / 21 | 0.0465 | 6 / 129 |
| `complaint_escalation` | 0.000 | 0 / 67 | 0.000 | 0 / 83 |
| `life_event` | 0.000 | 0 / 11 | 0.000 | 0 / 139 |

**Three of the four signal types scored exactly zero.** Every true positive in the whole benchmark
comes from a single cue, `c-close`.

### Why: the reader is a keyword matcher, and real people do not use its keywords

**24 of the 26 cues never fired on any of the 150 real narratives.** In the primary run only `c-close`
and `c-rival` fire at all (`c-move` fires once under whole-document wrapping). Never fired: `c-move`,
`c-switch`, `c-shop`, `c-exit-fee`, `c-dormant`, `c-notice`, `f-cant-pay`, `f-job`, `f-hours`,
`f-tight`, `f-credit`, `f-late`, `f-date`, `f-bounce`, `f-juggle`, `f-payday`, `e-nth`, `e-callback`,
`e-before`, `e-ref`, `l-bereave`, `l-separate`, `l-move`, `l-statpay`.

The escalation result is the sharpest illustration. 67 of 150 documents were marked as escalations,
often in unmistakable language — *"This is now the ninth time I have been told the same thing"*,
*"I spoke to more than 15 attendants"*, *"I have submitted three appeal letters with no response"* —
and the extractor found **none of them**, because `e-nth` matches only the literal form
`(second|third|…) time I've (called|rung|contacted)`.

**The strict/any-type gap routes the follow-up work, per §6.** Any-type recall is 0.0964 against
strict 0.0357 — both near zero. That is §6's second reading: the reader genuinely cannot see real
phrasing. It is *not* a taxonomy problem that could be fixed by moving cues between types.

### Sensitivity — all four variants

| variant | strict recall | false positives |
|---|---|---|
| sentence + configured *(primary)* | 4 / 112 | 10 / 488 |
| sentence + raw lexicon | 4 / 112 | 5 / 488 |
| whole-document + configured | 4 / 112 | 11 / 488 |
| whole-document + raw lexicon | 4 / 112 | 5 / 488 |

Recall is identical across all four by coincidence of small numbers, not by construction: every true
positive comes from `c-close`, which survives the simulated miss-rate draw in both configured runs.
The variants do differ — the false-positive counts move. **The wrapping question that §4
pre-registered as decisive turned out not to matter at all**, because too few cues fire for dampeners
to have anything to dampen. Most false positives in the configured runs are injected `:false-fire`
noise rather than cue matches; with the raw lexicon only 5 remain.

### The enrichment failed, as expectation 2 in §3 predicted

| | Panel A (uniform, 100) | Panel B stratum | enrichment |
|---|---|---|---|
| `churn_intent` | 10 / 100 | 1 / 17 | **negative** |
| `financial_distress` | 14 / 100 | 4 / 17 | ×1.7 |
| `complaint_escalation` | 50 / 100 | 7 / 16 | **negative** |

CFPB `issue` metadata barely predicts our constructs, and for two of the three it predicts them
*worse* than a uniform draw. The "Closing an account" bucket yielded exactly **one** churn-intent
document out of 17; the rest are the bank closing the customer's account, which §3 recorded in advance
as the expected failure mode. **Panel A is therefore the more informative panel** — the reverse of the
design intent, and the reason both are reported separately rather than pooled.

A second, unplanned observation from Panel A: escalation is present in **50 of 100** uniformly drawn
narratives. People who complain to a regulator have usually complained to the firm first. That is a
property of CFPB, not of bank conversations, and it is one more reason this corpus cannot stand in for
the generator (D-010).

### Inter-marker agreement

| subset | churn | distress | escalation | life event |
|---|---|---|---|---|
| **uncontaminated, 10 documents** | undefined | 1.000 | 1.000 | undefined |
| contaminated, all 30 — *not a headline* | 1.000 | 1.000 | 0.933 | 1.000 |

"Undefined" means neither marker used that type in those 10 documents, so Cohen's κ has no defined
value; reported rather than silently dropped. The uncontaminated subset agreed on 10 of 10 documents
across all four types, with zero disagreements. Read §5a before quoting either row.

### What this does NOT show

- It does not show the extractor is broken **for the corpus it was built for**. The synthetic 0.681
  stands and is unaffected; nothing upstream of it was touched.
- It does not show the accumulation thesis is wrong. This measures the **reader**, not the ledger.
- It is one benchmark, on 150 documents, from one year of one regulator's complaint database, drawn
  from retail-banking products only. Written complaints to a regulator are not calls or chats, and §6
  pre-registered genre mismatch as a live alternative explanation. The per-cue table is what
  distinguishes the two, and it points at cue coverage: a lexicon of 26 literal regexes does not
  generalise off the prose it was written against.

## 9. A second reader arm, added 2026-08-10 — after the results in §8

**Written after seeing §8, and marked as such.** §1–§7 are untouched and this section may not
change them. What it adds is an *arm*, not a question: the same 150 documents, the same committed
gold marks, the same `(document, signal_type)` grain, the same three metrics with the same
denominators, and the same §6 thresholds. Nothing about what the number is allowed to mean moves.

**Why.** §8 measures `OfflineLexiconExtractor`, the keyless 26-regex fallback. `Extractor` in
`src/earshot/extract.py` has always been a protocol with a second intended implementation — a
model — and until 2026-08-10 that implementation did not exist. So §8's 0.0357 describes the
fallback and not the reader this entry says it ships. `src/earshot/extract_model.py` is that
second implementation, and this section is how it gets scored against the same gold set.

**How to run it.** One command, and it needs a key:

```bash
EARSHOT_OPENROUTER_API_KEY=... \
  uv run python benchmarks/cfpb/steps/05_score.py --extractor model 2026-08-DD
```

It prints both readers side by side with their integers, writes `out/results-model.json`, appends
to `RUNLOG.md`, and records every model response into `artifacts/cache/extractor.jsonl` so the
measurement replays afterwards with `EARSHOT_CACHE_MODE=replay` and no key — the same
record-then-replay path the two committed live investigations use. `out/results.json` is not
rewritten, because §8's published artifact belongs to the run that produced it.

**Two deviations from §4, both stated rather than absorbed.**

1. The model arm runs the **pre-registered primary wrapping (sentence-per-turn) only** by
   default; `--wrapping document` runs the other. §4's wrapping question exists because the
   offline extractor applies dampeners *per turn*, so a whole-document turn lets one "my brother"
   damp the document. A model is shown the entire narrative either way and the wrapping changes
   only the grain at which it can cite a turn, so the sensitivity check is far less informative
   here. It is available, not automatic.
2. `rates` has no meaning for a model. `offline_miss_rate` and `offline_false_fire_rate` are
   simulated imperfection knobs on the lexicon; the model arm records `"rates": "n/a"` rather
   than pretending to a setting it does not have.

**What is not claimed.** As of 2026-08-10 this arm has **never been run**. There is no key in the
environment it was built in, no number for it exists in this repository, and none may be written
here, in `README.md`, or anywhere else until it is copy-pasted from the output of the command
above.
