# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-08-31** · commit `31cc1ca` · branch `build/ear-on-every-call` · **855 tests** (850 pass, 5
skip), separation guard over 45 modules, contrast gate over 650 colour pairs / 17 routes, ruff
clean, **30 UI routes**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. **LLM spend is stopped by the user's decision.** No model calls, no `--extractor model`, no keyed
   tool. `uv run earshot sweep` (offline, default) is free and is the source of quotable numbers.
3. `progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action

**THE ONE THING THAT NEEDS A HUMAN: `source tools/aws-login.sh`.** The SSO token expired 2026-08-31
and minting one needs a browser. Everything below it costs **under $1** and closes the last real gap.
Nothing else is blocked on money — the $12 budget is untouched.

Once logged in, in this order, **ONE process at a time, one cache path** (see the traps):

1. **Regenerate `ui/stream.js` and `ui/data.js`** (~$0.80). They were recorded 2026-08-28, so **the
   demo screens still show pre-Phase-C transcripts** — chats opening "Thank you for calling",
   repeated lines, ASR noise in typed text. Phase C fixed all of that in the generator and none of
   it on screen. This is the highest-value dollar in the project.
2. **Re-measure AT-57 / AT-58** (~$1.50, routing is free). 22 / 50 and 36 / 49 are labelled
   corpus-historical everywhere they appear; this makes them current.
3. **Reader coverage** (~$0.45) — the coverage claim the whole entry now rests on is one corpus old.

**Free and unblocked:** the IAM ticket (one inline policy plus `logs:*` — the Lambdas are
*unobservable*, not merely inert; JSON is in `aws-infrastructure.md`), the video and social
deliverable, and Phase C's leftovers in `../corpus/04-plan.md`.

## State

**The corpus was rebuilt 2026-08-31 (Phase C) and the pre-registered headline died.** `full-ledger`
vs `stateless-max` on diffuse: 29–0–1 → **15–13–2, `p=0.851`**. Cause was measured, not guessed: a
`plant_at` bug meant the planted fragment was **silently never spoken** in 69 of 600 arc
conversations, which had crippled the opponent. Fixing it un-crippled it. **D-031 re-registers** the
primary as `full-ledger` vs `window3-top2` (**30–0–0**, both tie-breaks) bound to a **co-primary
chance gate the entry currently FAILS** (18–8–4, `p=0.076`). The dead row keeps its place forever.

**The claim is now coverage, not ranking.** The keyless lexicon finds 59 / 282 planted arc
conversations and leaves **two of four desks with no case at all**; the model reader scores 0.8214
(92 / 112) on real CFPB language against the lexicon's 0.0357 (4 / 112). Every ranking arm sits in a
0.113–0.145 band whose floor is an RNG — that argument was never the winnable one.

**AT-52 answered: keep all four mechanisms.** The `dumb-ledger` "loss" (7–18–5, `p=0.043`) is a
tie-break artefact — that arm makes 5 distinct scores over 1,500 customers, and randomised it is
11–13–6, `p=0.839`. Structural leg: **239 / 485 ledger entries are worth more now than at write;
0 / 485 under a plain count.** Retro re-scoring cannot exist in a count.

One deployment (Northwind), nine seams, **five** the client's own. **One model, Haiku 4.5** (D-025).
**CDK does not work here** (D-024). `boto3` stays optional; a fresh clone runs keyless.

## Traps already paid for

- **NEVER point two model runs at one cache path.** `ResponseCache` loads its file once in
  `__init__` and never re-reads it (`llm/cache.py:66-85`), so concurrent processes are blind to each
  other's writes. On 2026-08-30 a broken liveness check (`pgrep` **does not exist on this machine**
  and reports every process dead) led to a second sweep being launched over a live one: **$12.33
  spent, $4.60 wasted, no artifact, and 39 cache lines torn by interleaved writes** — those
  completions are paid for and permanently unreplayable. Duplication started at record 185, not at
  the resume boundary. *(The first post-mortem blamed `prompt_sha` drift. It was wrong: a duplicate
  key proves the key was STABLE — drift would have produced zero duplicates. `progress.md` carries
  the corrected version.)*
- **`CachingProvider` counts hits/misses and never prints them** (`llm/cache.py:127-128`). A 47% miss
  rate stayed invisible for 3,275 paid calls. Print the counter before spending.
- **One cache file per provider AND per model AND per measurement.** A second reader arm through a
  shared path appends behind a published figure silently — keys do not collide, nothing errors.
  **`config_hash` does not cover the code**: it was byte-identical across two corpora that disagreed
  about who crosses. Manifests carry `pipeline_sha`. Land generator changes *before* spending.
- **Two thresholds disagree on purpose** — stream/`aws/ingest.py` use a fixed cut, `investigate`
  a budget-derived top-K. Never merge them.
- **The arc ceiling is gone; a test now pins its absence, not its presence.** Pools are 14/14/14/14;
  `test_the_shipped_default_no_longer_breaches_the_ceiling` asserts the warning never fires.
- **Quote nothing at 10 seeds** — not yet re-measured on the widened corpus (the deferred sweep).
- **`stream.py` stays guarded only because `cli.stream_inputs()` hands it conversations** —
  re-add `generate()` and the guard correctly fails.
- **The account tool takes `risk_signal`, never `latent_risk`** — renamed this session so
  `risk_signal=truth.latent_risk` reads as the error it would be.
- **Narration must never share the ledger reader's extractor**; the final turn-by-turn read equals
  the batch read byte for byte; a warm cache makes "live" a replay (`EARSHOT_CACHE_MODE=off`).
- **`outcome is not None` is always true** · a case id contains `#`, every link percent-encodes it ·
  never delete an `__init__.py` · verify `pwd` before committing, a worktree `cd` persists.
- **AWS/deploy traps live in `aws-infrastructure.md`**, not copied here.
