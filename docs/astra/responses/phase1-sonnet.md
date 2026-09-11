# Undertow

Build a system that watches for a customer being groomed out of their own money, months before the
wire goes out — sold to the Bank Secrecy Act officer, funded from financial-crimes compliance, proven
first against the bank's own suspicious-activity history, not against anything synthetic. Not card
attrition. Not a churn model with better inputs. The exact same engine — read everything, extract the
quote, remember it against the person, re-value the past when the present changes its meaning —
pointed at the one harm on the candidate list where the phenomenon itself is shaped like the
mechanism's proven strength: a pattern built slowly out of calls that individually look like nothing.

Call it **Undertow**. A swimmer on the surface looks fine. The undertow is what's actually happening
underneath, and it's invisible until someone is already in trouble. That is exactly the shape of an
elder or vulnerable-customer financial exploitation case, and it is exactly what every fraud tool a
bank already owns is built to miss.

## The premise is true, aimed at the wrong wall

"The bank reads every conversation and remembers no customer" is a real, well-evidenced gap —
per-interaction classification is universal among every vendor in this space, aggregation to a
dashboard is universal and isn't memory, and the one competitor with anything resembling persistent
per-customer state has published that it reconciles conflicting observations down to "current truth"
rather than keeping the old ones. Nobody accumulates without discarding. That part is correct, and not
close.

But it is not a pain. It's a capability gap, and capability gaps don't have budget lines. No bank has
ever opened a fiscal year with "we need to remember our customers better" as a line item, because
that's a description of an architecture, not a problem stated in anyone's own terms. Every real budget
line among the candidate directions is attached to a bad outcome that already has an owner, a number,
and a reason to act this year: attrition, delinquency, a complaint that turns into a regulatory event,
a fraud loss, a collections dollar. The memory mechanism is real, and it's the reason any of these
would work better than what's currently sold into that budget — but it can't be the pitch. It has to be
the thing that's revealed as the reason, after the pitch has already landed on an outcome someone is
already paying to prevent.

So: which outcome. Three questions, and they don't have the same answer. What's *true* — is the
capability actually good at this? What's *valuable* — is the number real and large? What's *sellable* —
does someone with budget and authority want to buy it this year? The current pitch, card attrition, is
sellable in the boring, comfortable sense — every retention head already owns a budget line for tools
like it — but it's the direction with the weakest evidence behind it. The experiment that matters most
here, does accumulated memory beat forgetting at the job of ranking customers by future risk, has the
full ledger finishing eighth of nine arms across the whole portfolio, worse than a random shuffle
(recall 0.115 against 0.113), and failing to clear a plain chance baseline on the exact evidence shape
— thin signal spread across many conversations — where it's supposed to be strongest (18-8-4,
p=0.076). And on the one external, non-synthetic test in the whole evidence set, 150 real CFPB
complaint narratives, the churn/attrition signal specifically gets one mark right out of eight on card
documents. That's not noise. It's the weakest number in the entire independent validation, sitting
directly under the signal family the current pitch depends on.

At the other extreme, cross-sell from a customer's stated life intent is, on paper, the largest revenue
number on the list — and it's close to unsellable, because it inverts the one structural fact that
makes any of this defensible. A system built with no outbound contact surface at all, specifically so
nothing it finds can turn into a sales trigger, cannot then be pointed at sales without becoming the
exact headline risk it was designed to avoid: *we listen to your calls to sell you things.* Highest
value, wrong direction, not close either.

