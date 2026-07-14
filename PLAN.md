# PLAN — Genesis 2026 Master Plan

**North star:** win Track A *and* leave with an asset a named client would fund as a POC. Every artifact serves both goals — the official rubric already rewards this (Zenon impact 25% + feasibility/production-readiness 25%).

## Reality check vs the official calendar

The kickoff deck's 12-week calendar: validation ended Jul 6 · Demo 1 Jul 20 · Demo 2 Aug 10 · Refine Aug 17 · Dry run Aug 24 · **Finals Sep 7**. Today is 2026-07-14, so the effective build budget is **~6–7 weeks with a 2–3 person team**. Ravi's directive: idea quality first, timelines second — but every idea we score gets sized against a ≤6 build-week budget (see METHOD.md sizing model), and checkpoint status should be confirmed with the Genesis Committee.

## Phases & gates

### P1 — Research (opened 2026-07-14, in flight)
Seven parallel tracks, July-2026 currency, all in `01_research/`:
agentic-AI landscape (opus) · finance = top priority (opus) · pharma (sonnet) · media (sonnet) · retail (sonnet) · startup/funding landscape (opus) · lessons-from-prior-work scrutiny (opus).
**Gate:** all briefs landed, spot-checked, INDEX updated; digest of cross-cutting themes; every brief ends in candidate use-case seeds.

### P2 — Ideation (next)
Divergence to **50+ ideas** using the pattern × value-chain matrix and multi-agent divergence protocol (METHOD.md), then the anti-slop gate. Ideas come from OUR evidence base; the igupta idea catalog is consulted only after Round-1 lock, as an overlap/coverage check.
**Gate:** ≥50 ideas, each traceable to evidence, ≥50% finance; survivors of anti-slop gate enriched into idea cards.

### P3 — Selection (top 3 → final 1)
Two-round scoring per RUBRIC.md: broad screen (me + independent judge-agent panel + Ravi) → top ~10 diligence sprints (competitor scan, synthetic-data feasibility, build sizing) → **top 3 with pre-mortems, 5-minute demo scripts, and build estimates** → Ravi picks the build (plus a designated fallback).
**Gate:** top-3 memo in `03_selection/`, decision recorded here.

### P4 — Architecture
For the chosen idea: agent topology, tool/MCP surface, synthetic-data pipeline with seeded ground truth, eval harness (the AI judge scores engineering quality — evals are a scoring weapon, not overhead), AWS deployment shape (CodeCommit), observability, cost/latency budget, HITL checkpoints.
**Gate:** design doc reviewed + walking skeleton runs end-to-end on one golden-path case.

### P5 — Build & Demo
Eval-first build in sprints aligned to competition checkpoints. Demo script includes one **deliberate failure-recovery moment** (agent catches a planted problem and corrects — the single best anti-slop demo device). Week-10 deliverables: client one-pager, accuracy/cost/latency summary, path-to-production spec, 1-min video.
**Gate:** two full dry runs; demo survives without live-API dependence (recorded fallback ready).

## Operating model

- **Trunk-based:** main is the source of truth; sessions commit progress directly; INDEX.md updated in the same commit as file changes.
- **Subagent tiering:** opus = deep research, judging, scrutiny · sonnet = scoped research, extraction · haiku = mechanical aggregation. Judge panels are independent (no shared context) to avoid anchoring.
- **Evidence discipline:** dated inline citations; time-sensitive hooks (regulatory deadlines, vendor stats) re-verified immediately before they appear in any pitch; unknowns written as "UNKNOWN — get from [person]", never filled with plausible prose.
- **Gaps companion:** every major research/decision artifact names its own weakest claims and what would verify them.

## Decision log

- **2026-07-14** — Repo scaffolded; internal rubric mirrors the official 5-axis weights exactly (impact 25 / depth 25 / feasibility 25 / originality 15 / presentation 10).
- **2026-07-14** — Bias containment (Ravi): igupta-branch content quarantined from the workspace; enters only via `01_research/lessons-from-prior-work.md`. His idea catalog (34 ideas) is sanctioned ONLY as a post-Round-1-lock cross-check.
- **2026-07-14** — Scrutiny verdict on prior attempt: B− overall, bimodal — research_IG largely sound (re-verify before quoting), ideation_IG weak (built before research, false-precision scoring). Key heuristics adopted into METHOD/RUBRIC: research-before-ideation, assurance-over-replacement idea shape, proprietary-domain-layer test, no decimal-theater scoring.
- **2026-07-14** — Python env: uv-managed (3.13), pytest + ruff dev group.

## Risks

| Risk | Mitigation |
|---|---|
| Idea too big for the window | Sizing gate in METHOD.md; prefer assurance/verifier shapes over full workflow replacement |
| Synthetic data reads as fake | Seeded ground truth + realism checks + domain-calibrated distributions (METHOD.md playbook) |
| Demo fragility live | Scripted golden path, recorded fallback, failure-recovery moment rehearsed |
| Idea is a commodity template | Proprietary-domain-layer test at the anti-slop gate; startup-landscape brief flags the graveyard |
| Official calendar already mid-flight | Confirm checkpoint expectations with GC; deliverables list drives sprint plan regardless |
| Stale "why now" hooks | Re-verify every date/stat at pitch time (EU AI Act high-risk deadline already moved once → 2027-12-02) |

## Team & operating answers (resolved Jul 2026)

- **Team:** Ravi, Ishant, Namit. No named task owners — work runs Claude-heavy with human reviews in between. Tasks live on the board in `actions-items.md`: anyone (human or Claude session) **autopicks the top OPEN item**, marks it CLAIMED, commits, and moves it to REVIEW/DONE.
- **HNB = Huntington National Bank** (confirmed).
- **ADP & Lendmark:** fair game as targets, but historically low willingness-to-pay → penalize on the impact/POC-path axis.

## Open questions for Ravi

1. API budget / AWS account access details from GC?
2. Status with GC: has our team's validation checkpoint been handled, or do we owe a problem statement immediately?
