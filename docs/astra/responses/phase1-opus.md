# Phase 1 — the idea

The mechanism you are proudest of does not do what you think it does. Memory that re-values the past is
not, on your own numbers, a better predictor of a customer — whole-portfolio it ranks 8th of 9 arms, it
does not clear a chance gate on the stratum it was designed for, and a version with every scoring
mechanism switched off beats it. What that same mechanism *is* extraordinarily good at is proving what
the institution was told, when it was told, and what it could reasonably have known at the time. Those
are two different products with two different buyers, and only one of them is supported by the evidence
you already have. **Build the second one.**

Here is the idea. Stop trying to predict the future of one customer. Start detecting the present state of
the bank. Every large remediation in retail banking has the same shape: a product, fee or servicing
failure that customers described to the call centre, individually, hundreds or thousands of times, for a
year or more; each call handled correctly, refunded, coded to a generic bucket and closed; nobody
connecting them; and then a regulator, an internal audit sample, a class action or a journalist connects
them, and the bank pays redress to everyone, plus a fine, plus the cost of a manual look-back through
two years of call recordings performed by forty contractors over eleven weeks. **The bank was told. It
was told in plain English, by name, with a date, thousands of times. It kept the transaction and threw
away the narration.**

The product is the system that reads the narration. It finds the emerging systemic issue from the
accumulated words of unconnected customers, months before anything in the bank's structured data moves,
and it produces two things no bank can produce today: **the date it was first told**, and **the list of
every customer who told it, with their own sentences attached.** It does not score a customer. It does
not predict anything. It counts what is already true and shows you the evidence.

I will argue this properly below, but the one-line version of why it is the right answer is this: **point
the machine at the problem where its measured strengths are the requirements and its measured weaknesses
are not on the critical path.** Recall of 0.6549, 13 bad quotes out of 5,736, $1.58 per thousand,
reproducible to the decimal, point-in-time reconstruction — those are the exact specifications for a
conduct-evidence system. Calibration, precision on a real book, and per-customer ranking — the three
things you have never measured or have measured badly — are not required by it at all.

---

## 1. The problem worth solving

### Where the current framing breaks

*"The bank reads every conversation and remembers no customer."* It is true. It is well put. It is the
wrong problem, in three specific ways.

**It names a capability gap, not a pain.** No bank on earth has a budget line, a named owner, an OKR or
an audit finding called "we do not remember our customers." Nobody is measured on it. Nobody has been
fired for it. Nobody has a consultant in the building about it this quarter. A true observation with no
owner cannot be sold, because a sale requires a person whose problem it is and whose year gets better
when it is fixed. When you pitch a capability gap, the buyer nods, agrees completely, and does nothing —
and you will read that nod as interest.

**It leads inevitably to prediction, which is where you are weakest.** If the value of memory is that it
makes the bank smarter about a customer, the very next question is *how much smarter*, and the honest
answer from your own harness is: not measurably. 18–8–4 at `p=0.076` against a seeded random arm.
`dumb-ledger` beating the full ledger. A pre-registered headline that died on a corpus rebuild, 29–0–1
becoming 15–13–2. Records reversing twice. That work is well run and its publication is to your credit,
but under the current framing it is a loaded gun sitting on the table in a room with two finance
executives. The framing writes a cheque the measurements say the mechanism cannot cash.

**It picks a fight it cannot win.** "We read every conversation" is the homepage of Verint, NICE,
CallMiner, Observe.AI, Level AI, Contact Lens and CCAI Insights. Entering a crowded category on the
incumbents' own axis, with no installed base, against vendors closing $300k–$1M deals, is the losing
position in enterprise software. You do not out-execute seven entrenched vendors at their own sentence.

### The better framing

**The bank is not failing to remember its customers. It is failing to hear itself.**

Every fact an institution needs about its own products, processes, pricing and failures is being narrated
to it thousands of times a day, in plain language, by the people it is failing. The narration is recorded,
transcribed, stored, retained for legal reasons, and never read by anything that can aggregate it. The
asset is not customer memory. It is **institutional memory of what customers reported** — a different
object, with a different owner, a different budget, and a far sharper price.

Three tests, and they resolve differently, which is exactly the gap the ask warns about:

- **Most valuable** problem near this capability is probably coached-victim scam and elder financial
  exploitation. FBI IC3 2025: 201,266 complaints from victims 60+, over $7.7bn lost, average above
  $38,000, up 37%. But the money is the customer's, not the bank's — Reg E does not reach authorised
  transfers — so enormous value converts to a modest price.
- **Most sellable** is conduct and systemic-issue detection. It sells to fear, which is a faster buying
  emotion than upside; the owner already exists and is already accountable; the budget line already
  exists; and the pilot is falsifiable in six weeks against the client's own history.
- **Most true to the built capability** is also conduct and systemic-issue detection, for the reasons in
  the opening.

Two of three align on the same answer, and the third is a module you add in year one rather than a
competing product. That alignment is why I am committing to it.

### Why the pain is sharp, urgent and unowned

A systemic issue costs the bank on four lines simultaneously, and every one of them scales with **time to
detection**, not with model accuracy:

