# INDEX — repo map (branch `build/ear-on-every-call`)

> **Maintenance rule:** any commit that adds, moves, or removes a file MUST update this index in the
> same commit. One line per file: what it is + status.
> Status legend: `[stable]` authored & reviewed · `[generating]` agent currently writing ·
> `[skeleton]` structure awaiting content · `[source]` external input, do not edit.

**This branch is scoped to the build only.** The research and ideation phases (`01_research/` in full,
`02_ideas/`, `02_ideas_v2/`, `03_selection/`, `PLAN.md`, `worklogs.md`, `actions-items.md`) were pruned
on 2026-08-09 so the tree is specific to shipping *Ear on Every Call*. Nothing is lost — all of it lives
on `main` and any file is one command away: `git checkout main -- <path>`.

## Reading order for a fresh session

1. `CLAUDE.md` — session rules
2. `00_sources/submission-ear-on-every-call.md` — **the contract with the committee**
3. `00_sources/genesis-committee-comms.md` — frozen dates, access status, what each gate expects
4. `04_architecture/BUILD-PLAN.md` — the plan: wedge, the experiment, components, stages, cut list
5. `05_build/` — source

## Root

- `README.md` — human-facing charter `[needs rewrite for build phase]`
- `CLAUDE.md` — LLM session instructions `[stable]`
- `INDEX.md` — this map `[stable]`
- `pyproject.toml` / `uv.lock` / `.python-version` — uv-managed Python (3.13; pytest + ruff dev group) `[stable]`
- `.gitignore` · `.markdownlint.json` `[stable]`

## 00_sources/ — primary inputs, do not edit

- `submission-ear-on-every-call.md` — verbatim text of the finalized Track A idea submitted to the
  Genesis Committee 2026-07-24. The contract; deltas logged in BUILD-PLAN §10 `[source]`
- `genesis-committee-comms.md` — frozen sprint/demo dates (2026-08-10 check-in · 2026-08-24 combined
  S1+S2 demo · 2026-09-07 S3), how the Sprint-1 downgrade happened, what the check-in expects, tooling
  and API-access status `[source]`
- `kickoff-notes.md` — distilled competition facts: tracks, deliverables, rules, judging rubric,
  committee `[stable]`
- `zenon-client-context.md` — client roster with evidence and engagement signals; input to the
  Zenon-impact narrative `[stable]`
- `2026 Zenon Agentic AI Competition Kickoff.pdf` — official GC kickoff deck `[source]`

## 01_research/ — retained grounding only

Two briefs kept because they feed the Zenon-impact axis (BUILD-PLAN §9); the rest of the research phase
is on `main`.

- `finance.md` — finance value-chain deep dive: collections, HOA bank-side ops, SMB virtual RM,
  disputes, wealth; fact-checked ROI table with withdrawn-claims log `[stable]`
- `client-ai-state-map.md` — per-client AI-adoption states (S0-S3) with dated evidence and engagement
  signals `[stable]`

## 04_architecture/ — build design

- `BUILD-PLAN.md` — **the anchor document.** v2 after three adversarial reviews. Contains: the reworded
  wedge (the submitted novelty sentence is refuted by Twilio Conversation Memory, GA 2026-05-06) ·
  rubric→artifact map · the four-arm experiment with equal-alert-budget equalisation, negative controls
  and uncertainty quantification · 9 design rules · 8 components · re-cut build stages · the Aug-24
  minimum demo and cut list · risk table · Zenon-impact gap · deltas-from-submission log
  `[v2 2026-08-09, stable]`

- `SPRINT-1-CHECKIN.md` — brief for the 2026-08-10 committee check-in: committed-vs-completed table,
  the week-one finding (the thesis does not yet hold at portfolio level — ledger wins the diffuse
  stratum 0.191 vs 0.143 but loses overall 0.128 vs 0.154, and a dumb sum matches the full ledger),
  the Twilio novelty collision and the narrower claim, the API-access roadblock with a date-certain
  ask, and the path to 2026-08-24 `[2026-08-09]`

## 05_build/ — MVP source

Runs with **zero API keys**. `uv run pytest` · `$env:PYTHONPATH="05_build"; uv run python -m ear.cli run`
· `... ear.cli demo`

- `ear/schema.py` — core types. `SeededSignal` (answer key) and `ExtractedSignal` (belief) are
  deliberately separate types so nothing can confuse one for the other. `LedgerEntry` carries the
  retro-re-score fields and `is_load_bearing()` `[stable]`
- `ear/config.py` — every tunable parameter; nothing magic in logic modules. Carries the recorded
  finding that saturation cannot affect equal-budget rankings `[stable]`
- `ear/corpus_lexicon.py` — **authoring pass A**: the utterance fragments that get planted `[stable]`
- `ear/extract_lexicon.py` — **authoring pass B**: extractor cues, written without reference to pass A.
  The partial overlap is the source of the honest miss rate — do not "fix" it `[stable]`
- `ear/corpus.py` — generator. Strata are labelled from Dirichlet generation parameters, never from
  what a baseline can detect; outcomes drawn stochastically from latent risk `[stable]`
- `ear/extract.py` — stateless extraction + the offline lexicon provider. Cannot import the corpus
  side `[stable]`
- `ear/memory.py` — **the heart**: append-only ledger + pure-code re-scorer with decay, corroboration,
  cross-channel, escalation, and retro re-scoring `[stable]`
- `ear/arms.py` — the four (now five) comparison arms sharing one code path: stateless-max ·
  dumb-ledger · long-context-10 · full-ledger · hybrid, plus per-mechanism ablations `[stable]`
- `ear/evals.py` — true equal-alert-budget comparison (top-K ranking, not quantile thresholds),
  per-stratum breakdown, lead-time survival, extraction fidelity, corpus diagnostics `[stable]`
- `ear/cli.py` — `run` and `demo`, run manifest, results artifacts `[stable]`
- `tests/test_separation.py` — **the honesty guard**: AST-level proof that the extractor cannot see the
  answer key, plus an assertion that it is measurably imperfect. Do not relax `[stable]`
- `tests/test_memory.py` — ledger invariants: never-discard, accumulation, retro re-score, decay,
  determinism, and the super-additivity/concavity interaction `[stable]`
- `results/` — per-run JSON artifacts with manifests `[generated]`
