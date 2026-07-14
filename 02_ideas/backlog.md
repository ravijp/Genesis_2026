# Idea Backlog

Status: **skeleton** — populated in Phase 2. Do not add ideas here that haven't come from the evidence base (`01_research/`, `00_sources/`).

## Format for one-liners (Stage 1)

`[value-chain node] × [pattern P1–P8] × [client]: the 10-second story` — evidence: [link]

## Seeds collated from research briefs

### From finance.md

- **S-001**: Vulnerable-customer collections triage agent • agentic because it must sequence contact-timing/tone/escalation decisions across a case, not single-shot classify • demo moment: agent detects distress signals mid-conversation and auto-escalates to human with a full audit trail • Barclays.
- **S-002**: Collections cost-to-collect optimizer • agentic multi-step channel/timing sequencing per account • demo moment: side-by-side cost/recovery simulation vs. static rules engine • Barclays.
- **S-003**: HOA lockbox-to-cash-application agent • agentic because remittance parsing → matching → exception resolution is a multi-step workflow with judgment calls • demo moment: auto-reconciles a batch of ambiguous/partial payments live • Western Alliance.
- **S-004**: HOA delinquency/lien workflow agent • agentic sequencing of notice stages, legal-threshold checks, board approvals • demo moment: end-to-end from missed-assessment flag to board-ready lien recommendation packet • Western Alliance.
- **S-005**: HOA board reporting agent • agentic synthesis across lockbox, assessment, and delinquency data into a governed monthly report • demo moment: auto-generated board packet with drill-down explainability • Western Alliance.
- **S-006**: Small-business cash-flow-risk RM co-pilot • agentic because it must monitor, reason over multiple signals, and draft outreach autonomously • demo moment: agent proactively flags a client's cash-flow risk and drafts a relationship-manager outreach note • Western Alliance / Huntington.
- **S-007**: Small-business onboarding/portfolio-configuration agent • agentic multi-step document + data assembly • demo moment: cuts a claimed 15hrs/week manual onboarding task to a supervised agent run • Western Alliance / Huntington.
- **S-008**: KYC/AML decision-assurance (QC) agent • agentic because it audits another system's alert dispositions across many cases for consistency • demo moment: agent flags an inconsistent disposition pattern a human reviewer missed • generic bank client, DJ crossover angle available.
- **S-009**: Dispute-evidence-assembly agent • agentic reasoning to construct/argue a chargeback response packet, not just route it • demo moment: agent builds a full evidence case with citations in minutes vs. hours • Capital One / Visa / Amex.
- **S-010**: Agentic-commerce dispute-attribution agent • agentic because it must reconstruct "did the AI agent or the consumer authorize this" • demo moment: resolves an ambiguous agent-initiated-purchase dispute • Visa / Mastercard hook, timely given Agent Pay rollout.
- **S-011**: Advisor next-meeting-prep synthesis agent • agentic because it cross-references a specific client portfolio against fresh research/market moves, not just past-meeting notes • demo moment: generates a pre-meeting brief flagging what changed and why it matters for this client • Morgan Stanley / Invesco (differentiated from shipped Debrief/AskResearchGPT).
- **S-012**: Loyalty-interaction authenticity scoring agent • agentic because it must reason over a redemption/engagement sequence, not single-event classify • demo moment: flags a suspicious agentic-redemption pattern live and explains why • ampliFI.
- **S-013**: Loyalty offer-design risk scorer • agentic simulation of how an offer could be exploited by agentic/automated actors before launch • demo moment: red-teams a draft promotion and returns an exploitability score with fixes • ampliFI.
- **S-014**: Rewards-fraud investigation agent • agentic multi-step evidence gathering across accounts/redemptions • demo moment: builds a case file for a suspected rewards-fraud ring • ampliFI / issuer banks.
- **S-015**: Governance/audit-trail overlay agent (cross-cutting) • agentic because it must trace and explain any of the above agents' decisions on demand • demo moment: judge picks any prior agent action and gets a full explainability trace instantly • usable as a differentiator layered onto any of the above.

### From pharma.md