1. **Accrual.** Every month undetected, more customers are harmed and the redress population grows
   linearly. This is the dominant term and it is pure arithmetic.
2. **Look-back labour.** When you finally know, you must scope the affected population. Structured data
   gets you the mechanical part (everyone charged fee X). It cannot answer the harm question — did the
   customer say they did not understand, did they say they could not afford it, did an agent tell them
   something untrue — because that lives only in the calls. Today that is answered by outsourcing people
   to listen to a sample and extrapolate, and every bank knows its day rate.
3. **Handling cost.** Each individual instance was handled as a one-off at full cost, repeatedly,
   forever, because nobody knew it was one thing.
4. **The regulatory tail.** Unquantifiable, and I would leave it out of the arithmetic entirely — which is
   itself persuasive, because finance people respect a value chain that omits its own biggest number on
   the grounds that it cannot be defended.

And it is genuinely unaddressed. GRC and issue-management platforms — Archer, MetricStream, ServiceNow
IRM — are where an issue is *recorded after a human raises it*. Nothing in that stack *finds* one.
Complaint taxonomies classify into buckets someone wrote in advance, which by construction cannot contain
the bucket for a problem that started last month. Speech analytics is a **query tool**: it answers
questions you already thought to ask. The entire value here is finding the thing nobody thought to search
for.

---

## 2. The product

**A standing surveillance layer over everything customers tell the bank, which detects the bank's own
emerging failures from the accumulated words of unconnected customers, proves the date it was first told,
and produces the affected population with the evidence attached.**

Concretely, it does four things:

**It reads everything, nightly.** All transcripts, all chat, all secure-message threads, all complaint
free-text, all agent wrap-up notes. Not a 1–2% QA sample. At $1.58 per 1,000 conversations, a
20-million-conversation book costs roughly $32,000 a year in model spend to read completely. That number
matters less as a price than as an objection-killer: *"we cannot afford to read all of it"* is no longer
true, and has not been true for about eighteen months, and most banks have not noticed.

**It clusters what was said across customers, not within one.** This is the new code and it does not exist
yet. Signals are grouped by the *claim being made*, not by a pre-existing label, so a problem that has no
taxonomy code still forms a cluster. Each cluster carries a weekly volume series. The alert fires on
**rate of change against the cluster's own baseline**, not on level — which is the only way to see a new
issue at 88 conversations a week inside a complaints base rate of 3,000.

**It produces a case file, not a dashboard.** Header: what the cluster is, the date of the earliest
instance, how many distinct customers, how many conversations, across which channels, over how many
weeks. Body: ten verbatim quotes from ten different customers on ten different calls, each with the
conversation id, the turn index and the date. Footer: the full affected population, exportable. A
complaints analyst reads ten quotes in four minutes and knows whether it is real. That is the entire
human workflow.

**It answers "what did we know and when" as a read, not a rebuild.** Because both the then-value and the
now-value of every entry persist, the system can reconstruct the institution's knowledge state on any
past date. This is the feature you built thinking it was a forecasting feature. It is an audit feature,
and it is the most defensible thing in the product.

### Who signs, and which budget

| | |
|---|---|
| **Economic buyer** | Chief Compliance Officer, or Chief Risk Officer where conduct sits under risk. At a mid-size US issuer, often the Head of Complaints & Conduct with the CCO as sponsor. |
| **Operating owner** | Head of Complaints. This is your champion and the person who demos it internally for you. |
| **Co-signer you must win, not brief** | General Counsel. Covered in §5 — get this wrong and nothing else matters. |
| **Budget** | Complaints and remediation opex, plus operational-risk / issue-management. Both are cost lines with real money and, critically, **both are already being spent on humans doing this badly**. |
| **Second budget, year two** | Legal / remediation programme spend, for the look-back tool. It is a bigger budget than the first and it opens itself once the first is trusted. |

Note what is *not* on that list: the VP of Contact Center Operations and the Chief Customer Experience
Officer, who were the buyers named in the original submission. Contact-centre ops owns handle time and
agent performance. They are a gatekeeper you must get through — see §5 — but they do not own this
problem and they cannot fund it at this size.

### What changes on the day it goes live

Before: a complaints analyst reads a sample of last month's complaints and writes a themes report from
the taxonomy codes. The codes were written two years ago. Anything genuinely new is invisible, because
new problems do not have codes, and anything below a few hundred a month drowns in the base rate.

After: that same analyst opens a queue of machine-found clusters every morning, ranked by growth rate
rather than volume, each one with ten customer sentences underneath it. They dismiss six, escalate one,
and the escalated one goes into the issue-management system with a population attached and a date
attached. Their job gets better, not smaller — they stop counting and start judging — which is why they
will fight for it in the renewal conversation.

And the day an issue *is* confirmed, by any route, somebody types a sentence and gets the population in
an hour instead of commissioning eleven weeks of contract labour.

---

## 3. The sentence

> **Every remediation this bank has ever paid for was described to your call centre, by name, months
> before anyone joined the dots. We read all of it every night and give you the date.**

The second one, if you need a follow-through rather than a replacement:

> **And when you do find something, we hand you every customer who told you about it, in their own words,
> in an afternoon.**

