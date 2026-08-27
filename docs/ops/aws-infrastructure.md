# AWS infrastructure — what exists, and how to reach it

**Authored 2026-08-24, resources recorded 2026-08-25.** The single operational record of our AWS
estate: every live coordinate, what has been granted, and how this machine authenticates. If you need
an account ID, a bucket name, a repo URL or a region, it is here and it is not duplicated elsewhere.

**This file is fact; [infrastructure.md](../architecture/infrastructure.md) is design.** That document
argues *why* the architecture is shaped as it is (numbered assumptions, rejected alternatives, cost
model) and is written to be attacked. This one records *what is actually provisioned* and changes
whenever something is created or granted. Keep the boundary: no rationale here, no live coordinates
there.

---

## Start here, every session

```powershell
pwsh -File tools/aws-login.ps1 -Check      # PowerShell
```
```bash
source tools/aws-login.sh --check          # Git Bash — SOURCE it, or AWS_PROFILE is lost
```

Logs in only if the current token is dead, prints who you are, then verifies every permission the
build needs. A browser opens for approval; nothing else is interactive.

**`-Force` / `--force` is the fix when IT grants a permission and you still get `AccessDenied`.**
SSO bakes grants into the role session, so a new IAM policy does nothing until the session is
reissued. Re-login is the only way to pick it up, and that has already caused one round of confusion.

The scripts also guard three things that fail confusingly hours later:

- **A static `AWS_ACCESS_KEY_ID` in the environment outranks the SSO profile** and is unset for you.
- **The CLI is absent from the PATH of shells opened before it was installed**, so the absolute path
  is used as a fallback.
- **Region drift** — the console opens on `ap-southeast-2` while every model ARN and price in the
  design assumes `us-east-1`.

## Live resources

Region **us-east-1** for everything below.

| Resource | Coordinate | Notes |
|---|---|---|
| **Account** | `859430413223` | Console shows it dashed (`8594-3041-3223`); AWS config wants 12 digits, undashed |
| **Permission set** | `agentic-trio` | Federated as `AWSReservedSSO_agentic-trio_<suffix>/rprakash@zenon.ai` |
| **S3 bucket** | `s3://agentic-trio` | One bucket. Appendix A rows 13–14 assume **two** (`earshot-evidence` with Object Lock, `earshot-artifacts` versioned) — see the caveat below |
| **CodeCommit** | `https://git-codecommit.us-east-1.amazonaws.com/v1/repos/agentic-trio` | Push via `codecommit://genesis@agentic-trio`, never the HTTPS URL — see Step 4 |
| **DynamoDB** | `earshot-dev-ledger` · `earshot-dev-cases` · `earshot-dev-reviews` | Created 2026-08-28. On-demand, PITR **on**, no TTL on any of the three |
| **SQS** | `earshot-dev-transcripts.fifo` · `earshot-dev-investigations` (+ `-dlq`) | Created 2026-08-28. Redrive to the DLQ at 3 receives |
| **Lambda** | `earshot-dev-ingest` · `earshot-dev-investigate` · `earshot-dev-api` | Deployed 2026-08-28, python3.13, zip sha `532a888f9bf4`, all passing `zenon-poc-lambda-execution`. **Inert — see the IAM gap below** |
| **Reviewer API URL** | `https://omqdmdwrekgdrkybgerq7ggkji0soujn.lambda-url.us-east-1.on.aws/` | Function URL, `AuthType=AWS_IAM`. `GET /health` returns 200; everything touching a store returns 500 until the role is fixed |
| **SSO start URL** | *still unknown* | The one value blocking `aws sso login`. IAM Identity Center → Dashboard → *Settings summary* → **AWS access portal URL** |

> **The region is confirmed, not assumed.** The CodeCommit host is literally
> `git-codecommit.`**`us-east-1`**`.amazonaws.com`, so the source of record already lives in us-east-1 —
> which is what D-022 chose on pricing and model-ARN grounds. The console opening on `ap-southeast-2`
> (Sydney) is cosmetic. These coordinates were previously scattered across
> [committee-requirements-email.md](../gates/committee-requirements-email.md) and
> [genesis-committee-comms.md](../sources/genesis-committee-comms.md); this table is now the one
> place to change them.

### The IAM gap that makes the deployment inert — found 2026-08-28

**`zenon-poc-lambda-execution` can be *passed*, but it cannot *do* anything of ours.** Its only
attached policy is `zenon-poc-s3-lambda`; there are no inline policies. So:

- `lambda:CreateEventSourceMapping` fails with `InvalidParameterValueException` — *"The function
  execution role does not have permissions to call ReceiveMessage on SQS"*. **Neither queue is
  wired to its handler**, so nothing flows end to end.
- Anything touching DynamoDB returns `ClientError`. Verified against the deployed function:
  `GET /health` → 200, `GET /cases` → 500 with `api.error ... ClientError` in the log.
- Bedrock invoke would fail the same way, which is why both handlers are deployed with the
  offline provider.

**D-024 verified deployability, not functionality**, and that distinction was not visible until a
handler actually had to read a table. The fix is one scoped inline policy on that role —
`sqs:ReceiveMessage`/`DeleteMessage`/`GetQueueAttributes` on the two `earshot-dev-*` queues,
DynamoDB `PutItem`/`GetItem`/`Query`/`UpdateItem` (**never `DeleteItem`** — A6) on the three tables
and the cases GSI, `s3:GetObject`/`PutObject`/`ListBucket` on the `evidence/` and `artifacts/`
prefixes, and `bedrock:InvokeModel`. We cannot write it ourselves: `iam:SimulatePrincipalPolicy` is
denied, so even asking "may I?" is denied. **This is a new IT ask, and it is small and precise.**

### Services granted

Bedrock · IAM · DynamoDB · S3 · Lambda · SQS · ECR · CodePipeline + CodeBuild · CloudWatch + X-Ray ·
API Gateway (HTTP API) · CloudFront + S3 static site · Cognito · SSM Parameter Store · Bedrock
Invocation Logging · ECS Fargate · EventBridge

**What that list does not contain, and what it costs us:**

- **Kinesis Data Streams** — §3.1's *target-state* event bus. Not granted. §3.1 already names **SQS
  FIFO** as the MVP substitute with `MessageGroupId = customer_id`, which preserves the per-customer
  ordering that makes `score_at_write` honest. What is lost is *replay*, and never-discard means we
  re-score history — so the target-state argument stands and must be presented as target state, not as
  built.
- **One S3 bucket, not two.** Object Lock is **OFF** on `agentic-trio` (verified 2026-08-25) and is not
  enablable after creation without an AWS Support case. So the evidence archive's write-once guarantee
  degrades from structural to an IAM convention — precisely the distinction A6 refuses to blur. Say so
  on stage rather than implying parity, the way §3.6 handles CloudFront-vs-bank-VPC. **A6's ledger
  guarantee is unaffected**: that is DynamoDB, no TTL, no delete permission, and DynamoDB is fully
  granted. Do not let the two claims merge.

### The S3 permission bug — a missing `/*`, not a missing policy

**Verified 2026-08-25.** The permission set's inline policy reads:

```json
{ "Effect": "Allow", "Action": ["s3:*"], "Resource": ["arn:aws:s3:::agentic-trio"] }
```

That ARN is the **bucket**. Object operations require the **objects** ARN, `arn:aws:s3:::agentic-trio/*`.
S3 treats those as different resources, so the split is exact and reproducible:

| Action class | Example | Result |
|---|---|---|
| Bucket-level | `ListBucket`, `GetBucketVersioning`, `GetBucketEncryption` | **works** |
| Object-level | `PutObject`, `GetObject`, `DeleteObject` | **AccessDenied** |

So this is a two-line correction to an existing policy, not a new grant. The fix is to list both ARNs:

```json
"Resource": ["arn:aws:s3:::agentic-trio", "arn:aws:s3:::agentic-trio/*"]
```

Worth asking for in exactly those terms — "add `/*` to the existing statement" is a far smaller ask
than "give us S3 access", and it is almost certainly an oversight rather than a policy decision.

## The principle

**Nothing secret is stored anywhere in this repository, and nothing needs recreating.** Credentials are
short-lived tokens minted by IAM Identity Center on demand. The repo holds only a *template* naming
where to get them ([.aws.config.example](../../.aws.config.example)) — no account ID, no key, no token.

The one long-lived secret the design previously required — an OpenAI API key
([infrastructure.md](../architecture/infrastructure.md) §3.4, Appendix A row 4) — **is no longer
needed.** Both model arms now go through Bedrock, which is IAM-authenticated. See D-022.

## What is stored, and where

| Item | Location | Secret? | In git? |
|---|---|---|---|
| SSO start URL, region, account, role name | `~/.aws/config` | No | No — template only |
| SSO bearer token | `~/.aws/sso/cache/*.json` | **Yes**, plaintext, short-lived | Never |
| STS role credentials | `~/.aws/cli/cache/*.json` | **Yes**, plaintext, ~1h | Never |
| Static access keys | *nowhere — deliberately* | — | Never |
| CodeCommit Git username/password | *nowhere — deliberately* | — | Never |

