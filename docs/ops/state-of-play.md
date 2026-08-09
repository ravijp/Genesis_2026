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

**AT-43 landed 2026-08-09 and the answer is bad, which is what makes it worth having.** On 150
hand-marked real CFPB narratives the extractor scores **0.0357 strict recall (4 / 112)** against
**0.681 (496 / 728)** on our own prose; three of four signal types scored **exactly zero** and 24 of
26 cues never fired. Everything — pre-registration, gold set, results, and the two failures I
disclosed — is in `benchmarks/cfpb/`; `steps/05_score.py` reproduces it offline. Nothing upstream was
touched, so the synthetic 0.681 stands.

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
  competent reviewer on 7k lines. Everything found so far is fixed. What remains is
  listed below and is deliberately not being chased; writing it up as `docs/ops/known-issues.md` —
  what is wrong, how it was found, what a fix would cost — is a half-day job nobody has done yet.
  **Do not open an unbounded round 7.** If a further pass is wanted, bound it: one reviewer, one
  lens (what a judge sees on 08-24), a severity bar of "changes a published number or breaks on
  stage", against a pinned SHA.
- **Open defects, deliberately unfixed and not yet written up:** the recall band pins only
  `extract.py` (a leak planted in `memory.py` moved the headline 8-0-2 → 9-0-1 while the band did
  not move at all); the artifact-reproducibility test cannot observe the failure it names; the AST
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

## Next three things — in this order, set 2026-08-10 by D-020

**D-020 overrides AT-43's pre-registered consequence, deliberately and in writing.** §6 of the
protocol promoted the corpus regrounding; the evidence turned out to implicate the *extractor's* cues
instead, and the experiment that is actually blocking the entry needs only *more* fragments, not
*real* ones. Read D-020 before re-arguing this.

**1. Make the reader able to read prose it did not grow up with.** This was work 3, then deferred by
D-020, and is now first on evidence rather than argument — see the measurement below. Fix the cue
vocabulary in `extract_lexicon.py`. `benchmarks/cfpb/out/results.json` names the 24 cues that never
fired and `benchmarks/cfpb/out/gold.jsonl` is a 150-document marked development set; the 56
blind-authored fragments in `benchmarks/pool-widening/` are the **held-out check** that catches
tuning to it. Do not fit the cues to either set alone.

**Why it moved back to first, and it is not a preference.** Widening the fragment pools (the
prerequisite for the history-length experiment) was done and measured, then reverted. The extractor
catches **0.5325 (82/154)** of the original 24 fragments and **0.0353 (22/624)** of 56 new ones
authored blind to the same construct definitions, in the same spoken UK bank register. Overall recall
falls 0.681 → 0.1337, and `stateless-top2` collapses into `stateless-max` on every seed because there
is no longer enough extracted signal to differentiate arms. So the history-length question cannot be
asked on a corpus the reader cannot read — the reader is genuinely blocking, which is what AT-43's
pre-registration guessed at while naming the wrong file.

**0.0353 on blind-authored synthetic utterances against 0.0357 on real CFPB narratives is the same
number from two directions**, and it closes the genre-mismatch escape route AT-43 left open. The
published **0.681 measures how much pass A and pass B were co-developed, not what the extractor can
read.** That is a finding about our own foundational separation claim and it should be presented that
way on 09-07 rather than discovered by a judge.

**Then, and only then, the history-length experiment (~1 day once the reader works).** Splice
`benchmarks/pool-widening/fragments.py`, re-measure, move `RECALL_BAND` deliberately, re-run
everything, then sweep 30 seeds at (2,5)/(4,9)/(8,20) and publish the curve. Done already:
`--conversations-per-customer MIN,MAX` exists and refuses a range wider than the scarcest pool.

**2. The reviewer queue UI.** `AT-61/62/64`. Never started, and the whole client-facing axis of a
Track A entry — needed for 2026-08-24. It is blocked on persistence, not design: `cli.py:494` builds
each case record and discards `ctx.score` and `ctx.signal_type`, and the retro re-score fields
(`memory.py:161-173`) are computed and printed by `cmd_demo` but written to no artifact. So none of the
three beats — ranked list, evidence chain, retro re-score — can be rendered from disk today. Persist
those fields first, then build it *functional* and stop (§9: polish scores nothing). **The dangerous
shortcut is regenerating the corpus from `manifest.seed` to recover transcripts** — that puts the
evidence chain and `stratum`/`outcome`/`latent_risk` on one object behind a client-facing screen.

**3. Cost per 1,000 conversations and p50/p95 latency.** A *named* required deliverable still marked
"not measured", and the answer to the feasibility question a judge is most likely to ask. Note an
unpriced risk surfaced 2026-08-10: if a bank does not already transcribe, **ASR dominates our cost
story**, and our cost narrative currently ignores it entirely.

**Still off the table before 09-07**, settled: fitting the generative distribution to CFPB
(working-agreements §9), and stitching real complaints into invented histories (D-010). AT-43 added a
third reason — uniformly drawn CFPB narratives carry escalation in **50 of 100** cases, because people
who complain to a regulator have usually complained to the firm first. That is the complaint channel,
not bank conversations.

**Unverified and worth checking before 09-07:** a claim that NICE ships an *Enlighten AI for
Vulnerable Customers* product. If true it is a second novelty collision of the D-006 kind and the
wedge needs narrowing again in the same honest way. Nobody has confirmed it.

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
- **Two of four trajectories can never carry more than 4 signals, and this bounds every published
  number.** Fragments are planted without replacement and the `complaint_escalation` and `life_event`
  pools hold 4, while arcs run to 5 conversations — so on those trajectories the later conversations
  are empty by construction. Found 2026-08-10 when the new pool guard rejected the *default* range.
  Every command now prints this. It is the reason work 1 starts with widening the pools.
- **The extractor barely works on language it did not write.** 0.0357 strict recall (4 / 112) on real
  CFPB narratives against 0.681 (496 / 728) on ours; three of four signal types at exactly zero. This
  is measured, published in `benchmarks/cfpb/`, and is now work 1.
- Extraction is matched at conversation level, not character spans.
- Throughput falls sharply with corpus size — roughly 7x between 400 and 15,000 customers on one
  laptop. Not optimised, and not pinned by a committed manifest at the larger size.
- The cost cap bounds cumulative spend, not a single anomalous call. Documented, with a test.
- No reviewer queue exists yet — the demo shows case files, not a working queue.
