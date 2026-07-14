# Grounded Track (T14) — day-1 use cases + combined pitches

**Status: 2026-07-15 — drafted per `reground-brief.md`, then red-teamed by a 3-lens independent panel (SaaS-minded-leadership judge · founding chief architect · skeptical buyer replaying the v2 critique) and reworked per the adjudicated verdicts (§3). Lock decision with Ravi (T12).**

This file is deliverable 2 of the re-grounding pass: the resurrected first-order use cases with **day-1 stories** (work at a client with zero agents in production), and the **combined pitches** — one grounded doer workflow + exactly one second-order differentiator — that are the likely build candidates. The differentiator answers "why is this not just SaaS"; the doer answers "why would my client pay this quarter." Tiers and the full two-horizon concept text live in `north-stars.md` (v3); evidence lives in `01_research/finance.md` and `00_sources/zenon-client-context.md`.

## 1. Resurrected grounded use cases (day-1 stories)

Format: persona · trigger · story · artifact · buyer · dollar path · runs-on. All finance-first scope. Freshness tags from `backlog.md`.

### R-001 — Collections case worker (Barclays; F2)

Collections case handler working a delinquent-account queue. *Trigger:* UK delinquency deteriorating at record pace (FICO Apr 2026: 2-missed-payment accounts +16.3% YoY). *Story:* the agent sequences contact timing/channel/tone per account within Reg-F/Consumer-Duty policy, detects distress signals mid-conversation, freezes contact, escalates to the handler with the full case file. *Artifact:* governed case file per account. *Buyer:* head of collections & recoveries (live Zenon engagement). *Dollar path:* recovery-rate/deflection analogs (TrueAccord 96% no-human resolution, ~15% cost savings; Salient >$1B processed, 60% handle-time reduction) — no audited cost-to-collect benchmark exists, stated honestly; the demo's seeded simulation generates its own before/after. *Runs on:* case-management exports, contact logs, policy documents — plus transcripts Barclays' GenAI contact-centre summarization already produces. Team review note stands: demo must lead with live case-sequencing, not detection.

### R-004 + R-005 — HOA cash application + lien workflow (WAB; F2/F1)

Lockbox exceptions specialist, Alliance Association Bank ops. *Trigger:* daily lockbox file lands with unmatched/partial/ambiguous remittances; downstream, delinquent dues need notice-stage sequencing toward board-ready lien packets. *Story/artifact/buyer/dollar/runs-on:* see N-004's day-1 story (`north-stars.md`) — this pair is its substrate; R-005 cards together with R-004 (shared account data, strict human-approval gate on lien recommendations per team review). Bank-side white space verified: no HOA-specialist bank advertises AI in the lockbox→reconciliation→reporting chain; $124.2B annual assessments.

### R-002 — Collections conduct verifier (Barclays/Lendmark; F1/F2)

Collections QA lead. This is N-001's day-1 story (`north-stars.md`): replays 100% of collector decisions (human + dialler + rules) against Reg-F/Consumer-Duty policies-as-code; catches the missed vulnerable-customer escalation; artifact = Mills-Review-ready exception report + examiner pack. Runs on transcripts/contact logs that exist today. Team risk note stands: synthetic-demo honesty + prepared judge answer on messy real data.

### R-009 — KYC/AML alert-disposition QC (Capital One/WAB; F2)

AML QA/quality-assurance officer. *Trigger:* 85-95% false-positive rates industry-wide; investigators disposition thousands of alerts; QA samples a sliver. *Story:* the agent audits dispositions for consistency — catches contradictory rulings on near-identical cases (planted pair in the eval, per team review) without flagging noise. *Artifact:* examiner-ready defensibility memo. *Buyer:* head of FIU/AML ops. *Dollar path:* $25-50 per alert investigation cost; consistency failures are enforcement exposure. *Runs on:* the existing screening tool's alert + disposition exports. Positioning confirmed by team review: QC-of-decisions, not another screener. Natural queue inside N-001's family; DJ Risk & Compliance crossover (R-010) available for originality.

### R-017 / R-027 — Rewards-fraud ring investigation (ampliFI/issuers; F2)

Loyalty fraud analyst. *Trigger:* a redemption-abuse pattern spans accounts; today's tooling is single-signal. *Story:* the agent gathers multi-account evidence across redemption chains (R-027: + card + returns signals), builds the case file, proposes — never executes — suspensions. *Artifact:* escalation-ready case file with connection graph. *Buyer:* loyalty fraud ops. *Dollar path:* unresolved — team review split on loss sizing; rewards-fraud benchmarks are a T7 gate (also N-003 promotion gate 1). *Runs on:* redemption/engagement logs (exist). Compare R-017 vs R-027 side-by-side at selection per review note.

