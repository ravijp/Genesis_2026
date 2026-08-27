# Build progress

**The build log.** One line per unit of work, newest section first. Append here; do not rewrite
history. `state-of-play.md` says where we are *now*; this says what has actually been done.

Status: `TODO` · `WIP` · `DONE` · `BLOCKED (who owns it)` · `DROPPED (why)`

---

## Deployment approach — settled 2026-08-25

**CDK is not usable. We deploy with boto3 scripts.** This is forced, not preferred.

`cdk bootstrap` needs three permissions we do not have, all tested:

| Needs | Result | Why it matters |
|---|---|---|
| `s3:CreateBucket` | DENIED | Our S3 grant is scoped to `agentic-trio` only; CDK wants its own assets bucket |
| `iam:CreateRole` | DENIED | CDK creates 4-5 deploy roles |
| `ecr:CreateRepository` | DENIED | ECR PowerUser gives push/pull to existing repos, not creation |

**What works instead, all verified by creating and deleting the real resource:**

- **Lambda deploy** by passing the existing role `arn:aws:iam::859430413223:role/zenon-poc-lambda-execution`.
  Created and deleted a function with it. This is the unlock — no new role needed.
- **DynamoDB** create + delete.
- **SQS** create + delete.
- **S3** put + get + delete objects in `agentic-trio`.
- **Bedrock** Haiku 4.5, Nova Lite, Nova Micro, Llama 3 8B all invocable.

**Consequences to carry forward:**

- **Zip deploys, not container images.** No ECR repo we can create; the two that exist belong to
  someone else. `Dockerfile` stays for local runs and for when ECR opens up, but the deployed artifact
  is a zip. This drops §3.5's "promote the same image digest" claim — say so rather than implying it.
- **One shared Lambda role**, not one role per function. §A.1's per-function least privilege becomes
  target-state. Name it on stage.
- **`infrastructure.md` §3.5's CDK commitment is now wrong.** Do not edit it yet; supersede it in
  `decisions.md` when the provisioning script lands.

---

## Work packages

| # | What | Status | Notes |
|---|---|---|---|
| W3 | Bedrock provider (`llm/bedrock.py`) | **DONE** | Converse both ways, Haiku 4.5 default, computed-not-charged cost, lazy client. 33 stub tests |
| W1 | Persist case fields | **DONE** | `case_record.py` — one serializer for the disk artifact and the DynamoDB item. Unblocks W10 |
| W4 | Spend cap in our own code | TODO | Budgets/Cost Explorer not granted. Put the ceiling next to `COST_CAP_PER_CASE_USD` |
| W5 | First keyed reader run | TODO | Needs W3. 150 CFPB docs, ~$0.30, both arms |
| W6 | Ledger + case DynamoDB stores | **DONE (code); tables not created** | `aws/stores.py` + `tools/provision.py`. Conditional writes, no delete path on the ledger, scoring delegated. 39 stub tests. Dry-run verified against the real account |
| W7 | Ingest path (SQS FIFO → handler) | **DONE** | `aws/ingest.py`. Partial batch failure, conditional append, scoring delegated. 18 tests, no AWS |
| W8 | Investigate path | **DONE (code)** | `aws/investigate.py` + `aws/transcripts.py`. Loop unchanged, score recomputed not trusted, account data labelled synthetic. 29 tests |
| W9 | CI/CD | BLOCKED (IT) | CodeBuild + CodePipeline denied. `buildspec.yml` is written and parked, ready to run |
| W10 | Reviewer UI, 3 screens | **TODO — unblocked, next** | W1 done, and `aws/api.py` now serves the five reads + one write it needs. Whole client-facing axis |
| W11 | Observability (EMF) | TODO | CloudWatch granted; no SNS, so alarms target EventBridge → Lambda |
| W12 | Sweep runner | DROPPED for now | Fargate needs VPC subnets; keep the sweep local |

## Blocked, and who owns it

| Item | Owner | Ask |
|---|---|---|
| **SQS/DynamoDB/Bedrock on `zenon-poc-lambda-execution`** | **IT (Vikash)** | **NEW 2026-08-28, and now the blocker.** One inline policy on that role. Without it the three deployed Lambdas are inert and neither queue can be wired. Exact actions in `aws-infrastructure.md` |
| CodeBuild + CodePipeline | **IT (Vikash)** | Scope to `earshot-*`, or he creates the project + pipeline |
| Bedrock invocation logging | IT (Vikash) | In progress, not blocking |
| S3 Object Lock | IT, Support case | Off, unchangeable now. Evidence write-once degrades to IAM. Accept and state it |

**Do NOT ask for these — we do not need them:**

