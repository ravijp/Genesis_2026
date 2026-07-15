# Stage 3 — Merged & deduplicated idea pool (T16, 2026-07-15)

Input: 72 raw ideas (ideas-raw-G1..G6.md, 12 each). Orchestrator-performed semantic dedup.
**Collapse: 8 ideas absorbed into 7 clusters → 64 surviving clusters (11% collapse rate).**
Lighter than the "expect heavy" prior — evidence that Stage-1 direction stratification worked:
overlaps concentrated exactly where assigned directions abut semantically. **Cross-generator
convergence (independent contexts, same idea) noted per cluster — treat as signal, not noise.**

**Anti-slop gate (content-neutral only: chatbot-wrapper / dashboard-only / no-artifact-of-record /
single-prompt-suffices): 0 kills.** The generation prompts required acting agents with artifacts,
so the gate was pre-enforced at generation. No shape preference applied (v1 assurance-lean retired).

Full card text lives in the raw files; this file is the index of record. Seed = most specific member
(kept verbatim as card basis); variants noted, never flattened.

## Merge log

| Cluster | Seed | Absorbed | Rationale |
|---|---|---|---|
| C06 | G1-6 Agent-Purchase Referee | G2-3 Machine Chargeback Desk | Same core: bank-side dispute resolution for agent-initiated transactions. G2-3 adds machine-readable intake/standing, micro-dispute batch-netting, A2A pre-network convergence. **Convergent ×2 (G1, G2)** |
| C09 | G3-4 Drift Witness | G1-9 Drift Auditor | Same core: procedure-vs-practice divergence detection from system exhaust. G1-9 adds living-SOP maintenance, workaround promotion. **Convergent ×2 (G1, G3)** |
| C19 | G2-9 Dialect Keeper | G2-5 Rails Rosetta | Same mechanism (agent-maintained message-dialect mapping w/ regression-tested fixes); domains differ (SWIFT/ISO vs agent-payment protocols). Same generator — no convergence signal. |
| C23 | G3-1 Evidence Chaser | G3-5 Standing Exam | Same problem region (exam evidence production); G3-5 is the natural vision arc of G3-1's near-term slice — merged as one two-horizon card. Same generator. |
| C43 | G5-1 RateWatch | G4-10 Fee Forensics Agent | Same core: statement-level fee audit → drift detection → renegotiation/dispute execution on contingency. G4-10 adds SMB segment + bank-account fees + behavior fixes. **Convergent ×2 (G4, G5)** |
| C47 | G5-3 Accord | G6-8 First-Call-Right Hardship Desk, G6-9 Promise-Keeper | Same core: policy-bounded, individually-tailored arrears relief. G5-3 = negotiation loop; G6-8 = open-banking I&E + one pre-approved first-call offer; G6-9 = daily arrangement tending/pre-breakage amendment (G5-3 has this as re-open trigger). **Convergent ×2 (G5, G6)** |
| C52 | G5-8 PerAct | G5-12 Backstop | Same core: price + bind micro-warranties per agent action/outcome, auto-adjudicate from traces; differ on unit (action vs contracted outcome) and distribution (rail vs vendor-embedded). Same generator. |

Adjacencies noted, NOT merged (genuinely distinct products): G1-2↔C55 (recall on traditional vs agentic rails) · G1-4↔G3-6 (customer redress vs MRA closure) · G1-5↔G2-10 (internal breaks vs inter-institution files) · G4-2↔C39 (business succession vs consumer life events) · G4-8↔G6-6 (SMB treasury vs consumer guardian) · G5-7/G5-10↔C52 (underwrite/monitor vs warrant) · C47↔G6-12 (relief structuring vs pre-recovery exhaustion certificate).

## Surviving clusters (64)

Format: ID · Name (seed; members) — one-line gist. [key claims for Stage-4 verify]

### D1 — Exception & dispute repair in money flows

