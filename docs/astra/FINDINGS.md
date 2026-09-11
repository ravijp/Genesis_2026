# What the outside read said — 2026-09-11

**Total spend: $0.00.** `gpt-6-astra` was never reachable (see `README.md` §access). Everything below
came from free-tier models, which weakens the *authority* of the result and not its *content* — read it
as an argument to check, not a verdict to obey.

| Run | Model | State |
|---|---|---|
| Phase 1 · 2 · 3 | `deepseek-v4.1-flash` (DeepSeek) | done — the full trajectory |
| Phase 1 · 2 | `gpt-5.6-luna` (OpenAI) | done — the replication check |
| Phase 1 | `qwen3.8-27b` (Alibaba) | done — and it went somewhere neither other model did |

---

## The one-line result

**All three models threw card attrition away, unprompted.** None was told what we had chosen, none was
given the option rankings, none was asked to evaluate the choice. They were asked what the product
should be, and none of them said this one.

**They did not agree on where to go instead**, and the disagreement is more useful than agreement would
have been:

| Model | Reframe | Needs a rebuild? |
|---|---|---|
| `deepseek` | Elder financial exploitation / APP fraud — a compliance-grade ledger feeding the BSA queue | **Yes** — new signal family, new corpus, new arcs |
| `luna` | Authorized-payment scam, triggered by a pending payment event | **Yes** — plus real-time payment integration |
| `qwen` | **Stop predicting anything.** Serve the memory: a pre-call agent brief, and a marketing suppression flag | **No** — reuses the existing demo |

### How much weight the fraud convergence carries — honestly

