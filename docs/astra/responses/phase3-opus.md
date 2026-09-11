# Phase 3 — the recommendation

**Written 2026-09-11, for a 20:30 IST gate.** The direction argument is for after tonight. §0 is the
tonight/build split, and it is first because you need it first.

---

## The decision, in five words

**Accumulate across customers, not within one.**

That is the whole recommendation. It changes the *axis* of accumulation and nothing else. Every build
rule in `CLAUDE.md` survives verbatim — never discard a sub-threshold signal, code counts and the model
reads, ground truth authored before the text, retro re-scoring observable rather than asserted. The
extractor, the ledger, the citation contract, the corpus generator, the eval harness, the deployed
pipeline, the 908 tests: all unchanged. What changes is what you group over, what you sell, and who
signs.

The long version:

> **The product is the record of what your customers told you, and when.** Not a score that predicts a
> person. A standing layer that reads 100% of conversations and produces two objects no bank can produce
> today: **the date the institution was first told about a problem**, and **the list of every customer
> who told it, with their own sentence attached.** Sold to the Chief Compliance Officer or the Head of
> Complaints, out of complaints and remediation opex — a cost line that already exists and is already
> being spent on forty contractors listening to a sample.

I recommended this in phase 1 from the brief alone. Phase 2 strengthened it on the team's own documents.
Phase 3 does not soften it. But phase 3 adds the thing the first two lacked: **the experiment that would
settle it, on real public data, for under $400 and about five weeks** — §6. Until now my direction had
the same defect I charged theirs with: it was unmeasured. That is now fixable and cheap, and naming the
fix is the actual output of this phase.

**Why this is not a reversal of anything you built.** Under attrition, the mechanism you are proudest of
— an entry that stores what it was worth *then* and what it is worth *now* — is a scoring device whose
value is unproven, on a stratum where a version with every mechanism switched off ties it (13–11–6,
`p=0.839`). Under conduct, the identical mechanism is **point-in-time institutional knowledge
reconstruction**, which is an audit artefact, is the genuinely novel thing in the entry, and is already
measured: **239 of 485 entries worth more now than at write, 0 of 485 under a plain count.** Same code.
Same field names. The reframe does not discard the strongest thing here. It rescues it.

And the name already fits. *An ear on every call* is a surveillance sentence. It was always the right
name for this product. Do not rename anything.

---

## 0. Tonight versus build — the split, up front

You have hours, zero dry runs completed, and no deck for the US story. So tonight is almost entirely
**subtraction and relabelling**. Every item in the left column is words. Nothing in it requires a commit.

| Tonight — words only, ~90 min of prep | Needs build — pitch as direction, do not fake |
|---|---|
| **Delete the $1.65M chain.** Replace with the three-number money answer (§2). | The cross-customer cluster layer (2–3 weeks) |
| Say the nulls out loud before anyone finds them — chance gate, `dumb-ledger` (§5, Q3) | Population-arc corpus with planted issue + distractors (3–4 days) |
| Relabel what the demo proves: a record, not a prediction (§3) | Time-to-detection metric, pre-registered (~1 week after the above) |
| Deploy the CFPB split as evidence *for*, not a wound to manage (§2, §5) | The CFPB historical back-test — **the undeniable thing** (~1–2 weeks on top) |
| Put the direction, the price and the duration on the table in **minute one** | Case-file document view (3–5 days; the UI framework exists) |
| Move the buyer off Head of Retention Analytics | NL look-back query + population export (4–5 days) |
| Say 239/485 with its 0/485 control, on stage | ASR-degradation curve (1–2 days, ~$50) |
| Put the reproducibility stack on stage, not in an appendix | Ledger deletion / tombstoning (~1 week) |
| Four slides maximum. Do not build a deck. | Confidence float → three tiers (1 day, a formality) |

**If you can only do four things tonight, do these, in this order:** delete the money chain · say the
nulls first · relabel the demo · put the ask on the table. The first three are pure subtraction and make
the pitch *shorter and easier to deliver cold*, which matters when you have not rehearsed. The fourth is
the swing, and it is the one that answers the question the judges actually asked.

---

## 1. The product idea, in one paragraph

**Ear on Every Call is a conduct-evidence layer.** It reads 100% of a bank's customer conversations —
calls, chat, secure messages, complaint free-text, agent wrap-up notes — extracts what each customer
actually claimed with the verbatim quote, conversation id and turn index behind it, and accumulates
those claims **across unconnected customers** rather than within one. When enough customers describe the
same thing, it opens a case file: what the cluster is, the date of the earliest instance, how many
distinct customers, and ten quotes from ten different people, with the full affected population
exportable. It is bought by the **Chief Compliance Officer**, championed by the **Head of Complaints**,
co-signed by **General Counsel**, out of complaints and remediation opex. It solves the problem that
every remediation a bank has ever paid for was described to its call centre, individually, hundreds of
times, for a year or more before anyone joined the dots — and the bank, which kept every transaction,
threw away every narration. It does not score a customer, does not predict anything, and has no outbound
contact surface. It counts what is already true and shows you the evidence.

