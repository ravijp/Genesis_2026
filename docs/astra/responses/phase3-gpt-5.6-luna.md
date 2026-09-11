Do **not** pitch the current card-attrition product. Repoint it to **Scam Sentinel**, an authorized-payment scam evidence layer for a bank’s existing payments-fraud queue. It reads transcripts and authenticated chats, keeps customer-level evidence across time, and when a pending wire, ACH or instant payment arrives, re-scores the history and gives the fraud analyst a cited case before release. The buyer is the **Head of Payments Fraud or Chief Fraud Officer**, with BSA/AML and customer-protection as control partners; the budget is fraud operations and loss prevention. The bank does not buy a conversation platform. It buys more useful decisions from the payment queue it already staffs.

The current attrition story should become a retired fixture and an appendix, not the stage product.

## 1. The product

### What it is

**Scam Sentinel: conversation evidence for payment-fraud decisions.**

It connects:

```text
Contact-centre transcripts
Authenticated chat
CRM identity
        │
        ▼
Customer evidence ledger
        │
        ├── persistent signals, quotes, timestamps
        ├── decay and corroboration
        └── retroactive re-scoring
        │
Pending payment / fraud alert
        │
        ▼
Existing fraud case-management queue
```

It detects evidence such as:

- a third party coaching the customer;
- secrecy or isolation;
- unusual urgency;
- impersonation;
- a “secure account” or “safe account” story;
- uncertainty about the payment;
- pressure to use a particular beneficiary or rail;
- a customer being told not to speak to the bank.

It does not automatically decline a payment, freeze an account or call the customer. It enriches the existing human review process.

The sentence for the room is:

> **Before an authorized scam payment leaves the bank, we show the fraud analyst the customer’s own earlier words that the transaction screen cannot see.**

### Why this replaces attrition

Attrition fails on three fronts:

1. **Weak evidence:** the only real card-specific churn result is 1/8; the headline memory ranking is eighth of nine arms overall.
2. **Weak consuming process:** when the customer is not calling, nothing happens unless the bank separately creates an outbound motion.
3. **Weak economics:** the $1.65 million is a ceiling built from unmeasured precision, save rate and client assumptions.

Scam Sentinel has a stronger operational trigger. A pending payment already creates a time-sensitive human decision. The product does not need to invent an action.

Complaint escalation is the strongest current evidence-supported fallback, but I would not choose it. It is closer to existing complaint analytics, has no hard US per-case value anchor, and does not exploit the most distinctive capability as clearly as a payment event re-evaluating prior evidence.

### What happens to the existing work

Most of the technical foundation survives. The following changes:

- `churn_intent`, rewards and annual-fee taxonomy become scam/coaching/urgency/impersonation taxonomy;
- `TRAJECTORY_TEAM` becomes fraud-review routing;
- the cardholder demo becomes a payment-event demo;
- the retention value chain is deleted;
- generic churn results become engineering appendix evidence, not product evidence;
- the existing agent becomes a bounded case investigator, not a fraud adjudicator.

This is not a new system. It is a new product built on the right parts of the system.

## 2. How the value becomes obvious

Do not lead with the FBI’s $7.7 billion. That is market urgency and customer harm, not bank ROI.

Do not lead with “the average victim loses $38,000.” That is not necessarily the bank’s money.

The value argument is simpler:

> **The bank already pays analysts to review a fixed number of payment alerts. At the same review capacity, does conversation evidence cause them to catch more confirmed scams before release?**

That produces a finance-grade value equation:

```text
Incremental confirmed scams caught before release
× bank loss/reimbursement exposure per case
+ analyst hours saved
− product and operating cost
= client value
```

The client already owns the relevant fields:

- payment amount;
- bank reimbursement or loss amount;
- whether the payment was released;
- whether the case was confirmed scam;
- analyst handling time;
- existing transaction-model score.

The demo should show **incremental cases at a fixed alert budget**, not a market-size extrapolation.

For example, the portfolio screen should eventually say:

```text
Same analyst capacity: 200 reviews

                         Confirmed scams caught    Median exposure
Transaction model only              [measured]          [measured]
Transaction + conversation          [measured]          [measured]

Incremental cases: [measured]
Incremental bank exposure identified before release: [measured]
```

Those numbers must come from a frozen synthetic replay, not from an invented scenario. Until that run exists, show blanks or label the numbers as synthetic. Do not manufacture confidence for the sake of a prettier slide.

The commercial ask is:

> **An eight-week, one-payment-rail retrospective and shadow-mode pilot. We compare the bank’s existing fraud champion with the champion plus conversation evidence at the same alert budget. If the challenger does not improve pre-release scam capture, we stop.**

A plausible initial price is a **$150,000–$250,000 fixed-fee pilot**, followed by an annual license based on payment volume and case throughput. That is a pricing hypothesis, not a claim about an established market rate.

## 3. The seven-minute demo

The demo needs a new synthetic benchmark and one new screen. It is worth building.

### Synthetic story

Customer: **Maya Chen**, a retail-banking customer. Do not make age the explanatory variable. The evidence is about the situation, not a demographic label.

#### Day 0 — chat

> “Daniel says the investment account is safer than leaving the money here, but I’m still checking.”

Low-confidence evidence. No case.

#### Day 19 — phone

> “He told me the transfer has to happen today. I don’t want to cause a delay.”

Still ambiguous. No case.

#### Day 42 — payment event

- first payment to a new beneficiary;
- $18,500 wire;
- transaction model: medium risk;
- payment pending release.

The payment event wakes the ledger.

#### Day 42 — phone

> “Please don’t call him while you verify it. He said the bank will freeze the account.”

Now the system re-scores the earlier remarks and creates a cited review case.

### Screen sequence

#### 0:00–0:45 — the existing queue

Show the transaction-only view:

```text
$18,500 wire
New beneficiary
Transaction model: Medium
Current action: Standard review
```

Say:

> “This is what the bank sees today. The transaction is plausible, but the model has no view of the customer’s social situation.”

#### 0:45–1:45 — the conversation history

Show the Day 0 and Day 19 conversations with:

- exact quote;
- channel;
- timestamp;
- initial contribution;
- “below threshold — no action.”

This is important. The product did not turn every ambiguous sentence into an alert.

#### 1:45–2:30 — the payment event

Introduce the pending payment. The screen should visibly call:

```text
Payment event received → retrieve customer evidence → re-score
```

No theatrical chatbot animation. Show the actual event and the resulting ledger update.

#### 2:30–3:30 — the moment

Show the retroactive comparison:

| Evidence | Relevance when written | Relevance after payment event |
|---|---:|---:|
| “investment account is safer” | low | supporting |
| “has to happen today” | low | supporting |
| “don’t call him while you verify it” | high | high |

Then display:

> **Why this case opened now:** the pending payment corroborates previously weak coaching and urgency evidence.

This is the moment. The room should see that a payment event changes the meaning of the past.

The line is:

> **The first two conversations were not enough to stop anything. The payment event made them relevant before release.**

#### 3:30–4:45 — the analyst case file

Show the case that lands in the existing fraud workflow:

- payment facts;
- current transaction risk;
- evidence timeline;
- three exact quotes;
- conversation IDs and turn references;
- “why now” explanation;
- contradictory or mitigating evidence;
- previous analyst cases;
- recommended route: enhanced verification;
- human disposition options.

The product should say “review before release,” not “fraud confirmed.”

#### 4:45–5:30 — legitimate twin

Show a second synthetic customer with nearly identical language:

> “The adviser says I need to transfer it today.”

But the twin also says:

> “I called the number on the bank’s website and independently verified the beneficiary.”

The system should not escalate the twin at the same level.

This is essential. Without a legitimate twin, the demo is a keyword detector with a timeline.

#### 5:30–6:30 — portfolio value

Show the fixed-budget comparison:

```text
Same 200 analyst reviews
Transaction-only champion vs conversation challenger

Confirmed scams caught before release
Precision / review yield
Median lead time
Analyst handling time
```

Use measured synthetic numbers only after the benchmark is built. The key metric is:

> **Incremental confirmed authorized-payment scams caught before release at the same review capacity.**

#### 6:30–7:00 — close

Return to the case file and say:

> **Every bank already has a payment model and every bank already has transcripts. The loss sits in the gap between them. We close that gap by turning the customer’s earlier words into cited evidence for the analyst who can still act. We will prove it against the bank’s existing fraud champion at the same alert budget—or we will not ship it.**

### What not to show

Do not show:

- a generic “conversation intelligence” dashboard;
- a fraud probability generated by the LLM;
- an autonomous payment decline;
- a fake $18,500 saving;
- an elder-fraud demographic profile;
- a giant customer timeline with no decision attached;
- the current retention demo;
- the model-vs-regex table during the seven minutes;
- the agent declaring “scam” without evidence.

The reader comparison and reproducibility evidence belong in the technical appendix and Q&A.

## 4. What to keep

### Must survive

#### 1. The signal ledger and retroactive re-scoring

This is the core asset. The four persisted values—contribution at write, score at write, contribution now and score now—make the temporal mechanism inspectable.

Do not reduce it to a normal latest-state customer profile.

#### 2. Exact evidence references

Keep:

- conversation ID;
- turn index;
- timestamp;
- verbatim quote;
- boundary validation;
- human-readable case citation.

This is the difference between an auditable evidence product and an opaque LLM alert.

#### 3. Deterministic scoring outside the model

Keep accumulation, decay, corroboration, cross-channel logic and thresholds in tested code. The LLM should extract and classify evidence; it should not own the score.

But fix the raw confidence issue. Bucket it or remove it now. Do not carry an uncalibrated self-reported float into a fraud workflow.

#### 4. Event-triggered investigation

The current system re-scores as new conversation evidence arrives. Scam Sentinel needs the reverse trigger too:

> **A payment event must wake up and re-score old conversation evidence.**

That is the new load-bearing feature.

#### 5. Bounded human-in-the-loop agent

Keep the investigator agent for:

- retrieving payment details;
- gathering prior conversations;
- checking existing cases;
- identifying contradictory evidence;
- assembling the case.

Do not use the current 29/50 verdict result as evidence of production readiness. The agent should not make the final fraud decision.

#### 6. Failure isolation, reproducibility and deployment controls

Keep:

- committed response cache;
- model/prompt fingerprinting;
- malformed-record isolation;
- alarm history;
- cost and latency measurement;
- local/deployed agreement tests;
- model-swap evaluation.

Before making production claims, fix the known fingerprint gaps:

- include sampling parameters in cache keys;
- include reader code in the pipeline fingerprint;
- persist model ID on each extracted signal;
- write deployed run manifests;
- add deletion and retention semantics.

#### 7. No autonomous outbound action

Keep the absence of a contact route. It is a strong safety boundary. But do not describe it as sufficient governance. The bank still needs controls on how downstream systems consume the exported feature.

### Stop carrying these as product assets

- the card-attrition value chain;
- the $1.65 million central case;
- the 58-day “result”;
- the card-retention demo;
- “the model is the product”;
- the generic retention coverage table;
- the 1/20 to 16/20 retention desk result as commercial evidence;
- the claim that model migration is only re-baselining;
- the current append-only ledger as production-ready.

Keep the attrition code and fixtures in the repository as regression tests if useful. Do not let sunk engineering determine the product.

## 5. The three questions that decide it

### Question 1: “Does this actually find anything our payment model cannot?”

Answer:

> **That is the primary test. We are not asking you to trust standalone LLM accuracy. We will compare your existing transaction champion with the same champion plus conversation evidence, at the same alert budget. The primary metric is additional confirmed scams caught before release. If the number is zero, the product has no value.**

On screen, show the transaction-only versus conversation-enriched case and the legitimate twin. A language model finding more phrases than regex is not the answer.

### Question 2: “What happens operationally, and who is accountable?”

Answer:

> **Nothing is automatically blocked. A pending payment event enriches the fraud case already owned by Payments Fraud Operations. The analyst decides whether to release, hold or route it under your existing policy. We write evidence and disposition back to the existing case system. The product adds evidence to a decision; it does not create a new autonomous decision-maker.**

