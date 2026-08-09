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
```

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
1,500 customers — 1,945 outcome customers in total** — with every arm paired seed by seed and compared
with a two-sided sign test.

Recall at a **10% review budget**, since a review team's capacity is the real constraint. Both arc
strata are shown, because the result is a **trade** and reporting only one side of it would be picking
the answer out of a comparison the code computes in full:

| Arm | Recall | Hits / outcomes | **Diffuse arcs** | hits / n | **Concentrated arcs** | hits / n |
|---|---|---|---|---|---|---|
| window3-top2 *(last 3 conversations, keep the best 2)* | 0.134 | 261 / 1945 | **0.195** | **152 / 780** | 0.173 | 109 / 629 |
| stateless-top2 *(sum the two loudest calls)* | 0.132 | 256 / 1945 | 0.188 | 147 / 780 | 0.173 | 109 / 629 |
| dumb-ledger *(unweighted count)* | 0.129 | 250 / 1945 | 0.177 | 138 / 780 | 0.175 | 110 / 629 |
| full-ledger *(decay, corroboration, channel, escalation)* | 0.131 | 254 / 1945 | 0.172 | 134 / 780 | 0.189 | 119 / 629 |
| stateless-top3 *(sum the three loudest calls)* | 0.136 | 265 / 1945 | 0.149 | 116 / 780 | 0.235 | 148 / 629 |
| long-context-3 *(last 3 conversations pooled)* | 0.135 | 262 / 1945 | 0.144 | 112 / 780 | 0.237 | 149 / 629 |
| hybrid *(rank-combined)* | 0.140 | 272 / 1945 | 0.126 | 98 / 780 | 0.277 | 174 / 629 |
| stateless-max *(score each call, forget)* | 0.142 | 276 / 1945 | 0.123 | 96 / 780 | **0.286** | **180 / 629** |

Read the two stratum columns together and the shape is a **trade, not a winner**: arms that aggregate
across conversations do better on thin evidence and worse on a single loud call, and `stateless-max` —
which aggregates nothing — is the extreme of both.

That is as far as the ordering goes. It is *not* monotone in how many conversations an arm may
combine: `stateless-top3` is significantly **worse** than `stateless-top2` on diffuse arcs
(`10–0–0`, `p=0.002`) despite seeing strictly more of them. The stable claim is "aggregating a few
conversations beats aggregating one on diffuse arcs, and the reverse on concentrated ones"; the exact
row order below is specific to the 10% budget, which is the only operating point we evaluate.

What survives a paired test:

- **Memory wins on the arcs it exists for, and it is significant.** On diffuse arcs — evidence spread
  thin, nothing alarming in any single conversation — the full ledger catches **134 of 780** against
  **96 of 780** for scoring-and-forgetting, winning **8 seeds of 10 with 2 ties and zero losses**
  (`p=0.008`). This is the entry's pre-registered headline, and `earshot sweep` prints it first. It is
  the one comparison declared before the run; at `--seeds 30` it strengthens to **27–0–3**.
- **And memory loses on concentrated arcs, by a comparable margin.** **119 of 629** against
  **180 of 629**, losing 8 seeds of 10 (`p=0.039`; at 30 seeds, **3–25–2**). Accumulation dilutes a
  single decisive signal. We publish this because it is the same size as the win and comes from the
  same run — and because it is the actual argument for running a memory *alongside* per-call detection
  rather than instead of it.
- **Two much cheaper arms beat the whole ledger on the stratum the entry is built on.** This is the
  most important thing on this page and it goes against us.

  `stateless-top2` sums the two loudest calls — two floats per customer, no ledger, no never-discard,
  no retro re-scoring. `window3-top2` keeps only the last three conversations and only the best two of
  those — strictly *less* state than a ledger. At 30 seeds, on diffuse arcs:

  | comparison (diffuse, 30 seeds) | record | p |
  |---|---|---|
  | full-ledger vs `stateless-top2` | **7–21–2** (ledger loses) | **0.013** |
  | full-ledger vs `window3-top2` | **7–21–2** (ledger loses) | **0.013** |
  | full-ledger vs `stateless-max` *(pre-registered)* | 27–0–3 (ledger wins) | 0.000 |

  On concentrated arcs the ledger beats `stateless-top2` (`17–5–8`, `p=0.017`) but **not**
  `window3-top2` (`16–8–6`, `p=0.152`). So `window3-top2` is not a trade against us — it matches the
  ledger where the ledger is strong and beats it where the ledger is supposed to be strongest. All of
  these are exploratory among 84 uncorrected tests; only the `stateless-max` row was declared in
  advance. We are not going to soften them.

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
be quoted as such. Extractor recall **0.681 (496 / 728 planted signals)** — it misses 32% and is
deliberately the weaker option; portfolio outcome rate **13.5% (54 / 400)**. Extraction is matched at
conversation level — did the extractor find *this signal type in this conversation* — not at
character-span level.

The corpus plants two kinds of decoy and they are reported separately, because a firing means the
opposite thing in each: **extractor decoys** are lookalikes and firing on one is a mistake
(**2.9%, 4 / 140**); **accumulator decoys** are genuine weak signals that never amount to anything, so
firing is *correct* (**42.7%, 53 / 124**) and what is under test is whether the ledger goes on to
over-accumulate them — it does not, their flag rate at the 10% budget is 0.000.

**The rule-based offline reader barely works on language it did not write, and we measured it rather
than waiting to be asked.** Read the provider label before the number: this is
`OfflineLexiconExtractor`, the keyless 26-regex fallback that exists so everything runs with no API
keys and no network. **It is not the production reader.** `Extractor` in
[extract.py](src/earshot/extract.py) is a protocol, and its model implementation now exists —
[extract_model.py](src/earshot/extract_model.py), stateless per conversation, quotes verified
verbatim, cost and latency captured per call. **It has never been run against a real model**, so
there is no accuracy figure for it anywhere in this repository and every extraction number on this
page still describes the fallback. One keyed run of `benchmarks/cfpb/steps/05_score.py --extractor
model` produces the comparison and commits its cache for keyless replay. Against 150
hand-marked real CFPB complaint narratives (public domain, CC0) the offline reader scores **0.0357
strict recall — 4 / 112** — versus **0.681** above on our own prose. `financial_distress`, `complaint_escalation` and `life_event` each scored **exactly zero**, and
24 of its 26 cues never fired on any of the 150 documents. The sampling frame, the marking guide, the
gold set and the interpretation thresholds were all committed **before** any narrative was read, and
two failures of our own — a contaminated inter-marker comparison and a defect in the marking guide —
are disclosed in the write-up rather than smoothed over. Everything is in
**[benchmarks/cfpb/](benchmarks/cfpb/)**; `uv run python benchmarks/cfpb/steps/05_score.py`
reproduces every figure offline with no network. This is the reason the cue vocabulary is being
regrounded (D-019). It measures the **reader**, not the ledger, and it left the numbers above
untouched.

**Not yet measured:** verdict and routing accuracy for the agent, cost per 1,000 conversations, and
p50/p95 latency. The last two are now *instrumented* rather than measured — the model reader
accumulates real spend and per-call latency and prints both, including cost per 1,000
conversations, but no run has produced them. Evidence groundedness is reported as a first-attempt repair rate by `earshot
investigate`, but is structurally zero on the offline provider (it copies quotes out of the ledger),
so only a model provider exercises it — measuring it against a known answer at volume is AT-57. The two live Claude Sonnet 4.5 investigations in
`artifacts/cache/` cost **$0.089 and $0.097** and took 30.3s and 33.4s. They are committed, and this
exact command replays them with no network and a deliberately invalid key:

```bash
EARSHOT_CACHE_MODE=replay EARSHOT_OPENROUTER_API_KEY=invalid \
  uv run earshot investigate --provider openrouter --customers 200 --limit 2