Why the first works on a finance executive: it contains a threat they have personally lived through, it
makes no claim about accuracy, and it ends in a deliverable that is a single unambiguous object — a date.
"By name" is doing quiet, heavy work: it tells the buyer the affected population is already identified,
which is the expensive half of every remediation they have ever run.

---

## 4. The category

**Conduct surveillance.**

Say it to anyone who has worked in a bank and they will place it immediately, because the structural
analogue already exists, is universally deployed, and is expensive: **trade and communications
surveillance**. Nasdaq SMARTS, Behavox, Shield, Relativity Trace, NICE Actimize, Smarsh. Those systems
read 100% of employee communications, accumulate per person over time, surface patterns to a human review
queue with the verbatim message as the evidence, keep an append-only audit trail, and must be explainable
to a regulator. That is, line for line, the architecture you have built. It is simply pointed at
employees.

So the category sentence is:

> **Trade surveillance, pointed at what your customers tell you instead of what your traders tell each
> other.**

This is worth a great deal, because every consequence of it is favourable. The buyer needs no education
on the shape of the product. The budget line exists and is large. The architecture is pre-validated at
scale. The review-queue-plus-human-disposition workflow is the one compliance already runs. And the
category's incumbents — comms-surveillance vendors and GRC platforms — do not touch customer
conversations at all, so you are not walking into anyone's installed base.

One word of care. Do not let "surveillance" attach to the customer. The object under surveillance is **the
bank's own conduct**, evidenced by what customers said. That framing is not a euphemism — it is more
accurate, it survives a journalist, and it is the version that gets past General Counsel. If you want a
softer label for the same thing, *early issue detection* works and needs no explanation. I would use
"conduct surveillance" in a risk committee and "early issue detection" on a slide.

Naming is the cheapest thing in this document to change, so treat this lightly: I would call the product
**Earwitness** and the artefact it produces **the first-told date** — because the artefact name is what
people actually say in meetings, and *"pull the first-told date on that"* is a sentence a bank will start
saying without being taught to.

---

## 5. How a bank runs it, and how it is sold

### Inside one bank

**What it reads from.** The contact-centre recording and transcription store first — NICE Engage, Verint,
Genesys Cloud, Amazon Connect with Contact Lens, Five9, whichever they run. Then webchat and in-app
messaging transcripts. Then secure-message threads from the online banking inbox. Then, and do not skip
this, **the free-text in the complaints case management system** — Pega Customer Service, Salesforce
Service Cloud, or a homegrown one. Complaint free-text is the single richest and most neglected source in
the bank, because a trained handler has already written a prose summary of the customer's actual point,
and it is sitting in a varchar column that nothing has ever read. Then agent wrap-up notes and email.

Explicitly not: audio (transcripts only, and hold that line — it removes ASR from your cost, your
latency, your accuracy argument and your procurement), and nothing from outside the bank's own systems.

**The hard integration is identity, and it is not glamorous.** Contact-centre platforms key by interaction
id and often by *account*, not customer. You need the CIF or party id on every conversation or the ledger
is worthless. The normal route is the CTI or IVR authentication event, which carries an account or party
id for authenticated calls; you join transcripts to it on interaction id. Unauthenticated contacts — and
at a card issuer that is a meaningful share — either get dropped or matched on ANI with a confidence flag
that never ranks as highly. **Identity resolution is what moves the coverage number that the whole value
chain multiplies by.** Scope it first, budget it properly, and never let it be discovered in month three.

**What it writes to.** Three things, and no more:

1. An **issue object** in the complaints or issue-management system — ServiceNow IRM, Archer,
   MetricStream, or the complaints platform if the bank has no formal issue register.
2. A **per-customer feature row** into the feature store, CDP or warehouse — Snowflake, Databricks,
   Amazon Customer Profiles — for any team that wants the signals as a model input. This is not the
   product; it is the socket that makes year two cheap.
3. An **evidence export** — parquet or CSV of population plus citations, and a PDF case file — for Legal
   and remediation.

**What it touches.** Nothing that contacts a customer. There is no outbound surface, no offer object, no
eligibility concept, no route and no button. Say that in the first meeting, say it again in the
compliance review, and put it in the contract. The absence is a feature you can prove with a grep, and
for this buyer it is worth more than any capability you could add.

**Where it runs.** Inside the bank's own cloud tenancy, their VPC, their KMS keys, their model endpoint
(Bedrock, Vertex, Azure OpenAI). The data never leaves. This is not a preference, it is the entry ticket
— and it is quietly a moat. The most sensitive PII in the institution is a recording of a customer
describing their divorce, their illness and their debts. A bank will not push that to a CPaaS. **A product
that must run inside the tenancy is a product that platform vendors are structurally bad at selling**,
which is a large part of why Twilio Conversation Memory is not the competitor it looks like on paper.

### What must be true on their side, and what is realistically true