Elder and vulnerable-customer exploitation is the one place all three questions land on the same
answer. It's true: the FBI's own 2025 numbers are the best-sourced dollar figures anywhere in the
evidence — more than $7.7 billion lost, up 37% year over year, an average loss above $38,000, more than
12,400 victims losing six figures, verified against two primary federal sources rather than a trade
estimate. It's valuable in a way that needs no translation for a CEO and a COO: this isn't a margin
optimization, it's people losing their retirement savings at an accelerating rate, and a regulator has
already stated in writing why the transaction record can't catch it — a coached victim's transfers are
individually plausible and self-authorized, so the tell exists only in what they say, never in what
they do. And it's sellable in the sense that actually matters: the consuming process already exists and
is already mandatory. A suspicious-activity report gets filed today, by law, the moment a bank suspects
this. Nobody has to invent a new motion, staff a new desk, or win a new budget from scratch — the
budget, the queue, and the legal obligation to act on a good tip are all already there. Compare that to
attrition, where "what physically happens when the score fires" requires inventing an outreach motion
that doesn't exist today, aimed at a customer the current value chain assumes is caught with 100%
precision, because nobody has costed what it does to the customers who were never leaving at all.

There's a fourth test, and it isn't stated anywhere in the evidence directly — it comes from reading two
separate results side by side. The measured advantage of never discarding a weak signal isn't uniform:
it wins decisively on *diffuse* arcs, evidence spread thin across many separate conversations, 30 seeds
to 0 to 0, p<0.001. It loses just as decisively on *concentrated* arcs, 0 to 30 to 0. A slow grooming
pattern is diffuse almost by definition — normalizing small requests over weeks so no single call is
alarming is the entire method. A customer about to leave over a fee, or a complaint that escalates
because of one bad call, is closer to a concentrated event. The system's best-proven property maps
cleanly onto the shape of exploitation and maps poorly onto the shape of the current pitch. That
convergence — the best dollar anchor, the only pre-existing mandatory consuming process, and the only
direction whose real-world shape matches the mechanism's own best-measured strength — is the whole
argument. It isn't a preference. It's the one place true, valuable, and sellable stop disagreeing.

| | Card attrition (current pitch) | Elder / vulnerable-customer exploitation |
|---|---|---|
| Conversation exists | Uncertain — most people who leave just leave, without calling to say so | Strong, structurally — the victim is usually the one calling, repeatedly, about routine-looking requests |
| Not already structural | Weak — tenure, product mix, and rate-shopping already sit in the warehouse | Strong — the transactions are individually authorized and plausible; the tell is only in the words |
| Consuming process exists | No — needs a new outreach motion, never costed for false positives | Yes — suspicious-activity filing is already mandatory, today |
| Money verifiable | Weak — addressable population a fraction of a percent of a placeholder book; the voluntary/involuntary split is unpublished anywhere | Strong — federal, primary-sourced, cross-verified, and rising |
| Matches the mechanism's proven strength | Poor — this is a ranking task, and ranking is where the system is weakest, worse than chance at portfolio scale | Strong — grooming is a diffuse arc, and diffuse arcs are the one place the system wins outright |

That's the case for throwing away the current wall and pointing the same engine at this one instead.

## What Undertow does

For the institution that buys it: every retail customer gets a standing record of what they've actually
said, across every call and chat, for as long as they've banked there — not a transcript archive, a
*valued* record, where each entry carries what it meant the day it was said and what it means today,
and where a remark that meant nothing in isolation gets connected, automatically, to the next one that
gives it meaning. When the combined weight of everything a specific customer has said crosses a
threshold, a case opens — not an alert, a *brief*: the full quoted, dated, channel-tagged sequence of
everything that built to this point, readable in under a minute.

Who signs: the Bank Secrecy Act Officer or Head of Financial Crimes Compliance, with the Chief
Compliance Officer as co-signer — the standard buying pattern for any BSA/AML tooling, because that's
what this is being bought as. Budget: financial-crimes compliance and BSA/AML operations opex, a line
that exists at every regulated depository institution and isn't discretionary the way a retention or
marketing budget is, because the reporting obligation behind it is a legal one. That makes this a
shorter sale than a new retention signal with no track record — nobody has to be convinced the problem
exists or that the bank must act on it; that's already settled by statute. The only open question is
whether this finds the pattern earlier and more completely than what they have now.