- **S-016**: PV case intake → triage → draft ICSR narrative, with mandatory human sign-off gate • why agentic: multi-step (extract → code MedDRA → dedupe → draft → escalate) mirrors ArisGlobal's real NavaX workflow; demo moment: agent flags an ambiguous case and defers to a human reviewer with reasoning shown; J&J hook: J&J runs a global PV operation processing large case volumes, directly comparable to the "sixth global pharma" ArisGlobal case study.
- **S-017**: Deviation report → root-cause hypothesis → CAPA draft, with QP-equivalent sign-off gate • why agentic: mirrors BMS-Anthropic's named use case exactly; demo moment: agent surfaces 3 similar historical deviations via RAG and proposes a CAPA, human approves/edits; J&J hook: J&J is a major manufacturer with real deviation-management scale.
- **S-018**: Health-authority query response drafting (e.g., FDA information request) with citation-traceable RAG • why agentic: directly addresses Elsa's biggest weakness (hallucinated citations) by only allowing retrieved, source-linked answers; demo moment: side-by-side showing every claim traces to a real (synthetic) source document; hook: positions the team as solving the exact failure mode FDA's own tool has publicly struggled with.
- **S-019**: MLR/promotional review compliance-gate agent • why agentic: checks claims against approved label language and flags unapproved claims autonomously, similar to Falcon MLR; demo moment: agent catches an off-label claim a human reviewer missed in a synthetic ad; J&J hook: J&J has a large MLR review volume across consumer/pharma business units.
- **S-020**: TMF document intake/classification/QC agent • why agentic: mirrors Medable's real TMF Agent; demo moment: messy inbox of misnamed/misfiled synthetic documents gets auto-classified, QC'd, and queued for one-click eTMF submission; hook: directly addresses the "95% still manual" stat cited industry-wide.
- **S-021**: CSR/protocol section drafting agent with traceable source attribution • why agentic: mirrors Merck's real 180hr→80hr workflow; demo moment: side-by-side of AI first draft vs. final human-edited version, with every data point traced to underlying (synthetic) trial data; hook: quantifiable time-savings story any pharma exec immediately understands.
- **S-022**: Cross-functional "safety signal to regulatory filing" handoff agent • why agentic: no vendor currently owns this cross-functional lane (PV and RA are separate silos in every vendor's product); demo moment: a synthetic safety signal automatically triggers a draft regulatory notification with full audit trail across two "departments"; hook: this is the differentiated, harder-to-copy use case since it requires orchestrating across systems no single vendor currently bridges.
- **S-023**: Site-monitoring / CRA risk-prioritization agent • why agentic: mirrors WCG's ClinSphere and Medable's Clinical Monitoring Agent; demo moment: agent ranks synthetic trial sites by risk score with explainable reasoning, surfaces the top 3 for human CRA review; hook: directly addresses site-monitoring cost, a persistent pain point in trial ops.
- **S-024**: Batch record review agent with exception-only human escalation • why agentic: verifies every synthetic critical process parameter against spec and only surfaces exceptions to a human, rather than requiring full manual review; demo moment: a 200-page synthetic batch record reduced to 3 flagged exceptions in seconds; hook: matches the "autonomous QC gate, human at exceptions only" pattern identified as still more aspiration than proven in the market — a good spot to look ahead of the curve.
- **S-025**: Annual Product Quality Review (APQR) cross-system aggregation agent • why agentic: mirrors LG CNS's real AWS Marketplace product; demo moment: agent pulls from synthetic "EDMS/LIMS/ERP/QMS" stand-ins and assembles a structured draft report with a plan-execute-verify trace visible to the judge; hook: manufacturing quality is the most mature agentic beachhead per Deloitte/BMS evidence, so this reads as credible rather than speculative.
- **S-026**: Regulatory dossier gap-checker against health-authority guideline changes • why agentic: mirrors ArisGlobal's Distribution Agents (validates guideline changes against internal logic); demo moment: a simulated new health-authority guideline triggers the agent to scan a synthetic dossier and flag exactly which sections need updating; hook: directly usable across any of J&J's therapeutic areas facing frequent guideline changes.
- **S-027**: "Elsa-proofing" — a submission pre-check agent that specifically anticipates and answers likely reviewer AI queries • why agentic: turns FDA's own well-publicized Elsa hallucination problem into a design constraint (only cite what's retrievable/traceable); demo moment: show the agent refusing to answer a question it can't source, then escalating to a human, in direct contrast to Elsa's documented failure mode; hook: extremely timely narrative hook — "we built the tool that helps you pass an AI reviewer, safely," which is both original and grounded in a real, recent, widely-reported regulatory pain point.

