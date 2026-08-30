# Ear on Every Call — the use case

**Client-ready one-pager (deliverable ① of three).** Zenon Genesis 2026, Track A, team Agentic Trio.
Built and demonstrated on synthetic data only.

---

## The problem

**A bank reads every conversation and remembers no customer.**

Every financial institution runs millions of customer conversations a year — calls, chats,
complaints. It is the earliest and richest warning the institution ever gets. Today almost none of
that signal reaches anyone who can act: quality teams listen to a sample to score agents, and the
rest is transcribed, filed and forgotten. The bank paid to record the conversation and then discarded
the part that mattered.

The tools banks already own make this worse, because of how they are built. Call analytics,
agent-assist and complaint systems all work **inside a single call**. When a call ends and gets a
score, the signal is archived — not carried forward to the next call, the next channel or the next
agent.

So a customer can show frustration in a chat in March, raise a complaint in May, and call about
closing an account in July, and the bank treats all three as separate events. It never notices they
are the same customer, getting closer to the door.

## What we built

A **conversation signal layer** that sits over all customer conversations and turns them into a
living, per-customer memory that any team can read.

**Listen.** Read 100% of conversations, not a sample. Overnight batch, so the cost that matters is
cost per conversation — **$1.66 per 1,000, measured** — not latency on a live call.

**Extract.** Pull out what the customer said — intent to leave, money stress, a life event, a
repeated complaint — with a confidence score and **the exact quote behind it**.

**Remember and re-score.** Keep a standing record per customer that adds signals across
conversations, channels and time, and **re-scores them as new conversations arrive**. A weak signal
today plus a weak signal next month can add up to a strong one. Nothing is ever discarded.

**Investigate and hand over.** When a customer crosses the review threshold, an agent pulls
transactions, account state and prior cases through tools and produces a case file with a verdict, an
owning team, a recommendation and cited evidence. **A person decides every action.**

## The moment that shows it

One customer, four months, four ordinary conversations. None alarming on its own.

| | what she said | ledger | action |
|---|---|---|---|
| **March** | "moving back in with family" | 0.10 | none — **retained** |
| **April** | "on statutory pay just now" | 0.29 | none — **retained** |
| **April** | "we're separating, joint accounts" | 0.66 | none — **retained** |
| **June** | "my husband passed away" | **0.80** | **case opened** |

No single-conversation tool catches this, because no single conversation is alarming. And when the
case opens, **March is re-read in light of June** — the screen shows what each quote scored *then* and
what it contributes *now*. Remove any one of the load-bearing quotes and the case falls back below
the threshold.

That is the product: not detecting a signal in a call, which is commodity, but **accumulating weak
signals no one would act on individually and re-scoring the past when the present changes it.**

## Who reads it

One feed, several teams, each getting a ranked queue of decision-ready cases with the conversations
behind them: **Retention · Collections · Vulnerable Customer Unit · Complaints.** A team with no cases
still appears, and cases the agent declined to route are listed under **"Not routed"** rather than
hidden — a declined route is the case a reviewer most needs to see.

**Lead buyer:** VP/SVP Contact Center Operations, or the Chief Customer Experience Officer — they own
the budget and are measured on retention and complaint-driven risk. **Co-signer:** the Chief
Compliance Officer, who signs off on anything touching 100% of conversations.

One purchase, many owners.

## What is proven, and what is not

**Stated plainly, because a client who discovers an overclaim stops believing the rest.**

**Measured and reproducible:**
- Reads real customer language at **0.8214 recall (92 / 112)** on public complaint narratives.
- **$1.66 per 1,000 conversations**, p50 latency 1,244 ms.
- Routes to the right desk **36 / 49 correct, 2 wrong, 11 declined** — its failure mode is declining,
  which is safe in a human-worked queue.
- Every case cites a verbatim quote that resolves to a real conversation turn: **0 repairs in 50
  investigations**.

**Known limits:**
- **The agent escalates rather than filters** — 22 / 50 on verdicts. What it buys today is routing and
  an assembled audit trail, not a smaller queue.
- The review queue is **~90% false alarm** at a 10% budget (25 real outcomes in 240 crossings).
- **Whether unbounded memory beats a cheap three-conversation window is unproven.** Aggregating a few
  conversations clearly beats aggregating one; that unbounded memory beats a short window is not yet
  shown on our synthetic corpus, whose customers average ~3.5 conversations — far shorter than a real
  customer history.

**It never contacts a customer.** No outbound surface exists anywhere in the system — not disabled,
absent.

## What it would take

Read the conversation feeds a bank already produces; write cases into a queue each team already works.
No speech recognition of ours — banks at this size already transcribe for QA and compliance, and we
consume that output. Nine pipeline stages, **five of them the client's own systems, unchanged.**

Runs as an overnight batch on standard managed services. Ledger updates cost **no model call at all**.

---

*Synthetic data only, per competition rules. Full numbers with denominators: `README.md`. Accuracy,
cost and latency detail: `onepager-accuracy-cost-latency.md`. Deployment detail:
`onepager-path-to-production.md`. Current to 2026-08-30.*
