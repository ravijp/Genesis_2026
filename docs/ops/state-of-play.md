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
`docs/gates/2026-08-10-sprint-1-checkin.md`, updated for round 4). Real gates: **2026-08-24** combined
Sprint 1+2 demo, **2026-09-07** Sprint 3.

The system runs end to end with zero API keys: dataset generation → extraction → per-customer ledger →
an investigator agent that calls tools and produces case files with cited evidence. **160 tests**,
ruff clean, `earshot sweep` produces every published number and now prints every comparison behind them.

**The headline holds and strengthened.** On thin-evidence customers the ledger catches 134/780 against
96/780 for score-each-call-and-forget — 8 seeds of 10, 2 ties, no losses, p=0.008; at 30 seeds, 27-2-1.

**Two things round 4 changed about what we claim.** The ledger *loses* on concentrated arcs by a
comparable margin (119/629 vs 180/629, p=0.039), which we now publish — the result is a trade, not a
win. And a two-float baseline, `stateless-top2`, matches it on thin evidence (147/780), so the honest
claim is *aggregation beats no aggregation*, not *memory beats detection*. See D-015 and D-016.

## In flight

- **Round 4 of adversarial review found more than rounds 1-3 combined** and all of it is fixed. The
  worst: the answer-key import guard could be walked past with `from earshot import corpus` (a
  reviewer used it to lift published extractor accuracy 0.66 → 0.84 with every test green); the
  groundedness metric was still zero by construction after round 2 supposedly fixed it; two published
  p-values no command could produce. **Round 5 has not run.**
- **Nothing is marked Done on the board, deliberately** — one author, no second reviewer. Namit and
  Ishant have not seen any of it.

## Blocked on someone else

- **Jira project admin** — cannot delete the `[DELETE ME]` issues, cannot enable Sprints.
- **AWS CodeCommit** — a named required deliverable, no repo provisioned. Requesting after the 08-10 call.
- **Zenon model keys** — running on a personal OpenRouter account; rules say Zenon supplies them.

## Next three things — in this order, set 2026-08-09

**1. Run round 5, and keep going until a round comes back with nothing material.** Round 4's fixes
changed the arm roster, the sweep output, three guards and the demo's baseline definition, so there is
a fresh surface. Hunt the same shape — *looks rigorous, is rigged, unenforced, or unreproducible* —
and add the new one round 4 taught us: **a guard that is never tested against the attack it exists to
stop.** Do not start work 2 until this converges.

**2. Does never-discard ever beat keep-the-best-two?** This is now the entry's central open question,
not a nice-to-have. It cannot be answered in the current corpus: customers average 3.5 conversations,
so top-2 discards almost nothing, and two of the four trajectories have only 4 authored fragments, so
long diffuse arcs exhaust the pool and are forced to plant their loudest fragment. Widen the fragment
pools, lengthen histories, re-run. If the ledger pulls ahead, that is the entry. If it does not, we
need to know before 09-07. Fold **AT-42/AT-43** (CFPB grounding) in behind it.

**3. A UI that makes it look like a product.** Reviewer queue (**AT-61/62/64**): ranked case list, a
case with its evidence chain and retro re-score, approve / dismiss / route. It reads from run artifacts
already on disk, works with zero keys and no network, and must never become a second source of truth
for a number. If it starts competing with the evaluation for attention, stop and ship the numbers.

## Known-weak, stated rather than hidden

- Decay, corroboration and channel weighting earn nothing in recall. Confidence weighting does earn
  something and it is not recall: it gives the ledger ~808 distinct scores against `long-context-3`'s
  ~69, so 0.7% of its alert queue is decided alphabetically against long-context's 69.5%.
- The `long-context-3` comparison is weak for that reason and we do not defend it hard.
- The effect is scoped to short histories — it weakens at (3,7) conversations and is gone by (6,14).
- Agent verdict/routing accuracy, cost per 1,000 conversations and p50/p95 latency are not measured.
  Evidence groundedness is now reported as a first-attempt repair rate (AT-57).
- Extraction is matched at conversation level, not character spans.
- Throughput falls with corpus size: ~1,500 conv/s at 400 customers, ~460/s at 15,000. Not optimised.
- The cost cap bounds cumulative spend, not a single anomalous call. Documented, with a test.
- No reviewer queue exists yet — the demo shows case files, not a working queue.