### From retail-agentic-commerce.md

- **S-028**: Agent-readiness consulting product • structured data, MCP endpoints, and policy surfaces — a concrete, buildable consulting product ("make client X agent-ready, measurably").
- **S-029**: Agentic-commerce fraud/abuse and agent-vs-bot discrimination layer • crosses retail into Visa/AmEx/Capital One — a strong Zenon crossover seed.
- **S-030**: Protocol-abstraction / governance layer for enterprises • enterprises need this due to Amazon v. Perplexity injunction + protocol fragmentation (ACP/AP2/UCP/TAP).
- **S-031**: Loyalty in the agentic era protection service • loyalty programs directly threatened by agent-mediated purchasing disintermediating offers — "loyalty in the agentic era" is an underexplored, client-fundable theme.

### From retail-internal-ops.md

- **S-032**: Returns-fraud triage agent • flags AI-faked damage claims/return-abuse patterns in real time • agentic because it must reason over claim text+image+history, not just rules • demo moment: agent catches a synthetic "damaged item" photo submission and auto-routes to human review • Kohl's hook: Amazon returns counter exposure + ampliFI fraud-trust crossover.
- **S-033**: Markdown/pricing exception copilot • recommends markdown timing/depth per SKU-store against margin targets • agentic because it must weigh competing signals (sell-through, competitor price, season) and justify a recommendation • demo moment: live before/after margin simulation on synthetic SKU data • Kohl's hook: directly answers CEO Bender's "pricing execution" turnaround language.
- **S-034**: Inventory allocation exception agent • detects and resolves stockout/overstock mismatches across stores • agentic because root-cause + re-allocation recommendation requires multi-step reasoning • demo moment: agent reallocates synthetic inventory from an overstocked store to a stockout store and shows the working-capital delta • Kohl's hook: same "inventory management" turnaround plank.
- **S-035**: Loyalty-offer adjudication agent • decides sub-second personalized offers at checkout in an agent-mediated (ACP/AP2) world • agentic because it must reconcile brand economics + member tier + real-time context faster than legacy batch segmentation • demo moment: two synthetic shoppers (one loyalty member, one agent-mediated anonymous buyer) get differently adjudicated offers in real time • ampliFI hook: direct product-line extension for ampliFI's card-linked-offers business.
- **S-036**: Sephora-at-Kohl's associate copilot • cross-catalog associate assistant spanning two brand experiences in one footprint • agentic because it must route between two distinct product/policy knowledge bases • demo moment: associate asks a hybrid Sephora/Kohl's question and gets a correctly-sourced answer • Kohl's hook: literal current strategic bet (Sephora partnership expansion through 2026).
- **S-037**: Markdown-to-Sephora-shelf reallocation agent • extension of #2/#5: reassigns physical shelf space from underperforming Kohl's apparel SKUs to expanding Sephora footprint • agentic because it's a constrained-optimization + negotiation problem across two P&Ls • demo moment: synthetic store-plan reshuffle with projected revenue-per-sq-ft delta • Kohl's hook: ties directly to the Sephora expansion narrative.
- **S-038**: Card-linked-offer fraud/abuse agent • detects synthetic/gamed offer redemption patterns • agentic because it must correlate loyalty, card, and return-fraud signals together • demo moment: agent flags a ring of accounts gaming a promo • ampliFI hook: sits squarely in ampliFI's card-processing/loyalty core business, a strong Zenon dual-client crossover.
- **S-039**: Vendor/supplier exception-management agent • automates supply disruption detection + re-routing recommendations • agentic because it chains detection → root cause → recommended action → human approval • demo moment: synthetic supplier delay triggers agent-proposed reallocation across DCs • Kohl's hook: general applicability to "inventory management" plank, lower originality than #1-4.
- **S-040**: Store associate task-prioritization copilot • competes with Microsoft's Store Operations Agent but scoped narrower (e.g., markdown-execution tasks only) • agentic because it must prioritize across competing floor tasks in real time • demo moment: agent reprioritizes associate task queue when a markdown event hits • Kohl's hook: execution-focused, but risks looking like a Copilot Studio clone — use only with a sharp differentiator.
- **S-041**: Agent-mediated commerce fraud/trust layer (cross-cutting) • verifies legitimate shopping agents vs. bot/scraper traffic at the retailer's edge (Visa Trusted Agent Protocol-adjacent) • agentic because it must classify traffic intent in real time • demo moment: agent distinguishes a legitimate ChatGPT/Gemini shopping agent from a scraping bot and applies differential access • Kohl's/ampliFI hook: connects back to the protocol-fragmentation white space already flagged in `retail-agentic-commerce.md` — good if Track A wants to bridge both research files.

