# Phase 2 — judging the team's case against my own

**Where this lands, up front:** I hold the phase-1 recommendation. Undertow — elder and vulnerable-
customer exploitation — over card attrition. Having read the team's own documents, I think their
numbers, disaggregated rather than summed, argue for my conclusion more than their prose does. But
hostile re-reading of the same evidence base also finds the weakest plank in my own phase-1 case and
makes it weaker than I presented it, and it finds that my recommended direction currently has *zero*
real-world validation where theirs has some — bad validation, but some. Net: I still think they have
the wrong lead, for a reason their own scoring already contains and their own prose never asks about.
I also think their decision not to switch two days before the gate was very likely the right call
regardless — that is a different question from which direction the evidence favors, and I want to be
explicit that I am answering the second one, not relitigating the first.

Before anything else, one fact worth naming because it changes how I read everything that follows:
**four of my five phase-1 screening tests and their five (T1–T5) are, independently, close to the same
test**, in the same order I listed mine. Conversation exists. Not already structural. Consuming
process exists without outbound contact. Money verifiable. Mine and theirs converge, unprompted, on
four axes out of five. That is a genuinely useful data point about the two processes — it means the
right set of questions to ask isn't in dispute, mine and a fully-resourced internal red-team landed on
almost the same ones cold. Where we diverge is instructive too: I added a fifth test they don't have
(does the direction's real-world shape match the mechanism's *proven* strength) and they added two I
don't have (regulatory ease of the sale, reuse of what's already built). Their two additions are not
padding — they are exactly the right correction for the fact that they are not choosing on a blank
slate and I was. Keep that asymmetry in mind; it does real work in section 2.

---

## 1. Where I was wrong

**Update — the "dollar value impact" criterion cuts harder against Undertow than I credited.**
Venkat and Farhan are explicitly finance people judging "dollar value impact," and the FBI/FinCEN
numbers I leaned on are the *customer's* loss, not the bank's. `04-ALTERNATE-STORIES.md` says this
plainly and I should have weighed it harder in phase 1: *"the money is not the bank's money... Pitch
it anywhere else and it collapses on the first question."* I still think a federal, cross-verified,
$7.7bn/37%-YoY primary figure reads as more rigorous to two numerate executives than a chain built on
an unpublished voluntary/involuntary split and a zero false-positive assumption — see section 2 — but
I was too quick in phase 1 to treat "needs no translation for a CEO and a COO" as settling the money
question. It doesn't. It only settles that the *harm* is legible. Whether a competition scored partly
on "dollar value impact" rewards a legible-but-third-party harm over a smaller-but-first-party one is a
real, open question I glossed over.

**Update, and the more important one — my "fourth test" was over-stated.** Phase 1 called the
diffuse/concentrated arc split "the whole argument": diffuse arcs (evidence spread thin across many
conversations) beat capped-memory alternatives 30–0–0, concentrated arcs lose 0–30–0, and grooming is
diffuse almost by definition, so the system's one clearly-proven relative strength maps onto
exploitation and not onto attrition. Reading the brief adversarially now, two things I did cite but
under-weighted cut directly against how much that argument can carry:

1. The 30–0–0 result is a comparison against *other memory designs* (capped-memory arms). The *same*
   diffuse arcs, compared against a *random ranking*, go 18–8–4, `p=0.076` — the pre-registered bar was
   significance, and this is published as a failure. So the honest statement is: on the evidence shape
   I'm claiming is exploitation's home turf, the full ledger reliably beats worse memory designs but
   does *not yet* reliably beat a coin flip. That is a real difference and I let the first result stand
   in for both.
2. I did not know, and should have gone looking for, the `dumb-ledger` result: every scoring mechanism
   switched off beats the full ledger on diffuse arcs 18–7–5 (`p=0.043`) — until you notice 70.8% of
   that arm's queue was decided alphabetically, at which point fair tie-breaking collapses it to
   13–11–6, `p=0.839`. That is not evidence *for* attrition. It is evidence that, on the exact stratum
   I built my whole case around, nobody has yet shown that the *sophistication* — decay, corroboration,
   confidence weighting, escalation, the stuff that makes this more than a spreadsheet count — is
   earning its keep. Accumulation-vs-forgetting (30-0-0 vs capped memory) and sophistication-vs-a-dumb-
   count are two different claims, and only the first one is actually established on diffuse arcs.

