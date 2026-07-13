# Genesis 2026 — Track A: Client-Facing Agentic AI

**Mission:** win Zenon's Genesis 2026 GenAI competition with a client-facing agentic AI system that is real enough to walk into a named client as a POC the week after finals.

## The competition (from the official kickoff deck — details in [00_sources/kickoff-notes.md](00_sources/kickoff-notes.md))

- **Track A "Client Facing Solutions"** — agentic AI workflows that solve real client problems, shipped client-ready
- 12-week program: June 17 → **Sept 7, 2026 finals** (New Delhi); teams of 2–3
- **Judging:** Zenon impact 25% · technical depth & innovation 25% · feasibility & production readiness 25% · originality 15% · presentation + social 10% — 3 human judges + an **AI judge scoring engineering quality**
- Rules: synthetic/anonymized data only, Anthropic/OpenAI APIs allowed (Zenon keys), AWS CodeCommit + JIRA discipline, reproducible setup required

## Repo map

| Path | What lives here |
|---|---|
| `INDEX.md` | Machine-readable file map — the first thing an LLM session should read |
| `PLAN.md` | Master plan: phases, gates, operating model, decision log, risks |
| `CLAUDE.md` | Session instructions: uv env, conventions, bias-containment rules |
| `00_sources/` | Primary inputs: kickoff deck + notes, LinkedIn corpus, client context |
| `01_research/` | July-2026 research briefs: agentic AI landscape, finance, pharma, media, retail, startups, lessons from prior attempt |
| `02_ideas/` | Ideation machinery: METHOD (how we get to 50+ non-slop ideas), RUBRIC (how we judge), backlog |
| `03_selection/` | Scoring runs, top-10 diligence, top-3 decision memo *(created when phase opens)* |
| `04_architecture/` | Competition build design *(created when phase opens)* |
| `05_build/` | MVP source *(created when phase opens)* |

## How we work

- **Trunk-based:** `main` is the single source of truth; every working session commits progress here
- **INDEX.md discipline:** any commit that adds/moves/removes files updates INDEX.md in the same commit
- **Evidence or it didn't happen:** every research claim carries a dated source; every idea traces back to evidence
- **Anti-slop:** ideas must pass the gate in [02_ideas/METHOD.md](02_ideas/METHOD.md) before they earn a rubric score
- **Bias containment:** the prior attempt (igupta branch) enters this workspace only through the scrutinizer's lessons file; its idea list is consulted only *after* our own divergent round locks

## Python

Managed with uv: `uv sync`, then `uv run python <script>`. Conventions in [CLAUDE.md](CLAUDE.md).

## Status (2026-07-14)

Phase 1 (Research) in flight: 6-track research fleet + prior-work scrutiny landing in `01_research/`. Next: Phase 2 ideation sprint to 50+ ideas.
