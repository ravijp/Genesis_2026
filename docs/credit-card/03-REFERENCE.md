# Reference — depth behind the story

**You do not need to read this before the gate.** It is what you reach for when challenged, and what
whoever builds the card corpus works from. `00-READ-THIS-FIRST.md` and `01-THE-STORY.md` are the ones
that matter on the night.

Market: **United States**, settled 2026-09-09. **Any UK figure in sections 1-6 is an error** — a
prior pass assumed a UK issuer and was discarded. **The one deliberate exception is §7**, the UK
complaints appendix, which Ravi kept as a footnote when he cut the two competing scripts down to one.
Everything in §7 is labelled UK and is an *answer to a question*, never a beat.

Contents: **1.** the signal taxonomy · **2.** the score, defined · **3.** how it is consumed ·
**4.** the value model · **5.** claims triage — what we may and may not quote · **6.** the red-team
record · **7.** appendix: the UK complaints variant, and the one published tariff this pitch does not
have.

---

# 1. The signal taxonomy

## Why the current four families are not good enough

Today the system has `churn_intent`, `financial_distress`, `complaint_escalation`, `life_event` —
generic retail banking. The cues talk about taking your business elsewhere and money going somewhere
else. **No cue in `src/earshot/extract_lexicon.py` mentions APR, annual fee, points, or balance
transfer.**

A card executive hears that and concludes we have not worked in cards. The taxonomy is where domain
credibility is won or lost, and it is cheap to fix relative to what it buys.

## The four tests a signal must pass

| Test | Question |
|---|---|
| **(a) Said out loud** | Does the customer articulate it, or would the model infer it from tone? |
| **(b) Not already structural** | Does the bank already capture it continuously and more reliably? |
| **(c) Leading, not coincident** | Does it precede the decision, or restate a trend they already see? |
| **(d) Actionable** | Does it point at one specific retention lever? |

Test (b) is the ruthless one, and it is what answers *"we already have this."*

## The eight families, with US phrasings

| # | Family | Sub-signals | US verbatim, as a cardholder would say it | Lever | Already structural? |
|---|---|---|---|---|---|
| 1 | **Competitive displacement** | Named rival · unnamed comparison · specific rival term quoted | *"Chase is giving me 0% for 21 months"* · *"I just got the Amex, it's 5x on groceries"* · *"I'm looking at what else is out there"* | Match offer, pricing exception | **No** — you cannot see a rival's offer |
| 2 | **Closure-mechanics enquiry** | Payoff amount · points-on-closure · balance-transfer-out · direct closure request | *"What's my payoff amount if I clear it today?"* · *"Do I lose my points if I close this?"* · *"I'd like to close the account"* | Warm transfer to retention | **No** — only the closure event, afterwards |
| 3 | **Price/value objection** | Annual-fee anniversary · APR objection · "not worth it" | *"The $95 just hit and I'm not sure it's worth it"* · *"26.99% is insane"* · *"I don't get enough back from this card"* | Fee waiver, **product change** to a no-fee card | Partly — a waiver *request* is logged, the value framing is not |
| 4 | **Rewards dissatisfaction** | Devaluation · redemption friction · unexpected expiry | *"The points aren't worth what they used to be"* · *"Third time I've called trying to redeem"* · *"My points expired and nobody told me"* | Rewards escalation, goodwill points | Partly — redemptions are logged, the felt loss is not |
| 5 | **Service failure and trust breach** | Repeat contact · unresolved promise · escalation language · **regulator/AG threat** · fraud handled badly | *"This is the third time I've called about this"* · *"Somebody was supposed to call me back"* · *"I'm filing a complaint with the CFPB"* · *"You basically called me a liar about the fraud"* | Case-owner escalation, complaints routing | Partly — a *logged* complaint is structural; the intent one step earlier is not |
| 6 | **Credit-limit friction** | Increase denied · limit decreased · declined at point of sale | *"You denied my credit limit increase again"* · *"You cut my limit and now I can't use it"* · *"It got declined at the register"* | Manual underwriting review | **Yes** — the decision is logged. Only the *reaction* is new |
| 7 | **Distress preceding attrition** | Payoff-then-leave intent · minimum-payment-as-resignation · letter fatigue | *"I'm paying this off and then I'm done with it"* · *"I just pay the minimum now, that's all this card is for"* | Conditional retention offer — **or vulnerability routing** | Partly — payment ratio is structural, the *intent* is not |
| 8 | **Life-event driven need change** | Relocation · retirement · bereavement · business closure | *"I'm moving overseas, will this even work there?"* · *"I just retired, I don't need this"* · *"My husband passed away"* | Product swap, fee waiver, or **nothing** | **No** — usually surfaces nowhere before the account event |

## The correction that matters: leading the DECISION vs leading the EVENT

The original table used one word, "leading", for two different things. An adversarial pass caught it,
aimed at the exact signal that opened the case in the demo's first draft.

| | Meaning | Worth |
|---|---|---|
| **Leading the event** | Earlier than any account record — before the closure code | Operationally useful, **but the customer may already have decided** |
| **Leading the decision** | Genuinely pre-decisional | **This is where "the available lever changes" lives** — and therefore where the value lives |

| # | Family | Corrected label | Why |
|---|---|---|---|
| 1 | Competitive displacement | **Event only** | Quoting a specific rival term means the shopping is done. A balance transfer needs an application and a hard pull — a share of these people are already approved |
| 2 | Closure-mechanics | **Coincident with the decision, by definition** | We already concede everyone catches it |
| 3 | Price/value objection | **Decision** — with the **worst base rate** in the set | Most annual-fee grumbles do not leave. Reasoned from mechanism, **not measured** |
| 4 | Rewards dissatisfaction | **Decision** | The original "mixed" label was already honest |
| 5 | Service failure / trust | **Not leading for attrition** | Leading for a *complaint*; coincident or lagging for closure. Card service-failure attrition usually shows as reduced usage, not closure. **This family predicts the pre-reframe product** |
| 6 | Credit-limit friction | **Not leading** | Downstream of the bank's own logged action |
| 7 | Distress preceding attrition | **Downgrade** | Stated intent to pay down is among the least reliable things a distressed customer says — and if they are distressed, closure may not count as *voluntary* attrition under the bank's own label |
| 8 | Life event | **Decision** | Genuinely leading, no proxy, low base rate |

**Net: genuinely leading-the-decision *and* non-structural is families 3, 4 and 8.** The two clean
structural wins (1 and 2) are leading-the-event only.

**So claim three, not eight.** All eight still *feed* the score; only three support the "we caught it
before they decided" argument. Saying three honestly is worth more than implying eight.

## The US-specific insight worth having: not all attrition is worth stopping

The United States has a well-established sign-up-bonus churner population — customers who open a card
for the bonus, meet the minimum spend, and close at or before the first annual-fee anniversary.

**Retaining those customers destroys value.** A score that cannot separate them from a profitable
long-tenure customer drifting away is worse than no score, because it spends retention budget on the
people the issuer would rather lose.

Two consequences, and both make the pitch stronger:

1. **The score must be consumed alongside the issuer's value score, not instead of it.** That is
   already the architecture — see §3. This is the concrete reason why.
2. **Tenure and acquisition channel are the client's data, not ours.** We surface the intent; their
   value model decides whether the intent is worth acting on.

Saying this unprompted signals card literacy faster than anything else in the taxonomy.

## The three signals we dropped

The drop list is how the taxonomy proves it was built by someone applying a filter rather than
brainstorming.

| Dropped | Failed | Why |
|---|---|---|
| **Wallet-share / spend migration** as a standalone family | (b), (c) | A spend-trend decline is already continuous, structural and more reliable than an occasional *"I only use this one for the odd thing now."* The spoken version **lags** the trend rather than leading it. Kept only as corroborating colour inside family 3 |
| **Generic negative sentiment** | (d) | *"Customer sounds annoyed"* points at no lever. Sentiment scoring is exactly the commodity framing to avoid |
| **Credit-limit increase *request*** (not denied) | (c) | Closer to an **anti-signal** — asking for more limit signals engagement. Only denial, decrease and decline-at-POS made family 6 |

## Vulnerability is a hard branch, not a judgement call

**Bereavement, letter fatigue, badly-handled fraud, and any distress language layered on a closure or
limit signal must route to a duty-of-care review — never to a sales retention offer.**

In the US the exposure is **UDAAP** (Dodd-Frank §§1031/1036), and specifically the "abusive" prong,
which reaches taking unreasonable advantage of a consumer's inability to protect their own interests.
Turning a disclosed hardship into a sales trigger is the textbook shape of that risk.

**This must be a deterministic branch in code, not a prompt preference.** Two reasons:

1. It is the difference between a system a US bank's compliance function approves and one it does not.
2. **It is a strong pitch beat, not a caveat.** Two executives listening to an AI pitch are waiting for
   the moment the vendor shows they know where the harm is. *"This signal makes us deliberately **less**
   likely to sell to that customer"* is that moment.

**The live consequence, stated rather than discovered on stage:** families 7 and 8 feed the score and
are blocked from offer eligibility, so **a customer can cross the threshold on evidence that cannot be
acted on commercially.** The answer is that it becomes a duty-of-care case on a different desk. Have it
ready.

## Decoys — the false friends

Credibility rests as much on what the system does *not* fire on.

| Decoy | Why it looks like attrition | What they actually say |
|---|---|---|
| Lost/stolen replacement | Contains "cancel" | *"I need to cancel this card, it was stolen — send me a new one"* |
| Routine address change | Mentions moving | *"I just moved, can you update my address"* |
| Travel notice | Mentions going abroad | *"I'm going to Mexico next week, just so it isn't blocked"* |
| Happy dispute outcome | Mentions a problem | *"That chargeback went through fine, thanks"* |
| Autopay change | Sounds like closing | *"Cancel the autopay, I'll just pay it manually"* |
| Authorised-user removal | Sounds like an ending | *"Take my son off the account, he has his own now"* |
| **Product change / upgrade enquiry** | Sounds like dissatisfaction | *"Is there a version of this without the annual fee?"* — **this is a retention-POSITIVE signal.** They want to stay, cheaper |

**The shared tell: none carries an *exit* framing**, and several explicitly name staying. A keyword
extractor firing on "cancel", "stolen" or "another card" without a direction check misfires on all
seven. **That direction check belongs in the confidence rubric, before strength is scored.**

## Half-lives and accumulation

