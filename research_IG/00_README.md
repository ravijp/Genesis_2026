# Research Sweep — Genesis 2026 (`research_IG/`)

**Date:** 13 Jul 2026 · **Owner:** Ishant Gupta · **Purpose:** a time-boxed, decision-oriented market/domain research sweep that maximizes **net-new Track A candidate ideas (I11+)** for Genesis 2026, building on (not duplicating) `ideation_IG/`. Output feeds the Weeks 2–3 problem-statement brief.

## Method

Six workstreams: **WS1–WS5 ran as parallel web-research agents** (Claude Sonnet — breadth, citations), each ending with concrete candidate ideas; **WS6 ran as a synthesis agent** (Claude Fable — judgment, de-dup, scoring) that consolidates everything into one tagged, ranked catalog.

| File | Workstream | Angle |
|------|-----------|-------|
| [01_startup_funding_landscape.md](01_startup_funding_landscape.md) | WS1 | Agentic-AI startups & funding in finance (2024–2026) — read as *demand signal + white space + crowded-to-avoid*, not a copy list |
| [02_opensource_and_frameworks.md](02_opensource_and_frameworks.md) | WS2 | Agentic frameworks + open finance/analytics projects — a **feasibility booster** for a 2–3 person, 6-week build |
| [03_domain_painpoints.md](03_domain_painpoints.md) | WS3 | Pain points by banking division (Retail, Loan, Commercial data, Fraud, AML) + Zenon-adjacent domains |
| [04_regtech_governance.md](04_regtech_governance.md) | WS4 | RegTech / cross-jurisdiction governance & compliance (the whiteboard seed) |
| [05_future_roadmaps.md](05_future_roadmaps.md) | WS5 | Where banks/finance say agentic AI is going (2025–2026 roadmaps, exec/analyst views) |
| [06_idea_catalog.md](06_idea_catalog.md) | WS6 | **The payoff** — consolidated, de-duped, scored, tagged Track A idea catalog, IDs from **I11** |
| [07_gaps_and_open_questions.md](07_gaps_and_open_questions.md) | — | What research couldn't answer, contradictions, and the ideas worth a deeper dive |

## Locked decisions

- **Goal:** maximize net-new ideas (I11+); only light de-dup vs I1–I10 — no re-validation of the existing shortlist.
- **Track focus:** **A — client-facing.** Stray Track B/C ideas are logged and labeled, not the target.
- **Scope:** finance only, broad within it — subscription/media, banking & credit, payments, asset management, plus banking divisions (Retail, Loan, Commercial data, Fraud, AML).

## Per-idea schema (every entry, so 50 ideas stay comparable)

`ID · Name · One-liner · Track · Zenon anchor · Target user/client · The pain · Why it's agentic · Synthetic-data viability · 6-wk feasibility · Market/competition (incumbents, funded players, OSS) · White-space/originality · Rubric quick-score (ZI/TD/FR/OR/PR, weights 25/25/25/15/10) · Tags · Sources (URL + date)`

## Tag definitions (applied consistently by all agents)

- **`[Align with Zenon]`** — rides Zenon's demonstrated DNA (forecasting, credit-risk/collections, DQ/reconciliation, reporting), a named client domain (Dow Jones / Barclays / Visa / Invesco), or a structural edge (synthetic-data generation, validation/QC discipline, business-rules+ML hybrid). I.e., *Zenon can pitch it more credibly than a generic team.*
- **`[Recommended]`** — passes **all five hard filters** *and* scores ≥4 on each of the 75%-core dimensions (Zenon impact, technical depth, feasibility). A genuine contender for the pitch.

**Hard filters** (all must pass): genuinely agentic (planning/tools/memory/multi-step, not a prompt wrapper) · synthetic-data-demoable · buildable in ~6 weeks by 2–3 people · named target user/client + movable metric ($ or hours) · runs on AWS + budget-capped external LLM APIs.

## Source-credibility bar

Every non-obvious market/funding/roadmap claim carries a **dated URL**; funding and roadmap sources must be **2024–2026** (prefer 2025–2026). Prefer primary sources: company/funding announcements, official docs and repos, regulator publications, bank statements/earnings calls, named analyst reports. Unverifiable claims are flagged, not asserted.

## Reused inputs (not duplicated here)

`ideation_IG/01_competition_brief.md` (rubric), `02_zenon_capabilities.md` (the Zenon lens), `03_ideation_framework.md` (scoring), `04_idea_candidates.md` + `05_shortlist_and_recommendation.md` (existing I1–I10 that this sweep extends and challenges).