### R-007 — SMB cash-flow-risk ambient monitor (WAB/Huntington; F2)

Relationship manager. Day-1 substrate of N-012 (`north-stars.md`): watches the bank's own SMB transaction streams, flags deterioration weeks before overdraft/covenant breach, drafts evidence-attached outreach. Team review requirement stands: must show the *act* step (investigate → draft → track → escalate) or it dies as a dashboard at T6.

**Not resurrected here:** R-032 (returns fraud — out of finance-first scope), R-013/R-014/R-022 (F3-parked, reasons stand), R-018 (layer-not-pitch rule stands — it became mandatory card furniture).

## 2. Combined pitches (the likely build candidates)

Shape per the brief: **one grounded doer + exactly one second-order differentiator.** Each answers the full SaaS-judge checklist; each names its appetite moment in one sentence. Sizing uses METHOD.md's model; all three fit ≤6 build-weeks for 2-3 people.

### CP-1 — "The First Agent Earns Its Job" (N-004: HOA cash-application doer + earned-autonomy machinery) — anchor: Western Alliance

- **Doer:** HOA lockbox cash-application exception worker (R-004), with the lien-packet workflow (R-005) as the demonstrated second queue on paper.
- **Differentiator:** the autonomy-graduation controller — supervised by default, promoted per case-class on Wilson-bound evidence (n≥100), CUSUM-demoted on drift. This is the "why not just SaaS": HighRadius sells matching; nobody sells *earned, revocable* autonomy as the product.
- **Day-1 story:** N-004's, verbatim (`north-stars.md`). Zero agents presupposed — this pitch *introduces* the client's first agent, and the graduation machinery is precisely the answer to "how would a bank like ours ever trust one?"
- **Appetite one-liner:** autonomy promoted live on accumulated evidence, then revoked on a planted slip — "an employee who lost the keys" — the most retellable, lowest-fragility moment in the portfolio.
- **Vision arc to narrate:** Exception-Operations Platform across five regulated queues; the graduation trust-ledger as the compliance spine; N-001 as the audit layer it grows.
- **Judge-checklist posture:** strongest on user story, runs-on (file-in/file-out), infrastructure (none beyond a container + LLM API), guardrails, evals (the harness IS the control surface). Weakest on: bank-side dollar impact (T7 bottom-up estimate — **now a pre-pitch blocker**, and the answer must price the *delta of earned autonomy over HighRadius's 95% touchless*, not just the queue cost — SaaS-judge's hardest question); the matching substrate is F3-commodity, so the demo must never lead with the happy path (kill-pass rework, standing).
- **Sizing:** 2M — with the architect's honesty note: the synthetic data is a *relational* linked corpus (remittance ↔ owner master ↔ ledger) and the eval is a seeded *time-series* choreographed so promotion/demotion land on cue — the sizing holds, but that stream-authoring is the week-1 spike, not an afterthought.
- **Week-1 spike (red-team):** build the seeded remittance→ledger stream + the Wilson/CUSUM controller against it; prove promotion crosses n≥100 and drift demotes on schedule.

### CP-2 — "The Governed Collections Case Worker" (R-001 doer + N-001-lite audit ledger) — anchor: Barclays — REWORKED per red-team (2026-07-15)

- **Doer (re-scoped):** hardship-aware collections case worker operating **between contacts, not inside them** — sequences the next contact's timing/channel/tone within policy, runs distress/vulnerability detection on **completed-contact transcripts** (the post-call summaries Barclays' GenAI pipeline already produces), freezes the case before the next contact fires, escalates with the full file (R-001). *Rework rationale — two lenses independently flagged the original "mid-conversation" framing:* it presupposed real-time transcript streaming the client doesn't have (residual v2-style presupposition), and no zero-agent bank puts its first agent inside live contact with possibly-vulnerable customers. Between-contact sequencing keeps humans/diallers on the phone and the agent on the case.
- **Differentiator:** the N-001-lite conformance ledger — decisions recorded/replayable against Reg-F/Consumer-Duty policies-as-code, examiner pack auto-assembled. **Stated substrate on stage (rework): the client's existing human + dialler decisions AND our doer** — the ledger is not a self-licking certifier of the agent we brought; it audits the estate that exists today (N-001's day-1 story) and our doer inherits the same scrutiny.
- **Day-1 story:** R-001's above, with the re-scope. Live engagement + FCA AI Live Testing cohort membership make this the highest Zenon-impact anchor on the board.
- **Appetite one-liner:** the agent reads last night's contacts, freezes a case on a distress signal before today's call goes out, escalates — then the judge picks any prior action (human or agent) and the ledger produces the rule-cited trace in seconds.
- **Vision arc to narrate:** Decision Assurance Stack across the whole automated estate; N-008 closing the loop (find → prove → repair); N-009 as the endgame ("when the customer's agent shows up, the policy envelope is already here").
- **Judge-checklist posture:** strongest on willingness-to-pay (live engagement, regulator-forced timing: FCA collections rules in force since 2026-04-01), dollar path via recovery analogs + QA-coverage delta. Weakest on: no audited cost-to-collect benchmark (withdrawn in fact-check — ROI runs on analogs + seeded simulation, say so before a judge asks); collections-agent category is F2 (Salient proves it, no UK deployment; differentiation = UK/FCA conduct depth + the ledger — a knowledge moat, thin against a motivated incumbent, per the copyability verdict); accountability question must be rehearsed ("who answers to the FCA when a distress signal is missed — show the log line").
- **Sizing (recounted per architect):** the synthetic conversational corpus (transcripts with seeded, gradable distress signals + Reg-F contact patterns) is an honest **L**, not a freebie → **1L + 2M, at the METHOD ceiling.** As originally scoped (live in-call inference) this was NOT-IN-6-WEEKS; the re-scope above is what makes it buildable.
- **Week-1 spike (red-team):** generate 20 synthetic collections transcripts with seeded distress signals; run the detector cold and measure precision/recall — if it can't reliably catch distress without false-freezes, the demo moment gets pre-staged and stated as such.