The engine already supports per-type half-lives plus corroboration, cross-channel and escalation
bonuses (`src/earshot/config.py`, `ScoringConfig`). These are the proposed card values.

**They are argued from each signal's real-world persistence, authored before any corpus is scored, and
NOT fitted.** Saying so is mandatory — fitting them after seeing which numbers look better is the
banned move D-020 already named once in this project.

| Family | Half-life | Why | Corroborate? |
|---|---|---|---|
| 1 Competitive displacement | **240 d** | A considered intent to move, not a mood | **Yes** |
| 2 Closure-mechanics | **21 d** | Hottest and most perishable — they close within weeks or the moment passes | **No** — one clean hit is enough |
| 3 Price/value objection | **150 d**, pulsed at each fee anniversary | Tied to a 12-month billing cycle; each anniversary is a fresh pulse | **Yes**, across years |
| 4 Rewards dissatisfaction | **90 d** | A recurring theme rather than a one-off shock | **Yes** — repeated gripes are the tell, one is noise |
| 5 Service failure / trust | **30 d** per incident; **365 d** for a regulator threat | Friction fades once resolved; a regulator threat is a durable relationship fact | Yes for repeat contact; no for the threat |
| 6 Credit-limit friction | **75 d** | Reaction fades unless the event repeats | **Yes** |
| 7 Distress preceding attrition | **180 d** | A considered abandonment plan, not a cash-flow blip | **Yes** — the paradigm accumulation case |
| 8 Life event | **300 d** | Stays relevant a long time, usually high-confidence on first mention | **No** — one credible mention routes immediately |

**The line to show a judge: family 2 at 21 days and family 1 at 240 days in the same system.** A payoff
enquiry is hot and perishable; a competitor comparison is cool and durable. A single global half-life
gets both wrong. That is the argument for per-type decay in one sentence.

### The cross-channel bonus needs an argument, because it had none

Evidence spanning phone *and* chat scores higher than the same evidence on one channel — and it is one
of three named drivers of the demo's crossing.

**The best available argument:** two channels means **two independent authoring contexts.** The same
customer, described by two different agents in two different systems, is less likely to be an artefact
of one agent's paraphrase. It is a weak-*independence* argument, not a strength argument.

**If it will not hold under questioning, drop it from the demo's causal story** and let
corroboration-across-conversations carry the crossing alone. Never defend a constant you cannot explain.

### The circularity problem — say it before the modeller does

**Our own headline accumulation result does not establish the accumulation claim.**

*"Two weak signals across two conversations beat one loud one"* is, as built, a consequence of **chosen
constants**, none fitted to an observed attrition outcome. And the supporting result — full-ledger
**30–0–0** over `window3-top2` — asks whether a scorer that accumulates recovers arcs that were
**authored to accumulate**, with the answer key and the score function's shape chosen by the same team.

The **0 / 485** retro figure has the same shape: it proves the function is concave, which is what it
was selected to be.

**The falsifying test — worth more than the 30–0–0 result, because it is a bet:**

> On a client's labelled book, run three scorers over the same extracted signals — **(a)** the ledger as
> built, **(b)** a recency-weighted count with no corroboration or cross-channel bonus, **(c)** a
> logistic fit on per-family signal counts — and compare **top-decile uplift** against the observed
> label.
>
> If (b) matches (a), our bonuses are decoration. If (c) beats both, the honest product is the
> extraction layer plus the client's own fitting.

Naming this on stage converts the weakest part of the evidence base into the strongest part of the
credibility.

## What the prompt has to say differently

Changes to `prompts/extractor/v1/`. The mechanics are unchanged — verbatim-quote rule, four-word
minimum, exact-substring check, discard unverifiable quotes. The **content** changes:

1. **US card vocabulary in the operational definitions**: APR, annual fee, cash back, points, balance
   transfer, minimum payment, credit limit, intro/promotional APR, product change, retention offer.
2. **A direction check before a confidence score.** *"Asking about a balance transfer"* is a signal
   only when it is **outbound**. Classify direction first, then strength. Without this the
   transfer-*in* decoy contaminates family 1.
3. **A double-counting rule for the commonest card pattern.** A customer who says *"not worth the
   fee"* **and** *"the points aren't worth it"* in one breath is making **one** complaint unless a
   specific rewards mechanic is named (devaluation, redemption, expiry). Otherwise family 3 only.
   Without this rule, the single most common card grumble inflates every score.
