# Idea Candidates

10 candidates across all three tracks, each scored with the [framework](03_ideation_framework.md). Scores are 1–5 per dimension; **weighted total** out of 5.0. See [05_shortlist_and_recommendation.md](05_shortlist_and_recommendation.md) for the ranked shortlist.

Legend: **ZI** = Zenon impact (25%), **TD** = technical depth (25%), **FR** = feasibility/readiness (25%), **OR** = originality (15%), **PR** = presentation (10%).

---

## TRACK A — Client-Facing Solutions

### I1 · Forecast Copilot — agentic subscription/revenue forecasting with auto-QC + narrative
**Anchor:** Dow Jones (FAST, new-order forecasting, curve library, financial forecast).

- **Problem.** Forecasting subscriber acquisition, renewals and revenue is slow, spreadsheet-heavy, and only trusted when assumptions are documented and QC'd. Analysts spend days reconciling curves, re-running scenarios, and writing the "why did it change" narrative.
- **Target user/client.** FP&A / subscription-analytics teams at subscription media & SaaS businesses (Dow Jones-like).
- **Solution (agentic).** An orchestrator agent that: (1) ingests subscription data + a **curve library** (renewal/save/stick); (2) runs a forecasting engine (business-rules + statistical baseline) for new orders → circulation → revenue; (3) spawns a **QC/validation agent** that checks against history, trend sanity, and finance reconciliation; (4) a **narrative agent** explains drivers and variance vs. prior forecast in plain English; (5) supports "what-if" scenario prompts ("raise the intro-price by 10%").
- **Why Zenon wins.** This *is* the Dow Jones engagement, productized. Nobody off-the-shelf encodes renewal/save/stick logic + GAAP-vs-management nuance.
- **Synthetic data.** Generate synthetic subscriber cohorts with realistic seasonality/curves (we know the shapes). Safe and convincing.
- **6-wk scope.** One product line, new-order + revenue forecast, curve library, QC agent, variance narrative, scenario prompt. Streamlit/React UI + charts.
- **Risks.** Forecast accuracy scope-creep; keep the *baseline* simple and let the agentic QC + narrative + scenarios be the star.
- **Scores.** ZI 5 · TD 5 · FR 4 · OR 4 · PR 5 → **weighted 4.60**

### I2 · Credit-Risk / Collections Strategy Copilot — explainable portfolio analyst
**Anchor:** Barclays (collections analytics, impairment, CLD, Apollo vs XGBoost).

- **Problem.** Collections/risk teams manually monitor DQ buckets and roll rates, then argue about which strategy to apply — with weak, non-reproducible explanations. Regulators + management demand **explainability**.
- **Target user/client.** Collections strategy & credit-risk teams at banks/lenders.
- **Solution (agentic).** Agent that monitors a synthetic loan portfolio, detects roll-rate/DQ-bucket shifts, recommends collections actions, and produces an **explainable rationale** blending business rules (CLD-style indicators) with an ML score (XGBoost) — surfacing *why* (SHAP-style drivers) in natural language. Optional impairment-coverage explainer.
- **Why Zenon wins.** Directly mirrors Barclays; the rules+ML-with-explanation pattern is exactly Zenon's "Apollo vs XGBoost" learning.
- **Synthetic data.** Synthetic loan book with DQ transitions/roll rates — we know the mechanics.
- **6-wk scope.** Portfolio monitor + anomaly flag + strategy recommender + explainability narrative on one synthetic portfolio.
- **Risks.** Regulated-domain nuance; keep it decision-support, not decisioning.
- **Scores.** ZI 5 · TD 5 · FR 4 · OR 4 · PR 4 → **weighted 4.50**

### I3 · Data-Trust Agent — automated data-QC, anomaly detection & reconciliation
**Anchor:** cross-client (DJ finance reconciliation, Barclays portfolio reconciliation, Visa DQ validation).

- **Problem.** Before any analysis is trusted, someone burns hours reconciling numbers across sources (finance vs operational, source vs warehouse, snapshot vs snapshot) and hunting anomalies. It's manual, repetitive, and the #1 hidden cost on every engagement.
- **Target user/client.** Any data/analytics team — highest *reusability* across Zenon's whole book.
- **Solution (agentic).** An agent that profiles two/more datasets, proposes reconciliation keys, runs checks (row/sum reconciliation, drift, nulls, schema, referential integrity), **investigates** each break (drill down, form a hypothesis about the cause), and writes a prioritized **data-quality report** with suggested fixes and SQL to reproduce. Learns/records rules per dataset (memory).
- **Why Zenon wins.** Universal pain we've solved manually for DJ, Barclays, Visa. Easy to show real hours saved.
- **Synthetic data.** Trivial — inject known errors into synthetic tables and watch the agent find them (great demo).
- **6-wk scope.** Two-source reconciliation + anomaly investigation + report generation, on synthetic finance-vs-ops data.
- **Risks.** Could look "just a data-quality tool" — lean into the *agentic investigation* (root-cause hypotheses) to show depth.
- **Scores.** ZI 5 · TD 4 · FR 5 · OR 3 · PR 4 → **weighted 4.35** *(highest floor)*

