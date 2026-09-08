# Prompt for the next conversation

Copy everything below the line into a fresh conversation.

---

You are the **judge and orchestrator** for a hardening pass on the Genesis 2026 pitch. You do not
write the research yourself — you **delegate, judge, decide, and hold the thread.** Tier your agents:
**opus** for adversarial attack and judgement, **sonnet** for scoped research and synthesis, **haiku**
for mechanical inventory and web search. Do not spawn an agent for work that is cheaper done directly.

**Spend discipline is a hard requirement.** Cap web searches per agent explicitly in the prompt you
give it. Use haiku for anything search-heavy. Take agents' returned summaries as your working material
and **do not read their full reports unless a specific claim needs checking** — reading long reports
is where budget actually goes. Never run more than four agents at once.

## Read first

Everything in `docs/credit-card/` — five files, in this order: `00-READ-THIS-FIRST.md`,
`01-THE-STORY.md`, `02-THE-DEMO.md`, `04-ALTERNATE-STORIES.md`, then `03-REFERENCE.md` (long; skim
sections 2, 3 and 5).

Context you need: the gate is **2026-09-11**, judges are **Venkat (CEO)** and **Farhan (COO)**, both
finance-background, both commercially minded rather than technical. Market is the **United States**.
The product is a conversation signal layer that reads 100% of a card issuer's customer conversations
and accumulates them into a per-customer ledger that re-scores over time; the headline artefact is a
**conversation attrition score**. `04-ALTERNATE-STORIES.md` argues that **pre-delinquency is worth
7–10× more per event than attrition** and may be the better story — that recommendation is live and
unresolved.

## Mission 1 — defend the score. This is the priority.

**The question that has not been answered anywhere in the folder, and it is the most dangerous one
available to a numerate executive:**

> *"Your score depends on an LLM reading a transcript. LLM outputs are not reproducible, and the
> confidence values are not real probabilities. What happens when that model is retired, or when a
> better one comes out and you switch? Does my whole feature change under me? Do I have to re-validate
> everything? How is this a controlled input to a regulated model?"*

Attack this properly. The honest structure of the problem is:

- The **score arithmetic** is deterministic Python — same signals in, bit-identical score out, and it
  is unit-tested. That half is genuinely reproducible.
- The **inputs** are not. Signal type, the verbatim quote, and above all the **model-emitted
  confidence value** come from an LLM, which is version-dependent and not bit-stable. **The score
  inherits the reading's instability, and the folder currently glosses over this.**
- The model-emitted `confidence` float is the weakest link in the entire design. There is published
  literature showing verbalized/self-reported LLM confidence is poorly calibrated — find it, and use
  it *against* our own design before someone else does.

**Candidate defences to stress-test — do not accept any of them without attacking it first:**

1. **Three-tier separation in the bank's own vocabulary.** The extractor is a *feature generator*, the
   ledger is a *deterministic transformation*, the host propensity model is the *decision model* —
   three tiers, three different change-control regimes under SR 11-7. Does that hold up to a real model
   risk function?
2. **Stop trusting model-emitted confidence.** Options: collapse to a binary "quoted signal present";
   or calibrate against a held-out answer key and store the *calibration map* rather than the raw
   number; or derive confidence from self-consistency across N samples or agreement between two models.
   **Which is strongest, and what does each cost?** Judge this — it may be a build recommendation, not
   just a talking point.
3. **Reproducibility by fingerprint, not by determinism.** Model id, `prompt_sha` and extractor version
   are already in the cache key, so a score is reproducible *given a pinned fingerprint*. Is "every
   score carries the exact model and prompt fingerprint that produced it, and re-running that
   fingerprint reproduces it" a sufficient answer for an auditor? Where does it fail?
4. **A documented re-baselining protocol for model migration** — run old and new readers over a frozen
   benchmark, measure signal-level agreement and score-level rank correlation, re-fit calibration,
   report the delta, then champion/challenger on the host model. **Frame model change as a planned,
   documented, routine event rather than a catastrophe.** Is that credible to a COO?
5. **Rank stability, not value stability.** The consuming use is top-decile ranking, not a calibrated
   probability, so the metric that matters is top-K overlap and rank correlation across model versions
   — a much easier and more *honest* bar because it matches the actual use. Interrogate whether this is
   rigour or a dodge.
6. **The frozen benchmark is the invariant; the model is replaceable.** Probably the strongest answer
   available, and **we have already demonstrated it**: the repo contains a measured two-model
   comparison on the same 282 conversations — Nova Lite vs Claude Haiku 4.5, coverage 181/282 vs
   177/282, cost $0.0982 vs $1.58 per 1,000, and 10 non-verbatim quotes vs 0. *"You're asking what
   happens when the model changes — we've already changed it and measured it"* is a demonstrated
   answer, not a promise. **Verify those figures in the repo before relying on them**, then judge how
   hard this can be pushed.