- **C01 · Repair Desk** (G1-1) — agent repairs STP-fallout wires pre-cut-off within tolerances, auto-releases low-risk, full diff log. [ISO 20022 field structure claims]
- **C02 · Recall Chaser** (G1-2) — owns misdirected/duplicate-payment recovery end-to-end: recall messages per rail, decaying-schedule chasing, gpi status tracking, indemnity drafts. [gpi stop-and-recall mechanics]
- **C03 · Reg E Caseworker** (G1-3) — runs EFT dispute cases against the 10-day/45-day clocks: evidence pull, adjudication, letters, GL, audit pack; human gate on denials. [Reg E deadlines; 146M/$15.3B dispute projection; ~20% first-party fraud]
- **C04 · Make-Whole Machine** (G1-4) — remediation program in a box: population ID, per-account redress calc, letters, payments, returns handling, regulator evidence pack; gates at methodology/batch/out-of-tolerance. [contractor-army cost claims]
- **C05 · Break Detective** (G1-5) — investigates the unmatched recon residual nightly: lineage trace, hypothesis, proposed resolving entry as ready-to-approve package; root-cause clustering. [95%+ touchless cash-app benchmarks]
- **C06 · Agent-Purchase Referee** (G1-6 ⊕ G2-3) — the dispute desk for agent-initiated purchases: reconstructs mandate/consent/session chain, adjudicates consumer-authorized vs agent-error vs fraud, files network format; builds precedent + procedure manual; G2-3 variant adds machine-readable dispute intake for agent principals, micro-dispute netting, bank-to-bank A2A convergence. **Convergent ×2.** [Mastercard Agent Pay, Visa TAP, Amex ACE protection, x402 volume — all load-bearing]

### D5 — Expertise capture & transfer

- **C07 · Last Twelve Months** (G1-7) — year-long agent shadow of a retiring expert's live queue; asks one question per surprising disposition; validated decision playbook with predict-vs-expert agreement score + gap list.
- **C08 · Ask Marge** (G1-8) — precedent oracle over the desk's resolved-case corpus: auto-attaches 3 most similar priors + drafted disposition; overrides become new precedent; drift-from-precedent flags.
- **C09 · Drift Witness** (G3-4 ⊕ G1-9) — full-population procedure-vs-practice divergence detection from system exhaust; classifies benign workaround vs control-defeating shortcut vs stale doc; drafts SOP update or remediation flag. **Convergent ×2.** [OCC Bulletin 2026-13 MRM exclusion claim]
- **C10 · Nightmare Simulator** (G1-10) — generates synthetic hard-case training scenarios w/ seeded ground truth from historical corpus; plays counterparties; grades vs veteran playbook; certifies readiness.
- **C11 · Incident Scribe** (G1-11) — post-incident synthesis into living runbook + in-incident precedent retrieval/first-response drafting.
- **C12 · Handoff Guardian** (G1-12) — writes the shift handoff a veteran supervisor would: ranked risks, deadline math, first-hour plan; learns from breach/double-handling outcomes.

### D7 — The machine customer

- **C13 · KYA Desk** (G2-1) — Know-Your-Agent onboarding case end-to-end: verify attestation chain, parse mandate to enforceable authority, graduated "parole" limits, legacy customer-master mapping. [A2A v1.0 signed agent cards; AP2 60+ orgs]
- **C14 · Mandate Enforcement Bridge** (G2-2) — compiles signed mandates into each legacy system's native limits, continuously audits divergence, chases revocation through every system, signed revocation attestation. [Cedar policy engines]
- **C15 · Zombie Agent Hunter** (G2-4) — reconciles authority graph vs reality graph for non-human identities with payment authority; orphan/dormant/scope-drift detection; graduated response; quarterly attestation pack. [88% orgs agent-incident stat]
- **C16 · Agent Relations Manager** (G2-6) — bank-side machine-customer service desk exposed as MCP/A2A endpoint: real decline diagnosis, authorized fixes, machine-readable remediation, agent-to-agent term negotiation within policy.

