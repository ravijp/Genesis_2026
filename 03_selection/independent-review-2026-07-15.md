# Independent review of the idea portfolio — 2026-07-15 (evening)

Requested by Ravi ("rate the current ideas; do we redo research; what do we submit"). Two checks run
in this session, both independent of the T16 machinery:

1. **Blind competition-rubric judging** (fable agent): scored all 64 v2 cards against the *official*
   Genesis weights (impact 25 / depth 25 / feasibility 25 / originality 15 / presentation 10) + AI-judge
   engineering criteria + competition constraints (2-3 people, ~6 build-weeks, synthetic data, generic
   applicability, 10-min live demo). Instructed to ignore embedded N/B/A scores and actively disagree
   with the embedded shortlist. This lens had NOT been run before — the T16 judges scored
   novelty/buyer/architect, none scored as a Genesis panel.
2. **Web collision spot-check** (sonnet agent, 2026-07-15): fresh searches on the 6 differentiation
   claims that carry the top of the shortlist.

## Verdict headline

- **Portfolio quality: A−** (independent judge, blind). "The raw material for a winning entry is
  unambiguously here; the risk is choosing by buyer heat instead of by demo-day physics."
- **Do NOT redo 01_research.** One refuted freshness claim out of six spot-checked (see below) is a
  normal error rate; the v2 quarantined redo independently reproduced the v1 chain's core ideas
  (C47↔P-003, C62↔P-007, C06↔P-005, C05↔P-002 …), which is evidence the *research base* is sound.
  The correction needed is a **re-rank against the competition rubric**, not a re-run of research
  or ideation.
- **The embedded shortlist ordering optimizes the wrong objective for the competition.** It ranks by
  "signs this quarter" buyer conviction (a Zenon-pipeline objective); the competition rubric pays 75%
  for impact × depth × feasibility of a *generic, demoable, well-engineered prototype*. Both objectives
  are legitimate — but the submission must be picked with the second one.

## Collision-check corrections (apply to ideas.md / grounding.md before lock)

| Cluster | Prior claim | Finding (2026-07-15) | Action |
|---|---|---|---|
| **C05 Break Detective** | F2, "residual investigation open" | **REFUTED — COLLISION.** SmartStream "Smart Agents" (businesswire 2025-12-04, GA 2026-03-26) ships agentic aged-break investigation: root-cause, lineage retrieval, counterparty outreach, proposed resolution ("70% investigation-time reduction"). Duco agentic exception layer (fintech.global 2026-05-27) similar. | **Re-tier F3 / park or rework.** Remove from shortlist #3. Also taints near-miss C20/C17 one-sided framings — re-check before any swap-in. |
| **C47 Accord** | F2, "negotiation layer open" | **PARTIAL.** C&R Software + AperiData partnership (2026, openbankingexpo.com) already drives treatment changes off real-time open-banking affordability, incl. pre-emptive plan modification. Salient Taylor does voice hardship negotiation. Still unclaimed: full relief-permutation simulation vs affordability AND lifetime loss → one pre-approved first-call offer + arrangement tending. | Keep, but **narrow the stated moat** to the offer-optimization + tending loop; name C&R/AperiData as incumbent. Originality axis drops. |
| **C28 Reason-Code Honesty** | F1, CFPB Circular 2026-03 forcing function | **CONFIRMED CLEAR.** Circular is real (consumerfinance.gov, issued 2026-05-05: lenders must document how model outputs map to stated reasons, independently reviewable). No vendor (Zest, FairPlay, SolasAI, Stratyfy) ships stated-reason faithfulness auditing — existing tools do protected-class counterfactuals + reason *generation*, not faithfulness. | Strengthen card with the 2026-05-05 date. |
| **C63 Postcode Shockwave** | F1 | **CONFIRMED CLEAR.** BofA Institute aggregates payroll-inflow data for macro reporting only; WARN trackers are separate public feeds; nobody connects employer-inflow anomaly → pre-emptive hardship enrollment. | None. |
| **C64 Last-Door Case Agent** | F1 | **CONFIRMED CLEAR.** Industry coverage explicitly flags repossession-alternatives work as human-led; no exhaustion-certificate artifact anywhere. | None. |
| **C61 Ear on Every Call** | F2, action chain open | **PARTIAL (thin delta).** Detection fully commoditized (Observe.AI/CallMiner/Cresta); auto-opened pre-arrears hardship cases unshipped, but it's a small step from what's sold. | Keep as engagement play; weak competition entry. |

