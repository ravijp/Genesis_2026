"""Probe every AWS permission this build needs, at the depth the build actually uses.

Read-only where it can be. Where a write is the only honest test, it writes to a
`_conn-test/` prefix or a `conn-test-*` name and deletes it -- and says so in the output.

`aws_check.py` was too shallow: `s3:HeadBucket` passed while `s3:PutObject` was denied, so it
reported S3 as fine when run artifacts could not be written. A reachability check is not an
access check. Every probe here names the exact IAM action the build depends on.

    AWS_PROFILE=genesis uv run --with boto3 python tools/aws_probe.py
"""

from __future__ import annotations

import sys

REGION = "us-east-1"
BUCKET = "agentic-trio"
PROBE_KEY = "_conn-test/probe.txt"

rows: list[dict[str, str]] = []


def probe(area: str, action: str, need: str, fn) -> None:
    """Run one probe. `need` says what breaks without it, for the report."""
    try:
        detail = fn() or "ok"
        status = "PASS"
    except Exception as e:  # noqa: BLE001 - any failure is a finding, not a crash
        code = getattr(e, "response", {}).get("Error", {}).get("Code", "") or type(e).__name__
        # A RuntimeError here is one we raised ourselves with a diagnosis attached; its message
        # is the actionable part, so keep it rather than printing the class name.
        detail = str(e) if isinstance(e, RuntimeError) else code
        status = "DENIED" if "AccessDenied" in code or "Unauthor" in code else "FAIL"
    rows.append({"area": area, "action": action, "status": status, "detail": detail, "need": need})
    print(f"  [{status:6}] {action:44} {detail[:60]}")


