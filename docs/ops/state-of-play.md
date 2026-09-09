# State of play

**Updated 2026-09-09.** Rewritten in place every working session — **never appended to**. If
something will not fit, it belongs in `decisions.md` (a choice), `working-agreements.md` (a rule), or
Jira (work). Anything historical belongs in git.

> ## The three live things, 2026-09-09
>
> **1. The gate is 2026-09-11, 20:30-21:00 IST** — moved from 09-10 (which had already replaced
> 09-07). Venkat and Farhan judge; it decides the shortlist.
>
> **2. Two scripts exist for it and they disagree on market. This is the open decision and it is
> Ravi's.** `gates/2026-09-11-sprint-review.md` is the **UK** story leading with the **£650 Ombudsman
> tariff**; `docs/credit-card/` (7 files) is the **US** story and treats a pound sign as a way to lose
> the room. The US work is deeper — two red-team passes, KS-1..KS-16 — but it gave up the best number
> in the repo to get there, because the US has no tariff equivalent. **Neither is deleted.**
>
> **3. A keyed 10-seed run is in flight** (~$10.6, Haiku 4.5). It was set up to test whether
> accumulation survives a model reader — **and a free control shows it cannot.** At 200 customers /
> K=20 the *offline* reader gives `full-ledger` vs `window3-top2` **4-3-3, p=1.00**, against its
> published **30-0-0** at 1500. **The scale is the confound, not the reader**, and a powered keyed
> version is blocked by wall-clock rather than money. **30-0-0 stands.** The run still buys the
> reader-quality headline at ten seeds, quote fidelity, cost and keyed ablations.
>
> **Standing instruction from Ravi, 2026-09-09:** this is a generative-AI product. **The keyless
> lexicon is a fallback and an auditor's reproducibility property — never a product claim, and never
> the source of a headline number.**

**Fresh session, read in this order:** this file → `decisions.md` → `working-agreements.md` →
`../../README.md` → `../architecture/architecture.md`. Then `../architecture/infrastructure.md` for the
AWS design and `aws-infrastructure.md` for what is actually provisioned.

---

## Where we are

**The corpus was rebuilt on 2026-08-31 (Phase C) and the entry's framing changed with it.** An arc now
reads as one relationship: back-references that are true, a promise schedule authored before any prose,
strict turn-taking, channel-correct language, complaints that are one author. What it cost is written
down in `../corpus/06-phase-c-record.md`; what the entry claims now is decided in
`../corpus/07-framing-decision.md` and implemented across every published document as of today.

**The claim leads with coverage, not ranking — and both halves of it are now measured.** Between our
two readers, strict recall on real CFPB complaint narratives is 0.0357 (4 / 112) against 0.8214
(92 / 112); on our own shipping corpus the keyless lexicon finds **59 of 282** planted arc
conversations and the model reader finds **177 of 282**. Through the same ledger at the same threshold,
crossings per desk:

| Desk | offline lexicon | model reader |
|---|---|---|
| **Complaints** | **0 / 20** | **20 / 20** |
| **Vulnerability** | **0 / 20** | **19 / 20** |
| **Retention** | **1 / 20** | **16 / 20** |
| Collections | 9 / 20 | 10 / 20 |

