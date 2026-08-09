# Decisions

Why things are the way they are, and what not to re-open. One entry per decision, newest first.

**Format:** date · what was decided · why · what we rejected. Status is `ACCEPTED`, or `SUPERSEDED BY
<id>` — superseded entries are cut to a single line rather than deleted, so the record stays honest
without the file growing. If an entry no longer affects any current choice, delete it; git remembers.

**This file exists so a fresh session does not re-litigate settled ground.** If you are about to argue
for something listed under "rejected", read the reason first.

---

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
Everything runs with zero keys, and the demo replays committed model responses with no network. This
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