| Not asking for | Why not |
|---|---|
| `iam:CreateRole` | **We never needed it.** Lambdas deploy by *passing* the existing role `zenon-poc-lambda-execution`; verified by creating and deleting a real function. Asking for role creation is a broad grant to avoid a script we can write in a day. |
| `s3:CreateBucket` | `s3://agentic-trio` is the team's provisioned bucket and object read/write works. Prefixes (`dev/`, `demo/`, `evidence/`, `artifacts/`) do the rest. |
| `ecr:CreateRepository` | Zip deploys instead of container images (D-024). Costs us the "same digest promoted" claim, which we retire honestly. |
| Claude Sonnet 4.5 / the Anthropic form | **No longer blocking** (D-025). Haiku 4.5 does both jobs and is already invocable. Worth filing eventually; nothing waits on it. |

## Log

**2026-08-28 (AWS is real)** · **Provisioned and deployed, on Ravi's go-ahead.** 3 DynamoDB tables
(PITR on, no TTL), 3 SQS queues with DLQ redrive, and all three Lambdas live on python3.13 from one
zip (sha `532a888f9bf4`), each passing `zenon-poc-lambda-execution`. Reviewer API on a Function URL
with `AuthType=AWS_IAM`. `tools/deploy.py` is the deploy path, same shape as `provision.py`.

**Two real bugs, both invisible to any stub test:**

1. **PITR silently did not enable.** `create_table` + the `table_exists` waiter returns while the
   continuous-backups subsystem is still catching up, and DynamoDB says
   `ContinuousBackupsUnavailableException` — which reads exactly like a permission problem. The first
   real run left all three tables with PITR **DISABLED** while reporting the tables created. Fixed
   with a bounded retry on that one error code; a second run converged 13/13.
2. **A Windows-built zip cannot run on Lambda.** `pydantic-core` is a compiled extension, so the
   naive `uv pip install --target` vendors a `.pyd`. The build now cross-compiles
   (`--python-platform x86_64-manylinux2014 --python-version 3.13 --only-binary :all:`).