What changes on day one it goes live: today, a BSA analyst learns about a coerced customer three ways —
a transaction-monitoring rule trips on an unusual transfer, a teller or agent happens to notice
something off in one call and manually escalates it, or a family member reports it after the money is
already gone. All three are late, because all three require something to already look wrong in the
moment. On day one with Undertow running, that same analyst opens a morning queue that already
contains a case for a customer whose combined signal crossed threshold overnight — built not from one
alarming call but from a remark six weeks ago about "a new friend helping with the accounts" and a call
yesterday asking about the daily wire limit, connected, cited, dated, and ranked, before either call
individually would have tripped anything. The analyst isn't searching for it. The case is already built
when they sit down.

## The sentence

*Your fraud team catches the wave. We watch the undertow — for months, before it breaks.*

## The category

Not conversation analytics — that category is universal and crowded, and every serious incumbent
already reads 100% of calls with a generative layer bolted on; "we read every call" no longer separates
anyone from anyone else. Not customer memory either — the one credible competitor with anything like
persistent per-customer state has already published that its design goal is the opposite of this one:
reconcile to current truth, keep only what's still valid, discard the rest.

The right category is one banks already have a budget and a mental model for, just missing this half of
it: **the conversational case file.** Every bank already keeps a file that accumulates over the life of
a relationship and is never fully discarded — a KYC file, a customer due-diligence record, a credit
file. All of them are built from documents and structured facts about identity and money. None of them
contains a single word the customer has actually said. Undertow is that same kind of standing,
cumulative, append-only record, built instead from what people say — feeding whichever compliance or
risk desk needs to see it first. A BSA officer already knows what a case file is. This just tells them
theirs has been missing half its evidence.

## Running it inside a bank

**Where it sits.** It reads transcripts from wherever the contact-centre platform already lands them —
Genesys, NICE, Amazon Connect, an in-house ASR pipeline, whatever exists — and from the case-management
system for existing written complaint text. Overnight batch, the same design choice already made here:
the cost that matters is per conversation, not latency on a live call, because nothing here intervenes
on the call in progress. It writes to two places: its own ledger store, which is genuinely new
infrastructure, and the BSA/AML case-management tool the analyst already works in — Actimize, Verafin,
NetReveal, or an internal queue — as an *additional alert source feeding the same triage list*, not a
second screen nobody has time to check. That distinction is the whole adoption story in one sentence:
this has to show up inside the tool the analyst already opens every morning, not next to it.

**What has to be true first.** Transcripts need to already exist in text, for both phone and chat — true
at most large and mid-size banks now, not reliably true at a smaller one. A case-management system
needs to exist to receive output — true almost everywhere a BSA/AML program runs, because it's
federally required. The one prerequisite that is genuinely not reliable even at a sophisticated bank: a
single customer identity that's the same whether they called, chatted, or walked into a branch. This
system's entire value depends on attaching every remark to *one* standing person, not a call ID or a
case number, and at a bank that isn't a technology leader, the phone platform, the chat platform, and
the branch CRM often don't share a customer key cleanly. That's the honest, largest deployment risk,
worth saying plainly rather than assuming away: if cross-channel identity resolution isn't already
solved, it becomes this project's first six months, not a footnote.

**Who operates it day to day.** No new headcount to *consume* it — the same BSA analysts who already
work the queue, now seeing better-built cases inside it. A small team, two to four people, to run the
pipeline, watch the extractor for drift, and own the signal-family content — the phrase families and
thresholds that define what "grooming" sounds like, which need periodic re-authoring the same way any
detection content does. That's a real, ongoing cost, but a small one: re-pointing the content at a new
signal family runs on the order of a day of authoring and under a dollar of model spend, which is what
makes this maintainable rather than a one-time science project.

**The adoption path.** First deployment is one desk, in shadow mode, back-tested against the bank's own
confirmed suspicious-activity filings and exploitation cases from the past year or two: did the signal
exist in the transcripts before the bank's own process caught it, and by how many days. That's the
number that sells the next conversation — not a synthetic benchmark, the bank's own history. If the
lead time is real, even two or three weeks ahead of a case the bank already confirmed, the next step is
live cases feeding the existing queue, human-gated throughout, with no new headcount. Realistically: a
contracted shadow-mode result inside a quarter, production inside two, and — because the underlying
engine already routes to complaints, retention, and collections desks by design — a second desk, most
plausibly complaint escalation given how strongly that signal already reads on real complaint text,
sold into an adjacent budget in the same institution within the first year.

