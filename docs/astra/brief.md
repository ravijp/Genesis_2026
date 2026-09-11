# Ear on Every Call — factual brief

A conversation signal layer for financial institutions, built for a company-internal AI competition
(Track A: client-facing agentic AI). Built and demonstrated on synthetic data, which is a competition
rule.

This document states what the system is, what has been measured, what has not, what the market looks
like, and what directions the capability could be pointed at. **It deliberately contains no
recommendations and no conclusions.** Where a choice has been made, it is reported as a fact about the
current state, not as an argument for that choice.

---

## 1. The problem as originally stated

Every financial institution runs millions of customer conversations a year — phone calls, chats,
complaints. These are the first place a customer says something is wrong: *"I'm thinking of moving my
money."* *"This is the third time I've called about this fee."* *"I just lost my job."*

Almost none of that reaches anyone who can act. Quality teams listen to a small sample to score agents.
The rest is transcribed, filed, and forgotten.

The tools banks own work **inside a single interaction**. Call analytics, agent-assist and complaint
systems score a call, a chat or a channel, then archive the result. The signal is not carried to the
next call, the next channel or the next agent. A customer can show frustration in a chat in March,
raise a complaint in May, and call to threaten leaving in July, and the institution treats all three as
separate events.

Stated in one line: **the bank reads every conversation and remembers no customer.**

---

## 2. What the system does

A per-customer **signal ledger** that accumulates evidence across conversations, channels and time, and
**re-scores earlier evidence when new evidence arrives**.

Four stages:

1. **Listen** — read 100% of conversations as text, not a sample. Overnight batch, not real-time, so
   the cost that matters is per conversation rather than latency on a live call.
2. **Extract** — pull out what the customer said (intent to leave, money stress, a life event, a
   repeated complaint) with a confidence value and **the exact quote and timestamp behind it**.
3. **Remember and re-score** — keep a standing per-customer record that adds signals up across
   conversations and time. A weak signal today plus a weak signal next month can sum to a strong one.
4. **Serve** — one queryable feed several teams read. A person decides every action.

### The design rule

> **Code counts and remembers. The model reads and judges.**

Accumulation, decay, corroboration and thresholds are deterministic, unit-tested Python. Reading
natural language and weighing ambiguous evidence is the model's job. A test enforces the separation:
the offline extractor cannot import the ground-truth plan.

### Three layers

- **Layer 1, deterministic core, no LLM:** synthetic corpus with ground truth authored before the
  prose · append-only signal ledger · re-scorer (decay, corroboration, cross-channel, escalation) ·
  threshold check.
- **Layer 2, agentic:** extractor (conversation → signals + the quote behind each) · investigator agent
  that plans, calls tools (ledger, conversations, transactions, accounts, prior cases) and emits a
  decision. Bounded: max 6 steps, max 2 retries, per-investigation cost cap checked before each call.
  Budget exhaustion returns `insufficient_evidence` rather than raising.
- **Layer 3, human:** ranked review queue; approve, dismiss or route. Dismissal writes back to the
  ledger.

### Evidence discipline

A decision must cite at least one evidence reference — conversation id, turn index, and a quote of **at
least four consecutive words** of that turn, matched on word boundaries. A decision citing an
unresolvable reference fails validation and is retried. This bounds splicing, not meaning: a quote can
still drop a leading negation, which is why the case file prints the citation for a human to read.

### The retro-scoring mechanism

Every ledger entry stores four numbers, not one:

| Field | Meaning |
|---|---|
| `contribution_at_write` | what this entry added on the day it arrived |
| `score_at_write` | the customer's total that day, using only what was known then |
| `contribution_now` | what it adds today, given everything since |
| `score_now` | the customer's total today |

Both values persist, so a point-in-time query is a read rather than a rebuild.

### Structural constraints, by construction

- **No outbound contact surface exists anywhere in the system** — no route, no button, no handler. Not
  disabled; absent. A grep of the source for an offer or eligibility concept returns nothing. What
  exists is a routing map (`TRAJECTORY_TEAM`) sending financial distress → collections, life event →
  vulnerability, churn intent → retention.
- **Transcripts only, never audio.**
- **The ledger is append-only.** There is no delete, purge or forget method.
- Runs with **zero API keys** against a committed response cache; a fresh clone reproduces every
  published number.