**This differs from the current direction.** Card attrition predicts an event about a person. This
counts a fact about an institution. The difference is not cosmetic: it moves the unit of analysis from
the customer to the issue, which moves the buyer, the budget, the consuming process, and — decisively —
takes every unmeasured thing in this entry off the critical path.

**What happens to the work already done: almost none of it is lost.** Concretely:

- **Survives untouched (Layer 1 + Layer 2 + infra):** extractor, citation contract, append-only ledger
  with all four score fields, re-scorer, threshold check, corpus generator framework, multi-seed harness,
  run manifests, separation guard over 45 modules, 908 tests, AWS pipeline, DLQ and poison-record
  isolation, cost/latency instrumentation, model-swap capability, 30 UI routes.
- **Changes:** the *content* layer — signal family definitions, phrase pools, planted arcs. The brief
  prices this at "roughly a day of authoring plus ~$0.45 of model spend." For a population arc it is
  3–4 days, not a day, because you must plant an incidence curve and distractors as well as fragments.
- **New code:** one aggregation module (cluster layer) and one metric (time-to-detection). That is it.
- **Deleted:** the attrition value chain. One document.

**And that cheapness is the originality claim in your submitted contract being true rather than
asserted.** The submission says *"one layer, many teams… none of these is the headline; the layer is."*
Phase 2 §2.4 found that this claim and the "Reuse: 5 vs 3" column in `04-ALTERNATE-STORIES.md` cannot
both hold — either re-pointing is cheap, in which case Reuse was never a reason to stay, or re-pointing
is expensive, in which case the layer claim is weaker than the contract says. Re-pointing for real, and
finding it costs three weeks and not three months, resolves that contradiction in the honest direction
and proves the 15 originality points rather than claiming them. **You are not changing the entry. You
are executing it.**

---

## 2. How the value becomes obvious

This is the section you said you most need, so I am going to be blunt about the mechanism before giving
you the words.

### Why the current chain cannot be fixed

A finance executive does not disbelieve your number. He disbelieves your **chain**. Every multiplication
is a place where he substitutes his own assumption and watches your answer collapse. Five million
accounts × 5% × 40% × 30% × 10% × $550 gives him **six** such places, and he only needs one to discount
everything downstream — including the numbers that are genuinely strong.

He will find at least three, and they are not subtle:

1. **5% collides with your own beat 1.** You verify 0.7–1.0% closing per month, 8–12% a year, CFPB
   2025-12-30, corroborated against Amex at 11.8%. Then you multiply through 5%. The bridge is the
   voluntary/involuntary split, which your own folder says is *"not published anywhere"* and rests on a
   2012 trade estimate. Two numbers for the same quantity, a factor of two apart, eleven minutes apart.
2. **No false-positive leg.** 1.9 million conversing non-leavers on the same placeholder book have no
   number attached. The chain silently assumes precision 1.0. You have not measured precision on any
   real book and §4 of your own brief says so.
3. **The repair destroys the number.** *"A queue doesn't need precision, it needs ranking"* is correct
   and it is the best idea in your folder. It also means the honest quantity is the **delta in saves at
   fixed capacity**, not the value of working 30,000 names. Those are different quantities and the
   second is much smaller and uncomputed.
4. **There is no cost side at all.** At ~2,000 cases per analyst-year, 30,000 cases is roughly fifteen
   FTE. Against $1.65M gross, that is most of the number. Plus model spend, integration,
   identity resolution, and an SR 26-2 validation cycle you yourself say costs the client's team time.

You cannot patch this. A chain with six assumptions and no cost side is not repaired by adding a seventh
assumption for cost. **Delete it.**

### The replacement — three numbers, ordered by how hard they are to puncture

Finance people accept three shapes without argument: **a price you can look up**, **a cost they already
pay, replaced**, and **an arithmetic where they supply every input but one**. The current chain is none
of them. Here are all three.

**One — the price of the blind spot.** Uncontestable; both inputs are checkable in the room.

> Your bank records, transcribes and stores 100% of your calls. It reads about two percent, to score
> agents. Reading all of it costs **$1.58 per thousand conversations**. On a twenty-million-conversation
> book that is **$31,600 a year**. There is no assumption in that number — it is a published token price
> times a token count we measured, and it is $0.0982 per thousand if you want it cheaper on Nova Lite.
> The reason nobody reads all of it is not cost. It stopped being cost about eighteen months ago and
> nobody re-checked.

This is not the value argument. It is the *enabler*, and it goes early because it converts the room's
question from "prove your model works" to "so what is in the other 98%." Do not stop here — phase 1 §1
is right that a capability gap with no owner cannot be sold.

**Two — the substitution.** This is the fundable number, and every input is theirs.

