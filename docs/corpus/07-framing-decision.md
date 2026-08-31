# Phase 7 — the framing decision

**2026-08-31.** Phase C rebuilt the corpus and killed the pre-registered headline. This document
decides what the entry claims instead, and it is a decision, not a menu. Everything below is written
to be checkable: the AI judge can run `uv run earshot sweep --seeds 30 --customers 1500` and see all
144 comparisons, and any framing that needs a number not to be looked at fails.

**Everything here was measured today, offline, at zero API spend**, on `921ec42`
(`build/ear-on-every-call`, post-Phase-C merge).

---

## 0. What was re-measured today, and what is new

Four runs. The first reproduces the record; the other three are new evidence that decides §3 and §5.

| # | run | cost | result |
|---|---|---|---|
| 1 | `earshot sweep --seeds 30 --customers 1500` | free, 113 s | **`arms`, `comparisons`, `samples`, `budget_curve` byte-identical** to the committed `artifacts/runs/sweep-30x1500-2d916ad3ceb0.json`. Only `git_sha` and `elapsed_seconds` moved. Phase C's numbers reproduce exactly. |
| 2 | the same sweep under `randomise_ties=True`, both arms of the comparison | free, ~2 min | **`dumb-ledger`'s diffuse win over `full-ledger` disappears** — 18–7–5 `p=0.043` becomes **13–11–6 `p=0.839`**. See §3. |
| 3 | retro re-score direction under both scoring configs, n=1500, seed 20260809 | free | Of 485 multi-signal ledger entries, **239 are worth more now than at write under `full-ledger`; 0 of 485 under `dumb-ledger`.** See §3. |
| 4 | `tools/reader_coverage.py --reader offline --per-trajectory 20 --customers 2400` | free | **The offline lexicon's coverage collapsed across all four families on the Phase C corpus.** See §1. This is the biggest new fact in this document. |

Run 1 modified `artifacts/runs/sweep-30x1500-2d916ad3ceb0.json` in place (identical results, new
`git_sha`); it was restored with `git checkout`. Run 4's artifact was deleted. **The tree is
unchanged apart from this file.**

### The new fact that reorders everything — the reader went dark on three of four desks

`tools/reader_coverage.py`, offline arm only, 20 customers per trajectory over 2,400, 282
conversations. Denominator is what was **planted**. Threshold 0.2753, the budget-derived top-K cut.

| trajectory → desk | planted | found | ratio | ratio *before* Phase C | best score | crossed |
|---|---|---|---|---|---|---|
| `churn_intent` → **Retention** | 77 | 16 | **0.21** | 0.43 | 0.4486 | **1 / 20** |
| `complaint_escalation` → **Complaints** | 65 | **1** | **0.02** | 0.67 | 0.0485 | **0 / 20** |
| `financial_distress` → Collections | 72 | 33 | 0.46 | 0.74 | 0.7218 | 9 / 20 |
| `life_event` → **Vulnerability** | 68 | 9 | **0.13** | 0.86 | 0.2681 | **0 / 20** |
| **total** | **282** | **59** | **0.209** | | | **10 / 80** |

**Three of four review desks now receive zero cases under the offline reader**, where before Phase C
only Retention was dark. Nothing was tuned to cause this: Phase C authored ~1,500 new customer
sentences, reworded six fragments, gated eleven and added five, all in a pass whose author did not
read the extractor's vocabulary. The 26-regex lexicon was co-developed with the *old* prose. Make
the prose realistic and the lexicon stops working — which is the same result the CFPB benchmark
already published against real customer language (**4 / 112**), arriving now from the other
direction.

This is not a defect to fix. Widening the cues to close a gap discovered by measuring against the
answer key is precisely the tuning the build rules forbid, and `06-phase-c-record.md` §5 already
records the same effect at fragment level. **It is published, and it becomes the claim.**

---

## 1. The claim this entry makes

### The sentence everything else is written to

> **Coverage and retention of evidence are what make an at-risk customer visible to a bank. Ranking
> is not.** Between our two readers, strict recall on real complaint narratives is **0.0357 (4 / 112)
> against 0.8214 (92 / 112)**, and on our own shipping corpus the weak reader leaves **three of four
> review desks receiving zero cases**. Of the nine ranking strategies we test, the two that never
> discard a weak signal rank **first and second** on thin evidence, and both bounded-memory arms lose
> **30–0–0 at p<0.001** — while every arm, ours included, sits inside a **0.113–0.145** band whose
> floor is a seeded random number generator.

### The stage version, fifteen words

> **"Read every conversation, keep every weak signal, and a desk gets a case it would never have seen."**

### Why this claim and not the old one

