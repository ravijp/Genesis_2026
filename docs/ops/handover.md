# Handover

**Paste this file's path into a fresh conversation to resume the build.** Rewritten in place at every
handover; never appended to. If it is more than one screen it has failed.

Last handover: **2026-08-25** · Commit: `37a7374` · Branch: `build/ear-on-every-call`

---

## Read these first, in order

1. This file.
2. `docs/ops/progress.md` — what is done, what is blocked, who owns each blocker.
3. `docs/ops/state-of-play.md` — where the *product* stands, including what we lose on.
4. `docs/ops/decisions.md` — settled ground. Read before arguing for anything.
5. `CLAUDE.md` — the build rules. Load-bearing, not style.

Then start with: `source tools/aws-login.sh --check` (or `pwsh -File tools/aws-login.ps1 -Check`).

## The one thing to know

**CDK does not work here; deploy with boto3.** `cdk bootstrap` needs `s3:CreateBucket`,
`iam:CreateRole` and `ecr:CreateRepository` — all denied, all tested. Lambdas deploy fine by passing
the existing role `arn:aws:iam::859430413223:role/zenon-poc-lambda-execution`. Proven by creating and
deleting a real function. Do not re-litigate this; `progress.md` has the evidence table.

## Next action

**W3 — the Bedrock provider, `src/earshot/llm/bedrock.py`.** Everything else waits on it.

- New file beside `openrouter.py`, implementing the same two-method `LLMProvider` protocol
  (`llm/base.py:101-108`). Additive: `openrouter.py` and `resolve_api_key()` stay.
- `bedrock-runtime` **Converse** API. Translate `tools` ⇄ `toolUse`/`toolResult` both ways.
- Bedrock returns **tokens, not dollars**. Compute cost from a price table and label every derived
  figure **"computed from published prices"**, never "charged". This is G1 and it is a real reduction
  in honesty that must stay visible.
- **Anthropic models need the `us.` inference-profile prefix.** The bare `anthropic.claude-...` id
  fails with "on-demand throughput isn't supported". Nova and Llama take the bare id.
- `uv add --optional aws boto3` — the `aws` extra, so a fresh `uv sync` stays boto3-free.
- Unit-test against a stub first, exactly as `test_extract_model.py` already does. Zero network.

Then **W1** (persist case fields) and **W10** (reviewer UI), which need no AWS at all.

## Models

| Model | Id | State |
|---|---|---|
| Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | invocable |
| Nova Lite | `amazon.nova-lite-v1:0` | invocable |
| Llama 3 8B | `meta.llama3-8b-instruct-v1:0` | invocable |
| Sonnet 4.5 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | **blocked** — Anthropic use-case form |

Reader arm B is undecided and that is fine — any second Bedrock family works, and it is ~zero extra
work once the provider exists. **The brief never asked for two vendors**: it says "a comparison model
runs through the same harness" (`docs/sources/submission-ear-on-every-call.md:86-87`).

## Traps that have already cost time

- **A new IAM grant does nothing until the SSO session is reissued.** Run the login script with
  `--force`. This looked like IT not having applied a change.
- **`git ls-remote` on an empty repo returns nothing and exits 0**, indistinguishable from auth
  failure. Use `--exit-code`: 2 = authenticated, no refs; 128 = auth failed.
- **Never delete an `__init__.py`.** It drops the separation guard from 20 modules to 19 and the suite
  75 → 72 **with everything still green**. Empty the body if you must.
- **Reachability is not access.** `s3:HeadBucket` passed while `PutObject` was denied. Probe the action
  the build actually uses.
- **Two probe bugs looked like permission denials** (X-Ray timestamps, Anthropic model-id prefix).
  When something reads as AccessDenied, check the error *message*, not just the code.

## Rules that are load-bearing, not preferences

- Ground truth is authored before the text; the answer key never comes from a model.
- Re-scoring maths is plain code, never the model.
- Never discard a sub-threshold signal. This is the originality claim.
- Everything runs with zero API keys. Offline numbers are labelled and never headlined.
- Nothing is published from one dataset. `earshot sweep` is the only source of quotable numbers.
- No outbound contact surface anywhere. HITL is enforced by absence.
- Every number carries its denominator. Every date is absolute.

## Working mechanism

**The orchestrator conversation delegates and judges; it does not implement.** Subagents write code;
the orchestrator reviews, decides, and keeps the thread. Practical limits worth knowing:

- A subagent lives only inside its parent conversation. **Nothing persists across conversations except
  this file, `progress.md`, and git.** That is why these files exist rather than a long-running agent.
- Tier the work: opus for judging and adversarial review, sonnet for scoped implementation and
  research, haiku for mechanical formatting. Do not spawn an agent for work that is cheaper done
  directly.

**When to hand over** — the orchestrator should say so unprompted, at the first of:

1. **Context above ~50%.** Quality degrades before the limit, not at it.
2. **The next task is a large multi-file implementation.** Start it fresh rather than half-fed.
3. **A commit just landed and the next unit is independent.** Cleanest possible boundary.

**How to hand over:** rewrite this file (do not append), append a line to `progress.md`, commit, then
give the fresh conversation this file's path and nothing else. If the new conversation needs anything
that is not in here or `progress.md`, this file was wrong — fix it rather than explaining in chat.
