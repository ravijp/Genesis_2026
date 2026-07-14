# Production Track (T15) — the 80% pool

**Status: 2026-07-15, fresh ideation landed; lock decision with Ravi.** This file is the T15 deliverable per the reground-brief **ADDENDUM**: ideas that earn their keep in the present state — pinned to each client's *researched, actual* AI-adoption state (`01_research/client-ai-state-map.md`), with a **3-week-fit story** (competition MVP → client pitch → ~3 weeks fitting into their infrastructure) and a **1-year engagement arc** (POC → Phase 1 → Phase 2 → stable production → client team takes over). The 20% vision tier stays in `north-stars.md`.

**Provenance.** Two independent fable generators, no shared context, quarantined from all of `02_ideas/` (fresh thinking, not relabeling): lens **D** = delivery engineer (what clears a bank's risk committee and ships), lens **B** = P&L-owner buyer (what I'd sign this quarter). Both read only the state map + `finance.md` + client context. Convergence between them signals salience on shared evidence, not independent validation (standing caveat). Raw outputs preserved in the session task transcripts; ~90% of their content is folded below with D#/B# provenance.

**Convergence headline:** the two lenses independently produced near-identical top-5 signing lists — Barclays conversation QA ranked #1/#3 and WAB lockbox #2/#2 on both. Twelve of sixteen distinct ideas appeared in both passes.

## Scoreboard — "signs this quarter" ranking (synthesized from both lenses)

| # | Candidate | Client (state) | Both lenses? | Maps to | 3-wk-fit quality |
|---|---|---|---|---|---|
| P-001 | Consumer-Duty conversation QA | Barclays (S2) | ✅ D2+B1, top-3 both | R-002 / N-001 day-1 | **Best on roster** — transcript pipeline already runs |
| P-002 | HOA lockbox cash-application (+lien phase 2) | WAB (S1) | ✅ D3/D4+B4/B5, #2 both | R-004/R-005 / CP-1 doer | **Pure file-in/file-out** |
| P-003 | Collections treatment sequencer (shadow-mode) | Barclays (S2) | ✅ D1+B2, D's #1 | R-001 / CP-2 doer re-grounded | Case exports, shadow only — no send rights |
| P-004 | Loyalty authenticity + offer red-team bundle | ampliFI (S0) | ✅ D11+B10/B11 | R-015/R-016 / N-003 day-1 | Logs + T&Cs, zero core changes; warm engagement |
| P-005 | ACE agent-error dispute adjudication | Amex (S2→S3) | ✅ D8+B8 | R-012 / **N-002's day-1 wedge** | New program = clean small data surface |
| P-006 | AI-servicing assurance (QC of their AI) | Capital One (S3) | ✅ D7+B7 | R-047/R-049 concretized | Interaction logs, offline |
| P-007 | SMB cash-flow sentinel (RM outreach drafts) | Huntington/WAB (S1→S2) | ✅ D5+B6 | R-007 / N-012 day-1 | Read-only telemetry extract |
| P-008 | AML alert-disposition assurance QC | Huntington/WAB (S1) | ✅ D14+B12 | R-009 | Closed-case exports — lowest-risk compliance data ask |
| P-009 | External-agent MCP watchtower | Morgan Stanley (S3) | ✅ D10+B13 | **NEW — no prior cluster** | Gateway logs, read-only |
| P-010 | Agent-onboarding conformance harness | Visa (S3) | ✅ D9+B9 | R-048 | Specs + sandbox; impact math thin at today's volume |
| P-011 | Consumer-Duty evidence-pack agent | Barclays (S2) | B3 only | **NEW** (N-001 examiner-pack as standalone buy) | MI/complaints/QA exports |
| P-012 | Loss-mit authority QC + hardship recommender | Lendmark (S1) | ✅ D13+B14 (pair) | R-030 + R-019 | Decision exports + DOA matrix; WTP caveat |
| P-013 | Protective-services case investigator | Huntington (S1→S2) | D6 only | R-017-adjacent (banking fraud) | Flag feed + telemetry, read-only |
| P-014 | Reconciliation break-resolution | Invesco (S0) | D12 only | near parked R-022 — **freshness check required** | Recon exports; no public pain anchor |

**Portfolio math (80/20):** 14 production-track candidates + the north-star vision tier (N-002/N-009 arcs, N-001 full stack, N-004 platform vision — `north-stars.md`) ≈ 80/20 by count and by pitch-time allocation. The competition MVP should be the top production candidate built properly (evals, HITL, audit) with its north-star arc narrated as chapter two.

## The candidates

Format: buyer + state hook · pain · agent (HITL) · 3-week fit · the number that moves · 1-year arc · notes.

