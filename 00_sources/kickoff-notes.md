# Kickoff Deck — Distilled Facts

Source: `2026 Zenon Agentic AI Competition Kickoff.pdf` (official Genesis Committee deck, June 2026, 9 pages). Extracted 2026-07-14. This file is the canonical reference for competition facts — cite it, don't re-read the PDF.

## What the competition is

**"Genesis: Zenon's GenAI Competition 2026"** — kicked off June 2026. Objectives (slide 2):

1. Accelerate **Agentic AI capability** development within the firm
2. **Surface real-world solution ideas** applicable to clients and internal operations
3. Develop an AI-first, engineering-focused culture
Tagline: teams practice structured execution while producing **assets that can be pitched and shipped**.

## Tracks (slide 3) — we are Track A

- **TRACK A: Client Facing Solutions** — "Agentic AI workflows or GenAI tools that solve real client problems and can be shipped as client-ready solutions" ← our track
- TRACK B: Internal Ops & Tooling (outreach, proposal generation, knowledge mgmt)
- TRACK C: Open Category (eval frameworks, agentic optimization; committee approval required)
- Teams: **2–3 members**, cross-functional/cross-geographical encouraged

## Timeline (slide 4) — 12 weeks

| Week | Dates | Milestone |
|---|---|---|
| 1 | Jun 17 (pre-launch May 18) | Kickoff: track selection, team formation, mentor pairing |
| 2–3 | → Jul 6 | **Validation**: idea validation, problem-statement submission; review by GC + judge agent |
| 4–5 | Jul 6–20 | Build Sprint 1 |
| 6 | Jul 20 | **Demo 1** (GC + mentor + judge agent) |
| 7–8 | Jul 20–Aug 10 | Build Sprint 2 |
| 9 | Aug 10 | **Demo 2** |
| 10 | Aug 17 | Refine demo + deck |
| 11 | Aug 24 | Final dry run |
| 12 | **Sep 7** | **Finals Day** (buffer noted) |

Top 5 teams (shortlisted by GC + judge agent) reach finals. Finals = full-day event in **New Delhi**; US team joins virtually in the morning-ET window (5:30–9:00 PM IST = 8:00–11:30 AM EST: kickoff, top-5 presentations, results).

⚠️ As of 2026-07-14 we are inside Build Sprint 1 on the official calendar; Demo 1 is nominally Jul 20. Effective build budget: **~6–7 weeks**.

## Required deliverables (slide 5)

1. **1–2 page brief** (Weeks 2–3): problem statement, proposed solution, target user/client, sprint plan
2. **Functional prototype** (Weeks 4–10): code in **AWS CodeCommit**, reproducible setup, setup/usage documentation
3. **Three one-pagers** (Week 10): ① client-ready use case/impact ② internal **accuracy/cost/latency** summary ③ implementation spec: **path-to-production/client deployment**
4. **Social media content**: 1-min use-case video (Week 10), 1–2 sentences on what was built/learned, 3–5 sentence team use-case summary, behind-the-scenes photos

## Engineering operating model (slide 5)

- Problem framing: problem statement, target user, success metrics, owner, **backlog in JIRA**
- Build discipline: **CodeCommit with meaningful commits and PRs**; sprint tracking in JIRA
- **Evidence of readiness: accuracy, cost, latency, eval approach, path-to-production**
- **Evidence of reproducibility: fresh-machine setup from README.md**

## Rules & guardrails (slide 6)

1. All IP belongs to Zenon
2. External APIs (OpenAI, Anthropic, etc.) permitted — **Zenon provides API keys with budget limits**
3. **No confidential client data — synthetic or anonymized only** (deck explicitly flags "exposure to develop synthetic data" as a skill to build)
4. Original work created during the competition window
5. Team name must resonate with the use case; portrait + team photos required

## Judging (slide 8) — memorize this

**Panel: 3 human judges (internal leadership + external judges) + 1 AI judge focused on engineering quality.**

| Axis | Weight |
|---|---|
| Zenon impact (revenue potential / time savings) | **25%** |
| Technical depth & innovation | **25%** |
| Feasibility & production readiness | **25%** |
| Originality | **15%** |
| Presentation quality + social media materials | **10%** |

Strategic read: 75% of the score is impact × depth × feasibility — a *credible, well-engineered, client-anchored* system beats a flashy toy. The AI judge means repo hygiene, evals, and reproducibility literally score points. Presentation is only 10% but is the channel through which the other 90% is perceived.

## Genesis Committee (slides 4, 9)

Core: Novnit Kashyap, Riya Gupta, Priyesh Kumar, Suyash Baderiya. Planning/support: Bharti Sahai, Pooja Pandey, Abhishek Pradhan, Gennifer Niezgoda, Paula Ureta, Rohit Chhabra.
