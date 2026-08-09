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
an investigator agent that calls tools and produces case files with cited evidence. **170 tests**,
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

- **Rounds 4 and 5 each found more than rounds 1-3 combined**, and all of it is fixed. Round 4: the
  import guard could be walked past with `from earshot import corpus`; a groundedness metric still
  zero by construction after round 2 was recorded as fixing it; a stratum loss the code computed and
  never printed. Round 5 found defects **inside those fixes** — the 30-seed figures came from a scratch
  script on a seed base no command uses and one of them inverted a conclusion; the guard was still
  walkable via `sys.modules`; a set-valued field broke artifact reproducibility; the ranking-resolution
  claim named the wrong mechanism. **Round 6 has not run, and the rate is not falling.**
- **Nothing is marked Done on the board, deliberately** — one author, no second reviewer. Namit and
  Ishant have not seen any of it.

## Blocked on someone else

- **Jira project admin** — cannot delete the `[DELETE ME]` issues, cannot enable Sprints.
- **AWS CodeCommit** — a named required deliverable, no repo provisioned. Requesting after the 08-10 call.
- **Zenon model keys** — running on a personal OpenRouter account; rules say Zenon supplies them.

## Next three things — in this order, set 2026-08-09

**1. Run round 6, and keep going until a round comes back with nothing material.** Two rounds have now
found their worst defects *inside the previous round's fixes*, so review the round-5 changes first:
the recall band, the ranking-resolution block, the split decoy rates, the day-ordered long-context
window, the demo's narration, and the `-dirty` SHA suffix. Hunt the standing shape — *looks rigorous,
is rigged, unenforced, or unreproducible* — plus the two the last rounds added: **a guard never tested
against its own attack**, and **a number quoted from anything other than the command's own output**.
Hand the reviewer a pinned SHA and do not edit the tree while it runs. Do not start work 2 until this
converges.

**2. Does never-discard beat anything cheaper than itself?** The entry's central open question, and
right now the answer on the evidence is *no*: `stateless-top2` beats the ledger on the pre-registered
stratum at 30 seeds, and `window3-top2` — last three conversations, keep the best two — beats it too.
The corpus cannot yet pose the question fairly: customers average 3.5 conversations, so top-2 discards
almost nothing, and two of the four trajectories have only 4 authored fragments, so long diffuse arcs
exhaust the pool and are forced to plant their loudest. Widen the fragment pools, lengthen histories,
re-run, and add `window3-top2` as a shipped arm. If the ledger pulls ahead, that is the entry. If it
does not, we need to know before 09-07 and the pitch becomes the agent, not the ledger. Fold
**AT-42/AT-43** (CFPB grounding) in behind it.

**3. A UI that makes it look like a product.** Reviewer queue (**AT-61/62/64**): ranked case list, a
case with its evidence chain and retro re-score, approve / dismiss / route. It reads from run artifacts
already on disk, works with zero keys and no network, and must never become a second source of truth
for a number. If it starts competing with the evaluation for attention, stop and ship the numbers.

## Known-weak, stated rather than hidden

- No scoring mechanism earns anything in recall, and the full-ledger vs plain-count comparison flips
  sign across seed sets. **Decay** earns something that is not recall: it gives the ledger 675 distinct
  scores against the plain count's 6, so 0.7% of its alert queue is decided alphabetically against
  70.3%. Confidence weighting, corroboration, cross-channel and escalation have no defence yet.
- Ranking resolution cuts against our own claims, not someone else's: the headline's opponent
  (`stateless-max`) is 40.8% alphabetical and the `dumb-ledger` ablation is 70.3%. `earshot sweep`
  prints the table.
- **A two-float baseline beats us on the pre-registered stratum at 30 seeds** (`stateless-top2`,
  `p=0.013`), and so does a bounded three-conversation window (`window3-top2`, `p=0.013`). Exploratory,
  but pointed at the mechanic the entry rests on.
- The effect is scoped to short histories — it weakens at (3,7) conversations and is gone by (6,14).
- Agent verdict/routing accuracy, cost per 1,000 conversations and p50/p95 latency are not measured.
  Evidence groundedness is now reported as a first-attempt repair rate (AT-57).
- Extraction is matched at conversation level, not character spans.
- Throughput falls with corpus size: ~1,500 conv/s at 400 customers, ~460/s at 15,000. Not optimised.
- The cost cap bounds cumulative spend, not a single anomalous call. Documented, with a test.
- No reviewer queue exists yet — the demo shows case files, not a working queue.
