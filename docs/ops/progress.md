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
| W8 | Investigate path | BLOCKED (Ravi) | Needs Sonnet 4.5 → Anthropic use-case form |
| W9 | CI/CD | BLOCKED (IT) | CodeBuild + CodePipeline denied |
| W10 | Reviewer UI, 3 screens | TODO | Needs W1 only. Whole client-facing axis |
| W11 | Observability (EMF) | TODO | CloudWatch granted; no SNS, so alarms target EventBridge → Lambda |
| W12 | Sweep runner | DROPPED for now | Fargate needs VPC subnets; keep the sweep local |

## Blocked, and who owns it

| Item | Owner | Ask |
|---|---|---|
| CodeBuild + CodePipeline | **IT (Vikash)** | Scope to `earshot-*` resources, or he creates project+pipeline |
| Claude Sonnet 4.5 | **Ravi** | One-time Anthropic use-case form. Blocks the investigator only |
| Bedrock invocation logging | IT (Vikash) | In progress, not blocking |
| S3 Object Lock | IT, Support case | Off, unchangeable now. Evidence write-once degrades to IAM |
| `iam:CreateRole`, `ecr:CreateRepository`, `s3:CreateBucket` | IT — **not yet asked** | Would restore CDK and per-function roles. Ask only if we want them |

## Log

**2026-08-25** · Branch prepared for the AWS build. Repo reorg (D-023), build scaffolding,
`.claude/settings.json` approval tiers, duplication and dead-code pass, one-command AWS login.
IT fixed S3 object ARNs, CloudFormation, ECR, X-Ray, ECS: probe went 23/34 → 30/34.
`build/ear-on-every-call` pushed to CodeCommit. CDK ruled out; boto3 deploy path proven.
