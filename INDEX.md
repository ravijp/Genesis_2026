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

## 01_research/ — July-2026 research briefs

- `agentic-ai-landscape.md` — models, agent stacks, MCP/A2A, orchestration, evals/observability, enterprise platforms, security; commodity-vs-cutting-edge verdicts `[landed 2026-07-14, unreviewed]`
- `startup-landscape.md` — ~$2.5B YTD agentic funding, YC RFS themes, 30-row funding table, white space (HOA bank-side ops, compliance-aware collections, loyalty ops, payroll exceptions), graveyard, 15 seeds `[landed 2026-07-14, unreviewed]`
- `lessons-from-prior-work.md` — forensic scrutiny of igupta branch (verdict B−, bimodal): root causes, salvage list, do/don't rules, idea autopsy, fact-check audit `[landed 2026-07-14, unreviewed]`
- `retail-agentic-commerce.md` — salvaged sub-brief: ACP/AP2/UCP protocols, Instant Checkout reversal, Amazon v. Perplexity, agent-readiness playbook, traffic/margin numbers `[stable]`
- `retail-internal-ops.md` — retailer-internal agent deployments (Sparky, Magic Apron, Mylow...), value-chain verdicts, Kohl's turnaround context, vendor map incl. returns-fraud white space `[landed 2026-07-14, review pending]`
- `pharma.md` — clinical ops, PV, regulatory, MLR `[landed 2026-07-14 — completeness verified; ends with Sources + flagged-unverified section]`
- `media-findings-digest.md` — preserved essentials from the media research track: agent-ready-data/MCP wave (S&P, Moody's, LSEG, FactSet, Bloomberg), compliance-vendor map, DJ R&C white space, newsroom agents, rights-tech `[stable]`
- `media.md` — full media synthesis (deepens the digest): DJ/News Corp AI specifics, newsroom agents (Mediahuis/McClatchy/Semafor Intelligence), 5-vertical rights/royalty negative sweep (Whip Media Helix strongest anchor), ad-tech governed-autonomy, media AI economics, commodity-vs-cutting-edge, unverified-claims log `[landed 2026-07-14, unreviewed]`
- `T7-verification-pack.md` — consolidated, prioritized human-review checklist: every brief's open-verification items + cross-brief discrepancies + red-team evidence gaps, tiered by pitch-load-bearing-ness `[stable]`
- `finance.md` — TOP-PRIORITY value-chain deep dive: collections (Mills Review published, FCA AI Live Testing), HOA bank-side ops (sized, Vantaca context), SMB virtual RM, disputes (agent-attribution wedge), wealth, loyalty; fact-checked ROI table with withdrawn-claims log `[enriched pass 2 + citation fact-check 2026-07-14, human review pending]`
- `client-ai-state-map.md` — per-client AI-adoption states (S0-S3) with dated evidence, engagement signals, and 3-week-fit surfaces; grounding input for production-track ideation (T15) — compiled from existing briefs, no new research `[2026-07-15]`

## Root (tracking)

- `actions-items.md` — resume point: prioritized remaining research (P0 finance, P0 retail), token-discipline rules for agents, deferred items, open questions for Ravi `[stable]`
- `worklogs.md` — session & run history (what was tried/run: which sessions/agents produced what, failures/salvage, sequencing). Process narration lives here, not in content files `[stable]`

## 02_ideas/ — ideation machinery

- `METHOD.md` — evidence → 50+ ideas pipeline: pattern×value-chain matrix, multi-agent divergence, anti-slop gate, sizing model, synthetic-data playbook, anchoring rules; Stage-3 card template carries two-horizon lines + appetite one-liner + SaaS-judge 12-question checklist; Stage-4 = standing selection protocol (T13, 2026-07-15) `[stable]`
- `RUBRIC.md` — scoring aligned to official judging weights + hard gates + degrees of freedom; two-horizon scoring note (day-1 → A1/A3/G2, vision → A4); corrected judge personas + minority-veto/randomization/premortem protocol (T13, 2026-07-15) `[stable]`
- `backlog.md` — the idea backlog: 85 seeds (all clustered) · 46 active clusters (10 F3 parked by freshness gate) with F-tier/incumbent/applicability retro-tags + ELI5 lines · team review notes folded 2026-07-15 · finance-first scope 2026-07-15 (Retail/Pharma/Media deferred, not killed) · N-tier pointers · gate math (52 pre-human, ≥50 holds) · NOT locked — lock decision pending `[updated 2026-07-15]`
- `round1-raw-agent-outputs.md` — verbatim Round-1 divergence one-liners under the four ideation lenses (A operator-pain / B startup-thesis / C demo-first + D gap-fill); provenance for the Round-1 clusters `[stable]`
- `north-stars.md` — **v3 (2026-07-15, T14 two-horizon)**: 10 concepts re-tiered on the day-1 test — GROUNDED LEAD N-004/N-008 (N-008 reframed to any-automated-decision remediation) / GROUNDED LAYER N-001 (day-1 = QC of existing automation) / GROUNDED-GATED N-005·N-003·N-012 / HORIZON BET N-002·N-009·N-011 (honest demotions) / GATED N-010; every concept carries DAY-1 STORY + VISION ARC + SaaS-judge checklist + appetite one-liner; v2 verdicts condensed inline, v2 full text in git history `[v3 2026-07-15, lock decision pending]`
- `grounded-track.md` — **T14 deliverable 2**: resurrected first-order use cases with day-1 stories (R-001, R-002, R-004/5, R-007, R-009, R-017/27) + combined pitches CP-1 (HOA doer + earned autonomy, WAB), CP-2 (collections doer + conformance ledger, Barclays — re-scoped between-contact), CP-3 (remediation doer + auditable proofs — descoped) + adjudicated 3-lens red-team verdicts (CP-1 consensus lead) `[2026-07-15; T15 banner: CP-1 confirmed, CP-2 → P-001+P-003, CP-3 event-driven]`
- `production-track.md` — **T15 deliverable (the 80% pool)**: 14 production candidates P-001..P-014 pinned to researched client adoption states, each with 3-week-fit story + 1-yr engagement arc + HITL/metric; from 2 independent fable lenses (delivery + buyer), convergence provenance + "signs this quarter" scoreboard; 2 new clusters (P-009 MCP watchtower, P-011 evidence-pack) `[2026-07-15, lock decision pending]`
- `north-stars-redteam.md` — verbatim adversarial red-team verdicts (freshness + feasibility passes) + adjudication (accepted/rejected attacks, standing rules) `[stable]`
- `reground-brief.md` — T14 executable spec from Ravi's v2 review (2026-07-15): two-horizon rule (day-1 story at zero-agent clients + vision arc), grounded/visionary balance, SaaS-minded-leadership judge model + question checklist, appetite gate; kickoff prompt for the fresh session at the bottom `[stable]`

## 02_ideas_v2/ — fresh-lens ideation redo (T16, opened 2026-07-15)

> Bias note: `02_ideas/` is retained untouched as the coverage-check corpus; v2 sessions must not read it (or old idea content anywhere) until the protocol's Stage 7. If you are a fresh session running T16: read only `CLAUDE.md` + `02_ideas_v2/PROTOCOL.md` and stop reading this INDEX now.

- `PROTOCOL.md` — executable spec for the v2 ideation pipeline: quarantine rules, direction stratification, 6 ordinary-persona generators, verification, novelty-protected judging, coverage cross-check; kickoff prompt at the bottom `[stable]`
- `RESEARCH-BASIS.md` — cited evidence behind every protocol rule (fixation, persona diversity, direction stratification, judge unreliability, novelty protection) `[stable]`
- `RUNSTATE.md` — run manifest: all 8 stages DONE 2026-07-15; stage log + resume notes `[T16 in REVIEW]`
- `directions.md` — Stage 1: 12 mutually-distant semantic directions D1-D12 `[stable]`
- `ideas-raw-G1..G6.md` — Stage 2: verbatim generator outputs, 12 ideas each (G1 ops / G2 integration / G3 compliance / G4 SMB-owner closed-book / G5 fintech-PM / G6 contact-centre closed-book) `[stable — provenance, do not edit]`
- `clusters.md` — Stage 3: 72 → 64 clusters, merge log, convergence flags, 0 anti-slop kills `[stable]`
- `verification-V1.md` / `verification-V2.md` — Stage 4: claim verdicts + F1/F2/F3 freshness w/ named comparators; 0 refuted, 8 corrections, 4 F3 parks `[stable]`
- `grounding.md` — Stage 5: tiers (50 PROD / 10 HORIZON / 4 PARKED), anchor+transfers, 3-week-fit, engagement arcs, MVP sizing `[stable]`
- `judging-novelty.md` / `judging-buyer.md` / `judging-architect.md` — Stage 6: three independent judges, randomized orders; protected outliers C63/C64/C28 `[stable]`
- **`ideas.md` — THE T16 DELIVERABLE: 64 cards (both horizons each), 15-idea shortlist (12 prod + 3 horizon, ⅓ domain cap), Stage-7 coverage report vs 02_ideas/ (igupta pending T12 lock), run-integrity notes** `[2026-07-15 — awaiting Ravi lock call]`

## Later phases (created when opened)

- `03_selection/` — scoring runs, top-10 diligence, top-3 memo
- `04_architecture/` — competition build design
- `05_build/` — MVP source