The old framing led with a ranking result — *the ledger beats per-call detection on diffuse arcs* —
and that result is dead (§2). Worse, it was never worth 100 rubric points even when alive: it was a
three-point spread over a chance floor, on a stratum, at one budget, from one corpus.

The claim above leads with the two facts in this repo that are **large, checkable, and stable under
corpus change**:

1. **The reader gap is 23×** and it is measured on public CC0 data nobody here wrote
   (`benchmarks/cfpb/`, 150 hand-marked narratives, protocol committed before any narrative was
   read). It does not move when our corpus moves, because it does not touch our corpus.
2. **Coverage decides whether a desk exists.** Not a metric — a product fact. Complaints & Redress
   receives 0 of 20 cases under the lexicon. Under the model reader, measured on the previous corpus,
   the dead Retention route went from 0 / 20 to 9 / 20. A judge understands "this desk gets nothing"
   in one sentence; nobody's pulse changes for 0.151 versus 0.141.

And it keeps the originality claim (D-006) intact and now better evidenced than ever: never-discard
is §1's third clause, it is **30–0–0 under both tie-break rules**, and §3 shows it is the *only*
configuration that can make a past conversation worth more than it was.

### How the claim maps to 100 points

| rubric | what carries it |
|---|---|
| Zenon impact **25** | Four desks get cases they currently never receive. FCA Consumer Duty / FG21/1, and the FCA's 2025-04-12 retail-bank review whose verbatim findings describe this product's absence. One purchase, four owners. |
| Technical depth **25** | Nine arms, 144 paired sign tests, a shipped chance control, a pre-registered headline that **died in public** and is re-registered with the death still in the table, an ablation floor that **beat us** and the measurement that explains why, two readers scored on the same gold set at the same grain, two-level answer-key guards. |
| Feasibility **25** | Runs keyless on a fresh clone; no speech recognition anywhere; nine seams, five of them the client's own systems; $1.66 / 1,000 conversations measured; **no outbound contact surface exists at all**; AWS deployed, and the one IAM policy blocking it named rather than hidden. |
| Originality **15** | Incumbents reconcile to current truth; we accumulate and re-score. Now with a structural proof: **239 / 485 vs 0 / 485** (§3). |
| Presentation **10** | Beat order in §5. Losses first. |
| AI judge (engineering quality) | The sweep reproduced byte-identical today. Every rate carries integers. Every loss is printed by the command itself. |

---

## 2. The dead headline, and the re-registration

### What died

The pre-registered headline was `full-ledger` vs `stateless-max` on diffuse recall.

| | record | p |
|---|---|---|
| published, pre-Phase-C corpus | 29–0–1 | <0.001 |
| **Phase C corpus, deterministic tie-break (the default)** | **15–13–2** | **0.851** |
| Phase C corpus, randomised tie-break | 17–9–4 | 0.169 |

**It is dead under both tie-break rules**, which matters: the death is not a tie-break artefact, so
it cannot be argued away the way §3's ablation loss can.

**The cause is measured, not guessed.** `stateless-max`'s diffuse recall went 0.088 → 0.141 while
`full-ledger`'s barely moved (0.154 → 0.151). Before Phase C, a diffuse customer's loudest extracted
signal was *anti*-correlated with their outcome — mean max confidence 0.320 for the outcome group
against 0.329 overall. After, it is correlated: 0.341 against 0.292. **A large part of the
pre-registered win was measuring an opponent the old corpus had crippled.** That is the finding, and
it is worth more than the win was.

### What replaces it

**Primary: `full-ledger` vs `window3-top2` on diffuse recall. Today: 30–0–0, p<0.001, under both
tie-break rules.**

`window3-top2` is chosen deliberately over `stateless-top2` (also 30–0–0) because it is the only arm
bounded in **both** time and capacity — it is the literal negation of never-discard, which is exactly
what D-006 narrowed the novelty claim to. `arms.py` already calls it "the HARDEST opponent it has".
Testing the claim we actually make beats testing the one with the biggest number.

**Co-primary, and we currently fail it: `full-ledger` vs `random-rank` on diffuse recall. Today:
18–8–4, p=0.076, identical under both tie-breaks.**

The claim is declared to hold only if **both** gates pass. As of 2026-08-31 the primary passes and
**the chance gate does not**. That is the entry's declared position and it is reported as a failure,
not omitted. A headline that beats other strategies while not beating a random number generator is
not worth 100 points, and a judge finds that out in one command; binding ourselves to a gate we
currently fail is the only version of this that survives contact.

### The honesty machinery, because a re-registration on a moved corpus is the shape of p-hacking

Four commitments, all mechanical:

1. **The dead headline stays in every published table, permanently, with its p-value.** It is a row,
   not a deletion. `cli.py` still prints it under the label `PRE-REGISTERED HEADLINE`; that label
   changes to `PRE-REGISTERED HEADLINE (2026-08-09) — DIED 2026-08-31, see D-031` and nothing else
   about it changes.
2. **State the weakness out loud:** the new headline was chosen from a matrix that was already
   visible. Several rows would have served (`dumb-ledger` vs `window3-top2` is 29–0–1;
   `long-context-3` vs `window3-top2` is 24–0–6). The mitigation is that we did not pick the biggest,
   we picked the one that matches the stated mechanism, **and** we bound it to a gate we fail.
3. **Pre-register something genuinely unseen at the same time**, so the entry is not only
   re-registering after the fact. `04-plan.md`'s silence-permitting corpus arm — every arc
   conversation currently carries a plant, so "diffuse" means *a weak signal every time*, not
   *silence between signals* — is pre-registered here, before it is generated, as a **declared second
   arm published beside the first, never a substitution**.
4. **Every headline gets its randomised-tie-break record printed beside it, not just the
   pre-registered one.** `cli.py` runs `randomise_ties` for one comparison today. It should run for
   the re-registered headline, the chance gate and the ablation floor. Free, offline, and it is the
   first thing §3 would have caught earlier.

### The `decisions.md` entry, ready to paste

`D-019` and `D-002` are already folded away; **D-031 is the next free number.**

```markdown
### D-031 · 2026-08-31 · The diffuse headline is re-registered against `window3-top2`, with a chance gate we currently fail `ACCEPTED`
Phase C rebuilt the corpus and the pre-registered headline died: `full-ledger` vs `stateless-max` on
diffuse recall went 29–0–1 `p<0.001` to **15–13–2 `p=0.851`** (17–9–4 `p=0.169` randomised, so the
death is not a tie-break artefact). Measured cause, not guessed: before Phase C a diffuse customer's
loudest extracted signal was *anti*-correlated with their outcome (0.320 for the outcome group against
0.329 overall) and is now correlated (0.341 against 0.292) — a large part of the win was measuring an
opponent the old corpus had crippled. **The new primary is `full-ledger` vs `window3-top2` on diffuse
recall (30–0–0, `p<0.001`, both tie-breaks)**, chosen because it is the only arm bounded in both time
and capacity and therefore the literal negation of the D-006 claim — not because it is the largest
record available. **A co-primary chance gate is declared with it: `full-ledger` vs `random-rank` on
diffuse. Today that is 18–8–4, `p=0.076` — we FAIL it, and say so.** The claim holds only if both pass.
Consequences that are not style choices: the dead headline keeps its row in every table forever, its
`cli.py` label becoming `PRE-REGISTERED HEADLINE (2026-08-09) — DIED 2026-08-31`; the randomised
tie-break record prints beside every headline, not only the original; and the silence-permitting corpus
(`corpus/04-plan.md`) is pre-registered NOW, unseen, as a declared second arm published beside the
first. **Rejected:** quietly promoting `stateless-top2` (also 30–0–0) and not mentioning the death —
misconduct, and `earshot sweep` prints all 144 comparisons anyway. **Rejected:** dropping the chance
gate because we fail it, which is the specific dishonesty that makes every other number unbelievable.
**Rejected:** re-registering with no forward commitment; a re-pick after seeing the matrix is only
defensible next to an experiment that has not been run.
```

---

## 3. AT-52 — do decay, corroboration, cross-channel weighting and escalation survive?

**Answer: keep all four. They tie the plain count on recall under a fair tie-break, they buy a queue
that can be ranked at all, and they are the only way the product's stated observable exists. Ship
`dumb-ledger` permanently as a published arm and print both tie-break records for it, always.**

The question is sharp because `arms.py` pre-declared the standard in its own docstring:

> `dumb-ledger` — *"The floor the full ledger has to clear: if it ties the full ledger, every
> mechanism in `memory.py` is decoration."*

### Leg 1 — the loss is real as printed, and it is a tie-break artefact

| `dumb-ledger` vs `full-ledger`, diffuse, 30 seeds | record | p | dumb pooled | full pooled |
|---|---|---|---|---|
| deterministic tie-break (`customer_id`, the default) | **18–7–5** | **0.043** | 0.1664 (377 / 2265) | 0.1506 (341 / 2265) |
| randomised tie-break (independent seeded RNG) | **13–11–6** | **0.839** | 0.1550 (351 / 2265) | 0.1506 (341 / 2265) |

