# Decisions

Why things are the way they are, and what not to re-open. One entry per decision, newest first.

**Format:** date · what was decided · why · what we rejected. Status is `ACCEPTED`, or `SUPERSEDED BY
<id>` — superseded entries are cut to a single line rather than deleted, so the record stays honest
without the file growing. If an entry no longer affects any current choice, delete it; git remembers.

**This file exists so a fresh session does not re-litigate settled ground.** If you are about to argue
for something listed under "rejected", read the reason first.

---

### D-021 · 2026-08-10 · The model reader is built and instrumented, and stops at the number `ACCEPTED`
`Extractor` in `extract.py` had exactly one implementation and the docstring had promised a second
"later" since the file was written. `extract_model.py` is that second implementation. Four
properties are not negotiable and each is pinned by a test: **stateless** — the prompt carries the
turns and the channel and nothing else, so the model cannot tell which customer or which day it is
reading, which is what keeps the memory ablation meaningful; **it never sees the answer key** — it
is on the discovered separation surface and the prompt was authored from what each construct
*means*; **a quote is verbatim or the signal is dropped**, sliced out of the turn rather than copied
from the reply; **cost and latency accumulate per call**, which is what finally makes cost per 1,000
conversations measurable.

**No accuracy number for it exists, deliberately.** There was no key in the environment it was
built in, so it has never been run. Everything is arranged so that ONE keyed run of
`benchmarks/cfpb/steps/05_score.py --extractor model` produces the comparison and records its cache
for keyless replay — the same record-then-replay path the two committed live investigations use.
**Rejected:** a placeholder, an estimate, or an extrapolation from the investigator's costs. A
number in a document has to have been copy-pasted from a command's output; anything else is the
failure mode this project has retracted twice already. **Also rejected:** making the model reader
the default. D-004 stands — everything runs with zero keys, and nothing reaches for the network
unless the caller asked for it by name.

### D-020 · 2026-08-10 · The history-length experiment goes first, overriding AT-43's pre-registered consequence `ACCEPTED`
**This overrides a pre-registration, so it is written down as an override rather than absorbed.**
`benchmarks/cfpb/PROTOCOL.md` §6 said a score below 0.30 sends *"work 3 (regrounding the corpus
lexicon in CFPB phrasing)"* ahead of the reviewer queue. It scored 0.0357. We are not doing that next.

Two things came out after the number that the pre-registration could not have known:

1. **It named the wrong file.** §6 assumed the only fix for "the reader fails on real language" was to
   make the *corpus* more real. AT-43's own per-cue table says otherwise: 24 of 26 cues in
   `extract_lexicon.py` never fired, so the defect is in the **reader's cue coverage**, not in the
   realism of the planted prose. D-019 quietly retargeted the work to the extractor without flagging
   the substitution; that substitution is correct on the evidence but it was a judgement call, and
   calling it "the pre-registered consequence" in a commit message was wrong.
2. **The blocking experiment does not need real language at all, only more of it.** Fragments are
   planted *without replacement* (`corpus.py`, `used` set), so the scarcest pool — 4 fragments — caps
   how many signals any arc can carry. That, not realism, is why the corpus cannot pose the question
   `window3-top2` raises. Widening pools with newly authored fragments unblocks it; regrounding them
   in CFPB phrasing is a separate and much more expensive project, and working-agreements §9 says
   corpus realism scores close to nothing.

So the order is: **history-length experiment → reviewer queue → cost/latency**, with cue regrounding
bounded and deferred. The justification is that `stateless-top2` and `window3-top2` beating the ledger
on its own pre-registered stratum is a larger threat to the entry than the reader's vocabulary, it
carries depth (25) and originality (15), and the result publishes either way.
**Rejected:** following §6 literally. A pre-registration binds you against choosing a *result* after
seeing the data; it does not oblige you to do work its own evidence has since shown to be aimed at the
wrong file. **Also rejected:** doing this silently — the override is the kind of thing that looks like
integrity drift later, so it is dated, reasoned and attributable here.

### D-019 · 2026-08-09 · The extractor is regrounded in real phrasing `SUPERSEDED BY D-020`
The measurement stands and is the reason any of this is known — 0.0357 strict recall (4 / 112) on real
CFPB narratives against 0.681 (496 / 728) on ours, written up in `benchmarks/cfpb/`. What D-020 overturns
is only its scheduling conclusion, and its claim that the ordering followed automatically from the
pre-registration.

