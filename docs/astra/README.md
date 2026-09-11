# `docs/astra/` — external model review

Home for an independent review of the Genesis 2026 entry by **`gpt-6-astra`** (Experiential Labs
gateway, OpenAI-compatible). Everything for these calls lives here: the brief we send, the questions we
ask, the scripts that send them, and the raw responses that come back.

**Why it exists.** Every judgment in this repo so far is our own. This folder buys one genuinely
external read — a model that has never seen the project, given the facts and none of our conclusions,
asked what the strongest version of the idea is and how to make its value obvious.

## The design rule for this folder

> **The brief carries facts. It does not carry our verdicts.**

`brief.md` is written so a reader cannot tell what we decided or why. No "we chose", no "corrected", no
"never say X", no rankings, no recommendations. Measured numbers appear with their denominators and
their losses. Candidate directions appear as a menu, not a shortlist.

The reason is specific: if the reviewer is told what we already concluded, it either defers to that or
strains to contradict it, and both are noise. Told nothing, it produces an independent read — and where
that read **converges** with conclusions we reached separately, the convergence is evidence. Where it
**diverges**, that is the thing worth looking at.

**Do not edit `brief.md` to add justification for a choice.** That is the one change that destroys what
this folder is for.

## Three phases, in order

The review is deliberately split. Each phase chains to the last via `previous_response_id`, so the
reviewer keeps everything it has already said.

| Phase | Sees | Asked for |
|---|---|---|
| **1** | `brief.md` only | **Its own idea.** Is the problem framed right, what should the product be, the one sentence, the category, and a demo story beat by beat — plus a hostile read of the evidence |
| **2** | *plus* the team's own working documents | To **judge** that analysis, not adopt it. Where it was wrong, where they are wrong, what both missed |
| **3** | nothing new | The recommendation: the product idea to take into the room, how value becomes obvious, what to demo, what to keep |

**Phase 1 is generative, not evaluative.** It explicitly licenses throwing away the current framing —
the mechanism re-points for about a day of authoring and under a dollar, so an answer optimised for
what is already built is the wrong answer. Getting the reviewer to commit to *its own idea* before it
sees ours is also what makes phase 2 a real test rather than a rubber stamp.

**Why split it.** Phase 1 commits the reviewer to a position before it has seen a word of our
reasoning. That makes phase 2 an actual test: it cannot be silently anchored, because its own answer is
already on the record. Where it updates, that is a real update; where it holds, a real disagreement —
and the two are distinguishable, which they would not be in a single blended call.

**Phase 1 must not know a phase 2 exists.** If the reviewer knows more context is coming it will hedge
and defer, and the commitment that makes the design work never happens. `ask-phase1.md` is written to
read as the only call it will ever get. Keep it that way.

## Files

| File | What it is |
|---|---|
| `brief.md` | The facts. Stable — system, evidence, market, the 13 candidate directions, competitors, what is unproven |
| `ask-phase1.md` · `ask-phase2.md` · `ask-phase3.md` | The question for each phase |
| `run.py` | Builds the payload, chains the phases, sends, saves |
| `responses/` | `phaseN.json` (raw) and `phaseN.md` (the prose), one per phase |

## Running

```bash
python docs/astra/run.py 1            # dry run — prints size and cost, sends nothing
python docs/astra/run.py 1 --send     # send phase 1
python docs/astra/run.py 2 --send     # phase 2, chained to phase 1
python docs/astra/run.py 3 --send     # phase 3, chained to phase 2
```

Defaults to `--effort max`. A phase refuses to run if the one before it has not been saved. The key is
read from `C:\tmp\astra_key.txt` and is never committed.

## Gateway facts worth knowing before you spend

| | |
|---|---|
| Endpoint | `https://api.experientiallabs.ai/v1/responses` |
| Context / max output | 1,050,000 / 128,000 tokens |
| Price in / out / cached | **$10 / $50 / $1** per million |
| Reasoning | `reasoning.effort` — `low, medium, high, xhigh, max`; default `medium` |

## Access reality — checked 2026-09-11, and it is not what the credit page implies

**`gpt-6-astra` could not be called.** A `$1` card verification is **not** spendable credit: every paid
model returns `429 insufficient_quota` with `model_requires_purchase`. Probing 35 models — the frontier
tier of every provider on the gateway, *and* every model whose slug ends `-free` — found exactly **four**
callable, which is the same list the 429 error itself names:

| Provider | Model | Notes |
|---|---|---|
| DeepSeek | `deepseek-v4.1-flash`, `deepseek-v4-flash` | 1.05M context, 393K max output |
| OpenAI | `gpt-5.6-luna` | reports reasoning tokens |
| Alibaba | `qwen3.8-27b` | 1M context; bills a trivial amount rather than exactly $0 |

Everything else is gated, **including the explicitly-named `-free` models** — `minimax-m3-free`,
`nemotron-3-ultra-550b-a55b-free`, `gemma-4-26b-a4b-it-free` and the rest all 429. Do not assume a
`-free` slug means callable; probe it.

**Per-route parameter quirks cost two wasted calls to find.** The routes disagree about `reasoning`:

| Model | Rejects | Use |
|---|---|---|
| `deepseek-v4.1-flash` | `reasoning.summary` | `--no-summary` |
| `qwen3.8-27b` | `effort: "high"` (allows `low`, `medium`, `xhigh`) | `--effort xhigh --no-summary` |
| `gpt-5.6-luna` | — | defaults work |

A 400 costs nothing, so probe a new model with a 16-token request before sending the brief.

**Three traps.**

1. **`temperature` and `top_p` are unsupported on this model.** The catalog declares
   `supports_temperature: false`; sending either returns `400 unsupported_parameter` and wastes the
   call.
2. **Reasoning tokens bill as output at $50/M**, and the provider does **not** report the count
   (`reports_reasoning_tokens: false`). A `reasoning_tokens: 0` in the usage block does not mean
   reasoning was off.
3. **Output dominates cost.** Input is cheap enough that sending the whole brief is not the expense;
   a long answer at high effort is. Budget ~$1–2 per deep call.

`store: true` keeps the response for 24h, so a follow-up can pass `previous_response_id` and ask a
second question without resending the brief.
