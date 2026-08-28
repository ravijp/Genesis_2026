# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-08-28** · commit `5b0633f` · branch `build/ear-on-every-call` · **559 tests**, guard at 114,
ruff clean, 21 UI routes

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. AWS: `AWS_PROFILE=genesis` works; `source tools/aws-login.sh --check` re-mints it, `--force` if
   a grant IT says is live still reads as denied (SSO caches grants in the role session).
3. `progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action

**Blocked on IT — one inline policy.** `zenon-poc-lambda-execution` has no SQS, DynamoDB or
Bedrock permissions, so the three deployed Lambdas are inert and neither queue is wired.
`iam:PutRolePolicy` was attempted and denied. **The policy JSON and the two reproducible error
lines are in `aws-infrastructure.md`, written to be pasted into a ticket.** Once it lands,
`tools/deploy.py --stage dev --no-dry-run` is idempotent and adds the two event source mappings.

**Not blocked, in order of value:**

1. **A bigger AT-57 sample.** The measured 4 / 10 is a direction, and a bad one: the agent called
   `genuine` nine times out of ten and dismissed none of five false alarms. 30–50 cases at ~$0.03.
2. **Routing accuracy.** Never measured; `verdict_accuracy.py` already collects `owning_team`. The
   streamed run shows the agent concentrating routing and sometimes returning `"none"`.
3. **`decisions.md` is owed two entries** (ask Ravi first): a tenant is a configuration and the
   team map is display-only so `OwningTeam` stays closed; and the console's primary user is the
   reviewer, not the agent on the call.
4. **A stopped design agent left an uncommitted worktree** at
   `.claude/worktrees/agent-ade2e23d7e6368e38` with a 479-line `ui/styles.css` rewrite — a
   coherent dark-first token system. Ravi's call whether to lift the palette or discard it.

**Delegate file-writing work with `isolation: "worktree"`.**

## State

One deployment (Northwind), framed as an integration: nine pipeline seams, six of them the
client's own systems. **One model, Haiku 4.5, for reader and investigator** (D-025); its verdict
accuracy on a multi-turn loop is **unmeasured**, so D-025's cost argument is not yet earned. Both
Lambdas run the **offline** provider today; `deploy.py --provider bedrock` flips it.

**CDK does not work here** (D-024). `tools/provision.py` and `tools/deploy.py` are the path, both
idempotent and dry-run by default. Do not re-litigate. CodeBuild stays blocked on the same
`iam:CreateRole` gap. `boto3` stays **optional** — a fresh clone runs every test keyless.

## Traps already paid for

- **Two thresholds exist and disagree on purpose.** Stream and `aws/ingest.py` use a fixed cut;
  `earshot investigate` uses a budget-derived top-K. A streaming consumer has no population to
  rank against. Both are labelled on their own screen — never merge them on stage.
- **`stream.py` stays on the separation-guarded surface only because `cli.stream_inputs()` hands
  it the conversations, the `ToolContext` factory and the account snapshot.** Re-add `generate()`
  there and the guard fails, correctly. The exemption list is capped at three by its own test.
- **The account header must take `financial_state`, never `latent_risk`.** The latter is a
  function of how much evidence was planted, so anything given it recovers `Stratum` without
  reading a word. This repo got that wrong once; the wiring is now pinned, not just the statistics.
- **Narration must never share the ledger reader's extractor.** 54 prefix reads counted as 54
  conversations divides the same money by nine times the work.
- **The final turn-by-turn read must equal the batch read byte for byte** — that is what makes the
  animated belief the belief that was appended.
- **A warm reader cache makes a "live" run a replay.** `--serve` names the cache mode in the LIVE
  badge; `EARSHOT_CACHE_MODE=off` forces new calls.
- **One response cache per provider.** A keyed Bedrock run once appended Haiku completions into the
  pinned Sonnet demo cache the README quotes.
- **The reader is named after the model that ANSWERED**, not the one requested.
- **`outcome is not None` is always true.** `Outcome.NONE` is the no-outcome value.
- **A measurement drawn from the top of the queue cannot be wrong in the direction that matters.**
- **Anything verified against a stub is unverified.** Exercise tools against reality.
- **A Windows-built zip cannot run on Lambda** — the build cross-compiles; do not simplify it.
- **PITR does not enable immediately after `create_table`**; without the retry it lands DISABLED.
- **When something reads as AccessDenied, read the error *message*.** Several were not.
- **A case id contains `#`.** Every UI link percent-encodes it.
- **Never delete an `__init__.py`.** Drops the guard and the suite silently.
- **Agents that write files need `isolation: "worktree"`**, and `cd` into one and stay there and
  your next commit lands on its throwaway branch. Verify `pwd` before committing.
