# Competition Brief — Genesis 2026 (distilled)

Source: *2026 Zenon Agentic AI Competition Kickoff* deck. This is the reference sheet; every idea is judged against it.

## What it is

Zenon's internal GenAI / Agentic AI competition. 12 weeks, kicked off June 2026. Teams build a pitch-and-ship-able asset.

**Objectives**
1. Accelerate **Agentic AI** capability development within the firm.
2. Surface **real-world solution ideas** applicable to clients and internal operations.
3. Develop an **AI-first, engineering-focused culture**.

> "Teams practice structured execution while producing assets that can be pitched and shipped."

## Tracks (pick one)

| Track | Focus | Notes |
|-------|-------|-------|
| **A — Client-Facing Solutions** | Agentic workflows / GenAI tools that solve real client problems and can ship as client-ready solutions | Highest "Zenon impact" ceiling; needs a credible client story |
| **B — Internal Ops & Tooling** | Internal productivity: prospect outreach, proposal generation, knowledge management, firm enablement | Clear *time-savings* ROI; easy to dogfood + measure |
| **C — Open Category** | Exploratory: eval frameworks, agentic optimization, "anything" | Highest originality ceiling; needs Committee approval |

**Team:** 2–3 members. Cross-functional and cross-geographical encouraged.

## Timeline (12 weeks)

| Week | Date | Milestone |
|------|------|-----------|
| 1 | 17 Jun | Kickoff — track selection, team formation, mentor pairing |
| 2–3 | ~6 Jul | **Validation** — idea validation + **problem-statement brief** submitted; reviewed by GC + judge agent |
| 4–5 | 6 Jul → | Build Sprint 1 (initial development) |
| 6 | 20 Jul | **Demo 1** (GC + mentor + judge agent) |
| 7–8 | | Build Sprint 2 (feature development) |
| 9 | 10 Aug | **Demo 2** (GC + mentor + judge agent) |
| 10 | 17 Aug | Refine demo + deck; **one-pagers due** |
| 11 | 24 Aug | Final dry run |
| 12 | 7 Sep | **Finals Day** — top-5 teams present, live judging (New Delhi, US joins virtually) |

**Top 5** shortlisted by GC + judge agent go to finals. **We are at the Weeks 2–3 checkpoint now.**

## Required deliverables

1. **1–2 page brief (Wk 2–3):** problem statement, proposed solution, target user/client, sprint plan.
2. **Prototype (Wk 4–10):** functional prototype, code in **AWS CodeCommit**, reproducible setup + setup/usage docs.
3. **One-pagers (Wk 10):** (a) client-ready use case/impact; (b) internal accuracy/cost/latency summary; (c) implementation spec / path-to-production.
4. **Social content:** 1-min use-case video; 1–2 sentences on what was built/learned; 3–5 sentence use-case summary; behind-the-scenes photos.

## Engineering operating model (this is scored)

1. **Problem framing** — clear statement, target user, **success metrics**, owner, **JIRA backlog**.
2. **Build discipline** — AWS CodeCommit, meaningful commits + PRs, JIRA sprint tracking.
3. **Evidence of readiness** — accuracy, cost, latency, **eval approach**, path-to-production.
4. **Evidence of reproducibility** — setup works on a fresh machine from `README.md`.

## Rules & guardrails

- All IP belongs to Zenon.
- External APIs (OpenAI, Anthropic, …) allowed; Zenon provides keys with **budget limits** → cost efficiency matters.
- **No confidential client data** in demos — **synthetic or anonymized only**. (Deck flags "develop synthetic data — approach for this" as an open need.)
- Original work created in the competition window.
- Team name must resonate with the use case; portrait + group photos required.

## Judging rubric (memorize this)

| Criterion | Weight | What it rewards |
|-----------|-------:|-----------------|
| **Zenon impact** (revenue potential / time savings) | **25%** | A hard, quantified $ or hours-saved story |
| **Technical depth & innovation** | **25%** | Real agentic design (planning, tools, memory, eval), not a prompt |
| **Feasibility & production readiness** | **25%** | Shippable in the window; clear path to production; runs on synthetic data |
| **Originality** | **15%** | Differentiation from off-the-shelf tools |
| **Presentation quality + social media** | **10%** | Crisp demo + polished narrative/video |

Panel: **3 human judges + 1 AI judge**; the AI judge focuses on **engineering quality**. Genesis Committee (GC): Novnit Kashyap, Riya Gupta, Priyesh Kumar, Suyash Baderiya.

## Implications for idea selection

- Optimize for the **75%** (impact + depth + feasibility) first; treat originality/presentation as tie-breakers.
- The AI judge scores engineering quality → clean repo, evals, cost/latency tables, reproducible README are worth real points.
- **Synthetic-data-friendly** ideas have a structural advantage (no data-access blockers, safe to demo).
- Cost matters (budget-limited API keys) → design for token efficiency and be ready to show a cost table.
