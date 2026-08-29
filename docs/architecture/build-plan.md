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

**Four things on this list were unmeasured until 2026-08-28 and are now measured.** They are recorded
here with their denominators because three of the four go against us, and because the point of the
section is that it is checkable rather than reassuring.

- **Agent verdict accuracy: 22 / 50.** `tools/verdict_accuracy.py`, keyed Haiku 4.5 run, 50 crossings
  drawn evenly from customers who went on to have a real outcome and customers who did not. It caught
  **19 of 25** real cases and dismissed only **3 of 25** false alarms, abstaining once
  (`insufficient_evidence`, which the scorer counts as wrong on both arms deliberately). **The agent
  barely discriminates: it escalates.** That is the honest read, it is worse than the earlier 4 / 10
  sample suggested on the dismissal arm, and it means the investigator currently buys routing and an
  audit trail rather than filtering.
- **Routing accuracy: 36 / 49 correct, 2 wrong, 11 declined.** `tools/routing_accuracy.py`, scored
  against each customer's seeded trajectory via `schema.TRAJECTORY_TEAM`, over the customers that
  have a seeded family at all. Customers with no seeded trajectory are reported separately and never
  folded into this denominator — they have no correct team, so including them would manufacture
  either errors or free accuracy. The failure mode is still mostly declining to route
  (`owning_team: "none"`), which is safe in a human-in-the-loop queue, but **it is no longer zero
  wrong**: both wrong routes are unmoored from the evidence on hand rather than near-misses.

  **This number was 41 / 49 with 0 wrong until 2026-08-30, and the earlier figure was measured on
  the pre-fix corpus** (`config_hash 3ebd9fb57097`, the one whose planter re-used fragments and paid
  a corroboration bonus for one utterance copied twice). Both artifacts are in `artifacts/runs/`;
  they differ by corpus, not by prompt. It is the second time a stale figure survived a corpus fix
  because `config_hash` alone did not distinguish the two — which is why every manifest now carries
  `pipeline_sha`.
- **Cost per 1,000 conversations: \$1.6563.** Reader, on-demand rate, from the 150-document CFPB keyed
  run of 2026-08-28 (`benchmarks/cfpb/RUNLOG.md`). Computed from published Bedrock prices, not charged.
- **p50 / p95 reader latency: 1,244 ms / 2,212 ms.** Same run.

**Still not measured, and not pretended otherwise:** **a second model arm through the same harness** —
arm B has never been run, and under D-022 it is now a Bedrock model (Nova Lite or Llama 3 8B) rather
than GPT-4o-mini. It costs ~\$0.01 of model spend and one run to close; it is unclosed because of
scheduling, not difficulty, and §8 logs it as an open delta against the brief. Also still open:
first-attempt evidence groundedness against a known answer — the loop rejects unresolvable citations
before they can leave, so the honest signal is the repair rate `earshot investigate` prints, and
measuring it at volume against a key has not been done.

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
8. **The comparison model was never run, and it is an open delta rather than a retired obligation.**
   The brief promises "a comparison model runs through the same harness so the numbers are honest"
   ([`:86-87`](../sources/submission-ear-on-every-call.md)). It was retired on the reasoning that the
   brief never asked for two *vendors* — true, and beside the point: it asked for a comparison **model**,
   and one vendor's two models satisfy it exactly. So the obligation stands and is unmet. **Cost to
   close: ~\$0.01 of model spend and one run** — Nova Lite or Llama 3 8B, both on-demand and invocable
   today, both already priced in `llm/bedrock.py`, and `--extractor model` already takes the flag. There
   is no integration work; this is unmet because of scheduling, and saying so is cheaper than defending
   a retirement.
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