### D8 — Inter-institution back-office plumbing

- **C17 · Fail Fixer Pair** (G2-7) — per-institution settlement-fail agents investigate own side, negotiate to shared facts over A2A, jointly-signed break-resolution record + root-cause feed. [CSDR penalties, T+1, A2A 150+ orgs]
- **C18 · Corporate-Action Golden Record** (G2-8) — adjudicates event terms from primary docs vs vendor/custodian feeds w/ per-field citations; converges with counterparty agents pre-deadline.
- **C19 · Dialect Keeper** (G2-9 ⊕ G2-5) — agent-maintained counterparty message-dialect models: diagnose repair-queue hits, draft mapping fix, regression-test vs archive, deviation reports; variant: same layer for agent-payment protocol fragmentation (x402/AP2/ACP/MPP). [protocol traction claims]
- **C20 · Night Watch** (G2-10) — learns per-counterparty file rhythms, investigates anomalies (late/short/schema-drift), executes runbooks under policy, machine-precise counterparty coordination at 3am.
- **C21 · Claims Clerk** (G2-11) — inter-bank fails-claims lifecycle: detect claimable events, compute w/ show-your-work, file to counterparty's claims agent, negotiate within bounds, propose bilateral netting; unlocks unfiled sub-$5k tail.
- **C22 · SSI Drift Sentinel** (G2-12) — continuous bilateral SSI verification via digest exchange; on mismatch traces each side's version to source evidence, executes last-mile internal updates behind HITL.

### D4 — The supervision interface

- **C23 · Evidence Chaser → Standing Exam** (G3-1 ⊕ G3-5) — near-term: decomposes exam request lists, fetches/chases artifacts, consistency-checks, provenance-lined production set. Vision arc: two-sided machine-examinable interface — institution evidence ledger + supervisor query agent with scope negotiation, standing queries replacing exam sieges. [Mills Review 2026-07-06; FCA AI Live Testing dates]
- **C24 · Signature Support Memo** (G3-2) — decomposes attestations into atomic assertions, evidence-checks each, returns signed-basis memo w/ unverifiable items flagged. [SM&CR personal liability trend]
- **C25 · Cell-to-Source** (G3-3) — regulatory-return lineage tracer through the actual production chain incl. EUC spreadsheets; per-cell defense packs; independent recomputation.
- **C26 · Finding-to-Closure** (G3-6) — owns MRA/finding lifecycle: milestone decomposition to system-observable outcomes, continuous evidence, post-closure re-testing, repeat-finding detection.

### D6 — Explainable decisioning at origination

- **C27 · Middle-Band Adjudicator** (G3-7) — investigating underwriter for the grey zone: resolves specific uncertainties, decides within delegated envelope, writes the individually-reasoned decision memo. [CFPB explainability expectation]
- **C28 · Reason-Code Honesty** (G3-8) — counterfactual adverse-action verifier: remediate stated reasons, re-run decision, flag unfaithful explanations, faithfulness audit + in-line gate.
- **C29 · Underwriter's Witness** (G3-9) — insurance referral-desk sidecar: maps risk vs guidelines, interrogates acceptance rationale vs file evidence, writes the acceptance memo, cross-desk consistency scan.
- **C30 · Override Ledger** (G3-10) — intercepts every human override at decision time: structured elicitation, immediate verification of checkable claims, permitted-override classification, continuous disparity monitoring.
- **C31 · Second-Look Standing Desk** (G3-11) — re-examines declines in the reviewable band + builds comparator files vs similarly-situated approvals; individual-level consistent-treatment evidence.
- **C32 · Time Capsule** (G3-12) — as-of-date decision archiving (forward) + reconstruction (backward); defense memos; portfolio model-defect queries.

### D9 — Life-event administration