> When you confirm an issue, you have to scope the affected population. Today that is a sample, listened
> to by contractors. You know your day rate and you know it is something like forty people for eleven
> weeks. Use your number, not mine. We produce the **population**, not a sample, from the same recordings
> you already pay to store, with each customer's own sentence attached to their name, in an afternoon.
> That is not a forecast of anything. It is the same work, done by reading instead of by sampling.

A COO costs this in his head in about four seconds, because he has signed the invoice. It is a real
single-event cost, it recurs, and it converts directly into a fee. **This is the number that makes the
project sellable**, which is one of the three things the judges said they are judging.

**Three — the clock.** The big one. Name it, price the experiment, and refuse to state it yet.

> Every remediation has an accrual curve — customers harmed per month until you find it. Move the
> discovery date left and the population stops growing. You know your accrual rate, your redress per
> customer, and your look-back cost. **I contribute exactly one number: how much earlier.** I do not
> have it yet. I am asking for three weeks and about four hundred dollars to go and get it on real
> public data, and I will tell you if it comes back null.

### The verbatim money moment

Say this when asked "what's the dollar impact," and say it in this order:

> "Three numbers, and I'll tell you which ones I'd defend in front of your board.
>
> **One.** You store 100% of your calls and read two percent. Reading all of it costs $1.58 a thousand —
> thirty-two thousand dollars a year on a twenty-million-conversation book. That's arithmetic, not a
> forecast.
>
> **Two.** Every look-back you've ever run was forty people for eleven weeks producing a sample. We
> produce the population with the quote attached, in an afternoon. Use your day rate. That's a cost you
> already pay, and it's the same work done by reading instead of sampling.
>
> **Three** is the big one and I don't have it: what an earlier discovery date is worth. Every input to
> that is yours except one, and the one is mine, and I haven't earned it yet.
>
> I'd rather give you two numbers I can stand behind and one I'm going to go and earn, than a chain of
> six assumptions that arrives at a bigger number."

**That last sentence is the point of the whole section.** Two people with finance backgrounds are
deciding whether you would embarrass them in front of a client. A $1.65M number they do not believe
scores worse on impact than a $32,000 number they do, because disbelief contaminates everything
downstream — including quote fidelity and the byte-identical re-run, which are the two best assets you
own.

### The objection to this section, and the answer

*"Impact is 25 points. If you delete the only million-dollar number, don't you score zero?"* No. You are
not deleting dollars; you are replacing one fragile seven-figure number with two defensible ones and one
named-and-priced unknown. Impact is scored on **what the judge believes when he walks out**, not on the
largest integer you said. And the look-back substitution is comfortably a seven-figure recurring number
at any real bank — you just make them compute it, which means they own it.

---

## 3. What to demonstrate

**Seven minutes inside an eighteen-minute slot, plus ~12 minutes of questions.** Tonight you demo what
exists. You do not fake the cluster layer, and you do not skip it either — you show what it will be, and
say plainly that it is three weeks out.

### The eighteen minutes

**0:00–1:00 — the claim and the ask, before anything else.**

> "I'm going to show you a system that reads 100% of a bank's customer conversations and keeps a record
> of what the bank was told, and when. By the end I want three things from you: whether the product is
> right, whether the money is real, and three weeks to run one experiment on real public data that would
> settle it. Everything on screen is synthetic — competition rule — and every number in it is one we
> planted. Judge the mechanism, not the number."

Your own folder's best tactical call was "project on the table in minute three." Move it to minute one.
A CEO can approve an experiment without believing anything else you say, and putting it first means
every subsequent minute is him evaluating a thing he has already been offered rather than waiting to
find out what you want.

**1:00–3:00 — the problem, stated so a finance person feels it.**

Not *"the bank reads every conversation and remembers no customer"* — that names a capability gap with
no owner and no budget line, and it walks you straight into a category with seven entrenched vendors.
Say instead:

> "Every remediation your bank has ever paid for was described to your call centre, by name, with a
> date, hundreds of times, months before anyone joined the dots. Each call was handled correctly,
> refunded, coded to a generic bucket, and closed. The bank was told. It kept the transaction and threw
> away the narration."

Then the price of the blind spot (§2, number one).

**3:00–10:00 — the demo. Seven minutes, live, on what you already have.**

**Beat 1 (90s) — one call, one quote, "the bank learned nothing."**
Day 0. The transcript on the left; the extracted record on the right — signal type, verbatim quote,
conversation id, turn index, timestamp, channel. The customer mentions the $95 fee in passing. The agent
handles it perfectly.
Say: **"This call was handled well. The agent did everything right. And the bank learned nothing."**
Nine words. Do not elaborate. Move.

**Beat 2 (90s) — day 74. Nothing was discarded.**
Score crosses, a case opens, and the day-0 remark now contributes materially more than it did.
Say: *"Nothing was thrown away. That remark was worth almost nothing on day 0. It's worth something now,
and both values are stored."*

**Beat 3 (2 min) — THE MOMENT. Retitle it. This is the strongest screen you own.**
Full screen, two columns, on the day-0 entry:

