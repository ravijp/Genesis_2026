

# Phase 3 — The Recommendation

## 1. The product idea

**Re-point the product from a score to a memory.** The system is a customer conversation memory: it reads every transcript, extracts what the customer said with the verbatim quote, accumulates it against that customer across months and channels, re-values old evidence when new evidence arrives, and produces two outputs. **Output one** is a brief on the agent's screen before the call connects: four items, each with date, channel, summary, and quote, plus any active flag and a trajectory note. The agent reads it in ten seconds. **Output two** is a suppression flag in the marketing platform's suppression list: a boolean with a reason, a date, a quote, and a review date, checked before any campaign fires. The buyer is the VP of Contact Center Operations for the brief and the CCO or Head of Consumer Protection for the flag. The budget lines are contact-center opex and financial-crimes / compliance opex. The first deployment is one contact center, one product line, 50 agents, 8 weeks. The score, the queue, and the feature export to the propensity model are the second deployment, six months later, signed by the Retention Analytics person.

This differs from the current direction in four specific ways. The product is the brief and the flag, not the score and the queue. The buyer is Operations and Compliance, not Analytics. The value claim is operational (handle time, the email that doesn't go out, the UDAAP control that exists), not a margin chain. The demo ends on the agent's screen, not the score crossing. The work already done — the extraction, the ledger, the retro re-scoring, the quote-citation discipline, the 908 tests, the deployed pipeline, the model-swap measurement, the reader comparison, the CFPB benchmark — all survives. What changes is the output, the buyer, the value argument, and the climax of the demo. The engine does not change. The content re-pointing (signal families for the brief and the flag rather than for the score) is a day of authoring and under a dollar of model spend.

I am overriding the team's choice of Head of Retention Analytics as buyer. I am overriding the team's framing of the score as the product. I am overriding the demo climax (the "58 days earlier" line becomes the agent's screen). I am not overriding the demo structure (three conversations, retro column, day-74 crossing). I am not overriding the six-week back-test as the ask. I am not overriding the latency headline. I am not overriding the honesty beat. I am not overriding the refusal to claim a retention lift that hasn't been measured.

---

## 2. How the value becomes obvious

The $1.65M/year chain is a ceiling with four unmeasured haircuts and no precision leg. Do not present it as a chain. Do not multiply it through out loud. The finance executives will build their own version in their heads and find the missing precision leg before you reach the "gross ceiling" caveat.

The value argument that is self-evident to two finance people is a **ratio, not a chain**:

> **The cost of reading every conversation is $1.58 per thousand. A bank that handles ten million conversations a year pays about $16,000. The value of saving one card customer is roughly $550 — $300 of margin plus $250 of avoided acquisition, both your numbers, not mine. You need to save twenty-nine customers to break even on the reading. On a five-million-account book with 8 to 12 percent annual attrition, that is 400,000 to 600,000 closures a year. Even if the system captures one in a thousand of those — which is a fraction of one percent of the book — that is 400 to 600 saves, $220,000 to $330,000, which is fourteen to twenty times the cost of the reading. Affordability was never the question. The question is whether the capture rate is real. That is exactly what your back-test measures, and it is the one number we refuse to guess.**

Say it in one breath. Do not build the chain. Do not say "five million accounts, 5 percent, 40 percent, 30 percent." Say the ratio. Say the break-even. Say the order of magnitude. Then say the one thing you cannot give them: the capture rate. Then say the back-test is the measurement.

The second value argument is for the CCO, and it is not a number. It is a control:

> **Under UDAAP's abusive prong, turning a disclosed hardship into a marketing trigger is the textbook risk shape. Your customer told you on August fourteenth that she just lost her job. Your marketing system sent her a rewards-upgrade email on August nineteenth. You recorded the call. You did not read it. The flag on the suppression list would have stopped that email. The flag is not a prediction. It is a control. And it is the one thing your model risk file does not currently have.**

This is the line that makes the CCO lean forward. It is not a margin argument. It is a liability argument. The CCO does not need a dollar figure. The CCO needs a documented control that says "we identified the distress on the date, we suppressed the contact on the date, here is the quote, here is the review date." The flag is that control. The absence of the flag is the gap the CCO knows exists and cannot currently close.

If the honest answer is that the dollar value cannot yet be made obvious: **it cannot, and you should say so.** The value is a ratio that says "this is not a cost question, it is a capture-rate question, and the capture rate is what the back-test measures." That is fundable. A CEO can fund a measurement. A CEO cannot fund a margin chain with a hole in it. The six-week back-test with a pre-registered criterion and an explicit walk-away is the thing the CEO says yes to. The $16K cost is the number that makes the yes feel safe. The $550 per save is the number that makes the yes feel worthwhile. The capture rate is the number you do not have, and the back-test is the number you will have in six weeks.

---

## 3. What to demonstrate, and how

Seven minutes. Live. Two finance executives. Synthetic data. No p-values. No code. No sign tests. No CFPB benchmark. No model-vs-lexicon table. No "908 tests." No "183 lines of Python." No "SR 26-2."

**The story:** One customer. A cardholder. Rewards card. $95 annual fee. 0% intro APR until September 30th. Three conversations over 132 days. She is about to make a fourth.

**Beat 1: "What the bank has today." 45 seconds.**

On screen: the CRM record. Account balance. Product. Last interaction: **7/14, phone, "billing inquiry, resolved."** A disposition code. A timestamp. That is the entire history the bank's systems carry forward.

Say: "That is what the agent sees when she picks up the phone. One line. A disposition code. 'Billing inquiry, resolved.' That is the bank's entire memory of this customer. She has called three times in four months. The bank recorded all three calls. The bank will not read any of them again."

**Beat 2: "What she actually said." 90 seconds.**

On screen: a timeline. Three dots. You click each one. The conversation text appears. The system highlights the quote.

Day 0, phone: card declined in Lisbon, fixed. Last two minutes: *"I just noticed the annual fee posted and honestly I'm not sure this card is worth it anymore."* The system records a **price/value objection**. Confidence: low. Quote: attached. **No case opens. Nothing is discarded.** The call is logged as "billing inquiry, resolved."

Day 74, chat: rewards redemption failed twice. She asks: *"And what the APR reverts to when the intro period ends, because I still have about four thousand on there."* The system records **rewards dissatisfaction** and **APR concern**, both with quotes. The evidence now spans two conversations and two channels.

Day 132, phone: she asks for her **payoff figure** and what happens to her **points**. The system records **payoff inquiry** and **points-liquidation inquiry**, both with quotes.

Say: "She told the bank, in her own words, over 132 days, that she is considering leaving. The bank recorded all three conversations. The bank will not read any of them again."

**Beat 3: "What the agent sees." 90 seconds. This is the moment.**

On screen: the agent's desktop. The call is about to connect. The panel appears.

Four items:

| Date | Channel | Signal | Quote |
|---|---|---|---|
| 4/12 | Phone | Price/value objection | *"not sure this card is worth it anymore"* |
| 6/24 | Chat | Rewards dissatisfaction | *"failed twice, I've been trying since May"* |
| 6/24 | Chat | APR/interest concern | *"what the APR reverts to… I still have about four thousand"* |
| 7/22 | Phone | Payoff + points inquiry | *"what's the payoff amount and what happens to my points"* |

**Flag:** CHURN TRAJECTORY — ACTIVE. Set 6/24. Last updated 7/22. Four signals, three conversations, two channels.

**Trajectory:** Fee objection (4/12) → Rewards dissatisfaction (6/24) → Payoff inquiry (7/22). Escalating. 71-day span.

**The retro column.** A small bar chart. Three bars. The 4/12 item: **contribution at write: 0.12. Contribution now: 0.47.** The bar is visibly longer. You point at it and say:

"This remark meant nothing on April twelfth. It was a passing comment after a declined card. The system recorded it, kept it, and did nothing. Then she came back in June with the rewards issue and the APR question. And today she asked for the payoff. The April remark is worth four times what it was on the day it was said, because of what happened since. The system changed its mind about the past. It did not predict the future. It remembered."

Say: "The agent reads this in ten seconds. She picks up the phone. She does not say 'thank you for calling, how can I help you today.' She says: 'I can see you've been dealing with the rewards issue since May, and you mentioned the fee was a concern back in April. Before we get into the payoff, let me check what I can do on the fee and the points.' The call is seven minutes. The customer does not have to re-explain. The customer does not have to threaten to leave for the agent to take it seriously."

**Beat 4: "What the marketing system sees." 45 seconds.**

On screen: the suppression list. One row.

**Customer [ID]. MARKETING SUPPRESSED. Reason: CHURN TRAJECTORY + PRICE/VALUE OBJECTION. Active since 6/24. Review: 8/22. Do not initiate cross-sell, promotional, or credit-line-increase contact.**

Say: "Her bank's marketing system is building next month's rewards-upgrade campaign. It checks the suppression list. Her name is on it. She does not get the email. Without this flag, she would have gotten an email offering a new card with a better rewards rate, four days after she asked for her payoff figure. That is not a sales problem. That is a UDAAP problem. And the flag is not a prediction. It is a control. It is the thing your model risk file does not currently have."

**Beat 5: "The call that should have been seven minutes." 60 seconds.**

On screen: the "without the brief" transcript, or a 90-second audio clip. The agent picks up. "Thank you for calling, how can I help you?" The customer explains the payoff question. The agent looks it up. The customer asks about the points. The agent says, "I'm not sure, let me have a specialist call you back." The customer says, "I'm thinking of switching cards, honestly." The agent says, "I'm sorry to hear that. Is there anything we can do to change your mind?" The customer says, "Maybe." Fourteen minutes. Disposition code: "churn risk, retention offer pending." Goes into a queue. Nobody looks at it for three weeks.

You do not say "see?" They already saw it.

**Beat 6: The ask. 30 seconds.**

Say: "What we want is a six-week retrospective back-test. Your existing call recordings. Your existing closure label. No production integration. No customer contact. Pre-registered success criterion: the brief changes the agent's documented action in the top hundred flagged customers, measured by disposition-code change and handle-time delta on the pilot desk. And, separately, the score's top-decile uplift as a challenger feature against your production model. Fixed fee. Explicit walk-away. If the criterion is not met, the answer is no and we say so. Reading every conversation costs $1.58 per thousand. Your ten million conversations a year cost about $16,000. You need to save twenty-nine customers to break even. The question is not whether it is affordable. The question is whether the capture rate is real. That is what the six weeks settle."

You stop.

**What must be built for this demo:**

1. **The "what the bank has today" screen.** The sparse CRM record. Disposition code. Account balance. Product list. Deliberately empty where it should be full. *Two hours.* This is the contrast that makes the brief land.

2. **The agent-brief panel.** Four items. One flag. One trajectory. The retro bar chart (0.12 → 0.47, animated: the bar grows when you click it). The call is about to connect; the panel is there. *One to two days.* The data is already in the ledger. This is a presentation layer. The current demo shows the retro column; re-skin it as the agent's screen, add the flag line and the trajectory line.

3. **The suppression-list screen.** One row. One customer. The flag. The reason. The quote. The review date. *Four hours.* Static. No CRM integration needed for the demo.

4. **The "without the brief" transcript or audio clip.** Scripted. 90 seconds. The generic retention script. The disposition code. *Three hours to script, two hours to produce if audio.*

5. **The "with the brief" transcript or audio clip.** Scripted. 90 seconds. The agent has the panel. The agent says the right thing. *Three hours to script, two hours to produce if audio.*

Total build: **three to five days** of focused work. The extraction, the ledger, the retro re-scoring, the quote-citation discipline: all already built and measured. What is being built is the presentation layer and the two screens that do not exist yet.

**What the demo must not do:**

- Do not show the score as a number. The score is an intermediate representation. The brief is the output. If a number appears, it is the 0.12 → 0.47 bar, which is the retro column, and it is shown as a mechanism, not as a product output.
- Do not say "58 days earlier." Say "the evidence was complete on day 74. A per-call system first flags it on day 132." The structural claim. Not the prediction claim.
- Do not show the model-vs-lexicon table. Q&A material.
- Do not show the CFPB benchmark. Q&A material.
- Do not say "agentic." The product is a memory. The agent is the LLM. The code counts and remembers. The human decides.
- Do not show the nine-arm ranking test. Do not show the 30-seed sign test. Do not show the dumb-ledger result. Do not show the p-value.
- Do not say "we spot churn." Say "we remember what the customer said."
- Do not end on the score crossing. End on the agent's screen and the flag.

---

## 4. What to keep

**Load-bearing. Must survive any reframing. Do not touch:**

- **The extraction layer** (model + lexicon, with the verbatim-quote discipline, the four-plus-word word-boundary match, the exact-substring check, the discard-on-unresolvable-reference rule). This is the thing that works. 0.6549 recall. 5,723 of 5,736 verbatim. It is the product. The brief is made of extracted signals with quotes. Without this, there is no brief.

- **The append-only ledger with the four-number retro re-scoring** (`contribution_at_write`, `score_at_write`, `contribution_now`, `score_now`). This is the mechanism. 239 of 485 entries are worth more now than at write. 0 of 485 under unweighted count. The 0.12 → 0.47 bar in the demo is this mechanism. Without this, there is no "the system changed its mind about the past." Without this, the product is a search index, not a memory.

- **The deterministic scoring core** (the code that counts, accumulates, decays, corroborates, and checks thresholds, with the unit test that asserts bit-identical output). The design rule: code counts and remembers, the model reads and judges. This is what makes the score reproducible given a fingerprint. This is what the model risk function needs to see. This is what SR 26-2's "deterministic rule-based processes" language covers. Keep it.

- **The 908 tests, the reproducibility harness, the byte-identical re-run from a different commit, the seed-by-seed manifests with git SHAs.** This is the engineering quality the AI judge scores. This is the "a fresh clone reproduces every published number with no key in 104 seconds" claim. This is the "we already swapped the model and measured it for $0.027705" claim. All of it is the answer to "is this production-ready?" Keep every test. Do not cut any.

- **The deployed AWS pipeline agreeing with local.** The CloudWatch alarm that went OK → ALARM → OK. The 260-message re-run producing the same 34 entries and 1 case. The malformed-transcript isolation. This is the "it is not a notebook, it is a deployed system" claim. Keep it.

- **The model-swap measurement** (Nova Lite vs Haiku, same 282 conversations, $0.027705). This is the answer to "what happens when the model changes?" Keep it.

- **The reader comparison** (model vs lexicon, same 282 conversations, same planted ground truth, the 60/65 vs 1/65, the 27/72 vs 33/72 loss, the 7x false-positive counterweight). This is the answer to "what does the AI actually do?" Keep it. Do not put it in the demo. Put it in Q&A.

- **The CFPB benchmark** (150 narratives, 55 card, 29/29 fired, 26/35 exact type, 1/8 churn intent, 23/24 complaint escalation). This is the honesty beat. Keep it. Say the 1/8 in the same breath as the 29/29.

- **The confidence float measurement** (21 distinct values, 28.4% at 0.85, the ablation showing it is the least load-bearing mechanism under the model reader). This is the answer to "is the confidence number real?" Keep it. Concede it. Say bucketing is the next thing you build.

- **The SR 26-2 governance framing** (the three-tier structure, the GenAI scope carve-out read as "your AI governance policy governs," the fingerprint protocol, the model-migration protocol). This is the answer to "model risk will kill this." Keep it.

- **The six-week back-test structure** (fixed fee, pre-registered criterion, explicit walk-away, no production integration, no customer contact). This is the ask. Keep it. Add the operational criterion (disposition-code change, handle-time delta on the pilot desk) alongside the model criterion (top-decile uplift).

- **The TRAJECTORY_TEAM routing** (distress → collections, life event → vulnerability, churn intent → retention). This is the "we do not sell to a distressed customer" claim. This is the mapping that becomes the suppression flag. Keep it. Extend it.

- **The "no outbound contact surface" design** (no route, no button, no handler, not disabled, absent, a grep for offer or eligibility returns nothing). This is the safety case. This is the line that makes the two executives stop listening to the pitch and start thinking about their own business. Keep it. Make it operational with the flag.

- **The two refusals** (the incremental save rate and the margin per account are the client's numbers, not yours). Keep them. They are the credibility anchor for the value argument.

**Sunk cost. Stop carrying:**

- **The "conversation attrition score" as a product name and concept.** The score is an intermediate representation. The brief is the product. The flag is the product. The score feeds the queue in year two. The score is not what the agent reads. The score is not what the marketing system checks. The score is not what the CCO files in the model risk document. Stop calling the product a score.

- **The queue as the primary output.** The queue is a feature of the brief for the desk that needs ordering. The brief is useful whether it is first in the queue or fourteenth. The queue's ranking quality is 8th of 9 and indistinguishable from random. Do not sell the queue. Sell the brief.

- **The $1.65M value chain as the primary value claim.** The ratio ($16K cost, $550 per save, 29 to break even) is the claim. The chain is the ceiling. Do not multiply the chain through out loud. Do not present it as a chain. Present the ratio.

- **The "58 days earlier" as the demo climax.** The agent's screen is the climax. The "58 days earlier" is a structural observation ("the evidence was complete on day 74") that can be said in Q&A if asked. Do not say it on stage.

- **The Head of Retention Analytics as the sole buyer.** Operations signs the brief. Compliance signs the flag. Analytics signs the feature export in year two. Three buyers. Two deployments. The current documents have one buyer and one deployment. Fix the buyer. Keep the deployment.

- **The reader beat as a numbered beat in the story.** It is Q&A material. The CEO does not need the 60/65 vs 1/65 table. The AI judge scores it separately. Remove it from `01-THE-STORY.md` as a beat. Keep it in the objection playbook.

- **The "layer" framing on stage.** "One layer, many teams, none of these is the headline, the layer is." This is architecturally true and commercially wrong. The headline is the screen. The headline is the flag. The layer is the reason the second desk is cheap to add, not the reason the first desk is worth buying. Say it once, at the end of the demo, as the expansion path. Do not lead with it.

- **The pre-delinquency, cross-sell, credit-line-decrease, agent-coaching, deposit-flight, and credit-line-increase directions.** They are correctly cut, correctly withdrawn, correctly refused. Keep them in `04-ALTERNATE-STORIES.md` as Q&A depth. Do not re-open them. Do not re-point the product at any of them. The re-pointing is from score-and-queue to brief-and-flag, not to a different problem.

---

## 5. The three questions that decide it

**Question 1: "We already have a retention model."**

This is the first question. The CEO will ask it in the first two minutes. It is the "you already own this" objection in its most specific form.

Say:

"You almost certainly do. And it is usually a value score. It tells you how much you care if a customer leaves. It does not tell you they are leaving. Different questions. Most issuers run both. And the first deployment is not your model. The first deployment is the agent's screen and the marketing suppression list. Your model is the second deployment, six months from now, when the feature is exported to the data warehouse and runs as a challenger against your production champion. The back-test measures both: the operational impact on the pilot desk, and the model uplift. The ask covers both. The first one is yours to judge in six weeks. The second one is yours to judge after that."

Why this works: it does not compete with their model. It sits alongside it. It names the integration (feature export, challenger cycle). It gives the CEO a two-phase answer that matches the two-phase deployment. It does not say "our model is better." It says "our model is different, and the first thing you get is not a model at all, it is a screen."

**Question 2: "Day seventy-four. The customer is not calling. She is at home. What physically happens next?"**

This is the question that ends the pitch if you do not have the answer ready. The team has the answer: "we never contact them, the case briefs the next agent." That answer is incomplete. It covers the brief. It does not cover the flag. It does not cover the 58 days in between.

Say:

"Two things. First, the case sits on the account. The next time she calls — and in cards, she does; the payoff call, the points call, the 'I'm switching' call — the agent picks up and the brief is already on the screen. She does not have to re-explain. The agent does not run the generic script. That is the contact-center side. Second, and this is the compliance side: the suppression flag is in the marketing list. The rewards-upgrade campaign that would have gone out in week four checks the list. Her name is on it. She does not get the email. We never contact her. We change what your agent knows and what your marketing system does. Neither of those requires you to build anything. The flag is a row in a table your platform already queries."

Why this works: it answers the question with two things, not one. It covers the 58 days (the flag stops the email). It covers the next call (the brief changes the agent's behavior). It makes "no outbound surface" operational: the system cannot call her, and the marketing system will not call her, and here is the flag that makes the second true. It names the specific integration (the suppression-list query, which the marketing platform already does). It does not require a new contact motion.

**Question 3: "Why isn't this what Verint or NICE or Observe already sells me?"**

This is the "you are a feature" objection. The CEO will have looked at the vendor list. The contact center already has a conversation analytics tool. The question is: what do I get that I do not already have?

Say:

"They score the call. They tell you what happened in this interaction. Sentiment. Topic. Compliance flag. The call is the unit. The call is the product. When the call ends, the score is filed and the customer walks away from it. We do not score the call. We remember the customer. The unit is the customer across time, across channels. The per-call output is our input. The product is what accumulates: the fee objection from April that meant nothing in April and means something in July because of the rewards issue in June and the payoff inquiry this week. The nearest thing on the market is Twilio's Conversation Memory, which shipped in May. Their own documentation says that when two things a customer said conflict, they reconcile and keep only the current truth. They discard the old entry. We keep both, and the old one can become worth more later. Theirs is memory for a conversation. Ours is evidence for a decision. And the per-call vendors do not do this, because their business model is per-interaction pricing. The accumulation is not a feature they will add. It is a different product."

Why this works: it names the real competitor (Twilio, not Verint) and cites their own documentation. It says "they discard, we keep" in one sentence, which is the architectural difference. It explains why the incumbents will not add it (business model). It does not say "we are the only one." It says "the nearest one does the opposite." It is sourced, not asserted. It converts the objection from "you are a feature" to "you are a different product that the feature vendors will not build because it would change their pricing model."

---

## 6. What would make this undeniable, and what it costs

**The operational measurement. This is the one thing that converts this from interesting to fundable.**

The back-test measures the score's top-decile uplift in the propensity model. That is the Analytics person's metric. It is necessary. It is not sufficient. The Operations person's metric is: on the pilot desk, for the top hundred flagged customers in the next 30 days, does the disposition code change? Does the handle time drop? Does the "churn risk, retention offer pending" disposition become "retention offer accepted" or "fee waiver processed" instead of "cancellation processed"?

The structure of the measurement:

- **Pre-registration:** before the back-test starts, register: the top hundred flagged customers on the pilot desk over the next 30 days. The success criterion is: the disposition code for at least 30 of them is different from the disposition code that would have been assigned without the brief, measured by a blinded coding of the call transcript. The handle-time delta is reported descriptively, not as a success criterion. The model top-decile uplift is a separate, parallel criterion.
- **Blinding:** the agent does not know the customer is in the study. The brief appears on the screen. The disposition code is coded by a QA analyst who does not know the brief was present. The coding is: "what was the agent's action?" not "was the brief useful?"
- **Walk-away:** if fewer than 15 of the 100 have a changed disposition code, the answer is no. The brief does not change agent behavior at this scale. The product is not the brief. The back-test costs the fixed fee. The relationship ends.

This is the measurement that the CEO can fund. It is not a model validation. It is an operational A/B test with a blinding protocol. It takes six weeks. It costs the client's data and the client's QA team's time. It costs the vendor the fixed fee. It produces a number: "30 of 100 disposition codes changed, here they are, here is the before and after." That number is the thing that the Operations person signs the second deployment with.

**Cost to build the operational measurement into the back-test proposal:** the protocol is a document. The blinding is a QA process. The coding is a disposition-code comparison. The engineering is: the brief appears on the pilot desk's screen (which is the first deployment), the disposition code is logged (which the CRM already does), the comparison is a join. Two days of writing the protocol. One day of engineering for the join. No new model. No new extraction. No new ledger.

**The suppression flag. Build it. One day of engineering.**

The flag is not in the product. It is a sentence in Beat 4. It should be a row in a table. The build:

- The `TRAJECTORY_TEAM` routing already maps churn intent → retention. Extend it: when a churn trajectory is active (score above threshold, two or more signals, two or more conversations), the system writes a boolean to the CRM's suppression-list object. The object already exists. The marketing platform already queries it. The write is one line of code in the batch pipeline.
- The flag carries: customer ID, reason (the signal family), the date set, the quote, the review date (90 days, configurable).
- The flag is reviewed by the CCO's team on the review date. They can dismiss it. The dismissal writes back to the ledger (the system already has this: "dismissal writes back to the ledger").
- The flag is in the model risk document. It is a control. It has a date, a reason, a quote, a review date, and a disposition (active or dismissed).

The build is one day. The legal opinion on the suppression flag's interaction with the bank's existing UDAAP controls and the marketing platform's existing suppression-list logic is the bank's cost, not the product's. But the product should be able to say: "here is the flag, here is what it writes, here is where it goes, here is the review process, here is the model risk documentation."

**The agent's screen. Build it. One to two days of engineering.**

The screen is the product. The demo shows it. The pilot deploys it. The build:

- The CRM integration: a related object on the customer record containing the four items, the flag, the trajectory note. The agent's desktop (Genesys, NICE, Avaya, Salesforce CTI) displays the related object as a panel. The panel is: four rows (date, channel, signal, quote), one flag line, one trajectory line, one retro bar (the 0.12 → 0.47). No scrolling. No tabs. Ten seconds to read.
- The data source: the ledger. The batch pipeline runs overnight. The ledger is updated. The CRM object is refreshed. The agent's panel reads the CRM object on call connect. Latency: under 100 ms (it is a CRM read, not a model call).
- The signal families: the same eight families that already exist. The brief shows the top four by contribution_now. The flag shows the active trajectory. The trajectory note shows the escalation path.

The build is one to two days. The content re-pointing (the signal-family definitions, the phrase pools, the thresholds) is a day of authoring and under a dollar of model spend. The extraction does not change. The ledger does not change. The retro re-scoring does not change. The quote-citation discipline does not change. The 908 tests do not change.

**Total cost to make this undeniable:**

| Item | Cost | Duration |
|---|---|---|
| Agent-brief screen (CRM integration + desktop panel) | ~$0 model spend | 1-2 days engineering |
| Suppression flag (CRM suppression-list write + review process) | ~$0 model spend | 1 day engineering |
| Operational back-test protocol (blinding, coding, disposition comparison) | ~$0 model spend | 2 days writing, 1 day engineering |
| Content re-pointing (signal families for brief and flag, not score and queue) | ~$0.45 model spend | 1 day authoring |
| Demo re-skin (agent's screen + flag screen + "without the brief" clip) | ~$0 model spend | 3-5 days |
| Legal opinion (data retention, deletion, suppression-flag interaction) | Bank's cost | 2 weeks |
| **Total vendor cost** | **~$0.45 model spend** | **8-10 days engineering** |

This is not a rebuild. This is a re-pointing. The engine, the extraction, the ledger, the tests, the pipeline, the measurements: all survive. The output changes. The buyer changes. The value claim changes. The demo climax changes. The back-test criterion gets a second leg. The flag is built. The screen is built. The protocol is written.

**What I am overriding from my own Phase 1:**

In Phase 1 I said the demo should end on the agent's screen and the flag. I said the buyer is Operations and the CCO. I said the value is operational. I said the product is a memory, not a prediction. I am keeping all of that. What I am adding from Phase 2 is: the score is not the product, the queue is not the product, the $1.65M chain is not the value argument, and the buyer is three people across two deployments, not one person across one deployment. What I am overriding from the team is: the buyer is not Analytics, the score is not the product, the demo does not end on the score crossing, and the value is a ratio, not a chain.

**What I am not overriding:**

The demo structure (three conversations, retro column, day-74 crossing). The six-week back-test as the ask. The latency headline (used in minute one, attributed to the flag and the queue, not the feature export). The honesty beat (the corpus limitation, the 1/8, the CFPB split). The two refusals (save rate and margin are the client's numbers). The "no outbound surface" line (routing plus absence, not a branch in code). The SR 26-2 governance framing. The model-swap measurement. The confidence float concession. The reader comparison in Q&A. The "we never discard" line. The Twilio citation. The "your value score, our propensity score" distinction. The "not all attrition is worth stopping" line. The "we'll run the three-scorer falsification" offer. All of it survives. The re-pointing changes the product, the buyer, the value argument, and the demo climax. It does not change the evidence, the governance, the objections, or the ask.

**The one sentence that should survive the room:**

Not "we turn the conversations you already record into a live feature inside the churn model you already run." That is the team's sentence, and it is about the score and the model. It is true. It is the second deployment. It is not the product.

The sentence that survives the room is:

**"Your agents make every call blind. Your customers have already told you what matters. We make sure the next conversation starts where the last one ended — and we make sure the next email doesn't go out to someone who has told you they can't afford it."**

The first half is the brief. The second half is the flag. The first buyer is Operations. The second buyer is Compliance. The product is a memory. The ask is a measurement. The cost is $16,000 a year. The break-even is 29 customers. The walk-away is explicit. The six weeks settle it.