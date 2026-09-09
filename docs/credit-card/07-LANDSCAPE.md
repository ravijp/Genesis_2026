# The landscape — who else is walking these lines

**2026-09-09, US market.** Researched to answer one question honestly: **is accumulation across
conversations actually our differentiator, or is everyone doing it?** Plus what the answer implies for
pricing and for the "not a moat" concession already in `01-THE-STORY.md`.

**Search-budget note:** this was capped at 14 searches. It is a survey of what vendors *publish*, not
an audit of what they *build*. A vendor with an unpublished capability will not appear here, and the
`## Could not verify` list at the end is where the honest gaps live.

---

## The verdict in five lines

1. **Per-interaction classification is universal.** Verint, NICE, CallMiner, Observe.AI, Level AI,
   Contact Lens, CCAI Insights — all of them read 100% of interactions and all of them have a GenAI
   layer as of 2026. **"We read every call" is worth nothing in this room.** The story already knows
   this and must keep knowing it.
2. **Aggregation to dashboards is also universal, and it is not accumulation.** Journey analytics,
   trend views and CSAT curves aggregate *for reporting*. None of them is a persistent per-customer
   feature that a downstream model consumes.
3. **Persistent per-customer conversation state has one credible published example**, and it is not a
   contact-centre vendor: **Twilio Conversation Memory**, launched **May 2026**, which LLM-extracts
   observations and stores them against an identity-resolved cross-channel profile.
4. **And Twilio's own documentation draws our line for us.** Its **observation reconciliation** step
   exists to *"reconcile the conflict and keep only the current truth."* **That is the design this
   entry inverts, stated by the nearest competitor in their own words** — the strongest single piece
   of evidence in this document, and it upgrades the differentiator from "nobody publishes doing it"
   to "the closest one publishes doing the opposite.".
5. **None of this is a moat and the story is right to say so.** It is a feature set with a lead, not a
   defensible position. Twilio is one product decision away.

**The one-sentence version for the room:** *"Everyone reads the call. We're the only ones who go back
and change what an old call was worth."*

---

## What everyone does — the vendor table

Tagged `[verified]` where a primary vendor doc or pricing page states it, `[vendor claim]` where it is
marketing copy that describes an outcome rather than a computation. All retrieved 2026-09-09.

| Vendor | What it does with conversations | Per-interaction or accumulated | GenAI layer | Pricing signal |
|---|---|---|---|---|
| **Verint** | Sentiment at interaction and moment level; auto-flags coaching and compliance; trends across sources | Per-interaction → trends | Yes | Not published; module-based quote |
| **NICE (Enlighten / Mpower)** | Journey orchestration; combines conversation + metadata + analytics | Per-interaction → journey analytics | Yes | Not published; per-session charges on top tiers |
| **CallMiner Eureka** | Interaction scoring across voice/chat/email; performance and sentiment scoring | Per-interaction | Yes | Not published. Reported enterprise deals **$300K–$1M/yr** `[vendor-adjacent trade press]` |
| **Observe.AI** | Post-fact call scoring against rubrics; coaching recommendations | Per-interaction | Yes | Subscription; rates not published |
| **Level AI** | Evaluates individual calls, routes flagged calls, samples for coaching | Per-interaction | Yes | Per-seat; rates not published |
| **AWS Contact Lens** | Transcribes, sentiment, PII redaction, compliance flagging; 100% of interactions | Per-interaction + persistent chat context | Yes | **$0.015/min** (0–5M min), **$0.0125/min** (5M+) `[verified]` |
| **Google CCAI Insights** | Per-interaction autolabelling + correlation rules; Quality AI evaluations | Per-interaction with correlation linking | Yes | **$0.02–$0.04 per interaction** `[verified]` |
| **Genesys** | Aggregates cross-channel events into unified profiles; journey health, customer effort | Per-interaction → journey level | Yes | Not published |
| **Salesforce Einstein Conversation Insights** | Records, transcribes, analyses; summaries stored natively in CRM; can trigger Flow | Per-interaction, stored in CRM and reachable by workflow | Yes | Not published; part of FSC SKU |
| **Twilio Conversation Memory** (launched May 2026) | LLM-extracts observations; identity-resolved cross-channel profile. **Reconciles conflicts to "keep only the current truth"** `[verified, their docs]` | **Accumulated — but reconciled, not retained** | Yes | Not published; platform bundle |
| **Snowflake Cortex** | LLM functions for extraction from transcripts. No built-in accumulation | Per-interaction (primitives only) | Yes | **$4 per million tokens** `[verified]` |
| **Personetics** | Proactive alerts and guidance — but on **transaction and behavioural data**, not conversations | Per-customer, wrong input | Yes | Not published |
| **nCino** | AI benchmarking and workflow guidance; not conversation-led | Not conversation-focused | Yes | Not published |
| **Zest AI, Scienaptic** | Credit decisioning and risk. **Not conversation products** — they belong in a different comparison | n/a | Yes | Not published |

