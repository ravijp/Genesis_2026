# State of play

**Updated 2026-08-30.** Rewritten in place every working session — **never appended to**. If
something will not fit, it belongs in `decisions.md` (a choice), `working-agreements.md` (a rule), or
Jira (work). Anything historical belongs in git.

**Fresh session, read in this order:** this file → `decisions.md` → `working-agreements.md` →
`../../README.md` → `../architecture/architecture.md`. Then `../architecture/infrastructure.md` for the
AWS design and `aws-infrastructure.md` for what is actually provisioned.

---

## Where we are

**The corpus was widened 2026-08-30** — fragment pools 8/8/4/4 → 14/14/14/14, 32 new fragments
authored in a genuine blind pass A. The arc ceiling that used to cap two of four trajectories at 4
signals is **gone**, and a test now pins its *absence* rather than warning on its presence. Every
published number was regenerated against the new corpus (`git=35e5bdf`). **827 tests** (all pass;
`uv run pytest --collect-only -q` sums to 827 across 28 files), ruff clean, separation guard over
**44 modules**, **30 UI routes** (`ui/smoke.mjs`, plus 31 crawled links), a contrast gate over **650**
rendered colour pairs across 17 routes and 2 themes. Next gate **2026-09-07**.

**`random-rank` is now a shipped arm, and it is the most important fact on this page.** It ranks
customers by a seeded RNG and ignores every signal — a chance floor rather than an assertion. On
diffuse arcs, the stratum the ledger is built for, **full-ledger is not statistically distinguishable
from random-rank**: 17–11–2, `p=0.345`. Whole-portfolio, full-ledger is **7th of 9 arms** at
0.119 recall against chance's 0.109 (+0.010). The ledger's edge is real on diffuse arcs and small
everywhere else.

**The headline flipped in both directions, and that is the finding.** Pre-registered
`full-ledger` vs `stateless-max` on diffuse arcs: **29–0–1, `p<0.001`**, holds as it did before. But
`stateless-top2` and `window3-top2` — both of which **beat** the ledger on the previous (unwidened)
corpus at `p=0.023` and `p=0.002` — now **lose** to it at `p<0.001` each (26–2–2 both). Widening how
many fragments exist to plant reversed a published headline in both directions on the same stratum.
That is the strongest evidence in this repo that these records describe the corpus at least as much
as the mechanism.

**The offline lexicon finds 1 of the 32 newly-authored fragments** (vs 21 of the original 24 —
0.03 against 0.88). The reader is the binding constraint, not the ranking: every arm is crowded
between 0.109 (chance) and 0.138 (`stateless-max`), a three-point band, and no ranking strategy
escapes a reader this weak. That is why the model reader's **0.8214 (92/112)** strict recall on real
CFPB narratives matters more to this product than any row in the sweep table.

**A keyed run on 2026-08-30 cost $12.32 and produced no artifact.** It hit the $5 spend ceiling
half way (3,561 / 7,035 conversations); resuming with a raised cap re-bought 3,275 already-paid-for
reads because `cli.py` was committed between the two halves, moving `prompt_sha` and orphaning the
cache the resume should have hit. Isolating a cache by *path* protects a published figure; it does
not protect a *resume* if the prompt hash moves underneath it. 5,494 unique reads are banked at
`artifacts/cache/extractor-widened-arcs.jsonl` (3.4 MB) — from the cache alone, independent of the
sweep, the model reader fired on 2,390 / 5,494 (0.4350) with zero unparseable responses. **Pin
`prompt_sha` before resuming a keyed run, or do not resume it.**

**LLM spend is stopped.** Everything above is free (`earshot sweep`, offline). Nothing keyed will run
until the user restarts spend. What is buildable without it: corpus/lexicon work, UI, docs, CI, tests.

**New this session, all committed:** real CI at `.github/workflows/ci.yml` (ruff → pytest → UI smoke
→ UI contrast → a 3-seed keyless sweep, on every push); `pipeline_sha` on every manifest
(`7b525d8`); the tool-side risk parameter renamed `risk_signal` so `CustomerTruth.latent_risk` cannot
be passed by habit (`93b3393`, `010ffc9`); the reviewer desk's day cursor — cases now arrive on
`#/desk` as the clock advances rather than rendering as a still image (`2ca8cb6`, `65fb054`); a fix
to the desk's re-score link plus an href-crawl guard in `smoke.mjs` that renders every link the UI's
own markup emits, not just the declared route list (`99da968`); the three required deliverables in
`docs/impact/` (`onepager-use-case.md`, `onepager-accuracy-cost-latency.md`,
`onepager-path-to-production.md`); precision as a paired metric and a four-budget recall/precision
curve (`sweep_budgets`, byte-identical to recall's win/loss/tie because every arm flags the same
count at an equal budget); a randomised tie-break harness (`randomise_ties`) that moves the
pre-registered headline record by one pair (29–0–1 → 28–0–2) without moving its significance.

