# Accuracy, cost and latency — Ear on Every Call

**Internal one-pager (deliverable ② of three).** Zenon Genesis 2026, Track A, team Agentic Trio.
Every figure below carries its denominator and names the run it came from. Where a number goes
against us it is printed anyway, because a reader who finds an unstated loss stops trusting the
stated wins.

**Reproduce any of it with no API key and no network** — the model responses are committed:

```bash
uv sync && uv run pytest                                # the test suite
uv run earshot sweep --seeds 30 --customers 1500        # every recall figure and p-value
EARSHOT_CACHE_MODE=replay uv run python tools/reader_coverage.py \
  --reader both --per-trajectory 20                     # the desk table in §1
EARSHOT_CACHE_MODE=replay uv run python tools/verdict_accuracy.py \
  --provider bedrock --per-arm 25 --customers 2400      # the agent table in §4
uv run python tools/routing_accuracy.py                 # routing, zero model calls
```

---

## 1. Which review desks exist — the strongest result in the entry

**Measured 2026-08-31 on the shipping corpus, keyed Claude Haiku 4.5 on Bedrock, $0.445562.** The same
282 planted conversations, 20 customers per trajectory, both readers' signals through the **same**
`SignalLedger` at the **same** threshold and the same scoring config. One variable: who reads.

| Desk | crossed, offline lexicon | crossed, model reader |
|---|---|---|
| **Complaints** | **0 / 20** | **20 / 20** |
| **Vulnerability** (life event) | **0 / 20** | **19 / 20** |
| **Retention** (churn) | **1 / 20** | **16 / 20** |
| Collections (distress) | 9 / 20 | 10 / 20 |

**Two of four desks receive nothing at all under the keyless reader.** That is not an accuracy
percentage — it is whether a queue exists for a vulnerable customer to appear in. Coverage of planted
conversations moves **59 / 282 → 177 / 282** (complaint 0.02 → 0.92, life event 0.13 → 0.74, churn
0.21 → 0.52). Unplanted fires: 0 in all four families, both arms.

> **The model column is an UPPER BOUND. Do not present it without this.** The threshold (0.2753) is a
> budget-derived top-K cut over the **offline** reader's ranking of the corpus, held fixed across both
> arms so the arms stay comparable. A reader that finds more raises every customer's score, so the
> same 10% review budget would settle at a **higher** cut than this one. Deriving the model's own cut
> means a keyed pass over all 8,429 conversations — **$13.96**, not spent. The tool prints this line
> itself on every run.

**Where the model loses, on the same run.** `financial_distress` coverage is **0.38 (27 / 72) against
the lexicon's 0.46 (33 / 72)** — worse on the one family the lexicon was written for — and it pushes
**3 / 20 churn and 6 / 20 distress** customers over the line on a *different* signal family, so those
cases exist but arrive at the wrong desk. This is a differently-shaped reader, not a uniformly better
one, and choosing a reader is an operational decision about which desk you under-serve.

**Sample: n=20 customers per trajectory, one dataset, one seed.** A direction with denominators on it,
not a sweep. Samples nest (first N by `customer_id`), so doubling to n=40 re-reads nothing already
cached.

```bash
EARSHOT_CACHE_MODE=replay uv run python tools/reader_coverage.py --reader both --per-trajectory 20
```

---

## 2. Reading a conversation — cost, latency, fidelity

| | measured 2026-08-31 |
|---|---|
| Cost per 1,000 conversations | **$1.58** ($0.445562 over 282) |
| Latency p50 / p95 | **1,333 ms / 2,162 ms** |
| Unparsable replies | **0 / 282** |
| Relocated quotes | **0** — every citation stayed where the model put it |
| Signals emitted | 272 (1 quote dropped for not being a customer turn) |

Corroborated independently on the streamed deployment demo, re-recorded the same day: **$1.5256 per
1,000** over 130 conversations, p50 **1,230 ms**, p95 **1,786 ms**, 103 signals, 0 unparsable. Two
keyed measurements of the same reader at different sample sizes; neither is a projection.

**Strict recall on real customer language — 0.8214 (92 / 112)**, false-positive rate 0.1598
(78 / 488), against the offline lexicon's **0.0357 (4 / 112)** at 0.0205 (10 / 488) on the identical
gold set. The model is ~23× better at finding real signal and ~8× worse at firing where there is none.
**That measurement is on 150 real CFPB complaint narratives — an external, public-domain corpus — so
it does not move when ours does** and is not affected by the 2026-08-31 rebuild.

**Why a regex fallback exists at all:** it needs no key, so a fresh clone runs the whole pipeline
offline. Every screen and every table labels which reader produced it. Offline numbers are never a
headline.

---

## 3. Investigating a crossing

Keyed run 2026-08-31, 50 crossings, Haiku 4.5 through Bedrock.

