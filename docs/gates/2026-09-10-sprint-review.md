# Sprint review — 2026-09-10, 20:00–20:30

**Ravi's script for the cut round.** Written 2026-09-03 from what is measured and deployed on that
date.

**What is different about this one, and it changes the shape of everything below:**

- **Venkat (CEO) and Farhan (COO) are judging.** Not the technical committee. Lead with the business
  case; architecture only when asked.
- **It decides the shortlist** for the Final Dry Run and Finals. This is a cut, not a checkpoint.
- **The explicit ask is narrow:** *"progress against your sprint plan — what you committed to for this
  sprint vs what's actually done."* Answer that question first and directly. The committee said in
  Sprint 1 that they did **not** want a Jira walkthrough; nothing suggests that changed.
- **30 minutes, ~10 invitees.** Budget **12 minutes of talking** and expect the round to be won or
  lost in Q&A. §8 is the Q&A prep and is the most important section here.

**Calendar discrepancy — confirm this before the 8th.** `CLAUDE.md` and
`sources/genesis-committee-comms.md` both record the Sprint 3 gate as frozen on **2026-09-07**. This
invite is **09-10**. Either the gate moved or this is a separate round. `2026-09-07-sprint-3-demo.md`
is the product-demo script and stays valid for whichever slot is the demo; **this** file is the
committed-vs-done review.

---

## 1. Open with the answer (60 seconds)

> A bank reads every conversation and remembers no customer. Call analytics, agent-assist and
> complaint tools all work *inside a single call* — when the call ends and gets a score, the signal is
> archived, not carried forward. So a customer shows frustration in a chat in March, raises a
> complaint in May, and calls to close the account in July, and the bank treats all three as separate
> events. It never notices they are the same person getting closer to the door.
>
> We built the layer that remembers. It reads 100% of conversations, keeps a standing per-customer
> record, and **re-scores the past when the present changes it.** Nothing is ever discarded.

**Then say the commercial shape immediately, because this is a CEO and a COO:**

> **$1.58 per 1,000 conversations, measured.** Overnight batch, so the number that matters is cost per
> conversation, not latency on a live call. **Lead buyer: VP/SVP Contact Center Operations or the
> Chief Customer Experience Officer** — they own the budget and are measured on retention and
> complaint-driven risk. **Co-signer: the Chief Compliance Officer**, who signs anything touching 100%
> of conversations. One purchase, several owners.

---

## 2. Committed vs completed — the actual question they asked

The submitted brief committed Sprint 3 to five things
([`:124-126`](../sources/submission-ear-on-every-call.md)). **Three done, one partial, one missed.**

| # | Committed for Sprint 3 | State |
|---|---|---|
| 1 | All three team views live on the same feed | **Done** — and it is four desks, not three: Retention, Collections, Vulnerability, Complaints. A desk with no cases still appears, and cases the agent declined to route are shown under "Not routed" rather than hidden |
| 2 | Accumulation demo rehearsed **and recorded as a fallback** | **Partial.** Built and it replays with no API key and no network. **Not yet recorded.** Recording is booked for 09-09 |
| 3 | Full eval numbers (accuracy, cost, latency) in the README | **Done, and past the commitment** — three readers compared, every rate carries its denominator, and the losses are published alongside the wins |
| 4 | **Two dry runs done** | **Not done. Zero.** The clearest miss on this list — see §6 |
| 5 | Path-to-production plan written | **Done** — `docs/impact/onepager-path-to-production.md` |

**Then the part that is worth more than the table:** the biggest thing built this sprint was not on
that list at all.

> The brief committed to a *proof*. What we have is **running on AWS**. Three Lambdas, four queues,
> three DynamoDB tables, and the whole customer book pushed through it end to end — and the deployed
> system agrees with our local pipeline to the last digit. That was not a Sprint 3 commitment. We
> pulled it forward because "it works on my laptop" is not an answer to a feasibility question.

---

## 3. The moment that shows it (3 minutes — do not cut this)

One customer, three months, three ordinary conversations. Printed by `earshot demo`, not written for
a slide.

| | what he said | ledger | action |
|---|---|---|---|
| **day 69**, chat | *"Can you tell me the very last day I can pay without a charge?"* | 0.131 | none — **retained** |
| **day 150**, call | *"Things have been tight since my hours got cut."* | **0.400** | **case opened** |
| **day 160**, call | *"My other half's hours got cut too, so it's both of us at once."* | 0.731 | case stands |

Say:

> Nothing here is alarming on its own, and that is the point. The per-call approach never reaches its
> own threshold on this customer — it peaks at 0.189 and is ranked out of the queue at every step. And
> when the case opens, **the day-69 question is re-read in light of day 160**: the record shows it
> supported 0.131 when it arrived and supports 0.731 now.

**Give the denominator in the same breath, because a CEO who finds the caveat later stops believing
the rest:**

> 7 of 132 thin-evidence customers are caught this way where per-call detection never fires — and
> **10 of 132 go the other way**, caught by per-call and missed by us. It is a trade, on one dataset,
> and the command prints that itself.

**Then land it on the deployed system**, which is the new part:

> That is the demo. Here is the same behaviour in production: a signal that scored **0.1306** on day
> 21 against a 0.60 cut — a fifth of the threshold, the kind every system in this market discards —
> read back out of the deployed database 73 days later as the **load-bearing** evidence in an open
> case.

---

