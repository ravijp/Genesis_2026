# Shortlist & Recommendation

Carried forward from [04_idea_candidates.md](04_idea_candidates.md). Goal: converge on the Weeks 2–3 problem-statement brief.

## The shortlist (top 4)

| Rank | Idea | Track | Total | One-line thesis |
|:----:|------|:-----:|:-----:|-----------------|
| 1 | **I1 · Forecast Copilot** | A | 4.60 | Productize Zenon's crown-jewel (subscription/revenue forecasting) as an agent with auto-QC + variance narrative + scenarios. Highest ceiling, best client $ story. |
| 2 | **I3 · Data-Trust Agent** | A | 4.35 | Agentic data-QC + reconciliation + root-cause investigation. Highest *floor*: universal pain, trivial synthetic data, killer demo. |
| 3 | **I8 · Synthetic Data Studio** | C | 4.15 | Domain-aware synthetic data generator — solves the competition's own stated constraint; highest originality + firm enablement. |
| 4 | **I5 · Proposal/SOW Studio** | B | 4.05 | Fastest, safest time-savings win; dogfoodable; clear internal ROI. |

## Recommendation

**Primary pick: I1 — Forecast Copilot (Track A).**

It maximizes the 75%-weighted core of the rubric simultaneously:
- **Zenon impact (25%):** it *is* the Dow Jones engagement, productized — a real, nameable, revenue-relevant client story. Strongest possible answer to "why does this matter to Zenon?"
- **Technical depth (25%):** genuine multi-agent design — forecasting engine + QC/validation agent + variance-narrative agent + scenario planner + a curve-library "memory." Reads as deep, not a wrapper.
- **Feasibility (25%):** we know the domain cold and can generate faithful synthetic subscriber data, so there are no data-access blockers; the risk is scope, which we control by keeping the statistical baseline simple and letting the *agentic* QC/narrative/scenarios be the star.
- **Originality (15%) + Presentation (10%):** no off-the-shelf tool encodes renewal/save/stick logic and GAAP-vs-management nuance, and the demo has an obvious wow moment — "type a scenario, get a forecast + QC pass + plain-English explanation in seconds vs. days."

**Backup / hedge by team profile:**
- **Smaller team or lower risk appetite → I3 (Data-Trust Agent).** Highest floor, easiest reproducible demo (inject known errors, watch the agent find + explain them), and it reuses across every engagement.
- **Want maximum originality / a Track-C angle → I8 (Synthetic Data Studio).** Bonus: whichever flagship we pick, I8's generator becomes the synthetic-data engine behind our own demo — so it's worth building a slice regardless.

**Powerful combination if we want one narrative:** Build **I1** and use a scoped **I8** to produce its synthetic data and a scoped **I9** (eval harness) to produce its accuracy/cost/latency evidence. That yields one coherent, deeply-engineered story that hits impact *and* the AI judge's engineering-quality bar — without three separate products.

## Why not the others (brief)
- **I2 Credit-Risk Copilot** — nearly tied with I1 and equally on-brand; choose it over I1 only if the team is stronger in banking/risk than in subscription forecasting.
- **I6 Engagement Memory** — safest build but "just RAG" risk caps depth/originality; better as an internal quick-win than a finals flagship.
- **I4 / I7 / I9 / I10** — either crowded (I4, I7) or better as *supporting* components (I9, I10) than standalone pitches.

## Suggested problem-statement brief skeleton (for I1)

Fill this for the Weeks 2–3 deliverable:
1. **Problem statement** — forecasting subscriber/revenue is slow, assumption-heavy, and only trusted after manual QC; analysts lose days per cycle.
2. **Target user/client** — FP&A / subscription-analytics teams at subscription media & SaaS businesses.
3. **Proposed solution** — Forecast Copilot: orchestrator + forecasting engine + QC/validation agent + variance-narrative agent + scenario planner over a reusable curve library.
4. **Success metrics** — forecast cycle time ↓ (days→minutes), QC coverage/accuracy, variance-explanation quality, cost/query, forecast error vs. holdout.
5. **Sprint plan** — Sprint 1: synthetic data + baseline forecast + curve library + UI skeleton. Sprint 2: QC agent + variance narrative + scenario prompts + eval harness + cost/latency table.
6. **Team name** — something that resonates (e.g., "Curve", "Forecastra", "North Star", "RenewAI"). Finalize with the team.

## Open decisions before we lock (see [00_README.md](00_README.md))
1. Confirm **track & primary idea** (recommendation: Track A / I1).
2. Confirm **team size/skills** — decides I1 vs. I3 backup.
3. Confirm **appetite** — flagship (I1) vs. safe floor (I3).

## Immediate next steps once we lock
- [ ] Draft the 1–2 page brief from the skeleton above.
- [ ] Stand up **AWS CodeCommit** repo + `README.md` (reproducibility is scored).
- [ ] Create **JIRA** backlog with the Sprint 1/2 stories + success metrics + owner.
- [ ] Build the synthetic-data generator first (unblocks everything; reuses I8 thinking).
- [ ] Define the eval harness early (Demo-1 needs accuracy/cost/latency evidence).
