# BUILD PLAN — Ear on Every Call

**Status:** v2, 2026-08-09, branch `build/ear-on-every-call`. v1 revised after three adversarial
reviews (eval integrity · originality collision · build feasibility) — all three landed hits, and this
document is the repair.

**Anchored to:** the finalized Track A submission sent to the Genesis Committee 2026-07-24
([`00_sources/submission-ear-on-every-call.md`](../00_sources/submission-ear-on-every-call.md)). That
document is the contract; the covering email reserved room for refinement. Deltas are logged in §10.

**Scope of this pass:** *what* gets built and in *what order*. Task-level dates are absent by design;
gate shape is present because the demo dates are frozen
([`00_sources/genesis-committee-comms.md`](../00_sources/genesis-committee-comms.md)).

---

## 1. The use case, and the wedge as it must now be worded

A **conversation signal layer**: batch-reads 100% of customer conversations (calls-as-text, chats,
complaints), extracts signals with evidence, accumulates them into a **standing per-customer ledger
that re-scores as new conversations arrive**, and serves one ranked feed that several teams read. A
human decides every action; the system never contacts a customer.

### 1.1 The submitted wording is refuted and must change

The submission says: *"What none of them keep is a customer-level memory that accumulates and re-scores
signals across every conversation over time."* As literally worded, that is **false as of 2026-05-06**:

- **Twilio Conversation Memory** went GA 2026-05-06, marketed as a persistent, identity-resolved,
  cross-channel per-customer profile — *"persistent, contextual and continuous across every channel."*
  It owns our vocabulary.