---

## 3. What has been measured

All figures from a multi-seed harness writing run manifests with seed lists and git SHAs. Denominators
included throughout. **Losses are reported alongside wins.**

### Reader comparison — model vs rule engine

Two readers over the **same 282 conversations** with the **same planted ground truth**. The lexicon is
a hand-tuned 26-regex fallback that exists so the system runs without an API key. The model is Claude
Haiku 4.5.

| Signal family | 26-regex lexicon | Claude Haiku 4.5 |
|---|---|---|
| Churn intent | 16 / 77 planted conversations | **40 / 77** |
| Complaint escalation | 1 / 65 | **60 / 65** |
| Life event | 9 / 68 | **50 / 68** |
| Financial distress | **33 / 72** | 27 / 72 — *the model loses* |

A larger keyed run across **10 datasets and 6,990 conversations**: extraction recall **0.6549** for the
model against **0.2435** for the lexicon. Quote fidelity **11 non-verbatim and 2 relocated out of 5,736
signals**. Counterweight: the model also fires roughly **7× more unplanted extractions** than the
lexicon.

### Desk coverage — generic retail-banking corpus

Both readers' signals through the **same ledger at the same threshold**; denominators are planted
counts.

| Desk | rule-engine reader | model reader |
|---|---|---|
| Complaints | 0 / 20 | 20 / 20 |
| Vulnerability | 0 / 20 | 19 / 20 |
| Retention | 1 / 20 | 16 / 20 |
| Collections | 9 / 20 | 10 / 20 |
| Overall coverage | 59 / 282 | 177 / 282 |

The model column is an **upper bound**: the threshold is a top-K cut over the offline reader's ranking,
held fixed across arms.

### Does memory beat forgetting — nine ranking arms at equal alert budget

30 seeds, 5,796 outcome customers, paired seed-by-seed with an exact sign test.

- On **diffuse** arcs (evidence spread thin across conversations), the full ledger beats both
  capped-memory arms **30–0–0**, `p<0.001`, under both tie-break rules. The two arms that never discard
  a weak signal rank first and second of nine.
- On **concentrated** arcs it loses **0–30–0** to three separate arms.
- **Whole-portfolio it is 8th of 9 arms** — recall 0.115 (665 / 5,796) against random ranking's 0.113
  (657 / 5,796).
- **Against chance on diffuse arcs it does not win: 18–8–4, `p=0.076`.** A seeded RNG that ignores
  every signal is a shipped arm. This was pre-registered with significance as the bar, and is published
  as a failure.
- **`dumb-ledger`** — every scoring mechanism switched off — **beats the full ledger on diffuse arcs
  18–7–5, `p=0.043`**, which becomes 13–11–6 `p=0.839` once ties are randomised, because 70.8% of that
  arm's queue is decided alphabetically against the full ledger's 0.0%.
- A pre-registered headline from an earlier corpus **died** on a rebuild: 29–0–1 became 15–13–2,
  `p=0.851`.
- Records have **reversed twice across two corpus rebuilds**, so they describe the corpus at least as
  much as the mechanism.
- Every arm figure above is on the **weak (rule-engine) reader**, which finds 617 of 2,700 planted
  signals and leaves two of four desks receiving no case at all. This crowds every arm between 0.113
  and 0.145.
- The same arms measured with the **model** reader at feasible scale (10 datasets, 200 customers) come
  out **5–4–1, `p=1.00`** — and a free control with the offline reader at that same scale gives
  **4–3–3, `p=1.00`**, i.e. at 200 customers every arm sits on chance. Reproducing the 30-seed scale
  with a model reader needs ~52,000 sequential model calls.

### Retro re-scoring, observed

**239 of 485 ledger entries are worth more now than at write** under the full ledger, and **0 of 485**
under an unweighted count.

### The agent

- Verdicts **29 / 50** (16/25 caught, 13/25 dismissed, 0 abstained).
- Routing **27 / 48** (2 wrong, 19 declined).
- Evidence resolves on the **first** attempt **50 / 50**, no repairs.
- The routing figure is measured on a queue already flattened by reader coverage: the `complaints` row
  of its confusion matrix is entirely empty because no complaint customer ever crossed under the
  offline reader, and 43 of 48 scorable cases are one desk.