**Why.** `dumb-ledger` produces **5 distinct scores across 1,500 customers**, so **70.8% of its alert
queue is decided alphabetically by customer id** — and customer ids are assigned in generation order.
The full ledger produces **236 distinct scores** and **0.0%** of its queue is tie-decided.

Ranking resolution, mean per seed, printed by the sweep itself:

| arm | distinct scores | queue decided alphabetically |
|---|---|---|
| full-ledger | 236.3 | **0.0%** |
| random-rank | 796.3 | 0.0% |
| hybrid | 212.6 | 0.6% |
| long-context-3 | 52.2 | 7.7% |
| stateless-top2 · stateless-top3 · window3-top2 | 49.0 · 65.4 · 49.0 | 15.7% · 15.8% · 15.8% |
| stateless-max | 15.0 | 42.9% |
| **dumb-ledger** | **5.0** | **70.8%** |

**The full ledger is the only arm in the sweep whose recall does not move at all when the tie-break
rule changes** — 665 / 5796 overall and 341 / 2265 diffuse, both ways. Every other arm moves.

**This is not tuning until it wins, and the git history proves it.** `randomise_ties` and
`random-rank` landed together on 2026-08-30 in `04aa24a`, the day *before* Phase C (`921ec42`)
produced this loss. `dumb-ledger` has existed since 2026-08-09 (`fdcfc79`). The harness predates the
finding, it is applied to every arm symmetrically, the deterministic record stays the default, and
both records are published. Say all of that in the README next to the table, because it is the first
thing a technical judge probes.

### Leg 2 — the mechanisms are the only way retro re-scoring exists

Measured today, n=1,500, seed 20260809, over every multi-signal ledger entry:

| config | entries | worth **more** now than at write | worth less | unchanged | max gain |
|---|---|---|---|---|---|
| `full-ledger` | 485 | **239** | 25 | 221 | 0.1861 |
| `dumb-ledger` | 485 | **0** | 264 | 221 | 0.0000 |

With every multiplier off, the score is `1 − exp(−saturation · n)` in the plain count, which is
concave, so an entry's marginal contribution can only **shrink** as more arrive. *"March is worth
more because of June"* — the submitted brief's stated heart, the demo's centrepiece, and the
observable the build rules require to be **observable rather than asserted** — **cannot happen at
all** under an unweighted count. It is 0 of 485, by construction, not by parameter.

This is a structural argument, not a tuned one. No half-life or bonus value changes it.

### Leg 3 — the cost, stated

- **Recall: the mechanisms buy nothing measurable.** Tied with a plain count under a fair tie-break
  (13–11–6, p=0.839). Under the default deterministic tie-break they *lose* (18–7–5, p=0.043). Both
  records get published, side by side, forever.
- **Whole-portfolio the full ledger is 8th of 9 arms** at the 10% budget (0.115, 665 / 5796) against
  chance at 0.113 (657 / 5796) — one place *worse* than the 7th of 9 the current README reports.
- What they buy: a queue that is rankable at every budget, invariance to the tie-break rule, and the
  only mechanism that makes a prior conversation worth more.

### The falsifier, so this is not an unfalsifiable excuse

Two conditions, either of which removes the machinery:

1. A formulation with **no corroboration, cross-channel or escalation multiplier** that still makes
   an earlier entry's contribution rise. If one exists, the multipliers go.
2. A run at a **larger seed count or on the silence-permitting corpus** where `dumb-ledger` beats
   `full-ledger` on diffuse recall **under the randomised tie-break**. Today it does not (13–11–6).
   If it does, the recall loss is real rather than an artefact and the machinery is decoration.

### What we do not do

Tune half-lives or bonus values until `full-ledger` wins. It is forbidden by
`working-agreements.md` §1, and it would be visible in `git log`.

---

## 4. Where `random-rank` at p=0.076 sits in the narrative

**It is the second sentence of the results section and a beat in the demo. It is never a footnote,
and it is one of the two gates the re-registration binds the claim to (§2).**

The exact sentence, to be used verbatim wherever the results are summarised:

> **On the stratum this entry is built for, the ledger is not yet distinguishable from ranking
> customers at random: 18–8–4, p=0.076 at 30 seeds, identical under both tie-break rules. It moved
> from p=0.345 to p=0.076 when the corpus became more realistic. That is a direction, not a result,
> and we do not claim it as progress.**

**And then the explanation, which is the whole point of leading with coverage.** `random-rank`'s
diffuse recall is 0.132 in a field spanning 0.109 to 0.166. A negative control landing mid-field is
not evidence the mechanism is worthless — it is evidence **there is almost nothing in the stream to
rank**. The offline lexicon finds 59 of 282 planted arc conversations (0.209) on the shipping corpus,
and **1 of 65** complaint conversations. Chance is competitive because the signal is missing, not
because memory does not work.