### D-018 · 2026-08-09 · A static guard is the first net; the behavioural band is a partial backstop `ACCEPTED`
**Amended after round 6, which showed the original wording overclaimed.** The band pins the
EXTRACTOR's recall, not the system's honesty. A reviewer put a leak into `memory.py` that substituted
the generator's true planted strength for the extractor's confidence: the band moved by nothing at all
(0.6813, to four decimals) while the published headline went 134/780 to 143/780 and p=0.008 to p=0.004.
A decoy-only leak is likewise free, because decoys appear in neither term of the recall fraction, and a
partial leak tuned to `share=0.4` sits inside the band's headroom. The band is also measured on ONE
dataset, which D-007 forbids for anything published. It remains worth having and it is not the
guarantee the previous wording claimed. What is still open: a second pinned behavioural quantity
covering the rest of the surface, and measuring the band across the same seed base `sweep` uses.

The static scan still cannot be completed — `sys.modules`, `getattr` on the package, `__import__` on an
assembled name and reading the file as text all pass it, verified. **Rejected:** lengthening
`FORBIDDEN_IDENTIFIERS` until the current attack list passes, which is a guard tuned to the attacks
someone thought of and described as proof; and, now, describing any single measured quantity as "the
guarantee" — round 6 built exactly that mistake one file away, in the commit that wrote this down.

### D-017 · 2026-08-09 · Numbers are quoted from the command's own seed base, never an ad-hoc script `ACCEPTED`
Our 30-seed figures were computed in a scratch script on seeds `7000..7029` while `earshot sweep
--seeds 30` uses `20260809+`. Every triple was wrong, and one of them inverted a conclusion: the
ledger does not "match" `stateless-top2` on the pre-registered stratum, it loses to it (`7-21-2`,
`p=0.013`). This is the same defect as round 4's unreachable p-values, committed inside the fix for
it. **Rejected:** keeping the scratch numbers and noting the seed set — if a command cannot print it,
it is not a published number.

### D-016 · 2026-08-09 · Both arc strata are published, always `ACCEPTED`
The ledger wins on diffuse arcs (`p=0.008`) and loses on concentrated ones by a comparable margin
(`p=0.039`; 3-25-2 at 30 seeds). `evals.py` computed both from the start and `sweep` printed only the
win. The result is a **trade** — depth of aggregation buys thin evidence and costs loud single calls —
and stated that way it is the argument for running memory alongside per-call detection rather than
instead of it. **Rejected:** reporting the win and describing the loss as "out of scope"; it is the
same size, from the same run, and a judge finds it by printing a dict the code already builds.

### D-015 · 2026-08-09 · `stateless-top2` is the baseline of record, even though it beats us `ACCEPTED`
Summing the two loudest calls — two floats, no ledger, no never-discard, no retro re-scoring — takes
147/780 diffuse arcs against the full ledger's 134. Our published baseline was a running *max*, which
loses to anything that adds a second call, so "memory beats detection" was really "several calls beat
one call". The arm is now shipped and published. What this costs is the simple version of the claim;
what it buys is the real question — whether never-discard pulls ahead as histories lengthen, which our
corpus (3.5 conversations per customer) cannot currently answer. **Rejected:** keeping `stateless-max`
as the only baseline and describing top-2 as "future work".

### D-014 · 2026-08-09 · Adversarial review runs until a round is empty, not a fixed number of times `ACCEPTED`
Four rounds, four sets of real defects, and round 4 found more than the previous three combined —
including an import guard that could be walked past with `from earshot import corpus`, a groundedness
metric still structurally pinned at zero after round 2 supposedly fixed it, and two published p-values
no command could produce. Each round's fixes create the next round's surface. **Rejected:** declaring
the code reviewed after three rounds; the defect rate had not fallen, which is the only signal that
means anything.

### D-013 · 2026-08-09 · The board tracks what we build, not what we owe the committee `ACCEPTED`
Tickets whose purpose was to chase access or explain ourselves were removed. Asking for API keys is a
conversation, not a work item. **Rejected:** a "blockers" epic — it made the board read as written for
an audience, which is the tell that it is not being used.

### D-012 · 2026-08-09 · Nothing is Resolved until a second person has reviewed it `ACCEPTED`
A weekend of work that would have been marked Done contained a rigged demo threshold, an answer-key
leak, a no-op comparison arm and an unenforced cost cap. "Done" would have been false on the merits,
not merely optimistic. Consequence: the board runs at high In-Progress until Namit and Ishant review.

