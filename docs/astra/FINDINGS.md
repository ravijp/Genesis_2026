# What seven independent reviews said — 2026-09-11

**Total spend: $0.055** of the $5.96 balance. `gpt-6-astra` was never reachable (see `README.md`
§access); four models ran on the gateway's free tier and three ran as subagents. Nothing here is
authoritative — read it as seven arguments to check, not a verdict to obey.

---

## The result in one line

**Seven models read the same neutral brief. Not one chose card attrition.**

None was told what we had picked. None was given our rankings or our reasoning — `brief.md` carries
facts and no conclusions by design. They were asked what the product should be, and they produced six
different answers, none of them ours.

| Reviewer | Direction chosen | Route |
|---|---|---|
| **Opus** | **Conduct surveillance** — find the *bank's* emerging systemic failures from what unconnected customers say | subagent |
| Sonnet | Elder / vulnerable-customer exploitation | subagent |
| Haiku | Complaint escalation | subagent |
| `deepseek-v4.1-flash` | Elder exploitation / APP fraud | gateway, `high` |
| `deepseek-v4-flash` | **Pre-delinquency** — the direction we withdrew | gateway, `max` |
| `gpt-5.6-luna` | Authorized-payment scam, payment-event triggered | gateway, `high` |
| `qwen3.8-27b` | **None — stop predicting at all.** Serve the memory: agent brief + suppression flag | gateway, `medium` |

*(An eighth, Fable, died on a `429 out of usage credits`.)*

### What that unanimity is and is not worth

**It is not seven independent inventions.** Three landed on fraud-adjacent directions partly because
direction #5 has the longest profile in `brief.md` — it had the most verified anchors (IC3, FinCEN
FIN-2022-A002, the Reg E carve-out) and length is itself a signal. I may have pointed at it.

**But the unanimity survives that.** Opus, qwen and haiku ignored those anchors entirely and reasoned
from the *measurements*, and they still did not pick attrition. And `deepseek-v4-flash` picked
**pre-delinquency** — the option we formally withdrew — which no amount of brief-emphasis explains,
since the brief states its opt-in hardship problem and its 4.5× precision sensitivity plainly.

The honest claim: **no reader of the facts alone reconstructs our choice.**

---

## The diagnosis that replicated three times

Each of the three models that ran phase 2 — reading our actual working documents *after* committing to
its own position — independently reached the same finding in different words:

| Model | Its phrasing |
|---|---|
| `deepseek` | *"The measurement gets the skepticism; the strategy gets the confidence."* |
| `luna` | *"The team has found a way to make the case for attrition more honest without making it more true."* |
| `qwen` | *"The self-criticism is aimed at the numbers, not at the architecture."* |

DeepSeek read our own verbs back at us — *corrected, withdrawn, cut, superseded* around every number
versus *settled, decided, my recommendation* around every strategic choice. Luna listed the pattern as
five instances: churn 1/8 → keep attrition · 8th of 9 → keep the favourable stratum · `p=1.00` → call it
a power failure · precision unmeasured → still say `$1.65M` · latency doesn't apply to path 1 → keep
latency as the headline.

**This one cannot be explained by what the brief emphasised**, because the brief contains no
self-criticism at all. That was the point of writing it that way. Qwen's version is the most actionable:
we corrected the numbers and never corrected the architecture — *the score is still the product* even
though the evidence says the score's ranking doesn't work.

And its consequence, which is the sentence to sit with:

> **"The CEO is being asked to fund a test, not to buy a thing. The product has not been sold. It has
> been proposed."**

---

## The single best idea: Opus

Read `responses/phase1-opus.md` in full. Its reasoning is the strongest in the set.

**The reframe:** stop predicting one customer's future; detect **the bank's present**. Every large
remediation has the same shape — customers described the failure to the call centre, individually,
hundreds of times, for a year; each call handled correctly, refunded, coded generically, closed; nobody
connecting them; then a regulator connects them and the bank pays redress plus a fine plus a
forty-contractor eleven-week look-back. *"The bank was told. It kept the transaction and threw away the
narration."*

**Why this direction and not another — the argument that makes it stick:**

> *"Point the machine at the problem where its measured strengths are the requirements and its measured
> weaknesses are not on the critical path."*

Recall 0.6549 · 13 bad quotes in 5,736 · $1.58/1,000 · reproducible to the decimal · point-in-time
reconstruction — **those are the specifications for a conduct-evidence system.** Calibration, precision
on a real book, per-customer ranking — the three things we never measured or measured badly — **are not
required by it at all.**

**Category: conduct surveillance.** Trade surveillance pointed at customers instead of traders. Nasdaq
SMARTS, Behavox, Shield, Smarsh already read 100% of employee comms, accumulate per person over time,
queue to a human with the verbatim message as evidence, and keep an append-only audit trail. That is our
architecture line for line, aimed at the other population — so the buyer needs no education, the budget
line exists, and the incumbents don't touch customer conversations.

**The consent finding, which nobody else got and which may decide everything:** recordings made *"for
quality and training purposes"* genuinely do cover monitoring service quality, complaint handling and
conduct — that is what the words say. They do **not** cover marketing, cross-sell or retention. So
conduct is the one direction that fits inside the consent the bank already has; every customer-value
framing needs a new consent conversation nobody wants to have. **That is an argument about whether the
deal closes, independent of the model.**

**The demo is two dates.** *3 March* — when the system would have opened the case. *14 November* — when
the bank actually found out. **256 days.** Then the accrual in the client's own numbers: 412 customers
and ~$19K on the first date; 31,000 customers, $3.4M redress, a 21-month look-back by 40 people over 11
weeks, and a consent order on the second.

