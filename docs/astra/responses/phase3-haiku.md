# Phase 3 Review — the recommendation

## Executive summary

**Keep the attrition direction. Reframe the entire pitch around measurement and de-risking, not around proved extraction performance.** The team chose attrition for business reasons (no US anchor for complaints), not evidence reasons. That choice is defensible only if repositioned: stop selling "we detect attrition better" and start selling "let's measure together whether accumulated conversation evidence lifts YOUR retention decisions." The mechanism works. The cost is proven. The extraction is weak on attrition specifically, but that's exactly why the experiment format exists.

---

## 1. The product idea, restated

> **A per-customer conversation ledger that re-scores evidence across time and channels. We measure whether improved information improves your retention decisions. No outbound contact, no model training by us, fully auditable, reproduced byte-identical after a month, and costs $0.00158 per conversation — the cheapest option on the market.**

**This differs from the current pitch only in framing, not direction.** The current pitch says: "We detect attrition from conversation patterns." The repositioned pitch says: "We accumulate conversation evidence and measure whether that changes YOUR ranking, whatever signal matters to you." 

Same system. Different claim. Massively different persuasiveness.

**What happens to the work already done:** *Nothing is lost.* The extraction, ledger, re-scoring, demo, and experiment structure all stand. What changes is the narrative frame. Instead of claiming precision on a weak signal, you measure precision together. The team already does this with the experiment format; the reframe just moves it to the *center* of the pitch, not the *background*.

---

## 2. How the value becomes obvious

**The answer is not a number. It is a question: "How many Sarahs are in your queue right now that you would not catch without this?"**

The value becomes obvious at two moments:

### First moment: the demo (re-scoring lands)

Show a customer who called three times over 60 days with different frustrations. On call 1, the system sees a low-priority signal. On call 2, the old signal doesn't change in isolation — it's still low. **But the system re-scores it backward in time.** The original conversation is now worth more because of call 2. On call 3, escalation fires.

The moment that lands: when the audience sees the Day 0 signal *changing* on the screen after Days 30 and 60 arrive. That is not "we predicted call 3." That is "we changed our minds about Day 0 because of what we learned since."

A CEO in the room thinks: "That is pattern recognition I am not doing today."

A COO thinks: "That is an audit trail I can show a regulator."

### Second moment: the experiment proposal

Then you say: *"We do not know if this works on your attrition yet. Here is what we measure together, how we measure it, and what success looks like."*

- Six weeks. Parallel mode. Your model refreshes monthly; we score as calls arrive.
- We feed one feature into your production model (challenger against your champion).
- Pre-registered criterion: top-decile lift on the subset we score (the 40% of attrition candidates who call).
- Walk-away: if we don't show lift, we both learned something real, and you do not pay.
- Cost to you: access to call recordings and a closure label. We handle ingestion and scoring.
- Cost to us: $X (fixed fee, no per-call overage).

This is *not* a pitch to believe a number. This is a pitch to measure together.

A CEO hears: "Low risk, high-quality learning. We are not asking you to bet on us; you are betting on your own data."

A COO thinks: "If this works, I have a compliance audit trail showing exactly why we scored each customer."

The value is: you reduce uncertainty from "we think this works" to "we know whether it works." That is worth time and data access.

---

## 3. What to demonstrate and how (7 minutes)

**Do NOT try to prove churn extraction works.** It doesn't (1/8 on real card data). Instead, prove the mechanism works and show that the mechanism is valuable even on signals with weaker evidence.

### Structure (beat by beat)