- **C33 · Wind-Down Clerk** (G4-1) — full business-dissolution task graph discovered from transaction history; files, closes, cancels in dependency order; "fully dead" certificate. [closed-book UNVERIFIED tags]
- **C34 · Keys to the Shop** (G4-2) — peacetime succession pack maintenance + wartime owner-death runbook execution (continuity, notifications, payroll). [account-freeze practice UNVERIFIED]
- **C35 · Bank Transplant** (G4-3) — full bank-switch surgery from 24-month transaction map: parallel-run, payer-by-payer follow-up, zero-inflow close gate. [SMB switching-rate UNVERIFIED]
- **C36 · After the Fire** (G4-4) — disaster finance officer: claim reconstruction from financial exhaust, filings, deadline calendar, forbearance negotiation, lowball counter. [SBA program UNVERIFIED]
- **C37 · Second-State Setup** (G4-5) — cross-state expansion registration graph executed (foreign entity, license, payroll accounts, bonds) + permanent two-state compliance calendar.
- **C38 · Sale Room** (G4-6) — perpetually sale-ready data room as by-product of operations; sale-side diligence sequence when buyer appears. [unsold-business stats UNVERIFIED]
- **C39 · Life-Event Autopilot** (G6-5; generated in D3, semantically D9) — consumer bereavement/divorce/redundancy case owner: task graph, mechanical execution, sequenced judgment decisions, deadline protection. [death-notification rails UNVERIFIED]

### D11 — Autonomous SMB finance office

- **C40 · Polite Bulldog** (G4-7) — receivables ownership: automatic lien-notice preservation, GC-behavior-calibrated dunning in owner's voice, retainage recon, escalation tripwires. [lien-deadline law UNVERIFIED]
- **C41 · Nightly Money Router** (G4-8) — executes nightly SMB treasury: sweep, LOC paydown/draw timing, terms-timed payables, payroll pre-positioning; one-line daily report. [payment-initiation API availability UNVERIFIED]
- **C42 · Margin Watchdog** (G4-9) — three-way-matches supplier invoices vs bid vs PO; price-creep disputes and change orders drafted before work done; live per-job margin.
- **C43 · Fee Forensics / RateWatch** (G5-1 ⊕ G4-10) — statement-level fee audit → drift/downgrade detection → leverage dossier → executed renegotiation or provider switch, contingency-priced; variant covers SMB bank+merchant fees w/ behavior fixes. **Convergent ×2.** [interchange parsing; outcome-pricing norm claims]
- **C44 · Gap Shopper** (G4-11) — normalizes all working-capital options to one true annualized cost, recommends mix, executes on approval, reports actual gap cost back into bids. [MCA characterization UNVERIFIED]
- **C45 · Certified Payroll Ghostwriter** (G4-12) — prevailing-wage engine: classification×county×job fringe computation, weekly certified report generation + filing, misclassification pre-flags. [Davis-Bacon/WH-347 UNVERIFIED]

### D2 — Machine-speed negotiation