### From startup-landscape.md

- **S-042**: Salient/Kastle proved AI voice+workflow collections lift payment rates 20-30% → a Reg-F-compliant, hardship-aware collections agent for *Barclays* card delinquencies that detects distress and escalates to humans.
- **S-043**: AgentCollect/Salient proved consumer-lending servicing agents → an end-to-end delinquency & loss-mitigation agent for *Lendmark* installment loans (promise-to-pay orchestration + settlement offers within policy).
- **S-044**: Vantaca (+$300M) proved HOA management software → an *HOA bank-ops* agent for *Western Alliance*: auto cash-application of homeowner dues, reserve-fund anomaly detection, lien/delinquency workflow.
- **S-045**: EliseAI proved property-ops assistants → a small-business banking onboarding + deposit-ops exception agent for *Western Alliance* SMB clients (KYC-lite, doc chase, cash-flow underwriting for <$250K credit).
- **S-046**: Diligent AI / Norm Ai proved KYC-AML agents clear false positives → a *false-positive-triage* alert-adjudication agent for a *Capital One / Western Alliance* AML queue with full audit trail (attacks the 95%-wasted-investigator-time stat).
- **S-047**: Decagon/Sierra proved outcome-priced CX agents → a *dispute & chargeback orchestration* agent for *Visa/Amex/Capital One* (evidence gathering, network-rule reasoning, representment drafting).
- **S-048**: Stabile + x402/PYMNTS proved loyalty must adapt to agentic commerce → a *loyalty-ops* agent for *ampliFI/Amex* that optimizes offer targeting and detects rewards fraud/abuse in real time.
- **S-049**: Fazeshift/Daylit proved AR agents (>90% automation, opex -75%) → an *AR/collections + cash-application* agent for *Invesco/Morgan Stanley* institutional back-office (invoice→match→reconcile→dunning).
- **S-050**: Warp/Niural proved AI payroll+compliance → a *payroll-exception* resolution agent for *ADP* (retro pay, garnishments, multi-jurisdiction tax, off-cycle) with human sign-off — attacking exceptions, not the whole stack.
- **S-051**: Harvey/Legora/Eudia proved contract-review agents → a *vendor-contract & obligation-tracking* agent for *J&J* or *Kohl's* procurement (renewal risk, clause deviation, SLA/obligation monitoring).
- **S-052**: Adonis/Abridge proved AI-first RCM (denials 41%) → a *prior-auth + denial-appeal* agent for *J&J*-adjacent patient-access / market-access programs (CMS 7-day turnaround as the target metric).
- **S-053**: AgentOS/Lumari/Traza proved procurement agents (opex -30%) → a *retail merchandise/vendor procurement* agent for *Kohl's* (RFQ, PO expediting, supplier chase, exception routing).
- **S-054**: DiligenceSquared/Zarna proved diligence-associate agents → an *investment-diligence / fund-doc* agent for *Invesco/Morgan Stanley* (data-room extraction, memo drafting, red-flag surfacing).
- **S-055**: Corgi/Harper proved insurance claims/underwriting agents → a *small-business insurance or credit-insurance* underwriting-triage agent for a *Western Alliance / Lendmark* lending workflow.
- **S-056**: Dow Jones adjacency: media has no breakout vertical agent → a *newsroom research + entity/market-event monitoring* agent for *Dow Jones* that turns filings/wires into structured, sourced briefs (mirrors OpenEvidence's "act on data" pattern in a media context).

### From agentic-ai-landscape.md

- **S-062**: AML/fraud alert investigation agent (Amex/Capital One/Barclays/Western Alliance) • autonomously queries registries, cross-references internal records, validates transactions across many steps, clears alerts alert-to-closure • demo: an alert resolved in minutes with a full audit trail and a confidence score, plus a verifier that catches a planted false-positive.
- **S-063**: KYC/onboarding due-diligence agent (Morgan Stanley/Lendmark/ampliFI) • runs CIP sourcing, ownership-structure unwrapping, sanctions + adverse-media screening in parallel, shifting KYC from calendar-based to always-on • demo: onboarding cut from days to minutes with parallel sub-agents and a policy-adherence check.
- **S-064**: Reconciliation & exception-handling agent (Visa/Invesco) • multi-step matching, root-causes breaks, drafts adjusting entries, escalates only true exceptions with HITL • demo: a batch of synthetic breaks auto-resolved, exceptions routed for approval, with cost/latency shown per item.
- **S-065**: Investment-research / earnings-synthesis agent (Morgan Stanley/Invesco/Dow Jones) • plans a research task, pulls filings + news (Factiva-style synthetic corpus), self-critiques, cites sources • demo: a research memo with inline citations and a reflection pass that corrects a planted error.
- **S-066**: Regulatory-change / compliance-monitoring agent (all finance) • continuously monitors rule changes, maps them to internal policies, drafts gap analyses • demo: a new synthetic regulation ingested → affected policies flagged → remediation drafted, with audit trail.
- **S-067**: Credit / underwriting decision-support agent (Capital One/Lendmark/Western Alliance) • gathers applicant data, runs checks, produces an explainable recommendation with a policy-compliance verifier • demo: a decision with a full reasoning trace and a "why not approved" explanation.
- **S-068**: Pharma safety / literature-triage agent (J&J) • screens adverse-event reports or literature, extracts structured signals, escalates • demo: a synthetic AE dossier triaged with structured extraction + human-review checkpoint.
- **S-069**: Retail merchandising / supply agent (Kohl's) • monitors inventory signals, reconciles across systems, drafts reorders with approval gates • demo: a stockout risk detected → cross-checked → reorder proposed for human approval.
- **S-070**: Payroll/HCM exception & compliance agent (ADP) • validates payroll runs across jurisdictions, catches anomalies, explains discrepancies • demo: a synthetic multi-jurisdiction payroll batch validated, anomalies flagged with explanations and audit trail.
- **S-071**: Contract / T&C analysis agent (cross-industry) • extracts terms, checks against policy, flags risky clauses, drafts redlines with a verifier • demo: a contract analyzed → risky clauses flagged with rationale → redline proposed, judge-verified.

### From media-findings-digest.md

- **S-057**: Adverse-media/sanctions screening assurance agent on DJ Risk & Compliance-style data for bank onboarding (Dow Jones × Barclays/WAB crossover; DJ itself has no agentic product).
- **S-058**: "Orca-for-X": continuous corpus-mining agent over niche audio/video/filings for a data business (validated by WSJ's award).
- **S-059**: Agent-ready data productization: build a client's proprietary dataset into a governed MCP server + agent skills (the S&P/Moody's/FactSet playbook applied to a mid-market client).
- **S-060**: Claims-extraction + verification agent for research/editorial workflows (Semafor Intelligence pattern, applied to financial research at MS/Invesco).
- **S-061**: Evals-first agent governance harness as a differentiator in ANY build (Bloomberg CTO quote; AI-judge scoring).

_Collated verbatim on 2026-07-14 by mechanical pass; no dedup or judgment applied. Total: 71 seeds (S-062..S-071 from agentic-ai-landscape.md added manually)._

## Round-1 ideas (divergence sprint)

*(pending Phase 2 ideation sprint — 3 independent ideation agents + Ravi + Claude)*

## Parked / killed (with reason)

*(kill reasons stay visible so we don't re-litigate)*
