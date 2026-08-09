# INDEX — repo map (branch `build/ear-on-every-call`)

> **Maintenance rule:** any commit that adds, moves, or removes a file MUST update this index in the
> same commit. One line per file: what it is + status.
> Status legend: `[stable]` authored & reviewed · `[skeleton]` structure awaiting content ·
> `[source]` external input, do not edit · `[generated]` produced by a command, never hand-edited.
>
> *Broken by three commits on 2026-08-09, including the one that added the conventions documents.
> Run `git show --stat` against this file before committing.*

**This branch is scoped to the build.** The research and ideation phases were pruned 2026-08-09 and the
build promoted to a `src/` layout. Nothing is lost — all of it is on `main`:
`git checkout main -- <path>`.

## Reading order for a fresh session

1. `docs/ops/state-of-play.md` — **start here.** Current state, in one screen
2. `docs/ops/decisions.md` — what is settled and what was rejected
3. `docs/ops/working-agreements.md` — the disciplines, each bought with a mistake
4. `README.md` — what this is, and the current numbers
5. `docs/architecture/architecture.md` — the shape of the system, with diagrams

## Root

- `README.md` — front door: quick start, the numbers with their denominators, model access, repo map `[stable]`
- `CLAUDE.md` — LLM session instructions and the load-bearing build rules `[stable]`
- `INDEX.md` — this map `[stable]`
- `pyproject.toml` / `uv.lock` / `.python-version` — uv-managed Python 3.13, hatchling build, `earshot` installed editable, console script `earshot` `[stable]`
- `.env.example` — every `EARSHOT_*` variable with dummy values; the real `.env` is gitignored `[stable]`
- `.gitignore` — ignores regenerable output and secrets; deliberately KEEPS `artifacts/cache/` and `artifacts/runs/pinned/` tracked so a judge can replay without keys `[stable]`
- `.markdownlint.json` `[stable]`

## src/earshot/ — the product

Commands: `earshot sweep` (the only source of quotable numbers) · `earshot demo` · `earshot investigate` · `earshot run` (single dataset, debugging only)

- `schema.py` — core types. `SeededSignal` (answer key) and `ExtractedSignal` (belief) are separate types on purpose. `CustomerTruth` keeps `latent_risk` and `financial_state` apart `[stable]`
- `config.py` — every tunable parameter; records that saturation cannot affect equal-budget rankings `[stable]`
- `corpus_lexicon.py` — **authoring pass A**: the utterance fragments that get planted `[stable]`
- `extract_lexicon.py` — **authoring pass B**: extractor cues, authored without reference to pass A. The partial overlap is the source of the honest miss rate — do not "fix" it `[stable]`
- `corpus.py` — dataset generation. Strata labelled from generation parameters; outcomes drawn from latent risk `[stable]`
- `extract.py` — stateless extraction + the offline lexicon provider `[stable]`
- `memory.py` — **the heart**: append-only ledger + pure-code re-scorer. `score()` returns copies and never mutates the ledger `[stable]`
- `arms.py` — six comparison arms through one code path + per-mechanism ablations. `stateless-top2` is the strongest fair per-call baseline and currently matches the ledger `[stable]`
- `evals.py` — equal-alert-budget comparison by top-K ranking, per-stratum breakdown, extraction fidelity, corpus diagnostics `[stable]`
- `sweep.py` — **multi-seed evaluation**: paired seed-by-seed comparison on any metric, exact sign test, and the integers behind every rate `[stable]`
- `cli.py` — the four commands, run manifests, artifacts `[stable]`
- `__init__.py` (package root, and in `agent/`, `core/`, `llm/`) — package markers; all are covered by the separation guard `[stable]`
- `core/accounts.py` — synthetic account state and transactions behind the agent's tools. Derives from `(customer_id, financial_state, seed, as_of_day)` and **never** from a truth object `[stable]`
- `agent/schemas.py` · `tools.py` · `investigator.py` · `prompts.py` — the investigator: strict decision schema with mandatory evidence, five pure tools, a bounded loop, versioned prompt loading `[stable]`
- `llm/base.py` · `openrouter.py` · `offline.py` · `cache.py` — provider abstraction, cost and latency capture, content-addressed response cache with record/replay `[stable]`

## tests/

- `test_separation.py` — **import guard**: nothing on the decision path may import the generator, its lexicon, or a ground-truth type. Discovers its own surface by glob `[stable]`
- `test_no_answer_key_leak.py` — **data guard**: nothing may receive a value that *encodes* a ground-truth field. The one that would have caught the leak we actually had `[stable]`
- `test_memory.py` — ledger invariants: never-discard, accumulation, retro re-score, decay, determinism `[stable]`
- `test_tools.py` — every agent tool, in-memory, no network `[stable]`
- `test_no_answer_key_leak.py` — also discovers `AccountSnapshot`'s numeric fields rather than listing them; a hand-written list named a field that did not exist and silently skipped `[stable]`
- `test_agent.py` — decision schema, bounded loop, the cost cap holding under a rising cost curve (and the documented spike case where it cannot), a crashing tool being contained `[stable]`
- `test_sweep.py` — the multi-seed harness: sign test vs hand computation, pairing on seed, denominators present and identical across arms, equal alert budget, determinism, counted-not-reconstructed integers, artifact reproducibility `[stable]`
- `test_cli.py` — the commands, and the demo's internal consistency: its narration may not contradict the claim it selected on, and its denominator must count customers `[stable]`

