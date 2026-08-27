# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything. Rewritten
in place at each handover. **Keep it under ~60 lines** — it loads into every conversation. It is a
baton, not a history: next action, live blockers, traps already paid for. History goes in
`progress.md` or git.

**2026-08-25** · commit `04d6d2d`+ · branch `build/ear-on-every-call` · **312 tests**, guard at 81, ruff clean

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. `source tools/aws-login.sh --check` (or `pwsh -File tools/aws-login.ps1 -Check`). Add `--force` if a
   permission IT says is granted still reads as denied — SSO caches grants in the role session.
3. `docs/ops/progress.md` for work-package status and blocker owners. `decisions.md` before arguing
   for anything.

## Next action — the Lambda handlers

`src/earshot/aws/ingest.py`, `investigate.py`, `api.py`. The stores and the provider both exist, so
this is the glue that closes the end-to-end path.

- **`ingest`**: one SQS record → `Conversation` → `extract()` → `LedgerStore.append()` (conditional,
  so a redelivery is a no-op) → re-score via the unchanged `SignalLedger` → if the threshold is
  crossed, enqueue to the investigations queue. **Do not reimplement scoring** — load, delegate,
  persist. That is the one thing this architecture forbids.
- **`investigate`**: queue consumer running the existing `investigate()` loop unchanged, writing a case
  through `CaseStore.put_case()`. W1 first, though — `cli.py` still discards `ctx.score`,
  `ctx.signal_type`, `ctx.threshold` and the retro fields, and **all three reviewer-UI beats are
  unrenderable from disk until that lands**.
- **`api`**: five read endpoints over `CaseStore` + `ReviewStore` for the SPA.
- Deploy: **zip, passing the existing role** `arn:aws:iam::859430413223:role/zenon-poc-lambda-execution`.
  No new role, no container image (D-024).
- **Delegate this to a subagent with `isolation: "worktree"`.** Two agents in one tree already
  collided here and one wiped the other's untracked files.

**Ravi's call before anything real is created:** `tools/provision.py --stage dev --no-dry-run` makes
billed resources. Dry-run is clean — 3 tables, 3 queues, 4 PARKED rows. Do not run it unprompted.

## State

**One model, Haiku 4.5, for reader and investigator** (D-025) — `us.anthropic.claude-haiku-4-5-20251001-v1:0`.
Nova Lite and Llama 3 8B are the arm-B candidates; arm B is deliberately undecided. Sonnet is dropped,
which *unblocked* the investigator. Haiku's verdict accuracy on a multi-turn loop is **unmeasured** —
not a cost win until AT-57 says so.

**CDK does not work here** (D-024): `cdk bootstrap` needs `s3:CreateBucket`, `iam:CreateRole`,
`ecr:CreateRepository`, all denied. boto3 scripts instead. Do not re-litigate.

**Only real IT ask left: CodeBuild + CodePipeline.** `buildspec.yml` is written and parked. Note it is
blocked by the same `iam:CreateRole` gap as the Lambda roles — the one role we can pass is scoped to
Lambda's trust policy, not CodeBuild's.

`boto3` is installed via the `aws` extra. It stays **optional** in `pyproject.toml` so a fresh clone
runs all 312 tests keyless — that guarantee is load-bearing, do not promote it to a hard dependency.

## Traps already paid for

- **A new IAM grant does nothing until the SSO session is reissued.** Use `--force`.
- **Agents that write files need `isolation: "worktree"`.** Untracked files + another agent's
  `git stash -u` nearly lost three of them, and the only tell was a `reset` in reflog, after the fact.
- **Never delete an `__init__.py`.** Drops the guard 20 modules → 19 and the suite silently.
- **Green stub tests are not proof.** Two provisioner bugs lived in the seam between our code and the
  SDK: SQS's absent-queue wire code differs from botocore's class name, and PITR was probed on a table
  dry-run never created. Exercise tools against reality.
- **A test that assumes an optional dep is absent is broken.** The missing-boto3 test flipped to
  failing the moment `uv sync --extra aws` ran. Simulate absence, never assume it.
- **When something reads as AccessDenied, read the error *message*.** Two probe bugs and the Anthropic
  model-id prefix all masqueraded as permission problems.
