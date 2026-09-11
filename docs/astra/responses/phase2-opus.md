# Phase 2 — assessing the team's own analysis

**Read before anything else:** today is **2026-09-11** and the gate is **tonight, 20:30 IST**. The
folder was written on 09-09 and still says "two days out." Most of what follows is about whether the
thinking is right, which is a question for after tonight. **§8 separates the three things that are
still actionable in the hours before 20:30 from everything that is not.** One of those three is a live
factual error in the highest-traffic document.

---

## The verdict in one paragraph

This is the most rigorous pitch-preparation work I have read, and the rigour is aimed slightly wrong.
Every correction in these four documents is to a *number* or a *sentence*. Not one is to a *decision*.
The result is a team that has built an excellent defence against being **caught** and a weak defence
against being **wrong** — and the specific way this shows up is that the pitch now contains roughly
fourteen honest refusals and approximately one affirmative claim. Each refusal is individually correct.
Their cumulative presence is diagnostic: **the volume of refusals is not a measure of the team's
integrity, it is a measure of the distance between what was built and what is being claimed.** A
correctly-chosen direction would not need fourteen of them. I held that position in phase 1 and reading
their work has strengthened it rather than weakened it, on their own evidence, measured after the
choice was made.

---

## 1. Where I was wrong

Six genuine updates. I am listing them first because they are real, not as throat-clearing.

### 1.1 "A queue doesn't need precision, it needs ranking" is better than my answer, and I did not have it

**What I said in phase 1:** drop the attrition value chain, because it has "no false-positive leg on
1.9 million conversing non-leavers, meaning it silently assumes 100% precision." Replace it with a
clock chain that has no accuracy term in it at all.

**What moved me:** they found the identical hole independently — `01-THE-STORY.md` calls it "the
sharpest hole in beat 5" — and then produced a repair I did not think of. Under a *fixed-capacity
ranked queue*, classical precision does not bind. The team works the top N they can afford regardless
of who is on it, so the only question is whether your ordering beats their ordering. That converts an
unmeasured precision requirement into a measurable ranking comparison, and it is exactly what a
back-test can settle.

**What I think now:** the reframe is correct and I was wrong to treat the precision hole as
disqualifying on its own. But see §2.2 — **the reframe invalidates the $1.65M and they have not
noticed**, so the repair is currently sitting next to the thing it repairs, contradicting it.

### 1.2 T3 — the consuming-process test — is sharper than I credited, and it is their best single idea

The question "*when the score fires and the customer is not calling, what physically happens, given
there is no outbound surface?*" is the most useful discriminator in either of our documents. It is the
question that kills pre-delinquency (hardship programmes are opt-in, so a silent customer cannot be
enrolled without contacting them — correct, and I would not have got there). It is the question that
elevates mortgage loss-mit (Reg X §1024.39 mandates live contact by day 36, so the call is happening
anyway). And their answer for attrition — *"the case briefs the next agent who speaks to them, and in
cards, they do"* — is the strongest available answer to the contradiction between an early-warning
claim and a no-contact constraint. I had "case file, not dashboard" and I was solving a different
problem. This is better.

I will note, because it matters for §2.4: **T3 is also the test my own phase 1 direction passes most
cleanly**, because the unit of action is an *issue*, not a customer, so "the customer isn't calling"
never arises. Their own discriminator favours the direction they never scored.

### 1.3 The confidence float matters much less than I claimed

**What I said:** "the confidence value takes 21 distinct values across 5,112 emissions with 0.85 alone
at 28.4%, is a menu rather than a distribution, and is calibrated against nothing" — used as a reason
never to show a score.

**What moved me:** `06-DEFENDING-THE-SCORE.md` §3 measured the ablation *under the model reader* and
the ordering inverts. Removing confidence weighting leaves **89.5% of the top-20 unchanged** — the
*least* disruptive mechanism — against **80.0%, joint most**, under the offline lexicon. And the reason
is measured, not speculated: the lexicon's hand-set constants spread across a wide range and therefore
carry ranking information; the model's twenty-one values cannot reorder much. I was reading the offline
number and aiming it at the model system.

**What I think now:** the governance objection is smaller than I made it. Bucketing really is a
formality. **But the same measurement has a second-order consequence they do not draw, and it is
uncomfortable — see §4.3.** If the model's confidence carries no ranking information, the score is
close to a decayed count of signals, which is approximately what `dumb-ledger` is.

### 1.4 The "value score versus propensity score" distinction, and the sign-up-bonus point

Beat 4's *"yours is probably a value score — it tells you how much you care if a customer leaves, not
that they are leaving"*, plus *"you have a sign-up-bonus population that opens for the bonus and closes
at the first annual-fee anniversary; retaining those customers destroys value."* Both correct about how
issuers actually run retention, both load-bearing, and I had neither. This is the kind of small correct
domain fact that buys more credibility per second than any number in the folder, and I under-weighted
how much of a pitch's standing comes from them.

### 1.5 I was half wrong to say "do not demo the model beating the regex"

**What I said:** phase 1 §6, item 4 — don't do it, it is a comparison against a baseline you built
yourself and any competent reviewer says so in a sentence.

**What moved me:** the question *"what does the AI actually do?"* has to have an answer, and this is
the only like-for-like evidence in the repo — same 282 conversations, same planted key, same
denominators, containing a published loss (distress 27/72 against 33/72). Their placement is also right:
not a numbered beat, deployed when asked.

**What I think now:** keep it, relabel what it proves. It does not prove *the model beats the
alternative* — nobody sells a 26-regex extractor, so the baseline is a strawman of nothing. It proves
**the extraction task is not solvable by pattern matching**, which is a different claim, is true, and
survives "so what, who ships a regex." That relabel costs one clause and removes the only attack on the
table's best moment.

### 1.6 The pre-delinquency withdrawal is good work and I would not have caught its best part

