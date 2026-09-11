# Twenty-one independent reviews — 2026-09-11

**Seven models × three phases. Total spend $0.0785.** Four ran on the Experiential gateway's free tier;
three ran as subagents. `gpt-6-astra` was never reachable — see `README.md` §access.

**The phase design is what makes this worth reading.** Phase 1 gave each model a brief carrying facts
and *none of our conclusions*, and made it commit. Phase 2 then showed it our actual working documents
and asked it to judge them. Phase 3 asked for a decision. Because each model's position was already on
disk before it saw a word of our reasoning, "they convinced me" and "I deferred to someone with more
context" stay distinguishable.

---

## The result

**Seven models chose a direction cold. Six kept it after reading our best arguments for attrition.**

| Model | Phase 1 | After seeing our documents |
|---|---|---|
| **Opus** | Conduct surveillance | **held** — strengthened, plus the experiment that would settle it |
| **Sonnet** | Elder exploitation | **held** — "Undertow", BSA Officer |
| `deepseek-v4.1-flash` | Elder / APP fraud | **held** — pitch the pivot at the gate |
| `gpt-5.6-luna` | Authorized-payment scam | **held** — attrition becomes "a retired fixture and an appendix" |
| `deepseek-v4-flash` | Pre-delinquency | **held** — collections input, credit-loss budget |
| `qwen3.8-27b` | Stop predicting; brief + flag | **held** — "re-point the product from a score to a memory" |
| **Haiku** | Complaint escalation | **MOVED → keep attrition**, reframed as measurement |

Phase 2 handed every model the corrected pre-delinquency arithmetic, the T3 discriminator, the 4.5×
precision-sensitivity argument, the full decision log and the objection playbook. **One model came
back.** What convinced Haiku was not the direction argument but the *commercial* one — it credits the
six-week back-test with a pre-registered criterion and walk-away as *"something a CEO can act on,"* and
says that solved a problem its own phase 1 had missed.

**Read that as the finding it is: the shape of the ask is the strongest asset in the packet. The
direction is the weakest.**

### The honest discount

Three landed on fraud-adjacent directions partly because direction #5 has the longest profile in
`brief.md` — it had the most verified anchors and length is itself a signal. I may have pointed at it.
But Opus, qwen and haiku ignored those anchors and reasoned from the measurements, and
`deepseek-v4-flash` chose **pre-delinquency**, which we formally withdrew. And all of this came from
free-tier and subagent models, not the frontier model we wanted.

The claim that survives: **no reader of the facts alone reconstructs our choice.**

---

## The diagnosis, reached five times independently

| Model | Its phrasing |
|---|---|
| **Opus** | *"An excellent defence against being caught, a weak defence against being wrong."* |
| `deepseek` | *"The measurement gets the skepticism; the strategy gets the confidence."* |
| `luna` | *"A way to make the case for attrition more honest without making it more true."* |
| `qwen` | *"The self-criticism is aimed at the numbers, not at the architecture."* |
| **Sonnet** | Asymmetric scrutiny, caught in one place — see below |

**This cannot be explained by what the brief emphasised**, because the brief contains no self-criticism
at all. That was the point of writing it that way.

**Sonnet's version is the most checkable.** Two results from the *identical* 10-seed keyed run are
treated oppositely: the arm comparison came out 5-4-1 `p=1.00` and we call it a **power failure**; the
reader comparison came out 0.6549 against 0.2435 and we call it **the answer to give**. Same run. There
*is* a defensible justification — the reader result rests on 5,736 signals and the arm result on ten
paired seeds — and we never made it.

**Qwen's version is the most actionable:** we corrected the numbers and never corrected the
architecture. The score is still the product even though the evidence says the score's ranking does not
work. Its consequence:

> **"The CEO is being asked to fund a test, not to buy a thing. The product has not been sold. It has
> been proposed."**

---

## One error found and already fixed

Opus caught a live contradiction inside `00-READ-THIS-FIRST.md`. Line 283 asserted, as *"the single
best line you have"*, the exact claim line 265 lists as a thing that ends the pitch — that distress
signals are *"blocked in code"* from feeding an offer. **Eighteen lines apart, on the page read last
before walking in.** Both the correction and the violation were ours. Fixed 2026-09-11; it now says
routing plus absence with the `TRAJECTORY_TEAM` reference.

---

## The single most valuable output: the CFPB historical back-test

From Opus phase 3 §6. **This is worth having whatever is decided about direction.**

Pull the public **CFPB Consumer Complaint Database**. Pick 3–5 issuer/product pairs with a **publicly
dated event** — a consent order, an enforcement action, a disclosed remediation. Take 24 months of
narratives before each. Ask one pre-registered question: **on what date does a cluster describing the
mechanism first form, and how many days is that before the public event date?** Publish the
distribution, the misses, and the false-cluster rate on control pairs with no known event.

