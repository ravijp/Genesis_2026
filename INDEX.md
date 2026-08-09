# INDEX — repo map (branch `build/ear-on-every-call`)

> **Maintenance rule:** any commit that adds, moves, or removes a file MUST update this index in the
> same commit. One line per file: what it is + status.
> Status legend: `[stable]` authored & reviewed · `[skeleton]` structure awaiting content ·
> `[source]` external input, do not edit · `[generated]` produced by a command, never hand-edited.

**This branch is scoped to the build.** The research and ideation phases (`02_ideas/`, `02_ideas_v2/`,
`03_selection/`, most of `01_research/`, `PLAN.md`, `worklogs.md`, `actions-items.md`) were pruned
2026-08-09 and the build was promoted to a `src/` layout 2026-08-09. Nothing is lost — all of it is on
`main`: `git checkout main -- <path>`.

## Reading order for a fresh session

1. `README.md` — what this is, and the fresh-machine quick start
2. `CLAUDE.md` — session rules and the build rules that must not be weakened
3. `docs/architecture/architecture.md` — the shape of the system, with diagrams
4. `sources/submission-ear-on-every-call.md` — **the contract with the committee**
5. `docs/architecture/build-plan.md` — the plan of record

## Root

- `README.md` — front door: quick start, what it does, the honest state of the numbers, model access, repo map `[stable]`
- `CLAUDE.md` — LLM session instructions + the load-bearing build rules `[stable]`
- `INDEX.md` — this map `[stable]`
- `pyproject.toml` / `uv.lock` / `.python-version` — uv-managed Python 3.13, hatchling build, `ear` installed editable, console script `ear` `[stable]`
- `.gitignore` — ignores regenerable output and secrets; deliberately KEEPS `artifacts/cache/` and `artifacts/runs/pinned/` tracked so a judge can replay without keys `[stable]`
- `.markdownlint.json` `[stable]`

## src/earshot/ — the product

- `schema.py` — core types. `SeededSignal` (answer key) and `ExtractedSignal` (belief) are separate types on purpose. `LedgerEntry` carries retro-re-score fields and `is_load_bearing()` `[stable]`
- `config.py` — every tunable parameter; records the finding that saturation cannot affect equal-budget rankings `[stable]`
- `corpus_lexicon.py` — **authoring pass A**: the utterance fragments that get planted `[stable]`
- `extract_lexicon.py` — **authoring pass B**: extractor cues, authored without reference to pass A. The partial overlap is the source of the honest miss rate — do not "fix" it `[stable]`
- `corpus.py` — generator. Strata labelled from Dirichlet generation parameters, never from what a baseline can detect; outcomes drawn stochastically from latent risk `[stable]`
- `extract.py` — stateless extraction + the offline lexicon provider `[stable]`
- `memory.py` — **the heart**: append-only ledger + pure-code re-scorer (decay, corroboration, cross-channel, escalation, retro re-scoring) `[stable]`
- `arms.py` — five comparison arms through one code path + per-mechanism ablations `[stable]`
- `evals.py` — true equal-alert-budget comparison, per-stratum breakdown, extraction fidelity, corpus diagnostics `[stable]`
- `cli.py` — `ear run` · `ear demo` · `ear investigate`; run manifests into `artifacts/runs/` `[stable]`
- `core/accounts.py` — synthetic account state + 90-day transactions, derived from `(customer_id, latent_risk, seed, as_of_day)` only. Deliberately noisy: informative about risk without being a readout of it. **No LLM import allowed** `[stable]`
- `agent/` — `schemas.py` (strict decision contract, ≥1 evidence ref) · `tools.py` (five pure tools, OpenAI schemas derived from pydantic) · `investigator.py` (bounded loop: 6 steps, 2 retries, cost cap) · `prompts.py` (versioned prompt loading + sha) `[stable]`
- `llm/` — `base.py` (provider protocol, cost/latency/token capture) · `openrouter.py` (the only network call) · `offline.py` (rule-based, keyless, deliberately worse) · `cache.py` (content-addressed jsonl; record · replay · off) `[stable]`

## tests/

- `test_separation.py` — **the honesty guard.** AST-level proof that nothing on the path from conversation to decision can import the answer key. Its danger surface is DISCOVERED by glob, so new agent tools are covered the moment they exist. Do not relax `[stable]`
- `test_memory.py` — ledger invariants: never-discard, accumulation, retro re-score, decay, determinism, super-additivity vs concavity `[stable]`
- `test_tools.py` — every tool in memory, zero network. Includes the two honesty properties: no tool result mentions an outcome, and latent risk shifts the account without determining it `[stable]`
- `test_agent.py` — decision contract (no evidence → rejected), loop termination (step cap, retry cap, cost cap, provider failure all still emit a decision), offline path end-to-end, cache record→replay `[stable]`

## prompts/

- `investigator/v1/` — `system.md` (role, decision policy, evidence rule, routing) + `task.md` (slot template). Versioned files so a prompt change is a reviewable diff; the sha of both goes into the cache key and the run manifest `[stable]`

## docs/

- `architecture/architecture.md` — the shape of the system: three layers, data flow, agent loop, runtime, what is measured. Mermaid diagrams `[stable]`
- `architecture/build-plan.md` — plan of record: the wedge, the experiment, components, stages, cut list, risks, deltas-from-submission log `[stable]`
- `gates/2026-08-10-sprint-1-checkin.md` — Sprint 1 check-in brief: committed-vs-completed, the week-one finding, the Twilio collision, access status `[stable]`
- `gates/committee-requirements-email.md` — draft tooling/access email, to send right after the 2026-08-10 call `[stable]`

## artifacts/

- `runs/` — per-run JSON with manifest (seed, git SHA, config hash). Ignored except `runs/pinned/` `[generated]`
- `cache/` — committed model responses so the demo replays with no keys and no network `[generated]`

## sources/ — primary inputs, do not edit

- `submission-ear-on-every-call.md` — verbatim finalized Track A idea sent to the committee 2026-07-24. The contract `[source]`
- `genesis-committee-comms.md` — frozen gate dates, the Sprint-1 downgrade, what the check-in expects, tooling status `[source]`
- `kickoff-notes.md` — distilled competition facts: tracks, deliverables, rules, judging rubric `[stable]`
- `zenon-client-context.md` — client roster; input to the Zenon-impact narrative `[stable]`
- `2026 Zenon Agentic AI Competition Kickoff.pdf` — official kickoff deck `[source]`

## 01_research/ — retained grounding only

- `finance.md` — finance value-chain deep dive; feeds the Zenon-impact axis `[stable]`
- `client-ai-state-map.md` — per-client AI-adoption states with dated evidence `[stable]`

## Tracked elsewhere

Sprint backlog lives in JIRA project **AT (Agentic Trio)**, `https://zenonai.atlassian.net` — 5 epics,
32 tasks. AWS CodeCommit is not yet provisioned; to be requested after the 2026-08-10 call.
