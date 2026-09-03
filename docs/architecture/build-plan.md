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
seed by seed with an exact sign test.

**[`../../README.md`](../../README.md) is the source of record for every sweep figure. Where this file
and the README disagree, the README is right.** Sweep numbers move whenever the corpus or the arms
change: a corpus defect was fixed on 2026-08-28 (commit `08b20cc`) and **every record and p-value in
this section predates that fix and is being regenerated.** A plan of record that keeps its own copy of a
moving number goes stale silently and then contradicts the README in front of a judge — which is why
new claims here are written as **directions**, with the records left in one place. Reproduce either with
`earshot sweep`.

- **The pre-registered headline holds.** On thin-evidence customers the ledger catches **134 of 780**
  against **96 of 780** for score-each-call-and-forget: 8 wins, 2 ties, no losses, `p=0.008`. At 30
  seeds it strengthens to 27-0-3.
- **And it loses on concentrated arcs by a comparable margin**: **119 of 629** against **180 of 629**,
  `p=0.039` (3-25-2 at 30 seeds). Published alongside the win; the result is a trade, not a victory.
- **The strongest fair per-call baseline beats us, and it beats us on the stratum the entry is built
  on.** `stateless-top2` — sum the two loudest calls, two floats, no ledger, no never-discard, no retro
  re-scoring — takes more diffuse arcs than the full ledger, significantly, at 30 seeds. `window3-top2`
  does the same. This line previously read "matches us" on a 10-seed comparison that was not
  significant; **at 30 seeds the tie resolves into a loss**, and the 30-seed record is the one that
  counts because it is the one the README publishes. See the README's baseline table for the records
  and p-values. The honest claim is *aggregating a few conversations beats not aggregating*, not
  *memory beats detection*.
- **Overall, no arm is distinguishable from any other.** Memory neither beats nor loses to per-call
  detection across the whole portfolio.
- **The scoring mechanisms earn nothing in recall.** Full ledger vs a plain unweighted count:
  `p=1.000` on diffuse arcs, and the sign flips across seed sets (on `100..109` the plain count wins
  it, `p=0.004`). At 30 seeds the ledger does significantly beat the plain count on *concentrated*
  arcs (`17-5-8`, `p=0.017`) — unclaimed until round 5. Separately, **decay** (not confidence
  weighting) is what makes the ranking well-defined: none of the ledger's queue is decided
  alphabetically against `dumb-ledger`'s 55.1%. `earshot sweep` prints the table.

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
extraction fidelity against planted signals at conversation level, with the miss rate published ·
multi-seed spread and paired significance · tokens, steps, latency and cost per investigation.

**Five things on this list were unmeasured and are now measured, all re-run on 2026-08-31 against the
shipping corpus.** They are recorded here with their denominators because several go against us, and
because the point of the section is that it is checkable rather than reassuring.

- **Which review desks exist at all: 0 / 20 → 20 / 20 complaints, 0 / 20 → 19 / 20 vulnerability,
  1 / 20 → 16 / 20 retention, 9 / 20 → 10 / 20 collections.** `tools/reader_coverage.py --reader both
  --per-trajectory 20`, keyed Haiku 4.5, \$0.445562. Both readers' signals through the SAME
  `SignalLedger` at the SAME threshold and scoring config, denominators = planted counts. Coverage
  59 / 282 → 177 / 282. **The model column is an UPPER BOUND**: the threshold is a budget-derived
  top-K cut over the OFFLINE reader's ranking, held fixed across arms so the arms stay comparable, and
  deriving the model's own cut costs \$13.96 over all 8,429 conversations — not spent. Against us on
  the same run: the model's `financial_distress` coverage is **0.38 (27 / 72) against the lexicon's
  0.46 (33 / 72)**, and it pushes 3 / 20 churn and 6 / 20 distress customers over the line on a
  different signal family, so those cases arrive at the wrong desk.
- **Agent verdict accuracy: 29 / 50.** `tools/verdict_accuracy.py`, keyed Haiku 4.5 run, 50 crossings
  drawn evenly from customers who went on to have a real outcome and customers who did not. It caught
  **16 of 25** real cases and dismissed **13 of 25** false alarms, with **0 abstentions**.

  **This read 22 / 50 with 4 / 25 dismissals on the corpus that preceded the 2026-08-31 rebuild, and
  the conclusion printed here was "the agent barely discriminates: it escalates."** That conclusion is
  retracted. **No part of the agent changed** — the rebuild made decoys paraphrase the real signal
  instead of repeating it verbatim, stopped mangling quotes as though through speech recognition, and
  made each arc cohere, so the old corpus had been leaking the answer through surface form. A number
  that moves when the measurement gets more honest is a fact about the measurement. Reported
  confidence is not diagnostic either way: **0.837 mean on the 21 wrong verdicts against 0.852 on the
  29 right ones**.
