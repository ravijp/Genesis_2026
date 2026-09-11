# What the outside read said — 2026-09-11

**Total spend: $0.00.** `gpt-6-astra` was never reachable (see `README.md` §access). Everything below
came from free-tier models, which weakens the *authority* of the result and not its *content* — read it
as an argument to check, not a verdict to obey.

| Run | Model | State |
|---|---|---|
| Phase 1 | `gpt-5.6-luna` (OpenAI) | done |
| Phase 1 · 2 · 3 | `deepseek-v4.1-flash` (DeepSeek) | done — the full three-phase trajectory |
| Phase 1 | `qwen3.8-27b` (Alibaba) | timed out at the gateway twice |
| Phase 2 | `gpt-5.6-luna` | running |

---

## The one-line result

**Both models that answered threw away card attrition, unprompted, and landed on scam / elder
financial exploitation.** Neither was told what we had chosen, neither was told the option rankings,
and neither was asked to evaluate the choice — they were asked what the product should be.

### How much weight that carries — honestly

**Less than it first looks, and still enough to act on.** Direction #5 has the longest profile in
`brief.md`, because it had the most verified anchors (the IC3 figures, FinCEN's FIN-2022-A002, the Reg E
carve-out). Both models leaned on exactly those. So this is closer to *"the best-evidenced option in
the brief is not the one we are pitching"* than to *"two models independently invented the same idea."*

That is a weaker claim. It is also still an uncomfortable one, because it is true.

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

---

## Where the two models disagreed

| | `gpt-5.6-luna` | `deepseek-v4.1-flash` |
|---|---|---|
| Name | Scam Sentinel | Standing Record |
| Trigger | **A pending payment event wakes the memory** | Nightly batch, threshold crossing |
| Category | Payment-fraud decisioning (existing category) | **"The stated record"** — the fourth source of truth beside transactions, balances and bureau |
| Metric | Incremental recall at fixed alert budget | **Warning days** — because you cannot A/B a fraud intervention; you will not let half the scams through |
| Buyer | Head of Payments Fraud | BSA Officer |

**The best version is a composite**, and neither model proposed it: luna's *payment-event trigger* is a
better mechanism than threshold-crossing, deepseek's *warning days* is a better metric than lift, and
deepseek's *"stated record"* is a better category than either product name.

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

- **Pitch the mechanism and name the direction**, using the current demo as the demonstration apparatus
  while saying plainly which desk the evidence actually points at.
- **Take the money argument now.** It needs no new build — two published numbers and a division.
- **Fix the demo's peak** — move the climax from the 58-day gap to the retro column. Wording only.
- **Say the 1/8 finding as the reason for the direction**, rather than as a disclosure. Phase 3's
  version: *"that is the strongest honest evidence against the direction we were pitching, and it is
  why we are not pitching it anymore."*

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

## Two things it got wrong or thin

- **"No anchor" for complaint escalation is one search short** — it says so itself about our document,
  and the same applies to its own dismissal. Issuer remediation reserves and complaints-team headcount
  disclosures are derivable; nobody hunted them.
- **The unit economics do not close and it admits it.** It proposes a `$150K` floor against a `$7,900`
  cost of goods, which is 19×, while conceding a regex does 30% of the job. There is a real pricing
  question here that no one has answered.