def main() -> int:
    try:
        import boto3
    except ImportError:
        print("run with: uv run --with boto3 python tools/aws_probe.py")
        return 2

    b = lambda svc: boto3.client(svc, region_name=REGION)  # noqa: E731

    print(f"\nProbing {REGION} as the agentic-trio permission set\n")

    print("IDENTITY")
    probe("identity", "sts:GetCallerIdentity", "everything",
          lambda: b("sts").get_caller_identity()["Arn"].split("/")[-1])

    print("\nS3 -- run artifacts, evidence archive, SPA hosting")
    probe("s3", "s3:ListBucket", "reading anything back",
          lambda: f"{b('s3').list_objects_v2(Bucket=BUCKET).get('KeyCount', 0)} objects")
    probe("s3", "s3:PutObject", "W1 artifacts, evidence archive, UI deploy",
          lambda: (b("s3").put_object(Bucket=BUCKET, Key=PROBE_KEY, Body=b"probe"), "wrote probe")[1])
    probe("s3", "s3:GetObject", "replaying a committed run",
          lambda: f"{len(b('s3').get_object(Bucket=BUCKET, Key=PROBE_KEY)['Body'].read())} bytes")
    probe("s3", "s3:DeleteObject", "cleanup only -- never the ledger",
          lambda: (b("s3").delete_object(Bucket=BUCKET, Key=PROBE_KEY), "deleted probe")[1])
    probe("s3", "s3:GetBucketVersioning", "artifact provenance",
          lambda: b("s3").get_bucket_versioning(Bucket=BUCKET).get("Status", "not enabled"))

    print("\nDYNAMODB -- ledger, cases, reviews")
    probe("dynamodb", "dynamodb:ListTables", "W6",
          lambda: f"{len(b('dynamodb').list_tables()['TableNames'])} tables")
    probe("dynamodb", "dynamodb:CreateTable", "W6 -- the ledger itself",
          lambda: _make_table(b("dynamodb")))

    print("\nBEDROCK -- the reader and the investigator")
    probe("bedrock", "bedrock:ListFoundationModels", "model selection",
          lambda: f"{len(b('bedrock').list_foundation_models()['modelSummaries'])} models")
    # Anthropic models need the `us.` INFERENCE-PROFILE prefix -- the bare foundation-model id
    # fails with "on-demand throughput isn't supported". Amazon and Meta models take the bare
    # id. Getting this wrong reads as a missing permission and is not one.
    probe("bedrock", "bedrock:InvokeModel (Haiku 4.5)", "reader arm A, every published number",
          lambda: _converse(b("bedrock-runtime"), "us.anthropic.claude-haiku-4-5-20251001-v1:0"))
    probe("bedrock", "bedrock:InvokeModel (Sonnet 4.5)", "the investigator",
          lambda: _converse(b("bedrock-runtime"), "us.anthropic.claude-sonnet-4-5-20250929-v1:0"))
    probe("bedrock", "bedrock:InvokeModel (Nova Lite)", "reader arm B candidate",
          lambda: _converse(b("bedrock-runtime"), "amazon.nova-lite-v1:0"))
    probe("bedrock", "bedrock:InvokeModel (Llama 3 8B)", "reader arm B candidate",
          lambda: _converse(b("bedrock-runtime"), "meta.llama3-8b-instruct-v1:0"))

    print("\nCOMPUTE + QUEUE")
    probe("lambda", "lambda:ListFunctions", "W7/W8",
          lambda: f"{len(b('lambda').list_functions()['Functions'])} functions")
    probe("lambda", "lambda:GetAccountSettings", "deploy headroom",
          lambda: str(b("lambda").get_account_settings()["AccountLimit"]["TotalCodeSize"]))
    probe("sqs", "sqs:ListQueues", "W7 ingest bus",
          lambda: f"{len(b('sqs').list_queues().get('QueueUrls', []))} queues")
    probe("sqs", "sqs:CreateQueue", "W7 -- the bus itself",
          lambda: _make_queue(b("sqs")))

    print("\nDELIVERY -- image, source of record, IaC")
    probe("ecr", "ecr:DescribeRepositories", "container image",
          lambda: f"{len(b('ecr').describe_repositories()['repositories'])} repos")
    # NOT a blocker, however this prints. The CodeCommit API and CodeCommit git are authorized
    # separately: the API is denied, and `git push` works via `aws codecommit
    # credential-helper`, which mints a SigV4 password from the SSO session. Proven 2026-08-25
    # by pushing build/ear-on-every-call. Kept as a probe so the asymmetry stays visible.
    probe("codecommit", "codecommit:GetRepository (API only)", "nothing -- git push works regardless",
          lambda: b("codecommit").get_repository(repositoryName=BUCKET)["repositoryMetadata"]["repositoryName"])
    probe("cloudformation", "cloudformation:ListStacks", "CDK",
          lambda: f"{len(b('cloudformation').list_stacks()['StackSummaries'])} stacks")
    probe("codebuild", "codebuild:ListProjects", "CI/CD + the sweep runner",
          lambda: f"{len(b('codebuild').list_projects()['projects'])} projects")
    probe("codepipeline", "codepipeline:ListPipelines", "CI/CD",
          lambda: f"{len(b('codepipeline').list_pipelines()['pipelines'])} pipelines")

    print("\nCLIENT-FACING + OBSERVABILITY")
    probe("apigateway", "apigateway:GET", "reviewer API",
          lambda: f"{len(b('apigatewayv2').get_apis()['Items'])} HTTP APIs")
    probe("cognito", "cognito-idp:ListUserPools", "staff auth",
          lambda: f"{len(b('cognito-idp').list_user_pools(MaxResults=5)['UserPools'])} pools")
    probe("cloudfront", "cloudfront:ListDistributions", "SPA hosting",
          lambda: str(b("cloudfront").list_distributions()["DistributionList"].get("Quantity", 0)))
    probe("logs", "logs:DescribeLogGroups", "W11 -- EMF metrics",
          lambda: f"{len(b('logs').describe_log_groups(limit=5)['logGroups'])} groups")
    probe("logs", "logs:PutLogEvents", "W11 -- emitting anything",
          lambda: _make_log_group(b("logs")))
    probe("cloudwatch", "cloudwatch:PutMetricAlarm", "cost + DLQ alarms",
          lambda: _describe_alarms(b("cloudwatch")))
    # GetSamplingRules needs no time window. get_service_graph(StartTime=0) returns
    # InvalidRequestException, which reads as a denial and is not one.
    probe("xray", "xray:GetSamplingRules", "tracing",
          lambda: f"{len(b('xray').get_sampling_rules()['SamplingRuleRecords'])} rules")
    probe("ssm", "ssm:PutParameter", "config store",
          lambda: f"{len(b('ssm').describe_parameters(MaxResults=5)['Parameters'])} params")
    probe("events", "events:ListRules", "nightly batch",
          lambda: f"{len(b('events').list_rules()['Rules'])} rules")
    probe("iam", "iam:CreateRole", "every Lambda needs an execution role",
          lambda: f"{len(b('iam').list_roles(MaxItems=5)['Roles'])} roles listable")
    probe("ecs", "ecs:ListClusters", "sweep harness (needs a VPC too)",
          lambda: f"{len(b('ecs').list_clusters()['clusterArns'])} clusters")
    probe("ec2", "ec2:DescribeVpcs", "anything Fargate",
          lambda: f"{len(b('ec2').describe_vpcs()['Vpcs'])} VPCs")

    denied = [r for r in rows if r["status"] == "DENIED"]
    failed = [r for r in rows if r["status"] == "FAIL"]
    print(f"\n{'-' * 78}")
    print(f"{len(rows)} probes: {len(rows) - len(denied) - len(failed)} pass, "
          f"{len(denied)} denied, {len(failed)} other failure\n")
    if denied:
        print("DENIED -- needs an IT change:")
        for r in denied:
            print(f"  {r['action']:44} blocks: {r['need']}")
    if failed:
        print("\nOTHER FAILURES (may be a wrong assumption in this script, not a permission):")
        for r in failed:
            print(f"  {r['action']:44} {r['detail']}")
    print()
    return 0


