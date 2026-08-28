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

---

## Quick start — fresh machine

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13 (uv installs it for you).

```bash
git clone <repo-url> && cd Genesis_2026
uv sync                                                 # installs deps + the `earshot` package
uv run pytest                                           # the whole suite
uv run earshot sweep --seeds 10 --customers 1500        # the numbers below (~30s)
uv run earshot demo --customers 400                     # the accumulation moment, narrated
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

The harness was built to *test* the claim, not illustrate it. Figures below are from **10 seeds ×
1,500 customers — 1,904 outcome customers in total** — with every arm paired seed by seed and compared
with a two-sided sign test. The 30-seed records quoted alongside come from **5,760 outcome customers**.

**Regenerated 2026-08-28** after a corpus defect was fixed (commit `08b20cc`): the planter re-used an
already-planted fragment once a trajectory's pool ran out, so the same sentence appeared in two
conversations and the ledger paid a cross-conversation corroboration bonus for one utterance copied
twice. It hit 120 / 822 arc customers at this corpus size. Every figure below is post-fix, and the
headline moved — see the pre-registered bullet.

Recall at a **10% review budget**, since a review team's capacity is the real constraint. Both arc
strata are shown, because the result is a **trade** and reporting only one side of it would be picking
the answer out of a comparison the code computes in full:

**Every row below reads the same offline-lexicon signal stream.** `earshot sweep` runs
`OfflineLexiconExtractor` — the keyless 26-regex fallback, not a model — and now prints
`reader=offline-lexicon` in its own header and stamps `provider` into the artifact manifest, so the
source is never left unlabelled. That reader is weak in absolute terms (**0.0357 strict recall,
4 / 112**, against real CFPB language — measured further down this page), but this table is not
testing that number. Every arm consumes the identical stream from the identical reader, so the
arm-vs-arm comparison stays internally valid regardless of how weak the reader is: a stronger reader
would move every row's absolute recall up together, not reorder them. What moves between rows here
is the memory mechanism, not the evidence it is fed.

| Arm | Recall | Hits / outcomes | **Diffuse arcs** | hits / n | **Concentrated arcs** | hits / n |
|---|---|---|---|---|---|---|
| window3-top2 *(last 3 conversations, keep the best 2)* | 0.139 | 265 / 1904 | **0.205** | **150 / 730** | 0.183 | 115 / 628 |
| stateless-top2 *(sum the two loudest calls)* | 0.138 | 263 / 1904 | 0.201 | 147 / 730 | 0.185 | 116 / 628 |
| dumb-ledger *(unweighted count)* | 0.120 | 229 / 1904 | 0.164 | 120 / 730 | 0.170 | 107 / 628 |
| full-ledger *(decay, corroboration, channel, escalation)* | 0.124 | 236 / 1904 | 0.160 | 117 / 730 | 0.188 | 118 / 628 |
| long-context-3 *(last 3 conversations pooled)* | 0.124 | 237 / 1904 | 0.145 | 106 / 730 | 0.205 | 129 / 628 |
| stateless-top3 *(sum the three loudest calls)* | 0.123 | 235 / 1904 | 0.134 | 98 / 730 | 0.215 | 135 / 628 |
| hybrid *(rank-combined)* | 0.129 | 246 / 1904 | 0.108 | 79 / 730 | 0.266 | 167 / 628 |
| stateless-max *(score each call, forget)* | 0.143 | 273 / 1904 | 0.114 | 83 / 730 | **0.303** | **190 / 628** |

Read the two stratum columns together and the shape is a **trade, not a winner**: arms that aggregate
across conversations do better on thin evidence and worse on a single loud call, and `stateless-max` —
which aggregates nothing — is the extreme of both.

That is as far as the ordering goes. It is *not* monotone in how many conversations an arm may
combine: `stateless-top3` is significantly **worse** than `stateless-top2` on diffuse arcs
(`10–0–0`, `p=0.002`) despite seeing strictly more of them. The stable claim is "aggregating a few
conversations beats aggregating one on diffuse arcs, and the reverse on concentrated ones"; the exact
row order below is specific to the 10% budget, which is the only operating point we evaluate.

What survives a paired test:

- **Memory wins on the arcs it exists for — at 30 seeds, and not at 10.** On diffuse arcs — evidence
  spread thin, nothing alarming in any single conversation — the full ledger catches **390 of 2,252**
  against **226 of 2,252** for scoring-and-forgetting, winning **26 seeds of 30 with 2 ties and 2
  losses** (`p=0.000`). This is the entry's pre-registered headline, the one comparison declared before
  the run, and `earshot sweep` prints it first.
  **At 10 seeds the same comparison is `7–2–1`, `p=0.180` — it does not clear 0.05.** Before the
  corpus fix of 2026-08-28 the 10-seed record read `8–0–2`, `p=0.008`, and part of that margin was the
  duplicated-fragment artefact. The effect itself did not shrink — the 30-seed diffuse gap widened from
  0.068 to 0.073 — but **ten seeds is no longer enough to see it**, and any claim from this page should
  be quoted at 30.
- **And memory loses on concentrated arcs, by a comparable margin.** **118 of 628** against
  **190 of 628** at 10 seeds, losing 9 of 10 (`p=0.021`; at 30 seeds, **2–28–0**, `p=0.000`).
  Accumulation dilutes a single decisive signal. We publish this because it is the same size as the win
  and comes from the same run — and because it is the actual argument for running a memory *alongside*
  per-call detection rather than instead of it.
- **Two much cheaper arms beat the whole ledger on the stratum the entry is built on.** This is the
  most important thing on this page and it goes against us.

  `stateless-top2` sums the two loudest calls — two floats per customer, no ledger, no never-discard,
  no retro re-scoring. `window3-top2` keeps only the last three conversations and only the best two of
  those — strictly *less* state than a ledger. At 30 seeds, on diffuse arcs:

  | comparison (diffuse, 30 seeds) | record | p |
  |---|---|---|
  | full-ledger vs `stateless-top2` | **6–18–6** (ledger loses) | **0.023** |
  | full-ledger vs `window3-top2` | **5–21–4** (ledger loses) | **0.002** |
  | full-ledger vs `stateless-max` *(pre-registered)* | 26–2–2 (ledger wins) | 0.000 |

  On concentrated arcs the ledger now beats **neither**: `stateless-top2` `16–9–5` (`p=0.230`) and
  `window3-top2` `17–9–4` (`p=0.169`). Before the corpus fix it beat `stateless-top2` at `p=0.017`;
  that win did not survive, and the loss to `window3-top2` on diffuse got *worse* (`p=0.013` → `0.002`).
  So `window3-top2` is not a trade against us — it matches the ledger where the ledger is strong and
  beats it where the ledger is supposed to be strongest. All of these are exploratory among 84
  uncorrected tests; only the `stateless-max` row was declared in advance. We are not going to soften
  them.

  What the ledger *does* beat on diffuse arcs, at 30 seeds, is every arm that pools a window without
  ranking inside it: `long-context-3` **20–8–2** (`p=0.036`) and `stateless-top3` **22–7–1**
  (`p=0.008`). Both became significant only after the corpus fix. The pattern across all of it is that
  **selectivity beats volume** — the arms that beat us keep the best two of what they see, and the arms
  we beat keep everything they see. That is a finding about ranking, not about memory.

  So the honest reading of the pre-registered headline is **aggregating a few conversations beats
  aggregating one**, not *memory beats detection*. Our diffuse customers average about 2.5 extracted
  signals, so "keep everything" discards almost nothing more than "keep the best two out of the last
  three" — and on the evidence so far the cheap bounded rule is *better*, not merely equal. **What
  never-discard buys over a three-conversation window is, right now, unproven.** Whether it pulls ahead
  as histories lengthen is the question the ledger has to answer, and the corpus cannot currently pose
  it (see the fragment-pool limit in the build plan).
- **Overall, memory neither beats nor loses to per-call detection.** Every pairing involving the full
  ledger is non-significant on whole-portfolio recall.
- **Our scoring machinery still earns nothing.** Full ledger vs a dumb unweighted count on diffuse
  arcs: **3–4–3, `p=1.000`**. But this flips sign across seed sets — on seeds `100..109` the plain
  count significantly **beats** the full ledger on diffuse arcs (`0–9–1`, `p=0.004`) — and points the
  other way on the other stratum, where at 30 seeds the full ledger significantly beats the plain
  count on concentrated arcs (`17–5–8`, `p=0.017`). So "decoration" is too strong in one direction and
  too generous in the other. The honest statement: the mechanisms are not distinguishable on the
  stratum we pre-registered, and nothing we have earns a claim either way elsewhere.
- **Multiplicity.** `earshot sweep` runs **84 pairwise tests** (28 pairings × 3 metrics) with no
  correction, and prints every one. Only the headline above was declared in advance; any other single
  `p` under 0.05 is a hint, not a result. Every number quoted in this README appears in that output.

> **A caveat on ranking, and it cuts against our own headline.** Alerts are the top *K* of a ranked
> list, and the arms differ enormously in how many distinct scores they produce — so part of each
> queue is filled by the `customer_id` tie-break rather than by evidence. `earshot sweep` prints this:
>
> | arm | distinct scores | share of queue decided alphabetically |
> |---|---|---|
> | full-ledger | 673 | **0.0%** |
> | stateless-top3 | 106 | 3.0% |
> | window3-top2 | 61 | 6.3% |
> | long-context-3 | 74 | 7.6% |
> | hybrid | 522 | 8.1% |
> | stateless-top2 | 60 | 25.4% |
> | stateless-max | 15 | **40.8%** |
> | dumb-ledger | 6 | **55.1%** |
>
> The two arms most affected are **the pre-registered headline's own opponent** (`stateless-max`,
> 40.8%) and the ablation behind "our machinery earns nothing" (`dumb-ledger`, 55.1%). So this caveat
> cuts against our own claims, not against a comparison we lose.
>
> Ties are broken by `customer_id`, deterministically. **We have not measured how much the headline
> depends on that** — there is no randomised-tie-break harness in this repo, so treat `96 / 780` as
> carrying an unquantified tie-break component rather than as a precise integer.
>
> What buys the ledger its resolution is **decay**, not confidence weighting: switching confidence
> weighting off alone leaves the ranking as well-defined, while switching decay off collapses the
> number of distinct scores by roughly a third. `earshot run` prints the ablations; it does not yet
> print their tie-share, so we quote the direction and not the digits.

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

**What it is evidence for.** The lexicon is the keyless fallback, not the reader the deployed system
runs. The model reader scores 0.8214 (92 / 112) against the lexicon's 0.0357 (4 / 112) on real CFPB
language, and whether it closes *this* gap is being measured rather than assumed —
`tools/reader_coverage.py` runs both readers over the same sampled conversations and reports the same
table. A route that is dead under the fallback and alive under the model is the strongest argument
this repo has for the model reader; a route that is dead under both is a finding about the corpus we
would have to publish instead. Either way the number goes on this page.

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
