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
uv run earshot sweep --seeds 10 --customers 1500        # the numbers below (~30s)
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

The harness was built to *test* the claim, not illustrate it. Every figure below is **30 seeds ×
1,500 customers — 5,834 outcome customers** — every arm paired seed by seed, compared with an exact
two-sided sign test. `uv run earshot sweep --seeds 30 --customers 1500` reproduces all of it offline
with no key, in about 70 seconds.

**Regenerated 2026-08-30**, on a corpus whose fragment pools were widened from 8/8/4/4 to
14/14/14/14. That lifted the arc ceiling — two of four trajectories previously capped at 4 signals,
and their later conversations were empty by construction — and it moved almost every number on this
page, several of them across zero. The previous corpus and its records are in git.

**Every row reads the same offline-lexicon signal stream.** `earshot sweep` runs the keyless 26-regex
fallback, prints `reader=offline-lexicon` in its own header, and stamps the provider into the
artifact manifest, so the source is never unlabelled. That reader is weak in absolute terms and got
**weaker** on this corpus: of the 32 fragments authored for the widened pools — in a pass whose
author never saw the extractor's vocabulary — it finds **1**. Of the original 24 it finds 21. The
arm-vs-arm comparison stays internally valid because every arm eats the identical stream, but hold
that 1-of-32 in mind, because it explains the shape of everything below.

### The floor: what chance looks like

**`random-rank` is a shipped arm.** It ranks customers by a seeded RNG, ignores every signal, and
flags exactly what the budget allows. It exists because *"does any of this beat chance?"* deserves an
arm rather than an assertion.

| Arm | Recall @10% | Hits / outcomes | Above chance |
|---|---|---|---|
| stateless-max *(score each call, forget)* | **0.138** | 806 / 5834 | +0.029 |
| hybrid *(rank-combined)* | 0.129 | 754 / 5834 | +0.020 |
| long-context-3 *(last 3 conversations pooled)* | 0.129 | 751 / 5834 | +0.020 |
| stateless-top3 *(sum the three loudest)* | 0.121 | 705 / 5834 | +0.012 |
| window3-top2 *(last 3, keep best 2)* | 0.120 | 698 / 5834 | +0.011 |
| stateless-top2 *(sum the two loudest)* | 0.119 | 697 / 5834 | +0.010 |
| **full-ledger** *(decay, corroboration, channel, escalation)* | **0.119** | **695 / 5834** | **+0.010** |
| dumb-ledger *(unweighted count)* | 0.112 | 655 / 5834 | +0.003 |
| **random-rank** *(chance)* | **0.109** | **633 / 5834** | — |

**The full ledger is seventh of nine on whole-portfolio recall, one point above chance.** That is the
most important line on this page. Everything below is a statement about *where* the ledger's small
edge lives — not a claim that the edge is large.

### Where the ledger wins: diffuse arcs

On diffuse arcs — evidence spread across conversations, nothing alarming in any single one — the
ledger beats **every** baseline at 30 seeds:

| Comparison (diffuse, 30 seeds) | Record | p |
|---|---|---|
| vs `stateless-max` **(pre-registered)** | **29–0–1** | **<0.001** |
| vs `stateless-top2` | **26–2–2** | **<0.001** |
| vs `window3-top2` | **26–2–2** | **<0.001** |
| vs `hybrid` | 26–1–3 | <0.001 |
| vs `stateless-top3` | 20–4–6 | 0.002 |
| vs `long-context-3` | 20–3–7 | <0.001 |
| **vs `random-rank`** | **17–11–2** | **0.345** |

**Read the last row before the others.** On the stratum this entry is built for, the ledger is **not
statistically distinguishable from ranking customers at random.** Diffuse recall is 0.154 (359 /
2332) against chance at 0.128 (298 / 2332).

**On the previous corpus, `stateless-top2` and `window3-top2` beat the ledger here** — at `p=0.023`
and `p=0.002`. On this corpus the ledger beats both at `p<0.001`. Changing how many fragments exist
to plant reversed a headline in both directions, which is the strongest evidence available that these
records describe the corpus at least as much as the mechanism.

**And the arms it beats are worse than chance on this stratum.** `stateless-max` scores 0.088 on
diffuse against random's 0.128 — concentrating on the loudest call is *actively wrong* when evidence
is spread thin. Beating it is a lower bar than it sounds.

### Where the ledger loses: concentrated arcs

A clean sweep of losses, published because it is the same run:

| Comparison (concentrated, 30 seeds) | Record | p |
|---|---|---|
| vs `stateless-max` | **0–30–0** | <0.001 |
| vs `window3-top2` | **0–30–0** | <0.001 |
| vs `long-context-3` | **0–30–0** | <0.001 |
| vs `hybrid` | **0–30–0** | <0.001 |
| vs `stateless-top2` | 0–29–1 | <0.001 |
| vs `random-rank` | 18–7–5 | 0.043 |

Accumulation dilutes a single decisive signal. The ledger beats chance here and loses to everything
else — which is the argument for running a memory *alongside* per-call detection rather than instead
of it.

### The ranking is not stable across operating points

`earshot sweep` evaluates every arm at 1%, 2%, 5% and 10% review budgets — data the harness always
computed and never printed — and reports whether the order holds. **It does not:**

```
1%:  stateless-top2 > window3-top2 > stateless-max > … > full-ledger (6th of 9)
10%: stateless-max > hybrid > long-context-3 > … > full-ledger (7th of 9)
```

`random-rank` is last at every budget, which is the sanity check that the control behaves. Any table
quoting a single budget — including the one above — is one slice of an unstable ranking, and the
command says so in its own output rather than letting a reader assume the order is a property of the
arms.

### Tie-breaks, measured rather than caveated

Alerts are the top *K* of a ranked list, so an arm producing few distinct scores decides much of its
queue alphabetically: `dumb-ledger` **65.9%**, `stateless-max` **21.9%**, the full ledger **0.0%**.
This page used to say that dependence was unmeasured. It now is — `earshot sweep` runs the
pre-registered headline under both tie-break rules and prints both:

| Headline (diffuse, 30 seeds) | Record | p |
|---|---|---|
| deterministic (`customer_id`, the default) | 29–0–1 | <0.001 |
| randomised (independent seeded RNG) | 28–0–2 | <0.001 |

**The record moves**, so the exact integer was never precise — as the old caveat guessed. The
conclusion survives both ways at `p<0.001`.

### What this adds up to

**Aggregating a few conversations beats aggregating one, on evidence that is genuinely spread out.**
Supported at `p<0.001` — and it reverses when the corpus changes shape, so treat it as a statement
about a regime, not a law.

**That unbounded memory beats a cheap bounded window is unproven.** On the previous corpus the window
was *better*. Never-discard has not yet earned its place on recall.

**The binding constraint is the reader, not the ranking.** A lexicon finding 1 of 32 fragments written
outside its vocabulary leaves every arm crowded between 0.109 and 0.138 — a chance floor and a ceiling
three points above it. No ranking strategy escapes a reader that weak, which is why the model reader's
**0.8214 (92 / 112)** on real customer language matters more to this product than any row above.

**Precision says nothing recall does not.** The precision matrix is byte-identical to overall recall —
same records, same p-values — because at an equal alert budget every arm flags the same count, so both
metrics rank on hits alone. Printed anyway, with that note, because a reader is entitled to check
rather than take it on trust.

**Multiplicity.** `earshot sweep` runs 84 pairwise tests with no correction and prints every one. Only
the `stateless-max` diffuse row was declared in advance; any other single `p` under 0.05 is a hint,
not a result.

> **What buys the ledger its ranking resolution is decay, not confidence weighting.** Switching
> confidence weighting off alone leaves the ranking as well-defined; switching decay off collapses the
> number of distinct scores by roughly a third. That is decay's defence, and it is not a recall
> defence — it is what stops the alert queue being ordered alphabetically. `earshot run` prints the
> ablations; it does not yet print their tie-share, so the direction is quoted and not the digits.

> **Two retractions, both from earlier today.** (1) A first version of this table came from a single
> 400-customer run with 39 outcome customers, where every rate was an integer over 39 — differences of
> one customer, inside binomial noise, written up as findings. (2) That corpus also gave every decoy
> and clean customer a latent risk of exactly `0.0` while every real arc was `≥0.55`, which made the
> risk value a lossless encoding of the answer key and leaked it into the agent's account tool. Both
> are fixed; the numbers above are post-fix, and the earlier claim that "memory loses overall" and that
> "long-context beats us" did not survive either correction.

**Diagnostics, from the committed 400-customer run** in `artifacts/runs/pinned/` — these describe the data and the extractor rather
than comparing arms, so a single dataset is appropriate; they are not comparison results and should not
be quoted as such, and they were **regenerated on 2026-08-28 after the corpus fix** from a clean tree
(`git_sha` `660dca4`, no `-dirty`). Extractor recall **0.659 (492 / 747 planted signals)** — it misses
34% and is deliberately the weaker option; portfolio outcome rate **12.75% (51 / 400)**. Extraction is matched at
conversation level — did the extractor find *this signal type in this conversation* — not at
character-span level.