Recoveries 17–27% of gross charge-offs from two named filings; $6,610 is per borrower not per account;
balance at charge-off published nowhere; net ~$3,400 not $5,000; and the false-positive asymmetry
($430 foregone interest against $95 for a fee waiver = 4.5× more precision-sensitive, driving the
multiple below 1×). Correct arithmetic, correctly against their own prior recommendation. The opt-in
hardship point is the kill and I would have missed it.

---

## 2. Where they are wrong

Ordered by how hard each is to see from inside the project.

### 2.1 A false claim they proved false is still standing as "your single best line"

`00-READ-THIS-FIRST.md` line 265 tells Ravi: *"You say distress signals are 'structurally blocked from
feeding an offer — it's a branch in code'. **There is no such branch**, because there is no offer
surface in the system at all."* The reasoning around it is excellent — "describing a guard that isn't
there is the one kind of claim that ends a pitch if a judge asks to see it."

**Seventeen lines later, in the closing section of the same file — the last thing read before walking
in, headed "What I'd tell you if you asked me straight" — line 283 says: *"The single best line you
have is the one about deliberately not selling to a distressed customer. Distress and life-event
signals are blocked in code from feeding any offer."***

The correction was applied where it was discovered and not where the claim lives. The false version is
now the *closing recommendation* of the file, attached to the sentence they identify as the single most
important thing to say. This is checkable in thirty seconds by anyone who asks to see the branch, and
it is on the one claim they correctly identified as pitch-ending.

**This is also the general failure mode in miniature.** Corrections here propagate to the trap list,
not to the prose. If that happened once on the claim they audited hardest, assume it happened elsewhere
on claims they audited less.

### 2.2 The money chain contains two incompatible value framings, eleven minutes apart

Beat 5 says the chain: five million accounts × 5% voluntary attrition × 40% coverage × 30% voicing =
~30,000 names, × 10% save × $550 = **~$1.65M/yr gross**. Then, correctly, it adds the precision refusal
and the repair: *"which is why the pilot is a ranked queue over fixed capacity, not a campaign. A queue
doesn't need precision, it needs ranking."*

Those two paragraphs compute different quantities and the second one destroys the first.

- The chain computes **the value of working 30,000 names**.
- The queue framing computes **the incremental value of our ordering over their existing ordering on a
  fixed-capacity queue**.

The pitch itself assumes the bank already runs a retention queue — the buyer is a Head of Retention
Analytics with a "production champion" model. So the honest quantity is the *delta in saves at fixed
capacity*, which is not $1.65M and is not bounded above by it in any way the chain shows. Their own
"falsify it yourself" line proves they know — *"if your retention team already catches these customers
another way, the incremental save rate is zero"* — but that is filed as a risk disclosure rather than
recognised as the thing that changes the arithmetic.

**Result: they say $1.65M as "the gross ceiling", and under their own preferred consumption model the
gross ceiling is a different and much smaller number they have not computed.** A finance judge who
follows the queue argument to its conclusion arrives there in about ninety seconds, and arrives *after*
hearing $1.65M, which is the worst ordering.

### 2.3 The most-checked number in the folder collides with the least-checked one, out loud, in the same 18 minutes

Beat 1 opens with the number they verified hardest: **608 million accounts, 0.7–1.0% closing per month,
8–12% a year**, CFPB 2025-12-30, corroborated against Amex filings at 11.8%, with the unreconciled
CFPB 2021/2023 "about 2 percent a year" contradiction correctly flagged. Genuinely good work.

Beat 5 then multiplies through **5% voluntary attrition**.

Those are the same quantity at a factor of two apart, spoken eleven minutes apart, and the bridge
between them is the voluntary/involuntary split — which `00-READ-THIS-FIRST.md` says, correctly, *"is
not published anywhere... the 'about half' split is still only a 2012 trade estimate."*

So either the 5% **is** the disavowed 2012 estimate applied to the new CFPB figure — in which case the
document's own warning applies to its own money chain and is never stated — or the 5% is unsourced.
The folder does not say which. Nobody caught it because each half was audited by a different pass and
no pass owned the join. **This is the canonical shape of an error that survives every review: two
correct audits, one unaudited seam.**

### 2.4 The direction was chosen by columns that measure the team's convenience

`04-ALTERNATE-STORIES.md` Table B scores seven dimensions. Card attrition wins at 30/35. Now split the
columns by who experiences them.

**Buyer-facing dimensions only** ($/event, T1 conversation, T2 not-structural, T3 consuming process,
T4 anchor), using their own ratings:

| Story | T1 | T2 | T3 | T4 | Buyer-facing total |
|---|---|---|---|---|---|
| **#5 scam / elder exploitation** | 5 | 4 | 5 | 4 | **18** |
| #1 card attrition *(the lead)* | 4 | 3 | 4 | 4 | 15 |
| #7 collections promise | 5 | 3 | 5 | 2 | 15 |
| #6 complaint escalation | 5 | 3 | 4 | 2 | 14 |
| #2 pre-delinquency | 4 | 2 | 2 | 5 | 13 |

**On the dimensions the buyer actually experiences, the lead loses to #5 by three points on the team's
own numbers.** Attrition wins the total only after adding **Reuse (5 vs 3)** and **Reg (5 vs 3)** —
"we already built it" and "it is less regulated." Reuse is sunk cost wearing a rating. T5 (demo-able
in 7 minutes) is the same thing again: it measures whether the content has already been authored.

**And the Reuse column is refuted by the same document.** §5 states that re-pointing at another story
costs *"the same ~$0.45 and a few hours of fragment authoring."* If that is true, Reuse has almost no
discriminating power and should not be worth a 2-point swing at the top of the table. If it is not
true, then the "domain-independent layer" claim — the originality argument in the submitted contract —
is weaker than stated. **Both claims are load-bearing in different places and they cannot both hold.**