**And one finding that changes the critical path: D-024 verified that the shared role can be
*passed*, not that it can *do* anything.** `zenon-poc-lambda-execution` has one attached policy,
`zenon-poc-s3-lambda`, and no inline policies — so no SQS, no DynamoDB, no Bedrock. Neither event
source mapping could be created (*"the function execution role does not have permissions to call
ReceiveMessage on SQS"*) and `GET /cases` on the deployed API returns 500 with `ClientError`.
`GET /health` returns 200, which proves the artifact and the code are fine. **The deployment is
correct and inert.** New IT ask, small and precise; exact actions in `aws-infrastructure.md`.

Incidentally proved in production: the API's "a 500 carries no stack trace" guarantee. The first
real error returned `{"error": "internal error"}` and put the detail in the log.

**2026-08-28 (end of session)** · **`aws/api.py` — the reviewer API.** Five reads (ranked queue,
one case, its reviews, a customer's standing ledger, the transcript behind a quote) and one write.
406 tests (+27), ruff clean. **All three Lambda handlers now exist**; the end-to-end path closes in
code, with nothing created in AWS.

Four choices the tests hold rather than the prose:

- **The write annotates and cannot mutate evidence.** infrastructure.md Q3 — reduce the score,
  suppress the customer, or only annotate — is answered "only annotate". A test reads the case
  before and after a dismissal and compares the evidence chain.
- **No endpoint contacts anyone, and a test asserts the absence.** HITL here is enforced by there
  being no outbound surface. If that test ever has to change, the entry's central safety claim has
  changed with it.
- **CORS is off unless `EARSHOT_ALLOWED_ORIGIN` is set.** A default of `*` publishes a reviewer's
  case queue to any page a browser loads, and a default nobody set is a default nobody reviews.
- **A 500 carries no stack trace.** A traceback in a response body names the tables.

The action set is closed (`approve`/`dismiss`/`route`) because `update_status` writes straight into
the GSI partition key — a free-text status would silently create a queue nothing lists. A dismissal
with no reason is refused: those are the rows anyone will actually want to read later.

**2026-08-28 (later still)** · **W8 done — `aws/investigate.py`, plus `aws/transcripts.py`.**
379 tests (+35), ruff clean. Three things surfaced that the work package did not name:

1. **W7 had a hole: the investigator had nothing to read.** The ledger stores signals, not
   conversations, and `unresolved_evidence()` rejects any decision whose citations do not resolve
   against a transcript. Deployed, the loop would have burned its whole retry budget rejecting its
   own decisions and landed a case saying "insufficient evidence" about a customer with plenty. So
   `transcripts.py` owns the wire format and an S3 archive, and ingest now archives **before** it
   extracts — a signal whose transcript is missing is unrecoverable, a transcript with no signal
   costs kilobytes.
2. **Write-once degrades and the code says so.** A.1 line 13 wants Object Lock in compliance mode;
   it must be enabled at bucket creation and `s3://agentic-trio` was not. The substitute is a
   conditional put (`IfNoneMatch="*"`), which stops overwrite and redelivery but not a deliberate
   `DeleteObject`. Say the smaller thing on stage. **The ledger's A6 guarantee is untouched** and
   must not be merged with this one.
3. **There is no bank core feed, so the account tools are fiction — and each case now says so.**
   `core/accounts.py` needs a `latent_risk`; locally that is the corpus's `financial_state`.
   Deployed it is a SHA-256 draw from the customer id (stable per customer, derived from nothing
   real) and every case carries `account_data: "synthetic"`. A single constant instead would make
   every customer's account identical, which is a worse thing to put on a screen. **This is the
   seam a real feed replaces.**

Also: the queue message's score is never trusted. A conversation can land between the crossing and
the investigation, so the score is recomputed from the ledger and the message's copy is used only
to report drift.

**2026-08-28 (later)** · **W7 done — `aws/ingest.py`.** SQS record → `Conversation` → `extract()` →
conditional append → reload → unchanged `SignalLedger` → threshold → enqueue. 344 tests (+18), ruff
clean. Three choices worth carrying:

- **`batchItemFailures`, not a raised exception.** A raise redelivers the whole batch and re-runs
  every extraction in it — with a model reader that is real money spent to punish one malformed
  neighbour.
- **The online threshold is a fixed cut (`EARSHOT_THRESHOLD`, default 0.60), not the local one.**
  `cli.py:_queue` derives its threshold from a review budget over a whole population; a streaming
  handler has no population snapshot. The two are different quantities and will disagree about
  whether a given customer crossed. Stated in the module docstring rather than smoothed over.
- **A crossing that stays crossed re-investigates on every later conversation.** Bounded by
  conversation volume, one investigation each time. It does not multiply cases — `make_case_id`
  keys on the first crossing day — but it is a cost the demo should not pretend away.

The tests assert the design claims on the deployed path, not just the plumbing: never-discard
(a sub-threshold signal is retained and still counts later), accumulation (0.270 and 0.146 alone,
0.459 together, cut at 0.35), and no second scorer (the handler's number equals an in-memory
`SignalLedger` over the same signals, bit for bit).

**2026-08-28** · **W1 done.** `src/earshot/case_record.py`: one `case_record()` builds both the
`earshot investigate` artifact and the DynamoDB `CASES` item, so the reviewer UI renders either and
neither can drift from the other. `cli.py` was writing `decision` and `trace` only. 323 tests
(315 → +7 unit, +1 end-to-end on the artifact), guard 81 → 84 by glob, ruff clean.

Two defects the ticket's own wording would have shipped:

1. **The evidence chain must come from the customer TODAY, not from `open_case()`.** A `Case` carries
   the evidence known at the crossing, so building the record from it freezes the retro chain on the
   opening day — the "we re-read March in light of July" beat would render empty for exactly the
   customers who kept accumulating, which are the ones the entry is about. Caught by a test asserting
   three evidence rows and getting one, not by review.
2. **A case has two scores and they are not interchangeable.** The crossing-day score and the score
   today differ under decay. One field for both either ranks a faded case at its opening-day seat
   forever, or loses the crossing. The record carries `score` (today, what the GSI ranks on) and
   `score_at_open`, named apart. `CaseStore.put_case` now ranks the queue on the current score,
   matching what `cli.py:_queue` already documented as the question it asks.

Verified against a real artifact rather than asserted: `CUST-0006#life_event#000123` renders four
evidence rows, day 39 supporting 0.100 when it arrived and 0.875 now (+0.775), all load-bearing.

**2026-08-25 (late)** · W3 and W6 built by two parallel subagents: `llm/bedrock.py`, `aws/stores.py`,
`tools/provision.py`, 72 new stub tests. Suite 236 → 312; separation guard 75 → 81 by glob discovery,
with no edit to the test. Provisioner dry-run verified against the live account: 3 tables, 3 queues
with DLQ redrive, 4 PARKED rows.

Three defects found by review rather than by the tests, all worth remembering:
(1) SQS reports an absent queue with a wire code that differs from botocore's exception class name, so
the most ordinary first-run case crashed; (2) PITR was probed on tables dry-run had not created,
printing FAILED TableNotFoundException three times — which reads exactly like a permission problem;
(3) the missing-boto3 test *assumed* boto3 was absent and flipped to failing once `uv sync --extra aws`
ran. All three lived where stubs are blind.

**Process failure:** the two agents shared one working tree. One ran `git stash -u` for a clean
baseline and swept the other's three untracked, half-written files back to HEAD. Both recovered, by
luck. Rule now in CLAUDE.md and working-agreements §8: any agent that writes files gets
`isolation: "worktree"`.

**2026-08-25** · Branch prepared for the AWS build. Repo reorg (D-023), build scaffolding,
`.claude/settings.json` approval tiers, duplication and dead-code pass, one-command AWS login.
IT fixed S3 object ARNs, CloudFormation, ECR, X-Ray, ECS: probe went 23/34 → 30/34.
`build/ear-on-every-call` pushed to CodeCommit. CDK ruled out; boto3 deploy path proven.
