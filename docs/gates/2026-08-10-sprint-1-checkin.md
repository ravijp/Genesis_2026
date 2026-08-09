# Sprint 1 check-in — 2026-08-10, 10:30-10:45

The committee asked for three things and explicitly not a Jira walkthrough: **committed vs completed**,
**reasons and next steps for anything pending**, and **roadblocks**.

---

## 1. Committed vs completed

**Committed** (Sprint 1 in the submitted overview): build the synthetic multi-channel corpus with seeded
ground truth · build the signal-extraction pipeline and run it at volume · show first recall and
precision numbers · build and rehearse the three-conversation accumulation scenario.

**Completed — all four, plus one item pulled forward from Sprint 2:**

| # | Item | State |
|---|---|---|
| 1 | Synthetic multi-channel corpus (calls, chats, complaints) with ground truth authored **before** the prose | Done — 4 signal families, generative difficulty strata, two kinds of decoy, stochastic outcomes. 400 customers / 1,393 conversations generated and scored in under a second |
| 2 | Signal-extraction pipeline, run at volume | Done — ~1,750 conversations/sec, no API keys required |
| 3 | First recall and precision numbers | Done — with an honest caveat, see §2 |
| 4 | The three-conversation accumulation scenario | Done and reproducible on demand |
| 5 | *(Sprint 2)* Per-customer ledger and re-scoring logic as a pure, tested function | **Pulled forward** — the accumulation scenario cannot be rehearsed without it. 18 unit tests, deterministic, no model calls |

Also landed: a four-arm comparison harness, per-mechanism ablations, one-command reproducibility with a
run manifest (seed, git SHA, config hash), and committed result artifacts per run.

## 2. Where the numbers stand

**Short version for the room:** first numbers are in. Memory helps exactly where we said it would —
on customers whose worry is spread thin across several conversations — and costs us on the obvious
cases. The scoring refinements we built on top are not yet earning their place. We are carrying that
into Sprint 2 as the open question rather than tuning it quietly.

Measured across 10 independent datasets of 1,500 customers each (1,651 customers who went on to have
a real outcome), at a review capacity of 10% of the portfolio:

- On **thin-evidence cases**, memory catches 0.147 vs 0.114 for a tool that scores each call and
  forgets — winning 8 of the 10 datasets.
- **Overall it loses**, 0.150 vs 0.177, on 10 datasets out of 10. Accumulating evidence dilutes a
  single decisive conversation, and most real cases are decisive.
- **A plain count of signals does as well as our weighted scoring** (5–4–1 across datasets). Decay,
  corroboration and channel weighting have not yet paid for themselves.

*Not to volunteer, but the honest answer if asked how solid this is:* an earlier single-dataset run
suggested a stronger negative result, and it turned out to be one customer's worth of noise. We
re-ran it at ten times the scale before writing anything down.

## 2b. Detail, if the room wants it

The entry rests on one claim: a customer-level memory that accumulates weak signals beats a per-call
tool that scores each conversation and forgets it. We built the harness to test that claim rather than
to illustrate it. At 400 customers, equal alert budget (every arm flags exactly the same number of
customers, which is how a review team's capacity actually works):

- **On the stratum the memory exists for** — arcs where evidence is spread thin across conversations —
  the ledger arms beat per-call detection: **0.191 vs 0.143 recall**, a 34% relative lift.
- **Overall, per-call detection still wins: 0.154 vs 0.128.** Memory loses badly where a single loud
  conversation carries the signal (0.071 vs 0.214) — accumulation dilutes a decisive one-off.
- **A dumb unweighted sum matches the full ledger exactly.** Every sophisticated mechanism —
  corroboration weighting, cross-channel weighting, confidence weighting — currently contributes zero.
- **Decay and escalation actively hurt**: removing either *improves* recall by 0.026.

We would rather know this on 2026-08-09 than on 2026-09-07. Sprint 2 is now pointed at the specific
question the data raised: does the accumulation layer earn its place once it is combined with per-call
detection instead of replacing it — which is what the overview always described ("it adds a memory on
top of tools banks already run, rather than replacing them").

Two false starts are worth naming because they are the kind of error that survives into a demo if
nobody checks: a first attempt at combining the two arms was byte-identical to the ledger alone (the
two score scales are not comparable), and a first "equal budget" implementation let one arm flag 47
customers while another flagged 21 (score ties broke the budget). Both are fixed.

## 3. One thing we found about our own novelty claim

The overview says *"what none of them keep is a customer-level memory that accumulates and re-scores
signals across every conversation over time."* We pressure-tested that against the market and it is not
accurate as written: **Twilio shipped a product called Conversation Memory to GA on 2026-05-06** —
persistent, cross-channel, per-customer. MorganAsh MARS already runs a standing per-customer
vulnerability score in UK financial services.

The narrower claim that survives is stronger, and it is what we are building: Twilio's memory
**reconciles to current truth** — new observations supersede old ones, which is right for
personalization and wrong for risk, because three faint signals must *sum* rather than overwrite. What
no one ships is a ledger that **never discards a sub-threshold signal** and **re-scores earlier
conversations in light of later ones**. That retro re-score is now on screen in the demo rather than
asserted in prose.

## 4. Access — our miss, now unblocked, with three things still open

**Owning it first:** the committee asked for tooling requirements by 2026-07-24 and chased on
2026-07-29. We never replied. That is on us, not on the committee, and it is why we spent two weeks
without model access. The requirements list goes over immediately after this call.

**We unblocked ourselves rather than wait.** The pipeline runs end to end with **zero API keys** on a
deterministic offline provider, and model access has been bridged on a personal OpenRouter account so
the agent layer could be built. So there is no blocked work to report — but three things are still open:

| # | Open item | Why it matters |
|---|---|---|
| 1 | **Zenon-provided model keys** (Claude + a comparison model, with the budget limit) | Rule 2 says Zenon provides keys with budget limits and rule 1 says the IP is Zenon's. The final submission should not be running on a team member's personal account. Also please confirm direct API vs AWS Bedrock |
| 2 | **AWS CodeCommit repository URL + credentials** | *"Functional prototype: code in AWS CodeCommit"* is a named required deliverable, and commits/PRs are scored in the operating model. We have no repo URL, so we cannot comply even in principle. Our full commit history is intact and will be pushed as history, not squashed |
| 3 | **JIRA project key / board confirmation for Agentic Trio** | The backlog and sprint tracking are scored. We have board access; we want to confirm we are filing under the right project before we load it |

None of these blocks this week's build. Items 2 and 3 do block the *evidence* the rubric asks for, so
we would rather resolve them now than in September.

## 5. Next, to the combined Sprint 1+2 demo on 2026-08-24

Corpus at full volume with the four strata · the memory question in §2 resolved either way · reviewer
queue with approve/dismiss/route · cost and latency next to accuracy · the accumulation moment plus a
deliberate failure-recovery beat · **a recorded fallback taken on 2026-08-17**, so a live failure on the
day cannot cost us the demo.
