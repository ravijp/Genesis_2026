# PLAN — Genesis 2026 Master Plan

**North star:** win Track A *and* leave with an asset a named client would fund as a POC. Every artifact serves both goals — the official rubric already rewards this (Zenon impact 25% + feasibility/production-readiness 25%).

## Reality check vs the official calendar

The kickoff deck's 12-week calendar is defunct (Ravi 2026-07-15: **Jul 20 is no longer the demo date**). Operating plan: **6 build-weeks from idea-freeze to a heavily-scoped MVP demo** — scoped hard enough to be buildable by a 2-3 person team working *on top of 100% core-project utilization*, but the scoping must not cap the use case's capability story. Idea-freeze starts the clock; confirm checkpoint expectations with the Genesis Committee when convenient.

## Phases & gates

### P1 — Research (opened 2026-07-14, in flight)

Seven parallel tracks, July-2026 currency, all in `01_research/`:
agentic-AI landscape · finance (top priority) · pharma · media · retail · startup/funding landscape · lessons-from-prior-work scrutiny.
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
- **2026-07-14 (Ravi)** — Official checkpoint dates expected to postpone; **idea-freeze starts the build clock**. Plan against build-weeks-from-freeze, not calendar dates.
- **2026-07-14 (Ravi, review session)** — Ideation corrections adopted: (a) ideas are **problem-space products**, clients are the lens — one-liners carry an applicability line (anchor + ≥2 transfers), single-client-only caps A1 at 3; (b) **freshness gate** added as METHOD Test 11 (F1/F2/F3 vs named closest incumbent) — 10 already-shipped-at-scale clusters parked with rework notes; (c) **north-star tier (Stage 1b)** added — 7 CTO-depth problem-space concepts authored (`02_ideas/north-stars.md`), adversarially red-teamed same day (N-007 parked, N-006 conditional on GC track ruling). Organizing thesis: second-order agentic (govern/attribute/certify/graduate agents) is the 2026-27 white space our evidence supports.
- **2026-07-15 (Ravi)** — **Finance-first scope:** T6 scoring proceeds on the finance clusters + finance-anchored N-tier only; Retail/Pharma/Media clusters deferred (retained, revivable), not killed.
- **2026-07-15** — **Team review pass folded:** Ishant/Namit reviewed backlog copies offline; comments captured as dated neutral notes on 15 finance clusters; 4 new verification items added to weakest-claims (fed to T7). ELI5 plain-language lines added to all active clusters + north stars. **Round-1 lock NOT declared** — Ravi decides after reading the 2026-07-15 findings digest; igupta quarantine remains in force.
- **2026-07-15** — **Selection methodology adopted** (evidence-backed protocol, researched 2026-07-15): independent judge contexts (no score visibility between judges), rubric-anchored integer scoring with mandatory per-score citations, presentation-order randomization, **minority-veto on kill signals** (one credible objection forces rework — never averaged away), premortem before kill-pass, retrieval-grounded idea generation. Applies to this session's north-star work and to T6.
- **2026-07-15 (Ravi)** — **Model policy for make-or-break work:** fable-class agents for the far-sighted/judging-critical tasks (idea generation contrast, competition judging, contrarian kill-pass); opus for deep scrutiny; sonnet for scoped research/extraction. North-star tier being re-thought toward ~10 concepts with honest confidence tiers.
- **2026-07-15 (Ravi, v2 review)** — **Re-grounding required before lock (T14); lock = HOLD.** (a) Schedule: Jul-20 demo date defunct; 6 build-weeks from freeze to a heavily-scoped MVP. (b) Core critique of north-stars v2: the tier over-indexed on second-order agentic — Zenon clients (Barclays, HNB, WAB, ampliFI…) have **zero agents in production**, so slices that presuppose agentic infrastructure are 2-3 years ahead of any buyer's reality and the felt need is absent; where they are useful they may also be quick for others to build. Required: **two-horizon rule** — every concept carries a *day-1 story* (works at a client with no agents in production: concrete user story, buyer, dollar impact, runs-on-what) plus the vision arc; concepts with no honest day-1 story re-tier as horizon bets, and the portfolio must balance grounded first-order use cases with the dreamy ones. (c) **Judge model corrected:** expect SaaS-minded leaders learning agentic — trivial-then-suddenly-hard questions on user story, runtime requirements, infrastructure, willingness-to-pay, scaling, vision realism, evals/guardrails/failure-handling/logging, cost, latency, and dollar impact — adopted as the standing T6 card checklist. (d) **Appetite gate:** a concept must have a visible "aha / sales / winner" moment to lead the build — this is a side initiative on top of fully-utilized people. Spec: `02_ideas/reground-brief.md`.
- **2026-07-15 (Ravi)** — **Ideation stance: startup-grade, two-stage.** (a) Lenses upgraded from corporate CTO-depth to **founder-CEO** (startup-scale dreaming, category creation) + **founding chief architect** (the engineer who takes an idea to a funded MVP in 6 months); judge panel personas follow (CEO · chief architect · AI-engineering judge). (b) **Vision/grounding decoupled to avoid competition bias:** open-thinking generation runs unbounded by competition constraints (no 6-week/synthetic-data/rubric self-censoring), then a separate grounding pass narrows each vision to a competition MVP slice. North stars carry BOTH layers — full-potential arc + ≤6-wk slice — so the entry reads as chapter one of something big.

- **2026-07-15 (Ravi, post-T14 correction)** — **"Zero agents" was directional, not literal; frame = present-state pinning + engagement economics.** (a) Ideas must pin to each client's **researched, actual AI-adoption state** (Barclays: Copilot 50k + GenAI contact-centre summarization + FCA AI Live Testing; CapOne: Chat Concierge production; WAB: Fiserv agent-bank partnership; etc.) — the buyer is mid-adoption and needs pilots→production help, not a blank slate. (b) Commercial unit = **1-year Zenon engagement**: competition MVP → client pitch (Barclays has a revenue-share model) → **~3-week fit into client infrastructure** → POC/Phase-1/Phase-2 → stable production → client team takes over. The 3-week-fit is an architecture test on every idea (thin integration surface, policy-as-config, client-cloud deployable, HITL for fast risk sign-off). (c) **Portfolio mix 80/20:** ~80% ideas that earn their keep in the present state (production-fit agents with measurable results), ~20% far-future north stars. Fresh ideation pass required for the 80% pool — not a relabel of existing clusters. (d) "SaaS-minded judge" = a preparedness checklist (the questions to have answers for), not a formal judge persona.

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
2. Status with GC: has our team's validation checkpoint been handled, or do we owe a problem statement immediately? *(Ravi 2026-07-14: dates expected to shift — low urgency, still worth asking.)*
3. GC ruling needed: is an agent-certification/eval product (north-star N-006) Track A or Track C? Written answer required before it can be carded.