**Why nothing else we have measured is like this:**

- **The text is not ours and the ground truth is not ours.** A consent-order date is a public fact we
  cannot plant, tune to, or be accused of having authored an arc to recover — which is exactly the
  circularity charge our own documents make against the arms programme.
- **It satisfies the competition rule.** CFPB publishes narratives only with consumer consent and
  scrubs PII.
- **It measures the actual claim**, not a proxy.
- **$79–395 of model spend, ~5 weeks, one engineer.**

Two cheap items alongside: an **ASR degradation curve** (1–2 days, ~$20–50 — every number we own is on
clean authored text while production input is ASR output, the largest unmeasured synthetic-to-real gap),
and **ledger tombstoning** (~1 week — append-only with no purge fails the first compliance review).

---

## Available tonight — wording only, no build

Every reviewer that addressed the gate converged on these, and none needs a commit:

1. **Delete the `$1.65M` chain.** Unanimous. Opus: six assumptions, no cost side, and the queue repair
   invalidates it — *"a chain with six assumptions and no cost side is not repaired by adding a seventh
   assumption for cost."* At ~2,000 cases per analyst-year, 30,000 cases is ~15 FTE against $1.65M
   gross.
2. **Fix the live contradiction in the money beat.** Beat 1 says 8–12% of accounts close annually; beat
   5 multiplies through 5% voluntary. **Same quantity, factor of two, eleven minutes apart**, bridged
   only by the 2012 estimate our own docs disavow.
3. **Move the demo's climax off the 58-day gap.** It is an authored fixture we tell the room we chose.
   Put the retro column there instead — and **say 239/485 with its 0/485 control**, which appears in
   neither `00-READ-THIS-FIRST.md` nor `01-THE-STORY.md` and is the only quantified statement we have
   about the thing we claim as the invention.
4. **Say the nulls before anyone finds them** — the chance gate at `p=0.076`, and `dumb-ledger`'s
   corrected **13-11-6, `p=0.839`**, which appears in none of the four pitch documents while the
   playbook offers to run that very test for a client.
5. **Put the ask in minute one**, not minute three.

---

## The direction question — after tonight

| Option | Build | What it buys |
|---|---|---|
| **Qwen** — brief + suppression flag | ~1 week | Needs no new evidence; every measurement problem stops applying. Keeps the submitted brief's own buyer |
| **Opus** — conduct surveillance | ~3–5 weeks | Strongest story; the only value chain with **no accuracy term**; and the CFPB back-test makes it falsifiable on real data |
| **Sonnet / deepseek** — elder exploitation | ~2 weeks | Best mechanism fit: never-discard wins **30-0-0 on diffuse** evidence and loses **0-30-0 on concentrated** — grooming is diffuse, attrition is concentrated |
| **Haiku** — keep attrition, reframe as measurement | 0 | The back-test becomes the product rather than the proof of one |

**All four keep the engine, the ledger, the four retro fields, the verbatim-quote contract, the deployed
pipeline and the 908 tests. None is a rebuild.** Opus prices its version at one new aggregation module
and one new metric, and notes that re-pointing cheaply is the *originality* claim in the submitted
contract being **true rather than asserted**.

---

## What every reviewer said to keep

The extractor and citation contract — *"under a prediction product it is plumbing; under an evidence
product it is the product"* · the ledger's four fields · the corpus generator with ground truth authored
before the prose · the multi-seed harness and the **byte-identical re-run**, which several models say is
badly under-used · the separation guard over 45 modules · the deployed pipeline · cost and latency ·
model-swap at `$0.027705` · `TRAJECTORY_TEAM` plus the absence of any outbound surface · the 908 tests ·
and **the SR 26-2 section unchanged**, which two models independently called the strongest work in the
packet.

**Two claims to stop making:** *"the demo is the only thing a competitor cannot reproduce"* — stated
three times, and false; the reproducibility stack is. And **30-0-0 as the accumulation headline** —
offline reader, corpus-dependent, records reversed twice.

---

## What this exercise cannot tell you

- **No frontier model on the gateway was reachable.** These are free-tier and subagent models.
- **I wrote the brief**, so its emphasis shaped the answers — demonstrably so on direction #5.
- **Six models preferring a direction is not evidence that direction works.** Opus says this against
  itself: *"My direction has never been measured. Theirs has been measured and has failed. Those are not
  the same thing and I will not dress the second as an advantage."*
- **Nobody has checked whether CFPB narratives satisfy the competition's data rule** for our *existing*
  benchmark use. Opus argues they do. It has not been verified.
