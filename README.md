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
   (call/chat/     (with evidence      (append-only,             (re-scored     (tools: transactions,   (approve /
    complaint)      spans)              never discards)           each batch)    accounts, cases)        dismiss / route)
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

Recall at a **10% review budget**, since a review team's capacity is the real constraint:

| Arm | Recall | Spread (min–max) | **Diffuse arcs** | Hits / outcomes |
|---|---|---|---|---|
| stateless-max *(score each call, forget)* | 0.142 | 0.117–0.182 | 0.126 | 276 / 1945 |
| hybrid *(rank-combined)* | 0.140 | 0.103–0.168 | 0.127 | 272 / 1945 |
| long-context-3 *(last 3 conversations pooled)* | 0.135 | 0.112–0.170 | 0.143 | 262 / 1945 |
| full-ledger *(decay, corroboration, channel, escalation)* | 0.131 | 0.100–0.157 | **0.174** | 254 / 1945 |
| dumb-ledger *(unweighted count)* | 0.129 | 0.103–0.155 | **0.179** | 250 / 1945 |

What survives a paired test:

- **Memory wins on the arcs it exists for, and it is significant.** On diffuse arcs — evidence spread
  thin, nothing alarming in any single conversation — the full ledger scores **0.174 against 0.126**
  for scoring-and-forgetting, winning **8 seeds of 10 with 2 ties and zero losses** (`p=0.008`). This
  is the entry's central claim and it holds.
- **Overall, memory neither beats nor loses to per-call detection.** Every pairing involving the full
  ledger is non-significant (`p≥0.29`). One unrelated pairing does reach `p=0.039` (hybrid vs
  dumb-ledger) — with 14 pairwise tests and no multiplicity correction, that is a hint, not a result,
  and we are not going to report it as one.
- **Our scoring machinery still earns nothing.** Full ledger vs a dumb unweighted count on diffuse
  arcs: **3–4–3, `p=1.000`**. Decay, corroboration, cross-channel weighting and escalation are
  decoration until shown otherwise — a plain count of retained signals does the same work.
- **Long-context does not beat the ledger.** On diffuse arcs the ledger leads it 8–2 (`p=0.109`).

> **Two retractions, both from earlier today.** (1) A first version of this table came from a single
> 400-customer run with 39 outcome customers, where every rate was an integer over 39 — differences of
> one customer, inside binomial noise, written up as findings. (2) That corpus also gave every decoy
> and clean customer a latent risk of exactly `0.0` while every real arc was `≥0.55`, which made the
> risk value a lossless encoding of the answer key and leaked it into the agent's account tool. Both
> are fixed; the numbers above are post-fix, and the earlier claim that "memory loses overall" and that
> "long-context beats us" did not survive either correction.

Supporting figures, all from the same sweep: the offline extractor's measured recall is **0.681** —
it misses 32% of planted signals and is deliberately the weaker arm; it fires on 22% of the lookalikes
that were planted to fool it. Portfolio outcome rate 13.5%.
Throughput ~1,770 conversations/sec. A live investigation on Claude Sonnet 4.5 costs **$0.078** and
takes 33s.

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
| `src/earshot/arms.py`, `evals.py`, `sweep.py` | The five comparison arms, the metrics, and the multi-seed harness |
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
