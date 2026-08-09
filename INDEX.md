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

## 05_build/ — MVP source

`[skeleton — being created]`
