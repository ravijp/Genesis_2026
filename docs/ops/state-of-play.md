# State of play

**Updated 2026-08-28.** Rewritten in place every working session — **never appended to**. Hard cap:
this file fits on one screen. If something will not fit, it belongs in `decisions.md` (a choice),
`working-agreements.md` (a rule), or Jira (work). Anything historical belongs in git.

**Fresh session, read in this order:** this file → `decisions.md` → `working-agreements.md` →
`../../README.md` → `../architecture/architecture.md`. Then `../architecture/infrastructure.md` for the
AWS design and `aws-infrastructure.md` for what is actually provisioned.

---

## Where we are

**The decision is made: everything runs on AWS.** Whatever works ships to AWS, pushes to CodeCommit,
and is tracked on the AT board. Team size and calendar are not treated as constraints — Claude Code is
building it. Next gate **2026-09-07**. The 08-10 check-in and the 08-24 combined demo have passed; no
artifact records what 08-24 showed.

The system runs end to end with zero API keys: dataset generation → extraction → per-customer ledger →
investigator agent producing case files with cited evidence. **406 tests**, ruff clean.

**The AWS layer now exists in code.** `llm/bedrock.py` (Converse, Haiku 4.5, computed-not-charged cost),
`aws/stores.py` (DynamoDB ledger/cases/reviews, conditional writes, no delete path on the ledger) and
`tools/provision.py` (idempotent, dry-run by default). All stub-tested with zero AWS access. **No table
has been created yet** — that needs Ravi's go-ahead, since it bills.

**A case now survives the process that produced it (W1, 2026-08-28).** `case_record.py` builds the
disk artifact and the DynamoDB item from one function, so the reviewer UI renders either and they
cannot drift. A case carries **two moments, named apart**: `score_at_open`/`opened_on_day` from the
crossing, and `score`/`as_of_day`/`evidence` from the customer today. Merging them is not a style
choice — take the score from the crossing and a faded case keeps its opening-day seat at the top of
the queue; take the evidence from the crossing and the retro chain freezes on the opening day, which
empties the beat for every customer who kept accumulating.

**All three Lambda handlers exist, and the end-to-end path closes in code (2026-08-28).**
`aws/ingest.py` (archive → extract → conditional append → re-score → threshold → enqueue),
`aws/investigate.py` (crossing → unchanged `investigate()` loop → `CaseStore`), `aws/api.py` (five
reads + one write). Plus `aws/transcripts.py`, which W7 needed and did not have: the ledger stores
signals, not conversations, so without an archive every deployed citation would be unresolvable.
Three things to carry:

- **The online threshold is a fixed cut (`EARSHOT_THRESHOLD`, default 0.60), not the budget-derived
  local one.** A streaming handler has no population to rank against. The two will disagree about
  whether a given customer crossed; do not present them as one number.
- **Write-once on the evidence archive is a conditional put, not Object Lock.** It stops overwrite
  and redelivery, not a deliberate `DeleteObject`. The ledger's A6 guarantee is DynamoDB and is
  untouched — keep the two apart on stage.
- **The account tools are synthetic and every case says so** (`account_data: "synthetic"`). There is
  no bank core feed; `latent_risk` is a SHA-256 draw from the customer id. That is the seam a real
  feed replaces.

**AWS is provisioned and reachable.** Account `859430413223`, permission set `agentic-trio`,
**us-east-1** (confirmed — the CodeCommit host says so), bucket `s3://agentic-trio`, repo
`agentic-trio`. Coordinates and setup: `aws-infrastructure.md`.

**The AWS CLI is not a blocker — that was wrong and is corrected.** boto3, `npx cdk` and
`git-remote-codecommit` all read credentials from the environment. Only `aws sso login` needs the v2
CLI. Use the no-`@` CodeCommit URL (`codecommit::us-east-1://agentic-trio`) until SSO exists.

**Deployment is boto3, not CDK** (D-024) — bootstrap needs three permissions we do not have. Lambdas
deploy by passing the existing `zenon-poc-lambda-execution` role. Zip artifacts, not images.

**Branch is prepared for the build.** `[dependency-groups] infra` (CDK cannot leak into the Lambda
image), `[project.optional-dependencies] aws` (a fresh clone stays boto3-free), `Dockerfile`,
`.dockerignore`, `buildspec.yml`, `src/earshot/aws/`, `infra/`, `ui/`. Adding `earshot/aws/` took the
separation guard 75 → 81 tests **with no edit to the test** — the deployed decision path is guarded
by construction.

## Blocked, and on what

- **CodeBuild + CodePipeline — the only real IT ask left.** `buildspec.yml` is written and parked. It is
  blocked by the same `iam:CreateRole` gap as the Lambda roles: the one role we can pass is scoped to
  Lambda's trust policy, not CodeBuild's.
