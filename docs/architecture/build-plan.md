# Build plan

**v3, 2026-08-09.** Rewritten because v2 predated the agent layer entirely and had drifted into
arguing with reviewers who are no longer in the room. Current state lives in
[`../ops/state-of-play.md`](../ops/state-of-play.md); settled choices in
[`../ops/decisions.md`](../ops/decisions.md); the system's shape in
[`architecture.md`](architecture.md). This file is only what is left to build and what is still open.

---

## 1. What we are building

A conversation signal layer for retail banks. It reads 100% of customer conversations, extracts risk
signals with the quote behind each, and keeps a **standing per-customer ledger** that never discards a
weak signal and re-scores it as new conversations arrive. When a customer crosses the review-capacity
threshold, an **investigator agent** pulls transactions, account state and prior cases through tools and
produces a case file with a verdict, an owning team, a recommendation and cited evidence. A person
decides every action; the system has no outbound surface.

Two mechanics carry it: **never-discard** (incumbent customer memory reconciles to current truth, so new
observations supersede old ones — right for personalization, wrong for risk) and **retro re-scoring**
(a March conversation is re-read in light of July). Detection inside a single conversation is
commodity and is treated as input, not contribution.

## 2. Where the numbers stand

Measured over 10 seeds × 1,500 customers (1,945 outcome customers), equal review budget of 10%, paired
seed by seed with an exact sign test. Full table in the README; reproduce with `earshot sweep`.

- **The pre-registered headline holds.** On thin-evidence customers the ledger catches **134 of 780**
  against **96 of 780** for score-each-call-and-forget: 8 wins, 2 ties, no losses, `p=0.008`. At 30
  seeds it strengthens to 27-0-3.
- **And it loses on concentrated arcs by a comparable margin**: **119 of 629** against **180 of 629**,
  `p=0.039` (3-25-2 at 30 seeds). Published alongside the win; the result is a trade, not a victory.
- **The strongest fair per-call baseline matches us.** `stateless-top2` — sum the two loudest calls,
  two floats, no ledger — takes **147 of 780** diffuse arcs against the ledger's 134 (`p=0.508`). The
  honest claim is *aggregation beats no aggregation*, not *memory beats detection*.
- **Overall, no arm is distinguishable from any other.** Memory neither beats nor loses to per-call
  detection across the whole portfolio.
- **The scoring mechanisms earn nothing in recall.** Full ledger vs a plain unweighted count:
  `p=1.000` on diffuse arcs, and the sign flips across seed sets (on `100..109` the plain count wins
  it, `p=0.004`). At 30 seeds the ledger does significantly beat the plain count on *concentrated*
  arcs (`17-5-8`, `p=0.017`) — unclaimed until round 5. Separately, **decay** (not confidence
  weighting) is what makes the ranking well-defined: 0.7% of the ledger's queue is decided
  alphabetically against `dumb-ledger`'s 70.3%. `earshot sweep` prints the table.

Two earlier conclusions — "memory loses overall" and "long-context beats us" — were artifacts of a
single 39-positive dataset and an answer-key leak. Both retracted in writing in the README.

## 3. The agent layer

Absent from v2 of this document, which is the main reason it needed replacing.

**Loop.** Bounded at 6 steps and 2 schema retries, with a cost pre-flight that refuses a call it cannot
afford. Always returns a decision — budget exhaustion yields `insufficient_evidence` rather than an
exception, and an unexpected error anywhere is contained rather than raised.

**Tools.** `get_ledger_summary`, `get_conversation`, `get_transactions`, `get_account_state`,
`get_prior_cases`. Plain functions over pydantic models, with JSON schemas derived from those models so
the contract cannot drift from the code. No LLM import; each is unit-tested with no network.

**Decision contract.** `InvestigationDecision` requires at least one `EvidenceRef` — conversation id,
turn index, verbatim quote — that resolves against the corpus. A decision that cannot point at real
words fails validation and is retried.

**Providers.** Offline rule engine (ships first, needs no key), OpenRouter, and a content-addressed
replay cache. The demo runs from committed responses with an invalid key set, so a room without wifi
cannot break it.