### I4 · Insight Narrator — "talk to your warehouse/dashboard" with validated SQL + narrative
**Anchor:** cross-client (Tableau/BigQuery on every engagement).

- **Problem.** Business users can't self-serve; analysts field endless "what does this number mean / show me X sliced by Y" requests. NL-to-SQL alone is untrusted because it silently returns wrong numbers.
- **Target user/client.** Business stakeholders + analysts on any BI engagement.
- **Solution (agentic).** NL question → planner → SQL generation → **self-verification agent** (checks query against schema + business-metric definitions, runs sanity checks, cross-checks totals) → chart + **narrative** with cited assumptions. The trust/verification layer is the differentiator.
- **Why Zenon wins.** We own the semantic/business-metric definitions (renewal rate, DQ bucket, coverage) that generic tools guess at.
- **Synthetic data.** Synthetic star-schema warehouse + a semantic layer of Zenon-style metric definitions.
- **6-wk scope.** NL→SQL + verification + narrative on one synthetic warehouse with ~15 governed metrics.
- **Risks.** Crowded space (many NL-BI tools) → originality is the weak point; win it on the **verification + governed-metric** angle.
- **Scores.** ZI 4 · TD 4 · FR 4 · OR 2 · PR 5 → **weighted 3.80**

---

## TRACK B — Internal Ops & Tooling

### I5 · Proposal / SOW Studio — agentic proposal & scope generation from past engagements
**Named directly in Track B ("proposal generation").**

- **Problem.** Writing proposals/SOWs is slow and reinvents the wheel; approach, scope, effort, and staffing get re-derived each time instead of reused from past wins.
- **Target user/client.** Zenon BD / delivery leads (internal).
- **Solution (agentic).** Intake a prospect brief → retrieval over an engagement-pattern library (DJ forecasting, Barclays risk, Visa reporting) → **draft agent** produces problem framing, proposed approach, phased scope, effort/staffing estimate, and risks → **critic agent** checks completeness/consistency → export to deck/doc.
- **Why Zenon wins.** Direct time-savings ROI on a real firm bottleneck; dogfoodable immediately.
- **Synthetic data.** Anonymized/generalized past-engagement patterns (we already have the `.md` history as a seed).
- **6-wk scope.** Brief → retrieval → structured proposal draft → critic pass → export.
- **Risks.** Quality of generated scope depends on the pattern library; seed it well.
- **Scores.** ZI 5 · TD 3 · FR 5 · OR 3 · PR 4 → **weighted 4.05**

### I6 · Engagement Memory — knowledge copilot over Zenon's project history
**Named directly in Track B ("knowledge management"). Most dogfoodable.**

- **Problem.** Institutional knowledge is tacit and trapped in people's heads (these very `.md` files prove it). New joiners and cross-staffed teams can't answer "how did we approach forecasting for a subscription client?" without hunting down a person.
- **Target user/client.** Every Zenon consultant (internal enablement).
- **Solution (agentic).** RAG + agentic retrieval over engagement docs, code, and decisions, with an agent that **cross-references clients** (per the Claude Context guidelines), cites sources, flags gaps ("no confirmed info on X") instead of hallucinating, and can assemble reusable-asset packs (e.g., "the curve-library approach"). Memory of what's been asked → suggests related knowledge.
- **Why Zenon wins.** Lowest build risk, immediate internal value, and we can literally demo it on the provided history repo.
- **Synthetic data.** Uses the generalized/anonymized knowledge base — no confidential data.
- **6-wk scope.** Ingestion + retrieval + cross-client synthesis + gap-flagging + cited answers + asset-pack assembly.
- **Risks.** Could read as "just RAG" → differentiate with cross-client synthesis, gap-honesty, and asset assembly (agentic, not lookup).
- **Scores.** ZI 4 · TD 3 · FR 5 · OR 3 · PR 4 → **weighted 3.85** *(safest build)*

### I7 · Prospect Radar — research & tailored-outreach agent
**Named in Track B ("prospective client outreach").**

- **Problem.** BD outreach is generic and slow; researching a prospect's analytics pain and tailoring a pitch is manual.
- **Target user/client.** Zenon BD (internal).
- **Solution (agentic).** Given a prospect, an agent researches public signals, maps likely analytics pain to a matching Zenon capability/past win, and drafts a tailored outreach + a one-page "why Zenon" mapping.
- **Why Zenon wins.** Time-savings + pipeline quality; ties research to our real capabilities.
- **Synthetic data.** Public data + synthetic prospect profiles.
- **6-wk scope.** Research agent → pain-to-capability mapping → outreach draft.
- **Risks.** Web-research reliability; "AI SDR" tools exist → originality soft.
- **Scores.** ZI 3 · TD 3 · FR 4 · OR 2 · PR 3 → **weighted 3.10**

---

## TRACK C — Open Category

