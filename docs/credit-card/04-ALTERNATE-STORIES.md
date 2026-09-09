# Alternate stories — 13 ways to point the same layer

**Purpose: pick one.** The system underneath does not change. What changes is **what the score
predicts, who buys it, and where the money is.** Read the two comparison tables, then the profile of
whatever catches your eye.

> ## ⚠ THE RECOMMENDATION IN THIS FILE IS WITHDRAWN — 2026-09-09
>
> **The 7–10× multiple below is wrong, and §3's T3 rating for pre-delinquency is backwards.** Do not
> act on this file's recommendation. The verdict and the corrected arithmetic are at the top of
> `00-READ-THIS-FIRST.md`. In short: recoveries run **17–27% of gross charge-offs**, the **$6,610 is
> per borrower not per account** ($1.263T ÷ 608M = **$2,077 per open account**), the balance at
> charge-off is **published nowhere**, honest net loss is **~$3,400 (range $2,300–$5,000)**, and the
> multiple is **3–9×, centrally about 5×** — before a precision haircut that makes pre-delinquency
> about **4.5× more sensitive to false positives** than attrition, which can drive it **below 1×**.
> And **hardship programmes are opt-in**, so you cannot enrol a silent customer without contacting
> them: pre-delinquency's T3 is **worse** than attrition's, not a 5/5.
>
> **This file is retained as Q&A depth and as the record of how the comparison was made.** Its
> thirteen profiles and five tests are still useful. Its §3 recommendation and the ★ ranking in
> Table B are not.

**The original headline finding, retained so the correction has something to point at:**

> **Attrition is the *cheapest* event we can predict.** Saving a card customer is worth roughly
> **$550–$800** (margin plus avoided re-acquisition). Preventing a charge-off on an average
> **$6,610** balance is worth roughly **$5,000+** net of recoveries. **That is 7–10× more money per
> event, from the same conversations, using a signal family we have already built.**
>
> And the label arrives in **90 days** instead of a year, so a back-test is faster and cheaper.

---

## 1. What every story has to survive

Same five tests for all thirteen. These are the ones that actually killed things in the red-team pass.

| Test | The question | Why it kills |
|---|---|---|
| **T1 Conversation exists** | Do customers *talk* about this, in volume, before the event? | No conversation, no product |
| **T2 Not already structural** | Does the bank already see it in its own data, sooner and better? | If yes, we add nothing |
| **T3 Consuming process** | When the score fires and the customer *is not calling*, what physically happens — **without outbound contact?** | This is the question that ends pitches. We have no outbound surface, deliberately |
| **T4 Money is verifiable** | Is there a published anchor, or at least a number the client already knows and cannot dispute? | Invented numbers destroy credibility with finance people |
| **T5 Demo-able in 7 minutes** | Can accumulation and re-scoring be *shown*, not described? | Our only unreproducible asset is the demo |

**T3 is the discriminator.** Several of the highest-value stories fail it, and that is the single most
useful thing in this document.

---

## 2. The comparison — rebuilt 2026-09-09 with anchors, denominators and a cut list

**What changed in this pass.** The first version of these tables was judgement with a dollar guess
attached. This one is anchored: every `$/event` either shows its arithmetic from a published source or
says **"no anchor"** out loud. Three stories were **cut**, two are kept only as **named refusals**, and
one new column — **ledger-dependent?** — turned out to matter more than any of the scores.

### Table A — what each story is

