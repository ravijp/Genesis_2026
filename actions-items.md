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
| T4 | P1 | Collation of research seeds into `02_ideas/backlog.md` | DONE (2026-07-14 — **71 seeds** S-001..S-071 across 7 briefs; landscape-brief seeds S-062..S-071 patched in manually. **Redux 2026-07-14:** per-brief completeness audit recovered 14 more seeds → S-072..S-085, total **85**; new seeds flagged for clustering before Round-1 lock; no errata in existing seeds beyond the already-parked S-055 stretch. **Fold-in complete 2026-07-14:** S-072..S-085 clustered → R-047..R-056 + merges, S-083 parked; 56 clusters total) |
| T5 | P1 | Phase 2 ideation sprint per `02_ideas/METHOD.md`: 3 independent ideation lenses (operator-pain / startup-thesis / demo-first) + humans → ≥50 one-liners → anti-slop gate. igupta catalog ONLY after Round-1 lock | REVIEW (2026-07-14 — 99 agent + 8 session one-liners → 46 gated clusters R-001..R-046 in `02_ideas/backlog.md`, raw provenance in `round1-raw-agent-outputs.md`. **2026-07-15: Ishant/Namit review folded as dated cluster notes; finance-first scope applied; lock decision with Ravi after the findings digest — only after lock may the igupta cross-check run**) |
| T6 | P1 | Rubric scoring round: enrich top ~20 into idea cards, judge-panel scoring per `02_ideas/RUBRIC.md`, top-10 → top-3 memo in `03_selection/` | OPEN — blocked on T5 |
| T7 | P2 | Human review pass of research briefs (spot-check citations, esp. anything time-sensitive before it enters a pitch) | OPEN — **unblocked 2026-07-14: consolidated prioritized checklist ready at `01_research/T7-verification-pack.md`** (Tier 1 = pitch-load-bearing, incl. 2 cross-brief discrepancies + 3 red-team evidence gaps). **2026-07-15 review pass added 4 items** (see backlog weakest-claims #6-9): R-003 collections risk-bucket baseline source + savings delta · R-004 per-bank HOA savings sizing · R-008 onboarding pain source (elevated, flagged twice independently) · R-017/R-027 rewards-fraud loss benchmarks |
| T8 | P2 | Ask GC: validation-checkpoint status, API budget, AWS account access, **and the N-006 track ruling (eval/certification product — Track A or C? written answer)** | OPEN (human task — any of the three; Ravi 2026-07-14: dates expected to postpone, low urgency) |
| T9 | P3 | Optional full `media.md` synthesis from `media-findings-digest.md` + session task transcripts | DONE (2026-07-14 — `01_research/media.md` (197 lines) synthesized from the completed media-track child briefs via mechanical extraction (zero re-research) incl. adversarial-verify corrections and a do-not-cite list of 3 fabricated claims) |
| T11 | P1 | North-star concept tier (Ravi 2026-07-14: problem-space-reframing ideas, CTO depth, no narrow scopes) — session-authored `north-stars.md` + adversarial red-team + backlog N-tier pointers | REVIEW (**v2 landed 2026-07-15**: 10 active concepts (5 CORE incl. new N-008 remediation + N-009 agent-to-agent servicing desk; N-003 demoted with promotion gates; N-005 spike-gated; N-010 GC-gated; N-006 parked on F3 collision) — generated via decoupled open/grounded ideation, scored by an independent 3-persona judge panel + adversarial kill-pass, originality collision-verified with dated sources. **Humans: review the v2 scoreboard + CORE five before lock**) |
| T12 | P1 | **Ravi: Round-1 lock decision** — **HOLD (Ravi 2026-07-15): blocked on T14 re-grounding**; re-arm after the two-horizon pass lands. Lock starts the build clock and permits the igupta cross-check. Also confirm with Ishant whether his review reaching no N-tier comments meant "no concerns" or "didn't get there" | HOLD (blocked on T14) |
| T14 | P0 | **Re-grounding pass per `02_ideas/reground-brief.md`** (Ravi v2 review 2026-07-15): two-horizon restructure of north-stars (day-1 story at zero-agent clients + vision arc), resurrect grounded R-clusters, 2-3 combined pitches (doer + one differentiator layer), corrected judge model (SaaS-minded leadership question checklist), appetite-gate one-liners → north-stars v3 + revised scoreboard. Run in a fresh session — kickoff prompt at the bottom of the brief | OPEN (next session) |
| T13 | P1 | T6 prep: fold the 2026-07-15 selection-methodology protocol (independent judges, citation-forced integer scores, order randomization, minority-veto kills, premortem) into `02_ideas/METHOD.md`/`RUBRIC.md` as the standing T6 scoring procedure | OPEN |
| T10 | P3 | Markdown-lint cleanup (MD060/MD022 warnings across docs) | DONE (2026-07-14 — MD022/MD032 blank-line fixes applied whitespace-only across 10 docs; `.markdownlint.json` added tuning MD052/MD060/MD013 to repo citation/table conventions instead of churning every brief; also fixed stale notes: retail-commerce header now points to landed T2 brief, landscape source [22] re-pointed to primary METR TH1.1 and stale "sources to be appended" line removed) |

## Done log

- 2026-07-14 — Repo scaffold, kickoff distillation, LinkedIn corpus, igupta scrutiny, landscape/startup/pharma/retail-commerce briefs, media digest, HNB=Huntington + team + ADP/Lendmark answers folded into PLAN/client-context.