| Prerequisite | Realistic state at a bank that is not a tech leader |
|---|---|
| Transcripts exist, retained 12+ months | Usually yes for voice, retention 6–24 months set by Legal. Quality mediocre — diarisation errors, PAN redaction already applied, which helps you. |
| Customer id joinable to interactions | Partial. Good for authenticated servicing calls, poor for chat, poor for email. **This is your longest pole.** |
| Permission to use recordings for analytics | **The most common deal-killer, and the one people discover late.** Recordings made "for quality and training purposes" are a different stated purpose from analytics, and roughly a dozen states are all-party consent. |
| Somebody owns "issues" | Large bank: Operational Risk / Issue Management, formally. Mid-size: the Head of Complaints, informally and without tooling. |
| Appetite to be told bad news | Varies enormously and is worth qualifying for on the first call. |

On consent, there is a point here that is not obvious and that I think is decisive for direction. The
"quality and training" purpose under which nearly all call recording is done **does** reasonably cover
monitoring service quality, complaint handling and conduct — because that is literally what it says. It
does **not** cover marketing, cross-sell or retention offers. Which means the conduct use case is the one
that fits inside the consent the bank already has, and the cross-sell and retention framings are the ones
that require a new consent conversation nobody wants to have. That is an independent argument for this
direction that has nothing to do with the model and everything to do with whether the deal closes.

### Who operates it

- **0.5 FTE complaints or conduct analyst** triages the cluster queue daily. Their job changes as
  described in §2.
- **0.2 FTE data engineer** owns the ingest and the identity join.
- **Model risk** gets a validation package. Above $30bn this is a model under SR 26-2, joint OCC/Fed/FDIC,
  and you will be validated. Here is the good news, and it is genuinely unusual: a pipeline that
  reproduces to the last decimal place from a committed cache, with run manifests carrying seed lists and
  git SHAs, and a hard citation contract that refuses to emit a decision without a resolvable verbatim
  quote, is a gift to a validation team. Most GenAI vendors arrive with nothing. Put the reproducibility
  evidence in the validation pack, not the demo.

### What is genuinely hard here that is not hard elsewhere

1. **Purpose limitation on recordings.** Above. Surface it on day one.
2. **Identity federation.** Banks are organised by product, so the card platform, the deposit platform and
   the complaints system have three different customer keys and a reconciliation nobody owns.
3. **Model risk validation.** Two to four months, and it is a gate, not a formality.
4. **Discovery.** General Counsel's instinct on hearing "searchable index of every time a customer said
   they were struggling" is that you have just built plaintiff's exhibit A. **Meet this head on and do not
   duck it.** The answer is: the recordings already exist and are already discoverable; you have created
   no new liability. What you have changed is *who can find the three calls that matter*. Today a
   plaintiff's firm with a subpoena and a room of paralegals can find them and the bank cannot. You are
   ending an information asymmetry that currently runs entirely against your client. And — this is the
   part that closes it — the point-in-time record is the only artefact in the bank that can demonstrate
   the pattern *was not visible* on an earlier date. It is as much a defence as an exposure.
5. **Retention and deletion.** Your ledger is append-only with no purge or forget method. That is
   currently **incompatible** with a bank's records-retention schedule and with state privacy deletion
   rights, and it will be the first thing a compliance reviewer finds. Fix it before you sell: tombstoning,
   jurisdictional retention windows, and a proof-of-deletion artefact. It is about a week of work and it
   is not optional.
6. **The contact-centre team is a gatekeeper with no incentive.** You cannot get a transcript feed without
   contact-centre ops, who are not the buyer, do not get the benefit, and are measured on availability.
   Budget three months and put it on the critical path of the plan, not in the risk register.

### The adoption path

| Phase | What | How long | What proves it |
|---|---|---|---|
| **0** | Retrospective back-test. Their transcripts, their last 5–10 closed issues with the internal discovery date for each. Fixed fee, pre-registered criterion, explicit walk-away. | 6 weeks | A distribution of *days earlier*, not an anecdote. |
| **1** | Live cluster monitoring on one product line, one desk, one read-only queue, writing into complaints. | 3–4 months | N genuine issues surfaced that existing MI did not, plus the analyst saying the job is better. |
| **2** | The look-back tool becomes standing capability for Legal and remediation. | 6–12 months | Second budget opens. Usually larger than the first. |
| **3** | More channels, more products, then the per-customer uses — vulnerability routing, complaint-escalation prediction, scam arcs — off the ledger that is now populated and trusted. | Year 2 | This is where "one layer, many teams" finally becomes true rather than aspirational. |

The Phase 0 shape is the one already on the table in §8 of the brief. Keep the shape exactly — six weeks,
fixed fee, pre-registered, walk-away. Change only what is measured. **Retention uplift against a matched
control is a hard, slow, contestable measurement on a customer population.** *Days from first customer
report to internal discovery* is a hard, fast, uncontestable measurement against events the client has
already documented, with a label that is a known past fact rather than a forecast. Same six weeks. Vastly
better evidence.

### Across many banks

**One product, one configuration axis.** The engine is identical everywhere. What changes per client is
the content layer: signal family definitions, phrase pools, the product taxonomy, and the cluster naming
vocabulary. That is the day of authoring you already cost. Sell it as a configuration, price it as
onboarding, do not let it become bespoke software.

**They do not all buy the same thing, and one segment should not buy it at all.**

