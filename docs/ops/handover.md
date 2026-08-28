# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything. Rewritten
in place at each handover. **Keep it under ~60 lines** — it loads into every conversation. It is a
baton, not a history: next action, live blockers, traps already paid for. History goes in
`progress.md` or git.

**2026-08-28** · commit `1c21c19` · branch `build/ear-on-every-call` · **557 tests**, guard at 114, ruff clean

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. AWS: `AWS_PROFILE=genesis` works today; `source tools/aws-login.sh --check` re-mints it, `--force`
   if a grant IT says is live still reads as denied (SSO caches grants in the role session).
3. `docs/ops/progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action — the IT ask, then a bigger sample

**The demo layer landed 2026-08-28** (`1275f95` → `1c21c19`): `earshot stream`, `read_live.py`,
`tenants.py`, and the demo UI screens. Conversations arrive in global day order; the reader is
re-asked after each customer turn so a belief is watched forming (3 withdrawn, 1 requoted in real
output); one deployment, framed as an integration into a client's stack with six of nine pipeline
stages marked as theirs. Keyed on Bedrock: $0.469 total, cached so it replays keyless.
`--serve --narrate-live` does the turn-by-turn live. `ui/README.md` is the operator's guide.

**Two agents were in flight at this handover** — an opus UI design pass (worktree) and research into
retail-banker desktop conventions. The intent: product screens should read as *our panel inside the
client's console*, a labelled stand-in and never a clone of a real vendor's branding, with the
stream and retro screens kept as the demo's explanatory half. If neither landed, that is the
next action.

**Everything else buildable is built.****Everything else buildable is built.** W1, W4, W7, W8, W10, W11 and the reviewer API are done; AWS is
provisioned, all three Lambdas are deployed (zip sha `8323ff7cd3ca`), six CloudWatch alarms exist,
and the first keyed runs have produced real numbers. What is left needs either IT or more money.

**Blocked on IT — one inline policy.** `zenon-poc-lambda-execution` has no SQS, DynamoDB or Bedrock
permissions, so the deployed handlers are inert and neither queue is wired.
`iam:PutRolePolicy` was attempted and denied; `iam:SimulatePrincipalPolicy` is denied too. **The
policy JSON and the two reproducible error lines are in `aws-infrastructure.md`, written to be
pasted into a ticket.** Once it lands: `tools/deploy.py --stage dev --no-dry-run` is idempotent and
will add the two event source mappings it could not create.

**Not blocked, in order of value:**

1. **A bigger AT-57 sample.** The measured 4 / 10 is a direction, not an estimate — and the
   direction is bad: the agent called `genuine` nine times out of ten and dismissed none of the
   five false alarms. 30–50 cases at ~$0.03 each says whether that holds. Then try a better prompt
   or a stronger model; D-025's cost argument for Haiku is not earned until it does.
2. **Routing accuracy** — which team a case is sent to. Never measured, and `verdict_accuracy.py`
   already collects `owning_team`.
3. **The UI's write path**, once the API is reachable from a browser. A static page cannot sign an
   `AuthType=AWS_IAM` Function URL, so this needs an auth decision, not just the IAM fix.

**Delegate file-writing work with `isolation: "worktree"`.**

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
- **A measurement drawn from the top of the queue cannot be wrong in the direction that matters.**
  The first keyed investigator run scored 8 / 8 and meant nothing: no negative in the sample.
  `tools/verdict_accuracy.py` samples both arms, and the real answer is 4 / 10.
- **`outcome is not None` is always true.** `Outcome.NONE` is the no-outcome value. Use
  `evals._outcome_customers`, or a whole arm silently disappears.
- **One response cache per provider.** A keyed Bedrock run appended Haiku completions into the
  pinned Sonnet demo cache the README quotes; only the test pinning that file's contents caught it.
- **The reader is named after the model that ANSWERED**, not the one requested — `bedrock.py`
  substitutes its own default for `base.DEFAULT_MODEL` by design, and the first keyed run was
  logged under the wrong model name because of it.
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
- **There are now two thresholds and they disagree on purpose.** The stream and `aws/ingest.py`
  use a fixed cut; `earshot investigate` uses a budget-derived top-K. A streaming consumer has no
  population to rank against. Both are labelled on their own screen — never merge them on stage.
- **`stream.py` stays on the separation-guarded surface only because `cli.stream_inputs()` hands
  it the conversations and the `ToolContext` factory.** Re-add `generate()` there and the guard
  fails, correctly. The exemption list is at three and `test_evaluation_exemptions_stay_small`
  caps it.
- **A warm reader cache makes a "live" run a replay.** `--serve` names the cache mode in the LIVE
  badge for exactly this reason; `EARSHOT_CACHE_MODE=off` forces new calls. A live badge over
  cached completions is the one dishonest pixel the demo could have had.
- **Narration must never run on the ledger's extractor.** `ExtractionTelemetry.conversations` is
  the denominator of the published cost-per-1,000 figure; 54 prefix reads counted as 54
  conversations divides the same money by nine times the work. Both narration paths build a
  second extractor instance for this reason.
- **The final turn-by-turn read must equal the batch read.** Byte-identical messages, so under a
  content-addressed cache they are one entry — that is the guarantee the animated belief is the
  belief that got appended. `test_read_live.py` pins it.
- **A case id contains `#`** (`make_case_id` joins its triple with it). Every UI link now
  percent-encodes it and `smoke.mjs` renders both forms.
- **Agents that write files need `isolation: "worktree"`.** Untracked files + another agent's
  `git stash -u` nearly lost three of them.
- **Never delete an `__init__.py`.** Drops the guard and the suite silently.