| | measured 2026-08-31 |
|---|---|
| Cost per case | **$0.0306** (50 cases, $1.5305; p95 $0.0361, max $0.0384) |
| Model latency p50 / p95 | **20.8 s / 28.1 s** |
| Model calls per case | 4–6 |
| Loop exits | `decided` **50 / 50** — no budget exhaustion, no step-limit hit |
| First-attempt evidence groundedness | **0 / 50 repairs** — every citation resolved on the first try |

**Cost ceiling:** $0.10 per case, ~2.6× the worst observed case, re-derived from this measurement. A
cap that cannot be reached is not a cap, so it comes from data rather than a guess.

---

## 4. Is the agent right?

**Yes on a balanced sample, and this reverses what this page said for weeks.** 29 / 50.

50 crossings, sampled deliberately as 25 with a real downstream outcome and 25 without — the top of
the queue is nearly all true positives, so a sample drawn from it could not be wrong in the
direction that matters.

| | verdict `genuine` | verdict `false_alarm` | abstained |
|---|---|---|---|
| outcome present (25) | **16** | 9 | 0 |
| outcome absent (25) | 12 | **13** | 0 |

**Overall 29 / 50.** It catches 16 of 25 real cases and dismisses **13 of 25** false alarms, with
**0 abstentions**.

**Retraction, and the agent is not the reason.** This page published **22 / 50 with 4 / 25
dismissals** and the conclusion *"it escalates rather than discriminates, and that is the headline
result."* At 13 / 25 that conclusion is false. **Not one line of the agent changed.** The 2026-08-31
corpus rebuild stopped leaking the answer through surface form: decoys now **paraphrase** the real
signal instead of repeating it verbatim, quotes are no longer mangled as though through speech
recognition, and each arc coheres as one relationship. The old task was easier to pass in one
direction and noisier in the other. **A number that moves when the measurement gets more honest is a
fact about the measurement**, and we are not claiming a better agent.

**Confidence is not diagnostic.** Mean confidence is **0.837 on the 21 wrong verdicts against 0.852 on
the 29 right ones**. A reviewer cannot use the reported number to decide which verdicts to trust, and
no screen invites them to.

**Routing got worse — 27 / 48 correct, 2 wrong, 19 declined, down from 36 / 49 — and it ships as
worse.** The confusion matrix says why:

| truth \ routed | retention | collections | vulnerability | complaints | none |
|---|---|---|---|---|---|
| retention | **2** | 0 | 0 | 0 | 0 |
| collections | 0 | **22** | 1 | 1 | 19 |
| vulnerability | 0 | 0 | **3** | 0 | 0 |
| **complaints** | 0 | 0 | 0 | **0** | 0 |

**The `complaints` row is entirely empty** — no complaint customer ever crossed under the offline
reader (§1, 0 / 20), so no complaint case existed to route. The 48 scorable cases are **43 collections,
3 vulnerability, 2 retention, 0 complaints**, and all 19 declines sit in the collections row. This is
§1's coverage gap arriving through a second door, not an independent finding: routing is being graded
on a queue one reader's blind spots had already flattened onto a single desk. Both wrong routes matched
**neither** the seeded trajectory nor the ledger's own dominant signal at the crossing — unmoored from
the evidence on hand, not near-misses.

**So what the investigator buys is triage on a balanced sample, routing, and an audit trail — with a
human deciding every case.** The queue it is handed is ~90% false alarm by construction (25 real
outcomes in 240 crossings at a 10% review budget). Any ROI case rests on triage and evidence assembly
plus the coverage in §1, never on the agent alone shrinking the queue.

**Sampling caveat, disclosed:** the 50 are the highest-scoring 25 of each class, so the negatives are
the *hardest* false alarms in the queue. The true dismissal rate across the whole cut is likely better
than 13 / 25. The bias runs against us.

---

## 5. Does memory beat forgetting?

30 seeds × 1,500 customers, equal 10% review budget, paired by seed, exact two-sided sign test.

| comparison, diffuse arcs | record | p |
|---|---|---|
| full ledger vs `window3-top2` — last three calls, best two *(re-registered, D-031)* | **30–0–0** | **<0.001** |
| full ledger vs `stateless-top2` — sum the two loudest calls | **30–0–0** | **<0.001** |
| **full ledger vs `random-rank`** — a seeded RNG, ignores every signal *(chance gate)* | **18–8–4** | **0.076** |
| full ledger vs score-each-call-and-forget *(pre-registered 2026-08-09 — DIED)* | **15–13–2** | **0.851** |
| **full ledger vs `dumb-ledger`** — our own ablation floor | **7–18–5** | **0.043 (a loss)** |

