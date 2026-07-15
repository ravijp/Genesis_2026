# Stage 5 — Grounding & client mapping (T16, 2026-07-15)

Orchestrator pass. Inputs opened at this stage per protocol: `01_research/client-ai-state-map.md`,
`00_sources/zenon-client-context.md`, `02_ideas/METHOD.md` sizing table + `02_ideas/RUBRIC.md`
(content-neutral machinery only). Verification inputs: verification-V1.md / V2.md.

Per cluster: **tier** · **applicability** (anchor + ≥2 transfers; single-client caps impact at 3) ·
**3-week fit** (surface, runs-on-what, HITL, the number that moves) · **1-yr arc** (POC→P1→P2→handover) ·
**MVP sizing** (per METHOD sizing table; ≤1 L + ≤2 M axes to pass G2). Vision arcs stay as generated
in the raw cards — not restated here.

**Tier counts: 50 PRODUCTION · 10 HORIZON (kept — the ~20%) · 4 PARKED (F3).**
Active-engagement-domain flags (for the ⅓ shortlist cap at Stage 6): collections/Barclays,
HOA-SMB/WAB, lending/Lendmark, loyalty/ampliFI, payroll/ADP.

Client-map frame applied: modal client is S1-S2 (GenAI live, no production agent) → sellable move =
first governed agent on a felt workflow, or QC layer over existing AI decisions. File/export surfaces
fit 3 weeks; core-write or real-time streams do not. Don't out-build S3 clients (CapOne/Visa/MS) on
their own turf — sell assurance, conformance, unautomated queues.

---

## D1 — Exception & dispute repair

**C01 Repair Desk — PRODUCTION** (engagement-domain: none)
- Anchor WAB payments ops; transfers HNB, Barclays, Invesco. 3-wk: repair-queue export in → proposed repairs + before/after diff out (advisory; human applies); runs on daily extracts, no core write. Number: % of repair queue auto-proposed correctly before cut-off.
- Arc: advisory POC → P1 supervised auto-release ≤$ threshold in sandbox → P2 production tolerances → handover w/ eval suite. MVP M: 2 agents, 3 tools, CLI+report, 1 synthetic MT/pacs corpus w/ seeded failures, golden set + auto-scoring.

**C02 Recall Chaser — PRODUCTION**
- Anchor HNB; transfers WAB, Amex, Barclays. 3-wk: investigations case list in → drafted recall/return messages per rail + chase schedule + live case log out; HITL on every outbound. Number: $ recovered per 100 misdirected payments / time-to-first-recall.
- Arc: drafting POC → P1 sends within policy → P2 full chase automation + gpi tracking → handover. MVP M: 1-2 agents, 3-4 tools, single dashboard, 1 corpus (case histories w/ seeded recoverables), golden set.

**C03 Reg E Caseworker — PRODUCTION**
- Anchor CapOne disputes (assurance-over-AI posture); transfers Amex, HNB, Barclays (UK PSR analog). 3-wk: dispute case exports + auth/3DS logs → determination draft + evidence-cited audit pack; human gate on denials. Number: cases/day per analyst; clock-breach rate.
- Arc: co-pilot adjudication POC → P1 auto-resolve clear approvals → P2 provisional-credit automation → handover. MVP M: 2 agents, 4 tools, dashboard, 2 linked corpora (transactions+contact history, seeded fraud patterns), golden + auto-scoring. Watch G2: keep to M.

**C04 Make-Whole Machine — PRODUCTION**
- Anchor Barclays (Consumer Duty redress; UK); transfers CapOne, HNB, Lendmark. 3-wk: error definition + account-history extract → population query + per-account redress calc + QC sample + letter drafts; gates at methodology/batch. Number: cost & weeks per 10k-account remediation vs contractor baseline.
- Arc: single-program POC on one live remediation → P1 payments initiation → P2 program-office platform → handover. MVP M: 2-3 agents, 3 tools, notebook+report, 1 synthetic account-history corpus w/ seeded error population, golden set. UNRESOLVED cost-color claims are non-load-bearing (V1).

**C05 Break Detective — PRODUCTION** ★file-fit
- Anchor WAB (lockbox→recon loop is manual — confirmed white space); transfers Invesco, HNB, ampliFI (rewards recon). 3-wk: nightly unmatched-residual file in → per-break hypothesis + evidence + proposed resolving entry out; human approves. Number: aged-break count / % residual auto-resolved.
- Arc: advisory POC on lockbox exceptions → P1 approved auto-booking → P2 root-cause feed upstream → handover. MVP S/M: 1-2 agents, ≤3 tools, CLI+report, 1 corpus (statements/ledger w/ seeded breaks), golden set. Strongest 3-week-fit shape in D1. Engagement-domain: WAB.