`~/.aws/` lives in your home directory, **outside** the repository, so it cannot be committed. The
patterns in [.gitignore](../../.gitignore) are belt-and-braces against a stray copy inside the repo;
they are verified by `git check-ignore`.

> The SSO token cache is **unencrypted JSON** on disk
> ([AWS SDK reference](https://docs.aws.amazon.com/sdkref/latest/guide/feature-sso-credentials.html)).
> It is a live credential until it expires. That is an accepted, documented AWS default — the mitigation
> is that it is short-lived and re-mintable, not that it is protected at rest.

## Do NOT use the two things you may already have

**1. The static key trio you were given** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`AWS_SESSION_TOKEN`). These expire and then need recreating, which is the exact problem SSO solves.
Worse, **environment variables outbid the SSO profile**: AWS CLI and boto3 both rank env vars *above*
any profile in `~/.aws/config`
([precedence docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)). If
those variables are set, your SSO profile is silently ignored and everything breaks the moment the
token lapses — with a confusing `ExpiredToken` rather than anything pointing at the real cause.

So before anything else, make sure they are not set — including persisted user-level vars:

```powershell
# session
Remove-Item Env:AWS_ACCESS_KEY_ID, Env:AWS_SECRET_ACCESS_KEY, Env:AWS_SESSION_TOKEN -ErrorAction SilentlyContinue
# persisted (returns nothing if clean)
[Environment]::GetEnvironmentVariable('AWS_ACCESS_KEY_ID','User')
# to clear a persisted one:
[Environment]::SetEnvironmentVariable('AWS_ACCESS_KEY_ID', $null, 'User')
```

**2. The CodeCommit HTTPS username/password.** It is a long-lived static secret, and AWS documents that
it **cannot** be used with SSO/federated access at all
([setup docs](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up.html)). Use
`git-remote-codecommit` instead (below), which signs each request with your SSO session and stores
nothing.

## The start URL — corrected 2026-08-25

**`https://identitycenter.amazonaws.com/ssoins-7223528ddbceb375` works.** An earlier version of this
file said it was only the instance console URL and that `aws sso login` would reject it. **That was
wrong, and it was asserted three times before anyone tested it.** Tested on aws-cli/2.36.29: the CLI
accepts it, registers an OIDC client against `oidc.us-east-1.amazonaws.com`, and returns a real
authorize URL. It is in `~/.aws/config` and is the configured value.

The reasoning that produced the error was plausible and still partly true — `ssoins-…` *is* the
instance ID from `arn:aws:sso:::instance/ssoins-…`, and the canonical portal forms really are
`https://d-xxxxxxxxxx.awsapps.com/start` and `https://ssoins-….portal.<region>.app.aws`. What was
wrong was concluding that anything else must be refused. The CLI only requires an `https` scheme and a
resolvable OIDC endpoint; it does not enforce a hostname pattern.

**The lesson, since it cost real time:** a one-command check beats a confident inference. `aws sso
login --profile <p> --no-browser` prints the authorize URL and exits without needing a browser, so
validating a start URL is free.

If you ever do need the canonical portal URL: IAM Identity Center console → **Dashboard** →
*Settings summary* → **AWS access portal URL**.

### Mapping the live values onto config keys

Account and permission set come from the **Live resources** table above — `859430413223` is
`sso_account_id`, `agentic-trio` is `sso_role_name`. Only `sso_start_url` is still missing.

`Access denied` on *Account name* and *Account colour* in the console dropdown is expected: the
permission set lacks `account:GetAccountInformation`. It says nothing about your access to Bedrock,
DynamoDB or CodeCommit, and needs no fixing.

### Two regions, and they are not the same setting

The console opens on **`ap-southeast-2` (Sydney)**. That is *not* the build region.

- **`sso_region`** — where the Identity Center instance lives. Reported as `us-east-1`. Shown beside
  the start URL on the same console page.
- **`region`** (on the profile) — where Bedrock and every resource lives. **`us-east-1`, and this is now
  confirmed rather than chosen:** the CodeCommit repo is at `git-codecommit.us-east-1.amazonaws.com`, so
  the source of record is already there. It also happens to be what D-022 wanted — Appendix A pins every
  model ARN to `us-east-1`, §A.1's inference profiles use the `us.` prefix, and **every price in
  Appendix B is us-east-1 list price**. The console's region picker is cosmetic; the profile's `region`
  is what the CLI and boto3 obey.

If `aws sso login` fails once the start URL is right, `sso_region` is the next suspect — the instance
may live in `ap-southeast-2` alongside the console.

## Setup

### Step 1 — AWS CLI v2 (an administrator, once — but it does NOT block the build)

**Correction, verified 2026-08-25: the CLI is a convenience, not a gate.** An earlier version of this
file called it "the one blocker that cannot be worked around". That was wrong, and the mistake was
assuming every AWS path runs through the CLI. None of them do:

| Task | Needs the CLI? | What it actually uses |
|---|---|---|
| Bedrock, DynamoDB, S3, SQS, Lambda from Python | **No** | boto3 → default credential chain → **env vars first** |
| `cdk deploy` | **No** | `npx cdk` (Node v22.20.0 present) → AWS SDK for JS → same env vars |
| `git push` to CodeCommit | **No** | `git-remote-codecommit` — see the URL rule below |
| `aws sso login` | **Yes** | The only thing it uniquely provides |

**The CodeCommit URL form decides this, and it is easy to get wrong.** `git_remote_codecommit.parse()`
branches on whether the netloc contains `@`:

- `codecommit://genesis@agentic-trio` — **needs** a `genesis` profile in `~/.aws/config`, and raises
  `ProfileNotFound` without one. This is the SSO form, and it needs the CLI.
- `codecommit::us-east-1://agentic-trio` — **no `@`, so no profile**. Falls through to a bare
  `botocore.session.Session()`, which resolves credentials from the environment. **This form works
  today with the static keys and no CLI at all.**

So the CLI install buys durable, self-refreshing credentials. Until it lands, export the static trio
per shell and everything builds. Below is why the install is awkward, kept because it will come up:

- **`awscli` on PyPI is v1 only** and v1 has **no `aws sso login`** — verified locally on v1.46.0, which
  offers only `sso logout`, `list-accounts`, `list-account-roles`, `get-role-credentials`. So `uv` alone
  cannot start an SSO session.
- **There is no portable Windows zip** — `AWSCLIV2.zip` returns 404.
- **The MSI ignores `INSTALLDIR`** and installs to `C:\Program Files\Amazon\AWSCLIV2` regardless, so a
  per-user install fails with **1603**. Verified: the installer log shows the hardcoded path.
- `winget` is not present on this Windows 10 build; the `awscliv2` PyPI wrapper just shells out to Docker.

The MSI is already downloaded to `%TEMP%\AWSCLIV2.msi`. An administrator runs:

```powershell
msiexec /i "$env:TEMP\AWSCLIV2.msi" /qn
```

Verify with `aws --version` (expect `aws-cli/2.36.x`) in a **new** shell.

#### Until that install happens — the interim path

The static key trio is how you authenticate today. That is a real tension with the "do not use them"
rule above, and the rule is not wrong — hold both:

- **Use them now, deliberately and temporarily.** Export per shell; every tool in the table above picks
  them up with no further config.
- **Never persist them.** Per-shell only — never `setx`, never `.env`. A persisted value outranks the
  SSO profile forever after and produces exactly the confusing `ExpiredToken` this document warns about.
  When the token dies you re-paste; that recreation cost is why this is interim rather than the answer.
- **Use the no-profile CodeCommit URL** (`codecommit::us-east-1://agentic-trio`) while there is no
  profile to name. Switch to `codecommit://genesis@agentic-trio` once SSO is configured.

```powershell
$env:AWS_ACCESS_KEY_ID='...'; $env:AWS_SECRET_ACCESS_KEY='...'; $env:AWS_SESSION_TOKEN='...'
$env:AWS_DEFAULT_REGION='us-east-1'
uv run python -c "import boto3; print(boto3.client('sts').get_caller_identity()['Arn'])"
```

### Step 2 — configure the SSO session

Let the CLI write the config; it avoids the URL-format trap above:

```powershell
aws configure sso --profile genesis
```

It prompts for session name, start URL, SSO region (`us-east-1`), scopes
(`sso:account:access`), then opens a browser, then asks you to pick the account and role. The
equivalent hand-written config is in [.aws.config.example](../../.aws.config.example) — use the
`[sso-session]` form shown there, **not** the older flat per-profile style, because only the session
form auto-refreshes.

### Step 3 — daily use

```powershell
aws sso login --profile genesis     # once per session; opens a browser
$env:AWS_PROFILE = 'genesis'        # then nothing else needs a flag
aws sts get-caller-identity         # confirms who you are
```

When the token lapses, re-run `aws sso login`. Nothing is ever recreated or re-pasted.

### Step 4 — CodeCommit: WORKING, via the credential helper

**Verified 2026-08-25: `build/ear-on-every-call` is pushed.** No static Git password was needed and
none is stored.

**The API and git are authorized separately.** `codecommit:GetRepository` and `ListRepositories` are
denied for the `agentic-trio` permission set — but `git push` works, because
`aws codecommit credential-helper` mints a short-lived SigV4 password from the SSO session. An API
denial is therefore expected and is **not** a blocker. `aws_check.py` reports it as WARN for that
reason.

Configured locally, scoped to the CodeCommit host so it cannot affect GitHub:

```bash
git config --local credential."https://git-codecommit.us-east-1.amazonaws.com".helper "$HOME/bin/cc-cred.sh"
git config --local credential.UseHttpPath true
git remote add codecommit https://git-codecommit.us-east-1.amazonaws.com/v1/repos/agentic-trio
```

`~/bin/cc-cred.sh` is a two-line wrapper around the AWS CLI. It exists because git's inline
`!`-helper syntax breaks on the space in `C:\Program Files\...` — the failure is an unhelpful
`[Errno 22] Invalid argument`, so the wrapper is worth keeping rather than rediscovering.

**You do not need the `rprakash-at-859430413223` HTTPS Git credential.** It would work, but it is a
long-lived static secret and the helper above needs none. D-022's reasoning stands.

**Reading an empty repo's response:** `git ls-remote` on a repo with no commits returns nothing and
exits 0, which is indistinguishable from a silent auth failure. Use `--exit-code`: exit 2 means
"authenticated, no refs", 128 means "auth failed". That distinction cost real time.

### Step 4b — the old no-static-secret notes

`git-remote-codecommit` signs each push with the SSO profile. Under uv, no global install:

```powershell
uv tool install git-remote-codecommit          # verified to build (1.17)
git remote add codecommit codecommit://genesis@agentic-trio
git push codecommit HEAD
```

The `codecommit://<profile>@<repo>` URL contains **no credential** — it names a profile. Safe to commit,
safe to share. It does require the v2 CLI from step 1 to be on PATH for SSO support, so this step is
**blocked until the admin install** (see the interim note in Step 1).

**Do not use the HTTPS URL** `https://git-codecommit.us-east-1.amazonaws.com/v1/repos/agentic-trio` as a
git remote. It is the repo's canonical address and belongs in the Live resources table, but pushing to
it needs either the static Git username/password (a long-lived secret AWS documents as unusable with
SSO) or a credential helper. `codecommit://` avoids both.

### Step 5 — Python, via uv

Nothing to configure. boto3 discovers `~/.aws/config` and `AWS_PROFILE` on its own, and refreshes the
SSO token itself:

```powershell
uv add boto3                     # runtime dependency, when the Bedrock provider lands
```

The Bedrock provider is **additive** next to `openrouter.py` — it does not replace it. `resolve_api_key()`
stays: it is referenced by README, the CFPB protocol, and the test suite, and OpenRouter remains a
working provider for anyone with a key. Bedrock simply needs no key of its own.

## Bedrock model access — this has changed

[infrastructure.md](../architecture/infrastructure.md) §A.1 says model access needs a **per-model
console opt-in on the Model access page**, and calls it the most common cause of a confusing
`AccessDeniedException`. **That page was retired in 2025-10**
([AWS security blog, 2025-10-15](https://aws.amazon.com/blogs/security/simplified-amazon-bedrock-model-access/)):
serverless models are now reachable region-wide once IAM allows it, and
`bedrock:PutFoundationModelEntitlement` is gone.

Two things still gate a first call, so §A.1's warning is **narrowed, not void**:
- **Anthropic models require a one-time usage/EUA form acceptance** on the account.
- Marketplace-listed models still need a subscription.

Scope IAM to specific model ARNs, never `bedrock:*` — unchanged, and still right.

## Verifying you are set up

```powershell
aws --version                                    # 2.x, not 1.x
Get-ChildItem Env:AWS_ACCESS_KEY_ID -ErrorAction SilentlyContinue   # must be EMPTY
aws sts get-caller-identity --profile genesis     # see expected output below
git ls-remote codecommit://genesis@agentic-trio   # CodeCommit reachable
```

`get-caller-identity` should return account `859430413223` and an ARN of the form
`arn:aws:sts::859430413223:assumed-role/AWSReservedSSO_agentic-trio_<suffix>/rprakash@zenon.ai`.
If the account matches but the ARN names a plain IAM user rather than `AWSReservedSSO_…`, a static
key is still winning the precedence contest — go back and clear the environment variables.