The corpus plants two kinds of decoy and they are reported separately, because a firing means the
opposite thing in each: **extractor decoys** are lookalikes and firing on one is a mistake
(**1.4%, 2 / 141**); **accumulator decoys** are genuine weak signals that never amount to anything, so
firing is *correct* (**49.7%, 94 / 189**) and what is under test is whether the ledger goes on to
over-accumulate them — it does not, their flag rate at the 10% budget is 0.000.

**The rule-based offline reader barely works on language it did not write, and we measured it rather
than waiting to be asked.** Read the provider label before the number: this is
`OfflineLexiconExtractor`, the keyless 26-regex fallback that exists so everything runs with no API
keys and no network. **It is not the production reader.** `Extractor` in
[extract.py](src/earshot/extract.py) is a protocol with two implementations, and **both have now
been scored against the same 150 hand-marked real CFPB complaint narratives** (public domain, CC0),
on the same committed gold marks, at the same `(document, signal_type)` grain, by one scorer in one
execution.

| reader | strict recall | any-type recall | false-positive rate |
|---|---|---|---|
| offline lexicon, 26 regexes | 0.0357 (4 / 112) | 0.0964 (8 / 83) | **0.0205 (10 / 488)** |
| Claude Haiku 4.5 on Bedrock | **0.8214 (92 / 112)** | **0.9759 (81 / 83)** | 0.1598 (78 / 488) |

**Read the third column before the first two.** The model is roughly 8× worse on false positives,
and almost all of it is one signal type: `complaint_escalation` fires on **0.8072 (67 / 83)** of the
documents that should not carry it. It marks nearly every complaint as an escalation. Per type its
strict recall is complaint_escalation 0.9701 (65 / 67), financial_distress 0.8571 (18 / 21),
life_event 0.3636 (4 / 11), churn_intent 0.3846 (5 / 13) — so two of the four types are still weak.

**What this changes and what it does not.** The 0.0357 above measures the **26-regex fallback**, not
the system: on real language the lexicon misses 96% of what a model catches, `financial_distress`,
`complaint_escalation` and `life_event` each scored **exactly zero**, and 24 of its 26 cues never
fired on any of the 150 documents. It does **not** rescue the 0.659 on our own prose — that number
still measures how much pass A and pass B were co-developed, and nothing here touches it. The sampling frame, the marking guide, the
gold set and the interpretation thresholds were all committed **before** any narrative was read, and
two failures of our own — a contaminated inter-marker comparison and a defect in the marking guide —
are disclosed in the write-up rather than smoothed over. Everything is in
**[benchmarks/cfpb/](benchmarks/cfpb/)**; `uv run python benchmarks/cfpb/steps/05_score.py`
reproduces every figure offline with no network. This is the reason the cue vocabulary is being
regrounded (D-019). It measures the **reader**, not the ledger, and it left the numbers above
untouched.

### What the agent actually costs, and where it fails

All from keyed runs on 2026-08-28, Claude Haiku 4.5 through Bedrock, every response committed for
keyless replay.

| | measured |
|---|---|
| Reader, cost per 1,000 conversations | **$1.66** ($0.24845 over 150) |
| Reader latency | p50 **1,244 ms**, p95 **2,212 ms** |
| Investigation, cost per case | **$0.0295** (50 cases, $1.4733; p95 $0.0357, max $0.0368) |
| Investigation latency, model time | p50 **19.8 s**, p95 **24.7 s** |
| Evidence repairs (first-attempt groundedness) | **0 / 50** |
| Loop exits | `decided` 50 / 50 — no `cost_cap`, no `max_steps`; 4–5 model calls per case |

**The agent does not discriminate, and this is the headline result of AT-57.** Fifty crossings —
25 with a real outcome and 25 without — sampled deliberately, because the top of the queue is nearly
all true positives and a run drawn from it cannot be wrong in the direction that matters:

| | verdict `genuine` | verdict `false_alarm` | abstained |
|---|---|---|---|
| outcome present (25) | **18** | 6 | 1 |
| outcome absent (25) | **21** | **4** | 0 |

It caught 18 of 25 real cases and dismissed **4 of 25** false alarms, at a mean confidence of 0.86 on
the wrong answers. **Overall 22 / 50.** An earlier 10-case run read 4 / 10, and a 50-case run on the
pre-fix corpus also read 22 / 50 — five times the sample and a regenerated corpus moved the number by
one case in each direction and did not move the conclusion.

