# Accuracy, cost and latency — Ear on Every Call

**Internal one-pager (deliverable ② of three).** Zenon Genesis 2026, Track A, team Agentic Trio.
Every figure below carries its denominator and names the run it came from. Where a number goes
against us it is printed anyway, because a reader who finds an unstated loss stops trusting the
stated wins.

**Reproduce any of it with no API key and no network** — the model responses are committed:

```bash
uv sync && uv run pytest                                # 812 tests
uv run earshot sweep --seeds 30 --customers 1500        # every recall figure and p-value
EARSHOT_CACHE_MODE=replay uv run python tools/verdict_accuracy.py \
  --provider bedrock --per-arm 25 --customers 2400      # the agent table
```

---

## 1. Reading a conversation

Claude Haiku 4.5 on Bedrock. Keyed run 2026-08-28, 150 CFPB complaint narratives, responses
committed for keyless replay.

| | measured |
|---|---|
| Cost per 1,000 conversations | **$1.66** ($0.24845 over 150) |
| Latency p50 / p95 | **1,244 ms / 2,212 ms** |
| Strict recall on real customer language | **0.8214 (92 / 112)** |
| False-positive rate | 0.1598 (78 / 488) |

**Against the offline fallback, on the identical gold set:** the 26-regex lexicon scores **0.0357
(4 / 112)** at a false-positive rate of 0.0205 (10 / 488). The model is ~23× better at finding real
signal and ~8× worse at firing where there is none.

**Why a regex fallback exists at all:** it needs no key, so a fresh clone runs the whole pipeline
offline. Every screen and every table labels which reader produced it. Offline numbers are never a
headline.

**One measured trade, stated because it is operational rather than technical.** Swapping the offline
reader for the model takes the Retention desk from **0 crossings to 9 of 20** — that desk received
nothing at all under the lexicon — and drops Collections from **4 to 1**. Choosing a reader decides
which desk you under-serve. One dataset, n=20 per trajectory; a direction with denominators, not a
sweep.

---

## 2. Investigating a crossing

Keyed run 2026-08-29, 50 crossings, Haiku 4.5 through Bedrock.

| | measured |
|---|---|
| Cost per case | **$0.0295** (50 cases, $1.4733; p95 $0.0357, max $0.0368) |
| Model latency p50 / p95 | **19.8 s / 24.7 s** |
| Model calls per case | 4–5 |
| Loop exits | `decided` **50 / 50** — no budget exhaustion, no step-limit hit |
| First-attempt evidence groundedness | **0 / 50 repairs** — every citation resolved on the first try |

**Cost ceiling:** $0.10 per case, derived from this measurement at ~2.7× the worst observed case.
A cap that cannot be reached is not a cap, so it was re-derived from data rather than guessed.

---

## 3. Is the agent right?

**No, mostly. It escalates rather than discriminates, and that is the headline result.**

50 crossings, sampled deliberately as 25 with a real downstream outcome and 25 without — the top of
the queue is nearly all true positives, so a sample drawn from it could not be wrong in the
direction that matters.

| | verdict `genuine` | verdict `false_alarm` | abstained |
|---|---|---|---|
| outcome present (25) | **18** | 6 | 1 |
| outcome absent (25) | **21** | **4** | 0 |

**Overall 22 / 50.** It catches 18 of 25 real cases and dismisses only **4 of 25** false alarms, at a
mean confidence of **0.86 on the answers it got wrong**.

**Routing is the half that works: 36 / 49 correct, 2 wrong, 11 declined.** Its failure mode is
declining to route rather than routing wrongly, which is the safe failure in a queue a human works.
Both wrong routes were unmoored from the evidence on hand rather than near-misses.

**So what the investigator buys today is routing and an audit trail, not filtering.** The queue it is
handed is ~90% false alarm by construction — 25 real outcomes in 240 crossings at a 10% review
budget — and the agent removes 4 of 25 of that noise. Any ROI case has to rest on triage and
evidence assembly, not on the agent shrinking the queue.

**Sampling caveat, disclosed:** the 50 are the highest-scoring 25 of each class, so the negatives are
the *hardest* false alarms in the queue. The true dismissal rate across the whole cut is likely
better than 4 / 25. The bias runs against us.

---

## 4. Does memory beat forgetting?

30 seeds × 1,500 customers, equal 10% review budget, paired by seed, exact two-sided sign test.

| comparison, diffuse arcs | record | p |
|---|---|---|
| full ledger vs score-each-call-and-forget *(pre-registered)* | **26–2–2** | **<0.001** |
| full ledger vs `stateless-top2` — sum the two loudest calls | **6–18–6** *(we lose)* | 0.023 |
| full ledger vs `window3-top2` — last three calls, best two | **5–21–4** *(we lose)* | 0.002 |

**The pre-registered headline holds and two cheaper baselines beat us on the same stratum.**
`window3-top2` holds strictly less state than a ledger and wins where the ledger is supposed to be
strongest. The honest claim is **aggregating a few conversations beats aggregating one** — not
*memory beats detection*. What never-discard buys over a bounded three-conversation window is
**unproven**.

**Why the corpus cannot yet settle it, and what that costs.** Customers average ~3.5 conversations,
so an arm that keeps the best two discards almost nothing. Widening the fragment pools on 2026-08-30
(8/8/4/4 → 14/14/14/14) lifted the arc ceiling and doubled planted evidence per customer; on that
corpus the ledger stops losing (4–1–1, 3–0–3, 1–1–4 across three settings of the spread parameter).
**Six seeds, not significant, and nothing is published from it.** The 10-seed keyed sweep that would
settle adoption has not been run.

**One objection, answered by measurement rather than argument.** *"Your diffuse stratum is defined by
the parameter that spread the evidence thin, so an aggregator winning there is arithmetic."* A
tenfold change in that parameter does not swing the comparison, on either corpus — pinned by
`test_the_diffuse_result_is_not_a_restatement_of_the_dirichlet_alpha`. The stratum sets how thinly
evidence is spread; what decides whether accumulation pays is **how many conversations there are to
accumulate over**, which is a claim about history depth and is measurable.

---

## 5. What is not measured

Listed because a checkable gap is worth more than a reassuring silence.

- **A second model arm.** Never run. ~$0.01 on Nova Lite closes an explicit promise in the submitted
  brief. Unmet through scheduling, not difficulty.
- **Retention lift against a matched control** — the anchor metric the brief names. Not computed, and
  **not currently computable**: the corpus has no intervention model, so a lift figure would measure
  targeting rather than retention. Construction is specified in `build-plan.md` §8.9.
- **ROC / PR curves and dev-split calibration.** Recall and precision are computed at four review
  budgets; only the 10% row is published.
- **Batch latency end to end.** Per-conversation reader latency is measured; a whole-portfolio
  nightly figure is not.

---

## 6. What the numbers are worth

**Load-bearing and reproducible:** reader cost and latency, investigator cost and latency, evidence
groundedness, the 30-seed recall comparison, CFPB recall on real language. All replay from committed
responses with no key.

**Directional, quoted with denominators, never as headlines:** reader-coverage-by-desk (n=20 per
trajectory, one dataset), the widened-corpus result (6 seeds).

**Known weak, published anyway:** the agent's 22 / 50 verdict accuracy; the ~90%-false-alarm queue;
the two cheaper baselines that beat the ledger on the pre-registered stratum; the offline lexicon's
0.0357 on real language.

*Figures current to 2026-08-30. `README.md` is the source of record; where this page and the README
disagree, the README is right.*