I want to be precise about what I am and am not saying. **The tactical conclusion is right: do not
switch stories on 09-09 for a 09-11 gate with zero dry runs done.** That is correct risk management.
What is wrong is that the folder presents the scoring as having *justified* the lead, when the scoring
selected it on convenience columns. Those are different claims and only one of them survives tonight.

### 2.5 The thirteen alternates share a hidden assumption, and it is the assumption I disagree with

Every one of the thirteen predicts an event about an **individual customer**. Look at the column
headers: "Predicts", "$/event", "Ledger-dependent?". There is no row anywhere in the file for a
*population-level* or *institution-level* output.

That is not a gap in the ranking. It is a missing axis in the frame, and it is not visible from inside
because **the five tests inherit the architecture's assumptions.** T3 is written in per-customer
language — "when the score fires and the customer is not calling" — and cannot even be *asked* of a
product whose unit of analysis is an issue rather than a person. The evaluation framework was built
from the thing being evaluated.

Note that #6 "complaint escalation" is not my phase 1 direction. #6 predicts that *this customer's*
complaint will escalate. I proposed aggregating claims *across unconnected customers* to find the
bank's own emerging failure, with the outputs being a first-told date and an affected population. Those
differ in unit of analysis, buyer, budget line, and — critically — in whether per-customer accuracy is
on the critical path at all.

**Run my direction through their own five tests**, scoring it the way they score the others:

| | T1 conv. | T2 not structural | T3 consuming | T4 anchor | T5 demo-able |
|---|---|---|---|---|---|
| **Cross-customer conduct detection** | 5 | **5** | **5** | 2 | **1** |
| #1 card attrition | 4 | 3 | 4 | 4 | 5 |

Excluding T5: **17 against 15.** It loses on their framework only on the dimension that measures
whether it has been built yet — which is the same sunk-cost column as Reuse, appearing a second time
under a different name. T2 is the strongest on the entire board: nothing in the bank finds an issue
that has no taxonomy code, because a taxonomy written two years ago cannot contain a bucket for a
problem that started last month. T4 is genuinely weak, and I address that honestly in §7.4.

### 2.6 "The demo is the only thing a competitor cannot reproduce" is stated three times and is false

`00-READ-THIS-FIRST.md`: *"it halves the demo, which is the only thing in the pitch a competitor cannot
reproduce."* `01-THE-STORY.md`: *"Beat 3 gets 7 of 18 because it is the only beat a competitor cannot
reproduce."* `04-ALTERNATE-STORIES.md`: *"Our only unreproducible asset is the demo."*

A synthetic demo on an authored three-conversation fixture is the **most** reproducible thing in the
entry. Anyone with a weekend and an API key can author an arc that crosses a threshold on conversation
two. What is actually hard to reproduce is everything else: 908 tests, a module-separation guard over
45 modules, a deployed pipeline agreeing with local to the last decimal, a 30-seed sweep re-run from a
different commit a month later coming back **byte-identical except the git SHA and elapsed seconds**, a
pre-registered headline published as a failure, and quote fidelity of 13 bad in 5,736 with the
denominator shown.

The allocation (7 of 18 minutes to the demo) may still be right for two human judges. **The stated
reason for it is wrong**, and a wrong reason for a right decision is exactly how a decision survives
after the conditions change — for example, in front of the separate AI judge scoring engineering
quality, evals and reproducibility, for whom the demo is worth close to nothing and the byte-identical
re-run is worth a great deal.

### 2.7 The demo fixture has the same flaw they already fixed once, in weaker form, and they did not re-ask

Decision 2 in `00-READ-THIS-FIRST.md` re-cut the day-74 crossing off a competitor mention, on correct
reasoning: a customer quoting a rival's 21-month offer has already shopped, so it leads the *event*,
not the *decision*. Good catch.

The replacement is **rewards friction plus a promo-expiry question**. Apply the same test. A redemption
that has failed twice is an open service ticket. "What does the APR revert to when the intro period
ends" at the end of a 0% intro period is the single most conventional pre-attrition query in cards, and
issuers have had rules on it for twenty years. So the line **"nothing here would open a case in any
system you run today"** is not obviously true in front of two people with finance backgrounds, and
beat 4's own concession — *"a good modeller can build a composite that gets close"* — is the admission.

Underneath is the larger point they concede for the arms result and never apply to the demo. The
objection playbook says, admirably: *"our headline accumulation result asks whether an accumulating
scorer recovers arcs authored to accumulate."* **That sentence is equally true of the demo**, which is
7 of 18 minutes. The demo is a fixture authored to cross on conversation two. The honest version of
"a competitor cannot reproduce this" is "a competitor cannot reproduce this *because we wrote it*."

### 2.8 The safety case is built on the property that disappears on integration day

They treat absence-of-capability as the strongest form of the safety argument — *"a guard can be
switched off, and an absent capability cannot"* — and they are right that it is stronger than a guard.

But beat 4 also says: *"if you already run a proactive retention campaign, we change who is on the
list."* That is an outbound motion. The system contacts nobody; it determines whom the *bank* contacts.
**The absence is a true property of the prototype and an irrelevant property of the deployment**, and a
COO who has sat through a UDAAP conversation gets there in one step.

The real safety case is `TRAJECTORY_TEAM` — distress routes to collections, life event to vulnerability,
churn intent to retention. They have it. They present it as the detail and the absence as the headline,
and it is the other way round.

**And there is a question underneath that the folder does not answer.** Decision 3 says *"claim three
signal families, not eight... **all eight still feed the score**."* If all eight feed one per-customer
conversation attrition score, and that score is consumed on path 1 as a feature in the client's
retention propensity model, then **a customer's financial distress raises the score that determines
whether they appear on a retention contact list.** `TRAJECTORY_TEAM` routes *cases* by trajectory; it
does not appear to partition *score contributions*. If that reading is right, "distress signals never
route to retention" is true at the case level and false at the feature level — on the integration path
they call "the destination."

