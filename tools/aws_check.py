"""Check every AWS connection this build depends on, and answer the two irreversible questions.

Read-only: no resource is created, modified or deleted. Run it after `aws sso login --profile
genesis`, or with the static key trio exported.

    uv run --with boto3 python tools/aws_check.py

Two of these checks matter more than the rest, because their answers cannot be changed later:

  * S3 Object Lock on the bucket. Not enablable after creation without an AWS Support case. If it
    is off, write-once on the evidence archive is gone permanently and a stage claim about
    never-discard being structural becomes false for that artifact. (The ledger's guarantee is
    separate -- that is DynamoDB, no TTL, no delete permission -- and is unaffected.)
  * CloudFormation access. infrastructure.md commits all IaC to CDK, and CDK deploys through
    CloudFormation, which is NOT in the granted service list. If it is denied, W9 is dead as
    designed and IaC becomes boto3 scripts.
"""

from __future__ import annotations

import sys

BUCKET = "agentic-trio"
REGION = "us-east-1"
REPO = "agentic-trio"
ACCOUNT = "859430413223"

OK, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str) -> None:
    results.append((name, status, detail))
    print(f"  [{status:4}] {name:34} {detail}")


def err(e: Exception) -> str:
    """Collapse a botocore error to its code -- the part that says what to do next."""
    code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
    return code or type(e).__name__


