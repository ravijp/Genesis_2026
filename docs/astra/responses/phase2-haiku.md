# Phase 2 Review — assessment of the team's analysis

## Executive summary

The team has done rigorous self-criticism and made one genuinely smart strategic move: reframing from "here is a value chain" to "here is a funded experiment with a pre-registered criterion." That move solves a real problem. But they have chosen the wrong direction on the evidence, and the self-criticism, while honest, is sometimes a substitute for interrogation rather than an alternative to it.

The mechanism is strong. The evidence supports complaint escalation overwhelmingly — 60/65 vs 1/65 on the CFPB-derived metric, and 23/24 vs 1/8 on real credit-card complaint text. The direction they chose (churn intent) fires 1/8 on the same real card text. They know this. They chose attrition anyway, for reasons that are defensible but not strategic.

---

## 1. Where I was wrong

**The experiment framing wins.** I recommended complaint escalation as a product, which is correct on the evidence. But I missed that this evidence is not actionable without a client's data. The team solved that problem by pivoting from "here's the value chain, validate it" to "let's measure it together, with a walk-away." That's a better pitch to a CEO and it's a better risk allocation. A CEO can say yes to a six-week experiment; he cannot say yes to a value chain with a 0.6% addressable population and an unmeasured precision haircut.

**The latency claim is not what I thought it was.** I assumed they meant "we detect churn 58 days early" (a number they explicitly call out as authored). Reading their final version, the latency claim is structural: "Your model refreshes monthly, ours moves the moment the transcript lands." That's unattackable and it doesn't rest on causality or lift. It's true by construction. That's smarter than I credited.

**Honesty as a tactical move has force.** The honesty beat — quoting 29/29 fired on marked card documents *and* "churn intent 1/8" in the same breath, never separating them — is not just integrity. It's a framing device. It disarms the one objection that would land hardest if discovered in a follow-up: "You quoted 29 out of 29 and buried that only 1 of 8 for churn." Volunteering it costs the moment but buys credibility for everything after.

