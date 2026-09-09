# Read this first

**Ravi — this is the whole thing in one page. Gate is 2026-09-11, 20:30-21:00 IST.**

> ## What happened while you slept — 2026-09-09 overnight
>
> **The market decision is settled. What is left is rehearsal.** Everything below is done and committed.
>
> **① SETTLED — you decided this on 2026-09-09. Nothing left to do.** There were two competing
> scripts for this gate. **US attrition runs. The UK complaints story is a footnote**, distilled into
> **`03-REFERENCE.md` §7** with the £650 Ombudsman tariff and the two questions that make it the right
> answer. The old UK script is bannered superseded at `docs/gates/2026-09-11-sprint-review.md`, kept
> because it holds the only **published tariff** in this entry. **Rehearse from `01-THE-STORY.md`
> only. Never say a pound sign unless you are answering "is any of your value a hard number rather
> than a model?" — and then say "UK" in the same sentence.**
>
> **② The lexicon no longer carries the numbers.** You asked for a gen-AI story, and the evidence was
> already bought — see *the reader beat* in `01-THE-STORY.md`. On the same 282 conversations Haiku
> 4.5 finds complaint escalation in **60 of 65** planted conversations against the regex lexicon's
> **1 of 65**. It **loses** financial distress, 27/72 against 33/72, and we publish that.
>
> **③ The keyed 10-seed run finished — $10.66, and it did one job well and one not at all.**
> **The reader result is decisive and is now your gen-AI headline:** across 10 datasets and 6,990
> conversations, **Haiku 4.5 recovers 0.6549 of the planted evidence against the regex lexicon's
> 0.2435** — 2.7×, same corpora, same answer key. Quote fidelity: **11 non-verbatim and 2 relocated
> out of 5,736 signals.** Say the counterweight with it: **it also fires ~7× more unplanted
> extractions.** Better reader, noisier reader.
>
> **The arm comparison came out inconclusive and you should know why.** `full-ledger` vs
> `window3-top2` was **5-4-1, p=1.00** against the published **30-0-0**. **That is a power failure,
> not a refutation** — a free control at the same scale with the *offline* reader gave **4-3-3,
> p=1.00**. At 200 customers every arm sits on chance. The published scale needs ~52,000 sequential
> model calls, which is blocked by **wall-clock, not money. So 30-0-0 stands, and stays labelled an
> offline-reader result.**
>
> **④ One build decision is now settled by measurement.** The model's confidence float takes **21
> distinct values across 5,112 emissions, ten of which cover 95.3%, with 0.85 alone at 28.4%** — a
> menu, not a probability. Removing it entirely moves only **10.5%** of the queue, making it the
> *least* load-bearing mechanism under a model reader. **Bucketing it to three tiers is a formality,
> not a trade-off — see `06-DEFENDING-THE-SCORE.md` §3.**
>
> **Also done:** the alternates file is now anchored and three stories are cut · the gate date moved
> and both dead dates struck · `06-DEFENDING-THE-SCORE.md` answers the model-reproducibility
> question · SR 11-7 is rescinded and corrected everywhere.

**Seven files that matter, in reading order** (an eighth, `05-NEXT-CONVERSATION-PROMPT.md`, is a
spent brief and is bannered as such). If you only read one, read this. If you read two, add
`06-DEFENDING-THE-SCORE.md` — because it answers the question most likely to end the pitch.

| File | What it is | Read? |
|---|---|---|
| **`00-READ-THIS-FIRST.md`** | This page. Recommendation, your decisions, checklist | **Yes** |
| **`01-THE-STORY.md`** | The pitch. Six beats, the actual words, objection playbook | **Yes** |
| **`02-THE-DEMO.md`** | The demo, screen by screen | Skim |
| **`03-REFERENCE.md`** | Everything else — signals, score, governance, value model, what we may/may not quote, the red-team record | **No.** For when you're challenged |
| **`04-ALTERNATE-STORIES.md`** | 13 other ways to point the same layer. **The recommendation to switch to pre-delinquency is now withdrawn — see the verdict below.** Q&A depth only | Skim |
| **`06-DEFENDING-THE-SCORE.md`** | **"LLM outputs aren't reproducible — what happens when you switch models?"** The four sentences you say, the SR 11-7 correction, and the confidence float | **Yes, second** |
| **`07-LANDSCAPE.md`** | Who else does this, what it costs them, and the one real competitor | Skim |