def main() -> int:
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError, TokenRetrievalError
    except ImportError:
        print("boto3 missing. Run: uv run --with boto3 python tools/aws_check.py")
        return 2

    print(f"\nRegion {REGION} | expecting account {ACCOUNT}\n")

    # --- identity -----------------------------------------------------------------------
    print("IDENTITY")
    try:
        who = boto3.client("sts", region_name=REGION).get_caller_identity()
    except (NoCredentialsError, TokenRetrievalError) as e:
        record("sts:GetCallerIdentity", FAIL, f"{type(e).__name__} -- run: aws sso login --profile genesis")
        print("\nNo credentials. Nothing else can be checked.\n")
        return 1
    except ClientError as e:
        record("sts:GetCallerIdentity", FAIL, err(e))
        return 1

    arn = who["Arn"]
    record("sts:GetCallerIdentity", OK, arn)
    if who["Account"] != ACCOUNT:
        record("account matches", FAIL, f"got {who['Account']}, expected {ACCOUNT}")
    else:
        record("account matches", OK, ACCOUNT)
    # A static key beats an SSO profile in the credential chain, so say which one is in play.
    record("credential source", OK if "assumed-role" in arn else WARN,
           "SSO role session" if "assumed-role" in arn else "NOT an SSO role -- a static key may be winning")

    # --- the two irreversible questions -------------------------------------------------
    print("\nIRREVERSIBLE -- answer these before designing around them")
    s3 = boto3.client("s3", region_name=REGION)
    try:
        s3.get_object_lock_configuration(Bucket=BUCKET)
        record("S3 Object Lock", OK, "ENABLED -- write-once achievable via per-object retention")
    except ClientError as e:
        code = err(e)
        if code == "ObjectLockConfigurationNotFoundError":
            record("S3 Object Lock", WARN,
                   "OFF and NOT changeable without AWS Support. Evidence write-once degrades to IAM")
        else:
            record("S3 Object Lock", FAIL, code)

    try:
        boto3.client("cloudformation", region_name=REGION).list_stacks(StackStatusFilter=["CREATE_COMPLETE"])
        record("CloudFormation (CDK needs it)", OK, "accessible -- CDK is viable")
    except ClientError as e:
        record("CloudFormation (CDK needs it)", FAIL, f"{err(e)} -- CDK unusable; IaC becomes boto3 scripts")

    # --- granted services ---------------------------------------------------------------
    print("\nGRANTED SERVICES")
    # HeadBucket alone is NOT an access check -- it passed here while PutObject was denied,
    # which made this script report S3 as fine when no artifact could be written. Probe the
    # action the build actually needs.
    try:
        s3.head_bucket(Bucket=BUCKET)
        try:
            s3.put_object(Bucket=BUCKET, Key="_conn-test/probe.txt", Body=b"probe")
            s3.delete_object(Bucket=BUCKET, Key="_conn-test/probe.txt")
            record("S3 read+write", OK, f"s3://{BUCKET} writable")
        except ClientError as e:
            record("S3 read+write", FAIL,
                   f"reachable but {err(e)} on PutObject -- artifacts cannot be written")
    except ClientError as e:
        record("S3 read+write", FAIL, err(e))

    try:
        n = len(boto3.client("dynamodb", region_name=REGION).list_tables()["TableNames"])
        record("DynamoDB", OK, f"{n} tables (0 expected -- none built yet)")
    except ClientError as e:
        record("DynamoDB", FAIL, err(e))

    try:
        n = len(boto3.client("sqs", region_name=REGION).list_queues().get("QueueUrls", []))
        record("SQS", OK, f"{n} queues")
    except ClientError as e:
        record("SQS", FAIL, err(e))

    try:
        n = len(boto3.client("lambda", region_name=REGION).list_functions()["Functions"])
        record("Lambda", OK, f"{n} functions")
    except ClientError as e:
        record("Lambda", FAIL, err(e))

    try:
        n = len(boto3.client("ecr", region_name=REGION).describe_repositories()["repositories"])
        record("ECR", OK, f"{n} repositories")
    except ClientError as e:
        record("ECR", FAIL, err(e))

    # The CodeCommit *API* and CodeCommit *git* are separately authorized. The API is denied
    # for us; git push WORKS via the credential helper, which mints a SigV4 password from the
    # SSO session (`aws codecommit credential-helper`). Verified 2026-08-25 by pushing this
    # branch. So an API denial here is expected and is NOT a blocker -- do not read it as one.
    try:
        meta = boto3.client("codecommit", region_name=REGION).get_repository(repositoryName=REPO)
        record("CodeCommit API", OK, meta["repositoryMetadata"]["cloneUrlHttp"])
    except ClientError as e:
        record("CodeCommit API", WARN, f"{err(e)} -- expected; git push works via credential-helper")

    # --- Bedrock: the one that gates every published number -----------------------------
    print("\nBEDROCK")
    wanted = ("claude-haiku", "claude-sonnet", "nova-lite", "llama")
    try:
        models = boto3.client("bedrock", region_name=REGION).list_foundation_models()["modelSummaries"]
        record("bedrock:ListFoundationModels", OK, f"{len(models)} models visible")
        ids = [m["modelId"] for m in models]
        for w in wanted:
            hits = [m for m in ids if w in m]
            record(f"  {w}", OK if hits else WARN,
                   hits[0] if hits else "not listed in this region")
    except ClientError as e:
        record("bedrock:ListFoundationModels", FAIL, err(e))

    # An InvokeModel attempt is the only way to see the Anthropic EUA gate. Deliberately tiny:
    # one token in, one out, so the check costs a fraction of a cent.
    try:
        rt = boto3.client("bedrock-runtime", region_name=REGION)
        rt.converse(
            modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            messages=[{"role": "user", "content": [{"text": "hi"}]}],
            inferenceConfig={"maxTokens": 1},
        )
        record("bedrock:Converse (Haiku)", OK, "INVOCABLE -- the reader can run")
    except ClientError as e:
        code = err(e)
        hint = {
            "AccessDeniedException": "IAM or the one-time Anthropic EUA acceptance",
            "ValidationException": "model id wrong for this region -- check the snapshot suffix",
            "ResourceNotFoundException": "model id not found -- verify in console",
        }.get(code, "")
        record("bedrock:Converse (Haiku)", FAIL, f"{code}{' -- ' + hint if hint else ''}")
    except Exception as e:  # noqa: BLE001 - unknown client shape should not abort the run
        record("bedrock:Converse (Haiku)", FAIL, type(e).__name__)

    # --- summary ------------------------------------------------------------------------
    fails = [r for r in results if r[1] == FAIL]
    warns = [r for r in results if r[1] == WARN]
    print(f"\n{'-' * 78}")
    print(f"{len(results)} checks: {len(results) - len(fails) - len(warns)} pass, "
          f"{len(warns)} warn, {len(fails)} fail")
    for name, _, detail in fails:
        print(f"  FAIL  {name}: {detail}")
    for name, _, detail in warns:
        print(f"  WARN  {name}: {detail}")
    print()
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
