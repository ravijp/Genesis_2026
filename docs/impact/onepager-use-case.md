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
cost per conversation — **$1.58 per 1,000, measured** — not latency on a live call.

**Extract.** Pull out what the customer said — intent to leave, money stress, a life event, a
repeated complaint — with a confidence score and **the exact quote behind it**.

**Remember and re-score.** Keep a standing record per customer that adds signals across
conversations, channels and time, and **re-scores them as new conversations arrive**. A weak signal
today plus a weak signal next month can add up to a strong one. Nothing is ever discarded.

**Investigate and hand over.** When a customer crosses the review threshold, an agent pulls
transactions, account state and prior cases through tools and produces a case file with a verdict, an
owning team, a recommendation and cited evidence. **A person decides every action.**

## The moment that shows it

One customer, three months, three ordinary conversations. None alarming on its own.

Printed by `uv run earshot demo --customers 3000`, not written for this page — customer `CUST-2688`,
review budget 10%, ledger threshold 0.307:

| | what he said | ledger | action |
|---|---|---|---|
| **day 69**, chat | "Can you tell me the very last day I can pay without a charge?" | 0.131 | none — **retained** |
| **day 150**, call | "Things have been tight since my hours got cut." | **0.400** | **case opened** |
| **day 160**, call | "My other half's hours got cut too, so it's both of us at once at the minute." | 0.731 | case stands |

No single-conversation tool catches this, because no single conversation is alarming: the per-call
arm only ever reaches 0.189, its own cut, and is ranked out of the queue at every point. And when the case opens, **the day-69
question is re-read in light of day 160** — the ledger records that it supported 0.131 when it arrived
and supports **0.731** now. Remove any one of the load-bearing quotes and the case falls back below
the threshold.

**The denominator, printed by the same command:** 7 of 132 thin-evidence customers with a real outcome
are caught this way while per-call detection never fires — and **10 of 132** go the other way, caught
by per-call detection and missed by the ledger. It is a trade, one dataset, and the command says so
itself.

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

**Measured on the corpus that ships today, every figure replaying at zero API spend:**

- **Which desks exist at all.** Same 282 planted conversations, same ledger, same threshold, one
  variable — who reads:

  | Desk | keyless lexicon | model reader |
  |---|---|---|
  | **Complaints** | **0 / 20** | **20 / 20** |
  | **Vulnerability** | **0 / 20** | **19 / 20** |
  | **Retention** | **1 / 20** | **16 / 20** |
  | Collections | 9 / 20 | 10 / 20 |

  Two desks receive nothing under the keyless reader. The evidence was in the conversations the whole
  time. **This is the claim of the entry, measured** — and the model column is an **upper bound**,
  because the threshold is a top-K cut over the *offline* reader's ranking held fixed across both arms;
  deriving the model's own cut costs $13.96 and was not spent.
- Reads real customer language at **0.8214 recall (92 / 112)** on public complaint narratives, against
  the keyless lexicon's **0.0357 (4 / 112)**. Scored on an external gold set that no corpus change
  touches.
- **$1.58 per 1,000 conversations** ($0.445562 over 282), p50 latency **1,333 ms**, **0 unparsable
  replies, 0 relocated quotes**.
- **Never-discard earns its place:** on thin evidence the two arms that keep every weak signal rank
  first and second of nine, and both capped-memory arms lose **30 – 0 – 0, p<0.001**.
- **Retro re-scoring is real, not asserted:** 239 of 485 multi-signal ledger entries are worth more
  now than when they were written. Under an unweighted count it is **0 of 485** — the mechanism is
  what makes it possible at all.
- Every case cites a verbatim quote that resolves to a real conversation turn: **0 repairs in 50
  investigations**. The agent judges a balanced sample at **29 / 50** — 16 of 25 real cases caught,
  13 of 25 false alarms dismissed, 0 abstentions, **$0.0306 per case**.

**Known limits:**

- **Routing to the right desk got worse, not better: 27 / 48 correct, 2 wrong, 19 declined**, down
  from 36 / 49 on the previous corpus. The reason is the coverage gap above seen from the other side —
  the confusion matrix's `complaints` row is **entirely empty**, because no complaint customer ever
  crossed under the keyless reader, so no complaint case existed to route. 43 of the 48 scorable cases
  are one desk.
- **The 29 / 50 is not our agent improving.** It read 22 / 50 with 4 / 25 dismissals on the previous
  corpus, and **no part of the agent changed**. The 2026-08-31 rebuild made decoys paraphrase instead
  of repeat verbatim and stopped mangling quotes, so the task got harder to pass by surface form. The
  measurement got more honest; that is all.
- **The model reader is not uniformly better.** It is beaten by 26 regexes on `financial_distress`
  coverage (0.38 vs 0.46) and pushes 3 churn and 6 distress customers over the line at the *wrong*
  desk. Choosing a reader decides which desk you under-serve.
- The review queue is **~90% false alarm** at a 10% budget (25 real outcomes in 240 crossings), and a
  human works every case either way. Reported confidence does not help them triage: **0.837 mean on
  wrong verdicts against 0.852 on right ones**.
- **The ledger does not yet beat chance.** Against a seeded RNG that ignores every signal it is
  18 – 8 – 4, `p=0.076` on the stratum it is built for. We report that as a failure, not a trend.
- **Unbounded memory beats a bounded window on diffuse arcs and loses on concentrated ones** —
  30 – 0 – 0 one way, 1 – 28 – 1 the other, and unproven across the whole portfolio. Our synthetic
  customers average ~3.5 conversations, far shorter than a real customer history.
- **n = 20 customers per trajectory and 50 cases, one dataset each.** Directions with denominators on
  them, not intervals.

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
`onepager-path-to-production.md`. Every figure above was measured on **2026-08-31** against the corpus
that ships, and replays from committed model responses with no API key. The CFPB recall figures are
scored on an external public gold set and are unaffected by any change to our corpus.*
