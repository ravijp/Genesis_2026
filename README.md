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
uv sync                                        # installs deps + the `ear` package
uv run pytest                                  # the whole suite
uv run earshot run --customers 400                 # full eval: five arms, per-stratum, ablations
uv run earshot demo --customers 200                # the accumulation moment, narrated
uv run earshot investigate --customers 200 --limit 3   # the agent working three cases
```

**Every command above runs with no API keys and no network.** The offline provider is a first-class
implementation, not a stub. To use real models instead, see [Model access](#model-access).

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

We built the eval harness to *test* the claim rather than illustrate it, and as of 2026-08-09 it does
not hold. Every figure below comes from the committed run at
[`artifacts/runs/pinned/`](artifacts/runs/pinned/) — 400 customers, 1,393 conversations, seed `20260809`,
config `07db21651cfa`. Reproduce with `uv run earshot run --customers 400`.

Recall at a **10% review budget** — every arm flags exactly 40 of 400 customers, because a review team's
capacity is the real constraint:

| Arm | Overall | Diffuse arcs | Concentrated arcs | False alarms |
|---|---|---|---|---|
| stateless-max *(score each call, forget)* | **0.154** | 0.143 | **0.214** | 0.000 |
| dumb-ledger *(unweighted count)* | **0.154** | 0.191 | 0.143 | 0.000 |
| long-context-3 *(last 3 conversations pooled)* | **0.154** | **0.238** | 0.071 | 0.000 |
| full-ledger *(decay, corroboration, channel, escalation)* | 0.128 | 0.191 | 0.071 | 0.000 |

What that actually says:

- **Accumulation wins where it should.** On diffuse arcs — evidence spread thin, no single conversation
  alarming — every memory arm beats scoring-and-forgetting.
- **It loses overall**, because it dilutes a single decisive conversation. Per-call detection is better
  at obvious cases, which is most of them.
- **Our scoring mechanisms are not earning their place.** A dumb unweighted count matches the full
  ledger, and removing decay or escalation *improves* recall by 0.026 each.
- **Long-context currently beats us on our own home ground** (0.238 diffuse). That is the question a
  judge will ask, and today the honest answer is that we do not have an accuracy win over it — the
  ledger's case rests on cost, auditability and determinism instead. See
  [build-plan.md](docs/architecture/build-plan.md) §3.5.
- **No arm produces false alarms** on the decoy or clean-customer populations at this budget.

Supporting figures: the offline extractor's measured recall is **0.632** — it misses 37% of planted
signals and is deliberately the weaker arm; it fires on 20% of decoys. Portfolio outcome rate 9.75%.
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
| `src/earshot/core/` | Deterministic core — corpus, ledger, re-score math. No LLM import allowed |
| `src/earshot/agent/` | The investigator: loop, tools, decision schemas, prompts |
| `src/earshot/llm/` | Provider abstraction, response cache, cost + latency capture |
| `prompts/` | Prompts as versioned files, so a prompt change is a reviewable diff |
| `tests/` | Including `test_separation.py` — proves the extractor cannot see the answer key |
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
