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
investigator agent producing case files with cited evidence, and a five-screen UI that opens from disk. **539 tests**, ruff clean.

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

**AWS is real, and the deployment is correct but inert (2026-08-28).** 3 DynamoDB tables with PITR
on, 3 SQS queues with DLQ redrive, 3 Lambdas on python3.13 from one zip (sha `532a888f9bf4`), and a
Function URL for the reviewer API at `AuthType=AWS_IAM`. `GET /health` returns 200 in 1.4s cold.
Everything touching a store returns 500 and neither queue is wired — see the IAM row below.
Account `859430413223`, permission set `agentic-trio`, **us-east-1**, bucket `s3://agentic-trio`.
Coordinates, the deployed resource table and the IAM ask: `aws-infrastructure.md`.

**The demo layer is built and paid for (2026-08-28).** `earshot stream` walks a book in **global
day order across all customers** — the arrival pattern, not a batch with a clock on it — and emits a
frame per conversation carrying what the reader found, the score before and after, the re-ranked
board, and the per-call cost and latency. `tenants.py` makes that three deployments: **a tenant is a
configuration** (own corpus, own half-lives, own fixed threshold, own names for the four canonical
`OwningTeam` slots), never a fork, and the team map is display-only so the model's decision contract
stays a closed `Literal`. Haiku 4.5 on Bedrock read all 460 conversations ($0.653, p50 ~1.1s, zero
unparsable) and worked 12 crossings ($0.412). Both are cached, so a fresh clone replays every screen
keyless. `--serve` runs the same loop over SSE on 127.0.0.1 for a genuinely-live stage demo.

Four things to carry about it, all of them on screen rather than in a caption:

- **No speech recognition exists in this system.** What replays is the arrival pattern; at 1× each
  frame is held for the reader's own measured latency. `manifest.asr` is `"none"` and the smoke test
  fails the build if it changes.
- **The stream threshold is a fixed cut**, mirroring `aws/ingest.py`. It is *not* the budget-derived
  one `earshot investigate` reports. They disagree about who crossed. Do not merge them on stage.
- **12 of 33 crossings were investigated**, four per tenant, to bound a re-record. The other 21 are
  listed unworked with the reason.
- **`stream.py` sits on the separation-guarded surface** because `cli.stream_inputs()` hands it the
  conversations and the `ToolContext` factory. It never holds a `Corpus`. The exemption list stayed
  at three.

**The reviewer UI exists and needs nothing (W10).** `ui/index.html` opens from disk — no npm, no
bundler, no network. Ranked queue, one case with its evidence chain, and the retro re-score, all
rendering the same objects the deployed API returns because both come from `case_record()`.

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

- **The blocker: `zenon-poc-lambda-execution` has no SQS, DynamoDB or Bedrock permissions.** One
  attached policy, `zenon-poc-s3-lambda`, no inline ones. So the three deployed Lambdas cannot reach
  anything and neither event source mapping can be created. `iam:PutRolePolicy` was attempted and
  denied (nothing changed); `iam:SimulatePrincipalPolicy` is denied too. **The exact policy JSON and
  the two reproducible error lines are in `aws-infrastructure.md`, written to be pasted into a
  ticket.** D-024 verified the role could be *passed*, not that it could *do* anything — the gap
  only surfaced when a handler had to read a table.
- **CodeBuild + CodePipeline — the other IT ask.** `buildspec.yml` is written and parked. It is
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
- **The agent does not discriminate (AT-57, measured 2026-08-28).** Ten crossings, five with a real
  outcome and five without: it called `genuine` nine times, caught 4 / 5 real cases and dismissed
  **0 / 5** false alarms, at mean confidence 0.90 on the wrong answers. **Overall 4 / 10.** So
  D-025's cost argument for Haiku is not yet earned — it is cheap and fast and it escalates
  everything. Until that changes the investigator adds routing and an audit trail, not filtering.
- **The ledger hands the agent a queue that is 78% false alarm.** Of 40 crossings at a 10% review
  budget, 9 have a real outcome and 31 do not. The recall table never reports this.

## Next, in order

1. **The IAM policy** (above). One ticket, and the end-to-end path closes on AWS.
2. **First keyed run**, both arms, 150 CFPB docs, ~$0.30. **Not blocked** — it runs from the laptop.
   Converts four "not measured" deliverables into numbers, and the committed response cache then
   replays keyless forever. This is the highest-value unblocked work.
3. **Observability** (W11, EMF) and the spend ceiling in our own code (W4).
4. **The UI's write path** (`POST /cases/{id}/reviews`), once the API is reachable from a browser.
   A static page cannot sign an `AuthType=AWS_IAM` Function URL, so this needs a decision about how
   the SPA authenticates — not just the IAM fix. `--serve` does **not** close this: it serves a demo
   stream from local state and has no write route by design.
5. **Routing accuracy**, now that there is data to measure it against. The streamed run shows Haiku
   sending 3 of Northwind's 4 cases to one team and leaving 2 of Meridian's 4 `unrouted`. That is a
   direction, not an estimate, and `verdict_accuracy.py` already collects `owning_team`.

**One model, Haiku 4.5, for reader and investigator** (D-025). Sonnet is dropped, which *unblocked* the
investigator — it needed an Anthropic use-case form and Haiku does not. **Haiku's verdict accuracy on a
multi-turn tool loop is unmeasured**; not a cost win until AT-57 says so. Arm B stays deferred:
Nova Lite and Llama 3 8B are both invocable and the choice is ~zero work now the provider exists.
**The brief never required two vendors** — it says "a comparison model runs through the same harness"
(`../sources/submission-ear-on-every-call.md:86-87`). That obligation was self-imposed and is retired.

## Known-weak, stated rather than hidden

- **The LEXICON barely works on language it did not write** — 0.0357 strict recall (4 / 112) on real
  CFPB narratives; three of four signal types exactly zero. The **model reader** scores 0.8214
  (92 / 112) on the identical gold set (measured 2026-08-28), so this is a fallback limitation, not
  a system one. It costs 8x the false-positive rate to get there: 0.1598 (78 / 488) against 0.0205,
  almost all of it `complaint_escalation` at 0.8072 (67 / 83).
- **The published 0.681 (496 / 728) on our own prose still measures how much pass A and pass B were
  co-developed, not what a reader can read.** Nothing in the keyed run touches that. Blind-authored
  synthetic fragments give 0.0353 (22 / 624) for the lexicon — the same number from two directions,
  which closes the genre-mismatch escape route.
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
- **Measured 2026-08-28:** reader $1.66 per 1,000 conversations (p50 1,244 ms / p95 2,212 ms);
  investigation $0.0289 per case (p50 17.6 s / p95 32.6 s); 0 / 10 evidence repairs; 10 / 10 loop
  exits `decided`. **Routing accuracy is still not measured**, and 10 cases is a direction rather
  than an estimate.
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
