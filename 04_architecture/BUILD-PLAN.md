# BUILD PLAN — Ear on Every Call

**Status:** first pass, opened 2026-08-09 on branch `build/ear-on-every-call`.
**Anchored to:** the finalized Track A submission *"Ear on Every Call"* sent to the Genesis Committee 2026-07-24 (`Ear-on-Every-Call-Idea-Overview.docx`). That document is the contract with the committee; where this plan and that document differ, the difference is recorded in §10 and must be a deliberate, stated refinement — the submission explicitly reserved the right to refine ("some details may differ a little").

**Scope of this pass:** *what* gets built and in *what order*. Task-level dates are deliberately absent; sequencing and gate-shape are here because the three demo dates are externally frozen and drive scope, not because tasks have been scheduled yet.

---

## 1. The locked use case, stated precisely

A **conversation signal layer**: batch-reads 100% of customer conversations (calls-as-text, chats, complaints), extracts signals with evidence, accumulates them into a **standing per-customer memory that re-scores as new conversations arrive**, and serves one ranked, queryable feed that several teams read at once. A human decides every action; the system never contacts a customer.

**The wedge, said honestly.** Reading a single call and tagging sentiment/intent/compliance risk is commodity — Observe.AI, CallMiner, NICE, Verint, Cresta all ship it. We do not claim that part. What none of them keep is a **customer-level memory that accumulates and re-scores across conversations, channels, and time**. They score the call and archive it; we remember the customer. Everything in this build plan exists to make that one claim measurable.

**Why this framing matters and must not drift.** This repo's own blind rubric judging scored the earlier version of this idea (C61) as top-of-pool on buyer value but a *trap on originality* — "demos like a call-analytics vendor pitch, and that category is saturated" ([03_selection/meeting-doc-2026-07-15.md](../03_selection/meeting-doc-2026-07-15.md)). The submitted version repairs that by moving the wedge from detection to memory. If the build drifts back toward "we detect distress in calls," the entry reverts to the version that was already judged a loser. **Every demo beat and every headline number must be about accumulation, not detection.**

---

## 2. What we are actually measured on

Official weights: Zenon impact 25 · technical depth 25 · feasibility & production readiness 25 · originality 15 · presentation 10 — plus an AI judge scoring engineering quality (evals, reproducibility, accuracy/cost/latency evidence).

| Axis | The artifact that earns it | Where it's built |
|---|---|---|
| Technical depth 25 | Per-stratum recall breakdown, calibration, memory ablation, sensitivity analysis | Stage 4, 5 |
| Feasibility & production readiness 25 | HITL everywhere, thin integration surface, cost/latency table, PII+retention story, failure-recovery moment, recorded fallback | Stage 3, 6, 7 |
| Zenon impact 25 | Named first-dollar path on a live engagement, not just the horizontal story (§9) | Stage 7 (narrative), evidenced by Stage 5 numbers |
| Originality 15 | The memory-vs-baseline experiment, and only that | Stage 1, 5 |
| Presentation 10 | The three-conversation accumulation moment, rehearsed and recorded | Stage 1, 7 |
| AI judge (engineering) | One-command reproducibility, seeded determinism, pinned prompt/model versions, real cost accounting | Stage 0, 5 |

**Reading of the table:** originality is the smallest official weight but the largest *risk*, because it is the axis on which this idea has already been killed once. It is bought entirely by one experiment. That experiment is therefore the highest-priority engineering object in the build, ahead of any UI.

---

## 3. The one experiment that carries the entry

> **Memory vs. Forgetting.** The identical extractor, on the identical corpus, with the identical thresholds — run twice. Once with the per-customer ledger and re-scorer in the loop. Once with each conversation scored alone and then archived. Report the difference.

Three engineering rules follow, and they are non-negotiable because each one is a way this experiment can be dishonest:

**Rule 1 — the baseline must be strong and fair.** Same model, same prompt, same signal taxonomy, same thresholds. The *only* ablated variable is cross-conversation state. A strawman baseline (weaker model, worse prompt, keyword matching) invalidates the entire entry, and it is the first thing a technical judge will probe.

**Rule 2 — the corpus must not rig the result.** If every seeded arc is written so that no single conversation is diagnostic, memory wins by construction and the number means nothing. The corpus carries **difficulty strata** (§5, C1) and every headline metric is reported **per stratum**. Memory must be shown to *also* win or tie on the strata where the baseline should do well — otherwise we have not built a better system, we have built a differently-biased one.

**Rule 3 — the win must survive parameter changes.** Decay half-lives, corroboration bonuses, and thresholds are config, not magic numbers, and a sensitivity sweep shows the memory advantage is not an artifact of one lucky tuning. Expect the question.

---

## 4. Design rules that apply everywhere

1. **Ground truth is authored before the text, never inferred from it.** Deterministic Python builds the plan (who, which trajectory, which conversation carries which planted utterance, on what date); generation only writes prose around that plan. The answer key never comes from a model.
2. **The re-scoring math is plain code, not the model.** The submission promises this explicitly. It is what makes the core logic testable, deterministic, and reproducible — and it is a direct answer to the AI judge's engineering-quality axis.
3. **Every stage is independently demoable.** No stage may leave the system in a state where there is nothing to show. This is forced by having one builder on top of full client utilization, and by an Aug 24 gate that carries two sprints.
4. **Runs with zero API keys.** A deterministic offline extractor ships as a first-class provider, not a stub. Model access is currently unavailable (§8, R1); the pipeline, the evals, and the demo must not be hostage to it.
5. **One command reproduces every number in the README.** Seeded, cached, pinned.
6. **A human is in front of every action, and the system never contacts a customer.** Stated in the submission; enforced in code by there being no outbound surface at all.

---

## 5. System components

### C1 · Synthetic corpus generator
Multi-channel conversation corpus with seeded ground truth. Synthetic-only, per competition rules.

- **Entity model:** customers (tenure, products held, segment), accounts, transactions, conversations (channel = call transcript · chat · complaint), agents.
- **Trajectory model:** each customer is assigned a latent arc — `churn_intent`, `financial_distress`, `complaint_escalation`, `life_event`, or `none` — that unfolds across N conversations spanning weeks or months.
- **Difficulty strata** — the anti-rigging device:
  - **S1 · SINGLE** — one conversation carries a decisive signal ("I'm closing the account next week"). The per-call baseline *should* catch these. Memory must not lose them.
  - **S2 · CUMULATIVE** — no single conversation crosses threshold; only the accumulation does. This is where memory wins, and the utterances must be *honestly* weak, not artificially mute.
  - **S3 · DECOY** — remarks that look like signals but aren't (venting that resolves, a customer describing someone else's situation, rhetorical frustration). Drives false-positive rate.
  - **S4 · NULL** — clean customers with no trajectory. Drives specificity.
- **Ground-truth record per seeded signal:** customer id · conversation id · signal type · intended strength · exact span of the planted utterance · date the signal became actionable · realised outcome (churned / went delinquent / resolved / none). Outcomes are what make lead-time measurable.
- **Realism budget:** disfluency, ASR-style transcription error, agent turns and hold/IVR noise, compliance boilerplate, and a majority of conversations that are genuinely about nothing. Without noise the extraction task is trivial and every downstream number is worthless.
- **Rigging-validation pass:** an automated check that S2 arcs really are sub-threshold conversation-by-conversation under the baseline, and that S1 arcs really are catchable alone. A corpus that fails this check is a bug, not a result.

### C2 · Extraction
Conversation in → structured signals out, one conversation at a time, stateless by construction.