- **Top-five issuer.** Hundreds of millions of conversations. The pipeline engineering is a genuine
  streaming problem and they have people who will want to build it. Sell them the *taxonomy, the
  evaluation harness, the time-to-detection benchmark and the model-validation pack*, not the pipeline.
  Nine-month procurement. Good logo, bad first customer.
- **Regional bank or mid-size issuer, roughly $50–250bn.** The target, unambiguously. Enough volume for
  clusters to be statistically real, enough regulatory pressure to have a named conduct owner, not enough
  internal capacity to build it. Under $30bn they also escape SR 26-2, which removes two months from the
  cycle.
- **Credit union.** Do not sell to them. Cluster detection has a **volume floor**: at 50,000 members, a
  real 0.5%-incidence issue produces about twelve conversations, and twelve is not a cluster, it is a
  coincidence. The floor is roughly where a low-incidence issue produces 50+ conversations a month —
  call it one to two million conversations a year. Say this out loud in the pitch. Volunteering the
  segment you cannot serve is one of the cheapest credibility purchases available to you.

**Horizontal or vertical — the question the brief keeps circling.** The honest answer: **the original
"one layer, many teams" instinct was right about the architecture and wrong about the sales motion, and
the current narrowing to one use is right about the sales motion and should not be mistaken for a change
of architecture.**

A first sale that promises to serve four teams dies in the steering committee where four teams must agree
a budget split, and it dies slowly, which is worse. Sell one desk, one queue, one number, one signature.
But build the ledger and the feature-store socket so the second desk is a configuration change, and then
let your champion sell the second desk internally for you — which they will, for free, because their
credibility is now attached to it. The way you get to horizontal is by being narrow first, in the one
department whose existing consent already covers you. Never say the word "platform" in the first sale. Say
it in the second.

**Land and expand, concretely.** Land: cluster detection on the card complaints desk. Expand, in order:
the look-back tool for Legal (bigger budget, and it sells itself the first time an issue is confirmed) →
additional product lines, which is pure config → the per-customer signals as features into the propensity
models the bank already runs, which is where the data-science org becomes an internal advocate → the
vulnerability and scam signal families, which are new content in the same machine and a different routing
rule. Year two, if year one goes well, is three to five times year one and comes largely from the same
account.

---

## 6. The demo

Seven minutes, live, two finance executives. Here it is, beat by beat.

**The story.** A mid-size US card issuer. On 1 February the rewards redemption platform is migrated. A
servicing consequence nobody modelled: when a cardholder redeems points for a statement credit, the credit
now posts *after* the statement cuts, so interest is assessed on a balance the customer believed they had
paid. It affects a fraction of one percent of redemptions. The fee is assessed **correctly** by the
system's own rules, so nothing in the structured data is wrong. Complaints arrive one at a time, get
refunded $11 under a generic goodwill code that fires thousands of times a month for a hundred unrelated
reasons, and get coded to "billing dispute" alongside 3,000 a week of everything else.

That fixture is chosen deliberately and I would not substitute a different one. It is mundane and every
banker in the room has lived one like it. The structured data looks clean — which is precisely why
structured monitoring misses this class of problem. And the *cause* is stated in exactly one place in the
entire institution: the customer's own sentence.

---

**Beat 0 — 0:00 to 0:30. Set the clock and declare the constraint.**

No slide. One sentence: *"I'm going to show you a fee problem at a card issuer. It cost them $3.4 million
and a consent order, and the first customer to describe it precisely did so on 6 February — nine months
before anyone at the bank knew. Then I'll show you the system that would have told them on 3 March."*

Then, immediately: *"All of this is synthetic — competition rules — and every number you see is one I
planted. So judge the mechanism, not the number."*

Declaring the synthetic constraint in the first thirty seconds and then never apologising for it again is
worth more than any amount of hedging later. It also inoculates you against the one question that can
derail the whole seven minutes.

**Beat 1 — 0:30 to 1:30. One call. One quote. "The bank learned nothing."**

On screen: a single transcript, 6 February, a two-minute servicing call. The customer called about a
declined transaction. At turn 31, in passing, almost as an afterthought:

> *"...and honestly, while I've got you — I paid that balance off with my points last month and you still
> charged me eleven dollars of interest. I don't understand it."*

The agent apologises, refunds $11, resolves the call. Perfectly handled.

Beside the transcript, the extracted record: signal type, the verbatim quote, conversation id, turn 31,
timestamp, product, channel.

Say: **"This call was handled well. The agent did everything right. And the bank learned nothing."**

Nine words carrying the entire thesis. Do not elaborate on them. Move.

**Beat 2 — 1:30 to 2:30. The same sentence, four hundred times.**

Zoom out to the portfolio. One chart, nothing else on screen. Weekly count of that cluster over twelve
months: flat at 2–4 a week through January, then from 6 February: 9, 22, 51, 88, 140.

Overlay the bank's own complaint-category volume for "billing dispute." Flat. Dead flat.

Say: *"Same period, same bank. Their complaints MI is the flat line, because these got spread across four
generic codes and drowned in a base rate of three thousand a week. Every one of these was handled. Every
one cost eleven dollars and forty minutes. Nobody looked at them together, because nothing in the bank put
them in the same bucket — and the bucket is the customer's sentence."*