| # | Story (predicted event) | Buyer (signs) | Budget line | Signal families | Ledger-dependent? |
|---|---|---|---|---|---|
| **1** | **Card attrition** — voluntary closure / run-off *(the lead)* | Head of Retention Analytics | Cards retention & acquisition marketing opex | churn_intent (+ life_event) | **Yes** |
| **2** | **Pre-delinquency** — first missed payment, 30/60/90 roll | Head of Collections Strategy or Credit Risk | Credit loss provision + collections opex | financial_distress | **Yes** |
| **3** | **Balance attrition** — transfer out / paydown-to-zero, card stays open | Cards P&L / portfolio owner | Promotional-pricing (interest income) | churn_intent + financial_distress | **Yes** |
| **4** | **Deposit flight** — outflow, rate-shopping, relationship exit | Treasury / Deposit Strategy | Deposit-pricing (funding cost) | churn_intent + life_event | Partial |
| **5** | **Scam / elder financial exploitation** — customer is being defrauded now | **BSA Officer** signs; Fraud Ops + vulnerable-customer lead use | **Financial-crimes compliance opex** | *needs a new family*; nearest are financial_distress + life_event | Partial |
| **6** | **Complaint escalation** — complaint becomes formal / regulator-facing | Head of Complaints / Regulatory Affairs | Complaints opex + remediation reserve | complaint_escalation | **Yes** |
| **7** | **Collections promise reliability** — will this promise-to-pay hold | Head of Collections Operations | Collections opex (dialler + agent capacity) | financial_distress | Partial |
| **8** | **Mortgage loss-mit intake** — borrower hardship, loss-mit eligibility | Head of Default Servicing | Servicing opex + default compliance | financial_distress + life_event | **Yes** |
| **9** | **Cross-sell from life intent** — imminent need (home, auto, business) | CMO / Consumer Lending | Marketing | life_event | **Yes** |
| **10** | **Credit-line increase** — capacity and appetite for more credit | Head of Portfolio Management | Credit strategy | life_event | Partial |
| **11** | **Credit-line decrease** — deterioration before the bureau shows it | Chief Credit Officer | Credit strategy / provision | financial_distress | **Yes** |
| **12** | **SMB relationship risk** — SMB attrition or distress | Head of Business Banking | RM coverage opex | churn_intent + financial_distress | **Yes** |
| **13** | **Agent coaching / QA** — which calls need coaching | Contact Centre Ops | **Contact-centre opex — the line Verint/NICE already own** | none (per-call, not per-customer) | **No** |

**Read the last column first.** A story marked **No** cannot demo accumulation or retro re-scoring —
the only thing in this build a competitor cannot reproduce. Its score is not comparable to the others.

### Table B — how each scores

Seven dimensions, 1–5, high is good, **35 max**. All ratings `[our judgement]`, calibrated against the
anchors found in this pass and the KS-1..KS-16 record. **Reg is scored 5 = light.** This ranks the
options *behind* the settled lead; it is not a re-ranking of the lead.

| # | Story | $/event | T1 conv. | T2 not structural | T3 consuming | T4 anchor | T5 demo | Reg | Reuse | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **Card attrition** *(lead)* | ~$550–800 | 4 | 3 | 4 | 4 | 5 | 5 | 5 | **30** |
| **5** | **Scam / elder exploitation** | see note | **5** | **4** | **5** | 4 | 5 | 3 | 3 | **29** |
| **6** | **Complaint escalation** | no anchor | **5** | 3 | 4 | 2 | 4 | 4 | **5** | **27** |
| **2** | **Pre-delinquency** | ~$3,400 | 4 | **2** | **2** | **5** | 5 | 2 | 5 | **25** |
| **7** | **Collections promise** | no anchor | **5** | 3 | **5** | 2 | 3 | 3 | 4 | **25** |
| **3** | **Balance attrition** | ~$705/yr | 3 | **2** | 3 | 4 | 4 | 4 | 4 | **24** |
| **13** | **Agent coaching / QA** | ~$10s | 5 | 4 | 4 | 1 | 3 | 5 | 2 | **24 — not comparable. CUT** |
| **8** | **Mortgage loss-mit** | 42% of UPB* | 4 | 3 | **5** | 3 | 3 | 2 | 2 | **22** |
| **9** | **Cross-sell** | no anchor | 4 | 3 | 3 | 1 | 4 | **1** | 3 | **19 — refusal, not option** |
| **12** | **SMB relationship risk** | no anchor | 3 | 3 | 3 | 2 | 2 | 4 | 2 | **19** |
| **4** | **Deposit flight** | **~$271/yr** | **2** | **2** | 3 | 2 | 3 | 4 | 2 | **18 — CUT** |
| **10** | **Credit-line increase** | no anchor | 3 | **1** | 3 | 1 | 3 | 2 | 3 | **16 — CUT** |
| **11** | **Credit-line decrease** | no anchor | 3 | **1** | 2 | 1 | 3 | **1** | 3 | **14 — refusal, not option** |

