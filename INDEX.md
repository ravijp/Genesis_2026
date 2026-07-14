# INDEX — machine-readable repo map

> **Maintenance rule:** any commit that adds, moves, or removes a file MUST update this index in the same commit. One line per file: what it is + status.
> Status legend: `[stable]` authored & reviewed · `[generating]` agent currently writing · `[skeleton]` structure awaiting content · `[source]` external input, do not edit.

## Reading order for a fresh LLM session

1. `CLAUDE.md` — session rules (uv env, bias containment, conventions)
2. `INDEX.md` — this file
3. `PLAN.md` — current phase, gates, decision log
4. `00_sources/kickoff-notes.md` — competition facts (rubric, timeline, rules)
5. Files of the current phase (see PLAN.md status)

## Root

- `README.md` — human-facing charter: mission, competition facts, repo map, status `[stable]`
- `CLAUDE.md` — LLM session instructions for this project `[stable]`
- `INDEX.md` — this map `[stable]`
- `PLAN.md` — master plan: 5 phases with gates, operating model, decision log, risks, open questions `[stable]`
- `pyproject.toml` / `uv.lock` / `.python-version` — uv-managed Python env (3.13; pytest + ruff in dev group) `[stable]`
- `.gitignore` — standard Python template (covers `.venv`) `[source]`
- `.markdownlint.json` — lint rules tuned to repo conventions (numbered citations, compact tables) `[stable]`

## 00_sources/ — primary inputs

- `2026 Zenon Agentic AI Competition Kickoff.pdf` — official GC kickoff deck, 9 pages, June 2026 `[source]`
- `kickoff-notes.md` — distilled competition facts: tracks, 12-week timeline, deliverables, rules, judging rubric, committee `[stable]`
- `zenon-client-context.md` — client roster with evidence, engagement signals, domain mapping, open identity questions `[stable]`
- `zenon-linkedin-posts.md` — full extraction of Zenon's LinkedIn posts (vision-transcribed from 20 screenshots) + analysis: PE-portfolio positioning, clients, agentic themes `[stable]`

## 01_research/ — July-2026 research briefs (agent fleet output)

- `agentic-ai-landscape.md` — models, agent stacks, MCP/A2A, orchestration, evals/observability, enterprise platforms, security; commodity-vs-cutting-edge verdicts `[landed 2026-07-14, unreviewed]`
- `startup-landscape.md` — ~$2.5B YTD agentic funding, YC RFS themes, 30-row funding table, white space (HOA bank-side ops, compliance-aware collections, loyalty ops, payroll exceptions), graveyard, 15 seeds `[landed 2026-07-14, unreviewed]`
- `lessons-from-prior-work.md` — forensic scrutiny of igupta branch (verdict B−, bimodal): root causes, salvage list, do/don't rules, idea autopsy, fact-check audit `[landed 2026-07-14, unreviewed]`
- `retail-agentic-commerce.md` — salvaged sub-brief: ACP/AP2/UCP protocols, Instant Checkout reversal, Amazon v. Perplexity, agent-readiness playbook, traffic/margin numbers `[stable]`
- `retail-internal-ops.md` — retailer-internal agent deployments (Sparky, Magic Apron, Mylow...), value-chain verdicts, Kohl's turnaround context, vendor map incl. returns-fraud white space `[landed 2026-07-14, review pending]`
- `pharma.md` — clinical ops, PV, regulatory, MLR `[landed 2026-07-14 — verify completeness, agent died right after writing]`
- `media-findings-digest.md` — preserved essentials from ~12 completed media child briefs: agent-ready-data/MCP wave (S&P, Moody's, LSEG, FactSet, Bloomberg), compliance-vendor map, DJ R&C white space, newsroom agents, rights-tech `[stable]`
- `media.md` — full synthesis of the ~12 media child briefs the dead agent never wrote: DJ/News Corp AI specifics, newsroom agents (Mediahuis/McClatchy/Semafor Intelligence), 5-vertical rights/royalty negative sweep (Whip Media Helix strongest anchor), ad-tech governed-autonomy, media AI economics, commodity-vs-cutting-edge, unverified-claims log `[landed 2026-07-14, unreviewed]`
- `finance.md` — TOP-PRIORITY value-chain deep dive: collections (Mills Review published, FCA AI Live Testing), HOA bank-side ops (sized, Vantaca context), SMB virtual RM, disputes (agent-attribution wedge), wealth, loyalty; fact-checked ROI table with withdrawn-claims log `[enriched pass 2 + citation fact-check 2026-07-14, human review pending]`

## Root (tracking)

- `actions-items.md` — resume point: prioritized remaining research (P0 finance, P0 retail), token-discipline rules for agents, deferred items, open questions for Ravi `[stable]`

## 02_ideas/ — ideation machinery

- `METHOD.md` — evidence → 50+ ideas pipeline: pattern×value-chain matrix, multi-agent divergence, anti-slop gate, sizing model, synthetic-data playbook, anchoring rules `[stable]`
- `RUBRIC.md` — scoring aligned to official judging weights + hard gates + degrees of freedom `[stable]`
- `backlog.md` — the idea backlog: 85 seeds (all clustered) · 46 active clusters (10 F3 parked by freshness gate) with F-tier/incumbent/applicability retro-tags · N-tier pointers · gate math (52 pre-human, ≥50 holds) · NOT locked — awaiting human additions `[updated 2026-07-14, review pending]`
- `round1-raw-agent-outputs.md` — verbatim outputs of the 3 ideation agents + session contributor, provenance for the Round-1 clusters `[stable]`
- `north-stars.md` — Stage-1b north-star concepts N-001..N-007: problem-space reframes at CTO depth with ≤6-wk competition slices (Ravi directive 2026-07-14); red-teamed + revised same day (N-007 parked, N-006 conditional on GC track ruling) `[landed 2026-07-14, human review pending]`
- `north-stars-redteam.md` — verbatim verdicts of the 2 adversarial sonnet red-team agents + session adjudication (accepted/rejected attacks, standing rules) `[stable]`

## Later phases (created when opened)

- `03_selection/` — scoring runs, top-10 diligence, top-3 memo
- `04_architecture/` — competition build design
- `05_build/` — MVP source