**Read the last three rows first.** On the stratum this entry is built for the ledger is **not
statistically distinguishable from ranking customers at random**; the comparison pre-registered on
2026-08-09 **died** when the corpus was rebuilt on 2026-08-31, because a large part of that win was
measuring an opponent the old corpus had crippled; and our own ablation floor — every mechanism in
`memory.py` switched off — beats us here. All three are printed by `earshot sweep` itself.

**What does hold, and it is the originality claim:** the two arms that never discard a weak signal
rank **first and second of nine** on this stratum, and both capped-memory arms lose 30–0–0 under
both tie-break rules.

**Whole-portfolio, the ledger is 8th of 9 arms** at the 10% budget — recall 0.115 (665 / 5796) against
chance at 0.113 (657 / 5796) and a ceiling of 0.145. **On concentrated arcs it loses 0–30–0** to three
separate arms and does not beat chance there either (16–12–2, `p=0.572`).

**And these records reverse when the corpus changes.** They have now reversed twice, in both
directions, across two corpus rebuilds. Treat them as statements about a regime, not laws.

**The ablation loss, answered with two measurements rather than an argument.** `dumb-ledger` produces
**5 distinct scores across 1,500 customers**, so **70.8%** of its queue is decided alphabetically by
customer id; the full ledger produces 236 and 0.0%. Randomise the tie-break and the loss becomes
13–11–6, `p=0.839`. The harness that does this (`randomise_ties`, `random-rank`) landed in `04aa24a`
on 2026-08-30, the day *before* the loss existed, applies to all nine arms symmetrically, and the
deterministic record stays the default. Both records are published, always.

**The binding constraint is the reader.** The offline lexicon finds **617 of 2,700** planted signals
on our own prose, and leaves two of four review desks receiving no case at all. With a reader that
weak every arm crowds between 0.113 and 0.145, and no ranking strategy escapes it. That is why the
model reader's 0.8214 matters more than any row in this table.

**One objection, answered by measurement rather than argument.** *"Your diffuse stratum is defined by
the parameter that spread the evidence thin, so an aggregator winning there is arithmetic."* A
tenfold change in that parameter moves the ledger's record against `stateless-top2` by +4 / +8 / +9 —
a swing of 5 — pinned by
`test_the_diffuse_result_is_not_a_restatement_of_the_dirichlet_alpha`. The stratum sets how thinly
evidence is spread; what decides whether accumulation pays is **how many conversations there are to
accumulate over**, which is a claim about history depth and is measurable.

---

## 6. What is not measured

Listed because a checkable gap is worth more than a reassuring silence.

- **A second model arm.** Never run. ~$0.01 on Nova Lite closes an explicit promise in the submitted
  brief. Unmet through scheduling, not difficulty.
- **Retention lift against a matched control** — the anchor metric the brief names. Not computed, and
  **not currently computable**: the corpus has no intervention model, so a lift figure would measure
  targeting rather than retention. Construction is specified in `build-plan.md` §8.9.
- **ROC curves and dev-split calibration.** Recall and precision at four review budgets are now
  computed AND printed, with the arm ordering's instability across them stated in the output. A
  full ROC and a reliability diagram are still not built.
- **Batch latency end to end.** Per-conversation reader latency is measured; a whole-portfolio
  nightly figure is not.

---

## 7. What the numbers are worth

**All of it is on the shipping corpus, and all of it replays at zero API spend.** The 30-seed recall
comparison, extraction fidelity and retro re-score direction run keyless from a fresh clone. Every
keyed figure on this page — **both arms of reader-coverage-by-desk, reader cost and latency,
investigator cost and latency, evidence groundedness, verdict accuracy, routing accuracy, the streamed
demo** — was measured on **2026-08-31** against the corpus that ships, and replays from committed
responses with `EARSHOT_CACHE_MODE=replay`, where a cache miss raises rather than calling out. Nothing
on this page is a projection and nothing is corpus-historical.

**CFPB recall on real language (0.0357 vs 0.8214) is on an external corpus** — 150 public-domain
narratives, scored against a gold set committed before any narrative was read. It never touches our
corpus, so it does not move when ours does, and none of the above affects it.

**Known weak, published anyway:** the ledger does not beat chance on any stratum at 30 seeds
(18–8–4 `p=0.076` diffuse); the pre-registered headline died; our own ablation floor beats us on
diffuse under the default tie-break; **routing fell to 27 / 48 on a queue whose complaints desk is
empty**; the model reader's own threshold is unmeasured, so its coverage column is an upper bound; the
model reader is **worse than the lexicon on `financial_distress` coverage** (0.38 vs 0.46); the
~90%-false-alarm queue; the offline lexicon's 0.0357 on real language and 617 / 2,700 on our own.

*Sweep figures measured 2026-08-31. `README.md` is the source of record; where this page and the
README disagree, the README is right.*
