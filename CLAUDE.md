# Genesis 2026 — Project Instructions (branch `build/ear-on-every-call`)

## RESUME THE BUILD — do this before anything else

The build is a relay across conversations. The file below is the baton and it is **imported here, so
you already have it** — no one needs to paste anything.

@docs/ops/handover.md

**On your first turn in a new conversation, without being asked:** state in two lines where the build
stands and what the next action is, from that file. Then start it. Do not re-derive the plan, do not
re-explore what `progress.md` already records, and do not ask permission to continue work that is
already the agreed next action.

If the import above did not resolve, read `docs/ops/handover.md` yourself — that is the failure mode to
check first, before assuming there is no plan.

**You are the orchestrator. Delegate implementation; do not write it yourself.** Subagents write code
and do research; you judge, review, decide, and hold the thread. Tier them: opus for judging and
adversarial review, sonnet for scoped implementation, haiku for mechanical formatting. Do not spawn an
agent for work that is cheaper done directly.

**Any agent that WRITES FILES must get `isolation: "worktree"`.** Two agents sharing one tree is a
corruption hazard, not a theoretical one: on 2026-08-25 two implementation agents ran concurrently
here, one ran `git stash -u` to get a clean test baseline, and it wiped the other's three
half-written files back to HEAD. Both happened to recover. Read-only agents (Explore, research,
review) can share the tree safely. After a worktree agent finishes, review its diff before merging —
isolation prevents collisions, it does not make the work correct.

**Commit as soon as a unit of work verifies.** Uncommitted work is the only work that can be lost.

**Watch your own context and call the handover.** Say so unprompted at the first of: context above
~50% (quality degrades before the limit, not at it) · the next task is a large multi-file
implementation · a commit just landed and the next unit is independent. To hand over: rewrite
`handover.md` in place, append a line to `progress.md`, commit. The next conversation then resumes from
the import above with no action from Ravi.

Read `docs/INDEX.md` for the current file map. Keep it updated **in the same commit** whenever
files are added, moved, or removed.

## Mission

Zenon Genesis 2026 competition, **Track A: client-facing agentic AI**. The entry is **Ear on Every
Call** — a conversation signal layer that reads 100% of a bank's customer conversations and accumulates
them into a standing per-customer ledger that re-scores as new conversations arrive.

The finalized idea was submitted to the Genesis Committee on 2026-07-24 and is the contract:
`docs/sources/submission-ear-on-every-call.md`. `docs/architecture/architecture.md` describes the system;
`docs/architecture/build-plan.md` (v3) covers what is left to build, what is measured and what is not,
and the deltas from the submitted brief.

Sprint backlog: JIRA project **AT (Agentic Trio)** at `https://zenonai.atlassian.net`.

Official judging: Zenon impact 25 / technical depth 25 / feasibility & production readiness 25 /
originality 15 / presentation 10, plus an AI judge scoring engineering quality (evals, reproducibility,
accuracy/cost/latency evidence).

Frozen gates: **2026-08-10** 15-min check-in · **2026-08-24** combined Sprint 1+2 demo ·
**2026-09-07** Sprint 3 demo. Details in `docs/sources/genesis-committee-comms.md`.

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

## Starting a fresh session — read these, in this order

0. **`docs/ops/handover.md`** — already imported at the top of this file. The next action lives there.
   `docs/ops/progress.md` is its companion: work-package status and blockers with owners.
1. **`docs/ops/state-of-play.md`** — where we are right now, what is in flight, what is blocked, the
   next three things. One screen, rewritten in place each session, never appended to.
2. **`docs/ops/decisions.md`** — why things are the way they are, and what was rejected. Read this
   before arguing for something; it exists so settled ground is not re-litigated.
3. **`docs/ops/working-agreements.md`** — the disciplines, each one bought with a real mistake.
4. **`README.md`** — what the thing is, and the current numbers.

Then `docs/architecture/architecture.md` for the shape of the system, and
`docs/architecture/build-plan.md` for what is left to build and what is still open.

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

## How to write

Plain English. Short sentences. Active voice. The test: can Ravi skim it in 30 seconds and act?

**Do:**

- Lead with the answer. Then the reason.
- One idea per sentence. Tables and lists beat paragraphs when the content is a set of facts.
- Every number carries its denominator (`4 / 112`, not "3.5%"). Every date is absolute (`2026-08-25`).
- Say what broke, what we lost, what is still unproven. A stated loss buys more credit than a clean sweep.
- Code comments explain **why**. The code already shows what.

**Don't:**

- No fluff openers, no restating the question, no "Certainly".
- No hedging to sound careful. "Unproven" beats "may potentially not fully hold".
- No bold on every third phrase. If everything is emphasised, nothing is.
- **Don't cut the *why* to save words.** Dense is the goal, not short. This repo's value is its recorded
  reasoning — `decisions.md` exists so settled ground is not re-argued. A doc that drops the trade-off
  costs an hour later. Compress the prose, never the content.

## Files: what to maintain, what to ask about

Prefer editing an existing file over adding one. A new `.md` needs a reason. Delete stale content
instead of leaving it — git remembers.

**Maintain freely** — keep current, rewrite, prune, no need to ask:

- `docs/INDEX.md` · `docs/ops/state-of-play.md` · `docs/ops/aws-infrastructure.md`
- `README.md` numbers, when a run produces new ones
- anything created in the current session

**Ask first** — one line on what and why, then wait:

- `docs/ops/decisions.md` — append only. Never rewrite or delete an entry; supersede it.
- `docs/ops/working-agreements.md` — every rule there was bought with a real mistake.
- `CLAUDE.md` · `docs/architecture/*.md` · `benchmarks/*/PROTOCOL.md` (pre-registered)

**Never edit:** `docs/sources/` — the committee contract and competition rules. Not ours. It sits inside
`docs/` for a tidy repo root (D-023), but the edit boundary is unchanged: everything else under `docs/`
is ours to rewrite, that folder is not.