4. **The distress/life-event overlap rule stays as is** — a job loss is both; report both.
5. **Refuse rather than guess**, unchanged: nothing from a hypothetical (*"if you raised my fee again
   I'd have to think about it"*), nothing already resolved, nothing where only the agent raised the
   topic and the customer did not confirm it.

## What the bank already knows, and what the conversation adds

This is the table the pitch lives on, because *"we already have this"* is the first objection.

| Family | Structural proxy they already have | What the conversation adds |
|---|---|---|
| 1 Competitive displacement | **None** | The rival's identity and specific term. Invisible to every internal system |
| 2 Closure-mechanics | **None** — only the closure event, afterwards | The earliest possible warning, weeks before any account action |
| 3 Price/value objection | A fee-waiver-request disposition code | The *reason* framing, which predicts whether a waiver alone holds them |
| 4 Rewards dissatisfaction | Redemption transaction logs | The felt sense of devaluation. A redemption that "worked" can still read as a loss |
| 5 Service failure / trust | Disposition codes; a complaint case once opened | Pre-complaint escalation intent and trust-language severity, one step earlier |
| 6 Credit-limit friction | The limit decision system logs every denial | The stated reaction — *"I'll just use my other card"* — which no decision log holds |
| 7 Distress preceding attrition | Payment-ratio and minimum-payment flags | **Whether they intend to leave once clear, or are simply still struggling** |
| 8 Life event | Almost nothing until a formal process triggers | Often the only place it surfaces before the account event |

**Row 7 is the strongest line in the document — and it is oversold.** The claim that a payment-ratio
flag cannot separate *struggling but staying* from *paying down in order to leave* is real. But a
competent modeller answers:

> *"Payment ratio, plus zero new purchase activity, plus a declining balance, plus no promo rate
> expiring. That's a rule, and I already run it."*

They are largely right. The spoken intent is cleaner and earlier, but the composite gets close.
**Present row 7 as our best line, not as an unanswerable one.**

Rows 1, 2 and 8 are the clean wins — no structural proxy at all. Row 6 is the concession: the underlying
event is already logged, and only the *reaction* is new. If that gets challenged hard, concede it.

---

# 2. The score, defined

Ravi's note said *"define score -"*. The trailing dash was the point: it was undefined. This is that
definition.

## Naming — one word, and it does real work

Keep **attrition**; it fixes the outcome and it is the right word for the room.

**Recommend: "conversation attrition score."** The qualifier is not decoration. It says in the name
that this is derived from conversations only and is therefore *partial*, which pre-empts the
assumption that it is a calibrated replacement for the issuer's own model. Calling it "the attrition
score" invites exactly the comparison we cannot win and do not need.

## The definition

| Property | Definition |
|---|---|
| **What it is** | A per-customer **ordinal** accumulation of conversation-derived attrition evidence, with per-signal decay, corroboration across conversations, and a cross-channel term. Deterministic arithmetic over extracted signals |
| **Target** | A proxy for voluntary closure or effective abandonment — **defined by the issuer's own attrition label**, not by us. They already have a label; we do not invent one |
| **Horizon** | Not fixed by us. Signals accumulate continuously; their model picks its own observation window (30/60/90 days is common) and we supply the value as of that date |
| **Range** | Bounded, monotone in evidence, decaying in time |
| **Cadence** | **Event-driven.** It changes the moment a transcript lands |
| **Explainability** | Every unit traces to one conversation, one signal family and one verbatim quote — plus what that entry contributed *then* versus *now* |

## What it is NOT — say two of these, not all four

The first draft listed four. Two is enough on stage; keep the others for Q&A.

- **Not a customer-value score.** No spend or margin data reaches the system.
- **Not a decision.**

*(Also, for Q&A: not a credit-risk score — no repayment, utilisation or bureau data reaches it. And not
a next-best-action — it chooses no offer, channel or amount.)*

## The event-driven property is the whole differentiator

Incumbent propensity models are **batch-refreshed**, commonly monthly. A call that happened an hour ago
is invisible to them until the next run.

**Ours is live the moment the transcript lands.** That is not an accuracy claim — it is a **latency**
claim, and latency needs no causal study, no lift number and no client data to be true. It is the one
property no incumbent batch-scored model has, which makes it the safest thing to lead with.

## Calibration — concede it immediately

**It is not a calibrated probability.** Nothing in the system is trained against an observed attrition
outcome; it is a deterministic accumulation of matched signal strength.

Describe it to a model-risk reviewer as an **ordinal risk-ranking feature**. It can rank-order
customers within the scored population, and it can be tested for monotonic association with the
issuer's own label once they supply one. **It cannot be read as "this customer has an X% chance of
leaving"** until their model, or a calibration layer built on their outcomes, maps it onto that scale.

Saying otherwise to a modelling reviewer is the fastest way to lose the room. Volunteering it is the
fastest way to earn it.

### The harder calibration problem, which this section previously missed — added 2026-09-09

Conceding *"the score is not a calibrated probability"* is necessary and it is **not sufficient**,
because it concedes the wrong thing. It concedes that the **output** is uncalibrated. The sharper
attack is that an **input** is uncalibrated and is load-bearing.

**`memory.py:99`: `weight = s.confidence if cfg.confidence_weighting else 1.0`.** The model's
self-reported confidence float is a **direct multiplier** on every signal's contribution, and
`confidence_weighting` defaults to `True` (`config.py:73`). Worse, the offline lexicon's confidence is
a hardcoded per-cue constant flowing through the **same field** into the **same arithmetic** — a
regex's 0.92 and a model's 0.92 are treated as the same quantity by code that cannot tell them apart.

**And it is the most load-bearing mechanism in the design.** Removing it moves the top-40 ranking more
than removing decay, corroboration, cross-channel or escalation.

**The literature is against us and we should say so first** — Xiong et al., ICLR 2024
(arXiv:2306.13063) find LLMs consistently overconfident when verbalising confidence across five models
and five datasets; Tian et al., EMNLP 2023 (arXiv:2305.14975) find RLHF degrades calibration relative
to the base model. **Full treatment, the recommendation to bucket it, and the build cost are in
`06-DEFENDING-THE-SCORE.md` §3.** This section exists so §2 no longer implies calibration is only an
output-side concession.

## Coverage — the real weakness, stated plainly

**The score exists only for customers who have had a recorded conversation.** For everyone else there
is no score.

We could not find a published figure for the share of a US card book that contacts the issuer in a
year — issuer contact rates are not disclosed. **That is a client input and we will not invent it.**

What we control is the treatment of everyone outside the scored population, and this is a design
decision with teeth:

> **A customer with no conversation gets an explicit `no-evidence` null state, carried as its own
> category with its own denominator. Never a defaulted zero.**

A zero reads to a downstream tree model or an eligibility rule as *confirmed low risk* — a false
signal, and actively worse than having no feature at all. **The coverage gap must be visible in the
feature-store schema, not silently resolved into a number.**

This is the single most likely place for an experienced modeller to probe. Get there first. And see
the selection-bias problem in section 6 — the harder half of this.

---

# 3. How the score is consumed, and how it survives US governance

This answers the deal-deciding note: *"How will the score be consumed in the end? will it be part of
existing mechanism like retention modeling"*.

**The answer in one sentence:** the score is a **feature and a trigger, never a decision.** It sits
upstream of the issuer's existing attrition model and upstream of their existing save-desk queue, and
it never touches a customer.

## First, the distinction that defeats "we already have this"

Card issuers do not have *one* retention score. They run at least four separate things.

| System | Question it answers | Basis |
|---|---|---|
| **Attrition / churn propensity model** | *How likely is this customer to leave in the next N days?* | Supervised on an observed closure label, **batch-refreshed** |
| **Customer value / CLV score** | *How much do we care if they leave?* | Forward value over a horizon, weighted by retention probability |
| **Next-best-action / offer decisioning** | *Given every score and rule, what do we do now?* | Rules or optimisation over many inputs |
| **Save desk (human)** | *They called to cancel — what do I say right now?* | Agent, live call, approval-limited offer ladder |

**The load-bearing fact: a value score answers "how much do we care", a propensity score answers "how
likely". They are different scores and issuers run both** — a next-best-action engine needs the
product of the two, because value decides whether an expensive offer is justified and propensity
decides whether one is needed at all.

**So when a judge says "issuers already have a retention score", the answer is: yes — and it is usually
a value score, which tells you who to save, not who is leaving.**

Two honest riders, because overplaying this is a trap:

- Some issuers genuinely do run a churn propensity model too. Ours competes with nothing there
  either — it becomes a feature *inside* it.
- **Ours is a candidate feature on the propensity side only, never the value side.** No spend, margin
  or product-holding data reaches this system. Claiming it substitutes for CLV would be false, and a
  competent risk function catches that in the first meeting.

## The four consumption paths, ranked

| # | Path | What the issuer builds | Governance burden | Time to value |
|---|---|---|---|---|
| **1** | **Feature into the existing propensity model** | One feature-store field, event-driven, joined point-in-time-correct; one retrain cycle | Host model's own lifecycle unchanged; ours is a **third-party model input** | Slowest to first value, **fastest to durable value** |
| **2** | **Prioritisation over fixed review capacity** | A ranked queue over an existing case queue. No retrain | **Lightest** — no automated action, a human decides every time | **Fastest** — this is what the demo shows |
| 3 | Trigger into the offer/campaign engine | One eligibility flag; existing eligibility rules still gate everything | Medium — the trigger must be auditable | Medium |
| 4 | Real-time nudge on the inbound save desk | Live score in the agent's screen, mid-call | **Highest** — closest to a live decision | Slowest; heavy change management |

**Pitch path 1 as the destination and path 2 as month one.** Path 1 is the only path that puts the
score *inside* machinery the issuer already owns, validates and governs — which is what closes "just
another dashboard". Path 2 is what a pilot actually is: no retrain, no model-risk cycle, value provable
in weeks, and it is the only path we can *demonstrate* rather than describe.

## KS-1 — what consumes a case when the customer is NOT calling

**This was the largest hole in the first draft and it is the question that ends the pitch:** *"Day 74.
The customer isn't calling. They're at home. What physically happens next?"*

The headline value is an early warning about someone not in contact. The proudest claim is that the
system cannot contact anybody. Stated four minutes apart, **those contradict each other** unless the
consuming process is named.

| | Consuming process | What the issuer builds | Why it works |
|---|---|---|---|
| **1** | **Next-inbound-contact treatment** | **Nothing.** The case sits on the account | The next agent who speaks to that customer, for any reason, opens the call already briefed. Card customers *do* call — the demo's own day-0 call is a decline. HITL-by-absence stays literally true |
| **2** | **Feed their existing proactive retention campaign** | Nothing new, if they run one | Many large US issuers do run outbound retention campaigns. **Confirm the client has one before leaning on this** |
| 3 | Hold for the next servicing touchpoint | Nothing | Weakest — depends entirely on contact frequency |

**Say this on stage:**

> We never contact your customer. We change what your agent knows the next time they do — and in
> cards, they do. If you already run a proactive retention campaign, we change who is on the list.

**Note a US-specific gap versus the earlier UK version of this argument.** The UK draft leaned on the
FCA persistent-debt regime, which *mandates* customer contact at 18 and 27 months — "a conversation the
regulator already requires you to have". **There is no US equivalent.** The CARD Act and Regulation Z
require *disclosures* — the minimum-payment box on the periodic statement, 45-day advance notice of a
significant change such as an APR increase — but a disclosure is not a conversation. **Drop that
argument for the US.** Do not try to translate it.

## What path 1 actually requires — state it unprompted

Naming the hard parts separates a team that has integrated a feature from one that has read about it.

- **Sparsity.** Populated for the scored subset, null elsewhere. Tree models route missing values
  natively; a GLM needs an explicit missing-indicator plus imputation. Solved problem — but it belongs
  in the model documentation, not discovered during validation.
- **Point-in-time correctness — genuinely dangerous for us specifically.** Training must use the
  feature **as it stood on the observation date**, not today's re-scored value. Joining on "latest
  known value" is the classic leakage pattern, and our design deliberately re-scores history.
  **The resolution, said unprompted: training joins `score_at_write`; inference and the operational
  queue use `score_now`.** Retro re-scoring earns its keep in production scoring and the human queue,
  never in the training join. Both are stored fields, so point-in-time is a query, not a rebuild.
- **Measuring lift: uplift at the operating decile, not global AUC.** The business only acts on the
  top slice of the ranked book, so a global discrimination metric answers the wrong question.
- **Champion / challenger.** Their model plus our feature runs as challenger against the production
  champion on the same population, graduated on their own criteria. Standard practice they already
  have — not something we invent.

## US model governance — the regime map

The earlier draft was built for the UK (PRA SS1/23, FCA Consumer Duty, FG21/1, UK GDPR Article 22).
**All of it is replaced.**

| Concern | UK version (discarded) | **US version** |
|---|---|---|
| Model risk | PRA SS1/23 | **SR 26-2**, "Revised Guidance on Model Risk Management", issued **2026-04-17** — joint OCC/Fed/FDIC, applies over **$30bn total assets**. It **supersedes SR 11-7** (2011-04-04) and SR 21-8, and **OCC Bulletin 2026-13 rescinds OCC 2011-12**. ~~SR 11-7~~ **is dead — do not cite it** |
| Third-party/vendor risk | SS1/23 vendor expectations | **Interagency Guidance on Third-Party Relationships: Risk Management**, June 2023 (OCC Bulletin 2023-17, Fed SR 23-4, FDIC FIL-29-2023) |
| Consumer protection | FCA Consumer Duty (PRIN 2A) | **UDAAP** — Dodd-Frank Act **§1031** and **§1036**; plus **FTC Act §5** |
| Vulnerable customers | FCA FG21/1 | **No direct analogue.** The nearest is UDAAP's **"abusive"** prong |
| Mandated conversation | FCA persistent-debt regime | **None. Drop the argument** |
| Automated decisions | UK GDPR Article 22 | **ECOA / Regulation B** adverse action for credit decisions; **CCPA/CPRA** and state ADMT rules for profiling |
| Privacy / secondary use | UK GDPR purpose limitation | **GLBA / Regulation P**, plus **state comprehensive privacy laws** |
| Call recording | Single-party consent, UK | **State two-party/all-party consent laws** — a real patchwork |

### SR 11-7 IS RESCINDED — corrected 2026-09-09, read this before the table above

**The regime map above is out of date and so is the subsection below it.** SR 11-7 was **superseded on
2026-04-17 by SR 26-2, "Revised Guidance on Model Risk Management"** (which also supersedes SR 21-8).
It is **one joint interagency document** from the OCC, the Federal Reserve and the FDIC — not a Fed
letter later paralleled — and **OCC Bulletin 2026-13 rescinds OCC Bulletin 2011-12**. It applies to
banking organizations with **over $30 billion in total assets**.
*(federalreserve.gov/supervisionreg/srletters/SR2602.htm, retrieved 2026-09-09.)*

**Two things it changes for us, one helpful and one not:**

- **Helpful.** The definition of "model" explicitly *"excludes simple arithmetic calculations... as
  well as deterministic rule-based processes and software where there are no statistical, economic, or
  financial theories underpinning their design or use"* (attachment p.3). **The ledger arithmetic is
  a deterministic rule-based process.** Claim the light end of the tiering — but not exemption; the
  half-lives are argued from signal persistence, which a validator may fairly call a theory.
- **Not helpful, and do not misread this one.** Footnote 3, p.3: *"Generative AI and agentic AI models
  are novel and rapidly evolving. As such, they are not within the scope of this guidance."* That is a
  **scope carve-out, not an exemption from model risk**. It means there is no settled supervisory
  playbook for the extractor, so the bank's own AI governance policy governs. **Presenting that to a
  COO as good news reads as evasive.**

The subsection immediately below is **retained as written for its reasoning about vendor obligations
and tiering, which SR 26-2 preserves** — its vendor section requires *"developing an understanding of
the vendor model, including its conceptual soundness, design, development data, and performance"*
(pp.11-12) — **but every instance of "SR 11-7" in it should be read as "SR 26-2", and never spoken as
SR 11-7 on 09-11.** Full treatment in `06-DEFENDING-THE-SCORE.md` §2.

### ~~SR 11-7~~ **SR 26-2**, and why it is lighter than it sounds

*(Reasoning below is retained and still correct; SR 26-2 preserves all of it. Read every "SR 11-7" as
"SR 26-2" and never say the old number out loud.)*

SR 11-7 requires a model inventory, risk-based tiering, **"effective challenge"** — critical
independent review — documented development and validation, and it explicitly extends to
**vendor and third-party models**: a bank must validate a purchased model and must obtain enough
information from the vendor to do so.

**That last clause is about us.** We should expect and welcome it: documented target definition, data
provenance, and a stated **use restriction — feature only, never a standalone decision.**

**But do not overstate the burden, because it scares the buyer.** A retention/marketing feature that
gates no credit and no pricing is a **low-to-moderate tier** model input. It does not attract the
validation intensity of a capital or credit model. The right sentence is: *"your model risk team will
tier this low, and we will give them everything they need to do that."*

### UDAAP is where the vulnerability trap lives

Dodd-Frank's **"abusive"** prong reaches an act that takes **unreasonable advantage of a consumer's
inability to protect their own interests** in selecting or using a financial product.

**Turning a disclosed hardship into a sales trigger is the textbook shape of that risk.** So the
control has to be structural:

> Distress- and life-event-family signals are **not eligible** to feed an offer trigger. They route to
> a duty-of-care review for a human. Only churn-intent-family signals are offer-eligible.

That is a branch in code, not a policy preference — and it is a **strong pitch beat**, not a caveat.

### ECOA / Regulation B — where the line is, and why we stay behind it

Our score influences **retention marketing**, not credit decisions. That keeps it out of adverse-action
territory.

**But note the roadmap trap.** The "credit-line decisions" adjacency — using a prosperity or strain
signal to inform a limit increase or decrease — **crosses the line.** A credit-limit decrease is an
adverse action requiring notice under Reg B, and if it rests on a consumer report, FCRA attaches too.
**Do not let a judge's enthusiasm pull the conversation there.** Say plainly: no signal here gates a
limit, a rate or an approval.

### Fair lending and disparate impact — a real, unresolved exposure

Transcripts encode accent, dialect, English-language proficiency and other proxies for national origin,
age and disability. An extractor tuned on a narrow dialect distribution can systematically under- or
over-detect distress by group.

**We have no evidence either way, and the honest position is to say so — but not as a bare open risk
with no owner, which is exactly what a COO writes down. Give it a gate:**

> Subgroup coverage and false-negative testing is a **gated pre-condition of path 1 go-live**, and it
> needs your segment labels.

### Privacy, consent and call recording — the US patchwork, and do not pretend it is solved

- **GLBA / Regulation P.** Using customer information for a secondary internal purpose is generally
  permissible, but notice obligations and the issuer's own privacy policy govern. **Their
  determination, not ours.**
- **State two-party consent.** A dozen or so states require all parties to consent to recording —
  California, Florida, Illinois, Maryland, Massachusetts, Pennsylvania, Washington and others. A
  national issuer already handles this for recording itself; **the open question is whether recordings
  captured under a quality-and-training disclosure may be reused for an analytics purpose.** That is a
  client-side legal determination. Say so; do not imply it is solved.
- **CCPA / CPRA and the other state privacy laws.** Purpose limitation and opt-out rights around
  profiling and automated decision-making. California's automated-decision-making technology rules are
  the ones to check for current status and compliance dates before making any claim.
- **Illinois BIPA — and here we have a genuine advantage worth stating.** BIPA reaches **voiceprints**
  as biometric identifiers. **We work from transcripts, not audio.** A transcript is not a biometric.
  That is a real reduction in exposure relative to any vendor doing voice analysis, and it is worth one
  sentence on stage.

## The three governance sentences, US version

> Our score is an input to your model, never a decision. A human, or your own supervised model with an
> observed outcome, always sits between our signal and any customer action. Every point traces to a
> verbatim quote, we work from transcripts and never from audio, and the system has no way to contact a
> customer at all — the safety case is that the capability does not exist, not that it is switched off.

## Where we stop, and the five seams that are theirs

```
conversation -> transcript -> extractor -> signal + verbatim quote
    -> ledger (accumulate | decay | re-score, deterministic code)
    -> crossing
        |- case for a human            (path 2 / 4)
        |- feature value to the model  (path 1)
        |- eligibility flag            (path 3)
              -> THEIR EXISTING DECISION -> THEIR EXISTING ACTION
```

**We stop at the crossing.** Naming what is theirs is a feature of the pitch, not a disclaimer:

1. The attrition label definition.
2. The coverage denominator — their book, their contact rate.
3. Feature-store integration and the retrain cycle.
4. The consent and secondary-use determination on call recordings.
5. Fair-lending subgroup testing, using their segment labels.

## What we can prove now, and what we cannot

**Provable today on synthetic data with seeded ground truth:** extractor recall and precision per
family with denominators · that retro re-scoring is real and observable · that zero-conversation
customers show a null state, never a defaulted zero · that the point-in-time query returns the correct
historical value.

**Not provable until a client back-test — say so:** incremental lift on their own model · actual
coverage · subgroup fairness on real demographics · any specific save-rate or dollar lift.

**The line to hold in the room:** *we can prove the mechanism works; only your data can prove it moves
your number.*

---

# 4. The value model — US

## The anchor problem, and what actually replaced the tariff

The pre-reframe UK pitch led with a **published per-case tariff** — the Ombudsman charges a firm a
fixed fee per complaint, win or lose. A number a CEO verifies by clicking a link.

**The US has no equivalent.** Two candidate replacements were tested and **both failed as *published*
anchors:**

| Candidate | Verdict |
|---|---|
| **Re-acquisition cost** — a closed account must be replaced, and card CAC is high | **USABLE, and stronger than first assessed.** No issuer discloses "CAC" as a line item, but two disclose **both a marketing numerator and a new-account denominator**, so it is derivable from primary filings — see the anchors table. **Roughly $430–$550 per new card.** The "~$80" figure circulating online has no traceable primary source and is contradicted by that arithmetic by about 6x. **Do not quote $80** |
| **CFPB enforcement risk** | **Do not use.** As of 2026 the CFPB's funding and headcount are materially reduced (~1,300 staff, down from ~1,700), enforcement principles were rolled back in June 2026, and fair-lending supervision is expected to contract sharply. **Anchoring a value story on CFPB enforcement in 2026 would be read as naive** |

**So the money story is built differently, and the change is an improvement.** Instead of one published
tariff, it rests on:

1. **published market arithmetic** for what an account is worth in revenue terms, and
2. **client-verifiable inputs** for the two numbers that convert that into value.

**Re-acquisition cost now has BOTH a published upper bound and a client number.** State the derived
figure, then hand the precise one back to them: *"your own marketing team knows your number; here is
what your peers' filings imply."* A client cannot argue with their own CAC, and they cannot argue with
Amex's 10-K either.

**Carry the limitation, because a CFO will find it in ten seconds.** Marketing expense covers brand,
retention and cross-product spend — Capital One's own 10-K says marketing *"includes ... promotional
efforts to attract **and retain** customers ... and certain customer incentives, **including
spend-based bonuses**."* So **marketing / new accounts is an upper bound and a blended proxy, not
CAC.** Amex's is the tightest (a card-first issuer disclosing its own denominator); JPMorganChase's is
the loosest (firmwide marketing over card accounts only). **Say "upper bound" out loud every time.**

**And do NOT use "acquiring a customer costs 5 to 25 times more than retaining one."** It traces to a
2014 HBR article that explicitly prefaces it with *"depending on which study you believe"* and cites no
study, dataset or source. It is an assertion, not a finding, and quoting it to a finance audience is a
tell. **The properly sourced adjacent claim is Bain's:** in financial services, a 5% increase in
retention produces more than a 25% increase in profit.

## Published US anchors

| Metric | Figure | Source | As of |
|---|---|---|---|
| Total US credit card balances outstanding | **$1.263 trillion** | Federal Reserve G.19 | Q2 2026 |
| Share of US adults holding at least one card | **78%** | CFPB Consumer Credit Card Market Report | end-2024 |
| Average APR, accounts **assessed interest** | **22.15%** | Federal Reserve G.19 | Q2 2026 |
| Average APR, all accounts | **20.94%** | Federal Reserve G.19 | Q2 2026 |
| Average balance **per borrower** | **$6,610** | TransUnion / Federal Reserve | Q2 2026 |
| Average balance **per open account** | **$2,077** | derived: $1.263T ÷ 608M accounts | Q2 2026 |
| Card **net charge-off** rate | **3.82%** | Federal Reserve **CORCCACBS** ("Charge-Off and Delinquency Rates on Loans and Leases at Commercial Banks"), updated 2026-08-25 | Q2 2026 |
| Card 30+ day delinquency | **2.85%** | Federal Reserve, commercial banks | Q2 2026 |
| Share of card **balances** 90+ days delinquent | **12.92%** | NY Fed Consumer Credit Panel | Q2 2026 |
| **Open general-purpose card accounts** | **608 million** (plus **185 million** private label) | **CFPB Consumer Credit Card Market Report** (pub. 2025-12-30) | year-end 2024 |
| **Account closure rate — general purpose** | **"Between 0.7 and 1 percent of general purpose accounts are closed each month"** → **8.4–12.0% per year** | **CFPB**, same report, §Account Closure, from the Consumer Credit Information Panel (2% national longitudinal sample) | year-end 2024 |
| Account closure rate — private label | **1–2% monthly**, with a spike to **3.4%** in May 2024 | CFPB, same report | 5-yr avg to 2024 |
| **Amex implied gross attrition** | **11.8–12.0%** (FY2025), **11.1–11.3%** (FY2024) | **Derived from primary SEC filings** — 8-K Exh. 99.2 filed 2026-01-30 and FY2023 10-K filed 2024-02-09 | FY2024–FY2025 |
| Inactivity termination floor | **3 consecutive months** is the earliest point inactivity-based termination is permitted | **Regulation Z, 12 CFR §1026.11(b)(2)** | current |
| **Amex acquisition cost per new card, worldwide** | **$500** (2025) · $465 (2024) · $427 (2023) — marketing $6,252 m / 12.5 m new proprietary cards | **Derived from AXP FY2025 10-K**, filed 2026-02-06 | FY2023–FY2025 |
| **Amex, US Consumer Services only** | **$549** (2025) — USCS marketing $3,187 m / 5.8 m US new cards | **Derived from AXP 10-K + Q4'25 deck** | FY2025 |
| **JPMorganChase per new card account** | **$532** (2025) — firmwide marketing $5,531 m / 10.4 m new card accounts | **Derived from JPM FY2025 10-K + 4Q25 release** | FY2025 |
| Card-bank marketing intensity | Card banks spend **1–2% of assets per year** on marketing, about **10x** other banks. Capital One $5.9 bn and Amex $6.3 bn in 2025 | NY Fed Staff Report 1143, *Credit Card Banking* | Mar 2025, rev. Aug 2026 |
| Solicitation volume | Issuers mailed an average of **414 million solicitations per month** across 2023–2024, **+40%** vs 2018–19 | CFPB, published 2025-12-30 | to end-2024 |
| **Rewards cost vs interchange** | Industry rewards ~ **1.57% of purchase volume** against interchange ~ **1.82%**. The six largest issuers' rewards expense was **$67.9 bn** in 2023 | NY Fed Staff Report 1143 | 2023 |
| Retention to profit, financial services | *"A 5% increase in customer retention produces more than a 25% increase in profit"* | **Bain & Company / Reichheld**, *Prescription for cutting costs*, 2001-10-24 (tracing to Reichheld & Sasser, HBR Sept–Oct 1990) | 2001 |
| Gross annual attrition, trade estimate | ~12%, *"half charge-offs, half card members calling to close"* | R.K. Hammer | **2012 data, and the source page could not be retrieved directly (HTTP 403)** |
| Save rate on voluntary closure | 25% average, 75% best practice | R.K. Hammer | **2012–13, provenance NOT directly verified — unverified trade estimate** |

> **Two corrections, 2026-09-09.** The charge-off row previously read **3.70%, "Federal Reserve"**, and
> was often cited in this repo as **G.19**. **G.19 is the Consumer Credit release and publishes no
> charge-off rates at all.** The correct series is **CORCCACBS**, which reads **3.82%** for Q2 2026.
> And **$6,610 is per borrower, not per account** — the table said "per account" and that is a
> three-fold error at the account level: $6,610 × 608M accounts is $4tn against $1.263tn of actual
> balances. **Never put $6,610 in the same sentence as an account count.**

**Three warnings.**

1. **The closure rate has a regulator source now — use it, and know its one weakness.** Three
   independent sources converge on **roughly 11–12% of accounts closed per year, gross**: CFPB's
   0.7–1.0% monthly (primary, 608 M denominator), Amex's 11.1–12.0% implied from its own filings, and
   Hammer's 12% (trade, 2012). **But CFPB's own 2021 and 2023 reports say "about 2 percent of accounts
   are closed each year"** — four to six times lower, and neither report reconciles it with the 2025
   figure (the underlying panel changed). **Quote the monthly figure, and if pressed, volunteer the
   contradiction.** Knowing it exists is worth more than pretending it does not.
2. **Gross closure is not voluntary closure, and the split is NOT published.** CFPB *defines*
   voluntary versus involuntary closure and gives **no numeric split**. The only split available is
   Hammer's *"about half"* — a 2012 trade estimate. So voluntary attrition is roughly **4–6%** on that
   basis, and every use of it must say the split is a trade estimate, not a regulator figure.
3. **Do not conflate accounts, active accounts and cardholders.** An ex-card-book executive knows the
   difference cold. Open general-purpose accounts is 608 M; that is not cardholders and not active
   accounts.
4. **The save-rate row is the weakest thing in this table.** 25%/75% is a 2012–13 trade estimate whose
   source page **could not be retrieved** — it is the only published US save-rate benchmark found
   anywhere, and it should be labelled as an unverified trade estimate every single time. Better still,
   do not lead with it: the save rate is the link we refuse to fill.
5. **The 90+ delinquency figure is share of balances, not accounts.** Different denominator from the
   30+ figure. Do not put them side by side without saying so.
6. **No US issuer publishes an attrition rate.** An EDGAR full-text search returns "card member
   attrition" in **14 filings, all American Express**, and all qualitative. That is itself a usable
   line: *"nobody in your industry publishes this, which is why the only honest version of the number
   is yours."*

## What an account is worth — published arithmetic, and where it stops

> $6,610 average balance × 22.15% APR ≈ **$1,464 per year of gross interest** on an
> interest-assessed account.

**That is gross interest, not margin, and the gap is large.** Subtract cost of funds, credit losses
(charge-offs are running at **3.82%**, roughly **$253** per year on a $6,610 borrower balance), rewards cost, and
servicing and operating cost.

**Do not do that subtraction on stage and present the result as their margin.** Show the structure,
then hand it over:

> That is what the account earns. What it *makes* is your number, not ours — and quoting gross interest
> as value per saved customer is the single most common vendor error in this space.

## The value chain, multiplied through

**Multiply it yourself, first, out loud.** The UK draft built this chain and never multiplied it, which
invited the worst moment available: *"I'll do your arithmetic."*

Central case, a plausible large US issuer. Every row tagged.

| Step | Value | Running total | Owner |
|---|---|---|---|
| Card accounts | 5,000,000 | 5,000,000 | **[CLIENT]** |
| × **voluntary** attrition 5% | | 250,000 lost/yr | **[CLIENT]** — CFPB gives **gross** closure of 8.4–12%/yr; the voluntary share is **not published**, and the only split available is a 2012 trade estimate of "about half" |
| × conversation coverage 40% | | 100,000 | **[CLIENT]** |
| × share voicing a leading signal 30% | | **30,000 surfaced** | **[OURS]** shape, **[CLIENT]** scale |
| | | **= 0.6% of the book** | |
| × incremental save rate | **[REFUSED]** | — | **the client's back-test** |
| *at 10%, illustrative only* | | 3,000 saved | |
| × annual margin per account, *$300 illustrative* | | $0.90M | **[CLIENT]** |
| **+ avoided re-acquisition**, 3,000 × CAC, *$250 deliberately conservative* | | **+$0.75M** | **[CLIENT]**, against a primary-derived upper bound of **$427–$549** |
| | | **≈ $1.65M gross per year** | |

**Say the small number before they find it: the addressable population is under 1% of the book.** Four
multiplicative haircuts do that, and each haircut is a fact about their book, not about our accuracy.

**Then say what makes it worth doing anyway** — and this is the strongest line in the money beat:

> Reading every conversation costs **$1.58 per thousand**. At ten million conversations a year that is
> about **$16,000**. Against a couple of million dollars of value on assumptions you control. **The
> question is never whether this is affordable — it is whether the save rate is real, and that is the
> one number we refuse to invent.**

**Note what the re-acquisition leg does.** It roughly doubles the value of a save, because a lost
account costs twice — the margin you stop earning *and* the cost to replace it. That leg is entirely
[CLIENT INPUT], which is why it belongs in the chain rather than in a headline.

## The three links a finance executive will ask about

1. **False positives.** Reading 100% of conversations surfaces more candidates than a keyword system —
   that is the entire pitch. It also produces more wasted retention contacts unless precision holds.
   We can measure our false-positive rate; only they can price a wasted contact.
2. **Cannibalisation.** A save rate measured without a control group counts customers who would have
   stayed for free. **This is exactly why the save-rate link is refused rather than assumed** — and the
   cost *increases* with earliness, which the narrative must not pretend otherwise.
3. **Margin, not revenue.** See above.

## Why refusing the save-rate link is a strength

It is the one number in the chain that cannot be derived from any public source, because it depends on
their retention process, their offer menu, their agents and their customer base — none of which we
observe.

**A vendor who fills it in anyway is not giving a CEO information. They are giving a CEO a number
engineered to look large.** Both judges have been on the receiving end of one.

The chain is complete except that link, and they can close it with a held-out test on their own
back-book. **That refusal is what makes every other link credible.**

## Coverage lift — the trap

The temptation is the desk table: retention **1/20 → 16/20**. **It was measured on a generic
retail-banking corpus with zero credit-card vocabulary.** Mechanism evidence only, labelled. See
section 5.

## Sensitivity — the honest version

Every **[CLIENT]** cell is a placeholder range, not a claim about any real issuer.

| Link | Pessimistic | Central | Optimistic |
|---|---|---|---|
| Card accounts | 1,000,000 | 5,000,000 | 20,000,000 |
| Voluntary attrition *(CFPB gross closure is 8.4–12%; voluntary share unpublished)* | 4% | 5% | 6.5% |
| Conversation coverage | 20% | 40% | 60% |
| Share voicing a leading signal | 15% | 30% | 45% |
| **Incremental save rate** | **0%** | **[REFUSED]** | **[REFUSED]** |
| Annual margin per account | $150 | $300 | $600 |
| Avoided CAC per save *(primary-derived upper bound $427–$549)* | $100 | $250 | $500 |

**The save-rate row is deliberately empty. Multiply everything else by zero and net value is zero,
leaving only the cost lines** — which is the correct answer until they supply that figure or run a
back-test.

**What collapses the model to zero:** their retention team already catches these customers another way,
or offer cost exceeds margin protected. Both testable. Say so.

## The one-slide money story

> **Three published facts. There are 608 million open general-purpose card accounts in the US, and
> the CFPB says between 0.7 and 1 percent of them close every month — call it 8 to 12 percent a year.
> Americans carry $1.263 trillion at 22.15% APR on balances assessed interest — about $2,077 per open
> account. And charge-offs are running at 3.82%.** *(CFPB Consumer Credit Card Market Report,
> published 2025-12-30; NY Fed Q2 2026; charge-off rate CORCCACBS, updated 2026-08-25.)*
>
> *(Corrected 2026-09-09: this script previously said "$1,464 a year of gross interest on an average
> $6,610 balance" and "3.70% ... Federal Reserve G.19". **$6,610 is per borrower, not per account**,
> and **G.19 publishes no charge-off rate**. Do not restore either.)*
>
> **And here is the gap that matters: nobody publishes how much of that closure is voluntary. Not the
> regulator, not a single issuer 10-K. Which is the first sign that this is a number managed
> internally and never measured well.**
>
> **In that market, the customers you least want to lose are the profitable ones who leave quietly.**
> And when they do go, they usually say something first — on a call, weeks before they close. Today
> that call is read once, dispositioned, and thrown away.
>
> **A closed account costs you twice: the margin you stop earning, and what you pay to replace it.**
>
> **The chain, out loud:** your book × your voluntary attrition rate × your conversation coverage × the
> share of leavers who say something first — we measure that — × **your** incremental save rate ×
> your margin plus your acquisition cost. On a five-million-account book that is roughly 30,000 names,
> **six tenths of one percent**, and about **$1.65 million a year** on assumptions you control.
>
> **Two numbers we will not invent: your incremental save rate net of customers who'd have stayed
> anyway, and your margin per account. Any vendor who hands you those made them up.**
>
> **Reading every conversation costs $1.58 per thousand — about $16,000 a year at ten million
> conversations. Affordability is not the question. The question is whether the save rate is real, and
> that is exactly the thing your back-test settles and we refuse to guess.**

## Cheap shots to avoid

- **Any UK figure.** No pounds, no Ombudsman, no FCA, no UK Finance.
- **The unsourced ~$80 CAC.** It has no primary origin. Excluded, not laundered.
- **The 2012–13 attrition and save rates without their date.**
- **Gross interest as value per saved customer.** Interest income is not margin.
- **Interchange revenue as margin**, or ignoring rewards cost.
- **Ignoring cannibalisation** — a raw save rate with no control group counts free wins.
- **$1.263 trillion × an invented capture rate.** A market-size number times a made-up percentage is
  not a business case.
- **Leaning on CFPB enforcement risk.** In 2026 that reads as not having checked.
- **Double-counting a customer across two desks.** One saved customer, not two.
- **Leading with the optimistic column.**

---

# 5. Claims triage — what we may and may not quote

**Read this before quoting any number on 2026-09-11.**

The reframe does not change the code. It changes what the existing measurements are *evidence for*.

## The sentence that has to be said out loud

> **Every internal, own-measured number in this repo — coverage, recall, agent verdicts, routing,
> cost, the deployed AWS proof — was measured on a generic retail-banking corpus with no
> credit-card content anywhere in it.**

Balance checks, standing orders, mortgage statements, branch hours, gym memberships. **Zero fragments
mention a card product, APR, credit limit, minimum payment, rewards or an annual fee.**

What carries into a card story is the **mechanism** and the **external market facts**. What does not
yet exist is a single measured number that is both about attrition *and* about credit cards.

**Say it yourself, immediately after the demo and before the money beat.** Not in beat 1 — told to two
finance judges before anything has been shown to work, it produces the sentence *"they admitted none
of their numbers are about credit cards"*, which is then the only thing they remember. Sequencing is
not hiding; it still arrives before any quotable number, which is the actual obligation.

## Three claims that are FALSE as card evidence

### 1. The four-desk coverage table

| Desk | Keyword reader | Model reader |
|---|---|---|
| Complaints | 0 / 20 | 20 / 20 |
| Vulnerability | 0 / 20 | 19 / 20 |
| Retention | **1 / 20** | **16 / 20** |
| Collections | 9 / 20 | 10 / 20 |

Measured 2026-08-31, `tools/reader_coverage.py`, on four generic trajectories in generic retail-bank
prose. **A true measurement of a different corpus than the one being pitched.** The retention row is
the most tempting number in the repo for an attrition story and the most dangerous.

**Permitted:** *"on our generic corpus the model reader surfaced 16 of 20 retention cases where a
keyword reader surfaced 1 — mechanism evidence, and the card-specific run is what we do next."*
**Forbidden:** any sentence where 16/20 is the card-attrition number.

### 2. The Ombudsman money lead — now dead entirely, not merely relabelled

The pre-reframe pitch led with the UK Financial Ombudsman Service tariff. **The market is now the US,
and there is no US equivalent per-case regulator fee.** This is not a claim that needs a caveat; it is
a claim that has to be **removed and replaced.** See section 4 for what replaces it.

Anything in this repo still quoting the FOS tariff, UK Finance, the FCA, PRA SS1/23 or the FCA
persistent-debt regime as the live argument is **stale UK work.** Do not carry it into the room.

### 3. The submission's own committed positioning

> *"None of these is the headline; the layer is."* — `docs/sources/submission-ear-on-every-call.md:111`

Leading with one attrition score is the **literal negation** of that sentence — the opposite design
philosophy from what was submitted to the committee on 2026-07-24.

**But do NOT volunteer this on stage.** Venkat and Farhan did not write that brief and are unlikely to
have it in mind. Quoting your own contract against yourself to a *commercial* audience imports a
governance problem into a sales pitch and burns 30 seconds of 18 minutes.

**On stage, one non-defensive clause:** *"we've narrowed from the layer to its strongest single view
for this sprint."*
**Have the full answer ready** if a committee member is present: *"our brief said no single view should
have to carry the pitch; we're testing whether the strongest one can anyway — a deliberate experiment
this sprint."*

## What is genuinely domain-independent — the safe core

Stand the pitch on these. None depends on what the conversations are about.

- **Never-discard versus reconcile-to-current-truth.** A statement about an algorithm.
- **Retro re-scoring, and that it is mathematically impossible under a plain count.** The score
  function is concave, so "an entry is worth more later" cannot happen without the weighting
  machinery. **239 / 485** multi-signal entries worth more now than at write; **0 / 485** under a
  plain count.
- **The deployed pipeline agrees with local to the last digit, is idempotent under re-feed, and
  survives one poison record without corrupting the batch.** Plumbing does not know its subject.
- **Human-in-the-loop by absence of any outbound contact surface.** A structural property of the code.
- **The evaluation discipline** — nothing from one dataset, every rate with its denominator, losses
  beside wins, a chance gate declared and failed openly. This is what makes the reframe read as rigour
  rather than a rewrite.
- **908 tests** (903 pass, 5 skip), ruff clean, separation guard over 45 modules.

## The reader is the product — say the model's numbers, not the lexicon's (2026-09-09)

**Standing instruction from Ravi, 2026-09-09: the keyless lexicon is a fallback, not the story.** This
entry is a generative-AI product and the evidence quoted on stage should be the model's.

**The one table that makes the case**, measured on the same 282 conversations against the same planted
ground truth, model = Claude Haiku 4.5 on Bedrock (what the deployed system runs), lexicon = the
hand-tuned 26-regex fallback:

| Family | lexicon | Haiku 4.5 |
|---|---|---|
| churn intent | 16 / 77 | **40 / 77** |
| complaint escalation | 1 / 65 | **60 / 65** |
| life event | 9 / 68 | **50 / 68** |
| financial distress | **33 / 72** | 27 / 72 |

*(`artifacts/runs/reader-coverage-20260809-1ee962fd608f-offline-model-pt20-replay.json`.)*

**The distress row is a loss and it is published.** A regex is good at fixed phrases — "I lost my job"
— and that is most of what the distress family looks like. **It is also the family a pre-delinquency
story would depend on**, which is one more reason that story was withdrawn.

**How to talk about keylessness without sounding like a regex vendor:** it is a *reproducibility*
property for an auditor, never a product claim. *"Every number replays from a committed cache with no
key, so you can check it yourself — but the system runs on a model."* **Never open with "it works
offline."**

**Two things are still measured only with the lexicon, and they are the headline mechanism claims:**
the arm comparison (`full-ledger` vs `window3-top2`, **30-0-0**) and the mechanism ablations. **The
keyed 10-seed re-measurement ran on 2026-09-09 ($10.66) and did not change that** — it settled the
reader decisively and was underpowered on the arms, for reasons the next section sets out. **30-0-0
remains an offline-reader result and must be described as one.**

## The keyed re-measurement — 2026-09-09, $10.66, and what it did and did not settle

**Ravi raised the budget to $10-15 on 2026-09-09 to put the gen-AI reader behind the numbers.** This
is what it bought. **10 seeds × 200 customers, 6,990 conversations, one model call each, Claude Haiku
4.5 on Bedrock, $10.6586** (plus a $0.21 pilot). Invocation:
`earshot run --seed 1..10 --customers 200 --extractor model`, cache
`artifacts/cache/extractor-cardstory-haiku.jsonl`.

### What it settled: the reader, decisively

| | offline lexicon, 10 seeds | **Haiku 4.5, 10 seeds** |
|---|---|---|
| **extraction recall** | **0.2435** (min 0.2202, max 0.2819) | **0.6549** (min 0.6243, max 0.7003) |
| quotes not verbatim | n/a (regex quotes the span) | **11** of 5,736 emitted signals |
| quotes relocated | n/a | **2** |
| unparsable replies | n/a | 11 of 6,990 calls (0.16%) |
| cost per 1,000 conversations | $0 | **$1.524** |

**The model reader finds 2.7× more of the planted evidence than the hand-tuned 26-regex lexicon, on
the same corpora, against the same answer key, across ten independent datasets.** That is the
gen-AI-led number this run was bought for, and it is the one to quote.

**And the honest counterweight, which must be said with it: it also fires far more that was never
planted — 2,818 unplanted extractions against the lexicon's ~40 per seed.** Roughly seven times as
many. That mirrors the CFPB result exactly (0.8214 strict recall against 0.0357, at **8× the
false-positive rate**), so it is a stable property of the trade, not an artefact. **Better reader,
noisier reader.** Whether that is a good trade depends on the operating point, and for a ranked queue
over fixed capacity it usually is.

### What it did NOT settle, and it was never going to

**The pre-registered primary did not reproduce.** `full-ledger` vs `window3-top2` came out **5-4-1,
p=1.00** across the ten keyed seeds — against the published **30-0-0** — and `full-ledger` sits 7th of
9 arms by mean recall (0.1111), above `random-rank` (0.0863) but below five simpler arms.

**Do not read that as the accumulation claim failing under a real reader.** A free control settles it:
running the **offline** reader — the exact reader that produced 30-0-0 — at this same scale gives
**4-3-3, p=1.00**. **The scale is the confound, not the reader.** At 200 customers the queue is 20
names deep and every arm sits on top of chance; the published result lives at 1,500 customers and a
150-deep queue, where the arms separate.

**Why it was not run at the published scale: wall-clock, not money.** 30 seeds × 1,500 customers is
~52,000 sequential model calls — hours of inference, and the extractor makes one call per conversation
with no safe parallel path (pointing two model runs at one cache is the most expensive mistake this
project has made). **So `30-0-0` stands as an offline-reader result, unchallenged and un-corroborated,
and that is exactly how it should be described.**

**Say it this way if asked:** *"The accumulation comparison is measured with the cheap reader because
that is the only reader we can afford to run thirty times. We re-ran it with the real model at a
smaller scale and it was inconclusive — and so was the cheap reader at that same smaller scale, which
tells you the experiment ran out of power, not that the result went away."*

### The finding that changes a build decision

**With a model reader, the confidence float is the LEAST load-bearing mechanism in the ledger.**
Top-20 overlap against the full ledger when each mechanism is removed, 10 keyed seeds:

| mechanism removed | model reader | *(offline lexicon, 30 datasets)* |
|---|---|---|
| **confidence weighting** | **89.5%** — least disruptive | *80.0% — joint most* |
| cross-channel | 89.0% | *92.7%* |
| escalation | 86.5% | *100.0% — inert* |
| decay | 85.0% | *92.4%* |
| corroboration | **82.0%** — most disruptive | *79.8% — joint most* |

**The ordering flips between readers, and the reason is measurable.** The lexicon's confidences are
hand-set per-cue constants that spread across a wide range, so they carry real ranking information.
**The model's do not: 5,112 emitted values take only 21 distinct rounded values, ten of which cover
95.3%, with 0.85 alone accounting for 28.4%.** A number that lands on the same ten values cannot
reorder much.

**This makes the §3 recommendation nearly free, and it is now measured from both directions:** the
distribution says the float is a menu, and the ablation says removing it entirely only moves 10.5% of
the queue. **Bucketing to three tiers is a formality, not a trade-off. Do it.**

## The chance gate — complete it or do not raise it

*"The published chance gate we fail at p=0.076"* tells a non-technical CEO **it doesn't work**.
Incomplete disclosure costs more than either full disclosure or silence.

> Against a random ranker on the thin-evidence stratum: **18 wins, 8 losses, 4 ties across 30 seeds.**
> Directionally positive, **underpowered at 30 seeds**, and published as a failure because our
> pre-registered bar was statistical significance and we did not clear it.

## Numbers that carry, need relabelling, or must be re-run

| Claim | Verdict |
|---|---|
| CFPB reader benchmark: strict recall 4/112 offline vs 92/112 Haiku; any-type 8/83 vs 81/83; FP 10/488 vs 78/488 | **RELABEL — and check the sample.** This is **real US customer complaint language**, not our authored corpus, which makes it the strongest carry-over candidate *and* it is US-sourced. **Whether the 150-narrative sample is card-heavy is unverified.** Ten minutes to check, free, and if it is card-heavy this becomes the best card-specific evidence in the repo |
| Full-ledger vs `window3-top2`: 30-0-0, p<0.001 | CARRIES qualitatively / RE-RUN numerically |
| Retro direction 239/485 vs 0/485 | **CARRIES** |
| Nova Lite vs Haiku: 181/282 vs 177/282; $0.0982 vs $1.58 per 1,000; 10 vs 0 non-verbatim quotes | CARRIES qualitatively / RE-RUN numerically |
| Extraction fidelity 617/2,700; decoy FP 9/470 | RE-RUN |
| Agent verdicts 29/50 / routing 27/48 | RE-RUN — and routing is structurally mismatched to a one-score product |
| Deployed `dev` vs `demo`: 34 vs 103 entries, 1 vs 9 cases | CARRIES as infra / RELABEL the counts |
| Cost $1.58 per 1,000 | CARRIES to order of magnitude / RE-MEASURE for precision (a card prompt runs longer) |
| Streamed demo: 130 conversations, 103 signals, 9 crossings, $0.4792 | RELABEL — re-record for a card story |
| Anchor metric: retention lift vs matched control | **NEVER BUILT** — and it now sits directly under the one metric being sold |
| Two dry runs | **ZERO DONE** |

## The re-run list — minimum credible set is about $0.45

**Remaining budget is about $9.55 of $12** (~$2.45 spent as of 2026-09-03, not re-verified since).

| | Item | Cost | Buys |
|---|---|---|---|
| **A** | Author 5-10 US-card churn fragments into `corpus_lexicon.py` | **$0** | **Structurally required.** The only way anything below becomes honestly card-flavoured |
| **B** | `earshot sweep --seeds 30 --customers 1500` | **$0** | First preliminary card recall and chance-gate read |
| **C** | `tools/reader_coverage.py --reader both --per-trajectory 20` | **~$0.45** | **The most pitch-relevant number available** |
| D | `tools/verdict_accuracy.py --provider bedrock --per-arm 25` | ~$1.53 | Investigator judgement on card evidence. Next day, not overnight |
| E | `tools/routing_accuracy.py` | $0 | Gated on the one-desk-vs-four product decision |
| F | Model coverage over all 8,429 conversations | $13.96 | **Exceeds remaining budget** |
| G | 10-seed keyed sweep | ~$10 | **Declined 2026-09-03. Do not re-propose** |

**A is not optional and A comes first.** Running C, D or E without authoring card content produces
*the same generic numbers with a new label* — precisely the failure this section exists to prevent.

## Landmines in the code

- **`TRAJECTORY_TEAM` (`src/earshot/schema.py`) and every importer.** `tools/routing_accuracy.py`,
  `core/accounts.py` and `tenants.py` assume the same four slots; `agent/schemas.py` closes
  `OwningTeam` to that exact `Literal`. **Decide the product shape before touching it.**
- **Separation-guard exemption caps are at their ceiling** — `_CORPUS_SIDE` 4/4, `_EVALUATION_SIDE`
  3/3, `_TOOLS_EVALUATION_SIDE` 3/3. Adding a new module trips the guard. **Extend the existing files
  instead.** Raising a cap is a decision the tests exist to force.
- **The two thresholds disagree on purpose (D-027)** — a fixed 0.60 cut in `aws/ingest.py`, a
  budget-derived top-K in `cli.py`. A pitch about "the score consumed by an existing model" invites
  exactly the merge D-027 forbids. **State which one any delivered feature value is, every time.**
- **Per-type half-lives were tuned for retail-bank pacing.** Retuning them after seeing which numbers
  look better is the banned move D-020 named once already.
- **The four `SignalType` values are hardcoded across five-plus modules** plus the separation test's
  literal-string table. Adding a family is a cross-cutting refactor, not a config edit.
- **The fragment-pool ceiling caps arc length.** Adding fragments will likely move the recall-band pin
  in `tests/test_separation.py` — expected and required, but move it deliberately with a written
  reason, never by silencing the test.
- **Cache discipline.** Editing prompts changes `prompt_sha`, which is already in the cache key, so
  that part is safe by construction. The procedural trap stands: **never point two live model runs at
  one cache path.**

---

# 6. The red-team record

An adversarial pass on 2026-09-09 attacked the first draft in the voice of a CEO, a COO, and a hostile
ex-card-book propensity modeller. **This section exists so the fixes are not silently reverted.**

| # | The attack | What changed |
|---|---|---|
| **KS-1** | *"Day 74. The customer isn't calling. They're at home. What physically happens next?"* The headline value is an early warning about a silent customer; the proudest claim is that we cannot contact anybody. **The value beat and the safety beat contradicted each other four minutes apart** | Answered unprompted: **next-inbound-contact treatment** — the case sits on the account and briefs the next agent who speaks to them. Card customers *do* call. Keeps HITL-by-absence literally true, requires the bank to build nothing |
| **KS-2** | *"I'll do your arithmetic."* Four multiplicative haircuts put the addressable population **under 1% of the book**, and nobody had multiplied the chain through | The money beat now **multiplies it through first, out loud**, and the money lead is rebuilt on US re-acquisition cost — see section 4 |
| **KS-3** | *"A customer quoting a rival's 21-month offer has already shopped, and a balance transfer needs a hard pull — half of them are already approved."* Aimed at the exact signal that opened the case | Taxonomy split into **leading-the-decision vs leading-the-event**; the demo crossing re-cut to fire on rewards friction plus promo-expiry instead of a competitor mention |
| **KS-4** | *"The people you can score are the people who already generate a record, and the people you say I'm blind to are the ones you have nothing on. Which is it?"* | **The invisible-third opener is cut.** The claim is now the smaller true one — *of the leavers who do speak to you, you learn on the last conversation; we learn on the first* |
| **KS-5** | *"Who picked day 74?"* 58 = 132 - 74, both authored fixtures, and the docs forbade speaking illustrative numbers then scripted exactly that | **Headline moved to latency** — their model refreshes monthly, ours moves when the transcript lands. Structural and unattackable. 58 days survives only as a labelled illustration |
| **KS-6** | *"You told me the score rewrites history, so the thing you just demoed is the thing I have to switch off"* | Answered unprompted: **training joins `score_at_write`; inference and the queue use `score_now`** |
| **KS-7** | *"What's the invoice?"* Eight documents contained a cost of inference and **no price, no buyer, no contract shape, no duration** | **The project moved to beat 1** — named buyer, fixed-fee back-test, pre-registered criterion, explicit walk-away |
| **KS-8** | *"Verint and NICE already run intent detection on 100% of my calls. What are you that they aren't?"* And beat 2 volunteered "183 lines of Python", received as *"so there's no product here"* | Answer added: incumbents **classify per interaction and reconcile to current truth**. We add the persistent ledger, per-family decay, corroboration, retro re-scoring and the point-in-time query. **Stated as a real feature set and explicitly not a moat.** Line count deleted |

## The second pass — 2026-09-09, KS-9 onward

A second adversarial pass ran the same three voices against the revised draft, plus a repo audit and a
governance review. **The eight fixes above were not reverted.** New ground:

| # | The attack | What changed |
|---|---|---|
| **KS-9** | *"I'll do your arithmetic — again."* **The value chain has no false-positive leg.** Every haircut applies to leavers; the ~1.9M conversing non-leavers have no number attached, and the annual fee posts on every account every year. **Precision is 100% by construction.** Distinct from KS-2: that said the population was small, this says the number is wrong | **A third refusal added to beat 5** — precision is unmeasured and multiplies against the save rate — and the escape to path 2: a ranked queue over fixed capacity needs *ranking*, not precision. The $1.65M is now stated as a gross ceiling or not at all |
| **KS-10** | *"You opened with 'moves the moment the transcript lands' and ninety seconds later sold me a feature in my monthly model."* **The headline claim dies on the path being sold** | Beat 4 now resolves it out loud: **latency is what path 2 buys, information is what path 1 buys.** Path 2 is the pilot, path 1 the destination |
| **KS-11** | *"Your score depends on an LLM reading a transcript. What happens when the model is retired?"* **Not answered anywhere in the folder** — and the model-emitted `confidence` float is a direct multiplier in the score (`memory.py:99`), uncalibrated, sharing a field with the rule engine's hardcoded constants | **`06-DEFENDING-THE-SCORE.md`**, the whole document. Fingerprint not determinism; bucket the float; the Nova-vs-Haiku swap as a *demonstrated* migration |
| **KS-12** | *"Callers-only isn't a coverage gap, it's a population-validity defect"* — selection is endogenous to the outcome, and §6's own stated mitigation ("report performance inside *and outside* the scored population") **cannot be computed**, because outside it there is no score | Concede fast, fight only on **content-of-call vs fact-of-call**, and offer the three-model falsifier. **The "report outside" promise must be dropped or restated** — it is currently a commitment we cannot keep |
| **KS-13** | *"CCPA deletion. Your ledger never discards anything — you just showed me the retro column that proves it"* | **No answer exists.** Verified 2026-09-09: `memory.py` has no delete, purge or forget method. Named as an unbuilt seam in the playbook. **Do not improvise this one on stage** |
| **KS-14** | **Two citation faults.** "3.70% charge-offs, Fed G.19" — G.19 publishes no charge-off rates; and "$6,610 average balance" beside "608 million accounts" is a per-borrower figure standing in for a per-account one | Both corrected in beat 1. $1.263T ÷ 608M = **$2,077 per open account**; charge-offs **3.82%** (CORCCACBS, updated 2026-08-25) |
| **KS-15** | *"You said distress signals are structurally blocked from feeding an offer — show me the branch"* | **There is no branch, because there is no offer surface to block.** Restated as routing (`schema.py:35-40`) plus absence — which is the stronger claim anyway |
| **KS-16** | *"SR 11-7?"* — cited twice in the folder, **rescinded 2026-04-17** | Corrected to **SR 26-2 / OCC 2026-13** throughout §3 and the playbook |

**And one finding that is not an attack:** the CFPB gold set is **55/150 credit-card narratives**, so
the first card-specific measured numbers now exist — including the uncomfortable one, **churn intent
1/8 on card documents**. See the honesty beat in `01-THE-STORY.md`.

## The deepest structural flaw — understand it, do not just patch it

**The scored population is close to the complement of the population the first draft called invisible.**

1. The opener defined the blind spot as silent, eventless departure.
2. The product scores **only customers who have a recorded conversation.**
3. Card servicing contact is driven by **friction** — declines, disputes, fraud, fee queries, payment
   problems. A satisfied transactor drifting to a better rewards card has no reason to call, ever.
4. So the scored population is **enriched for friction and distress and depleted of exactly the silent
   attriters** the opener promised to reveal.

**Two mitigations are real and neither closes the gap:** card contact is substantially *transactional*
rather than complaint-driven (the demo's own day-0 call is a declined transaction, which loyal
transactors experience too), and some contact is driven by servicing obligations rather than
self-selection.

**Consequence, accepted rather than argued away:** the product cannot claim to illuminate silent
attrition. It converts conversations already had and already discarded into an earlier, ordered read on
**the leavers who do speak.** Smaller, true, still saleable.

**And the measurement to commit to in the back-test** — ~~report performance separately inside and
outside the scored population~~ **corrected 2026-09-09 (KS-12): that is not computable.** Outside the
scored population there is no score, so there is no performance to report. It was a commitment we
could not keep, aimed at the one reader most likely to try to collect on it.

**What is computable, and is what to commit to:**

1. **Coverage among actual leavers** — not among the book. If leavers are over-represented among
   people who call, that is a strong finding and it is cheap to compute. If they are
   under-represented, we need to know before the client does.
2. **Their model's lift with vs without our feature**, on the scored population only.
3. **The base-rate difference** between the scored and unscored populations — which *is* computable
   from their own label alone, needs nothing from us, and is the honest way to size the selection
   effect.

**And concede the limit rather than engineering around it:** a feature built from conversations can
never be validated on customers who never had one. That is true of every conversation-derived feature
ever built, and saying so is cheaper than being shown it.

## "Earlier" is worth nothing without a differential save rate

The story asserts the available lever changes — fee waiver or product change at day 74, a retention
offer to someone already walking out at day 132. Plausible. **Zero evidence.**

Worse: the only save-rate figures anywhere in this research describe the **inbound save desk** — the
day-132 lever. **The evidence base supports the intervention the pitch argues against.**

And the earlier lever carries two costs the narrative did not price: **cannibalisation** (a waiver to a
grumbler who was staying — and this *increases* with earliness) and **salience** (raising the question
with an undecided customer).

**The expert framing, stronger than "58 days is the product":**

> We move the detection point. **You decide the treatment point** — and we will help you find it. The
> optimal moment is not the earliest detectable one; it is where the product of leaving-probability and
> marginal save-probability-per-dollar peaks. That is an empirical question your data can answer.

## Disclosure triage — honesty that earns trust vs unforced error

The house style is right that stated losses buy credit. These are the ones that did not.

| Disclosure | Verdict |
|---|---|
| "183 lines of deterministic Python" | **STOP.** Keep *"the score is arithmetic, not model output"* |
| Bare "7/132 ours, 10/132 theirs" | **KEEP, REFRAME.** Unaccompanied it says the incumbent wins more often, and it is misleading *against us* — disjoint-catch counts, not a head-to-head |
| Chance gate failed, p=0.076 | **KEEP, COMPLETE IT** — 18-8-4 at 30 seeds, underpowered, failed against a pre-registered significance bar |
| Contradiction with our own submitted brief | **STOP VOLUNTEERING, move to prepared Q&A** |
| "No card-specific number exists" | **KEEP, RE-SEQUENCE** to immediately after the demo |
| "Not a calibrated probability" | **KEEP AS IS.** Pure gain with the modeller, costless with the other two |
| "No outbound contact surface exists" | **KEEP — but always attached to KS-1's answer** |
| Bias exposure, "no evidence either way" | **KEEP, GIVE IT A GATE** — subgroup testing is a gated pre-condition of go-live and needs their segment labels |
| $1.58 per 1,000 as the money beat's strong number | **DEMOTE to Q&A.** Affordability is not the objection; value is |
| The no-balance-accounts statistic | **CUT.** A statistic needing three protective sentences is not earning its place |
| Five adjacent use cases with status labels | **CUT FROM STAGE, move to Q&A.** Breadth reads as unfocus to a CEO deciding fundability |

## What the panel could not check

- The literal text of `prompts/extractor/v1/`, `memory.py`, `config.py`, `extract_lexicon.py`.
  *(A separate consistency audit did verify the scoring formula, the half-life defaults, the four
  stored ledger fields, the two thresholds and the separation-guard caps against the code, and found
  them accurately stated.)*
- Whether the 18-8-4 chance-gate result sits on the same measurement now used for the primary.
- Base rates for annual-fee objection at renewal — the claim that family 3 has the worst precision is
  **reasoned from mechanism, not measured.**
- Whether the CFPB 150-narrative gold set is card-heavy. **Still open, still ten minutes, still free,
  and now more valuable because it is US data.**
---

# 7. Appendix — the UK complaints variant, kept as a footnote

**Settled 2026-09-09: the pitch is the US attrition story. This appendix is the footnote.** For two
days there were two competing scripts for the 09-11 gate — this folder and a UK-market script leading
on the Financial Ombudsman tariff. Ravi cut it: **US attrition runs, UK complaints is retained as an
appendix.** The full UK script stays in git at `docs/gates/2026-09-11-sprint-review.md`, superseded
and bannered; what is worth carrying is below.

**Why it is kept at all, and it is not sentiment.** The UK variant owns **the one number this pitch
does not have: a published per-case tariff.** Everything in the US money beat is a chain of
client-supplied inputs with an admitted false-positive hole (KS-9). The UK number is a price list.
**If someone asks "is there anywhere this has a hard number rather than a model?", this is the
honest answer, and it is a good one.**

## The number

**The UK Financial Ombudsman charges a respondent firm £650 per case when a complaint is upheld
against it and £475 when it is not — the firm pays either way**, capped at £680 against a £2,000
annual allowance
([Financial Ombudsman Service, case fees](https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/case-fees)).
From **2026-04-01** the largest firms are billed **quarterly in advance on expected volumes**
([FOS consultation, 2025-08](https://www.financial-ombudsman.org.uk/files/324663/2025-08-Differentiated-case-fee-consultation.pdf)),
which makes it a forecastable line item a COO already owns rather than a contingent cost.

**Volume:** the Ombudsman took **214,600 new complaints in 2025/26**, down ~30% from **305,700** the
year before; **credit cards alone were ~22,800**
([FOS annual complaints data 2025/26](https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/our-insight/annual-complaints-data-and-insight-2025-26)).

**The arithmetic, with no invented input:** per **1,000** complaints stopped before referral,
**£650,000 in case fees alone** — before redress, handling time or remediation. The multipliers on top
are the client's, not ours.

## Why this pairing is unusually strong, and why it still lost

**It is the only story where our best-measured signal family and the best available money anchor are
the same family.** Complaint escalation is what the reader reads best — **60 / 65** planted
conversations on the synthetic corpus against the lexicon's 1 / 65, and **23 / 24** on real US
credit-card complaint narratives in the CFPB benchmark, against churn intent's **1 / 8** on that same
corpus. Zero new build; it is already deployed and measured.

**It lost on three grounds, and they are recorded so this is not re-argued:**

1. **Market.** The judges and the entry are being pitched US. A pound sign in a US-framed room is one
   of the three fastest ways to lose it (`00-READ-THIS-FIRST.md`).
2. **Depth of preparation.** The US folder carries two adversarial passes and sixteen answered kill
   shots. Two days out with **zero dry runs done**, switching to the less-rehearsed script is the
   higher-variance move regardless of which is theoretically stronger.
3. **There is no US equivalent to import.** The CFPB's enforcement posture contracted through 2026 and
   no US per-case tariff exists, so the "US market, complaints lead" hybrid gets the evidence
   advantage and loses the money advantage — the worst of both.

## What to actually do with it in the room

**Do not volunteer it.** It is an answer, not a beat. Two questions make it the right answer:

> **"Is any of your value based on a hard number rather than a model?"**
>
> Not in the US, and I won't pretend otherwise — the US has no per-case tariff and I'd be inventing
> one. **In the UK it does: the Ombudsman charges £650 a case whether the firm wins or loses, billed
> quarterly in advance from April.** Same layer, same signals, and complaint escalation happens to be
> the family we read best — 60 of 65 on our corpus, 23 of 24 on real card complaints. **If you ever
> point this at a UK book, the money stops being a model and becomes a price list.**

> **"Does this only work for US cards?"**
>
> No — and the cleanest proof is that we costed a UK complaints version of exactly this layer against
> a published regulator tariff. **Same code, same ledger, different desk and different currency.**

**Two guardrails.** Never quote the £650 without saying "UK" in the same sentence. And **never mix the
desk coverage table into the US story** — 0/20 → 20/20 was measured on a generic retail-banking corpus
and is permitted only as labelled mechanism evidence (`§5`, and it is the most tempting number in the
repo).
