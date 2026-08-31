# Accuracy, cost and latency — Ear on Every Call

**Internal one-pager (deliverable ② of three).** Zenon Genesis 2026, Track A, team Agentic Trio.
Every figure below carries its denominator and names the run it came from. Where a number goes
against us it is printed anyway, because a reader who finds an unstated loss stops trusting the
stated wins.

**Reproduce any of it with no API key and no network** — the model responses are committed:

```bash
uv sync && uv run pytest                                # 817 tests
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
rank **first and second of nine** on this stratum, and both bounded-memory arms lose 30–0–0 under
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

## 5. What is not measured

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

## 6. What the numbers are worth

**Load-bearing and reproducible today, at zero API spend:** the 30-seed recall comparison, the
offline reader's coverage by desk, extraction fidelity, retro re-score direction. Every one of them
re-runs from a fresh clone with no key.

**Load-bearing but CORPUS-HISTORICAL — measured before the 2026-08-31 rebuild and not re-measured:**
reader cost and latency ($1.66 / 1,000, p50 1,244 ms), investigator cost and latency, evidence
groundedness (0 / 50), verdict accuracy (22 / 50), routing accuracy (36 / 49), the model arm of
reader-coverage-by-desk, the streamed demo. They replay from committed responses with no key, but they
replay what the model said about conversations the generator no longer produces in this shape.
Re-measuring needs a key; the AWS SSO token is expired and LLM spend is stopped.

**CFPB recall on real language (0.0357 vs 0.8214) is unaffected by any of this** — it is scored
against an external gold set of 150 public narratives and never touches our corpus. It is the one
number here that does not move when the corpus moves.

**Known weak, published anyway:** the ledger does not beat chance on any stratum at 30 seeds
(18–8–4 `p=0.076` diffuse); the pre-registered headline died; our own ablation floor beats us on
diffuse under the default tie-break; the agent's 22 / 50 verdict accuracy; the ~90%-false-alarm queue;
the offline lexicon's 0.0357 on real language and 617 / 2,700 on our own.

*Sweep figures measured 2026-08-31. `README.md` is the source of record; where this page and the
README disagree, the README is right.*