---

## Where the closest competitors sit, and what they would have to build

### 1. Twilio Conversation Memory — the real one, and its own docs draw the line for us

**Launched May 2026.** It already does the hard half: LLM **observation extraction** from every
interaction across voice, SMS and chat, into a **persistent cross-channel customer profile** resolved
by identity. Retention windows are configurable and **audit trails are on the roadmap for H2 2026**.
*(Twilio product and docs pages, retrieved 2026-09-09.)*

**And then it does the opposite of us, in its own words.** Twilio documents a step it calls
**observation reconciliation**:

> *"If a customer said they prefer email contact in January and called in to change that preference in
> April, the memory system needs to reconcile the conflict and keep only the current truth."*

**"Keep only the current truth" is the exact thing this entry inverts.** That is not our
characterisation of a competitor — it is their design, stated by them, and it is the cleanest evidence
in this document that the never-discard inversion is a real design fork rather than a marketing
distinction.

**The distinction to say out loud, and it is now sourced rather than asserted:**

> The nearest thing to us isn't Verint — it's Twilio's Conversation Memory, which shipped this year
> and does persistent per-customer extraction properly. **The difference is in their documentation:
> when two things a customer said conflict, they reconcile and keep the current truth. We keep both,
> and the old one can become worth more later.** Theirs is memory for a conversation. Ours is evidence
> for a decision.

To become us it would still need: **retroactive re-evaluation** of earlier entries when new evidence
lands; **entry versioning** (what it contributed *then* vs *now*); and **deterministic re-weighting
outside the model**. None is hard. **Our lead is time and specificity, not architecture** — and their
audit-trail roadmap item is the one to watch.

**One more thing they advertise that we should not ignore:** *"Memory is stored independently of any
LLM runtime, so you can swap models without losing customer context."* **A competitor is already
selling model-swap resilience as a feature**, which is exactly the ground `06-DEFENDING-THE-SCORE.md`
covers. It raises the bar on that answer rather than lowering it.

### 2. Amazon Connect + Contact Lens + Customer Profiles

Contact Lens does 100% interaction analysis; Customer Profiles persists per-customer attributes (with
a documented size limit). **The pieces are on the shelf.** What is not published is any LLM feature
extraction writing into Customer Profiles, or any re-scoring. **A competent bank platform team could
assemble a weaker version of this in-house** — which is a real answer to "why buy", and the answer is
the ledger semantics and the evidence discipline, not the reading.

### 3. Genesys Journey Analytics

Unified profiles built from event aggregation. Reporting consolidation, not a consumed feature. Not a
near competitor on the mechanism, but it is the product a judge is most likely to name.

---

## Pricing — and a comparison we must stop making

**Published rates:**

