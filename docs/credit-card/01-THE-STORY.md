# The story — 2026-09-11, Venkat and Farhan

18 minutes. A CEO and a COO, both finance-background, deciding a shortlist. They want: **how strong
the product is · dollar value impact · could I pitch this to a company and win a project.**

Market: **US card issuer.** Dollars, APR, annual fee, points, retention offer, product change.

---

## The sentence they should leave with

> **We turn the conversations you already record and already throw away into a live feature inside
> the churn model you already run.**

Every clause is verifiable, names the integration, contains no invented number, and answers *could I
win a project with this*. If one sentence survives the room, this is it.

**Not** "we spot churn 58 days early." That is a number we chose, wrapped around the commodity
detection framing this entry was explicitly built to avoid — and it was already judged a loser once in
that framing.

## The headline claim: latency, not clairvoyance

> **Your propensity model refreshes on a batch cadence — monthly, typically — and it never sees what
> the customer actually said. Ours moves the moment the transcript lands.**

Structural. Needs no causal study, no lift number, no client data. **Unattackable, which is why it
leads.**

---

## The six beats

| # | Beat | Min |
|---|---|---|
| 1 | The gap, and the project | 3 |
| 2 | The inversion | 1 |
| 3 | **The demo** | 7 |
| 4 | The score, and how you consume it | 3 |
| 5 | The money | 3 |
| 6 | Committed vs delivered, and the ask | 1 |
| | **18 total** | |

Beat 3 gets 7 of 18 because it is the only beat a competitor cannot reproduce. **Beats 1 and 2 must
not sprawl** — the temptation is five minutes on the problem, and it costs you the demo.

**Two sections in this file are not beats and have no minutes of their own:** *the reader beat* (the
model-vs-lexicon table — say it whenever someone asks what the AI actually does, most likely inside
beat 4 or in Q&A) and *the honesty beat* (which sits between beats 3 and 5, ~30 seconds taken out of
beat 5).

---

## Beat 1 — the gap, and the project (3 min)

### Open with the market, because these two judges are finance people

