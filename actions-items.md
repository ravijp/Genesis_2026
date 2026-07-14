# TASK BOARD — Genesis 2026

Team: Ravi, Ishant, Namit + Claude sessions. **No named owners.**

## Autopick protocol

1. Pick the **topmost OPEN task** whose priority you can serve (humans may skip; Claude sessions must not cherry-pick without reason).
2. Mark it `CLAIMED (<date>, <who/session>)` and **commit immediately** so parallel sessions don't collide.
3. Do the work → move to `REVIEW` (human review needed) or `DONE` (mechanical, self-verifying) → commit with the task ID in the message.
4. New work discovered mid-task gets ADDED as a new task, not silently absorbed.
5. Keep this file and `INDEX.md` truthful in the same commit as the work.

## Token discipline (standing rule)

Research/mechanical agents = **sonnet or haiku**, prompts must say "Do NOT spawn sub-agents", cap searches (~≤15), single output file. Opus only with Ravi's explicit OK.

## Tasks

| ID | P | Task | Status |
|---|---|---|---|
| T1 | P0 | Finance brief → `01_research/finance.md` | REVIEW (pass 2 enrichment + fact-check 2026-07-14: Mills Review published 2026-07-06 w/ agentic-finance rec, Barclays in FCA AI Live Testing, HOA market sized ($124.2B), Salient/Kastle/InDebted verified, 3 pass-1 numbers withdrawn (₹ cost-to-collect = recycled vendor hypothetical, KYC $13-130 mis-transcribed, Zyphe 35-45% self-flagged unconfirmed). Open items listed in brief §"Open verification items" → feeds T7) |
| T2 | P0 | Retail internal-ops brief → `01_research/retail-internal-ops.md` | REVIEW (landed 2026-07-14, 197 lines; standout seeds: markdown/inventory-exception agent, returns-fraud triage) |
| T3 | P1 | Verify pharma.md completeness | DONE (2026-07-14 — 181 lines, ends with Sources + flagged-unverified section; complete) |
| T4 | P1 | Haiku collation of research seeds into `02_ideas/backlog.md` | DONE (2026-07-14 — **71 seeds** S-001..S-071 across 7 briefs; haiku missed the landscape brief, patched manually. **Redux 2026-07-14:** 7-agent per-brief completeness audit recovered 14 more seeds → S-072..S-085, total **85**; new seeds flagged for clustering before Round-1 lock; no errata in existing seeds beyond the already-parked S-055 stretch. **Fold-in complete 2026-07-14:** S-072..S-085 clustered → R-047..R-056 + merges, S-083 parked; 56 clusters total) |
| T5 | P1 | Phase 2 ideation sprint per `02_ideas/METHOD.md`: 3 sonnet ideation agents (operator-pain / startup-thesis / demo-first lenses) + humans → ≥50 one-liners → anti-slop gate. igupta catalog ONLY after Round-1 lock | REVIEW (2026-07-14 — 99 agent + 8 session one-liners → 46 gated clusters R-001..R-046 in `02_ideas/backlog.md`, raw provenance in `round1-raw-agent-outputs.md`. **Humans: add your one-liners, then declare Round-1 lock** — only after lock may the igupta cross-check run) |
| T6 | P1 | Rubric scoring round: enrich top ~20 into idea cards, judge-panel scoring per `02_ideas/RUBRIC.md`, top-10 → top-3 memo in `03_selection/` | OPEN — blocked on T5 |
| T7 | P2 | Human review pass of research briefs (spot-check citations, esp. anything time-sensitive before it enters a pitch) | OPEN — **unblocked 2026-07-14: consolidated prioritized checklist ready at `01_research/T7-verification-pack.md`** (Tier 1 = pitch-load-bearing, incl. 2 cross-brief discrepancies + 3 red-team evidence gaps) |
| T8 | P2 | Ask GC: validation-checkpoint status, API budget, AWS account access, **and the N-006 track ruling (eval/certification product — Track A or C? written answer)** | OPEN (human task — any of the three; Ravi 2026-07-14: dates expected to postpone, low urgency) |
| T9 | P3 | Optional full `media.md` synthesis from `media-findings-digest.md` + session task transcripts | DONE (2026-07-14 — the dead media agent's ~40 child transcripts were found intact in the prior session's `subagents/` dir; final reports extracted mechanically (python, zero re-research) and synthesized into `01_research/media.md` (197 lines) incl. adversarial-verify corrections and a do-not-cite list of 3 fabricated claims) |
| T11 | P1 | North-star concept tier (Ravi 2026-07-14: problem-space-reframing ideas, CTO depth, no narrow scopes) — session-authored `north-stars.md` + 2-sonnet red-team + backlog N-tier pointers | REVIEW (2026-07-14 — 7 concepts authored, adversarially red-teamed same day (`north-stars-redteam.md`), revisions folded: N-007 parked for competition, N-006 conditional on GC Track-A confirmation, all slices re-sized honestly. **Humans: review N-001..N-006 before Round-1 lock**) |
| T10 | P3 | Markdown-lint cleanup (MD060/MD022 warnings across docs) | DONE (2026-07-14 — MD022/MD032 blank-line fixes applied whitespace-only across 10 docs; `.markdownlint.json` added tuning MD052/MD060/MD013 to repo citation/table conventions instead of churning every brief; also fixed stale notes: retail-commerce header now points to landed T2 brief, landscape source [22] re-pointed to primary METR TH1.1 and stale "sources to be appended" line removed) |

## Done log

- 2026-07-14 — Repo scaffold, kickoff distillation, LinkedIn corpus, igupta scrutiny, landscape/startup/pharma/retail-commerce briefs, media digest, HNB=Huntington + team + ADP/Lendmark answers folded into PLAN/client-context.
