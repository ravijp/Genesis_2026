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
| 1 | Synthetic multi-channel corpus (calls, chats, complaints) with ground truth authored **before** the prose | Built — 4 signal families, difficulty strata set by how the evidence is spread, two kinds of lookalike, outcomes drawn rather than assigned. 15,000 customers scored in ~20 seconds |
| 2 | Signal-extraction pipeline, run at volume | Built — ~1,770 conversations/sec, no API keys required |
| 3 | First recall and precision numbers | Built, then rebuilt at proper scale — see §2 |
| 4 | The accumulation scenario | Built and reproducible on demand |
| 5 | *(Sprint 2)* Per-customer ledger and re-scoring logic as a pure, tested function | **Pulled forward** — the accumulation scenario cannot be rehearsed without it. Deterministic, no model calls |

Also landed, beyond the commitment: **an investigator agent** that works each flagged customer using
tools (transactions, account history, prior cases) and produces a case file with quoted evidence; a
five-arm comparison harness with per-mechanism ablations; multi-dataset evaluation with proper
significance testing; 94 tests; and one-command reproduction with a run manifest.

**A word on status.** Nothing above is marked Done on our board, and that is deliberate. All of it was
written by one person over a weekend and none of it has been reviewed by a second — Namit and Ishant
have not seen it yet. Given what our own review then found (§3), "Done" would have been the wrong word.

## 2. Where the numbers stand

**Short version for the room:** the core idea works, measured properly. On the customers it exists
for — worry spread thin across several conversations, nothing alarming in any one of them — the
customer memory catches meaningfully more than a tool that scores each call and forgets. Across the
whole portfolio the approaches are level. The extra scoring refinements we layered on top are not yet
earning their keep, and that is Sprint 2's question.

Measured across 10 independent datasets of 1,500 customers each — 1,945 customers who went on to have
a real outcome — at a review capacity of 10% of the portfolio:

- On **thin-evidence cases**: memory catches **134 of 780**; scoring-each-call-and-forgetting catches
  **96 of 780**. Memory wins **8 of the 10 datasets, ties 2, loses none** (p=0.008). This is the claim
  the entry is built on, and it holds.
- **Across the whole portfolio, nothing separates the approaches.** Memory neither beats nor loses to
  per-call detection overall.
- **A plain count of signals does as well as our weighted scoring.** Decay, corroboration and channel
  weighting have not paid for themselves yet — either we justify them in Sprint 2 or we take them out.

*If asked how solid this is:* solid enough that we threw away our own first answer. Our first run used
a single dataset with 39 relevant customers, where every difference we reported was one or two people —
noise. We rebuilt the evaluation to run ten datasets and test the comparisons properly before putting
any number in writing.

## 3. We reviewed our own work adversarially, and it found six real problems

This is the part we would most want a technical judge to hear. We ran independent reviews over the
code and the evaluation with one instruction: assume it is wrong and prove it. They found six genuine
defects, all in work we would otherwise have called finished:

| What was wrong | Why it mattered |
|---|---|
| The demo's alert threshold was calculated *from the answer* | It guaranteed the headline moment for any customer, next to a claim about a comparison we never actually ran |
| Our test data leaked the answer key into the agent's tools | A customer's risk value was a perfect stand-in for whether they were a real case, so the agent could partly cheat without reading anything |
| A comparison arm had a window that never applied | "The alternative a judge will ask about" was silently the same as another arm |
| The spending cap per case was never actually passed | We claimed bounded cost and shipped none |
| A quality metric was printed as zero by construction | It was never measured |
| Our headline number came from 39 customers | Every "finding" was a difference of one or two people |

All six are fixed, and the fixes are why §2's numbers changed. Two conclusions we had already written
down did not survive, and we retracted them in writing rather than quietly editing.

The point for the committee: **we would rather find these now than have a judge find them in
September.** The reviews are cheap and we are running them every sprint.

## 4. One thing we found about our own novelty claim

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

## 5. Access — our miss, now unblocked, with three things still open

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
| 3 | **A project admin on JIRA `AT`** | We have the board and the backlog is loaded, but we cannot delete issues or turn on sprints — both need someone with project-admin rights. Sprint tracking is scored, and our gates are named Sprint 1/2/3 |

None of these blocks this week's build. Items 2 and 3 do block the *evidence* the rubric asks for, so
we would rather resolve them now than in September.

## 6. Next, to the combined Sprint 1+2 demo on 2026-08-24

Corpus at full volume with the four strata · the memory question in §2 resolved either way · reviewer
queue with approve/dismiss/route · cost and latency next to accuracy · the accumulation moment plus a
deliberate failure-recovery beat · **a recorded fallback taken on 2026-08-17**, so a live failure on the
day cannot cost us the demo.