## benchmarks/cfpb/ — AT-43, the extractor on real complaint narratives

Self-contained and replicable end to end: pre-registration, marking guide, one script per step, every
API call and output hash logged. Run `steps/05_score.py` alone to reproduce the numbers offline.

- `README.md` — how to replicate, in order; what is in the folder; data provenance and licence `[stable]`
- `PROTOCOL.md` — **the pre-registration**, frozen before any narrative was read: frame, panels, wrapping rule, interpretation thresholds, freeze rules, and an amendment log `[stable]`
- `MARKING-GUIDE.md` — how a narrative is marked, derived from the construct definitions and never from the extractor's cues `[stable]`
- `RUNLOG.md` — append-only log of every run: command, date, counts, output SHA-256. Corrections are appended, never edited in `[generated]`
- `steps/_common.py` — API client with logging, the frame constants, hashing, run log `[stable]`
- `steps/01_frame.py` — frame counts via the search API; now an independent cross-check of the archive `[stable]`
- `steps/02_download.py` — the bulk archive (~1.3 GB), verified by size and SHA-256, stored outside the repo `[stable]`
- `steps/03_filter.py` — streams the archive into the 2025 retail-banking frame; fails if it disagrees with the API total `[stable]`
- `steps/04_draw.py` — seeded, exactly uniform draw of Panel A and Panel B from the local frame `[stable]`
- `steps/05_score.py` — the unmodified extractor against the gold marks; offline, no keys `[stable]`
- `steps/mark.py` — the marking tool: shows documents with panel/stratum withheld, validates a mark set (every positive mark's span must appear verbatim in its narrative), picks the second-marker subset from the seed, and reports Cohen's kappa `[stable]`
- `out/` — committed: frame counts, the drawn sample, the gold marks, the results `[generated]`

## tools/jira/

- `adf.py` — renders a markdown subset into Atlassian Document Format so descriptions are readable `[stable]`
- `client.py` — minimal Jira client that records and reports every failure `[stable]`
- `apply_standards.py` — board content for every issue, in one reviewable place `[stable]`

## prompts/

- `investigator/v1/system.md` · `task.md` — prompts as versioned files, so a change is a reviewable diff `[stable]`

## docs/

- `ops/state-of-play.md` — **the boot file.** Where we are, what is in flight, what is blocked, the next three things. One screen, rewritten in place, never appended `[stable]`
- `ops/decisions.md` — why things are the way they are and what was rejected, so a fresh session does not re-litigate settled ground `[stable]`
- `ops/working-agreements.md` — **read before changing anything.** Evaluation discipline, the two-level answer-key guards, demo honesty, keeping docs in step with code, test discipline, bulk-operation discipline, delegation `[stable]`
- `ops/jira-conventions.md` — how the AT board is written and updated `[stable]`
- `architecture/architecture.md` — the shape of the system: three layers, data flow, agent loop, runtime, what is measured `[stable]`
- `architecture/build-plan.md` — **v3.** What is left to build and what is still open: the agent layer, what is measured vs not, four open questions, the 08-24 scope, risks, and the deltas from the submitted brief `[stable]`
- `gates/2026-08-10-sprint-1-checkin.md` — Sprint 1 check-in brief `[stable]`
- `gates/committee-requirements-email.md` — tooling/access email, to send after the 2026-08-10 call `[stable]`
- `impact/finance-brief.md` — finance value-chain research; feeds the Zenon-impact axis `[stable]`

## artifacts/

- `runs/pinned/` — one committed run + manifest `[generated]`
- `cache/investigator-demo.jsonl` — committed model responses so the demo replays with no keys `[generated]`
- `runs/` (unpinned) — per-run output, gitignored `[generated]`

## sources/ — primary inputs, do not edit

- `submission-ear-on-every-call.md` — verbatim finalized Track A idea sent to the committee 2026-07-24 `[source]`
- `genesis-committee-comms.md` — frozen gate dates, the Sprint-1 downgrade, tooling status `[source]`
- `kickoff-notes.md` — competition facts: tracks, deliverables, rules, judging rubric `[stable]`
- `zenon-client-context.md` — client roster; input to the Zenon-impact narrative `[stable]`
- `2026 Zenon Agentic AI Competition Kickoff.pdf` — official kickoff deck `[source]`

## Tracked elsewhere

Sprint backlog: JIRA project **AT (Agentic Trio)**, `https://zenonai.atlassian.net` — 8 epics, 37 live
tasks. Issues prefixed `[DELETE ME]` are dead and await a project admin. AWS CodeCommit is not yet
provisioned.