That is the bridge from the sweep to the claim, and it is why the two must be presented together and
in that order: coverage first, ranking second. Presented the other way round the entry spends the
demo defending a number it cannot defend.

**What would settle it, priced.** A keyed sweep on the model reader — 10 seeds, pinned `prompt_sha`,
about **$10** (item 3 in `state-of-play.md`). It is the single most valuable unspent measurement in
the entry, it is unspent because LLM spend is stopped by the owner's decision and not by a technical
block, and the entry says exactly that rather than implying the experiment was not thought of.

**Do not** describe the p=0.345 → p=0.076 movement as approaching significance. One corpus change.

---

## 5. The demo, 2026-09-07 — beat order and the claim each beat carries

Roughly ten minutes. Ordering logic: **coverage before accumulation, accumulation before the agent,
the agent before the scoreboard.** The sweep arrives *after* the audience already knows why every arm
is crowded near chance, so the weakest evidence is explained rather than defended.

| # | beat | time | the claim it carries |
|---|---|---|---|
| 0 | **The regulator's sentence.** FCA 2025-04-12 retail-bank review, verbatim on screen. | 0:30 | The absence this product fills is described by the regulator, not by us. *(impact)* |
| 1 | **One arc, read as one relationship.** `CUST-0102` from `06-phase-c-record.md` §8 — a complaint in April nobody actions, chased in June and July, and "this is the fourth time I've called" landing in an arc that genuinely holds four contacts, each with a broken undertaking behind it. | 1:30 | The data is a relationship, not four scenes sharing a customer id — and the answer key was authored before the prose. *(depth, feasibility)* |
| 2 | **Two readers, one conversation, side by side.** | 1:30 | **Coverage is the product.** On screen: 4 / 112 vs 92 / 112 on real CFPB narratives; and on our own shipping corpus the lexicon finds 59 / 282 planted arc conversations and **1 of 65** complaint ones. |
| 3 | **Three dark desks.** The desk screen under the offline reader: Complaints **0 / 20**, Vulnerability **0 / 20**, Retention **1 / 20**, Collections 9 / 20. Then the model reader. | 1:00 | A desk exists or does not exist depending on the reader. That is a product decision, not a metric. **Honesty beat, on the screen:** the model half of this comparison was measured 2026-08-29 on the *previous* corpus (n=20 per trajectory, $0.4260) and has not been re-measured since Phase C. The direction is not in doubt; the magnitude on this corpus is **unmeasured**, and costs about $0.45. |
| 4 | **Accumulation and retro re-scoring.** `earshot demo`: four weak conversations, the ledger crosses, then the retro panel — what each quote scored *then*, what it supports *now*. | 1:30 | **Never-discard, and the past re-read.** 239 of 485 multi-signal entries are worth more now than at write; under an unweighted count it is 0 of 485. |
| 5 | **The agent works one case.** Tools, bounded loop, cited evidence, owning team, and the `POST /cases/{id}/reviews` body it *would* send and did not. | 1:30 | Track A: an agent with tools, structured decisions, mandatory evidence, a human in front of every action. On screen with the losses: 22 / 50 verdicts, 36 / 49 routing (2 wrong, 11 declined), 0 / 50 evidence repairs, $0.0295 per case, and a queue that is ~90% false alarm. **Say the sentence: the investigator is a router and an audit trail, not a filter.** Both figures are corpus-historical — pre-Phase-C — and the screen says so. |
| 6 | **The scoreboard, losses first.** | 1:30 | This entry can be checked, and we did the checking. *(depth, AI judge)* |
| 7 | **Deployment, and what is inert.** Nine seams, five the client's own. No ASR anywhere. No outbound surface anywhere. AWS deployed and blocked on one IAM policy, named. | 0:45 | Feasibility, with the blockers said out loud. |
| 8 | **Close.** Repeat the claim. One ask: the $10 keyed sweep that settles the chance gate. | 0:20 | |

**Beat 6 has its own internal order, and it is not negotiable — the losses come first:**

1. The chance control and where we sit against it: **18–8–4, p=0.076. Not yet beaten.**
2. The pre-registered headline that **died**: 15–13–2, p=0.851 — and the measured cause (the old
   corpus crippled the opponent; mean max confidence for diffuse outcome customers went from
   anti-correlated 0.320/0.329 to correlated 0.341/0.292).
3. The re-registered headline: **30–0–0 against both bounded-memory arms, p<0.001, under both
   tie-break rules.**