- **Routing accuracy: 27 / 48 correct, 2 wrong, 19 declined — worse than the 36 / 49 it replaces, and
  published as worse.** `tools/routing_accuracy.py`, scored against each customer's seeded trajectory
  via `schema.TRAJECTORY_TEAM`, over the customers that have a seeded family at all. Customers with no
  seeded trajectory are reported separately and never folded into this denominator — they have no
  correct team, so including them would manufacture either errors or free accuracy.

  **The confusion matrix explains the drop and it is not the router's fault: the `complaints` row is
  entirely empty.** No complaint customer ever crossed the review threshold under the offline reader
  (0 / 20 above), so no complaint case existed to route. The 48 scorable cases are **43 collections,
  3 vulnerability, 2 retention, 0 complaints**, and all 19 declines sit in the collections row. This
  is the coverage failure of the first bullet arriving through a second door, and it will not improve
  by leaving the reader alone — fixing the reader means re-measuring routing on a distribution this
  figure has never seen. Both wrong routes matched **neither** the seeded trajectory nor the ledger's
  own dominant signal at the crossing, so neither was an evidence-consistent near-miss.

  This figure has now moved twice for corpus reasons (41 / 49 → 36 / 49 → 27 / 48). The first move
  happened because `config_hash` alone did not distinguish two corpora that disagreed about who
  crosses, which is why every manifest now carries `pipeline_sha`.
- **Cost per 1,000 conversations: \$1.58.** Reader, \$0.445562 measured over the 282 conversations of
  the coverage run. Corroborated independently at **\$1.5256 / 1,000** over the 130 conversations of
  the re-recorded streamed demo. Charged, not projected from a price list.
- **p50 / p95 reader latency: 1,333 ms / 2,162 ms**, on the same 282-conversation run — 1,230 / 1,786
  on the demo's 130. **0 unparsable replies and 0 relocated quotes** on both.

**Arm B is measured — 2026-09-03, \$0.027705, and this list no longer has a cheap open item.** Nova
Lite (`amazon.nova-lite-v1:0`, D-022's Bedrock substitution for GPT-4o-mini) over the identical 282
conversations, identical `config_hash` (`1ee962fd608f`) and `pipeline_sha` (`4d71d37cae12`), identical
ledger and threshold. One variable: which model reads. Its own cache file, so the Haiku figures above
still replay byte for byte — verified by replaying both after the fact.

| | offline lexicon | Haiku 4.5 | Nova Lite |
|---|---|---|---|
| Coverage of planted conversations | 59 / 282 | 177 / 282 | **181 / 282** |
| `financial_distress` coverage | 33 / 72 | 27 / 72 | **42 / 72** |
| Customers crossing | 10 / 80 | **65 / 80** | 60 / 80 |
| Cost per 1,000 conversations | \$0 | \$1.58 | **\$0.0982** |
| p50 / p95 latency | — | 1,333 / 2,162 ms | **873 / 1,253 ms** |
| Quotes rejected as not verbatim | — | **0** | 10 |
| Quotes relocated | — | **0** | 9 |
| Unparsable replies | — | 0 | 0 |

**It is a frontier, not a winner, and the entry says so.** Nova Lite finds *more* planted evidence
than Haiku at a sixteenth of the cost and converts *less* of it into cases — 181 / 282 against
177 / 282, but 60 / 80 crossings against 65 / 80. Finding evidence and accumulating it past a
threshold are not the same skill, and this is the cleanest measurement of that gap in the repo.

**It repairs the one desk where Haiku loses to the keyless lexicon.** `financial_distress` coverage
goes 0.375 → **0.583**, past the lexicon's 0.458. The loss recorded above is therefore **Haiku's, not
the model reader's**, and §4's earlier framing of it as a model-reader weakness was too broad.

**And it is measurably worse at citing, which is what decides D-025.** On identical text: 10 quotes
rejected for not being verbatim, 9 relocated, 1 too short — against Haiku's 0, 0 and 0 — with 0
unparsable replies on both arms, so this is not a formatting artefact. The cheaper model paraphrases
evidence it was instructed to quote, and `extract_model.py`'s verbatim guard caught all 20. For a bank
an evidence chain a reviewer cannot verify word-for-word is not evidence, so the 16× buys citation
discipline rather than recall. **D-025 now rests on measurement instead of convenience.**

Also still open, and each one is priced: **the model reader's own threshold** (\$13.96 — until it is
spent, every model-arm crossing figure above is an upper bound, and the tool prints that itself);
**routing on a queue whose complaints desk is not empty**, which needs the model reader in front of
the investigator rather than more spend on the agent; **any of the agent figures at a sample size
worth a confidence interval** — 50 cases and n=20 per trajectory on one dataset each are results, not
intervals.

