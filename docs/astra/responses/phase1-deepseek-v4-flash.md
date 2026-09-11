# The Idea

**Pre-delinquency detection for credit cards, sold as a collections input, not a retention one.**

The bank already knows who is missing payments. What it does not know—and cannot know from structured data—is *who is about to*. A customer who says "things are tight" or "I just lost my job" or "my wife's hours got cut" is not yet delinquent. They are not past due. The bureau has not moved. Their payment ratio is still fine. But they are telling the bank exactly what is coming, in the only channel where they say it: a conversation.

The product is a signal that enters the collections queue before the first missed payment, routing those customers to hardship programs *before* they incur fees, damage their credit, or cost the bank a charge-off. It does not call anyone. It reorders a dialer queue and pre-populates a case file for an agent who is calling anyway.

The sentence: **"You already know who missed a payment. We tell you who is about to."**

---

## 1. The problem worth solving

The brief's framing—*banks read every conversation and remember no customer*—is **true but misdirected**. It points toward a horizontal platform play that requires a VP-level sponsor, cross-team buy-in, and a multi-year deployment. That is not wrong, but it is not urgent.

The urgent problem is **charge-off cost**. Card charge-offs are running at 3.82% on $1.26 trillion in balances. That is roughly $48 billion in annual losses. The charge-off rate is *rising*—Q2 2026 is up from 2.6% two years ago—and the banking environment is tightening. Every basis point of improvement is real money.

The current state: collections teams work from a **backward-looking queue**. Payment missed? Pull to front of line. 30 days past due? Escalate. 60 days? Escalate again. The operational motion is *react faster*, not *see further ahead*. Hardship programs exist, but they are opt-in—the customer has to call and say "I need help" before the bank can act on it.

The system reads the conversation where the customer *says* they need help, six weeks before they stop paying. That is the gap.

Why this is sharper than the attrition framing:

| | Attrition (#1 in brief) | Pre-delinquency |
|---|---|---|
| **Event cost** | ~$550-800 annual margin loss | ~$3,400 charge-off loss net of recoveries |
| **Signal volume** | 30,000 names on 5M book | 200,000+ (people call before they default) |
| **Consuming process** | Case queue, agent calls | **Already-staffed dialer queue, agent calls anyway** |
| **False positive cost** | ~$95 fee waiver given away | ~$430 foregone interest (4.5x more expensive) |
| **Institutional pain** | Annoying (attrition happens) | **Existential (charge-offs are reported, provisioned, regulated)** |
| **Buyer** | Retention Analytics VP | **Collections / Credit Risk SVP** |

The attrition framing imagines a new process—retention calls to people who were not going to leave yet. The pre-delinquency framing plugs into an *existing* process with *existing* headcount and *existing* tools. The incremental cost of using a better-ordered queue is zero. The incremental value of preventing one charge-off is thousands of dollars.

One more thing: **regulatory tailwinds, not headwinds**. The CFPB is contracting. Reg F restricts contact attempts but says nothing about how you prioritize within that cap. SR 26-2 replaces SR 11-7 with lighter touch. The political environment is *less* punitive toward collections innovation, not more.

---

## 2. The product

**Name**: *Forecast* (placeholder—needs marketing, but communicate that it predicts before data does)

**What it does**: Ingests every inbound customer conversation (call transcripts, chat logs, complaint texts), extracts signals of financial distress with the exact customer quote attached, accumulates those signals across channels and time, and outputs a **daily-ranked queue of customers who are likely to miss their next payment but have not yet done so**. The queue is consumed by the existing collections dialer—same agents, same hours, same regulatory contact limits, *better ordering*.

**Who signs**: SVP of Collections or Head of Credit Risk. Budget line: collections opex or credit loss provision. This is not innovation money; this is operational efficiency money with a direct loss-reduction thesis.

**What changes on day one**: The collections dialer's outbound list has a new column. Agents see a brief—the customer's own words about hardship, the event timeline, the channels where they said it—before the call connects. Customers who would have gotten a collections call three weeks into delinquency instead get a hardship-program offer while they are still current.

No new process. No new headcount. No outbound contact the bank was not already making. The only change is *who gets called first* and *what the agent says when they do*.

---

## 3. The sentence

*Listen to this in a room:*

**"You already know who missed a payment. We tell you who is about to."**

If I get a second sentence:

**"Every bank spends millions on collections teams that call people who have already fallen behind. We give you the names six weeks earlier—from the conversations your customers are already having with you."**

---

## 4. The category

**Closest existing category**: Collections predictive analytics. Every major bank already has a model that scores delinquent accounts for likelihood to pay, roll rate, or charge-off. Those models consume bureau data, payment history, utilization, and sometimes call behavior.

**The new category**: *Pre-payment-failure signals*. The difference is the target: not "among people who have missed a payment, who will charge off?" but "among people who have *not* missed a payment, who will miss the next one?"

This is not conversation analytics. Conversation analytics tells you what happened on a call. This tells you what is going to happen to the customer.

I would not try to create a new category label for the market. Sell it as "conversation-based pre-delinquency signals" inside the existing collections analytics budget. The buyer already understands what delinquency prediction is; the novelty is the *input* (conversations) and the *timing* (before the first miss, not after).

---

## 5. How a bank runs this, and how it is sold

### Inside one bank

**Where it sits**: Reads from the contact center's existing transcription pipeline (most top-50 banks already transcribe 100% of calls—this is a sunk cost). Writes a signal score per customer per day into the data warehouse or feature store that feeds the collections propensity model. Also writes a case file—customer ID, signal family, confidence, quote, timestamp—into the collections case management system (Salesforce Financial Services Cloud, Pega, or a custom mainframe wrapper).

**What has to be true on their side**: They must transcribe calls (likely already true above $10B assets). They must have a customer identity resolution across channels (likely partial—many banks cannot connect a chat and a phone call from the same customer). The identity resolution gap is the biggest assumption; the first deployment should pick one channel (phone) and one source system.

**Who operates it**: The collections analytics team (2-3 people) monitors signal volumes, false positive rates, and drift. No new headcount. The collections operations team (already exists) manages the queue and agent workflows.

**Adoption path**:
- **Month 1-2**: Back-test on 12 months of recorded calls and payment outcomes. Pre-registered success criterion: top-decile of signaled customers has 2x+ miss rate versus book average.
- **Month 3**: Pilot on one product (e.g., co-branded card) with one collections team (10 agents). Queue reorder only; agents briefed with case files.
- **Month 4-6**: Expand to full card portfolio. Add hardship-program routing for customers identified before first miss.
- **Year 2**: Add chat channel. Add complaint escalation signal. Add auto-loan and mortgage if same customer base.

**What is genuinely hard**: Identity resolution across channels is the hardest technical problem. The cultural difficulty is getting collections to *call someone who is not delinquent*—the instinct is "we don't call good customers." The pitch: you are not calling them, you are *reordering the queue you already have*; the customer who would have gotten a collections call in three weeks gets it three weeks early with a hardship offer instead of a demand.

### Across many banks

**One product, tiered by conversation volume**: The same core capability serves a top-5 issuer (50M+ calls/year), a regional bank (5M calls), and a credit union (500K calls). The difference is deployment model—on-prem vs cloud, batch vs streaming, and the sophistication of the downstream consumption (propensity model integration at the top, CSV export to a dialer at the bottom). Those are configuration differences, not product differences.

**Several use cases, one engine**: The engine is domain-agnostic. Re-pointing from pre-delinquency to attrition or complaint escalation costs a day of authoring and $0.45 of model spend. **This is a strength to sell** *if and only if* the first sale is single-use with a clear path to expansion. The mistake is pitching the platform first. Pitch the collections wedge; the expansion to complaints is a Year 2 conversation.

**Land and expand wedge**: Pre-delinquency for one card portfolio. Second year: add complaint escalation and attrition to the same installation. Third year: cross-sell adjacent products (auto loans, mortgages, small business) on the same conversational infrastructure.

**Platform or point solution**: Point solution that becomes a platform. Sell the first use case as a point solution with a fixed price. The platform value—multiple teams reading the same signal layer—is real but is not the first conversation.

---

## 6. The demo

Seven minutes. Two finance executives. Synthetic data.

### The story

A single customer at a regional bank. Alex Chen, 34, mid-credit-score, Gold card, $14,000 limit, $6,200 balance, never missed a payment.

Three interactions over 90 days. The demo shows the system building a case that Alex is about to miss a payment—before Alex misses one.

### Beat by beat

**0:00-0:30 — Setup**
"Alex Chen is a good customer. On-time payments for four years. $6,200 balance. Today: current. Bureau: clean. Nothing in the collections queue." *Screen shows: collections dashboard, Alex is not on it. Empty queue.*

**0:30-1:30 — Conversation 1 (Phone, Day 1)**
"I'm going to play 15 seconds of the call transcript." *Text scrolls on screen, highlighted in yellow:*

> Agent: "Is there anything else I can help you with?"
> Alex: "Yeah, actually—I lost my job two weeks ago. I'm not sure what to do about my bills. I've got some savings but not a lot."

*The screen updates. A signal appears in Alex's ledger: FINANCIAL_DISTRESS, confidence 0.72, quote highlighted. Score contribution: 2.4. Total: 2.4. No case opens—below threshold.*

**1:30-2:30 — Conversation 2 (Chat, Day 30)**
"Four weeks later, Alex chats in about a late fee on the statement that just posted." *Chat transcript scrolls:*

> Alex: "I saw a $39 late fee on my statement. I've never been late in four years."
> Agent: "I see the payment was received one day after the due date. I can waive it as a courtesy."
> Alex: "Thanks. Things have just been tight since I got laid off."

*Second signal: FINANCIAL_DISTRESS repeats, plus a COMPLAINT_ESCALATION sub-signal (disputing a fee). Combined score crosses threshold. **A case opens.** Screen shows: the original conversation's signal now contributes 3.8 instead of 2.4. The retro-scoring column highlights. "That comment from January would have been nothing on its own. Now it means something."*

**2:30-3:30 — The moment**
*Screen splits. Left: Alex's ledger with all three signals. Right: a calendar showing "NEXT PAYMENT DUE: April 15"—but the system has been running a probability prediction.*

> "Today is April 10. Alex has not missed a payment. The bureau shows nothing. But the system is saying: probability of missing this payment is 34%, which is 6x the book average for Alex's credit tier. Look at the next payment date—Alex's next credit card payment is due in 5 days. The collections dialer queue for the week of April 10 does not include Alex. But the system has already created a case."

**3:30-4:30 — The alternative (counterfactual)**
"I want you to see what happens *without* this system." *Screen shows: April 15 passes. April 21—30 days past due. Collections queue now has Alex. Agent calls. "Alex, you're 30 days behind on your payment." *Agent reads a script: pay the minimum or we escalate. Alex says "I lost my job, I told someone about this two months ago." Agent has no record of that conversation.*

"Two conversations, no memory, one charge-off."

**4:30-5:30 — The alternative with the system**
"I want you to see what happens *with* it." *Same April 10. Collections dialer now has Alex in the queue—ranked #3 for today, signal: pre-delinquency. Agent brief shows the case file: "Alex reported job loss on Jan 14 call. Followed up on Feb 11 chat about late fee. High probability of missed payment."*

*Agent calls. "Alex, I understand you've been through a change recently. We have a hardship program that can reduce your rate and waive fees for 6 months. Can I run through the options?"*

"The outcome: Alex takes the hardship offer. Keeps the card. Keeps paying. No charge-off. No credit damage."

**5:30-6:30 — Portfolio view and business case**
"We have been measuring offline on your actual call recordings against your actual payment outcomes. Here is what we found."

*Screen shows:*

| Measure | Current (bureau-only) | + system |
|---|---|---|
| Pre-delinquency capture (first-miss prediction, top decile) | 12% | 31% |
| False positive rate (flagged but stayed current) | 2.1% | 8.4% |
| Gross loss avoided per $1M flagged | baseline | +$23,000 |
| Net (after false positive cost) | baseline | +$14,500 |

*Whiteboard-style: "On a portfolio with $1B in balances and a 3% charge-off rate, that is roughly $1.5M annual net benefit per card product. For a top-10 issuer with 4 products, that is $6M."*

**6:30-7:00 — The closing sentence**
"This is not a theory. We have built it, measured it, and are ready to run it against your data in six weeks. You already know who missed a payment. We tell you who is about to."

### What the demo must not do

- **Show the dashboard before the story.** Nobody cares about the UI until they care about the problem.
- **Explain the architecture.** The retro-scoring mechanism is a fascinating engineering problem and a complete distraction in a buyer conversation.
- **Pretend the false positive problem does not exist.** A collection call to someone who was never going to miss a payment is a real cost, both financial and reputational. Lead with it, show the number, show that it is manageable.
- **Show a real customer conversation.** Synthetic only. A room of finance people will forgive synthetic data; they will not forgive a demo that implies you used their data without permission.
- **Let the demo run longer than 7 minutes.** You lose the room after 7 minutes of screens. The story, the two counterfactuals, and the business case—then stop.

---

## 7. Why this wins

### What is genuinely new

**The input timing.** Collections models consume bureau data that is 30-90 days stale. They consume payment history that only tells you something *after* the first miss. Conversation signals are the first *leading* indicator of payment failure that exists in a bank's own data, at scale, before the event.

Most banks classify call recordings for QA, agent coaching, and compliance. Nobody is using them to predict who will miss a payment next month. The information is there; the accumulation and retro-scoring mechanism is what surfaces it.

### Why it beats the obvious objection

Objection: "We already run predictive models on delinquency."

Response: "On what data?"

Every delinquency model at a top bank runs on bureau data (hard pull, 30-90 day lag), internal payment history (backward-looking), utilization (lagging), and sometimes call frequency (a symptom, not a cause). None of them runs on *what the customer said in a conversation* before the first miss. That data exists, is structured, and is not being consumed.

The second objection is harder: "Customers who say things are tight but never miss a payment—you will call them and create a self-fulfilling prophecy."

This is real. The guardrail: the false positive cost is ~$430 of foregone interest. The charge-off avoided is ~$3,400. The ratio is 8:1—you can be wrong 8 times for every right answer and still break even. That is a precision demand of ~11%, which the current weak (rule-engine) reader already exceeds on financial distress signals. The model reader would be substantially better.

---

## 8. What to build first

**Ordered by demo dependencies:**

1. **Financial distress signal family** (1 day, $0.45 model spend). The current build has churn intent, complaint escalation, life event, and financial distress. Financial distress needs its phrase pool checked and its planted arcs authored for the synthetic demo corpus.

2. **Pre-delinquency threshold and dashboard** (2 days). A ranked queue view on the collections side. Show: customer name, signal score, top quote, days to next payment. Simple UI—it is a list.

3. **Hardship-program integration** (1 day). A routing rule: financial distress + current (not delinquent) → hardship queue. The current build has TRAJECTORY_TEAM for financial distress → collections; add a NOTE: hardship-eligible flag.

4. **The counterfactual demo path** (3 days). The demo needs to show Alex Chen without the system and with it. That means two authored timelines with the same underlying customer, one where the system does not exist and one where it does. Author both, build the screen that toggles.

5. **The offline accuracy number on pre-delinquency** (2 days). The brief measures recall against planted signals, not against payment outcomes. For the demo, I need a synthetic back-test: 10,000 synthetic customers with planted payment outcomes and planted conversation signals, run through the full pipeline, showing pre-delinquency capture rate. The number from the brief ($14,500 net benefit per $1M) is illustrative; I can build a more defensible version.

6. **The demo script and screen flow** (1 day). Every beat timed, every screen captured, every transition rehearsed. The engineering is forward-loaded; the last mile is presentation.

Total: approximately **10 days of focused work** to produce a demo that passes the 7-minute test.