**Beat 3 — 2:30 to 3:30. The case file. A document, not a dashboard.**

Click the cluster. What opens is a **document**:

> **Emerging issue — points redemption, interest assessed on redeemed balance**
> First observed **2026-02-06** · **412 customers** · **419 conversations** · 4 channels · 9 weeks ·
> growth **+340% over trailing 8-week baseline**

Below: ten verbatim quotes from ten different customers, ten different agents, four channels, each with
its conversation id, turn index and date. Below that: the affected population, 412 customer ids, with an
export button.

Say: *"Not a score. Not a probability. A list of people and the sentences they said. Your complaints lead
reads ten of these in four minutes and knows whether it's real."*

**Beat 4 — 3:30 to 4:45. THE MOMENT. Two dates.**

Clear the screen. Two dates, very large, side by side.

> **3 March 2026** — the day this system would have opened the case
> **14 November 2026** — the day the bank actually found out
> **256 days**

Underneath, three lines of arithmetic, and name whose numbers they are:

> On 3 March: **412 customers**, roughly **$19,000** of refunds.
> On 14 November: **31,000 customers**, **$3.4M** of redress, a **21-month look-back** performed by 40
> people over 11 weeks, and a consent order.

Say: *"The claim is not that this makes you smarter. It's that it moves one date. Everything on that
second line is your own arithmetic — your incidence rate, your redress per customer, your day rate. The
only number we contribute is the first one."*

**Why this is the beat.** A finance executive does not have to believe a model to believe a date. There
is no accuracy term anywhere in that claim, no precision assumption, no calibration to attack, no
counterfactual about customer behaviour. And every executive in that room has personally sat through the
sequence on the right-hand side. You are not selling them a capability; you are showing them a scar and
telling them when the cut happened.

This is also where a seven-minute demo earns its 25 points for impact and its 25 for feasibility
simultaneously, because the mechanism and the money are the same picture.

**Beat 5 — 4:45 to 5:45. The look-back, in ten seconds.**

*"Now the other half. It's 14 November. You've found it. Legal needs the population."*

Type, in plain English: *"Every customer since 1 January who said a points redemption credit did not clear
before interest was assessed."*

Returns: **31,412 customers**, each row carrying conversation id, turn, date and the quote. Export.

Say: *"That is the eleven weeks and the forty people. And unlike a sample, that is the population, with
the evidence attached to each name — which is what your remediation programme actually has to produce."*

This is the beat a COO costs in their head instantly, because they know the day rate. Let the silence sit
for two seconds.

**Beat 6 — 5:45 to 6:30. What did you know, and when.**

Back to one customer — the 6 February caller. Her ledger entry, two columns:

| | |
|---|---|
| **What this was worth when it was written** | A one-off billing query. Resolved, refunded, closed. No pattern existed. Contribution: nil. |
| **What it is worth now** | The earliest recorded instance of a systemic issue, and the date on which the institution was first told. |

Say: *"Your bank's record now shows the date it was first told — and it shows that on that date, nobody
could reasonably have known. That is not an admission, that is a defence. It is the difference between 'you
ignored eleven hundred warnings' and 'here is the exact date the pattern became visible, and here is what
we did within eleven days.' Nothing else in the bank can produce that, because nothing else stores what it
thought at the time."*

That paragraph is doing two jobs: it lands the one genuinely novel mechanism, and it pre-empts the
discovery objection before the General Counsel in the room raises it.

**Beat 7 — 6:30 to 7:00. The ending.**

Kill the screen. Black.

> *"Every conversation you just saw is one this bank already owned. It paid to record it, paid to
> transcribe it, paid to store it for seven years, and then never read it. We need no new data, no new
> consent, and no contact with a single customer."*

Then the ask, which is the real ending:

> **"Give me your last five remediations and the date you found each one. In six weeks, I'll give you five
> different dates."**

Stop there. That close converts a demo into a falsifiable, cheap, fast pilot run on the client's own data
with the client's own labels — and crucially, **they can approve it without believing anything you just
said.** That is the most valuable property a close can have.

**Marked as needing to be built:** the cluster time-series view (Beat 2), the case-file document (Beat 3),
the two-date screen (Beat 4), the NL look-back query and export (Beat 5). The ledger entry with both
values (Beat 6) exists and needs only relabelling. See §8.

### What the demo must not do

Seven things. Each one of these feels good to whoever built the system and lands flat or badly with
someone who runs a business.

1. **Do not show a risk score, a confidence number, or a ranked list of individual customers.** The moment
   a number appears claiming to predict a person, you have volunteered for cross-examination on
   calibration — and you would lose, because the confidence value takes 21 distinct values across 5,112
   emissions with 0.85 alone at 28.4%, is a menu rather than a distribution, and is calibrated against
   nothing. **Counts and quotes cannot be attacked.** Show counts and quotes.
2. **Do not show the investigator agent thinking.** Watching an agent plan and call tools thrills
   engineers and reads to an executive as an unsupervised system forming opinions about customers. Show
   its output document, never its chain of thought. Its own numbers — 29/50 verdicts, 27/48 routing on a
   queue where 43 of 48 cases are one desk — are not numbers you want examined in a room.