### P-001 — Consumer-Duty Conversation QA (Barclays) — ✅ both lenses, top-3 both

- **Buyer:** Head of Collections Ops / QA lead. **State hook:** GenAI contact-centre summarization already in production (Feb 2026) — transcripts exist and nobody acts on them; FCA collections rules live since 2026-04-01; FCA AI Live Testing cohort 2 member.
- **Pain:** QA samples ~2% of calls; 49% UK-adult vulnerability incidence; every unsampled call is Consumer Duty exposure signed off blind.
- **Agent:** reads every transcript/summary, scores vulnerability handling + treatment fairness + disclosure compliance against policies-as-code + LLM judgment, builds evidence-linked findings; compliance officer dispositions every flag (HITL).
- **3-week fit:** the transcript feed already exists — batch, read-only, redacted; runs in client VPC. Retroactive run on last quarter's transcripts gives results in week 2.
- **Number:** QA coverage 2%→100%; breach-detection rate vs the human-sampled baseline, within 6 weeks.
- **1-yr arc:** POC on 3 months of historical transcripts → P1 daily batch with QA disposition → P2 near-real-time flagging feeding contact gates → handover as an examiner-ready capability inside their FCA-sandbox story.
- **Notes:** maps to R-002 = N-001's day-1 story — the fresh pass independently re-derived it and both lenses ranked it top-3. Differentiation: speech-analytics keyword-spots; Salient's UDAAP monitor is US + collector-specific; nobody ships FCA Consumer-Duty conversational QA. Demo: agent catches a distress signal the human QA pass scored "pass," reasoning chain shown.

### P-002 — HOA Lockbox Cash-Application, lien workflow as phase 2 (WAB) — ✅ both lenses, #2 both