| What this bank's record said about day 0, **on day 0** | What it says about day 0, **today** |
|---|---|
| A one-off fee grumble. Handled, closed. Contributed almost nothing. No case existed. | The earliest recorded instance, and the date the institution was first told. |

Say:

> "This is the only system I know of that answers *what did we know, and when did we know it* as a read
> instead of a rebuild. On day 0 this institution could not reasonably have known. On day 74 it could.
> It can now prove **both** — and the second half of that is a defence, not an admission. In our test
> book, **239 of 485 entries are worth more now than the day they were written. Under a plain count of
> signals, zero of 485 are.** That is the mechanism, and that is the only number we have about it."

Currently 239/485 appears in neither `00-READ-THIS-FIRST.md` nor `01-THE-STORY.md`. It is the single
quantified statement in the repo about the thing you claim as the invention. Say it on stage.

**Beat 4 (90s) — the evidence panel, built from real model output.**
Ten extractions from the keyed 10-seed run, ten different customers, each with the verbatim quote,
conversation id, turn and date. These are genuine Haiku 4.5 outputs from 6,990 conversations, not a
fixture. Say:

> "Of 5,736 extractions, **eleven were not verbatim and two were attributed to the wrong turn**. A
> decision that cites a quote it can't resolve fails validation — it isn't a warning, it's an error.
> Every GenAI conversation vendor in this market has a problem in exactly this spot and not one of them
> publishes a denominator."

**Beat 5 (60s) — where it goes, labelled as unbuilt.**
One static screen, watermarked *not built — three weeks*. A case-file document: header (issue, first
observed date, distinct customers, conversations, channels, weeks, growth against its own baseline),
then ten quotes from ten different customers, then an export button.

> "Same mechanism, different axis. Instead of accumulating across time for one customer, accumulate
> across customers for one claim. This is a mock-up — I'm not going to show you a screen we haven't
> built. It's three weeks and about four hundred dollars, and §6 is what I'd measure with it."

**Showing a labelled mock-up is strictly better than faking it and strictly better than omitting it.** A
CEO who has been shown one honest mock-up trusts the four live screens more, not less.

**10:00–14:00 — the direction, and why the measurements chose it.** This is the section that wins or
loses the room. Words in §5, Q1 and Q3.

**14:00–16:00 — what is built and what is not.** 908 tests. A deployed AWS pipeline agreeing with local
to the last decimal. A 30-seed sweep re-run a month later from a different commit coming back
**byte-identical except the git SHA and elapsed seconds**. A module-separation guard over 45 modules
that makes it structurally impossible for the offline reader to see the answer key. $1.58/1,000, p50
1,333 ms. A model swap priced at $0.027705. Then the gap, named: the cross-customer layer does not
exist.

**16:00–18:00 — the ask.** Three weeks, one engineer, under $400 of model spend, pre-registered, with a
walk-away. §6.

### On slides

**Do not build a deck tonight.** A twenty-slide deck assembled in four hours and delivered with zero dry
runs is worse than none. Build **four** full-screen slides, each carrying one object: (1) the claim,
(2) the three money numbers, (3) built / not built, (4) the ask. Everything else is the live system.
Forty-five minutes of work, and it is a stronger presentation than a deck — presentation is 10 points
and a confident four-slide talk over a working system outscores a nervous deck every time.

### What the demo must not do

Carried forward from phase 1, all still correct, one now moot:

1. **No risk score, no confidence number, no ranked list of individual customers.** Counts and quotes
   cannot be cross-examined. A score can.
2. **Do not show the investigator agent thinking**, and keep its numbers off stage — 29/50 verdicts and
   27/48 routing on a queue where 43 of 48 cases are one desk are not figures you want examined in a
   room. Keep the code; it is your case-file generator.
3. **Do not show the architecture or the 908 tests during the seven minutes.** They are excellent
   answers in the twelve minutes of questions and they are where the AI judge's score lives.
4. **No save-rate or retention claim anywhere.**
5. **Do not imply an outbound offer.** There is no offer surface and the instant you imply one you have
   donated the UDAAP argument for free.
6. **Say "AI" once.**
7. *(Moot under the reframe: the confidence float. You are not showing a score, so the whole
   calibration question never arises. Bucket it to three tiers in a day and stop discussing it.)*

---

## 4. What to keep

You said you would rather not discover later that a reframe quietly threw away the strongest thing here.
It does not. Here it is explicitly.

### Load-bearing — must survive any reframe, and does