- Output schema: `signal_type`, `confidence`, `evidence_quote`, character span, turn index, timestamp. Evidence is mandatory — an unquotable signal is discarded.
- Strict JSON, schema-validated, bounded retry on invalid output.
- Response cache keyed on `(conversation_hash, model, prompt_version)` so re-runs are near-free and results are reproducible.
- **Provider abstraction** with three implementations: offline deterministic (ships first), Claude, comparison model. Identical interface, identical prompt contract, so the model comparison is apples-to-apples.

### C3 · Memory ledger + re-scorer — *the heart, pure code*
- Append-only per-customer signal ledger.
- `score(customer, as_of_date) -> {per-category score, contributing evidence chain}`.
- Mechanics that make the accumulation defensible rather than "we added the numbers up":
  - **Time decay** — signals fade on a per-type half-life; a job loss mentioned two years ago is not live risk.
  - **Corroboration** — independent signals of the same type in *different* conversations reinforce super-additively; repetition inside one conversation does not.
  - **Cross-channel weighting** — the same theme in a call, a chat, and a complaint is stronger evidence than three mentions in one channel.
  - **Escalation detection** — the same unresolved issue recurring is its own signal ("third time I've called about this fee").
  - **Confidence weighting** — low-confidence extractions contribute proportionally less.
  - **Threshold crossing** emits a **case** carrying the full evidence chain and the date it crossed.
- Deterministic, no model calls, exhaustively unit-tested. Parameters live in config.

### C4 · Baseline — the ablation
Same extractor, same corpus, same thresholds, no ledger. Each conversation scored alone; a case opens only if a single conversation crosses threshold on its own. Deliberately built to be as strong as it fairly can be (Rule 1).

### C5 · Eval harness
- **Signal recall** at customer level, memory vs baseline, **broken out per stratum**.
- **Precision / false-positive rate** on S3 decoys and S4 nulls.
- **Lead time** — days between the system flagging and the realised outcome date. This is arguably the stronger headline than recall, because it is the business claim in the submission: help was ready *before* the first missed payment.
- **Calibration** — are the confidence scores meaningful, since the accumulator weights by them.
- **Cost** — real token accounting → cost per 1,000 conversations, per model. Reading 100% of conversations is exactly where a judge attacks the economics.
- **Latency / throughput** — batch conversations-per-minute and projected wall-clock for a realistic nightly volume.
- **Model comparison** — Claude vs comparison model through the identical harness.
- **Sensitivity sweep** — does the memory advantage survive parameter perturbation.
- Emits machine-readable results plus a generated Markdown scorecard. One command.

### C6 · Serve + team views
One feed, three lenses over the *same* case objects — Retention (lead), Risk & Compliance, Commercial. Each lens is a filter and a ranking, not a separate pipeline: that identity **is** the horizontal proof, and it must be visibly true.
Reviewer actions: approve · dismiss · route. Dismissals write back to the ledger and suppress recurrence — that write-back is both the HITL evidence and the feedback loop.
Starts as a generated report; upgrades to a minimal web view only if the numbers are already solid. A judge cares more that the numbers are real than that the screen is pretty.

### C7 · Demo
- **The accumulation moment.** One customer, three ordinary conversations weeks apart, none alarming alone; the running score crosses into high risk only after the third — shown side by side with the baseline staying silent through all three.
- **The failure-recovery moment.** *Missing from the submitted plan; adding it.* [PLAN.md](../PLAN.md) names a deliberate failure-recovery beat as the single best anti-slop demo device, and the feasibility axis rewards it. Concretely: a planted decoy that the extractor initially scores as genuine distress, which the accumulator then declines to escalate because corroboration never arrives — and/or a reviewer dismissal propagating back and suppressing a case. The system visibly catches a planted problem and corrects.
- Recorded fallback maintained from the first demo onward, not from Sprint 3.