**What's genuinely hard here, specifically because it's a bank.** Getting access to the transcripts at
all is not a formality — recordings made for quality and training purposes are a different legal
purpose from analytics, and roughly a dozen US states require all-party consent, so privacy and legal
sign-off gates the very first transcript read, before any conversation about accuracy even starts.
Second, anything feeding a BSA/AML process inherits the joint OCC/Fed/FDIC model-risk standard that
took over this year from the older Fed guidance, applying above $30 billion in assets — independent
model validation and documentation aren't hardening added later, they're required before this touches a
live case. Third, and unglamorous: bank vendor-risk review — security certification, penetration
testing, data residency — gates procurement regardless of how good the back-test looks, and runs on its
own calendar that has nothing to do with how convinced anyone in the room already is.

## Running it across many banks

One product, not several — the ledger, the extractor, and the re-scoring engine are shared, and what
changes per desk is a content pack: the signal-family definitions, the phrase pools, the thresholds,
the routing target. That's an engineering fact, not a sales pitch, and it should stay that way for a
while. The original idea of this as a horizontal layer serving several teams at once is *correct as
architecture* and a *trap as a first pitch*. Selling "a signal layer for however many teams want one" on
day one means no single budget owner is accountable for the yes, no team feels it's theirs, and — worst
for a live eighteen-minute review — there's no single moment to build a demo around, because a platform
pitch has no story, only a diagram. The platform is real. It's a year-two conversation, not a slide in
the first one.

A top-five card issuer, a regional bank, and a credit union are not the same buyer. A large national
bank has the call volume, the existing BSA/AML infrastructure, and an in-house model-risk function that
can absorb this the way it absorbs any new detection tool — sell them the wedge-then-expand motion
above, self-serve on the engineering, heavy on the validation paperwork. A regional bank has real
exploitation exposure per customer but far less compliance infrastructure and usually no team to own
ongoing signal-family maintenance — for them this needs more of the operating model bundled in, closer
to a managed service than a platform license, which changes the margin but not the wedge. A credit
union has smaller absolute exposure per institution, but an older, longer-tenured, more geographically
concentrated membership that skews toward exactly the demographic this protects, and a
mission-driven receptiveness to "protect our most vulnerable members" that a pure P&L pitch doesn't need
at a bank — but likely can't fund a platform license at all. Say that plainly rather than pretend one
SKU serves all three: the credit union is a phase-three, shared-service story, not a first customer.

The land-and-expand motion: the wedge is the vulnerable-customer desk, funded from BSA/AML opex. The
second desk, ideally within twelve to eighteen months, is complaint escalation — the one signal family
with genuine external validation on real complaint text, sold into complaints or regulatory affairs
inside the same institution, at close to zero marginal engineering cost because the ledger is already
running. Worth saying plainly: that pairing was found after the fact, not predicted in advance, so it
should be pitched as a strong second desk, not oversold as proof of anything more than what it is. A
third desk — collections queue ordering or retention — comes later, whichever internal relationship is
strongest by then. Sell it as a point solution every time. Build it as a platform every time. That
asymmetry is the whole strategy.

## The demo

**The story.** A synthetic, twenty-two-year customer, call her Eleanor, seventy-four. Five ordinary
calls over four months. None of them, alone, is alarming: a request to raise her daily transfer limit,
"because a friend is helping me with something." A question about how gift cards work, "for someone I'm
helping." A call asking to expedite a wire. A call where she sounds distracted, asks the agent to
repeat things twice. A call asking whether a transfer can be undone once it's sent. Every one of those,
taken alone, is a Tuesday at a call centre. Nothing here would trip a fraud rule — a transfer-limit
increase is routine, a gift-card question is not unusual, a distracted elderly caller is not a flag.