4. **Our own ablation floor beating us** — `dumb-ledger` 18–7–5, p=0.043 — and the two measurements
   that answer it: 70.8% of its queue decided alphabetically, and 13–11–6 p=0.839 once ties are
   randomised.

**If time runs short, cut beats 1 and 7. Never cut beat 6.** The losses are the entry's strongest
asset and the only thing on the list a competitor will not also have.

### One prerequisite that must land before the demo, and it is free

`earshot demo --customers 3000` currently opens its case on two false fires. Verified today:

```
conversation 2  heard: "Postcode's the same one, ends 7QB."           cue l-separate:false-fire
conversation 3  heard: "Would - lose the interest I've already earned?"  cue l-statpay:false-fire
```

Two of the four quotes carrying the accumulation moment are the extractor firing on a **security
answer** and on an unrelated question. The mechanism is real — 7 of 132 thin-evidence customers with
an outcome are caught by the ledger while per-call detection never fires, against 10 the other way,
and the command prints both — but this *instance* is the single most-looked-at string in the entry
and it reads as a bug. `06-phase-c-record.md` §7 item 4 predicted exactly this and left it as the
owner's call.

**Decided: make `demo` prefer a customer whose crossing is carried by seeded signals.** It is free,
offline, and it does not breach separation — D-009 puts `cli` on the evaluation side, which may read
the answer key. Teaching `extract.py` to skip the verification answer *would* breach it and is
refused.

---

## 6. Kill list — sentences that are no longer supportable

Line numbers are as of `921ec42`. **False** = contradicted by today's run. **Stale** = the number
moved. **Underclaim** = we are now more right than the sentence says.

### `README.md` — the source of record, and the worst affected

| line | sentence | verdict | replacement |
|---|---|---|---|
| 68 | "5,834 outcome customers" | stale | **5,796** |
| 70 | "in about 70 seconds" | stale | 113 s measured today |
| 72–75 | "Regenerated 2026-08-30 … pools widened from 8/8/4/4 to 14/14/14/14" | stale | superseded by Phase C, 2026-08-31 |
| 80–83 | "of the 32 fragments … it finds **1**. Of the original 24 it finds 21." | unverified | replace with the directly measured **59 / 282 (0.209)** planted arc conversations found, per family — it is the number a reader actually cares about |
| 91–101 | the entire nine-row "floor" table | stale | every row moved; `full-ledger` 0.115 (665 / 5796), `random-rank` 0.113 (657 / 5796), `stateless-max` 0.145 (841 / 5796) |
| 103 | "**seventh of nine** on whole-portfolio recall" | stale | **eighth of nine** at the 10% budget |
| 110 | "the ledger beats **every** baseline at 30 seeds" | **FALSE** | it **ties** `stateless-max` (15–13–2) and **loses** to `dumb-ledger` (7–18–5) |
| 112–120 | the diffuse comparison table, all seven rows | stale | 29–0–1→15–13–2 · 26–2–2→**30–0–0** (×2) · 17–11–2/0.345→**18–8–4/0.076** · hybrid 26–1–3→24–1–5 · top3 20–4–6→21–1–8 · long-context 20–3–7→23–2–5 |
| 123–124 | "Diffuse recall is 0.154 (359 / 2332) against chance at 0.128 (298 / 2332)" | stale | 0.151 (341 / 2265) against 0.132 (299 / 2265) |
| 131–133 | "`stateless-max` scores 0.088 on diffuse … concentrating on the loudest call is *actively wrong*" | **FALSE** | 0.141 against chance's 0.132. This sentence *was* the crippled-opponent artefact, and killing it is the finding |
| 139–146 | the concentrated table | stale | `stateless-top2` 0–29–1→1–28–1; and only **three** arms now beat us 0–30–0, not four |
| 148 | "**The ledger beats chance here**" (concentrated) | **FALSE** | 16–12–2, **p=0.572**. It does not |
| 158–159 | the two budget-ordering lines | stale | 1%: `long-context-3` leads, full-ledger 6th. 10%: full-ledger **8th** |
| 162 | "`random-rank` is last at every budget" | **holds** | verified at 1 / 2 / 5 / 10%. Keep |
| 170 | tie-shares "`dumb-ledger` 65.9%, `stateless-max` 21.9%, full ledger 0.0%" | stale | **70.8% · 42.9% · 0.0%**, and add the distinct-score column (5 · 15 · 236) |
| 174–180 | the tie-break headline table (29–0–1 / 28–0–2) | stale | 15–13–2 / 17–9–4 — and the conclusion inverts: it no longer "survives both ways" |
| 184–186 | "**Aggregating a few conversations beats aggregating one** … Supported at p<0.001" | **FALSE** | the arm that aggregates one ties us on diffuse and beats us on the portfolio |
| 188–189 | "That unbounded memory beats a cheap bounded window is **unproven**" | **UNDERCLAIM** | 30–0–0, p<0.001, both tie-breaks, on diffuse. Say the two-sided truth: proven on diffuse, **lost** on concentrated (1–28–1), not proven whole-portfolio (9–17–4, p=0.169) |
| 191–194 | "every arm crowded between 0.109 and 0.138" | stale | **0.113 and 0.145** |
| 201 | "runs **84** pairwise tests" | stale | **144** |
| 207–209 | the decay-vs-confidence ablation note | unverified | not re-measured on this corpus, and it must now be stated against `dumb-ledger`'s 5 distinct scores |
| 219–231 | the pinned 400-customer diagnostics — extractor recall **0.659 (492 / 747)**, outcome rate 12.75%, decoy rates 1.4% / 49.7% | **stale, worst offender** | from a corpus that no longer exists (`660dca4`). Phase C measured **0.2285 (617 / 2700)** at n=1500 and decoy rates 0.0191 / 0.4871. The headline extractor figure is off by roughly 3× |
| 256 | "It does not rescue the 0.659 on our own prose" | stale | same |
| 338–344 | the retention-dead table (churn 0.40 / complaint 0.71 / life 0.76 / distress 0.77) | **all four FALSE** | measured today: **0.21 / 0.02 / 0.13 / 0.46** |
| 346–355 | "Not one of 325 can cross. **The Retention desk never receives a case.** … It is a pass-B gap: the extractor cues for churn fire in fewer of the conversations where churn was planted" | **too narrow** | the conclusion is now much larger: **three** desks are dark, not one, and it is not a churn-specific gap. Rewrite as the general result |
| 360–375 | the two-reader coverage table | stale + unmeasured | every lexicon column moved; the model column was never measured on this corpus and must be labelled corpus-historical |
| 382–386 | "of the 240 customers … 25 have a real outcome and 215 do not" | unverified | not re-measured post-Phase-C |
| 405–417 | the streamed-demo table | corpus-historical | recorded 2026-08-28; `06-phase-c-record.md` §6 records the offline Northwind stream going 1 crossing → 0 after Phase C |

