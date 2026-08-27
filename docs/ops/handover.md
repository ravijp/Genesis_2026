# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything. Rewritten
in place at each handover. **Keep it under ~60 lines** — it loads into every conversation, so length
here is a tax on all of them. It is a baton, not a history: next action, live blockers, traps already
paid for. History goes in `progress.md` or git.

**2026-08-25** · commit `3e0a80a` · branch `build/ear-on-every-call` · 236 tests, ruff clean

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. `source tools/aws-login.sh --check` (or `pwsh -File tools/aws-login.ps1 -Check`). Add `--force` if a
   permission IT says is granted still reads as denied — SSO caches grants in the role session.
3. `docs/ops/progress.md` for work-package status and blocker owners. `decisions.md` before arguing
   for anything.

## The one thing to know

**CDK does not work here. Deploy with boto3.** `cdk bootstrap` needs `s3:CreateBucket`,
`iam:CreateRole`, `ecr:CreateRepository` — all denied, all tested (D-024). Lambdas deploy by passing
the existing role `arn:aws:iam::859430413223:role/zenon-poc-lambda-execution`; proven by creating and
deleting a real function. Zip artifacts, not container images. Do not re-litigate.

## Next action — W3, the Bedrock provider

`src/earshot/llm/bedrock.py`, beside `openrouter.py`. Everything else waits on it.

- Same two-method `LLMProvider` protocol (`llm/base.py:101-108`). **Additive** — `openrouter.py` and
  `resolve_api_key()` stay; they are load-bearing in tests, README and the CFPB protocol.
- `bedrock-runtime` **Converse**; translate `tools` ⇄ `toolUse`/`toolResult` both ways.
- Bedrock returns **tokens, not dollars**. Compute from a price table and label every derived figure
  **"computed from published prices"**, never "charged" (G1).
- `uv add --optional aws boto3` — the `aws` extra, so a fresh `uv sync` stays boto3-free.
- Stub-test first, as `test_extract_model.py` does. Zero network.

Then **W1** (persist case fields) and **W10** (reviewer UI) — neither needs AWS.

| Model | Id | State |
|---|---|---|
| Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | invocable |
| Nova Lite | `amazon.nova-lite-v1:0` | invocable |
| Llama 3 8B | `meta.llama3-8b-instruct-v1:0` | invocable |
| Sonnet 4.5 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | **blocked** — Anthropic use-case form (Ravi) |

Arm B is undecided and that is fine: any second Bedrock family works, ~zero extra work once the
provider exists. **The brief never required two vendors** — it says "a comparison model runs through
the same harness" (`docs/sources/submission-ear-on-every-call.md:86-87`).

## Traps already paid for

- **A new IAM grant does nothing until the SSO session is reissued.** Use `--force`. This looked like
  IT not having applied a change.
- **Never delete an `__init__.py`.** Drops the separation guard 20 modules → 19 and the suite 75 → 72
  **with everything still green**. Empty the body if you must.
- **Reachability is not access.** `s3:HeadBucket` passed while `PutObject` was denied.
- **Anthropic models need the `us.` inference-profile prefix.** Bare ids fail with "on-demand
  throughput isn't supported". Nova and Llama take the bare id.
- **When something reads as AccessDenied, check the error *message*.** Two probe bugs (X-Ray
  timestamps, a wrong model id) masqueraded as permission problems.
- **`git ls-remote` on an empty repo returns nothing, exit 0** — same as auth failure. Use
  `--exit-code`: 2 = authed, no refs; 128 = auth failed.
