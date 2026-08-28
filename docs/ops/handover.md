# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-08-29 (late)** · commit `74536fc` · branch `build/ear-on-every-call` · **812 tests**, separation guard over
44 modules, a contrast gate over 634 colour pairs, ruff clean, **30 UI routes**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. AWS: SSO was re-minted 2026-08-29 and every keyed item ran. **`aws sts get-caller-identity`
   is a lying probe** — it answers from a cached role credential while the SSO token underneath
   is dead. Probe Bedrock. `source tools/aws-login.sh` when it is; the login needs a browser.
3. `progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action

**Everything keyed is done and republished.** AT-57 **22 / 50** and AT-58 **36 / 49** on the
shipping corpus and both replay; the streamed demo is re-recorded with both arms keyed; the
cost cap is re-derived from measurement. Read `state-of-play.md` — the numbers moved. In order:

1. **The IAM ticket** — the only hard blocker. One inline policy, and it now also needs `logs:*`:
   the deployed Lambdas are **unobservable**, not merely inert. JSON in `aws-infrastructure.md`.
2. **Arm B: $0.01** on Nova Lite for the reader arm ($0.28 both). Last item on `build-plan.md`'s
   "not measured" list. `extractor_cache_path()` is per-model now, so it cannot pollute the cache
   behind the published reader figures.
3. **Extend the reader-coverage sample.** n=20 per trajectory is a direction; samples nest, so
   `--per-trajectory 40` pays only the delta (~$0.45). The **collections regression** is the half
   most worth a bigger denominator.
4. **Regenerate `ui/data.js` from a keyed investigate run.** The recorded document screens — queue,
   case, retro, the one `ui/README.md` calls "the proof" — are still the offline rule engine.
5. **The design fork is superseded.** `.claude/worktrees/agent-ade2e23d7e6368e38` is a restyle of
   the pre-console UI (18 routes to 30) and main now has a generated design system it was
   reacting to. Recommend discard; still Ravi's call.

**Delegate file-writing work with `isolation: "worktree"`.** The Agent tool's own isolation was
refusing to start on 2026-08-28; `git worktree add -b wp/<name> /c/tmp/<name> HEAD` and telling
the agent the absolute path works fine.

## State

One deployment (Northwind), framed as an integration: nine seams, **five** of them the client's
own systems (the prose said six for weeks; the screen was always right). **One model, Haiku 4.5**
(D-025) — now measured on a multi-turn loop: **22 / 50** verdicts, **41 / 49** routing. The
investigator is a **router and an audit trail, not a filter**. **CDK does not work here** (D-024);
`provision.py` and `deploy.py` are the path. `boto3` stays optional; a fresh clone runs keyless.

## Traps already paid for

- **A keyed run's cache is one file per provider AND per model AND per measurement.** A second
  reader arm through the shared path appends into the cache behind a published figure, silently:
  keys do not collide, nothing errors, the file just quietly holds two models.
- **`config_hash` does not cover the code.** It was byte-identical across two corpora that
  disagreed about who crosses. Manifests carry `pipeline_sha`; a guard comparing config hashes
  alone will bless a stale artifact. Land generator changes *before* spending on keyed runs.
- **A failed replay used to overwrite the run it was replaying** — same seed, hash and provider,
  so the same path. Cache mode is in the filename now and an all-`provider_error` run refuses to
  write. Do not remove either.
- **Two thresholds exist and disagree on purpose.** Stream and `aws/ingest.py` use a fixed cut;
  `earshot investigate` uses a budget-derived top-K. Never merge them on stage.
- **The corpus warns on every run** that two of four trajectories cap at 4 signals. That is the
  arc ceiling, it is honest, and widening the pools moves the published recall.
- **Quote nothing at 10 seeds.** The pre-registered win is 26–2–2 `p=0.000` at 30 and
  7–2–1 `p=0.180` at 10.
- **`stream.py` stays on the guarded surface only because `cli.stream_inputs()` hands it the
  conversations.** Re-add `generate()` and the guard fails, correctly.
- **The account header must take `financial_state`, never `latent_risk`** — and that wiring now
  has a behavioural pin, not just a source-string match, because the string match was defeatable.
- **Narration must never share the ledger reader's extractor**; the final turn-by-turn read must
  equal the batch read byte for byte; a warm cache makes a "live" run a replay
  (`EARSHOT_CACHE_MODE=off`); one response cache per provider, named after the model that ANSWERED.
- **`outcome is not None` is always true** (`Outcome.NONE`) · **a case id contains `#`**, every UI
  link percent-encodes it · **never delete an `__init__.py`**, it drops the guard and the suite
  silently · **verify `pwd` before committing**, a `cd` into a worktree persists across tool calls.
- **The AWS/deploy traps live in `aws-infrastructure.md`** and are not copied here.