### `docs/ORIENTATION.md`

| line | sentence | verdict |
|---|---|---|
| 69 | "the offline lexicon finds only 1 of the 32 new fragments … At 3,000 it finds 6 of 150" | stale — though the 3,000-customer demo **does** still work (7 of 132 verified today) |
| 146 | "the full ledger beats **every** competing strategy" | **FALSE** |
| 154–155 | "17–11–2, `p=0.345`" | stale → 18–8–4, p=0.076 |
| 157–158 | "ranks **7th of 9**, recall 0.119 against chance at 0.109" | stale → **8th of 9**, 0.115 against 0.113 |
| 158–159 | "loses 0–30–0 to **four** different arms" | stale → **three** |
| 163–164 | "**Aggregating a few conversations beats aggregating one** … That is supported." | **FALSE** |
| 165 | "unbounded memory beats a cheap three-conversation window is unproven" | **UNDERCLAIM** |
| 167–169 | "1 of 32 … crowds between 0.109 and 0.138" | stale |
| 175–181 | the agent table | corpus-historical; label it |
| 209, 215 | "827 collected, 817 passing", "650 colour pairs" | inconsistent with `handover.md`'s 634 and 812 — re-count, and put the number in one place |

### `docs/impact/onepager-accuracy-cost-latency.md`

| line | sentence | verdict |
|---|---|---|
| 101–104 | the four-row diffuse table (29–0–1 · 26–2–2 · 26–2–2 · 17–11–2) | **all four stale** |
| 110–111 | "7th of 9 … 0.119 (695 / 5834) against chance at 0.109 (633 / 5834) and a ceiling of 0.138" | stale on every figure |
| 113–116 | "these records reversed when the corpus changed" | true, but now understates it — a bigger reversal has happened since |
| 118–121 | "finds **1 of the 32**" | stale |
| 122+ | "A tenfold change in that parameter does not swing the comparison, on either corpus" | must be restated against the re-registered opponent; `06-phase-c-record.md` §4 has the post-fix swing (+4 / +8 / +9) against `stateless-top2` |

### `docs/impact/onepager-path-to-production.md`

| line | sentence | verdict |
|---|---|---|
| 127–131 | "17-11-2, p=0.345 … 7th of 9 arms, one point above chance (0.119 vs 0.109)" | stale numbers, **right conclusion** |
| 135–140 | "the value proposition that is *claimed but unproven* is that unbounded memory beats a three-conversation window" | **UNDERCLAIM** — 30–0–0 on diffuse. But the surrounding paragraph, *"the value proposition that is measured is coverage and triage"*, is **already the framing this document decides on.** Promote it; do not rewrite it |