**C06 Agent-Purchase Referee — PRODUCTION (timing-early, honest)** ★convergent ×2
- Anchor Visa (DRN w/ GenAI drafting GA late 2026 — rails-adjacent tooling is what Visa buys) or Amex (ACE agent-error protection live Apr 2026); transfers CapOne, Barclays. 3-wk: synthetic agentic-token dispute corpus → adjudication desk + evidence standard + the procedure manual that doesn't exist yet; HITL on all determinations. Number: % disputes correctly bucketed (consumer-authorized / agent-error / fraud) vs seeded truth; per-dispute cost vs $9-10 baseline.
- Arc: conformance/procedure POC pre-volume → P1 live pilot on trickle volume → P2 issuer desk production as class arrives → handover. MVP M: 2 agents, 3-4 tools, dashboard, 2 linked corpora (mandates+sessions, seeded truth), golden + adversarial. All four rail claims VERIFIED (V1). Volume caveat: Visa agent transactions still "hundreds" (Dec 2025) — sold as preparation, impact math is forward-looking.

## D5 — Expertise capture & transfer

**C07 Last Twelve Months — PRODUCTION**
- Anchor Invesco ops (S0, discovery needed) or WAB ops; transfers HNB, Barclays ops. 3-wk: resolved-case history ingest → first predict-vs-expert agreement score + gap list; expert answers async questions. Number: playbook agreement % on held-out dispositions.
- Arc: corpus POC → P1 live-queue shadow → P2 successor curriculum + oracle → handover (the product IS the handover). MVP M: 1-2 agents, ≤3 tools, notebook, 1 case corpus w/ seeded "expert rules", golden set.

**C08 Ask Marge — PRODUCTION (F2/F3-lean flag from V1)**
- Anchor WAB/HNB exceptions desk; transfers CapOne servicing, Invesco. 3-wk: case-management export → precedent attach + drafted disposition on new cases; analyst confirms. Number: time-to-disposition; consistency (same-pattern-same-outcome) rate.
- Arc: retrieval POC → P1 drafting → P2 compounding precedent + QA drift flags → handover. MVP S: 1 agent, 2-3 tools, CLI, 1 corpus, golden set. Judges: score on the compounding/drift layer, not RAG retrieval (V1 F3-lean note).

**C09 Drift Witness — PRODUCTION** ★convergent ×2
- Anchor Barclays collections (SOPs + case exhaust in a live engagement) or Lendmark (productionization frame); transfers CapOne, HNB. 3-wk: procedure docs + case-system event logs → divergence report w/ benign/control-defeating classification + drafted SOP updates; read-only. Number: procedure-practice gaps found per 100 cases; % full-population coverage vs sample-of-25.
- Arc: witness POC → P1 continuous monitoring → P2 living-SOP maintenance loop → handover. MVP M: 2 agents, 3 tools, report UI, 2 linked corpora (SOP prose + event logs, seeded divergences), golden + auto-scoring. OCC 2026-13 claim VERIFIED. Engagement-domain: Barclays/Lendmark.

**C10 Nightmare Simulator — PRODUCTION**
- Anchor Barclays contact-centre/collections training; transfers CapOne, HNB, WAB. 3-wk: historical case corpus → 20 synthetic hard scenarios w/ seeded ground truth + grading harness; trainers review. Number: time-to-certified-readiness; error rate of sim-trained vs control.
- Arc: scenario-pack POC → P1 counterparty roleplay loop → P2 certification integration → handover. MVP M: 2-3 agents (scenario-gen, counterparty, grader), ≤3 tools, single app view, full-sim corpus (this axis is the L — keep others S), golden set. Synthetic-data-native: competition-friendly.

**C11 Incident Scribe — PRODUCTION**
- Anchor HNB/WAB ops; transfers Invesco, Barclays. 3-wk: bridge chats + tickets from 3 past incidents → living runbook v1 + precedent-match demo on replayed incident. Number: time-to-diagnosis on recurrence.
- Arc: post-mortem POC → P1 in-incident retrieval → P2 first-responder drafting → handover. MVP S/M: 1-2 agents, ≤3 tools, report, 1 corpus (seeded incident patterns), golden set.

**C12 Handoff Guardian — PRODUCTION (weak wow — flag for A5)**
- Anchor WAB/Invesco follow-the-sun ops; transfers HNB, Barclays. 3-wk: EOD queue export → generated handoff w/ ranked risks + deadline math; incoming lead rates usefulness. Number: shift-boundary clock breaches / double-handling.
- Arc: brief-generation POC → P1 interactive interrogation → P2 cross-site triage standard → handover. MVP S: 1 agent, 2 tools, report, 1 corpus, golden set.

## D7 — Machine customer

