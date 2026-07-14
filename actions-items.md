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
| T1 | P0 | Finance brief → `01_research/finance.md` (sonnet, scope in git history of this file) | CLAIMED (2026-07-14, Claude session — agent running) |
| T2 | P0 | Retail internal-ops brief → `01_research/retail-internal-ops.md` | CLAIMED (2026-07-14, Claude session — agent running) |
| T3 | P1 | Verify pharma.md completeness | DONE (2026-07-14 — 181 lines, ends with Sources + flagged-unverified section; complete) |
| T4 | P1 | Haiku collation: gather all "Candidate use-case seeds" from `01_research/*.md` into `02_ideas/backlog.md` (verbatim, no invention) | OPEN — blocked on T1/T2 |
| T5 | P1 | Phase 2 ideation sprint per `02_ideas/METHOD.md`: 3 sonnet ideation agents (operator-pain / startup-thesis / demo-first lenses) + humans → ≥50 one-liners → anti-slop gate. igupta catalog ONLY after Round-1 lock | OPEN — blocked on T4 |
| T6 | P1 | Rubric scoring round: enrich top ~20 into idea cards, judge-panel scoring per `02_ideas/RUBRIC.md`, top-10 → top-3 memo in `03_selection/` | OPEN — blocked on T5 |
| T7 | P2 | Human review pass of research briefs (spot-check citations, esp. anything time-sensitive before it enters a pitch) | OPEN |
| T8 | P2 | Ask GC: validation-checkpoint status, API budget, AWS account access | OPEN (human task — any of the three) |
| T9 | P3 | Optional full `media.md` synthesis from `media-findings-digest.md` + session task transcripts | OPEN |
| T10 | P3 | Markdown-lint cleanup (MD060/MD022 warnings across docs) | OPEN |

## Done log

- 2026-07-14 — Repo scaffold, kickoff distillation, LinkedIn corpus, igupta scrutiny, landscape/startup/pharma/retail-commerce briefs, media digest, HNB=Huntington + team + ADP/Lendmark answers folded into PLAN/client-context.
