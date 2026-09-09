# The demo

**7 of your 18 minutes.** This is the only beat a competitor cannot reproduce, so it gets the most
time and the most rehearsal.

US card issuer. Dollars, APR, annual fee, points, retention offer, product change.

---

## The one thing it has to prove

Not that a model can read a transcript. That is commodity, and this idea was already judged a loser
in that framing once.

> **A conversation that was worth nothing on the day it happened is worth something later — and the
> system knew before the obvious call arrived.**

That is a claim about **memory**. Memory is the only thing here a per-call tool cannot copy.

---

## Shape: one customer, three conversations, starting from empty

Three is the right number. Two does not demonstrate accumulation — any diff shows a delta between two
states. Four adds nothing and costs you 90 seconds you do not have.

Start with an empty ledger **on screen**. Feed a transcript. Show what changed. Repeat.

---

## The arc

A single US cardholder. A rewards card with a **$95 annual fee** and a **0% intro APR** period.
Deliberately ordinary — drama is what a keyword system already catches.

### Conversation 1 — day 0, inbound phone: "my card was declined"

Card declined at a restaurant while travelling. The agent fixes it. Call closes.

Mid-call, unprompted, the customer says **the $95 annual fee posted last month and they are not sure
the card is worth it any more.**

| | |
|---|---|
| **What a per-call system does** | Dispositions the call `transaction declined — resolved`, which is *correct*, and discards the fee remark. There is no case to open. Nobody is wrong — the remark is genuinely below any sensible action threshold, and a system built to reconcile to current truth has nowhere to put it |
| **What we do** | Record it as a price/value objection, with the **verbatim quote**, a low confidence, and a date. Open no case. **Discard nothing** |

**That is the entire inversion, on one screen, in the first 90 seconds.**

### Conversation 2 — day 74, web chat: a failed redemption and a question about the rate

The customer is chasing a **rewards redemption that has failed twice**, and asks **what the APR
reverts to** when the intro period ends.

Two signals: **rewards dissatisfaction (redemption friction)** and **promo-expiry price sensitivity**.

**The score crosses here. A case opens.** Three drivers, separable on screen:

- a second and third signal enter the ledger;
- **corroboration** — the evidence now spans two conversations, not one;
- **cross-channel** — it spans phone and chat.

And the day-0 fee remark, worth almost nothing on day 0, **now contributes materially.** A fee
objection followed by rewards friction and rate sensitivity is a different animal from a fee objection
alone.

**The line to land. Slow down and say it:**

> Nothing here would open a case in any system you run today. And we have opened a case.

### Conversation 3 — day 132, inbound phone: "what's my payoff amount?"

The customer asks for the payoff amount and what happens to their points if they close.

**Everybody catches this one. Say so first, immediately, before they think it.** A keyword list
catches it. A per-call classifier catches it. Volunteering that is the most credible thing in the demo.

The point is what is *available* at each moment. At day 132 the customer has decided, and the only
lever left is a retention offer to somebody already walking out the door. At day 74 the levers were a
fee waiver, a product change to a no-fee card, or a points gesture — and the customer had not decided.

---

## Two things NOT to say, and they matter

### 1. Never say "we detect attrition 58 days early"

58 = 132 − 74. **Both are fixture parameters we authored.** Speaking an authored number as a result is
the fastest way to lose a technical listener, and it breaks this project's own rule about illustrative
figures.

**Say instead:** *"in this arc, 58 days — the gap is the point, and the number is ours to choose until
a client's data sets it."*

### 2. The claim that carries the same weight with none of the exposure

> **Your propensity model refreshes on a batch cadence — monthly, typically — and it never sees what
> the customer actually said. Ours moves the moment the transcript lands.**

That is a **latency** claim. It is structural, needs no causal study, no lift number and no client
data, and it cannot be attacked. **Lead with it.** Let the 58 days be a labelled illustration inside
the demo rather than the headline.

---

## The four screens

| # | Screen | On it | The line |
|---|---|---|---|
| 1 | **Empty ledger** | Customer, card, empty signal list, no score | "Nothing. We know nothing about this customer from conversation." |
| 2 | **After conversation 1** | One signal, its verbatim quote, a low score, **no case** | "One remark. No action taken. And we kept it." |
| 3 | **After conversation 2** | Three signals, score crossed, case opened, **the retro column** | "Nothing here opens a case in any system you run. We opened one." |
| 4 | **After conversation 3** | Five signals, the obvious one among them, the day-74 crossing still in the history | "Everyone catches this call. On this arc we opened the case 58 days earlier." |

**Screen 3 is where you slow down.** Screen 4 takes 20 seconds.

---

## The retro column — the hardest thing to fake, and therefore the thing to show

Every ledger entry stores **four** numbers, not one:

| Field | Meaning |
|---|---|
| `contribution_at_write` | What this entry added **on the day it arrived** |
| `score_at_write` | The customer's total **on that day**, using only what was known then |
| `contribution_now` | What it adds **today**, given everything since |
| `score_now` | The customer's total today |

Point at the day-0 fee remark and **read both numbers out loud.** A conversation worth almost nothing
is now worth something — and the system recorded *both* facts instead of overwriting the first.

**Observable, not asserted.** They are stored fields. That is a deliberate build rule, not a
convenience.

Then the sentence that de-risks the whole thing for a CEO:

> **The score is arithmetic, not model output.** Accumulation, decay and thresholds are deterministic,
> unit-tested code. The model's only job is to read the transcript and quote it.