### C8 · Reproducibility, ops, and the compliance story
- Single-command run; pinned seeds, prompt versions, model ids; committed cache for offline replay.
- README carrying the numbers table, regenerated by the harness rather than typed.
- **PII / retention note** — the submission names the Chief Compliance Officer as co-signer, so the coverage-and-privacy answer ships with the build: synthetic-only data, redaction hook on ingest, an explicit ledger retention and right-to-erasure path, evidence quotes stored as spans into source rather than duplicated text, and no outbound contact surface anywhere in the system.
- Mirror to AWS CodeCommit (the official competition repo) alongside this one.

---

## 6. Build stages

Ordered by dependency and by "what is demoable if everything after this stops."

### Stage 0 · Skeleton
- [ ] Package layout, config system, seeded RNG discipline
- [ ] Provider abstraction + offline deterministic extractor registered as a real provider
- [ ] Data schemas (customer, conversation, signal, ledger entry, case) as typed, validated objects
- [ ] One command runs the whole empty pipeline end to end
- [ ] Test scaffold + lint wired to the existing uv env

### Stage 1 · Thin vertical slice — *the first thing worth showing*
- [ ] ~10 customers, ~30 conversations, hand-shaped arcs across S1/S2/S3
- [ ] One signal family end to end (churn intent)
- [ ] Offline extractor producing real structured signals with evidence spans
- [ ] Ledger + re-scorer with decay and corroboration, unit-tested
- [ ] Baseline path implemented as the ablation
- [ ] Recall printed for both arms, per stratum
- [ ] **The three-conversation accumulation moment reproducible on demand**

### Stage 2 · Corpus for real
- [ ] All four strata, at volume
- [ ] Four to five signal families (churn intent · financial distress · complaint escalation · life event · vulnerability)
- [ ] Realism budget applied (noise, disfluency, ASR error, boilerplate, mostly-boring conversations)
- [ ] Outcomes and outcome dates for lead-time measurement
- [ ] Corpus statistics report
- [ ] **Rigging-validation pass** green

### Stage 3 · Real extraction
- [ ] Claude provider live behind the same interface
- [ ] Prompt versioning + strict schema validation + retry
- [ ] Response caching
- [ ] Comparison model through the identical harness
- [ ] Confidence calibration measured
- [ ] Extraction quality measured against seeded spans (did it find the planted utterance, and quote it correctly)

### Stage 4 · Memory depth
- [ ] Decay, corroboration, cross-channel, escalation fully implemented and parameterised
- [ ] All parameters in config; no magic numbers in code
- [ ] Exhaustive unit tests on the scoring function
- [ ] Sensitivity sweep showing the memory advantage is not a tuning artifact

### Stage 5 · Evals complete
- [ ] Per-stratum recall, precision, FP rate
- [ ] Lead-time distribution, memory vs baseline
- [ ] Cost per 1,000 conversations, per model, from real token accounting
- [ ] Latency / throughput and projected nightly wall-clock
- [ ] Model comparison table
- [ ] Generated scorecard; README numbers auto-populated

### Stage 6 · Serve and the horizontal proof
- [ ] Case objects with full evidence chains
- [ ] Three team views as filters/rankings over one feed
- [ ] Reviewer actions: approve · dismiss · route
- [ ] Dismissal write-back suppressing recurrence
- [ ] Minimal web view *only if* Stage 5 is already solid

### Stage 7 · Demo hardening and the pitch
- [ ] Failure-recovery beat built and rehearsed
- [ ] Demo script written to the minute
- [ ] Recording as fallback
- [ ] Two dry runs
- [ ] Path-to-production spec
- [ ] Client one-pager + Zenon-impact narrative (§9)
- [ ] PII/retention note finalised

---

## 7. Gate shape

The three demo dates are frozen (Genesis Committee, 2026-07-29 and 2026-08-07). Sprint 1's demo was downgraded to a check-in and folded into a **combined Sprint 1+2 demo on 2026-08-24**; Sprint 3 is 2026-09-07.

