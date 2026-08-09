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
`docs/gates/2026-08-10-sprint-1-checkin.md`). Real gates: **2026-08-24** combined Sprint 1+2 demo,
**2026-09-07** Sprint 3.

The system runs end to end with zero API keys. Dataset generation → signal extraction → per-customer
ledger → an investigator agent that calls tools and produces case files with cited evidence. 128 tests,
ruff clean, `earshot sweep` produces every published number.

**The headline holds:** on thin-evidence customers the ledger catches 134/780 against 96/780 for
score-each-call-and-forget — 8 seeds of 10, 2 ties, no losses, p=0.008. Overall, no arm is
distinguishable from any other.

The system runs end to end with zero API keys, and the demo replays committed model responses with an
invalid key set — a room without wifi cannot break it. **144 tests**, ruff clean.

## In flight

- **Nothing is marked Done on the board, deliberately** — one author, no second reviewer. Namit and
  Ishant have not seen any of it.
- Three adversarial review rounds done; each found real defects, and each round's fixes created work
  for the next. Round 4 has not run.

## Blocked on someone else

- **Jira project admin** — cannot delete the `[DELETE ME]` issues, cannot enable Sprints. Both need
  permissions the team does not have.
- **AWS CodeCommit** — a named required deliverable, no repo provisioned. Requesting after the 08-10 call.
- **Zenon model keys** — running on a personal OpenRouter account; rules say Zenon supplies them.

## Next three things

1. Decide **AT-53** — does the memory layer ship alongside per-call detection, or not at all? It wins
   on thin evidence and ties elsewhere, and the naive combination was worse than either half.
2. Resolve **AT-52** — decay, corroboration and channel weighting are indistinguishable from a plain
   count. Justify them or remove them.
3. Ground the reader on real CFPB complaints (**AT-43**) — the strongest available answer to "your
   extractor only works on prose you wrote yourself".

## Known-weak, stated rather than hidden

- Scoring mechanisms (decay, corroboration, channel weighting) are indistinguishable from a plain count.
- Agent verdict/routing accuracy, first-attempt evidence groundedness, cost per 1,000 conversations and
  p50/p95 latency are **not yet measured**.
- The cost cap bounds cumulative spend, not a single anomalous call. Documented, with a test.
- No reviewer queue exists yet — the demo shows case files, not a working queue.