Also required: **do not overclaim determinism.** Model risk regimes require auditability and
repeatability of *process*, not bit-identical outputs, and claiming more than is true is worse than
explaining the regime honestly. Work out where that line sits.

## Mission 2 — the Gen AI landscape

Who else is walking these lines, and what does that mean for our differentiation and our pricing?
Cover: conversation-intelligence incumbents adding LLMs (Verint, NICE Enlighten, CallMiner, Genesys,
Observe.AI, Level AI); cloud-native (AWS Contact Lens / Amazon Connect, Google CCAI Insights,
Microsoft/Nuance); banking-specific AI (Personetics, Zest AI, Scienaptic, Salesforce Financial Services
Cloud, nCino); and the "unstructured data into the feature store" pattern (Snowflake Cortex,
Databricks). Also: **is anyone doing accumulation across conversations over time, or is everyone doing
per-interaction classification?** That distinction is our entire claimed differentiator — **verify it
or break it.**

Then the governance discourse: what regulators and the industry are currently saying about GenAI in
model risk management, LLM-derived features, and validation of non-deterministic components. NIST AI
RMF, any OCC/Fed/FFIEC commentary, and how banks are actually handling LLM model-version churn today.

**Cap this research tightly.** One haiku agent for search-heavy landscape work with a hard search
limit, one sonnet agent for the governance discourse. Do not let it sprawl.

## Mission 3 — make the stories stronger

Run an **opus** adversarial pass on `01-THE-STORY.md` and `04-ALTERNATE-STORIES.md`, in the voice of
Venkat, Farhan, and a hostile ex-card-book propensity modeller. `03-REFERENCE.md` §6 records the eight
kill shots from the last such pass and what changed — **read it so you attack new ground rather than
re-finding KS-1 through KS-8.**

Specifically unresolved and worth attacking:
- The `04-ALTERNATE-STORIES.md` recommendation to switch to **pre-delinquency**. Is the 7–10× claim
  sound? Its **$5,000 per avoided charge-off is an unverified estimate of net loss after recoveries** —
  verify or correct it. Does pre-delinquency survive T3 (what consumes the score when the customer is
  not calling) as cleanly as claimed?
- Six of the thirteen alternate stories have **no verified anchors at all** (deposits, scams, mortgage,
  SMB, CLI, CLD). If any of those is going to be recommended, it needs figures.
- Whether the **two-desk pairing** (pre-delinquency as beat A, attrition as beat B) is genuinely
  stronger than one score, or just a compromise that muddies the pitch.

## Rules — these are load-bearing

- **Every non-obvious claim gets an inline source and an absolute date.** No "recently".
- **Every rate carries its denominator** — `4 / 112`, never "3.5%".
- **Never invent a client's internal number** (their attrition rate, book size, save rate, CAC, model
  lift). Published anchors and client-supplied inputs only, tagged as such.
- **Every agent report ends with `## Could not verify`.** Those lists are load-bearing, not decoration.
- Read `CLAUDE.md` and `docs/ops/working-agreements.md` before changing anything, and
  `docs/ops/decisions.md` before arguing for something already settled.
- **`isolation: "worktree"` is broken in this repo** — it checks out an obsolete tree. Never run two
  file-writing agents at once; have agents write to a scratchpad and do repo edits yourself.
- **RTK is not installed here.** Use plain `git`, `gh`.
- Do not modify anything in `docs/sources/` — that is the committee contract and is never-edit.

## Deliverables

1. **`docs/credit-card/06-DEFENDING-THE-SCORE.md`** — the answer to Mission 1. Must contain: the honest
   statement of what is and is not reproducible; the three-tier governance framing; **a recommendation
   on whether to keep, replace or calibrate the model-emitted confidence value**, with the build cost;
   the written model-migration protocol; and **the three or four sentences Ravi actually says out loud**
   when Venkat asks the question. Lead with those sentences.
2. **`docs/credit-card/07-LANDSCAPE.md`** — Mission 2. Who does what, where we are genuinely different,
   where we are not, and what it implies for pricing and for the "not a moat" concession already in the
   story.
3. **Surgical patches** to `01-THE-STORY.md` (objection playbook and beat 4) and `03-REFERENCE.md`
   (§2 calibration, §3 governance). **Patch, do not rewrite** — and record what changed and why, the
   way `03-REFERENCE.md` §6 records the last pass.
4. **A verdict on pre-delinquency vs attrition**, with the corrected charge-off arithmetic. One
   paragraph, stated plainly, in `00-READ-THIS-FIRST.md`.

**Start by telling me in two lines what you are going to do, then do it.** Report what broke, what you
could not verify, and what you decided — not a summary of how many agents you ran.
