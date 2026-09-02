# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-08-31 (late)** · commit `bd375a4` · branch `build/ear-on-every-call` · **855 tests** (850
pass, 5 skip), separation guard over 45 modules, contrast gate over 674 colour pairs / 17 routes,
ruff clean, **30 UI routes**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. **Every keyed figure is measured and published. ~$2.42 of $12 spent.** All replay free with
   `EARSHOT_CACHE_MODE=replay` — a miss raises rather than calling out, so a replay cannot spend.
   **The SSO token expires in hours, not days.** Every AWS call failing with `TokenRetrievalError`
   is a dead token, NOT a permissions problem — `sts:GetCallerIdentity` needs no permissions and
   fails too. Fix: `source tools/aws-login.sh --force`. Then `tools/aws_probe.py` (34 probes, ~1 min).
3. `progress.md` for work-package status and blocker owners. `decisions.md` before arguing.

## Next action

**THE IAM BLOCKER IS GONE — cleared by IT on 2026-08-31 and verified.** `zenon-poc-lambda-inline`
carries all four statements (SQS, DynamoDB, Bedrock `InvokeModel`, CloudWatch Logs) and
**`dynamodb:DeleteItem` is correctly absent**, so never-discard is now enforced at the IAM layer and
not only by a test. `GET /cases`, which touches DynamoDB, returns **200** where it returned 500.
`earshot-dev-ingest` returns `batchItemFailures: []`. The deployed path is no longer a diagram.

Work this unblocked, in order. **All of it is free except item 4.**

1. **Wire the queues to their consumers.** Event source mappings: `earshot-dev-transcripts.fifo` →
   `earshot-dev-ingest`, `earshot-dev-investigations` → `earshot-dev-investigate`. Nothing consumes
   either queue today, so the pipeline is permissioned but not connected.
2. **Feed it end to end and prove it.** The tables are empty (`count: 0` is real, not an error).
   Push a batch through ingest → ledger → threshold → investigate → `GET /cases` and get a non-zero
   queue out of the deployed system rather than a local run. **This is the feasibility evidence the
   entry does not yet have** — 25 of 25 rubric points are scored on production readiness.
3. **Give the six alarms an action.** They are created and page nobody. No SNS on this account, so
   the route is EventBridge → Lambda. `tools/alarms.py`.
4. **Arm B, ~$0.01.** `bedrock:InvokeModel` works, so the last "not measured" item in
   `build-plan.md` §4 and the brief's explicit comparison-model promise close for a cent. Nova Lite:
   `extractor_cache_path()` is per-model so it cannot pollute the published Haiku cache.
5. **The UI write path.** A static page cannot sign an `AuthType=AWS_IAM` Function URL. The decision
   buttons currently print the request body they *would* send and say so. Decide the signing story.

**Still denied, and neither matters:** `codebuild:ListProjects` and `codepipeline:ListPipelines`.
CodeBuild was declined deliberately on 2026-08-31 — `buildspec.yml` is stale (calls `cdk deploy`,
`cd infra`, `ui/package.json`, none of which exist) and CI runs on GitHub Actions. `iam:CreateRole`
**now passes**, so if CodeBuild is ever wanted the service role is self-serve; the blocker is our own
buildspec, not IT.

**Never spent, and priced:** the model reader's own threshold ($13.96 — until then every model-arm
crossing figure is an **upper bound**, and the tool prints that itself) and the 10-seed keyed sweep
(~$10, the one measurement that would settle the chance gate). ~$9.5 of the $12 budget is unspent.

## State

**The corpus was rebuilt 2026-08-31 (Phase C) and the pre-registered headline died.** `full-ledger`
vs `stateless-max` on diffuse: 29–0–1 → **15–13–2, `p=0.851`**. Cause was measured: a `plant_at` bug
meant the planted fragment was **silently never spoken** in 69 of 600 arc conversations, crippling
the opponent. **D-031 re-registers** the primary as `full-ledger` vs `window3-top2` (**30–0–0**, both
tie-breaks) bound to a **co-primary chance gate the entry FAILS** (18–8–4, `p=0.076`). The dead row
keeps its place forever.

