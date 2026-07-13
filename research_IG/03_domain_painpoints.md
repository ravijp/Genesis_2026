# WS3 — Domain Pain Points by Division (Banking + Zenon-Adjacent)

*Research date: 13 Jul 2026 · Workstream 3 of the Genesis 2026 parallel sweep*

## TL;DR — so what for Genesis 2026

Three pains stand out as the most "agent-shaped" (multi-step, judgment-heavy, currently done by a human stitching together 3+ systems) and best matched to Zenon's edge:

1. **Covenant monitoring & annual loan review in commercial/CRE lending** — a $200M-CRE-lender case study shows manual covenant tracking eating **200+ analyst-hours/month, cut to <30 hours/month with automation** [Aloan.ai, 2026](https://aloan.ai/guides/covenant-monitoring-best-practices) — a clean, quantified, rules+ML+document-extraction wedge squarely in Zenon's credit-risk DNA.
2. **AML/fraud alert triage** is the single biggest quantified labor sink in all of banking ops: **90–95% of transaction-monitoring alerts are false positives** [FluxForce, 2024](https://www.fluxforce.ai/statistics/false-positive-rates-transaction-monitoring), each false positive costs **$6–50 in analyst time** [FluxForce, 2025](https://www.fluxforce.ai/blog/why-your-fraud-team-spends-70-of-their-time-on-false-alerts), and the first **20–40 minutes per alert is pure multi-system data-gathering** — exactly the "investigate across systems, then draft a defensible rationale" job an agent (not a dashboard) is built for.
3. **Commercial/corporate onboarding and periodic KYC refresh** is bleeding clients, not just hours: **70% of financial institutions lost clients in the past year to slow onboarding** (up from 67% in 2024, 48% in 2023) [Fenergo, Oct 2025](https://resources.fenergo.com/newsroom/global-financial-institutions-struggle-with-rising-client-losses-and-compliance-costs-as-ai-adoption-increases-fenergo), with UK corporate onboarding regularly exceeding six weeks — a document-chasing + entity-resolution problem, not a policy problem.

Across all six areas the pattern repeats: **the pain is never "we lack a dashboard," it's "someone has to gather facts from 3–8 systems, apply judgment/policy, and write a defensible narrative" — the exact shape of a multi-step agentic workflow**, and precisely where RPA (too rigid) and BI tools (read-only) fall short.

---

## Findings

### A. Retail banking ops

**Pain & owner.** Complaint handling, dispute/chargeback resolution, and account-servicing sit with retail operations and compliance teams. Volume is large and rising: the CFPB received **6.6 million consumer complaints in 2025**, more than double the ~3.2 million in 2024 and ~1.6 million in 2023 [ABA Banking Journal, Apr 2026](https://bankingjournal.aba.com/2026/04/cfpb-received-6-6m-consumer-complaints-in-2025/); credit-card and checking/savings issues are the top retail-banking categories [CFPB Consumer Response Annual Report, May 2025](https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2025-05.pdf).

**Manual process.** (1) Complaint intake across channels (branch, call center, CFPB portal, app); (2) manual triage/categorization against a root-cause taxonomy; (3) case research across core banking, card, and CRM systems; (4) drafting a Reg-E/UDAAP-compliant written response within statutory deadlines; (5) logging root cause for trend reporting to compliance/regulators. For card disputes specifically: intake → **Regulation E investigation**, which the bank must generally complete within **10 business days (extendable to 45 days with provisional credit; up to 90 days for certain debit/foreign-ATM cases)** [CFPB Reg E §1005.11](https://www.consumerfinance.gov/rules-policy/regulations/1005/11/); analysts must assemble evidence, apply liability rules, and issue a written outcome within 3 business days of completing the investigation [Consumer Compliance Outlook, 2025](https://www.consumercomplianceoutlook.org/2025/third-issue/error-resolution-procedures/).

**Quantification.** Each disputed transaction costs financial institutions **$9–10 to process**, and US FIs need roughly **1 FTE per $13–14K of annual dispute volume** — over 200 back-office staff at a typical large FI [Mastercard, 2025](https://www.mastercard.com/us/en/news-and-trends/Insights/2025/what-s-the-true-cost-of-a-chargeback-in-2025.html). A separate 2025 survey finds **each dispute takes 2–3 analyst-hours to assess, gather evidence, and respond**, and **61% of chargeback teams run with only 1–3 staff** [PayCompass, Apr 2025](https://paycompass.com/blog/chargeback-statistics/) — a capacity mismatch against millions of annual complaints/disputes.

**Why it persists.** Complaint/dispute handling requires synthesizing unstructured customer narrative, transaction history, and product-specific liability rules (Reg E, Reg Z) — genuinely a judgment task, not a lookup. Case-management software digitizes the *workflow* but still requires a human to read, research, and draft every case; no incumbent tool reasons across systems and drafts a compliant, evidence-backed response.

**Agentic wedge.** An agent that (1) pulls transaction/account history + prior complaint history automatically, (2) classifies root cause against a taxonomy, (3) checks Reg E/Z liability logic, (4) drafts a compliant response letter with cited evidence, and (5) flags edge cases for human review — collapsing the 2–3 hour manual assembly step while preserving an audit trail. Dashboards can't draft a defensible customer-facing letter; RPA can't handle the judgment calls in liability determination.

---

### B. Lending / Loan operations

**Pain & owner.** Origination doc-checking and underwriting (credit analysts), covenant monitoring (portfolio/credit risk ops), and loan servicing/annual reviews (relationship managers, credit review) are all manual, spreadsheet-and-PDF-driven workflows.

**Manual process — underwriting/spreading.** Analysts extract data from tax returns, financial statements, and bank statements into a standardized spread, then write a credit memo synthesizing the spread, policy checks, risk factors, and a recommendation. **Manual underwriting takes 10–21 days** end-to-end vs. 24–72 hours automated [Amerisave, 2026](https://www.amerisave.com/learn/manual-underwriting-in-complete-guide-to-human-review-mortgage-approval); commercial-loan AI adopters report cutting approval cycles from **12–15 days to 6–8 days (50–75% reduction)** [V7Labs, 2025](https://www.v7labs.com/blog/ai-commercial-loan-underwriting).

**Manual process — covenant monitoring.** Analysts key compliance-certificate figures into spreadsheets, chase missing reports by email, recompute ratios, and compile risk reports quarterly/annually — a process one practitioner describes as "spreadsheet plus email plus PDF folder" with breaches often surfacing at the *next* annual review rather than the quarter they occurred [Aloan.ai, 2026](https://aloan.ai/guides/covenant-monitoring-best-practices). Manual covenant checks take roughly **30–60 minutes per loan** [MightyBot, 2026](https://mightybot.ai/use-cases/covenant-monitoring/), which scales to thousands of hours across a portfolio of hundreds of relationships.

**Quantification.** A **$200M CRE lender's ops team spent 200+ hours/month** on covenant review, chasing reports, and compiling risk reports — reduced to **under 30 hours/month** after automating tracking [Aloan.ai, 2026](https://aloan.ai/guides/covenant-monitoring-best-practices). Credit-memo drafting takes **4–8 hours on a straightforward deal, a full day on a complex one**; AI-assisted memo generation cuts this by ~63%, shifting analyst time to a 30–60 minute review/judgment pass [Abrigo, 2025](https://www.abrigo.com/blog/writing-effective-credit-memos-efficiently/) and financial-spreading vendors [Aloan.ai glossary](https://aloan.ai/glossary/financial-spreading). Financial spreading itself is "historically performed manually in Excel" [Aloan.ai glossary](https://aloan.ai/glossary/financial-spreading); manual, disconnected credit workflows are cited as a direct constraint on lender growth capacity [BeSmartee, 2025](https://www.besmartee.com/blog/manual-credit-workflows-holding-back/).

**Why it persists.** Covenant definitions vary loan-by-loan (what counts as "debt" for a leverage covenant differs by credit agreement), financial statements arrive in inconsistent formats (PDF, scanned, Excel) at inconsistent cadences, and breach detection requires *recalculating* from source financials, not just capturing a submitted number — a reasoning + extraction task existing LOS/covenant-tracking software only partially automates (most still require manual data entry per source, per practitioner accounts above).

**Agentic wedge.** A document-ingestion + recompute agent that reads compliance certificates and financials, recalculates covenant ratios from source data (not trusting the borrower's self-reported number), flags breaches/trending-toward-breach with an explainable rationale, chases missing documents autonomously, and drafts the credit-memo/annual-review narrative — collapsing both the extraction and the write-up steps that today require separate analyst hours.

---

### C. Commercial banking data

**Pain & owner.** Client onboarding data collection and entity data mastering sit with commercial-banking onboarding teams and KYC operations; credit-memo assembly and annual reviews are shared with lending (see B).

**Manual process.** A prospective commercial client is contacted **on average 10 times** during onboarding to submit documents [Forrester Consulting estimate, cited in Fenergo research]; despite this, **52% of treasurers report their bank uses a secure portal** for document exchange — the rest still rely on email (31%) or paper (17%) [Fenergo, 2025]. Behind the scenes, onboarding/KYC ops must resolve the prospective entity against internal records (subsidiaries, beneficial owners, prior relationships) — a master-data "golden record" problem where financial-services firms hold duplicate customer/entity records across onboarding, CRM, trading, risk, and compliance systems with conflicting legal-entity and ownership hierarchies [D&B MDM glossary](https://www.dnb.com/en-us/resources/master-data/what-are-golden-records-in-master-data-management.html); [OpenCorporates, Jun 2025](https://blog.opencorporates.com/2025/06/17/entity-resolution-for-data-aggregators/).

**Quantification.** Traditional document-heavy KYC checks stretch from **two weeks to 6+ weeks for complex corporate cases**, with UK corporate banks frequently exceeding six weeks; **EMEA commercial clients wait 49 days on average** to complete onboarding [Fenergo, Oct 2025](https://resources.fenergo.com/newsroom/global-financial-institutions-struggle-with-rising-client-losses-and-compliance-costs-as-ai-adoption-increases-fenergo). This is now an acute revenue problem, not just an efficiency one: **70% of FIs lost clients in the past year due to slow onboarding** (up from 67% in 2024, 48% in 2023), and **56% of customer drop-offs happen at the KYC stage alone** [Fenergo, Oct 2025]. Periodic KYC review costs **$2,500+ per commercial client** [Corporate Compliance Insights, 2023](https://www.corporatecomplianceinsights.com/kyc-review-cost-survey-2023/); large FIs report **1,000–2,500 employees** dedicated to KYC tasks, with **31–60% of KYC review work still manual** [BAI, 2025](https://www.bai.org/banking-strategies/a-kyc-tipping-point-for-banks-and-steps-your-institution-can-take/).

**Why it persists.** Entity resolution across systems isn't a clean-match problem — it requires reconciling names, addresses, LEIs, beneficial-ownership chains, and household/relationship links with explainable confidence, because false merges create regulatory and credit risk. MDM vendors themselves frame the differentiator as "can it explain who is who, why it thinks that, and what evidence supports the decision" — i.e., the hard part is judgment and evidence, not matching.

**Agentic wedge.** A document-chasing agent (auto-requests, tracks, and validates missing KYC/financial documents against a checklist) paired with an entity-resolution agent that proposes matches/golden records *with cited evidence and confidence*, escalating only genuinely ambiguous cases — turning a 49-day, 10-contact slog into a tracked, mostly autonomous pipeline with a human checkpoint only where risk warrants it.

---

### D. Fraud operations

**Pain & owner.** Fraud alert triage and case investigation sit with fraud-ops analysts; the core pain is alert-volume vs. false-positive burden.

**Manual process.** Rule-based fraud/transaction-monitoring systems fire alerts continuously; an analyst opens each alert and must first gather context from multiple systems (transaction history, device/IP data, prior case notes, customer profile) before making a disposition decision. **The first 20–40 minutes of every alert are spent purely on cross-system data assembly** — described as "the single largest driver of investigation time and cost" [FluxForce, 2025](https://www.fluxforce.ai/blog/why-your-fraud-team-spends-70-of-their-time-on-false-alerts).

**Quantification.** Community banks with legacy rule-based systems process roughly **400 alerts/day across 4 analysts**, and at ~95% false-positive rates and ~4 minutes/alert this is **~25 hours of wasted analyst time per day**; some mid-sized institutions generate **900+ alerts/day** [FluxForce, 2025]. Mid-market false-positive rates commonly run **92–97%** [FluxForce, 2025]; a manually reviewed false positive costs **$6–10 per case** (analyst time + tooling + customer-service calls), so 100,000 alerts/month at an 85% false-positive rate wastes **$510K–$850K/month** [FluxForce, 2025]. Separately, industry estimates put the aggregate cost of false positives at **~$3.5 billion annually** across the industry [Retail Banker International, 2025](https://www.retailbankerinternational.com/comment/hidden-cost-of-aml-how-false-positives-hurt-banks-fintechs-customers/). A team that reviewed 300 alerts/shift can drop to 60–80 after proper triage automation [FluxForce, 2025], implying most of the "work" was noise.

**Why it persists.** Fraud typologies evolve faster than static rules can be retuned, so banks keep thresholds conservative (favoring false positives over missed fraud) — a defensible but labor-expensive trade-off. Existing case-management tools present the alert but don't *do the investigative legwork* (pulling and cross-referencing evidence) — that step remains manual because it requires judgment about which evidence matters for *this* alert type.

**Agentic wedge.** An agent that, on alert creation, autonomously gathers and cross-references the multi-system evidence an analyst would otherwise spend 20–40 minutes assembling, applies a rules+ML risk score with an explainable rationale, drafts a disposition recommendation (close as false positive / escalate / file SAR-adjacent), and only routes genuinely ambiguous or high-risk cases to a human — directly attacking the 90%+ noise share that dashboards can only *display*, not resolve.

---

### E. AML / KYC

**Pain & owner.** Transaction-monitoring alert adjudication, SAR drafting, and periodic KYC refresh/EDD sit with AML compliance operations; regulatory exposure for getting it wrong is severe.

**Manual process.** Alerts from rule-based TM systems are queued for analyst review; analysts research the customer/transaction across systems, decide disposition, and — for confirmed suspicious activity — draft a **SAR narrative** covering the five/six W's (who, what, when, where, why, how), required to be filed within **30 calendar days** of detection in most jurisdictions, with the narrative section deemed the "critical" part of the filing [Abrigo, 2024](https://www.abrigo.com/blog/sar-narrative-writing-best-practices-for-a-strong-aml-cft-program/). Separately, **Enhanced Due Diligence (EDD)** for higher-risk customers requires multi-source screening (adverse media, sanctions, beneficial ownership, source of wealth) and can take **days to weeks manually** [didit.me, 2025](https://didit.me/blog/enhanced-due-diligence-edd-1/).

**Quantification.** **90–95% of AML transaction-monitoring alerts are false positives** per PwC-cited industry benchmarks, with some sources reporting rates as high as 95–99% [FluxForce, 2024](https://www.fluxforce.ai/statistics/false-positive-rates-transaction-monitoring); **fewer than 5% of alerts ever become a filed SAR** [industry benchmark, FluxForce 2024]. Manual alert review costs **$25–50/alert** at mid-size institutions, and banks report spending **$1,500–4,000 per analyst per month** on triage that yields nothing actionable [FluxForce, 2024]. A manual EDD case costs **$500–1,500** to investigate vs. **$50–200 automated (up to ~90% savings)** [didit.me, 2025](https://didit.me/blog/enhanced-due-diligence-edd-1/). At the macro level, global financial institutions spent an estimated **$34.7B on financial-crime-compliance technology and $155.3B on operations in 2024 (~$190B combined)** [Celent, 2024](https://www.celent.com/en/insights/445011014). Enforcement stakes are existential: the **OCC fined TD Bank $450 million** (part of a >$3B combined US penalty) in **Oct 2024** for BSA/AML failures including "hundreds of millions" in unmonitored suspicious transactions and prioritizing growth over controls [OCC, Oct 10 2024](https://www.occ.treas.gov/news-issuances/news-releases/2024/nr-occ-2024-116.html); regulators announced **>36 BSA/AML/CFT enforcement actions in 2024** totaling **>$4.3B in fines** [K&L Gates, Feb 2025](https://www.klgates.com/Lessons-From-2024-Bank-Secrecy-Act-Anti-Money-Laundering-Enforcement-Actions-2-12-2025).

**Why it persists.** Regulatory risk asymmetry (a missed SAR is catastrophic; an over-conservative rule is merely expensive) keeps rule thresholds loose and false-positive volume high; rules must also be auditable and explainable to examiners, which has historically discouraged black-box ML in favor of static, over-inclusive rules.

**Agentic wedge.** An agent that (1) investigates each TM alert across systems and drafts a disposition rationale referencing specific evidence (auditable, examiner-ready), (2) auto-drafts SAR narratives from investigation findings for analyst sign-off, and (3) proactively assembles KYC-refresh/EDD packets (screening results, adverse media, ownership chain) ahead of the review due date rather than waiting for a backlog — converting a reactive, backlogged process into a continuously-refreshed one, with a rules+ML explainability layer that satisfies examiner scrutiny (Zenon's Barclays "Apollo vs. XGBoost" muscle, applied to AML instead of collections).

---

### F. Zenon-adjacent domains

**Subscription/media analytics (churn/renewal/pricing ops).** Digital-media/entertainment churn averages **~6.5%** vs. ~3.8% for SaaS broadly, with streaming churn averaging **6.7% monthly** [Recurly Research, 2025](https://recurly.com/research/churn-rate-benchmarks/); [SubJolt, 2026](https://www.subjolt.com/guides/churn-rate-benchmarks/). The gap between top- and bottom-quartile net revenue retention has widened to **34 percentage points**, and the differentiator is reported to be automation/analytics infrastructure rather than product quality. Pain: cohort-level "why did retention drop" diagnosis is still a manual, ad hoc analyst exercise pulling pricing, marketing-spend, and competitive-event data together — a diagnostic/investigative job distinct from (and complementary to) forward-looking forecasting.

**Asset management (client reporting, performance attribution, data ops).** Portfolio teams spend hours per reporting cycle manually downloading files from multiple custodians, comparing holdings, and investigating discrepancies; reporting breaks most often stem from identifier/mapping gaps, trade-vs-settlement-date timing, inconsistent pricing sources, and stale private-asset valuations [Wealth Mosaic/Infront, 2025](https://www.thewealthmosaic.com/vendors/infront/blogs/stop-wasting-hours-on-client-reports-the-pms-guide/). Linking performance data directly into reports saves **21+ hours/month per user** where automated [Wealth Mosaic/Infront, 2025]. NAV reconciliation against custodians/administrators requires investigating every break (communicating with custodians, brokers, admins) and remains manual at many alternative-fund shops, where "data quality and manual reconciliation remain the leading sources of NAV production delays" [Limina, 2025](https://www.limina.com/blog/pnl-and-nav-reconciliation-guide).

**Credit-risk & collections (strategy analysis, impairment reporting).** Collections strategy analysts build/maintain roll-rate, cure-rate, and flow-rate models and run champion/challenger tests, but practitioner accounts describe risk analysts being pulled into ad hoc "data mining" to patch impairment-reporting problems rather than doing strategy work [FICO blog, 2025](https://www.fico.com/blogs/collections-analytics-are-we-missing-credit-risk-revolution); collections KPI tracking (queue/handle time, roll rates, recovery rates) is still described as a manual-to-digital transition in progress as of 2026 [Bridgeforce, 2026](https://bridgeforce.com/insights/credit-union-collections-kpis-2026/). This is Zenon's own Barclays domain (DQ buckets, roll rates, Apollo-vs-XGBoost, call-center handle/queue/transfer analytics) — call-center operational analytics specifically (handle time, queue time, transfers, callbacks) is adjacent to but distinct from the strategy-copilot angle already captured in I2.

**FP&A forecasting (budget cycles, variance analysis).** Only **31–35% of FP&A time** goes to high-value analysis/storytelling; the rest (**~65–69%**) is manual data gathering, reconciliation, and reporting [FP&A Trends Survey 2024/2025](https://fpa-trends.com/sites/default/files/docs/FPA-Trends-Survey-2024.pdf); **46% of FP&A time** is spent on data collection/validation specifically [GrowCFO Q3 2025 Innovation Report](https://www.growcfo.net/wp-content/uploads/2025/08/Q3-Innovation-Report-Planning-Budgeting.pdf); **29% of companies take >10 days** just to finalize a forecast, and **96% still use spreadsheets** for planning.

**Data-quality/reconciliation (finance vs. ops, regulatory reporting).** Month-end close still takes **120–150 manual hours** across a finance team in a traditional (non-automated) setup, spans **8–10 business days**, and manual-transaction error rates run as high as **23%**; **94% of finance teams still rely on Excel** for close, with 50% citing it as the main cause of delay [Ledge, "State of month-end close 2025"](https://www.ledge.co/content/month-end-close-benchmarks-for-2025). Cash reconciliation alone consumes **30+ hours/month**, and one delayed source pushes back the entire close [Ledge, 2025].

**Why these persist.** Each is a cross-system synthesis-plus-judgment task (reconcile custodian vs. internal ledger, explain a variance, diagnose a churn cohort) that BI/dashboard tools can *surface* (show the number) but not *resolve* (explain why, and what to do) — precisely Zenon's cross-client pattern (DJ, Barclays, Visa, Invesco all involve this same "reconcile, investigate, explain" motion).

**Agentic wedge.** A multi-step agent that pulls from multiple sources (custodian feeds, GL, subscriber cohorts, budget submissions), reconciles/flags discrepancies, forms a root-cause hypothesis, and drafts the explanatory narrative for a human reviewer — the exact motion Zenon already sells as consulting labor, here productized.

---

## Candidate ideas

Tags: `[Align with Zenon]` = rides Zenon's DNA / named client domain / structural edge. `[Recommended]` = passes all 5 hard filters AND scores ≥4 on ZI, TD, FR.

### WS3-A · Covenant Compliance Sentinel
**Name.** Covenant Compliance Sentinel
**One-liner.** An agent that reads compliance certificates and borrower financials, recalculates covenant ratios from source data, flags breaches/trending-toward-breach, and chases missing documents automatically.
**Track.** A
**Zenon anchor.** Barclays (credit-risk, rules+ML explainability, portfolio monitoring) + structural DQ/reconciliation edge.
**Target user/client.** Commercial/CRE loan portfolio ops teams and credit-risk officers at mid-size banks/lenders.
**The pain.** Manual covenant tracking runs 200+ hours/month at a $200M CRE lender, dropping to <30 hours/month once automated [Aloan.ai, 2026](https://aloan.ai/guides/covenant-monitoring-best-practices); breaches often surface only at the next annual review.
**Why it's agentic.** Multi-step: extract financials from heterogeneous documents → recompute (don't trust self-reported figures) → detect trend-toward-breach → autonomously request missing documents → escalate with an explainable rationale.
**Synthetic-data viability.** High — synthetic loan book + covenant schedules + compliance certificates with injected breach scenarios; Zenon already models DQ/roll-rate mechanics.
**6-wk feasibility.** Document extraction (financials + certificates) + ratio recompute engine + breach-detection rules + document-chase workflow, on one synthetic portfolio of ~50 loans.
**Market/competition.** Aloan.ai, MightyBot, BankStride, Termgrid (all funded/emerging point solutions; none show deep rules+ML explainability or Zenon's collections-domain fluency).
**White-space/originality.** Most incumbents automate tracking dashboards; few show *recalculation from source* + autonomous document-chasing + narrative memo drafting combined.
**Rubric quick-score.** ZI 5 · TD 4 · FR 4 · OR 3 · PR 4 → weighted **4.20**
**Tags.** `[Align with Zenon]` `[Recommended]`
**Sources.** [Aloan.ai, 2026](https://aloan.ai/guides/covenant-monitoring-best-practices); [MightyBot, 2026](https://mightybot.ai/use-cases/covenant-monitoring/)

### WS3-B · Credit Memo & Spreading Copilot
**Name.** Credit Memo & Spreading Copilot
**One-liner.** Ingests borrower financials, produces a policy-aligned spread and a full draft credit memo (narrative, risk factors, recommendation) for analyst review.
**Track.** A
**Zenon anchor.** Barclays (credit-risk analytics, explainability) + rules+ML hybrid.
**Target user/client.** Commercial-lending credit analysts / underwriting teams.
**The pain.** Manual spreading is done in Excel; credit-memo drafting takes 4–8 hours (a full day for complex deals) [Abrigo, 2025](https://www.abrigo.com/blog/writing-effective-credit-memos-efficiently/); AI-assisted drafting cuts this ~63%.
**Why it's agentic.** Extract → normalize/spread → apply policy rules → synthesize risk narrative → flag exceptions for human judgment — a plan-execute-verify loop, not a template fill.
**Synthetic-data viability.** High — synthetic borrower financial statements/tax returns across industries and credit tiers.
**6-wk feasibility.** Spreading engine + policy-rule checker + narrative-drafting agent + reviewer UI for one commercial-lending vertical.
**Market/competition.** Aloan, Crediflow AI, Abrigo, BeSmartee — active, funded space; differentiation must be in explainability/audit trail, not novelty.
**White-space/originality.** Moderate — crowded category; win on the reviewer-facing "show your work" audit trail Zenon's validation discipline enables.
**Rubric quick-score.** ZI 4 · TD 3 · FR 4 · OR 2 · PR 4 → weighted **3.55**
**Tags.** `[Align with Zenon]`
**Sources.** [Abrigo, 2025](https://www.abrigo.com/blog/writing-effective-credit-memos-efficiently/); [Aloan.ai glossary](https://aloan.ai/glossary/financial-spreading)

### WS3-C · Commercial Onboarding Orchestrator & Entity Resolver
**Name.** Commercial Onboarding Orchestrator & Entity Resolver
**One-liner.** Agentic document-chaser plus explainable entity-resolution agent that turns commercial KYC onboarding into a tracked, mostly autonomous pipeline.
**Track.** A
**Zenon anchor.** Visa (data-quality/reconciliation), structural DQ/reconciliation edge.
**Target user/client.** Commercial-banking onboarding/KYC ops teams.
**The pain.** 70% of FIs lost clients to slow onboarding in the past year [Fenergo, Oct 2025]; EMEA commercial onboarding averages 49 days; 56% of drop-offs occur at the KYC stage.
**Why it's agentic.** Autonomously tracks required documents per entity type, chases missing items, proposes entity/golden-record matches with cited evidence and confidence scores, escalates only ambiguous matches.
**Synthetic-data viability.** High — synthetic corporate-entity hierarchies with intentional duplicates/near-matches for the resolver to solve.
**6-wk feasibility.** Document-checklist tracker + entity-matching agent (with evidence citations) + escalation workflow for one entity type (e.g., corporate borrower).
**Market/competition.** Fenergo, ncino, Sumsub, Moody's KYC — well-funded incumbents; most are workflow/verification tools, not evidence-explainable entity resolvers.
**White-space/originality.** Moderate-high — the "explainable confidence + evidence trail" framing (vs. black-box matching) is a differentiator few tout explicitly.
**Rubric quick-score.** ZI 4 · TD 4 · FR 3 · OR 3 · PR 3 → weighted **3.55**
**Tags.** `[Align with Zenon]`
**Sources.** [Fenergo, Oct 2025](https://resources.fenergo.com/newsroom/global-financial-institutions-struggle-with-rising-client-losses-and-compliance-costs-as-ai-adoption-increases-fenergo); [OpenCorporates, Jun 2025](https://blog.opencorporates.com/2025/06/17/entity-resolution-for-data-aggregators/)

### WS3-D · Annual Loan Review Assembly Agent
**Name.** Annual Loan Review Assembly Agent
**One-liner.** Assembles the full annual-review package (updated cash-flow analysis, covenant status, risk-rating recommendation, collateral status) for relationship managers ahead of renewal.
**Track.** A
**Zenon anchor.** Barclays (portfolio risk monitoring).
**Target user/client.** Commercial relationship managers / credit review teams.
**The pain.** Annual reviews require reassembling financials, covenant status, and risk ratings before loan maturity; regulatory guidance requires this "typically annually, on renewal" — currently a manual multi-source compilation exercise (see Section B/C).
**Why it's agentic.** Pulls from covenant-monitoring output (WS3-A), credit-memo history, and updated financials; drafts a risk-rating recommendation with rationale — a synthesis-across-time-and-sources task.
**Synthetic-data viability.** High — reuses the same synthetic loan-portfolio dataset as WS3-A.
**6-wk feasibility.** Natural extension of WS3-A; higher risk if built standalone (needs covenant + credit-memo history as inputs) — best scoped as a joint module, which slightly hurts standalone feasibility.
**Market/competition.** Abrigo, Bonadio Group (loan-review-as-a-service), NCUA guidance tooling — mostly services, not agentic products.
**White-space/originality.** Moderate — few dedicated agentic products target *annual review* specifically vs. origination.
**Rubric quick-score.** ZI 4 · TD 3 · FR 3 · OR 3 · PR 3 → weighted **3.30**
**Tags.** `[Align with Zenon]`
**Sources.** [Abrigo](https://www.abrigo.com/blog/risk-based-time-saving-approach-to-annual-loan-review/); [NCUA Examiner's Guide](https://publishedguides.ncua.gov/examiner/Content/ExaminersGuide/Loans/Commercial&MBL/ExamProcedures/ReviewSteps.htm)

### WS3-E · Fraud Alert Investigation Copilot
**Name.** Fraud Alert Investigation Copilot
**One-liner.** On every fraud alert, autonomously gathers and cross-references multi-system evidence, applies a rules+ML risk score with explainable rationale, and drafts a disposition recommendation.
**Track.** A
**Zenon anchor.** Barclays (rules+ML explainability — "Apollo vs. XGBoost" pattern applied to fraud).
**Target user/client.** Fraud-operations teams at retail/community banks.
**The pain.** 92–97% false-positive rates at mid-market banks; ~25 wasted analyst-hours/day at a 4-analyst/400-alert shop; $6–10 wasted cost per false positive; $510K–850K/month wasted at 100K alerts/month [FluxForce, 2025].
**Why it's agentic.** The 20–40 minutes of manual, multi-system evidence-gathering per alert is the exact "investigate, don't just display" task an agent automates; then it must weigh evidence and draft a defensible disposition — not a static rule.
**Synthetic-data viability.** High — synthetic transaction streams with injected true-fraud and false-positive patterns at realistic ratios.
**6-wk feasibility.** Evidence-gathering agent (multi-source synthetic data) + risk-scoring/explainability layer + disposition-drafting on one alert type (e.g., card-not-present fraud).
**Market/competition.** Feedzai, NICE Actimize, SEON, Unit21 — well-funded incumbents with detection models; fewer show the "investigation assembly + explainable disposition draft" agentic framing vs. pure scoring.
**White-space/originality.** Moderate — crowded fraud-detection space, but the evidence-assembly-agent angle (vs. yet another scoring model) is under-marketed.
**Rubric quick-score.** ZI 5 · TD 4 · FR 4 · OR 3 · PR 4 → weighted **4.20**
**Tags.** `[Align with Zenon]` `[Recommended]`
**Sources.** [FluxForce, 2025](https://www.fluxforce.ai/blog/why-your-fraud-team-spends-70-of-their-time-on-false-alerts); [Retail Banker International, 2025](https://www.retailbankerinternational.com/comment/hidden-cost-of-aml-how-false-positives-hurt-banks-fintechs-customers/)

### WS3-F · AML Alert Disposition & SAR Drafting Agent
**Name.** AML Alert Disposition & SAR Drafting Agent
**One-liner.** Investigates transaction-monitoring alerts across systems, drafts an examiner-ready disposition rationale, and auto-drafts SAR narratives for analyst sign-off.
**Track.** A
**Zenon anchor.** Barclays (rules+ML explainability); regulated-domain validation discipline.
**Target user/client.** AML/BSA compliance operations teams at banks.
**The pain.** 90–95% of TM alerts are false positives [FluxForce, 2024]; $25–50/alert manual cost, $1,500–4,000/analyst/month wasted; SAR narratives are legally critical and time-boxed to 30 days [Abrigo, 2024]; enforcement risk is existential (TD Bank's $450M OCC penalty + $3B+ combined, Oct 2024).
**Why it's agentic.** Multi-step investigate-across-systems → weigh evidence with an auditable rules+ML rationale → draft SAR narrative (who/what/when/where/why/how) → route for human sign-off — directly mirrors Zenon's collections explainability pattern, applied to a much higher-stakes domain.
**Synthetic-data viability.** High — synthetic transaction network with embedded true-suspicious patterns (structuring, layering) and injected noise at realistic false-positive ratios.
**6-wk feasibility.** Alert investigation agent + explainability layer + SAR-narrative drafter on one typology (e.g., structuring) with synthetic transaction graph.
**Market/competition.** NICE Actimize, Verafin (Nasdaq), ComplyAdvantage, Unit21 — heavily funded, mature category; Zenon's edge is explainability/audit framing, not detection novelty.
**White-space/originality.** Moderate — crowded but the SAR-narrative-drafting-from-investigation angle (vs. pure alert scoring) is less commoditized.
**Rubric quick-score.** ZI 5 · TD 4 · FR 3 · OR 3 · PR 3 → weighted **3.80**
**Tags.** `[Align with Zenon]`
**Sources.** [FluxForce, 2024](https://www.fluxforce.ai/statistics/false-positive-rates-transaction-monitoring); [OCC, Oct 2024](https://www.occ.treas.gov/news-issuances/news-releases/2024/nr-occ-2024-116.html); [Abrigo, 2024](https://www.abrigo.com/blog/sar-narrative-writing-best-practices-for-a-strong-aml-cft-program/)

### WS3-G · Perpetual KYC Refresh Agent
**Name.** Perpetual KYC Refresh Agent
**One-liner.** Proactively assembles periodic-review and EDD packets (screening, adverse media, ownership chain) ahead of due dates instead of reacting to a backlog.
**Track.** A
**Zenon anchor.** Visa/cross-client DQ discipline; structural synthetic-data edge for sensitive KYC data.
**Target user/client.** AML/KYC operations teams managing periodic-review backlogs at mid-size/regional banks.
**The pain.** KYC review costs $2,500+/commercial client [Corporate Compliance Insights, 2023]; 1,000–2,500 staff typically dedicated to KYC at large FIs with 31–60% still manual [BAI, 2025]; manual EDD costs $500–1,500/case vs. $50–200 automated [didit.me, 2025].
**Why it's agentic.** Continuously monitors trigger events (adverse media, ownership change, risk-tier shift) rather than waiting for a calendar date, assembles the review packet autonomously, and only surfaces genuinely elevated-risk cases — investigate + assemble + prioritize, not just screen.
**Synthetic-data viability.** High — synthetic customer/entity base with simulated adverse-media and ownership-change events.
**6-wk feasibility. ** Trigger-detection agent + packet-assembly + risk-tier prioritization on a synthetic customer base of a few hundred entities.
**Market/competition.** Moody's/Fenergo/kyc360/ComplyAdvantage — well-established KYC-utility vendors; "perpetual KYC" is an emerging framing (2026) most vendors are only now adopting.
**White-space/originality.** Moderate-high — "perpetual" vs. "periodic" KYC is a genuinely emerging (not yet saturated) framing per industry sources.
**Rubric quick-score.** ZI 4 · TD 3 · FR 3 · OR 3 · PR 3 → weighted **3.30**
**Tags.** `[Align with Zenon]`
**Sources.** [BAI, 2025](https://www.bai.org/banking-strategies/a-kyc-tipping-point-for-banks-and-steps-your-institution-can-take/); [Corporate Compliance Insights, 2023](https://www.corporatecomplianceinsights.com/kyc-review-cost-survey-2023/)

### WS3-H · Complaint Root-Cause & Response Drafting Agent
**Name.** Complaint Root-Cause & Response Drafting Agent
**One-liner.** Classifies incoming retail-banking complaints, pulls the relevant account/transaction evidence, and drafts a Reg-E/UDAAP-compliant response within the statutory window.
**Track.** A
**Zenon anchor.** Cross-client DQ/reconciliation + reporting discipline.
**Target user/client.** Retail-banking complaint-handling/compliance ops teams.
**The pain.** CFPB complaints hit 6.6M in 2025 (up from 3.2M in 2024) [ABA Banking Journal, Apr 2026]; each dispute takes 2–3 analyst-hours to assess and respond, with 61% of teams running only 1–3 staff [PayCompass, 2025].
**Why it's agentic.** Classify → gather evidence across core/card/CRM systems → apply liability rules (Reg E/Z) → draft compliant response → flag root cause for trend reporting — synthesis + judgment + drafting, not a canned-response bot.
**Synthetic-data viability.** High — synthetic complaint narratives + account/transaction histories with known ground-truth root causes.
**6-wk feasibility.** Classification + evidence-retrieval + response-drafting on one complaint category (e.g., unauthorized transaction disputes).
**Market/competition.** Quantivate, Kustomer, Zendesk (general case management) — none specialize in Reg-E liability reasoning + compliant drafting.
**White-space/originality.** High — few point solutions combine compliance-rule reasoning with narrative drafting for this specific regulated workflow.
**Rubric quick-score.** ZI 4 · TD 3 · FR 4 · OR 4 · PR 3 → weighted **3.65**
**Tags.** `[Align with Zenon]`
**Sources.** [ABA Banking Journal, Apr 2026](https://bankingjournal.aba.com/2026/04/cfpb-received-6-6m-consumer-complaints-in-2025/); [PayCompass, 2025](https://paycompass.com/blog/chargeback-statistics/)

### WS3-I · Collections Call-Center & Queue Analytics Agent
**Name.** Collections Call-Center & Queue Analytics Agent
**One-liner.** Investigates handle-time, queue-time, transfer, and callback anomalies in collections call-center operations and recommends staffing/script fixes with root-cause explanations.
**Track.** A
**Zenon anchor.** Barclays call-center analytics (handle time, queue time, transfers, callback metrics) — a distinct sub-domain from I2's strategy-copilot framing.
**Target user/client.** Collections operations managers at banks/lenders.
**The pain.** Collections ops is still transitioning from manual to digital-first KPI tracking as of 2026 [Bridgeforce, 2026]; practitioner accounts describe risk analysts pulled into ad hoc "data mining" instead of strategy work when operational reporting breaks [FICO blog, 2025].
**Why it's agentic.** Investigates *why* handle-time or transfer-rate spiked (agent-level, script-level, or portfolio-segment-level root cause), not just reports the metric — the "investigate and explain" motion dashboards can't do.
**Synthetic-data viability.** High — synthetic call-center logs (handle time, transfers, queue) correlated with synthetic collections-portfolio segments.
**6-wk feasibility.** Anomaly-detection + root-cause-investigation agent + narrative report on synthetic call-center + portfolio data.
**Market/competition.** NICE, Genesys (call-center analytics broadly) — general-purpose, not collections-specific; original angle is tying call-center ops metrics to portfolio/DQ segments.
**White-space/originality.** High — this specific intersection (collections-portfolio segment × call-center ops metric root-cause) is not a commoditized product category.
**Rubric quick-score.** ZI 3 · TD 4 · FR 4 · OR 4 · PR 3 → weighted **3.55**
**Tags.** `[Align with Zenon]`
**Sources.** [FICO blog, 2025](https://www.fico.com/blogs/collections-analytics-are-we-missing-credit-risk-revolution); [Bridgeforce, 2026](https://bridgeforce.com/insights/credit-union-collections-kpis-2026/)

### WS3-J · Asset Management Reconciliation & Client-Reporting Agent
**Name.** Asset Management Reconciliation & Client-Reporting Agent
**One-liner.** Reconciles custodian/administrator feeds against the internal ledger, investigates NAV breaks, and auto-drafts the client performance report with an attribution narrative.
**Track.** A
**Zenon anchor.** Invesco (investment analytics, reporting, forecasting support) + Visa-style DQ/reconciliation discipline.
**Target user/client.** Asset-management operations/client-reporting teams at mid-size asset managers or fund administrators.
**The pain.** Reporting breaks stem from identifier/mapping gaps, trade-vs-settlement timing, and stale valuations; automated performance-linking saves 21+ hours/month/user [Wealth Mosaic/Infront, 2025]; NAV reconciliation delays are attributed largely to manual data-quality issues [Limina, 2025].
**Why it's agentic.** Reconcile multi-custodian feeds → investigate each break (form a root-cause hypothesis, not just flag a mismatch) → draft the client-facing attribution narrative — directly extends Zenon's Data-Trust-Agent (I3) pattern into a named, dollar-quantified asset-management workflow.
**Synthetic-data viability.** High — synthetic multi-custodian position/transaction feeds with injected breaks (timing, pricing, identifier mismatches).
**6-wk feasibility.** Reconciliation engine + break-investigation agent + attribution-narrative drafting on one synthetic multi-asset portfolio.
**Market/competition.** FactSet, Confluence, Broadridge, SS&C — large, entrenched incumbents; differentiate on investigative/explainable-break narrative vs. their dashboard-first design.
**White-space/originality.** Moderate — crowded incumbent space, but "investigate the break, don't just flag it" is a genuine agentic differentiator.
**Rubric quick-score.** ZI 4 · TD 4 · FR 3 · OR 3 · PR 3 → weighted **3.55**
**Tags.** `[Align with Zenon]`
**Sources.** [Wealth Mosaic/Infront, 2025](https://www.thewealthmosaic.com/vendors/infront/blogs/stop-wasting-hours-on-client-reports-the-pms-guide/); [Limina, 2025](https://www.limina.com/blog/pnl-and-nav-reconciliation-guide)

### WS3-K · Churn Root-Cause Investigator
**Name.** Churn Root-Cause Investigator
**One-liner.** Given a cohort-level retention drop, autonomously investigates pricing changes, marketing-spend shifts, and competitive events to produce a ranked, evidenced root-cause diagnosis.
**Track.** A
**Zenon anchor.** Dow Jones (subscription/renewal curve expertise) — a diagnostic complement to I1's forecasting focus.
**Target user/client.** Subscription/media-analytics teams at Dow-Jones-like subscription businesses.
**The pain.** Media/digital churn averages ~6.5% (streaming 6.7% monthly) [Recurly Research, 2025]; top/bottom-quartile NRR gap is 34 points, attributed to automation infrastructure, not product quality — implying diagnosis speed is a competitive differentiator.
**Why it's agentic.** Multi-source investigation (pricing, marketing, competitor, seasonality, cohort curves) → hypothesis ranking with evidence → narrative — distinct from I1's forward-looking forecast/scenario focus; this is backward-looking diagnosis.
**Synthetic-data viability.** High — Zenon already knows renewal/save/stick curve shapes; inject synthetic shocks (price change, campaign pause) and have the agent recover the cause.
**6-wk feasibility.** Cohort-drop-detection + multi-source hypothesis agent + evidenced narrative on one synthetic subscription business.
**Market/competition.** ChartMogul, Amplitude, Recurly (churn dashboards) — descriptive only; none do agentic root-cause investigation with ranked hypotheses.
**White-space/originality.** High — genuinely differentiated from dashboard-first churn tools and from I1's forecasting focus.
**Rubric quick-score.** ZI 4 · TD 4 · FR 4 · OR 4 · PR 4 → weighted **4.00**
**Tags.** `[Align with Zenon]` `[Recommended]`
**Sources.** [Recurly Research, 2025](https://recurly.com/research/churn-rate-benchmarks/); [SubJolt, 2026](https://www.subjolt.com/guides/churn-rate-benchmarks/)

### WS3-L · Budget Assembly & Variance Investigation Agent
**Name.** Budget Assembly & Variance Investigation Agent
**One-liner.** Consolidates bottom-up budget submissions from business units, reconciles them against top-down targets, and investigates/explains variances as they emerge.
**Track.** A
**Zenon anchor.** Dow Jones (FP&A, forecasting, GAAP-vs-management reconciliation) — a budget-cycle-assembly complement to I1's subscriber-forecast focus.
**Target user/client.** FP&A teams running annual/quarterly budget cycles.
**The pain.** Only 31–35% of FP&A time is high-value analysis; 65–69% is manual data-gathering/reconciliation [FP&A Trends Survey 2024/2025]; 29% of companies take >10 days to finalize a forecast; 96% still use spreadsheets.
**Why it's agentic.** Consolidate multi-BU submissions → detect inconsistent assumptions/definitions across units → investigate variance drivers → draft the variance narrative for leadership — a reconcile-investigate-explain loop, not a rollup macro.
**Synthetic-data viability.** High — synthetic multi-BU budget submissions with intentionally inconsistent assumptions for the agent to catch.
**6-wk feasibility.** Consolidation engine + inconsistency-detection + variance-narrative agent on synthetic multi-BU data for one planning cycle.
**Market/competition.** Datarails, Vena, Planful, Workday Adaptive — established FP&A software; differentiator is the agentic "catch inconsistent assumptions + explain variance" layer vs. their rollup/reporting focus.
**White-space/originality.** Moderate — crowded FP&A-software space; overlaps meaningfully with I1 (flag in synthesis).
**Rubric quick-score.** ZI 4 · TD 3 · FR 3 · OR 2 · PR 3 → weighted **3.15**
**Tags.** `[Align with Zenon]`
**Sources.** [FP&A Trends Survey 2024](https://fpa-trends.com/sites/default/files/docs/FPA-Trends-Survey-2024.pdf); [GrowCFO Q3 2025](https://www.growcfo.net/wp-content/uploads/2025/08/Q3-Innovation-Report-Planning-Budgeting.pdf)

### WS3-M · Month-End Close Reconciliation Agent
**Name.** Month-End Close Reconciliation Agent
**One-liner.** Reconciles finance-vs-ops ledgers during month-end close, investigates each break, and drafts a prioritized close-exceptions report with suggested journal entries.
**Track.** A
**Zenon anchor.** Visa (data-quality validation) + cross-client reconciliation pattern — a close-cycle-specific instance of I3 (Data-Trust Agent).
**Target user/client.** Corporate controllership/finance-ops teams.
**The pain.** Traditional month-end close takes 120–150 manual hours over 8–10 business days with error rates up to 23%; 94% of teams still rely on Excel; cash reconciliation alone takes 30+ hours/month [Ledge, 2025].
**Why it's agentic.** Reconcile multiple ledgers/sources → investigate each break with a root-cause hypothesis → propose (not auto-post) correcting entries → prioritized report — same motion as I3 but scoped tightly to the close cycle with a controller-facing deliverable.
**Synthetic-data viability.** High — synthetic GL + sub-ledger data with injected timing/mapping/duplicate errors.
**6-wk feasibility.** Very high — narrowly scoped, reuses I3's reconciliation core with a close-specific narrative/report template.
**Market/competition.** BlackLine, FloQast, Trintech — mature, well-funded close-automation incumbents; must differentiate on investigative narrative depth, not just matching.
**White-space/originality.** Low-moderate — most overlaps with I3; best framed as I3's flagship vertical use case rather than a standalone idea.
**Rubric quick-score.** ZI 4 · TD 3 · FR 5 · OR 2 · PR 3 → weighted **3.55**
**Tags.** `[Align with Zenon]`
**Sources.** [Ledge, "State of month-end close 2025"](https://www.ledge.co/content/month-end-close-benchmarks-for-2025)

---

## Notes for synthesis

**Suspected overlaps with I1–I10:**
- WS3-K (Churn Root-Cause Investigator) and WS3-L (Budget Assembly & Variance Investigation) both sit close to **I1 (Forecast Copilot)** — they're diagnostic/backward-looking complements to I1's forward-looking forecasting; if I1 is chosen, these could become *features* of it (a "why did the forecast miss" mode) rather than separate builds.
- WS3-A (Covenant Compliance Sentinel), WS3-B (Credit Memo Copilot), WS3-D (Annual Loan Review), and WS3-I (Collections Call-Center Analytics) all sit in the same credit-risk family as **I2 (Credit-Risk/Collections Strategy Copilot)**. WS3-A is the most differentiated and best-quantified of the four — recommend it as I2's strongest alternative/extension, or a sharper wedge than I2 if the team wants a narrower, better-quantified scope.
- WS3-M (Month-End Close Reconciliation) and, to a lesser extent, WS3-C (Onboarding Entity Resolver) and WS3-J (Asset Management Reconciliation) are all specific verticals of **I3 (Data-Trust Agent)**. This suggests I3's biggest strategic choice isn't *whether* to build a reconciliation agent but *which vertical* to demo it on — WS3-A (covenants) and WS3-E/F (fraud/AML alert investigation) have the most dramatic, best-cited hour/cost quantification of the whole set and would make the strongest I3-style demo verticals.
- WS3-E (Fraud Alert Investigation) and WS3-F (AML Disposition/SAR Drafting) are new territory not covered by I1–I10 — closest conceptual cousin is I2's rules+ML explainability pattern, but applied to a much higher-stakes, higher-volume workflow (90-95% noise) with clearer $ quantification than any existing idea in the deck.
- WS3-G (Perpetual KYC) and WS3-C (Onboarding Orchestrator) are also net-new territory, closest to I3 in mechanism (reconcile/investigate) but with onboarding/KYC as the named vertical.

**Highest-stakes findings:**
1. **Fraud/AML alert triage is the largest, best-quantified labor sink uncovered in this entire sweep** — 90–97% false-positive rates, $6–50 per-alert waste, $510K-850K/month at just 100K alerts, and ~25 analyst-hours/day wasted at a single 4-person team [FluxForce, 2025]. If Genesis 2026 wants the single most defensible "$ saved" story for the judging rubric's 25%-weighted Zenon-impact criterion, WS3-E/F (fraud/AML investigation agents) likely beat every other candidate across all five research workstreams on raw quantification — but they carry the highest regulatory-sensitivity/compliance-perception risk of anything in this set, so framing as strictly "decision-support, not decisioning" (as I2 already does) is essential.
2. **Onboarding/KYC friction is now a revenue-loss story, not just a cost story**: 70% of FIs lost clients to slow onboarding in the past year, up from 67% (2024) and 48% (2023) [Fenergo, Oct 2025] — a clean, escalating trend line that makes a compelling "cost of doing nothing" chart for a pitch deck, and one none of I1–I10 currently cites.
