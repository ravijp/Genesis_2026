# Phase 3 — The Recommendation

## 1. The product idea

**Pre-delinquency for card collections, pitched as an input to an already-existing process, not as a new one.** Same engine, same demo, one re-pointed signal family, the same six-week back-test as the ask.

The product is a daily-ranked queue inserted into the existing collections dialer: customers who have not missed a payment but whose conversation history predicts they will. The collections team calls them in the same dialer, on the same contact-capacity budget, with a pre-populated casefile showing the customer's own words about hardship. The system never contacts anyone. It reorders a queue that already exists.

The buyer is the **Head of Collections Strategy or SVP of Credit Risk**. The budget line is **credit loss provision** or **collections opex** — not innovation or retention marketing. The pitch is cost avoidance on a known P&L line, not revenue protection through a model the bank already runs.

**This overrides my phase 1 pre-delinquency recommendation, the team's settled attrition pitch, and both of our framings.** Neither of us had the right combination.

What the team picked (attrition) is the safer story — better T3, simpler demo, less regulatory weight — but it is small: 0.6% of the book, $1.65M gross ceiling, unknown precision haircut. And the evidence for it is weakest where it matters most: the reader finds churn intent in 1 of 8 real card documents. The team acknowledges this and pitches the six-week test anyway. That is honest, but it means the attrition pitch is a bet on the 7 of 8 documents the reader missed, which is a strange bet to lead with.

What I picked in phase 1 (pre-delinquency) has larger absolute value and better evidence for the signal family: financial distress was the only family where the lexicon beat the model (33/72 vs 27/72), meaning the model is not even needed for the main signal — it can be hardcoded. But I missed the T3 problem: hardship programmes are opt-in, so you cannot enrol a silent customer. Pre-delinquency as a *retention* pitch fails for exactly that reason.

**The correction is to sell pre-delinquency as a *collections* input, not a *retention* one.** The collections team calls people who are delinquent. We change *who they call first* and *what they say when they connect* — within a budget of calls they are already making, to customers who are already past due. The system does not need to reach a current customer. It reaches a 10-day-past-due customer who, according to the conversation history, is more likely to charge off than the next 10-day-past-due customer. The outbound contact is the collections call they were going to get anyway; we just move it up and brief it differently.

This repairs the T3 problem: no opt-in, no silent customer, no new contact motion. The collections team works its normal queue; the system just reorders it and briefs the agent. The regulator permits 7 attempts per debt per 7 days; better ordering has value *independent of precision*.

**What happens to the work already done:** most of it carries. The reader comparison (model vs lexicon) is load-bearing for any story. The accumulation and retro-scoring mechanism is the same. The deployed pipeline, test suite, and evaluation harness are domain-independent. What changes: the demo corpus has to be re-authored from an attrition arc to a collections arc (job loss → missed payment → hardship offer vs standard dunning). The signal family focus narrows to financial distress / life event, which were already the best-measured families. The value model switches from avoided-acquisition to avoided-charge-off.

Cost to re-point: roughly a day of fragment authoring and $0.45 of model spend. The demo needs a new ending (the collections call at day 10 vs the retention call at day 74). Everything else — the identity of the system, the demo structure, the six-week back-test ask — stays.

---

## 2. How the value becomes obvious

**Do not walk them through the assumptions. Show them the published arithmetic and then put the question back on them.**

> "The US card industry charged off **3.82% of balances** in Q2 2026 — roughly **$48 billion**. The 90-day delinquency rate is **12.92%**. The question is not whether the problem is big enough. It is whether conversations predict it sooner than the data you already watch.

> "What we know: the CFPB estimates **0.7-1.0% of all card accounts close every month**. Most of those closures are preceded by a conversation — a complaint, a hardship disclosure, a question about payoff. The conversations exist, they are transcribed, and they are thrown away.

> "What we do not know — and what I will not pretend to know — is **how many of the people who tell you they lost their job actually miss their next payment**. That is a fact about your book, not about our model. It is exactly the fact the six-week back-test settles."

Then show the CFPB CORCCACBS charge-off rate on the screen. Not a chain of haircuts. A public series your buyer already reports. Then:

> "If you lose **$3,400 per charge-off** — and we can argue the number, but it is between $2,300 and $5,000 — then every hundred customers your existing process catches as charge-offs, if we catch **ten more** before they happen, the project pays for itself across the card portfolio in under a quarter. If we do not, you walk away having spent six weeks and a fixed fee that is cheaper than the legal review for a vendor contract."

**The value is not in a number I invent. It is in the ratio: charge-off cost vs experiment cost.** The charge-off cost is published and large. The experiment cost is small and capped. No number I put on the screen can be as persuasive as that ratio, because the ratio is true regardless of my assumptions.

**The one number to put on the screen: "six weeks, fixed fee, explicit walk-away."** That is the only dollar amount that needs to survive the room.

---

## 3. What to demonstrate, and how

Seven minutes. Same spine as the team's demo (one customer, three conversations, accumulation across time, the retro column), but re-pointed to collections.

### The story

Customer: Marcus Webb, 41, Platinum card, $18,000 limit, $9,400 balance. Current. Never missed a payment in six years.

**Beat 1 (0:00-1:30) — The collections queue, before the system**

Screen: a standard collections queue. 30-day past-due names, 60-day past-due names. Marcus is not on it — he is current.

> "This is the queue your collections team works every morning. Two things to notice: it is backward-looking — these customers are already past due. And it is silent about what any of them said."

**Beat 2 (1:30-3:30) — The conversations the bank already threw away**

> "Marcus talked to your bank three times in the last 90 days. Here is what happened."

- **Conversation 1 (Day 0, phone):** Marcus calls to ask about a late fee. "I've been out of work for six weeks. I'm burning through savings. Is there anything you can do?" The agent waives the fee. The system records a financial distress signal with the verbatim quote. Score: 3.2. No case opens — below threshold.
- **Conversation 2 (Day 35, chat):** Marcus asks about balance transfer options. "I'm trying to lower my monthly payment until I find a new job." The system records a second financial distress signal. Score crosses threshold. **A case opens.** The day-0 remark now contributes 5.1 instead of 3.2.
- **Conversation 3 (Day 72, phone):** Marcus misses his payment. The collections team calls.

**Beat 3 (3:30-5:00) — The moment**

> "Day 72. Marcus is 10 days past due. He is on the collections queue — but he is buried behind 60-day names. The first agent to call him reads a script: 'Your payment is 10 days late. Can you pay the minimum today?'

> "Now look at what the system gives that agent."

Screen switches to the casefile the agent sees: Marcus Webb, conversation history, verbatim quotes from both calls about job loss, the cumulative score, the retro column showing the day-0 quote's re-evaluation. A highlighted button: "Hardship program eligible — 6 months reduced rate, fee waiver."

> "That information exists in your system today. No agent sees it, because no system remembers it across conversations."

**Beat 4 (5:00-6:30) — The alternative**

Split screen. Left side: Marcus without the system. Standard dunning. 30 days past due. 60 days past due. 90 days past due. Charge-off. "On your current path, that is a $3,400 loss and a customer who will never bank with you again."

Right side: Marcus with the system. The collections call at day 10. Agent offers hardship programme. Marcus accepts. "He stays current. No charge-off. No credit damage. You keep the relationship."

> "The system does not contact Marcus. The collections team was calling him anyway. We changed *when* and *what*."

**Beat 5 (6:30-7:00) — The ask**

> "The demo uses one customer on synthetic data. The six-week back-test uses 12 months of your actual call recordings and your actual payment outcomes. A pre-registered success criterion: top-decile uplift on pre-delinquency capture. If the criterion is not met, we say so and walk away."

**What needs to be built:** The demo corpus needs to be re-authored from the attrition arc to the collections arc. That is about a day of work. The casefile screen showing hardship-eligibility flag needs to exist in the demo UI — it does not currently. That is two days of front-end work. Everything else — the three-conversation structure, the retro-scoring column, the split-screen counterfactual — already exists in the team's demo and just needs re-scripting.

**What the demo must not do:** Use the phrase "we predict who will miss a payment." Say "we surface the conversations that predict it." The system does not predict; the model reads. The people in the room are finance and will distinguish.

---