\* 2019 figure, cycle-dependent. **"no anchor" means no published US per-event figure was found in
this pass — not that the value is zero.**

**Only three columns actually discriminate: T2, T3 and T4.** T1 is high nearly everywhere, because
people talk about most of these. Where a story dies, it dies because **the bank already sees it (T2)**,
because **the consuming process needs enrolment or an outbound motion (T3)**, or because **there is no
number (T4)**.

### The cut list, and why cutting is the point

| Story | Verdict | Why |
|---|---|---|
| **#4 deposit flight** | **CUT** | Its money collapsed under its own arithmetic: SCF-2022 median transaction balance **$8,000** × FDIC Q4-2025 net interest margin **3.39%** = **$271/yr**, not the "$1,000s–10,000s" the first draft claimed. And T2 kills it independently — **a deposit leaving is the loudest structural signal in retail banking.** We would be predicting a balance move from conversation while the balance itself is on the screen |
| **#10 credit-line increase** | **CUT** | No anchor found in two searches. Worst T2 on the list — utilisation and bureau data *are* the CLI decision inputs. And it is the on-ramp to #11, which this document already says never to raise |
| **#13 agent coaching / QA** | **CUT** | Scores 24 and the score is an artefact: it is **the only ledger-independent story on the list**. It throws away accumulation, retro re-scoring and the per-customer ledger — everything we are actually selling — and lands in the one budget line Verint and NICE already own |
| **#9 cross-sell**, **#11 credit-line decrease** | **Keep as named refusals** | With a CEO and a COO, *"we ruled this out and here is exactly why"* is worth more than a marginal option. #11 is adverse action under **Reg B §1002.9** with **FCRA §1681m** attaching |

### Corrections to the first version's numbers

- **#3 balance attrition halved on its own source.** The first draft implied the headline **25.2% APR**.
  The right figure is the *effective* yield: CFPB 2025 reports **$160bn of interest on >$1.2tn** of
  balances = **13.3%**. So $5,300 × 13.3% = **~$705/yr**, not ~$1,336.
- **#5's money is not the bank's money.** **Reg E (12 CFR §1005.2(m)) does not cover *authorised*
  transfers**, so the $38,506 average is the **customer's** loss. That is why the buyer is the **BSA
  Officer** and the budget line is **financial-crimes compliance opex**. Pitch it anywhere else and it
  collapses on the first question.
- **#8 mortgage keeps the best T3 and loses its dollar figure.** **Reg X §1024.39 mandates live contact
  by day 36** — a legally required call we would prioritise and brief. But the only severity anchor
  found is **2019** (Philadelphia Fed WP 19-19: GSE loss severity **42% of UPB**), and severity is
  cycle-dependent.

---

## 3. The recommendation — attrition leads, and here is what sits behind it

**The lead is settled** (see the banner at the top of this file and the verdict in
`00-READ-THIS-FIRST.md`). What follows is the bench, ranked, for Q&A and for the next quarter.

### 1st reserve — #5, scam and elder financial exploitation *(29/35)*

**The only story where the conversation beats the structured data for a reason a regulator has already
written down.** A coached victim's transactions are *authorised* and individually plausible, so the
tell is in what the customer says — which is FinCEN's own position (advisory **FIN-2022-A002**).

- **T3 is the best available short of a legal mandate:** a SAR / elder-financial-exploitation alert
  queue that already exists and is already legally required. Nothing to build, no outbound motion.
- **Two government primary anchors with hard denominators.** FBI IC3 2025 Elder Fraud Report:
  **$7.75bn across 201,266 complaints** from victims aged 60+ (**$7.75bn ÷ 201,266 = $38,506
  average**), with **12,400 victims losing ≥$100,000**. FinCEN Financial Trend Analysis (2024-04-18):
  **~$27bn flagged across 155,415 BSA filings** in the year to 2023-06-15 (**$173,733 per filing**),
  **banks filed 72%**.