### Real-world complaint text — CFPB benchmark

150 hand-marked US consumer complaint narratives, of which **55 are credit-card** (51 general-purpose
or charge, 4 store).

| | Card (55 docs) | Non-card (95 docs) |
|---|---|---|
| fired something on a document marked as carrying a signal | 29 / 29 | 52 / 54 |
| got the exact signal type right | 26 / 35 marks | 66 / 77 marks |
| false positives, (document, type) pairs | 27 / 185 | 51 / 303 |
| **churn intent specifically** | **1 / 8** | 4 / 5 |

Of what the reader finds on card narratives, the overwhelming majority is complaint escalation
(**23 / 24**). This split is **post-hoc**, not pre-registered. CFPB narratives are complaints by
construction — everyone in that corpus was angry enough to write to a regulator, which is not what a
servicing call looks like.

### Cost and latency

- **$1.58 per 1,000 conversations read** (Claude Haiku 4.5); **$0.0982 per 1,000** (Amazon Nova Lite).
- **$0.0306 per investigation.**
- Reader latency p50 **1,333 ms**, p95 **2,162 ms**.
- A model-swap comparison across the same 282 conversations cost **$0.027705**.

### The confidence value

The model emits a confidence float that is used as a **direct multiplier** in the score, sharing a
field with the rule engine's hand-set constants. Measured: it takes **21 distinct values across 5,112
emissions**, ten of which cover 95.3%, with **0.85 alone at 28.4%** — a menu rather than a
distribution. Removing it entirely moves **10.5%** of the queue under a model reader (**20%** of the
top-150 under the offline reader), and one signal family is completely inert (100.0% unchanged on all
30 datasets). It is not calibrated against any observed outcome.

### Engineering state

908 tests (903 pass, 5 skip) · linter clean · a module-separation guard over 45 modules · 30 UI routes ·
one deployed AWS pipeline agreeing with the local pipeline to the last decimal place · re-running the
same book twice (260 messages) produces the same 34 ledger entries and the same 1 case · a deliberately
malformed transcript is isolated and raises while healthy records commit, and the deployed alarm has
been observed firing (OK → ALARM → OK) in CloudWatch history.

---

## 4. What has not been measured

- **Precision on any real book.** Every haircut in every value chain is applied to customers who leave.
  Customers who stay and are flagged anyway have no number attached.
- **Retention lift against a matched control** — the anchor metric named in the original submission —
  is not built.
- **Whether transcript signals predict attrition beyond structured data.** No published card-specific
  study establishes this, and none has been run here.
- **Whether customers talk about any given event, in volume, before it happens.** No published US
  figure for issuer contact rates was found. It is a client input for every candidate direction.
- **Calibration.** The score is not a probability. Nothing is trained against an observed outcome. It
  is an ordinal ranking.
- **Subgroup / bias testing.** Accent, dialect and proficiency can proxy protected characteristics.
  Untested.
- **Data deletion.** The append-only ledger has no mechanism to honour a deletion request.
- **Almost every own-measured number above was measured on a generic retail-banking corpus with no
  credit-card content in it.** The CFPB split in §3 is the exception.

---

## 5. Market context — US credit cards

Figures with their primary sources.

| Fact | Value | Source |
|---|---|---|
| Open general-purpose card accounts | **608 million** | CFPB Consumer Credit Card Market Report, published 2025-12-30 |
| Accounts closing | **0.7–1.0% per month** (8.4–12.0%/yr) | same, from a 2% national longitudinal credit-record sample |
| Balances | **$1.263 trillion** | NY Fed Household Debt & Credit, released 2026-08-11 |
| APR on balances assessed interest | **22.15%** | Federal Reserve G.19 |
| Effective yield (interest ÷ balances) | **13.3%** ($160bn on >$1.2tn) | CFPB 2025 |
| Charge-off rate | **3.82%** (Q2 2026) | Federal Reserve CORCCACBS |
| 90+ delinquency | **12.92% of balances** (Q2 2026) | — |
| Balance per open account | **$2,077** ($1.263T ÷ 608M) | derived from the two rows above |
| Balance per borrower | **$6,610** | — |
| Recoveries as share of gross card charge-offs | **17–27%** | Capital One Domestic Card H1-2026 27.1% (10-Q Table 26); Synchrony FY2025 21.8% (10-K) |
| Cost per new card acquired | **$500** (Amex worldwide 2025), **$549** (Amex US consumer), **$532** (JPMorganChase) | derived from FY2025 10-Ks + quarterly decks |