Replay it with no credentials and no network:

```bash
EARSHOT_CACHE_MODE=replay uv run python tools/verdict_accuracy.py   --provider bedrock --per-arm 25 --customers 2400
```

That reproduces 22 / 50 and $1.4733 from the committed cache, and it writes to a **separate**
`-replay` artifact rather than over the recorded one. Both of those are scar tissue: a failed replay
once overwrote the keyed run it was replaying — same seed, same config hash, same provider, same
filename — and `config_hash` turned out not to cover the *code* that turns a seed into a queue, so
manifests now also carry a `pipeline_sha`.

So the D-025 cost argument for Haiku is **not yet earned**: it is cheap and it is fast, and on this
sample it escalates everything. Whether a stronger model, a better prompt or a false-alarm-aware
loop fixes it is open, and the honest position until then is that the investigator adds routing and
an audit trail, not filtering.

**Routing accuracy, measured for the first time on 2026-08-28 — and it is the good news.** Each
customer carries a seeded `trajectory`, so a correct owning team exists; `tools/routing_accuracy.py`
grades the `owning_team` the investigator already recorded, making **zero further model calls**. On
the same 50 cases: **36 of 49 routed to the right team, 2 wrong, 11 declined**
(`owning_team="none"`). Its dominant failure mode is refusing to route rather than misrouting, and
the declines concentrate in `collections` (8 of 22). Both wrong routes are the bad kind — neither
matched the ledger's own dominant signal at the crossing, so they are unmoored from the evidence on
hand rather than defensible near-misses. The 50th case is a decoy-accumulator customer with no seeded
trajectory: no correct team exists for it, so it is reported separately and never enters the
denominator.

**`retention` has no row in that table at all, and that is not sampling.** See the next section — the
route is structurally unreachable under the offline reader, so this figure is really measured on three
teams out of four.

Read together, the two results say the investigator is a **router and an audit trail, not a filter**:
it addresses the case correctly and escalates almost everything.

### The retention route is dead under the offline reader

Measured 2026-08-29, and it is the sharpest thing on this page.

The corpus plants four signal families evenly. The offline lexicon finds churn evidence in **1.35 of
3.42** planted conversations — a coverage ratio of **0.40**, against 0.71 / 0.76 / 0.77 for the other
three families. Corroboration in the ledger is *cross-conversation*, so a customer whose evidence
lands in one conversation never corroborates with anything:

| trajectory | conversations planted | conversations found | ratio | best score reached | crossings |
|---|---|---|---|---|---|
| `churn_intent` -> retention | 3.42 | 1.35 | **0.40** | **0.646** | **0 / 325** |
| `complaint_escalation` -> complaints | 3.24 | 2.28 | 0.71 | 0.903 | 55 / 304 |
| `life_event` -> vulnerability | 3.29 | 2.49 | 0.76 | 0.960 | 109 / 358 |
| `financial_distress` -> collections | 3.56 | 2.73 | 0.77 | 0.955 | 85 / 323 |

At a threshold of **0.675**, churn customers top out at **0.646**. Not one of 325 can cross. **The
Retention desk never receives a case** — and Retention is the *lead* team in the submitted brief. It
is also why `retention` has no row in the routing table above: the agent has never been handed a churn
case to route.

This is not the corpus favouring some families over others. Fragment strengths are comparable across
all four and churn's are the strongest (max 0.95). It is a **pass-B gap**: the extractor cues for
churn fire in fewer of the conversations where churn was planted. Pass A and pass B are authored
without reference to each other on purpose — that independence is what makes the miss rate honest —
and widening the churn cues now to close a gap we discovered by measuring the answer key is precisely
the tuning that rule exists to prevent. So it is published rather than fixed.

**Measured 2026-08-29: the model reader revives retention and loses collections.** Both readers over
the identical 288 sampled conversations (20 customers per trajectory), $0.4260, `tools/
reader_coverage.py`. Coverage is against what was **planted**, and the second pair of columns is what
a reviewer actually gets — the same signals through the same ledger at the same 0.6747 cut:

| trajectory -> desk | lexicon coverage | model coverage | lexicon crossings | model crossings |
|---|---|---|---|---|
| `churn_intent` -> **Retention** | 30 / 70 (0.43) | **55 / 70 (0.79)** | **0 / 20** | **9 / 20** |
| `financial_distress` -> Collections | 56 / 76 (0.74) | **32 / 76 (0.42)** | 4 / 20 | **1 / 20** |
| `complaint_escalation` -> Complaints | 41 / 61 (0.67) | 42 / 61 (0.69) | 3 / 20 | 3 / 20 |
| `life_event` -> Vulnerability | 60 / 70 (0.86) | 64 / 70 (0.91) | 10 / 20 | 16 / 20 |