> There are **608 million open general-purpose card accounts** in the US, and the CFPB says
> **between 0.7 and 1 percent of them close every month** — call it **8 to 12 percent a year**.
> *(CFPB Consumer Credit Card Market Report, published 2025-12-30.)* Americans carry **$1.263
> trillion** at **22.15%** APR on balances assessed interest, and charge-offs are running at
> **3.82%**. *(NY Fed Q2 2026; charge-off rate CORCCACBS, Federal Reserve "Charge-Off and
> Delinquency Rates on Loans and Leases at Commercial Banks", updated 2026-08-25.)*
>
> **And here is the tell: nobody publishes how much of that closure is voluntary. Not the regulator,
> not one issuer 10-K.** Which is the first sign this is a number managed internally and never
> measured well.
>
> **In a book like that, the customers you least want to lose are the profitable ones who leave
> quietly.**

**Two corrections made on 2026-09-09 — the old version of this paragraph was wrong twice.**
**(a)** It said charge-offs were **3.70%, per Fed G.19**. G.19 is the Consumer Credit release and
publishes **no charge-off rates at all**; the right series is CORCCACBS and it reads **3.82%** for Q2
2026. **(b)** It quoted **"$1,464 a year of gross interest on an average $6,610 balance"** in the same
breath as 608 million accounts. **$6,610 is per borrower, not per account** — and the two published
figures in this very paragraph prove it: $1.263T ÷ 608M accounts = **$2,077 per open account.**
$6,610 across 608 million accounts would be $4 trillion, three times the balance that actually exists.
**Do not say $6,610 anywhere near an account count.** Either drop the per-unit balance or say
"about $2,000 per open account, around $6,600 per borrowing household."

### Then the claim — in the only form that survives an ex-card-book executive

> When a card customer is on their way out, they usually tell you — on a call, weeks before they
> close. **Today you learn it on the cancellation call, because every call before that was read once,
> dispositioned, and thrown away.**
>
> **Of the leavers who do speak to you, you learn on the last conversation. We learn on the first.**

That is smaller than "we reveal silent attrition" and it is **true**, which the bigger claim is not.
See `03-REFERENCE.md` §6 for why — the population we can score is close to the complement of the
population a "we see the invisible ones" opener would promise. **Do not make that claim.**

### Say the evidence limit here, once, and let the market carry the argument

> **There is no published, card-specific study showing transcript signals predict attrition beyond
> structured data.** We are not going to claim one.

**And do not reach for a regulatory argument.** The UK version of this pitch leaned on a
regulator-mandated customer conversation; **there is no US equivalent** — the CARD Act and Regulation Z
require *disclosures*, not conversations. Separately, the CFPB's enforcement posture contracted through
2026, so **anchoring on CFPB risk would read as not having checked.** Lead with economics. Treat
regulation as a constraint to satisfy, not a threat to monetise.

### Then put the project on the table — in minute three, not minute eighteen

**This is the single highest-value change from the first draft.** A pre-registered experiment with a
walk-away is something a CEO can say yes to on Thursday. A value chain with a hole in it is something
he says "interesting" to.

> **What we want is a six-week retrospective back-test.** Your existing call recordings, your existing
> closure label. No production integration, no customer contact.
>
> - **Buyer:** Head of Retention Analytics. **Sponsor:** Cards MD. **Blocker we expect:** Model Risk.
> - **Pre-registered success criterion:** top-decile uplift, our feature added to your model as a
>   challenger against your production champion. Registered before we see the data.
> - **Fixed fee, explicit walk-away.** If the criterion is not met, the answer is no and we say so.
>
> **Phase 1** if it clears: a ranked queue on one desk. **Phase 2**: the feature-store integration.

---

## Beat 2 — the inversion (1 min)

One sentence, then move:

> Every system you run reconciles to current truth. A signal that did not clear a threshold is
> dispositioned and gone, because on its own it was not actionable. **We never discard it** — and it
> becomes actionable later, when something corroborates it.

Then the line that de-risks the whole thing for a CEO:

> **The score is arithmetic, not model output.** Accumulation, decay and thresholds are deterministic,
> unit-tested code. The model's only job is to read the transcript and quote it.

**Do not quote the line count of that code.** "It's 183 lines of Python" is meant as reassurance and
lands as *"so there's no product here."*

---

## Beat 3 — the demo (7 min)

Full script in **`02-THE-DEMO.md`**. The spine:

One US cardholder, rewards card, **$95 annual fee**, 0% intro APR. Empty ledger. Three conversations.

| Day | Channel | What happens | What we do |
|---|---|---|---|
| **0** | phone | Card declined while travelling — fixed. In passing: the $95 fee posted and they're not sure it's worth it | Record it with the **verbatim quote**. **Open no case. Discard nothing** |
| **74** | chat | Chasing a rewards redemption that failed twice; asks what the APR reverts to when the intro period ends | **Score crosses. Case opens.** Two conversations, two channels — and the day-0 remark is now worth materially more |
| **132** | phone | Asks for the payoff amount and what happens to their points | **Everyone catches this one.** We opened the case on day 74 |

**The line to land at day 74. Slow down:**

> Nothing here would open a case in any system you run today. And we have opened a case.

**Then, at day 132, before they think it:**

> Every tool on the market catches this call. On this arc we opened the case 58 days earlier.

**Say "on this arc" every time.** 58 = 132 − 74, both authored fixtures. Speaking an authored number as
a result is how you lose a technical listener. The claim that carries the same weight with none of the
exposure is the latency claim at the top of this page.

**Then the retro column** — the hardest thing to fake. Four stored numbers per entry: what it
contributed *then*, the total *then*, what it contributes *now*, the total *now*. Point at the day-0
remark and read both. **Observable, not asserted.**

Three claims while the screens are up: **safe to re-run** (260 messages fed twice → still 34 entries,
1 case) · **fails visibly** (poison records isolated and raised — *verify the alarm history first, the
repo contradicts itself*) · **a human decides** (no outbound contact surface anywhere — not switched
off, **absent**).

---

## Beat 4 — the score, and how you consume it (3 min)

**What it is:** a per-customer **conversation attrition score** — ordinal, event-driven, bounded,
decaying, every point traceable to a verbatim quote.

**Two things it is not:** not a customer-value score (no spend or margin data reaches it), and **not a
decision.**

**Concede calibration immediately.** Not a calibrated probability — nothing here is trained against an
observed outcome. It is an **ordinal risk-ranking feature**, testable for monotonic association with
their label once they supply one. Volunteering this is pure gain.

### The answer to "we already have a retention model"

> You almost certainly do — and it is usually a **value** score. It tells you how much you care if a
> customer leaves. It does not tell you they are leaving. Different questions, and most issuers run
> both. Ours is a feature on the propensity side, never the value side.

### The US-specific line that proves card literacy

> And not all attrition is worth stopping. You have a sign-up-bonus population that opens for the
> bonus and closes at the first annual-fee anniversary — **retaining those customers destroys value.**
> Which is exactly why our score sits *alongside* your value score, not instead of it. We surface the
> intent; your value model decides whether the intent is worth acting on.

Say this unprompted. It signals you have worked in cards faster than anything else available.

### The question that ends the pitch — answer it before it's asked

> *"Day 74. The customer isn't calling. They're at home. What physically happens next?"*

> **We never contact your customer. We change what your agent knows the next time they do — and in
> cards, they do.** The case sits on the account and the next agent opens the call already briefed. And
> if you already run a proactive retention campaign, we change who is on the list.

**Requires nothing built, and keeps "no outbound surface" literally true.** Without this sentence, the
early-warning claim and the safety claim contradict each other four minutes apart.

### Point-in-time, answered unprompted

> *"You told me the score rewrites history. My feature store serves the value as it stood on the
> observation date. So the thing you just demoed is the thing I have to turn off."*

> **Training joins `score_at_write`. Inference and the operational queue use `score_now`** — because
> for a live decision, today's best estimate is what you want. Retro re-scoring earns its keep in
> production scoring and the human queue, never in the training join. Both are stored, so
> point-in-time is a query, not a rebuild.

### Coverage — get there before the modeller does

> The score exists only for customers who've had a conversation. Everyone else gets an explicit
> `no-evidence` null with its own denominator — **never a defaulted zero**, because a zero reads
> downstream as *confirmed low risk*, which is worse than no feature at all.
>
> And in the back-test we'll report coverage **among actual leavers** — not among the book — and your
> model's performance **with and without our feature**, on the same population.

**Wording corrected 2026-09-09 and this one matters.** The earlier promise was to report performance
*"inside and outside the scored population"*. **That cannot be computed** — outside the scored
population there is no score, so there is nothing to measure performance *of*. It was a commitment we
could not keep, offered to the one person in the room most likely to try to collect on it.

**What is computable, and is the right offer:** coverage among leavers (do the people who leave
actually talk to you?), and your model's lift **with vs without** our feature on the customers who
have a score. **If a modeller pushes further** — *"then you can't tell me the feature generalises"* —
the answer is yes, that is true, and it is a property of every conversation-derived feature ever
built, ours included.

### The governance sentence

> Our score is an input to your model, never a decision. A human, or your own supervised model with an
> observed outcome, always sits between our signal and any customer action. Every point traces to a
> verbatim quote, **we work from transcripts and never from audio**, and the system has no way to
> contact a customer at all — the safety case is that the capability does not exist, not that it's
> switched off.

*(The transcripts-not-audio clause is worth its place: it keeps you clear of Illinois BIPA voiceprint
exposure that any voice-analysis vendor carries.)*

### The latency claim and path 1 contradict each other — patched 2026-09-09

**This beat opens with "ours moves the moment the transcript lands" and then sells path 1: a feature
inside their *monthly* model. Those two sentences are ninety seconds apart and a modeller will put
them together.** Say the resolution yourself:

> On path 1 — the feature-store integration — you get our value at your next model run, same as every
> other feature. **The latency is not what path 1 buys you; the information is.** Latency is what
> **path 2** buys you, the ranked queue on one desk, which reads the score the moment it changes.
> That's why path 2 is the pilot and path 1 is the destination.

**Do not leave the latency line as the unqualified headline of a beat that then sells a monthly
feature.** It is still the right headline for the pitch — it just belongs to path 2.

### And the harm you deliberately avoid

> Distress and life-event signals never route to retention. They go to collections and to a
> vulnerability desk — **that's a mapping in code**, not a policy preference. And the system has **no
> offer mechanism at all** for a distress signal to feed, because it has no way to contact anybody.

**Wording corrected 2026-09-09, and the correction matters.** The previous version said distress
signals are *"structurally blocked from feeding any offer trigger — that's a branch in code."*
**Checked: there is no such branch, because there is no offer trigger in the system to be blocked
from.** Grepping `src/earshot/` for an offer or eligibility concept returns nothing. What does exist
is `TRAJECTORY_TEAM` (`src/earshot/schema.py:35-40`), which maps distress → collections, life event →
vulnerability, churn intent → retention.

**The true version is stronger, so this costs nothing:** a guard can be switched off, and an absent
capability cannot. But **describing a guard that isn't there is the one kind of claim that ends a
pitch if a judge asks to see it**, and this is the line `00-READ-THIS-FIRST.md` calls your single best
line. Say routing plus absence. Never say "branch" or "blocked".

Under UDAAP's "abusive" prong, turning a disclosed hardship into a sales trigger is the textbook shape
of the risk. **Showing you know where the harm is, unprompted, is what separates you from every other
AI pitch they saw this year.**

---

## Beat 5 — the money (3 min)

Full detail in `03-REFERENCE.md` §4.

### Give up the easy number first

> A closed account costs you twice: **the margin you stop earning, and what you pay to replace it.**
>
> We can show you the first from published data. And for the second, **your peers' own filings give us
> an upper bound: Amex spent about $500 per new card last year, JPMorganChase $532 — both derived from
> their own 10-Ks.** Upper bound, because marketing money also buys brand and retention. But it tells
> you the order of magnitude, and **you know your real number precisely. We don't, and we're not going
> to pretend otherwise.**
>
> *(And I'm not going to quote you the "acquiring costs five to twenty-five times more than retaining"
> line. It traces to a magazine article that says "depending on which study you believe" and cites
> nothing.)*

### Then multiply your own chain through, out loud

> Five million accounts, 5% voluntary attrition, 40% conversation coverage, 30% voicing a leading
> signal. **That's about 30,000 names — six tenths of one percent of the book.** At a 10% incremental
> save, $300 margin and $250 acquisition cost, roughly **$1.65 million a year, gross.**
>
> **I'd rather say that than have you work it out while I talk.**

Four multiplicative haircuts do that, and **each haircut is a fact about their book, not about our
accuracy.** Say so.

### The chain has no false-positive leg — added 2026-09-09, and this is the sharpest hole in beat 5

**Every haircut in that chain is applied to leavers. Stayers are never counted.** On the same
placeholder book that produces 30,000 names, roughly **1.9 million conversing non-leavers** have no
number attached to them at all — and the annual fee posts on every account every year, so grumbling
about it is not rare. **The chain quietly assumes precision is 100%.** A modeller will see this the
moment they look, and it is a worse finding than the small-population one because that one said the
number was *small*, and this one says it is *wrong*.

**Make it the third refusal rather than waiting to be caught:**

> And there's a third number I can't give you: **how many of those 30,000 were never leaving.** Our
> precision is unmeasured on card data — that's the same gap as the save rate and it multiplies
> against it. **Which is why the pilot is a ranked queue over fixed capacity, not a campaign.** A
> queue doesn't need precision, it needs ranking: your retention team works the top N they can afford
> either way, and the only question is whether our order beats their current order. **That is exactly
> what the back-test measures.**

**So say the $1.65M as what it is — the gross ceiling before a precision haircut nobody has
measured — or don't say a total at all.** Do not present it as an expected value.

### The two refusals

> Two numbers we will not invent: **your incremental save rate net of customers who'd have stayed
> anyway, and your margin per account.** Any vendor who hands you those made them up.

### Then the line that makes it obviously worth trying

> Reading every conversation costs **$1.58 per thousand**. Ten million conversations a year is about
> **$16,000**. **Affordability is not the question. The question is whether the save rate is real —
> and that's exactly what your back-test settles and what we refuse to guess.**

### Falsify it yourself

> If your retention team already catches these customers another way, the incremental save rate is
> zero and so is the value. **That's a test, not a leap of faith.**

**Three traps:** don't multiply $1.263T by an invented capture rate · don't quote the $1,464 gross
interest as value per saved customer (it's before cost of funds, 3.82% charge-offs, rewards and opex) ·
don't lead with the optimistic column.

---

## The reader beat — NOT a numbered beat. The answer to "what does the AI actually do?" (2026-09-09)

**Ravi's instruction, 2026-09-09: stop letting the keyless lexicon carry the numbers. This is a
generative-AI product and the evidence should be the model's.** It already is — this table was
measured and paid for, and it is the single best evidence in the repo that the model is the product.

**Same 282 conversations, same planted ground truth, two readers.** The lexicon is a hand-tuned
26-regex fallback that exists so a judge with no API key can still run everything. The model is
Claude Haiku 4.5 on Bedrock, which is what the deployed system runs.

| Signal family | 26-regex lexicon | **Claude Haiku 4.5** |
|---|---|---|
| Churn intent | 16 / 77 planted conversations | **40 / 77** |
| Complaint escalation | 1 / 65 | **60 / 65** |
| Life event | 9 / 68 | **50 / 68** |
| **Financial distress** | **33 / 72** | **27 / 72 — the model loses** |

> **A rule engine finds one of the sixty-five conversations where a customer is escalating a
> complaint. The model finds sixty.** That gap is the product. **And on financial distress the rule
> engine beats it, 33 to 27** — because "I've lost my job" is a phrase, and phrases are what regexes
> are for. We publish the row we lose.

**Three reasons this is the right thing to lead with:**

1. **It is a like-for-like comparison** — same conversations, same answer key, same denominators.
2. **It contains a loss**, and the loss is mechanically explicable rather than embarrassing.
3. **It is about reading, not ranking** — so it cannot be attacked as circular the way the
   accumulation result can.

**Do not describe the lexicon as "our offline mode" or lead with "it runs with zero API keys."** That
is a reproducibility property for a judge, not a product claim, and to a CEO it sounds like the
product is a regex. **Keyless reproducibility belongs in Q&A**, phrased as: *"every number we quote
replays from a committed cache with no key, so you can audit it — but the system runs on a model."*

## Beat 6 — committed vs delivered, and the ask (1 min)

**Lead with the misses.** It's faster and it buys the rest.

- **Two dry runs committed, zero done.**
- **The anchor metric — retention lift against a matched control — still not built.** It now sits
  directly under the one metric being sold.
- **Every own-measured number in this repo was measured on a generic retail-banking corpus with no
  credit-card content in it.**
- What is done: **908 tests** (903 pass, 5 skip) · the comparison-model arm · the deployed AWS pipeline
  agreeing with local to the last digit · a published chance gate we **fail**.

**On the chance gate, complete it or don't raise it.** "We fail at p=0.076" reads as *it doesn't work*.
The whole version: **18 wins, 8 losses, 4 ties across 30 seeds** — directionally positive, underpowered
at 30 seeds, published as a failure because the pre-registered bar was significance.

Then the ask: beat 1's experiment in one line.

---

## The honesty beat — placement matters

**Say it immediately after the demo, immediately before the money.** Not in beat 1: told to two finance
judges before anything has been shown to work, it produces the sentence *"they admitted none of their
numbers are about credit cards"* — and that becomes the only thing they remember.

Sequencing is not hiding. It still lands before any quotable number, which is the actual obligation.

> Every own-measured number we have was measured on a generic retail-banking corpus with **no
> credit-card content in it**. What carries into a card story is the *mechanism* and the *market
> facts*. **What does not yet exist is a single measured number that is both about attrition and about
> credit cards.**

### That is no longer quite true — 2026-09-09, and it cuts both ways

**The CFPB benchmark turned out to be card-heavy, and it is real US consumer complaint language, not
synthetic.** Of its 150 hand-marked narratives, **55 are credit-card complaints** (51 general-purpose
or charge card, 4 store card). Splitting the existing published run by product costs **$0** — it
replays from cache — and produces the first card-specific measured numbers in the repo.

**On those 55 card narratives, the model reader:**

| | Card (55 docs) | Non-card (95 docs) |
|---|---|---|
| fired *something* on a document marked as carrying a signal | **29 / 29** | 52 / 54 |
| got the exact signal type right | **26 / 35** marks | 66 / 77 marks |
| false positives, (document, type) pairs | 27 / 185 | 51 / 303 |
| **churn intent specifically** | **1 / 8** | 4 / 5 |

**The last row is the one that matters and you must not bury it.** The signal family this entire
attrition pitch rests on is the **worst-performing family on real credit-card complaint text** — 1 of
8. What the reader finds on card narratives is overwhelmingly complaint escalation (23/24), which is
the desk this pitch is *not* selling.

**Three things keep this honest and none of them is a rescue:**

1. It is a **post-hoc subgroup split**, not pre-registered. `PROTOCOL.md` was not touched and no
   published file was rewritten. It is descriptive evidence and must be labelled as such.
2. **CFPB narratives are complaints by construction.** Everyone in that corpus was angry enough to
   write to a regulator, which is not what a servicing call looks like. It over-represents complaint
   language and under-represents the quiet fee grumble the demo is built on.
3. **n = 8 for card churn intent.** That denominator cannot carry a conclusion in either direction.

**What to say on stage — this replaces the old absolute claim:**

> We finally have one card number, from real US complaint narratives rather than our synthetic corpus.
> **On credit-card documents our reader finds a signal in 29 out of 29** where a human marked one.
> **And the honest half: on churn intent specifically it got 1 out of 8** — the family this whole
> story rests on is the one it reads worst, on eight documents, in a corpus made of complaints rather
> than calls. **That's a direction to chase, not a result to quote.**

**Saying the 1/8 out loud is the whole value of having run it.** Quoting 29/29 alone would be the
exact dishonesty the claims triage exists to prevent — and a judge who later found the 1/8 would be
right to discount everything else you said.

**Two numbers forbidden as card evidence:** the desk coverage table (retention 1/20 → 16/20 — true
measurement, wrong corpus; permitted only as labelled mechanism evidence), and any UK figure at all.

---

## Objection playbook

| They ask | You say |
|---|---|
| **"We already have a retention model."** | Yours is probably a *value* score. Ours is propensity, a feature inside yours, not a rival. And yours refreshes monthly; ours moves when the transcript lands. |
| **"Day 74 — the customer isn't calling. What happens?"** | We never contact them. The case briefs the next agent who speaks to them — and in cards, someone does. Nothing for you to build. |
| **"Why isn't this what Verint or NICE already sells me?"** | They classify per interaction and reconcile to current truth — the sub-threshold remark is dispositioned and gone. We add a **persistent ledger, per-family decay, corroboration across conversations and channels, retro re-scoring, and a point-in-time query.** That's a real feature set and it is **not a moat** — I'd rather say so than pretend. |
| **"Which of your signals lead the *decision*, not the *event*?"** | Three of eight: price/value objection, rewards dissatisfaction, life event. A competitor mention and a payoff enquiry mean the decision is likely already made. We relabelled the taxonomy for exactly that reason. |
| **"Isn't this all in our structured data?"** | For most families, partly. For a competitor's offer, a payoff enquiry and a life event, **no structural proxy at all.** Our best line — your payment-ratio flag can't separate *struggling but staying* from *paying down in order to leave* — is real, but a good modeller can build a composite that gets close. I'm not going to oversell it. |
| **"Where did your scoring constants come from?"** | Argued from each signal's real-world persistence, authored before the corpus was scored, **not fitted.** And the honest exposure: our headline accumulation result asks whether an accumulating scorer recovers arcs authored to accumulate. **The falsifying test** is three scorers on your labelled book — our ledger, a recency-weighted count, and a logistic fit on signal counts — compared on top-decile uplift. If the count matches us, our bonuses are decoration. **We'll run that.** |
| **"How accurate is it?"** | On our generic corpus, with denominators, losses beside wins. On card data: **unmeasured.** The run costs $0.45 and I'd rather tell you that than quote a number from a different corpus. |
| **"Hallucination?"** | Every signal carries its verbatim quote, exact-substring checked. Unverifiable quotes are discarded. The score is arithmetic, not model output. |
| **"Model risk will kill this."** | **SR 11-7 was superseded on 2026-04-17 by SR 26-2** — joint OCC/Fed/FDIC, and OCC 2026-13 rescinds 2011-12. It tiers this as a third-party **feature input** that gates no credit and no pricing. We'll give your validation team the target definition, the data provenance and a written use restriction. *(**Do not cite SR 11-7 on 09-11.** Citing rescinded guidance is the fastest way to be marked as not having checked — see `06-DEFENDING-THE-SCORE.md` §2.)* |
| **"LLM outputs aren't reproducible. What happens when you switch models — does my feature change under me?"** | **The most dangerous question available and the whole of `06-DEFENDING-THE-SCORE.md` answers it. Lead with:** the arithmetic is fixed code with a determinism test; the reading is a model, so we promise a **fingerprint**, not determinism — model id and prompt hash on every score. **Then the closer: "we've already changed the model and measured it"** — Nova Lite vs Haiku, same 282 conversations, for $0.027705. |
| **"Your confidence numbers aren't real probabilities."** | **Concede immediately, do not defend.** It's a raw model output, it's a direct multiplier in the score (`memory.py:99`), and the literature says verbalised LLM confidence is overconfident *(Xiong et al., ICLR 2024, arXiv:2306.13063)*. **Bucketing it is the next thing we build**, and the ablation to prove the effect already exists. |
| **"CCPA — a customer asks you to delete their data. Your ledger never discards anything."** | **No good answer exists yet and do not invent one.** Checked 2026-09-09: `memory.py` has **no delete, purge or forget method**. The ledger is append-only. Say: *"the prototype ledger is append-only; deletion is one of the seams that has to be built before any production integration, and it's on the list."* **The retro column you just demoed is the evidence for this objection** — expect it right after the demo. |
| **"Can you use our call recordings for this?"** | Your determination, not ours. Recordings made for quality and training are a different purpose, and a dozen states require all-party consent. **I'm not going to tell you it's solved.** |
| **"Bias in transcripts?"** | A real, unresolved exposure — accent, dialect and proficiency can proxy protected characteristics. **Subgroup testing is a gated pre-condition of go-live, and it needs your segment labels.** |
| **"What's the invoice?"** | Six-week fixed-fee back-test, pre-registered criterion, explicit walk-away. Then a ranked queue on one desk, then the feature-store integration. |

---

## What to cut

**Cut from the stage entirely — decide now, not on the night:**

- Any account-count or "invisible third of the book" statistic.
- "183 lines of deterministic Python."
- The contradiction with our own submitted brief → **prepared Q&A only.** On stage, one clause: *"we've
  narrowed from the layer to its strongest single view for this sprint."*
- The bare "7/132 – 10/132" pair. Say it whole (see `02-THE-DEMO.md`) or not at all.
- The five adjacent use cases → Q&A. Breadth reads as unfocus to a CEO deciding fundability.
- Any UK figure.
- Two of the four "what it is not" bullets.

**If running long, cut in this order:** beat 2 to one sentence · the "what is done" credits in beat 6 ·
the day-132 walkthrough.

**Never cut:** the day-74 crossing · the retro column · the day-74 "what happens next" answer · the
consumption answer · the two refusals · the honesty beat · the six-week experiment.