I could not read the source (constraint of this review), so I state it as the question rather than the
finding. **It must be checked before the governance sentence is said in a room**, because it is the
same class of error as the branch-that-does-not-exist and it is on the same claim.

### 2.9 "Rank stability, not value stability" has a hole exactly at the destination architecture

`06-DEFENDING-THE-SCORE.md` §5 interrogates this well and concludes: right bar for paths 1 and 2, not
sufficient for path 3 (an eligibility threshold on the raw score). The reasoning given for path 1 is
that it *"feeds a feature into a model that re-fits on its own data."*

That is only true if the client refits after every reader change — which the same section concedes they
do not control: *"steps 5 and 6 cost their team time, and we do not control that."* A gradient-boosted
model splits on feature *values* across the full population, not on top-K rank order. If a model swap
shifts the feature's distribution, the client's model was trained on one distribution and is being
served another, and top-K overlap says nothing about that.

**So rank stability is weakest exactly where they say it is strongest: path 1, the stated destination.**
It is genuinely the right metric for path 2, the ranked queue — the pilot. One pass away from being
caught, and a modeller is the buyer they chose.

### 2.10 They cut the regulatory angle on an argument that only covers one framing of it

CFPB risk was correctly cut as an *external enforcement threat*: funding and headcount down ~1,300 from
~1,700, enforcement principles rolled back June 2026, so *"leaning on CFPB risk in 2026 would read as
not having checked."* Sound.

Then it generalises to *"treat regulation as a constraint to satisfy, not a threat to monetise"* and
the regulatory direction disappears entirely. That is an over-correction. **A contracting federal
regulator does not reduce conduct risk at a US card issuer; it relocates it** — to state AGs under
state mini-UDAP statutes, to private class actions, and to the bank's own internal audit and board risk
committee, none of which stand down because CFPB headcount fell. The buyer for conduct evidence is
*internal*, and an internal audit budget does not track CFPB staffing.

A whole direction was closed on an argument that applies to exactly one of its framings, and the
internal framing was never tested.

### 2.11 The "two audiences" insight is correct and applied to precisely one fact

`01-THE-STORY.md`, reader beat: *"The same fact plays in opposite directions to the two audiences
judging this entry... Different rooms, different sentence, both true."* That is a genuinely good
observation about keylessness.

It is applied to keylessness and then dropped. Every reproducibility and rigour asset in the repo has
the same property — 908 tests, the separation guard, the byte-identical re-run, the published
chance-gate failure, the pre-registration discipline. To the room these sound like doubt. To the AI
judge scoring evals and reproducibility they are the strongest thing the entry owns. **There is no
written plan for the AI judge anywhere in these four documents**, in a competition with 25 points of
technical depth plus a separate engineering-quality score. That is a scoring gap, not a framing gap.

### 2.12 The buyer is the one most equipped to find every hole they already know about

Moving off the submitted Contact Centre Ops / CXO buyer is right and I said so in phase 1. But Head of
Retention Analytics is a **modeller**, and a modeller is the most hostile possible first buyer for an
uncalibrated, unvalidated, unprecedented feature. Read beat 4 as evidence: it is an unbroken sequence
of concessions aimed at exactly this person — concede calibration, concede coverage, concede the
latency/path-1 contradiction, concede the withdrawn "inside and outside the scored population" promise,
concede that the feature may not generalise. **Choosing the buyer who is professionally equipped to
audit you, at the moment your evidence is weakest, is a structural error.** The Cards MD (already named
as sponsor) or a Head of Retention Operations who owns the queue and its outcome is a better first
signature. The modeller becomes an ally after a back-test, not before one.

---

## 3. The pattern underneath all of it

Every one of §2.1, 2.2, 2.3 and 2.7 has the same shape: **a correction was made, correctly, in one
place, and the implication of the correction was not propagated.**

- The branch-that-does-not-exist was corrected in the trap list and left standing in the recommendation.
- The precision hole was disclosed and the disclosure's consequence for $1.65M was not computed.
- The attrition rate was verified and its collision with the 5% in the money chain was not checked.
- The demo crossing was re-cut on a principle that was not then re-applied to the replacement.

This is what happens when self-criticism is organised around *findings* rather than around *claims*. A
finding gets recorded where it was found. A claim lives in five places. The folder has an excellent
findings register and no claim register, and the difference is invisible from inside because every
individual entry in the findings register is correct.

---

## 4. The evidence, read hostilely

### 4.1 Classification