**Less than it first looks.** Direction #5 has the longest profile in `brief.md`, because it had the
most verified anchors (IC3, FinCEN's FIN-2022-A002, the Reg E carve-out). Both models leaned on exactly
those. So the honest claim is *"the best-evidenced option in the brief is not the one we are pitching"*
— not *"two models independently invented the same idea."* Qwen, which ignored the anchors entirely and
reasoned from the measurements instead, went somewhere else.

---

## The answer that deserves the most attention

`qwen3.8-27b` did something neither other model did: **it read our losing numbers as evidence about
what the system actually is.**

> *"The system is a faithful, thorough, quote-backed **reader and rememberer**. It is not a good
> **forecaster**."*

It cites 8th of 9 whole-portfolio, `dumb-ledger` beating the full ledger, and churn intent 1/8 — and
concludes the problem is not the direction but **the decision to predict at all**. A score goes into
someone else's model and becomes a feature with a weight of 0.003. So instead:

- **The agent brief** — before the call connects, four items with their verbatim quotes, a flag line,
  a trajectory note. The agent reads it in ten seconds.
- **The suppression flag** — written to the CRM's suppression object. *"DO NOT INITIATE MARKETING
  CONTACT. Reason: customer stated job loss and payment difficulty, 8/14, quote on file."*

**Why this is worth taking seriously for today specifically:**

1. **It needs no back-test, no control group, no 90-day wait, and no precision number.** The value is
   immediate and observable — the next call goes differently and the next email does not go out. Every
   evidence problem in `FINDINGS` above simply stops applying.
2. **It reuses the demo we already have.** Same cardholder, same `$95` fee, same day 0 / 74 / 132 arc.
   What changes is what the demo *claims*. This is the only one of the three that is actionable in
   hours rather than weeks.
3. **It turns our safety property into the product.** No outbound surface stops being a limitation to
   explain away and becomes the thing being sold: the flag exists to stop the bank's *own* systems
   contacting a distressed customer. The UDAAP argument becomes the compliance sale.
4. **It keeps the submitted brief's buyer** — VP/SVP Contact Centre Operations with the CCO as
   co-signer — which is the one the committee contract actually names, and which both other models
   discarded.

**Its demo opens by showing what the bank has today:** the CRM record, and one line of history —
*"7/14, phone, billing inquiry, resolved."* Then: *"That is the bank's entire memory of this
customer."* The moment is the agent panel appearing, with the day-0 remark's contribution visibly
grown from 0.12 to 0.47. *"The system changed its mind about the past. It did not predict the future.
It remembered."*

**And one instruction worth reading twice:** *do not say "agentic."* The track is called client-facing
agentic AI and the judges will expect the word — qwen argues that using it makes a COO hear "chatbot",
and that the product is a memory, not an agent.

---

## The finding that earned the exercise

Phase 2 is where `deepseek` — having committed in phase 1 without seeing a word of ours — read our
working documents and diagnosed the pattern:

> **"The measurement gets the skepticism; the strategy gets the confidence."**

It read our own verbs back at us. Around numbers: *corrected · withdrawn · cut · superseded ·
resequenced*. Around strategic choices: *settled · decided · my recommendation*. Then:

> *"They are scrupulously honest about holes in numbers they can buy their way out of, and evasive
> about holes in the strategic choices they have settled on."*

It credits the rigour as real — the pre-delinquency withdrawal, the `$6,610` per-borrower catch, the
SR 11-7 → SR 26-2 correction, publishing the `p=0.076` failure — and then says that rigour is **aimed at
the recoverable errors and not at the unrecoverable ones.**

### It replicates — and the second model puts it harder

`gpt-5.6-luna` ran the same phase 2 independently and reached the same diagnosis in different words:
*"The documents repeatedly identify evidence that should change the product decision, then preserve the
decision anyway."* It lists the pattern as five instances:

| We found | We then did |
|---|---|
| churn intent 1/8 on real card text | kept attrition as the lead |
| full ledger 8th of 9 arms overall | kept the favourable diffuse stratum as the headline |
| model reader 5-4-1, `p=1.00` | called it a power failure, kept the offline result |
| precision unmeasured | still put `$1.65M` in the pitch |
| latency does not apply to path 1 | kept latency as the headline |

Its closing line is the sharpest sentence either model produced:

> **"The team has found a way to make the case for attrition more honest without making it more true."**

Two models, no shared context, same structural finding. That is the strongest result here, and unlike
the direction convergence it **cannot** be explained by what the brief emphasised — the brief contains
no self-criticism at all, because that was the whole point of writing it that way.

---

## Three findings that stand on their own, whatever we decide about direction

### 1. The retro property has no user

Training joins `score_at_write`. Inference and the queue use `score_now`. The next agent sees today's
score. **So the retro column is displayed and never consumed** — it is the demo's mechanism, not the
product's.

The one user it does have is **point-in-time audit**: *what did you know, and when did you know it?*
No other feature in a bank answers that. That is a compliance value proposition and it belongs to a
CCO or BSA Officer, not a retention analyst.

### 2. The demo peaks at the wrong beat

The emotional climax is currently the 58-day gap — **a number we have just told the room we authored.**
The peak should be the retro column, where a day-31 remark is worth eleven times more on day 79. We
half-make that switch already (`02-THE-DEMO.md` calls the retro column "the hardest thing to fake") and
should finish it.

### 3. The sunk cost is the demo itself

> *"Everything downstream of 'we have a strong attrition demo' has been shaped to protect the continued
> use of that demo… the doc says 'the demo is genuinely strong' as if that settled the direction
> question, when what it settles is the demo question."*

---

## The money argument worth stealing regardless

This is the single most portable thing in the whole read. No chain, no haircuts, no invented rate:

> **Reading every conversation your bank records costs about $8,000 a year. The FBI puts the average
> confirmed elder financial exploitation loss above $38,000. One catch pays for the system five times.**

Both numbers are either published or already the bank's own. Compare the current chain — five
multiplicative haircuts to `$1.65M gross` with no false-positive leg, which our own docs concede
assumes precision is 100%.

It also names an asymmetry we never articulated: **a retention false positive annoys a customer; an
elder false positive costs a specialist a minute and reaches nobody**, because there is no contact
surface. Same unmeasured precision, very different blast radius.

### But the other model says do not say it — and it is right

This is the most useful disagreement in the whole exercise, and it only exists because two models ran.

`gpt-5.6-luna` **revised its own phase-1 position** on exactly this number:

> *"The team is right that the FBI's $7.7 billion and $38,000 average loss are **not bank value**. They
> are market urgency and societal scale, not the buyer's ROI… I would not lead with 'we save $38,000
> per victim.'"*

**It is correct, and our own `brief.md` already says why:** Reg E (12 CFR §1005.2(m)) does not reach
*authorised* transfers, and a coached victim authorises their own payments. **The $38,000 is the
customer's money, not the bank's.** A CFO will get there in one question, and the whole money beat
collapses on it.

So: **the structure of the argument survives, the number does not.** What the bank actually saves is
avoided reimbursement where it bears it, analyst investigation time, conduct and litigation exposure,
and a BSA obligation it is already funding. The `$8,000` cost line is fine; the `$38,000` has to be
labelled as the customer's loss and societal scale in the same breath, or dropped.

**Neither model would have caught this alone.** One proposed it, the other killed it.

---

## Where the two models disagreed

| | `gpt-5.6-luna` | `deepseek-v4.1-flash` | `qwen3.8-27b` |
|---|---|---|---|
| Name | Scam Sentinel | Standing Record | **Afterword** |
| What it outputs | A fraud case before payment release | A case into the BSA queue | **A brief a human reads, and a flag a system enforces** |
| Trigger | **A pending payment event wakes the memory** | Nightly batch, threshold crossing | The next inbound call |
| Category | Payment-fraud decisioning (existing) | **"The stated record"** — the fourth source of truth beside transactions, balances and bureau | **"Customer memory"** |
| Metric | Incremental recall at fixed alert budget | **Warning days** — you cannot A/B a fraud intervention | Handle time, first-call resolution, escalations |
| Buyer | Head of Payments Fraud | BSA Officer | **VP Contact Centre Ops + CCO** (the submitted brief's own buyer) |

**No single answer is the best one, and the composite is better than any of them:** qwen's *reframe
away from prediction* removes every evidence problem · luna's *event trigger* is a better wake-up than
a threshold · deepseek's *warning days* is the right metric for a memory · deepseek's *"the stated
record"* is the strongest category line anyone wrote.

---

## What phase 3 recommends, and the one thing it cannot see

**Pivot to elder exploitation and pitch the pivot itself at the gate** — not quietly afterwards,
because a greenlight given for the old framing buys three weeks of reframing a product nobody approved.
It calls our reason for holding — *two days out, zero dry runs* — a decision-procedure argument
promoted to a merit argument.

**It believes there are two days. The gate is today.** That was not in the brief and it inferred the
date from our own documents. Authoring a new signal family, re-planting arcs and rebuilding the demo is
a day of work minimum, so *pivot the demo today* is not on the table.

What is on the table, given Ravi has said he can ask for more time and this is not the final round:

- **The qwen reframe is the only one that fits in hours**, because it reuses the demo that exists and
  changes what it claims. Same customer, same arc, same screens. It stops claiming prediction and
  starts claiming memory — which is the one claim every measurement in the repo actually supports.
- **Fix the demo's peak** — move the climax off the 58-day gap and onto the retro column. Wording only,
  and all three models independently said to do it.
- **Add the suppression flag as a beat.** It needs one screen, it converts our safety property from a
  caveat into a product, and it gives the CCO a reason to co-sign.
- **Say the 1/8 finding as the reason for the framing**, not as a disclosure. Deepseek's version:
  *"that is the strongest honest evidence against the direction we were pitching, and it is why we are
  not pitching it anymore."*
- **Do not say `$1.65M` as an expected value.** All three said so, in three different ways.

---

## What it says to KEEP

Worth reading in full, because a reframe that quietly discards the good parts is the real risk:

the deterministic ledger · the four retro fields · the verbatim-quote extractor with its four-word
boundary match · the deployed pipeline and every reproducibility guarantee · **the reader comparison
including its losses** — complaint escalation 60/65 and life event 50/68 are the registers grooming
actually shows up in, so those rows carry into an elder story where churn 40/77 does not · the
no-autonomous-action property, which becomes *no model-authored accusation* · the test suite · **and
the SR 26-2 section unchanged**, which it calls the strongest piece of work in the packet.

## What it says to STOP carrying

The `$1.65M` chain · the 58-day gap as the emotional peak · churn intent as the lead family · the name
"conversation attrition score" · the pre-delinquency analysis and the 13-alternates document as pitch
content, both demoted to Q&A.

---

## Eight things only the second model caught

`gpt-5.6-luna`'s phase 2 found these and `deepseek` did not. Several are more actionable than anything
about direction.

1. **The competition may not permit the CFPB data.** The rules say synthetic or anonymised only.
   *"Public does not automatically mean compliant with the competition rule."* If it does not qualify,
   **every card-specific number we have is unusable in the competition** — and that is a
   submission-control issue, not an evidence footnote. Nobody has checked this.
2. **We never tested against a competent non-LLM baseline.** Beating 26 hand-tuned regexes proves a
   model reads better than a deliberately limited pattern matcher. It says nothing against a supervised
   text classifier, an embedding classifier, the bank's existing speech analytics, or a simple feature
   built from complaint codes and contact reasons. *"The 'model is the product' line is wrong."*
3. **Label leakage in the target definition.** "Voluntary closure" is not one event — product change,
   balance transfer, paydown-to-zero, downgrade, inactivity, fee cancellation all differ. And **a
   day-132 payoff enquiry may already be a near-outcome signal rather than an early-warning feature.**
4. **Exporting the feature defeats the no-outbound argument.** Once the score is in a client's feature
   store, *the client* can use it for offers, pricing or eligibility. Absence of an outbound surface in
   our system does not constrain what the bank does downstream — that needs purpose limitation and
   contractual restriction, not architecture.
5. **The back-test measures predictive lift, not retention lift.** Top-decile uplift against a closure
   label shows the feature ranks future closures; it does not show that acting on it makes anyone stay.
   *"The team has quietly converted a causal value claim into a predictive model experiment."* The
   submitted brief's anchor metric was retention lift against a matched control.
6. **"Six weeks" is the modelling calendar, not the bank's.** Procurement, data access, privacy review
   and model-risk intake make it three to six months.
7. **Wall-clock is not a scientific barrier.** Our reason for not reproducing the 30-seed result with a
   model reader is 52,000 sequential calls. *"With a year and a real budget, the calls can be
   parallelised, batched, cached or run on a cheaper model."*
8. **Deletion is a product blocker, not a Q&A item.** An append-only ledger with no purge means
   production readiness is **not currently defensible** — and this is not a minor seam in a product
   whose value depends on retaining quotes indefinitely.

Its verdict on the demo is also more concrete than ours: label the crossing a **mechanism
demonstration** rather than 58-day early prediction · **add a legitimate twin** with the same fee,
rewards and APR language who does not leave · show a portfolio queue at fixed review capacity against a
baseline. *"The current demo makes one authored customer look like a validated use case."*

---

## Two things it got wrong or thin

- **"No anchor" for complaint escalation is one search short** — it says so itself about our document,
  and the same applies to its own dismissal. Issuer remediation reserves and complaints-team headcount
  disclosures are derivable; nobody hunted them.
- **The unit economics do not close and it admits it.** It proposes a `$150K` floor against a `$7,900`
  cost of goods, which is 19×, while conceding a regex does 30% of the job. There is a real pricing
  question here that no one has answered.
