# Ideation & Scoring Framework

How we filter and rank ideas so the pick maximizes expected finals placement — not just gut feel.

## Step 1 — Hard filters (must pass all)

An idea is disqualified unless it clears every gate:

- [ ] **Genuinely agentic.** Uses planning, tool-use, memory, or multi-step autonomy — not a single-prompt chatbot. (The competition is *Agentic* AI; the AI judge will notice.)
- [ ] **Synthetic-data-viable.** Can be demoed convincingly on synthetic/anonymized data with no confidential client data.
- [ ] **Buildable in ~6 build-weeks** by 2–3 people to a *functional, reproducible* prototype (not a mockup).
- [ ] **Has a named target user/client** and a metric we can move (dollars or hours).
- [ ] **Fits a track** (A/B/C) cleanly.

## Step 2 — Rubric-aligned scoring (1–5 each, then weight)

Mirror the official rubric so our internal ranking predicts the judges'.

| Dimension | Weight | 1 (weak) | 5 (strong) |
|-----------|-------:|----------|------------|
| **Zenon impact** | 25% | Vague "productivity" | Quantified $ revenue or hours saved, named client/team |
| **Technical depth & innovation** | 25% | Prompt wrapper | Multi-agent orchestration, tools, eval loop, novel mechanism |
| **Feasibility & production readiness** | 25% | Research-y, data-blocked | Clear 6-wk scope + path-to-prod + synthetic data ready |
| **Originality** | 15% | Off-the-shelf clone | Hard for a generic tool to replicate; Zenon-specific edge |
| **Presentation / demo-ability** | 10% | Abstract, hard to show | Obvious "wow" moment in a 3-min live demo |

**Weighted score = Σ(score × weight).** Max = 5.0.

## Step 3 — Tie-breakers (when scores are close)

Prefer the idea that:
1. **Demos in one screen** — a judge sees the value in 60 seconds.
2. **Rides existing Zenon domain** — credible client story + we already know the data.
3. **Is dogfoodable** — we can use it *inside the competition itself* (e.g., generate our own synthetic data, manage our own knowledge). Living proof beats slideware.
4. **Has a clean cost/latency/accuracy story** — cheap to run, easy eval → the AI judge rewards it.

## Winning heuristics (lessons baked into the design)

- **Chase the 75%.** Impact + depth + feasibility dominate. A brilliant-but-unbuildable idea loses to a solid, shippable one.
- **Show, don't tell, the evals.** Bring an accuracy/cost/latency table and an eval harness. Half the panel (AI judge + feasibility criterion) is engineering rigor.
- **Narrow the scope, deepen the wedge.** One high-value workflow done end-to-end (with QC + narrative) beats a broad "analyst copilot" that does everything shallowly.
- **Encode Zenon's rules, don't relearn them.** Our edge is knowing renewal/save/stick curves, DQ buckets, GAAP-vs-management. An agent that *embeds* that domain logic is deep + original at once.
- **Design for the demo.** Pick a use case with a visible before/after: a manual, hours-long analyst task collapsed to minutes on screen.
- **Budget-aware by design.** API keys are capped → build in caching, model-tiering (cheap model for routine steps, strong model for reasoning), and be ready to defend cost.

## How to read the candidates

[04_idea_candidates.md](04_idea_candidates.md) applies this framework to 10 ideas. [05_shortlist_and_recommendation.md](05_shortlist_and_recommendation.md) carries forward the top few with full scores and a recommended pick.
