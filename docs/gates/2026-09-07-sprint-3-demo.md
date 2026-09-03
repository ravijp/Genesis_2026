# Sprint 3 demo — 2026-09-07

**Ravi's script.** Written 2026-09-03 from what is measured and deployed on that date. Every number
below carries its denominator and is quotable as written; anything not in here is not ready to say
out loud. **Duration assumed 15 minutes** (the Sprint 1 slot), with §9 marking what to cut for 10 and
what to add for 20.

**The one sentence, if you only get one:** *every bank already reconciles each conversation to the
customer's current truth and throws away what did not clear the bar — we keep it, and re-score it
when the next conversation arrives.*

**The trap to avoid all the way through:** this idea was already judged a loser when framed as
single-call signal detection, which is commodity. **Every beat is about accumulation and retro
re-scoring.** If a question pulls you toward "how good is your classifier", answer it and steer back
to the ledger.

---

## 1. Beat sheet

| # | Beat | On screen | Proves | Time |
|---|---|---|---|---|
| 1 | The inversion | one slide, no product | originality 15 | 1:00 |
| 2 | **One customer, three conversations** | reviewer UI, ledger view | originality + depth | 3:00 |
| 3 | Who reads decides which desk exists | coverage table, then two live stages | Zenon impact 25 | 3:00 |
| 4 | It runs on real infrastructure | terminal + AWS console | **feasibility 25** | 3:00 |
| 5 | What we got wrong | one slide | technical depth 25 | 2:00 |
| 6 | Cost, and it reproduces | terminal | AI judge / eng quality | 2:00 |
| 7 | Close | — | — | 1:00 |

---

## 2. Beat 2 — the one that wins it

**This is the strongest thing in the repo and it has never been shown.** Open `CUST-0006` in the
ledger view. Three conversations, 73 days apart, one case.

| conversation | day | scored at write | retro delta | now |
|---|---|---|---|---|
| `CUST-0006-C0` | 21 | **0.1306** | **+0.5220** | load-bearing |
| `CUST-0006-C2` | 88 | 0.2872 | +0.3655 | contributing |
| `CUST-0006-C3` | 94 | 0.6527 | 0.0 | **crossed** |

Say, roughly:

> On day 21 this customer asked *"Can you tell me the very last day I can pay without a charge?"* Our
> reader scored it **0.13** against a cut of 0.60 — a fifth of the threshold. Every system in this
> market discards that, because it does not clear the bar and the customer's current state is fine.
> We wrote it down. Seventy-three days later a third conversation arrives, and that day-21 line is
> now the **load-bearing** piece of evidence in an open case. The `retro_delta` column is the system
> showing its work: what this scored then, what it scores now.

**Then say the part that makes it credible:** that record was not computed for the slide. It is what
`GET /cases/{id}` returned from DynamoDB on the deployed stack. Have the raw JSON one keystroke away.

**Why this beat and not a live-stream demo:** the live stream is prettier and proves less. This is
the only beat that shows the thing no competitor does.

---

## 3. Beat 3 — who reads decides which desk exists

Same 282 planted conversations, same ledger, same threshold, **one variable: who reads.**

| trajectory → desk | keyless lexicon | model reader |
|---|---|---|
| `complaint_escalation` → **Complaints** | **0 / 20** | **20 / 20** |
| `life_event` → **Vulnerability** | **0 / 20** | **19 / 20** |
| `churn_intent` → Retention | 1 / 20 | 16 / 20 |
| `financial_distress` → Collections | 9 / 20 | 10 / 20 |

> Two desks receive **nothing** under the cheap reader. Not fewer cases — none. The evidence was in
> the conversations the whole time; whether a desk exists at all is decided by whether anything can
> read them.

**Then land it on the deployed system, which is new and is the part nobody expects.** Two live
stages, same book, same infrastructure, one variable:

| | `dev` — keyless lexicon | `demo` — Haiku 4.5 |
|---|---|---|
| ledger entries | 34 | **103** |
| cases opened | 1 | **9** |
| desks receiving work | Collections only | **Complaints, 9 of 9** |

**Say the caveat before anyone asks:** the model column in the desk table is an **upper bound** — the
threshold is a top-K cut over the *offline* reader's ranking, held fixed so the arms stay comparable.
Deriving the model's own cut costs $13.96 and we did not spend it. Saying this first is worth more
than being caught by it.

---

## 4. Beat 4 — feasibility, which is 25 points and usually undefended

Run it. `tools/feed.py --stage dev` in a terminal, or show the recording if the room has no wifi.

Three things to say while it runs:

1. **It agrees with the local pipeline to the last digit.** The tool predicts the answer *before* it
   sends — deployed `0.6526618648909545` against local `0.652662` — and **exits non-zero** if the
   deployment disagrees. There is one scorer in the codebase and the Lambda delegates to it.
2. **At-least-once delivery cannot double-count.** Fed twice: **260 messages, still 34 ledger entries
   and 1 case.** The conditional write is what makes redelivery a no-op, and `DuplicateDeliveries 34`
   with `SignalsWritten 0` is the second run reporting exactly that about itself.