**Contradictions and gaps in the above, stated:**

- CFPB's own 2021 and 2023 reports say *"about 2 percent of accounts are closed each year"* — four to
  six times lower than the monthly figure implies, unreconciled, because the underlying panel changed.
- **The voluntary-versus-involuntary closure split is published nowhere.** CFPB defines both and gives
  no numbers. The commonly cited "about half" is a 2012 trade estimate.
- **Cost per new card is an upper bound.** Marketing expense also covers brand and retention spend;
  Capital One's 10-K states its marketing line includes efforts to *"attract and retain"* plus
  spend-based bonuses.
- **The balance at charge-off is published nowhere.**
- The widely circulated claim that acquiring costs 5–25× more than retaining traces to a 2014 magazine
  article that prefaces it with *"depending on which study you believe"* and cites nothing. A sourced
  alternative: Bain finds that in financial services a 5% increase in retention produces more than a
  25% increase in profit.

**Regulatory context.** SR 11-7 (model risk management) was **rescinded 2026-04-17** and replaced by
**SR 26-2**, joint OCC/Fed/FDIC, applying above $30bn; OCC 2026-13 rescinds OCC 2011-12. The CARD Act
and Regulation Z require *disclosures*, not conversations — there is no US analogue to a
regulator-mandated customer conversation. CFPB funding and headcount are materially down (~1,300 staff
from ~1,700), enforcement principles were rolled back in June 2026, and fair-lending supervision is
contracting. Under UDAAP's "abusive" prong, turning a disclosed hardship into a sales trigger is a
recognised risk shape. A credit-line decrease is an adverse action under Reg B §1002.9 with FCRA
§1681m attaching. Call recordings made for quality and training purposes are a different purpose from
analytics, and a dozen states require all-party consent.

---

## 6. Candidate directions

The engine is domain-independent. What changes between directions is **what the score predicts, who
buys it, and where the money is**. The content — signal family definitions, phrase pools, planted arcs
— has to be re-authored per direction; the cost of doing so is roughly a day of authoring plus ~$0.45
of model spend.

Thirteen directions have been profiled. **They are listed here in their original numbering with no
ranking.** `$ / event` shows published arithmetic where a primary source was found and says *no anchor*
where none was.

| # | Predicts | Buyer | Budget line | $ / event | Uses the ledger? |
|---|---|---|---|---|---|
| 1 | **Card attrition** — voluntary closure | Head of Retention Analytics | Cards retention & acquisition opex | ~$550–800 | Yes |
| 2 | **Pre-delinquency** — first missed payment, 30/60/90 roll | Head of Collections Strategy / Credit Risk | Credit loss provision + collections opex | ~$3,400 (range $2,300–5,000) | Yes |
| 3 | **Balance attrition** — transfer out / paydown-to-zero, card stays open | Cards P&L owner | Promotional pricing (interest income) | ~$705/yr | Yes |
| 4 | **Deposit flight** — outflow, rate-shopping, relationship exit | Treasury / Deposit Strategy | Deposit pricing (funding cost) | ~$271/yr | Partial |
| 5 | **Scam / elder financial exploitation** — customer being defrauded now | BSA Officer signs; Fraud Ops + vulnerable-customer lead use | Financial-crimes compliance opex | see note below | Partial |
| 6 | **Complaint escalation** — complaint becomes formal / regulator-facing | Head of Complaints / Regulatory Affairs | Complaints opex + remediation reserve | no US anchor | Yes |
| 7 | **Collections promise reliability** — will this promise-to-pay hold | Head of Collections Operations | Collections opex (dialler + agent capacity) | no anchor | Partial |
| 8 | **Mortgage loss-mit intake** — borrower hardship, eligibility | Head of Default Servicing | Servicing opex + default compliance | 42% of UPB (2019) | Yes |
| 9 | **Cross-sell from stated life intent** — imminent need | CMO / Consumer Lending | Marketing | no anchor | Yes |
| 10 | **Credit-line increase** — capacity and appetite | Head of Portfolio Management | Credit strategy | no anchor | Partial |
| 11 | **Credit-line decrease** — deterioration before the bureau shows it | Chief Credit Officer | Credit strategy / provision | no anchor | Yes |
| 12 | **SMB relationship risk** — attrition or distress | Head of Business Banking | RM coverage opex | no anchor | Yes |
| 13 | **Agent coaching / QA** — which calls need coaching | Contact Centre Ops | Contact-centre opex | ~$10s | **No** |