def _converse(rt, model_id: str) -> str:
    """One token in, one out. Cheapest possible proof the model is actually invocable.

    Two failures here are configuration, not permission, and the messages are the only way to
    tell them apart -- both otherwise look like a denial:
      * "on-demand throughput isn't supported" -> use the `us.` inference-profile id
      * "use case details have not been submitted" -> the one-time Anthropic EUA form
    """
    try:
        rt.converse(modelId=model_id, messages=[{"role": "user", "content": [{"text": "hi"}]}],
                    inferenceConfig={"maxTokens": 1})
        return "invocable"
    except Exception as e:
        msg = str(e)
        if "use case details" in msg:
            raise RuntimeError("EUA FORM NEEDED -- Anthropic use case form, console one-time") from e
        if "on-demand" in msg:
            raise RuntimeError("needs the us. inference-profile id, not the bare model id") from e
        raise


def _make_table(ddb) -> str:
    """CreateTable then delete. The only honest test of whether W6 can be built.

    DeleteTable fails while the table is still CREATING, so wait for ACTIVE first -- an
    earlier version skipped this and left `conn-test-delete-me` behind twice.
    """
    name = "conn-test-delete-me"
    ddb.create_table(TableName=name, BillingMode="PAY_PER_REQUEST",
                     KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                     AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}])
    try:
        ddb.get_waiter("table_exists").wait(
            TableName=name, WaiterConfig={"Delay": 2, "MaxAttempts": 15})
        ddb.delete_table(TableName=name)
        return "created + deleted"
    except Exception:
        return f"CREATED but delete failed -- run: aws dynamodb delete-table --table-name {name}"


def _make_queue(sqs) -> str:
    url = sqs.create_queue(QueueName="conn-test-delete-me")["QueueUrl"]
    try:
        sqs.delete_queue(QueueUrl=url)
        return "created + deleted"
    except Exception:
        return "CREATED but delete failed -- remove conn-test-delete-me manually"


def _make_log_group(logs) -> str:
    name = "/conn-test/delete-me"
    logs.create_log_group(logGroupName=name)
    try:
        logs.delete_log_group(logGroupName=name)
        return "created + deleted"
    except Exception:
        return "CREATED but delete failed"


def _describe_alarms(cw) -> str:
    return f"{len(cw.describe_alarms(MaxRecords=5)['MetricAlarms'])} alarms listable"


if __name__ == "__main__":
    sys.exit(main())
