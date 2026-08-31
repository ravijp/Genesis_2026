# Ear on Every Call

**A conversation signal layer that remembers every customer, across every conversation.**

Zenon Genesis 2026 · Track A (client-facing agentic AI) · Team **Agentic Trio** · synthetic data only

Banks run millions of customer conversations a year, and a customer tells you something is wrong long
before they leave. Today that signal is scored inside one call and archived. A customer can show
frustration in a chat in March, raise a complaint in May, and call to threaten leaving in July, and the
bank treats all three as separate events.

This system keeps a **standing per-customer signal ledger** that never discards a weak signal and
re-scores it as new conversations arrive — and when it crosses a threshold, an **agent investigates**
and hands a decision-ready case to a human. It never contacts a customer.

**New to this project?** Read [`docs/ORIENTATION.md`](docs/ORIENTATION.md) first — fifteen minutes,
assumes no prior context, and defines the vocabulary the rest of these documents use.

---

## Quick start — fresh machine

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13 (uv installs it for you).

```bash
git clone <repo-url> && cd Genesis_2026
uv sync                                                 # installs deps + the `earshot` package
uv run pytest                                           # the whole suite
uv run earshot sweep --seeds 30 --customers 1500        # the numbers below (~2 min)
uv run earshot demo --customers 3000                    # the accumulation moment, narrated
uv run earshot investigate --customers 200 --limit 3    # the agent working three cases
uv run earshot run --customers 400                      # one dataset, for debugging only
uv run earshot stream                                   # conversations arriving, turn by turn
```

**The demo opens from disk.** `open ui/index.html` — no npm, no server, no network. Where this
sits in a client's stack, a live arrival stream with the model's read forming turn by turn, the
reviewer queue, and every case with the quotes behind it. Details in [ui/README.md](ui/README.md).