### Per-direction detail

**1 · Card attrition.** Margin plus avoided re-acquisition. Consuming process: a case brief for the
next inbound agent. Known weaknesses: on a placeholder five-million-account book the addressable
population works out at roughly 0.6% of the book; the voluntary/involuntary split is unpublished; and
the population that can be scored skews toward customers who complain rather than customers who leave
quietly.

**2 · Pre-delinquency.** Avoided charge-off, net of 17–27% recoveries, on a balance at charge-off that
is published nowhere. Consuming process: hardship-programme eligibility and the pre-collections queue,
both already staffed — **but hardship programmes are opt-in**, so a silent customer cannot be enrolled
without contacting them. Heavier supervisory scrutiny than attrition. A false positive here costs
roughly $430 of foregone interest against roughly $95 for an attrition fee waiver, making it about 4.5×
more precision-sensitive. Open question: whether a spoken *"things are tight"* beats a payment-ratio
trend the bank already watches.

**3 · Balance attrition.** Direct net-interest-income loss at the effective yield, not the headline
APR. Consuming process: retention-pricing eligibility. Weakness: a balance transfer out is visible
structurally the moment it happens, so the window is narrow, and customers who move balances are
rate-shoppers.

**4 · Deposit flight.** SCF-2022 median transaction balance $8,000 × FDIC Q4-2025 net interest margin
3.39% = ~$271/yr. Weakness: a deposit leaving is the loudest structural signal in retail banking, and
deposit customers contact the bank far less than card customers.

**5 · Scam / elder financial exploitation.** Consuming process: a SAR / elder-financial-exploitation
alert queue that already exists and is legally required. Money anchors: **FBI IC3 2025 Elder Fraud
Report** *(verified against fbi.gov and ic3.gov, 2026-09-09)* — **201,266 complaints** from victims
aged 60+, losses **more than $7.7 billion**, average loss **above $38,000**, at least **12,400 victims
losing $100,000 or more**, losses **up 37% on 2024**. **FinCEN Financial Trend Analysis (2024-04-18)**
*(secondary source, unverified)* — ~$27bn across **155,415 BSA filings** to 2023-06-15 ($173,733 per
filing), **72% filed by banks**. **The money is the customer's, not the bank's:** Reg E (12 CFR
§1005.2(m)) does not reach *authorised* transfers, and a coached victim authorises their own payments.
Why conversation beats structured data here, per FinCEN's own advisory FIN-2022-A002: a coached
victim's transactions are authorised and individually plausible, so the tell is in what they say.
Weakness: elder exploitation is deposit- and wire-weighted, so at a card issuer this feeds an existing
programme rather than reducing card loss; and it needs one genuinely new signal family.

**6 · Complaint escalation.** Consuming process: case-owner escalation inside the existing complaints
workflow. **This is the direction the current card evidence best supports** — 23 of 24 marked card
documents in the CFPB benchmark, against churn intent at 1 of 8 on the same corpus — and it requires no
new build. Weakness: there is no US per-case tariff; the UK's Financial Ombudsman charges a respondent
firm **£650** per upheld case and **£475** otherwise, win or lose, and took 214,600 new complaints in
2025/26 of which ~22,800 were credit cards — but no American equivalent exists, and CFPB enforcement
posture contracted through 2026.

**7 · Collections promise reliability.** Consuming process: it reorders a dial list the bank already
works — no new contact motion of any kind. Contact capacity is **capped by regulation at 7 attempts per
debt per 7 days** (Reg F §1006.14(b)(2)(i)), so better ordering has value **independently of
precision**. Fastest label available: the promise date, so a back-test settles in about a month.
Weaknesses: no published value anchor (BLS May 2025 median collector wage $47,030 is a cost anchor, not
a value one); most likely of any direction to already exist in some form; and a promise is a
per-episode judgement, so accumulation has less to work with.