### `docs/impact/onepager-use-case.md`

| line | sentence | verdict |
|---|---|---|
| 54–63 | the "moment that shows it" table (0.10 / 0.29 / 0.66 / 0.80) | not produced by any run, and Phase C reworded *"my husband passed away in June"* to *"passed away earlier this year"*. Regenerate from `earshot demo` or label illustrative |
| 79–81 | "Routes to the right desk 36 / 49 correct" | corpus-historical; label it |
| 94–97 | "**Whether unbounded memory beats a cheap three-conversation window is unproven** … not yet shown" | **UNDERCLAIM** — the one place the entry is currently harder on itself than the evidence requires |
| 112–114 | "Current to 2026-08-30" | stale |

### `docs/architecture/architecture.md` — **ask-first, flagged not edited**

| line | sentence | verdict |
|---|---|---|
| 203 | "Measured 2026-08-30: full-ledger vs chance on diffuse arcs is 17–11–2, `p=0.345`" | stale → 18–8–4, p=0.076 |
| 211–213 | "the ledger beats **every** competing arm … `26–2–2` against each … 7th of 9 … 0.119 against 0.109" | **FALSE** and stale |
| 217–219 | "finds 1 of 32 … crowds every arm between 0.109 and 0.138" | stale |
| 224–225 | "what never-discard buys over a cheap bounded window is currently unproven" | **UNDERCLAIM** |

### The three sentences to grep for and kill everywhere

1. **"On diffuse arcs the ledger beats every baseline."** It ties one and loses to one.
2. **"Aggregating a few conversations beats aggregating one."** The pre-Phase-C corpus produced that
   sentence; the fixed corpus refutes it.
3. **"Whether unbounded memory beats a bounded window is unproven."** Both directions are now
   measured: won on diffuse 30–0–0, lost on concentrated 1–28–1, unproven whole-portfolio.

`docs/ops/state-of-play.md` and `docs/ops/handover.md` are pre-Phase-C throughout and are rewritten
rather than patched — they are maintain-freely files.

---

## 7. What I was least sure about

**1. Whether a re-registration on a corpus that moved underneath it is defensible at all.** My answer
is that it is defensible only when the death is published as loudly as the replacement *and* an
unseen experiment is pre-registered at the same time — hence the four commitments in §2. If that
reads as insufficient, the fallback is to publish **no** ranking headline and lead entirely on the
CFPB reader benchmark, which is genuinely pre-registered (`benchmarks/cfpb/PROTOCOL.md`, committed
before any narrative was read) and untouched by any corpus change. I judged that too austere — it
throws away a clean 30–0–0 — but it is the honest floor if anyone disagrees.

**2. The lead claim's second half rests partly on a stale measurement, and money would fix it.** The
"three dark desks" beat is fully measured for the lexicon arm (today, this corpus). The model arm
that revives them was measured 2026-08-29 on the *previous* corpus. The direction is not in doubt —
0.0357 vs 0.8214 on CFPB is corpus-independent — but the magnitude on the shipping corpus is
unmeasured, and it costs about **$0.45**. If exactly one dollar of spend is ever released, spend it
here and not on the $10 sweep; it repairs the entry's *lead* claim rather than a gate the entry
already admits it fails.

**3. Whether leading with coverage reads as retreat from the originality claim.** I judge it does
not — never-discard is beat 4, it is 30–0–0 under both tie-break rules, and §3 gives it a structural
proof it never had. But a judge hunting for one killer performance number will not find one, and
that is a real cost of this framing which I am accepting deliberately.

**4. Whether §3's tie-break argument will read as motivated.** It is a genuine measurement and the
git history clears it (`04aa24a`, 2026-08-30, one day before the loss existed) — but "we lost, then
changed the tie-break rule, then tied" is a sentence a hostile reader can construct. The defence has
to be *in the README next to the table*, not in this file: harness predates the finding, applied
symmetrically to all nine arms, deterministic stays the default, both records always printed.

**5. Which mechanism inside `memory.py` actually buys the ranking resolution.** The README's old note
attributes it to decay rather than confidence weighting, and that was measured on a corpus that no
longer exists. `dumb-ledger` switches off five things at once, so §3 justifies the *set*, not any
member of it. A per-mechanism ablation of the tie-share — `mechanism_ablations()` already exists in
`arms.py` — is free, offline, and would let the entry say which one earns its keep instead of
defending all four together. **It is the single cheapest open item in this document.**