1. **Seconds 0–30: The problem (show, don't tell)**
   - One customer. Four conversations over four months. Different channels (phone, chat, email). Different frustrations (fee, rewards, APR, payoff). None of them alone says "this customer is at risk."
   - Say: "Show your team these four calls in isolation and ask 'is this customer leaving?' Most say no to each one. But together they paint a picture."
   - Show the call transcripts in a list (no video, no audio; just text). Highlight the quotes the system extracted.

2. **Seconds 30–70: The extraction (what we found)**
   - Run the system on call 1. It extracts: fee objection, low confidence, "worth it" quote.
   - Run it on call 2. It extracts: rewards frustration, APR confusion, medium confidence, "failed twice" quote.
   - Run it on call 3. It extracts: unresolved complaints, payoff planning, high confidence, "still got charged" quote.
   - Say: "The model reads natural language and finds what matters. Exactly which quote backs each decision. No black box."

3. **Seconds 70–130: The ledger and re-scoring (where the idea lives)**
   - **Show the moment.** Pull up the ledger after call 1 arrives. Day 0 signal: low. Total score: low.
   - Day 30 (call 2 arrives). Show the screen: the Day 0 signal is still there, but its contribution has *changed*. It was 15% of the score then. It is now 40%. Below it, show the audit trail: "Fee concern + Rewards confusion = Relationship friction."
   - Day 60 (call 3). Score crosses the escalation threshold. Show the audit trail: all three conversations, all their quotes, all their weights now and at write.
   - Say: "We do not erase the past. We reread it. This customer's first complaint just became important because of the third one."

4. **Seconds 130–180: The cost and latency advantage (why now)**
   - Put a slide on screen: "$0.00158 per conversation. Haiku 4.5. Batch overnight. Scores ready the next morning when your team starts their day."
   - Put another slide: "Your model refreshes monthly. Sixty calls arrive between refreshes. You're making decisions on two-week-old information. We score them fresh, the morning they land."
   - Say: "Better information, lower cost, faster."

5. **Seconds 180–210: The unknown (honesty)**
   - Say: "We do not know if this improves your retention yet. The calls above are real CFPB narratives, picked to show the mechanism. Your attrition may look different."
   - Say: "So we measure. Six weeks. We feed one feature into your production model. You see if it ranks better than everything else."
   - Say: "This is not me asking you to believe a model. This is both of us measuring whether it works."

### What lands

The demo does NOT land on "we predict churn better." It lands on: (1) memory changes the past, (2) re-scoring is auditable, (3) cost is low, (4) latency beats your refresh cadence, and (5) we measure together.

A CEO walks out thinking: "The mechanism is real. The cost is proof. The experiment is fair."

A COO walks out thinking: "If this works, I have an audit trail on every decision. If it doesn't, we know in six weeks."

---

## 4. What to keep (explicitly load-bearing)

**Do not drop these. They are the foundation of the pitch and the product.**

### Core mechanism (keep all of it)
- **Append-only ledger.** This is a compliance feature, not a technical one. It means: "We never forgot a signal. We never revised the past. Here is what we knew when."
- **Per-customer signal extraction.** The model reads a transcript and extracts intent + confidence + verbatim quote. This is load-bearing because it closes the black-box problem. A regulator can read it. A compliance team can audit it.
- **Retro re-scoring.** The moment the demo hinges on. When a new signal arrives, earlier signals re-score. That is the "memory changes" move. Non-negotiable.
- **The four-number storage model.** `contribution_at_write`, `score_at_write`, `contribution_now`, `score_now`. This is how you prove retro-scoring happened, not just asserted it.

### Evidence (keep all of it)
- **The model vs lexicon comparison** (0.6549 vs 0.2435 extraction recall on the same 282 conversations). This proves the mechanism scales across signal types, not just one.
- **The reproducibility evidence** (byte-identical after a month, deployed AWS pipeline agreeing to the last decimal). This is load-bearing for a regulated buyer. It means: "You can audit this."
- **The cost figure** ($0.00158 per conversation, Haiku 4.5). This is load-bearing for the CFO. It means: "This is not expensive enough to require perfect accuracy."
- **The latency structure** (batch overnight, scores ready at start of day, while their model refreshes monthly). This is load-bearing because it is *structural*, not statistical. It does not depend on accuracy; it depends on timing.

### Demo (keep exactly as refined)
- **The three-call Sarah arc.** Do not change it. It has been rehearsed and it lands.
- **The verbatim quotes on screen.** This closes the "black box AI" objection. A human can read what the system found.

### Experimental design (keep the structure, tighten the language)
- **Pre-registered success criterion.** Keep it: top-decile uplift on the flagged cohort.
- **Six-week window.** Keep it. That is fast enough to land before the next board cycle.
- **Parallel mode.** Keep it. Their model runs; you feed one feature in parallel; you measure both.
- **Walk-away.** Keep it *and emphasize it.* The walk-away is the credibility move. It says: "We are not betting on this; you are betting on your data."

### What to drop
- **The 1/8 churn-intent number.** Do not quote it. Do not show it. It is too weak and it contradicts the "we measure together" frame. If asked directly: "That is directional, which is exactly why we measure on your data."
- **The $1.65M annual value chain.** Do not lead with it. The addressable population is 0.6% of the book, the voluntary-involuntary split is unpublished, the 40% conversation coverage is an assumption. Instead, lead with: "We measure whether these five million accounts see accuracy uplift. If they do, the math is yours."
- **The 58-day latency claim** ("we detect churn 58 days early"). This is an authored fixture parameter, not a measured result. The real latency advantage is structural: they refresh monthly, you move daily. Keep that; drop the 58-day number.
- **The diffuse-arc 30-0-0 result as a headline.** It is real, but it is corpus-specific and on the weak offline reader. If you quote it, expect: "What happens on concentrated arcs?" Answer: "We lose 0-30-0 on concentrated. Your data will tell us which regime you're in." Better: don't quote it as a win; quote the Haiku comparison (2.7x better than the lexicon) and move on.

---

## 5. The three questions that decide it (with answers you should have ready)

### Question 1: "If extraction fires 1 of 8 times on attrition, how do I know it will work on my data?"

**Your answer:**
"You don't. That is exactly why we measure. The 1 of 8 is CFPB narrative data — everyone in that set was angry enough to write a regulator. Your servicing calls look different. Your attrition language might be stronger. The experiment will tell us.

Alternatively: 'We built this extraction for complaint escalation and it fires 23 of 24 times on the same CFPB set. Attrition is harder. We are measuring which direction lifts your retention decisions. If attrition doesn't, we have others profiled.'

**Why this lands:** It is honest. It does not pretend the current extraction is proved. It positions the experiment as a decision, not validation."

### Question 2: "Why attrition and not the complaints angle, where you showed 23 of 24?"

**Your answer:**
"Fair question. Complaints fire better (23/24 vs 1/8 on CFPB text). But the US anchor for complaint escalation is weak — CFPB enforcement is contracted and there is no per-case tariff. Attrition has a published re-acquisition cost: $500-$550. 

That said: both work through the same mechanism. The experiment format lets us measure which direction gives you lift on your data. If attrition shows 15%+ improvement and complaints show 25%, you know. We are not betting on attrition; you are betting on your data. We measure both if you want."

**Why this lands:** It is direct. It answers why you chose attrition (the money anchor) without pretending it is an evidence decision. It also opens the door to measurement, which is more interesting to a bank than "we picked this and we are confident.""

### Question 3: "What happens if your score does not beat our model on the back-test?"

**Your answer:**
"Then we have measured something valuable: that attrition patterns do not appear in conversation ahead of time at your scale, or not for the customers who call. That is data. 

From there, you have choices: (a) we measure one of the 12 other directions we've profiled — pre-delinquency is $3.4K, mortgage loss-mit is legally mandated, scam detection is $7.7B in annual elder fraud loss; (b) we build a PoC on complaint escalation in parallel and you compare; or (c) you have a measurement-ready system and the next team that wants to use it can do it in weeks, not months.

The walk-away is real, but 'it did not work' is never the end. It is the *beginning* of understanding your conversation patterns."

**Why this lands:** It treats the back-test as what it is: an experiment with uncertainty. It also opens the door to the platform story — same system, other signals. A CEO thinks: 'I could see this becoming useful for multiple things.'"

---

## 6. What would make this undeniable and what it costs

There is one measurement that converts this from "interesting" to "fundable": **the back-test run on the bank's own data showing 15%+ lift.**

But there are several paths to undeniable:

### Path A (the planned one): Attrition back-test only
- **Measurement:** Six weeks, parallel model, top-decile uplift on the flagged cohort.
- **Cost:** 6 weeks + bank data access.
- **Payoff:** You know if attrition works. If it does, you have a headline number and a path to production. If it doesn't, you know it doesn't and you measure something else.
- **Risk:** If attrition is weak in their data (e.g., silent leavers never call), you learn nothing about the mechanism's value.

### Path B (recommended addition): Dual measurement
- **Measurement:** Same attrition back-test, *plus* a 3-week PoC building complaint escalation and measuring it on the same call corpus.
- **Cost:** 3-4 additional weeks, no additional bank data (use the same set).
- **Payoff:** You see attrition vs. complaints on the same calls, same ledger, same threshold. If attrition shows 5% and complaints show 20%, you have found a new direction. If attrition shows 20% and complaints show 5%, the original direction is right.
- **Why this is worth the time:** The cost of running both is ~10% more effort than running one. The information gain is 10x. And if you pivot to complaints, you have already built it.

### Path C (if time has suddenly opened): Quick escalation win before the pitch
- **Measurement:** Build complaint escalation extraction on the CFPB set, measure precision/recall on the full 150-document set, not just the 55 card narratives.
- **Cost:** 2-3 weeks, no bank data needed, measure against public CFPB labels.
- **Payoff:** Walk into the room and say: "On the signal where the evidence is cleanest (complaint escalation), we show 23/24 on card narratives. We are measuring that direction live, and measuring attrition in parallel on your data. Here are the results on our side."
- **Why this matters:** It de-risks the attrition back-test. You are not asking the bank to believe a weak signal; you are showing them a strong signal and measuring both.

---

## 7. Where I override my own prior reasoning

**In Phase 1, I recommended complaint escalation as the product direction.** Evidence supports it decisively: 60/65 on extraction, 23/24 on real card narratives, existing consumption process, higher precision (51.8% acceptable for ranking). I still believe that evidence.

**But I now recommend staying with attrition.** Here is why my view changed:

1. **The experiment format is better than I credited.** Pivoting to the client's data is the right move. It de-risks by deferring the value-chain assumptions to the client. That is strategically stronger than my "build the demo and prove it" recommendation.

2. **Reopening the fork now is the highest-risk move.** Ravi decided. The demo is rehearsed. The pitch is in days. Pivoting is not a matter of "we found better evidence"; it is a matter of "we are going to rehearse a new direction in 72 hours."

3. **Repositioning the pitch (not changing the direction) solves the problem.** Instead of walking in saying "we detect attrition at 1/8 accuracy," you walk in saying "we measure whether accumulated evidence improves your model." That is true and it is strong. It does not require a different direction; it requires a different frame.

4. **The mechanism is load-bearing whether you measure attrition or complaints.** If attrition doesn't work and you pivot to complaints mid-experiment, the same extraction + ledger + re-scoring system is there. The only question is which signal you optimize for. That can change week 2 of the back-test without losing the work.

**What I hold.** I still believe complaint escalation has stronger evidence and clearer value. But the experiment format lets you measure this against the client's own data. That is *better* than me being right. It means the client decides, not me, and they decide on their own numbers.

---

## 8. Summary

**The pitch is strong if you stop selling a direction and start selling a measurement.**

The team has built something real: accumulation works, re-scoring works, the mechanism is auditable, it reproduces exactly, it costs less than any competitor, and the latency beats a monthly refresh.

The team's uncertainty about attrition is not a weakness. It is the *source* of credibility. A bank's CFO wants: "Show me, on my data, whether this improves my decisions. If it does, I deploy. If it doesn't, I know." That is exactly what you are offering.

Walk in. Show the demo. Explain the mechanism. Show the experiment. Answer the three questions above. Offer the walk-away. 

If you do that, Venkat and Farhan will understand: this is not a bet on your extraction accuracy. It is a bet on your system's ability to measure and improve *their* decisions. That is a fundable pitch.

The back-test is not Phase 2. It is Phase 1. The measurement phase. And if you pass it, the product phase begins. If you don't pass it, you have learned something that no other team has: whether this mechanism actually improves retention decisions at a real bank. That is valuable regardless of the answer.
