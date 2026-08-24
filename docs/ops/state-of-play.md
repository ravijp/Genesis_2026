# State of play

**Updated 2026-08-25.** Rewritten in place every working session — **never appended to**. Hard cap:
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
investigator agent producing case files with cited evidence. **236 tests**, ruff clean.

**AWS is provisioned and reachable.** Account `859430413223`, permission set `agentic-trio`,
**us-east-1** (confirmed — the CodeCommit host says so), bucket `s3://agentic-trio`, repo
`agentic-trio`. Coordinates and setup: `aws-infrastructure.md`.

**The AWS CLI is not a blocker — that was wrong and is corrected.** boto3, `npx cdk` and
`git-remote-codecommit` all read credentials from the environment. Only `aws sso login` needs the v2
CLI. Use the no-`@` CodeCommit URL (`codecommit::us-east-1://agentic-trio`) until SSO exists.

**Branch is prepared for the build.** `[dependency-groups] infra` (CDK cannot leak into the Lambda
image), `[project.optional-dependencies] aws` (a fresh clone stays boto3-free), `Dockerfile`,
`.dockerignore`, `buildspec.yml`, `src/earshot/aws/`, `infra/`, `ui/`. Adding `earshot/aws/` took the
separation guard 72 → 75 tests **with no edit to the test** — the deployed decision path is guarded
by construction.

## Blocked, and on what

- **Four granted-list gaps, none of them fatal, all needing a substitution.** **CloudFormation** is not
  granted and CDK deploys through it — verify before the CDK commitment in §3.5 is load-bearing;
  `cdk bootstrap` also wants its own bucket, ECR repo and IAM roles. **VPC/EC2** is not granted, so
  ECS Fargate cannot launch (it needs a subnet) — substitute CodeBuild for the sweep, or keep it local.
  **SNS** is not granted — alarm targets become EventBridge → Lambda. **Budgets/Cost Explorer** are not
  granted — put the spend ceiling in our own code beside `COST_CAP_PER_CASE_USD`, which is the A9
  argument applied to cost and lives in the repo a judge reads.
- **Object Lock on `agentic-trio` is unverified and irreversible.** `aws s3api
  get-object-lock-configuration --bucket agentic-trio`. If it is off, write-once on the evidence archive
  is gone permanently. **A6's ledger guarantee is unaffected** — that is DynamoDB, no TTL, no delete
  permission. Do not conflate them on stage.
- **Zero model calls have ever been made.** The reader has no accuracy figure, and must not be given one
  until a keyed run prints it.

## Next, in order

1. **Bedrock provider** (`src/earshot/llm/bedrock.py`). `uv add --optional aws boto3`; Converse
   translation both ways; price table labelled "computed from published prices", never "charged" (G1).
   Absorbs the dead OpenAI package — one provider now serves both reader arms.
2. **Persist case fields** (W1). `cli.py:531` writes `decision` and `trace` and drops `ctx.score`,
   `ctx.signal_type`, `ctx.threshold` and the retro fields. **All three reviewer-UI beats are
   unrenderable from disk until this lands.** The dangerous shortcut is regenerating the corpus from
   `manifest.seed` — it puts `stratum`/`outcome`/`latent_risk` behind a client-facing screen.
3. **First keyed run**, both arms, 150 CFPB docs, ~$0.30. Converts four "not measured" deliverables into
   numbers. Commit the response cache and it replays keyless forever.
4. **Ledger + case stores → ingest → investigate → reviewer UI** (W6 → W7 → W8 → W10).

**Arm B is deferred, deliberately.** GPT-4o-mini is unreachable; any second Bedrock family works and
the choice is ~zero incremental work once the provider exists. Candidates: Nova Lite, Llama, Mistral.
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
