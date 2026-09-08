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

## 2. The comparison

### Table A — what each story *is*

| # | Story | What the score predicts | Buyer | What consumes it when the customer isn't calling (T3) |
|---|---|---|---|---|
| **1** | **Card attrition** *(current)* | Voluntary closure / balance run-off | Head of Retention Analytics | Case briefs the next inbound agent · feeds existing churn propensity model |
| **2** | **Pre-delinquency / early hardship** | First missed payment, 30/60/90-day roll | Head of Collections Strategy or Credit Risk | **Hardship-program eligibility flag** · feeds existing roll-rate and loss-forecast models · pre-collections queue |
| **3** | **Balance attrition (not account attrition)** | Balance transfer out / paydown-to-zero | Cards P&L owner, NII owner | Retention-pricing eligibility · feeds balance-forecast model |
| **4** | **Deposit flight** | Deposit outflow, rate-shopping, relationship exit | Treasury / Deposit Strategy | Rate-exception eligibility · feeds deposit-beta and liquidity models |
| **5** | **Scam and elder financial exploitation** | Customer is being defrauded *right now* or shortly | BSA/AML, Fraud Ops, Vulnerable Customer lead | **Hold/verify flag on the account** · alerts existing fraud queue |
| **6** | **Complaint escalation avoidance** | Complaint becomes formal, regulator-facing, or litigated | Head of Complaints / Regulatory Affairs | Case-owner escalation in the existing complaints workflow |
| **7** | **Collections promise reliability** | Whether a promise-to-pay will actually be kept | Collections Ops | Re-prioritises the existing dial/queue list. **No new contact — reorders contact they already make** |
| **8** | **Mortgage loss-mitigation intake** | Borrower hardship, loss-mit eligibility | Default Servicing | **Reg X early-intervention contact is legally required** — we prioritise and brief a call they must make anyway |
| **9** | **Cross-sell from stated life intent** | Imminent need: home, auto, business, education | Consumer Lending / Marketing | Next-best-product flag into existing campaign engine |
| **10** | **Credit-line increase (prosperity)** | Capacity and appetite for more credit | Cards Growth / Portfolio | CLI campaign eligibility |
| **11** | **Credit-line decrease / exposure management** | Deterioration before the bureau shows it | Credit Risk | Line-management review queue |
| **12** | **Small-business relationship risk** | SMB attrition or distress | Business Banking | RM briefing · relationship review queue |
| **13** | **Agent coaching / QA at 100% coverage** | Which calls need coaching | Contact Centre Ops | Coaching queue |

### Table B — how each story *scores*

Ratings are my judgement, 1–5, high is good. **$/event is order of magnitude, not a quote.**

| # | Story | $ per event | Anchor quality (T4) | T3 answer | Reg weight *(low=good)* | Reuse of what's built | Demo-able | **Total** |
|---|---|---|---|---|---|---|---|---|
| **2** | **Pre-delinquency / hardship** | **~$5,000+** | **5** — Fed charge-off 3.70%, NY Fed delinquency, all primary | **5** | 3 | **5** — `financial_distress` already built | **5** | **★ 28** |
| **5** | **Scam / elder exploitation** | ~$1,000s | 4 | **5** | 3 | 3 | **5** | **★ 25** |
| **7** | **Collections promise reliability** | ~$100s–1,000s | 3 | **5** — reorders calls they already make | 4 | 4 | 4 | **★ 25** |
| **1** | **Card attrition** *(current)* | ~$550–800 | 4 — CFPB closure rate, Amex/JPM CAC | 4 | **5** | **5** | **5** | 24 |
| **8** | **Mortgage loss-mit intake** | ~$1,000s–10,000s | 4 | **5** — Reg X *mandates* the call | 2 | 3 | 4 | 24 |
| **3** | **Balance attrition** | ~$1,000+ | 4 | 4 | **5** | 4 | 4 | 23 |
| **6** | **Complaint escalation** | ~$100s–1,000s | 3 (US has no per-case tariff) | 4 | 4 | **5** — already built and measured | 4 | 22 |
| **4** | **Deposit flight** | **~$1,000s–10,000s** | 3 — anchors not yet verified | 3 | 4 | 2 | 3 | 20 |
| **12** | **SMB relationship risk** | ~$1,000s | 2 | 3 | 4 | 3 | 3 | 18 |
| **10** | **Credit-line increase** | ~$100s | 3 | 3 | 3 | 3 | 3 | 18 |
| **9** | **Cross-sell from life intent** | ~$100s–1,000s | 2 | 3 | 2 — **worst optics** | 3 | 4 | 16 |
| **11** | **Credit-line decrease** | ~$1,000s | 3 | 3 | **1** — adverse action, ECOA/Reg B, FCRA | 3 | 3 | 15 |
| **13** | **Agent coaching / QA** | ~$10s | 2 | 4 | 5 | 2 | 3 | **14 — do not pick** |