## 4. What to keep

Load-bearing and must survive any reframing:

- **The reader comparison harness and the model-vs-lexicon table.** This is the strongest evidence in the repo that the system does something a regex cannot. "A rule engine finds one of the sixty-five conversations where a customer is escalating a complaint. The model finds sixty." That sentence is worth keeping through any reframe.
- **The accumulation and retro-scoring mechanism.** It is the only thing in the build a competitor cannot reproduce in a quarter. Twilio's Conversation Memory reconciles to current truth; this system does not. That is the product differentiator.
- **The no-outbound-surface design.** It is the governance story. It is baked into the system. It must be described as "not switched off — absent."
- **The append-only ledger with point-in-time query.** The four-number per-entry design (contribution_at_write, score_at_write, contribution_now, score_now) is the implementation of retro-scoring. It is what the demo shows. It must stay.
- **The deterministic core.** Contrary to the team's instinct to hide it, the fact that accumulation, decay, and thresholds are unit-tested Python is the answer to "what happens when the model changes" and "is this a black box." Keep it visible.
- **The six-week back-test framing.** It is the only credible ask given the evidence gaps. Do not change it.
- **The honesty beat placement** — after the demo, before the money. Keep that sequence.
- **The reader coverage table** (0/20 → 20/20 for complaints, 0/20 → 19/20 for vulnerability, 1/20 → 16/20 for retention, 9/20 → 10/20 for collections). This shows the mechanism works across desks. Label it as generic-corpus evidence.

Sunk cost worth dropping:

- **Any pre-registered comparison on the offline reader alone.** If the team has run experiments that only use the offline lexicon, those results cannot support a product claim. Publish them in an appendix; cut them from the pitch.
- **The 30-0-0 diffuse-arc headline.** It is a corpus effect, not a mechanism effect. It supports the accumulation design but cannot bear the weight the team puts on it. Replace it with "we have measured that the retro-scoring mechanism changes 239 of 485 entries" — observational, not comparative.
- **The CFPB complaint benchmark churn-intent 1/8.** It is real evidence and the team is right to publish it, but it argues *against* the attrition pitch. In the collections reframe, it becomes a curiosity rather than a threat — the signal family for pre-delinquency is financial distress, not churn intent, and financial distress was not measured on the CFPB card subset. So the 1/8 becomes "the family we do not need for this story."
- **The model migration protocol document.** It is thorough and correct, but it belongs in technical Q&A, not the pitch. The pitch gets one sentence: "We have already swapped the model once and measured the delta for under three cents."
- **The competitive landscape survey beyond Twilio.** Verint, NICE, CallMiner, Observe.AI — none of them does accumulation. Name the one competitor that does (Twilio) and move on.

---

## 5. The three questions that decide it

### Question 1: "You are asking me to call a good customer who has only missed one payment and offer them a hardship programme. What if they were never going to default?"

> "That call was going to happen anyway. Your collections team calls 10-day-past-due customers. The only change is *when* in the queue they appear and *what* the agent says. A false positive here costs about $430 of foregone interest — the difference between full APR and the hardship rate for six months. A charge-off avoided saves about $3,400. You can be wrong eight times for every right answer and still break even.

> "But the real answer is: the pilot does not use a hardship offer. It reorders the dialer queue and briefs the agent. The agent decides what to say. The system only surfaces information that already exists in the transcripts. It never contacts anyone, and it never makes a decision."

### Question 2: "Why can't we build this ourselves? We already transcribe calls."

> "You can, and you should consider it. Two things that would be harder than they look:

> "First: most of the value is not in the model that reads a single conversation. It is in the ledger that keeps the weak signal across conversations and re-values it when new evidence arrives. That is unit-tested Python, not a model. It is the kind of thing that looks like a few hundred lines and takes a team several months of iteration to get right — because the threshold tuning, the decay functions, the cross-channel corroboration, and the point-in-time query are all things that have to be correct in production, not in a notebook.

> "Second: a six-week fixed-fee back-test is cheaper than the internal team stand-up to run the same experiment. If the experiment fails, you are out a fixed fee. If it succeeds, you can build your own version and we will compete on the next procurement. Either way, the test is the fastest way to know."