## Blind rubric-judge ranking (top 8 of 64, /100)

| Rank | Cluster | Score | One-line rationale | Biggest risk |
|---|---|---|---|---|
| 1 | **C28 Reason-Code Honesty** | **87** | Real technical substance (counterfactual re-execution); seeded-unfaithful-mapping synthetic engine = best AI-judge story in pool (author the lie, agent finds it — non-circular ground truth); generic to any lender; live regulatory hook | Demo subtlety — must land "the letter lied and we proved it" viscerally |
| 2 | **C63 Postcode Shockwave** | **84** | Most retellable narrative in 64 cards; town-economy corpus w/ seeded closure is exactly what the data rule rewards; second-order (the café) = genuine graph reasoning | "Who buys this?" in Q&A (no single budget line) |
| 3 | **C06 Agent-Purchase Referee** | **81** | The only idea *about* the agentic era; maximal originality; seeded synthetic disputes fully buildable | Volume "hundreds" today — impact judge can dismiss |
| 4 | **C47 Accord** | **78** | Top impact score — sellable to every lender; cure/re-default = crisp headline metric | Originality (category proven by Salient; now also C&R/AperiData); negotiation loop doesn't fit 6 weeks |
| 5 | **C64 Last-Door Case Agent** | **76** | New artifact class (negative proof) with moral charge; real depth | Heaviest build in top 8; shallow version collapses to a checklist |
| 6 | **C62 Main-Street Early Warning** | **76** | Generic to any SMB bank; seasonality-vs-decay seeded corpus is a discriminating eval | Depth/originality ride entirely on the judgment chain beating a threshold alert |
| 7 | C15 Zombie Agent Hunter | 75 | Bounded read-only build, visceral finale, meta-appeal | Depth ceiling ("sophisticated joins"); NHI vendors exist |
| 8 | C56 After-Call Answer Pack | 74 | Tight engineering story; violations=0 headline | UK-specific regime narrows genericity; zero-claims invite live attack |

**Trap list (strong in-file, weak with this panel):** C61 (#2 embedded — rank rests on client engagement,
which the rubric discounts; demos like a call-analytics vendor) · C05 (#3 embedded — driest possible
demo theater, now also collided) · C50/C55/C53 (horizon: near-zero on the 25% feasibility axis — deck
slides, not entries) · C23 (impressive part is narration, not prototype) · C04 (scope risk — 12-month
program in a card).

## Recommended competition slate (generic framing, no client dependence)

1. **PRIMARY — C28 "Reason-Code Honesty"**: *for any company that sends automated adverse-action /
   decision notices* — an agent that proves whether the stated reason is the real reason, with a
   seeded-ground-truth synthetic decisioning engine as the eval. Wins on: depth + originality +
   AI-judge engineering story + fully synthetic-native + 6-week-sized (MVP S/M). Named regulatory
   why-now (CFPB Circular 2026-03, 2026-05-05). Vision arc: no notice goes out unfaithful; extends to
   any automated decision (credit, insurance, claims).
2. **FALLBACK — C63 "Postcode Shockwave"**: *for any retail/community bank* — employer-inflow shock
   detection → affected-cohort identification (incl. second-order businesses) → pre-emptive hardship
   response. Wins on: presentation (best story) + synthetic corpus + clear collision-free white space.
   Prep the Q&A answer for budget owner (collections prevention + community-reinvestment/CRA line).
3. **ALTERNATE (impact-maximal) — C47 "Accord"**, re-scoped to the offer-engine slice only, C61+C57
   narrated as the surrounding arc: *for any consumer lender's collections function*. Choose this only
   if leadership signal favors revenue-story over originality — and accept the Salient/C&R comparison
   will be made.

C06 is the zeitgeist wildcard (originality 15/15) if the team prefers to bet on the agentic-commerce
narrative; honest about today's volume. C64 folds naturally into C28's vision chapter ("negative-proof
gates for adverse actions") rather than standing alone.

**Note on the two idea folders:** `02_ideas/` (v1) remains the *client-engagement pipeline* view —
correct for Zenon selling, biased for the competition. `02_ideas_v2/` is the competition corpus.
Nothing is wasted; they answer different questions. Final lock call remains Ravi's (T12).