3. **Do not show the architecture, the three layers, the 908 tests, or the module-separation guard.** In
   the seven minutes they are noise. In the twelve minutes of questions they are excellent answers, and
   in the written pack they are where the engineering-quality score is won. Different artefacts, different
   audiences.
4. **Do not demo "the model beats the regex."** It is a comparison against a baseline you built yourself
   and any competent reviewer will say so within a sentence. If you need a comparison, compare against
   *the bank's actual current process*: a 1–2% QA sample and a taxonomy written two years ago.
5. **Do not make a save-rate or retention claim anywhere, in any beat.** Every one invites *"what is your
   precision on my book"*, and §4 of your own brief says you have no answer. The clock claim contains no
   precision term. Keep it that way.
6. **Do not show a customer being helped by an offer.** There is no outbound surface, and the instant you
   imply one you have donated the UDAAP conversation — turning a disclosed hardship into a sales trigger —
   to the other side for free.
7. **Do not say "AI" more than once.** Those two people have heard it four hundred times this year and
   the word now subtracts credibility from anything adjacent to it.

---

## 7. Why it wins

### What is genuinely new

Three things, ordered by how hard they are to copy.

**Point-in-time knowledge reconstruction.** Both the then-value and the now-value of every piece of
evidence persist, so "what did this institution know on 14 March" is a read rather than a rebuild. I have
not seen this in a conversation product, and I do not think it exists in one. It is the actual invention
here. It was built as a forecasting feature and it is an audit feature, and audit features in banks are
worth considerably more than forecasting features, because they are bought by people with no alternative.

**A verbatim citation contract enforced at validation time.** A decision cannot exist without a resolvable
quote of four or more consecutive words matched on word boundaries; failure is a validation error, not a
warning. 5,736 signals produced 11 non-verbatim and 2 relocated. Every GenAI conversation product in the
market has a hallucination problem in exactly this spot, and not one of them publishes a fidelity
denominator. For a model-validation team, this is the difference between approvable and not. Copyable in
principle; almost nobody does it, because it requires you to make your system fail more often.

**Cross-customer accumulation of unlabelled claims.** Everyone aggregates *categories*. Nobody aggregates
*claims that have no category yet*. That is the mechanism that finds an issue that did not exist when the
taxonomy was written, and it is the only one that can.

Per-customer cross-channel memory itself — the thing the current framing leads with — I would not claim
as new. Twilio shipped it in May 2026. It is copyable, the brief says so, and defending it is a fight over
six months of lead time. Note however that Twilio's documented design decision is explicitly the opposite
(*"keep only the current truth"*), they are a CPaaS that no bank will hand its complaint transcripts to,
and their audit trail is a roadmap item. So it is a real competitor to the *idea* and a poor competitor
to the *product*.

### Why it beats the obvious objection

*"We already own Verint, and we already have an attrition model."* Three moves, in order.

**Concede completely and fast.** *"Yes. You read every call. You read them one at a time, and you score
them for how the agent handled it. That is a good product and I am not replacing it."* Conceding
immediately buys you the next ninety seconds, and refusing to concede costs you the room.

**Then the category test, asked as a question.** *"Can you produce, this afternoon, a list of every
customer who mentioned a specific product problem in the last ninety days, with their quote attached? Not
calls — customers. Not a sample — all of them."* They cannot. Their speech analytics can run an ad-hoc
keyword search, which returns *calls* not *customers*, has no memory, no accumulation, no cross-channel
join and no first-told date — **and it requires someone to have already guessed the keyword.** That is the
whole argument in one clause: a query tool cannot find an unknown unknown, and every issue that matters is
an unknown unknown until the day it is not.

**On the attrition model, refuse the fight.** *"Your attrition model is fine. I am not in that business."*
Under this framing you never have to compete with a model the bank's own data science team built and
defends.

And there is a credibility play available here that I would take deliberately, because it converts your
single biggest liability into your strongest signal of seriousness:

> *"We tested whether this kind of memory improves per-customer ranking. At every scale we could afford,
> it does not beat chance — we pre-registered it, we published it as a failure, and a version with every
> scoring mechanism switched off beat it. That is precisely why this product does not rank customers. It
> counts what customers told you, which is a fact, not a forecast."*

Two finance executives will read that as unusual integrity, and an AI judge scoring evaluation quality
will reward it heavily. It also permanently removes the one line of questioning that could unravel the
pitch, by getting there first.

### The honest weaknesses of my own recommendation

A review that finds no fault in its own answer is not worth reading. Five:

1. **It is a cost-avoidance sale**, which is slower than a revenue sale and usually needs a trigger — an
   open finding, a recent remediation, a new CCO in post. Qualify for the trigger on the first call.
2. **The value is lumpy.** You cannot promise four issues a year. The pilot on historical events is what
   converts an unpromisable benefit into a measured one, which is why Phase 0 is non-negotiable.
3. **There is a real ceiling.** The system finds problems customers *notice and describe*. A mispriced
   fee nobody spots is invisible to it, permanently. Say so before someone else does.
4. **Deletion and retention are currently a failing answer**, and the first compliance reviewer will find
   it. Build it.
