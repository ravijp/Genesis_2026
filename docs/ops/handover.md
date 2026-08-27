# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything. Rewritten
in place at each handover. **Keep it under ~60 lines** — it loads into every conversation. It is a
baton, not a history: next action, live blockers, traps already paid for. History goes in
`progress.md` or git.

**2026-08-28** · commit `6611d07` · branch `build/ear-on-every-call` · **416 tests**, guard at 96, ruff clean

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. AWS: `AWS_PROFILE=genesis` works today; `source tools/aws-login.sh --check` re-mints it, `--force`
   if a grant IT says is live still reads as denied (SSO caches grants in the role session).
3. `docs/ops/progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action — unblock the deployed path, then measure

**AWS is real and the deployment is correct but inert.** 3 DynamoDB tables (PITR on), 3 SQS queues,
3 Lambdas from one zip, a Function URL for the API (`AuthType=AWS_IAM`). `GET /health` returns 200;
everything touching a store returns 500 and neither queue is wired, because
**`zenon-poc-lambda-execution` has no SQS, DynamoDB or Bedrock permissions** (its only policy is
`zenon-poc-s3-lambda`). `iam:PutRolePolicy` was attempted and denied — nothing changed — and
`iam:SimulatePrincipalPolicy` is denied too, so this is IT's. **The ask is copy-pasteable in
`aws-infrastructure.md`**: one inline policy plus the two reproducible error lines. Once it lands,
re-run `tools/deploy.py --stage dev --no-dry-run`; it is idempotent and will add the two event
source mappings it could not create.

Not blocked meanwhile: the **first keyed run** (both arms, 150 CFPB docs, ~$0.30, runs from the
laptop and the committed cache then replays keyless forever), **W11 observability**, **W4's spend
ceiling**, and the UI's write path once the API is reachable from a browser.

**W10 is done.** `ui/` — open `index.html`, no build step, all three beats render from a committed
artifact with zero AWS. Rebuild its data with `earshot investigate --customers 400 --limit 8` then
`tools/ui_fixture.py`. **Delegate file-writing work with `isolation: "worktree"`.**

## State

**One model, Haiku 4.5, for reader and investigator** (D-025); arm B deliberately undecided. Haiku's
verdict accuracy on a multi-turn loop is **unmeasured** — not a cost win until AT-57 says so. Both
Lambdas run the **offline** provider today: keyless, no spend, `deploy.py --provider bedrock` flips it.

**CDK does not work here** (D-024). `tools/provision.py` and `tools/deploy.py` are the path, both
idempotent and dry-run by default. Do not re-litigate. CodeBuild + CodePipeline stay blocked on the
same `iam:CreateRole` gap; `buildspec.yml` is parked. `boto3` stays **optional** (the `aws` extra) —
a fresh clone runs all 416 tests keyless, and that is load-bearing.

## Traps already paid for

- **Three deployed numbers are not what they look like, and each is stated in code, not just docs.**
  (1) The online threshold is a fixed cut (`EARSHOT_THRESHOLD`, default 0.60), **not** the local
  budget-derived one — a streaming handler has no population to rank against, and the two will
  disagree. (2) Evidence-archive write-once is a conditional put, not Object Lock: it stops
  overwrite and redelivery, not a deliberate delete. The ledger's A6 guarantee is DynamoDB and is
  untouched — keep the two apart on stage. (3) The account tools are synthetic (`account_data:
  "synthetic"` on every case); there is no bank core feed.
- **Anything verified against a stub is unverified.** A shared role that can be *passed* is not a
  role that can *do* anything (D-024 checked deployment and stopped); a test that *assumes* an
  optional dep is absent breaks the day it is installed; two provisioner bugs lived in the seam
  between our code and the SDK. Exercise tools against reality.
- **A Windows-built zip cannot run on Lambda.** `pydantic-core` is a compiled extension. The build
  cross-compiles (`--python-platform x86_64-manylinux2014 --only-binary :all:`); do not simplify it.
- **PITR does not enable immediately after `create_table`.** A table is ACTIVE seconds before its
  backups subsystem is; the gap reports as `ContinuousBackupsUnavailableException`, which reads like
  a permission problem. Without `provision.py`'s retry, a real run left PITR silently DISABLED.
- **When something reads as AccessDenied, read the error *message*.** Two probe bugs, the Anthropic
  model-id prefix and the SQS mapping failure all masqueraded as permission problems — and one of
  them actually was. Also: a new IAM grant does nothing until the SSO session is reissued (`--force`).
- **Agents that write files need `isolation: "worktree"`.** Untracked files + another agent's
  `git stash -u` nearly lost three of them.
- **Never delete an `__init__.py`.** Drops the guard and the suite silently.