**The claim is coverage, not ranking, and it is the entry's strongest evidence.** Same 282 planted
conversations, same ledger, same threshold, one variable — who reads: **Complaints 0/20 → 20/20,
Vulnerability 0/20 → 19/20**, Retention 1/20 → 16/20, Collections 9/20 → 10/20. The keyless lexicon
finds 59/282 and leaves two desks empty. Model reader **$1.58/1,000**, p50 1,333 ms, 0 unparsable.
**The model column is an upper bound** (threshold is a top-K cut over the offline ranking).

**AT-57 is 29/50** (was 22/50), dismissals **13/25** (was 4/25) — *the agent did not change*, the
corpus stopped leaking the answer through surface form. **AT-58 is 27/48, worse** than 36/49, because
the confusion matrix's `complaints` row is empty: no complaint customer crosses under the offline
reader, so 43 of 48 scorable cases are one desk.

**AT-52 answered: keep all four mechanisms.** The `dumb-ledger` "loss" (7–18–5, `p=0.043`) is a
tie-break artefact — 5 distinct scores over 1,500 customers; randomised it is 11–13–6, `p=0.839`.
Structural leg: **239/485 ledger entries are worth more now than at write; 0/485 under a plain
count.**

One deployment (Northwind), nine seams, **five** the client's own. **One model, Haiku 4.5** (D-025).
**CDK does not work here** (D-024). `boto3` stays optional; a fresh clone runs keyless.

## Traps already paid for

- **NEVER point two model runs at one cache path.** `ResponseCache` loads its file once in
  `__init__` and never re-reads it (`llm/cache.py:66-85`), so concurrent processes are blind to each
  other's writes. On 2026-08-30 a broken liveness check (`pgrep` **does not exist on this machine**
  and reports every process dead) led to a second sweep being launched over a live one: **$12.33
  spent, $4.60 wasted, no artifact, and 39 cache lines torn by interleaved writes** — those
  completions are paid for and permanently unreplayable. Duplication started at record 185, not at
  the resume boundary. *(The first post-mortem blamed `prompt_sha` drift. It was wrong: a duplicate
  key proves the key was STABLE — drift would have produced zero duplicates. `progress.md` carries
  the corrected version.)*
- **`CachingProvider` counts hits/misses and never prints them** (`llm/cache.py:127-128`). A 47% miss
  rate stayed invisible for 3,275 paid calls. Print the counter before spending.
- **One cache file per provider AND per model AND per measurement.** A second reader arm through a
  shared path appends behind a published figure silently — keys do not collide, nothing errors.
  **`config_hash` does not cover the code**: it was byte-identical across two corpora that disagreed
  about who crosses. Manifests carry `pipeline_sha`. Land generator changes *before* spending.
- **A replay at the wrong sample size looks like a broken cache and is not.** AT-57 replays only at
  `--per-arm 25 --customers 2400`; at `--customers 400` there are just 10 outcome customers, so the
  run draws 35 cases and 27 come back `provider_error`. Match the published invocation exactly — it
  is in `README.md` next to the figure — before concluding a cache is stale.
- **A wrapper that hides an exit code turns a failure into a false success.** `timeout 590 … | tail`
  both under-ran a 17-minute AT-57 job and let the kill return 0, so a truncated run looked clean.
  Twice, ~$1.15. Same family as the `pgrep` mistake.
- **Two thresholds disagree on purpose** — stream/`aws/ingest.py` use a fixed cut, `investigate`
  a budget-derived top-K. Never merge them.
- **The arc ceiling is gone; a test now pins its absence, not its presence.** Pools are 14/14/14/14;
  `test_the_shipped_default_no_longer_breaches_the_ceiling` asserts the warning never fires.
- **Quote nothing at 10 seeds** — not yet re-measured on the widened corpus (the deferred sweep).
- **`stream.py` stays guarded only because `cli.stream_inputs()` hands it conversations** —
  re-add `generate()` and the guard correctly fails.
- **The account tool takes `risk_signal`, never `latent_risk`** — renamed this session so
  `risk_signal=truth.latent_risk` reads as the error it would be.
- **Narration must never share the ledger reader's extractor**; the final turn-by-turn read equals
  the batch read byte for byte; a warm cache makes "live" a replay (`EARSHOT_CACHE_MODE=off`).
- **`outcome is not None` is always true** · a case id contains `#`, every link percent-encodes it ·
  never delete an `__init__.py` · verify `pwd` before committing, a worktree `cd` persists.
- **AWS/deploy traps live in `aws-infrastructure.md`**, not copied here.
