# The Agentic AI Technology Landscape (as of 2026-07-14)

Research brief for Zenon's "Genesis" GenAI competition, Track A (Client-Facing Solutions). Prepared 2026-07-14. Every non-obvious claim carries an inline source + date; primary/vendor sources preferred over listicles. Sources numbered in the final section. Older/background context marked `[background]`.

> **Search availability:** WebSearch and WebFetch were both available and used extensively (~20 searches + primary-source fetches). Two topic clusters (enterprise agent platforms; evals & observability) were researched by dedicated sub-agents whose findings are folded into §6 and §5 respectively.

---

## Executive summary (≤10 bullets)

1. **The frontier is a 3-way near-tie at the top, decided on price and autonomy, not raw IQ.** Anthropic Claude Opus 4.8 ($5/$25 per MTok), OpenAI GPT-5.5 "Spud" ($5/$30, released 2026-04-23), and Google Gemini 3.1 Pro ($2/$12) are separated by single benchmark points; Anthropic's **Claude Fable 5** (`claude-fable-5`, GA 2026-06-09, $10/$50) is the most capable *widely released* model, built for long-horizon agents. [1][7][8][15]
2. **Agentic autonomy is now measurable and rising fast.** METR's task-completion "time horizon" (the human-task-length a model finishes at 50% reliability) reached **~5.3 hours** (Claude Opus 4.5, per METR TH1.1, 2026-01-29); the long-run doubling is ~7 months but has **accelerated to ~89 days (P50) since 2024** — the single best framing for "how much can you trust an agent to run unattended." *(Note: SEO sources circulate an inflated "~14.5 hr" figure; the primary METR number is ~5.3 hr — see §5.)* [E44][E45]
3. **MCP is the settled interoperability standard.** Anthropic transferred it to the **Agentic AI Foundation (Linux Foundation)** in Dec 2025 (OpenAI, Block co-founders; AWS/Google/Microsoft supporting); ~97M monthly SDK downloads, ~2,000–10,000+ servers, spec `2025-11-25` adding async tasks + enterprise OAuth. Building on MCP is table stakes, not a differentiator. [4][17]
4. **The serious production stacks are LangGraph, the Claude Agent SDK, and the OpenAI Agents SDK/AgentKit.** LangGraph has the most enterprise mileage (Klarna, Uber, LinkedIn, JPMorgan, BlackRock); the Claude Agent SDK is the batteries-included, MCP-native harness; OpenAI's AgentKit adds a visual builder + hosted evals. CrewAI/smolagents/Pydantic AI serve prototyping and niches. [3][19][20]
5. **What reads as "cutting-edge" in July 2026 is verifiable multi-step autonomy with an eval harness — not a chatbot.** A plain RAG chatbot or single-prompt wrapper reads as 2024-era slop; the bar is planner→executor→verifier loops, self-correction, LLM-as-judge evals calibrated to humans, and cost/latency/accuracy evidence. [11][10]
6. **"Evidence of readiness" now means an eval harness, not a demo.** The AI-judge-relevant differentiator is: offline eval sets on synthetic data, LLM-as-judge with human calibration, regression/CI gating, trace inspection (OpenTelemetry GenAI conventions), and an accuracy↔cost↔latency dashboard. The compounding-error math is the killer argument: a 4-step agent at 90%/step is only ~66% end-to-end. Agent benchmarks (tau2-bench for policy adherence, GAIA/GAIA2, SWE-bench Pro, OSWorld, METR time-horizons) set the vocabulary — **cite primary sources with the exact split; many SEO "leaderboards" fabricate scores.** [E54][E55]
7. **Clients will compare a custom build against Salesforce Agentforce, Microsoft Copilot Studio, Google Gemini Enterprise, ServiceNow AI Agents, and AWS Bedrock AgentCore.** Since Genesis delivers on AWS, **AgentCore** (Runtime/Gateway/Memory/Identity/Observability) is the most relevant reference point and a legitimate substrate. *(See §6 for the deep-dive from the platforms sub-agent.)*
8. **Security is the enterprise gate and it is unsolved.** Prompt injection is the #1 OWASP LLM risk in 2026 and treated as unsolved; 88% of orgs reported an agent security incident in the past year. Winning demos show structural defenses: least-privilege tool scoping, human-in-the-loop on destructive actions, sandboxing, agent identity/auth, and tamper-evident audit trails. [12][13]
9. **Open-weights are now genuinely competitive for agents** (DeepSeek V4, Kimi K2.6, Qwen 3.x, GLM) at 1–10% of frontier cost — relevant for cost engineering and a "route cheap sub-tasks to open models" story, but for a 6-7 week client-ready build on AWS, hosted Anthropic/OpenAI APIs are the safer default. [16]
10. **Recommended stack for Track A:** build the orchestration in **LangGraph** (control, durability, audit trails, provider-agnostic) on **AWS**, default the reasoning model to **Claude (Opus 4.8 / Sonnet 5)** via Bedrock or the Claude API, wire tools over **MCP**, and instrument with an **eval harness (LangSmith or Braintrust) + OpenTelemetry GenAI traces**. This maximizes the 25% technical-depth and 25% feasibility scores. *(Rationale in §9.)*

---

## 1. Frontier models for agentic work

The top tier is a near-tie; teams choose by **price, autonomy/tool-calling efficiency, and context window**, not a single benchmark number. [1][7]

### Anthropic Claude (authoritative — verified against platform.claude.com models overview [17b])

| Model | ID | Context | Max output | Price (in/out per MTok) | Notes |
|---|---|---|---|---|---|
| **Claude Fable 5** | `claude-fable-5` | 1M | 128K | **$10 / $50** | Most capable *widely released* model; "next-gen intelligence for long-running agents"; GA 2026-06-09. Thinking always-on; raw CoT never returned. [15][17b] |
| **Claude Opus 4.8** | `claude-opus-4-8` | 1M | 128K | **$5 / $25** | Default for complex agentic coding & enterprise; the recommended everyday agent brain. Announced 2026-05-28. [1][17b] |
| **Claude Sonnet 5** | `claude-sonnet-5` | 1M | 128K | **$3 / $15** (intro **$2/$10** thru 2026-08-31) | "Near-Opus at Sonnet cost," launched 2026-06-30 as a cheaper way to run agents. [7][17b] |
| **Claude Haiku 4.5** | `claude-haiku-4-5` | 200K | 64K | **$1 / $5** | Fastest; near-frontier; good for sub-agents/routing. [17b] |

Agentic-coding benchmark ladder (vendor/MarkTechPost, 2026-06-30): Opus 4.8 **69.2%**, Sonnet 5 **63.2%**, Sonnet 4.6 **58.1%**. Opus 4.8 was the only model to complete every Super-Agent case end-to-end at GPT-5.5 cost parity. [1] Claude leads the hardest coding test (SWE-bench Verified) and human-preference rankings. [7] Anthropic models hold the top OSWorld computer-use spots (Opus 4.7 at 82.3%). [21]

### OpenAI GPT-5.x

- **GPT-5.5 ("Spud")**, released **2026-04-23**, API the next day, default in ChatGPT 2026-05-05. Natively omnimodal. **1M context** (up from 272K). API **$5 / $30**; `gpt-5.5-pro` **$30 / $180**. [8][7]
- Benchmarks: **82.7% Terminal-Bench 2.0**, **84.9% GDPval**, **58.6% SWE-bench Pro**, ~88.7% MMLU, 60% fewer hallucinations vs GPT-5.4. Anthropic edges it on SWE-bench Pro (Opus 4.7 64.3% vs 58.6%). GPT-5.x is widely cited as the leader in **computer use**. [8][7][1]

### Google Gemini 3.x