---

## 3. My recommendation

### ~~Lead with #2, pre-delinquency and early hardship.~~ **WITHDRAWN 2026-09-09 — see the banner at the top of this file. The five reasons below are preserved with their faults marked.**

**Five reasons, in order of how much they matter to these two judges.**

1. ~~**The money is 7–10× bigger per event.**~~ **Corrected to 3–9×, centrally about 5×, and below 1×
   once precision is priced in.** The $5,000 applied a 75% loss-given-charge-off to **$6,610, which is
   a per-borrower balance standing in for a per-account one** — this book's own figures give $2,077
   per open account. Balance at charge-off is published nowhere. Honest net loss **~$3,400**. See the
   banner.
2. **The anchors are all primary and all current.** Card net charge-offs **3.70%**, 30+ delinquency
   **2.85%**, share of balances 90+ days delinquent **12.92%** (Fed and NY Fed, Q2 2026), against
   **608 million open general-purpose accounts** and **$1.263 trillion** outstanding (CFPB, published
   2025-12-30; Fed G.19). **Nothing needs inventing** — and unlike attrition, the *loss* side is
   disclosed by every issuer every quarter.
3. ~~**T3 answers itself.**~~ **THIS IS BACKWARDS — the single biggest error in this file.** Hardship
   programmes and forbearance are **opt-in**: the customer has to apply, or you have to reach out and
   invite them. **You cannot enrol a silent customer without contacting them**, which is precisely the
   thing this system is architecturally incapable of doing. So pre-delinquency's T3 answer is **worse
   than attrition's**, not better — attrition's next-inbound-contact treatment works because the
   customer eventually calls about something, whereas a hardship enrolment that waits for an inbound
   call has usually waited past the missed payment. *(The pre-collections queue half survives: you can
   reorder a dial list they already dial. But that is story #7, not story #2.)*
4. **The label arrives in 90 days, not a year.** Delinquency roll is observable in one quarter.
   Attrition takes a year of observation to label properly. **That halves the back-test and makes the
   six-week pre-registered experiment far more credible** — you can genuinely settle it fast.
5. **We have already built the signal family.** `financial_distress` exists, is measured, and has the
   longest half-life in the config. The card-flavouring work is the same ~$0.45 job either way.
   **But measured on what:** the CFPB benchmark's card evidence for distress is **2 / 2 documents**,
   because **none of its 17 distress-enriched narratives is a credit-card complaint**. There is no
   card-specific distress evidence at all — which is worse than attrition's position, not better.

**The one thing that gets harder:** collections and hardship sit under closer supervisory scrutiny than
retention marketing, and the "don't turn distress into a sales trigger" rule becomes *the whole
product* rather than a guardrail. That is manageable — and honestly, it makes the ethical beat stronger,
not weaker. *"We find people in trouble earlier and route them to help, and the system is
architecturally incapable of contacting them"* is a better sentence than anything in the attrition
story.

### The strongest pairing for 18 minutes

> **One layer. Two desks. The same three conversations.**
>
> **Beat A — pre-delinquency.** The customer says money is tight. Nothing crosses. Two months later
> another remark corroborates it, and we open a hardship case **before a payment is missed** — which
> is where the $5,000 lives.
>
> **Beat B — attrition.** *The same customer, the same ledger, a different reader.* Now the signals
> are about the annual fee and a failed redemption, and the case goes to retention instead.
>
> **That is the layer argument made concrete instead of asserted** — and it happens to be what the
> committee brief said the entry was in the first place.

That also repairs the sharpest tension in the current pitch: the submitted brief says *"none of these
is the headline; the layer is"*, and leading with one score negates it. **Two desks off one ledger
honours the brief and still gives a CEO a single number to hold.**

### If you want one dark-horse instead

**#5, scam and elder financial exploitation.** Lower dollar value than pre-delinquency, but it is the
**best story in the room** — a customer being coached by a fraudster says things on a call that no
structured system can see, the harm is vivid, and "we cannot contact anyone, we can only tell your
fraud team sooner" is an unimpeachable safety position. If the judges' scoring weights presentation
and originality more than you expect, this is the one that gets remembered. **Weakest on T4** — I have
not verified the loss anchors, and that is a search away, not an assumption to make.

---

## 4. The profiles

Short. What it predicts · where the money is · the T3 answer · the honest weakness.

### 1. Card attrition *(the current story)*
**Predicts** voluntary closure. **Money:** margin + avoided re-acquisition, ~$550–800 per save; CAC
derivable at **$500** (Amex) and **$532** (JPM) from FY2025 filings. **T3:** case briefs the next
inbound agent. **Weakness:** the addressable population is **0.6% of the book**, the voluntary/
involuntary split is published nowhere, and the scored population skews toward complainers rather than
quiet leavers. Fully worked in `01-THE-STORY.md`.

### 2. Pre-delinquency / early hardship ★
**Predicts** first missed payment and 30/60/90-day roll. **Money:** avoided charge-off, order of
**$5,000** per event on a $6,610 average balance; charge-offs running **3.70%** and 90+ delinquency at
**12.92% of balances** (Q2 2026). **T3:** hardship-programme eligibility and the pre-collections queue,
both already staffed. **Reuse:** `financial_distress` already built. **Weakness:** heavier supervisory
scrutiny; and the honest question of whether a spoken *"things are tight"* beats a payment-ratio trend
the bank already watches — our best answer is the intent/state distinction (§ `03-REFERENCE.md` row 7).

### 3. Balance attrition, not account attrition
**Predicts** balance transfer out or paydown-to-zero — the customer keeps the card and takes the
balance. **Money:** direct NII loss; at 22.15% APR on a $6,610 balance that is ~$1,464/yr of gross
interest per balance lost. **T3:** retention-pricing eligibility. **Weakness:** a balance transfer out
is *visible* structurally the moment it happens, so the window is narrow — and the customers who move
balances are rate-shoppers you may not want.

### 4. Deposit flight
**Predicts** deposit outflow and rate-shopping. **Money:** highest per-relationship value on this list —
a single deposit relationship dwarfs a card. Board-level topical since 2023. **T3:** rate-exception
eligibility and existing deposit-retention campaigns. **Weakness:** deposit customers talk to the bank
far less often than card customers, so T1 is genuinely weaker; our whole build is card/servicing
flavoured; **and I have verified no anchors here.**

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

### 10. Credit-line increase / prosperity signals
**Predicts** capacity and appetite for more credit. **Money:** incremental balances and interchange.
**T3:** CLI campaign eligibility. **Weakness:** low value per event, and it drifts toward credit
decisioning where Reg B and FCRA attach.

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

### 13. Agent coaching / QA at 100% coverage
**Predicts** which calls need coaching. **Weakness: this is what Verint, NICE and CallMiner already
sell, and they sell it well.** We would be entering their category with their feature. It also throws
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