| | Published price | Per 5-minute call |
|---|---|---|
| AWS Contact Lens | $0.015/min → $0.0125/min at 5M+ min | ~$0.063–$0.075 |
| Google CCAI Insights | $0.02–$0.04 per interaction | $0.02–$0.04 |
| Snowflake Cortex | $4 per million tokens | ~$0.001–$0.004 per extraction |
| **Ours (Haiku 4.5)** | **$1.58 per 1,000 conversations** | **$0.00158** |
| **Ours (Nova Lite)** | **$0.0982 per 1,000 conversations** | **$0.0000982** |

Verint, NICE, CallMiner, Observe.AI, Level AI, Genesys and Salesforce publish no per-unit rate at all.

### The comparison to refuse

It is tempting to say *"we are 40× cheaper than Contact Lens."* **Do not.** Contact Lens's per-minute
price includes **automatic speech recognition**; our $1.58 does not, because we work from transcripts
and transcription is the client's cost, already sunk on recordings they already keep. **Comparing a
transcript-in price to a speech-in price is exactly the kind of unlike-for-unlike a finance judge
catches**, and being caught on a pricing comparison costs more than the point is worth.

**The honest version, which is still strong:** *"Reading every conversation costs $1.58 per thousand
on top of transcripts you already have. Ten million conversations is about $16,000 a year.
Affordability was never the question."* That is already how `01-THE-STORY.md` beat 5 puts it. **Keep
it that way and do not add a competitor multiple to it.**

### What the pricing landscape actually implies

1. **We cannot be priced per-minute or per-interaction.** At $0.00158 a conversation, usage pricing
   prices us at approximately nothing and anchors the buyer on cost rather than value. **Price the
   outcome or the seat, not the token.**
2. **The enterprise comparators sit at $300K–$1M/yr for conversation analytics.** That is the budget
   line this displaces or joins — and it is the right frame for what a six-week fixed-fee back-test
   should cost. **A pilot priced like software support is priced wrong.**
3. **Cost of inference is a Q&A number, not a headline** — which `03-REFERENCE.md` §6 already
   concluded, and this research confirms for a different reason: our cost advantage is mostly an
   artefact of not doing ASR.

---

## What this does to the "not a moat" concession

**The concession stays, and it gets more specific.** The current playbook line — *"That's a real
feature set and it is not a moat — I'd rather say so than pretend"* — is correct and it now has
evidence behind it. Two upgrades:

**Add the specific competitor, because naming it is stronger than conceding in the abstract:**

> *"The nearest published thing to us isn't Verint — it's Twilio's Conversation Memory, which shipped
> this year and does persistent per-customer extraction. What it doesn't do is go back and re-value an
> old conversation. That's the part nobody's published, and I'd expect someone to within a year."*

**And keep the honest floor:** a bank platform team with Amazon Connect and Customer Profiles could
build a weaker version in-house. The reason to buy is the ledger semantics, the evidence discipline
and the fact that it exists now — not that it is unbuildable.

---

## Could not verify

- **Twilio's reconciliation is documented for *preferences and conflicting facts*.** Whether it also
  discards or overwrites *evidence* of the kind we accumulate is not stated. The quote is real and
  load-bearing, but **do not stretch it into a claim about their whole architecture** — it is about
  conflicting observations, which is the case they chose to document.
- **Whether Twilio's entries are versioned or only appended.** Audit trails are on its H2 2026
  roadmap; internals not published. If that ships as entry-level versioning, the gap narrows fast.
- **Amazon Q in Connect's conversation-to-feature workflow.** No technical detail published on whether
  extracted features write into Customer Profiles.
- **Genesys "predictive engagement"** — whether it re-scores retroactively or only forward.
- **NICE Enlighten XM "Experience Memory" internals** — whether it re-scores or is query-only.
- **Every enterprise vendor's per-unit pricing.** The $300K–$1M CallMiner range is trade press, not a
  vendor document. Treat it as an order of magnitude.
- **Personetics and nCino conversation ingestion** — both position on transactional data; conversation
  ingestion not published either way.
- **Unpublished roadmaps generally.** This survey sees what vendors say. Any of them may already have
  built accumulation and not shipped it.