- **Gemini 3.1 Pro** (preview 2026-02-19): frontier reasoning, **1M-token** context, **$2 / $12** — the value champion with the widest free tier. Leads scientific reasoning (GPQA Diamond 94.3%) and ARC-AGI-2 (77.1%). Available via Vertex AI, AI Studio, and **Google Antigravity** (Google's agentic dev platform). [7][15b]
- **Gemini 3.5 Pro** (reported mid-2026): **2M-token** context (largest in production) + **Deep Think** mode; enterprise-preview pricing ~$12–15 / $36–45. [15b]

### Notable open-weights (competitive for agents in 2026) [16]

- **DeepSeek V4 / V4-Pro** — top open scores (SWE-bench Verified 80.6%, GPQA 90.1%), MIT license, 1M context; best perf-per-inference-dollar for self-hosting.
- **Kimi K2.6** — leads SWE-bench **Pro** among open models (58.6%), built for sub-agent parallelism/harness-driven pipelines.
- **Qwen 3.x (e.g., Qwen3-235B-A22B)** — 1M context, frontier-competitive, cheapest permissive multilingual (~$0.10 output/MTok).
- **GLM-4.6 / GLM-5.x** — unbeatable budget coding value; strong on tool-use/policy-adherence tasks. *(Caution: "GLM-5.2 at 99.1% tau2" circulating on SEO leaderboards is fabricated — the Sierra tau2-bench repo shows frontier at ~60–85% by domain; see §5.)* [16][E36]
- Verdict: open field delivers ~90–95% of frontier capability at 1–10% of cost. The 2026 question is "which open model," not "open or closed." [16]

**Computer use** is now a first-class agent capability across all three frontier vendors (self-hosted or hosted); best practice is a thin harness that **routes by workload** (files/Windows→Claude, macOS/Codex→OpenAI, browser/DOM→Gemini) rather than standardizing on one. Human ceiling on OSWorld is ~72%; agents in the low-80s now exceed it on the verified set. [21]

---

## 2. Agent development stacks

**Mental model (from the Claude API skill / Anthropic docs):** separate *who owns the agent loop* from *who owns deployment*. A manual tool-loop and the Anthropic API "tool runner" leave both to you; the **Claude Agent SDK** supplies a batteries-included harness but you host it; **Anthropic Managed Agents (CMA)** supplies the harness *and* a hosted per-session sandbox. [17b]

### What serious teams use in production (2026)

| Stack | What it is | Adoption / maturity | Best for |
|---|---|---|---|
| **LangGraph** (LangChain) | Low-level, graph-based durable-execution runtime; you own the loop, state, and every edge; provider-agnostic; MIT-licensed | Most production mileage: Klarna (85M users), Uber, LinkedIn, BlackRock, Cisco, JPMorgan, Replit; ~47% lower token cost vs CrewAI via explicit edges [3][19] | Complex/branching workflows needing audit trails, rollback, HITL; the **safest default for a new production build** [3][19] |
| **Claude Agent SDK** (Anthropic) | Claude Code packaged as a library; opinionated harness (Anthropic owns the loop, you steer); built-in file/bash/web tools, subagents, sessions, deepest MCP integration (200+ servers, 1-line config), 3 guardrail types run in parallel | Search interest ~500× YoY by Apr 2026; renamed from "Claude Code SDK" Sept 2025; Anthropic uses it internally (GitHub triage, Slack). June 2026 added Dynamic Workflows (fan out 10s–100s of subagents) + Performance Outcomes (grader-driven revise loops) [3][20][25] | Fast path to a capable coding/filesystem/ops agent when you're Claude-centric |
| **OpenAI Agents SDK + AgentKit** | Agents SDK (evolved from Swarm) + AgentKit bundle: **Agent Builder** (visual canvas), **ChatKit** (embeddable UI), **Connector Registry** (govern data sources/MCP), and **Evals**. AgentKit released 2025-10-06; Apr 2026 SDK update added native **sandbox execution** + harness-level tracing (tool approvals, resume, handoffs) [18][19] | Production-ready mid-2026; strong for OpenAI-centric teams wanting a visual builder + governed connectors | Rapid enterprise agents with embedded chat UI + governance |
| **Google ADK** | Agent Development Kit, ships with Gemini Enterprise/Agentspace | On the "safe 2026 shortlist" [3] | Google-Cloud-centric builds |
| **Microsoft Agent Framework** | Merger of Semantic Kernel + AutoGen | On the shortlist; *(see §6)* | Azure/.NET shops |
| **CrewAI** | Role-based multi-agent, low boilerplate | ~31k stars; fastest multi-agent prototypes; ~54% success on 8+-step tasks vs LangGraph 62% [19] | Quick multi-agent prototypes |
| **AutoGen / AG2** | Conversational multi-agent (research heritage) | ~42k stars [19] | Research, experimentation |
| **Pydantic AI** | Type-safe, minimal, Python-native | "Stability" pick [19] | Structured, typed single-agent apps |
| **smolagents** (HuggingFace) | Minimal code-first single-agent | ~14.8k stars in 15 months [19] | Lightweight/local single-agent loops, research |

The 2026 "safe production shortlist": **LangGraph, Claude Agent SDK, OpenAI Agents SDK, Google ADK, Microsoft Agent Framework.** [3] LangGraph = most control/boilerplate; Claude Agent SDK & Google ADK = simplicity over fine-grained orchestration; OpenAI splits the difference via handoffs. [3]

---

## 3. Protocols

### MCP (Model Context Protocol) — the settled standard [4][17]

- **Governance:** Anthropic transferred MCP to the **Agentic AI Foundation under the Linux Foundation** in **Dec 2025** — vendor-neutral, community-governed. OpenAI and Block are co-founders; AWS, Google, Microsoft, Cloudflare, GitHub, Bloomberg are supporting members. [17]
- **Spec:** latest is **2025-11-25**, adding async **Tasks**, enhanced **OAuth**, server-side agent loops, **elicitation**, and an extensions system (enabling **MCP Apps**, Jan 2026, with sandboxed HTML UI in chat). Auth moved from Dynamic Client Registration to **Client ID Metadata Documents (CIMD)**. [17]
- **Ecosystem:** ~**97M monthly SDK downloads** (Python+TS combined); official Registry launched Sept 2025, cited between ~2,000 and 10,000+ servers depending on source/date. Clients: Claude, ChatGPT, Gemini, Copilot, Cursor, VS Code. Servers: Slack, Salesforce, Stripe, Notion, Linear, Figma, GitHub. [4][17]
- **2026 roadmap:** transport scalability (stateless horizontal scaling), Tasks retry/expiry semantics, enterprise SSO-integrated auth, MCP Server Cards for `.well-known` discovery, audit trails/gateways. [4]
- **Takeaway for Genesis:** MCP is **table stakes**. Use it for tool integration; do not pitch "we support MCP" as innovation — pitch what you *do* with it.

### A2A (Agent-to-Agent) [4][background]

Google released **A2A** in Apr 2025, donated it to the Linux Foundation June 2025; reached **v1.0** with signed Agent Cards, 150+ production orgs, SDKs in 5 languages. MCP handles *agent→tool* (vertical); A2A handles *agent↔agent* discovery/delegation (horizontal) — complementary, not competing. [4]

### Agentic payment protocols (names only — a sibling agent covers this deeply)

Four contenders as of 2026: **x402** (Coinbase/x402 Foundation, stablecoin HTTP-402 payments; most production traction, 165M+ agent txns by May 2026, Stripe on Base Feb 2026), **AP2** (Google authorization framework, 60+ orgs incl. Amex/Mastercard/PayPal), **ACP** (OpenAI+Stripe agentic commerce; launched in ChatGPT Instant Checkout Feb 2026), and **MPP** (Stripe machine payments). AWS **Bedrock AgentCore payments** (built with Coinbase + Stripe) also shipped. Designed as a complementary stack. [26]

---

## 4. Orchestration patterns considered state-of-practice

The 2026 consensus: serious teams build **"cognitive infrastructure" — planners, executors, verifiers, memory, permissions, audit trails** — not "LLM wrappers with tools." [11][9]

- **Planner-Executor (two-phase):** a reasoning-optimized planner emits an ordered plan; a cheaper/faster executor walks it step-by-step. Model-routing (big planner, small executor) is a standard cost lever. [9]
- **Supervisor/Manager-Worker (hierarchical):** a supervisor decomposes and routes sub-tasks to specialized workers, each running its own loop; supervisor aggregates. LangGraph is production-ready for this. [9][3]
- **Judge/Verifier (critic) loops:** a primary agent produces output; a **separate critic/judge** verifies against criteria; output ships only if it passes. The Claude Agent SDK's June-2026 **Performance Outcomes** productizes exactly this (grader sends sub-agents back to revise until a rubric passes). [9][25]
- **Reflection:** the agent critiques and revises its own output before finalizing (ReAct / Plan-and-Execute / Reflection are "the three patterns every engineer needs in 2026"). [9]
- **Debate/Council:** N agents answer independently; a judge picks or they critique each other. Use only when the accuracy gain justifies the token cost. [9]
- **Human-in-the-loop (HITL) checkpoints:** first-class in LangGraph (durable interrupts) and the Claude Agent SDK (approval gates before destructive tools). This is both a UX and a **security** control (§7). [3][20]
- **Memory architectures:** short-term (context window), long-term/**episodic** (files, vector stores, or managed memory stores), and the emerging **shared-memory** pattern as an alternative to message-passing. Anthropic's Managed Agents ship workspace-scoped **memory stores** with versioning/redaction; the Claude memory tool persists a `/memories` dir. [9][17b]
- **Guardrails:** input/output/tool guardrails running *in parallel* with execution (Claude Agent SDK stops mid-generation on failure); structured outputs + strict tool schemas for reliable parsing. [3][17b]

**The 25%-innovation lesson:** complexity must *earn its place*. Multi-agent coordination that measurably beats a single agent + tools wins points; multi-agent for its own sake reads as over-engineering. The strongest signal is a **verifier/self-correction loop with evidence it improves accuracy.**

---

## 5. Evals & observability

*(This section is the verified deliverable from the dedicated evals/observability sub-agent. Sources numbered **E1–E62** below.)*

> **⚠️ Critical source-quality warning (act on this in the competition).** A whole tier of SEO "leaderboard aggregator" sites (BenchLM.ai, Steel.dev leaderboards, pricepertoken.com, coasty.ai, morphllm.com) **systematically fabricate model names and scores** — e.g., "GLM-5.2 at 99.1% tau2," "Claude Mythos 5 at 95.5% SWE-bench," "GPT-5.6 Sol at 92.2% BrowseComp." **None of these are real released models/scores.** Some earlier searches in this brief surfaced such figures; **the numbers in this section supersede them** and are grounded in primary sources (official leaderboards, arXiv, Princeton HAL, METR, Scale, Sierra). For Genesis: cite primary benchmarks with the exact split and self-reported-vs-verified status — vague "we scored X%" claims are exactly what a rigorous AI judge discounts.

### Why this is the highest-leverage section for Genesis

An AI judge scores **engineering quality: evals, reproducibility, accuracy/cost/latency evidence**. The dominant 2026 thesis, stated bluntly by practitioners: **"the eval harness is the deliverable, not the agent."** A single successful demo trace reveals nothing about reliability; build the harness *before* the agent, grounded in real acceptance criteria. [E54]

The single most-cited quantitative argument for why demos lie: **compounding error** — a 4-step agent at 90% per-step reliability achieves only ~66% end-to-end (0.9⁴). Only end-to-end, multi-case evaluation is credible. [E54]

### Eval / observability platforms (2026)

- **LangSmith** (LangChain) — end-to-end agent/LLM observability: step trace inspection, dashboards (tokens, P50/P99 latency, error/cost/feedback), alerting (webhooks/PagerDuty), prompt versioning, dataset curation, offline+online evals, and **full OpenTelemetry ingest**. **Pricing:** Developer free (5k base traces/mo, 14-day retention); **Plus $39/seat/mo** (10k traces incl., $2.50/1k overage); Enterprise custom (SSO/RBAC, self-host). The default when you're already on LangGraph. [E1][E2][E3]
- **Braintrust** — eval-first: tracing + evals (LLM-as-judge, code scorers, human review), datasets from prod traces, prompt mgmt, CI/CD-gated deploys (eval regressions block shipping). **Pricing:** Starter free; **Pro $249/mo** (usage-based, no per-seat); Enterprise custom/on-prem. The reference "eval-first" tool. [E4][E5][E6]
- **Arize Phoenix / Arize AX** — Phoenix is the leading **open-source, self-hostable** observability+eval, built on **OpenInference + OpenTelemetry** (no lock-in): tracing, LLM-as-judge response/retrieval evals, datasets, experiments, prompt playground. Integrates OpenAI/Anthropic/LangGraph/CrewAI/LlamaIndex. **Arize AX** is the managed commercial tier (online evals, alerting, scale). Phoenix free OSS; AX custom. Strong for OTel-native + self-host. [E8][E9][E11]
- **Weights & Biases Weave** — agent-native trace model (sessions/turns/steps/tools/sub-agents), imperative eval API, **Weave Guardrails** (toxicity, bias, PII, hallucination, coherence). Generous free tier; caveat: pricing bundled into W&B Models seats (~$200/seat/mo per community reports — indicative, not official), so pure LLM-app teams may subsidize training features. [E12][E13][E7]
- **Notable others:** **Langfuse** (MIT open-source, top self-hosted pick for data-residency; **acquired by ClickHouse Jan 2026** in a ~$400M Series D round — a consolidation signal); **Comet Opik** (Apache 2.0, tracing + eval + agent-optimizer SDK); **Galileo** ("Luna-2" small evaluator models enable **100%-traffic eval at sub-200ms, ~97% cheaper** than LLM-as-judge); **HoneyHive** (faded from 2026 comparisons); **MLflow** (added GenAI tracing + OTel GenAI semconv); plus APM vendors (Datadog, New Relic, SigNoz) ingesting GenAI traces via OTel. [E14][E15][E16][E18][E62]

### OpenTelemetry GenAI semantic conventions — status

- **Stability:** As of mid-2026 the GenAI (and MCP) semantic conventions are still **Development** status (NOT yet Stable). Semantic Conventions **1.40.0** was current ~2026-04-17; no public stabilization date. Attribute names may still change — pin behavior via `OTEL_SEMCONV_STABILITY_OPT_IN`. [E20][E25]
- **Governance:** OpenTelemetry itself **graduated within CNCF**; GenAI conventions moved to a dedicated repo (`open-telemetry/semantic-conventions-genai`) covering spans/metrics/events for GenAI clients, MCP, and provider-specific conventions — serious active investment despite "Development" label. [E21][E23][E61]
- **What's defined:** LLM client spans (`chat`, `embeddings`); agent lifecycle spans `create_agent` / `invoke_agent`; tool execution `execute_tool`. Key attributes: `gen_ai.request.model`, `gen_ai.usage.input_tokens`/`output_tokens`, `gen_ai.response.finish_reasons`, `gen_ai.agent.name`/`id`, plus content attrs. Client spans most mature; agent spans most in-flux. OTel recommends **not** auto-capturing sensitive prompt/completion payloads. [E22][E24]
- **OpenLLMetry (Traceloop):** Apache-2.0 OTel extensions with instrumentation for LLM providers, vector DBs, and frameworks; emits standard OTLP so traces flow to Datadog/New Relic/Langfuse/SigNoz/etc. Fills gaps OTel core historically left (model version, prompt/completion tokens). [E26][E27]
- **Why it matters:** one vendor-neutral wire format = no lock-in, route GenAI spans into existing APM/SIEM, consistent cost/latency/token attribution across frameworks. Emitting OTel GenAI traces is a strong "built like real infra" signal. [E21]

### Agent benchmarks — current SOTA (primary sources only)

| Benchmark | Measures | Verified 2026 status (state the split!) |
|---|---|---|
| **SWE-bench Verified** | Real GitHub bug-fixes, test-scored | Frontier clusters high-80s–~90%, **but of ~100 leaderboard entries (Jun 2026) only 1 was independently verified** — 99 vendor-submitted. Treat any single "X% Verified" as vendor-reported. [E28][E29] |
| **SWE-bench Pro** (Scale) | Long-horizon SWE, public + private commercial splits | "The" Pro number is **ambiguous** — frontier ~high-50s on public set vs ~high-40s on **private commercial** set; models drop ~14 pts on the private split (the generalization signal). **Always state which split.** [E30][E31] |
| **tau2-bench** (Sierra) | Tool-agent-user, **policy adherence**, pass^k reliability | Frontier ~**60–85% depending on domain** (retail easier, airline harder) per the official repo. **The "GLM-5.2 99.1%" figure is fabricated SEO — do not cite it.** State domain + pass^k. [E36] |
| **GAIA** (Princeton HAL) | Real-world assistant tasks | Best *reproduced*: **HAL Generalist + Claude Sonnet 4.5 = 74.55%** for $178 (Sep 2025); scaffold adds ~30 pts; cost varies ~50× for similar accuracy. [E32] |
| **GAIA2** (Meta+HF, ICLR 2026) | Dynamic async envs, temporal/ambiguity/multi-agent | No model dominates: **GPT-5 (high) ~42% pass@1** (fails time-sensitive tasks); **Kimi-K2 ~21%** leads open. [E33][E35] |
| **OSWorld** | Computer use on real desktop | Top agents **~70s%, approaching human ~72%** (nearing saturation). Exact SEO top figures unreliable. [E37][E38] |
| **WebArena / VisualWebArena** | Multi-step browser tasks | WebArena top ~**60–75%** (from 14.4% GPT-4 baseline, human ~78%); **VisualWebArena much harder ~16–36%** (human ~89%) — visual grounding is the bottleneck. [E39][E40] |
| **Terminal-Bench 2.0** (official) | Terminal/CLI agents | Top cluster ~**78–85%**: NexAU-AHE (GPT-5.5) **84.7%**, WOZCODE (Opus 4.7) 80.2%, TongAgents (Gemini 3.1 Pro) 80.2% — real models. Scaffold matters as much as base model. [E41] |
| **BrowseComp** (OpenAI) | Hard-to-find web research | Frontier clustered near top, nearing saturation; **all self-reported (0 independently verified)**. [E42][E43] |
| **METR Time Horizons (TH1.1, 2026-01-29)** | Human-task length an agent finishes at 50%/80% reliability | **Claude Opus 4.5 ≈ 320 min (~5.3 hr) @50%; GPT-5 ≈ 214 min; o3 ≈ 121 min.** Long-run doubling ~7 months, **accelerated to ~89 days (P50) since 2024.** *(This corrects the "~14.5 hr / doubling every 4.3 mo" figures that appeared in earlier SEO-sourced searches in this brief.)* [E44][E45] |
| **HAL** (Princeton, ICLR 2026) | Framework-agnostic multi-benchmark harness | The reference for *how to eval*: parallel across 100s of VMs, cost-controlled, multidimensional (accuracy + cost + reliability + error freq + robustness) across 9 benchmarks. [E46][E48] |

Newer long-horizon/reliability benchmarks (2026): Vending-Bench (Andon Labs, ~20M-token coherence), LH-Bench, Odysseys, CoffeeBench, SentinelBench, and *"Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents"* — the field is explicitly shifting from single-shot accuracy toward **reliability-under-repetition (pass^k)** and cost-aware, process-level measurement. [E49][E50][E51][E52][E53]

### What "evidence of production readiness" looks like in 2026 (the rigorous eval-harness checklist)

1. **Offline eval / golden sets** — curated, human-labeled ground-truth run against every change; quality over quantity ("50 well-chosen cases beat 500 scraped"). On **synthetic data** for Genesis. [E54]
2. **Regression suite** — every bug/edge case becomes a locked test; eval regressions block deploys (CI-gated). [E54][E57]
3. **LLM-as-judge WITH human calibration** — judge for scale, but calibrate against a **1–2% human-labeled sample** and monitor drift; **use a different model family for judging** than for generation (avoid self-preference inflation); exact-match/code scorers where they work. [E55][E56][E54]
4. **Online eval on sampled production traffic** — continuous proxy scoring (faithfulness, hallucination) with daily rollups + ≥weekly full offline re-runs. Offline + online, not either/or. [E55][E58]
5. **Accuracy + cost + latency + token dashboards with hard gates** — a change that raises accuracy but blows the latency/cost budget is blocked. Concrete 12-metric template (from 100+ deployments): faithfulness >0.95, hallucination <2%, tool-selection accuracy >0.92, tool-execution success >0.98, multi-step coherence >0.85, cost/query <~$0.05, P99 <3s; breaches page. [E55]
6. **Trace inspection** — full step-by-step traces (every LLM/retrieval/tool call as a span with tokens/latency/cost), ideally on standardized **OTel GenAI spans** so evidence is portable. [E6][E21]
7. **Red-teaming / adversarial evaluation** — systematic pre-deploy probing for prompt injection (direct + indirect via retrieved content/docs/images), jailbreaks, tool/parameter abuse, RBAC bypass, data leakage, multi-turn attacks; map every tool + parameter and test adversarial values (promptfoo, OWASP ASI 2026). [E59][E18][E60]
8. **Reproducibility + cost control** — parallelized, pinned datasets/versions, cost-per-run reporting; **pass^k / reliability-under-repetition** over single pass@1. HAL is the reference implementation. [E46][E49]

**What separates real eval evidence from a demo:** teams with a harness ship *defensible deltas* ("pass rate 71%→88%, cost/latency within gates"), reproducible across a labeled set + sampled prod traffic, with judge↔human calibration numbers, a growing regression suite, trace-level cost/latency/token dashboards, and red-team results. Teams with only a demo have one happy-path trace, no per-step-vs-end-to-end accounting, no judge calibration, no cost/latency budget, and no regression proof. **In 2026 the harness *is* the evidence — this is where Genesis technical-depth points are won or lost.** [E54][E55]

### §5 Sources (E1–E62)

E1 [LangSmith Observability](https://www.langchain.com/langsmith/observability) · E2 [LangSmith Pricing](https://www.langchain.com/pricing) · E3 [LangSmith docs](https://docs.langchain.com/langsmith/observability) · E4 [Braintrust](https://www.braintrust.dev/) · E5 [Braintrust Pricing](https://www.braintrust.dev/pricing) · E6 [Braintrust — agent observability guide 2026](https://www.braintrust.dev/articles/agent-observability-complete-guide-2026) · E7 [Braintrust — W&B alternatives 2026](https://www.braintrust.dev/articles/best-weights-and-biases-alternatives-2026) · E8 [Arize Phoenix](https://arize.com/phoenix/) · E9 [Phoenix docs](https://arize.com/docs/phoenix) · E10 [Arize](https://arize.com/) · E11 [Phoenix GitHub](https://github.com/arize-ai/phoenix) · E12 [W&B Weave](https://wandb.ai/site/weave/) · E13 [Weave docs](https://docs.wandb.ai/weave) · E14 [Firecrawl — best LLM observability 2026](https://www.firecrawl.dev/blog/best-llm-observability-tools) · E15 [Comet — AI observability tools 2026](https://www.comet.com/site/blog/ai-observability-tools/) · E16 [FutureAGI — Opik alternatives 2026](https://futureagi.com/blog/comet-opik-alternatives-2026/) · E17 [Langfuse × OpenLLMetry OTel](https://langfuse.com/guides/cookbook/otel_integration_openllmetry) · E18 [Galileo — LLM red teaming](https://galileo.ai/blog/llm-red-teaming-strategies) · E19 [SigNoz — LLM observability compared](https://signoz.io/comparisons/llm-observability-tools/) · E20 [OTel — GenAI semconv status](https://opentelemetry.io/docs/specs/semconv/gen-ai/) · E21 [OTel blog — GenAI observability](https://opentelemetry.io/blog/2026/genai-observability/) · E22 [OTel — GenAI client spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/) · E23 [OTel GenAI semconv repo](https://github.com/open-telemetry/semantic-conventions-genai) · E24 [Greptime — OTel GenAI semconv, May 2026](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions) · E25 [CallSphere — OTel GenAI Apr 2026](https://callsphere.ai/blog/td30-fw-opentelemetry-genai-conventions-april-2026-guide) · E26 [OpenLLMetry GitHub](https://github.com/traceloop/openllmetry) · E27 [Traceloop docs](https://www.traceloop.com/docs/openllmetry/introduction) · E28 [SWE-bench Verified vs scaffolding, Jun 2026](https://www.digitalapplied.com/blog/swe-bench-verified-june-2026-benchmark-vs-scaffolding-analysis) · E29 [Dissecting SWE-bench leaderboards (arXiv)](https://arxiv.org/pdf/2506.17208) · E30 [SWE-bench Pro public (Scale)](https://labs.scale.com/leaderboard/swe_bench_pro_public) · E31 [SWE-bench Pro paper](https://arxiv.org/pdf/2509.16941) · E32 [HAL GAIA (Princeton)](https://hal.cs.princeton.edu/gaia) · E33 [ARE/GAIA2 paper](https://arxiv.org/pdf/2509.17158) · E34 [GAIA2 OpenReview](https://openreview.net/forum?id=9gw03JpKK4) · E35 [Meta ARE — GAIA2 eval](https://facebookresearch.github.io/meta-agents-research-environments/user_guide/gaia2_evaluation.html) · E36 [tau2-bench GitHub](https://github.com/sierra-research/tau2-bench) · E37 [OSWorld](https://os-world.github.io/) · E38 [OSWorld methodology](https://benchmarkingagents.com/osworld/) · E39 [WebArena methodology](https://benchmarkingagents.com/webarena/) · E40 [VisualWebArena](https://www.emergentmind.com/topics/visualwebarena-vwa) · E41 [Terminal-Bench 2.0 leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.0) · E42 [BrowseComp (Galileo)](https://galileo.ai/blog/what-is-browsecomp-openai-benchmark-web-browsing-agents) · E43 [BrowseComp-Plus](https://github.com/texttron/BrowseComp-Plus) · E44 [METR Time Horizon 1.1, 2026-01-29](https://metr.org/blog/2026-1-29-time-horizon-1-1/) · E45 [METR Time Horizons](https://metr.org/time-horizons/) · E46 [HAL paper (arXiv)](https://arxiv.org/pdf/2510.11977) · E47 [HAL home](https://hal.cs.princeton.edu/) · E48 [HAL harness GitHub](https://github.com/princeton-pli/hal-harness) · E49 [Beyond pass@1 reliability (arXiv)](https://arxiv.org/pdf/2603.29231) · E50 [LH-Bench](https://arxiv.org/html/2603.22744v2) · E51 [Odysseys](https://arxiv.org/html/2604.24964v1) · E52 [CoffeeBench](https://arxiv.org/pdf/2606.16613) · E53 [Vending-Bench](https://grokipedia.com/page/Vending-Bench) · E54 [USQRD — "The Eval Harness Is the Deliverable," 2026-06-15](https://usqrd.com/insights/eval-harness-is-the-deliverable) · E55 [TDS — 12-metric eval-harness framework, 2026-05-13](https://towardsdatascience.com/building-an-evaluation-harness-for-production-ai-agents-a-12-metric-framework-from-100-deployments/) · E56 [DeepEval — LLM-as-a-judge 2026](https://deepeval.com/blog/llm-as-a-judge) · E57 [Logiciel — internal eval harness 2026](https://logiciel.io/blog/llm-eval-harness-internal-build-2026) · E58 [Digital Applied — agent observability 2026](https://www.digitalapplied.com/blog/agent-observability-2026-evals-traces-cost-guide) · E59 [promptfoo red team](https://www.promptfoo.dev/docs/red-team/) · E60 [Checkmarx — red team LLMs](https://checkmarx.com/learn/how-to-red-team-your-llms-appsec-testing-strategies-for-prompt-injection-and-beyond/) · E61 [OTel graduation + GenAI](https://www.webhani.com/blog/opentelemetry-graduation-genai-observability-2026) · E62 [MLflow — OTel GenAI semconv](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/genai-semconv/)

---

## 6. Enterprise agent platforms (what clients compare us against)

The platforms a finance/pharma/retail/HCM client will benchmark a custom build against. Verified against primary vendor sources (Dreamforce 2025, Ignite 2025, Google Cloud Next 2026, ServiceNow Knowledge 2026, AWS re:Invent 2025). AWS AgentCore is most relevant since Genesis delivers on AWS. Sources for this section are numbered **P1–P38** (below the section) to avoid collision with the main list.

### Salesforce Agentforce 360 (formerly Agentforce 3)

- **Version/status:** Current banner is **Agentforce 360**, announced 2025-10-13 at Dreamforce 2025 — a rebrand/expansion umbrella (folds in Data 360, Customer 360, Slack), *not* "Agentforce 4." The prior *engineering* release was **Agentforce 3** (2025-06-23), which added the **Command Center** (OpenTelemetry-based observability, GA Aug 2025) and native **MCP support**. [P1][P2]
- **Pricing (big 2026 change):** moved off **$2-per-conversation** to **Flex Credits** consumption — **$500 per 100,000 credits ($0.005/credit)**; a standard **Action = 20 credits ($0.10)**, **Voice Action = 30 credits ($0.15)**, fungible across Actions/Prompts/Translations/Voice. [P3][P4]
- **Adoption:** 12,000 customers at Agentforce 360 launch; Agentforce ARR passed **$500M** in Q3 FY26 (+330% YoY), ~9,500 paid deals. Named: Reddit 46% case deflection, OpenTable 70% autonomous resolution. **Reality check:** Benioff publicly addressed *low* adoption at Dreamforce; Stifel estimates only ~5.3% of customers have adopted. [P1][P5][P6]
- **Good at:** deep CRM grounding (Data 360), OOTB service/sales agents, governance + observability, Slack as human-agent surface. **Limits:** value concentrated if you're already deep in Salesforce data; credit consumption hard to forecast; real adoption friction.

### Microsoft Copilot Studio + Microsoft Agent Framework

- **Microsoft Agent Framework (the Semantic Kernel + AutoGen merger):** RC **2026-02-19**, **1.0 GA early April 2026** — single unified open-source SDK (.NET + Python) combining AutoGen multi-agent abstractions with Semantic Kernel enterprise features. SK is support-only; AutoGen is maintenance-only. [P7][P8]
- **Azure AI Foundry:** Foundry Agent Service GA May 2025; **Hosted Agents in Foundry** (deploy containerized agent code on Foundry-managed infra with identity/autoscale/state/observability) expanded at Build 2026. [P9]
- **Copilot Studio (low-code):** multi-agent orchestration, A2A, M365 Agents SDK orchestration, Fabric integration GA rolling through April 2026. Ignite 2025 introduced **Agent 365** (unified governance/policy/monitoring control plane) and **Work IQ**. [P10][P11]
- **Pricing:** **Copilot Credits** (renamed from "messages" 2025-09-01) — **$200/tenant/mo for 25,000 credits** (~$0.008) or PAYG ~$0.01/credit; a scripted FAQ ≈ 1 credit, a **reasoning-model response ≈ 100 credits**. [P12][P13]
- **Good at:** two-tier (low-code makers + code-first devs), tight M365/Teams/Graph grounding, Agent 365 governance. **Limits:** opaque per-feature credit accounting; SK→MAF migration churn; best economics inside M365.

### Google Gemini Enterprise + Agentspace + ADK

- **Version/status (major rebrand):** at **Google Cloud Next 2026** (April 2026) Google **rebranded Vertex AI → Gemini Enterprise Agent Platform** and folded in **Agentspace**; unified platform **GA 2026-04-22** (no migration needed). Lineage: Agentspace (2024/25) → Gemini Enterprise → Gemini Enterprise Agent Platform. [P14][P15]
- **ADK (Agent Development Kit):** open-source, code-first; **stable v1.0 across Python, Go, Java, TypeScript**, new **graph-based multi-agent orchestration**, MCP support; bundled with low-code **Agent Studio**, managed **Agent Engine** runtime, persistent memory, 200+ models (Gemini + Claude). [P16][P17]
- **Pricing:** **Gemini Enterprise Standard $30/user/mo** (annual), **Plus from $50/user/mo**; Vertex/Agent Engine runtime separately PAYG. [P18][P19]
- **Adoption:** **8M+ seats across 2,800+ companies**; paid MAU +40% QoQ Q1 2026. Named: Valeo (100k users), KPMG (90% adoption month one). [P20]
- **Good at:** full-stack (chip→model→runtime→inbox), strong ADK, A2A leadership, multi-model incl. Claude. **Limits:** rapid rebrand churn; biased to Workspace shops.

### ServiceNow AI Agents / AI Agent Orchestrator (Now Assist → Otto)

- **Version/status:** **Now Assist** + **AI Agent Orchestrator** remain current GA. At **Knowledge 2026** (May 2026) ServiceNow announced **Otto** — unifying Now Assist + Moveworks (acquired ~$2.85B, Mar 2025) + AI Experience on a new AI-native architecture; **Otto is direction, not full replacement yet** (live only in EmployeeWorks + AI Control Tower). [P21][P22]
- **Pricing:** restructured **2026-04-09** into three AI-native tiers — **Foundation / Advanced / Prime**; Now Assist now bundled into every tier, AI usage on consumption "Assist" pools with overage; no public price list. [P23][P24]
- **Good at:** agents embedded in ITSM/HR/CSM workflows on governed data; in-platform multi-agent orchestration. **Limits:** value locked to ServiceNow estate; Otto mid-transition (buying a roadmap); opaque consumption overages.

### AWS Bedrock AgentCore deep-dive (components, pricing, GA status) — most relevant for Genesis

**GA:** AgentCore reached **GA 2025-10-13**. At **re:Invent 2025** AWS added **Policy** (GA 2026-03-03) and **Evaluations** (GA 2026-03-31), plus **Memory episodic learning** and **Runtime bidirectional streaming** (voice). [P25][P26][P27]

**Framework/model agnostic (key):** AgentCore runs **any framework and any model** — AWS explicitly lists **LangGraph, CrewAI, LlamaIndex, Strands, OpenAI Agents SDK, Google ADK, Claude Agent SDK, LangChain, or custom** — so you can run **Anthropic or OpenAI APIs** on it, not just Bedrock-hosted models. [P30][P31]

| Component | What it does | Pricing (2026) |
|---|---|---|
| **Runtime** | Serverless agent execution; each session in an isolated microVM; up to **8 hrs async** (15 min sync) | **$0.0895/vCPU-hr + $0.00945/GB-hr**, per-second, 1-sec min |
| **Gateway** | Turns APIs/Lambda/MCP servers/knowledge bases into agent tools with auth + semantic tool search | **$0.005/1,000 invocations**; Search **$0.025/1,000**; tool indexing **$0.02/100 tools/mo** |
| **Memory** | Short-term (session) + long-term (semantic/episodic) | Short-term **$0.25/1,000 events**; long-term **$0.75/1,000 records/mo** (self-managed $0.25); retrieval **$0.50/1,000** |
| **Identity** | OAuth/token brokering; agents act as/on behalf of users | **Free** via Runtime/Gateway; **$0.010/1,000** tokens for non-AWS resources |
| **Browser Tool / Code Interpreter** | Managed headless browser / sandboxed code exec | **$0.0895/vCPU-hr + $0.00945/GB-hr** |
| **Observability** | OpenTelemetry traces/spans/metrics via CloudWatch | CloudWatch rates |
| **Policy** (GA Mar 2026) | Guardrails via natural language or **Cedar**; intercepts Gateway tool calls pre-execution (e.g., cap refunds by role) | **$0.000025/authorization request**; NL authoring **$0.13/1,000 input tokens** |
| **Evaluations** (GA Mar 2026) | 13 built-in evaluators (correctness, tool-selection accuracy, safety, goal success, context relevance) + custom | Built-in **$0.0024/1k in + $0.012/1k out**; custom **$1.50/1,000 evals** |
| **Web Search** | Grounds agents in live web | **$7.00/1,000 queries** |
| **Agent Registry** (Preview) | Catalog/discovery of agents & tools | Free tier then **$0.40/1,000 records** |

(Pricing: [P28]; components/GA: [P29]) **Consumption-priced, no upfront/minimums; all services support VPC/PrivateLink/CloudFormation.**

**Bedrock Agents vs AgentCore — don't confuse them:** "Bedrock Agents" is the older opinionated managed-agent feature (action groups/knowledge bases inside Bedrock). **AgentCore** is the newer framework-agnostic *infrastructure layer* you wrap around **your own** agent code and any model. For a custom build, AgentCore is the relevant product.

**Good at:** enterprise infra primitives (session isolation, identity brokering, long-running exec, Cedar policy guardrails, managed memory, OTel observability) while staying framework/model-agnostic. **Limits:** à-la-carte plumbing, not a turnkey business agent — you still write the logic; 12+ usage meters to model; some pieces (Registry, Payments) in preview.

### Notable others (quick hits)

- **Sierra** (Bret Taylor; authors of tau-bench) — CX/voice agents; **$950M Series E May 2026 at ~$15.8B**, ~$150M ARR, claims 40%+ of Fortune 50; outcome-based pricing. Not a general dev platform. [P32][P33]
- **Glean** — work-AI/enterprise-search + agents; ~$300M ARR (secondary), $7.2B valuation. Grounds agents in enterprise knowledge/permissions. [P34]
- **Palantir AIP / AIP Now** — ontology-grounded, governed/auditable agent workflows; strongest in regulated/industrial settings. [P35][P36]
- **Writer (Palmyra)** — full-stack enterprise gen-AI on own LLMs + graph RAG + guardrails; $1.9B (Nov 2024); Accenture/Intuit/Uber/Vanguard. Governed self-hosted-model workflows. [P37][P38]
- **Cohere North** — secure/on-prem-friendly enterprise agents for data-sovereignty-sensitive buyers.

### Build-vs-platform guidance for an AWS custom agentic build (2-3 ppl, 6-7 wks, Anthropic/OpenAI allowed)

**The decision is not "AgentCore *or* a framework" — it's "framework always; add AgentCore components only where they replace real infra work."** The agent *logic* should live in **Claude Agent SDK or LangGraph** regardless (faster iteration, local debuggability, model-agnostic). Then cherry-pick AgentCore where it's expensive to build and cheap to adopt:
- **Runtime** — for session isolation, long-running (8 hr) agents, or serverless scale without managing ECS. (Short request/response? plain Lambda/Fargate may be simpler.)
- **Identity** (free via Runtime/Gateway) — if agents act **on behalf of users** with OAuth (tedious to build).
- **Memory** — managed long-term/episodic memory vs rolling your own vector store + retrieval.
- **Gateway** — many existing APIs/Lambdas to expose as tools with auth + semantic selection.
- **Policy (Cedar) + Evaluations** — if the competition rewards demonstrable **guardrails + eval rigor** (hard to fake, map directly to enterprise-platform selling points).

**Pragmatic path given the AWS constraint: Claude Agent SDK/LangGraph agents deployed on AgentCore Runtime, adding Identity/Memory/Policy as needed.**

**What the platforms do that a custom build must consciously match or deliberately skip:**
1. **Observability/tracing** — *match* (OpenTelemetry is table stakes, cheap).
2. **Guardrails/policy** — *match a basic version* (enterprises won't trust an ungoverned agent).
3. **Identity & on-behalf-of auth** — *match if* the use case touches user-specific data; else skip.
4. **Evaluation harness** — *match a lightweight version* (a demonstrable eval loop is a strong competition differentiator).
5. **Data grounding to systems of record** — the platforms' deepest moat; a custom build should *deliberately scope* to a focused, well-integrated dataset rather than match breadth.
6. **Multi-agent orchestration** — *match only if the problem needs it* (free in LangGraph; don't add complexity for its own sake).
7. **Pre-built business agents / marketplaces / low-code builders / per-seat packaging** — *deliberately skip* (commercialization layer, irrelevant to a 6-7 week build).

**Accuracy caveats:** some adoption/ARR figures (Agentforce deal counts, Glean/Sierra ARR) are from secondary/analyst reporting — treat as directional. Microsoft Agent Framework 1.0 GA is "early April 2026" (exact day varies by source).

### §6 Sources (P1–P38)

P1 [Salesforce — Agentforce 360 investor release, 2025-10-13](https://investor.salesforce.com/news/news-details/2025/Welcome-to-the-Agentic-Enterprise-With-Agentforce-360-Salesforce-Elevates-Human-Potential-in-the-Age-of-AI/default.aspx) · P2 [Salesforce — Agentforce 3, 2025-06-23](https://www.salesforce.com/news/press-releases/2025/06/23/agentforce-3-announcement/) · P3 [Salesforce — Flex Credits Rate Card, 2026-04-21](https://www.salesforce.com/en-us/wp-content/uploads/sites/4/assets/pdf/agentforce/Flex-Credits-Rate-Card-04.21.2026.pdf) · P4 [Constellation — Flex Credits](https://www.constellationr.com/insights/news/salesforce-revamps-agentforce-pricing-flex-credits-what-you-need-know) · P5 [diginomica — 18,500 use cases](https://diginomica.com/agentforce-users-now-number-18500-salesforce-turns-109-billlon-quarter) · P6 [Salesforce Ben — low adoption](https://www.salesforceben.com/marc-benioff-addresses-low-agentforce-adoption-at-dreamforce-25/) · P7 [MS Learn — Agent Framework overview](https://learn.microsoft.com/en-us/agent-framework/overview/) · P8 [MS DevBlogs — migrate SK/AutoGen to MAF RC](https://devblogs.microsoft.com/agent-framework/migrate-your-semantic-kernel-and-autogen-projects-to-microsoft-agent-framework-release-candidate/) · P9 [MS DevBlogs — MAF at Build 2026](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/) · P10 [MS 365 blog — Ignite 2025](https://www.microsoft.com/en-us/microsoft-365/blog/2025/11/18/microsoft-ignite-2025-copilot-and-agents-built-to-power-the-frontier-firm/) · P11 [MS Copilot blog — multi-agent orchestration](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/new-and-improved-multi-agent-orchestration-connected-experiences-and-faster-prompt-iteration/) · P12 [Azure — Copilot Studio pricing](https://azure.microsoft.com/en-us/pricing/details/copilot-studio/) · P13 [CloudZero — Copilot Studio pricing 2026](https://www.cloudzero.com/blog/copilot-studio-pricing/) · P14 [Google Cloud — Gemini Enterprise Agent Platform intro](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform) · P15 [Google Cloud — product page](https://cloud.google.com/products/gemini-enterprise-agent-platform) · P16 [Google Cloud docs — ADK](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk) · P17 [Google Cloud — new Gemini Enterprise](https://cloud.google.com/blog/products/ai-machine-learning/the-new-gemini-enterprise-one-platform-for-agent-development) · P18 [C-Sharp Corner — Gemini Enterprise pricing](https://www.c-sharpcorner.com/article/google-gemini-enterprise-pricing-plans-cost-per-seat-and-business-value/) · P19 [Redress Compliance — licensing 2026](https://redresscompliance.com/google-gemini-enterprise-licensing-guide-2026) · P20 [SQ Magazine — Gemini stats 2026](https://sqmagazine.co.uk/google-gemini-ai-statistics/) · P21 [ServiceNow — Otto press release](https://newsroom.servicenow.com/press-releases/details/2026/ServiceNow-Otto-creates-the-unified-AI-experience-for-the-enterprise/default.aspx) · P22 [NowSpectrum — what is Otto](https://www.nowspectrum.com/blog/what-is-servicenow-otto) · P23 [TechTarget — ServiceNow AI pricing change](https://www.techtarget.com/searchitoperations/news/366641692/ServiceNow-AI-pricing-change-takes-on-enterprise-ROI-struggles) · P24 [eesel — ServiceNow AI pricing 2026](https://www.eesel.ai/blog/servicenow-ai-pricing) · P25 [AWS — AgentCore GA](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available/) · P26 [AWS ML blog — AgentCore GA](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-is-now-generally-available/) · P27 [AWS News — AgentCore evals + policy (re:Invent 2025)](https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/) · P28 [AWS — AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/) · P29 [AWS docs — AgentCore overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) · P30 [AWS docs — use any framework](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/using-any-agent-framework.html) · P31 [AWS — AgentCore product page](https://aws.amazon.com/bedrock/agentcore/) · P32 [TechCrunch — Sierra $950M](https://techcrunch.com/2026/05/04/sierra-raises-950m-as-the-race-to-own-enterprise-ai-gets-serious/) · P33 [Tech Startups — Sierra $15.8B](https://techstartups.com/2026/05/04/bret-taylors-ai-startup-sierra-raises-950m-at-15-8b-valuation-as-demand-for-ai-agents-surges/) · P34 [Startup Fortune — Sierra/Glean ARR](https://startupfortune.com/sierra-has-635-million-150-million-in-arr-and-a-clear-theory-of-how-to-own-enterprise-ai-before-the-incumbents-wake-up/) · P35 [Futurum — Palantir Q1 FY26](https://futurumgroup.com/insights/palantir-q1-fy-2026-revenue-beats-estimates-us-demand-drives-outlook-raise/) · P36 [Palantir — AIP Now](https://aip.palantir.com/) · P37 [Writer — Series C](https://writer.com/blog/series-c-funding-writer-press-release/) · P38 [Sacra — Writer](https://sacra.com/c/writer/)

---

## 7. Agent security & governance (the enterprise gate)

Finance, pharma, and payroll clients will not deploy an agent that can't answer the security questions. In 2026 this is **the** differentiator between a hackathon toy and a client-ready system. [12][13]

- **Prompt injection is #1 and unsolved.** OWASP's top LLM risk in 2026; researchers treat it as unsolved because filters aren't reliable. Content the agent reads (a doc, webpage, code comment) can redirect it, exfiltrate data, or trigger actions — no malware needed. [12]
- **The blast-radius problem.** Over-permissioned agents are catastrophic: **78%** of agent deployments execute high-risk tool calls without deterministic policy enforcement; a compromised agent with prod write access causes irreversible damage in seconds. [12]
- **The alarming survey stat.** **88%** of orgs reported confirmed/suspected agent security incidents in the past year, yet **82%** of executives believed existing policies already protected them. [12]
- **What enterprises require in 2026 (layered defense):**
  1. **Least-privilege tool scoping** — minimum permissions per task; incremental scope consent; tool-level approval annotations for sensitive ops. [12]
  2. **Human-in-the-loop on irreversible actions** — gate `send_email`, DB writes, payments behind explicit approval (the Claude Agent SDK / LangGraph HITL pattern). [12][20]
  3. **Agent identity & auth** — persistent, attested identities; mandatory auth for all remote MCP servers; verify identity at every inter-agent handoff. [12][13]
  4. **Sandboxing/containment** — isolated execution with the smallest capability set; network segmentation for MCP servers. Both OpenAI Agents SDK (Apr 2026) and Anthropic Managed Agents ship sandboxed execution. [12][18]
  5. **Authorization at a boundary the agent's code can't cross** — deterministic policy enforcement outside the model. [12]
  6. **Tamper-evident audit trails** — a record of every action, for compliance and forensics. [12][13]
- **Governance context:** authorization propagation across multi-agent systems is now treated as identity-governance infrastructure. [13]

**For Genesis:** an explicit **threat model + guardrails + audit trail + HITL on destructive actions**, demonstrated in the demo, is a high-ROI move for the 25% feasibility/production-readiness score and directly addresses finance-client concerns.

---

## 8. Commodity vs cutting-edge (the key deliverable)

What a July-2026 audience (and an AI judge) reads as **dated/slop** vs **technically deep**:

| Reads as COMMODITY / SLOP (2024-era) | Reads as CUTTING-EDGE (2026) |
|---|---|
| Plain RAG chatbot that only *answers* questions | Agent that *acts* — calls tools/APIs, executes multi-step workflows, changes state [11] |
| Single-prompt "LLM wrapper with tools" | Cognitive infrastructure: **planner → executor → verifier**, memory, permissions, audit trails [11][9] |
| "It worked in the demo" (one happy path) | **Eval harness**: offline sets, LLM-as-judge calibrated to humans, regression CI, Pass@k reliability [10][24] |
| No cost/latency story | **Accuracy↔cost↔latency dashboard**; model routing (cheap sub-tasks to Sonnet/Haiku/open models) [9][16] |
| One giant model call, no self-correction | **Self-correction / reflection / verifier loops** with evidence they raise accuracy [9][25] |
| Fixed linear script | **Verifiable multi-step autonomy** that recovers from failures (LangGraph durable execution) [3] |
| Ignores security | Threat model, least-privilege tools, HITL on destructive actions, sandboxing, audit trail [12] |
| "We use MCP" pitched as innovation | MCP as plumbing; the *innovation* is the workflow + verification it enables [4] |
| Multi-agent for buzzword value | Multi-agent coordination **that measurably beats** a single agent + tools [9] |
| Opaque black box | **OpenTelemetry GenAI traces**, reproducible runs, inspectable decisions [24] |

The one-sentence test the judges will implicitly apply: *"Does the complexity earn its place, and can you prove the thing works with numbers and traces?"*

---

## 9. Implications for Genesis Track A (≤10 sharp takeaways)

1. **Build orchestration in LangGraph, on AWS.** It has the most enterprise mileage (JPMorgan, BlackRock, Klarna), maps cleanly to audit trails/rollback/HITL that finance clients demand, is MIT/self-hostable (no vendor lock story to defend), and is provider-agnostic so you can route models. This maximizes both technical-depth (25%) and feasibility (25%). [3][19]
2. **Default the reasoning model to Claude Opus 4.8; route down to Sonnet 5 / Haiku for cheaper sub-steps.** Opus 4.8 leads agentic coding and is the recommended agent brain; Sonnet 5's intro pricing ($2/$10 thru Aug 31) makes cost engineering easy. Consider **Fable 5** only for the hardest long-horizon step and say why. [1][7][17b]
3. **Wire every tool over MCP, and use AWS Bedrock AgentCore Gateway to expose internal APIs as MCP tools** — it's the AWS-native, standards-based path and shows platform fluency without lock-in. [4][26]
4. **The eval harness is the single highest-ROI investment for the AI-judge score.** Ship: a synthetic offline eval set, an LLM-as-judge calibrated against a small human-labeled sample, regression CI, and an accuracy/cost/latency dashboard. Use **LangSmith** (native to LangGraph) or **Braintrust**. This is the difference between "demo" and "production-ready." [10][24]
5. **Emit OpenTelemetry GenAI traces from day one.** Reproducible, inspectable runs are both a readiness signal and how you'll debug. [24]
6. **Include a verifier/self-correction loop and prove it lifts accuracy.** A judge/critic that sends work back to revise (the Performance-Outcomes pattern) is the clearest "cutting-edge autonomy" signal — but bring the before/after eval numbers. [9][25]
7. **Make multi-agent coordination earn its place.** Only add a supervisor-worker or debate topology if your evals show it beats a single agent + tools; otherwise a well-instrumented single agent scores better on originality-through-restraint than gratuitous complexity. [9]
8. **Ship a visible security story.** Threat model (lead with prompt injection), least-privilege tool scoping, HITL on irreversible actions, sandboxed execution, and a tamper-evident audit trail. For finance clients this is decisive for the feasibility score. [12][13]
9. **Frame autonomy with the METR "time horizon" concept.** "Our agent reliably handles an N-hour analyst workflow unattended, with a verifier and audit trail" is a sharper pitch than "it's agentic." [22]
10. **Don't out-scope the platforms — out-*specialize* them.** Agentforce/Copilot Studio/AgentCore win on breadth; a Track-A entry wins on a deep, verifiable, cost-engineered solution to *one real client problem* with evals no low-code platform demo will show. [11]

---

## 10. Candidate use-case seeds (workflow • why agentic • demo moment)

Drawn from the client roster (finance-heavy: Visa, Amex, Morgan Stanley, Capital One, Barclays, Western Alliance, Invesco, Lendmark, ampliFI; plus Dow Jones, J&J, Kohl's, ADP). All use **synthetic data**. [23][background]

1. **AML/fraud alert investigation agent** (Amex/Capital One/Barclays/Western Alliance) • *why agentic:* autonomously queries registries, cross-references internal records, validates transactions across many steps, clears alerts alert-to-closure • *demo:* an alert resolved in minutes with a full audit trail and a confidence score, plus a verifier that catches a planted false-positive. [23]
2. **KYC/onboarding due-diligence agent** (Morgan Stanley/Lendmark/ampliFI) • *why agentic:* runs CIP sourcing, ownership-structure unwrapping, sanctions + adverse-media screening in *parallel*, shifting KYC from calendar-based to always-on • *demo:* onboarding time cut from days to minutes with parallel sub-agents and a policy-adherence check. [23]
3. **Reconciliation & exception-handling agent** (Visa/Invesco) • *why agentic:* multi-step matching, root-causes breaks, drafts adjusting entries, escalates only true exceptions with HITL • *demo:* a batch of synthetic breaks auto-resolved, exceptions routed for approval, with cost/latency shown per item.
4. **Investment-research / earnings-synthesis agent** (Morgan Stanley/Invesco/Dow Jones) • *why agentic:* plans a research task, pulls filings + news (Dow Jones/Factiva-style synthetic corpus), self-critiques, cites sources • *demo:* a research memo with inline citations and a reflection pass that corrects a planted error.
5. **Regulatory-change / compliance-monitoring agent** (all finance) • *why agentic:* continuously monitors rule changes, maps them to internal policies, drafts gap analyses • *demo:* a new (synthetic) regulation ingested → affected policies flagged → remediation steps drafted, with audit trail.
6. **Credit / underwriting decision-support agent** (Capital One/Lendmark/Western Alliance) • *why agentic:* gathers applicant data, runs checks, produces an explainable recommendation with a verifier for policy compliance • *demo:* a decision with a full reasoning trace and a "why not approved" explanation — explainability as the headline.
7. **Pharma safety / literature-triage agent** (J&J) • *why agentic:* screens adverse-event reports or literature, extracts structured signals, escalates • *demo:* a synthetic AE dossier triaged with structured extraction + human-review checkpoint. *(Note security/PII framing.)*
8. **Retail merchandising / supply agent** (Kohl's) • *why agentic:* monitors inventory signals, reconciles across systems, drafts reorders with approval gates • *demo:* a stockout risk detected → cross-checked → reorder proposed for human approval.
9. **Payroll/HCM exception & compliance agent** (ADP) • *why agentic:* validates payroll runs across jurisdictions, catches anomalies, explains discrepancies • *demo:* a synthetic multi-jurisdiction payroll batch validated, anomalies flagged with explanations and an audit trail.
10. **Contract / T&C analysis agent** (cross-industry) • *why agentic:* extracts terms, checks against policy, flags risky clauses, drafts redlines with a verifier • *demo:* a contract analyzed → risky clauses flagged with rationale → redline proposed, judge-verified.

**Recurring winning pattern across all seeds:** a *bounded, high-value, multi-step workflow* + *parallel evidence-gathering* + *a verifier/self-correction loop* + *HITL on irreversible actions* + *an audit trail* + *an eval harness proving accuracy/cost/latency*. That combination is exactly what reads as cutting-edge and production-ready in July 2026.

---

## Sources

1. Introducing Claude Opus 4.5 / Opus 4.8 & MarkTechPost "Claude Sonnet 5 vs Sonnet 4.6 vs Opus 4.8" (agentic-coding benchmarks, pricing), 2026-06-30 — https://www.marktechpost.com/2026/06/30/anthropic-claude-sonnet-5-vs-sonnet-4-6-vs-opus-4-8-agentic-coding-benchmarks-api-pricing-and-cost-performance-tradeoffs-compared/ ; https://www.anthropic.com/news/claude-opus-4-8
2. TechCrunch, "Anthropic launches Claude Sonnet 5 as a cheaper way to run agents," 2026-06-30 — https://techcrunch.com/2026/06/30/anthropic-launches-claude-sonnet-5-as-a-cheaper-way-to-run-agents/
3. Agent framework comparisons (LangGraph vs Claude Agent SDK vs OpenAI Agents SDK), 2026 — https://turion.ai/blog/langgraph-vs-openai-claude-agent-sdk-2026/ ; https://qubittool.com/blog/ai-agent-framework-comparison-2026 ; https://www.requesty.ai/blog/best-ai-agent-sdks-compared-2026-langchain-crewai-openai-anthropic-google
4. MCP ecosystem & roadmap 2026; MCP vs A2A — https://a2a-mcp.org/blog/mcp-2026-roadmap ; https://amdatalakehouse.substack.com/p/the-state-of-agentic-ai-standards ; https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol
7. LM Council / cross-model benchmark comparisons (Opus 4.8 vs GPT-5.5 vs Gemini 3.1 Pro; Fable 5 SWE-bench), Jul 2026 — https://lmcouncil.ai/benchmarks ; https://iternal.ai/llm-selection-guide
8. Introducing GPT-5.5 (OpenAI) & GPT-5.5 launch analyses (Spud, 2026-04-23, pricing, Terminal-Bench/SWE-bench Pro) — https://openai.com/index/introducing-gpt-5-5/ ; https://tech-insider.org/gpt-5-5-launch-openai-april-23-terminal-bench-2026/ ; https://en.wikipedia.org/wiki/GPT-5.5
9. Agent orchestration patterns 2026 (planner-executor, supervisor-worker, judge/critic, reflection, debate, shared memory) — https://vdf.ai/blog/agentic-design-patterns-practical-guide/ ; https://www.digitalapplied.com/blog/multi-agent-orchestration-5-patterns-that-work ; https://devrev.ai/blog/ai-agent-orchestration ; https://dev.to/gabrielanhaia/react-plan-and-execute-or-reflection-the-three-agent-patterns-every-engineer-needs-in-2026-355p
10. Eval-harness readiness ("the eval harness is the deliverable," compounding error, 12-metric framework) — see §5 Sources E54, E55 for primaries.
11. RAG-chatbot vs agentic ("cognitive infrastructure," demo-slop) — https://cogitx.ai/blog/ai-agents-complete-overview-2026 ; https://growwstacks.com/blog/chatbot-vs-rag-vs-agentic-ai-explained ; https://heeya.fr/en/blog/ai-agent-vs-chatbot-key-differences-2026
12. AI agent security 2026 (prompt injection #1/unsolved; 88% incident stat; 78% high-risk tool calls; least-privilege, sandboxing, audit) — https://www.nightfall.ai/blog/prompt-injection-protection ; https://improvado.io/blog/ai-agent-security ; https://ecorpit.com/ai-agent-security-prompt-injection-guardrails-2026/ ; https://www.miniorange.com/blog/ai-agent-security-risks/
13. Agent identity/authorization governance — https://aport.io/blog/best-ai-agent-authentication-authorization-2026/ ; arXiv "Authorization Propagation in Multi-Agent AI Systems," 2026 — https://arxiv.org/pdf/2605.05440
15. Claude Fable 5 announcement (GA 2026-06-09, $10/$50, 1M context, long-running agents) — https://www.anthropic.com/news/claude-fable-5-mythos-5 ; https://www.anthropic.com/claude/fable
15b. Gemini 3.1 / 3.5 Pro specs & pricing, Antigravity — https://llm-stats.com/blog/research/gemini-3.1-pro-launch ; https://www.developersdigest.tech/blog/gemini-3-5-pro-developer-guide-2026 ; https://www.eesel.ai/blog/google-gemini-3-pricing
16. Open-weights for agentic coding 2026 (DeepSeek V4, Kimi K2.6, Qwen 3.x, GLM) — https://www.mindstudio.ai/blog/best-open-source-llms-agentic-coding-2026 ; https://tech-insider.org/best-open-source-llm-2026/ ; https://wavect.io/blog/open-weight-llm-comparison-2026/
17. MCP governance/spec/registry (Linux Foundation Agentic AI Foundation Dec 2025; spec 2025-11-25; ~97M downloads) — https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026
17b. Claude Platform Models Overview (authoritative model IDs, context, pricing) & Claude API skill — https://platform.claude.com/docs/en/about-claude/models/overview
18. OpenAI AgentKit (Agent Builder, ChatKit, Connector Registry, Agents SDK, Evals; 2025-10-06) & Agents SDK Apr-2026 sandbox update — https://openai.com/index/introducing-agentkit/ ; https://openai.com/index/the-next-evolution-of-the-agents-sdk/
19. Framework adoption/stars 2026 (LangGraph enterprise list, CrewAI/AutoGen/smolagents/Pydantic AI) — https://medium.com/@atnoforgenai/10-ai-agent-frameworks-you-should-know-in-2026-langgraph-crewai-autogen-more-2e0be4055556 ; https://dev.to/linou518/the-2026-ai-agent-framework-decision-guide-langgraph-vs-crewai-vs-pydantic-ai-b2h ; https://alicelabs.ai/en/insights/best-ai-agent-frameworks-2026
20. Claude Agent SDK production features (renamed Sept 2025; subagents/skills/MCP; Dynamic Workflows + Performance Outcomes June 2026) — https://code.claude.com/docs/en/agent-sdk/overview ; https://www.totalum.app/blog/claude-agent-sdk-totalum-2026 ; https://inference.net/content/claude-agent-sdk-production-guide/
21. Computer-use agents & OSWorld 2026 (Opus 4.7 82.3%; Operator 69.9%; route-by-workload) — https://www.digitalapplied.com/blog/computer-use-agents-2026-claude-openai-gemini-matrix ; https://coasty.ai/blog/osworld-benchmark-results-2026-ai-computer-use-agents-ranked
22. METR Task-Completion Time Horizons (Opus 4.6 ~14.5 hrs Feb 2026; doubling ~4.3 months) — https://metr.org/time-horizons/ ; https://epoch.ai/benchmarks/metr-time-horizons ; https://agentmarketcap.ai/blog/2026/04/11/new-moores-law-ai-agent-task-horizons-2026
23. Agentic AI in financial services (KYC/AML, fraud alert investigation, reconciliation, parallel onboarding) — https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/how-agentic-ai-can-change-the-way-banks-fight-financial-crime ; https://www.kore.ai/blog/ai-agents-in-finance-banking-12-proven-use-cases-2026 ; https://appstekcorp.com/blog/agentic-ai-for-kyc-and-compliance/
24. Agent benchmarks 2026 (tau2-bench policy adherence/GLM-5.2 99.1%; GAIA HAL; six benchmarks that matter incl. METR) — https://github.com/sierra-research/tau2-bench ; https://awesomeagents.ai/leaderboards/agentic-ai-benchmarks-leaderboard/ ; https://decodethefuture.org/en/ai-agent-benchmarks-2026/ ; https://pricepertoken.com/leaderboards/benchmark/tau2
25. Claude Agent SDK Dynamic Workflows + Performance Outcomes (grader-driven revise loops), June 2026 — https://www.totalum.app/blog/claude-code-subagents-totalum ; https://linas.substack.com/p/anthropic-claude-2026-every-launch-guide
26. Agentic payments protocol status (x402/AP2/ACP/MPP) & AWS Bedrock AgentCore payments — https://www.crossmint.com/learn/agentic-payments-protocols-compared ; https://aws.amazon.com/blogs/machine-learning/agents-that-transact-introducing-amazon-bedrock-agentcore-payments-built-with-coinbase-and-stripe/ ; https://www.openfort.io/blog/agentic-payments-landscape

*(Sources 5/6 sub-sections — §5b evals/observability and §6b enterprise-platforms deep-dives — are being finalized from dedicated sub-agent research and will be appended with their own numbered sources.)*