I'm not abandoning the mapping — grooming genuinely does look like the textbook diffuse case, and nothing
above says the mechanism is bad, only that it isn't *proven* good yet at the standard the brief itself
sets everywhere else. But "the whole argument" was the wrong phrase in phase 1. It's a strong prior, not
a demonstrated result, and I should have flagged that gap myself instead of letting the team's silence
on it stand in for confirmation.

**Update — I did not sufficiently flag that the portfolio-wide "8th of 9, worse than random" result is
reader-confounded, not architecture-confirmed.** I quoted it in phase 1 as if it were a clean statement
about the accumulation idea. The brief's own caveat — "every arm figure above is on the weak
(rule-engine) reader, which finds 617 of 2,700 planted signals... this crowds every arm between 0.113
and 0.145" — means every arm was starved of input signal before it ever got to rank anything, so a
tight, low cluster of scores across nine very different designs is at least as much a statement about
signal *recall* as about ranking *sophistication*. I should have said this the first time; it cuts
against my own argument's tidiness (the failure isn't specifically an attrition failure or specifically
an exploitation-favoring failure — it's a "we haven't run a properly-powered, properly-fed test of this
architecture at all yet" failure, for either direction).

**Partial update — the team's "latency, not clairvoyance" reframe is better than anything I proposed.**
*"Your propensity model refreshes on a batch cadence... and it never sees what the customer actually
said. Ours moves the moment the transcript lands"* is structural, needs no lift study, and is genuinely
unattackable in a way my own demo framing wasn't forced to be, because I never had to defend a value
chain with a hole in it — Undertow's consuming process is a SAR queue, not a save-rate multiplication.
I think this reframe is *more* powerful pointed at exploitation than at attrition (early warning is
Undertow's entire premise, not a side benefit), and its absence from my phase-1 answer is a real gap in
craft, not substance.

**Non-update, worth naming as such.** Reading the corrected pre-delinquency arithmetic (7–10× walked
back to 3–9×, centrally ~5×, possibly under 1× risk-adjusted) didn't move me at all on the actual
question at hand, because I never considered #2 a contender in phase 1 — my comparison was always
attrition vs. exploitation vs. cross-sell. Seeing the team's demolition of it doesn't touch my case
either way; I'm noting it only so the absence of an update there isn't mistaken for having missed it.

---

## 2. Where they are wrong — and I'm holding this

**The core disagreement:** card attrition should not be the lead. It is defensible as *what ships
today*, given where they are two days out. It is not defensible as the evidentiary conclusion the
prose repeatedly calls it — *"the lead is settled"* (`04-ALTERNATE-STORIES.md`), *"Do not re-open this
before 09-11"* (`00-READ-THIS-FIRST.md`).

Here is Table B's own scoring, disaggregated instead of summed:

| Test | Question | Attrition (#1) | Exploitation (#5) | Winner |
|---|---|---|---|---|
| T1 — conversation exists | do customers talk about it? | 4 | **5** | exploitation |
| T2 — not already structural | does the bank already see it? | 3 | **4** | exploitation |
| T3 — consuming process | what happens with no outbound contact | 4 | **5** | exploitation |
| T4 — money verifiable | published anchor | 4 | 4 | tie |
| T5 — demoable in 7 min | can it be shown | 5 | 5 | tie |
| Reg | how hard to clear model-risk/validation | **5** | 3 | attrition |
| Reuse | how much is already built | **5** | 3 | attrition |
| **Total** | | **30** | **29** | attrition, by one |

On every single dimension that asks *"is this the right problem"* — does the conversation exist, does
the bank already see it another way, does a consuming process exist without inventing an outbound
motion, is the money real — exploitation wins three and ties two. Attrition's one-point lead is entirely
manufactured by the two dimensions that ask *"is this cheap to ship this week given what we already
built."* Those are legitimate questions. They are not the same question as "which is the better
pitch," and a document that sums both kinds of question into one number and then calls the sum
*"settled"* is quietly answering two different questions with one score. `04-ALTERNATE-STORIES.md`
even says the header column *"turned out to matter more than any of the scores"* about ledger-dependence
— and never runs that same "wait, does this column change the ranking" scrutiny on Reg/Reuse against
T1–T3, even though the same document states in its own honest-gaps section: *"Ratings in Table B are
my judgement, not measurements... two people could reasonably reorder the middle of the table."* A
one-point margin on a self-described non-measurement, where the margin is fully explained by two
switching-cost columns, is not a settled conclusion. It's a coin flip wearing a table.

**On the money specifically.** `01-THE-STORY.md`'s own beat 5 concedes: *"Every haircut in that chain
is applied to leavers. Stayers are never counted... The chain quietly assumes precision is 100%. A
modeller will see this the moment they look, and it is a worse finding than the small-population one...
this one says it is wrong."* That is the team's own words about their own headline number. Compare
that to exploitation's anchor: FBI IC3 2025, verified against fbi.gov and ic3.gov, $7.7bn, 37% YoY,
12,400+ victims over $100k. The exploitation number's *problem* is whose pocket it's in. The
attrition number's problem is that it might not be a real number at all once precision — never
measured — is applied. A wrong-pocket-but-real number and a right-pocket-but-possibly-fictional number
are not obviously ranked in attrition's favor for a rubric line called "dollar value impact," and the
document never runs that comparison explicitly; it runs "is $550–800 real" rigorously and "is $7.7bn
the bank's" rigorously, but never "which hole is worse," because doing so would require treating the
lead as a genuinely open question again.

**On T3 specifically**, since `04-ALTERNATE-STORIES.md` calls it *"the discriminator... the single most
useful thing in this document"* — attrition's T3 answer is *"case briefs the next inbound agent,"*
which only fires if the customer calls again. Exploitation's is *"a SAR queue that already exists and
is legally required,"* which fires regardless. The document names its own discriminator, scores
exploitation ahead on it, and never asks whether a discriminator that favors the alternative should be
allowed to discriminate.

**Where I think the team is right and I was too glib in phase 1:** the operational call. Two days out,
zero dry runs, a working demo built around Eleanor's card and the 74/132-day crossing, and — this
matters — a signal family for grooming/coercion that has *never been authored, tested, or run against a
single real or synthetic conversation.* My phase-1 "what to build first" says this costs "a day of
authoring and under a dollar of model spend" as if that settles the risk. It settles the *cost*, not
the *risk of a first-ever detection pass missing its own planted cues in front of the two people whose
judgment ends the competition.* Switching the lead 46 hours out, on content that has never been run
once, would very plausibly have been the wrong tactical call even though I think it's the right
strategic one. I am holding the analytical position — the evidence, read straight, favors exploitation
— while conceding the operational one is a genuinely separate question that the team, under real time
pressure, probably got right. My complaint is not "they should have switched on 09-09." It's that the
comparison was never run as a live question at any point *before* switching became reckless — which is
where section 5 goes.

---

## 3. What both of us missed

**Absent from my phase-1 answer and, as far as I can tell from the four documents I was given, from
theirs too:** the `dumb-ledger` reversal above. It may be treated in `03-REFERENCE.md`, which I was
told not to read, so I can't claim it's absent from the team's thinking generally — only that it does
not appear in `00-READ-THIS-FIRST.md`, `01-THE-STORY.md`, `04-ALTERNATE-STORIES.md`, or
`06-DEFENDING-THE-SCORE.md`, which is exactly where I'd expect the most adversarial internal document
(06, built specifically to pre-empt the hardest technical question) to engage it if it had been
absorbed into the pitch's own self-understanding. This is the single most technically serious result in
the brief and it is missing from the room.

**Absent from both, and this one nobody prompted:** deploying a detection capability can *raise* the
duty-of-care bar the deployer is later held to. A bank that has never claimed to detect slow-grooming
patterns is judged against the standard of care that existed before the capability did. A bank that
builds and runs Undertow, and then misses a case its own system was capable of catching, may be judged
against a standard it created for itself — several states now impose affirmative reporting duties on
banks for suspected elder financial exploitation, and "we had a tool for this and it didn't fire" is a
different fact pattern in front of a regulator or plaintiff's attorney than "no such tool existed."
This cuts against my own phase-1 enthusiasm more than it cuts against attrition, where no comparable
duty-of-care escalation exists — nobody sues a bank for failing to retain a customer. Neither the brief
nor either of our analyses raises this, and it belongs in the "what's genuinely hard here" list for
Undertow specifically, probably above cross-channel identity resolution.

**A synthesis neither document makes explicitly, worth adding now:** on defensibility over time, the
team's own competitive-landscape read says Twilio would need "retroactive re-evaluation of earlier
entries, entry versioning, and deterministic re-weighting outside the model... None of those is hard."
If the mechanism is easy to copy once demonstrated, the real moat is either the content (signal
families, thresholds) or the relationship (who's already validated and embedded where). A BSA/AML
vendor relationship, once through model-risk validation, is expensive to re-litigate and switch away
from; a retention-analytics feature is exactly the kind of thing an incumbent propensity vendor bolts on
as a checkbox next quarter. Neither of us used stickiness-over-time as a factor in choosing the
direction, and it's a real one — it argues for exploitation on grounds neither of us actually stated.

**A bias that cuts symmetrically and neither analysis applies symmetrically:** `01-THE-STORY.md`'s
honesty beat correctly notes *"CFPB narratives are complaints by construction... not what a servicing
call looks like"* to soften churn intent's 1/8 — and does so responsibly, calling it one of *"three
things [that] keep this honest and none of them is a rescue."* Fair. But the identical fact — a
complaints corpus over-represents complaint-shaped language — applies with exactly the same force to
complaint escalation's 23/24 and 60/65, which the same document calls *"the single best evidence in
the repo that the model is the product"* and repeats more than any other number in the pitch. A
complaint-detector doing well on a corpus of complaints is a much lower bar than doing well on the
ordinary servicing calls the actual product has to read in production (the architecture explicitly
reads 100% of conversations, not just the angry ones). The selection-bias caveat is invoked exactly
once, next to the one inconvenient number, and never next to the convenient one it applies to just as
much. I missed this in phase 1 too — I used the CFPB churn-intent number as a strike against attrition
without ever flagging that I was, in the same breath, treating complaint escalation's CFPB number (my
own stated fallback) as if it weren't subject to the identical corpus bias.

---

## 4. The evidence, read hostilely

Going through the ask's named results directly:

- **Chance-gate failure on diffuse arcs, 18–8–4, `p=0.076`.** Argues against over-confidence in *either*
  pitch, not specifically against attrition. It's a statement about the corpus's difficulty at this
  scale, not a directional finding. I used it correctly in phase 1 as a weakness of the current system;
  I should not have let it also silently support my own recommendation, since it's measured on the same
  stratum I'm claiming as exploitation's strength.
- **`dumb-ledger` beating the full ledger 18–7–5 (`p=0.043`), collapsing to 13–11–6 (`p=0.839`) once
  fairly tie-broken.** The most serious result in the whole evidence base and the least discussed. It
  argues against the "code counts and remembers, and the remembering adds value" claim generally — it
  is neutral-to-negative for both pitches, and more damaging to mine specifically, since my entire case
  rests on the mechanism's proven edge on exactly this stratum, and this result says that edge, once you
  strip out a tie-break artifact, may not exist.
- **Whole-portfolio 8th of 9, worse than random (0.115 vs 0.113).** Confounded by reader weakness (617
  of 2,700 planted signals recovered) — see section 1. Neutral on the attrition-vs-exploitation
  question; a genuine indictment of "we have properly tested this architecture," which nobody has done
  yet at both adequate signal recall and adequate statistical power simultaneously.
- **Records reversing twice across two corpus rebuilds.** General instability warning, applies to any
  number either pitch would quote, present or future. Argues for treating every headline figure in this
  system, on either side, as provisional.
- **CFPB churn intent 1/8.** Argues directly against attrition, since it's the only non-synthetic test
  of the specific signal family the pitch depends on. Does *not* argue for exploitation — nobody has
  built or tested a grooming-language family against anything real yet. This is the sharpest asymmetry
  in the whole evidence base: attrition has been tested against reality and found weak; exploitation has
  not been tested against reality at all. A weak, tested claim and an untested, hoped-for claim are not
  symmetric, and I should be honest that this is the biggest hole in my own recommendation, bigger than
  anything in section 1's updates.

**Over-read:** the $1.65M value chain, presented with real hedging but still presented as a number, on
a 100%-precision assumption the team's own text admits is false. The model-reader confidence-ablation
result (89.5%) treated as settling the bucketing question when it's a single 10-seed sample. And, from
my own side, the diffuse/concentrated mapping treated in phase 1 as "the whole argument" rather than a
strong, unproven prior.

**Under-used:** the T1–T3 disaggregation in Table B, computed but never asked to justify reopening the
lead. The `dumb-ledger` result, published but absent from every strategy document I read. The
escalation-bonus finding (100.0% inert on all 30 datasets) — noted once as a stage-fright warning, never
connected to the larger question of which of the four scoring mechanisms are validated versus
decorative, which is directly relevant to whether the system is as sophisticated as the pitch claims.

**Direct answer to "does the evidence support the idea I proposed, the one they're pitching, both, or
neither":** neither, cleanly, at the standard the brief holds itself to everywhere else. The evidence
weakly favors exploitation on architectural fit (proven relative strength on diffuse arcs, though not
yet proven against chance) and on the T1–T3 tests, and it weakly disfavors attrition on its one
real-world validation point and its unmeasured, admittedly-100%-precision-assumed money chain. But
exploitation has no content built and no test run against anything real, synthetic or otherwise. The
honest reading is that this evidence base supports a *sequence* — validate exploitation's signal family
next, with complaint escalation (the one direction genuinely proven against real text on both sides'
account) as the bridge — more than it supports either pitch standing alone, today, at full confidence.

---

## 5. Grading the self-criticism

**Real rigor, unevenly applied.** At the level of checkable fact — is a citation current, is an
arithmetic step right, is a claim computable at all — this is some of the most disciplined
self-correction I've read: SR 11-7 correctly identified as rescinded and replaced with SR 26-2; the
$6,610-per-borrower-vs-$2,077-per-account confusion caught and fixed in three separate places; the CAC
figure corrected from an unsourced $80 to a filings-derived $500–532 upper bound, in the *harder*
direction (strengthening a number they could have left alone); the "report performance inside and
outside the scored population" commitment withdrawn because *"that cannot be computed"* rather than
quietly kept; the deposit-flight and balance-attrition anchors both re-derived and both revised
downward on their own arithmetic. None of this is performative. It's real, and some of it (the
withdrawn commitment, specifically) is the kind of correction that costs credibility to make and buys
nothing but honesty.

**At the level of the strategic premise the facts serve, the same discipline goes almost silent.** Every
correction above operates entirely inside the frame "attrition is the pitch, make attrition's numbers
survive contact." None of them step back and ask whether the volume of correction attrition's numbers
have needed — an unpublished voluntary/involuntary split, a halved APR-vs-yield error, a 100%-precision
blind spot admitted outright, a 1/8 real-world hit rate on its lead signal family — should itself be
weighed against the alternative sitting one point behind it in their own scorecard. That is the answer
to "is this rigor or a substitute for rigor": it's genuine rigor, deployed asymmetrically toward
questions with checkable right answers and away from the one question — is this the right direction —
that doesn't have one. That is an extremely common, very human failure mode, and it is exactly the kind
of thing that "survives every pass" precisely because each individual pass is honestly, defensibly
about something else.

**The clearest single piece of evidence for this is small and precise, and it's worth stating exactly.**
`06-DEFENDING-THE-SCORE.md` reports two results from the identical 10-seed, 200-customer keyed run.
The arm-ranking comparison (full-ledger vs. window3-top2) comes out 5–4–1 against the published 30–0–0,
and gets: *"That is a power failure, not a refutation... At 200 customers every arm sits on chance."*
The confidence-weighting ablation, measured the same day on the same seeds, comes out 89.5% vs. the
30-dataset offline figure of 80.0% — a reversal of which mechanism is most load-bearing — and gets:
*"This is the answer to give, because it is the one about the system you actually sell... This
strengthens the recommendation rather than weakening it."* One 10-seed result that contradicts a
published headline is treated as too noisy to trust. An adjacent 10-seed result from the same run that
happens to mean a one-day fix has no downside is treated as decisive, twice, in two different documents.
There may be a real methodological reason the two deserve different confidence — a continuous overlap
metric across many customers within 10 seeds is a different effective sample size than a discrete
win/loss/tie sign test across 10 seeds — but the documents never make that argument. They just apply
scrutiny to the inconvenient result and skip it for the convenient one, with no stated reason either
way. That is the definition of motivated reasoning, stated as precisely as I can: not a lie, not even
necessarily a wrong conclusion, but a selectively-applied standard of doubt.

**And it is not a one-off.** The same shape appears at three different scales in these four documents:
macro, in the lead-direction choice itself (rigorous on every number *inside* attrition, silent on
whether attrition should still be the frame, despite a one-point, self-admittedly-unmeasured margin);
meso, in the CFPB selection-bias point applied to soften churn intent's 1/8 and never applied to
discount complaint escalation's 23/24, which rests on the identical corpus artifact; micro, in the
confidence-ablation example just above. Three instances of the identical pattern, at three different
resolutions, is not coincidence. It's a house style.

**One meta-observation, offered fairly:** nearly every correction in these four documents is dated
2026-09-09 — two days before the gate. That density is double-edged. It shows real capacity to find and
fix errors under pressure, which is worth crediting. It should also lower, not raise, confidence that
this is now a fully-scrubbed document, for the obvious reason: if six-plus substantive errors surfaced
in one 48-hour pass, it would be a coincidence if that pass happened to exhaust the supply exactly in
time for the deadline.

**One clean counter-example that keeps this fair.** The US-vs-UK market switch is a case where the team
*did* apply real strategic reconsideration, not just fact-checking — they gave up their best number (the
£650 Ombudsman tariff) and rebuilt the money story on less clean but more defensible ground, with the
reasoning shown, not asserted. That means the capacity for genuine premise-level reconsideration exists
in this team's process. It just wasn't turned on the attrition-vs-exploitation choice, which is the more
consequential one and the one that happens to be the direction chosen before any of the current evidence
existed.

---

## 6. The choices they made

**Direction (attrition over twelve others, exploitation included): defensible for today, wrong as a
settled conclusion.** Covered fully above. The tell is that the file ranking the alternatives states
outright it is *"not a re-ranking of the lead"* — the lead was fixed before the evidence that should
have been allowed to challenge it was gathered, and every subsequent pass defended rather than re-derived
it. That is a choice that looks like it was made for the reason the prompt asks me to name plainly:
what was already built, dressed as an evidentiary conclusion.

**Market (US over UK): right, and well-argued.** This is the one place I saw the team actually
re-open a settled premise and follow the evidence somewhere less comfortable — giving up a clean,
sourced, unarguable £650 tariff for a messier but primary-sourced US chain (608M accounts, 0.7–1.0%
monthly closures, CAC derived from 10-Ks rather than asserted). I have no competing document to check
this against, but on what's shown, this looks like the genuine version of the process section 5 finds
missing elsewhere.

**Buyer (Head of Retention Analytics over the submission's Contact Center/CCO): reasonable, and
correctly flagged as open rather than silently swapped.** `00-READ-THIS-FIRST.md` calls this out as a
decision Ravi should make explicitly, not bury. Good practice regardless of which way it's decided.

**Demo mechanics: agree, largely convergent with my own phase-1 instincts.** The re-cut crossing
(away from a competitor-mention trigger, which the team correctly notes means the customer has
"already shopped" — leading the event, not the decision), dropping "58 days early" as a spoken result
rather than an authored fixture parameter, claiming three signal families honestly rather than implying
eight — all of this matches, independently, what my own phase-1 demo discipline argued for (don't let
authored timing pose as a finding, don't open with a dashboard, say the human-in-the-loop line before
it's asked). Where we differ is only the persona the discipline is applied to.

**Value chain ($1.65M, with the no-false-positive-leg caveat added late): defensible, minor internal
tension.** The team says explicitly, *"Two numbers we will not invent: your incremental save rate...
and your margin per account"* — and then still leads with a specific total built on exactly those two
client-supplied numbers plus an unstated 100%-precision assumption. The hedging is honest and about as
thorough as it can be while still naming a number (*"say it as what it is — the gross ceiling before a
precision haircut nobody has measured — or don't say a total at all"*). I'd have made the second choice.
Small tension, not a large one.

**Dropping the CFPB-enforcement and UK-persistent-debt regulatory arguments: agree.** Both are
correctly identified as arguments that would read as not having done the work in 2026 — the first
because CFPB posture has visibly contracted, the second because no US analogue exists. Good discipline.

**Platform framing left off the stage, sold as a point solution: agree, strongly convergent.** My own
phase-1 conclusion — *"sell it as a point solution every time, build it as a platform every time"* —
is close to identical to theirs. Independent agreement on this specific point, for what it's worth,
across a cold read and an extensively war-gamed internal process, is a good sign the underlying
go-to-market instinct is sound regardless of which direction sits inside it.

---

## Where this leaves it

Two different questions got asked of the same evidence, and they have two different answers. *Which
direction does the evidence favor* — exploitation, on the four tests both of us independently converged
on, using the team's own numbers rather than their prose. *What should the team have walked into the
room with today, 2026-09-11* — almost certainly attrition, because the alternative's one load-bearing
asset (a signal family for grooming and coercion language) has never been authored, let alone run once,
and a first-ever detection pass debuting live in front of the two people who decide the shortlist is a
bad bet regardless of which direction the analysis favors. Both things are true at once, and the
team's documents mostly write as though answering the second question also answered the first. It
doesn't. The next unit of work this evidence base actually calls for isn't a better attrition pitch —
it's building and testing the one thing that would make the first answer more than a strong prior:
a grooming-language signal family run once against something real.