### CP-3 — "Find, Prove, Repair" (N-008 remediation doer + auditable-proof machinery) — anchor: Barclays / any regulated lender — DESCOPED per red-team (2026-07-15)

- **Doer:** the Remediation & Redress Worker, reframed to any automated decision — the fee-waiver rules-engine bug cleanup: population resolver over messy logs → parallel counterfactual re-decisions → deterministic redress calculator → drafted customer letters + FCA notice → HITL release.
- **Differentiator (re-stated):** the **auditable-proof machinery** — a machine-checkable inclusion/exclusion proof per account, refusal-with-named-missing-field on incomplete snapshots, redress math as policies-as-code an examiner can re-run. That assurance layer is the "why not a Big-4 spreadsheet." *Descope rationale (architect):* the original N-001 detection front-end was the weaker half — slideware framing for "one closed loop"; the defect now arrives **handed in and confirmed**, and the full find→prove→repair loop with N-001 is narrated as chapter two, not built.
- **Day-1 story:** N-008's, verbatim (`north-stars.md`). Zero agents anywhere in the story — the defective system is a rules engine, the installed base is decades deep, and Consumer Duty makes closure non-optional.
- **Appetite one-liner:** "140/140 harmed accounts found, 3 near-misses excluded with proofs, redress exact to the penny, regulator notice drafted — that's a Big-4 team's quarter, done in an afternoon."
- **Vision arc to narrate:** the redress clearing layer of Consumer-Duty/CFPB finance; N-001 in front makes it find→prove→repair; the same engine closes agent mistakes the day the client has agents.
- **Judge-checklist posture:** strongest on dollar impact **when the buyer is live** (remediation is a budgeted, regulator-forced cost center — the rare AI sale with a deadline), evals (authored bug → exact ground truth; refusal-correctness is the failure-handling story), F1 freshness (no agentic remediation product found in any brief or the collision scan), demo robustness (deterministic core — "if it computes in testing, it computes on stage"). Weakest on: **buyer timing** — felt need is episodic; the skeptical-buyer lens flagged "you will, and the engine is reusable" as the v2 disease relocated, so the pitch needs evidence Barclays-scale banks nearly always have a remediation program open (T7: source s166/past-business-review frequency and spend); **skilled-person positioning** — the engine must pitch as tooling *under* the skilled person's signature, not a replacement for it (SaaS-judge's hardest question); synthetic-eval circularity ("perfect recall on your own seeded bug") is answered by the refusal beat + cross-seeding (planter ≠ builder), stated on stage.
- **Sizing:** 2M (confirmed by recount after the descope; the real engineering is the population resolver's provable fuzzy-join — that gets the weeks the detection module gave back).
- **Week-1 spike (red-team):** population resolver against messy synthetic logs with 3 planted near-misses + 8 incomplete snapshots; prove per-account proofs and correct refusals.

### Portfolio note

CP-2 and CP-3 share the Barclays anchor and the N-001 spine — if both advance, they are one client narrative (govern the doer; repair what governance finds). CP-1 diversifies the anchor (WAB) and the failure mode (ops vs conduct). Per the seeded-eval-monoculture rule: whichever leads the finals pitch, lead with the **doer**, publish run distributions, and cross-seed defects (planter ≠ builder, stated on stage).

## 3. Red-team verdicts (2026-07-15) — adjudicated

Three independent lenses, no shared context: **SaaS-minded-leadership judge** (fable — the corrected judge model, firing the checklist questions) · **founding chief architect** (opus — buildability/honesty attack) · **skeptical buyer** (sonnet — replaying Ravi's v2 critique test-by-test). Verbatim reports: review workdir `redteam-cp-verdicts-verbatim.md`. Objections raised by any single lens were treated with minority-veto force (rework, never averaged away). CP-2 and CP-3 above already reflect the reworks.

**Headline: the v2 fatal flaw is substantially fixed.** All three lenses independently confirmed the day-1 stories run on files/logs that exist at zero-agent clients, and that N-002/N-009 are honestly demoted. Two residual presuppositions were caught and fixed in place (CP-2's real-time streaming; CP-2's self-licking ledger substrate).

| | SaaS-judge verdict | Architect verdict | v2-critique replay (a-e) |
|---|---|---|---|
| **CP-1** | **WOULD-PAY** — greenlight; rubric ~84; "the one moment a non-agent-native panel retells correctly" | **BUILDABLE-AS-SCOPED** — the only genuine 2M; rank 1 on week-6 confidence | (a)(c)(e) FIXED · (b) partial (P&L homework) · (d) still-broken (moat = framing + tuned loop, honestly labeled) |
| **CP-3** | **WOULD-PAY, conditional** on a live remediation trigger; rubric ~85 but demoted on buyer timing | **BUILDABLE-IF** (drop detection front-end — applied above); rank 2 | (a)(c)(e) FIXED — cleanest fix of critique (a) · (b) partial (episodic trigger) · (d) still-broken (Big-4 could follow in ~2 months) |
| **CP-2** | **WOULD-LISTEN** — rubric ~71; "won't put my first-ever agent in live contact with vulnerable customers; the piece I'd buy is the ledger" | **BUILDABLE-IF** (kill live in-call inference; corpus is an honest L — applied above); rank 3, highest live-failure risk | (a)(b)(e) FIXED · (c)(d) partial (synthetic proof-of-value; Salient category) |

**Adjudication (main session):**

1. **CP-1 is the consensus lead** — all three lenses ranked it first on their own criteria (buyer logic, build confidence, critique-resistance). Its two gaps are both fixable by us: the bank-side P&L bottom-up estimate (T7, now a pre-pitch blocker) and pricing the earned-autonomy delta over HighRadius.
2. **CP-3 is the strong second** — best dollar story and F1 originality in the set, deterministic demo core, but buyer timing is outside our control; the T7 item (source how often Barclays-scale banks have an open remediation program) decides whether its "this quarter" claim is honest.
3. **CP-2 as re-scoped survives, third** — the Barclays anchor and FCA timing are the portfolio's best willingness-to-pay evidence, but two lenses independently found its original signature moment presupposed infrastructure (real-time streaming) and buyer appetite (first agent in live contact) that don't exist — precisely the v2 disease. Re-scoped to between-contact sequencing it is honest and buildable at the sizing ceiling (1L+2M). Its strongest asset (the conformance ledger over existing human/dialler decisions) is exactly N-001's day-1 story — which argues for CP-2's ledger appearing inside whichever Barclays pitch advances, rather than CP-2 leading.
4. **Copyability is the portfolio-level weakness all three share** (no 6-week moat survives 6-12 months of a motivated incumbent): the honest pitch answer is speed + engagement trust + tuned execution, not defensibility — and the competition scores originality-now, not moat-in-2028. Keep the answer rehearsed; don't overclaim moats.
5. **Rhetorical-leak discipline (skeptical buyer):** the demoted horizon language ("agent-to-agent negotiation," "mandate fabric") must stay quarantined in ONE clearly-labeled vision beat of any live pitch — verbal narration can re-import what the documents excluded.

## Weakest claims & how to verify

1. CP-1 bank-side P&L number — T7 bottom-up estimate, **pre-pitch blocker** (market sized; per-bank impact is not); the estimate must price the earned-autonomy delta over HighRadius-class touchless matching, not just queue cost.
2. CP-2 ROI runs on analogs (TrueAccord/Salient) + seeded simulation — no audited cost-to-collect benchmark exists; the pitch must say so before a judge asks.
3. CP-3 buyer-timing claim ("remediation programs are common") — team domain input flagged by two red-team lenses; source the frequency/cost of UK past-business reviews (s166 spend, PBR prevalence at major banks) before pitch (T7).
4. CP-3 skilled-person positioning — confirm the engine pitches as tooling under the s166 reviewer's signature, not a replacement; get a domain read on whether the FCA would accept machine-generated inclusion/exclusion proofs as working papers (T7/human).
5. R-009 consistency-failure enforcement exposure — anchor to a named enforcement action if one exists (T7).
6. All dated hooks (Mills Review 2026-07-06, FCA rules 2026-04-01, FICO 2026-06-24, Vantaca 2025-10-15) — re-verify the day they enter a deck (standing rule).
