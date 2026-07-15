# Ideation v2 — Stage 1: Semantic Directions

**Stage:** direction stratification (regions of the problem space, NOT ideas)
**Date:** 2026-07-15
**Input:** exactly one repo file — `01_research/agentic-ai-landscape.md` — plus general knowledge. No other repo files were read (bias quarantine).
**Question:** where can agentic AI create value in and around financial services?

Each direction is a problem-space region: what it is, and why value might live there. No product concepts.

---

## Directions

**D1 — Exception and dispute repair in money flows.** The region where money movement breaks or is contested — failed payments, misdirected transfers, chargebacks, billing disputes, customer remediation — and someone must investigate, adjudicate, and make parties whole under regulatory clocks. Value lives here because repair work is high-volume, evidence-gathering-heavy labor with hard deadlines, where speed and consistency of resolution directly convert to cost, loss, and retention outcomes.

**D2 — Machine-speed negotiation between parties.** The region of bilateral and multilateral bargaining that finance runs on — fee and rate negotiations, contract renewals, syndication terms, collateral and margin agreements, vendor pricing — which today crawls through email threads and quarterly reviews. Value might live here because negotiated outcomes decay when humans lack time to renegotiate; continuous, well-bounded negotiation could recapture value currently left on the table by both sides' inattention.

**D3 — Financial guidance for the unadvised.** The region of customers who make consequential financial decisions (debt, savings, benefits, product choice) without access to human advice because advice economics only work above certain wealth thresholds. Value lives here because the teaching/coaching verb has never scaled — the open question is delivering judgment-laden guidance in a regulatorily safe, trust-earning way to the long tail of customers.

**D4 — The supervision interface between institution and regulator.** The two-sided region where institutions must prove compliance (regulatory reporting, attestations, exam preparation, evidence production) and supervisors must examine at scale (SupTech). Value lives here because proof today is produced by armies of people reconstructing evidence after the fact; making operations continuously examinable changes the cost structure on both sides of the interface.

**D5 — Expertise capture and transfer inside the institution.** The employee-facing region of tacit knowledge: what the 25-year operations specialist, workout banker, or claims adjudicator knows that never made it into procedure documents, and that walks out the door at retirement. Value lives here because financial institutions face demographic cliffs in scarce specialties, and the teach verb pointed inward — apprenticing, upskilling, and encoding judgment — is largely unserved.

**D6 — Explainable decisioning under uncertainty at origination.** The region of point-of-entry judgment calls — credit underwriting, insurance risk acceptance, limit and pricing decisions — where the institution must decide with incomplete information and later defend the decision. Value lives here because the binding constraint is not prediction accuracy but defensible, individually-explained decisions at volume, especially in the messy middle band that today gets escalated to humans or declined by default.

**D7 — The machine customer.** The region where software agents themselves become account holders, payers, and purchasers — a genuinely new customer segment requiring identity, mandates, spending authority, and dispute standing for non-human actors. Value might live here because every prior new-customer-segment shift (corporates, e-commerce) created new products, new rails, and new intermediaries, and agent-initiated commerce is emerging now with unsettled infrastructure.

**D8 — Inter-institution back-office plumbing.** The region of coordination toil between counterparties in market infrastructure: settlement fails, reconciliation breaks, corporate-action processing, reference-data disagreements, standards migrations. Value lives here because these are many-to-many coordination problems no single institution can fix alone — each break requires two organizations' back offices to converge on shared facts, and that convergence is currently manual, slow, and duplicated across the industry.

**D9 — Life-event administration on the customer's behalf.** The region of multi-institution paperwork that major life events impose on people — bereavement, divorce, relocation, home purchase, retirement — where the customer must personally do dozens of sequenced administrative tasks across banks, insurers, employers, and government. Value lives here because the burden falls on customers at their most stressed moments, no single institution owns the end-to-end journey, and completion (not advice) is the product.

**D10 — Insuring and warranting agentic action.** The insurance-adjacent region of risk transfer for what AI agents do: who bears the loss when an autonomous agent misroutes funds, breaches a mandate, or executes a bad trade — liability allocation, bonding, warranties, and the underwriting of agent operators and vendors. Value might live here because autonomy adoption is gated on "who pays when it fails," and a market that can price and absorb that risk unlocks deployment everywhere else.

**D11 — The autonomous finance office for small and mid-size businesses.** The commercial-banking region where business customers run their own finance function — cash-flow forecasting, receivables/payables, treasury, FX, working-capital decisions — chronically understaffed below the CFO-suite threshold. Value lives here because banks are positioned to operate (not just report on) their business customers' finances, converting the bank's role from ledger to doer and deepening deposit/lending relationships.

**D12 — Early warning and intervention across the credit and asset lifecycle.** The post-origination region of watching exposures for deterioration — covenant drift, pre-delinquency signals, portfolio concentration — and then intervening early with restructuring, hardship options, or hedges before losses crystallize. Value lives here because detection without timely, individually-tailored intervention captures nothing; the watch-then-repair combination, at per-account granularity, is beyond current staffing models.

---

## Distance self-check (performed)

All 66 pairs compared. Actions taken during the check:

- **Replaced:** a drafted "fraud/AML alert triage" direction — too close to D1 (both are queue-based exception investigation and resolution) and the default watch-region everyone converges on. Replaced with D7 (the machine customer), a different region entirely.
- **Replaced:** a drafted "third-party/vendor risk monitoring" direction — collapsed into the same watch/prove territory as D4. Replaced with D10, which keeps the vendor stakeholder but shifts the verb to insure/warrant.
- **Closest surviving pairs, judged distinct:** D1 vs D8 (customer-initiated claim repair vs. inter-institution plumbing — different stakeholders, offices, and failure origins); D3 vs D5 (teach pointed at customers vs. at employees); D6 vs D12 (point-in-time origination decision vs. post-origination lifecycle watching/intervening); D7 vs D10 (enabling agent transactions vs. transferring the risk of agent actions — different verbs and buyers); D9 vs D11 (consumer life-event completion vs. ongoing business finance operations).

Axis coverage: front office (D3, D7, D9, D11) / middle office (D2, D6, D12) / back office (D1, D8) / cross-office (D4, D5, D10); retail (D3, D9, D12), commercial (D2, D11), payments (D1, D7), wealth-adjacent guidance (D3), insurance-adjacent (D6, D10), market infrastructure (D8). Stakeholders: institution (D1, D6, D12), customer (D3, D9, D11), counterparty (D2, D8), regulator (D4), vendor (D7, D10), employee (D5). Verbs: repair (D1, D12), negotiate (D2), teach (D3, D5), prove (D4), decide (D6), transact/do (D7, D9, D11), coordinate (D8), insure (D10), watch (D12) — no verb dominates.