**Beat by beat, seven minutes.**

*0:00–1:00.* No software on screen. Say the numbers cold: Americans over 60 lost more than $7.7 billion
to fraud last year, up 37% in a single year, the average victim loses more than $38,000, over 12,400
lost six figures or more. Then the sentence that does the actual work: every one of those victims
called their own bank, more than once, before the money moved — and the money moves through transfers
they authorize themselves, which is exactly why watching the transaction never catches it in time.

*1:00–2:30.* Show Eleanor's five interactions the way any bank holds them today: an IVR log, a chat
transcript, a wire-request ticket, three different systems, no line connecting them. Let the room feel
how unremarkable each one is on its own. This is deliberate — the entire point is that nothing here
should look like a fraud case yet.

*2:30–4:30 — the moment.* Switch to Undertow's case view for Eleanor. One timeline, five entries, dates
and channels and the exact words she used. Open the very first entry — the transfer-limit remark — and
show two numbers side by side: what it scored the day it was said, next to what the identical entry
scores today, after everything since. Then the line that should land: this case was ready for a human
being — cited, quoted, dated — three weeks before the fifth call, and two weeks before the wire that
would have gone out. On screen, plainly: *flagged 14 days before the transfer that would have
followed.*

*4:30–5:30.* Show the analyst's queue with Eleanor's case near the top, a one-paragraph brief, click a
citation and land on the exact transcript line it came from. Say the sentence that has to be said out
loud, because it's true and the room will otherwise assume the opposite: nothing here contacts Eleanor,
blocks anything, or decides anything. It puts the complete history in front of the person whose job is
to decide, and that person still decides, every time.

*5:30–6:30.* The analyst calls Eleanor. Human-initiated, bank-initiated, days before anything would
have forced it. Land the dollar figure the whole beat has been building to — the transfer that didn't
happen, in the range the FBI itself publishes as the average loss for exactly this kind of case.

*6:30–7:00 — the ending.* Pull back for three seconds: "Eleanor was one customer. This same shape exists
in your book right now, and nobody's looking, because no single call is ever loud enough to notice."
Stop on: **"You already catch the wave. We watch the undertow that built it, for months, before it
breaks."**

**What the demo must not do.** It must not claim the system decided anything or predicted anything with
confidence — the honest, defensible claim is narrower than that, and a financially literate room will
find the gap in one follow-up question if the claim overreaches it. What's actually proven here is
retrieval, not judgment: the model finds and preserves far more of what a customer said than a
rule-based reader does — roughly 65% recall against 24%, on planted evidence — and the citation it
hands a human almost never breaks, thirteen non-verbatim or relocated quotes out of 5,736. What's not
proven is the verdict layered on top of that evidence: an agent that calls it right on the order of six
times out of ten, and a portfolio-wide ranking that a random shuffle matches just as well. Sell the
first thing. Say, plainly, that the second is exactly why a human is in the loop on every case, always
— that's not a hedge, it's the actual design, and stating it removes the room's best objection before
anyone raises it.

It must not open with a dashboard, a chart, or an accuracy percentage — that's the category every
incumbent already owns, and leading with it undercuts the claim of being different from them. It must
not let the then-and-now score sit as an abstract mechanism explained in words — it has to be shown
attached to one person's one remark on screen, or it reads as a pipeline diagram instead of a story. It
must not spend demo time on the architecture — deterministic ledger, agentic reader, none of it belongs
in the seven minutes; save it for the questions after, where a technically literate room will actually
want it. And it must not end soft. The closing line is a flat statement, not a hope.

One more thing, said plainly because it's a real risk and not a technical one: this demo uses a
synthetic elderly, vulnerable persona for dramatic effect in a room of executives, and that needs care
in how it's written and delivered — respectful, not exploited for spectacle, because the pitch's
credibility rests on taking the underlying harm seriously, not on using it for effect.

## Why this wins