| Gate | What must be true |
|---|---|
| Sprint 1 check-in (2026-08-10, 15 min) | Plan locked; Stage 1 running with real numbers on screen; roadblocks named (§8) |
| Combined Sprint 1+2 demo (2026-08-24) | Stages 0–5 landed, Stage 6 usable. The accumulation moment, the memory-vs-baseline table, and cost/latency all real |
| Sprint 3 demo (2026-09-07) | Stage 6 complete, Stage 7 done, recorded fallback, path-to-production |

**Consequence of the combined gate, and the reason for the stage ordering above:** the submitted sprint plan is a waterfall — corpus and extraction in Sprint 1, memory and reviewer screen in Sprint 2 — which leaves nothing end-to-end demoable if the first sprint slips, and it already has. It is also internally inconsistent: it asks for the three-conversation accumulation scenario to be rehearsed in Sprint 1 while placing the re-scorer that makes accumulation possible in Sprint 2. This plan resolves both by pulling the ledger and re-scorer forward into the thin slice — they are cheap deterministic code — and pushing the reviewer UI right.

---

## 8. Risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | **No model API access yet.** Requirements were requested by the committee on 2026-07-24; keys are not available on the build machine as of 2026-08-09 | Offline deterministic provider ships as a first-class implementation so every stage, eval, and demo runs with zero keys. Named as the roadblock at the check-in, with the specific ask: Claude API, comparison-model API, and confirmation of whether Bedrock is the intended route given the AWS stack |
| R2 | **Corpus rigs the result** — memory wins by construction | Difficulty strata, per-stratum reporting, automated rigging-validation pass |
| R3 | **Strawman baseline** invalidates the originality claim | Same model, same prompt, same thresholds; only cross-conversation state is ablated; documented as an ablation, not a competitor |
| R4 | **Originality attack** — "this is CallMiner with a database" | The per-stratum S2 numbers and the side-by-side silent baseline *are* the rebuttal. Rehearsed as a demo beat, not left to Q&A |
| R5 | **Solo capacity** on top of full client utilization | Thin-slice-first ordering; every stage independently demoable; UI deferred behind numbers |
| R6 | **Economics attack** — reading 100% of conversations is expensive | Real token accounting from Stage 3; batch-not-realtime is a deliberate design choice and is argued as one; cost per 1,000 conversations reported next to accuracy |
| R7 | **Demo depends on a live API call** | Cached responses committed; recorded fallback maintained from the first demo |

---

## 9. Zenon impact — the gap to close

The submission is written horizontally (banks, card issuers, lenders, credit unions, insurers, wealth). That is right for the capability story and wrong, alone, for a 25%-weighted axis scored on *Zenon's* business. This repo already holds the first-dollar path: the Barclays collections engagement is live, is measured on roll-rate, carries a revenue-share model, and the buyer-lens judge scored this idea 5/5 there ([02_ideas_v2/judging-buyer.md](../02_ideas_v2/judging-buyer.md)). Western Alliance and the HOA bank-side surface are the named transfers.

**Task, deferred to Stage 7 narrative work:** name the first engagement and the specific number it moves, without narrowing the capability claim to one client. Horizontal in what it is, specific in where the first dollar comes from.

---

## 10. Open decisions

1. **Deltas from the submitted document.** Two so far, both refinements the covering email reserved room for: (a) the re-scorer moves into Sprint 1 rather than Sprint 2 (§7); (b) a failure-recovery beat is added to the demo (§5, C7). Neither changes what was promised. Log further deltas here.
2. **Comparison model identity** — pending API access (R1).
3. **Web view or generated report** for the three team views — decided at the Stage 5/6 boundary on the evidence of whether the numbers are solid.
4. **CodeCommit mirroring** — when, and whether this repo or a fresh one is the source of truth for competition submission.
5. **Team split** — single-threaded until discussed; the stage boundaries in §6 are already cut to be parallelisable (corpus · extraction+evals · memory+views) if that changes.