**Do not quote the line count of that code.** "It's 183 lines of Python" is meant as reassurance and
lands as *"so there's no product here."*

---

## Answer the point-in-time question before it is asked

Showing the retro column invites the sharpest question a modeller has:

> *"You just told me the score rewrites history. My feature store has to serve the value as it stood
> on the observation date. So the thing you spent seven minutes demoing is the thing I have to turn
> off."*

Answer it unprompted and it becomes a sophistication beat instead of a liability:

> **Training joins on `score_at_write`. Inference and the operational queue use `score_now`** — because
> for a live decision, today's best estimate is exactly what you want. Retro re-scoring earns its keep
> in production scoring and in the human queue, never in the training join. Both values are stored, so
> point-in-time is a query, not a rebuild.

---

## Three claims while the screens are up

| Claim | Evidence | Status |
|---|---|---|
| **Safe to re-run** | 260 messages fed twice → still 34 entries, 1 case. No double-counting | Measured |
| **Fails visibly** | A malformed transcript is isolated and raises, rather than silently scoring zero — and the deployed alarm **did fire**: `earshot-dev-ingest-failures` OK → ALARM 2026-09-03 04:06:22 IST, back to OK 04:33:22 | **Measured, verified from CloudWatch 2026-09-09** |
| **A human decides** | No outbound contact surface exists anywhere — no route, no button, no handler. Not switched off. **Absent** | Structural |

**The middle one is verified — say it.** The repo used to contradict itself about whether any alarm
had ever fired. Settled from CloudWatch alarm history on 2026-09-09:
**`earshot-dev-ingest-failures` went OK → ALARM at 2026-09-03 04:06:22 IST and returned to OK at
04:33:22.** The other five alarms have never left OK, which is the honest half — one threshold is
observed, five are still reasoned.

**Caution on the third one.** *"A human decides"* must arrive **together** with the answer to "so what
happens on day 74 when the customer isn't calling?" (see `01-THE-STORY.md`, beat 4). Said alone, it
reads as an admission that we cannot act on our own headline.

---

## The counter-line — say it whole or not at all

On the generic corpus at 3,000 customers: **7 / 132** customers where the ledger catches what per-call
detection misses entirely, and **10 / 132** the other way.

**Never say the bare pair.** Unaccompanied, in the demo beat, to a CEO with 18 minutes, "7 ours, 10
theirs" says *the incumbent wins more often than we do* — and it is misleading **against us**, because
those are disjoint-catch counts, not a head-to-head.

Whole version:

> On the same corpus the model reader surfaced 16 of 20 retention cases where a keyword reader
> surfaced 1. There are also 10 of 132 customers the per-call approach catches and we don't, and 7 the
> other way. We publish both directions.

**Every figure in that sentence is generic-corpus. Label it as such.** See `03-REFERENCE.md`.

---

## What has to be true before this is a real demo

The mechanism is built and deployed. The card content is not. In order:

| | Step | Cost | Notes |
|---|---|---|---|
| **A** | Author 5–10 US-card-flavoured churn fragments into `corpus_lexicon.py` | **$0**, a few hours | **Not optional and not a re-run.** Running the tools without this produces the same generic numbers with a new label |
| **B** | `earshot sweep --seeds 30 --customers 1500` | **$0**, ~104s | First card-flavoured recall read |
| **C** | `tools/reader_coverage.py --reader both --per-trajectory 20` | **~$0.45** | The single most pitch-relevant number: does the model reader find card churn evidence the lexicon misses |

**Total ~$0.45.** Quote whatever it produces with its denominator and the explicit caveat that it is a
direction, not an interval.

**Budget update, 2026-09-09.** Ravi raised the ceiling to **$10-15** to make the gen-AI evidence
stronger, and **~$10.5 of it went on a keyed 10-seed run** with Haiku 4.5 (`earshot run --seed 1..10
--customers 200 --extractor model`). **Step A is still the constraint and still unbought** — it costs
hours, not dollars, and steps B and C without it produce the same generic numbers under a new label.

**And one card-specific result arrived for $0**, which is what step C was supposed to buy: the CFPB
benchmark turned out to be **55/150 credit-card narratives**, so splitting the already-published run
by product gives real card numbers from real US complaint language. **Both halves are in the honesty
beat of `01-THE-STORY.md`** — the reader fires on **29/29** marked card documents and gets **churn
intent 1 of 8**. Read it before quoting any of it.

---

## Rehearsal — the part that is actually behind

**Two dry runs were committed. Zero have been done.** Every fix in this revision is a *wording* change,
and wording changes only survive contact with a room if they have been said out loud at least once.

1. **Book both dry runs.**
2. **Record the demo the day before.** A room with no wifi must not be able to break your best beat.
3. **Narration must never share the reader's extractor.** A warm cache turns "live" into a replay — and
   that is a lie told by accident.
4. **Re-login to AWS the morning of, and again before walking in.** The SSO token expires in hours, and
   a dead token looks exactly like broken code.

---

## Timing inside the 7 minutes

| Beat | Min |
|---|---|
| Empty ledger + conversation 1 | 1.5 |
| **Conversation 2 — the crossing and the retro column** | **3.0** |
| Conversation 3 — "everyone catches this" | 0.5 |
| Point-in-time answer + the three claims | 1.5 |
| The counter-line | 0.5 |

The crossing gets the most time because it is the only part nobody else can show.
