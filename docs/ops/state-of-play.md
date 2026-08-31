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

**The claim leads with coverage, not ranking.** Between our two readers, strict recall on real CFPB
complaint narratives is 0.0357 (4 / 112) against 0.8214 (92 / 112); on our own shipping corpus the
keyless lexicon finds **59 of 282** planted arc conversations, and **two of four review desks receive
no case at all** while a third receives one in twenty. That is a product fact a judge understands in
one sentence, it is measured today at zero spend, and it explains why every ranking arm sits crowded
near chance. Ranking is the second half of the story, not the first.

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

**LLM spend is stopped and the AWS SSO token is expired**, so every keyed figure in the repo is
**corpus-historical**: 22 / 50 verdicts, 36 / 49 routing, $1.66 per 1,000 conversations, p50 1,244 ms,
0 / 50 evidence repairs, the model arm of reader-coverage-by-desk, and the recorded streamed demo. All
were measured before the 2026-08-31 rebuild. They are kept, labelled at the point of use, and never
restated as current. Everything published as current today is offline and free.

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
- **LLM spend is stopped by the user's decision, not by a technical block**, and **the AWS SSO token
  is expired** on top of it. Every keyed item below waits on both. `aws sts get-caller-identity` is a
  lying probe — it answers from a cached role credential while the SSO token underneath is dead.
  Probe Bedrock.
- CodeBuild/CodePipeline blocked by the same `iam:CreateRole` gap. Object Lock on `agentic-trio` is
  OFF and needs an AWS Support case. No SNS, no Budgets, no VPC subnets.

## Next, in order

1. **The IAM ticket** — the only hard blocker that is not a spend decision. One inline policy and the
   deployed path stops being a diagram. It now also needs `logs:*`.
2. **Re-measure reader coverage with the model arm, ~$0.45.** This is the cheapest repair of the
   *lead* claim, and it is worth more than the $10 sweep: the "dark desks" beat is fully measured for
   the lexicon on this corpus and its model half is stale. If one dollar of spend is ever released,
   spend it here.
3. **The per-mechanism tie-share ablation — free, offline, and the cheapest open item in the repo.**
   `mechanism_ablations()` already exists in `arms.py`. `dumb-ledger` switches five things off at
   once, so today's evidence justifies the *set*, not any member. Printing each mechanism's distinct-
   score count would let the entry say which one earns its keep instead of defending all four.
4. **`ui/data.js` regeneration** — needs a keyed `earshot investigate` run. The recorded document
   screens (queue, case, retro) are still the offline rule engine; `#/desk`, `#/desk/call` and
   `#/stream` are keyed Haiku. Waits on spend.
5. **The 10-seed keyed sweep** (~$10, ONE process on ONE cache path) — the single most valuable
   unspent measurement, because it is what would settle the chance gate. Deferred deliberately.
6. **Arm B**: Nova Lite for the reader arm (~$0.01 alone, $0.28 both). Last item on
   `build-plan.md`'s "not measured" list. `extractor_cache_path()` is per-model, so it cannot pollute
   the cache behind the published reader figures. Waits on spend.
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
- **`ui/data.js` is still the offline rule engine**, printed on screen, pending a keyed
  `earshot investigate` run that spend policy currently blocks.
- **A keyed run's cache is isolated by path but not by prompt hash across a resume** — the $12.32
  lesson. See `handover.md`'s traps.
- **No AT ticket covers any of the eleven AWS work packages.** 45 issues live, 28 In Progress,
  0 Resolved, as of the last live read (2026-08-25).