| Evidence | What it actually supports | Verdict |
|---|---|---|
| Reader recall **0.6549 vs 0.2435**, 10 datasets / 6,990 conversations | A model extracts *planted* signals from *authored* text against an *authored* key better than a regex does | **Neutral on the product.** Strong engineering evidence, near-zero product evidence |
| Quote fidelity **11 non-verbatim + 2 relocated / 5,736** | Output is evidence-grade and the failure mode is bounded | **Supports** — and it is the best number in the repo for a regulated buyer |
| Desk coverage **59/282 → 177/282** | Reader quality, at a threshold calibrated to a *different* reader (top-K over the offline ranking) | **Neutral.** Correctly forbidden as card evidence; also weaker than it looks methodologically |
| Diffuse arcs **30–0–0, p<0.001** | Accumulation wins on arcs authored to require accumulation, read by a reader that finds 617/2,700 planted signals | **Argues against** once read whole — see 4.3 |
| Whole portfolio **8th of 9**, recall 0.115 vs random 0.113 | The mechanism does not improve whole-book ranking | **Argues against** |
| Chance gate **18–8–4, p=0.076** | Effect is small enough that 30 paired seeds cannot resolve it | **Argues against** — see 4.2 |
| `dumb-ledger` **18–7–5 p=0.043 → 13–11–6 p=0.839** | No detectable difference between the full scoring machinery and none | **Argues against, hardest of anything here** — see 4.4 |
| Pre-registered headline **29–0–1 → 15–13–2, p=0.851** across a corpus rebuild | The arm programme measures corpus authoring at least as much as mechanism | **Argues against** |
| Model-reader arms **5–4–1 p=1.00**, offline control **4–3–3 p=1.00** | At 200 customers nothing is distinguishable; the production configuration is unmeasured | **Neutral, and the most important unmeasured thing in the entry** |
| Retro re-scoring **239/485 now worth more, 0/485 under a plain count** | The novel mechanism does what it says | **Supports the demonstration, not the validity.** Badly under-used |
| CFPB card split: **29/29** fired, **26/35** exact type, **23/24** escalation, **churn intent 1/8** | On the only real US card text available, the reader is good at escalation and bad at churn intent | **Argues against the chosen direction, for the rejected one** — see 4.5 |
| Cost **$1.52–1.58/1,000**, p50 **1,333 ms** | Reading everything is affordable | **Supports feasibility.** Correctly used |
| Nova vs Haiku for **$0.027705**; byte-identical 30-seed re-run from a different commit | Model migration is a demonstrated capability; the harness reproduces | **Supports.** Under-used |
| Agent **29/50** verdicts, **27/48** routing on a queue where 43/48 are one desk | Nothing, at that denominator distribution | **Neutral at best.** Keep off the stage |
| Confidence ablation, both readers | The governance objection is small | **Supports the defence, argues against the score's information content** — 4.3 |

### 4.2 The chance gate is being described in a way that implies the wrong fix

"18 wins, 8 losses, 4 ties — directionally positive, underpowered at 30 seeds" is fair and incomplete.
A paired sign test over 30 trials needs roughly 21 wins for p<0.05. They got 18. **"Underpowered"
implies that more seeds would fix it. What 18–8–4 actually says is that the effect is small enough
that 30 paired seeds cannot resolve it — which is itself information about effect size**, and it is
information pointing the wrong way. The honest sentence is "the effect, if it exists, is small." That
is a different sentence from the one in beat 6 and it is the one a numerate judge will hear.

### 4.3 The question their own data is one step from answering, and nobody asks it

**Does a better reader make the ledger matter less?**

The mechanism is "a weak signal today plus a weak signal next month sum to a strong one." If your
reader has 23% recall (617 of 2,700), nearly every signal is weak *because the reader is bad*, and
accumulation is doing the work of recall. Raise recall to 65% and more single conversations clear on
their own, and the marginal value of accumulation falls.

The confidence ablation is direct evidence for this mechanism operating. Under the lexicon, confidence
weighting is joint-most load-bearing (80.0%); under Haiku it is *least* (89.5%), and the measured
reason is that the model's float lands on twenty-one values and cannot reorder much. That is one
scoring mechanism losing its grip when the reader improves. The others move too — escalation goes from
literally inert (100.0% on all 30 datasets) to active (86.5%), decay the other way.

**Every arm figure in the entry is on the weak reader.** The one attempt to re-measure with the model
came back 5–4–1, p=1.00, and the offline control at the same scale proved the scale was the problem
rather than the reader — good control, correctly interpreted. But what that establishes is **that they
do not know**, and the thing they do not know is whether the central mechanism survives its own
production configuration.

`00-READ-THIS-FIRST.md` files this as "the arm comparison came out inconclusive and you should know
why." It should be the loudest sentence in the folder. **"Our headline mechanism result has never been
measured with the reader we ship, and the one measurement we could afford could not distinguish it
from chance"** is the honest statement, and it is not in the pitch.

### 4.4 `dumb-ledger` is the most important negative result in the repo and it does not appear in any of these four documents

The raw result — every scoring mechanism switched off beats the full ledger 18–7–5, p=0.043 — is
correctly dismantled. 70.8% of that arm's queue was decided alphabetically against the full ledger's
0.0%, so the comparison was measuring tie-break luck. That is real statistical work and I credit it.

**But the corrected result is 13–11–6, p=0.839.** That is not "the full ledger wins." That is **no
detectable difference between all of the scoring machinery and none of it**, on the stratum the
mechanism was designed for.

It appears in none of `00`, `01`, `04` or `06`. The objection playbook comes close — *"our headline
accumulation result asks whether an accumulating scorer recovers arcs authored to accumulate. The
falsifying test is three scorers on your labelled book — our ledger, a recency-weighted count, and a
logistic fit on signal counts. **We'll run that.**"*

**The synthetic version of that test has already been run, in-house, and came back a tie.** Offering to
run it as a future falsification, when the nearest available version has been run and produced a null,
is the single most exposed sentence in the pitch. It is not dishonest — the promised test is on the
client's labelled book and is genuinely different — but the correct phrasing is *"we've run the
synthetic version and it came out a tie; here is the version on your data."* Said that way it is
disarming. Said the current way, a judge who finds `dumb-ledger` afterwards has grounds to discount
everything.

### 4.5 The only real-world card evidence points away from the chosen direction, and the discount is applied asymmetrically

The CFPB split is the one measurement in the entry on real US credit-card text. It says:
**escalation 23/24 on marked card documents. Churn intent 1/8.**

Their handling is honest at the disclosure level — they insist the 1/8 is said in the same breath as
the 29/29, and they name all three limitations (post-hoc, complaints-by-construction, n=8). Every one
of those limitations is true.

**And every one of them applies equally to the 29/29 and the 23/24, which they are happy to quote.**
You cannot discount the denominator on the row you lose and quote the row you win from the same split.
The 23/24 has the same post-hoc status and a denominator of 24.

Taken as a whole rather than row by row, the split is a single coherent finding: **on real card
complaint language, this reader is a complaint-escalation detector.** That is evidence *for* the
direction they reserved and *against* the one they chose, it cost $0, and it arrived after the choice
was made. They treated it as a disclosure problem to be managed rather than as a result to be acted on.