- **C46 · YieldFloor** (G5-2) — treasurer's deposit-pricing negotiator: computes what balances should earn, negotiates per-bank monthly, solicits competing bids, executes moves; provable counterfactual. [Tier-1 bank agent deployment claim]
- **C47 · Accord** (G5-3 ⊕ G6-8 ⊕ G6-9) — policy-bounded tailored arrears relief: open-banking I&E, full relief-permutation simulation vs affordability + lifetime-loss, one pre-approved first-call offer OR iterative negotiation (incl. vs borrower's agent), daily arrangement tending w/ pre-breakage amendment. **Convergent ×2.** [Salient/Kastle traction; Reg-F guardrails]
- **C48 · MarginMatch** (G5-4) — collateral/margin-call dispute resolution at machine speed: reads CSAs, independently reprices, isolates divergence, negotiates resolution, cheapest-to-deliver selection. [Harvey/Legora contract-reasoning benchmark claim]
- **C49 · TermFlow** (G5-5) — live two-sided per-invoice early-payment-terms bargaining between supplier and buyer agents within mandates; standing-terms renegotiation. [Fazeshift/Daylit funding]
- **C50 · The Bourse** (G5-6) — the negotiation rail: registered agents w/ signed mandates, resident referee validating authority, enforcing bounds, notarizing transcripts, halting manipulation; binding term sheets. [Skyfire/Oasis KYA funding; x402 foundation membership]

### D10 — Insuring & warranting agentic action

- **C51 · Bindable** (G5-7) — underwriting desk for agent operators: ingests evals/guardrails/logs, adversarial sandbox probes, quantified risk profile, MGA policy/bond issuance, continuous re-rating. [AIUC raise + $500B market prediction; insurtech funding share]
- **C52 · PerAct** (G5-8 ⊕ G5-12) — per-action/per-outcome warranty rail in the action path: real-time risk scoring, bps premium quote, instant bind, trace-based auto-claims; variant: vendor-embedded outcome warranties. [x402 volume; Crescendo per-resolution pricing]
- **C53 · Recourse** (G5-9) — forensic claims adjuster for agent incidents: causal chain from traces, proximate-cause classification vs policy language, loss allocation, subrogation demands; precedent base compounds. [Braintrust/Langfuse valuations; 67% out-of-scope stat]
- **C54 · Telematic** (G5-10) — usage-based insurance for agent fleets: continuous behavior scoring, monthly attestation-driven repricing, pre-claim regression alerts w/ automatic scope-down, cross-operator loss bureau.
- **C55 · ClawNet** (G5-11) — recovery-and-loss network for agent payments: seconds-scale trace/freeze/clawback agents, private Reg-E-style rulebook, mutualized loss pool, liability tiers keyed to verified-safe operation. [x402 >100M payments; Fireblocks/AWS agentic-payment suites]

### D3 — Financial guidance for the unadvised

- **C56 · After-Call Answer Pack** (G6-1) — turns "we can't advise you" into a compliance-gated personalized guidance pack from transcript + account data; executes confirmed product steps. [FCA targeted-support reform UNVERIFIED]
- **C57 · Benefits Sweep-and-File** (G6-2) — entitlement sweep from transaction data + circumstances: eligibility, pre-filled applications, submission, chase-to-decision, award folded into revised budget/arrangement. [unclaimed-benefits £bn UNVERIFIED]
- **C58 · Wrong-Product Whistleblower** (G6-3) — whole-book product-fit audit per customer, quantified personal cost, switch letters, executed switches, remediation records. [Consumer Duty UNVERIFIED]
- **C59 · Big-Decision Second Chair** (G6-4) — real-time consequential-decision detection on live calls: consequences sheet mid-call, coercion/scam pattern checks, empowered friction (48h cool-off), specialist escalation. [APP scam losses UNVERIFIED]
- **C60 · Fiver-a-Month Adviser** (G6-6) — subscription standing money-guardian acting under bounded mandate: rate moves, bill renegotiation, entitlement sweeps, decision rehearsal, annual plain-language review. [advice-gap economics UNVERIFIED]

### D12 — Early warning & intervention

- **C61 · Ear on Every Call** (G6-7) — mines 100% of interactions for pre-delinquency signals, cross-checks transactions, opens pre-arrears case w/ tailored options pack + proactive contact, evidence trail. [full-coverage transcription cost]
- **C62 · Main-Street Early Warning** (G6-10) — continuous SME-account reading (seasonality vs decay), RM briefing pack + pre-modelled options menu + drafted outreach + booked call; live exposure view for credit. [RM account-load UNVERIFIED]
- **C63 · Postcode Shockwave** (G6-11) — employer-level payroll-inflow watch declares community credit events: cohort identification incl. second-order, pre-emptive hardship enrollment, frontline briefings, portfolio artifact.
- **C64 · Last-Door Case Agent** (G6-12) — pre-recovery exhaustive-alternatives engine: every restructure/scheme/assisted-sale path modelled dual-sided, best-alternative dossier, "nothing else was possible" certificate gating repossession. [repossession auditability UNVERIFIED]