### Question 3: "What does 'yes' look like today?"

> "A six-week retrospective back-test: your call recordings from the last 12 months, your payment outcome data, a pre-registered success criterion — top-decile uplift on pre-delinquency capture against your current production model — and an explicit walk-away if it fails. No production integration. No customer contact. Fixed fee, not variable.

> "If the test passes, the deployment is a ranked queue on one collections desk — no new headcount, no new process, no data leaving your environment. The model runs on Bedrock in your account. We deploy inside your perimeter."

---

## 6. What would make this undeniable, and what it costs

The single measurement that converts this from interesting to fundable:

**A card-specific reader coverage result on financial distress signals from real call recordings, labelled against observed payment outcomes, with precision and recall reported together.**

Cost: ~$0.45 in model spend, roughly two days of fragment authoring, and access to a labelled sample of bank call recordings. The team already has the evaluation harness and the signal definitions. The new work is finding a partner bank willing to provide ~500 labelled call recordings (10-20 hours of audio transcribed) where the label is "customer missed a payment within 60 days of this call" and the corpus includes both customers who said something about financial distress and customers who did not.

**If I could produce one number before walking into the room, it is this:**

| | Book average | Signalled by system |
|---|---|---|
| Pre-delinquency capture (miss within 60 days of call) | X% | **2-3x X%** |
| Non-signalled rate (flagged but stayed current) | — | **< Y%** |

Where X is the bank's known charge-off rate for the segment, and Y is the acceptable false-positive threshold given the 8:1 value ratio.

Without this number, the pitch is an argument about possibility. With it, the pitch is an argument about magnitude.

**What it costs:** $0.45 of inference, two days of the team's time, and a bank willing to share a labelled sample. The team's own budget remaining is ~$9.55 of $12. The constraint is not money — it is access to real labelled data.

**If I cannot get real data before the gate, the next-best thing is a synthetic corpus designed to test the pre-delinquency claim directly.** The current synthetic corpus tests signal extraction — does the model find the planted signal? A pre-delinquency corpus would test *outcome correlation* — for synthetic customers with planted financial distress signals and planted payment outcomes (some who miss, some who do not), does the system rank the missers above the payers? This is an overnight run costing essentially nothing, and it produces a rank-stability number the team does not currently have.

**I would spend the remaining ~$9.55 on exactly this before the gate. It is the highest-leverage build item available, and it produces the evidence the pitch is missing.**

---

## Summary of where I stand against my own earlier reasoning

| Phase 1 claim | Current position |
|---|---|
| Lead with pre-delinquency | **Hold** — same direction, fixed the T3 mistake |
| 7-10x value multiple | **Corrected** — 3-9x, centrally ~5x, with precision haircut |
| Hardship programmes are already staffed | **Corrected** — opt-in, so cannot enrol silent customers. Fix: sell to collections, not retention |
| The demo should show retention lift | **Changed** — demo shows charge-off avoidance, which is a concrete P&L line |
| The money story is a chain of haircuts | **Changed** — money story is the ratio of charge-off cost to experiment cost |

| Phase 2 assessment | Current position |
|---|---|
| The team's attrition pitch is safe but small | **Confirmed** — 0.6% of book, unknown precision, 1/8 churn intent on card data |
| The latency claim contradicts the consumption path | **Confirmed** — and the team's patch is insufficient |
| The 30-0-0 result is over-interpreted | **Confirmed** — corpus effect, not mechanism |
| The deterministic differentiator is hidden | **Confirmed** — should be visible in the pitch |
| The data privacy gap is unexamined | **Confirmed** — and it is a first-class requirement |
| The buyer is wrong | **Confirmed** — Right buyer is Head of Collections Strategy, not Retention Analytics |

---

## Final word

The product is the accumulation mechanism. The demo is the retro-scoring column. The pitch is the six-week back-test. The evidence gap is a labelled card sample. The risk is that none of the synthetic numbers transfer to real data. The hedge is that the experiment is cheap and the walk-away is explicit.

**Stay at the collections edge. It has the best anchors, the cleanest T3, and the most honest evidence story — "we do not know what conversations predict, but here is exactly how to find out."**