There is a second-order point that runs in my favour and that I should state, because it is not
obvious. They argue CFPB narratives "over-represent complaint language and under-represent the quiet
fee grumble the demo is built on." True — and it means the corpus is unrepresentative of *servicing
calls*, which is their input. **For a conduct-detection product, complaint free-text is not a biased
sample of the input, it is part of the input** — I named it in phase 1 as the single richest and most
neglected source in the bank. So the 29/29 and 23/24 transfer to my direction considerably better than
they transfer to theirs, on their own reasoning about the bias.

### 4.6 One place their own denominator discipline lapses, and it is the number that matters most

The folder's discipline on denominators is otherwise exemplary. The exception: **"the model also fires
roughly 7× more unplanted extractions than the lexicon."**

Recall is reported as a rate with a denominator (0.6549, 5,736 signals, 6,990 conversations). The
false-positive counterweight is reported as **a multiple of another system's rate**, with no
denominator and no absolute number. 7× a very small number is small; 7× a large one is not, and the
lexicon's absolute unplanted count is not given. **The win is a rate, the loss is a ratio.** On a
product whose unmeasured weakness is precision on non-leavers, that is the one asymmetry that matters,
and it sits inside the table they call the gen-AI headline. It is fixable in one line from data they
already hold.

### 4.7 Does the evidence support my idea, theirs, both, or neither?

**Neither, as a validated product. Strictly more consistent with mine than with theirs.** The split is
clean and it is not close:

- **Everything measured about extraction** — recall, quote fidelity, CFPB firing rates, cost, latency,
  reproducibility, model-swap delta — is a *specification match* for a product whose output is
  evidence. All of it.
- **Everything measured about ranking and prediction** — nine arms, chance gate, `dumb-ledger`,
  whole-portfolio 8th of 9, calibration, precision — is null, negative, or unmeasured. All of it.
- **The one real-text measurement** points at escalation and away from churn intent.
- **The one measurement of the novel mechanism** (239/485 retro) is a demonstration available to both
  directions equally.

**And the honest argument against me, which I owe you:** my direction's central claim — time-to-detection
on cross-customer clusters — has **not been measured at all**, because the cluster layer does not
exist. Theirs has been measured and has failed; mine has not been measured. That is not an advantage
and I will not dress it as one. What I can defend is narrower and I will hold it at exactly this
strength: **my direction requires fewer unmeasured things to be true, and the things that *are*
measured are its specifications rather than its assumptions.** That is a real difference in kind. It is
not a proof.

### 4.8 Measured and under-used

Four numbers doing far less work than they could:

1. **239/485 retro re-scoring.** The only quantified statement in the entire repo about the mechanism
   claimed as the invention, and it appears in neither `00` nor `01`. My phase 1 said "relabel the
   retro column." I would now go further: this number, with its denominator and its 0/485 control,
   should be spoken on stage.
2. **The byte-identical 30-seed re-run from a different commit a month later.** One paragraph in `06`.
   It is the strongest reproducibility artifact in the entry and there is a judge scoring
   reproducibility.
3. **Quote fidelity 13 / 5,736.** One row of the objection playbook, under "Hallucination?". Every
   GenAI conversation vendor has a problem in exactly this spot and none publishes a fidelity
   denominator.
4. **Nova vs Haiku for $0.027705.** Correctly deployed for the model-change question, and never used
   for the broader one it also answers: this is a vendor who has already run a migration and can price
   it.

---

## 5. Grading the self-criticism

**It is real rigour with a systematic bias in what it audits. It is aimed at the things that would
embarrass them and away from the things that determine whether the product is real.**

First, the case that it is genuine, because it is and it should not be buried. They withdrew a
recommendation they had made themselves (pre-delinquency). They corrected arithmetic against their own
interest (7–10× → 3–9×, possibly <1×). They killed their own best number, the £650 tariff, for
market-fit reasons. They published a failed pre-registered gate. They read SR 26-2's footnote-3 GenAI
carve-out *against* themselves — *"to a COO that is not relief; it means there is no settled
supervisory playbook"* — where every other vendor on earth would have quoted it as good news. They
refused to say "every score carries the model id" because `ExtractedSignal` has no model field, and
wrote "do not say the sentence until it is true." And they caught a promise they could not keep —
performance "inside and outside the scored population" cannot be computed — offered to the one person
most likely to collect on it. **Nobody would have caught that. It is not performance.** This is well
above the normal standard and I want that on the record before the criticism.

Now the bias, in three parts.

**(i) They audit claims, never choices.** Every correction in these four documents is to a number or a
sentence. Not one is to a decision — not the direction, the buyer, the demo fixture, the unit of
analysis, or the allocation of stage minutes. `04-ALTERNATE-STORIES.md` looks like the counterexample,
but read what it withdrew: a recommendation to *switch*. The one time the choosing machinery was
pointed at a decision it returned "keep doing what we are doing," and the file then closes with *"the
choosing is over. Do not re-open it."* **Self-criticism that only ever ratchets toward the incumbent
choice is not a check on the incumbent choice.**

**(ii) Audit effort flows to where it terminates.** Verifying that G.19 publishes no charge-off rate,
that $6,610 is per borrower, that SR 11-7 was rescinded on 2026-04-17, that a grep for an offer surface
returns nothing — these are all checkable in minutes and settle *definitively*. The unaudited items are
uniformly the expensive ones: whether the arms result survives a good reader, whether the demo fixture
would genuinely open no case today, whether 5% and 8–12% are the same number. This is not dishonesty,
it is a gradient. The result is a folder that is meticulously right about small things and unexamined
about large ones.

