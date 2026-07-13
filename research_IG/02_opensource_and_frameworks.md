# WS2 — Open-Source & Reference Builds (Feasibility Map)

*Research date: 13 Jul 2026. Workstream: WS2 of Genesis 2026 five-agent sweep. Focus: Track A (client-facing agentic finance).*

## TL;DR — so what for Genesis 2026

The OSS ground is genuinely solid enough that a 2–3 person Zenon team should spend near-zero build-weeks on plumbing and nearly all six weeks on the **domain layer** — the part judges can't get from a GitHub repo. Recommended default stack: **LangGraph** (MIT, 37.1k★, v1.2.9 Jul 2026) as the orchestration backbone for anything with real multi-agent state/HITL needs — it has the deepest checkpointing/observability story of any OSS framework and deploys cleanly on AWS (Lambda/ECS/Fargate) or via **Amazon Bedrock AgentCore**, which is now the AWS-blessed production harness (Bedrock Agents "Classic" stops taking new customers 30 Jul 2026 [AWS Prescriptive Guidance, 2026](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/bedrock-agents.html)). Pair it with **Claude Agent SDK** or **PydanticAI** for individual tool-using subagents where type-safe structured output matters (credit/compliance use cases). For the Zenon-specific capability layer: **Nixtla statsforecast/Darts/Prophet** for forecasting, **Great Expectations + Soda Core + Capital One's datacompy** for reconciliation/DQ (datacompy is *literally built by a bank* for this exact problem), **SDV** for synthetic tabular/relational data (note: **Gretel is gone** — NVIDIA acquired it and archived the OSS repos in Feb 2026, leaving SDV as the strongest fully-open option), **Docling** for document extraction, **SHAP** for credit-risk explainability, and **Langfuse + DeepEval/RAGAS + promptfoo** for the eval/observability stack the AI judge will be scoring for engineering rigor. The single highest-stakes finding: **Anthropic itself shipped 10 finance agent templates in May 2026** — including a GL reconciler, month-end closer, statement auditor, and KYC screener — built on a skills/connectors/subagents pattern [Anthropic, May 2026](https://www.anthropic.com/news/finance-agents). This is both a *reference architecture to copy* and a *competitive ceiling*: any Zenon idea that looks like "generic agent + generic connector" is now competing with a free vendor template. Zenon's white space is the proprietary domain layer these templates don't have: roll-rate/impairment semantics, curve libraries, bank-specific chart-of-accounts logic, and regulatory narrative generation — exactly the deep-domain layer OSS cannot and does not provide.

---

## 1. Agentic framework comparison (mid-2026 state)

| Framework | License | Maturity (mid-2026) | Orchestration model | Eval/observability | AWS deployability | 6-wk finance-build fit |
|---|---|---|---|---|---|---|
| **LangGraph** | MIT | Very high — 37.1k★, v1.2.9 (Jul 2026), LangGraph 1.0 shipped Q2 2026 [GitHub, Jul 2026](https://github.com/langchain-ai/langgraph) | Directed graph, explicit state schema, conditional edges | LangSmith (native, best-in-class tracing/checkpointing) | Runs anywhere (Lambda/ECS/EKS); no lock-in | **Best default** — most production-ready, steepest but manageable learning curve [QubitTool, 2026](https://qubittool.com/blog/ai-agent-framework-comparison-2026) |
| **CrewAI** | MIT | Very high — 55.4k★, v1.15.2 (Jul 2026), added A2A protocol + enterprise scheduling [GitHub, Jul 2026](https://github.com/crewAIInc/crewAI) | Role-based "crews," sequential/hierarchical process types | Growing but lighter than LangSmith; limited checkpointing | Straightforward container deploy | Fastest to a demo (20 lines to a working crew) but weaker durable-state story for HITL-heavy finance workflows |
| **AutoGen / AG2** | MIT | Medium — Microsoft put AutoGen in **maintenance mode**; community fork AG2 continues independently | Conversational GroupChat / debate patterns | In-memory by default, weaker persistence | Fine, but declining first-party investment | Good for "bull/bear/risk debate" style analysis agents; declining strategic bet |
| **Microsoft Agent Framework** | MIT | High — v1.0 shipped 3 Apr 2026, unifies AutoGen + Semantic Kernel into one enterprise SDK [Microsoft devblog, 2026](https://devblogs.microsoft.com/agent-framework/migrate-your-semantic-kernel-and-autogen-projects-to-microsoft-agent-framework-release-candidate/) | Session-based state + AutoGen-style multi-agent | Built-in telemetry, enterprise filters | Best for Azure; usable on AWS via containers | Strong if the team is already .NET/SK-invested; otherwise no edge over LangGraph for a Python finance build |
| **OpenAI Agents SDK** | MIT (open-source SDK) | High — recently added a "harness" system (same scaffolding as Codex) for long-running, resumable agents | Explicit typed **handoffs** + guardrails between specialized agents | Native tracing dashboard | Model-agnostic-ish but OpenAI-centric | Simplest orchestration model in the ecosystem; good if committing to OpenAI models |
| **Claude Agent SDK** | Open-source (Anthropic) | High — evolved directly from Claude Code; "give the agent a computer" (shell/fs/web) paradigm | Hooks + **subagents** (child-agent delegation), MCP for external tools | Session-based; weaker for multi-day workflows out of the box | Deploys as any containerized process; integrates with Bedrock via Claude models | Excellent for deep tool-use / document-heavy agents; state mgmt needs your own Redis/Postgres layer for long-running jobs [Composio, 2026](https://composio.dev/content/claude-agents-sdk-vs-openai-agents-sdk-vs-google-adk) |
| **PydanticAI** | MIT | High — 18.5k★, v2.9.0 (Jul 2026) [GitHub, Jul 2026](https://github.com/pydantic/pydantic-ai) | Type-safe agent + tool contracts, dependency injection | Tight Pydantic Logfire integration | Lightweight, deploys anywhere | **Strong fit for compliance-adjacent finance work** — structured, validated I/O is exactly what credit/KYC/regulatory outputs need [QED42, 2026](https://www.qed42.com/insights/choosing-the-right-agentic-ai-framework-smolagents-pydanticai-and-llamaindex-agentworkflows) |
| **smolagents** (Hugging Face) | Apache-2.0 | Medium-high — ultra-minimal (~1,000 LOC), code-first agent (writes/executes Python instead of JSON tool calls) | Single-agent, code-execution loop | Minimal built-in; bring your own | Easy to containerize | Good for narrow, fast prototypes; not a multi-agent orchestrator |
| **LlamaIndex Workflows** | MIT | High — Workflows 1.0 announced 22 Jun 2026, event-driven/async/step-based | Event-driven steps (not a strict graph) | LlamaIndex's own observability tooling | Standard container deploy | Best when the core task is RAG-grounded (filings, policy docs) rather than pure orchestration |
| **AWS Strands Agents SDK** | Apache-2.0 | High and AWS-native — active weekly commits through Jul 2026, first-class Bedrock/Anthropic/OpenAI/Gemini support [AWS Open Source Blog, 2026](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/) | Model-driven ("just describe the agent"), MCP + multi-agent patterns built in | Ships with AgentCore Observability integration | **Deepest AWS integration** — pairs directly with Bedrock AgentCore | Best choice if judges specifically reward "runs natively on our AWS/Bedrock stack" |
| **Amazon Bedrock AgentCore** | AWS managed service (not OSS) | GA in 2026; 2-call harness (CreateHarness/InvokeHarness) with managed memory, identity, tool gateway, CloudWatch observability, A2A support [AWS ML Blog, 2026](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-harness-is-now-generally-available-go-from-idea-to-production-grade-agent-in-minutes/) | N/A (managed) | Not a build framework, it's a **deployment target** | Native CloudWatch dashboards | Note: **Bedrock Agents "Classic" closes to new customers 30 Jul 2026** — any Bedrock-native design should target AgentCore, not Classic |

**Bottom line for the pitch deck:** LangGraph (or Strands if leaning into AWS-native positioning) for orchestration + Claude Agent SDK/PydanticAI for structured subagents + Bedrock AgentCore as the AWS production target is a stack no judge can call "just a prompt wrapper."

---

## 2. Open finance/analytics agent projects — what actually works vs. demo-ware

| Project | What it is | Status / maturity | Verdict |
|---|---|---|---|
| **FinRobot** (AI4Finance-Foundation) | Multi-agent equity-research platform: Lead Agent orchestrates specialist agents (data → valuation → debate → synthesis → report) | 7,000+★, actively maintained, now has a desktop app [Ultra Lab, 2026](https://ultralab.tw/en/blog/ai-finance-github-projects-2026); GitHub: [AI4Finance-Foundation/FinRobot](https://github.com/ai4finance-foundation/finrobot) | Real, well-architected reference for a "research pipeline" pattern (lead + specialists + debate). Good to study the orchestration graph, not to fork wholesale for a bank/credit use case — it's equity-research-flavored. |
| **OpenBB (Open Data Platform)** | Open data platform unifying market/company data behind one API, with MCP servers for agent consumption | Actively maintained, "connect once, consume everywhere" model; exposes Python, Excel, MCP, REST [GitHub, 2026](https://github.com/OpenBB-finance/OpenBB) | Useful as a **data-connector layer**, not an agent framework itself. Handy if a demo needs realistic market-data plumbing rather than synthetic-only. |
| **"AI hedge fund" repos** (bull/bear/fundamentals/technicals/risk debate agents) | Multi-persona debate agents producing trade recommendations | Described as the most-starred AI-finance repo category by a wide margin; growing fast | **Mostly demo-ware for Track A purposes**: fun for a debate-pattern reference, but they simulate trading conviction, not the reconciliation/credit/DQ work Zenon actually sells. Useful only as an orchestration-pattern reference (multi-perspective debate → synthesis), not a fork target. |
| **Vanna** (text-to-SQL) | MIT-licensed agentic-retrieval text-to-SQL framework | **Archived by its owner 29 Mar 2026** [towardsai.net, 2026](https://pub.towardsai.net/i-turned-an-archived-23k-star-text-to-sql-project-into-a-self-hosted-tool-that-actually-works-out-b08abcb6d0e3); commercial "Vanna Cloud" continues, OSS repo frozen [GitHub](https://github.com/vanna-ai/vanna) | **Important finding**: the leading OSS text-to-SQL project just went unmaintained. A fork is usable but needs hardening — this is a genuine white-space/timing opportunity (see WS2-D), not a "just npm install it" building block anymore. |
| **Anthropic Financial Services agent templates** | 10 packaged agent templates: pitch builder, meeting prep, earnings reviewer, model builder, market researcher, valuation reviewer, **GL reconciler, month-end closer, statement auditor, KYC screener** | Launched 5 May 2026; architecture = skills + connectors (FactSet, S&P CapIQ, Moody's, PitchBook, etc.) + subagents; deploys via Claude Cowork/Code or Claude Managed Agents; reference repo [anthropics/financial-services](https://github.com/anthropics/financial-services) [Anthropic, May 2026](https://www.anthropic.com/news/finance-agents) | **The most important reference architecture in this entire sweep.** Study the skills/connectors/subagents pattern directly. Also a competitive ceiling — see Section 5. |
| **Ballerine** | Open-source KYC/KYB/risk-decisioning infrastructure (rule engine, workflow engine, case-management back office) | YC-backed, 800+★, actively developed [ballerine-io/ballerine](https://github.com/ballerine-io/ballerine); TechCrunch coverage from 2023 confirms early real bank/fintech adoption | Real, usable infra for an AML/KYC onboarding agent — not demo-ware. License not independently confirmed in this pass (flag as **unverified** license text; check repo before committing to it). |
| **moov-io/watchman** | OFAC/sanctions/watchlist screening — HTTP server, Go library, and **MCP server** | Apache-2.0, 479★, maintained by Moov (real fintech-infra company) [GitHub, Jul 2026](https://github.com/moov-io/watchman) | Small but solid, single-purpose, and already MCP-native — drops straight into an agent tool belt for sanctions screening. |
| **vyayasan/kyc-analyst** | OSS KYC/AML plugin built specifically for Claude Cowork/Code, with 17 human-in-the-loop checkpoints and deterministic risk scoring | Recent 2026 project [GitHub](https://github.com/vyayasan/kyc-analyst) | Direct proof-of-concept that "agentic KYC on Claude" is already being built by others — worth studying for pattern, tempers originality of a similar Zenon pitch. |

---

## 3. Building blocks by Zenon-relevant capability

| Capability | Project | License | Maturity | What it saves you building |
|---|---|---|---|---|
| **Forecasting** | Nixtla **statsforecast** | Apache-2.0 | High, fast-moving [GitHub](https://github.com/Nixtla/statsforecast) | Millions-of-series-scale AutoARIMA/AutoETS/AutoCES/MSTL/Theta — "replaces Prophet in two lines" |
| | Nixtla **TimeGPT** (foundation model) + SDK | SDK is Apache-2.0; the hosted TimeGPT model itself is **closed-source/API-based** [GitHub license](https://github.com/Nixtla/nixtla/blob/main/LICENSE) | High | Zero-shot forecasting/anomaly baseline without training your own model — useful as a fast "second opinion" |
| | **Prophet** (Meta) | MIT [GitHub](https://github.com/facebook/prophet) | Very mature, low-maintenance-mode | Simple, explainable baseline forecaster non-technical stakeholders already trust |
| | **Darts** (Unit8) | Apache-2.0 [GitHub](https://github.com/unit8co/darts) | High, batteries-included | One API surface spanning classical, ML (GBM/RF), and deep (RNN/Transformer/NBEATS) models — good for scenario/ensemble work |
| **Data quality / reconciliation** | **Great Expectations** | Apache-2.0 | High, Python-first | Declarative "expectations" + orchestrator integrations (Airflow/Dagster) — the QC layer Zenon already does by hand |
| | **Soda Core** | Apache-2.0 | High, SQL-native | Lightweight CLI checks; ships **metric, record, and schema reconciliation checks** natively [PipeCode, 2026](https://pipecode.ai/blogs/data-quality-frameworks-great-expectations-vs-dbt-tests-vs-soda-core) |
| | **dbt tests** | Apache-2.0 (dbt Core) | Very high, ubiquitous | "Shift-left" QC embedded directly in the transform layer for teams already on dbt |
| | **datacompy** (Capital One) | Open-source, bank-built [Capital One Tech, 2026](https://www.capitalone.com/tech/open-source/datacompy-open-source-dataframe-comparisons/) | Very high — 12M+ downloads, supports Pandas/Spark/Polars/Snowflake [GitHub](https://github.com/capitalone/datacompy) | **Directly maps to Zenon's Visa/reconciliation work** — a bank already solved "human-readable dataframe diff with tolerances" so nobody has to rebuild PROC COMPARE |
| **Synthetic data** | **SDV** (Synthetic Data Vault / DataCebo) | Open-source core (SDV) | High, long track record across finance/healthcare/logistics [DataCebo](https://datacebo.com/sdv-dev/) | Tabular/relational/time-series synthesis (CTGAN and others) with real statistical fidelity — **now the strongest fully-open option** |
| | **Faker** | MIT | Very mature | Fast dummy PII (names/addresses/IDs) — not statistically faithful, use only to dress up SDV/rule-based cores |
| | ~~Gretel~~ | N/A | **Archived** — NVIDIA acquired Gretel (Mar 2025); GitHub org archived 18 Feb 2026; functionality absorbed into proprietary NVIDIA NeMo Data Designer under enterprise licensing [TechCrunch, Mar 2025](https://techcrunch.com/2025/03/19/nvidia-reportedly-acquires-synthetic-data-startup-gretel/); [SynthForge, May 2026](https://synthforge.io/alternatives/gretel/) | **Do not plan around Gretel OSS** — it no longer exists as an open option. This directly strengthens the case for Zenon building its own synthetic-data layer (I8) rather than assuming a strong OSS incumbent will always be there. |
| **Explainability** | **SHAP** | MIT | Very mature, industry-standard [GitHub](https://github.com/shap/shap) | Shapley-value feature attribution — the actual math behind every "explainable credit risk" claim; gives the numbers, not the regulator-ready narrative |
| **Document extraction** | **Docling** (IBM/DS4SD) | MIT [GitHub](https://github.com/docling-project/docling) | High, fast-moving (45 pg/s GPU, best-in-class complex-table extraction ~98% accuracy) | GAAP-agnostic but strong structural extraction (tables, layout) from PDFs/filings/statements |
| | **Unstructured** | Apache-2.0 (core), hosted API tier also available [GitHub](https://github.com/Unstructured-IO/unstructured) | High, 15.1k★ | Broader format coverage (DOCX/HTML/etc.); weaker on complex tables than Docling in recent benchmarks [Procycons, 2025](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) |
| **Evals / observability** | **Langfuse** | Open-core (OSS self-host available) | High | Production tracing (inputs/outputs/latency/cost) + LLM-as-judge scoring on live traffic — the piece most teams skip and the AI judge will look for |
| | **RAGAS** | Apache-2.0 | High | Academic-grade RAG-specific metrics (faithfulness, relevancy) |
| | **DeepEval** | Apache-2.0 | High | Python/CI-native eval suite, broad metric library, pytest-style integration |
| | **promptfoo** | MIT | High | Prompt regression testing + red-teaming; the right tool for a PR-time CI gate [helpmetest.com, 2026](https://helpmetest.com/blog/llm-evaluation-frameworks/) |

Recommended combo (mirrors what a mature 2026 eval stack looks like): Langfuse traces production runs → a scheduled job samples traffic and runs RAGAS/DeepEval → scores post back to Langfuse → promptfoo gates CI. This is directly reusable for I9 (Agentic Analytics Eval Harness) and should be the evals backbone for every other idea's "technical depth" story.

---

## 4. Reference architectures worth copying

1. **Anthropic Financial Services templates (skills + connectors + subagents)** — the cleanest publicly documented pattern for "agent that touches real financial workflows." Skills = domain instructions/prompts; connectors = governed data access (FactSet, Moody's, S&P CapIQ, etc.); subagents = smaller Claude calls for narrow sub-tasks (e.g., "check comparables," "verify methodology"). This maps almost one-to-one onto how a Zenon Genesis entry should be structured, with Zenon's proprietary rules/curves/taxonomies replacing the generic connectors [Anthropic, May 2026](https://www.anthropic.com/news/finance-agents); [anthropics/financial-services](https://github.com/anthropics/financial-services).
2. **Amazon Bedrock AgentCore** — the AWS-native production target: a managed harness (`CreateHarness`/`InvokeHarness`) that hands you memory, identity, a tool gateway, and CloudWatch-backed observability (session count, latency, token usage, error rate) without building that scaffolding yourself [AWS ML Blog, 2026](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-harness-is-now-generally-available-go-from-idea-to-production-grade-agent-in-minutes/); [AWS docs, 2026](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html). Given Bedrock Agents Classic sunsets for new customers 30 Jul 2026, any "we deploy on Bedrock" claim in a Genesis pitch should target AgentCore explicitly.
3. **AWS Strands + AgentCore sample** ([aws-samples/sample-strands-agent-with-agentcore](https://github.com/aws-samples/sample-strands-agent-with-agentcore)) — a ready-made reference wiring an OSS agent SDK into the managed AWS harness; a credible starting scaffold to point at in a feasibility slide.
4. **Coordinator + specialist-agent pattern** shows up consistently across FinRobot, Anthropic's templates, and AWS's own financial-services multi-agent examples (a Coordinator/Lead Agent routing to Market Analyst / Risk / Compliance specialist subagents). This is close to a de facto standard shape for a credible "real agentic design" story and should be the default architecture diagram for any Zenon Genesis entry.

---

## 5. Where OSS stops = where Zenon's edge lives

None of the above gives you:

- **Roll-rate, DQ-bucket, vintage-curve, or renewal/save/stick-curve definitions.** GE/Soda/datacompy tell you *that* two numbers disagree; they have zero opinion on what a "cured" vs "charged-off" transition means, or what a healthy stick-curve shape looks like for a subscription cohort. This is pure Barclays/Dow Jones institutional knowledge.
- **GAAP-vs-management reconciliation semantics.** No OSS tool knows a client's chart-of-accounts mapping or which management adjustments are "normal" vs a red flag — that logic has to be encoded by Zenon, per client.
- **Regulatory narrative logic** (Reg B adverse-action reason codes, SAR narrative conventions, CECL/IFRS9 impairment coverage rules). SHAP gives you feature attributions; turning those into an examiner-ready, compliant adverse-action letter or SAR narrative is a rules+ML+compliance-copy layer nobody ships open source, because it's jurisdiction- and institution-specific.
- **Domain-aware synthetic data constraints.** SDV generates statistically plausible tables; it has no built-in notion of "this loan tape must respect a realistic roll-rate/vintage curve" or "these two synthetic account balances must reconcile." Encoding those constraints on top of SDV is exactly Zenon's structural edge (I8).
- **Financial-statement-aware extraction schemas.** Docling/Unstructured extract tables and layout; they don't know what a covenant test, a footnote tie-out, or a NAV waterfall is. That mapping from "extracted table" to "audited, checked-against-policy number" is custom.
- **Domain-correctness evals.** RAGAS/DeepEval measure whether an LLM's output is faithful/relevant/well-formed — they have no notion of whether a forecast variance or a roll-rate is *financially sane*. A credible eval harness for finance needs domain ground-truth test sets (I9), which is itself a Zenon-buildable asset, not an OSS download.
- **The competitive ceiling to design around:** Anthropic's own templates already do generic GL reconciliation, month-end close, and KYC screening. A Zenon idea that stops at "wire an agent to a connector" is replaceable by a $0 vendor template. The winning pitch needs the domain layer above sitting *on top of* (or instead of) the generic template.

---

## Candidate ideas

**WS2-A**
**Name**: Recon-as-Code Agent (GL/NAV)
**One-liner**: An agent that runs datacompy/Soda-style reconciliation checks across GL/NAV feeds, then investigates and narrates *why* each break happened instead of just flagging it.
**Track**: A
**Zenon anchor**: Barclays (DQ/reconciliation discipline), Visa (cross-client reconciliation work)
**Target user/client**: Bank controller / month-end close ops lead at a regional bank or asset servicer
**The pain**: Analysts spend days each month chasing GL-to-subledger or NAV breaks manually in Excel
**Why it's agentic**: Multi-step loop — comparator agent flags breaks (datacompy/Soda), investigator agent forms and tests root-cause hypotheses (timing, FX, late postings), narrator agent writes the exception memo; not a single prompt call
**Synthetic-data viability**: High — synthetic GL/subledger pairs with injected break types are easy to construct and control
**6-wk feasibility**: High — datacompy + Great Expectations/Soda Core do most of the comparison plumbing; LangGraph for the investigate/narrate loop
**Market/competition**: Anthropic's own "General ledger reconciler" template ships this generically [Anthropic, May 2026](https://www.anthropic.com/news/finance-agents); AWS has published a similar reconciliation-automation case study
**White-space/originality**: Thin at the generic level — differentiation must come from bank-specific chart-of-accounts logic and NAV/roll-rate semantics baked in, not the reconciliation mechanic itself
**6-wk feasibility rationale covered above.**
**Rubric quick-score**: ZI 5, TD 4, FR 5, OR 2, PR 4 → weighted = 5(.25)+4(.25)+5(.25)+2(.15)+4(.10) = **4.20**
**Tags**: `[Align with Zenon]` `[Recommended]`
**Sources**: [Anthropic, May 2026](https://www.anthropic.com/news/finance-agents); [Capital One datacompy, 2026](https://www.capitalone.com/tech/open-source/datacompy-open-source-dataframe-comparisons/); [PipeCode, 2026](https://pipecode.ai/blogs/data-quality-frameworks-great-expectations-vs-dbt-tests-vs-soda-core)

---

**WS2-B**
**Name**: AML/KYC Onboarding Copilot
**One-liner**: An onboarding agent that assembles entity files, runs sanctions/adverse-media screening, and packages a risk-scored escalation for a human reviewer, built on Ballerine + watchman.
**Track**: A
**Zenon anchor**: Named division in scope (AML/Fraud); structural edge = rules+ML hybrid, validation discipline (human-in-loop)
**Target user/client**: Compliance ops lead at a mid-size regional bank or fintech
**The pain**: Manual KYC case assembly (entity resolution, sanctions checks, adverse media, risk memo) takes hours per case and scales linearly with headcount
**Why it's agentic**: Orchestrates entity-resolution, sanctions-screening, adverse-media-search, and risk-scoring subagents with a mandatory human-in-the-loop escalation gate
**Synthetic-data viability**: High — synthetic entities against a mock/synthetic watchlist
**6-wk feasibility**: Good — Ballerine (workflow/case-mgmt) + moov-io/watchman (OFAC/sanctions, MCP-ready) remove most of the plumbing
**Market/competition**: Anthropic's KYC screener template; OSS plugin vyayasan/kyc-analyst already does something very similar on Claude
**White-space/originality**: Low-moderate — this is a crowded lane; differentiate via bank-specific risk taxonomy and audit-trail packaging, not the screening mechanic
**Rubric quick-score**: ZI 4, TD 4, FR 4, OR 2, PR 4 → 4(.25)+4(.25)+4(.25)+2(.15)+4(.10) = **3.70**
**Tags**: `[Align with Zenon]`
**Sources**: [ballerine-io/ballerine](https://github.com/ballerine-io/ballerine); [moov-io/watchman](https://github.com/moov-io/watchman); [vyayasan/kyc-analyst](https://github.com/vyayasan/kyc-analyst); [Anthropic, May 2026](https://www.anthropic.com/news/finance-agents)

---

**WS2-C**
**Name**: Sanctions Alert Triage & False-Positive Reduction Agent
**One-liner**: An agent that enriches and disposes existing sanctions/watchlist alerts (from an incumbent screening tool) with an explainable recommendation, cutting analyst review time on the ~90%+ false-positive backlog.
**Track**: A
**Zenon anchor**: AML division in scope; rules+ML hybrid explainability
**Target user/client**: AML alert-review team lead at a bank already running a screening platform (Actimize/Fircosoft-style)
**The pain**: Alert backlogs are dominated by false positives; analysts burn hours per alert on manual disposition
**Why it's agentic**: Multi-step investigation — entity resolution against watchman/OFAC data, adverse-media cross-reference, explainable disposition recommendation with full audit trail — not a single classifier call
**Synthetic-data viability**: High — synthetic alert queues with known ground-truth dispositions
**6-wk feasibility**: Good — moov-io/watchman gives the matching infra; reasoning/audit layer is the custom build
**Market/competition**: Less crowded than generic KYC onboarding; incumbents (NICE Actimize, Fircosoft) sell the screening engine, not the triage layer
**White-space/originality**: Moderate — alert-triage economics (backlog size, cost-per-alert) is a sharper, less-commoditized wedge than onboarding
**Rubric quick-score**: ZI 5, TD 4, FR 4, OR 3, PR 4 → 5(.25)+4(.25)+4(.25)+3(.15)+4(.10) = **4.10**
**Tags**: `[Align with Zenon]` `[Recommended]`
**Sources**: [moov-io/watchman](https://github.com/moov-io/watchman)

---

**WS2-D**
**Name**: Credit/Collections Text-to-SQL Analyst (Vanna-fork)
**One-liner**: A hardened, typed fork of the now-archived Vanna text-to-SQL project, purpose-built with a credit/collections semantic layer (roll rates, DQ buckets) and PydanticAI-validated outputs.
**Track**: A
**Zenon anchor**: Credit-risk/collections (Barclays)
**Target user/client**: Credit/collections portfolio analyst who needs ad hoc self-serve queries without waiting on a data team
**The pain**: Every ad hoc portfolio question becomes a data-team ticket
**Why it's agentic**: Schema-retrieval → SQL generation → execution → self-correction retry loop → narrative summary
**Synthetic-data viability**: High — synthetic loan-level/collections schema
**6-wk feasibility**: Moderate — Vanna's OSS repo is archived (frozen but usable), so the team inherits some bit-rot/dependency risk rather than a maintained library
**Market/competition**: Crowded NL-to-SQL space (Vanna itself, plus many closed competitors); this idea overlaps heavily with I4 (Insight Narrator)
**White-space/originality**: Low as a standalone idea — the genuine new angle is *only* the timing opportunity created by Vanna's archival, not the underlying pattern
**Rubric quick-score**: ZI 4, TD 3, FR 4, OR 2, PR 4 → 4(.25)+3(.25)+4(.25)+2(.15)+4(.10) = **3.45**
**Tags**: `[Align with Zenon]`
**Sources**: [towardsai.net, 2026](https://pub.towardsai.net/i-turned-an-archived-23k-star-text-to-sql-project-into-a-self-hosted-tool-that-actually-works-out-b08abcb6d0e3); [vanna-ai/vanna](https://github.com/vanna-ai/vanna)

---

**WS2-E**
**Name**: Payments Exception & Break Investigation Agent
**One-liner**: A root-cause investigator agent for payment-rail exceptions (ACH/wire/card) that chains reconciliation-check hits into evidence-backed hypotheses instead of a raw break list.
**Track**: A
**Zenon anchor**: Visa (payments, reconciliation, DQ)
**Target user/client**: Payments operations lead at a card network, processor, or bank payments team
**The pain**: Break/exception investigation across payment rails is manual, rail-specific, and slow, with high analyst hours per case
**Why it's agentic**: Hypothesis-generation-and-evidence-gathering loop (timing windows, rail-specific rules, datacompy-style diffs) across multiple rails, not a single-shot diff
**Synthetic-data viability**: High — synthetic ledger/rail-feed pairs with injected break types per rail
**6-wk feasibility**: High — datacompy + Soda Core give the detection layer; LangGraph for the investigation chain
**Market/competition**: Reconciliation-agent space is filling in (see WS2-A); payments-rail specificity is a real niche vs. generic GL recon
**White-space/originality**: Moderate — the Visa-specific rail semantics differentiate this from generic reconciliation agents
**Rubric quick-score**: ZI 5, TD 4, FR 5, OR 3, PR 4 → 5(.25)+4(.25)+5(.25)+3(.15)+4(.10) = **4.35**
**Tags**: `[Align with Zenon]` `[Recommended]`
**Sources**: [Capital One datacompy, 2026](https://www.capitalone.com/tech/open-source/datacompy-open-source-dataframe-comparisons/); [PipeCode, 2026](https://pipecode.ai/blogs/data-quality-frameworks-great-expectations-vs-dbt-tests-vs-soda-core)

---

**WS2-F**
**Name**: Loan Covenant & Statement Compliance Auditor
**One-liner**: An agent that extracts figures from borrower financial statements (Docling), computes covenant ratios, and flags breaches against a policy-defined threshold set, with an audit trail.
**Track**: A
**Zenon anchor**: Credit-risk (Barclays); DQ/reconciliation discipline
**Target user/client**: Commercial-lending covenant-monitoring / credit risk officer
**The pain**: Quarterly covenant testing across a loan book is manual spreadsheet work prone to missed breaches
**Why it's agentic**: Extractor → calculator → auditor (compares to covenant policy) → exception-narrator chain of subagents
**Synthetic-data viability**: High — synthetic borrower financial statements with engineered covenant breaches
**6-wk feasibility**: Good — Docling handles extraction; covenant-threshold logic and ratio calculus are the custom (but bounded) build
**Market/competition**: Anthropic's "Statement auditor" template is adjacent and reduces originality; several fintech covenant-monitoring SaaS products exist (e.g., loan-monitoring platforms) as funded incumbents
**White-space/originality**: Moderate-low given Anthropic's adjacent template and existing SaaS players; needs Zenon's own covenant-rule library to differentiate
**Rubric quick-score**: ZI 4, TD 4, FR 4, OR 2, PR 4 → 4(.25)+4(.25)+4(.25)+2(.15)+4(.10) = **3.70**
**Tags**: `[Align with Zenon]` `[Recommended]`
**Sources**: [Docling GitHub](https://github.com/docling-project/docling); [Anthropic, May 2026](https://www.anthropic.com/news/finance-agents)

---

**WS2-G**
**Name**: Adverse-Action & Credit-Decision Narrative Agent
**One-liner**: Turns SHAP feature attributions from an existing credit model into compliant, reason-coded adverse-action notices (and favorable-decision memos), with a human compliance review gate.
**Track**: A
**Zenon anchor**: Credit-risk (Barclays); rules+ML hybrid explainability — a direct match to Zenon's structural edge
**Target user/client**: Retail-lending underwriting/compliance officer at a consumer bank or lender
**The pain**: Drafting individually compliant adverse-action notices (Reg-B-style reason codes) from model outputs is slow, manual, and a recurring compliance-risk chokepoint
**Why it's agentic**: Model-explain (SHAP) → reason-code mapping → compliant-template drafting → policy-compliance check chain, with mandatory human sign-off
**Synthetic-data viability**: High — synthetic loan applications + a synthetic credit model to explain
**6-wk feasibility**: Good — SHAP is mature and trivial to integrate; the reason-code mapping and regulatory templates are the custom domain layer, scoped to a handful of reason codes for a demo
**Market/competition**: Genuinely underserved — this specific narrative-generation-from-explainability niche is not in Anthropic's template set and not a commodity SaaS category yet
**White-space/originality**: High — directly exploits a documented OSS gap ("where OSS stops," Section 5) rather than competing with a generic template
**Rubric quick-score**: ZI 4, TD 4, FR 4, OR 4, PR 4 → 4(.25)+4(.25)+4(.25)+4(.15)+4(.10) = **4.00**
**Tags**: `[Align with Zenon]` `[Recommended]`
**Sources**: [SHAP GitHub](https://github.com/shap/shap)

---

**WS2-H**
**Name**: Forecast Variance Sentinel (independent forecast auditor)
**One-liner**: A "second opinion" agent that runs a statistical baseline (Nixtla) alongside an existing FP&A forecast (Anaplan/Hyperion/Excel) and narrates *why* the two diverge — a non-intrusive audit layer, not a replacement tool.
**Track**: A
**Zenon anchor**: Dow Jones (FAST forecast tool, renewal/save/stick curves) — direct anchor
**Target user/client**: FP&A / subscription-finance lead who already has a forecasting tool but no independent check on it
**The pain**: Forecast errors and mix-shift surprises reach the board deck before anyone catches them; nobody independently audits the forecasting tool's outputs
**Why it's agentic**: Runs an automated statistical baseline, computes variance against the human/tool forecast, investigates root cause (seasonality, mix shift, one-offs) and narrates it — a genuine investigate-and-explain loop, not a chart
**Synthetic-data viability**: High — synthetic subscription revenue series with engineered forecast errors
**6-wk feasibility**: High — Nixtla statsforecast/mlforecast stand up fast; the harder, still-feasible-in-6-weeks part is the variance-driver taxonomy
**Market/competition**: Lower-friction buying motion than a full forecasting copilot (doesn't require ripping out Anaplan) — differentiates from typical "replace your FP&A tool" pitches
**White-space/originality**: Good — the "auditor, not replacement" framing is a genuine differentiator versus most forecasting-copilot pitches, including I1 itself
**Rubric quick-score**: ZI 4, TD 4, FR 5, OR 4, PR 4 → 4(.25)+4(.25)+5(.25)+4(.15)+4(.10) = **4.25**
**Tags**: `[Align with Zenon]` `[Recommended]`
**Sources**: [Nixtla statsforecast GitHub](https://github.com/Nixtla/statsforecast); [Nixtla nixtla/TimeGPT license](https://github.com/Nixtla/nixtla/blob/main/LICENSE)

---

**WS2-I**
**Name**: Regulatory-Grade Synthetic Loan Tape / Deposit Book Generator
**One-liner**: An SDV-based synthetic-data agent that generates loan-level/deposit-level synthetic books constrained to respect real roll-rate/vintage-curve shapes, for model validation and stress-testing teams — filling the gap Gretel's archival just opened.
**Track**: A
**Zenon anchor**: Structural edge (synthetic data + validation discipline); credit-risk (Barclays curve library)
**Target user/client**: Model-validation / stress-testing team at a bank needing PII-free, statistically faithful test data
**The pain**: Model validation and CCAR/DFAST-style stress testing need realistic loan tapes without exposing real customer PII, and data-sharing approvals slow every validation cycle
**Why it's agentic**: Generate (SDV) → validate against curve/statistical constraints → refine loop, iterating until fidelity tests pass, rather than a single static generation call
**Synthetic-data viability**: N/A (this is the synthetic-data product itself) — demoable by construction
**6-wk feasibility**: Good — SDV is mature and well-documented; curve-constraint post-processing is the bounded custom layer
**Market/competition**: Gretel (the strongest commercial-grade open alternative) is gone — NVIDIA archived it in Feb 2026 — leaving a real gap; MOSTLY AI and similar remain closed/commercial
**White-space/originality**: Heavily overlaps I8 (Synthetic Data Studio) — treat as a sharpened, regulatory-stress-testing-specific variant of I8 rather than a standalone entry
**Rubric quick-score**: ZI 4, TD 4, FR 4, OR 2, PR 3 → 4(.25)+4(.25)+4(.25)+2(.15)+3(.10) = **3.60**
**Tags**: `[Align with Zenon]` `[Recommended]`
**Sources**: [DataCebo/SDV](https://datacebo.com/sdv-dev/); [TechCrunch, Mar 2025](https://techcrunch.com/2025/03/19/nvidia-reportedly-acquires-synthetic-data-startup-gretel/); [SynthForge, May 2026](https://synthforge.io/alternatives/gretel/)

---

**WS2-J**
**Name**: Document-to-Ledger Tie-Out Agent
**One-liner**: An agent that extracts figures from invoices/statements (Docling) and fuzzy-matches/ties them out against the general ledger (datacompy-style), flagging and investigating exceptions.
**Track**: A
**Zenon anchor**: DQ/reconciliation discipline (Visa, Barclays)
**Target user/client**: Back-office/AP ops lead doing month-end vendor/statement reconciliation
**The pain**: Manual invoice-to-ledger matching during month-end close consumes significant back-office hours
**Why it's agentic**: Extraction → matching/tie-out → exception investigation → narration subagent chain
**Synthetic-data viability**: High — synthetic invoices/statements plus a synthetic ledger with engineered mismatches
**6-wk feasibility**: Good — Docling + datacompy remove most of the plumbing
**Market/competition**: Invoice-matching agents are a very common enterprise-agent demo pattern; low novelty
**White-space/originality**: Low — this is essentially a specific vertical flavor of WS2-A/WS2-E; recommend the synthesis team treat A/E/J as three verticals of one "OSS-enabled reconciliation agent" family rather than three separate pitches
**Rubric quick-score**: ZI 4, TD 4, FR 4, OR 2, PR 3 → 4(.25)+4(.25)+4(.25)+2(.15)+3(.10) = **3.60**
**Tags**: `[Align with Zenon]`
**Sources**: [Docling GitHub](https://github.com/docling-project/docling); [Capital One datacompy](https://www.capitalone.com/tech/open-source/datacompy-open-source-dataframe-comparisons/)

---

## Notes for synthesis

- **Suspected overlaps with I1–I10**: WS2-A/E/J are all variants of I3 (Data-Trust Agent) sharpened by concrete OSS tooling (datacompy/Soda) and vertical (GL/NAV, payments rails, AP/vendor) — recommend consolidating into one I3-family idea with a chosen vertical rather than pitching all three. WS2-D is essentially I4 (Insight Narrator) with a "Vanna just got archived" timing hook — keep the hook, drop the idea if I4 is already the team's pick. WS2-H is conceptually adjacent to I1 (Forecast Copilot) but pitches a different buying motion (independent auditor vs. replacement copilot) — worth keeping as a distinct "beachhead" variant rather than merging. WS2-I overlaps I8 (Synthetic Data Studio) directly — treat as a sharpened sub-scope (regulatory stress-testing loan tapes), not a new idea. WS2-B/C overlap each other (KYC onboarding vs. alert triage) more than they overlap I1–I10; C is the sharper wedge of the two.
- **Track B/C note (logged, not a target)**: Independent of any single idea, Zenon could stand up an internal "Genesis starter kit" — a small template repo wiring LangGraph + Great Expectations + datacompy + Langfuse + a synthetic-data harness — as a reusable scaffold for *all* Genesis teams. This is an internal-ops (Track B/C-ish) meta-recommendation, not a competition entry.
- **Highest-stakes finding #1**: Anthropic shipped 10 finance agent templates in May 2026 (GL reconciler, month-end closer, statement auditor, KYC screener, etc.) built on a skills/connectors/subagents pattern. This changes the bar for every reconciliation/KYC/statement-audit idea in this sweep and in I1–I10: "wire an agent to a data connector" is now a commodity a client could get for free from Anthropic directly. Every Zenon pitch in this space needs a visibly proprietary domain layer (curve libraries, bank-specific taxonomies, regulatory narrative logic) foregrounded in the pitch, not buried as an implementation detail.
- **Highest-stakes finding #2**: Two OSS incumbents the team might have assumed were safe defaults are gone or frozen — **Vanna** (text-to-SQL leader, archived Mar 2026) and **Gretel** (leading synthetic-data platform, archived Feb 2026 post-NVIDIA acquisition). Both findings cut the same way: they raise the credibility of Zenon *building and owning* the equivalent proprietary capability (synthetic data especially — I8) rather than assuming a maintained OSS project will always be there to lean on. Also: **Bedrock Agents "Classic" stops accepting new customers 30 Jul 2026** — any AWS/Bedrock architecture claim in a pitch deck should reference **AgentCore**, not Classic, to avoid an easy technical-depth deduction from the AI judge.