- **Object Lock on `agentic-trio` is OFF**, verified, and not changeable without an AWS Support case. So
  write-once on the evidence archive degrades from structural to an IAM convention. **A6's ledger
  guarantee is unaffected** — that is DynamoDB, no TTL, no delete permission, and `LedgerStore` has no
  delete method at all. Do not let the two claims merge on stage.
- **No SNS, no Budgets, no Cost Explorer.** Alarms target EventBridge → Lambda; the spend ceiling goes
  in our own code beside `COST_CAP_PER_CASE_USD`, which is the A9 argument applied to cost and lives in
  the repo a judge reads.
- **No VPC subnets**, so ECS Fargate cannot launch. The sweep stays local, where a judge can reproduce
  it with no account.
- **Zero model calls have ever been made against a corpus.** The reader has no accuracy figure and must
  not be given one until a keyed run prints it. Bedrock connectivity is proven; reader *quality* is not.

## Next, in order

1. **Reviewer UI** (W10) — the whole client-facing axis of a Track A entry, and now fully unblocked.
   `aws/api.py` serves the three screens; `earshot investigate`'s artifact has the same shape offline
   (`case_record()`), so the SPA can be built and demoed with no AWS at all. **Never regenerate the
   corpus from `manifest.seed` to fill a gap** — that puts `stratum`/`outcome`/`latent_risk` behind a
   client-facing screen, and tests now scan both the artifact and every API response for those names.
2. **Deploy the three handlers** — zip, passing `zenon-poc-lambda-execution` (D-024). Needs the
   tables and queues, which bill: Ravi's call.
3. **First keyed run**, both arms, 150 CFPB docs, ~$0.30. Converts four "not measured" deliverables
   into numbers. Commit the response cache and it replays keyless forever.
4. **Observability** (W11) and the spend ceiling in our own code (W4).

**Not yet done and it bills:** `tools/provision.py --stage dev --no-dry-run` creates the real tables and
queues. Dry-run is clean. Needs Ravi's go-ahead.

**One model, Haiku 4.5, for reader and investigator** (D-025). Sonnet is dropped, which *unblocked* the
investigator — it needed an Anthropic use-case form and Haiku does not. **Haiku's verdict accuracy on a
multi-turn tool loop is unmeasured**; not a cost win until AT-57 says so. Arm B stays deferred:
Nova Lite and Llama 3 8B are both invocable and the choice is ~zero work now the provider exists.
**The brief never required two vendors** — it says "a comparison model runs through the same harness"
(`../sources/submission-ear-on-every-call.md:86-87`). That obligation was self-imposed and is retired.

## Known-weak, stated rather than hidden

- **The extractor barely works on language it did not write.** 0.0357 strict recall (4 / 112) on real
  CFPB narratives against 0.681 (496 / 728) on ours; three of four signal types exactly zero. Blind
  -authored synthetic fragments give 0.0353 (22 / 624) — the same number from two directions, which
  closes the genre-mismatch escape route. **The published 0.681 measures how much pass A and pass B were
  co-developed, not what the extractor can read.**
- **Two cheaper arms beat us on the pre-registered stratum at 30 seeds**: `stateless-top2` and
  `window3-top2`, both `7-21-2`, `p=0.013`. `window3-top2` also holds us to a tie on concentrated arcs.
  What never-discard buys over a three-conversation window is **unproven**. The honest claim is
  *aggregation beats no aggregation*, not *memory beats detection*.
- The ledger **loses** on concentrated arcs (119/629 vs 180/629, p=0.039). Published. It is a trade.
- Decay earns something that is not recall: 673 distinct scores against a plain count's 6, so 0.0% of
  its alert queue is decided alphabetically against 55.1%.
- **Two of four trajectories can never carry more than 4 signals**, bounding every published number —
  fragments are planted without replacement and the scarcest pool holds 4 while arcs run to 5.
- The cost cap bounds cumulative spend, not a single anomalous call. Documented, with a test.
- Agent verdict accuracy, cost per 1,000 conversations and p50/p95 latency are not measured.
- **Cost model has two known errors**: `B.3:655` says $1.24 where the arithmetic gives $1.12, and §1.2
  ("55–80×") contradicts B.4 ("55–140×") where B.3's own totals give **82–144×**. Both understate the
  strongest feasibility number in the entry.
- **The demo cache is invalidated by the provider move regardless of model pinning** — it was recorded
  through OpenRouter, so §1.5's pinning rationale survives only on cost comparability. Re-record on
  Bedrock, or say plainly that the demo and deployed investigators are different providers.
- **No AT ticket covers any of W1–W11.** The board predates `infrastructure.md`. 45 issues live, 28 In
  Progress, 0 Resolved. Sprints *are* enabled (board 209, `AT Sprint 1`, unstarted) — earlier notes
  saying otherwise are wrong.
- Adversarial review is **frozen at six rounds**; open defects are listed in git history and not yet
  written up as `known-issues.md`. Do not open an unbounded round 7.