| Asset | Why it survives, and why it is stronger under the reframe |
|---|---|
| **The extractor + citation contract** (≥4 consecutive words, word-boundary matched, validation failure not warning) | The core asset, full stop. Under a prediction product it is plumbing; under an evidence product **it is the product**. 13 bad in 5,736 with the denominator published is the best number in the repo for a regulated buyer |
| **The ledger's four fields** (`contribution_at_write`, `score_at_write`, `contribution_now`, `score_now`) | The actual invention. Becomes point-in-time institutional knowledge reconstruction, which is an audit artefact. Already measured: 239/485 vs 0/485 |
| **The corpus generator with ground truth authored before the prose** | This is what makes *any* future measurement possible, including the ones that are about to decide whether this is real. It is also why re-pointing costs days, not months |
| **The multi-seed harness, run manifests, seed lists, git SHAs, the byte-identical re-run** | The AI judge's entire score. The hardest thing in the entry to reproduce — and phase 2 §2.6 stands: your folder says three times that the demo is the only unreproducible asset, and that is exactly backwards |
| **The separation guard over 45 modules** | Makes an answer-key leak structurally impossible rather than promised. Model-validation teams have never seen this from a GenAI vendor |
| **Deployed pipeline, DLQ, poison-record isolation, alarm observed firing** | Feasibility and production readiness is 25 points and this is the only direct evidence for it |
| **Cost and latency** — $1.58/1,000, $0.0982 on Nova, p50 1,333 ms | The enabler for reading 100%, and money argument number one |
| **Model-swap capability** priced at $0.027705 | Proves vendor independence, which a bank cares about and almost no GenAI vendor can demonstrate |
| **`TRAJECTORY_TEAM` + absence of any outbound surface** | The real safety case. Present the routing map as the headline and the absence as the supporting detail — phase 2 §2.8, and it is the correct ordering now that line 283 is fixed |
| **The 30 UI routes** | The case-file view is a new route in an existing framework, not a new app. This is why the case file is days rather than weeks |
| **The zero-key replay path** | An auditor's reproducibility property. Never a product claim — your folder already has this right |

### Sunk cost — stop carrying, and what to do with each

| Asset | Disposition |
|---|---|
| **The nine-arm ranking experiment as a headline** | Demote to appendix. **Keep it as the credibility play** (§5, Q3) — it is worth more said out loud than buried |
| **30–0–0 on diffuse arcs as the accumulation headline** | Retire. Offline-labelled, on a reader that finds 617 of 2,700 planted signals, from a corpus whose records have reversed twice. Your own decision 14 was to keep it; I think that is wrong, and under the reframe you do not need it |
| **The attrition value chain** | Delete. Not caveat — delete. §2 |
| **Desk coverage 59/282 → 177/282 as a headline** | Retire. The threshold is a top-K cut over the *offline* ranking, so the model column is an upper bound against a bar calibrated for a different reader. Correctly forbidden as card evidence already; it is also methodologically weaker than it looks |
| **The investigator agent's 29/50 and 27/48** | Off stage until re-measured on a queue that is not degenerate. Keep the code |
| **Confidence float calibration work** | Bucket to three tiers, one day, close the ticket. Under the reframe nobody sees a score, so this stops being a governance question at all |
| **"Retention lift against a matched control" as the anchor metric** | Was named in the submission; is not built; should not be. Replaced by time-to-detection (§6) |
| **"The demo is the only thing a competitor cannot reproduce"** | Delete the sentence from all three files. It is false, and it is the stated reason for a stage-minute allocation, which means it will survive after the conditions change |

### One design rule the reframe adds, and it is against my own recommendation

**The population export is a recall floor, never a population of record.** At 0.6549 recall, roughly a
third of a planted population is absent. A machine-generated list that looks authoritative and is
systematically under-inclusive would exclude customers from redress they were owed — which is itself a
conduct exposure, and a worse one than anything on the attrition side. The export must be used to
**expand** a structurally-derived population (everyone charged fee X), never to substitute for one. Put
this in the product, in the contract, and say it unprompted in the room. I got this wrong in phase 1 and
it is the strongest argument anyone has made against my own direction.

---

## 5. The three questions that decide it

These are the three stated judging criteria, asked in a CEO's and a COO's own words. Nothing else
decides tonight.

### Q1 — "Who writes the cheque, and out of whose budget?" *(= could I pitch this and win a project)*

This is the one your entry has been weakest on, and it is the one they said out loud. The current answer
— Head of Retention Analytics — is the worst available choice, and phase 2 §2.12 explains why: a
modeller is the buyer most professionally equipped to audit an uncalibrated, unvalidated feature, and
your beat 4 is an unbroken sequence of concessions aimed at exactly that person. You picked the auditor
as the first signature at the moment your evidence is weakest.

**Say:**

> "The Chief Compliance Officer signs. The Head of Complaints champions it and demos it internally for
> me. General Counsel co-signs, and I win him rather than brief him. The budget is complaints and
> remediation opex plus operational-risk issue management — **both of which are already being spent, on
> people doing this by hand with a two-percent sample.** I'm not asking for new budget; I'm asking to do
> the same work by reading instead of sampling.
>
> The second budget — legal and remediation programme spend, for the look-back — is bigger than the
> first and it opens itself the first time an issue is confirmed. I don't sell it in the first meeting."

And have the trigger ready, because he will ask what makes them buy *now*: an open audit finding, a
remediation they have just paid for, or a new CCO in post. Qualify for it on the first call.

**If he says "we already own Verint,"** three moves, in this order:

> "Yes. You read every call, one at a time, and you score the agent. That's a good product and I'm not
> replacing it." *(Concede immediately and completely. Refusing to concede costs you the room.)*
>
> "Can you produce, this afternoon, a list of every customer who described a specific product problem in
> the last ninety days, with their quote attached? Not calls — customers. Not a sample — all of them."
>
> "You can't, and neither can they, because speech analytics is a query tool. It answers questions you
> already thought to ask, and **every issue that matters is an unknown unknown right up until the day it
> isn't.** Your complaint taxonomy was written two years ago, so by construction it cannot contain the
> bucket for a problem that started last month."

### Q2 — "Give me the dollar number." *(= dollar value impact)*

§2, the verbatim money moment. Say it in the order given: the checkable price, then the cost they already
pay, then the one you are going to earn. Close on *"I'd rather give you two numbers I can stand behind
and one I'm going to go and earn, than a chain of six assumptions that arrives at a bigger number."*

If he pushes for a single headline figure, give him the substitution, not the clock: *"Your last
look-back. Forty people, eleven weeks, your day rate. That's the number, and it's yours, not mine."*

### Q3 — "Everything you've shown me is data you wrote. Why should I believe it works on real conversations?" *(= how strong is the product)*

This is the deepest question in the room and you have the best possible answer to it, because it is the
one place where publishing your failures pays. **Answer in three moves, and do not shorten any of them.**

**Move one — concede the frame, completely.**

> "You're right, and it's worse than you think. Our headline accumulation result asks whether an
> accumulating scorer recovers arcs we authored to require accumulation. That's circular and we say so
> in our own documents."

**Move two — give them the nulls before they find them.** This is the move that converts the entry's
biggest liability into its strongest signal of seriousness:

> "So we pre-registered a test against chance. A seeded random ranking that ignores every signal is a
> shipped arm in our harness. **We won 18, lost 8, tied 4 — you need about 21 of 30 for that to mean
> anything. We published it as a failure.** Then we built a version with every scoring mechanism
> switched off. **Corrected for tie-break luck it came out 13–11–6, p=0.839 — no detectable difference
> between all of our scoring machinery and none of it.** Whole-portfolio, our ranking is 8th of 9 arms:
> recall 0.115 against random ranking's 0.113.
>
> So as a per-customer predictor, I cannot show you this works. I'm not going to pretend otherwise in
> front of two people who'll find it."

Phase 2 §4.4 found that your objection playbook currently *offers to run* a scorer-versus-count
comparison whose nearest synthetic version has already been run and come back a tie. Volunteered, that
is disarming. Discovered, it is disqualifying. Volunteer it.

**Move three — the reversal, which is the real answer.**

> "Here's the part that matters. The same measurements say what this *is* good at, and they're
> unambiguous. **Extraction recall 0.6549 against 0.2435 for a rule engine**, over 10 datasets and 6,990
> conversations. **Thirteen bad quotes in 5,736**, denominator published. $1.58 a thousand. p50 1.3
> seconds. A 30-seed run re-executed a month later from a different commit, **byte-identical except the
> git SHA**.
>
> And the only real-world text we've ever tested — **150 hand-marked US consumer complaints, 55 of them
> credit card, not written by us** — says the same thing. It fires on **29 of 29** documents marked as
> carrying a signal. Of what it finds on card narratives, **23 of 24 is complaint escalation**. It gets
> **churn intent right 1 time in 8.**
>
> Read that split as one finding instead of row by row and it isn't ambiguous: **on real card language,
> this is a complaint and conduct detector, not a churn predictor.** That evidence cost us nothing, it
> arrived after we'd chosen a direction, and it told us we'd chosen wrong. So we changed the product
> instead of changing the sentence."

**That last clause is the single most valuable thing you can say tonight.** Two finance executives are
deciding whether you would embarrass them in front of a client. A team that ran an experiment capable of
killing its own product, published the failure, and then *acted on it* is the answer to that question.
It also lands directly on the AI judge's evals criterion — and phase 2 §5 was that your self-criticism
had never once changed what you were building, only what you said about it. This is the sentence that
makes that charge false.

*(Same split, opposite sign: under attrition, CFPB churn-intent 1/8 is a wound to be managed and you
cannot honestly quote 23/24 while discounting 1/8 from the same corpus. Under conduct, the entire split
is evidence for you and you quote it whole. That asymmetry is itself an argument for the reframe.)*

---

## 6. What would make this undeniable

**One experiment. Real public data. External ground truth you did not author. Under $400 and about five
weeks.** Everything else on either of our build lists is secondary to this.

### The CFPB historical back-test

**The claim to test:** on real customer complaint language about a real issuer, a cluster describing a
systemic issue forms measurably before the date that issue became public.

**The design:**

1. Pull the **CFPB Consumer Complaint Database** — public, free, hundreds of thousands of published
   narratives, each carrying date received, product, sub-product, issue, **company**, and state. You
   already ingest this corpus for the 150-narrative benchmark, so the path exists.