### D-011 · 2026-08-09 · The cost cap bounds cumulative spend, not a single call `ACCEPTED`
A pre-flight estimate cannot bound a call that costs wildly more than every prior one. Stated as a
limit, with a test that documents the breach case. **Rejected:** iterating the estimator until an
adversarial test passed — it would have produced a cap that was still not a cap, with better wording.

### D-010 · 2026-08-09 · Synthetic data is a requirement of the measurement, not a fallback `ACCEPTED`
Searched public data thoroughly (regulators, ombudsmen, HuggingFace, Kaggle, LDC, dialogue and
agent-memory benchmarks). Nothing public has repeated contacts from the same identifiable customer over
time in financial services with an outcome label. More importantly, our experiment needs to know how
much evidence was placed in each conversation *before it was written* — no real dataset can supply
that. We adopt CFPB (3.8M real complaint narratives, public domain) to benchmark the **reader**.
**Rejected:** stitching real complaints into invented customer histories — incoherent people, and it
destroys the answer key that makes the measurement possible. Full findings: Jira **AT-38** comment.

### D-009 · 2026-08-09 · The evaluation layer may read the answer key; nothing else may `ACCEPTED`
Three-way boundary: the corpus side *authors* truth, the evaluation side (`evals`/`sweep`/`cli`)
*reads* it because scoring is what it does, everything else must never see it. The exemption list is
three files, commented per entry, with a test that fails if it grows.

### D-008 · 2026-08-09 · Guard the answer key at two levels `ACCEPTED`
An import guard alone could never have caught the leak we actually had — a ground-truth field handed to
the agent's tools as a plain float. `latent_risk` (how much was planted in conversations) and
`financial_state` (what the account looks like) are now separate fields.

### D-007 · 2026-08-09 · Nothing is published from a single dataset `ACCEPTED`
Our first headline came from one run with 39 outcome customers; every "finding" was a one-customer
difference. `earshot sweep` is the only source of quotable numbers, every rate carries its denominator,
and the diffuse-stratum comparison is the pre-registered headline.

### D-006 · 2026-08-09 · The novelty claim is narrowed to never-discard plus retro re-scoring `ACCEPTED`
The submitted wording — "none of them keep a customer-level memory that accumulates and re-scores" — is
false as of 2026-05-06: Twilio Conversation Memory shipped GA, and MorganAsh MARS runs a standing
per-customer vulnerability score. What survives: incumbents reconcile to *current truth* (new
observations supersede old), which is right for personalization and wrong for risk. **Rejected:**
emailing the committee a correction before we can show the fix; present it on 2026-08-24 as evidence of
rigour instead.

### D-005 · 2026-08-09 · The agent is the product shape; the ledger is the trigger `ACCEPTED`
The competition's stated objective is agentic AI capability and Track A is agentic workflows. A scoring
function is arithmetic. The investigator — tools, multi-step reasoning, structured decisions with
mandatory evidence, human handoff — is what makes this Track A rather than analytics.

### D-004 · 2026-08-09 · The offline provider is first-class, not a stub `ACCEPTED`
Everything runs with zero keys, and `earshot investigate --provider openrouter` replays committed
model responses with no network (`earshot demo` needs no provider at all). This
was a hedge against unprovisioned keys; it is now the reason a judging room without wifi cannot break
the demo. Consequence: offline numbers are always labelled and never headlined.

### D-003 · 2026-08-09 · Package is `earshot`, `src/` layout, build promoted to repo root `ACCEPTED`
`ear` was an unexplained abbreviation. `src/` forces tests to import the *installed* package, which is
what makes "works on a fresh machine" provable rather than asserted. **Rejected:** keeping the build
nested under a numbered folder with a `PYTHONPATH` hack.

### D-002 · 2026-08-09 · `sources/` stays out of `docs/` `ACCEPTED`
`docs/` is ours to edit; `sources/` holds the committee contract and competition rules and is not. That
boundary is worth a top-level folder.

### D-001 · 2026-07-24 · The entry is *Ear on Every Call*, submitted and locked `ACCEPTED`
All prior ideation (`02_ideas*`, `03_selection`, the C-numbered shortlists) is **superseded** and lives
on `main` as history. Do not reopen idea selection.