- **It demos better than anything except attrition** — retro re-scoring turns an innocuous first
  conversation into evidence of grooming, which is the most vivid thing this system does.
- **Two things that must be said in the same breath as the money**, or it collapses: the $38,506 is the
  **customer's** loss, not the bank's; and elder exploitation is deposit- and wire-weighted, so at a
  **card** issuer this is a detection surface feeding an existing programme, not a card-loss story.
- **Cost to point at it: ~$0.45 and a day of fragment authoring**, plus one genuinely new signal
  family — the largest content build of anything scoring above 24, and still small.
- **Verify before quoting:** both figures were read from secondary summaries in this pass because the
  IC3 and FinCEN PDFs returned unparseable binary. **Open the primaries before saying them on stage.**

### 2nd reserve — #6, complaint escalation avoidance *(27/35)*

**The only story on this list our own card evidence actually supports.** On the CFPB benchmark's real
US credit-card narratives the reader fires complaint escalation on **23 of 24** marked documents —
against churn intent at **1 of 8** on the same corpus. Highest reuse on the list: built, deployed,
measured, zero new build.

**Why it is not the lead: there is no US dollar anchor.** The UK's £650 Ombudsman tariff has no
American equivalent and CFPB's enforcement posture contracted through 2026, so the regulatory-threat
lever is weak. It is a cost-reduction story sold to a cost centre.

**This is the fallback if the attrition demo is challenged on evidence — a fallback, not a switch.**

### 3rd reserve — #7, collections promise reliability *(25/35)*

**The cleanest architectural fit on the entire list.** It reorders a dial list the bank already works —
**no new contact motion of any kind.** And contact capacity is *capped by regulation* at **7 attempts
per debt per 7 days (Reg F §1006.14(b)(2)(i))**, so better ordering has value **independent of
precision** — which is the one thing we have never measured, and the hole KS-9 opened in the money
chain. **Fastest label on the list: the promise date.** A back-test settles in a month.

**Why not higher:** no published value anchor (BLS May 2025 median collector wage **$47,030** is a cost
anchor, not a value one), it is the story most likely to already exist in some form, and it is **the
weakest demo of the top group** — a promise is a per-episode judgement, so accumulation has less to
bite on.

### Kept in the folder, but not as options

**#2 pre-delinquency** — the best anchors on the list, killed on T3, and settled. **#8 mortgage** — the
only legally-mandated consuming process, which makes it the right answer to *"does this only work for
cards?"*, but it is not a pitch.

## 4. The profiles

Short. What it predicts · where the money is · the T3 answer · the honest weakness.

### 1. Card attrition *(the current story)*
**Predicts** voluntary closure. **Money:** margin + avoided re-acquisition, ~$550–800 per save; CAC
derivable at **$500** (Amex) and **$532** (JPM) from FY2025 filings. **T3:** case briefs the next
inbound agent. **Weakness:** the addressable population is **0.6% of the book**, the voluntary/
involuntary split is published nowhere, and the scored population skews toward complainers rather than
quiet leavers. Fully worked in `01-THE-STORY.md`.

### 2. Pre-delinquency / early hardship ★
**Predicts** first missed payment and 30/60/90-day roll. **Money — corrected 2026-09-09:** avoided
charge-off, honestly **~$3,400 (range $2,300-$5,000)**, not $5,000; the old figure applied a 75%
loss-given-charge-off to **$6,610, which is per borrower, not per account**, and the balance *at
charge-off* is published nowhere. Charge-offs running **3.82%** (CORCCACBS, updated 2026-08-25 — not
G.19, which publishes none) and 90+ delinquency at **12.92% of balances** (Q2 2026). **T3:** hardship-programme eligibility and the pre-collections queue,
both already staffed. **Reuse:** `financial_distress` already built. **Weakness:** heavier supervisory
scrutiny; and the honest question of whether a spoken *"things are tight"* beats a payment-ratio trend
the bank already watches — our best answer is the intent/state distinction (§ `03-REFERENCE.md` row 7).

