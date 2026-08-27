# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything. Rewritten
in place at each handover. **Keep it under ~60 lines** — it loads into every conversation. It is a
baton, not a history: next action, live blockers, traps already paid for. History goes in
`progress.md` or git.

**2026-08-28** · commit `fb7e551` · branch `build/ear-on-every-call` · **406 tests**, guard at 96, ruff clean

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. `source tools/aws-login.sh --check` (or `pwsh -File tools/aws-login.ps1 -Check`). Add `--force` if a
   permission IT says is granted still reads as denied — SSO caches grants in the role session.
3. `docs/ops/progress.md` for work-package status and blocker owners. `decisions.md` before arguing
   for anything.

## Next action — the reviewer UI (W10)

**All three Lambda handlers exist and the end-to-end path closes in code.** `aws/ingest.py`,
`aws/investigate.py`, `aws/api.py`, plus `aws/transcripts.py` (the S3 evidence archive W7 needed and
did not have). Nothing has been created in AWS.

W10 is the whole client-facing axis of a Track A entry and is now fully unblocked:

- **Build it against the offline artifact first.** `earshot investigate` writes the same case shape
  the API returns — both come from `case_record()` — so all three screens can be built and demoed
  with **zero AWS**. `ui/` exists, is gitignored for `node_modules/` and `dist/`, and is excluded
  from ruff and pytest.
- The five reads and one write are in `aws/api.py`'s module docstring. The three beats: ranked queue
  (`GET /cases`), evidence chain (`GET /cases/{id}`), retro re-score (the `score_at_write` /
  `score_now` / `retro_delta` / `load_bearing` fields on every evidence row).
- **Never regenerate the corpus from `manifest.seed` to fill a gap.** It puts `stratum`, `outcome`
  and `latent_risk` behind a client-facing screen. Tests scan the artifact and every API response
  for those names.
- **Delegate with `isolation: "worktree"`.** Two agents in one tree already collided here.

Then: deploy the handlers (zip, passing `zenon-poc-lambda-execution`, D-024) and the first keyed run.

**Ravi's call before anything real is created:** `tools/provision.py --stage dev --no-dry-run` makes
billed resources. Dry-run is clean — 3 tables, 3 queues, 4 PARKED rows. Do not run it unprompted.

## State

**One model, Haiku 4.5, for reader and investigator** (D-025) — `us.anthropic.claude-haiku-4-5-20251001-v1:0`.
Arm B is deliberately undecided (Nova Lite / Llama 3 8B). Haiku's verdict accuracy on a multi-turn
loop is **unmeasured** — not a cost win until AT-57 says so.

**CDK does not work here** (D-024): bootstrap needs `s3:CreateBucket`, `iam:CreateRole`,
`ecr:CreateRepository`, all denied. boto3 scripts instead. Do not re-litigate.

**Only real IT ask left: CodeBuild + CodePipeline.** `buildspec.yml` is written and parked, blocked by
the same `iam:CreateRole` gap.

`boto3` is installed via the `aws` extra and stays **optional** — a fresh clone runs all 406 tests
keyless. Load-bearing; do not promote it to a hard dependency.

## Traps already paid for

- **Three deployed numbers are not what they look like, and each is stated in code, not just docs.**
  (1) The online threshold is a fixed cut (`EARSHOT_THRESHOLD`, default 0.60), **not** the local
  budget-derived one — a streaming handler has no population to rank against, and the two will
  disagree. (2) Evidence-archive write-once is a conditional put, not Object Lock: it stops
  overwrite and redelivery, not a deliberate delete. The ledger's A6 guarantee is DynamoDB and is
  untouched — keep the two apart on stage. (3) The account tools are synthetic (`account_data:
  "synthetic"` on every case); there is no bank core feed.
- **A new IAM grant does nothing until the SSO session is reissued.** Use `--force`.
- **Agents that write files need `isolation: "worktree"`.** Untracked files + another agent's
  `git stash -u` nearly lost three of them.
- **Never delete an `__init__.py`.** Drops the guard and the suite silently.
- **Green stub tests are not proof.** Two provisioner bugs lived in the seam between our code and the
  SDK. Exercise tools against reality.
- **A test that assumes an optional dep is absent is broken.** Simulate absence, never assume it.
- **When something reads as AccessDenied, read the error *message*.** Two probe bugs and the Anthropic
  model-id prefix all masqueraded as permission problems.
