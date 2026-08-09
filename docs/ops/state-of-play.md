# State of play

**Updated 2026-08-09.** Rewritten in place every working session — **never appended to**. Hard cap:
this file fits on one screen. If something will not fit, it belongs in `decisions.md` (a choice),
`working-agreements.md` (a rule), or Jira (work). Anything historical belongs in git.

**If you are a fresh session, read in this order:** this file → `decisions.md` →
`working-agreements.md` → `README.md` → `docs/architecture/architecture.md`. That is enough to work.
`docs/architecture/build-plan.md` covers what is left to build.

---

## Where we are

Sprint-1 check-in is **2026-08-10 10:30** (15 minutes, progress only — brief at
`docs/gates/2026-08-10-sprint-1-checkin.md`, updated through round 5). Real gates: **2026-08-24** combined
Sprint 1+2 demo, **2026-09-07** Sprint 3.

The system runs end to end with zero API keys: dataset generation → extraction → per-customer ledger →
an investigator agent that calls tools and produces case files with cited evidence. **189 tests**,
ruff clean, `earshot sweep` produces every published number and now prints every comparison behind them.

**The headline holds and strengthened.** On thin-evidence customers the ledger catches 134/780 against
96/780 for score-each-call-and-forget — 8 seeds of 10, 2 ties, no losses, p=0.008; at 30 seeds, 27-0-3.

**What rounds 4-5 changed about what we claim.** The ledger *loses* on concentrated arcs by a
comparable margin (119/629 vs 180/629, p=0.039), which we now publish — the result is a trade, not a
win. And a two-float baseline, `stateless-top2`, does not merely match it on thin evidence: at 30
seeds it **beats** it (`7-21-2`, `p=0.013`), as does a bounded three-conversation window. So the
honest claim is *aggregation beats no aggregation*, not *memory beats detection*, and what
never-discard adds over a cheap window is currently **unproven**. See D-015 through D-018.

## In flight

- **Adversarial review is FROZEN at six rounds.** Rounds 4-6 each found real defects, and each found
  its worst ones *inside the previous round's fixes* — twice the fix reproduced the defect it was
  fixing. The stopping rule was the problem: "run until a round finds nothing" never fires against a
  competent reviewer on 7k lines. Everything found so far is fixed. What remains is triaged into
  `known-issues.md` rather than chased. **Do not open an unbounded round 7.** If a further pass is
  wanted, bound it: one reviewer, one lens (what a judge sees on 08-24), a severity bar of "changes a
  published number or breaks on stage", against a pinned SHA.
- **Open defects, deliberately unfixed, all recorded in `docs/ops/known-issues.md`:** the recall band
  pins only `extract.py` (a leak planted in `memory.py` moved the headline 8-0-2 → 9-0-1 while the band
  did not move at all); the artifact-reproducibility test cannot observe the failure it names; the AST
  provenance guard misses 13 of 15 bypasses; `get_transactions` truncates mid-JSON at a schema-legal
  `max_rows` and the parse failure is swallowed into `{}`; the offline engine's `false_alarm` is
  unreachable; `overdraft_limit` is overstated 27.5% of the time and `savings_balance` is a 90-day
  outflow total; no committed manifest at 15,000 customers; `elapsed_seconds` makes "bit-for-bit
  reproducible" literally false for artifacts.
- **Nothing is marked Done on the board, deliberately** — one author, no second reviewer. Namit and
  Ishant have not seen any of it.

## Blocked on someone else

- **Jira project admin** — cannot delete the `[DELETE ME]` issues, cannot enable Sprints.
- **AWS CodeCommit** — a named required deliverable, no repo provisioned. Requesting after the 08-10 call.
- **Zenon model keys** — running on a personal OpenRouter account; rules say Zenon supplies them.

## Next three things — in this order, reset 2026-08-09 after the review freeze

