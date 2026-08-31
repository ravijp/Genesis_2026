# State of play

**Updated 2026-08-31.** Rewritten in place every working session — **never appended to**. If
something will not fit, it belongs in `decisions.md` (a choice), `working-agreements.md` (a rule), or
Jira (work). Anything historical belongs in git.

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

**LLM spend: ~$2.42 of $12 for all four.** The AWS SSO token was re-minted 2026-08-29 and every keyed
item ran. Total unspent and still open: the model's own coverage threshold ($13.96) and the 10-seed
keyed sweep (~$10).

**Health, measured 2026-08-31.** **850 passing, 5 skipped** (855 collected), ruff clean, separation
guard over **45** modules with both exemption lists still capped at 3, **30 UI routes** and 31 crawled
links (`ui/smoke.mjs`), a contrast gate over **650** colour pairs across 17 routes and 2 themes. Next
gate **2026-09-07**.

**AWS is real, correct, and inert.** 3 DynamoDB tables with PITR, 3 SQS queues with DLQ redrive, 3
Lambdas on python3.13 from one zip, a Function URL at `AuthType=AWS_IAM`. `GET /health` returns 200;
everything touching a store returns 500 and neither queue is wired. Account `859430413223`,
**us-east-1**, bucket `s3://agentic-trio`. Coordinates and the IAM ask: `aws-infrastructure.md`.

**One deployment (Northwind), framed as an integration.** Nine pipeline seams, **five** of them the
client's own systems — the screen counts them rather than asserting it.

## Blocked, and on what

- **The IAM policy — one inline policy, and the end-to-end path closes.** `zenon-poc-lambda-execution`
  has no SQS, DynamoDB, Bedrock **or CloudWatch Logs** permission, so the deployed Lambdas are not
  merely inert, they are **unobservable**: no log group exists despite invocations already made.
  `iam:PutRolePolicy` was attempted and denied. Policy JSON and the reproducible error lines are in
  `aws-infrastructure.md`.
- **Remaining LLM spend is a decision, not a technical block.** SSO was re-minted 2026-08-29 and every
  keyed item that was queued has run (~$2.42 of $12). What is left is priced and unspent, not blocked:
  the model's own coverage threshold ($13.96), the 10-seed keyed sweep (~$10), Arm B on Nova Lite
  ($0.01), a keyed `earshot investigate` for `ui/data.js`. `aws sts get-caller-identity` is a **lying
  probe** — it answers from a cached role credential while the SSO token underneath is dead. Probe
  Bedrock.
- CodeBuild/CodePipeline blocked by the same `iam:CreateRole` gap. Object Lock on `agentic-trio` is
  OFF and needs an AWS Support case. No SNS, no Budgets, no VPC subnets.

## Next, in order

1. **The IAM ticket** — the only hard blocker that is not a spend decision. One inline policy and the
   deployed path stops being a diagram. It now also needs `logs:*`.
2. **Extend the reader-coverage sample to n=40 per trajectory (~$0.45 delta).** The lead claim is
   measured at n=20 on one seed — a direction, not an interval — and samples nest (first N by
   `customer_id`), so doubling re-reads nothing already cached and pays only the delta. The
   **collections row is the half most worth a bigger denominator**: it is the one family where the
   model reader loses on coverage (0.38 vs 0.46) and wins by a single crossing (10 / 20 vs 9 / 20).
3. **The per-mechanism tie-share ablation — free, offline, and the cheapest open item in the repo.**
   `mechanism_ablations()` already exists in `arms.py`. `dumb-ledger` switches five things off at
   once, so today's evidence justifies the *set*, not any member. Printing each mechanism's distinct-
   score count would let the entry say which one earns its keep instead of defending all four.
4. **`ui/data.js` regeneration** — needs a keyed `earshot investigate` run. The recorded document
   screens (queue, case, retro) are still the offline rule engine; `#/desk`, `#/desk/call` and
   `#/stream` are keyed Haiku. `ui/README.md` calls those document screens "the proof", so this is
   the largest remaining gap between what the repo claims and what its screens show.
5. **The 10-seed keyed sweep** (~$10, ONE process on ONE cache path) — the single most valuable
   unspent measurement, because it is what would settle the chance gate. Deferred deliberately.
6. **Arm B**: Nova Lite for the reader arm (~$0.01 alone, $0.28 both). Last item on
   `build-plan.md`'s "not measured" list. `extractor_cache_path()` is per-model, so it cannot pollute
   the cache behind the published $1.58 / 1,000 reader figure.
7. **The silence-permitting corpus** — pre-registered in D-031 as a declared second arm published
   beside the first, never a substitution. It is an experiment, not a fix. Free.
8. **Observability (W11, EMF)** and **the UI's write path** — both need the IAM fix first.

## Known-weak, stated rather than hidden

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
- **`ui/data.js` is still the offline rule engine**, printed on screen, pending a keyed
  `earshot investigate` run that spend policy currently blocks.
- **A keyed run's cache is isolated by path but not by prompt hash across a resume** — the $12.32
  lesson. See `handover.md`'s traps.
- **No AT ticket covers any of the eleven AWS work packages.** 45 issues live, 28 In Progress,
  0 Resolved, as of the last live read (2026-08-25).