First-attempt evidence groundedness **is** now measured — **0 / 50 repairs** on the 2026-08-31 run,
where the honest signal is the repair rate `earshot investigate` prints, because the loop rejects
unresolvable citations before they can leave. What that figure cannot tell you is whether a resolvable
quote was the *right* quote; that remains unmeasured.

**Also not built:** ROC/PR curves, dev-split probability calibration, and the four negative controls
(time-shuffle, outcome-shuffle, volume confound, held-out generator config). v2 promised all of these;
none exist, and listing them as planned is more useful than listing them as design.

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
   recall — it is what stops the alert queue being ordered alphabetically (0.0% vs 55.1%). The other
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
7. **The three team views are four teams, and the Commercial view is gone.** The brief promises "three
   teams read the same feed in the demo: a Retention view, a Risk and Compliance view, and a Commercial
   view" ([`../sources/submission-ear-on-every-call.md:75-79`](../sources/submission-ear-on-every-call.md)),
   and makes all three a Sprint 3 deliverable (`:124`). The shipped team set is **four and different** —
   `retention` / `collections` / `vulnerability` / `complaints` (`schema.TRAJECTORY_TEAM`) — because the
   teams fell out of the four seeded signal families, which is what the routing scorer can grade against.
   Retention survives by name; Risk and Compliance is split across collections, vulnerability and
   complaints; **Commercial has no equivalent and was dropped without a note until this entry**. The
   demo's *per-team* promise is being met by a team-scoped filter over the existing `owning_team` field:
   the data is on every case row already, tenants carry a display-only team map (`tenants.py`, D-029),
   and routing was measured at **41 / 49 correct with 0 wrong** on 2026-08-28 — so the filter is a view
   over a field, not new inference. What is genuinely lost is the Commercial *use case*: an upsell or
   value read on a conversation, which the ledger has never modelled.
8. ~~**The comparison model was never run**~~ — **CLOSED 2026-09-03 for \$0.027705.** The brief
   promises "a comparison model runs through the same harness so the numbers are honest"
   ([`:86-87`](../sources/submission-ear-on-every-call.md)). It was once retired on the reasoning that
   the brief never asked for two *vendors* — true, and beside the point: it asked for a comparison
   **model**, and one vendor's two models satisfy it exactly. The obligation stood, and it is now met:
   Nova Lite through the same harness on the same 282 conversations, same `config_hash`, same
   threshold, own cache file. Full table and reading in §4. **The delta is retired on evidence, not on
   an argument about wording** — and the result was worth having rather than a formality: the cheaper
   model finds more evidence, converts less of it, repairs the desk Haiku loses on, and fails the
   verbatim guard 20 times where Haiku failed 0. That is what decides D-025.
9. **The anchor metric — retention lift against a matched control — is not computed anywhere.** The
   brief names it as the anchor: "signals surfaced and acted on before the outcome, measured as the
   retention lift in the flagged group against a matched control"
   ([`:106`](../sources/submission-ear-on-every-call.md)). Nothing in the repo computes lift, and no
   matched control is constructed; what we publish instead is recall at an equal alert budget, which
   answers *did we surface it* and not *did surfacing it change the outcome*. **It is constructible, and
   that is the point of logging it rather than dropping it:** the corpus seeds `CustomerTruth.outcome`
   per customer, so a matched control is customers who did **not** cross the threshold, matched to the
   flagged group on stratum, conversation count and pre-crossing score, with lift as the difference in
   seeded outcome rate between the two. What it would take: a matching function, a variance estimate
   across the seeds `earshot sweep` already runs, and one honest caveat — **the corpus has no
   intervention model**, so nothing in it makes a flagged customer's outcome change when a reviewer
   acts. Without that, a lift number measures the ledger's targeting, not retention. Building the
   intervention model is the larger half of the job and is not scoped.