**1. Ground the corpus on real public data — get the essence, not the text.** `AT-42`. CFPB gives
3.8M real, public-domain complaint narratives. Extract the *distributional* essence — complaint
length, how grievance escalates across a narrative, vocabulary and register, product/issue mix,
how often a real narrative carries more than one signal — and drive `corpus.py` and
`corpus_lexicon.py` from it instead of from fragments authored by hand. **The answer key still comes
first**: deterministic code decides what is true, real language only shapes how it is written. D-010
settles the boundary — do NOT stitch real complaints into invented customer histories; it produces
incoherent people and destroys the measurement. Then `AT-43`: benchmark the extractor on real
narratives against a hand-marked gold set. Together these answer "your reader only works on prose you
wrote yourself", which is the single most likely technical objection on 09-07.

**2. The reviewer queue UI.** `AT-61/62/64`. Never started, and it is the whole presentation axis of a
Track A *client-facing* entry — needed for the 2026-08-24 combined Sprint 1+2 demo. Ranked case list ·
a case with its evidence chain and the retro re-score visible · approve / dismiss / route.
Constraints, already settled: it reads run artifacts already on disk rather than re-running the
pipeline · works with zero API keys and no network · **never becomes a second source of truth for a
number** — it displays what `earshot sweep` and the run artifacts already produced. If it starts
competing with the evaluation for attention, stop and ship the numbers.

**3. Write `known-issues.md` and close the review out.** Triage the open list above against one
question: *would a technical judge's score change if this stayed broken?* Fix only those. Everything
else is documented with what is wrong, how it was found, and what fixing it would cost. Say plainly
that six adversarial rounds ran and the defect rate did not fall — that is a finding about the method,
and a written known-issues list buys more engineering-quality credit than a clean bill of health.

Still open underneath all three: **does never-discard buy anything over a cheap bounded window?**
`window3-top2` beats the ledger on the pre-registered stratum and ties it on the other. The corpus
cannot currently pose the question fairly (3.5 conversations per customer; two of four trajectories
have only 4 authored fragments). Work 1 widens the fragment pools as a side effect — when it does,
expose `conversations_per_customer` as a CLI flag and re-run at (2,5)/(4,9)/(8,20). If the ledger
pulls ahead, that is the entry. If not, the honest pitch is the agent with the ledger as its cheapest
trigger (D-005), and Ravi decides that, not a session.

## Known-weak, stated rather than hidden

- No scoring mechanism earns anything in recall, and the full-ledger vs plain-count comparison flips
  sign across seed sets. **Decay** earns something that is not recall: it gives the ledger 673 distinct
  scores against the plain count's 6, so 0.0% of its alert queue is decided alphabetically against
  55.1%. Confidence weighting, corroboration, cross-channel and escalation have no defence yet.
- Ranking resolution cuts against our own claims, not someone else's: the headline's opponent
  (`stateless-max`) is 40.8% alphabetical and the `dumb-ledger` ablation is 55.1%. `earshot sweep`
  prints the table.
- **Two cheaper arms beat us on the pre-registered stratum at 30 seeds**: `stateless-top2` and
  `window3-top2`, both `7-21-2`, `p=0.013`. `window3-top2` also holds us to a tie on concentrated arcs
  (`16-8-6`, `p=0.152`), so it is not even a trade. Both are shipped arms — `earshot sweep` prints
  this. What never-discard buys over a three-conversation window is currently unproven.
- Agent verdict/routing accuracy, cost per 1,000 conversations and p50/p95 latency are not measured.
  Evidence groundedness is now reported as a first-attempt repair rate (AT-57).
- Extraction is matched at conversation level, not character spans.
- Throughput falls sharply with corpus size — roughly 7x between 400 and 15,000 customers on one
  laptop. Not optimised, and not pinned by a committed manifest at the larger size.
- The cost cap bounds cumulative spend, not a single anomalous call. Documented, with a test.
- No reviewer queue exists yet — the demo shows case files, not a working queue.