Two desks receive nothing under the keyless reader. That is a product fact a judge understands in one
sentence, it replays at zero spend, and it explains why every ranking arm sits crowded near chance.
Ranking is the second half of the story, not the first. **The model column is an upper bound** — the
threshold is a top-K cut over the offline reader's ranking held fixed across arms; the model's own cut
costs $13.96 and was not spent. **The model also loses on `financial_distress` coverage** (0.38 vs the
lexicon's 0.46) and pushes 3 churn / 6 distress customers over at the wrong desk.

**Three published claims were false and are retracted; one was an underclaim and is corrected.**

| was published | is measured |
|---|---|
| "the ledger beats **every** baseline on diffuse arcs" | ties `stateless-max` 15–13–2, **loses** to `dumb-ledger` 7–18–5 |
| "the ledger beats chance on concentrated arcs" | 16–12–2, `p=0.572`. It does not |
| "aggregating a few conversations beats aggregating one" | refuted — the arm that aggregates one beats us whole-portfolio |
| "unbounded memory vs a bounded window is **unproven**" | **won 30–0–0 `p<0.001`** on diffuse; lost 1–28–1 concentrated; unproven whole-portfolio |
| extractor recall **0.659 (492 / 747)** | **0.2285 (617 / 2,700)** — the old figure was wrong by ~2.9× |

**The pre-registered headline died, and it is re-registered — D-031.** `full-ledger` vs
`stateless-max` on diffuse recall went 29–0–1 `p<0.001` to **15–13–2 `p=0.851`** (17–9–4 randomised, so
not a tie-break artefact). Measured cause: before the rebuild a diffuse customer's loudest signal was
*anti*-correlated with their outcome, and a large part of the win was measuring an opponent the old
corpus had crippled. The new primary is `full-ledger` vs `window3-top2`, **30–0–0 `p<0.001` under both
tie-break rules**, chosen for being the literal negation of never-discard rather than the biggest
record on the board. It is bound to a **co-primary chance gate the entry currently FAILS**:
`full-ledger` vs `random-rank`, 18–8–4, `p=0.076`. The dead row keeps its place in every table forever
and `cli.py` prints it under `PRE-REGISTERED HEADLINE (2026-08-09) — DIED 2026-08-31`.

**Our own ablation floor beats us, and both records are published.** `dumb-ledger` — every mechanism in
`memory.py` off — is 18–7–5 `p=0.043` against the full ledger on diffuse arcs. It produces **5 distinct
scores across 1,500 customers**, so **70.8%** of its queue is decided alphabetically by customer id
against the full ledger's **0.0%**; randomise the tie-break and it becomes 13–11–6 `p=0.839`. The
harness that does this landed in `04aa24a` on 2026-08-30, the day *before* the loss existed, applies to
all nine arms, and the deterministic record stays the default. What the mechanisms do buy is the one
thing a plain count cannot do at all: **239 of 485** multi-signal entries are worth more now than at
write under the full ledger, **0 of 485** under an unweighted count
(`uv run python tools/retro_direction.py`).

**Whole-portfolio, full-ledger is 8th of 9 arms** at the 10% budget — 0.115 (665 / 5796) against
chance's 0.113 (657 / 5796). Every arm sits between 0.113 and 0.145. That band is the reader's fault,
not the ranking's.

**Every keyed figure in the repo was re-measured on 2026-08-31 against the shipping corpus, and there
is no corpus-historical bucket left.** All four replay from committed caches at zero spend
(`EARSHOT_CACHE_MODE=replay`, where a miss raises rather than calling out):

| | measured 2026-08-31 | was |
|---|---|---|
| Reader coverage by desk | **0 / 20 → 20 / 20** complaints, **0 / 20 → 19 / 20** vulnerability, 1 / 20 → 16 / 20 retention, 9 / 20 → 10 / 20 collections | model arm stale, offline-only |
| Reader cost / latency | **$1.58 per 1,000** ($0.445562 / 282), p50 **1,333 ms**, p95 **2,162 ms**, 0 unparsable, 0 relocated | $1.66, p50 1,244, p95 2,212 |
| AT-57 verdicts | **29 / 50** — 16 / 25 caught, **13 / 25 dismissed**, 0 abstained, $0.0306 per case | 22 / 50, 4 / 25 dismissed |
| AT-58 routing | **27 / 48** correct, 2 wrong, **19 declined** | 36 / 49, 2 wrong, 11 declined |
| Streamed demo | 130 conversations, 103 signals, 9 crossings, 6 worked, **$0.4792**, $1.5256 / 1,000, p50 1,230 / p95 1,786 | 133 / 63 / $0.469 |
| Evidence repairs | **0 / 50** | unchanged |

**Two of those changed a conclusion and both are published with the reason.** AT-57's jump is **the
corpus getting more honest, not the agent getting better** — no line of the agent changed; the rebuild
made decoys paraphrase instead of repeat verbatim, stopped mangling quotes, and made arcs cohere, so
"the agent escalates rather than filters" is retracted at 13 / 25 dismissals. AT-58 **got worse and
ships as worse**: its confusion matrix's `complaints` row is entirely empty because no complaint
customer crossed under the offline reader, so 43 of 48 scorable cases are one desk — the coverage gap
above, arriving through the routing door.

**LLM spend: ~$2.45 of $12.** Arm B added $0.027705 on 2026-09-03; everything else this session was
free. Total unspent and still open: the model's own coverage threshold ($13.96) and the 10-seed keyed
sweep (~$10).

**Arm B is measured, and it is a frontier rather than a winner — the last "not measured" item in
`build-plan.md` §4 closes.** Nova Lite on the identical 282 conversations, identical config hash,
identical threshold; one variable, which model reads:

| | offline lexicon | Haiku 4.5 | Nova Lite |
|---|---|---|---|
| Coverage of planted conversations | 59 / 282 | 177 / 282 | **181 / 282** |
| `financial_distress` coverage | 33 / 72 | 27 / 72 | **42 / 72** |
| Customers crossing | 10 / 80 | **65 / 80** | 60 / 80 |
| Cost per 1,000 | $0 | $1.58 | **$0.0982** |
| p50 latency | — | 1,333 ms | **873 ms** |
| Quotes not verbatim / relocated | — | **0 / 0** | 10 / 9 |

Nova Lite finds *more* planted evidence at a sixteenth of the cost and converts *less* of it into
cases. It also repairs the one desk where Haiku loses to the keyless lexicon, so that published loss
is Haiku's rather than the model reader's. Against it: on identical text it produced 10 quotes that
were not verbatim and 9 that had to be relocated, against Haiku's zero of each, with 0 unparsable
replies on both — so it is paraphrasing evidence it was told to quote, and the verbatim guard caught
all 20. **D-025 stands on evidence now instead of convenience:** for a bank, an evidence chain a
reviewer cannot verify word-for-word is not evidence, and that is what the 16× buys.

**Health, measured 2026-09-03.** **903 passing, 5 skipped** (908 collected), ruff clean, separation
guard over **45** modules with both exemption lists still capped at 3, **30 UI routes** and 26 crawled
links (`ui/smoke.mjs`), a contrast gate over **674** colour pairs across 17 routes and 2 themes. Next
gate **2026-09-07**. Of the 49 new tests, 44 were written today — `test_provision.py` (19),
`test_feed.py` (21), `test_metrics.py` (14 → 18) — and the rest are `test_separation.py`'s glob
picking up the new modules, which is the discovery working. Every one pins a property that was
actually violated in production today rather than a label.

**AWS is real and it runs.** 3 DynamoDB tables with PITR, **4** SQS queues (both consumed queues
redrive at 3; a FIFO source needs a FIFO DLQ), 3 Lambdas on python3.13 from one zip, both event source
mappings Enabled with `ReportBatchItemFailures`, a Function URL at `AuthType=AWS_IAM`. All six API
routes answer against real DynamoDB.

**The whole Northwind book has been through the deployed path and it agrees with the local pipeline.**
`tools/feed.py`, 2026-09-03: 130 messages in 44 FIFO groups → **34 ledger entries → 1 case → `GET
/cases` 200**, matching the local prediction exactly, deployed score `0.6526618648909545` against
local `0.652662`. Fed twice — 260 messages, still 34 entries and 1 case, so at-least-once cannot
double-count on real infrastructure and not only in a stub. The case's evidence chain is the entry's
claim in a deployed record: `CUST-0006-C0` scored **0.1306 at write** on day 21, a fifth of the cut,
and is load-bearing 73 days later with `retro_delta 0.5220`. **This is the feasibility evidence the
entry did not have**, and 25 of the 100 rubric points are scored on it.

One crossing in 44 customers is the keyless lexicon's real rate and is reported as such. This run is
the deployment proof, not a reader result.

Account `859430413223`, **us-east-1**, bucket `s3://agentic-trio`. Coordinates:
`aws-infrastructure.md`. **`AWS_PROFILE=genesis` must be set** — without it boto3 finds no credentials
and fails looking exactly like a dead SSO token.

**One deployment (Northwind), framed as an integration.** Nine pipeline seams, **five** of them the
client's own systems — the screen counts them rather than asserting it.

## Blocked, and on what

- **The IAM policy is DONE** — cleared by IT on 2026-08-31, verified, and as of 2026-09-03 the
  deployed path is exercised rather than merely permissioned. `dynamodb:DeleteItem` is correctly
  absent, so never-discard is enforced at the IAM layer and not only by a test. Nothing is blocked on
  IT any more except CodeBuild, which we declined.
- **Remaining LLM spend is a decision, not a technical block.** SSO was re-minted 2026-08-29 and every
  keyed item that was queued has run (~$2.42 of $12). What is left is priced and unspent, not blocked:
  the model's own coverage threshold ($13.96), the 10-seed keyed sweep (~$10), Arm B on Nova Lite
  ($0.01), a keyed `earshot investigate` for `ui/data.js`. `aws sts get-caller-identity` is a **lying
  probe** — it answers from a cached role credential while the SSO token underneath is dead. Probe
  Bedrock.
- CodeBuild/CodePipeline blocked by the same `iam:CreateRole` gap. Object Lock on `agentic-trio` is
  OFF and needs an AWS Support case. No SNS, no Budgets, no VPC subnets.

## Next, in order

0. **Finish the `demo` stage — half-deployed, the only untidy state in the repo.** Ravi authorised
   the model reader on real infrastructure (~$0.21) on 2026-09-03; the SSO token expired mid-deploy.
   Tables, all four queues and `earshot-demo-ingest` (with its mapping) exist; `investigate` and
   `api` do not. Both tools are idempotent — the exact resume commands are in `handover.md`.
   **`dev` = keyless lexicon, `demo` = Haiku 4.5, same book, same infrastructure**, which is a better
   comparison than overwriting `dev` and is also the only option: `dev`'s ledger cannot be cleared,
   because `dynamodb:DeleteItem` is absent from the role by design.
1. **The reviewer UI's write path — now the largest open item, and it needs a decision.** A static
   page cannot sign an `AuthType=AWS_IAM` Function URL, so the decision buttons currently print the
   request body they *would* send and say so on screen. The options are a signing proxy, switching
   the URL to `AuthType=NONE` behind a shared secret (bad), or leaving it honestly read-only for the
   demo. Nothing else in the deployed path is unfinished.
2. **Extend the reader-coverage sample to n=40 per trajectory (~$0.45 delta).** The lead claim is
   measured at n=20 on one seed — a direction, not an interval — and samples nest (first N by
   `customer_id`), so doubling re-reads nothing already cached and pays only the delta. The
   **collections row is the half most worth a bigger denominator**: it is the one family where the
   model reader loses on coverage (0.38 vs 0.46) and wins by a single crossing (10 / 20 vs 9 / 20).
3. **The per-mechanism tie-share ablation — free, offline, and the cheapest open item in the repo.**
   `mechanism_ablations()` already exists in `arms.py`. `dumb-ledger` switches five things off at
   once, so today's evidence justifies the *set*, not any member. Printing each mechanism's distinct-
   score count would let the entry say which one earns its keep instead of defending all four.
4. **The reader behind `ui/data.js` is still the offline lexicon.** Its verdicts are keyed as of
   `4ec34cd` ($0.2326, 8 investigations, 0 / 8 evidence repairs), but `--extractor` does not apply
   to `earshot investigate`, so the extraction under those verdicts is the 26-regex fallback. Given
   §1's desk table, that is the gap most worth closing: the screens `ui/README.md` calls "the proof"
   are running the reader we publish as leaving two desks empty. Needs a code path, not just spend.
5. **The 10-seed keyed sweep** (~$10, ONE process on ONE cache path) — the single most valuable
   unspent measurement, because it is what would settle the chance gate. Deferred deliberately.
6. ~~**Arm B**~~ — **DONE 2026-09-03, $0.027705.** Nova Lite, own cache file, published Haiku
   figures still replay byte for byte. Result above; it is a frontier, not a winner.
7. **The silence-permitting corpus** — pre-registered in D-031 as a declared second arm published
   beside the first, never a substitution. It is an experiment, not a fix. Free.
8. **Give the six alarms an action, or decide not to.** They fire into nothing: no SNS on the
   account, and the EventBridge → notifier-Lambda route would be the first thing in this system that
   reaches outward, which the HITL-by-absence guarantee is built on. An operator notifier is not a
   customer notifier, so this is a gap to close deliberately or to leave closed deliberately —
   `tools/alarms.py`'s docstring already argues both sides. Worth noting the cheaper win first: **no
   alarm here has ever transitioned to ALARM**, so every threshold is reasoned rather than observed,
   and proving one fires costs nothing.
9. **`GET /cases/{id}` serves DynamoDB internals** — `pk`, `gsi1pk` and `gsi1sk` come back in the
   client-facing body. Not an answer-key leak and `test_api.py` is right to pass, but the list route
   does not do this and the detail route should not either.

## Known-weak, stated rather than hidden

- **The observability was decorative until 2026-09-03, and the reason is worth remembering.** EMF
  omitted the `_aws.Timestamp` it requires, so CloudWatch stored every log line and dropped every
  metric. 130 well-formed records produced zero datapoints. Because `TreatMissingData` is
  `notBreaching` throughout, the four alarms on the `Earshot` namespace read **OK** — not
  INSUFFICIENT_DATA — so the dashboard affirmatively reported health for metrics that did not exist.
  W11 had been marked DONE for a week. Nothing but running real traffic through it would have found
  this, which is the argument for `tools/feed.py` existing at all.
- **No alarm has ever transitioned to ALARM.** All six thresholds are reasoned, not observed. Six
  alarms that have never fired are six untested assertions, and two of them (`ingest-lag`,
  `investigations-dlq`) are on SQS metrics whose behaviour under real load we have also never seen.
- **The deployed end-to-end run proves the plumbing, not the product.** One crossing in 44 customers
  is the keyless lexicon's real rate; the interesting readers are not deployed. `--extractor bedrock`
  flips it and has never been run on AWS, so the deployed numbers and the published reader numbers
  come from different readers and must not be quoted together.
- **The ledger does not beat chance on any stratum at 30 seeds.** Diffuse 18–8–4 `p=0.076`;
  whole-portfolio 13–11–6 `p=0.839`; concentrated 16–12–2 `p=0.572`. The `p=0.345 → p=0.076` movement
  on diffuse is **one corpus change** and is not claimed as progress. Chance is competitive because
  there is almost nothing in the stream to rank, which is the coverage argument, not an excuse.
- **The re-registration is the shape of p-hacking and the mitigations are the answer, not a denial.**
  The replacement was chosen from a matrix already visible. Several rows would have served
  (`dumb-ledger` vs `window3-top2` is 29–0–1; `long-context-3` vs `window3-top2` is 24–0–6). We did
  not take the biggest, we bound the claim to a gate we fail, the dead row stays, and an unseen
  experiment is pre-registered alongside. If that reads as insufficient, the honest floor is to
  publish no ranking headline at all and lead entirely on the CFPB benchmark, which is genuinely
  pre-registered and untouched by any corpus change.
- **"Diffuse" still does not mean what the pitch implies.** Every arc conversation carries a plant
  (0 / 663 empty), so diffuse means *a weak signal every time*, not *silence between signals*. The
  realistic case — a customer calls eight times, three of which matter — is untested. This is item 7
  in "Next" and it moves every published number.
- **The corpus is tidy, and tidy is its own tell.** Live conversations take six discrete lengths
  (9, 11, 13, 15, 17, 19), 411 of 933 are 15, and every one is strictly alternating. Nobody
  interrupts. More follow-ups per topic is the fix and it is pure authoring.
- **A planted fragment is spoken register even inside a written complaint**, because every fragment
  was authored for speech and the evidence quote must be verbatim.
- **`ce-s1` is nearly extinct.** *"This is the fourth time I've called"* now needs a fourth contact
  and a broken undertaking, so it is planted 3 times per 1,500 customers against 34 before. That is
  the honest rate for that sentence.
- **The offline lexicon's coverage collapsed across all four families and is published, not fixed.**
  0.21 / 0.02 / 0.46 / 0.13 against what was planted. Widening the cues to close a gap discovered by
  measuring against the answer key is exactly the tuning the build rules forbid.
- **The ranking order is not stable across review budgets.** At 1% `long-context-3` leads and
  full-ledger is 6th of 9; at 10% `stateless-max` leads and full-ledger is 8th of 9. No single-budget
  table describes the arms in general.
- **The ledger loses cleanly on concentrated arcs** — 0–30–0 against three of the other eight arms
  and 1–28–1 against two more. Published as a trade: run memory alongside per-call detection, not
  instead of it.
- **The ledger hands the agent a queue that is ~90% false alarm by construction** — 25 of 240
  crossings at a 10% budget had a real outcome. Corpus-historical; not re-measured since the rebuild.
  It is the one figure in the agent story that still carries that label.
- **AT-58 routing fell to 27 / 48 and the cause is a coverage gap, not the router.** The `complaints`
  row of its confusion matrix is empty and all 19 declines sit in the `collections` row. Fixing the
  reader means re-measuring routing on a distribution this figure has never seen; it will not improve
  by leaving the reader alone.
- **AT-57's 29 / 50 is n=50 on one dataset**, and reported confidence does not help a reviewer triage
  it: 0.837 mean on the 21 wrong verdicts against 0.852 on the 29 right ones.
- **The model reader's own threshold is unmeasured**, so every model-arm crossing figure in the repo
  is an upper bound. $13.96, and the tool prints the caveat itself on every run.
- **`ui/data.js` is half-upgraded and the screens say which half.** Verdicts are keyed Bedrock as of
  `4ec34cd`; the reader under them is still the offline lexicon, because `--extractor` does not reach
  `earshot investigate`. So the document screens demonstrate the agent on the reader whose coverage
  gap those same screens exist to argue against.
- **A keyed run's cache is isolated by path but not by prompt hash across a resume** — the $12.32
  lesson. See `handover.md`'s traps.
- **No AT ticket covers any of the eleven AWS work packages.** 45 issues live, 28 In Progress,
  0 Resolved, as of the last live read (2026-08-25).