**8 · Mortgage loss-mitigation intake.** Consuming process is the only legally mandated one on the
list: **Reg X §1024.39 requires the servicer to establish live contact with a delinquent borrower by
day 36** — a call they must make anyway, which this would prioritise and brief. Weaknesses: default
servicing is the most heavily regulated corner of the bank; long sales cycles; no part of the current
build is mortgage-flavoured; and the only severity anchor found is 2019 (Philadelphia Fed WP 19-19, GSE
loss severity 42% of UPB) and is cycle-dependent.

**9 · Cross-sell from stated life intent.** Largest revenue upside on the list. Consuming process: a
next-best-product flag into an existing campaign engine. Weakness: *"we listen to your service calls to
sell you things"* is the available headline, and it places the system's governance properties on the
wrong side of the argument.

**10 · Credit-line increase.** No anchor found in two searches. Utilisation and bureau data *are* the
decision inputs today, so conversation adds least here of anywhere.

**11 · Credit-line decrease.** Real value — exposure reduction ahead of a charge-off. A line decrease
is an **adverse action** requiring notice under Reg B, with FCRA attaching if it rests on a consumer
report.

**12 · SMB relationship risk.** High value per relationship. Consuming process: relationship-manager
briefing. Weaknesses: lower and more relationship-mediated conversation volume; harder to demonstrate;
value diffuse across products.

**13 · Agent coaching / QA.** The **only direction that does not use the ledger at all** — coaching is
a per-call judgement, so accumulation and retro re-scoring contribute nothing. It is also the category
Verint, NICE and CallMiner already sell into.

### Five tests these were profiled against

1. **Conversation exists** — do customers talk about this, in volume, before the event?
2. **Not already structural** — does the bank already see it in its own data, sooner and better?
3. **Consuming process** — when the score fires and the customer is *not* calling, what physically
   happens, given there is no outbound contact surface?
4. **Money is verifiable** — is there a published anchor, or a number the client already knows?
5. **Demonstrable in 7 minutes** — can accumulation and re-scoring be *shown*?

---

## 7. Competitive landscape

Surveyed 2026-09-09, capped at 14 searches — a survey of what vendors **publish**, not an audit of what
they build.

- **Per-interaction classification is universal.** Verint, NICE, CallMiner, Observe.AI, Level AI, AWS
  Contact Lens, Google CCAI Insights all read 100% of interactions and all have a GenAI layer as of
  2026. *"We read every call"* distinguishes nothing.
- **Aggregation to dashboards is also universal and is not accumulation.** Journey analytics, trend
  views and CSAT curves aggregate *for reporting*; none is a persistent per-customer feature a
  downstream model consumes.
- **Persistent per-customer conversation state has one credible published example**, and it is not a
  contact-centre vendor: **Twilio Conversation Memory**, launched **May 2026**. It LLM-extracts
  observations into an identity-resolved cross-channel profile. Retention windows are configurable;
  audit trails are on its H2 2026 roadmap.
- **Twilio's documentation describes the opposite design choice**, verbatim: *"If a customer said they
  prefer email contact in January and called in to change that preference in April, the memory system
  needs to reconcile the conflict and **keep only the current truth**."* Twilio also advertises that
  memory is stored independently of any LLM runtime so models can be swapped without losing context.
- To match the accumulation design, Twilio would still need retroactive re-evaluation of earlier
  entries, entry versioning, and deterministic re-weighting outside the model. None of those is hard.
- **Amazon Connect + Contact Lens + Customer Profiles** has the pieces on the shelf; no LLM feature
  extraction writing into Customer Profiles is published. A competent bank platform team could assemble
  a weaker version in-house.

**Published per-unit pricing:**

| | Published price | Per 5-minute call |
|---|---|---|
| AWS Contact Lens | $0.015/min → $0.0125/min at 5M+ min | ~$0.063–0.075 |
| Google CCAI Insights | $0.02–$0.04 per interaction | $0.02–0.04 |
| Snowflake Cortex | $4 per million tokens | ~$0.001–0.004 per extraction |
| **This system (Haiku 4.5)** | **$1.58 per 1,000 conversations** | **$0.00158** |

