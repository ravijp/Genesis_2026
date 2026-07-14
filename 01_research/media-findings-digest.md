# Media & Information Services — Findings Digest (as of 2026-07-14)

> **Scope note:** Load-bearing findings from the media research track. The full synthesis lives in `media.md` (this file remains the quick-reference digest).

## The big cross-cutting pattern: "agent-ready data" is the 2025-26 gold rush

Every major financial-information provider now exposes data to AI agents via MCP — this is the strongest, most Zenon-relevant theme found:

- **S&P Global**: MCP servers via Kensho (Claude integration Jul 2025; AWS Dec 2025; ChatGPT app Feb 2026; Cohere Jun 2026). **Credit Memo Builder** (agentic, GA Jun 4, 2026, analyst-in-the-loop). Q1-26: AI features used by >1/3 of Capital IQ Pro users; Jul 6, 2026 reorg elevated Kensho to a client-facing vertical "to accelerate Agentic Solutions."
- **Moody's**: **Moody's Agentic Solutions** GA Sept 16, 2025 ("credit memo 40 hours → 2 minutes" claim); native app in Claude (Apr 9, 2026) incl. **KYC/compliance workflows live** (entity profiling, ownership mapping, adverse media, sanctions); AWS Marketplace Apr 2026; MCP servers on OpenAI platform; GRID screening + AI Review (~80% false-positive cut claim).
- **LSEG**: "LSEG Everywhere" — MCP partnerships stacked in 7 months (Databricks Sep 2025, Microsoft Oct 2025, Anthropic Oct 27 2025, OpenAI Dec 2025, Google May 2026); Workspace **Deep Research agent** (Jun 2026); World-Check On Demand/Verify launched but explicitly NOT agentic-branded.
- **FactSet**: claimed **first production-grade MCP server** (Dec 16, 2025; 9 datasets); **450 clients engaged, 13x QoQ API-call growth, >20% of top-100 clients paying** (Q3 FY26 call, Jul 1, 2026); Mercury knowledge agent line; Google Cloud strategic partnership Jun 30, 2026; AI SKUs >10% of ASV growth.
- **Bloomberg**: **ASKB** agentic Terminal interface in beta (Feb 23, 2026, ~1/3 of 375k users; multi-model routing incl. Anthropic); embraced MCP internally but NO public MCP server; CTO on record: "Evaluations... are the make-or-break of building a useful, trustworthy system."
- **Anthropic "Agents for financial services"** (May 5, 2026): 10 GA agent templates — pitch builder, earnings reviewer, **GL reconciler, month-end closer, statement auditor, KYC screener** — plus $1.5B JV with Wall Street firms; production users incl. JPMC, Goldman, Citi, AIG, **Visa**.

**Implication for Genesis:** "agent + trusted data via MCP + visible evals + analyst-in-the-loop" is the certified enterprise pattern of mid-2026. Building on it = credible; building a bare chatbot = dated.

## Compliance/KYC agent vendor map (crowded but validating)

- **ComplyAdvantage Mesh** agentic workflows: ~85% of routine L1 screening alerts auto-resolved (vendor claim, Gemini-based). **Nasdaq Verafin** "Agentic AI Workforce": 650+ FIs, EDD review time −50%. **FIS × Anthropic** Financial Crimes AI Agent: BMO + Amalgamated pilots, GA planned 2H 2026. **Bretton AI** (ex-Greenlite): Robinhood, Mercury, Gusto. Quantifind: Celent-audited $177.9M/yr efficiency claim for Tier-1 banks.
- Regulatory: Apr 2026 Fed/OCC/FDIC revised interagency model-risk guidance calls generative + agentic AI "novel and rapidly evolving"; RFI planned.
- **Dow Jones Risk & Compliance: NO agentic product as of Jul 2026** — Integrity Check (Apr 2024, w/ Xapien) is generative-AI due-diligence only. LexisNexis Risk: agentic messaging but no shipped agentic screening product. → **White space: agentic screening/monitoring built ON DJ R&C data is an open, originality-scoring crossover for Zenon (Dow Jones client + bank clients).**

## Newsroom/media agents — what's genuinely agentic vs not

- Genuinely agentic & shipped: **NYT Cheatsheet** (chainable AI "recipes" over datasets; GA newsroom-wide Feb 2026 — best-documented US example), **WSJ/Dow Jones "Orca"** (podcast-corpus mining pipeline; INMA Best in Show 2026 — a Dow Jones showcase!), **BBC Eye "Haystack"** (LangGraph multi-agent, 10k Russian posts), **Mediahuis 6-agent first-line news pipeline** (trial, Feb 2026), McClatchy Content Scaling Agent (live but triggered union backlash — cautionary tale).
- NOT agentic despite hype: AP Verify (manual toolkit dashboard), WaPo Ask The Post (single-shot RAG), Full Fact AI (classifier pipeline), most "AI fact-checking." Reuters Institute: 75% of industry expects large agentic impact in 2026 — expectation outruns deployment.
- **Implication:** true multi-step verification/monitoring agents in news are still rare → originality space if a Dow Jones-flavored idea is wanted.

## Rights, licensing & royalty automation — pre-agentic industry-wide

- No genuinely agentic rights-clearance/royalty system found anywhere (Getty, Shutterstock, Adobe, YouTube Content ID, PROs, MLC, streaming platforms). Closest: Whip Media "Helix" (pilot), Rightsline ($500M Hg raise May 2026 — agentic AI is explicitly future roadmap). TollBit/Cloudflare pay-per-crawl/Microsoft Publisher Content Marketplace = rules-based licensing infra for agent traffic, not agents.
- Publisher economics: AI-referral traffic +670-758% YoY holiday 2025; conversion flipped from −23% (Jul 2025) to +31% vs other channels; SPUR coalition building content-telemetry pricing standard.
- **Implication:** "agentic era" monetization/licensing ops is white space but with weak direct Zenon-client demand vs finance nodes.

## Ad tech (context only)

Industry pattern = "governed autonomy": AI proposes, human approves (Google AI Max GA Apr 2026 but independent study shows CPA +16%, "coin toss"; Meta Advantage+ beats manual only 42% of time). Only Amazon **Alexa+ Agentic Ads** completes transactions in-conversation (2 partners, status disputed). Most autonomous B2B example (Vox Media/Boostr AdCP negotiation) is single-sourced.

## Seeds worth carrying into ideation

1. Adverse-media/sanctions **screening assurance agent** on DJ Risk & Compliance-style data for bank onboarding (Dow Jones × Barclays/WAB crossover; DJ itself has no agentic product).
2. **"Orca-for-X"**: continuous corpus-mining agent over niche audio/video/filings for a data business (validated by WSJ's award).
3. Agent-ready data productization: build a client's proprietary dataset into a governed **MCP server + agent skills** (the S&P/Moody's/FactSet playbook applied to a mid-market client).
4. Claims-extraction + verification agent for research/editorial workflows (Semafor Intelligence pattern, applied to financial research at MS/Invesco).
5. Evals-first agent governance harness as a differentiator in ANY build (Bloomberg CTO quote; AI-judge scoring).