What's genuinely new, once "we read every call" and "we remember the customer" are both stripped off as
already-owned or already-published elsewhere: accumulating *without discarding*, and re-valuing the
past when the present changes its meaning. That's the literal opposite of the one credible
persistent-memory product on the market today, which states its own design goal as keeping only the
current, reconciled truth. It's new in a way that pays for itself only for harms shaped like this one,
though — where the entire phenomenon is a pattern built out of things that individually looked like
nothing. For anything sharper and faster than that, it isn't an advantage at all, and the pitch should
never pretend otherwise.

Why it survives the obvious objection: the bank already owns tools that read every call, and the bank
already runs models that watch for exactly this kind of fraud. Both are true, and neither one is
actually this job. The reading tools are tuned to the loud event — the call or the transaction where
something is already, visibly wrong — which is a real, solved, commodity problem, and this isn't trying
to win it twice; on at least one measured signal family, financial distress language, a plain
rule-based reader actually beats the model here, so the honest pitch never claims uniform superiority
at that job. And the fraud models are watching transactions, which is precisely the layer a regulator
has already said can't see this: a coached victim's transfers are individually plausible and
self-authorized, so there's nothing for a transaction model to catch until the money is already gone.
What's left, and what nothing else in the building does, is remembering the quiet calls before there
was a transaction worth watching — because no existing vendor's business model rewards holding onto
something that wasn't alarming on the day it happened. And it does that at a cost that matters to
whoever signs the cheque: reading a conversation here runs a fraction of a cent, well under a tenth of
what a per-minute contact-centre analytics platform bills for the same call, because it works from a
transcript the bank has already paid to create.

## What to build first

1. A new signal family, built for this specifically — grooming and coercion language: a "friend" or
   "advisor" newly directing money decisions, secrecy framing ("don't tell the bank"), urgency,
   unusual-for-this-customer requests, a third party present on the call. None of the current signal
   families are built for this, and everything downstream is worthless without it. On the system's own
   economics, this is roughly a day of authoring and under a dollar of model spend once someone commits
   to writing it.
2. A synthetic dataset built around it: several planted grooming arcs, four to six calls each across
   weeks, seeded ground truth authored before any generation, mixed into an otherwise ordinary call
   population. This is what makes the demo and any back-test credible rather than one hand-tuned
   anecdote.
3. The specific demo fixture — Eleanor, five calls, the gaps and thresholds tuned for a clean
   seven-minute arc. Be honest that the timing is authored for narrative clarity, the same as any demo
   fixture; say so if asked, rather than presenting it as a discovered result.
4. The then-and-now case view, adapted to show one person's timeline against real dates in a form a
   non-technical executive reads in ten seconds — most likely an adaptation of something that already
   exists rather than new build.
5. A real back-test design against a partner bank's own suspicious-activity and confirmed-case history
   — the actual credibility engine for a paid pilot, distinct from the demo, worth scoping early even
   though it can't run without a bank's own data.
6. A mocked BSA/AML case-management integration for the demo — a case landing in something styled like
   the tool an analyst already uses, because "what does it write to" has to be shown on screen, not
   asserted in a sentence.

## The second idea, briefly

If the sales cycle into a BSA/AML department turns out slower than expected, or the data-sensitivity of
building convincing exploitation content proves harder than a day, the fallback is complaint escalation:
the one signal family with real, external, non-synthetic validation already in hand — the overwhelming
majority of what this system finds on real, marked credit-card complaint narratives is exactly this. It
has no clean US dollar anchor the way a UK regulator's per-case fee gives that market, which is the
honest weakness, but it needs no new signal family, sells into an existing complaints workflow, and
could be demoed inside a month. I'd still build Undertow first. The dollar figure is bigger, better
sourced, and harder for a competitor to shrug off, and the mechanism's proven strength lines up with the
shape of the problem in a way it simply doesn't for a complaint that escalates in the space of one bad
call. But if I had to ship something provable in thirty days, this is what I'd ship instead — and I'd
sell it as the second desk on the same ledger within the year regardless of which one goes first.
