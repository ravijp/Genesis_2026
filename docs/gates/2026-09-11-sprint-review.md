# The 09-11 pitch — 2026-09-11, 20:30-21:00 IST

> ## ⚠ RAVI — DECIDE THIS FIRST: there are now TWO scripts for this meeting, and they disagree on market
>
> **This file is the UK story.** It leads with the **£650 Financial Ombudsman case fee**, UK card
> delinquency and UK debt-collection buyers.
>
> **`docs/credit-card/01-THE-STORY.md` is the US story**, written 2026-09-09 for this same gate. It is
> dollars, APR, annual fee and points, it deleted ten UK files deliberately, and it lists *"quote a
> pound sign"* as one of the three things most likely to lose the room.
>
> **Both cannot be true. One of them has to go before you walk in**, and the handover already records
> that two competing demo scripts is the exact failure this repo cleaned up once before.
>
> **My read, but it is your call:** the US story is the later, deeper and more heavily red-teamed work
> (two adversarial passes, KS-1..KS-16), and your last three rounds of instruction have all been about
> it. **Its weakness is that it threw away the single best number in the repo** — the £650 is a
> *published tariff*, not a projection, and the US has no equivalent, which is why the US money beat
> had to be rebuilt on a chain with an admitted hole in it.
>
> **If the audience is a Zenon cut round judging a UK-market entry, this file wins on the strength of
> that one number. If the entry is US-market, this file is a liability.** I have not deleted anything.


**The gate.** The 09-07 date is dead; this replaces it. One document, one story, **18 minutes
including the demo**, leaving 12 for questions.

**Audience: Venkat (CEO) and Farhan (COO), judging a cut round** that decides the shortlist for the
Final Dry Run and Finals. What they are buying is: *is this a strong product, what is it worth in
money, and could I walk into a bank and win a project with it?* **Cost-per-conversation and
compliance mechanics are not the lead** — they are answers to questions 8 and 9, not the opening.

---

## The whole story in five sentences

1. A bank has millions of conversations a year and remembers **no customer** across them.
2. Every tool it owns works inside a single call, so a customer who drifts toward leaving across
   three months looks like three unrelated events.
3. We keep every signal — including the weak ones everyone discards — and **re-score the past when
   the present changes it**.
4. That turns two review desks from receiving **nothing** into receiving nearly everything.
5. Each complaint caught before it reaches the Ombudsman saves the bank **£650 in case fees alone**,
   win or lose.

**Say sentence 5 in the first ninety seconds.** It is the only number in this deck that a CEO cannot
argue with, because it is a published tariff and not a projection.

---

## 1. The money (3 minutes) — lead here