2. Pick **3–5 issuer/product pairs with a publicly dated event**: a consent order, an enforcement
   action, a public fee-practice change, a disclosed remediation. The event date is the ground truth and
   **it is external to you.**
3. Take all narratives for that company and product for the 24 months before each event.
4. Run the extractor, run the cluster layer, ask one pre-registered question: **on what date does a
   cluster describing the mechanism first form, and how many days is that before the public event
   date?**
5. Publish the distribution of days-earlier, the misses, and the false-cluster rate on control
   company/product pairs with no known event.

**Why this is the undeniable thing, and nothing else is:**

- **It is not synthetic.** Every other number in the entry is on text you authored against a key you
  authored. This is the single largest structural weakness of the whole submission and this experiment
  removes it.
- **The ground truth is not yours.** A consent-order date is a public fact. You cannot plant it, tune to
  it, or be accused of authoring an arc that your accumulator was built to recover. That is precisely
  the circularity charge your own folder makes against the arms programme, and this experiment is immune
  to it.
- **It is legal under the competition rules.** CFPB publishes narratives only with consumer consent and
  scrubs PII before publication. "Synthetic or anonymised only" is satisfied. This is the one real
  dataset available to you.
- **It measures the product's actual claim**, not a proxy for it.
- **It is cheap.** 50,000–250,000 narratives at $1.58/1,000 is **$79–$395** of model spend.

**Cost and duration, itemised:**

| Item | Duration | Model spend |
|---|---|---|
| Population-arc corpus (planted issue + distractors + one deliberate true negative you must *not* fire on) | 3–4 days | ~$5–20 |
| Cluster layer — embed extraction text, assign to stable centroids, weekly distinct-customer counts, rate-of-change alert against each cluster's own trailing baseline | 1 week demo-grade, 2–3 weeks stable | ~0 |
| Time-to-detection metric on synthetic, pre-registered | ~1 week | ~$100–350 |
| **CFPB back-test on 3–5 real events** | ~1–2 weeks on top | **$79–395** |
| Case-file document view | 3–5 days | 0 |
| Two-date screen | 1–2 days | 0 |
| **Total** | **~5 weeks, one engineer** (≈3 weeks for a demonstrable version without the CFPB run) | **under $400** |

**Pre-register it and state the walk-away out loud tonight:**

> "If a cluster does not form before the public event date on real complaints about real issues, I will
> come back and tell you it didn't, the same way we published the chance-gate failure."

**The honest risks, and say them yourself:**

- **Complaints to a regulator are already-escalated and self-selected.** A cluster in CFPB data forms
  *later* than one would in the bank's own call centre, so any lead time you measure is a **lower
  bound**. That biases against you, which is the right direction for a bias to run and is worth saying.
- **Media reflexivity.** Complaint volume spikes after press coverage. Mitigate by measuring the
  **first-told date** — the earliest narrative describing the mechanism — rather than the spike, and by
  checking against a news timeline. The first-told date is far more robust to this confound, which is
  fortunate because it is also the product's headline artefact.
- **It may come back null.** Real risk. Publish it either way; a published null on a pre-registered real-data
  test is worth more to the AI judge than a win on synthetic.

### The two cheap items I would buy alongside it

**The ASR degradation curve — 1–2 days, ~$20–50.** Corrupt the synthetic transcripts at known word error
rates, re-run extraction recall, publish the curve. Every number in the entry is on clean authored text;
the production input is ASR output, which at a card issuer runs materially worse on accented and noisy
audio. This is the largest single unmeasured factor between synthetic and real performance, it produces
a genuinely novel number, and it answers the AI judge's "accuracy evidence" criterion directly. It is
the best value-per-hour item on either of our lists and it improves the entry regardless of direction.

**Ledger deletion and tombstoning — ~1 week.** The append-only ledger has no purge, forget or
proof-of-deletion. That is currently incompatible with a bank's records-retention schedule and with
state privacy deletion rights, and it is the first thing a compliance reviewer will find. It is not for
the demo. It is for not failing the first compliance review of a product whose buyer is the CCO.

*(Deprioritised but real: drift and reflexivity monitoring — phase 2 §7.3. Once a case brief appears on
an account and agents learn that a fee grumble opens a case, the recorded language changes, and because
the ledger is cumulative that drift propagates into every historical comparison. `score_at_write` from
before the change stops being commensurable with `score_now`. The audit property you sell is the
property that breaks first. For a regulated deployment this is a larger model-risk gap than the
confidence float, and the confidence float has a document to itself.)*

---

## Where I am overriding — mine and theirs

**Overriding myself:**

