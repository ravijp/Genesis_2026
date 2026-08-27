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
| W3 | Bedrock provider (`llm/bedrock.py`) | **TODO — next** | Unblocked. Converse both ways, price table labelled "computed". Absorbs the dead OpenAI package |
| W1 | Persist case fields | **TODO — next** | `cli.py` drops `ctx.score`, `signal_type`, `threshold`, retro fields. Blocks all three UI beats |
| W4 | Spend cap in our own code | TODO | Budgets/Cost Explorer not granted. Put the ceiling next to `COST_CAP_PER_CASE_USD` |
| W5 | First keyed reader run | TODO | Needs W3. 150 CFPB docs, ~$0.30, both arms |
| W6 | Ledger + case DynamoDB stores | TODO | Verified creatable |
| W7 | Ingest path (SQS FIFO → handler) | TODO | Needs W3, W6 |
| W8 | Investigate path | **TODO — unblocked** | D-025 moved the investigator to Haiku 4.5, which is invocable. No longer waiting on the Anthropic form |
| W9 | CI/CD | BLOCKED (IT) | CodeBuild + CodePipeline denied. `buildspec.yml` is written and parked, ready to run |
| W10 | Reviewer UI, 3 screens | TODO | Needs W1 only. Whole client-facing axis |
| W11 | Observability (EMF) | TODO | CloudWatch granted; no SNS, so alarms target EventBridge → Lambda |
| W12 | Sweep runner | DROPPED for now | Fargate needs VPC subnets; keep the sweep local |

## Blocked, and who owns it

| Item | Owner | Ask |
|---|---|---|
| CodeBuild + CodePipeline | **IT (Vikash)** | **The only real ask left.** Scope to `earshot-*`, or he creates the project + pipeline |
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

**2026-08-25** · Branch prepared for the AWS build. Repo reorg (D-023), build scaffolding,
`.claude/settings.json` approval tiers, duplication and dead-code pass, one-command AWS login.
IT fixed S3 object ARNs, CloudFormation, ECR, X-Ray, ECS: probe went 23/34 → 30/34.
`build/ear-on-every-call` pushed to CodeCommit. CDK ruled out; boto3 deploy path proven.