Everything is **US-based**. Ten earlier UK-based files were deleted rather than left to poison the
room with a pound sign.

## The verdict on pre-delinquency vs attrition — settled 2026-09-09. Do not switch.

`04-ALTERNATE-STORIES.md` recommends leading with pre-delinquency on a claimed **7-10x** value per
event. **That recommendation is withdrawn. Lead with attrition.** The multiple was wrong and the
tiebreaker was backwards. **Corrected arithmetic:** recoveries run **17-27% of gross card charge-offs**
across six issuer observations FY2023-H1 2026 — Capital One Domestic Card, six months to 2026-06-30,
gross $8,552M / recoveries $2,314M = **27.1%** (10-Q Table 26); Synchrony FY2025, gross $6,673M /
recoveries $1,452M = **21.8%** (10-K) — so loss given charge-off is about **75%**. The **$5,000** came
from applying that to a **$6,610 balance that is per borrower, not per account** (the book's own
figures give **$1.263T ÷ 608M = $2,077 per open account**), and **the balance at charge-off is
published nowhere**. Honest net loss per charge-off is **~$3,400, range $2,300-$5,000**, so the
multiple is **3-9x, centrally about 5x — not 7-10x.** And that is *gross per event*: a
pre-delinquency false positive costs roughly **$430** of foregone interest against roughly **$95** for
an attrition fee waiver, making it about **4.5x more precision-sensitive** — and precision is exactly
what we have never measured. **Risk-adjusted, the multiple can fall below 1x.** Three non-money
reasons finish it: **T3 is backwards in the alternates file** — hardship programmes are *opt-in*, so
you cannot enrol a silent customer without contacting them, which makes pre-delinquency's "what
happens when they aren't calling" answer **worse** than attrition's, not a 5/5; it **destroys the best
line in the pitch** by making distress the product rather than the thing we deliberately refuse to
sell against; and the CFPB card evidence for distress is **2/2 documents** — a denominator of two,
because **none** of the benchmark's 17 distress-enriched narratives is a card complaint. Add that you
are **two days out with zero dry runs done**, and switching stories now is the highest-risk available
use of the remaining time. **Keep `04-ALTERNATE-STORIES.md` as Q&A depth. Do not re-open this before
09-11.**

**Two smaller calls that go with it.** The **two-desk pairing** (pre-delinquency as beat A, attrition
as beat B) is **rejected** — it doubles the anchor surface you have to defend, re-opens "so which desk
is it", and halves the demo, which is the only thing in the pitch a competitor cannot reproduce. Make
the layer argument in **one sentence at the end of the demo** instead. And of the six unanchored
alternates, **only #5 (scam and elder exploitation) is worth anchoring** — it is the one with a
government per-event dollar figure a single search away and the strongest T3. **Cut #10 (credit-line
increase) entirely**: it is the on-ramp to #11, which the document itself says never to raise.

---

## My recommendation, in five lines

1. **Lead with latency, not clairvoyance.** *"Your propensity model refreshes monthly and never sees
   what the customer said. Ours moves the moment the transcript lands."* Structural, needs no lift
   study, cannot be attacked. This replaces "we spot churn 58 days early", which was a number we chose.
2. **Put the project on the table in minute three, not minute eighteen.** A six-week fixed-fee
   retrospective back-test on their recordings and their closure label, with a **pre-registered**
   success criterion and an explicit walk-away. This is the single biggest change I made. A CEO can say
   yes to an experiment. He cannot say yes to a value chain with a hole in it.
