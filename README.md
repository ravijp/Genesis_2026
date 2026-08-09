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
| stateless-top2 *(sum the two loudest calls)* | 0.132 | 256 / 1945 | **0.188** | **147 / 780** | 0.173 | 109 / 629 |
| dumb-ledger *(unweighted count)* | 0.129 | 250 / 1945 | 0.177 | 138 / 780 | 0.175 | 110 / 629 |
| full-ledger *(decay, corroboration, channel, escalation)* | 0.131 | 254 / 1945 | 0.172 | 134 / 780 | 0.189 | 119 / 629 |
| long-context-3 *(last 3 conversations pooled)* | 0.135 | 262 / 1945 | 0.144 | 112 / 780 | 0.237 | 149 / 629 |
| hybrid *(rank-combined)* | 0.140 | 272 / 1945 | 0.126 | 98 / 780 | 0.277 | 174 / 629 |
| stateless-max *(score each call, forget)* | 0.142 | 276 / 1945 | 0.123 | 96 / 780 | **0.286** | **180 / 629** |

Read the two stratum columns together and the shape is one dial, not a winner: **the more
conversations an arm is allowed to combine, the better it does on thin evidence and the worse it does
on a single loud call.** That trade is the finding.

What survives a paired test:

- **Memory wins on the arcs it exists for, and it is significant.** On diffuse arcs — evidence spread
  thin, nothing alarming in any single conversation — the full ledger catches **134 of 780** against
  **96 of 780** for scoring-and-forgetting, winning **8 seeds of 10 with 2 ties and zero losses**
  (`p=0.008`). This is the entry's pre-registered headline, and `earshot sweep` prints it first. It is
  the one comparison declared before the run; at 30 seeds it strengthens to **27–2–1**.
- **And memory loses on concentrated arcs, by a comparable margin.** **119 of 629** against
  **180 of 629**, losing 8 seeds of 10 (`p=0.039`; at 30 seeds, **1–27–2**). Accumulation dilutes a
  single decisive signal. We publish this because it is the same size as the win and comes from the
  same run — and because it is the actual argument for running a memory *alongside* per-call detection
  rather than instead of it.
- **The cheapest possible aggregator matches the whole ledger.** `stateless-top2` sums the two loudest
  calls — two floats per customer, no ledger, no never-discard, no retro re-scoring — and takes
  **147 of 780** diffuse arcs, slightly ahead of the full ledger's 134 (`3–6–1`, `p=0.508`; at 30
  seeds the ledger is behind at `9–19–2`, `p=0.087`). It also beats `stateless-max` outright
  (`8–2–0`). So the honest reading of the headline is **aggregation beats no aggregation** — not
  memory beats detection. Our diffuse customers average 2.55 extracted signals, so "keep everything"
  and "keep the best two" are not yet distinguishable at this history length. Whether never-discard
  pulls ahead as histories lengthen is open, and is the question the ledger has to answer.
- **Overall, memory neither beats nor loses to per-call detection.** Every pairing involving the full
  ledger is non-significant on whole-portfolio recall.
- **Our scoring machinery still earns nothing.** Full ledger vs a dumb unweighted count on diffuse
  arcs: **3–4–3, `p=1.000`**. Decay, corroboration, cross-channel weighting and escalation are
  decoration until shown otherwise — a plain count of retained signals does the same work.
- **Multiplicity.** `earshot sweep` runs **45 pairwise tests** (15 pairings × 3 metrics) with no
  correction, and prints every one. Only the headline above was declared in advance; any other single
  `p` under 0.05 is a hint, not a result. Every number quoted in this README appears in that output.

> **A caveat on ranking, which cuts against one of our own comparisons.** Alerts are the top *K* of a
> ranked list, and arms differ enormously in how many distinct scores they produce. At 1,500 customers
> the full ledger produces ~808 distinct scores and only **0.7%** of its alert queue is decided by the
> `customer_id` tie-break; `long-context-3` produces ~69 and **69.5% on average, up to 95%**, of its
> queue is decided alphabetically. So "long-context does not beat the ledger" rests on an arm whose
> ranking is mostly arbitrary, and we would not defend that particular comparison hard. The headline
> comparison is not affected in direction — it survives randomised tie-breaks — but the exact
> `96 / 780` for `stateless-max` (mean 17% arbitrary) moves by roughly ±15 under a different tie-break.
> This is also the one concrete thing confidence weighting buys: it earns nothing in recall, but it is
> what makes the ledger's ranking well-defined instead of alphabetical.

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
deliberately the weaker option; it fires on **22% (57 / 264)** of the lookalikes planted to fool it;
portfolio outcome rate **13.5% (54 / 400)**. Extraction is matched at conversation level — did the
extractor find *this signal type in this conversation* — not at character-span level.

**Not yet measured:** verdict and routing accuracy for the agent, first-attempt evidence-groundedness,
cost per 1,000 conversations, and p50/p95 latency. The two live Claude Sonnet 4.5 investigations in
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
| `openrouter` | `EARSHOT_OPENROUTER_API_KEY`, or `EARSHOT_OPENROUTER_API_KEY_FILE=<path>` | Real models. Default `anthropic/claude-sonnet-4.5` |
| replay | `EARSHOT_CACHE_MODE=replay` | Replays committed responses from `artifacts/cache/` — real model output, zero network |

Keys are never committed and never logged. See `.env.example`.

---

## Repository

| Path | What |
|---|---|
| `src/earshot/corpus.py`, `memory.py` | The deterministic core: dataset generation, the signal ledger, the re-scoring maths |
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
