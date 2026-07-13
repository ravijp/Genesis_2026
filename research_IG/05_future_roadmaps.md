# WS5 — Where Banks & Finance Are Taking Agentic AI (2025–2026)

**Date:** 13 Jul 2026 · **Workstream:** WS5 (forward-looking roadmaps & stall-points) · **Track focus:** A (finance client-facing)

**TL;DR — so what for Genesis 2026:** Every major bank we checked (JPMorgan, Goldman, Citi, BofA, Morgan Stanley, Wells Fargo, HSBC, BNY, Barclays) has moved from "GenAI chatbot" to a named **agentic-AI platform** in the last 12 months, and Evident Insights measures agentic use cases jumping from **15% to ~32% of all reported bank AI use cases in a single quarter (Q4 2025 → Q1 2026)** [Evident Insights, Q1 2026](https://evidentinsights.com/insights/banking-use-case-trends-q1-2026) — this is happening *now*, not a 2027 story. But two things are stalling in lockstep with that speed: **(1) the regulators have explicitly punted** — the first Fed/OCC/FDIC model-risk-management rewrite in 15 years (SR 26-2, Apr 2026) **excludes generative and agentic AI from its scope**, telling banks their own governance must fill the gap [Federal Reserve SR 26-2, Apr 2026](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf); and **(2) McKinsey, Deloitte and Wells Fargo's own hiring decisions** all independently name the same failure mode — "pilot purgatory," fragmented data foundations, and legacy systems that can't absorb autonomous agents [McKinsey, Feb 2026](https://www.mckinsey.com/capabilities/operations/our-insights/the-paradigm-shift-how-agentic-ai-is-redefining-banking-operations). Both gaps are exactly the kind of validation-discipline, rules+ML-explainability, and reconciliation work Zenon already does for Dow Jones, Barclays and Visa — the market is asking, in public statements, for precisely what Zenon's DNA supplies.

---

## 1. Named-program table (institution / initiative / status / function / source)

| Institution | Initiative | Status (mid-2026) | Function | Source, date |
|---|---|---|---|---|
| **JPMorgan Chase** | LLM Suite (OpenAI + Anthropic models, model-agnostic) | Live — 250,000 employees; 450+ use cases in production, targeting **1,000 by end of 2026**; agent layer ("execute complex workflows") rolling out next | Enterprise-wide: compliance drafting, research, client service | [Forbes, Jul 2026](https://www.forbes.com/sites/bernardmarr/2026/07/01/how-jpmorgan-chase-is-building-the-ai-powered-bank-of-the-future/); [CompleteAITraining, 2026](https://completeaitraining.com/news/jpmorgans-agentic-ai-rollout-with-openai-and-anthropic/) |
| **JPMorgan** | Agentic asset-allocation research (8 agents vs. 60/40 benchmark) | **Research/backtest only** — strategists explicitly "wary to hand off asset-allocation decision-making to an agent" | Markets research / asset mgmt | [Bloomberg, 9 Jul 2026](https://www.bloomberg.com/news/articles/2026-07-09/jpmorgan-builds-ai-agents-that-beat-60-40-portfolio-in-backtests) |
| **Goldman Sachs** | GS AI Assistant + GS AI Platform (routing layer across model vendors) | Live firmwide since Jun 2025; CIO (Feb 2026) says **autonomous agents entering production soon** for trade accounting, due-diligence review, client onboarding | Banker productivity → agentic ops | [CNBC, 21 Jan 2025](https://www.cnbc.com/2025/01/21/goldman-sachs-launches-ai-assistant.html); [Bankers' Magazine, Feb 2026](https://bankersmagazine.com/ai-banking/articles/goldman-ai-architecture/) |
| **Morgan Stanley** | AI @ Morgan Stanley Debrief; agentic access to ShareWorks/Equity Edge via MCP | Debrief live for advisors; external-agent access **piloted with a handful of clients**, opening to all 3,400 stock-admin clients "next year" | Wealth advisor tools; stock-plan administration | [CNBC, 3 Jun 2026](https://www.cnbc.com/2026/06/03/ai-agents-morgan-stanley-wealth-management-funnel.html); [OpenAI case study](https://openai.com/index/morgan-stanley/) |
| **Citi** | Arc (agent "operating system"); Citi Sky (wealth) | Arc launched **Apr 2026**, developer-only rollout first, all agents "monitored, auditable, governed"; Citi Sky phased to Citigold clients from summer 2026 | Cross-functional agent building; wealth client service | [Axios, 30 Apr 2026](https://www.axios.com/2026/04/30/exclusive-citi-moves-into-agentic-ai); [CIO Dive, 2026](https://www.ciodive.com/news/citi-launches-arc-scale-ai-agents/819113/) |
| **Bank of America** | Erica (2nd-gen architecture) + agentic PoCs | Live 7+ yrs — 20.6M users, 169M+ interactions/quarter; **agentic PoCs** underway to expand what Erica can resolve | Retail/consumer servicing | [Fortune, 17 Mar 2026](https://fortune.com/2026/03/17/inside-bank-of-americas-build-once-ai-strategy/); [PYMNTS, 2026](https://www.pymnts.com/earnings/2026/erica-ai-and-digital-drive-operating-leverage-at-bank-of-america/) |
| **Wells Fargo** | Google Agentspace; CIB FX post-trade-inquiry agent | Piloting → scaling; **hired an AWS exec (Feb 2026) with the explicit mandate to move agentic AI "from pilots to scale"** | Corporate/investment banking ops | [CompleteAITraining, Feb 2026](https://completeaitraining.com/news/wells-fargo-taps-aws-exec-faraz-shafiq-to-take-agentic-ai/); [Google Cloud blog](https://cloud.google.com/blog/topics/financial-services/wells-fargo-agentic-ai-agentspace-empowering-workers) |
| **HSBC** | Google Cloud / Gemini Enterprise Agent Platform partnership | Announced 17 Jun 2026; targets 200+ new use cases over 2 years | Wealth mgmt, financial-crime detection, employee decision support | [HSBC press release, 17 Jun 2026](https://www.hsbc.com/news-and-views/news/media-releases/2026/hsbc-and-google-cloud-announce-transformative-ai-banking-partnership) |
| **Barclays** | Copilot rollout + GenAI call summarization; "governed autonomy" strategy | 50,000 colleagues on Copilot, doubling early 2026; 8M+ customer calls summarized since Oct 2025; **agentic AI still framed as the 2026 frontier, not yet delivered** | Colleague productivity, customer service | [Barclays Private Bank, Nov 2025](https://privatebank.barclays.com/insights/ai-outlook-2026-11-2025/); [home.barclays, Jul 2025](https://home.barclays/insights/2025/07/scaling-AI-at-Barclays/) |
| **BNY** | Eliza 2.0 multi-agent platform | Live — 20,000 "Empowered Builders" + 130+ autonomous "Digital Employees" (announced 16 Jan 2026); legal review time −75%, financial planning time −60% | Legal, financial planning, trade settlement | [OpenAI case study](https://openai.com/index/bny/); [TokenRing/Times-Online, 16 Jan 2026](https://business.times-online.com/times-online/article/tokenring-2026-1-16-bny-mellon-scales-the-agentic-era-with-deployment-of-20000-ai-assistants) |
| **HDFC Bank (India)** | Neev (in-house GenAI platform) + custom fraud-detection system | Deployed Jul 2026, part of a $1B FY26 tech-investment push | Customer service, lending, fraud, ops | [BusinessToday, 11 Jul 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/hdfc-bank-bets-big-on-ai-with-in-house-genai-platform-neev-plans-to-transform-customer-service-lending-and-operations-542375-2026-07-11) |
| **FIS (vendor)** | Agentic AI with Anthropic, starting with financial crimes | Launched 2026 | AML/financial-crime case investigation | [FIS press release, 2026](https://www.fisglobal.com/about-us/media-room/press-release/2026/fis-brings-agentic-ai-to-banking-with-anthropic-starting-with-financial-crimes) |

**Read on status:** almost nothing above is "fully autonomous in production." The honest pattern is: **firmwide GenAI copilots are live; agentic layers are in controlled pilots, developer-only rollouts, or "entering production soon" statements** — i.e., 2026 is the year the *press releases* caught up to "agentic," but the operational reality is still narrow, governed, function-specific automation (financial crime, trade ops, DD review, call summarization) rather than broad autonomous decision-making.

## 2. Exec / strategy statements on agentic AI specifically

- **Goldman Sachs CIO (Marco Argenti), Feb 2026:** autonomous agents "entering production soon," naming **trade accounting, due-diligence review, and client onboarding** first — a deliberately narrow, auditable starting list [Bankers' Magazine, Feb 2026](https://bankersmagazine.com/ai-banking/articles/goldman-ai-architecture/).
- **JPMorgan strategists, Jul 2026:** agentic asset-allocation agents beat the 60/40 benchmark in backtests, yet the team is explicitly "wary to hand off asset-allocation decision-making to an agent" — a rare public admission of trust lagging capability [Bloomberg, 9 Jul 2026](https://www.bloomberg.com/news/articles/2026-07-09/jpmorgan-builds-ai-agents-that-beat-60-40-portfolio-in-backtests).
- **Citi (Arc launch), Apr 2026:** explicit governance framing — "all agents operating on Arc will be monitored, auditable, and governed," with Citi retaining visibility into "what each agent does, how it operates, and the value it generates" [CIO Dive / Citigroup, 2026](https://www.citigroup.com/global/news/perspectives/2026/introducing-ai-agents-next-phase-citi-artificial-intelligence-journey).
- **Barclays Private Bank, "AI Outlook 2026" (Nov 2025):** "the most credible outlook for 2026 is not a world of fully autonomous super-agents, but **governed autonomy** operating at scale" — arguably the single clearest exec articulation of the market's actual 2026 ambition level [Barclays Private Bank, Nov 2025](https://privatebank.barclays.com/insights/ai-outlook-2026-11-2025/ai-in-2026-smarter-not-bigger/).
- **Wells Fargo's own org chart is a strategy statement:** hiring an AWS executive in Feb 2026 with the stated mandate to take agentic AI "from pilots to scale" is a bank admitting, structurally, that it has a pilot-to-production problem it needs outside expertise to solve [CompleteAITraining, Feb 2026](https://completeaitraining.com/news/wells-fargo-taps-aws-exec-faraz-shafiq-to-take-agentic-ai/).

## 3. Analyst / consultancy forward view

- **McKinsey ("The paradigm shift," Feb 2026):** 50 of the world's largest banks announced **160+ agentic use cases in 2025 alone**; early deployments cut manual workloads 30–50%; but slow adopters risk **"pilot purgatory"** — narrow use cases that never scale [McKinsey, 27 Feb 2026](https://www.mckinsey.com/capabilities/operations/our-insights/the-paradigm-shift-how-agentic-ai-is-redefining-banking-operations).
- **McKinsey (AI in Asia):** ~80% of Asian financial institutions report using AI, but a similar share report **no bottom-line impact yet** — adoption and value realization have decoupled [McKinsey, 2026](https://www.mckinsey.com/capabilities/operations/our-insights/ai-in-asia-reimagining-banking-operations-through-agentic-ai).
- **Deloitte ("Agentic AI in banking," 14 Aug 2025):** implementation is "throttled by brittle and fragmented data foundations, mounting compliance demands, outdated legacy systems, and internal resistance to change," leaving many initiatives "stuck in isolated proofs of concept, marked by weak governance, duplication, and uneven impact" [Deloitte, 14 Aug 2025](https://www.deloitte.com/us/en/insights/industry/financial-services/agentic-ai-banking.html).
- **Deloitte ("Managing the new wave of risks from AI agents in banking"):** agent autonomy creates risk categories that **existing risk-management frameworks may not fully address** [Deloitte, 2026](https://www.deloitte.com/us/en/insights/industry/financial-services/agentic-ai-risks-banking.html).
- **Gartner (2026 CIO Survey):** only **17% of organizations have deployed AI agents**, but **60%+ expect to within two years** — the steepest adoption curve of any technology in the survey; Gartner projects 40% of enterprise apps will embed task-specific agents by end of 2026 [Gartner, 2026](https://www.gartner.com/en/documents/7201830).
- **Gartner (2026 Hype Cycle for Agentic AI):** a defining 2026 signal is the emergence of **governance-, security-, and cost-focused profiles alongside core agentic technologies** — i.e., the market itself is now pricing in the need for oversight tooling, not just agent frameworks [Gartner, 2026](https://www.gartner.com/en/articles/hype-cycle-for-agentic-ai).
- **Evident Insights (Q1 2026 Banking Use-Case Trends):** agentic applications went from **15% of reported use cases (Q4 2025) to ~32% (Q1 2026)**; Anthropic was the most-referenced model vendor; a long tail of specialist vendors (beyond hyperscalers) now account for **68% of deployments**, concentrated in **credit, AML and treasury** [Evident Insights, 2026](https://evidentinsights.com/insights/banking-use-case-trends-q1-2026).
- **Celent:** agentic AI has "moved out of the demo and into procurement," but for established banks the real challenge is placing autonomous reasoning **on top of decades-old core ledgers, custodial systems and compliance pipelines without weakening controls** [Celent, 2026](https://www.celent.com/en/insights/shedding-light-on-agentic-ai-in-banking).
- **BCG (Global Asset Management Report 2026):** agentic systems could free **35–50% of capacity** in servicing/reporting/onboarding and deliver **25–35% cost reduction**, but "lasting agentic advantage primarily requires changes to the operating model, talent, and processes... not data and technology alone" [BCG, 2026](https://www.bcg.com/publications/2026/rebuilding-asset-management-for-an-ai-first-world).

## 4. Where it's stalling — and the wedge each struggle opens

| Struggle (documented) | Evidence | Wedge for Zenon |
|---|---|---|
| **Regulators explicitly excluded agentic AI from the first MRM rewrite in 15 years** | Fed/OCC/FDIC SR 26-2 & OCC Bulletin 2026-13 (17 Apr 2026) state gen/agentic AI models are "novel and rapidly evolving" and **out of scope**, while confirming banks' own risk-management practices must still govern them [Federal Reserve SR 26-2, Apr 2026](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf); [OCC Bulletin 2026-13](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html); [Sullivan & Cromwell memo, Apr 2026](https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management) | Banks need a **self-built governance/validation harness** now, ahead of formal rules — exactly Zenon's rules+ML-explainability and validation-discipline muscle (Barclays CLD/Apollo-vs-XGBoost pattern). |
| **FINRA names agent auditability as a top-4 supervisory risk** | FINRA 2026 Annual Regulatory Oversight Report (9 Dec 2025): "complicated, multi-step agent reasoning tasks can make outcomes difficult to trace or explain"; recommends logging, human-in-the-loop checkpoints, and ongoing testing [FINRA, 9 Dec 2025](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai) | A market for **agent-decision audit trails / evidence chains** — turning an opaque multi-step reasoning chain into a reviewable, cited narrative (same discipline as Zenon's QC/reconciliation reports). |
| **Fragmented, brittle data foundations throttle agentic rollout** | Deloitte, Aug 2025: legacy systems and weak data-integration protocols "complicate deployment"; many initiatives "stuck in isolated proofs of concept" [Deloitte, Aug 2025](https://www.deloitte.com/us/en/insights/industry/financial-services/agentic-ai-banking.html) | Directly maps to Zenon's DQ/reconciliation edge (I3) — a pre-deployment "agent-readiness" data grader is a natural, provable wedge. |
| **Legacy core systems can't simply be re-platformed for autonomous agents** | Celent, 2026: decades-old ledgers/custodial/compliance pipelines mean the real question is "how to place autonomous reasoning on top of a highly governed estate without weakening controls" [Celent, 2026](https://www.celent.com/en/insights/shedding-light-on-agentic-ai-in-banking) | Rules+ML hybrid design (business rules as the "governed" layer, ML/LLM as the reasoning layer) is precisely Zenon's structural answer. |
| **A named exec hire exists solely to solve "pilots not reaching production"** | Wells Fargo hired an AWS exec in Feb 2026 explicitly to move agentic AI "from pilots to scale, with controls and measurable outcomes" [CompleteAITraining, Feb 2026](https://completeaitraining.com/news/wells-fargo-taps-aws-exec-faraz-shafiq-to-take-agentic-ai/) | Validates I9-style eval/production-readiness offerings as *not* speculative — a bank is already budgeting headcount around exactly this gap. |
| **Real hallucination incidents with real financial/reputational cost** | Deloitte's Australian arm refunded part of a A$290K government report after AI-fabricated citations and a fake court quote were found (Oct 2025) [Fortune, 7 Oct 2025](https://fortune.com/2025/10/07/deloitte-ai-australia-government-report-hallucinations-technology-290000-refund/); [OECD.AI incident record](https://oecd.ai/en/incidents/2025-10-05-be45) | A vivid, citable cautionary tale for *any* consultancy shipping AI-authored deliverables — underscores why Zenon's own "validated, cited, gap-honest" design principle (see I6) is a differentiator, not a nice-to-have. |
| **Consumer trust is the explicit gating factor for the newest frontier (agentic commerce)** | 95% of consumers express at least one concern about AI-driven purchasing even as Visa/Mastercard build tokenized agent-payment rails [Payments Dive / PYMNTS, 2026](https://www.paymentsdive.com/news/visa-mastercard-race-agentic-ai-commerce-payments/750428/) | A brand-new fraud surface (agent-initiated transactions) with no established monitoring playbook yet — white space for a Visa-anchored idea. |
| **GenAI maturity has outpaced agentic maturity in asset/wealth management** | EY 2025 study: 95% of wealth/asset managers report scaling GenAI, only 78% are even exploring agentic AI — a real maturity gap one layer up [cited via Microsoft Cloud blog, Jun 2026](https://www.microsoft.com/en-us/microsoft-cloud/blog/financial-services/2026/06/16/trust-as-infrastructure-how-agentic-ai-is-rearchitecting-asset-management-at-scale/) | Invesco-anchor opportunity: firms behind the agentic curve need a concrete, low-risk first use case (client reporting/commentary) rather than a full autonomy leap. |

## 5. Adjacent-vertical view (subscription/media & asset management)

- **Dow Jones / News Corp:** CEO Almar Latour is building "the stack" (news + data + analytics + events) targeting **$1B Dow Jones EBITDA within 5 years**; Factiva has licensed **8,000+ premium sources for GenAI use**, and a licensing deal with Meta is reportedly worth **~$50M/year**; an AI publishing tool-chain (with Symbolic.ai, announced Jan 2026) reportedly yielded **up to 90% productivity gains on complex research tasks** [Axios, 16 Mar 2026](https://www.axios.com/2026/03/16/dow-jones-news-corp); [Yahoo Finance, 2026](https://finance.yahoo.com/sectors/technology/articles/news-corp-touts-ai-deals-110454635). Digital subscriptions still grew 12% YoY to 6M in Q2 FY26, WSJ digital-only up 11% to 4.3M — the subscription-forecasting engagement Zenon already knows is scaling, not shrinking.
- **Streaming/subscription churn:** Netflix holds the lowest monthly churn among premium streamers at ~2% [MediaPost, 26 Jun 2026](https://www.mediapost.com/publications/article/416128/netflix-monthly-subscriber-churn-still-leads-at-2.html); the 2026 narrative is agentic churn-prediction and dynamic-pricing agents, plus automated payment-retry workflows to cut *involuntary* churn from failed renewals [TV Tech, 2026](https://www.tvtechnology.com/insights/opinion/streamings-subscription-reset-why-agentic-ai-will-decide-the-next-phase-of-growth).
- **Asset management:** BCG's 2026 Global Asset Management Report projects agentic systems could free **35–50% of servicing/reporting capacity** and deliver **25–35% cost reduction**, but stresses the bottleneck is operating-model change, not technology [BCG, 2026](https://www.bcg.com/publications/2026/rebuilding-asset-management-for-an-ai-first-world). BlackRock shipped a narrow, concrete slice of this — **Aladdin Wealth Auto Commentary** (Jun 2026), automating portfolio-risk narrative writing for advisors — rather than broad autonomy [BlackRock/Aladdin, 2026]. Invesco's own 2026 outlook stays cautious on AI *software* exposure (favoring semiconductors/hardware), a useful signal that even AI-forward asset managers are hedging on where the value actually lands [PRNewswire, 2026](https://www.prnewswire.com/news-releases/invesco-releases-2026-midyear-investment-outlook-focused-on-resilient-economy-302800305.html).
- **Payments (Visa/Mastercard):** both networks are racing to build "agentic commerce" rails — tokenized credentials, agent identity, real-time authorization — with Visa partnering with OpenAI (Jun 2026) and Mastercard's Agent Pay live in Malaysia/Singapore [Payments Dive, 2026](https://www.paymentsdive.com/news/visa-mastercard-race-agentic-ai-commerce-payments/750428/); McKinsey/ICSC project **$1T US / $3–5T global agentic-retail revenue by 2030**, but 95% of consumers voice at least one trust concern — governance/monitoring for this new transaction type is still unbuilt.

---

## Candidate ideas

12 Track A candidates derived from the roadmap gaps and stall-points above. IDs `WS5-A` … `WS5-L` (temporary; renumbered I11+ at synthesis).

### WS5-A · Agentic-AI Model-Risk & Audit-Trail Pack ("MRM-for-Agents")
- **One-liner:** An agent that continuously tests a bank's other agents against a governance ruleset modeled on FINRA's 4 risk vectors and the SR-26-2 gap, producing an audit-ready compliance report before a regulator asks.
- **Track:** A
- **Zenon anchor:** Barclays rules+ML explainability pattern; validation/QC discipline (cross-client structural edge).
- **Target user/client:** Model-risk/compliance officers at a mid-size bank rolling out its first production agents.
- **The pain:** SR 26-2 (Apr 2026) explicitly excludes gen/agentic AI from formal MRM scope, and FINRA (Dec 2025) flags "auditability of multi-step reasoning" as a top supervisory risk — banks must self-govern with no template, and today do it with slow, manual documentation.
- **Why it's agentic:** A supervisor-agent ingests another agent's action/tool-call logs plus a policy ruleset, plans a battery of adversarial/compliance tests (scope creep, unauthorized data access, missing human checkpoints), executes them, and synthesizes a cited violation report with severity ranking — genuine multi-step investigation, not a static checklist.
- **Synthetic-data viability:** High — synthetic agent action logs + a synthetic policy corpus (mirroring FINRA's 4 vectors) are easy to generate and inject known violations into for a compelling demo.
- **6-wk feasibility:** Yes — scope to one target agent type (e.g., a customer-service agent) + one policy ruleset; output a scorecard + narrative report.
- **Market/competition:** Emerging vendors (Credo AI, TrustLogix, Galileo, Patronus AI) — mostly US enterprise-wide AI-governance platforms, not banking-specific with a rules+ML explainability lens.
- **White-space/originality:** High near-term — the regulatory vacuum is brand new (Apr 2026); very few packaged offerings map directly to SR-26-2 / FINRA's specific risk taxonomy yet.
- **Rubric quick-score:** ZI 5 · TD 4 · FR 4 · OR 4 · PR 4 → weighted **4.25**
- **Tags:** `[Align with Zenon]` `[Recommended]`
- **Sources:** [Federal Reserve SR 26-2, Apr 2026](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf) · [FINRA 2026 Oversight Report, 9 Dec 2025](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai) · [Sullivan & Cromwell memo, Apr 2026](https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management)

### WS5-B · Agent-Readiness Data Grader
- **One-liner:** Before a bank deploys an agent on a dataset, score that dataset's "agent-readiness" (schema clarity, freshness, lineage, access control, known-error density) and produce a remediation backlog.
- **Track:** A
- **Zenon anchor:** Data-Trust/reconciliation edge (I3 pattern); cross-client DQ discipline (DJ, Barclays, Visa).
- **Target user/client:** Data/AI platform teams at banks about to greenlight a new agentic use case.
- **The pain:** Deloitte (Aug 2025): agentic rollout is "throttled by brittle and fragmented data foundations" — teams discover this only after an agent misbehaves in production.
- **Why it's agentic:** Profiles the target dataset, forms hypotheses about likely failure modes for the *specific* intended agent task, runs targeted checks, and produces a prioritized go/no-go readiness report — an investigative pre-flight, not a generic profiler.
- **Synthetic-data viability:** High — inject realistic freshness/lineage/schema defects into synthetic tables.
- **6-wk feasibility:** High — reuses much of the I3 pattern, scoped to a "readiness gate" output format.
- **Market/competition:** Overlaps generic data-quality tooling (Monte Carlo, Great Expectations) — none frame it as an agent-specific pre-deployment gate.
- **White-space/originality:** Moderate — mostly a repackaging of data-quality tooling with an agent-specific lens.
- **Rubric quick-score:** ZI 4 · TD 3 · FR 5 · OR 2 · PR 3 → weighted **3.60**
- **Tags:** `[Align with Zenon]`
- **Sources:** [Deloitte, 14 Aug 2025](https://www.deloitte.com/us/en/insights/industry/financial-services/agentic-ai-banking.html)

### WS5-C · AML Investigation Copilot with Evidentiary Audit Trail
- **One-liner:** An explainable AML case-building agent that compiles alerts, cites exactly which rule/model signal triggered each conclusion, and drafts a SAR narrative with a reviewable evidence chain.
- **Track:** A
- **Zenon anchor:** Barclays rules+ML explainability pattern (Apollo vs. XGBoost), applied to the AML division named in-scope.
- **Target user/client:** AML/financial-crime investigation teams at a retail or commercial bank.
- **The pain:** Evident Insights (Q1 2026) shows specialist vendors already concentrating in credit/AML/treasury; FIS/Anthropic (2026) are targeting AML case-investigation speed, but the hard part — an auditable "why" behind every flag — is exactly where FINRA's auditability risk vector bites.
- **Why it's agentic:** Multi-step: pulls transaction/customer history, applies rules + an ML risk score, investigates root cause across linked accounts, drafts a SAR narrative, and outputs a step-by-step evidence chain a human reviewer can audit line by line.
- **Synthetic-data viability:** High — synthetic transaction network with known laundering typologies (structuring, layering) is standard and safe.
- **6-wk feasibility:** Good — one synthetic case-type (e.g., structuring), rules+ML fusion, narrative + evidence-chain output.
- **Market/competition:** Crowded and well-funded — Bretton AI (formerly Greenlite, $75M Series B, Feb 2026), Sardine, Hawk AI. Zenon's edge is the *explainability* framing over raw detection.
- **White-space/originality:** Moderate — differentiate on the audit-trail/evidence-chain artifact, not detection accuracy.
- **Rubric quick-score:** ZI 5 · TD 5 · FR 4 · OR 3 · PR 4 → weighted **4.35**
- **Tags:** `[Align with Zenon]` `[Recommended]`
- **Sources:** [Evident Insights, Q1 2026](https://evidentinsights.com/insights/banking-use-case-trends-q1-2026) · [FIS press release, 2026](https://www.fisglobal.com/about-us/media-room/press-release/2026/fis-brings-agentic-ai-to-banking-with-anthropic-starting-with-financial-crimes) · [FINRA 2026 Oversight Report](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai)

### WS5-D · Agentic-Commerce Fraud & Reconciliation Monitor
- **One-liner:** Detects anomalous AI-agent-initiated payment transactions and reconciles tokenized agent-commerce volumes against issuer risk rules — a brand-new fraud surface with no established playbook.
- **Track:** A
- **Zenon anchor:** Visa anchor; fraud/reconciliation edge.
- **Target user/client:** Issuer fraud-risk and reconciliation teams at a card network or bank.
- **The pain:** Visa/Mastercard are building tokenized "agentic commerce" rails in 2026, but 95% of consumers voice trust concerns and no mature monitoring pattern exists yet for agent-initiated (vs. human-initiated) transaction anomalies.
- **Why it's agentic:** Monitors a stream of agent-tagged transactions, flags pattern breaks (runaway agent spend, impersonation, agent-on-agent collusion signatures), and reconciles observed agent-commerce volume against expected token-authorization patterns.
- **Synthetic-data viability:** Good, though the domain is new enough that "realistic" synthetic agent-transaction patterns require more assumption-building than mature fraud domains.
- **6-wk feasibility:** Moderate — a novel transaction type means less off-the-shelf pattern knowledge to encode.
- **Market/competition:** Very early — Visa/Mastercard building their own rails; no independent monitoring layer publicly known yet.
- **White-space/originality:** High — this fraud surface is only months old.
- **Rubric quick-score:** ZI 3 · TD 4 · FR 4 · OR 5 · PR 3 → weighted **3.80**
- **Tags:** `[Align with Zenon]`
- **Sources:** [Payments Dive, 2026](https://www.paymentsdive.com/news/visa-mastercard-race-agentic-ai-commerce-payments/750428/) · [PYMNTS, 2026](https://www.pymnts.com/news/artificial-intelligence/2026/visa-and-mastercard-put-tokens-in-charge-of-ai-commerce/)

### WS5-E · AI Content-Licensing Royalty Reconciliation Agent
- **One-liner:** Audits AI-platform usage logs against content-licensing contracts to catch under-reported/under-paid royalties for publishers licensing content into GenAI systems.
- **Track:** A
- **Zenon anchor:** Direct Dow Jones anchor (Factiva licensing); reconciliation/DQ edge.
- **Target user/client:** Rights/finance teams at a subscription-media publisher (Dow Jones-like) licensing content to AI platforms.
- **The pain:** Dow Jones/Factiva has licensed 8,000+ sources for GenAI use and signed a reported ~$50M/year Meta deal; as more such deals proliferate, there is no standard tooling to verify a licensee's usage-based royalty payments match actual query/usage volume.
- **Why it's agentic:** Parses licensing-contract terms, ingests usage/query logs, computes expected royalty vs. paid royalty, investigates discrepancies (definitional mismatch vs. under-reporting vs. billing error), and produces a dispute-ready reconciliation report.
- **Synthetic-data viability:** High — synthetic licensing contracts + synthetic usage logs, no confidential data needed.
- **6-wk feasibility:** Good — scope to one publisher/one licensee relationship with a defined royalty formula.
- **Market/competition:** Traditional royalty-audit firms exist for music/publishing; none yet specialize in AI-content-licensing reconciliation.
- **White-space/originality:** High — the underlying deals are only 1–2 years old.
- **Rubric quick-score:** ZI 5 · TD 4 · FR 4 · OR 5 · PR 4 → weighted **4.40**
- **Tags:** `[Align with Zenon]` `[Recommended]`
- **Sources:** [Axios, 16 Mar 2026](https://www.axios.com/2026/03/16/dow-jones-news-corp) · [Yahoo Finance, 2026](https://finance.yahoo.com/sectors/technology/articles/news-corp-touts-ai-deals-110454635)

### WS5-F · Involuntary-Churn / Dunning Recovery Agent
- **One-liner:** Manages card-decline retry timing, channel and messaging per issuer decline code to recover subscription revenue lost to failed renewals (not voluntary cancels).
- **Track:** A
- **Zenon anchor:** Dow Jones subscription anchor + payments crossover; forecasting/curve-library edge (recovery curves).
- **Target user/client:** Subscription-billing/revenue-ops teams at a media or SaaS subscription business.
- **The pain:** 2026 subscription-churn commentary increasingly separates *voluntary* churn (well-served by prediction tools) from *involuntary* churn (failed payments) — a persistent, quantifiable revenue leak most tooling under-serves.
- **Why it's agentic:** Investigates each decline's reason code, selects optimal retry time/channel/payment-method fallback per historical recovery-curve segment, executes retries, monitors outcomes, and updates the recovery-curve model — a closed adaptive loop.
- **Synthetic-data viability:** High — synthetic subscription billing + card decline-code data is straightforward and safe.
- **6-wk feasibility:** High — one product line, decline-code taxonomy, retry-sequencing engine, recovery-rate dashboard.
- **Market/competition:** Established SaaS category (Chargebee, Recurly, Stripe Billing retries) — genuinely useful but not a green field.
- **White-space/originality:** Low-moderate — differentiate via Zenon's curve-library/forecasting lens (recovery-rate-as-a-forecast-curve) rather than pure retry logic.
- **Rubric quick-score:** ZI 4 · TD 4 · FR 5 · OR 3 · PR 4 → weighted **4.10**
- **Tags:** `[Align with Zenon]` `[Recommended]`
- **Sources:** [TV Tech, 2026](https://www.tvtechnology.com/insights/opinion/streamings-subscription-reset-why-agentic-ai-will-decide-the-next-phase-of-growth) · [MediaPost, 26 Jun 2026](https://www.mediapost.com/publications/article/416128/netflix-monthly-subscriber-churn-still-leads-at-2.html)

### WS5-G · Portfolio Commentary & Client-Reporting Verification Agent
- **One-liner:** Generates auditable portfolio/client-reporting narratives for asset managers and reconciles every claim against source NAV/holdings data before it reaches a client.
- **Track:** A
- **Zenon anchor:** Invesco anchor; reporting/reconciliation edge.
- **Target user/client:** Client-reporting / portfolio-commentary teams at a mid-size asset manager.
- **The pain:** BCG (2026) projects 35–50% capacity freed in reporting/servicing, but the operating-model gap (not tech) is the real blocker; BlackRock's Aladdin Auto Commentary shows the direction but is proprietary to Aladdin clients — most asset managers have no equivalent.
- **Why it's agentic:** Drafts narrative commentary from portfolio/performance data, cross-checks every figure and claim against source system data (NAV, holdings, benchmark), flags unreconciled or anomalous statements before human sign-off — narrative-generation-with-verification, not narrative alone.
- **Synthetic-data viability:** High — synthetic portfolio/NAV/holdings data across a few fund types.
- **6-wk feasibility:** Good — scope to one reporting template (e.g., quarterly commentary) across a few synthetic funds.
- **Market/competition:** BlackRock Aladdin Auto Commentary is a direct incumbent precedent (proprietary, Aladdin-only) — real competitive signal that the use case is validated and valuable.
- **White-space/originality:** Moderate — validated demand, but an independent (non-Aladdin-locked) offering for smaller/mid managers is under-served.
- **Rubric quick-score:** ZI 4 · TD 4 · FR 4 · OR 3 · PR 4 → weighted **3.85**
- **Tags:** `[Align with Zenon]` `[Recommended]`
- **Sources:** [BCG Global Asset Management Report, 2026](https://www.bcg.com/publications/2026/rebuilding-asset-management-for-an-ai-first-world) · [Microsoft Cloud blog, 16 Jun 2026](https://www.microsoft.com/en-us/microsoft-cloud/blog/financial-services/2026/06/16/trust-as-infrastructure-how-agentic-ai-is-rearchitecting-asset-management-at-scale/)

### WS5-H · Agentic-AI "Pilot Purgatory" Escape Kit
- **One-liner:** A structured production-readiness gate that scores a bank's specific agentic pilot (accuracy, cost, latency, audit-trail completeness, security) and issues a go/no-go plus remediation backlog.
- **Track:** A
- **Zenon anchor:** Validation/QC discipline (structural edge).
- **Target user/client:** A bank's AI/innovation team with a stalled pilot (mirrors Wells Fargo's own hiring rationale).
- **The pain:** McKinsey names "pilot purgatory" explicitly; Wells Fargo hired an exec specifically to solve it — proof this is a named, budgeted problem, not a hypothesis.
- **Why it's agentic:** Runs a candidate workflow through a battery of automated production-readiness evaluators and synthesizes a prioritized scorecard + remediation plan.
- **Synthetic-data viability:** High — synthetic task/eval sets.
- **6-wk feasibility:** Good.
- **Market/competition:** Crowded eval-tooling space (Galileo, Braintrust, Patronus AI, Arize).
- **White-space/originality:** Low — this is substantially **I9 (Agentic Analytics Eval Harness) repackaged for a bank buyer**; flagged as overlap, not a fresh technical idea.
- **Rubric quick-score:** ZI 4 · TD 3 · FR 4 · OR 2 · PR 3 → weighted **3.35**
- **Tags:** `[Align with Zenon]`
- **Sources:** [McKinsey, 27 Feb 2026](https://www.mckinsey.com/capabilities/operations/our-insights/the-paradigm-shift-how-agentic-ai-is-redefining-banking-operations) · [CompleteAITraining, Feb 2026](https://completeaitraining.com/news/wells-fargo-taps-aws-exec-faraz-shafiq-to-take-agentic-ai/)

### WS5-I · External-Agent Access Governance & Audit Layer (wealth/custody)
- **One-liner:** As custody/wealth platforms open MCP-based access to clients' own AI agents, a monitoring layer that logs what each external agent pulled, flags anomalous access, and produces client-facing usage reports.
- **Track:** A
- **Zenon anchor:** Validation/audit discipline (structural edge).
- **Target user/client:** Risk/ops teams at a custody or stock-plan administration platform (e.g., Morgan Stanley ShareWorks-like).
- **The pain:** Morgan Stanley is opening ShareWorks/Equity Edge to external client agents via MCP, starting with "a handful of clients" before a wider 2027 rollout — a governance/monitoring layer for agent traffic doesn't yet exist as a standard product.
- **Why it's agentic:** A meta-agent observes other (external, third-party) agents' access patterns, distinguishes normal from anomalous behavior, and compiles audit-ready usage narratives.
- **Synthetic-data viability:** Moderate — requires simulating MCP-style agent traffic, a newer and less-standardized pattern to fake convincingly.
- **6-wk feasibility:** Moderate — more novel infrastructure to stand up in 6 weeks than most candidates here.
- **Market/competition:** Very early; general API-security/observability vendors (Cloudflare, Salt Security) are adjacent but not MCP/agent-specific yet.
- **White-space/originality:** High.
- **Rubric quick-score:** ZI 3 · TD 4 · FR 3 · OR 4 · PR 3 → weighted **3.40**
- **Tags:** `[Align with Zenon]`
- **Sources:** [CNBC, 3 Jun 2026](https://www.cnbc.com/2026/06/03/ai-agents-morgan-stanley-wealth-management-funnel.html)

### WS5-J · Cross-Jurisdiction Agentic-AI Regulatory-Divergence Tracker
- **One-liner:** An agent that monitors and reconciles which agentic-AI governance obligations apply to a bank's specific deployment across the jurisdictions it operates in (US SR 26-2 exclusion, EU AI Act full enforcement Aug 2026, India/APAC rules), flagging gaps and conflicts.
- **Track:** A (flagged: heavy conceptual overlap with WS4's regtech/governance workstream — likely to be de-duped there)
- **Zenon anchor:** Weak direct fit to Zenon's DNA (forecasting/credit-risk/DQ/reporting); closer to a pure compliance-research play.
- **Target user/client:** Global bank's compliance/legal team managing multi-jurisdiction agentic rollouts.
- **The pain:** The EU AI Act reaches full enforcement 2 Aug 2026 requiring explainability/human-supervision for high-risk AI, while the US MRM rewrite explicitly excludes agentic AI — divergent, moving-target obligations across regions.
- **Why it's agentic:** Continuously monitors regulatory publications, maps clauses to a bank's specific use-case inventory, and flags where a deployment is newly in/out of compliance as rules change.
- **Synthetic-data viability:** Good — public regulatory text + a synthetic use-case inventory.
- **6-wk feasibility:** Moderate.
- **Market/competition:** RegTech monitoring vendors (Ascent, Compliance.ai) already do general regulatory-change tracking.
- **White-space/originality:** Moderate.
- **Rubric quick-score:** ZI 3 · TD 3 · FR 4 · OR 2 · PR 3 → weighted **3.00**
- **Tags:** (none — logged for cross-check against WS4, not tagged Align/Recommended)
- **Sources:** [Sullivan & Cromwell memo, Apr 2026](https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management)

### WS5-K · Retail Servicing Escalation & Policy-Grounded Agent
- **One-liner:** Handles the harder, policy-dependent retail-banking requests current chatbots (Erica-like) can't resolve, with grounded citations to internal policy docs and a clean human-handoff + audit trail.
- **Track:** A
- **Zenon anchor:** Weak direct DNA fit (not forecasting/credit-risk/DQ/reporting) — general retail-servicing play.
- **Target user/client:** Retail-banking contact-center ops at a bank already running a first-gen assistant (BofA/Barclays-like).
- **The pain:** BofA's Erica already resolves the easy cases (42% live-chat reduction); Barclays summarizes 8M+ calls — the next efficiency tranche is the harder, policy-dependent tier-2 requests, which is exactly where FINRA's "scope and authority" risk applies.
- **Why it's agentic:** Retrieves and reasons over policy documents, plans a multi-step resolution path, and hands off to a human with a structured summary when confidence is low.
- **Synthetic-data viability:** High.
- **6-wk feasibility:** Good.
- **Market/competition:** Extremely crowded (Erica, Kasisto, Ada, every major bank's own assistant) — low technical differentiation available in 6 weeks.
- **White-space/originality:** Low.
- **Rubric quick-score:** ZI 4 · TD 3 · FR 4 · OR 2 · PR 3 → weighted **3.35**
- **Tags:** (none)
- **Sources:** [Fortune, 17 Mar 2026](https://fortune.com/2026/03/17/inside-bank-of-americas-build-once-ai-strategy/) · [Barclays Private Bank, Nov 2025](https://privatebank.barclays.com/insights/ai-outlook-2026-11-2025/)

### WS5-L · Loan/Commercial Document Completeness & Consistency Agent
- **One-liner:** Cross-references a loan/commercial-lending applicant's submitted documents (income, collateral, KYC) against policy requirements, autonomously flagging missing or inconsistent items before underwriting.
- **Track:** A
- **Zenon anchor:** Loan/Lending division (named in scope); Barclays credit-risk anchor; DQ/reconciliation edge.
- **Target user/client:** Commercial or retail lending underwriting-ops teams.
- **The pain:** Wells Fargo names "loan triage" as an active agentic use case; Goldman's DD-review and BNY's contract-review agents (−75% review time) show the pattern works — but lending-specific document consistency checking is still manual at most banks.
- **Why it's agentic:** Investigates a document packet, cross-references figures across forms (income stated vs. paystub vs. tax return), applies policy rules, and produces a completeness+risk-flag report with citations to the specific inconsistency.
- **Synthetic-data viability:** High — synthetic loan-application packets with injected inconsistencies.
- **6-wk feasibility:** Good — one loan product type, a defined policy checklist.
- **Market/competition:** Document-review/DD agents are an active category (Evisort, Hyperscience, Goldman's internal tools) — moderately crowded.
- **White-space/originality:** Moderate.
- **Rubric quick-score:** ZI 4 · TD 4 · FR 4 · OR 3 · PR 4 → weighted **3.85**
- **Tags:** `[Align with Zenon]` `[Recommended]`
- **Sources:** [Google Cloud blog, 2026](https://cloud.google.com/blog/topics/financial-services/wells-fargo-agentic-ai-agentspace-empowering-workers) · [OpenAI/BNY case study](https://openai.com/index/bny/)

---

## Notes for synthesis

**Overlaps with I1–I10 to resolve at WS6:**
- **WS5-A** (MRM-for-Agents) and **WS5-H** (Pilot Purgatory Escape Kit) both shade into **I9 (Agentic Analytics Eval Harness)** — A is the sharper, more original angle (regulatory-vacuum framing, SR 26-2/FINRA-specific); H is essentially I9 repackaged for a bank buyer and should probably be folded into I9 rather than built separately.
- **WS5-C** (AML Investigation Copilot) is a same-pattern, different-division sibling of **I2 (Credit-Risk/Collections Strategy Copilot)** — same rules+ML-explainability design, AML instead of collections. Worth deciding whether Genesis pitches one deep (collections) or generalizes the pattern across divisions.
- **WS5-B** (Agent-Readiness Data Grader) is a specific "mode" of **I3 (Data-Trust Agent)**, not a separate build.
- **WS5-G** (Portfolio Commentary Verification Agent) echoes **I1's** narrative/verification-agent concept, applied to asset-management client reporting instead of subscription FP&A.
- **WS5-J** (Regulatory-Divergence Tracker) likely overlaps **WS4's** regtech/governance workstream — flag for de-dup, not a WS5-native idea.

**Top two highest-stakes findings:**
1. **The regulatory vacuum is the single biggest market-timing signal.** SR 26-2 (Apr 2026) — the first Fed/OCC/FDIC model-risk rewrite in 15 years — explicitly excludes generative and agentic AI, right as Evident Insights measures agentic use cases roughly doubling as a share of all bank AI use cases in one quarter (15%→32%, Q4 2025→Q1 2026) and FINRA (Dec 2025) has already built a 4-vector supervisory risk taxonomy for agents with no accompanying compliance template. Whoever helps a bank build its own agent-governance/validation framework *now*, before formal rules land, is selling into a documented, dated gap — not a hypothetical one.
2. **"Pilot purgatory" is now an org-chart problem, not just an analyst buzzword.** Wells Fargo's Feb 2026 hire of an AWS executive with the explicit mandate to move agentic AI "from pilots to scale, with controls and measurable outcomes" is a bank publicly budgeting headcount to solve exactly what McKinsey and Deloitte describe abstractly. This is strong, dated evidence that I9-style production-readiness/eval offerings (and their WS5 variants here) are aimed at a real, currently-unsolved buyer problem.