### 3. Balance attrition, not account attrition
**Predicts** balance transfer out or paydown-to-zero — the customer keeps the card and takes the
balance. **Money — halved on its own source, 2026-09-09:** direct NII loss, but at the **effective**
yield, not the headline APR. CFPB 2025 reports **$160bn of interest on >$1.2tn** of balances =
**13.3%**, so a $5,300 balance is **~$705/yr**, not the ~$1,464 this profile used to claim from
22.15% on $6,610 (which was also a per-borrower balance). **T3:** retention-pricing eligibility. **Weakness:** a balance transfer out
is *visible* structurally the moment it happens, so the window is narrow — and the customers who move
balances are rate-shoppers you may not want.

### 4. Deposit flight — **CUT 2026-09-09**
**Predicts** deposit outflow and rate-shopping. **Money — the claim collapsed when it was finally
anchored.** This profile said "highest per-relationship value on this list". Measured: Fed SCF-2022
median transaction balance **$8,000** × FDIC QBP Q4-2025 net interest margin **3.39%** = **~$271/yr**.
Not "$1,000s-10,000s". **And T2 kills it independently: a deposit leaving is the loudest structural
signal in retail banking** — we would be predicting from conversation a balance move the bank can
already see on the screen. **T1 is also weakest here** (deposit customers contact the bank far less
than card customers) and the whole build is card/servicing flavoured. **Cut. Do not revive without a
per-relationship anchor that survives arithmetic.**

### 5. Scam and elder financial exploitation ★ dark horse
**Predicts** that the customer is being defrauded now. **Money:** avoided loss, Reg E dispute cost,
reputational and supervisory exposure. **T3:** a hold/verify flag into the fraud queue — the strongest
T3 answer on the list, because the consuming process is *already* an alert queue. **Weakness:** anchors
unverified; and false positives here are expensive in customer trust, so precision matters more than
anywhere else.

### 6. Complaint escalation avoidance
**Predicts** a complaint becoming formal or regulator-facing. **Money:** remediation and handling cost.
**T3:** case-owner escalation inside the existing complaints workflow. **Reuse: highest on the list —
already built and already measured** (0/20 → 20/20 on the generic corpus). **Weakness:** this was the
pre-reframe story and it **lost its best number in the move to the US** — there is no US equivalent of
a per-case Ombudsman tariff, and CFPB enforcement posture contracted through 2026.

### 7. Collections promise reliability
**Predicts** whether a promise-to-pay will hold. **Money:** collector time is the most measurable
capacity constraint in banking, and roll-rate improvement is directly attributable. **T3: the best on
the list — it reorders calls the bank already makes**, so there is no new contact motion at all.
**Weakness:** narrow, unglamorous, and it reads as an optimisation rather than a new capability. Also
the most likely to already exist in some form.

### 8. Mortgage loss-mitigation intake
**Predicts** borrower hardship and loss-mit eligibility. **Money:** foreclosure avoidance is the
largest per-event number in retail banking. **T3: the only story with a legally mandated conversation —
Reg X early-intervention requires the servicer to establish live contact with a delinquent borrower.**
We prioritise and brief a call they are *required* to make. That repairs the exact gap the US switch
opened. **Weakness:** default servicing is the most heavily regulated corner of the bank, sales cycles
are long, and none of our build is mortgage-flavoured.

### 9. Cross-sell from stated life intent
**Predicts** imminent need — a house, a car, a business. **Money:** biggest revenue upside on the list.
**T3:** next-best-product flag into an existing campaign engine. **Weakness: the worst optics of any
story here.** *"We listen to your service calls to sell you things"* is the headline a journalist
writes, and it puts every governance advantage we have on the wrong side of the argument. **I would not
pick this** in a year when AI-and-consumers is a live political topic.

### 10. Credit-line increase / prosperity signals — **CUT 2026-09-09**
**Predicts** capacity and appetite for more credit. **Money: no published anchor found** in two
searches. **T2 is the worst on the list** — utilisation and bureau data *are* the CLI decision inputs,
so conversation adds least here of anywhere. And it is **the on-ramp to #11**, which this document
says never to raise. **Cut.**