The buyer is Payments Fraud. BSA/AML, Legal, Privacy and Model Risk are control partners, not a committee that owns the product.

### Question 3: “What am I paying for, and how do I know it is worth it?”

Answer:

> **You are buying a fixed-capacity challenger to an existing fraud queue, not a general AI platform. We will run one payment rail for eight weeks, use your historical payment outcomes, and measure incremental pre-release scam capture, bank exposure and analyst time. We agree the threshold before seeing the data. If the challenger does not improve the existing queue, we walk away.**

That is more credible than quoting a market-wide loss number or pretending synthetic dollars are a client ROI forecast.

## 6. What would make it undeniable

The current evidence does not support Scam Sentinel yet. The recommendation is based on a stronger product shape, not on a completed fraud evaluation. That evaluation must be built.

### Internal build: three weeks

Assume two engineers and one fraud-operations subject-matter expert.

#### Days 1–3: define the event and outcome

Specify:

- one rail first: wires or ACH;
- payment-event timestamp;
- “caught before release” outcome;
- confirmed scam label;
- legitimate payment label;
- transaction-only champion;
- fixed analyst review capacity;
- analyst handling-time measure.

Do not begin with “elder fraud.” Begin with authorized-payment scam behavior applicable across customers.

#### Days 4–8: build the synthetic benchmark

Create:

- at least 10,000 synthetic payment events;
- 1,000–2,000 customer conversation histories;
- 100–150 scam trajectories;
- legitimate near-matches;
- coaching, urgency, impersonation, secrecy and uncertainty language;
- negations and quoted third-party speech;
- multiple channels;
- temporal train/test split;
- outcomes authored before the model reads the text.

The critical design is the legitimate twin, not the number of conversations.

#### Days 9–12: wire the event trigger and case screen

Build:

- pending-payment event ingestion;
- retrieval of customer evidence;
- event-conditioned re-scoring;
- “why now” explanation;
- analyst case view;
- existing-workflow routing mock;
- disposition write-back.

#### Days 13–16: evaluate against a real baseline

Run:

- transaction-only champion;
- transaction plus simple rules;
- transaction plus conversation evidence;
- same alert budget;
- precision and incremental recall;
- lead time;
- analyst handling time;
- quote fidelity;
- subgroup and language checks.

Do not compare only against regex. Include a competent non-LLM baseline.

#### Days 17–21: harden the presentation and controls

Add:

- confidence bucketing;
- model/prompt fingerprints;
- deletion/retention design;
- failure injection;
- replay reproducibility;
- fixed-budget portfolio screen;
- explicit synthetic-data labels;
- a written go/no-go protocol.

### The internal kill criterion

Set this before viewing results:

> **At the same analyst alert budget, the conversation challenger must produce at least a 20% relative increase in confirmed scam payments identified before release, without an unacceptable increase in false positives or analyst handling time. Otherwise, kill the product rather than reverting to attrition.**

The 20% is an internal bar, not a universal industry standard. The point is to establish a bar that is meaningful enough to justify integration.

### Client proof: eight weeks after a buyer agrees

The competition demo cannot prove bank ROI. Only a client’s historical outcomes can do that.

The paid pilot should:

1. Replay one payment rail over 12–24 months.
2. Use the bank’s existing fraud champion as baseline.
3. Hold alert capacity constant.
4. Keep the bank’s actual outcome and exposure fields.
5. Run in shadow mode before affecting decisions.
6. Measure incremental confirmed scams caught before release, exposure and analyst time.
7. Include a walk-away.

The product becomes fundable when it can say:

> “On your data, at the same queue capacity, this identified more confirmed scam payments before release than your current champion, and here is the bank exposure associated with those incremental cases.”

Until then, it is an interesting and technically credible proposition—not a proven loss-reduction product.

The current team’s strongest work is the temporal evidence engine and the discipline around provenance. The wrong move is to spend more time polishing the attrition story. Build the payment-event trigger, the legitimate twin, and the fixed-budget outcome benchmark. Then pitch the product whose operational value can actually be tested.