**The hard floor, and it is a tariff, not an estimate.** The UK Financial Ombudsman charges a
respondent firm a case fee of **£650** when a complaint is upheld against it and **£475** when it is
not — *the firm pays either way* — capped at £680, against a £2,000 annual allowance
([Financial Ombudsman Service, case fees](https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/case-fees)).
From **1 April 2026** the largest firms are billed **quarterly in advance** on expected volumes
([FOS consultation, 2025-08](https://www.financial-ombudsman.org.uk/files/324663/2025-08-Differentiated-case-fee-consultation.pdf)),
so the cost is now a forecastable line item a COO already owns.

**The volume.** The Ombudsman took **214,600 new complaints in 2025/26**, down ~30% from **305,700**
the year before; credit cards alone were **~22,800**
([FOS annual complaints data 2025/26](https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/our-insight/annual-complaints-data-and-insight-2025-26)).

**The lever we measured.** Same conversations, same threshold, one variable — who reads:

| Desk | what the bank's current tooling surfaces | with our layer |
|---|---|---|
| **Complaints** | **0 of 20** | **20 of 20** |
| **Vulnerability** | **0 of 20** | **19 of 20** |
| Retention | 1 of 20 | 16 of 20 |
| Collections | 9 of 20 | 10 of 20 |

> Two desks receive **nothing**. Not fewer cases — none. The evidence was sitting in the
> conversations the whole time.

**The arithmetic, out loud, with no invented inputs:**

> Per **1,000** complaints a bank stops before referral: **£650,000 in Ombudsman case fees alone** —
> before redress, before handling time, before the remediation programme. That is the floor, and it
> is the one number in this pitch that is a published tariff rather than a forecast.
>
> The multiplier on top is theirs, not mine: what a retained current-account customer is worth, and
> what their complaints handling costs per case. **I would rather plug in their numbers than invent
> mine** — but the direction does not depend on the inputs, because the desks currently see zero.

**If pushed for a total business case,** give the model, not a number: *incremental customers
surfaced × their intervention success rate × their value per customer.* We supply the first term and
have measured it. **Do not manufacture the other two.** A CEO who catches an invented ROI stops
believing the measured part too — and the measured part is the good part.

---

## 2. The demo (8 minutes) — the product, in the customer's words

**One customer, three months, three ordinary conversations.** Printed by `earshot demo`, not written
for a slide.

| | what he said | our score | action |
|---|---|---|---|
| **day 69**, chat | *"Can you tell me the very last day I can pay without a charge?"* | 0.131 | **nothing — but retained** |
| **day 150**, call | *"Things have been tight since my hours got cut."* | **0.400** | **case opened** |
| **day 160**, call | *"My other half's hours got cut too, so it's both of us at once."* | 0.731 | case stands |

> Nothing there is alarming on its own — that is the point. A per-call tool peaks at 0.189 on this
> customer and ranks him out of the queue at every step. And when the case opens, **the day-69
> question is re-read in light of day 160**: our record shows it was worth 0.131 when it arrived and
> is worth 0.731 now. That re-reading of the past is the product.

**Give the trade in the same breath** — it costs 15 seconds and buys the room:

> On one dataset: 7 of 132 thin-evidence customers are caught this way where per-call detection never
> fires, and **10 of 132 go the other way** — caught by per-call, missed by us. The command prints
> that itself.

**Then show it running.** Two live environments on AWS, same customer book, one variable:

| | bank's current-generation reader | ours |
|---|---|---|
| signals remembered | 34 | **103** |
| cases opened | 1 | **9** |
| desks receiving work | one | **Complaints, 9 of 9** |

Three sentences on why it is real, then stop:

1. **Safe to re-run** — we fed the same book twice, 260 messages, and got the same 34 signals and the
   same one case. It cannot double-count a customer.
2. **Fails visibly** — we broke one transcript on purpose: that record failed alone, the healthy ones
   committed, and the monitoring alarm went red.
3. **A person decides everything** — there is **no way for this system to contact a customer**. Not
   switched off. Absent.

---

## 3. Can we sell this? (3 minutes) — the question they are actually asking

> Yes, and here is why I think a first project is winnable.

**Someone already got paid for a thinner slice of this.** Salient raised **$60M at a $350M
valuation**, led by a16z, for an AI voice agent that makes collections calls — named customers
including Westlake Financial, Exeter Finance and Consumer Portfolio Services
([a16z, 2025-07-28](https://a16z.com/announcement/investing-in-salient/)). That is one desk, one
channel, and no memory across conversations. The category is funded and proven.

**The specific space we would sell into is empty.** Our own research found **no named agentic
deployment at any UK debt-collection agency** — Lowell, Arrow, Intrum, Cabot — and at Barclays,
**no collections or servicing agent, a confirmed absence** rather than an unchecked one
(`docs/impact/finance-brief.md`, as of 2026-07-14).

**The buyer is identifiable and the timing is now.** UK card delinquency is deteriorating sharply:
accounts missing two payments **up 16.3% year-on-year** and three payments **up 17.3%**, which FICO
called the most significant annual deterioration across any delinquency category
([FICO via BusinessWire, 2026-06-24](https://www.businesswire.com/news/home/20260624361500/en/FICO-UK-Credit-Card-Market-Report-April-2026)).
The FCA published the **Mills Review on 2026-07-06** recommending the country "enable foundations for
agentic finance," and found **1 in 5 UK adults already open to AI making financial decisions for
them, strongest for debt advice** ([FCA](https://www.fca.org.uk/publication/corporate/the-mills-review.pdf)).
**Barclays is already inside the FCA's AI Live Testing sandbox** (cohort 2, from April 2026) — a bank
publicly rehearsing exactly this kind of deployment
([FCA, 2026-04](https://www.fca.org.uk/news/press-releases/fca-announces-second-cohort-ai-live-testing)).

**And the cautionary tale is on our side.** Klarna's AI assistant peaked at the work of 853 agents
and roughly **$60M in annual savings**, then publicly reversed and rehired humans after quality
complaints on nuanced cases ([CX Dive](https://www.customerexperiencedive.com/news/klarna-reinvests-human-talent-customer-service-AI-chatbot/747586/)).
That is the argument for our design, not against it: **we put a human in front of every action by
construction.** The market has already learned what happens otherwise.

---

## 4. Committed vs done (3 minutes) — they asked for this explicitly

The brief committed Sprint 3 to five things
([`:124-126`](../sources/submission-ear-on-every-call.md)). **Three done, one partial, one missed.**

| Committed | State |
|---|---|
| All three team views live on one feed | **Done** — four desks, not three. A desk with no cases still shows, and cases the agent declined to route appear under "Not routed" rather than hidden |
| Accumulation demo rehearsed **and recorded as fallback** | **Partial** — built and replays with no API key or network; **not yet recorded.** Recording booked 09-09 |
| Full eval numbers in the README | **Done, past the commitment** — three readers compared, every rate with its denominator, losses published beside wins |
| **Two dry runs** | **Not done. Zero.** See below |
| Path-to-production plan | **Done** |

**Own the miss in one breath, then move:**

> Two dry runs committed, zero done. That is mine. The deployment work took the sprint and I chose a
> running system over a rehearsed one. Both dry runs are 09-08 and 09-09, and the demo gets recorded
> on 09-09 so a room with no wifi cannot break it.

**Then the line that is worth more than the table:**

> The biggest thing we built this sprint was never on that list. The brief promised a proof; what we
> have is **running on AWS** — and the deployed system agrees with our local pipeline to the last
> decimal place. "It works on my laptop" is not an answer to a feasibility question.

---

## 5. The ask (1 minute) — do not waste this

Pick one and be specific:

- **An introduction to a design partner who owns a contact centre** — the fastest route from this to
  a paid project.
- **A real anonymised conversation feed** for the Finals. Everything so far is synthetic, which is
  the competition rule; one real feed changes what we can claim.
- **~$10 of model spend** to close the one statistical gate we currently fail.

---

## Timings

| Section | Min |
|---|---|
| The five sentences + the money | 3 |
| The demo | 8 |
| Can we sell this | 3 |
| Committed vs done | 3 |
| The ask | 1 |
| **Total** | **18** |

**Cut to 12:** keep the money and the demo. Compress §3 to the Salient valuation and the confirmed
white space. **Never drop the dry-runs miss** — in a cut round, the team that volunteers its miss is
the one believed about everything else.

---

## Fallback ladder — assume the room is hostile

| if | then |
|---|---|
| no wifi | everything but the live-AWS view runs from a local file, no server and no key |
| AWS unreachable | the live view becomes the recording. **Record it 09-09 and have it on the laptop** |
| SSO token expired | it lasts hours, not days. Re-login that morning **and** before walking in |
| laptop dies | the reviewer screens are static routes; any browser runs them from the repo |

---

## Questions to expect

**"What's it worth to a bank?"** §1. Lead with the £650 tariff, offer the model, refuse to invent the
client's two inputs — and say why: the measured part is the good part.

**"Is this real or a prototype?"** Deployed on AWS, fed end to end, 903 tests, reproducible from a
clean clone with no API key. Boundary stated: synthetic data only, and one integration modelled
rather than a live bank feed.

**"What stops it acting on a customer by mistake?"** It has no mechanism to. No outbound contact
surface exists.

**"Why shortlist you?"** The idea is not commodity — detection in a single call is a crowded market;
keeping what *failed* detection and re-scoring it is the inversion. It is built, not designed. And we
publish what we got wrong, including a pre-registered result that died and a statistical gate we
currently fail — any judge can find both in the repo in five minutes.

**"What's the catch?"** One shared permissions role instead of per-function least privilege · alarms
go red in a console and page nobody, because this account has no notification path · write-once
evidence degraded to permissions · the reviewer screen is read-only, deliberately.

**If asked something unmeasured, say so and give the price of finding out.** Every open gap in this
project has a number attached. In front of a COO that habit is worth more than any single result.