- **MorganAsh MARS** ships a standing per-customer vulnerability rating ("like a credit score, but for
  vulnerability") that combines multiple weak indicators and is monitored over a product lifetime — so
  accumulate-and-re-score is prior art in UK financial services.
- **Segment computed traits** already keep user-level traits current and fire an audience when one
  crosses a threshold.
- **Aveni's own marketing** contains our pitch nearly verbatim: *"A customer showing increasing
  financial pressure across multiple interactions triggers proactive support even if no single
  conversation contains explicit vulnerability statements."* Their product page does not evidence it —
  but a judge reading their site will not know that.

A judge finds all of this in one search. Left as written, we lose originality points to homework we
didn't do.

### 1.2 The claim that survives

> Extracting sentiment, intent and compliance risk from a call is commodity — several vendors do it
> well, and we use it as **input**, not as our contribution. Persisting customer memory is also
> shipped: Twilio's Conversation Memory (GA 2026-05-06) keeps a cross-channel per-customer profile.
> But it **reconciles to current truth** — new observations supersede old ones. That is right for
> personalization and structurally wrong for risk, because three faint distress signals must *sum*,
> not overwrite. And standing vulnerability scores exist (MorganAsh MARS) but are fed by
> human-administered questionnaires, not conversations. What no one ships is the intersection: a
> **risk-weighted signal ledger that never discards a sub-threshold signal, and re-scores earlier
> conversations in light of later ones**, so three individually-unalarming calls weeks apart jointly
> cross a threshold none of them crosses alone.

**Two mechanics now carry the entry, and both are buildable:**

1. **Never-discard.** Sub-threshold signals are retained and remain summable. This is the design
   inversion against Twilio's supersede-and-reconcile, and it is the most defensible sentence we own.
2. **Retro re-scoring.** Conversation #3 changes the *interpretation* of conversations #1 and #2 — a
   signal correctly scored "no action" in March is re-read in July. No vendor evidence was found for
   this. **It must be visible on screen in the demo**, not asserted in prose.

**Standing rule.** This repo's own blind rubric judging killed the earlier framing of this idea as a
competition entry — "demos like a call-analytics vendor pitch, and that category is saturated." If the
build drifts back toward *detection*, we revert to the version already judged a loser. Every demo beat
and every headline number is about **accumulation and retro re-scoring**, never detection.

---

## 2. What we are measured on

Zenon impact 25 · technical depth 25 · feasibility & production readiness 25 · originality 15 ·
presentation 10 — plus an AI judge scoring engineering quality (evals, reproducibility, accuracy/cost/
latency evidence).

| Axis | The artifact that earns it | Stage |
|---|---|---|
| Technical depth 25 | Four-arm ablation, negative controls, uncertainty quantification | 1.5, 4 |
| Feasibility & prod-readiness 25 | HITL, cost/latency, thin integration surface, recorded fallback | 5, 6, 7 |
| Zenon impact 25 | Named first-dollar path on a live engagement (§9) | 7 |
| Originality 15 | Retro re-scoring visible on screen + the never-discard argument (§1.2) | 1, 6 |
| Presentation 10 | The three-conversation accumulation moment, rehearsed | 1, 7 |
| AI judge (engineering) | One-command repro, run manifest, seeds, published miss rates | 0, 1.5 |

Originality is the smallest weight and the largest risk — it is where this idea has already been killed
once, and where a live vendor collision exists. It is bought by one experiment and one demo beat.

---

## 3. The experiment that carries the entry

**v1 designed a two-arm test that the eval review judged fundamentally circular.** Three separate
circularities, all now fixed:

| Circularity found | Fix adopted |
|---|---|
| Difficulty strata were defined *by reference to the baseline's decision function*, and the "rigging-validation pass" regenerated any arc where the baseline succeeded — selection on the dependent variable, dressed as a control | Strata are now **generative**: total arc evidence mass is split across k conversations by a Dirichlet draw, and strata are labelled from the **generation parameters**. The share of arcs that turn out single-call-detectable becomes a **reported corpus statistic**, not an enforced invariant. The rigging pass is demoted from gate to diagnostic |
| The re-scorer's mechanics are a near-inverse of the generator's trajectory model, written by the same author — the scorer is fit to the data-generating process by construction | **Negative controls** (§3.3) plus a **held-out generator config**: scorer parameters frozen before seeing a corpus generated under different arc dynamics, channel mix, and prose style |
| "Identical thresholds" across an accumulating sum and a per-conversation max is not identical — it is a scale gift | **Equal alert budget** replaces shared thresholds (§3.2) |

### 3.1 Four arms, not two

The v1 baseline was the weakest possible ablation. The ladder is now:

1. **Stateless-max** — each conversation scored alone; customer score = max. *(Note honestly: any
   customer-level score already implies an aggregator, so even this arm has a trivial memory. Say so.)*
2. **Dumb ledger** — unweighted sum of signals per customer. No decay, no corroboration, no channel
   weighting. **If this ties the full ledger, every mechanism in C3 is decoration and technical depth
   is unearned.** This is the arm that keeps us honest.
3. **Long-context** — last N conversations concatenated into one prompt, no ledger, no scoring math.
   *This is the arm a judge will actually ask about.*
4. **Full ledger** — decay + corroboration + cross-channel + escalation + retro re-scoring.

Plus a **per-mechanism ablation** of arm 4: each mechanism off one at a time, and cumulative.

### 3.2 Equalising the arms

- Never report a single operating point. Sweep thresholds; report **ROC and PR with AUC for every arm**.
- Headline at **equal alert budget** — the same flagged-customers-per-1,000-per-month, because a review
  team's capacity is the real constraint. Report at 1 / 2 / 5 / 10%.
- Calibrate each arm's score to P(outcome) on a **dev split**, then threshold both at the same
  probability on a **locked test split**. That is the only defensible reading of "identical thresholds."
- Add **accumulator-targeted decoys**: customers who accrue several weak corroborating signals across
  channels and months and never experience the outcome. v1's decoys only tried to fool the extractor.

### 3.3 Negative controls (all four are cheap and all are required)

- **Time-shuffle** — permute conversation order within a customer. If the memory advantage survives,
  decay and escalation do nothing and "memory" is just "more text."
- **Outcome-shuffle** — permute outcomes across customers. Recall and lead-time must collapse to chance.
- **Volume confound** — report score vs. conversation-count correlation, and recall on high-volume nulls.
- **Held-out generator config** — as above.

### 3.4 Primary metric

Move the headline off "did we detect the seeded signal" (authored, therefore circular) and onto
**outcome prediction**, where the outcome is drawn stochastically from latent state so neither arm is
handed the answer:

- **AUC-PR on outcome prediction**, per arm.
- **Detection-lead survival curve** — fraction of outcome customers detected ≥ D days before the
  outcome, D swept, never-detected censored, over *all* outcome customers in both arms. Reported in
  conversations-before-outcome as well as days, because days are an authored artifact.
- Prevalence-invariant reporting: FPR/recall plus a **PPV-vs-prevalence curve** anchored at a realistic
  portfolio base rate.
- **Uncertainty is not optional**: ≥10 corpus seeds end to end, bootstrap **clustered by customer**,
  paired McNemar on detection and paired Wilcoxon on lead-time. A point estimate from one generator draw
  is not a result. Pre-register the headline metric and operating point before running.

### 3.5 The killer question, and our answer

> *"Your baseline is a single conversation. The real alternative isn't statelessness — it's putting the
> customer's last twenty conversations in one long-context prompt. Did you run that arm, and if the
> ledger doesn't beat it on accuracy, what's left of your originality claim?"*

**Answer:** We ran it. On accuracy it's close — long-context matches at small histories and degrades
past roughly ten to twenty conversations and across channels. **We do not claim an accuracy win over
it.** The ledger wins on three axes we measured: **cost and latency**, because an incremental O(1)
ledger update re-scores the whole portfolio nightly without re-reading every history through a model —
the difference between viable and non-viable unit economics at 100% coverage; **auditability**, because
the score decomposes into a dated evidence chain a compliance officer can inspect and a reviewer can
write back to; and **determinism**, because the math is plain code and reproduces bit-for-bit. If
accuracy ties, the claim is that the ledger is the only *deployable* way to get that accuracy.

*Note: extraction cost is identical across arms — we do not claim a cost win there. The comparison is
ledger-update cost vs. long-context re-read cost per customer per night.*

---

## 4. Design rules

1. **Ground truth is authored before the text.** Deterministic Python builds the plan; generation only
   writes prose around it. The answer key never comes from a model.
2. **The re-scoring math is plain code.** Promised in the submission; it is what makes the core logic
   testable, deterministic, and reproducible.
3. **Never discard a sub-threshold signal.** The design inversion against supersede-and-reconcile.
4. **Retro re-scoring must be observable**, not asserted — the ledger records what a prior conversation
   scored *then* and scores *now*.
5. **Provider and corpus are mechanically separated.** The offline extractor gets its own lexicon file,
   authored in a separate pass with different vocabulary from the corpus generator's fragments, and
   **cannot import the ground-truth plan — enforced by a test that fails if the answer key is
   importable from provider code.** It carries a deliberate, *measured and published* miss rate.
6. **Every stage is independently demoable.** Forced by one part-time builder and a doubled Aug-24 gate.
7. **Runs with zero API keys**, and offline numbers are always labelled `provider=offline-lexicon` and
   never presented as a headline.
8. **One command reproduces every number**, with a run manifest: seed, git SHA, config hash, timestamp.
9. **No outbound surface exists in the system.** HITL is enforced by there being nothing to enforce.

---

## 5. Components

### C1 · Synthetic corpus generator
- **Entities:** customers (tenure, products, segment), accounts, transactions, conversations (call ·
  chat · complaint), agents.
- **Latent trajectories** — `churn_intent`, `financial_distress`, `complaint_escalation`, `life_event`,
  `none` — unfolding across conversations over weeks or months.
- **Generative strata (revised):** total arc evidence mass split across k conversations by a Dirichlet
  draw; strata labelled from generation parameters, never from what the baseline can do. Concentrated
  draws produce single-call-detectable arcs; diffuse draws produce cumulative-only arcs. **Observed
  detectability is measured and reported, not enforced.**
- **Decoys, two kinds:** extractor-targeted (remarks that look like signals — venting that resolves,
  describing someone else's situation) and **accumulator-targeted** (genuine weak signals that
  corroborate across channels and months but never lead to an outcome).
- **Outcomes drawn stochastically from latent state**, with dates — so outcome prediction is a real
  prediction task, not a lookup.
- **Realism budget:** disfluency, ASR-style error, agent turns, hold/IVR noise, compliance boilerplate,
  and a majority of conversations genuinely about nothing. Built as a **template + slot-filler grammar**
  (weighted fragments across strength tiers, deterministic assembly, seeded) — hand-authoring is
  reserved for the three arcs that appear in the demo. Obvious templating in filler is acceptable.
- **Contamination check:** null customers whose filler prose accidentally contains distress language
  corrupt specificity silently. Test for it.

### C2 · Extraction
Conversation in → signals out, stateless by construction. Schema: `signal_type`, `confidence`,
`evidence_quote`, char span, turn index, timestamp. Evidence mandatory — an unquotable signal is
discarded. Strict JSON, bounded retry, response cache keyed on `(conversation_hash, model,
prompt_version)`. Provider abstraction: offline-lexicon (ships first, constrained per Rule 5), Claude,
comparison model.

### C3 · Ledger + re-scorer — *the heart, pure code*
Append-only per-customer ledger. `score(customer, as_of_date) -> {per-category score, dated evidence
chain, per-signal then-vs-now contribution}`.

Mechanisms, each independently ablatable: **time decay** (per-type half-life) · **corroboration**
(independent signals in *different* conversations reinforce super-additively; repetition within one
conversation does not) · **cross-channel weighting** · **escalation on recurrence** · **confidence
weighting** · **retro re-scoring** (the then-vs-now contribution, surfaced). All parameters in config,
no magic numbers, exhaustively unit-tested, deterministic, no model calls.

### C4 · The four arms
Stateless-max · dumb ledger · long-context-N · full ledger. Identical extractor, prompt, corpus, splits.
Built as arms of one harness, not as separate programs.

### C5 · Eval harness
Everything in §3.2–§3.4, plus: extraction span precision/recall against planted spans and the
adjudicated rate of *unplanted* extractions; cost per 1,000 conversations from real token accounting
(and a defensible projection formula — tokens/conversation × published per-token price — so the cost
table exists before keys do); throughput and projected nightly wall-clock. Emits machine-readable
results, a generated Markdown scorecard, and a run manifest. One command.

**Confidence calibration is cut from the Aug-24 scope.** A deterministic extractor's "confidence" is a
constant we chose; a reliability diagram over it is theater a technical judge spots instantly. Replaced
by an **ablation on confidence weighting** (does weighting beat uniform on the same corpus) — same
engineering signal, honest offline, and it survives into the real-model stage.

### C6 · Serve
One ranked case feed with full evidence chains and the retro re-score visible. Reviewer actions:
approve · dismiss · route. **The three team views reduce to one feed plus a table showing the same case
object surfaced under three different rankings** — same horizontal claim, ~10% of the effort. No web
view for Aug 24.

### C7 · Demo
- **The accumulation moment** — one customer, three ordinary conversations weeks apart; the ledger
  crosses at #3 while the stateless arm stays silent through all three, **with the retro re-score of
  conversations #1 and #2 visible on screen**. Per the collision review, this is the one thing no
  incumbent can reproduce.
- **The failure-recovery beat** — an accumulator-targeted decoy that the extractor scores as genuine
  distress and the ledger declines to escalate; and/or a reviewer dismissal propagating back.
- Recorded fallback from **2026-08-17**, not Sprint 3. A bad recording beats a live failure.

### C8 · Reproducibility and compliance
Single command; pinned seeds, prompt versions, model ids; committed cache; per-run results artifact +
manifest; README numbers generated, never typed. PII/retention note (synthetic-only, redaction hook,
retention + erasure path, evidence stored as spans not duplicated text, no outbound surface). CodeCommit
mirror.

---

## 6. Build stages (re-cut)

The feasibility review moved three things, each for a reason worth keeping:

1. **S0 · Skeleton (halved).** Schemas, config, seeded RNG, one command. *Provider abstraction moves to
   S1 — designing three interfaces with zero implementations is speculative work.*
2. **S1 · Thin slice.** ~10 customers, one signal family, offline extractor, ledger + re-scorer,
   stateless arm, the accumulation moment reproducible on demand.
3. **S1.5 · Eval harness skeleton — moved LEFT (was S5).** Recall/precision/lead-time on 30
   conversations, one command. *On the critical path: without it there is no feedback loop for corpus
   work, and the corpus diagnostics are a precondition for corpus authoring, not a final checkbox.*
4. **S2 · Corpus at volume** — now gated by a harness that returns a number the same minute.
5. **S4 · Memory depth + ablations + sensitivity — moved BEFORE extraction.** Pure code, no keys, fully
   in our control, and it is what buys originality. *Do it while blocked.*
6. **S6 · Serve as a generated report** — always a report, never a web view for Aug 24.
7. **S3 · Real extraction — deferred, key-gated, strictly additive.** Runs whenever keys arrive. **The
   demo must be complete without it.**
8. **S7 · Demo hardening** — with the recorded fallback starting 2026-08-17.

**Fix-loop budget.** The sensitivity sweep and corpus diagnostics exist *in order to* come back red.
Each firing means re-authoring arcs or re-parameterising the scorer, then re-running. Run both against
the 30-conversation S1 corpus by **2026-08-14**, when a failure costs hours instead of a weekend. Sweep
scope: 3 parameters × 3 values, not a grid.

---

## 7. Gate shape, and the Aug-24 cut

| Gate | What must be true |
|---|---|
| Check-in **2026-08-10** (15 min) | Plan locked; S1 running with real numbers; roadblocks named, with a date-certain ask on keys |
| Combined S1+S2 demo **2026-08-24** | The minimum demo below, entirely on the offline provider |
| S3 demo **2026-09-07** | Real-model numbers if keys arrived; serve + demo hardening complete |

**Minimum viable Aug-24 demo** — scores on all five axes without a single API call:

- One command regenerates everything from seed → **the three-conversation accumulation moment with the
  retro re-score visible**, stateless arm silent beside it *(presentation, originality)*
- Four-arm comparison + per-stratum breakdown, ~40 customers / ~150 conversations, 2 signal families,
  with the **detection-lead survival curve** as headline *(technical depth)*
- Cost-and-latency table projected from measured throughput and published per-token pricing, clearly
  labelled projected *(feasibility)*
- One slide naming Barclays collections and the roll-rate number it moves *(Zenon impact)*
- Auto-generated README scorecard, pinned seeds, run manifest, committed cache *(AI judge)*

**Cut for Aug 24:** web view · comparison model · confidence calibration · dismissal write-back ·
PII/retention note · path-to-production · client one-pager · CodeCommit mirroring · signal families 3–5.
**Deferred:** all of S3. **Keep decay + corroboration**; cross-channel and escalation only if the
ablation shows they earn their place.

**Rule, written now to avoid a late scramble:** if keys arrive after **2026-08-20**, they are Sprint 3
scope only.

---

## 8. Risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | **No model API access.** Requested 2026-07-24, chased 2026-07-29, still unprovisioned at 2026-08-09 — 16 days elapsed, no ETA | Offline provider ships first-class. **Escalate at the 2026-08-10 check-in with a date-certain ask** ("keys by 2026-08-17 or the entry ships offline-only") — converts a silent risk into a committee-owned one, and costs 30 seconds of a 15-minute slot |
| R2 | **"So the S2 conversations are sub-threshold for your own matcher, which you also wrote?"** — the most likely way this collapses on stage | Mechanical provider/corpus separation (Rule 5) + generative strata + a *published* miss rate. The answer becomes: "it's a lexicon extractor, it misses N% of planted signals, it's the **weaker** arm — and the memory delta holds anyway. Swap in Claude and both arms improve." Turns the biggest liability into the strongest answer |
| R3 | **Vendor collision on originality** (§1.1) — Twilio Conversation Memory GA 2026-05-06, Aveni's marketing carries our pitch | Reworded claim (§1.2) + retro re-scoring on screen. Defend on the demo, not the sentence |
| R4 | **Dumb-ledger arm ties the full ledger** — all the scoring machinery is decoration | Better to find this in week one than on stage. If it ties, cut the mechanisms and re-pitch on auditability + cost + retro re-scoring, which survive regardless |
| R5 | **Corpus authoring is 3–5× underestimated** and is the largest hidden cost — it is a writing problem, not a code problem | Template + slot-filler grammar; cap cumulative arcs; hand-author only the demo arcs |
| R6 | **Economics attack** — reading 100% of conversations | Projection formula built before keys; batch-not-realtime argued as a deliberate choice; ledger-update vs long-context re-read cost is the honest comparison |
| R7 | **Solo capacity** on top of full client utilization | Thin-slice-first; every stage demoable; the cut list in §7 already applied |

---

## 9. Zenon impact — the gap to close

The submission is written horizontally, which is right for the capability story and insufficient alone
for a 25%-weighted axis scored on *Zenon's* business. The first-dollar path is the live Barclays
collections engagement — measured on roll-rate, revenue-share model, and the buyer-lens judging in the
ideation phase scored this idea highest there. Western Alliance and the HOA bank-side surface are the
named transfers; grounding evidence is retained in
[`01_research/finance.md`](../01_research/finance.md) and
[`01_research/client-ai-state-map.md`](../01_research/client-ai-state-map.md).

**Task (S7):** name the first engagement and the specific number it moves, without narrowing the
capability claim to one client.

---

## 10. Open decisions and deltas from the submission

**Deltas** — all within the refinement latitude the covering email reserved:

1. The re-scorer moves into Sprint 1 (the submitted plan asks for the accumulation scenario to be
   rehearsed in Sprint 1 while placing the re-scorer that makes accumulation possible in Sprint 2).
2. A failure-recovery beat is added to the demo.
3. **The novelty sentence is reworded** (§1.2) — the submitted wording is refuted by Twilio
   Conversation Memory. Capability unchanged; claim made accurate.
4. **The headline metric moves** from seeded-signal recall to outcome prediction + detection lead, and
   the two-arm test becomes four arms. The submitted metric was circular.
5. Sprint-1 "run at full volume" is descoped to a thin slice first; volume arrives at S2.
6. Confidence calibration is replaced by a confidence-weighting ablation until real models are available.

**Open:**

- Comparison model identity — pending keys.
- Whether cross-channel weighting and escalation survive their ablations.
- CodeCommit mirroring: when, and which repo is the submission source of truth.
- Team split — single-threaded for now; stage boundaries are cut to parallelise (corpus · evals ·
  memory) if that changes.