5. **"So it is a better complaints MI report"** is the dismissal you must survive. Your defence is Beat 4
   and Beat 5: a date and a population export are not a report, and no MI tool produces either.

---

## 8. What to build first

Ranked. Roughly eight weeks of work to make the §6 demo real, and about half of it is the corpus rather
than the code.

| # | Build | Effort | Why it is here |
|---|---|---|---|
| **1** | **The cluster layer.** Group extractions across customers by the *claim*, not the label. Embed extraction text, assign to existing centroids with a deterministic merge/split rule so cluster identity is stable week to week, model-write a cluster name from its member quotes, and alert on rate-of-change against the cluster's own trailing baseline. Keep the design rule: the counting and thresholding stay deterministic Python, the model only reads and names. | 2–3 weeks | This is the actual new capability and it does not exist. Hardest sub-problem is cluster stability across days; solve it with assignment-to-centroid, not re-clustering. |
| **2** | **Population-level corpus generation.** Extend the authoring layer to plant an *issue arc*: a start date, an incidence curve, an affected cohort, expressed in varied language across four channels. Plus a distractor layer — three or four ambient grumbles at stable rates, one *decaying* issue, and one real-but-flat issue the system should correctly **not** fire on. | 3–4 days | Without a planted population-level ground truth there is no honest evaluation and the demo is theatre. The deliberate true negative is worth more in the room than another win. |
| **3** | **Time-to-detection evaluation.** The metric that replaces everything currently measured: days from first planted instance to cluster alert, across N seeded issues at varying incidence and expression variety, with false-cluster rate as the counterweight. Pre-register it. Report the distribution and the misses. | ~1 week, after 1 and 2 | This single number is what the entire pitch rests on, and it is the number the AI judge will look for. |
| **4** | **The case-file document.** Header facts, ten cited quotes, population list, export. A document, not a dashboard. | ~1 week | 70% of the demo's screen time and the entire human workflow. |
| **5** | **The two-date screen.** Detection date, actual discovery date, elapsed days, three lines of accrual arithmetic. | ~2 days | The moment. Trivial to build, disproportionate value. Do not over-design it. |
| **6** | **NL look-back query and export.** Plain-English query → filtered evidence set → CSV/parquet with id, turn, date, quote. Thin translation layer over ledger retrieval. Show the count before the export. | 4–5 days | Beat 5, and it is the year-two revenue line in miniature. |
| **7** | **Relabel the retro column.** Not "the score went up" — *what the record showed then, and what it shows now.* | ~1 day | It already works. Only the words change, and the words are the whole point. |
| **8** | **Deletion and retention.** Tombstoning, per-jurisdiction retention windows, proof-of-deletion artefact. | ~1 week | Not for the demo. For the first compliance review, which you will fail without it. |

**What to stop doing, explicitly.**

- **Retire the nine-arm ranking experiment to an appendix**, with one honest line. It is well-run work on
  a question the product no longer asks, and left in the foreground it only generates counter-evidence in
  Q&A. Used as described in §7 it becomes an asset.
- **Drop the attrition value chain.** Five million accounts, 5%, 40%, 30%, 10%, $550 — six multiplied
  assumptions and **no false-positive leg on 1.9 million conversing non-leavers**, meaning it silently
  assumes 100% precision. Two finance executives will find that in about ninety seconds and everything
  after it will be discounted. Replace it with the four-input clock chain in §6 Beat 4, every input of
  which is the client's own number.
- **Move the model-versus-lexicon table to the appendix.** It is a comparison against a baseline you
  built, and it belongs in the engineering pack where it is evidence, not in the room where it is a
  target.

---

## The second idea, and which I would build

**Coached-victim scam and elder financial exploitation detection**, sold into a deposit-taking bank rather
than a card issuer. It is the strongest pure-money story available: over $7.7bn in losses from 201,266
complaints, average above $38,000, up 37% on 2024, and FinCEN's own advisory FIN-2022-A002 states the
mechanism that makes conversation essential — a coached victim's transactions are *authorised* and
individually plausible, so no amount of transaction monitoring sees it, and the only tell is what the
customer says. It is the one direction where accumulation is not merely present but *necessary*: the arc
runs over weeks — a new friend online in week one, a mention of a fee that must be paid first in week
three, a wire request in week five — each utterance harmless, the sequence damning. Retro re-scoring is
literally the mechanism: the call about the new friend becomes evidence the day the wire is requested. The
consuming process is a SAR and EFE alert queue that already exists and is legally required. And it is by
far the most emotionally powerful seven minutes you could build.

I would still build conduct surveillance first, for three reasons: the money is the customer's rather than
the bank's, so a spectacular value story converts to a modest price; at a card issuer it is
deposit-and-wire weighted and therefore the wrong buyer for the client hypothesis; and two executives who
asked specifically about **dollar value impact** will feel the moral force and then ask which line of the
P&L it comes out of.

But it is not a competing product. It is the same machine, the same ledger, the same review queue and a
different routing rule, with one new signal family — about a day of content authoring. **Make it the
second module in year one**, and show it as a thirty-second coda after Beat 7 only if the room has time
and you have read them as wanting it. It is the single best proof you own that the layer is genuinely a
layer, and it costs almost nothing to build once the first product exists.