**I underweighted the demo.** I designed the conceptual demo (Sarah's three-complaint arc). The team has actually built it, shown it, iterated it. They've discovered that the moment a competitor mention fires on is not a decision point — it's the event already happening. They moved it to rewards friction + promo expiry, which is genuinely pre-decisional. That's the kind of refinement that only happens by rehearsal. The demo is strong enough to carry a pitch if the value chain is weak. This team knows that.

---

## 2. Where I disagree and I'm holding my position

### The direction choice is wrong on the evidence.

I do not think the attrition choice is justified by the data, and the team's own data argues against it.

**The signal comparison shows complaint escalation is 60/65 real-world performance and churn intent is 1/8 on the same real credit-card narratives.** That is not a marginal difference; that is a category difference. The team extracts complaint signals from card documents with precision better than stated, but they extract churn intent with precision of 12.5%. They know this. It's in the honesty beat. But then they pitch churn intent anyway.

**The argument that "we can't build complaint escalation because we have no consumption process" is backwards.** The consumption process for complaint escalation is existing complaints workflow. Existing. A case opens, a specialist handles it, the outcome is known. That's not "needs building." The team explicitly says this in the alternates file (06-DEFENDING-THE-SCORE.md references "Complaint escalation avoidance (27/35)" as the 2nd reserve, with 23/24 marked documents). The reason they didn't pick it is not the evidence; it's that "there is no US dollar anchor" after the UK Ombudsman tariff went away.

**That is a money problem, not a product problem.** A product with strong evidence and an unclear value chain is a stronger pitch than a product with weak evidence and a clear value chain. They solved this by pivoting to the experiment format, which I credit. But the experiment format also means they're asking the client to validate a direction the evidence doesn't support. The back-test will measure attrition accuracy. It will not measure whether attrition is the right signal to measure.

**The team's own reasoning in 04-ALTERNATE-STORIES.md agrees with me, as written.** They rate complaint escalation 27/35 and card attrition 30/35 — a 3-point difference, well within noise, with the only substantive difference being "no anchor" on complaints. Then Ravi decides: attrition leads. That's a call Ravi makes; it's not an evidence decision. I'm not arguing Ravi was wrong to decide that. I'm saying the evidence does not support it, and the team knows it.

### The confidence float is a live technical debt they're treating as resolved.

**They say "bucketing is a formality" but they haven't built it.** The measured distribution is 21 distinct values, 28.4% at 0.85 — a menu, not a probability. Under the model reader, removing it changes 10.5% of the top-150. Under the offline lexicon, it changes 20%. That's real. They conclude "it costs almost nothing" and therefore "recommendation: bucket it."

But "bucket it" requires: (a) picking the bucket boundaries, (b) re-running the ablation to verify the ranking doesn't change, (c) updating the model call sites, and (d) updating the calibration guidance. They say "about a day of work." That may be true. **But it's not true for a 09-11 pitch.** They don't have the bucketed scores. They'll say "the next thing we build." That's honest. But it means a known source of regulatory friction remains live in the design.

**Where this bites:** when a bank's model-risk team asks "Is this an uncalibrated model output?" the answer is "Yes, for now." Then "What's the risk control?" is "We'll bucket it." Then "When?" is "After deployment." That's not a blocking objection, but it's not a non-objection either. The team should either (a) have bucketed it and shown the retest, or (b) owned the gap more explicitly in the pitch. Saying "it's load-bearing under the lexicon but not the model, so the production system is safe" is close, but it still leaves raw floats in cache until they rebuild.

### The addressable-population problem is undersold.

**40% conversation coverage is not a measured number; it's an assumption.** They derive it from "five million accounts × 5% voluntary attrition × 40% conversation coverage × 30% voicing a leading signal." The 40% is "a client input for every direction" — meaning they don't know what it is. A bank might have 5% attrition but only 10% of those people ever call. Or 70%. The value chain is exquisitely sensitive to this number. A 10-point swing in coverage swings the gross value by $330K.

**And there's a selection bias hiding in the 40%.** The 40% is the people who call and complain. The silent leavers — the ones most worth saving — may call less. So the system systematically scores the noisier, possibly-less-profitable part of the attrition population. The team acknowledges this is "a property of every conversation-derived feature ever built." That's true. But it means the addressable population may be smaller and less valuable than the math suggests. They don't have a sensitivity analysis: "If conversation coverage on attrition candidates is 10%, the value becomes..."

### The T3 answer (consumption path) rests on assumptions they don't validate.

**"We never contact your customer. We change what your agent knows the next time they do — and in cards, they do."** That's true *if the customer calls*. But: (a) do they? That's the contact-rate assumption. (b) Is the agent empowered to act on the brief? (c) Does the brief survive the call routing? None of this is false, but it's all an implementation detail. A bank that has a fully manual case-assignment process will get value. A bank that routes by IVR might not. The team glosses over this. It's not a fatal flaw, but it's a load-bearing assumption that's not tested.

### The generalization gap is larger than stated.

**"Almost every own-measured number was measured on a generic retail-banking corpus with zero credit-card content."** They say this explicitly and they label it clearly. They've run the CFPB split: 55 card narratives, 1/8 churn intent. But that's 8 documents. The team's own rules of evidence (never quote at 10 seeds) should apply here too. 1/8 is n=8 and it's post-hoc. They're honest that it's directional, not quotable. Good. But they're also pitching it as the thing that validates the direction. That's not a contradiction, but it's tense. The experiment format solves this by deferring validation to the client. But the client's back-test will tell them whether *their* attrition signal works, not whether *this* system's extraction is right.

---

## 3. What they missed entirely

### The ablation results suggest the mechanism doesn't generalize.

The team measures the full ledger against 9 ranking arms across 30 seeds. Result: 8th of 9, recall 0.115 vs. random's 0.113. On diffuse arcs it wins 30-0-0. On concentrated arcs it loses 0-30-0. On the whole portfolio, it is not better than random.

**The honest question they should have asked: why?** Is accumulation actually a weak mechanism? Do customers' complaints really not pattern over time? Or is the answer-key more sensitive to recent signals, so older entries decay to noise?

They don't answer this. They say "power failure, not refutation" and move on. But a 30-0-0 win on one arc type and an 8th-of-9 loss on the portfolio suggests the system is fit to a specific arc type (diffuse), not to the general problem. If a client's attrition is concentrated (three reasons, three conversations) rather than diffuse, this system will not help. The team has measured this and not flagged it prominently. That's a gap.

### The precision problem is not measured and could disqualify the direction.

**On 55 real credit-card CFPB narratives, the model fires something on 29/29 marked documents.** Precision: 29/56 fired = 51.8% on the (document, signal-type) pair. **Half the signals are false positives.**

In a demo, you hide false positives. In production, a compliance team needs precision. A system that flags half of its firings as false noise is not usable as a binary classifier. The team's answer is: "Use it as a ranking, not a classifier. Your retention team works the top N anyway." That's correct. **But it means the system is only useful inside a capacity-constrained queue, not as a flagging system.** That changes the consumption path. It also changes the value: you're not scoring everyone, you're ranking the top 10% of a compliance team's workload.

The team knows this. They don't hide it. But they also don't flag it as a major constraint on the direction choice. A direction where churn intent fires 1/8 and complaint escalation fires 29/29 might be quite different when you factor in that 29/29 includes false positives. The precision-on-false-positives comparison is different between the two directions.

### No dual validation, and they're not planning one.

**They measure extraction-level performance (do the signals fire?) and ranking-level performance (does the rank predict outcome?).** They do not measure validity — do the extracted signals make sense to a human? Is the read correct?

They say: "Every signal carries its verbatim quote, exact-substring checked." So a human can read it. But that's auditability, not validation. A system that reads signals correctly but ranks them wrong is worse than a system that reads incorrectly but ranks well. The team hasn't separated these. And they're not planning to: the back-test will use the client's closure label as ground truth. But that only validates ranking, not reading.

This matters because the CFPB precision split (51.8%) suggests the reading is noisy. A modeller might ask: "Why should I trust that my feature is stable if the underlying signal extraction is 50% false positives?" The team's answer would be: "Because the overall ranking is what matters." Maybe. But it's another assumption.

### The pre-delinquency recommendation is withdrawn on schedule grounds, not strategic ones.

**The team measured pre-delinquency: ~$3,400 multiple (3-9x), T3 is "worse than attrition" (hardship is opt-in, needs contact), but the T4 anchor is the strongest on the list.**

Then they say: "Do not re-open this before 09-11."

That's a decision. It's correct given the time constraint. But it means they've retired a direction with real evidence, not because the evidence is bad, but because switching now is "highest-risk available use of remaining time." That's honest. It's also an admission that the evidence could have gone either way if they'd had more time.

**The strategic question they don't ask: would a bank prefer to validate attrition with weak evidence or pre-delinquency with stronger evidence?** A bank's CFO might prefer the bigger multiple and accept that the extraction needs tuning. The back-test format would work for both directions. By shutting down pre-delinquency for schedule, the team is implicitly saying attrition is the better direction. On the evidence, I don't think they can claim that.

### The outbound-contact surface is not zero.

**"Distress and life-event signals never route to retention. They go to collections and to a vulnerability desk — that's a mapping in code."**

True. But the system still has an opinion on who gets flagged for collections. If that opinion is wrong or biased, it directs human attention to the wrong customers. And the system has no accountability mechanism for that. No audit trail of "we recommended this customer for collections and the result was X." The routing is safe (no automated contact), but the bias is not addressed.

They say: "The true version is stronger" — routing plus absence, not a guard. It is. But they haven't built a countervailing argument: "If we flag customers for collections, how do we know the flag is right?" The answer is probably "the collections team validates it" — which is real but offloads the responsibility.

---

## 4. The evidence, read with skepticism

### What actually supports the central claim?

**Central claim (team's version): attrition detection from conversation accumulation.**

Supporting evidence:
- **The extraction comparison (60/65 vs 1/65 on complaint escalation).** Genuine. Clear category difference. But the central claim is attrition, not complaints. So this evidence is orthogonal to the main claim.
- **The CFPB card narrative split (1/8 on churn intent).** This directly tests the central claim on real card text. Result: 12.5% recall. That is not supporting evidence; that is contradicting evidence.
- **The whole-portfolio ranking (8th of 9 on 30 seeds).** Not supporting. That's neutral to slightly negative.
- **The diffuse-arc result (30-0-0 on 30 seeds).** This supports accumulation as a mechanism for diffuse evidence. It does not support attrition detection specifically.

**What actually supports complaint escalation:**
- 60/65 on extracted complaint escalation.
- 23/24 on real CFPB card narratives.
- Existing consumption process (complaints workflow).
- Higher precision (51.8% is acceptable for a ranking feature to feed escalation decisions).

**Honest verdict: the evidence supports complaint escalation and contradicts churn-intent attrition.**

### What's being over-read?

**The whole-portfolio ranking is not a general-purpose win, and they're treating it like one.** 30-0-0 on diffuse arcs is great. But 8th of 9 on the whole portfolio and 0-30-0 on concentrated arcs means the system is not general. A bank with concentrated attrition will not see the 30-0-0 benefit. The team knows this. They emphasize the diffuse result and accept the portfolio result as a power problem. Maybe. But it also might be a signal that the mechanism only works in a narrow regime.

### What's being under-read?

**The chance-gate failure at p=0.076 is close to significance and the team treats it as safely published.** It is safely published — p=0.076 is not p=0.001, and the pre-registered criterion is met. But it's worth asking: why is a mechanism designed to detect distributed signals barely better than chance on a general ranking? The answer is probably "the general ranking task includes many signal types and many arc configurations." But it's also worth asking whether the 30-0-0 result on diffuse arcs is an overfitting artifact to the corpus structure, not a generalizable phenomenon.

### Which results support which product?

| Direction | Strongest evidence | Weakest evidence |
|---|---|---|
| **Attrition** | Diffuse-arc ranking (30-0-0), latency advantage (structural), retest stability | Churn intent on real card text (1/8), portfolio ranking (8th/9), consumed by unpublished contact rate (40%) |
| **Complaint escalation** | Real card narrative performance (23/24), extraction recall (60/65), existing consumption process | No US dollar anchor, CFPB enforcement weak, requires no new ledger just better routing |
| **Neither — measure only** | Whole-portfolio performance is not better than random; the system is fit to a specific arc type | Power problem is real; 52K sequential calls needed to replicate diffuse result with model reader |

**The evidence base supports the *idea* (accumulation works on diffuse signals) better than it supports the *direction* (attrition is the direction to monetize).** The team has measured the idea. They have not validated the direction without a client back-test. That back-test is correct and necessary. But it means the 09-11 pitch is selling an idea with evidence, a direction without evidence, and an experiment that will validate the direction. That's an honest position and the experiment framing is the right response to it.

---

## 5. The self-criticism: rigour or substitute?

**It is rigour in its honesty, but it is substitute for rigour in what it does not ask.**

Examples of real rigour:
- Withdrawing the pre-delinquency recommendation and explaining the arithmetical error (7-10x → 3-9x when the numbers are checked).
- Publishing the loss (financial distress 27/72 vs lexicon 33/72).
- Measuring their own mechanism's weakness (confidence distribution: 21 values, 28.4% at 0.85).
- Admitting the ablation hasn't been run (bucketing the confidence float is "should be done" not "is done").

Examples of avoiding the hard questions:
- "The portfolio ranking is 8th of 9, but that's a power problem" — *true, but have you modeled how much power you'd need?* The answer is ~52K sequential calls. That's a real constraint, but it also might mean the mechanism is just weaker than hoped.
- "Contact rate is 40%, a client input" — *true, but does that mean you're not responsible for validating the value chain?* The experiment format means the client validates it. That's correct. But the team could have said: "We're solving the attrition problem contingent on the bank's contact rate. Here's a sensitivity table."
- "We'll bucket the confidence float" — *true, but you haven't proven bucketing preserves ranking.* The answer is "the harness exists, run it before promising." That's honest. But it's also deferring a known technical risk to after the pitch.

**The pattern: the team is honest about what they haven't done, but not always rigorous about whether what they haven't done matters.** That's a valid trade-off given time pressure. But it's worth flagging: intellectual honesty is not the same as intellectual rigor. The team has the former. They could strengthen the latter by asking harder follow-up questions on the gaps they identify.

---

## 6. Assessing the choices made

| Choice | Verdict | Reasoning |
|---|---|---|
| **US attrition over UK complaints** | Defensible but not optimal. Evidence supports complaints. Schedule + money anchor favors attrition. | The £650 Ombudsman anchor is gone. Complaint escalation has no US tariff. Attrition has "acquired cost ~$500" from public filings. But extraction evidence favors complaints (60/65 vs 1/65). This is a business choice, not a data choice. |
| **Pitch the experiment, not the value chain** | Excellent. This is the single best move the team made. | Solves the fundamental problem: you can't prove the value chain without the client's data. Pivoting to "let's measure together, with a walk-away" is both honest and more fundable. |
| **Reframe from "attrition" to "latency + experiment"** | Good. Structurally defensible, tactically smart. | The latency claim (model refreshes monthly, ours moves instantly) is unattackable and doesn't rest on causality. The experiment claim (six-week back-test, pre-registered, explicit walk-away) is something a CEO can act on. |
| **Demo synthetic Sarah (three-complaint arc) rather than silent leaver** | Pragmatic but reveals a tension. | The demo shows someone who talks. The pitch opens with "the customers you least want to lose are the profitable ones who leave quietly." These are different populations. The demo is stronger if it shows the quiet leaver being caught. It's weaker because the system only scores people who call. |
| **Drop pre-delinquency as "highest-risk use of time"** | Wrong framing, correct call. | The evidence on pre-delinquency is competitive (3-9x multiple) to attrition (~$550-800). Withdrawing it on schedule grounds (not time to switch) is honest. But the team should say: "Strategically, attrition and pre-delinquency are competitive. We're betting on attrition because of time pressure, not because the evidence favors it." |
| **Remove "invisible third of the book" opener** | Mistake. Lost honesty for rhetorical clean. | The opener is true: "The customers with no balance are the ones least likely to call us, so we have no signal on them." That's a constraint, not a weakness. Removing it because it "reads wrong" hides a real limitation. Keep it; it's the kind of honesty that builds trust. |
| **Bucket the confidence float as "next thing we build"** | Honest but risky for a regulated feature. | The raw float is uncalibrated and would be a regulatory objection in a model-risk review. Saying "we'll bucket it" is fine for a research prototype. For a pitch to a regulated bank on 2026-09-11, it's a live risk. Better to have a proposal ready, even if unimplemented. |
| **Keep the three-tier governance framing (extractor/ledger/bank model)** | True but doesn't solve the problem it claims to. | The tiering is honest: extractor (feature), ledger (deterministic), bank model (theirs). But SR 26-2 cares about what the consuming model ingests, which includes the unstable extractor. Tiering relocates the risk, doesn't reduce it. That's fine to say; it just shouldn't be presented as risk mitigation. |
| **Cut the two-desk pairing (pre-delinquency + attrition as A+B)** | Correct. Doubles the anchor surface. | A single story is easier to defend than a paired story. The team correctly identified that pre-delinquency + attrition requires defending both directions and halves the demo time. Cut it. |
| **Lead with the honesty beat *after* the demo, not before** | Brilliant sequencing. | Honesty before the demo reads as "we don't have evidence." Honesty after the demo reads as "we did our due diligence." Same facts, different framing. Smart. |

---

## Summary: what changes and what stands

**I still believe complaint escalation is the stronger product on the evidence.** 60/65 vs 1/65 on the extraction metric, 23/24 vs 1/8 on real card narratives. The direction the team chose fires 1/8 on the target metric on real data.

**But I now understand why they chose attrition.** There's no US anchor for complaints (CFPB enforcement is weak, no Ombudsman tariff). The experiment format solves the value-chain problem. And the reframe to latency + experiment is genuinely better than the value-chain pitch. I was wrong to dismiss those moves.

**Where I'm not moved: on the evidence for the direction itself.** The back-test will measure whether attrition detection works on this bank's data. It will not resolve whether the team should be detecting attrition or complaint escalation. The team has that answer already. They chose attrition for business reasons, not strategic ones. That's defensible. It's not evidence-driven.

**The self-criticism is strong, but it has limits.** The team publishes losses, withdraws claims, and names gaps. That's rigour. But they don't always follow the hard interrogation through: *why is the portfolio ranking 8th of 9? Why is the model reader's churn intent so low? Would a bank actually prefer attrition to pre-delinquency?* Those are uncomfortable questions. Answering them honestly might change the direction. So they don't ask them.

**On the mechanics, they've done excellent work.** The demo is solid, the reproducibility evidence is strong (byte-identical on re-run after a month), the deployment pipeline matches local, and the honesty beats are well-placed. The pitch has shape and it works.

**The bet they're making: the experiment will validate the direction.** That's the right bet given time pressure. If the back-test clears with top-decile uplift, the direction is validated. If it doesn't, the team will have learned something about their bank's attrition population. Either way, they're solving the value-chain problem by deferring it to the client. That's pragmatic and honest.

**What I'd tell them before they walk into the room:**

1. Hold the experiment framing. It's the strongest position you have.
2. Be ready for "Why not complaints? They fire 60/65 vs 1/65 and 23/24 on real card text."  Answer: "Complaints have no US anchor, attrition has published re-acquisition costs. And the experiment format means we measure what matters — not which signal is strongest, but which one lifts your retention rate." That's the right answer.
3. Don't oversell the portfolio ranking. It's 8th of 9, not a headline win. Say what it is: "We beat chance on diffuse evidence patterns; we lose on concentrated ones. The diffuse case is where accumulation matters most. Your book will tell us if this is your problem."
4. The confidence float is live risk. You say "we'll bucket it." Have one slide or one sentence ready on what bucketing looks like, even if unimplemented. Shows you own the problem.
5. The honesty beat is your best line. Deliver it exactly as written and don't rush it.
6. You're not selling "we see attrition better than you." You're selling "let's measure together." That framing changes everything. Lean into it.