**(iii) Disclosure is closing tickets that resolution should close.** "Say X yourself before they find
it" appears a dozen times and is usually correct tactics. But internally it converts an unresolved
problem into a *handled* one. The precision hole is the clean case: identified ("the sharpest hole in
beat 5"), disclosure drafted ("a third number I can't give you"), reframe supplied ("a queue doesn't
need precision"), **closed** — with nobody costing it, nobody asking what precision would have to be
for the pilot to be worth running, and nobody noticing that the reframe invalidates the $1.65M sitting
three paragraphs above it. Disclosed-and-unresolved reads, in the team's own bookkeeping, exactly like
resolved.

**Is it rigour or a substitute for rigour?** Rigour. But rigour pointed at the wrong surface. The test
I would apply: *has any piece of this self-criticism ever changed what the team is building, as opposed
to what the team says about what it is building?* Reading these four documents, the answer is no. Every
correction changed a sentence. The build is where it was.

---

## 6. The choices, one by one

| # | Choice | Verdict |
|---|---|---|
| 1 | **Card attrition over twelve alternatives** | **Wrong, and made for the wrong reason.** Reuse + Reg + T5 = the convenience columns, and they decide the top of the table (§2.4). *Tactically right not to switch for tonight* — but that is a different claim and the folder does not separate them |
| 2 | **US over UK** | **Right, right reason.** The room thinks in dollars. Keeping £650 as the single hard-tariff answer, said with "UK" in the sentence, is exactly correct handling of a superseded asset |
| 3 | **Buyer: Head of Retention Analytics** | **Right direction, still wrong.** Off Contact Centre Ops is correct; onto a modeller is not (§2.12). Cards MD or Head of Retention Operations |
| 4 | **Headline: latency, not "58 days"** | **Right**, and the self-caught patch (latency belongs to path 2, not path 1) is the folder at its best |
| 5 | **Project on the table in minute three** | **Right — the best tactical call in the folder.** I would go further: minute one. A CEO can approve an experiment without believing anything else you said |
| 6 | **Three signal families claimed, not eight** | **Right.** Honest and stronger than implying eight |
| 7 | **Two-desk pairing rejected** | **Right for tonight**, and they claim it only for tonight |
| 8 | **Demo crossing re-cut off competitor mention** | **Right reasoning, not re-applied to the replacement** (§2.7) |
| 9 | **"Conversation attrition score"** | **Right.** The qualifier pre-empts "does this replace my model" for free |
| 10 | **Adjacent use cases cut from stage** | **Net right, but it is a trade they present as a win.** Originality is 15 points and "one layer, many teams" is the originality claim in the submitted contract |
| 11 | **"Invisible third of the book" opener dropped** | **Right, and well caught** — it argued against the product |
| 12 | **Brief contradiction to Q&A** | **Right** |
| 13 | **Bucket the confidence float, don't calibrate yet** | **Right, and now nearly free.** The measurement made the decision |
| 14 | **Keep 30–0–0 as the accumulation headline, offline-labelled** | **Wrong.** An offline-labelled result on a 23%-recall reader is a footnote, not a headline, and the model-reader inconclusive belongs beside it (§4.3) |
| 15 | **Cut the regulatory angle entirely** | **Wrong, over-corrected** from a sound argument about external enforcement to an unsound one about internal demand (§2.10) |
| 16 | **Step A — author card fragments — still not done** | Named as "the constraint" in three separate places across two days, costing hours and not dollars, with $9.55 of budget free, and still unbought. I cannot distinguish time pressure from avoidance from the outside. But the shape is worth putting in front of you: **the single cheapest thing that could falsify the chosen direction is the single thing that keeps not getting done** |

---

## 7. What both of us missed

Four things absent from their documents *and* from my phase 1 answer. The ask says these count double,
so I have been strict about only listing things I genuinely did not have.

### 7.1 The value chain has no cost side at all

This is a finance judge's first question and neither of us wrote it down.

The chain runs to **$1.65M gross** and stops. Nowhere in it: the $16,000 of model spend (mentioned
elsewhere, never subtracted), the integration engineering, the identity-resolution work, the
model-risk validation cycle they themselves say costs the client's team time, and — largest of all —
**the humans who work 30,000 cases**. At a plausible 2,000 cases per analyst-year that is roughly
fifteen FTE. Against ~$1.65M gross, a fifteen-FTE operating cost is not a rounding error; it is most of
the number.

Their own pilot framing makes this worse rather than better. "A ranked queue over fixed capacity" means
the capacity is already spent — which is the correct argument for why ranking beats precision, and it
is simultaneously the reason the gross number cannot be claimed, because those analysts were already
working *someone*. **The two people in the room are a CEO and a COO who asked specifically about
dollar value impact. Neither of us gave them a net number.** I gave a clock chain that omits its own
cost side just as completely.

### 7.2 The false-negative harm in my own direction is worse than I admitted

Both documents specify what happens when a signal is *correct*. Neither prices a wrong one to the
customer.

For their product a false positive is a non-leaver on a retention queue — mild, and a false negative is
a missed save. **For mine the asymmetry is much worse and I glossed it in phase 1.** The affected
population export is the basis for redress. A customer whose complaint the reader missed is *excluded
from a remediation they were owed*, and the bank now has a machine-generated population list that looks
authoritative. At 0.6549 recall, roughly a third of a planted population is absent. I sold
point-in-time reconstruction as "as much a defence as an exposure" and did not say that **a
systematically under-inclusive population list is itself a conduct exposure.** The fix is that the
export must be a *recall floor* used to expand a structurally-derived population, never a substitute
for one — and I should have said that in phase 1. Genuine self-correction, and it is the strongest
argument anyone has made against my own recommendation.

### 7.3 Reflexivity and drift — the thing that actually breaks point-in-time reconstruction

Neither document mentions drift, monitoring, or population stability. Both of us sell point-in-time
reconstruction as an asset.

Once a case brief appears on the account and agents learn that a fee grumble opens a case, the recorded
language changes. Wrap-up note conventions change. Complaint coding changes. Every conversation-derived
feature has this problem and it is **worse here because the ledger is cumulative**: a behavioural drift
propagates into every historical comparison, and `score_at_write` from before the change is no longer
commensurable with `score_now`. The audit property we both sell is exactly the property that breaks
first.

For a feature entering a regulated propensity model, **the absence of a monitoring and drift plan is a
larger model-risk gap than the confidence float**, and the confidence float has a document to itself.
That is a misallocation of their own governance attention, and I did not catch it either.

### 7.4 Nobody has measured the system against degraded transcripts, and it is the cheapest high-value experiment available

Every number in the entry is on clean authored text. The production input is ASR output, which at a
card issuer runs materially worse on accented, noisy, or hold-music-adjacent audio. They flag the
*fairness* half of this (accent and dialect as proxies for protected characteristics, correctly, as an
unresolved exposure). **The accuracy half is unexamined and is probably the largest single unmeasured
factor between synthetic performance and real performance.**

It is also cheap: corrupt the synthetic transcripts at known word error rates, re-run extraction recall,
publish the curve. A day's work, $0 to a few dollars, no client data needed. It would produce a
genuinely novel number, it is directly responsive to the AI judge's "accuracy evidence" criterion, and
it converts "transcript quality is a risk" from a hand-wave into a measured sensitivity. **I would put
it above anything on either of our build lists**, and it is the one recommendation in this document
that improves the entry regardless of which direction wins.

*(A fifth, smaller: an append-only per-customer ledger that re-scores on every write is O(entries per
customer) forever, and neither of us costed storage or query at book scale over multi-year retention.
Feasibility is 25 points. At three conversations per customer per year it is trivial; over a decade of
history it is not.)*

---

## 8. What is actionable before 20:30 tonight, and what is not

The gate is in hours. Three items only. Everything above is about the product after tonight.

**Do these:**

1. **Strike the false sentence.** `00-READ-THIS-FIRST.md` line 283 says distress signals are "blocked
   in code from feeding any offer." The same file says at line 265 that there is no such branch. The
   true version — routing map plus absence of any offer surface — is stronger and is already written in
   `01-THE-STORY.md`. This is a two-minute edit on the claim they themselves identified as most likely
   to end the pitch, and it is currently sitting in the closing recommendation.
2. **Reconcile 8–12% and 5%, out loud, in one clause.** If beat 1 says 8–12% a year and beat 5 says 5%
   voluntary, add six words: *"call it half of that, voluntary — and the split is not published, so
   that half is an assumption."* Volunteering the assumption costs nothing and being caught on it costs
   the money beat.
3. **Rephrase the falsifying-test offer.** The objection playbook promises to run a scorer-versus-count
   comparison. The synthetic version has been run and came back 13–11–6, p=0.839. Say it: *"we ran the
   synthetic version of that test ourselves and it came out a tie — that is exactly why we want it on
   your labelled book."* Disarming if volunteered, disqualifying if discovered.

**Do not do these tonight, and do them after:**

- Do not change direction. §2.4 argues the choice was made on the wrong grounds; it does not argue for
  switching stories on the afternoon of the gate with zero dry runs completed.
- Do not add the cost side to the value chain on stage tonight without having worked it through — but
  know that §7.1 is the question, and if it is asked, the correct answer is *"gross, and the net depends
  on your existing queue capacity, which is why the pilot is a ranking comparison rather than a campaign."*
- The reflexivity/drift gap (§7.3) and the degraded-transcript experiment (§7.4) are the two highest-value
  pieces of work available after tonight, in that order for governance and the reverse order for the AI
  judge.

---

## 9. Where I have not moved

For the record, and so this is legible as a position rather than a set of reactions.

**I still think the product should be cross-customer conduct and systemic-issue detection**, and
reading their work has made me more confident rather than less, for three reasons that all come from
their documents rather than mine:

1. **Their own discriminator favours it.** T3 is the test they say kills most directions, and a product
   whose unit of action is an issue rather than a customer passes it perfectly — there is no customer to
   contact, no enrolment, no consent question, no eligibility. Run through their own five tests it
   scores 17 against attrition's 15 excluding T5, and loses only on the column that measures whether
   it has been built.
2. **Their own real-world evidence points at it.** The CFPB split is the only real US card text in the
   entry and it says the reader is a complaint-escalation detector: 23/24 against churn intent 1/8.
   That evidence arrived for $0 after the direction was chosen and was handled as a disclosure problem.
3. **Their own refusals disappear under it.** Calibration, precision on a real book, save rate, margin,
   retention lift, per-customer ranking, the confidence float's weight in a score — every one of the
   fourteen refusals is a refusal about *predicting a person*. A product that counts what customers
   already said and reports a date and a population makes no prediction and needs none of them.

I hold my phase 1 position on the specifics: the sentence ("every remediation this bank has ever paid
for was described to your call centre, by name, months before anyone joined the dots"), the category
(conduct surveillance — trade surveillance pointed at customers instead of traders), the buyer (CCO or
Head of Complaints, with General Counsel as a co-signer you win rather than brief), the phase-0 shape
(six weeks, their last five remediations, days-earlier as the measured quantity), and the build order
(cluster layer, population-level corpus, time-to-detection metric).

And I hold the two concessions against myself: **the $3.4M and the 256 days in my phase 1 Beat 4 are
authored fixtures exactly as 58 days is, and I owe them the same "on this arc" discipline I applied to
the team's number.** The difference I will defend is that my chain's *inputs* are quantities the client
has already measured — the cost, population and discovery date of their own last five remediations —
where theirs require the client to estimate a save rate and a margin that nobody measures. That is a
real difference in kind. It is not a substitute for measurement, and the cluster layer that would
produce the measurement does not exist.