3. **Answer "what happens on day 74 when the customer isn't calling" before anyone asks.** The case
   briefs the next agent who speaks to them. Without that sentence your early-warning claim and your
   no-outbound-surface claim contradict each other four minutes apart — and that contradiction was the
   thing most likely to end the pitch.
4. **The money is a chain you multiply through yourself, out loud, including the small bit.** ~30,000
   names on a five-million-account book — **six tenths of one percent** — and about **$1.65M/year
   gross** on assumptions they control. Say it before they work it out. Then: reading every
   conversation costs about **$16,000/year**, so affordability was never the question.
5. **Say the corpus problem yourself, right after the demo.** Every number we own was measured on a
   generic retail-bank corpus with zero credit-card content. Placed after the demo it's credibility.
   Placed in beat 1 it's the only thing they remember.

---

## What the US switch changed

**We lost our best number.** The UK pitch led with the £650 Ombudsman per-case tariff — published,
verifiable, unarguable. **There is no US equivalent.** *(It is not thrown away: it is kept as the
appendix at `03-REFERENCE.md` §7, and it is the honest answer to "is any of your value a hard number
rather than a model?" — see the settled decision at the top of this page.)* One candidate replacement worked and one
did not.

**The one that did not — do not use it:**

- **CFPB enforcement risk.** As of 2026 the CFPB's funding and headcount are materially down
  (~1,300 staff from ~1,700), enforcement principles were rolled back in June 2026, and fair-lending
  supervision is contracting. **Leaning on CFPB risk in 2026 would read as not having checked.**

**So the money story changed shape, and it is better for it.** It now rests on published market
arithmetic — **608 million open general-purpose accounts**, **0.7–1.0% of them closing every month**
(CFPB, published 2025-12-30), $1.263T balances at 22.15% APR, **$2,077 per open account** (and
$6,610 per *borrower* — never mix the two), **3.82%** charge-offs (CORCCACBS, updated 2026-08-25;
**not** G.19, which publishes no charge-off rate) — plus **client-verifiable** inputs for the two numbers that
convert revenue into value. **Re-acquisition cost stays in the chain as their number, not ours.** That
is arguably stronger: a client cannot argue with their own CAC.

### The CAC correction — this improves the pitch

I first reported that no US issuer discloses acquisition cost, so it could only be a client input.
**That was too pessimistic.** No issuer discloses "CAC" as a line item, but **two disclose both a
marketing numerator and a new-account denominator**, which makes it derivable from primary filings:

| Issuer | Derived cost per new card | From |
|---|---|---|
| **American Express**, worldwide | **$500** (2025), $465 (2024), $427 (2023) | FY2025 10-K, filed 2026-02-06 |
| **American Express**, US consumer only | **$549** (2025) | 10-K + Q4'25 deck |
| **JPMorganChase** | **$532** (2025) | FY2025 10-K + 4Q25 release |

So the re-acquisition leg has a **published upper bound of roughly $430–$550**, and the "$80" figure
circulating online is contradicted by primary arithmetic by about 6x. **Do not quote $80.**

**Two things to carry.** First, say **"upper bound"** every time — marketing expense also covers brand
and retention spend, and Capital One's own 10-K admits its marketing line includes efforts to
*"attract **and retain**"* plus spend-based bonuses. Second, **do not use the "acquiring costs 5-25x
more than retaining" line** — it traces to a 2014 HBR piece that prefaces it with *"depending on which
study you believe"* and cites nothing. Use Bain's properly sourced one instead: **in financial
services, a 5% increase in retention produces more than a 25% increase in profit.**

I deliberately kept the value chain at a conservative **$250** per avoided re-acquisition rather than
the derived $500, so the $1.65M central case sits **below** what the filings would support. That is the
right way round.

**One argument had to be dropped entirely.** The UK version leaned on the FCA persistent-debt regime —
"a conversation the regulator already requires you to have." **There is no US equivalent.** The CARD
Act and Reg Z require *disclosures*, not conversations. Don't try to translate it.

**One thing got much better than expected.** The attrition anchor is no longer a 2012 trade estimate.
**The CFPB's own December 2025 report states that between 0.7% and 1.0% of general-purpose accounts
close every month** — 8.4% to 12.0% a year, against 608 million open accounts, from a 2% national
longitudinal credit-record sample. **That is a regulator primary source.** It is independently
corroborated by Amex's own filings: 13.0M new proprietary cards against a 83.6M→86.6M cards-in-force
move in FY2025 implies ~10.0M closures, or **11.8%** — derived from primary SEC documents, not a
vendor claim.

**Two caveats to carry, and the first one matters.** CFPB's *own* 2021 and 2023 reports say "about 2
percent of accounts are closed each year" — four to six times lower, unreconciled, because the
underlying panel changed. Quote the monthly figure and volunteer the contradiction if pressed.
And **the voluntary-versus-involuntary split is not published anywhere** — CFPB defines the two and
gives no numbers, so the "about half" split is still only a 2012 trade estimate.

---

## Decisions I made for you

Reverse any of these if you disagree, but they're all defensible and they're all in the docs.

| # | Decision | Why |
|---|---|---|
| 1 | **Headline is latency, not "58 days"** | 58 = 132 − 74, both authored fixtures. Speaking an authored number as a result is how you lose the one technical person in the room |
| 2 | **The demo's crossing was re-cut** | It fired on a competitor mention. A customer quoting a rival's 21-month offer has already shopped and may already have applied — that leads the *event*, not the *decision*. It now fires on rewards friction + promo-expiry, which is genuinely pre-decisional |
| 3 | **Claim three signal families, not eight** | Only price/value objection, rewards dissatisfaction and life event genuinely lead the *decision* and have no structural proxy. All eight still feed the score. Saying three honestly beats implying eight |
| 4 | **The brief-contradiction moved to Q&A** | Our submission says *"none of these is the headline; the layer is"*, and leading with one score negates it. But Venkat and Farhan didn't write that brief — quoting your own contract against yourself to a commercial audience imports a governance problem into a sales pitch. On stage: *"we've narrowed to the strongest single view for this sprint"* |
| 5 | **The five adjacent use cases are cut from the stage** | Breadth reads as unfocus to a CEO deciding fundability, and two of the five are "designed, not built" in credit decisioning — the most regulated adjacency there is |
| 6 | **Dropped the "invisible third of the book" opener** | It argued *against* the product: the accounts with no balance are the ones with the least reason ever to call us, so they're precisely the ones we have nothing on |
| 7 | **Named the score "conversation attrition score"** | You said "attrition score" and the word attrition stays. The qualifier says in the name that it's partial, which pre-empts the assumption it replaces their model |

---

## Decisions that are yours

**Only two really matter.**

### 1. Do we spend ~$0.45 and a few hours to get one honest card number? *(Recommend: yes)*

Right now **not a single measured number in this repo is about credit cards.** Everything — coverage,
recall, agent verdicts, cost — was measured on a generic retail-bank corpus with no APR, no annual fee,
no points anywhere in it.

The fix, in order, and **step A is not optional:**

| | Step | Cost |
|---|---|---|
| **A** | Author 5–10 US-card churn fragments into `corpus_lexicon.py` | **$0**, a few hours |
| **B** | `earshot sweep --seeds 30 --customers 1500` | **$0**, ~104s |
| **C** | `tools/reader_coverage.py --reader both --per-trajectory 20` | **~$0.45** |

Running B or C *without* A produces the same generic numbers with a new label — which is the exact
dishonesty the whole triage exists to prevent. Budget remaining is about **$9.55 of $12**, so cost is
not the constraint; your time on step A is.

**Without this, the honesty beat *is* the pitch.** With it, you have one card-flavoured coverage
number, honestly labelled as a direction rather than an interval.

### 2. Who is the buyer? *(Recommend: Head of Retention Analytics)*

Our submitted brief named a **Contact Centre Operations or Chief Customer Experience** buyer. But
"consumed by existing retention modelling" points at **Retention Analytics or Credit Risk.** Different
signature, different sales motion. This one is worth saying out loud on stage rather than swapping
quietly — it changes who signs.

---

## Before you walk in

| | | Why |
|---|---|---|
| 1 | **Do the two dry runs** | Two were committed, **zero done.** Every change I made is a *wording* change, and wording only survives a room if it's been said out loud once. This is the highest-value remaining work, ahead of any code |
| 2 | **Record the demo the day before** | A room with no wifi must not be able to break your best beat |
| 3 | **Step A — author 5–10 US-card churn fragments** | **Still the constraint, and still unbought.** It costs hours, not dollars. The $10.87 spent on 2026-09-09 bought the *reader* comparison, not card content — B and C without A still produce generic numbers under a card label. See decision 1 |
| 4 | ~~**Get a fresh CloudWatch alarm-history read**~~ **DONE 2026-09-09** | The repo contradicted itself; it is settled from CloudWatch. **`earshot-dev-ingest-failures` went OK → ALARM at 2026-09-03 04:06:22 IST and back to OK at 04:33:22**; the other five alarms have never left OK. `handover.md` was right, `state-of-play.md` was stale and is fixed. **Safe to say in the demo** |
| 5 | ~~**Check if the CFPB sample is card-heavy**~~ **DONE 2026-09-09** | **It is: 55 of 150** narratives are credit-card (51 general-purpose or charge, 4 store). Split by product for **$0** from the committed cache. On those 55 the reader fires on **29/29** marked documents and gets the exact type on **26/35** marks — **but churn intent is 1/8.** Post-hoc, not pre-registered. **Read the honesty beat in `01-THE-STORY.md` before quoting any of it**: the 1/8 goes in the same breath as the 29/29 |
| 6 | **Re-login to AWS the morning of, and again before walking in** | The SSO token expires in hours and a dead token looks exactly like broken code |

---

## The three things most likely to go wrong

1. **You quote the retention coverage row (1/20 → 16/20) as a card number.** It's a true measurement of
   a *different corpus*. Permitted only as labelled mechanism evidence. This is the single most tempting
   and most dangerous number in the repo.
2. **Someone asks what happens on day 74 and you don't have the answer ready.** It's in beat 4. Rehearse
   it until it's automatic.
3. **You say "cards" when you mean "accounts", or quote a pound sign.** Both mark you as not having done
   the work, instantly, to this audience.
4. **You say "SR 11-7".** It was rescinded on 2026-04-17 and replaced by **SR 26-2** (joint OCC/Fed/FDIC;
   OCC 2026-13 kills OCC 2011-12). Citing dead guidance to a bank audience is the same class of error as
   the CFPB-enforcement argument you already cut. **`06-DEFENDING-THE-SCORE.md` §2.**
5. **You say distress signals are "structurally blocked from feeding an offer — it's a branch in code".**
   **There is no such branch**, because there is no offer surface in the system at all. Say routing plus
   absence. The true version is stronger; the false version is checkable.
6. **You quote 29/29 on card documents without saying 1/8 in the same breath.** See the honesty beat.

---

## What I'd tell you if you asked me straight

**The mechanism is genuinely good and the demo is genuinely strong.** Accumulation, never discarding,
retro re-scoring, a deployed pipeline that agrees with local to the last digit, and no outbound surface
at all — that's a real system and it will show well.

**The weakness is that the value claim can't be proven without their data, and no amount of synthetic
work fixes that.** Which is why I turned the pitch from *a product with a value chain* into *a funded
experiment with a pre-registered criterion and a walk-away.* That's the version a CEO can act on.

**The single best line you have is the one about deliberately not selling to a distressed customer.**
Distress and life-event signals are blocked in code from feeding any offer. Two executives sitting
through an AI pitch are waiting for the moment the vendor shows they know where the harm is. Give them
that moment, unprompted, and most of the rest of the scepticism goes quiet.