**Every command above runs with no API keys and no network.** The offline provider is rule-based and
deliberately weaker than a model; its miss rate is measured and published. To use real models instead,
see [Model access](#model-access).

> `sweep` is the command that produces anything quotable. `run` executes a **single** dataset, where
> every recall is an integer over ~50 outcome customers and arms one or two customers apart look
> different but are not. It prints that warning itself.

---

## What it does

```
conversations ──▶ extract signals ──▶ per-customer ledger ──▶ threshold? ──▶ agent investigates ──▶ human decides
   (call/chat/     (with the quote     (append-only,             (re-scored     (tools: transactions,   (approve /
    complaint)      behind each)        never discards)           each batch)    accounts, cases)        dismiss / route)
```

One design rule runs through all of it: **code counts and remembers, the model reads and judges.**
Accumulation, decay and thresholds are plain deterministic Python, unit-tested and reproducible
bit-for-bit. Weighing ambiguous evidence is the model's job. A test enforces the boundary.

Full picture, with diagrams: **[docs/architecture/architecture.md](docs/architecture/architecture.md)**

---
## The honest state of the numbers

**The claim this entry makes, in one sentence.** Coverage and retention of evidence are what make an
at-risk customer visible to a bank; ranking is not. Between our two readers, strict recall on real
complaint narratives is **0.0357 (4 / 112) against 0.8214 (92 / 112)**, and on our own shipping
corpus the weak reader leaves **two of four review desks receiving no case at all and a third
receiving one in twenty** — while the model reader, over the identical 282 conversations and through
the identical ledger, takes **Complaints from 0 / 20 to 20 / 20 and Vulnerability from 0 / 20 to
19 / 20**. Of the nine ranking strategies we test, the two that never discard a weak signal rank
**first and second** on thin evidence, while the two arms that cap what they keep lose
**30–0–0 at `p<0.001`** — and every arm, ours included, sits inside a **0.113–0.145** band whose
floor is a seeded random number generator.

The order of this page follows from that: **the reader first, the ranking second.** Presented the
other way round, every arm looks crowded near chance for no stated reason. The desk table is
[one section down](#the-same-gap-on-our-own-corpus-and-what-it-does-to-the-desks).

**The corpus was rebuilt on 2026-08-31** (Phase C: arcs that read as one relationship — back-references
that are true, a promise schedule, real turn-taking, channel-correct language). It moved almost every
number here, killed the pre-registered headline, and is written up in
[`docs/corpus/06-phase-c-record.md`](docs/corpus/06-phase-c-record.md). Figures measured on the
corpus that preceded it are labelled **corpus-historical** at the point of use and are not current.

Every sweep figure below is **30 seeds × 1,500 customers — 5,796 outcome customers** — every arm
paired seed by seed, compared with an exact two-sided sign test.
`uv run earshot sweep --seeds 30 --customers 1500` reproduces all of it offline with no key, in 104 s
on the machine that produced this table.

**Every arm reads the same offline-lexicon signal stream.** `earshot sweep` runs the keyless 26-regex
fallback, prints `reader=offline-lexicon` in its own header, and stamps the provider into the artifact
manifest, so the source is never unlabelled. That reader is weak, the next section measures how weak,
and the arm-vs-arm comparison stays internally valid because every arm eats the identical stream.

---

## Part one: the reader, and which desks exist because of it

### Two readers, one gold set, real customer language

Both implementations of the `Extractor` protocol in [extract.py](src/earshot/extract.py) have been
scored against the same 150 hand-marked real CFPB complaint narratives (public domain, CC0), on the
same committed gold marks, at the same `(document, signal_type)` grain, by one scorer in one
execution.

| reader | strict recall | any-type recall | false-positive rate |
|---|---|---|---|
| offline lexicon, 26 regexes | 0.0357 (4 / 112) | 0.0964 (8 / 83) | **0.0205 (10 / 488)** |
| Claude Haiku 4.5 on Bedrock | **0.8214 (92 / 112)** | **0.9759 (81 / 83)** | 0.1598 (78 / 488) |

**Read the third column before the first two.** The model is roughly 8× worse on false positives, and
almost all of it is one signal type: `complaint_escalation` fires on **0.8072 (67 / 83)** of the
documents that should not carry it. It marks nearly every complaint as an escalation. Per type its
strict recall is complaint_escalation 0.9701 (65 / 67), financial_distress 0.8571 (18 / 21),
life_event 0.3636 (4 / 11), churn_intent 0.3846 (5 / 13) — two of the four types are still weak.

The 0.0357 measures the **26-regex fallback**, not the system: on real language it misses 96% of what
a model catches, `financial_distress`, `complaint_escalation` and `life_event` each scored **exactly
zero**, and 24 of its 26 cues never fired on any of the 150 documents. The sampling frame, the marking
guide, the gold set and the interpretation thresholds were all committed **before** any narrative was
read, and two failures of our own — a contaminated inter-marker comparison and a defect in the marking
guide — are disclosed in the write-up rather than smoothed over. Everything is in
**[benchmarks/cfpb/](benchmarks/cfpb/)**; `uv run python benchmarks/cfpb/steps/05_score.py` reproduces
every figure offline with no network.

This is the one measurement on this page that **does not move when our corpus moves**, because it does
not touch our corpus. It is why the reader, not the ranking, is the binding constraint.

*Corpus-historical: the Haiku row was measured on 2026-08-29 and the gold set is external and
unchanged, so this comparison stands. The synthetic-corpus recall the CFPB protocol cites separately
(0.681, 496 / 728) is from a corpus rebuilt twice since — see the dated note at the top of
`benchmarks/cfpb/PROTOCOL.md`.*

### The same gap on our own corpus, and what it does to the desks

`uv run python tools/reader_coverage.py --reader offline --per-trajectory 20 --customers 2400`,
measured 2026-08-31, free and offline. 2,400 customers, 8,429 conversations, 1,270 carrying a seeded
trajectory; 20 customers sampled per trajectory, 282 conversations. **The denominator is what was
planted**, never what was found.

| trajectory → desk | planted | found | ratio | best score | crossed |
|---|---|---|---|---|---|
| `churn_intent` → **Retention** | 77 | 16 | **0.21** | 0.4486 | **1 / 20** |
| `complaint_escalation` → **Complaints** | 65 | **1** | **0.02** | 0.0485 | **0 / 20** |
| `financial_distress` → Collections | 72 | 33 | 0.46 | 0.7218 | 9 / 20 |
| `life_event` → **Vulnerability** | 68 | 9 | **0.13** | 0.2681 | **0 / 20** |
| **total** | **282** | **59** | **0.209** | | **10 / 80** |

Threshold 0.2753, the budget-derived top-K cut. Unplanted fires: **0** in all four families.

**Two desks receive nothing and a third receives one case in twenty.** Complaints & Redress sees
1 of 65 planted complaint conversations. That is not a metric — it is whether a desk exists. A bank
buying this gets four queues; under this reader, one of them works.

**Nothing was tuned to cause this.** Phase C authored roughly 1,500 new customer sentences, reworded
six fragments, gated eleven and added five, in a pass whose author did not read the extractor's
vocabulary. The 26-regex lexicon was co-developed with the *old* prose. Make the prose realistic and
the lexicon stops working — which is the same result the CFPB benchmark already publishes against real
customer language (4 / 112), arriving from the other direction.

**It is published, not fixed — and the fix is not a wider lexicon.** Widening the cues to close a gap
discovered by measuring against the answer key is exactly the tuning `working-agreements.md` §1 exists
to prevent, and it would be visible in `git log`. Pass A and pass B are authored without reference to
each other on purpose; that independence is what makes the miss rate honest. The fallback stays as
weak as it measures. What closes the gap is the reader the system actually deploys, and the next
section measures exactly how much of it closes.

#### The same 282 conversations, read by the model — and this is the entry's strongest evidence

`--reader both --per-trajectory 20`, keyed Claude Haiku 4.5 on Bedrock, **measured 2026-08-31 on the
shipping corpus for $0.445562**. Identical conversations, identical `SignalLedger`, identical scoring
config, identical threshold. The only thing that changes is who reads.

| trajectory → desk | crossed, offline lexicon | crossed, model reader |
|---|---|---|
| `complaint_escalation` → **Complaints** | **0 / 20** | **20 / 20** |
| `life_event` → **Vulnerability** | **0 / 20** | **19 / 20** |
| `churn_intent` → **Retention** | **1 / 20** | **16 / 20** |
| `financial_distress` → Collections | 9 / 20 | 10 / 20 |

**Two desks that received nothing now receive nearly everything.** That is the whole claim of this
entry, measured: the evidence was in the conversations the entire time, and which desk exists is
decided by whether anything can read it. Coverage moves with it — the model finds
**177 / 282 planted conversations against the lexicon's 59 / 282** (complaint 0.92 vs 0.02, life event
0.74 vs 0.13, churn 0.52 vs 0.21).

**Read this before quoting the model column — it is an UPPER BOUND, and the tool prints so itself.**
The threshold (0.2753) is a budget-derived top-K cut over the **offline** reader's ranking of the
whole corpus, held fixed across both arms so the arms stay comparable. A reader that finds more raises
every customer's score, so the same 10% review budget would settle at a **higher** cut than this one.
Deriving the model's own cut means a keyed pass over all 8,429 conversations — **$13.96**, not spent.
The model column is therefore what this budget surfaces *at the offline cut*, not what a
model-thresholded deployment would surface. Never publish the row without this sentence.

**Where the model loses, on the same run.** Its coverage of `financial_distress` is **0.38 (27 / 72)
against the lexicon's 0.46 (33 / 72)** — worse, on the one family the lexicon was written to catch —
and it is only ahead on Collections crossings 10 / 20 to 9 / 20. It also pushes **3 / 20 churn and
6 / 20 distress customers over the line on a *different* signal family**, so those cases exist but
arrive at the wrong desk. This is a differently-shaped reader, not a uniformly better one.

Telemetry on the same 282 conversations: **$1.58 per 1,000 conversations** ($0.445562), p50
**1,333 ms**, p95 **2,162 ms**, 272 signals emitted, **0 unparsable replies, 0 relocated quotes**, one
quote dropped for not being a customer turn.

Replay both arms with no key and no spend — a cache miss raises rather than calling out:

```bash
EARSHOT_CACHE_MODE=replay uv run python tools/reader_coverage.py --reader both --per-trajectory 20
```

**n = 20 customers per trajectory, one dataset, one seed.** It is a direction with a denominator on
it, not an interval. Samples nest — first N by `customer_id` — so `--per-trajectory 40` re-reads
nothing already cached and pays only the delta.

### Extraction fidelity on our own prose

From `uv run earshot run --customers 1500` (`config=2d916ad3ceb0`, the same corpus configuration the
sweep uses). These describe the data and the extractor rather than comparing arms, so a single dataset
is appropriate; they are **not** comparison results and must not be quoted as such.

| | measured 2026-08-31 |
|---|---|
| Planted genuine signals | 2,700 |
| **Extraction recall** | **0.2285 (617 / 2,700)** — miss rate 0.7715 |
| Unplanted extractions | 296 |
| Portfolio outcome rate | 0.126 (189 / 1,500) |
| Conversations | 5,200, mean 3.47 per customer |

**Retraction, 2026-08-31.** This page published extractor recall as **0.659 (492 / 747)** for weeks.
That figure came from a 400-customer run on a corpus that no longer exists (`660dca4`) and it is wrong
by a factor of about **2.9** against the corpus that actually ships. The same measurement on today's
corpus reads 0.2285 at n=1,500 and 0.2308 (153 / 663) at n=400. Nothing was re-tuned; the prose got
more realistic and the lexicon stopped keeping up. Every claim that leaned on 0.659 is corrected on
this page.

Extraction is matched at conversation level — did the extractor find *this signal type in this
conversation* — not at character-span level.

The corpus plants two kinds of decoy and they are reported separately, because a firing means the
opposite thing in each: **extractor decoys** are lookalikes and firing on one is a mistake
(**0.0191, 9 / 470**); **accumulator decoys** are genuine weak signals that never amount to anything,
so firing is *correct* (**0.4871, 284 / 583**) and what is under test is whether the ledger goes on to
over-accumulate them — it does not, their flag rate at the 10% budget is 0.000.

---

## Part two: does memory beat forgetting?

### The floor: what chance looks like

**`random-rank` is a shipped arm.** It ranks customers by a seeded RNG, ignores every signal, and flags
exactly what the budget allows. It exists because *"does any of this beat chance?"* deserves an arm
rather than an assertion.

| Arm | Recall @10% | Hits / outcomes | Above chance |
|---|---|---|---|
| stateless-max *(score each call, forget)* | **0.145** | 841 / 5796 | +0.032 |
| long-context-3 *(last 3 conversations pooled)* | 0.136 | 791 / 5796 | +0.023 |
| hybrid *(rank-combined)* | 0.135 | 785 / 5796 | +0.022 |
| stateless-top3 *(sum the three loudest)* | 0.123 | 711 / 5796 | +0.010 |
| stateless-top2 *(sum the two loudest)* | 0.119 | 690 / 5796 | +0.006 |
| window3-top2 *(last 3, keep best 2)* | 0.119 | 689 / 5796 | +0.006 |
| dumb-ledger *(unweighted count)* | 0.118 | 686 / 5796 | +0.005 |
| **full-ledger** *(decay, corroboration, channel, escalation)* | **0.115** | **665 / 5796** | **+0.002** |
| **random-rank** *(chance)* | **0.113** | **657 / 5796** | — |

**The full ledger is eighth of nine on whole-portfolio recall at the 10% budget, two thousandths above
chance.** That is the most important line on this page, and it is one place worse than the seventh
this page reported before the rebuild. Everything below is a statement about *where* the ledger's
small edge lives — not a claim that the edge is large.

**Read the band, not the order.** Every arm sits between 0.113 and 0.145, and the floor of that band
is a random number generator. Part one is why: a reader that finds 617 of 2,700 planted signals leaves
very little in the stream to rank. No ranking strategy escapes a reader that weak.

### Diffuse arcs — where accumulation is supposed to pay

Evidence spread across conversations, nothing alarming in any single one.

| Comparison (diffuse, 30 seeds) | Record | p |
|---|---|---|
| vs `stateless-top2` | **30–0–0** | **<0.001** |
| vs `window3-top2` **(re-registered headline, D-031)** | **30–0–0** | **<0.001** |
| vs `hybrid` | 24–1–5 | <0.001 |
| vs `long-context-3` | 23–2–5 | <0.001 |
| vs `stateless-top3` | 21–1–8 | <0.001 |
| **vs `random-rank` (chance gate, D-031)** | **18–8–4** | **0.076** |
| vs `stateless-max` **(pre-registered 2026-08-09 — DIED 2026-08-31)** | **15–13–2** | **0.851** |
| **vs `dumb-ledger`** | **7–18–5** | **0.043 (a loss)** |

Diffuse recall is 0.151 (341 / 2265) against chance at 0.132 (299 / 2265).

**On the stratum this entry is built for, the ledger is not yet distinguishable from ranking customers
at random: 18–8–4, `p=0.076` at 30 seeds, identical under both tie-break rules.** It moved from
`p=0.345` to `p=0.076` when the corpus became more realistic. That is a direction, not a result, and we
do not claim it as progress — it is one corpus change.

A negative control landing mid-field (`random-rank` scores 0.132 in a field spanning 0.109 to 0.166)
is not evidence the mechanism is worthless. It is evidence there is **almost nothing in the stream to
rank** — 59 of 282 planted arc conversations found, and 1 of 65 complaint ones. Chance is competitive
because the signal is missing, not because memory does not work. Settling it costs a keyed sweep of
about **$10**; it is unspent because LLM spend is stopped by the owner's decision, not by a technical
block.

**What the ledger does win here is never-discard.** The two arms that never throw a weak signal away —
`dumb-ledger` and `full-ledger` — rank **first and second** of nine on diffuse recall (0.166 and
0.151). The two arms that cap what they keep — `stateless-top2` and `window3-top2` — lose 30–0–0.

### The pre-registered headline died, and what replaces it

The headline declared on 2026-08-09 was `full-ledger` vs `stateless-max` on diffuse recall. **It is
dead**, and it keeps its row above permanently rather than being deleted.

| | record | p |
|---|---|---|
| published, pre-rebuild corpus | 29–0–1 | <0.001 |
| **2026-08-31 corpus, deterministic tie-break (the default)** | **15–13–2** | **0.851** |
| 2026-08-31 corpus, randomised tie-break | 17–9–4 | 0.169 |

Dead under both tie-break rules, so the death is not a tie-break artefact.

**The cause is measured, not guessed.** `stateless-max`'s diffuse recall went 0.088 → 0.141 while
`full-ledger`'s barely moved (0.154 → 0.151). Before the rebuild, a diffuse customer's loudest
extracted signal was *anti*-correlated with their outcome — mean max confidence 0.320 for the outcome
group against 0.329 overall. It is now correlated: 0.341 against 0.292. **A large part of the
pre-registered win was measuring an opponent the old corpus had crippled.** That finding is worth more
than the win was, and it retires this page's former claim that "concentrating on the loudest call is
actively wrong on diffuse evidence" — it is not; that sentence was the artefact.

**The replacement (D-031): `full-ledger` vs `window3-top2` on diffuse recall, 30–0–0, `p<0.001`, under
both tie-break rules — bound to a co-primary chance gate the entry currently FAILS** (`random-rank`,
18–8–4, `p=0.076`). The claim holds only if both pass. As of 2026-08-31 the primary passes and the
chance gate does not.

`window3-top2` was chosen over `stateless-top2` — also 30–0–0 — because it is the only arm bounded in
**both** time and capacity, making it the literal negation of the never-discard claim D-006 narrowed
the novelty to. We did not pick the largest record available; `dumb-ledger` vs `window3-top2` is
29–0–1 and `long-context-3` vs `window3-top2` is 24–0–6. **State the weakness out loud:** the
replacement was chosen from a matrix already visible, which is the shape of p-hacking. The mitigations
are mechanical and checkable — the dead row stays, we picked the arm matching the stated mechanism
rather than the biggest number, we bound ourselves to a gate we fail, and an unseen experiment (the
silence-permitting corpus in `docs/corpus/04-plan.md`) is pre-registered now as a declared second arm
published beside the first, never a substitution. Full reasoning and rejected alternatives: **D-031**
in [`docs/ops/decisions.md`](docs/ops/decisions.md).

### Our own ablation floor beats us on diffuse, and we publish both records

`arms.py` pre-declared the standard in its own docstring: *"`dumb-ledger` — the floor the full ledger
has to clear: if it ties the full ledger, every mechanism in `memory.py` is decoration."* It does not
tie. It wins.

| `dumb-ledger` vs `full-ledger`, diffuse, 30 seeds | record | p |
|---|---|---|
| deterministic tie-break (`customer_id`, the default) | **18–7–5** | **0.043** |
| randomised tie-break (independent seeded RNG) | 13–11–6 | 0.839 |

Pooled, deterministic: `dumb-ledger` 0.166 (377 / 2265) against `full-ledger` 0.151 (341 / 2265).

**Why.** `dumb-ledger` produces **5 distinct scores across 1,500 customers**, so **70.8%** of its alert
queue is decided alphabetically by customer id — and ids are assigned in generation order. The full
ledger produces **236** distinct scores and **0.0%** of its queue is tie-decided. `earshot sweep`
prints this table itself:

| arm | distinct scores | queue decided alphabetically |
|---|---|---|
| full-ledger | 236 | **0.0%** |
| random-rank | 796 | 0.0% |
| hybrid | 213 | 0.6% |
| long-context-3 | 52 | 7.7% |
| stateless-top2 · stateless-top3 · window3-top2 | 49 · 65 · 49 | 15.7% · 15.8% · 15.8% |
| stateless-max | 15 | 42.9% |
| **dumb-ledger** | **5** | **70.8%** |

**The full ledger's own queue is never tie-decided** — 0.0% in the table above — so the tie-break
rule cannot change which customers it flags. Both D-031 gates print identical records under both
rules (30–0–0 and 18–8–4; `random-rank` is also tie-free at 0.0%). The two comparisons that *do*
move are exactly the ones whose **opponent** is heavily tie-decided: `stateless-max` at 42.9%
(15–13–2 → 17–9–4) and `dumb-ledger` at 70.8% (18–7–5 → 13–11–6).

**This is not tuning until it wins, and the git history is the proof a reader should check.**
`randomise_ties` and `random-rank` landed together on 2026-08-30 in `04aa24a`, the day *before* the
rebuild produced this loss. `dumb-ledger` has existed since 2026-08-09 (`fdcfc79`). The harness
predates the finding, it is applied to all nine arms symmetrically, **the deterministic record stays
the default**, and both records are published side by side, permanently.

**The cost, stated: on recall the four mechanisms buy nothing measurable.** They tie a plain count
under a fair tie-break and lose under the default one. What they buy is a queue that is rankable at
every budget, invariance to the tie-break rule, and one thing a plain count cannot do at all — see the
next paragraph.

**They are the only way retro re-scoring exists at all.** `uv run python tools/retro_direction.py
--customers 1500`, free and offline, over every multi-signal ledger entry — comparing each entry's
**marginal contribution** on the day it landed against its marginal contribution today:

| config | entries | worth **more** now | worth less | unchanged | max gain |
|---|---|---|---|---|---|
| `full-ledger` | 485 | **239** | 25 | 221 | 0.1861 |
| `dumb-ledger` | 485 | **0** | 264 | 221 | 0.0000 |

With every multiplier off the score is `1 − exp(−saturation · n)`, which is concave, so an entry's
marginal contribution can only shrink. *"March is worth more because of June"* — the submitted
brief's stated heart, the demo's centrepiece, and the observable the build rules require to be
*observable rather than asserted* — **cannot happen at all** under an unweighted count. It is 0 of
485 by construction, not by parameter: no half-life or bonus value changes it.

**The falsifier, so this is not an unfalsifiable excuse.** Either of these removes the machinery: a
formulation with no corroboration, cross-channel or escalation multiplier that still makes an earlier
entry's contribution rise; or a run at a larger seed count, or on the silence-permitting corpus, where
`dumb-ledger` beats `full-ledger` on diffuse recall **under the randomised tie-break**. Today it does
not (13–11–6).

### Concentrated arcs — where the ledger loses

A clean sweep of losses, published because it is the same run:

| Comparison (concentrated, 30 seeds) | Record | p |
|---|---|---|
| vs `stateless-max` | **0–30–0** | <0.001 |
| vs `long-context-3` | **0–30–0** | <0.001 |
| vs `hybrid` | **0–30–0** | <0.001 |
| vs `stateless-top3` | 0–28–2 | <0.001 |
| vs `stateless-top2` | 1–28–1 | <0.001 |
| vs `window3-top2` | 1–28–1 | <0.001 |
| vs `random-rank` | 16–12–2 | 0.572 |
| vs `dumb-ledger` | 19–8–3 | 0.052 |

Accumulation dilutes a single decisive signal. **The ledger does not beat chance here either** —
16–12–2 at `p=0.572`. This page previously claimed it did; that claim is retracted. Losing to
per-call detection on the stratum per-call detection is built for is the argument for running a memory
*alongside* it rather than instead of it.

### The ranking is not stable across operating points

`earshot sweep` evaluates every arm at 1%, 2%, 5% and 10% review budgets and reports whether the order
holds. **It does not:**

```
1%:  long-context-3 > stateless-max > stateless-top3 > window3-top2 > stateless-top2 > full-ledger (6th of 9)
10%: stateless-max > long-context-3 > hybrid > … > dumb-ledger > full-ledger (8th of 9)
```

`random-rank` is last at every budget — 1%, 2%, 5% and 10% — which is the sanity check that the control
behaves. Any table quoting a single budget, including the one above, is one slice of an unstable
ranking, and the command says so in its own output rather than letting a reader assume the order is a
property of the arms.

### What this adds up to

**Won, on diffuse arcs: unbounded memory beats a cheap bounded window.** 30–0–0 at `p<0.001` against
`window3-top2` and against `stateless-top2`, under both tie-break rules. This page called that
*unproven* for weeks; it is proven on this stratum, and correcting an underclaim matters as much as
correcting an overclaim.

**Lost, on concentrated arcs: 1–28–1** to the same bounded window. **Not proven whole-portfolio:**
9–17–4, `p=0.169`. All three directions are now measured, and the honest summary is the whole triple,
not the first line of it.

**Retracted: "aggregating a few conversations beats aggregating one."** The arm that aggregates one
(`stateless-max`) now ties us on diffuse (15–13–2) and beats us on the whole portfolio (1–28–1
against us). That sentence was produced by the pre-rebuild corpus and the rebuilt corpus refutes it.

**Not yet beaten: chance.** 18–8–4, `p=0.076` on diffuse; 13–11–6, `p=0.839` whole-portfolio;
16–12–2, `p=0.572` on concentrated. The ledger does not beat a seeded RNG on any stratum at 30 seeds.

**The binding constraint is the reader, not the ranking.** Everything in this part sits in a
0.113–0.145 band because part one's reader finds 617 of 2,700 planted signals. That is why the model
reader's **0.8214 (92 / 112)** on real customer language matters more to this product than any row
above.

**Precision says nothing recall does not.** The precision matrix is byte-identical to overall recall —
same records, same p-values — because at an equal alert budget every arm flags the same count, so both
metrics rank on hits alone. Printed anyway, with that note, because a reader is entitled to check
rather than take it on trust.

**Multiplicity.** `earshot sweep` runs **144** pairwise tests with no correction and prints every one.
Exactly one comparison was declared before any of them was seen — the 2026-08-09 headline, which died.
The 2026-08-31 replacement was chosen from a matrix already visible and is a **re**-registration, said
so plainly in D-031. Any other single `p` under 0.05 is a hint, not a result.

> **What the four mechanisms buy is ranking resolution, and the set is measured while the members are
> not.** `dumb-ledger` switches decay, corroboration, cross-channel weighting and escalation off
> together and drops from 236 distinct scores to 5, and from 0.0% to 70.8% of its queue decided
> alphabetically. That justifies the *set*. Which member earns its keep is **not measured on this
> corpus** — `mechanism_ablations()` in `arms.py` already exists and printing its tie-share is free
> and offline. This page previously attributed the resolution to decay rather than confidence
> weighting on the strength of a corpus that no longer exists; that attribution is withdrawn.

> **Two earlier retractions, kept.** (1) A first version of this table came from a single 400-customer
> run with 39 outcome customers, where every rate was an integer over 39 — differences of one customer,
> inside binomial noise, written up as findings. (2) That corpus also gave every decoy and clean
> customer a latent risk of exactly `0.0` while every real arc was `≥0.55`, which made the risk value a
> lossless encoding of the answer key and leaked it into the agent's account tool. Both are fixed.

---

## Part three: the agent

> **Re-measured 2026-08-31 on the shipping corpus.** Every figure in this part is current, keyed
> Claude Haiku 4.5 through Bedrock, and replays from the committed cache with no key. One conclusion
> changed direction and it is called out where it sits.

All from keyed runs, Claude Haiku 4.5 through Bedrock, every response committed for keyless replay.

| | measured 2026-08-31 |
|---|---|
| Reader, cost per 1,000 conversations | **$1.58** ($0.445562 over 282) |
| Reader latency | p50 **1,333 ms**, p95 **2,162 ms** |
| Investigation, cost per case | **$0.0306** (50 cases, $1.5305; p95 $0.0361, max $0.0384) |
| Investigation latency, model time | p50 **20.8 s**, p95 **28.1 s** |
| Evidence repairs (first-attempt groundedness) | **0 / 50** |
| Loop exits | `decided` 50 / 50 — no `cost_cap`, no `max_steps`; 4–6 model calls per case |

**AT-57: the agent discriminates, and that is a change of conclusion.** Fifty crossings — 25 with a
real outcome and 25 without — sampled deliberately, because the top of the queue is nearly all true
positives and a run drawn from it cannot be wrong in the direction that matters:

| | verdict `genuine` | verdict `false_alarm` | abstained |
|---|---|---|---|
| outcome present (25) | **16** | 9 | 0 |
| outcome absent (25) | 12 | **13** | 0 |

It caught 16 of 25 real cases and dismissed **13 of 25** false alarms, with **0 abstentions**.
**Overall 29 / 50.**

**This retracts a conclusion this page carried for weeks, and the agent is not the reason.** On the
previous corpus the same tool read **22 / 50 with only 4 / 25 dismissals**, and the honest sentence
next to that was *"the agent does not discriminate — it escalates rather than filters."* At 13 / 25
dismissals that sentence is no longer true. **Not one line of the agent changed.** What changed is the
corpus: the 2026-08-31 rebuild made decoys **paraphrase** the real thing instead of repeating it
verbatim, stopped mangling quotes as though through speech recognition, and made each arc cohere as one
relationship. The old corpus was leaking the answer through surface form — a verbatim decoy is a
different task from a paraphrased one — and the agent was being marked on a test that was easier than
it looked in one direction and noisier in the other. **A number that moves when the measurement gets
more honest is a fact about the measurement.** We are not claiming an improved agent.

29 / 50 is still 50 cases on one dataset. It is a result, not an interval. And **confidence is not
diagnostic**: mean confidence is **0.837 on the 21 wrong verdicts against 0.852 on the 29 right ones**.
A reviewer cannot use the number the model reports to decide which verdicts to trust, and no screen in
this system invites them to.

Replay it with no credentials and no network:

```bash
EARSHOT_CACHE_MODE=replay uv run python tools/verdict_accuracy.py   --provider bedrock --per-arm 25 --customers 2400
```

That reproduces 29 / 50 and $1.5305 from the committed cache, and it writes to a **separate**
`-replay` artifact rather than over the recorded one. Both of those are scar tissue: a failed replay
once overwrote the keyed run it was replaying — same seed, same config hash, same provider, same
filename — and `config_hash` turned out not to cover the *code* that turns a seed into a queue, so
manifests now also carry a `pipeline_sha`.

**AT-58 routing got worse, and the confusion matrix says why.** Each customer carries a seeded
`trajectory`, so a correct owning team exists; `tools/routing_accuracy.py` grades the `owning_team` the
investigator already recorded, making **zero further model calls**. On the same 50 cases:
**27 of 48 routed to the right team, 2 wrong, 19 declined** (`owning_team="none"`). On the previous
corpus this read 36 of 49 correct, 2 wrong, 11 declined. **It is worse and we publish it as worse.**

| truth \ routed | retention | collections | vulnerability | complaints | none |
|---|---|---|---|---|---|
| retention | **2** | 0 | 0 | 0 | 0 |
| collections | 0 | **22** | 1 | 1 | 19 |
| vulnerability | 0 | 0 | **3** | 0 | 0 |
| **complaints** | 0 | 0 | 0 | **0** | 0 |

**The `complaints` row is entirely empty, and that is the same failure as part one seen from the other
side.** No complaint customer ever crossed the review threshold under the offline reader — 0 / 20 in
the desk table — so no complaint case existed for the agent to route, correctly or otherwise. The 48
scorable cases are **43 collections, 3 vulnerability, 2 retention, 0 complaints**: a routing figure
measured on a queue that one reader's coverage gap had already flattened onto a single desk. The
declines are the same story — all 19 sit in the `collections` row. Fix the reader and this number is
measured on a different, harder distribution; it is not a number that improves by leaving the reader
alone.

Both wrong routes are the bad kind: **0 / 2 matched the ledger's own dominant signal at the crossing**,
so neither was an evidence-consistent mistake — they were unmoored from the evidence on hand. Two of
the 50 cases are decoy-accumulator customers with no seeded trajectory: no correct team exists for
them, so they are reported separately (1 routed anyway at confidence 0.78, 1 declined) and never enter
the denominator.

Read together, the two results still say the investigator is a **router and an audit trail, not a
filter** — but the reason has changed. It is no longer that it escalates everything; at 13 / 25
dismissals it does discriminate. It is that a human decides every case either way, and that routing is
graded on a queue the reader has already narrowed to one desk.

The D-025 cost argument for Haiku is **better supported than it was and still not settled**: at
$0.0306 per case it is cheap and it is fast, and it now sorts both arms of a balanced sample rather
than escalating everything. What is missing is the comparison that would actually settle it — the same
50 cases through a second model, which has never been run.

**One more number, corpus-historical:** of the 240 customers the ledger surfaced at a 10% review budget
over 2,400, **25 had a real outcome and 215 did not** — the ledger's own precision at the cut, and what
makes the agent's job hard. It is handed a queue that is **roughly 90% false alarm by construction**
and asked to sort it. Not re-measured since the rebuild.

**Still not measured:** any of this at a sample size worth a confidence interval — 50 cases on one
dataset is a result, not an interval — a second model through the same harness, and **routing on a
queue whose complaints desk is not empty**, which needs the model reader in front of it.

**Provider-historical, superseded by D-025 (2026-08-25):** two live Claude Sonnet 4.5 investigations,
recorded via OpenRouter on 2026-08-09, cost **$0.089 and $0.097** and took 30.3s and 33.4s — the only
live-model cost/latency this repo has ever measured for the investigator, kept as a data point rather
than deleted. **They no longer replay.** `artifacts/cache/investigator-demo.jsonl` is keyed on
`prompt_sha`, and the investigator prompt changed twice after the cache was recorded (`7229b70`,
`80c0914`); D-025 also moved both reader and investigator to Bedrock Haiku 4.5, which changes the
model string regardless. The old replay command now cache-misses and prints `provider_error` instead
of reaching the network, so it is not reproduced here.

### The streamed demo — re-recorded 2026-08-31 on the shipping corpus

One synthetic deployment, read end to end by Claude Haiku 4.5 on Bedrock. Every figure is counted
from the run, and the whole thing replays from the committed cache with no key.

| | |
|---|---|
| Conversations read | 130, across 44 customers over 178 days |
| Signals kept | 103 |
| Threshold crossings | 9 (fixed cut at 0.60) |
| Cases worked by the agent | 6 of 9 |
| Reader, one call each | 130 conversations · **$0.1983** · p50 **1,230 ms** · p95 **1,786 ms** |
| Reader, cost per 1,000 conversations | **$1.5256** |
| Re-read turn-by-turn | 6 of those conversations · 32 further calls · **$0.0474** |
| Agent investigations | 6 · **$0.2335** ($0.0389 per case) |
| **Total** | **$0.4792** |

**0 unparsable replies** across all 130 reads. The $1.5256 per 1,000 here and the $1.58 per 1,000 in
part one are two independent keyed measurements of the same reader on the same corpus at different
sample sizes (130 and 282 conversations); neither is a projection.

#### Reading a call while it is still open

Six conversations were read *again after each customer turn*, on the transcript heard so far, so a
belief can be watched forming rather than arriving finished. On `CUST-0008-C3`:

| After | Reader believes | Movement |
|---|---|---|
| 2 turns | `complaint_escalation` 0.75 | appeared |
| 4 turns | `complaint_escalation` 0.72 | faded |
| 6 turns | `complaint_escalation` 0.72 | requoted |
| 8 turns | `complaint_escalation` 0.78 | firmed, requoted |
| 10 turns | `complaint_escalation` 0.78 | requoted |
| 12 turns | `complaint_escalation` 0.78 | requoted |
| 13 turns | `complaint_escalation` 0.78 | |

Across the six: **7 appeared, 9 firmed, 1 faded, 4 requoted** (the model moves its citation to better
evidence) **and 0 withdrawn.** The browser does not decide any of that — `read_live._diff()` does, in
Python, and the page animates the result.

**Withdrawal did not occur in this recording, and the previous one is where the claim came from.** The
pre-rebuild recording produced 3 withdrawals — the model retracting a signal outright after hearing
more — and this page used to cite them as evidence that every movement type occurs in real output. On
the shipping corpus it does not: the arcs cohere, so a belief formed early is rarely contradicted
later. The `withdrawn` path is still implemented and still tested; it is simply not exercised by these
six conversations, and 6 conversations is too small a sample to conclude anything else from that.

Two properties make it a measurement rather than theatre, both tested: the model is handed a
genuine **prefix**, never the full transcript with a smaller number attached; and the final step's
request is byte-identical to the batch read, so under a content-addressed cache they are one entry.
That second one is the guarantee that the belief at the end of the animation is the belief that was
appended to the ledger.

Four things that must be said next to those numbers, not after them:

- **The threshold is a fixed cut, not the budget-derived one** the rows above this section use. A
  streaming consumer sees one conversation at a time and has no population to rank against, so it
  cannot take the top 10% of anything. This mirrors `aws/ingest.py`, the deployed path. The two
  numbers disagree about who crossed; they are labelled apart on every screen.
- **Only 6 of 9 crossings were investigated**, to bound the cost of a re-record, and only 6 of 130
  conversations were read turn-by-turn, because that costs a call per customer turn. Both
  denominators are on the screen, not inferable from it.
- **Routing on this deployment is not accuracy-measured, and what it shows is not flattering.** The
  agent concentrates its routing and sometimes returns `owning_team: "none"`. That is on the
  deployment screen because it is a finding, and AT-58 measures the same behaviour properly on 48
  scorable cases: **27 correct, 2 wrong, 19 declined**.
- **There is no speech recognition anywhere in this system.** The transcripts are generated text,
  and a bank at this size already transcribes for QA and compliance — that is the seam we consume,
  not one we build. What the stream replays faithfully is the *arrival pattern*, and at 1× each
  frame is held for the reader's own measured latency on that conversation. `manifest.asr` says
  `none`, every screen prints it, and the UI smoke test fails the build if it ever says otherwise.

---

## Model access

Runs three ways:

| Provider | How | Use |
|---|---|---|
| `offline` (default) | nothing needed | CI, tests, and a demo in a room with no wifi |
| `--extractor model` | a key, on `run` and `sweep` | Reads every conversation with a model instead of the regex lexicon. Never the default; refuses on other commands |
| `openrouter` | `EARSHOT_OPENROUTER_API_KEY`, or `EARSHOT_OPENROUTER_API_KEY_FILE=<path>` | Real models. Default `anthropic/claude-sonnet-4.5` |
| replay | `EARSHOT_CACHE_MODE=replay` | Replays committed responses from `artifacts/cache/` — real model output, zero network |

Keys are never committed and never logged. See `.env.example`.

---

## Repository

**[docs/INDEX.md](docs/INDEX.md) is the file map** — one line per file, kept current in the same commit
as any change. This section used to repeat it and had already drifted; a map in two places is a map
that disagrees with itself.

The four things worth knowing before you read any of it:

- **`src/earshot/`** — the product. `corpus.py` and `memory.py` are the deterministic core: generation,
  the signal ledger, the re-scoring maths. No model touches them.
- **`src/earshot/agent/`** — the investigator: bounded loop, five pure tools, decision schemas with
  mandatory evidence. This is the part that makes it Track A rather than analytics.
- **`tests/`** — two guards worth naming. `test_separation.py` proves no module on the decision path can
  *import* the answer key, and `test_no_answer_key_leak.py` proves it cannot be recovered statistically
  from what the tools return. Both discover their own surface by glob, so new files are covered without
  editing the test.
- **`prompts/`** — versioned files, so a prompt change is a reviewable diff. Their sha goes into the
  response-cache key, which is what makes "this recorded answer came from this prompt" checkable.
- **`ui/`** — five static screens, no build step, and the demo runs from `file://`. `stream.py`,
  `read_live.py` and `tenants.py` behind them add the arrival stream, the turn-by-turn read, and the
  per-client configuration layer. `earshot stream --serve` runs the same loop over SSE on localhost
  so the model calls happen while a room watches.

---

## Competition context

Judging: Zenon impact 25 · technical depth 25 · feasibility & production readiness 25 · originality 15 ·
presentation 10, plus an AI judge scoring engineering quality. Gates: **2026-08-10** check-in ·
**2026-08-24** combined Sprint 1+2 demo · **2026-09-07** Sprint 3.

All data is synthetic, generated with ground truth authored *before* the text, per competition rules.
No client data of any kind is used anywhere in this repository.