**The agent is a router, not a filter — unchanged this session, still the load-bearing result.**
AT-57 at n=50 keyed (25 with an outcome, 25 without): **22 / 50** overall, caught 18/25, dismissed
**4 / 25**, one abstention, mean confidence 0.86 on the wrong answers. AT-58 routing, free (scores the
artifact AT-57 already wrote): **36 / 49 correct, 2 wrong, 11 declined**. `retention` has no row —
the offline reader's churn coverage (0.43, 30 / 70) means 0 of 325 churn customers ever cross, so the agent is
never handed a case to route there. The model reader revives it: 9 of 20 churn customers reach
Retention in a coverage sample, but Collections crossings fall 4 → 1 in the same run (n=20 per
trajectory, one dataset, upper bound — the cut is derived from the offline reader's ranking).

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
- **LLM spend is stopped by the user's decision, not by a technical block.** Every "not measured"
  item below that needs a model call waits on that being lifted.
- CodeBuild/CodePipeline blocked by the same `iam:CreateRole` gap. Object Lock on `agentic-trio` is
  OFF and needs an AWS Support case. No SNS, no Budgets, no VPC subnets.

## Next, in order

1. **The IAM ticket** — the only hard blocker that is not a spend decision. One inline policy and the
   deployed path stops being a diagram. It now also needs `logs:*`.
2. **`ui/data.js` regeneration** — needs a keyed `earshot investigate` run. The recorded document
   screens (queue, case, retro) are still the offline rule engine; `#/desk`, `#/desk/call` and
   `#/stream` are already keyed Haiku. Waits on spend.
3. **The 10-seed keyed sweep** (~$10, pinned `prompt_sha`) that would decide whether the widened
   corpus changes the diffuse win at the smaller seed count. Deferred deliberately.
4. **Arm B**: Nova Lite for the reader arm (~$0.01 alone, $0.28 both). Last item on
   `build-plan.md`'s "not measured" list. `extractor_cache_path()` is per-model, so it cannot
   pollute the cache behind the published reader figures. Waits on spend.
5. **Extend the reader-coverage sample** past n=20 per trajectory — samples nest, so
   `--per-trajectory 40` pays only the delta. The collections regression is the half most worth a
   bigger denominator. Waits on spend.
6. **Observability (W11, EMF)** and **the UI's write path** — both need the IAM fix first.

## Known-weak, stated rather than hidden

- **Decoys are planted WITH replacement, deliberately — and the note saying so was accidentally
  deleted on 2026-08-30 and is restored here.** Measured 2026-08-31 at 400 customers: **33 / 303
  customers carry the same fragment twice, 38 duplicate plantings, every one of them a decoy and
  none an arc.** This is the same mechanism `08b20cc` removed from the arc paths, and it is left in
  the decoy paths on purpose: a recurring accumulator decoy earns a corroboration bonus it does not
  deserve, which makes the trap *harder* and biases the result **against** the ledger. That is why
  one was a defect and this is not. It is still unrealistic — nobody says the same sentence twice
  verbatim — so Phase C of `../corpus/04-plan.md` should replace the repeat with a paraphrase rather
  than simply stop repeating.
- **"Diffuse" does not mean what the pitch implies, and this is measured.** Every arc customer
  carries a planted signal in **100% of their conversations** — verified 2026-08-31 at 800 customers:
  **431 / 431 arc customers, zero silent conversations.** So diffuse means *a weak signal every
  time*, not *signal with ordinary conversations in between*. The pitch's own story — frustration in
  March, a complaint in May, a threat to leave in July — implies quiet conversations between the
  loud ones, and the corpus contains none. The realistic case (a customer calls eight times, three
  of which matter) is untested, and a judge who asks "what about the noise?" is asking about a real
  gap. Fixing it moves every published number.
- **The generated prose is not conversational, and it is on the demo screen.** Measured over 1,400
  conversations: 1,210 repeat a line verbatim, 129 / 450 chats open "Thank you for **calling**",
  4,018 / 11,378 customer turns get no reply, and only 109 / 973 planted signals get a responsive
  agent turn. The agent's whole repertoire is 10 sentences. `ui/data.js` — the screen `ui/README.md`
  calls "the proof" — carries 36 transcripts of which 30 repeat a line and 13 / 23 non-call ones
  show speech-recognition noise that cannot exist in typed text. Work in progress on
  `wp/real-transcripts`.

- **`random-rank` is not clearly beaten on the stratum this entry is built for.** 17–11–2,
  `p=0.345` on diffuse arcs. The ledger's statistically solid wins are against *other* aggregation
  strategies, not against chance.
- **Whole-portfolio, full-ledger is 7th of 9 arms.** `stateless-max` (naive per-call scoring) wins
  outright at 0.138. Accumulation's case rests entirely on the diffuse stratum, not the average case.
- **The ranking order is not stable across review budgets.** At 1% `stateless-top2` leads and
  full-ledger is 6th of 9; at 10% `stateless-max` leads and full-ledger is 7th of 9. No single-budget
  table, including the 10% one this repo leads with, describes the arms in general.
- **That unbounded memory beats a cheap bounded window is unproven, and now doubly so.**
  `window3-top2` beat the ledger on the old corpus and loses on the new one — same mechanism,
  opposite corpus, opposite result each time.
- **The ledger loses cleanly on concentrated arcs** (0–30–0 or similar against four of the other
  eight arms). Published as a trade: run memory alongside per-call detection, not instead of it.
- **The offline lexicon's churn coverage (0.43, 30 / 70) is a pass-B gap and stays unfixed** — widening those
  cues to close a gap found by measuring against the answer key is exactly the tuning the build rules
  forbid.
- **The lexicon barely works on language it did not write anywhere** — 0.0357 strict recall (4/112)
  on real CFPB narratives, and now also 1/32 on fragments authored blind for the widened pools. The
  model reader scores 0.8214 (92/112) on CFPB at 8x the false-positive rate (0.1598 vs 0.0205).
- **The ledger hands the agent a queue that is 90% false alarm by construction** — 25 of 240
  crossings at a 10% budget have a real outcome.
- **`ui/data.js` is still the offline rule engine**, printed on screen, pending a keyed
  `earshot investigate` run that spend policy currently blocks.
- **A keyed run's cache is isolated by path but not by prompt hash across a resume** — the $12.32
  lesson. See handover.md's traps.
- **No AT ticket covers any of the eleven AWS work packages.** 45 issues live, 28 In Progress,
  0 Resolved, as of the last live read (2026-08-25).