**The dead route comes alive**: churn peaks at 0.8509 under the model against 0.4899 under the
lexicon, and 9 of 20 churn customers now reach the Retention desk that had never received a case.

**And it costs us collections.** The model reader finds *less* planted distress evidence than 26
regexes do — 0.42 against 0.74 — and Collections crossings fall from 4 to 1. It is not a uniformly
better reader; it is a differently-shaped one, and swapping readers moves work between desks. We
publish that because it is the same size as the win and comes from the same run.

Two caveats stated rather than buried. **The threshold is a top-K cut derived from the *offline*
reader's ranking of the whole portfolio**, held fixed across both arms because deriving the model's
own cut means reading all 8,359 conversations at $13.85. A better reader raises every score, so a
real 10% budget would settle higher — the model crossings above are an **upper bound**. And this is
**one dataset at n=20 per trajectory**; it is a direction with denominators, not a sweep.

**One more number the recall table never reports:** of the 240 customers the ledger surfaces at a 10%
review budget over 2,400, **25 have a real outcome and 215 do not**. That is the ledger's own
precision at the cut, and it is what makes the agent's job hard — it is handed a queue that is **90%
false alarm by construction** and asked to sort it.

**Still not measured:** any of this at a sample size worth a confidence interval — 50 cases on one
dataset is a result, not an interval — and a second model through the same harness.

**Provider-historical, superseded by D-025 (2026-08-25):** two live Claude Sonnet 4.5 investigations,
recorded via OpenRouter on 2026-08-09, cost **$0.089 and $0.097** and took 30.3s and 33.4s — the only
live-model cost/latency this repo has ever measured for the investigator, kept as a data point rather
than deleted. **They no longer replay.** `artifacts/cache/investigator-demo.jsonl` is keyed on
`prompt_sha`, and the investigator prompt changed twice after the cache was recorded (`7229b70`,
`80c0914`); D-025 also moved both reader and investigator to Bedrock Haiku 4.5, which changes the
model string regardless. The old replay command now cache-misses and prints `provider_error` instead
of reaching the network, so it is not reproduced here. No Haiku-on-Bedrock investigation cost/latency
figures exist yet to replace it.

### The streamed demo, measured 2026-08-28

One synthetic deployment, read end to end by Claude Haiku 4.5 on Bedrock. Every figure is counted
from the run, and the whole thing replays from the committed cache with no key.

| | |
|---|---|
| Conversations read | 133, across 44 customers over 179 days |
| Signals kept | 63 |
| Threshold crossings | 9 (fixed cut at 0.60) |
| Cases worked by the agent | 6 of 9 |
| Read once — one call each | 127 conversations · **$0.187** · p50 1,101 ms · p95 1,564 ms |
| Read turn-by-turn | 6 conversations · 54 calls · **$0.073** |
| Agent investigations | 6 · **$0.209** |
| **Total** | **$0.469** |

**0 unparsable replies, 0 dropped quotes, 0 relocated quotes** across all 133 reads.

#### Reading a call while it is still open

Six conversations were read *again after each customer turn*, on the transcript heard so far, so a
belief can be watched forming rather than arriving finished. On `CUST-0043-C3`:

| After | Reader believes | Movement |
|---|---|---|
| 2 turns | — | |
| 5 turns | `complaint_escalation` 0.65 | appeared |
| 7 turns | `complaint_escalation` 0.70 | firmed |
| 9 turns | `complaint_escalation` 0.70 | |
| 10 turns | `complaint_escalation` 0.72 | firmed |

Across the six, every movement type occurs in real output: **9 appeared, 7 firmed, 1 faded, 3
withdrawn** (the model retracts a signal after hearing more) **and 1 requoted** (it moves its
citation to better evidence). The browser does not decide any of that — `read_live._diff()` does,
in Python, and the page animates the result.

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
- **Only 6 of 9 crossings were investigated**, to bound the cost of a re-record, and only 6 of 133
  conversations were read turn-by-turn, because that costs a call per customer turn. Both
  denominators are on the screen, not inferable from it.
- **Routing is still not accuracy-measured, and what it shows is not flattering.** The agent
  concentrates its routing and sometimes returns `owning_team: "none"`. That is on the deployment
  screen because it is a finding, and it is consistent with AT-57: the agent escalates rather than
  discriminates.
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
