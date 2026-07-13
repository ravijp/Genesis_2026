# The Agentic-AI Startup & Funding Landscape (as of 2026-07-14)

*Research brief for Zenon "Genesis" — Track A "Client-Facing Solutions." Purpose: use the startup/funding lens to (a) confirm where demand is validated by fresh capital, and (b) mine raw or under-served theses we can execute *better* inside a named Zenon enterprise client (finance, media, pharma, retail, HCM/payroll).*

> **WebSearch status: AVAILABLE and used extensively** (~30 searches + ~8 deep page fetches). Every quantitative claim below carries an inline source link and, where the source gives one, a date. Where a figure comes from a secondary aggregator rather than a primary announcement, that is noted.

---

## Executive summary (read this first)

1. **The dominant thesis is "service-as-software" / vertical agents that capture *labor* budgets, not IT budgets.** a16z, Bessemer, and Sequoia all converged on this in 2025-26: agents that *do the work* (sell the service) rather than *assist* a human, priced per outcome (tickets resolved, dollars recovered, invoices processed), competing against the labor line of the P&L rather than the software line. ([a16z](https://a16z.com/newsletter/december-2024-enterprise-newsletter-ai-is-driving-a-shift-towards-outcome-based-pricing/); [Bessemer](https://www.bvp.com/atlas/the-state-of-ai-2025))
2. **Money is flooding vertical agents, not chatbots.** Agentic-AI startups raised ~**$2.51B YTD through early July 2026, ~3.0x the comparable 2025 period ($840M)**, across 65 deals (up from 13). Vertical AI agents took **$1.37B (54.8%)**; agent execution infrastructure **$504M (20.1%)**, up from just $21M a year earlier. ([New Market Pitch](https://newmarketpitch.com/blogs/news/agentic-ai-funding-trends))
3. **YC has gone all-in on agents, and its Summer-2026 Request-for-Startups explicitly asks for "AI-native service companies" in insurance brokerage, accounting/tax/audit, compliance, and healthcare administration** — i.e., YC is publicly telling founders to build exactly the categories Zenon's clients live in. ([YC RFS](https://www.ycombinator.com/rfs); [PitchBook](https://pitchbook.com/news/articles/y-combinator-is-going-all-in-on-ai-agents-making-up-nearly-50-of-latest-batch))
4. **Financial-services ops is one of the hottest verticals, and the collections/loan-servicing niche has clear winners already — a direct match for Barclays collections + Lendmark consumer lending.** Salient (AI-native loan servicing/collections) raised a **$60M Series A** (a16z) and hit ~$25M ARR; YC's Kastle does the same for mortgage servicing. ([a16z](https://a16z.com/announcement/investing-in-salient/); [WebProNews](https://www.webpronews.com/salients-ai-loan-machine-25m-arr-in-two-years-without-a-single-customer-loss/); [YC](https://www.ycombinator.com/companies/kastle))
5. **HOA / community-association finance ops is a validated, still-open lane — direct match for Western Alliance's HOA banking.** Vantaca (AI HOA/community-association management) raised **$300M at a $1.25B valuation (Oct 2025)**; YC-backed Assembly is building "AI-native HOA management." Nobody has clearly won the *bank-side* HOA cash-application / reserve / delinquency problem. ([The AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge))
6. **Compliance / KYC-AML agents are a crowded-but-funded lane** (Diligent AI €2.1M seed, Mar 2026; Norm Ai >$140M incl. Citi Ventures; Greenlite→Bretton AI $75M Series B) — relevant to every Zenon bank client, but a "me-too" screening agent scores low on originality. ([EU-Startups](https://www.eu-startups.com/2026/03/yc-backed-diligent-ai-raises-e2-1-million-to-automate-kyc-and-aml-workflows-using-ai-agents/); [PYMNTS](https://www.pymnts.com/news/artificial-intelligence/2026/this-ceo-just-raised-110-million-to-make-banks-agent-first/))
7. **Finance/back-office (AR, accounting, CFO-suite) is fully validated with outcome pricing baked in** — Basis $100M at $1.15B (Feb 2026), Rillet $70M Series B (a16z/ICONIQ), Fazeshift $17M Series A (F-Prime, May 2026), Daylit $110M. Pricing is explicitly outcome-based ("dollars collected," "invoices processed"). Relevant to Invesco/Morgan Stanley back-office and ampliFI. ([CPA Practice Advisor](https://www.cpapracticeadvisor.com/2026/02/24/basis-raises-100-million-to-deploy-ai-agents-for-accounting-firms/178759/); [Crunchbase](https://news.crunchbase.com/fintech/fazeshift-accounts-receivable-ai-finance-ops-startup-funding/))
8. **Agent *infrastructure* is a parallel gold rush** — payments (x402 Foundation w/ Visa, Google, AWS, Anthropic; Skyfire $9.5M; Payman $13.8M w/ Visa), identity/non-human IAM (Oasis $120M; GitGuardian $50M), memory (Mem0 $24M; Letta $10M), evals/observability (Braintrust $80M at $800M), browser/computer-use (Browser Use $17M; Kernel $22M), and agent security (360 companies, ~$9.5B tracked). Zenon can *consume* these, not rebuild them — but agent-payments + agent-identity intersect directly with Visa/Amex/ampliFI. ([Chainalysis](https://www.chainalysis.com/blog/x402-agentic-payments-adoption/); [SC Media](https://www.scworld.com/brief/oasis-security-raises-120-million-for-non-human-identity-management))
9. **The graveyard: generic AI SDRs and meeting notetakers are commoditized/failing.** AI SDRs churn 50-70% annually and burn domain reputation; notetaker transcription accuracy is a commodity (90-95%+ across 8 tools). ~80% of AI startups are projected to fail by end-2026, mostly "chat-layer" wrappers with no data moat. **Avoid these entirely.** ([DigitalApplied](https://www.digitalapplied.com/blog/case-against-ai-sdrs-contrarian-analysis-2026); [IdeaProof](https://ideaproof.io/failures/ai-startups))
10. **The white space that keeps appearing in founder/VC discourse and maps to Zenon clients:** (a) *collections & loss-mitigation with compliant, empathetic, human-in-the-loop workflows* (Barclays/Lendmark); (b) *HOA/community-association bank-side finance ops* (Western Alliance); (c) *loyalty/rewards ops in the agentic-commerce era* (ampliFI/Amex/Visa); (d) *payroll/HR "exception" handling in regulated pay* (ADP). Each has funding proving the adjacent problem but no dominant winner on the exact enterprise-embedded version.

---

## 1. Y Combinator: recent batches & Requests for Startups

**Batch cadence & AI density.** YC now runs four batches/year. Across S25, F25, W26 the AI density is extreme: **S25 had 60%+ of startups referencing "AI"**; **F25 had 92%** of ~155 companies with AI in the core offering; PitchBook reported AI agents made up **nearly 50%** of a recent batch. ([CB Insights F25](https://www.cbinsights.com/research/y-combinator-fall2025/); [catalaize S25](https://catalaize.substack.com/p/y-combinator-s25-batch-profile-and); [PitchBook](https://pitchbook.com/news/articles/y-combinator-is-going-all-in-on-ai-agents-making-up-nearly-50-of-latest-batch))

**The through-line: from "build an agent platform" → "own one workflow end-to-end."** S25 shifted decisively to *domain-specific* agents (insurance-claim appeals, mortgage applications, warehouse logistics). F25 shifted again toward the *production stack* to deploy agents reliably. ([CB Insights S25](https://www.cbinsights.com/research/y-combinator-summer2025/))

**Financial-services agents in F25** ("beyond assistance to full workflow ownership"): **Zarna** and **DiligenceSquared** (AI associates automating private-markets diligence), **Zalos** (enterprise agents that plug into existing ERPs/accounting to complete repetitive tasks). ([CB Insights F25](https://www.cbinsights.com/research/y-combinator-fall2025/))

**Agent infrastructure in F25** (13 startups): **Hyperspell** (memory), **Metorial** (agent integration), **Castari** (dev platform), **The Context Company** (observability), **Locus** (payments). ([CB Insights F25](https://www.cbinsights.com/research/y-combinator-fall2025/))

**W26** was YC's "most technically complex cohort yet" — heavy on physical AI, RL-environment generation, and *software built for agents rather than humans*. Standouts: **Cardboard** (agentic video editor, top HN launch of the batch), **Polymath** (RL-environment generation), **VOYGR** (mapping infra for agents), **Sonarly** (auto root-cause of production incidents), **MouseCat** (fraud detection over Databricks/Snowflake). ([CB Insights W26](https://www.cbinsights.com/research/y-combinator-winter-2026/); [TechCrunch W26](https://techcrunch.com/2026/03/26/16-of-the-most-interesting-startups-from-yc-w26-demo-day/); [Extruct W26](https://www.extruct.ai/research/ycw26/))

**YC Requests for Startups (Spring/Summer 2026) — the money quote for Genesis.** The RFS opens: *"AI has stopped being a feature and started being the foundation … replace rather than assist. Sell the service. Do the work."* The **"AI-Native Service Companies"** RFS (Gustaf Alströmer) explicitly names target markets: **insurance brokerage, accounting/tax/audit, compliance, and healthcare administration.** Additional agent-relevant RFS: **"Software for Agents"** (machine-readable APIs/MCPs for the coming agent-users), **"Inference Chips for Agent Workflows,"** and **"The AI Operating System for Companies / Company Brain."** ([YC RFS](https://www.ycombinator.com/rfs); [The VC Corner](https://www.thevccorner.com/p/yc-summer-2026-requests-for-startups-ideas))

> **Genesis implication:** YC is publicly validating "do the work, per outcome" in *precisely* Zenon's client verticals. A Track-A entry that embodies "AI-native service, embedded in a named enterprise" is riding the strongest current signal in the market.

---

## 2. Vertical AI-agent raises by domain (Zenon-relevant)

### 2a. Financial-services ops — collections, lending, servicing
- **Salient** — AI-native loan servicing & collections (auto/consumer finance): automates outbound calls, servicing, regulatory audit, disputes, claims. **$60M Series A** (a16z-backed), ~**$25M ARR** in ~2 years, deployments processing billions in loans (e.g., Consumer Portfolio Services). Claims 80-90% of outbound calls automated, +20-30% payment rates. ([a16z](https://a16z.com/announcement/investing-in-salient/); [WebProNews](https://www.webpronews.com/salients-ai-loan-machine-25m-arr-in-two-years-without-a-single-customer-loss/); [StockTitan/CPSS](https://www.stocktitan.net/news/CPSS/consumer-portfolio-services-deploys-ai-powered-servicing-platform-uxgwpzptlf1v.html))
- **Kastle (YC)** — AI voice agents for mortgage servicing & consumer-lending collections (payment collection, escrow Q&A). **~$2.8M** across 2 rounds; latest seed Mar 2025. ([YC](https://www.ycombinator.com/companies/kastle); [Crunchbase](https://www.crunchbase.com/organization/kastle))
- **AgentCollect (YC)** — B2B debt collection via AI agents. ([YC](https://www.ycombinator.com/companies/agentcollect))
- **Taktile** — SMB credit underwriting / decisioning agents; **$110M** round led by Goldman Sachs Alternatives (also reported €51.5M Series B earlier). ([PYMNTS](https://www.pymnts.com/news/artificial-intelligence/2026/this-ceo-just-raised-110-million-to-make-banks-agent-first/); [Taktile](https://taktile.com/articles/introducing-taktile-smb-ai-agents))
- **Market context:** New York Fed (May 2026) — US household debt **$18.8T**, ~4.8-5.0% of balances delinquent; AI-for-collections market ~$3.34B (2024) → ~$15.9B (2034). McKinsey digital-first collections: resolution up multiple points, collection costs down ≥15%. ([HES FinTech](https://hesfintech.com/blog/ai-in-debt-collection-key-trends-and-approaches/); [Barclays US](https://cards.barclaycardus.com/banking/about-us/news-and-views/insights/top-five-ai-innovations-shaping-consumer-banking-in-2026/))

### 2b. Financial-services ops — CFO-suite, accounting, AR/finance back-office
- **Basis** — end-to-end AI agents for accounting firms (accounting/tax/audit). **$100M Series B at $1.15B** (Feb 24, 2026), led by a16z, w/ Tiger Global, Sequoia, YC. ([CPA Practice Advisor](https://www.cpapracticeadvisor.com/2026/02/24/basis-raises-100-million-to-deploy-ai-agents-for-accounting-firms/178759/); [SiliconANGLE](https://siliconangle.com/2026/02/24/ai-accounting-startup-basis-secures-100m-1-15b-valuation-firms-adopt-agent-based-workflows/))
- **Rillet** — AI-native ERP / accounting. **$70M Series B** (a16z + ICONIQ, w/ Sequoia, Oak HC/FT), ~Aug 2025 — 10 weeks after a $25M Series A; >$100M raised in <1 year. ([Rillet](https://www.rillet.com/blog/rillet-raises-70m-series-b-from-andreessen-horowitz-and-iconiq); [Crunchbase](https://news.crunchbase.com/fintech/startup-rillet-ai-seriesb-a16z-iconiq/))
- **Fazeshift** — AI agents for accounts receivable (invoicing, collections, payment matching, reconciliation across NetSuite/Salesforce/bank portals; claims >90% of manual AR automated). **$17M Series A** (May 7, 2026), led by F-Prime; Gradient Ventures, YC, Wayfinder, Pioneer, Ritual; $22M total. ([Crunchbase](https://news.crunchbase.com/fintech/fazeshift-accounts-receivable-ai-finance-ops-startup-funding/))
- **Daylit** — AR automation; **$110M** (Sept 2025); customers report AR opex down >75%, high-risk collections 3x. ([Yahoo/Daylit](https://finance.yahoo.com/sectors/technology/articles/ai-startup-giving-away-playbook-130000651.html))
- **Zalos** — computer-use agents for CFOs. **$3.6M seed** (14 Peaks, Cohen Circle, 20VC). **OpenCFO** — **$2M** (Endiya). ([TechFundingNews](https://techfundingnews.com/ai-meets-finance-zalos-snaps-3-6m-to-build-computer-agents-for-cfos/); [Ascendants](https://ascendants.in/business-stories/opencfo-raises-2m-ai-financial-operating-system/))
- **Demand context:** 54% of CFOs name integrating AI agents as their #1 digital-transformation priority (Deloitte 2026 CFO Signals); 76% of CFOs allocating budget to autonomous finance agents; 2026 agentic-AI spend ~$12.4B. ([ChatFin](https://chatfin.ai/blog/2026-finance-ai-spending-cfo-strategies-for-autonomous-agent-deployment/))

### 2c. Compliance / KYC-AML / regulatory screening
- **Diligent AI (YC)** — AI agents for end-to-end KYC/AML (clearing false positives, registry/adverse-media search, sanctions/payment-screening resolution). **€2.1M seed** (Mar 4, 2026), led by Speedinvest w/ Shapers, YC; angels from N26, Allica, IDnow. ([EU-Startups](https://www.eu-startups.com/2026/03/yc-backed-diligent-ai-raises-e2-1-million-to-automate-kyc-and-aml-workflows-using-ai-agents/))
- **Norm Ai** — regulatory-compliance agents; **>$140M** raised (Coatue, Bain Capital, Citi Ventures). **Bretton AI (formerly Greenlite)** — **$75M Series B** (Sapphire). **Spektr** — **$20M** (AI KYC/AML). **Steward** — **$5M** (AML/KYC onboarding, $100B assets). **Sphinx** — **$7.1M seed**. ([PYMNTS](https://www.pymnts.com/news/artificial-intelligence/2026/this-ceo-just-raised-110-million-to-make-banks-agent-first/); [AML Network](https://amlnetwork.org/aml-news/diligent-ai-secures-e2-1-million-seed-funding-to-automate-kyc-and-aml-compliance-workflows-with-ai-agents/); [Fintech Global](https://fintech.global/2026/03/18/ai-compliance-platform-steward-secures-5m-funding/))
- **Context:** global AML compliance costs >$200B/yr; false positives waste up to 95% of investigator time. ([AML Network](https://amlnetwork.org/aml-news/diligent-ai-secures-e2-1-million-seed-funding-to-automate-kyc-and-aml-compliance-workflows-with-ai-agents/))

### 2d. Banking back-office & SMB/commercial banking
- Nearly half of Tier-1 banks to deploy back-office agents by 2026 (KYC, loan-doc processing, transaction monitoring, regulatory reporting); reported 90% cut in KYC onboarding time, 50% less AML investigation time, 2.3x ROI within 13 months. **Unit21** ~$92M (used by Chime, Intuit, Sallie Mae). Small-dollar (<$250K) SMB lending via cash-flow analysis is repeatedly cited as an open opportunity. ([Beam](https://beam.ai/agentic-insights/ai-agents-banking-2026-beyond-chatbots); [Kore.ai](https://www.kore.ai/blog/ai-agents-in-finance-banking-12-proven-use-cases-2026))

### 2e. Insurance ops (claims, underwriting, brokerage)
- **AI captured 95.2% of all insurtech funding in Q1 2026** ($1.63B total, best since Q3 2022). **Corgi** (AI-native insurer) **$108M**; **Harper** (AI commercial-insurance brokerage) **$47M** seed+A; 65% of insurers planning scaled claims agents in 2026. ([FinanceX](https://www.financexmagazine.com/post/insurtech-s-1-63-billion-tell-ai-is-no-longer-the-pitch-it-s-the-plumbing); [Insurance Business](https://www.insurancebusinessmag.com/us/news/technology/quick-everyone-lets-make-an-insurance-ai-startup-581088.aspx))

### 2f. Healthcare admin (RCM, prior auth, clinical ops) — relevant to J&J-adjacent payer/provider workflows
- US loses **$262B/yr** to revenue-cycle inefficiency; denial rates 30% (2022) → 41% (2025); RCM AI market $14.9B (2024) → $21.7B (2025). **Adonis** (AI-first RCM, ex-Palantir) 4x revenue growth 2025; **Abridge** **$250M at $2.7B** (Apr 2026); CMS 2026 rules cut prior-auth turnaround 14→7 days (regulatory tailwind). ([Innovaccer](https://innovaccer.com/blogs/selecting-agentic-ai-healthcare); [Aspirion](https://www.aspirion.com/the-year-ai-transformed-revenue-cycle-2025-insights-and-2026-predictions/))

### 2g. Legal / contracts
- **Harvey** — **$200M at $11B** (Mar 25, 2026, GIC + Sequoia); ~$190M ARR, 3.9x YoY; expanding agent capabilities. **Legora** — **$550M Series D** (Accel, Mar 2026) + $50M extension → **$5.6B** (Nvidia, Atlassian); acquired Walter AI. **Eudia** — **$105M Series A** (General Catalyst), in-house legal at F500. Legal is the most mature vertical (Harvey ~$300M ARR by May 2026 per one source). ([CNBC](https://www.cnbc.com/2026/03/25/legal-ai-startup-harvey-raises-200-million-at-11-billion-valuation.html); [TechCrunch](https://techcrunch.com/2026/04/30/legal-ai-startup-legora-hits-5-6-valuation-and-its-battle-with-harvey-just-got-hotter/); [aifundingtracker](https://aifundingtracker.com/top-legal-ai-startups/))

### 2h. Real-estate / property management (HOA-adjacent — Western Alliance)
- **Vantaca** — AI HOA/community-association management. **$300M at $1.25B** (Oct 2025). ([The AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge))
- **EliseAI** — AI property-management assistant (tenant comms, tours, lease audits, maintenance). **$250M at $2.2B** (Aug 2025); Bessemer-highlighted. ([The AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge); [Bessemer](https://www.bvp.com/atlas/the-state-of-ai-2025))
- **Juniper Square** — AI fund admin/IR/CRM for RE investment managers. **$130M at $1.1B** (Jun 2025). **Assembly (YC)** — AI-native HOA management. Proptech VC hit ~$1.7B in Jan 2026 alone (+176% YoY). ([The AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge))

### 2i. Customer ops / CX
- **Decagon** — AI customer-support agents. **$250M Series D at $4.5B** (Jan 2026, Coatue + Index); ~$481M total; ~$35M ARR; +100 enterprise logos in 2025 (incl. financial services). **Sierra** — ~$100M ARR (Oct 2025, +400% YoY), **$350M** round (Greenoaks) at **$10B**. **Crescendo** — per-resolution pricing (~$1.25/resolution). **Parloa** $350M, **Netomi** $110M, **Wonderful** $150M. **Outcome pricing is the norm here.** ([Bloomberg](https://www.bloomberg.com/news/articles/2026-01-28/ai-customer-support-startup-decagon-valued-at-4-5-billion); [Businesswire](https://www.businesswire.com/news/home/20250623894798/en/Decagon-Raises-$131M-at-$1.5B-Valuation-to-Deliver-Concierge-Customer-Experience-with-AI-Agents); [Sacra](https://sacra.com/research/sierra-vs-decagon/))

### 2j. Procurement / supply chain
- **AgentOS** (Berlin) **$85M Series B** (a16z), valuation tied to cutting opex 30%. **Lumari (YC)** — sourcing/RFQ/PO agents (ex-Google/Tesla/Amazon/Stripe). **Lio** — multi-agent procurement (vendor research→negotiation→approval→tracking). **Traza** — **$2.1M pre-seed** (Base10), procurement for manufacturers/construction. ([New Market Pitch](https://newmarketpitch.com/blogs/news/agentic-ai-funding-trends); [Pulse2](https://pulse2.com/traza-2-1-million-raised-to-automate-procurement-and-supply-chain-operations-with-ai-workers/))

### 2k. HR / payroll ops (ADP)
- **Warp** — AI-native employee management (payroll, HR, compliance, benefits, IT). **$85M** (Battery, Peak XV, Sound, Sapphire, SV Angel, Homebrew). ([asanify digest](https://asanify.com/blog/news/ai-agents-enterprise-stack-april-28-2026/))
- **Niural** — AI payroll/PEO + compliance; **Series A extended to $52M** (+$21M); >$200M annualized gross revenue on PEO after an Aetna partnership (Apr 2026); launching "Niural AI Labs" for *long-horizon agents in high-stakes regulated areas* (workflow orchestration, automated compliance). **Central** and **Payslip** (Salica) also funded. ([Fundraise Insider](https://fundraiseinsider.com/blog/niural-adds-21m-expanding-series-a-to-52m-for-ai-payroll/))
- **Note:** Big incumbents are moving (Sage rolling AI agents across finance/HR/ops, Apr 2026) — meaning ADP itself is a *buyer/partner* under competitive pressure. ([Sage](https://www.sage.com/en-us/news/press-releases/2026/04/sage-expands-ai-agents-across-finance-hr-and-operations-to-automate-workflows/))

### 2l. Loyalty / payments ops (ampliFI, Amex, Visa)
- No breakout *pure-play* "loyalty-ops agent" unicorn yet — this is **open white space**. The action is in **agentic commerce**: PayPal↔Perplexity embedded checkout; Stabile (loyalty autopilot rewarding purchases made via ChatGPT/Copilot/Google AI Mode, launched Nov 5, 2025); PYMNTS: *"the most consequential customer a brand acquires in 2026 may be an AI agent."* Dispute resolution, fraud orchestration, routing, and pricing are increasingly agent-run in real time. ([PYMNTS agentic loyalty](https://www.pymnts.com/artificial-intelligence-2/2026/how-brands-are-reinventing-loyalty-for-the-ai-decision-maker/); [Chain Store Age](https://chainstoreage.com/when-ai-agents-shop-us-how-will-loyalty-programs-keep))

---

## 3. Agent-infrastructure funding (Zenon consumes this; two categories touch our clients)

- **Agent payments (touches Visa/Amex/ampliFI directly).** **x402 Foundation** (Coinbase + Cloudflare, launched 2025) — members include **Google, Visa, AWS, Circle, Anthropic, Vercel**; >100M payments processed since May 2025. **Skyfire** **$9.5M** (a16z CSX, Coinbase Ventures) for agent identity + "Know-Your-Agent." **Payman** **$13.8M** (w/ Visa, Coinbase Ventures) for FI-deployed agent transactions. AWS **Bedrock AgentCore Payments** (preview, May 7 2026); **Fireblocks Agentic Payments Suite** (May 20 2026). ([Chainalysis](https://www.chainalysis.com/blog/x402-agentic-payments-adoption/); [PRNewswire/Fireblocks](https://www.prnewswire.com/news-releases/fireblocks-joins-x402-foundation-launches-agentic-payments-suite-302777251.html))
- **Agent identity & non-human IAM.** **Oasis Security** **$120M Series B**; **GitGuardian** **$50M** (secrets + agent security); **Foundation** **$6.4M** (agent authorization). Akeyless: 67% of security leaders suspect agents accessed out-of-scope data; only 7% believe current controls would stop a compromised agent. ([SC Media](https://www.scworld.com/brief/oasis-security-raises-120-million-for-non-human-identity-management); [SiliconANGLE](https://siliconangle.com/2026/02/11/gitguardian-raises-50m-expand-non-human-identity-ai-agent-security/))
- **Agent memory.** **Mem0** **$24M** (Seed Kindred; Series A Basis Set; w/ Peak XV, GitHub Fund, YC) — market leader by adoption, exclusive memory provider for AWS Agent SDK. **Letta** **$10M seed** (Felicis; angels Jeff Dean, Clem Delangue). ([Mem0](https://mem0.ai/series-a); [BigDATAwire/Letta](https://www.hpcwire.com/bigdatawire/this-just-in/letta-emerges-from-stealth-with-10m-to-build-ai-agents-with-advanced-memory/))
- **Evals / observability.** **Braintrust** **$80M Series B at $800M** (customers Notion, Replit, Ramp); **Galileo** ~$68M total; **Langfuse** acquired by ClickHouse (Jan 2026, part of $400M Series D at $15B); LangSmith ~$125M+ cumulative. ([Braintrust](https://www.braintrust.dev/articles/best-ai-observability-tools-2026); [Presenc](https://presenc.ai/research/ai-agent-infrastructure-startups-2026))
- **Browser / computer-use.** **Browser Use** **$17M seed** (Felicis; users incl. Airbnb, Amazon, Anthropic); **Kernel** **$22M** (cloud browser infra). Amazon Nova Act, OpenAI CUA (Operator/Atlas), MS Computer Use for Copilot Studio all shipped. ([SiliconANGLE Browser Use](https://siliconangle.com/2025/03/23/browser-use-raises-17m-help-steer-ai-agents-internet/); [SiliconANGLE Kernel](https://siliconangle.com/2025/10/09/kernel-raises-22m-power-browser-infrastructure-ai-agents/))
- **Agent security / guardrails.** 360 companies tracked, ~$9.5B disclosed (as of Jul 13, 2026). **AIUC** — insurance + audit + AIUC-1 certification for AI agents; **$15M seed** (Jun 2025, Nat Friedman/NFDG; angels incl. Anthropic co-founder Ben Mann); predicts a $500B AI-agent insurance market by 2030. **CodeIntegrity** **$5M** (runtime control layer). ([Fortune/AIUC](https://fortune.com/2025/07/23/ai-agent-insurance-startup-aiuc-stealth-15-million-seed-nat-friedman/); [prompt.security map](https://startups.prompt.security/))

---

## 4. VC theses 2025-2026 ("vertical agents" & "service-as-software")

- **a16z — "Software is becoming labor."** Traditional service businesses (support, sales, back-office finance) become scalable software. **Per-seat is dead**; once outcomes are measurable, pricing shifts to **$ per outcome** (tickets resolved, dollars recovered, invoices processed). Winners "look less like SaaS and more like managed-labor platforms." Buyers of action-taking agents need permissions, spend caps, audit logs, escalation. ([a16z Dec-2024 enterprise newsletter](https://a16z.com/newsletter/december-2024-enterprise-newsletter-ai-is-driving-a-shift-towards-outcome-based-pricing/))
- **Bessemer — "Vertical AI: from systems of record to systems of action."** *"AI-native apps don't just store data—they act on it."* Targets previously "technophobic" industries with language/multi-modal-heavy work. Two archetypes: **"AI Supernovas"** (~$40M ARR yr1, ~$125M yr2) and **"AI Shooting Stars"** (~$3M yr1 → ~$100M yr4, 60% GM, "quadruple-quadruple-triple" growth). Highlights EliseAI (RE), Abridge/SmarterDx (health), EvenUp/Ivo/Legora (legal). ([Bessemer State of AI 2025](https://www.bvp.com/atlas/the-state-of-ai-2025); [Bessemer Vertical AI book, Jan 2026 PDF](https://www.bvp.com/assets/uploads/2026/01/BUILDING-VERTICAL-AI_PDF_BESSEMER_VENTURE_PARTNERS_BOOK_JANUARY_2026.pdf))
- **Sequoia — "Act Three: vertical agents" / "2026 is the year of agents."** Framework: Act 1 novelty → Act 2 reasoning/multimodal → **Act 3 (2025→2026) vertical agents trained end-to-end for specific workflows, replacing specific labor.** ~**$28B VC into agent companies in 2025 (4x 2024)**; best returns in industry-specific agents (legal, health, finance), not general platforms; long-horizon agents framed as "functionally AGI." ([Sequoia AI Ascent 2026](https://www.theaiopportunities.com/p/sequoia-ai-ascent-2026-the-future); [Sequoia AI 50](https://sequoiacap.com/article/ai-50-2025/))
- **Menlo — enterprise reality check.** Enterprise GenAI spend **$37B in 2025** (tripled YoY): ~$19B apps / ~$18B infra; industry-specific solutions $3.5B (led by healthcare). Crucially: **only ~16% of enterprise "agent" deployments are true agents** — most are fixed-sequence workflows. Anthropic now leads enterprise LLM spend (~40%). ([Menlo State of GenAI 2025](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/))
- **Market-structure signal.** Vertical AI agents = **48-55% of 2026 deals & capital**; median round shrank to **$18M** (from $30M) even as total capital rose — i.e., more shots, tighter checks, higher bar. Series-A check-writers now demand "proprietary multi-agent routing, persistent state, ironclad human-in-the-loop gates." ([New Market Pitch](https://newmarketpitch.com/blogs/news/agentic-ai-funding-trends))

---

## Funding table (selected, Zenon-relevant)

| Startup | What it does | Stage / Amount | Date | Investors | Source |
|---|---|---|---|---|---|
| **Salient** | AI-native loan servicing & collections (auto/consumer) | Series A / $60M; ~$25M ARR | 2025 | a16z | [a16z](https://a16z.com/announcement/investing-in-salient/), [WebProNews](https://www.webpronews.com/salients-ai-loan-machine-25m-arr-in-two-years-without-a-single-customer-loss/) |
| **Kastle (YC)** | AI voice agents, mortgage servicing/collections | Seed / ~$2.8M | Mar 2025 | YC | [YC](https://www.ycombinator.com/companies/kastle), [Crunchbase](https://www.crunchbase.com/organization/kastle) |
| **Taktile** | SMB credit underwriting/decisioning agents | Growth / $110M | 2026 | Goldman Sachs Alternatives | [PYMNTS](https://www.pymnts.com/news/artificial-intelligence/2026/this-ceo-just-raised-110-million-to-make-banks-agent-first/) |
| **Basis** | AI agents for accounting/tax/audit firms | Series B / $100M @ $1.15B | Feb 24 2026 | a16z, Tiger, Sequoia, YC | [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2026/02/24/basis-raises-100-million-to-deploy-ai-agents-for-accounting-firms/178759/) |
| **Rillet** | AI-native ERP / accounting | Series B / $70M | Aug 2025 | a16z, ICONIQ, Sequoia | [Rillet](https://www.rillet.com/blog/rillet-raises-70m-series-b-from-andreessen-horowitz-and-iconiq) |
| **Fazeshift** | AI agents for accounts receivable | Series A / $17M ($22M total) | May 7 2026 | F-Prime, Gradient, YC | [Crunchbase](https://news.crunchbase.com/fintech/fazeshift-accounts-receivable-ai-finance-ops-startup-funding/) |
| **Daylit** | AR automation | $110M | Sept 2025 | (n/d) | [Yahoo](https://finance.yahoo.com/sectors/technology/articles/ai-startup-giving-away-playbook-130000651.html) |
| **Diligent AI (YC)** | AI agents for KYC/AML | Seed / €2.1M | Mar 4 2026 | Speedinvest, Shapers, YC | [EU-Startups](https://www.eu-startups.com/2026/03/yc-backed-diligent-ai-raises-e2-1-million-to-automate-kyc-and-aml-workflows-using-ai-agents/) |
| **Norm Ai** | Regulatory-compliance agents | >$140M total | 2025-26 | Coatue, Bain, Citi Ventures | [PYMNTS](https://www.pymnts.com/news/artificial-intelligence/2026/this-ceo-just-raised-110-million-to-make-banks-agent-first/) |
| **Bretton AI (ex-Greenlite)** | AML/compliance agents | Series B / $75M | 2025-26 | Sapphire Ventures | [AML Network](https://amlnetwork.org/aml-news/diligent-ai-secures-e2-1-million-seed-funding-to-automate-kyc-and-aml-compliance-workflows-with-ai-agents/) |
| **Vantaca** | AI HOA/community-association mgmt | $300M @ $1.25B | Oct 2025 | (n/d) | [AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge) |
| **EliseAI** | AI property-management assistant | $250M @ $2.2B | Aug 2025 | (n/d) | [AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge) |
| **Assembly (YC)** | AI-native HOA management | Seed (YC) | 2025-26 | YC | [YC housing](https://www.ycombinator.com/companies/industry/housing-and-real-estate) |
| **Decagon** | AI customer-support agents | Series D / $250M @ $4.5B | Jan 2026 | Coatue, Index | [Bloomberg](https://www.bloomberg.com/news/articles/2026-01-28/ai-customer-support-startup-decagon-valued-at-4-5-billion) |
| **Sierra** | AI CX agents (outcome-priced) | $350M @ $10B; ~$100M ARR | Sept 2025 | Greenoaks | [Sacra](https://sacra.com/research/sierra-vs-decagon/) |
| **Harvey** | Legal AI agents | Series G / $200M @ $11B | Mar 25 2026 | GIC, Sequoia | [CNBC](https://www.cnbc.com/2026/03/25/legal-ai-startup-harvey-raises-200-million-at-11-billion-valuation.html) |
| **Legora** | Legal AI agents | Series D / $550M+$50M @ $5.6B | Mar-Apr 2026 | Accel, Nvidia, Atlassian | [TechCrunch](https://techcrunch.com/2026/04/30/legal-ai-startup-legora-hits-5-6-valuation-and-its-battle-with-harvey-just-got-hotter/) |
| **Abridge** | Clinical documentation → RCM | $250M @ $2.7B | Apr 2026 | (n/d) | [Aspirion](https://www.aspirion.com/the-year-ai-transformed-revenue-cycle-2025-insights-and-2026-predictions/) |
| **Corgi** | AI-native insurer | $108M | 2026 | (n/d) | [FinanceX](https://www.financexmagazine.com/post/insurtech-s-1-63-billion-tell-ai-is-no-longer-the-pitch-it-s-the-plumbing) |
| **Harper** | AI commercial-insurance brokerage | Seed+A / $47M | 2026 | (n/d) | [Insurance Business](https://www.insurancebusinessmag.com/us/news/technology/quick-everyone-lets-make-an-insurance-ai-startup-581088.aspx) |
| **AgentOS** | Procurement-automation agents | Series B / $85M | 2026 | a16z | [New Market Pitch](https://newmarketpitch.com/blogs/news/agentic-ai-funding-trends) |
| **Traza** | Procurement/supply-chain agents | Pre-seed / $2.1M | 2026 | Base10 | [Pulse2](https://pulse2.com/traza-2-1-million-raised-to-automate-procurement-and-supply-chain-operations-with-ai-workers/) |
| **Warp** | AI-native payroll/HR/compliance/IT | $85M | 2026 | Battery, Peak XV, Sapphire | [asanify](https://asanify.com/blog/news/ai-agents-enterprise-stack-april-28-2026/) |
| **Niural** | AI payroll/PEO + compliance | Series A ext → $52M | Apr 2026 | (n/d) | [Fundraise Insider](https://fundraiseinsider.com/blog/niural-adds-21m-expanding-series-a-to-52m-for-ai-payroll/) |
| **Skyfire** | Agent identity + payments (KYA) | $9.5M | 2025 | a16z CSX, Coinbase Ventures | [Chainalysis](https://www.chainalysis.com/blog/x402-agentic-payments-adoption/) |
| **Payman** | FI-deployed agent transactions | $13.8M | 2025 | Visa, Coinbase Ventures | [Chainalysis](https://www.chainalysis.com/blog/x402-agentic-payments-adoption/) |
| **Oasis Security** | Non-human / agent identity mgmt | Series B / $120M | 2026 | (n/d) | [SC Media](https://www.scworld.com/brief/oasis-security-raises-120-million-for-non-human-identity-management) |
| **Mem0** | Agent memory layer | Seed+A / $24M | 2025-26 | Kindred, Basis Set, YC | [Mem0](https://mem0.ai/series-a) |
| **Braintrust** | Agent evals/observability | Series B / $80M @ $800M | 2025-26 | (n/d) | [Braintrust](https://www.braintrust.dev/articles/best-ai-observability-tools-2026) |
| **Browser Use** | Browser/web-agent infra | Seed / $17M | Mar 2025 | Felicis, YC | [SiliconANGLE](https://siliconangle.com/2025/03/23/browser-use-raises-17m-help-steer-ai-agents-internet/) |
| **AIUC** | Insurance/audit/cert for AI agents | Seed / $15M | Jun 2025 | Nat Friedman/NFDG, Emergence | [Fortune](https://fortune.com/2025/07/23/ai-agent-insurance-startup-aiuc-stealth-15-million-seed-nat-friedman/) |

*(n/d = specific lead investor not disclosed in the source consulted.)*

---

## White space & the graveyard

### White space (pain repeatedly named, no clear enterprise-embedded winner)
1. **Compliant, empathetic collections & loss-mitigation** — Salient/Kastle prove outbound automation, but the *hard, defensible* part (state-by-state FDCPA/Reg-F compliance, hardship detection, promise-to-pay orchestration, human handoff on distress signals) inside a *named card/consumer-lending book* is unclaimed. Direct fit: **Barclays collections, Lendmark**. ([HES FinTech](https://hesfintech.com/blog/ai-in-debt-collection-key-trends-and-approaches/))
2. **HOA / community-association *bank-side* finance ops** — Vantaca/Assembly own the management-company side; nobody owns the *bank's* view: cash application of homeowner dues, reserve-fund monitoring, delinquency/lien workflows, fraud on association accounts. Direct fit: **Western Alliance HOA banking**. ([AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge))
3. **Loyalty/rewards ops in the agentic-commerce era** — no pure-play winner; agent-mediated purchasing threatens to disintermediate loyalty. Direct fit: **ampliFI, Amex, Visa**. ([PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2026/how-brands-are-reinventing-loyalty-for-the-ai-decision-maker/))
4. **Payroll/HR *exception* handling in regulated pay** — funded players (Warp/Niural) sell full stacks to SMBs; the enterprise pain is *exceptions* (retro pay, garnishments, multi-jurisdiction tax, off-cycle, benefits reconciliation). Niural itself is pivoting to "long-horizon agents for high-stakes regulated" work. Direct fit: **ADP**. ([Fundraise Insider](https://fundraiseinsider.com/blog/niural-adds-21m-expanding-series-a-to-52m-for-ai-payroll/))
5. **Dispute / chargeback orchestration** — cited as increasingly agent-run but no clear standalone winner; fits **Visa/Amex/Capital One**. ([PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2026/how-brands-are-reinventing-loyalty-for-the-ai-decision-maker/))

### The graveyard (do NOT pitch these)
- **Generic AI SDRs / outbound "AI BDR"** — 50-70% annual churn, deliverability collapse, brand/domain damage, commoditized datasets, "18-month half-life." ([DigitalApplied](https://www.digitalapplied.com/blog/case-against-ai-sdrs-contrarian-analysis-2026))
- **Meeting notetakers / transcription** — accuracy commoditized (90-95%+ across 8 tools); differentiators are just integrations. ([Laxis](https://www.laxis.com/blog/state-of-meeting-note-taking-2026/))
- **Thin "chat-layer" wrappers with no proprietary data/workflow moat** — ~80% of AI startups projected to fail by end-2026; margins collapse as models commoditize. ([IdeaProof](https://ideaproof.io/failures/ai-startups))
- **Me-too horizontal "AI copilot for X"** where a hyperscaler or incumbent (Sage, Waystar, ADP) is already shipping the same feature — you'll be commoditized on arrival.

---

## Implications for Genesis Track A

- **Pick a "service-as-software" framing, not a "copilot."** Judges reward impact + originality; the market rewards *doing the work* per outcome. Frame the demo as an **autonomous workflow that closes a labor-line task**, with a human-in-the-loop gate — exactly what a16z/Sequoia/Bessemer say wins, and what Series-A investors now demand (multi-agent routing + persistent state + HITL). This scores on impact (25) and originality (15) simultaneously.
- **Choose a client where the *exact* enterprise-embedded version is still open** (collections at Barclays, HOA bank-ops at Western Alliance, loyalty ops at ampliFI, payroll exceptions at ADP). The startup proof exists *adjacent* to each — de-risking feasibility (25) and impact (25) — but the named-enterprise version is novel (originality 15).
- **Lean on the outcome metric in the pitch.** Dollars recovered, delinquency-roll-rate reduction, false-positive reduction, hours saved per exception — mirror how funded startups quantify ROI (Salient +20-30% payment rates; Daylit AR opex -75%; KYC onboarding -90%). Feasibility judges love a crisp, measurable target on synthetic data.
- **Reuse infrastructure; don't rebuild it.** Anthropic/OpenAI for reasoning; borrow patterns from agent memory (Mem0), evals/observability (Braintrust-style eval harness — great for the "technical depth 25%" story), guardrails/HITL, and (for payments/loyalty concepts) x402/agent-identity vocabulary. Showing an **eval + guardrail layer** is the cheapest way to win "technical depth."
- **Avoid the graveyard** (SDRs, notetakers, generic copilots) and avoid categories a hyperscaler/incumbent already ships to your client (e.g., don't pitch generic RCM to a Waystar-served provider, or generic HR copilots to ADP).
- **Compliance is a feature, not a footnote.** In every Zenon finance client, the defensible moat is regulatory correctness (Reg F, FDCPA, FCRA, BSA/AML, garnishment law). Building the *compliance-aware* version of a proven agent is the highest-originality, highest-feasibility path — and it's precisely where thin startups fail.

---

## Candidate use-case seeds (one-liners: *Startup X proved Y → better Zenon-client version Z*)

1. **Salient/Kastle proved AI voice+workflow collections lift payment rates 20-30% → a Reg-F-compliant, hardship-aware collections agent for *Barclays* card delinquencies that detects distress and escalates to humans.** ([a16z](https://a16z.com/announcement/investing-in-salient/))
2. **AgentCollect/Salient proved consumer-lending servicing agents → an end-to-end delinquency & loss-mitigation agent for *Lendmark* installment loans (promise-to-pay orchestration + settlement offers within policy).** ([YC](https://www.ycombinator.com/companies/agentcollect))
3. **Vantaca (+$300M) proved HOA management software → an *HOA bank-ops* agent for *Western Alliance*: auto cash-application of homeowner dues, reserve-fund anomaly detection, lien/delinquency workflow.** ([AI Consulting Network](https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge))
4. **EliseAI proved property-ops assistants → a small-business banking onboarding + deposit-ops exception agent for *Western Alliance* SMB clients (KYC-lite, doc chase, cash-flow underwriting for <$250K credit).** ([Beam](https://beam.ai/agentic-insights/ai-agents-banking-2026-beyond-chatbots))
5. **Diligent AI / Norm Ai proved KYC-AML agents clear false positives → a *false-positive-triage* alert-adjudication agent for a *Capital One / Western Alliance* AML queue with full audit trail (attacks the 95%-wasted-investigator-time stat).** ([AML Network](https://amlnetwork.org/aml-news/diligent-ai-secures-e2-1-million-seed-funding-to-automate-kyc-and-aml-compliance-workflows-with-ai-agents/))
6. **Decagon/Sierra proved outcome-priced CX agents → a *dispute & chargeback orchestration* agent for *Visa/Amex/Capital One* (evidence gathering, network-rule reasoning, representment drafting).** ([Bloomberg](https://www.bloomberg.com/news/articles/2026-01-28/ai-customer-support-startup-decagon-valued-at-4-5-billion))
7. **Stabile + x402/PYMNTS proved loyalty must adapt to agentic commerce → a *loyalty-ops* agent for *ampliFI/Amex* that optimizes offer targeting and detects rewards fraud/abuse in real time.** ([PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2026/how-brands-are-reinventing-loyalty-for-the-ai-decision-maker/))
8. **Fazeshift/Daylit proved AR agents (>90% automation, opex -75%) → an *AR/collections + cash-application* agent for *Invesco/Morgan Stanley* institutional back-office (invoice→match→reconcile→dunning).** ([Crunchbase](https://news.crunchbase.com/fintech/fazeshift-accounts-receivable-ai-finance-ops-startup-funding/))
9. **Warp/Niural proved AI payroll+compliance → a *payroll-exception* resolution agent for *ADP* (retro pay, garnishments, multi-jurisdiction tax, off-cycle) with human sign-off — attacking exceptions, not the whole stack.** ([Fundraise Insider](https://fundraiseinsider.com/blog/niural-adds-21m-expanding-series-a-to-52m-for-ai-payroll/))
10. **Harvey/Legora/Eudia proved contract-review agents → a *vendor-contract & obligation-tracking* agent for *J&J* or *Kohl's* procurement (renewal risk, clause deviation, SLA/obligation monitoring).** ([CNBC](https://www.cnbc.com/2026/03/25/legal-ai-startup-harvey-raises-200-million-at-11-billion-valuation.html))
11. **Adonis/Abridge proved AI-first RCM (denials 41%) → a *prior-auth + denial-appeal* agent for *J&J*-adjacent patient-access / market-access programs (CMS 7-day turnaround as the target metric).** ([Innovaccer](https://innovaccer.com/blogs/selecting-agentic-ai-healthcare))
12. **AgentOS/Lumari/Traza proved procurement agents (opex -30%) → a *retail merchandise/vendor procurement* agent for *Kohl's* (RFQ, PO expediting, supplier chase, exception routing).** ([Pulse2](https://pulse2.com/traza-2-1-million-raised-to-automate-procurement-and-supply-chain-operations-with-ai-workers/))
13. **DiligenceSquared/Zarna proved diligence-associate agents → an *investment-diligence / fund-doc* agent for *Invesco/Morgan Stanley* (data-room extraction, memo drafting, red-flag surfacing).** ([CB Insights F25](https://www.cbinsights.com/research/y-combinator-fall2025/))
14. **Corgi/Harper proved insurance claims/underwriting agents → a *small-business insurance or credit-insurance* underwriting-triage agent for a *Western Alliance / Lendmark* lending workflow.** ([FinanceX](https://www.financexmagazine.com/post/insurtech-s-1-63-billion-tell-ai-is-no-longer-the-pitch-it-s-the-plumbing))
15. **Dow Jones adjacency: media has no breakout vertical agent → a *newsroom research + entity/market-event monitoring* agent for *Dow Jones* that turns filings/wires into structured, sourced briefs (mirrors OpenEvidence's "act on data" pattern in a media context).** ([Bessemer](https://www.bvp.com/atlas/the-state-of-ai-2025))

---

## Sources

**YC batches & RFS**
- YC Requests for Startups — https://www.ycombinator.com/rfs
- The VC Corner, YC Summer 2026 RFS — https://www.thevccorner.com/p/yc-summer-2026-requests-for-startups-ideas
- CB Insights, YC Summer 2025 — https://www.cbinsights.com/research/y-combinator-summer2025/
- CB Insights, YC Fall 2025 — https://www.cbinsights.com/research/y-combinator-fall2025/
- CB Insights, YC Winter 2026 — https://www.cbinsights.com/research/y-combinator-winter-2026/
- TechCrunch, 16 most interesting YC W26 — https://techcrunch.com/2026/03/26/16-of-the-most-interesting-startups-from-yc-w26-demo-day/
- Extruct AI, YC W26 breakdown — https://www.extruct.ai/research/ycw26/
- catalaize, YC S25 profile — https://catalaize.substack.com/p/y-combinator-s25-batch-profile-and
- PitchBook, YC all-in on agents — https://pitchbook.com/news/articles/y-combinator-is-going-all-in-on-ai-agents-making-up-nearly-50-of-latest-batch

**VC theses**
- a16z, outcome-based pricing — https://a16z.com/newsletter/december-2024-enterprise-newsletter-ai-is-driving-a-shift-towards-outcome-based-pricing/
- Bessemer, State of AI 2025 — https://www.bvp.com/atlas/the-state-of-ai-2025
- Bessemer, Building Vertical AI (Jan 2026 PDF) — https://www.bvp.com/assets/uploads/2026/01/BUILDING-VERTICAL-AI_PDF_BESSEMER_VENTURE_PARTNERS_BOOK_JANUARY_2026.pdf
- Sequoia AI Ascent 2026 — https://www.theaiopportunities.com/p/sequoia-ai-ascent-2026-the-future
- Sequoia AI 50 (agents beyond chat) — https://sequoiacap.com/article/ai-50-2025/
- Menlo Ventures, State of GenAI in the Enterprise 2025 — https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/

**Funding trends / market**
- New Market Pitch, agentic-AI funding trends 2026 — https://newmarketpitch.com/blogs/news/agentic-ai-funding-trends
- New Market Pitch, agentic-AI funding analysis 2025-26 — https://newmarketpitch.com/blogs/news/agentic-ai-funding-analysis
- SaaS Mag, vertical AI eating SaaS — https://www.saasmag.com/vertical-ai-agents-eating-horizontal-saas/

**Financial-services ops**
- a16z, Investing in Salient — https://a16z.com/announcement/investing-in-salient/
- WebProNews, Salient $25M ARR — https://www.webpronews.com/salients-ai-loan-machine-25m-arr-in-two-years-without-a-single-customer-loss/
- StockTitan/CPSS deploys Salient — https://www.stocktitan.net/news/CPSS/consumer-portfolio-services-deploys-ai-powered-servicing-platform-uxgwpzptlf1v.html
- YC, Kastle — https://www.ycombinator.com/companies/kastle
- Crunchbase, Kastle — https://www.crunchbase.com/organization/kastle
- YC, AgentCollect — https://www.ycombinator.com/companies/agentcollect
- Crunchbase, Fazeshift $17M — https://news.crunchbase.com/fintech/fazeshift-accounts-receivable-ai-finance-ops-startup-funding/
- CPA Practice Advisor, Basis $100M — https://www.cpapracticeadvisor.com/2026/02/24/basis-raises-100-million-to-deploy-ai-agents-for-accounting-firms/178759/
- SiliconANGLE, Basis $100M — https://siliconangle.com/2026/02/24/ai-accounting-startup-basis-secures-100m-1-15b-valuation-firms-adopt-agent-based-workflows/
- Rillet, $70M Series B — https://www.rillet.com/blog/rillet-raises-70m-series-b-from-andreessen-horowitz-and-iconiq
- Crunchbase, Rillet — https://news.crunchbase.com/fintech/startup-rillet-ai-seriesb-a16z-iconiq/
- Yahoo Finance, Daylit playbook — https://finance.yahoo.com/sectors/technology/articles/ai-startup-giving-away-playbook-130000651.html
- TechFundingNews, Zalos $3.6M — https://techfundingnews.com/ai-meets-finance-zalos-snaps-3-6m-to-build-computer-agents-for-cfos/
- ChatFin, 2026 finance AI spend — https://chatfin.ai/blog/2026-finance-ai-spending-cfo-strategies-for-autonomous-agent-deployment/
- Barclays US, AI in consumer banking 2026 — https://cards.barclaycardus.com/banking/about-us/news-and-views/insights/top-five-ai-innovations-shaping-consumer-banking-in-2026/
- HES FinTech, AI in debt collection 2026 — https://hesfintech.com/blog/ai-in-debt-collection-key-trends-and-approaches/
- PYMNTS, Taktile $110M agent-first banks — https://www.pymnts.com/news/artificial-intelligence/2026/this-ceo-just-raised-110-million-to-make-banks-agent-first/
- Beam, AI agents in banking 2026 — https://beam.ai/agentic-insights/ai-agents-banking-2026-beyond-chatbots
- Kore.ai, 12 banking use cases — https://www.kore.ai/blog/ai-agents-in-finance-banking-12-proven-use-cases-2026

**Compliance / KYC-AML**
- EU-Startups, Diligent AI €2.1M — https://www.eu-startups.com/2026/03/yc-backed-diligent-ai-raises-e2-1-million-to-automate-kyc-and-aml-workflows-using-ai-agents/
- AML Network, Diligent AI + regtech rounds — https://amlnetwork.org/aml-news/diligent-ai-secures-e2-1-million-seed-funding-to-automate-kyc-and-aml-compliance-workflows-with-ai-agents/
- Fintech Global, Steward $5M — https://fintech.global/2026/03/18/ai-compliance-platform-steward-secures-5m-funding/

**Healthcare admin**
- Innovaccer, agentic RCM 2026 — https://innovaccer.com/blogs/selecting-agentic-ai-healthcare
- Aspirion, RCM 2025 insights / 2026 predictions — https://www.aspirion.com/the-year-ai-transformed-revenue-cycle-2025-insights-and-2026-predictions/

**Legal**
- CNBC, Harvey $11B — https://www.cnbc.com/2026/03/25/legal-ai-startup-harvey-raises-200-million-at-11-billion-valuation.html
- TechCrunch, Legora $5.6B — https://techcrunch.com/2026/04/30/legal-ai-startup-legora-hits-5-6-valuation-and-its-battle-with-harvey-just-got-hotter/
- aifundingtracker, legal AI — https://aifundingtracker.com/top-legal-ai-startups/

**Real estate / HOA**
- The AI Consulting Network, proptech AI unicorns 2026 — https://www.theaiconsultingnetwork.com/blog/proptech-ai-unicorns-2026-cre-investment-surge
- YC, Housing & Real Estate companies — https://www.ycombinator.com/companies/industry/housing-and-real-estate

**Customer ops**
- Bloomberg, Decagon $4.5B — https://www.bloomberg.com/news/articles/2026-01-28/ai-customer-support-startup-decagon-valued-at-4-5-billion
- Businesswire, Decagon $131M — https://www.businesswire.com/news/home/20250623894798/en/Decagon-Raises-$131M-at-$1.5B-Valuation-to-Deliver-Concierge-Customer-Experience-with-AI-Agents
- Sacra, Sierra vs Decagon — https://sacra.com/research/sierra-vs-decagon/

**Procurement / HR-payroll**
- Pulse2, Traza $2.1M — https://pulse2.com/traza-2-1-million-raised-to-automate-procurement-and-supply-chain-operations-with-ai-workers/
- Fundraise Insider, Niural $52M — https://fundraiseinsider.com/blog/niural-adds-21m-expanding-series-a-to-52m-for-ai-payroll/
- asanify, AI enterprise stack (Warp) — https://asanify.com/blog/news/ai-agents-enterprise-stack-april-28-2026/
- Sage, AI agents across finance/HR/ops — https://www.sage.com/en-us/news/press-releases/2026/04/sage-expands-ai-agents-across-finance-hr-and-operations-to-automate-workflows/

**Loyalty / agentic commerce**
- PYMNTS, reinventing loyalty for the AI decision-maker — https://www.pymnts.com/artificial-intelligence-2/2026/how-brands-are-reinventing-loyalty-for-the-ai-decision-maker/
- Chain Store Age, AI agents shop for us — https://chainstoreage.com/when-ai-agents-shop-us-how-will-loyalty-programs-keep

**Insurance**
- FinanceX, insurtech $1.63B Q1 2026 — https://www.financexmagazine.com/post/insurtech-s-1-63-billion-tell-ai-is-no-longer-the-pitch-it-s-the-plumbing
- Insurance Business, "make an insurance AI startup" — https://www.insurancebusinessmag.com/us/news/technology/quick-everyone-lets-make-an-insurance-ai-startup-581088.aspx

**Agent infrastructure**
- Chainalysis, x402 agentic payments — https://www.chainalysis.com/blog/x402-agentic-payments-adoption/
- PRNewswire, Fireblocks x402 suite — https://www.prnewswire.com/news-releases/fireblocks-joins-x402-foundation-launches-agentic-payments-suite-302777251.html
- SC Media, Oasis Security $120M — https://www.scworld.com/brief/oasis-security-raises-120-million-for-non-human-identity-management
- SiliconANGLE, GitGuardian $50M — https://siliconangle.com/2026/02/11/gitguardian-raises-50m-expand-non-human-identity-ai-agent-security/
- Mem0, Series A ($24M) — https://mem0.ai/series-a
- BigDATAwire, Letta $10M — https://www.hpcwire.com/bigdatawire/this-just-in/letta-emerges-from-stealth-with-10m-to-build-ai-agents-with-advanced-memory/
- Braintrust, observability guide (funding refs) — https://www.braintrust.dev/articles/best-ai-observability-tools-2026
- Presenc, agent-infra startups May 2026 — https://presenc.ai/research/ai-agent-infrastructure-startups-2026
- SiliconANGLE, Browser Use $17M — https://siliconangle.com/2025/03/23/browser-use-raises-17m-help-steer-ai-agents-internet/
- SiliconANGLE, Kernel $22M — https://siliconangle.com/2025/10/09/kernel-raises-22m-power-browser-infrastructure-ai-agents/
- Fortune, AIUC $15M — https://fortune.com/2025/07/23/ai-agent-insurance-startup-aiuc-stealth-15-million-seed-nat-friedman/
- prompt.security, AI security startups map — https://startups.prompt.security/
- GeekWire, CodeIntegrity $5M — https://www.geekwire.com/2026/codeintegrity-raises-4-8m-to-put-permanent-guardrails-on-unpredictable-ai-agents/

**Graveyard**
- DigitalApplied, case against AI SDRs — https://www.digitalapplied.com/blog/case-against-ai-sdrs-contrarian-analysis-2026
- Laxis, state of note-taking 2026 — https://www.laxis.com/blog/state-of-meeting-note-taking-2026/
- IdeaProof, AI startups that failed — https://ideaproof.io/failures/ai-startups

---
*Compiled 2026-07-14 via WebSearch/WebFetch. Figures from secondary aggregators are labeled; verify exact round mechanics against primary filings before external use. Currency: emphasis on last ~12 months (mid-2025 → Jul 2026).*
