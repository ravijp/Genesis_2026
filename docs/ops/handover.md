# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-08-29** · commit `30dc7f8` · branch `build/ear-on-every-call` · **774 tests**, separation
guard over 44 modules, ruff clean, 21 UI routes

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. AWS: **the SSO session is expired.** `source tools/aws-login.sh` needs a browser — that is
   Ravi's action, and it blocks the one keyed run below. `--force` if a grant IT says is live
   still reads as denied.
3. `progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action

**A four-agent red team ran on 2026-08-28 and its findings are all landed** — read
`state-of-play.md` first, the numbers moved. In order of value:

1. **Re-run AT-57 keyed on the fixed corpus** (~$1.50, 50 balanced cases):
   `uv run --extra aws python tools/verdict_accuracy.py --provider bedrock --per-arm 25
   --customers 2400`. **Blocked on the SSO login only.** The published 22 / 50 was measured at
   `47a2be8`, before the corpus fix, and no longer replays — the README states that rather than
   hiding it, but it should not stay true. Then `tools/routing_accuracy.py` re-scores it free.
2. **The IAM ticket** — one inline policy and the deployed path stops being a diagram. It now
   also needs `logs:*`: the Lambdas are **unobservable**, not merely inert. JSON in
   `aws-infrastructure.md`, written to be pasted.
3. **Arm B, priced honestly: $0.01** on Nova Lite for the reader arm alone ($0.28 re-runs both).
   The last item on `build-plan.md`'s "not measured" list, and the brief did ask for a
   comparison model.
4. **The design fork is Ravi's call and he has the facts**: `.claude/worktrees/agent-ade2e23d7e6368e38`
   has **18 routes to main's 21** — it is a dark-first restyle of the *pre-console* UI and does
   not contain `#/desk` at all. Lift the palette or discard; do not merge it.

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
