# RUBRIC — How We Judge Ideas

Mirrors the official Genesis judging weights exactly (kickoff deck, slide 8). Scoring style: **integer 1–5 per axis + one-line evidence per score + confidence (H/M/L). No decimals** — false precision is banned (prior-attempt lesson).

## Hard gates (pass/fail BEFORE any scoring)

| Gate | Test |
|---|---|
| G1 | Anti-slop: 11/11 on METHOD.md Stage-2 tests (incl. Test 11 freshness gate) |
| G2 | Sizing: fits ≤6 build-weeks for 2–3 people (≤1 L axis, ≤2 M axes) |
| G3 | Synthetic data plan credible, with seeded ground truth |
| G4 | Demoable in ≤5 minutes by one presenter |
| G5 | No regulatory/ethical show-stopper (regulated decisions → HITL framing turns compliance into a feature) |
| G6 | Team skills actually cover the build |

## Scored axes (weights = official rubric)

### A1 — Zenon impact · 25%

*Official: revenue potential / time savings.*

- **5** — Named client + quantified pain + Zenon could credibly sell the POC within weeks; PE-portfolio-grade ROI story (payback measured in months). Adjacent to a live engagement (collections, HOA/SMB banking, lending, loyalty, payroll) = instant credibility.
- **3** — Plausible dollar value for a real client type, not yet quantified.
- **1** — "Someone might want this."

*Generalizability note (2026-07-14, Ravi):* clients are the lens, not the idea. Multi-client problem-space applicability (anchor client + ≥2 transferable clients or a named segment) **strengthens** this score; an idea that only works for one client **caps at 3** even with a live-engagement hook. A named first customer is still required — "problem-space product with a design anchor," not "logo pitch."

### A2 — Technical depth & innovation · 25%

- **5** — Verifiable multi-step autonomy with self-correction; orchestration or domain encoding judges haven't seen; the proprietary domain layer is visible in the demo (not claimed, shown).
- **3** — Solid single-agent + tools done well.
- **1** — Prompt wrapper / template clone.

### A3 — Feasibility & production readiness · 25%

*The AI judge lives here: evals, reproducibility, accuracy/cost/latency evidence are scored deliverables.*

- **5** — Walking skeleton imaginable in week 1; eval design exists on day 0; fresh-machine reproducible; AWS-deployable; the path-to-production one-pager writes itself.
- **3** — Buildable with identified risks.
- **1** — Research project in disguise.

### A4 — Originality · 15%

- **5** — White space or a novel crossover (e.g., two client domains fused); differentiated vs named startups; not in the graveyard.
- **3** — Fresh twist on a known category.
- **1** — Graveyard category (generic SDR, notetaker, doc chatbot).

*Freshness note (2026-07-14):* METHOD Test-11 F-tier feeds this axis — **F1** (no incumbent ships it) may score 5; **F2** (category proven, wedge open) caps at 4 unless a genuinely novel crossover lifts it; **F3** (shipped at scale) is parked pre-scoring. North-star concepts (Stage 1b) score A1/A4 on the full frame and G2/A3 on their competition slice.

*Two-horizon note (2026-07-15, T14):* the **day-1 story** (zero-agent-client reality) scores A1/A3/G2; the **vision arc** scores A4 (and A1 upside). A concept with no honest day-1 story is a horizon bet: it may keep a strong A4 but cannot lead the build regardless of total.

### A5 — Presentation potential · 10%

- **5** — Visceral 30-second demo moment + a one-sentence story a judge retells at dinner.
- **3** — Explainable with effort.
- **1** — Needs 10 minutes of context before anything happens.

## Degrees of freedom

**(a) As scoring tie-breakers** (when weighted totals are close):

1. Client transferability depth — does a named engagement adjacency exist today?
2. Demo fragility — live-failure risk, recorded-fallback quality
3. Data credibility — will synthetic data convince a domain expert?
4. Team energy — we build better what we're excited about

**(b) As design knobs** (vary these during ideation to multiply candidates from one concept):
domain · persona · autonomy level (copilot → supervised autonomy → full autonomy) · agent topology (single / multi / hierarchical) · interaction surface (chat / dashboard / ambient / embedded-in-workflow) · verification style (self-check / judge agent / deterministic validators / HITL checkpoints) · integration depth (mocked / sandbox APIs / real SaaS) · memory (session / persistent) · demo format (live / hybrid / recorded fallback).

## Judge panel protocol

3 independent judge agents, no shared context, no score visibility between judges, presentation order randomized per judge (protocol adopted 2026-07-15):

1. **Founder-CEO** — "is this a company, and would the named client pay for a POC this quarter?"
2. **Founding chief architect** — "is this technically impressive AND shippable to a funded MVP?"
3. **AI-engineering / competition judge** — "does this win against 20 other demos on the official rubric (evals, reproducibility, accuracy/cost/latency evidence)?"

Plus Ravi and me scoring independently. Output: per-axis integers + a citation per score + confidence → ranked list + rationale memo in `03_selection/`. Axis spread >2 → adjudicated with evidence, not averaged. **Minority-veto:** one credible kill objection forces rework — never averaged away. Premortem precedes any kill-pass.

**Corrected external-judge model (Ravi, 2026-07-15):** the real panel is SaaS-minded leadership just learning agentic — trivial-then-suddenly-hard questions. Every finalist carries rehearsed answers to the standing checklist (METHOD.md Stage-3 card template): user story · run requirements · infrastructure · willingness-to-pay · scaling · vision realism · evals · guardrails · failure handling + logging · cost · latency · dollar impact.