**C13 KYA Desk — HORIZON** (no roster bank has agent-customer intake demand this quarter; rails VERIFIED but volume "hundreds"). Vision intact; revisit when agent-commerce volume reaches roster banks. If forced to slice: Visa Agentic Registry conformance tooling.
**C14 Mandate Enforcement Bridge — HORIZON** (same timing; Cedar substrate VERIFIED and newly GA — strong later wedge; watch AgentCore Policy adoption at clients).
**C16 Agent Relations Manager — HORIZON** (machine-customer service traffic doesn't exist yet at roster banks; MS MCP endpoints are the earliest watch surface).

**C15 Zombie Agent Hunter — PRODUCTION** ★the D7 day-1 wedge
- Anchor Morgan Stanley (opened MCP endpoints to external agents Jun 2026 — governance layer has a real surface, and it's not competing with their in-house tools); transfers CapOne (agent-native), ampliFI (agentic-browser traffic +7,851% YoY threatens loyalty), Visa. 3-wk: IAM/gateway/credential exports → authority-vs-reality graph + orphan/drift findings + quarterly attestation pack; read-only. Number: % non-human identities with living owner + current mandate; orphans found.
- Arc: inventory POC → P1 graduated response (step-down/quarantine w/ HITL) → P2 continuous attestation → handover. MVP M: 2 agents, 4 tools, dashboard, 2 linked corpora (credential inventory + HR/vendor records, seeded zombies), golden + auto-scoring. 88% incident stat VERIFIED (Gravitee 2026).

## D8 — Inter-institution plumbing

**C17 Fail Fixer Pair — PRODUCTION (borderline: S0 anchor, one-sided-first)**
- Anchor Invesco (back-office ops, needs discovery); transfers MS, custodian segment. 3-wk: settlement-fail exports → own-side investigation + structured evidence pack + machine-precise counterparty notification (transitional one-sided mode); HITL on outbound. Number: fail-resolution days; CSDR penalty $ avoided.
- Arc: one-sided POC → P1 bilateral with one consenting counterparty → P2 A2A negotiation → handover. MVP M: 2 agents, 4 tools, dashboard, 2 corpora (SSIs+instructions, seeded fail causes), golden. T+1 jurisdiction nuance per V1 (US live, EU 2027-10-11).

**C18 Corporate-Action Golden Record — PRODUCTION**
- Anchor Invesco; transfers MS, custodian segment. 3-wk: issuer docs + vendor feeds + MT564s for N events → adjudicated golden record w/ per-field citation + divergence flags; analyst confirms elections. Number: fields correctly adjudicated vs seeded truth; time per event.
- Arc: single-event-type POC → P1 full calendar → P2 counterparty convergence → handover. MVP M: 2 agents, 3 tools, dashboard, 2 corpora (prospectus prose + feeds, seeded disagreements), golden. V1: F2 leaning F3 on "golden record" framing — differentiate on citations + convergence.

**C19 Dialect Keeper — PRODUCTION**
- Anchor WAB (HOA/lockbox vendor file formats — same mechanism, humbler messages) or Visa (rails-adjacent conformance); transfers Invesco, HNB. 3-wk: message/file archive per counterparty → inferred dialect models + repair-queue diagnosis + regression-tested mapping fixes; approval-gated deploys. Number: repair-queue recurrence rate; time-to-fix new dialect break.
- Arc: profiling POC → P1 fix-drafting → P2 auto-maintained mappings + deviation reports → handover. MVP M: 1-2 agents, 3 tools, CLI+report, 1 corpus (seeded dialect quirks), golden + regression harness (the eval story writes itself). Engagement-domain: WAB.

**C20 Night Watch — PRODUCTION** ★file-fit
- Anchor WAB (daily lockbox remittance files + activity reports — the exact surface); transfers Invesco, ampliFI, HNB. 3-wk: file-arrival history → learned rhythms + anomaly investigation (late/short/schema-drift) + machine-precise notifications; runbook execution behind approval. Number: batch-cascade delays; 3am pages avoided.
- Arc: watch POC → P1 benign-runbook execution → P2 counterparty coordination → handover. MVP S/M: 1-2 agents, ≤3 tools, dashboard, 1 corpus (file feed history w/ seeded anomalies), golden + auto-scoring. Engagement-domain: WAB.

**C21 Claims Clerk — PRODUCTION (borderline)**
- Anchor Invesco; transfers MS, broker-dealer segment. 3-wk: settlement data → claimable-event detection + show-your-work claim calcs + evidence packs (filing stays human). Number: claim $ identified in the unfiled tail; aging of claim queue.
- Arc: detection POC → P1 filing → P2 bilateral agent negotiation + netting → handover. MVP S/M: 1 agent, 3 tools, report, 1 corpus (seeded claimable events), golden.

**C22 SSI Drift Sentinel — PRODUCTION (borderline)**
- Anchor Invesco; transfers MS, WAB. 3-wk: internal SSI table + custodian confirms/notifications → drift detection + evidenced update drafts behind HITL (one-sided mode; digests later). Number: fails traced to stale SSIs; last-verified coverage %.
- Arc: one-sided POC → P1 bilateral digests w/ consenting counterparty → P2 continuous verification → handover. MVP S: 1 agent, 2-3 tools, report, 1 corpus, golden.

## D4 — Supervision interface

**C23 Evidence Chaser (vision: Standing Exam) — PRODUCTION**
- Anchor Barclays (FCA-supervised + sandbox posture; Mills Review 2026-07-06 VERIFIED — regulator side is speeding up); transfers HNB, CapOne, Lendmark. 3-wk: exam request list + document estate exports → decomposed request items, fetch/chase tracker, contradiction flags, provenance-lined production set; owners answer tracked tasks. Number: request items closed per week; contradictions caught pre-examiner.
- Arc: single-exam POC → P1 connector coverage → P2 continuous evidence ledger (the Standing Exam vision arc, regulator-signaled white space F1) → handover. MVP M: 2 agents, 4 tools, dashboard, 2 corpora (request list + doc estate, seeded contradictions), golden.

**C24 Signature Support Memo — PRODUCTION**
- Anchor Barclays (SM&CR personal liability — UK-sharp); transfers HNB (302 sub-certs), MS. 3-wk: one attestation + systems-of-record exports → assertion decomposition + evidence-per-assertion memo w/ unverifiable items flagged. Number: % assertions evidenced; signer time saved.
- Arc: one-attestation POC → P1 attestation calendar → P2 continuous basis-refresh → handover. MVP S/M: 1-2 agents, 3 tools, report, 1 corpus (seeded evidence gaps), golden. Personal-pain buyer (the nervous signer) — strong A5 story.

**C25 Cell-to-Source — PRODUCTION**
- Anchor HNB/WAB (call reports); transfers Barclays (COREP/FINREP), Invesco. 3-wk: one return schedule + extracts/EUC spreadsheets → lineage graph + plug/override hunt + per-cell defense pack; read-only. Number: cells traceable to source; EUC plugs surfaced.
- Arc: one-schedule POC → P1 full return → P2 living lineage map + independent recompute → handover. MVP M: 1-2 agents, 3 tools, report, 2 corpora (SQL+spreadsheets w/ seeded plugs), golden.

**C26 Finding-to-Closure — PRODUCTION**
- Anchor HNB or Lendmark (findings registers; productionization frame); transfers Barclays, CapOne. 3-wk: findings register + one remediation plan → milestone decomposition to system-observable conditions + evidence tracker + repeat-finding cross-reference. Number: closure-package assembly time; repeat findings caught.
- Arc: one-finding POC → P1 register-wide → P2 post-closure re-testing → handover. MVP S/M: 1-2 agents, 3 tools, dashboard, 1 corpus (seeded regressions), golden.

## D6 — Explainable decisioning

**C27 Middle-Band Adjudicator — PRODUCTION**
- Anchor Lendmark (consumer lending; WTP caveat — score honestly) or WAB virtual-RM SMB lending; transfers HNB, CapOne. 3-wk: referred-application exports → uncertainty identification + investigation memo + recommend-within-envelope; human decides. Number: middle-band cases/day; decision-memo completeness vs QA standard.
- Arc: memo POC → P1 delegated envelope on low bands → P2 volume production → handover. MVP M: 2 agents, 3-4 tools, dashboard, 2 corpora (applications + docs, seeded resolvable/unresolvable uncertainty), golden + adversarial. CFPB Circular 2026-03 VERIFIED. Engagement-domain: Lendmark.

**C28 Reason-Code Honesty — PRODUCTION** ★assurance-over-AI
- Anchor CapOne (QC layer over existing AI decisions = their map fit); transfers Lendmark, HNB, Amex. 3-wk: decision-engine sandbox API + notice sample → counterfactual re-runs + faithfulness audit report (the artifact that doesn't exist industry-wide, F1 per V1). Number: % notices with unfaithful reasons; segments skewed.
- Arc: sample-audit POC → P1 full-population continuous → P2 in-line generation gate → handover. MVP S/M: 1 agent, 2-3 tools, report, synthetic decision engine + applicant corpus (seeded unfaithful mappings), golden + auto-scoring. Clean eval story; strong originality.

**C29 Underwriter's Witness — PRODUCTION (no roster anchor — impact capped at 3)**
- Anchor: Zenon PE-portfolio insurance segment (posture fit); transfers Amex-adjacent underwriting? weak — treat as segment pitch. 3-wk: submissions + guidelines → deviation map + interrogated acceptance memo. Number: referral files with defensible rationale %.
- Arc: memo POC → P1 desk-wide consistency scan → P2 treaty-audit pack → handover. MVP M: 2 agents, 3 tools, report, 2 corpora, golden.

**C30 Override Ledger — PRODUCTION** ★map-literal fit
- Anchor Lendmark ("delegation-of-authority checks are read-only fits" — client map, verbatim surface); transfers CapOne, Barclays, HNB. 3-wk: override log + decision-engine outputs → real-time elicitation flow (sandbox) + verified justification files + disparity monitor; read-only start. Number: % overrides with falsifiable justification; disparity flags surfaced quarterly→live.
- Arc: retrospective audit POC → P1 at-decision-time elicitation → P2 population monitoring → handover. MVP M: 2 agents, 3 tools, single app view, 2 corpora (decisions + overrides, seeded biased pattern), golden. F1-leaning (V1: nobody instruments the human exception path). Engagement-domain: Lendmark.

**C31 Second-Look Standing Desk — PRODUCTION**
- Anchor CapOne; transfers Lendmark, HNB, Barclays. 3-wk: decline-band exports → re-investigation + comparator files (most-similar approved) + consistency exceptions. Number: recoverable declines found; comparator files per exam request.
- Arc: sample POC → P1 standing desk on band → P2 fair-lending exam artifact → handover. MVP M: 2 agents, 3 tools, report, 2 corpora (seeded recoverables + one seeded inconsistency), golden.

**C32 Time Capsule — PRODUCTION**
- Anchor CapOne (model-version churn; assurance posture); transfers Lendmark, HNB, Amex. 3-wk: forward capsule schema + archivist on decision stream (sandbox) + one backward reconstruction demo. Number: reconstruction hours→minutes; % decisions capsule-covered.
- Arc: capsule POC → P1 backward reconstruction service → P2 portfolio defect queries → handover. MVP M: 1-2 agents, 3 tools, CLI+report, 2 corpora (decision logs + policy versions, seeded defect), golden.

## D9 — Life-event administration

**C33 Wind-Down Clerk — PRODUCTION** · anchor HNB SMB (partnership template); transfers WAB, Barclays business. 3-wk: transaction-history export → discovered obligation graph + ordered dissolution plan + drafted filings (human files). Number: closure months→weeks; forgotten obligations caught. Arc: discovery POC → P1 portal execution → P2 completion certificate → handover. MVP M: 1-2 agents, 3-4 tools, checklist UI, 1 corpus (seeded obligations), golden.
**C34 Keys to the Shop — PRODUCTION** · anchor HNB/WAB SMB; transfers Barclays. F1 (V2). 3-wk: peacetime pack from account data — signatory gaps, guarantee-stranding flags, runbook draft. Number: % sole-signer SMBs with continuity pack. Arc: peacetime POC → P1 rehearsal drills → P2 wartime activation service → handover. MVP S/M: 1 agent, 3 tools, report, 1 corpus, golden.
**C35 Bank Transplant — PRODUCTION (buyer = acquiring bank)** · anchor HNB (acquisition weapon); transfers WAB, challenger segment. 3-wk: 24-mo transaction map → payer/pull inventory + migration plan + parallel-run dashboard (execution later). Number: switch completion days; dropped-payment count = 0. Arc: mapping POC → P1 letter/follow-up automation → P2 full transplant service → handover. MVP M: 1-2 agents, 3 tools, dashboard, 1 corpus (seeded payer relationships), golden.
**C36 After the Fire — PRODUCTION** · anchor HNB/WAB SMB; transfers Barclays, insurer segment. F1, SBA claims VERIFIED (V2). 3-wk (demo-sized): reconstructed claim pack from transaction exhaust on synthetic disaster case + deadline calendar. Number: claim-assembly days; deadline breaches = 0. Arc: reconstruction POC → P1 filing + forbearance drafting → P2 standing disaster-activation product → handover. MVP M: 1-2 agents, 3 tools, report, 2 corpora (transactions + supplier catalogs), golden. Episodic-demand caveat: sold as bank capability, not per-customer subscription.
**C37 Second-State Setup — PRODUCTION** · anchor WAB (multi-state footprint SMBs)/HNB; transfers ADP (payroll accounts). 3-wk: target-state requirements compile → ordered registration graph + tracker + drafted filings. Number: legal-to-work lead time. Arc: plan POC → P1 filing execution → P2 permanent compliance calendar → handover. MVP S/M: 1 agent, 3 tools, checklist UI, 1 corpus, golden.
**C38 Sale Room — PRODUCTION (PE crossover)** · anchor HNB/WAB SMB + Zenon PE practice (sell-side readiness for portfolio add-ons — crossover originality); transfers MS (wealth succession conversations). 3-wk: ledger + doc-store exports → normalized financials + assignability flags + owner-dependence report. Number: diligence-response time; readiness score. Arc: data-room POC → P1 continuous maintenance → P2 sale-side sequence → handover. MVP M: 1-2 agents, 3 tools, dashboard, 2 corpora, golden.
**C39 Life-Event Autopilot — PRODUCTION** · anchor Barclays (UK: Tell-Us-Once/Death Notification Service rails EXIST — V2 jurisdiction correction favors UK anchor); transfers HNB, MS wealth. Empathy.com = named comparator; differentiation = bank-embedded, account-data-native. 3-wk: bereavement case exports → task graph + drafted notifications/retitling paperwork + decision sequencing; bereavement team approves. Number: family task-hours; time-to-estate-settled. Arc: bereavement POC → P1 divorce/redundancy → P2 full case ownership → handover. MVP M: 2 agents, 3-4 tools, case UI, 2 corpora (holdings + tasks, seeded deadlines), golden.

## D11 — SMB finance office

**C40 Polite Bulldog — PRODUCTION (lien sub-component F3 — differentiate on bundle)** · anchor WAB (HOA receivables + virtual-RM frame) / HNB; transfers Barclays business. Levelset/Procore named for lien piece; bundle (behavior-calibrated dunning + forecast feed) is the product. 3-wk: AR ledger + GC payment history → behavior-timed dunning drafts in owner's voice + lien-deadline tracker; owner approves sends. Number: DSO; lien rights preserved %. Arc: drafting POC → P1 auto-send within tone policy → P2 escalation tripwires → handover. MVP S/M: 1 agent, 3 tools, dashboard, 1 corpus (seeded payer behaviors), golden. Engagement-domain: WAB.
**C41 Nightly Money Router — PARKED (F3: Ramp/Brex/Mercury ship this).** Residual if ever revived: bank-embedded variant using the bank's own LOC pricing, no relationship move. Not scored.
**C42 Margin Watchdog — PRODUCTION** · anchor HNB SMB (bank channel); transfers WAB, Barclays business. 3-wk: invoices + bid sheet + PO exports → three-way match + price-creep flags + drafted change orders. Number: margin leakage caught per job; unbilled change orders recovered. Arc: matching POC → P1 dispute/CO drafting → P2 live margin gauge → handover. MVP S/M: 1 agent, 3 tools, dashboard, 2 corpora (seeded creep), golden.
**C43 Fee Forensics / RateWatch — PARKED (F3: contingency fee-audit industry is established).** Residual: autonomous execution of renegotiation/switch. Not scored. Convergence ×2 noted for the record.
**C44 Gap Shopper — PRODUCTION** · anchor HNB/WAB SMB; transfers Barclays business, Lendmark (borrower side). 3-wk: forecast + offers corpus → true-annualized-cost normalization + recommended mix (execution later). Number: financing cost per gap event; MCA avoidance. Arc: comparison POC → P1 solicitation/negotiation drafts → P2 approved execution → handover. MVP S/M: 1 agent, 2-3 tools, report, 1 corpus (differently-shaped offers, seeded true costs), golden. C2FO named adjacent.
**C45 Certified Payroll Ghostwriter — PRODUCTION** · anchor ADP (payroll rails — WTP caveat, score honestly) crossover HNB SMB banking; transfers WAB. LCPtracker/eBacon named adjacents; differentiation = field-hours auto-classification + pre-submission flags + filing. 3-wk: timekeeping exports + wage-determination library → WH-347 drafts + misclassification flags. Number: office-hours per public job; violations pre-caught. Arc: drafting POC → P1 filing → P2 bid-unlock analytics → handover. MVP S/M: 1 agent, 3 tools, report, 2 corpora (hours + determinations, seeded misclassifications), golden. Engagement-domain: ADP.

## D2 — Machine-speed negotiation

**C46 YieldFloor — HORIZON** (buyer is off-roster corporate treasurers; bank-side inversion kills the value prop; keep as vision for treasury-agent era).
**C47 Accord (⊕ First-Call-Right ⊕ Promise-Keeper) — PRODUCTION** ★★ strongest map fit ★convergent ×2
- Anchor Barclays collections (LIVE engagement, revenue-share commercial model, confirmed absence of any collections/servicing agent, FCA sandbox posture); transfers Lendmark, CapOne, HNB. 3-wk: collections case exports + credit policy → I&E from transaction data + full relief-permutation simulation + one pre-approved first-call offer per account + arrangement-tending watchlist; reps deliver, humans gate. Number: cure rate / re-default rate on arrangements; revenue-share upside is direct.
- Arc: offer-engine POC (read-only) → P1 rep-delivered pre-approved offers → P2 negotiation loop + proactive amendment (Promise-Keeper mode) → handover. MVP M: 2-3 agents, 4 tools, dashboard, 2 linked corpora (accounts + transactions, seeded affordability truth), golden + auto-scoring. Salient $25M ARR VERIFIED — category proven, negotiation layer is the differentiated residual (V2). Engagement-domain: Barclays (counts against ⅓ cap).

**C48 MarginMatch — PRODUCTION (borderline: heavy domain, F1 white space)**
- Anchor MS (capital markets; MCP-open posture); transfers Invesco, bank segment. 3-wk: CSA corpus + positions → independent reprice + divergence isolation + drafted dispute notice; ops approves. Number: dispute-resolution days; over-collateral funding cost.
- Arc: reconciliation POC → P1 dispute drafting → P2 counterparty-agent negotiation → handover. MVP M: 2 agents, 3-4 tools, dashboard, 2 corpora (CSAs + marks, seeded divergences), golden. Harvey/Legora proof point is adjacent-domain inference (V2 nuance).

**C49 TermFlow — HORIZON** (two-sided agent presence required; Fazeshift/Daylit own the endpoints today — VERIFIED).
**C50 The Bourse — HORIZON (big swing)** · funding correction applied: Skyfire $9.5M, Oasis $120M — separate companies (V2). The composed rail is F1 white space; revisit as institutional negotiation agents proliferate.

## D10 — Insuring agentic action

**C51 Bindable — PARKED (F3: AIUC ships this — Beazley paper, ElevenLabs policy, 2026-05-15).** Residual: SMB-tier operators AIUC's enterprise motion misses. Not scored.
**C52 PerAct — HORIZON** (needs carrier capacity + payment-path embedding; x402 169M VERIFIED, Crescendo $1.25 VERIFIED; AIUC likely moves down-stack — window may close).
**C53 Recourse — HORIZON** (buyer = insurers/MGAs writing agent liability, nascent this quarter; Braintrust/ClickHouse-Langfuse infra VERIFIED; precedent-base moat argues for early entry — flag for Ravi).
**C54 Telematic — HORIZON** (loss-bureau network effect needs multi-operator adoption; F1 white space, Verisk-seat unclaimed).
**C55 ClawNet — HORIZON (big swing)** (network + mutualized loss pool; the missing-dispute-layer gap is real and VERIFIED — strongest horizon thesis in D10).

## D3 — Guidance for the unadvised

**C56 After-Call Answer Pack — PRODUCTION** ★regulatory tailwind VERIFIED & strengthened
- Anchor Barclays (contact-centre transcripts already flowing + FCA targeted-support regime LIVE 2026-04-06 — V2 correction makes this time-bound first-mover territory); transfers HNB, CapOne. 3-wk: call transcripts + account data → compliance-gated personal guidance packs + suitability-style records; compliance reviews every pack in POC. Number: packs/day; guidance-boundary violations = 0 (eval-able); repeat-call rate.
- Arc: after-call POC → P1 in-call prep → P2 targeted-support permission product (PASS application path) → handover. MVP M: 2 agents (drafter + compliance-rules judge), 3 tools, report UI, 2 corpora (transcripts + accounts, seeded eligibility truths), golden + adversarial (boundary tests). Engagement-domain: Barclays-adjacent (servicing, not collections — arguable).

**C57 Benefits Sweep-and-File — PRODUCTION**
- Anchor Barclays (UK; £24.1bn unclaimed VERIFIED, Policy in Practice FY2025/26); transfers HNB (US analogs), Lendmark (hardship borrowers). Cite-ready number is a gift. 3-wk: consented transaction data + circumstances → eligibility determinations + pre-filled applications (submission human-gated); folds awards into arrangements (pairs w/ C47). Number: £ awarded per 100 hardship customers.
- Arc: eligibility POC → P1 filing + chase → P2 arrears-arrangement integration → handover. MVP M: 1-2 agents, 3 tools, report, 2 corpora (transactions + rules library, seeded entitlements), golden + auto-scoring. entitledto/Turn2us = calculate-only adjacents (named).

**C58 Wrong-Product Whistleblower — PRODUCTION**
- Anchor Barclays (Consumer Duty in force — obligation exists, capability doesn't; V2); transfers HNB, Amex (card products). 3-wk: product book + usage exports → mismatch detection + quantified personal cost + switch letters; remediation team approves. Number: £ customer detriment remediated; complaints pre-empted.
- Arc: audit POC → P1 letter + switch execution → P2 continuous whole-book → handover. MVP S/M: 1 agent, 3 tools, report, 1 corpus (holdings + usage, seeded mismatches), golden. A5 note: "the bank that runs this openly wins the trust war" is a retellable line.

**C59 Big-Decision Second Chair — PRODUCTION**
- Anchor Barclays (transcripts + FCA sandbox; APP losses £576.4m/2025 VERIFIED — updated figure); transfers HNB, MS wealth, CapOne. 3-wk: recorded-call corpus → decision-forming detection + mid-call consequences sheet + coercion checks (offline replay POC; live is P1+). Number: seeded scam/coercion patterns caught; consequences-sheet latency.
- Arc: replay POC → P1 live pilot in sandbox cohort → P2 empowered friction (cool-off grants) → handover. MVP M: 2 agents, 3 tools, single app view, 1 corpus (synthetic calls w/ seeded scams — strong demo theater), golden + adversarial. Real-time latency is the honest technical risk (A3 flag).

**C60 Fiver-a-Month Adviser — PARKED (F3: Cleo/Plum/Chip occupy the positioning).** Residual: bank-embedded bounded-mandate execution depth. Not scored.

## D12 — Early warning & intervention

**C61 Ear on Every Call — PRODUCTION** ★★ Barclays-native
- Anchor Barclays collections (pre-delinquency signals from transcripts they already produce; detection layer commoditized — Observe.AI/CallMiner named — but the case-opening + options-pack + outreach chain is unshipped, V2); transfers CapOne, Lendmark, HNB. 3-wk: transcript corpus + transaction data → signal mining + pre-arrears case files w/ evidence trails + tailored options packs; humans initiate contact. Number: pre-arrears catches that avoid first missed payment; roll-rate delta.
- Arc: mining POC → P1 proactive-contact pilot → P2 full watch-then-repair loop (pairs w/ C47) → handover. MVP M: 2 agents, 3-4 tools, dashboard, 2 linked corpora (calls + transactions, seeded distress arcs), golden + auto-scoring. Engagement-domain: Barclays.

**C62 Main-Street Early Warning — PRODUCTION** ★WAB virtual-RM fit
- Anchor WAB (virtual RM for small-business banking — discovery decks Feb-Mar 2026) or HNB (SMB telemetry); transfers Barclays business, Lendmark. 3-wk: SME account telemetry → seasonality-vs-decay classification + RM briefing packs + pre-modelled options + drafted outreach; RM owns the call. Number: months-earlier detection; cure rate at intervention.
- Arc: watch POC → P1 options modelling → P2 provisioning feed + booked-call loop → handover. MVP M: 2 agents, 3 tools, dashboard, 1 corpus (SME transaction histories w/ seeded deterioration arcs vs seasonal decoys — lovely eval), golden + auto-scoring. Engagement-domain: WAB.

**C63 Postcode Shockwave — PRODUCTION** ★F1, demo-visceral
- Anchor HNB (regional-bank geography makes employer-cluster events legible) or Barclays; transfers Lendmark, WAB. 3-wk: payroll-inflow patterns → employer-level watch + community-event declaration + affected-cohort identification (incl. second-order) + portfolio artifact; humans run the play. Number: days from employer shock to coordinated response; cohort cure rate vs historical one-off handling.
- Arc: detection POC → P1 pre-emptive enrollment + frontline briefings → P2 recovery tracking → handover. MVP M: 1-2 agents, 3 tools, dashboard, 1 corpus (town economy simulation, seeded plant closure — strong synthetic-data story), golden. V2: F1 — no shipped equivalent.

**C64 Last-Door Case Agent — PRODUCTION**
- Anchor Barclays collections (pre-recovery cases in a live engagement) or Lendmark; transfers HNB, WAB. 3-wk: pre-recovery case files + policy/schemes library → exhaustive alternative enumeration + dual-sided modelling + best-alternative dossier + "nothing else was possible" certificate; specialists decide. Number: forced-sale avoidance rate; recovery delta vs repossession.
- Arc: dossier POC → P1 certificate gating → P2 upstream feed from C61/C62 → handover. MVP M: 1-2 agents, 3 tools, report, 2 corpora (cases + schemes, seeded better-alternatives), golden. Engagement-domain: Barclays.

---

## Stage-6 quota inputs

- Pool for judging: **60 clusters** (50 PRODUCTION + 10 HORIZON). PARKED (not scored): C41, C43, C51, C60.
- Portfolio quota at selection: ~80% production / ~20% horizon in the final list; **active-engagement-domain cap ~⅓ of shortlist** — domain-flagged clusters: C05, C09(part), C19, C20, C27, C30, C40, C45, C47, C56(arguable), C61, C62, C64.
- Novelty protection: top-3 novelty outliers auto-advance regardless of aggregate.
- WTP penalty (Ravi): ADP/Lendmark-anchored ideas score lower on POC-path (C45, C27, C30 partially — note in buyer judging).
