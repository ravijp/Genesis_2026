# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-08-30** · commit `35e5bdf` · branch `build/ear-on-every-call` · **827 tests**, separation
guard over 44 modules, contrast gate over 650 colour pairs / 17 routes, ruff clean, **30 UI routes**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. **LLM spend is stopped by the user's decision.** No model calls, no `--extractor model`, no keyed
   tool. `uv run earshot sweep` (offline, default) is free and is the source of quotable numbers.
3. `progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action

**The corpus was widened 2026-08-30** (pools 8/8/4/4 → 14/14/14/14); every published number was
regenerated free and offline. Read `state-of-play.md` — the numbers moved, some across zero.
Everything keyed is on hold. What does NOT need spend, in order:

1. **The IAM ticket** — the only hard blocker that isn't a spend decision. One inline policy, now
   also needing `logs:*`: the deployed Lambdas are **unobservable**, not merely inert. JSON in
   `aws-infrastructure.md`.
2. Corpus/lexicon, UI, docs, CI work — all free. `state-of-play.md`'s "Next, in order" splits what
   waits on spend (Arm B, `ui/data.js` regen, the 10-seed keyed sweep, a bigger reader-coverage
   sample) from what does not.

**When spend resumes:** 10-seed keyed sweep (~$10, ONE process, one cache path) on the widened corpus;
Arm B on Nova Lite (~$0.01–$0.28); reader-coverage past n=20/trajectory (~$0.45 for +20);
`ui/data.js` regen from a keyed `investigate` run.

**Delegate file-writing work with `isolation: "worktree"`** — `git worktree add -b wp/<name>
/c/tmp/<name> HEAD`, tell the agent the absolute path.

## State

**`random-rank` is a shipped chance-floor arm; full-ledger is indistinguishable from it on diffuse
arcs** (17–11–2, `p=0.345`) and is **7th of 9 whole-portfolio**. The pre-registered diffuse win over
`stateless-max` holds (29–0–1); `stateless-top2`/`window3-top2`, which beat the ledger on the old
corpus, now lose to it (26–2–2 each) — a corpus change flipped a headline both ways. Lexicon finds
1 of 32 fragments authored for the widened pools (21 of the original 24): reader, not ranking, is
the binding constraint. One deployment (Northwind), nine seams, five the client's own. One model,
Haiku 4.5 (D-025): **22/50** verdicts, **36/49** routing, router-not-filter. CDK doesn't work here
(D-024); `provision.py`/`deploy.py` are the path.

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
- **A keyed run's cache is one file per provider AND per model AND per measurement** — a second
  reader arm through the shared path appends behind a published figure, silently. **`config_hash`
  does not cover the code** — manifests carry `pipeline_sha` now (`7b525d8`); a config-hash-only
  guard blesses a stale artifact. **A failed replay used to overwrite the run it was replaying** —
  cache mode is in the filename and an all-`provider_error` run refuses to write; keep both.
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