### I8 · Synthetic Data Studio — domain-aware synthetic data generator for finance/subscription/risk
**Meta-play: solves the competition's *own* stated need ("develop synthetic data — approach for this").**

- **Problem.** Every team (and every Zenon client demo) needs realistic synthetic data that preserves statistical/business properties without touching confidential data. Generic synthesizers don't know subscription curves or roll rates.
- **Target user/client.** Zenon teams + clients needing safe demo/dev data; also *every other Genesis team*.
- **Solution (agentic).** An agent that takes a schema + a description of the business domain (or a small anonymized sample's *statistics only*), and generates a synthetic dataset that respects domain rules — renewal/save/stick curves, seasonality, DQ-bucket roll rates, referential integrity — plus a **fidelity report** (distribution match, privacy checks) and generation code.
- **Why Zenon wins.** We uniquely know the domain rules to encode. High originality + firm enablement + directly unblocks the whole competition.
- **Synthetic data.** It *is* the synthetic-data play — no data-access risk at all.
- **6-wk scope.** Schema/rules intake → generator → fidelity report, for the subscription and collections domains.
- **Risks.** "Fidelity vs privacy" rigor needs care; scope to two domains and show metrics.
- **Scores.** ZI 4 · TD 4 · FR 4 · OR 5 · PR 4 → **weighted 4.15** *(highest originality)*

### I9 · Agentic Analytics Eval Harness — accuracy/hallucination/SQL-correctness evals for analytics agents
**Ties directly to the competition's own "judge agent" and the readiness rubric.**

- **Problem.** Analytics/forecasting agents can't be trusted without evals: is the SQL correct? is the number hallucinated? is the forecast within tolerance? There's no standard harness for this at Zenon.
- **Target user/client.** Every team building analytics agents (incl. other Genesis teams) + Zenon delivery.
- **Solution (agentic).** A framework + judge agents that score analytics-agent outputs on: SQL correctness (execute-and-compare), numeric grounding/hallucination, forecast-accuracy vs holdout, and explanation quality — producing an accuracy/cost/latency scorecard. Reusable across other candidate ideas.
- **Why Zenon wins.** Positions Zenon as rigorous; the AI judge rewards eval maturity; usable as *our own* Demo-1/2 evidence.
- **Synthetic data.** Synthetic tasks + gold answers.
- **6-wk scope.** Eval harness + 3–4 evaluators + scorecard UI.
- **Risks.** Less of a flashy demo → invest in a clear scorecard visual.
- **Scores.** ZI 3 · TD 5 · FR 4 · OR 4 · PR 3 → **weighted 3.90**

### I10 · Agent Optimizer — cost/prompt/model-tier optimizer for agentic workflows
**Open-category "agentic optimization."**

- **Problem.** Agentic workflows are expensive and slow; teams hand-tune prompts, model choice, and step count with no systematic method — and the competition itself caps API budgets.
- **Target user/client.** Any team running agents at scale (incl. Zenon delivery).
- **Solution (agentic).** A meta-agent that, given a workflow + eval set, searches over prompts/model-tiers/routing/caching to hit a target accuracy at minimum cost/latency, reporting the Pareto frontier.
- **Why Zenon wins.** Real firm value (budget-limited APIs); strong technical story.
- **Synthetic data.** Uses any task + eval set.
- **6-wk scope.** Optimization loop over one workflow with an eval set; cost/accuracy Pareto report.
- **Risks.** Abstract; harder to tie to a *client* dollar story; needs a concrete workflow to optimize (could pair with I9).
- **Scores.** ZI 3 · TD 5 · FR 3 · OR 4 · PR 3 → **weighted 3.60**

---

## Scoreboard (weighted)

| # | Idea | Track | ZI | TD | FR | OR | PR | **Total** |
|---|------|:-----:|:--:|:--:|:--:|:--:|:--:|:---------:|
| I1 | Forecast Copilot | A | 5 | 5 | 4 | 4 | 5 | **4.60** |
| I2 | Credit-Risk Copilot | A | 5 | 5 | 4 | 4 | 4 | **4.50** |
| I3 | Data-Trust Agent | A | 5 | 4 | 5 | 3 | 4 | **4.35** |
| I8 | Synthetic Data Studio | C | 4 | 4 | 4 | 5 | 4 | **4.15** |
| I5 | Proposal / SOW Studio | B | 5 | 3 | 5 | 3 | 4 | **4.05** |
| I9 | Analytics Eval Harness | C | 3 | 5 | 4 | 4 | 3 | **3.90** |
| I6 | Engagement Memory | B | 4 | 3 | 5 | 3 | 4 | **3.85** |
| I4 | Insight Narrator | A | 4 | 4 | 4 | 2 | 5 | **3.80** |
| I10 | Agent Optimizer | C | 3 | 5 | 3 | 4 | 3 | **3.60** |
| I7 | Prospect Radar | B | 3 | 3 | 4 | 2 | 3 | **3.10** |

Scores are directional, meant to force ranking — not precise. Carried forward in [05_shortlist_and_recommendation.md](05_shortlist_and_recommendation.md).
