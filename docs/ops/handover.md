# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-08-31 (late)** · commit `bd375a4` · branch `build/ear-on-every-call` · **855 tests** (850
pass, 5 skip), separation guard over 45 modules, contrast gate over 674 colour pairs / 17 routes,
ruff clean, **30 UI routes**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. **Every keyed figure is measured and published. ~$2.42 of $12 spent.** All four replay free with
   `EARSHOT_CACHE_MODE=replay` — a miss raises rather than calling out, so a replay cannot spend.
   SSO was re-minted 2026-08-29; `aws sts get-caller-identity` is a **lying probe** (it answers from
   a cached role credential while the token underneath is dead). Probe Bedrock.
3. `progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action

**The documentation is caught up with the measurements as of 2026-08-31.** All four keyed figures are
published with denominators, both conclusions that moved are published with the reason, and no
superseded figure survives outside a labelled retraction. In order:

1. **The IAM ticket — the only hard blocker.** One inline policy, and it now also needs `logs:*`: the
   deployed Lambdas are **unobservable**, not merely inert — no log group exists despite invocations
   already made. JSON and the reproducible error lines are in `aws-infrastructure.md`.
2. **The reader behind `ui/data.js` is still the offline lexicon**, and that is now the sharpest
   inconsistency in the repo: the screens `ui/README.md` calls "the proof" run the exact reader we
   publish as leaving two desks empty. Its *verdicts* are keyed (`4ec34cd`); `--extractor` does not
   reach `earshot investigate`, so this needs a **code path**, not spend.
3. **Extend reader coverage to `--per-trajectory 40`** (~$0.45 delta). Samples nest, so it re-reads
   nothing cached. **Collections is the row worth the denominator** — the one family where the model
   reader loses on coverage (0.38 vs 0.46) and wins by a single crossing.
4. **Arm B: $0.01** on Nova Lite for the reader arm ($0.28 both). Last item on `build-plan.md`'s "not
   measured" list. `extractor_cache_path()` is per-model, so it cannot pollute the cache behind the
   published $1.58 / 1,000.
5. **Free and unblocked:** the video and social deliverable, Phase C's leftovers in
   `../corpus/04-plan.md`, and the per-mechanism tie-share ablation (`mechanism_ablations()` already
   exists in `arms.py`).

**Never spent, and priced:** the model reader's own threshold ($13.96 — until then every model-arm
crossing figure is an **upper bound**, and the tool prints that itself) and the 10-seed keyed sweep
(~$10, the one measurement that would settle the chance gate).

## State

**The corpus was rebuilt 2026-08-31 (Phase C) and the pre-registered headline died.** `full-ledger`
vs `stateless-max` on diffuse: 29–0–1 → **15–13–2, `p=0.851`**. Cause was measured, not guessed: a
`plant_at` bug meant the planted fragment was **silently never spoken** in 69 of 600 arc
conversations, which had crippled the opponent. Fixing it un-crippled it. **D-031 re-registers** the
primary as `full-ledger` vs `window3-top2` (**30–0–0**, both tie-breaks) bound to a **co-primary
chance gate the entry currently FAILS** (18–8–4, `p=0.076`). The dead row keeps its place forever.

**The claim is coverage, not ranking, and both halves are measured.** Same 282 planted conversations,
same ledger, same threshold, one variable — who reads: **complaints 0 / 20 → 20 / 20, vulnerability
0 / 20 → 19 / 20**, retention 1 / 20 → 16 / 20, collections 9 / 20 → 10 / 20; coverage 59 / 282 →
177 / 282. Corroborated externally at 0.8214 (92 / 112) vs 0.0357 (4 / 112) on real CFPB language.
Every ranking arm sits in a 0.113–0.145 band whose floor is an RNG — that argument was never the
winnable one. **The model column is an upper bound** (offline-derived threshold, held fixed).

**Two conclusions moved on 2026-08-31 and both are published with the reason.** AT-57 went 22 / 50 →
**29 / 50** and dismissals 4 / 25 → **13 / 25**, so "the agent escalates rather than filters" is
retracted — **not one line of the agent changed**, the corpus stopped leaking the answer through
surface form. AT-58 went 36 / 49 → **27 / 48** (2 wrong, 19 declined) and **ships as worse**: its
`complaints` row is empty because no complaint customer crossed under the offline reader, so 43 of 48
scorable cases are one desk. Do not let either be restated as an agent improvement or a regression.

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
- **A replay at the wrong sample size looks like a broken cache and is not.** AT-57 replays only at
  `--per-arm 25 --customers 2400`; at `--customers 400` there are just 10 outcome customers, so the
  run draws 35 cases and 27 come back `provider_error`. Match the published invocation exactly — it
  is in `README.md` next to the figure — before concluding a cache is stale.
- **A wrapper that hides an exit code turns a failure into a false success.** `timeout 590 … | tail`
  both under-ran a 17-minute AT-57 job and let the kill return 0, so a truncated run looked clean.
  Twice, ~$1.15. Same family as the `pgrep` mistake.
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