## 4. Where the implementation actually is (3 minutes)

**Two live environments, same customer book, same infrastructure, one variable: who reads.**

| | keyless reader | model reader |
|---|---|---|
| signals on the ledger | 34 | **103** |
| cases opened | 1 | **9** |
| desks receiving work | Collections only | **Complaints, 9 of 9** |

> Two desks receive **nothing** under the cheap reader — not fewer cases, none. Whether a review desk
> exists at all is decided by whether anything can read the conversations. That is the product
> argument in one number, and it is now demonstrated on deployed infrastructure rather than in a
> spreadsheet.

Three things to say about readiness, in business terms:

1. **It is safe to re-run.** We fed the same book twice — 260 messages — and it produced the same 34
   signals and the same one case. Duplicate delivery cannot double-count a customer.
2. **It fails visibly.** One malformed transcript: that record fails alone, the healthy ones commit,
   and the monitoring alarm goes red. We tested that by breaking it on purpose.
3. **A person decides every action.** There is **no outbound contact surface anywhere in the system** —
   not disabled, absent. It cannot email, message or call a customer. For the Compliance co-signer
   that is the whole conversation.

---

## 5. Why we should advance (60 seconds)

> Four reasons, and I would put the third first if you only take one.
>
> 1. **The idea is not commodity.** Detecting a signal in a call is a solved, crowded market. Keeping
>    the signals that *failed* detection and re-scoring them is the inversion, and we have not found
>    anyone doing it.
> 2. **It is built, not designed.** Deployed on AWS, fed end to end, 903 tests, reproducible from a
>    clean clone with no API key.
> 3. **We publish what we got wrong.** Including a pre-registered result that died and a statistical
>    gate the entry currently fails. Any judge can find those in the repo in five minutes — better
>    that we hand them over.
> 4. **There is a named buyer and a real price.** $1.58 per 1,000 conversations, and a Compliance
>    co-signer who can only say yes because there is no outbound path.

---

## 6. What is not done — say it before they ask

**The dry runs. Committed to two, done zero.** Do not soften this.

> That is a real miss and it is mine. The cause is that the deployment work took the sprint — I chose
> a running system over a rehearsed one. **Both dry runs happen 09-08 and 09-09**, and the demo gets
> recorded on 09-09 so that a room with no wifi cannot break it.

**The entry currently fails one of its own statistical gates** — the ranking comparison against a
random baseline is not significant. Frame it correctly and it is a strength:

> We pre-registered our headline result, the corpus was rebuilt, and the result died — so we retired
> it and published the dead row permanently rather than quietly re-cutting. The replacement passes
> 30–0. But the gate we tied it to, against a random ranking, we currently **fail**. The reason is the
> coverage finding above: there is so little in the stream for the cheap reader to rank that chance is
> competitive. That is an argument for the reader, not a defence of the ranking. **Closing it costs
> about $10 of model spend and we have the budget** — the decision is whether it is the best use of
> the remaining sprint.

**Other honest gaps, if pushed:** one shared permissions role instead of per-function least privilege ·
alarms go red in a console and page nobody, because there is no notification path on this account ·
write-once evidence storage degraded to permissions because the account cannot enable object locking ·
the reviewer screen is read-only, and that one is deliberate.

---

## 7. Timings

| Section | Minutes |
|---|---|
| 1 — the answer + commercial shape | 1 |
| 2 — committed vs completed | 3 |
| 3 — the moment | 3 |
| 4 — implementation | 3 |
| 5 — why we advance | 1 |
| 6 — what is not done | 1 |
| **Talk total** | **12** |
| Q&A | 18 |

**If you get cut to 10 minutes:** keep §2 (it is the question they asked) and §3 (it is the product).
Compress §4 to the two-column table and one sentence. **Never drop §6** — in a cut round, the team
that volunteers its miss is the one that gets believed about everything else.

---

## 8. Q&A prep — this is where a cut round is decided

**Venkat / Farhan are executives. Expect commercial and risk questions, not architecture.**

**"What does this save or earn a bank?"** Be careful here — **we have not measured revenue impact and
must not imply we have.** Say: *"We have measured what reaches a desk and what it costs to get there.
Two desks go from zero cases to nearly full coverage at $1.58 per 1,000 conversations. What that is
worth depends on the bank's own retention and complaint-handling economics, and I would want their
numbers rather than inventing mine."* **That answer is stronger than a made-up ROI and cannot be
punctured.**

**"Is this real or a prototype?"** Real, deployed, and reproducible — but say the boundary plainly:
synthetic data only, which is the competition rule, and one integration modelled rather than a live
bank feed.

**"What stops it acting on a customer by mistake?"** It has no way to. No outbound contact surface
exists in the system. Every action is a human decision on a queue.

**"Why should this be shortlisted over the other teams?"** §5. Lead with "it is built, not designed."

**"What do you need from us?"** Have an ask ready — a vague answer here wastes the best question you
will get. Candidates: a decision on the ~$10 to close the statistical gate · access to a real
anonymised conversation feed for the Finals · an introduction to a design partner who owns a contact
centre.

**"Can you show it now?"** Assume yes and be ready — `2026-09-07-sprint-3-demo.md` §7 has the fallback
ladder. If the room has no wifi, everything but the live-AWS beat still runs from a local file.

**If asked something you have not measured, say so and give the price of finding out.** Every open gap
in this project has a number attached; that habit is worth more in front of a COO than any single
result.