### 11. Credit-line decrease / exposure management
**Predicts** deterioration before the bureau shows it. **Money:** real — exposure reduction ahead of a
charge-off. **Weakness: the regulatory weight is disqualifying for a first pitch.** A line decrease is
an **adverse action** requiring notice under Reg B, and if it rests on a consumer report, FCRA attaches.
Using conversation content to cut someone's credit line is the single most attackable thing on this
list. **Do not lead with it. Do not even raise it as roadmap.**

### 12. Small-business relationship risk
**Predicts** SMB attrition or distress. **Money:** high per relationship. **T3:** RM briefing.
**Weakness:** SMB conversation volume is lower and more relationship-mediated; harder to demo; and the
value is diffuse across products.

### 13. Agent coaching / QA at 100% coverage — **CUT 2026-09-09**
**Predicts** which calls need coaching. **It scores 24/35 and the score is an artefact**: adding a
ledger-dependence column showed it is the **only story on the list that does not use the ledger at
all**, so its total is not comparable to the others. **Weakness: this is what Verint, NICE and
CallMiner already sell, and they sell it well.** We would be entering their category with their feature. It also throws
away our one real differentiator — the *per-customer ledger across time* — because coaching is a
per-call judgement. **Do not pick this.**

---

## 5. What changes if you pick something other than attrition

Reassuringly little. The build is domain-independent; the *content* is not.

| | Unchanged | Has to be re-authored |
|---|---|---|
| **Engine** | Accumulation, decay, corroboration, retro re-scoring, thresholds, the deployed pipeline, HITL-by-absence, 908 tests | — |
| **Signals** | The eight-family *structure* and the four tests | The families themselves, the cues, the US phrasings |
| **Corpus** | Ground-truth-before-text discipline, the answer-key guards | The fragment pools and the planted arcs |
| **Prompts** | Verbatim-quote rule, confidence rubric, refusal rules | The operational definitions |
| **Desks** | The routing mechanism | `TRAJECTORY_TEAM` — **and mind the landmines in `03-REFERENCE.md` §5** |
| **Money** | The chain structure, the tagging discipline, the two refusals | Every anchor |

**Cost to re-point at a new story: the same ~$0.45 and a few hours of fragment authoring.** The
expensive thing is not the code — it is choosing, which is why this file exists.

---

## 6. What I would do with your next hour when you wake up

1. **Read §3.** If pre-delinquency persuades you, say so and I will rebuild `01-THE-STORY.md` around it
   with attrition as beat B — that is a two-hour job, not a restart, and the demo arc barely changes.
2. **If you want the dark horse**, say so and the first thing needed is a verified loss anchor for scam
   and elder exploitation. One tight search, haiku, not a research programme.
3. **If you want to stay with attrition**, nothing changes and everything is ready.

**What I would not do:** pick #9, #11 or #13. Cross-sell has optics that undo our governance argument,
credit-line decrease is the most attackable idea on the list, and agent coaching is a fight with
incumbents on their own ground using our weakest asset.

## Honest gaps in this document

- **Ratings in Table B are my judgement, not measurements.** They are calibrated against the red-team
  findings, but two people could reasonably reorder the middle of the table.
- **Anchors are verified only for stories 1, 2, 3 and 6** (cards, delinquency, balances, complaints).
  For deposits, scams, mortgage, SMB, CLI and CLD I have named where the money is but **not verified a
  single figure.** Do not quote a number for those six without a search.
- **The 7–10× claim in the headline** comes from comparing ~$550–800 per retained customer against
  ~$5,000 per avoided charge-off on the published $6,610 average balance. The **$5,000** is my estimate
  of net loss after recoveries; I have **not** verified a published recovery or severity rate, so treat
  the multiple as an order of magnitude, not a figure.
- **T1 (does the conversation exist, in volume) is unverified for every story.** No published US figure
  for issuer contact rates was found in any pass. It is a client input everywhere.