Verint, NICE, CallMiner, Observe.AI, Level AI, Genesys and Salesforce publish no per-unit rate.
CallMiner enterprise deals are reported at **$300K–$1M/yr** (trade press, not a vendor document).

**One caution on that price comparison:** Contact Lens's per-minute price includes automatic speech
recognition and the $1.58 does not, because this system works from transcripts and transcription is a
cost the client has already sunk. A transcript-in price and a speech-in price are not like for like.

**Could not verify:** whether Twilio's reconciliation also discards *evidence* as opposed to
conflicting preferences (the quote is about conflicting observations, which is the case they chose to
document); whether Twilio's entries are versioned; Amazon Q in Connect's conversation-to-feature
workflow; whether Genesys predictive engagement re-scores retroactively; NICE Enlighten XM "Experience
Memory" internals; every enterprise vendor's per-unit pricing; any unpublished roadmap.

---

## 8. Current state of the entry

Reported as fact, not as argument.

- **The current working direction is #1, card attrition, aimed at a US card issuer.** The demo, the
  narrative and the value chain are built around it. This choice is one of the things under review.
- **The demo as built:** one US cardholder with a rewards card, **$95 annual fee**, 0% intro APR, and
  an empty ledger. Three conversations.

  | Day | Channel | What happens | What the system does |
  |---|---|---|---|
  | 0 | phone | Card declined while travelling, fixed. In passing the customer says the $95 fee posted and they are not sure the card is worth it | Records a price/value objection with the verbatim quote and a low confidence. No case opens. Nothing discarded |
  | 74 | chat | Chasing a rewards redemption that has failed twice; asks what the APR reverts to when the intro period ends | Score crosses; **a case opens**. Evidence now spans two conversations and two channels, and the day-0 remark contributes materially more than it did |
  | 132 | phone | Asks for the payoff amount and what happens to their points | A conventional per-call tool catches this one. The case has been open since day 74 |

  The 58-day gap between day 74 and day 132 is the difference between two authored fixture parameters,
  not a measured result. The retro column is shown on screen: the day-0 remark's value *then* and
  *now*, both stored.

- **The value chain currently used:** five million accounts → 5% voluntary attrition → 40% conversation
  coverage → 30% voicing a leading signal → **~30,000 names, 0.6% of the book** → 10% incremental save,
  $300 margin, $250 avoided acquisition cost → **~$1.65M/year gross**. Every haircut is a fact about
  the client's book rather than about system accuracy. **The chain has no false-positive leg:** on the
  same placeholder book roughly 1.9 million conversing non-leavers have no number attached to them, so
  the chain assumes precision is 100%.
- **The commercial proposal currently on the table:** a six-week fixed-fee retrospective back-test on
  the client's existing call recordings and existing closure label, with a pre-registered success
  criterion (top-decile uplift, the feature added as a challenger against their production champion)
  and an explicit walk-away. No production integration, no customer contact.
- **Two consumption paths:** a feature in the client's existing propensity model (which refreshes on a
  batch cadence, typically monthly), and a ranked queue on one desk that reads the score as it changes.

---

## 9. The competition context

An internal company competition, Track A (client-facing agentic AI). The next milestone is a review
before the **CEO and COO**, both with finance backgrounds, which decides the shortlist for the final.
**18 minutes including a live demo, then roughly 12 minutes of questions.**

What the two reviewers have said they want to judge: **how strong the product is · dollar value
impact · could I pitch this to a company and win a project.**

Official scoring: **impact 25 · technical depth 25 · feasibility and production readiness 25 ·
originality 15 · presentation 10.** A separate AI judge scores engineering quality — evals,
reproducibility, and accuracy/cost/latency evidence.

The original submission to the committee — which functions as the contract, with room reserved for
refinement — named the lead buyer as **VP/SVP of Contact Center Operations or the Chief Customer
Experience Officer**, with the Chief Compliance Officer as co-signer, and stated the anchor metric as
**retention lift in the flagged group against a matched control**. It also stated: *"One layer, many
teams… **none of these is the headline; the layer is.**"*

Competition rules require **synthetic or anonymised data only**.