- **Buyer:** Director of Association Banking ops. **State hook:** lockbox→reconciliation loop confirmed manual; Zenon AI discovery engagement Feb-Mar 2026; no HOA-specialist bank advertises AI in the chain.
- **Pain:** daily remittance files across thousands of associations; partial/ambiguous payments all queue to humans; industry touchless analogs run 95%+ (HighRadius; Billtrust 45%→90%).
- **Agent:** parses remittances, matches to assessment ledgers (partials, splits, wrong coupons), resolves ambiguity with documented reasoning; human approves every posting in POC/P1. Phase 2 adds delinquency→notice→lien-packet workflow (board approval gate, GSE 15%-threshold alerting).
- **3-week fit:** pure file-in/file-out — SFTP drop of files the bank already produces daily; zero core-banking integration; no posting rights. Cleanest fit on the roster.
- **Number:** exception auto-resolution rate + items-per-FTE-day within 4 weeks; touchless match rate vs manual baseline.
- **1-yr arc:** POC on 90 days of historical files → P1 supervised daily run → P2 auto-post below dollar threshold + lien workflow (this is CP-1's earned-autonomy graduation, which IS the P1→P2 gate mechanism) → handover as a bank product feature.
- **Notes:** = CP-1's doer; the graduation controller from `grounded-track.md` is the engagement arc productized — keep it as the differentiator and the competition demo mechanic. Bank-side P&L bottom-up estimate remains the pre-pitch blocker (T7).

### P-003 — Collections Treatment Sequencer, shadow-mode (Barclays) — ✅ both lenses, D's #1

- **Buyer:** Head of Collections & Recoveries (revenue-share model — the metric is literally the contract). **State hook:** live Zenon engagement; static rules-engine treatment paths; UK delinquency +16.3% YoY (FICO Apr 2026).
- **Agent:** nightly case exports → per-account channel/timing/tone sequencing with hardship/vulnerability reasoning; **shadow-mode first** — recommendations run against the champion strategy; vulnerable-flagged accounts auto-route to humans; no send rights, no dialler access (HITL by construction).
- **3-week fit:** case-management + contact-history exports; output = recommendation queue into the existing workflow tool; treatment policy + FCA rules as config.
- **Number:** simulated promise-to-pay / roll-rate uplift vs champion on held-out accounts in ~8 weeks; then live champion/challenger cell.
- **1-yr arc:** POC shadow → P1 10% live cell, human-approved → P2 auto-execute low-risk segments within an approved treatment library, humans own vulnerable cases → handover with the eval harness.
- **Notes:** this is CP-2's doer, re-grounded exactly as the red-team demanded (between-contact, shadow-first, no live customer contact). **P-001 + P-003 together are the corrected CP-2**: watcher on today's human/dialler estate + doer in shadow — one Barclays narrative, each independently sellable. Differentiation: TrueAccord/InDebted want the book outsourced; the bank wants the capability in-house — that's the Zenon engagement shape.

### P-004 — Loyalty Authenticity + Offer Red-Team bundle (ampliFI) — ✅ both lenses

- **Buyer:** ampliFI COO / program managers. **State hook:** Zenon engaged since Aug 2025 (Phase 2.1 Feb 2026); zero AI product (confirmed absence); agentic-browser traffic +7,851% YoY (HUMAN 2026) vs programs "secured like marketing databases."
- **Agent:** (a) pre-launch red-team — simulates automated exploitation of a draft offer's T&Cs, returns exploitability score + fixes (program manager decides launch); (b) redemption-sequence authenticity scoring human / legit-agent / abuse with case files (analyst approves any account action; never auto-suspends).
- **3-week fit:** redemption/engagement logs + offer T&Cs, batch; zero changes to the processing core; warm engagement = near-zero contracting friction.
- **Number:** exploitable-offer catch rate pre-launch (re-red-team past burned promos blind); flagged-abuse dollars + false-positive rate on live logs within 6 weeks.
- **1-yr arc:** POC historical → P1 pre-launch gate + weekly monitoring → P2 real-time scoring API productized to ampliFI's issuer clients (a new revenue line for the client — strong 1-yr story) → handover.
- **Notes:** = N-003's day-1 entry, independently re-derived by both lenses. N-003's promotion gates still bind for competition scoring (loyalty-fraud dollar primary source, hold-out exploit design — T7).

### P-005 — ACE Agent-Error Dispute Adjudication (Amex) — ✅ both lenses

- **Buyer:** VP Disputes / ACE program owner. **State hook:** Amex launched agent-error purchase protection (Apr 2026) — **they underwrite the liability today with no adjudication tooling**; every protection claim needs exactly this.
- **Agent:** reconstructs the authorization chain from agent-session logs, consent tokens/attestations, merchant records → attribution finding (agent error / consumer intent / fraud) with confidence + recommended disposition; analyst approves every outcome.
- **3-week fit:** ACE claim files + attestation formats — a brand-new program means a clean, small data surface with no legacy integration; sits beside the existing dispute queue.
- **Number:** analyst handle-time per agent-claim + determination consistency, visible immediately at today's low volume.
- **1-yr arc:** POC on synthetic seeded disputes → P1 co-pilot on the live trickle → P2 auto-disposition of clear-cut cases as rails volume grows → handover.
- **Notes:** **this is N-002's day-1 wedge** — the fresh pass found what the T14 re-tiering missed: the buyer (ACE) already exists and pays for this muscle *before* volume arrives. Small impact math today (say so); the north-star Mandate Fabric arc is the honest chapter two. Re-tier note added to `north-stars.md`.

### P-006 — AI-Servicing Assurance (Capital One) — ✅ both lenses

- **Buyer:** Head of Servicing Quality / second line. **State hook:** gen-AI servicing tool live at thousands of agents with a **published** 93%-vs-84% relevance baseline; ICML-grade agentic-safety research posture — they'll respect an evals-first vendor; don't out-build an S3 client, audit it.
- **Agent:** replays AI-assisted interactions, independently re-derives correct answers from policy/KB snapshots, flags divergence, clusters failure modes, detects drift/staleness; MRM/quality analyst dispositions findings.
- **3-week fit:** interaction-log export + KB snapshot, offline, no production hooks.
- **Number:** verified accuracy vs their own published 93%; time-to-detect a KB-staleness cluster — the baseline is one they already report.
- **1-yr arc:** POC offline → P1 daily QC feed → P2 pre-release regression evals for their agentic launches → handover into their MRM org.
- **Notes:** concretizes R-047/R-049 at the one client where the felt need is *provably* live (they published the number). Demo: a systematic wrong-answer cluster the 93% aggregate hides.

### P-007 — SMB Cash-Flow Sentinel (Huntington/WAB) — ✅ both lenses

- **Buyer:** Head of Small Business Banking. **State hook:** bank owns the deposit telemetry; True Link partnership proves the bolt-on-agent model at HNB; RMs 60-70% non-advisory (McKinsey-traceable).
- **Agent:** monitors SMB deposit/transaction streams, multi-signal deterioration/opportunity reasoning, drafts evidence-attached RM outreach; RM sends or discards — agent never contacts a customer.
- **3-week fit:** read-only telemetry extract for a pilot portfolio + CRM export; drafts into RM inbox.
- **Number:** RM-accepted alerts/week + meetings booked (6 weeks); killer POC move: **backtest on churned/defaulted accounts — "would we have seen it?"**
- **1-yr arc:** backtest POC → P1 live drafts for ~20 RMs (RM feedback = eval data) → P2 whole-book triage → handover. Gate: RMs use it voluntarily.
- **Notes:** = R-007/N-012 day-1; the act-step requirement from team review stands (investigate → draft → track → escalate, or it's a dashboard).

### P-008 — AML Alert-Disposition Assurance QC (Huntington/WAB) — ✅ both lenses

- **Buyer:** BSA Officer / Head of FIU. **State hook:** S1 banks buy screening tools; nobody QCs the dispositions; exam risk is *inconsistency*.
- **Agent:** re-adjudicates closed alerts at population scale, flags cross-analyst/typology inconsistency patterns, drafts defensibility findings; BSA officer owns every finding; SAR decisions stay human; never touches live alerts.
- **3-week fit:** closed-case exports, read-only, historical — the lowest-risk data ask in compliance; retroactive results week 2.
- **Number:** QC coverage sample→100%; inconsistency findings per 1,000 alerts vs a $1M-a-pop consultant lookback.
- **1-yr arc:** POC on 6-12 months of closed cases → P1 monthly QC cycle → P2 pre-closure second-look on high-risk dispositions → handover to compliance QA.
- **Notes:** = R-009, re-derived by both lenses; DJ Risk & Compliance crossover (R-010) available for originality at T6.

### P-009 — External-Agent MCP Watchtower (Morgan Stanley) — ✅ both lenses — NEW

- **Buyer:** Head of stock-plan platform ops / platform security. **State hook:** MS opened stock-plan platforms to external agents via MCP (Jun 2026) — first on Wall St; **opening the door created the monitoring problem the same day, and nobody (internal or vendor) covers it.**
- **Agent:** consumes MCP gateway logs, reconstructs each external agent's session into a plain-English intent narrative, profiles per-agent behavior, flags anomalies (scope creep, data over-pull, error loops), drafts incident reports; kill-switch/throttle decisions stay with ops (HITL).
- **3-week fit:** gateway log feed, read-only; no inline blocking in POC/P1.
- **Number:** % of external-agent sessions with a reviewed intent narrative; mean time-to-detect a seeded misbehaving agent — baseline is zero coverage (easy win, softer ROI math — say so).
- **1-yr arc:** POC on log replay → P1 daily review queue → P2 inline rate-limit/hold recommendations + policy engine → handover to platform security.
- **Notes:** **genuinely new cluster — no prior R/N covers external-agent monitoring on a bank's MCP surface** (R-025 is internal service-account auditing). Fresh (surface is weeks old), F1-flavored — needs a collision scan before carding (T7). Also the one production idea that literally monitors *agents*, bridging to the north-star governance arc without presupposing the client's own agents.

### P-010 — Agent-Onboarding Conformance Harness (Visa) — ✅ both lenses

- **Buyer:** Head of Ecosystem Risk / partner onboarding. **State hook:** TAP + Agentic Registry + Agent Score live; onboarding review is manual against a spec.
- **Agent:** adversarially exercises candidate agents against TAP/registry specs (mandate adherence, consent handling, failure modes, replay edge cases) → scored conformance report; Visa engineer signs certification.
- **3-week fit:** spec docs + sandbox endpoint; entirely outside production rails.
- **Number:** review hours per partner; defects caught pre-production. Volume caveat: "hundreds" of transactions network-wide — sign small, option to scale.
- **1-yr arc:** POC on reference agents → P1 in the intake path → P2 continuous re-certification of the registry → handover.
- **Notes:** = R-048. Demo: harness catches a consent-replay edge case in a "compliant" reference implementation.

### P-011 — Consumer-Duty Evidence-Pack Agent (Barclays) — lens B only — NEW

- **Buyer:** COO Retail Collections (co-signs the Consumer Duty board report + FCA sandbox submissions). **State hook:** Mills Review (2026-07-06) says supervision is going AI-enabled — outcome evidence needs to be machine-legible; assembly today is a quarterly consultant-grade fire drill (~£200k/quarter, non-cumulative).
- **Agent:** pulls complaints exports, QA outputs, MI packs → drafts the evidence pack with every claim traced to a source record, flags evidence gaps by cohort; human signs everything.
- **3-week fit:** read-only exports of MI/complaints/QA logs; no regulator-facing sends.
- **Number:** assembly weeks→days; % of claims with source-linked evidence, first quarter-end.
- **1-yr arc:** POC on last quarter's pack → P1 drafts this quarter's, team edits → P2 continuous evidence ledger → handover. Gate: compliance officer prefers it to the consultants' pack.
- **Notes:** new standalone buy of N-001's examiner-pack artifact; natural P2 of P-001 (same buyer chain). Demo: click any sentence in the report → underlying records instantly.

### P-012 — Loss-Mit Authority QC + Hardship Recommender (Lendmark) — ✅ both lenses (pair)

- **Buyer:** SVP Servicing. **State hook:** mid-productionization-roadmap with Zenon (Jan 2026, daily syncs) — the arc maps 1:1 onto the engagement they already pay for. **WTP caveat stands (Ravi): price/score accordingly.**
- **Agent:** (a) authority QC — reviews 100% of loss-mit decisions against the delegation-of-authority matrix + policy, flags out-of-authority patterns (read-only; audit-shaped); (b) hardship recommender — reads case + docs, recommends modification terms within DOA, every recommendation human-approved, above-DOA auto-escalates.
- **3-week fit:** decision exports + DOA matrix (a config document); no servicing-system writes.
- **Number:** exception-detection coverage sample→100% (8 weeks); decision-consistency score; re-default rate on modified accounts by Q2.
- **1-yr arc:** POC historical/shadow → P1 branch pilot → P2 auto-approve inside tight DOA bands → handover.
- **Notes:** = R-030 + R-019. Demo: two near-identical cases with opposite human decisions last month; the principled single answer shown.

### P-013 — Protective-Services Case Investigator (Huntington) — lens D only

- **Buyer:** fraud/protective-services ops. **State hook:** True Link Retina already flags scam merchants pre-charge at HNB (Jun 2026) — the *investigation* behind each flag is still human; the third-party-agent governance path is pre-paved.
- **Agent:** per flag, iteratively gathers evidence across accounts/transactions/prior cases, reconstructs the pattern, drafts a case file + recommended action; analyst approves any restriction or contact.
- **3-week fit:** read-only telemetry + existing flag feed; case files into the current queue.
- **Number:** minutes-per-case, cases-closed-per-analyst-day — continuous volume, measurable in weeks.
- **1-yr arc:** POC on historical flags → P1 live queue → P2 auto-close low-risk false positives → handover.
- **Notes:** new-ish (banking-side fraud investigation; R-017 is the loyalty cousin). Demo: from one flag, two related victim accounts nobody had connected.

### P-014 — Reconciliation Break-Resolution (Invesco) — lens D only — freshness-gated

- **Buyer:** head of fund ops. **State hook:** S0 client, no public pain anchor — a wedge-to-blank-slate play; recon extracts are universally file-based.
- **Agent:** ingests recon exports, investigates each NAV/custody/TA break (timing vs error vs corporate-action), drafts resolution + journal recommendation; analyst approves every adjustment.
- **Caveat:** adjacent to F3-parked R-022 (Fazeshift/HighRadius/free GL-reconciler templates set the commodity floor). Card only if a fund-ops-specific freshness check clears (T7) — the fund-accounting break niche differs from AR cash-app, but the burden of proof is ours.

## Relationship to the T14 combined pitches

- **CP-1 (WAB)** = P-002 + the graduation controller — **confirmed by the fresh pass** (both lenses independently top-2). The graduation machinery is the P1→P2 engagement gate productized; keep it as the competition demo mechanic.
- **CP-2 (Barclays)** = properly re-grounded as the **P-001 + P-003 pair** (watcher on today's estate + doer in shadow) — this resolves both red-team objections structurally, and each half is independently sellable this quarter.
- **CP-3 (remediation)** — **notably absent from both fresh passes.** Under the "pay this quarter, current pain" frame, neither the delivery engineer nor the buyer produced it — corroborating the red-team's buyer-timing objection. N-008 stays a GROUNDED LEAD concept on its merits (F1, regulator-forced when triggered), but as an *engagement* it is event-driven: keep it as the rapid-response offer in the portfolio narrative, not the lead engagement pitch, unless T7 finds evidence Barclays-scale banks nearly always have an open remediation program.

## Weakest claims & how to verify

1. P-002 bank-side P&L (T7, standing pre-pitch blocker). 2. P-009 collision scan (external-agent/MCP monitoring vendors — new idea, unverified freshness). 3. P-005 ACE claim volume/process reality — Amex ACE detail was thin at source (finance.md flags it); verify before pitch. 4. P-011's "£200k/quarter consultant" framing is persona-generated color, not evidence — source UK Consumer-Duty reporting spend or drop the number. 5. P-014 fund-ops freshness check. 6. B-lens personas' specific claims (e.g., "2% QA sampling") are plausible domain color, not cited facts — every number entering a card needs a brief anchor or an "UNKNOWN — get from client" tag. 7. Convergence caveat: both lenses read the same three files; 12/16 overlap signals evidence salience, not independent market validation.