**What the arms are for, now.** They answer *which trigger feeds the investigator best*, not *what the
product is*. That reframing is the honest consequence of §2: accumulation wins where evidence is thin
and ties elsewhere, so the trigger is a routing question and the agent is the product.

## 4. What is measured, and what is not

**Measured:** recall and precision at equal alert budget, per stratum · per-mechanism ablations ·
extraction fidelity against planted signals at conversation level, with the miss rate published · multi-seed spread and paired
significance · tokens, steps, latency and cost per investigation.

**Not measured, and not pretended otherwise:** agent verdict and routing accuracy · first-attempt
evidence groundedness against a known answer (the loop rejects unresolvable citations before they can
leave, so the honest signal is the repair rate `earshot investigate` now prints) · cost per 1,000
conversations · p50/p95 latency · a second model through the same harness. Also not built: ROC/PR
curves, dev-split probability calibration, and the four negative controls (time-shuffle,
outcome-shuffle, volume confound, held-out generator config). v2 promised all of these; none exist, and
listing them as planned is more useful than listing them as design.

## 5. Open questions

1. **Does never-discard beat anything cheaper?** The central open question, and the current corpus
   cannot answer it. At 30 seeds both `stateless-top2` and `window3-top2` beat the full ledger on the
   pre-registered stratum (`7-21-2`, `p=0.013` each), and `window3-top2` — last three conversations,
   keep the best two, strictly less state than a ledger — also ties us on concentrated arcs
   (`16-8-6`). Both are shipped arms, so `earshot sweep` prints it. The reason is structural: customers average 3.5 conversations, so `stateless-top2` discards
   almost nothing, and two of the four trajectories have only 4 authored fragments, so a long diffuse
   arc exhausts its pool and is forced to plant its loudest fragment. Widen the pools, lengthen
   histories, re-run. If the ledger pulls ahead this is the entry; if not, we need to know by 09-07.
2. **AT-53 — does the memory layer ship alongside per-call detection, or not at all?** It wins on thin
   evidence, loses on concentrated arcs, and ties overall. The naive rank-combined hybrid is worse than
   either parent on *both* strata, so the combination question is open rather than answered.
3. **AT-52 — do decay, corroboration, cross-channel weighting and escalation survive?** On recall the
   plain count matches them, and the sign flips across seed sets. Decay has a defence that is not
   recall — it is what stops the alert queue being ordered alphabetically (0.7% vs 70.3%). The other
   three have no defence yet: justify or remove.
4. **AT-43 — does the extractor work on real customer language?** CFPB gives 3.8M real complaint
   narratives. This is the strongest available answer to "your reader only works on prose you wrote".
5. **AT-57 — what is the real evidence-groundedness rate?** `earshot investigate` now prints the
   first-attempt repair rate; the open part is measuring it against a known answer at volume.

## 6. To 2026-08-24

Reviewer queue with approve / dismiss / route · agent decision quality against known answers · cost per
1,000 conversations and latency percentiles · a deliberate false-alarm beat in the demo · the three
one-pagers · **a recorded demo taken 2026-08-17**. Cut for this gate: a web UI, the second comparison
model, negative controls, corpus realism work.

## 7. Risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | Zenon model keys and CodeCommit not provisioned; CodeCommit is a named deliverable | Everything runs keyless; asking again after the 08-10 call |
| R2 | "Your extractor only reads prose you wrote" | Ground it on real CFPB narratives (AT-43); publish the miss rate |
| R3 | Capacity — three people on full-time client work, two gates left | Scope frozen to §6; nothing is Done until a second person reviews |
| R4 | The mechanisms never earn their place | Then remove them and pitch on auditability, determinism and the absent model call |

## 8. Deltas from the submitted brief

All within the refinement latitude the covering email reserved.

1. The re-scorer moved into Sprint 1 — the accumulation scenario cannot be rehearsed without it.
2. An investigator agent was added; the brief described a feed, not an agent.
3. The novelty sentence is narrowed (D-006) — the submitted wording is false as of 2026-05-06.
4. The headline metric is diffuse-stratum recall at equal alert budget, not seeded-signal recall.
5. Six comparison arms, not the two the brief implies.
6. A failure-recovery beat was added to the demo.