```

The cache holds those **two** investigations only. Asking for a third, or for a different corpus size,
is a cache miss — which reports itself as `provider_error` rather than reaching the network.

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

| Path | What |
|---|---|
| `src/earshot/corpus.py`, `memory.py` | The deterministic core: dataset generation, the signal ledger, the re-scoring maths |
| `src/earshot/extract.py`, `extract_model.py` | The two readers behind one protocol: the keyless regex lexicon, and the model |
| `src/earshot/arms.py`, `evals.py`, `sweep.py` | The six comparison arms, the metrics, and the multi-seed harness |
| `src/earshot/core/` | Synthetic account and transaction state behind the agent's tools |
| `src/earshot/agent/` | The investigator: loop, tools, decision schemas, prompts |
| `src/earshot/llm/` | Provider abstraction, response cache, cost + latency capture |
| `prompts/` | Prompts as versioned files, so a prompt change is a reviewable diff |
| `tests/` | Including `test_separation.py` (no module on the decision path can *import* the answer key) and `test_no_answer_key_leak.py` (nor recover it statistically from what the tools return) |
| `docs/architecture/` | [architecture.md](docs/architecture/architecture.md) · [build-plan.md](docs/architecture/build-plan.md) |
| `docs/gates/` | Sprint gate briefs for the Genesis Committee |
| `sources/` | The submitted brief and committee correspondence — `[source]`, do not edit |
| `artifacts/` | Run manifests and the committed response cache |

---

## Competition context

Judging: Zenon impact 25 · technical depth 25 · feasibility & production readiness 25 · originality 15 ·
presentation 10, plus an AI judge scoring engineering quality. Gates: **2026-08-10** check-in ·
**2026-08-24** combined Sprint 1+2 demo · **2026-09-07** Sprint 3.

All data is synthetic, generated with ground truth authored *before* the text, per competition rules.
No client data of any kind is used anywhere in this repository.
