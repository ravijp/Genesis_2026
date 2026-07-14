# Genesis 2026 — Project Instructions

Read `INDEX.md` first for the current file map. Keep INDEX.md updated **in the same commit** whenever files are added, moved, or removed.

## Mission

Zenon Genesis 2026 competition, **Track A: client-facing agentic AI**. Official judging: Zenon impact 25 / technical depth 25 / feasibility & production readiness 25 / originality 15 / presentation 10, plus an AI judge scoring engineering quality (evals, reproducibility, accuracy/cost/latency evidence). Phases and gates live in `PLAN.md`.

## Python environment (uv)

- Managed by **uv** (Python 3.13, pinned in `.python-version`). First-time setup: `uv sync`
- Run anything: `uv run python <script>` · `uv run pytest` · `uv run ruff check .`
- Add dependencies: `uv add <pkg>` (runtime) · `uv add --group dev <pkg>` (dev-only)
- Never `pip install` into the venv directly. Always commit `pyproject.toml` + `uv.lock` together.

## Working rules

- **Citations:** every non-obvious research claim gets an inline source + date. Absolute dates only ("2026-07-14", never "recently"). Prefer primary sources.
- **Bias containment:** do NOT load content from the `igupta/ideation-and-research` branch into ideation context before the Round-1 idea lock (rule defined in `02_ideas/METHOD.md`). Lessons from that work live in `01_research/lessons-from-prior-work.md`; that file is the only sanctioned channel.
- **Ideas:** follow the card template in `02_ideas/METHOD.md`; score only with `02_ideas/RUBRIC.md`. Ideas that fail the anti-slop gate don't get scored — they get killed or reworked.
- **Data:** synthetic or anonymized only, competition rule. Synthetic datasets need seeded ground truth so agent performance is measurable.
- **Subagent tiering:** opus = deep research, judging, scrutiny · sonnet = scoped research, extraction · haiku = mechanical aggregation and formatting.
- **RTK is NOT installed on this machine.** The global CLAUDE.md's `rtk` guidance does not apply in this repo — use plain `git`, `gh`, etc.