3. **The failure path is exercised, not asserted.** One malformed transcript: the record fails alone,
   its healthy neighbours commit, and `earshot-dev-ingest-failures` goes **OK → ALARM** while the
   other five stay OK. *Observed 2026-09-03.* The message then retries three times and moves to its
   dead-letter queue — the redrive is configured and the retry was in flight when we last looked,
   but **the DLQ arrival itself has not been watched end to end. Confirm it on 09-06 before saying
   it out loud**, or say "it is wired to dead-letter at three attempts" instead.

If asked what is *not* production-ready, answer without hedging: **one shared Lambda role instead of
per-function least privilege; no notification path, so alarms go red in a console and page nobody;
S3 Object Lock unavailable on this account so write-once evidence degrades to IAM; and the reviewer
UI is read-only, because a static page cannot sign an IAM Function URL.** That last one is a
deliberate choice — there is **no outbound contact surface anywhere in this system**, and human sign-off
is enforced by absence rather than by policy.

---

## 5. Beat 5 — what we got wrong

**Do not skip this to save time.** A stated loss buys more technical-depth credit than a clean sweep,
and every one of these is discoverable in the repo anyway.

- **The pre-registered headline died.** It went 29–0–1 to **15–13–2, `p=0.851`** when we rebuilt the
  corpus and found a bug that had been crippling the opponent. We re-registered (D-031), the new
  primary is 30–0–0, and **the dead row keeps its place in every table forever.**
- **The entry currently FAILS its own co-primary chance gate** — 18–8–4, `p=0.076`. We publish it as
  a failure. Chance is competitive because there is so little in the stream to rank, which is the
  coverage argument, not an excuse.
- **Our own ablation floor beat us**, until we found it was a tie-break artefact: 5 distinct scores
  across 1,500 customers meant 70.8% of its queue was ordered alphabetically. Randomised, it is
  11–13–6. We publish both records.
- **Routing got worse**, 36/49 → **27/48**, because the complaints desk is empty under the cheap
  reader so 43 of 48 cases are one desk. It ships as worse.
- **The cheaper model is better at finding and worse at citing.** Nova Lite: more evidence found
  (181/282 vs 177/282) at **1/16 the cost** — and 10 quotes that were not verbatim and 9 relocated,
  against Haiku's zero of each. That is why we pay 16×.

---

## 6. Beat 6 — cost and reproducibility

- **$1.58 per 1,000 conversations** read, p50 1,333 ms, 0 unparsable replies out of 282.
- **Everything replays with no API key and no network**, from committed caches — a miss raises rather
  than calling out, so a replay cannot spend.
- **903 tests, ruff clean, one command from a fresh clone.** The extractor is mechanically forbidden
  from importing the answer key, and there is a test that proves it.
- Total model spend across the whole build: **~$2.7 of a $12 budget.** ($2.42 through 2026-08-31,
  $0.0277 for the comparison-model arm, and ~$0.21 for the deployed model-reader run — that last one
  is projected from the published $1.58 per 1,000 rate over 130 conversations, not read off a meter.
  If you want the exact figure, it is in the `Earshot`/`CostUsd` CloudWatch metric for the `demo`
  stage.)

---

## 7. Fallback ladder — assume the room is hostile

| if | then |
|---|---|
| no wifi | the entire demo runs from `file://` with no server and no key (D-004). Beats 2, 3, 5, 6 are unaffected. |
| AWS unreachable | Beat 4 becomes a recording. **Record it on 09-06 and have it on the laptop.** |
| SSO token expired | it expires in hours, not days. **Re-login the morning of, and again before you walk in.** |
| laptop dies | the reviewer UI is 30 static routes; any machine with a browser runs it from the repo. |

**Rehearse Beat 2 and Beat 4 end to end at least once on 09-06.** Beat 4 is the only one with a live
dependency, and it is worth 25 points.

---

## 8. Questions to expect

**"Isn't this just signal detection?"** No — detection is one call in isolation and is commodity. The
claim is what happens to a signal that *fails* detection: it is kept and re-scored. Show the 0.13 row.

**"How do you know the model isn't just finding what you planted?"** The extractor cannot import the
generator — there is a test asserting it, over 45 modules. Ground truth is authored before the prose.
And the strongest reader number is on **real CFPB complaint narratives**, not our corpus: 0.8214
(92/112) against the lexicon's 0.0357 (4/112).

**"What does this cost at a real bank's volume?"** $1.58 per 1,000 conversations at today's reader.
Say the honest part: we have measured throughput to 15,000 customers and it degrades ~7× between 400
and 15,000. We have not optimised it and would flag it as the first thing to fix.

**"Why should we believe the accumulation math?"** It is deterministic Python, unit-tested, and never
the model. The model reads and judges; code counts and remembers. **239 of 485** multi-signal ledger
entries are worth more now than at write — under a plain count it is **0 of 485**.

---

## 9. Cutting to 10 minutes, or growing to 20

**Cut first:** Beat 6 (fold "$1.58 per 1,000, 903 tests, replays free" into the close) and the second
half of Beat 3. **Never cut Beat 2 or Beat 5** — Beat 2 is the only thing here nobody else has, and
cutting Beat 5 reads as hiding.

**If you get 20:** add the live-stream view showing the board re-ordering as conversations arrive,
and open one full case file with its evidence chain and the model's reasoning.
