# Genesis 2026 — Project Instructions (branch `build/ear-on-every-call`)

Read `INDEX.md` first for the current file map. Keep INDEX.md updated **in the same commit** whenever
files are added, moved, or removed.

## Mission

Zenon Genesis 2026 competition, **Track A: client-facing agentic AI**. The entry is **Ear on Every
Call** — a conversation signal layer that reads 100% of a bank's customer conversations and accumulates
them into a standing per-customer ledger that re-scores as new conversations arrive.

The finalized idea was submitted to the Genesis Committee on 2026-07-24 and is the contract:
`sources/submission-ear-on-every-call.md`. `docs/architecture/architecture.md` is the authoritative description of
the system. `docs/architecture/build-plan.md` is **stale** — it predates the agent layer and
contradicts the code in several places; do not cite it until it is rewritten.

Sprint backlog: JIRA project **AT (Agentic Trio)** at `https://zenonai.atlassian.net`.

Official judging: Zenon impact 25 / technical depth 25 / feasibility & production readiness 25 /
originality 15 / presentation 10, plus an AI judge scoring engineering quality (evals, reproducibility,
accuracy/cost/latency evidence).

Frozen gates: **2026-08-10** 15-min check-in · **2026-08-24** combined Sprint 1+2 demo ·
**2026-09-07** Sprint 3 demo. Details in `sources/genesis-committee-comms.md`.

## Python environment (uv)

- Managed by **uv** (Python 3.13, pinned in `.python-version`). First-time setup: `uv sync`
- The package lives at `src/earshot/` and is installed **editable**, so there is no `PYTHONPATH` hack and
  tests import the installed package. That is what makes the fresh-machine claim true rather than
  asserted — do not reintroduce path manipulation.
- Commands: `uv run pytest` · `uv run ruff check src tests tools` · **`uv run earshot sweep`** (the only
  source of quotable numbers) · `uv run earshot demo` · `uv run earshot investigate` ·
  `uv run earshot run` (one dataset, debugging only)
- Add dependencies: `uv add <pkg>` (runtime) · `uv add --group dev <pkg>` (dev-only)
- Never `pip install` into the venv directly. Always commit `pyproject.toml` + `uv.lock` together.

## Starting a fresh session — read these four, in this order

1. **`docs/ops/state-of-play.md`** — where we are right now, what is in flight, what is blocked, the
   next three things. One screen, rewritten in place each session, never appended to.
2. **`docs/ops/decisions.md`** — why things are the way they are, and what was rejected. Read this
   before arguing for something; it exists so settled ground is not re-litigated.
3. **`docs/ops/working-agreements.md`** — the disciplines, each one bought with a real mistake.
4. **`README.md`** — what the thing is, and the current numbers.

Then `docs/architecture/architecture.md` for the shape of the system. **Do not read
`docs/architecture/build-plan.md`** — it predates the agent layer and contradicts the code.

Session history is in git, deliberately: commit messages carry the *why*. `git log --grep` answers
"did we already try X?" better than any prose file, and it never needs curating.

**When you finish a working session:** rewrite `state-of-play.md` (do not append), add any new decision
to `decisions.md`, and add a rule to `working-agreements.md` if a mistake taught you one.

## Read before changing anything

**`docs/ops/working-agreements.md`** — the disciplines this project learned the hard way: evaluation
(never publish from one dataset, always show denominators), the two-level answer-key guards, demo
honesty, keeping documents and code in step, tests that assert properties rather than labels, and bulk
-operation discipline. Every rule there was bought with a real mistake.

**`docs/ops/jira-conventions.md`** — how the AT board is written and updated. Use `tools/jira/`
rather than hand-building Atlassian Document Format.

## Architecture in one line

**Code counts and remembers. The model reads and judges.** Accumulation, decay and thresholds are
deterministic Python in `corpus.py` and `memory.py`; weighing ambiguous evidence is the agent's job in
`src/earshot/agent/`. See `docs/architecture/architecture.md`.

## Build rules — load-bearing, not style preferences

- **Ground truth is authored before the text.** Deterministic code builds the plan; generation only
  writes prose around it. The answer key never comes from a model.
- **The re-scoring math is plain code, never the model.** Deterministic, unit-tested, reproducible.
- **Never discard a sub-threshold signal.** This is the design inversion the entry's originality rests
  on — incumbents reconcile to current truth, we accumulate.
- **Retro re-scoring must be observable**, not asserted: the ledger records what a prior conversation
  scored *then* and scores *now*.
- **Provider and corpus stay mechanically separated.** The offline extractor has its own lexicon and
  **must not be able to import the ground-truth plan** — there is a test asserting this. Never weaken it.
- **Everything runs with zero API keys.** Offline numbers are always labelled with their provider and
  never presented as a headline.
- **Nothing is published from a single dataset.** `earshot sweep` produces quotable numbers; `earshot
  run` is for debugging and says so itself. Every rate is quoted with its denominator.
- **No outbound contact surface exists anywhere in the system.** HITL is enforced by absence.
- **Don't drift toward detection.** Single-call signal detection is commodity and this idea was already
  judged a loser in that framing. Every demo beat and headline number is about accumulation and retro
  re-scoring.

## Working rules

- **Citations:** every non-obvious claim gets an inline source + date. Absolute dates only
  ("2026-07-14", never "recently"). Prefer primary sources.
- **Data:** synthetic or anonymized only, competition rule. Synthetic datasets need seeded ground truth
  so agent performance is measurable.
- **Honest numbers:** report the strata and arms where we lose or tie, not just where we win. A stated
  loss buys more technical-depth credit than a clean sweep.
- **Subagent tiering:** opus = judging, scrutiny, adversarial review · sonnet = scoped research,
  extraction · haiku = mechanical aggregation and formatting. Don't spawn agents for work that is
  cheaper done directly.
- **RTK is NOT installed on this machine.** The global CLAUDE.md's `rtk` guidance does not apply in this
  repo — use plain `git`, `gh`, etc.