| Phase 1/2 position | Now | Why |
|---|---|---|
| "Do not demo the model beating the regex" (P1 §6.4) | **Reversed in P2, kept reversed, and it is now stronger** | *What does the AI actually do* needs an answer, and under the conduct reframe the CFPB split stops being a wound and becomes the headline real-data evidence |
| The confidence float disqualifies showing a score (P1 §6.1) | **Moot** | The product shows no score. Bucket to three tiers in a day and the question never arises again |
| "Do not change direction tonight" (P2 §8) | **Refined, not reversed** | Do not change the *demo*. Do change the *claim* and the *ask*. Those are separable and only the demo needed rehearsal |
| Rename the product "Earwitness" (P1 §4) | **Withdrawn** | *An ear on every call* is already a surveillance sentence. It was always the right name for this product. Renaming mid-competition is cost with no benefit |
| Population export as a deliverable (P1 §2) | **Constrained** | Recall floor to expand a structurally-derived population, never a population of record. 0.6549 recall makes an under-inclusive list a conduct exposure (P2 §7.2) |
| "The clock chain is puncture-proof" (P1 §6, Beat 4) | **Demoted to number three** | My $3.4M and 256 days are authored fixtures exactly as 58 days is. It only becomes real after §6 |

**Overriding the team:**

| Their choice | My call |
|---|---|
| Card attrition, kept on `04-ALTERNATE-STORIES.md` scoring | **Overridden.** The lead wins that table only on Reuse, Reg and T5 — three columns that measure your convenience, not the buyer's experience. On buyer-facing dimensions alone it loses. And the CFPB evidence arrived for $0 *after* the choice and points elsewhere |
| Head of Retention Analytics as buyer | **Overridden.** CCO signs, Head of Complaints champions, GC co-signs |
| The $1.65M chain | **Deleted**, not caveated |
| "The demo is the only unreproducible asset" (stated 3×) | **Overridden.** The reproducibility stack is. A synthetic demo on an authored fixture is the *most* reproducible thing in the entry |
| 30–0–0 as the accumulation headline | **Demoted.** Offline reader, corpus-dependent, reversed twice |
| "Treat regulation as a constraint, not a threat to monetise" | **Overridden.** Correct about *external* enforcement — CFPB headcount is down ~1,300 from ~1,700 and leaning on that would read as not having checked. But a contracting federal regulator relocates conduct risk to state AGs, private class actions and internal audit; **the buyer here is internal and an internal audit budget does not track CFPB staffing.** A whole direction was closed on an argument that covers one of its framings |
| "The choosing is over. Do not re-open it." | **Overridden, for one specific reason:** the choosing machinery has been pointed at a decision exactly once and returned "keep going." Self-criticism that only ratchets toward the incumbent choice is not a check on the incumbent choice |

**Keeping, explicitly, because they are right:** US over UK, with £650 reserved as the single hard-tariff
answer and "UK" said in the same sentence · the project on the table early · three signal families
claimed rather than eight · the synthetic declaration in the first thirty seconds · the T3
consuming-process test, which is the best discriminator either of us produced and which my direction
passes perfectly, because the unit of action is an issue and there is no customer to contact · the
routing map as the real safety case.

---

## The honest case against this recommendation

A phase-3 answer that finds no fault in itself is not worth acting on. Five, in descending order of how
much they should worry you.

1. **My direction has never been measured. Theirs has been measured and has failed.** Those are not the
   same thing and I will not dress the second as an advantage. What I can defend, at exactly this
   strength: **my direction requires fewer unmeasured things to be true, and the things that *are*
   measured are its specifications rather than its assumptions.** That is a real difference in kind. It
   is not a proof, and §6 exists precisely because it is not a proof.
2. **Cluster stability is the hard part and I have priced it at 2–3 weeks.** Clusters that split and
   merge week to week destroy the time series the whole product rests on. Solve it with
   assignment-to-existing-centroids and a deterministic merge/split rule, never re-clustering from
   scratch. If that takes four weeks instead of two, the schedule slips; it does not change the answer.
3. **It is a cost-avoidance sale**, which is slower than a revenue sale and needs a trigger. Qualify for
   the trigger on the first call and do not chase accounts without one.
4. **The value is lumpy.** You cannot promise four issues a year. That is exactly why the six-week
   retrospective back-test on the client's own last five remediations is non-negotiable as the first
   engagement — it converts an unpromisable benefit into a measured one against events they have already
   documented.
5. **There is a real ceiling.** The system finds problems customers notice and describe. A mispriced fee
   nobody spots is invisible to it, permanently. Say that before someone else does.

---

## The one thing to hold on to tonight

You do not have to win the room on the product. You have to win it on the fact that you ran an
experiment that could have killed your own product, published the failure, and then **changed the
product rather than the sentence**. That is the sentence, and it is true as of tonight:

> "We spent two months trying to make this predict which customer leaves. We pre-registered the test
> against chance and we lost it. We built a version with every scoring mechanism switched off and it
> tied. We published both. Then the only real-world text we ever tested told us what this actually is —
> and we changed the product. What I'm asking for tonight is three weeks and four hundred dollars to
> measure the new claim on real public data, and a walk-away if it comes back null."

Two people with finance backgrounds, deciding whether you would embarrass them in front of a client,
will hear that as the answer to their question.