> *"A finance executive does not have to believe a model to believe a date."*

**The close:** *"Give me your last five remediations and the date you found each one. In six weeks I'll
give you five different dates."* — approvable **without believing anything you just said**.

**And it converts our worst result into the credibility play:** *we pre-registered whether this memory
improves per-customer ranking, it does not beat chance, we published it as a failure — which is
precisely why this product does not rank customers. It counts what customers told you, which is a fact,
not a forecast.*

---

## The most actionable today: Qwen

Opus's version needs a cluster layer that does not exist (~8 weeks). **Qwen's needs no rebuild.**

It reads our losing numbers as evidence about what the system *is*: *"a faithful, thorough, quote-backed
reader and rememberer — not a good forecaster."* So stop feeding a propensity model, where the score
becomes a feature with a weight of 0.003, and serve the memory directly:

- **The agent brief** — before the call connects, four items with verbatim quotes, a flag line, a
  trajectory note. Read in ten seconds.
- **The suppression flag** — written to the CRM suppression object. *"DO NOT INITIATE MARKETING CONTACT.
  Reason: customer stated job loss and payment difficulty, 8/14, quote on file."*

It costs *"a week of re-authoring plus a day building the suppression flag"* — same engine, same ledger,
same 908 tests. Output becomes brief-and-flag rather than score-and-queue · buyer becomes Operations and
the CCO (**the submitted brief's own buyer**) · demo climax becomes the agent's screen rather than the
score crossing · value becomes operational rather than a four-haircut chain.

Its demo opens on the CRM showing one line of history — *"billing inquiry, resolved"* — and says: **that
is the bank's entire memory of this customer.**

---

## The best technical argument: Sonnet

Sonnet made an argument nobody else did, and it is checkable against our own harness.

**The mechanism's own best-measured property maps onto grooming and not onto attrition.** Never-discard
beats forgetting **30-0-0 on diffuse** evidence and loses **0-30-0 on concentrated** evidence. Slow
grooming *is* diffuse — a new online friend in week one, a fee that must be paid first in week three, a
wire in week five, each utterance harmless and the sequence damning. Attrition is a concentrated ranking
task, which is exactly where the system underperforms chance at portfolio scale.

Its constraint is the one to carry into any direction: **claim retrieval and memory, never judgment.**
Agent verdict accuracy ~58% and sub-chance portfolio ranking do not support *"we predict fraud"* — only
*"we never lose the quiet evidence."*

---

## Things that stand regardless of direction

1. **The retro property has no user.** Training joins `score_at_write`, inference uses `score_now`, the
   next agent sees today's score. It is displayed and never consumed — the demo's mechanism, not the
   product's. Opus names its real user: **point-in-time audit**, *what did you know and when*. Built as
   a forecasting feature; it is an audit feature, and *"audit features in banks are worth considerably
   more than forecasting features, because they are bought by people with no alternative."*
2. **The demo peaks on an authored fixture.** The 58-day gap is a number we told the room we chose.
   Every model that addressed it said move the climax.
3. **The sunk cost is the demo itself.** *"Everything downstream of 'we have a strong attrition demo'
   has been shaped to protect the continued use of that demo."*
4. **`$1.65M` should not be said as an expected value.** Unanimous, on grounds of the missing
   false-positive leg.
5. **Deletion is a production blocker, not a Q&A item.** An append-only ledger with no purge is
   incompatible with retention schedules and state deletion rights. ~1 week to fix.
6. **Nobody has checked whether CFPB narratives satisfy the competition's synthetic-or-anonymised
   rule.** If they don't, every card-specific number is unusable. Submission-control issue.
7. **We never tested against a competent non-LLM baseline.** Beating 26 hand-tuned regexes says nothing
   about a supervised classifier or the bank's existing speech analytics.

---

## Where they disagreed, and the disagreement that mattered

`deepseek` built its money beat on the FBI's $38,000 average elder loss. `luna` **revised its own phase
1** to reject exactly that: *"the FBI's $7.7 billion and $38,000 average loss are not bank value… I
would not lead with 'we save $38,000 per victim.'"* Reg E does not reach authorised transfers — **the
money is the customer's.** Our own brief says so and neither we nor deepseek joined it up.

**One model proposed the argument and another killed it. Neither would have caught it alone.** That is
the strongest case for having run more than one.

`deepseek-v4-flash` also picked **pre-delinquency**, which we withdrew — worth reading as a challenge to
that withdrawal, not a refutation of it.

---

## What I would do with this

**Before the gate**, only the wording changes are available: move the demo's climax off the 58-day gap ·
stop presenting `$1.65M` as expected value · say the 1/8 card result as the *reason* for a framing
rather than a disclosure · and consider Opus's credibility play, which turns the chance-gate failure
from a liability into the reason the product doesn't rank customers.

**After it**, the real question is which of three the evidence should decide:

| | Cost | What it buys |
|---|---|---|
| **Qwen** — brief + flag | ~1 week | Needs no new evidence at all; every measurement problem stops applying |
| **Opus** — conduct surveillance | ~8 weeks | The strongest story and the only one whose value chain has no accuracy term |
| **Sonnet / deepseek** — elder exploitation | ~2 weeks | Best mechanism fit (diffuse), best-sourced anchor, mandatory consuming queue |

All three keep the engine, the ledger, the retro fields, the verbatim-quote contract, the deployed
pipeline and the test suite. **None of them is a rebuild.**
