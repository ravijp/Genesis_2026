# Zenon Capabilities & Unfair Advantages

Source: Zenon project history (Dow Jones, Barclays, Visa, Invesco). This is the lens we use to bias ideas toward things **only Zenon can pitch convincingly** — which is where the "Zenon impact," "feasibility," and "originality" scores come from.

## What Zenon actually is

An **analytics & data consulting firm** whose crown jewels are:
- **Forecasting** (subscription, revenue, financial planning)
- **Credit-risk & collections analytics**
- **Reporting, dashboards & data-quality / reconciliation**

Recurring theme across every engagement: **business context + validation matter as much as model accuracy.** ("Business first, analytics second, technology third.") That is a *perfect* fit for agentic AI, which is exactly about encoding business rules, orchestrating validation, and explaining assumptions.

## Client-by-client domain map

### Dow Jones — subscription forecasting & financial planning
Products: WSJ, Barron's, MarketWatch, IBD.
- **FAST tool** — forecast subscription performance via business rules → new-order estimates → downstream financial planning; built-in **QC/validation**.
- **New-order forecasting** — subscription starts w/ campaign behaviour, seasonality, history.
- **Financial forecast** — management-level revenue; connects operational forecasts to finance; supports planning cycles.
- **Curve library** — renewal / save / stick-rate curves, **reused across modules**.
- **Revenue forecasting** — lifecycle transitions; operational vs finance reporting.
- Concepts: renewal rate, save rate, stick rate, same-day stop-start, marketing programs, delivery calendar, revenue balance liability, **GAAP vs management reporting**.
- Stack: Athena, BigQuery, Tableau, SQL, Python.
- **Lessons:** business context ≥ model accuracy; assumptions must be documented; validate at every stage.

### Barclays — collections, impairment & credit risk
- **Collections analytics** — performance reporting, strategy measurement, operational dashboards.
- **Impairment framework** — coverage metrics, DQ tracking, portfolio monitoring.
- **CLD framework** — account-level risk indicators, business rules, decision support.
- **Apollo vs XGBoost** — rule-based vs ML comparison for prediction quality.
- **Call-centre analytics** — handle/queue time, transfers, callbacks, efficiency.
- Concepts: DQ buckets, roll rates, HRAM, risk segmentation, collections KPIs.
- Stack: Oracle, SQL, Python, Tableau, PCDS.
- **Lessons:** model **explainability** matters; business rules stay valuable alongside ML; operational metrics drive strategy.

### Visa — analytics consulting
Reporting, business analysis, dashboard support, **data-quality validation**.

### Invesco — investment-domain analytics
Business reporting, forecasting support (high-level context only).

## Cross-client patterns (the reusable pain points)

These repeat across engagements → the highest-leverage places to point an agent:

1. **Forecasting with documented assumptions + QC** (DJ, Invesco) — forecasts are only trusted if assumptions are explicit and validated.
2. **Finance ↔ operations reconciliation** (DJ GAAP-vs-management; Barclays portfolio reconciliation; Visa DQ) — reconciling numbers across sources is universal, manual, and error-prone.
3. **Explainable risk / strategy decisions** (Barclays) — rules + ML together, with a human-readable rationale.
4. **Turning dashboards into decisions** (all) — data exists; the bottleneck is analyst time translating it into narrative + action.
5. **Institutional knowledge is tacit** — these very `.md` files exist because engagement knowledge lives in people's heads, not a queryable system.

## Our unfair advantages for the competition

- **Realistic synthetic data is easy for us.** We understand subscription lifecycles, renewal/save/stick curves, DQ buckets and roll rates well enough to *generate* statistically faithful synthetic datasets — clearing the competition's #1 constraint while others struggle. (This is itself a candidate idea — see I8.)
- **We can name a real client and a real dollar story** for forecasting, collections, and reconciliation ideas → maxes the 25% "Zenon impact."
- **Validation/QC is in our DNA** → we naturally build the eval + accuracy evidence the rubric and AI judge reward.
- **Business-rules + ML hybrid thinking** → agentic designs that blend deterministic rules with LLM reasoning read as "deep," not gimmicky.

## Tech we're already fluent in (lowers build risk)

SQL, Python, Tableau, BigQuery, Athena, Oracle, AWS. The competition mandates **AWS CodeCommit** and permits OpenAI/Anthropic APIs — all inside our comfort zone.
