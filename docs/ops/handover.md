# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. Next action, live blockers, traps no test can catch. History
goes in `progress.md` or git.

**Budget: ~60 lines above "Traps", and the traps list is deliberately exempt.** It was one cap for
the whole file until 2026-09-03, when the file reached 180 lines and the rule was being quietly
broken instead of fixed. Splitting the traps into their own doc was the obvious move and is wrong:
this file is what `CLAUDE.md` imports, so a trap only earns its keep by being in context *before*
the mistake, not one link away. Prune a trap when a test starts enforcing it — that is what keeps
the list finite.

**2026-09-03** · `build/ear-on-every-call` · **908 tests** (903 pass, 5 skip) · ruff clean ·
separation guard over 45 modules + `tools/` · 30 UI routes · **~$2.45 of $12 spent**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. **`export AWS_PROFILE=genesis`** or boto3 finds no credentials and fails looking exactly like a
   dead token. Every keyed figure replays free with `EARSHOT_CACHE_MODE=replay` (a miss raises).
3. `progress.md` for status, `decisions.md` before arguing, `state-of-play.md` for the numbers.

## Next action — finish the `demo` stage

`dev` runs end to end and **agrees with the local pipeline**: 130 messages → 34 ledger entries → 1
case → `GET /cases` 200, deployed `0.6526618648909545` vs local `0.652662`. That was the missing
feasibility evidence.

**`demo` is half-deployed — the only untidy state in the repo.** Ravi authorised the model reader on
real infrastructure (~$0.21); the SSO token expired mid-deploy. Nothing charged, no partial ledger.

| resource | state |
|---|---|
| `earshot-demo-{ledger,cases,reviews}` | created, PITR on, empty |
| 4 × `earshot-demo-*` queues | created, redrive at 3, visibility 360s / 1800s |
| `earshot-demo-ingest` | **created**, `EARSHOT_EXTRACTOR=bedrock`, mapping Enabled |
| `earshot-demo-{investigate,api}` | **NOT created** |

```bash
source tools/aws-login.sh --force     # needs a browser; the token WILL be dead
uv run --with boto3 python tools/deploy.py --stage demo --no-dry-run --extractor bedrock
uv run --with boto3 python tools/feed.py  --stage demo --no-dry-run \
    --deployed-reader bedrock --settle 240
```

Both tools are idempotent — finished parts report SKIP. **`--deployed-reader bedrock` is required:**
`predict()` runs the offline lexicon, so equality is the wrong contract against a non-deterministic
model; the flag switches `verify()` to structural checks. **A second stage, not a re-feed of `dev`:**
mixing two readers in one ledger is not a thing anyone deploys, and `dev` cannot be cleared anyway —
`dynamodb:DeleteItem` is absent from the role, so never-discard is enforced at the IAM layer.
**`dev` = keyless lexicon, `demo` = Haiku 4.5, same book, same infrastructure.** That is the beat.

Then:

1. **The 09-07 demo beat sheet — Ravi's, and nothing exists.** `docs/gates/` has the 08-10 check-in
   and no plan for 08-24 or 09-07. Presentation is 10 points; the 25 feasibility points are earned
   *in* the demo. He was offered a draft and hasn't said yes — **offer again.** Strongest unused
   material: `CUST-0006-C0` scored **0.1306** on day 21 and is load-bearing 73 days later
   (`retro_delta 0.5220`), in a deployed record. It lives only in a commit message today.
2. **Prove an alarm fires — written, free, one command.** No alarm has ever reached ALARM, so all six
   thresholds are reasoned rather than observed.
   `tools/feed.py --stage dev --poison 1 --no-dry-run` sends one malformed transcript on a throwaway
   FIFO group and polls until `earshot-dev-ingest-failures` crosses. Exercises the `Failed` metric,
   the alarm, `batchItemFailures` isolation and the transcripts DLQ at once.

**Ravi's open decision — do not spend without him:** the **$10 10-seed sweep**, the only measurement
that would settle the co-primary chance gate the entry FAILS (18–8–4, `p=0.076`). ~$10 of ~$9.3
remaining, so it permanently rules out the model reader's own threshold ($13.96). He is waiting to see
whether the model-reader demo carries the weight without it.

**Settled 2026-09-03, do not reopen:** the UI write path **stays read-only and labelled** (a static
page cannot sign an IAM Function URL, and HITL-by-absence being literally true is an asset) · the
alarms get **no action** (EventBridge → Lambda would be the first outward-reaching thing here, and
CloudWatch already keeps two weeks of alarm history).

## State

**Arm B done** ($0.027705), so `build-plan.md` §4's last "not measured" item is closed — **but §4
still says otherwise and needs Ravi's sign-off to edit** (architecture doc, ask first). Nova Lite vs
Haiku on the same 282 conversations: coverage **181/282 vs 177/282** at **$0.0982/1,000 vs $1.58**,
p50 873 vs 1,333 ms, but **60/80 crossings vs 65/80** and **10 quotes not verbatim + 9 relocated vs
0 and 0**. It repairs the one desk Haiku loses to the lexicon, so *that published loss is Haiku's,
not the model reader's*. D-025 stands on evidence: the 16× buys citation discipline.

**D-031** re-registers the primary as `full-ledger` vs `window3-top2` (**30–0–0**), bound to the
chance gate above. The dead row keeps its place forever. **Coverage, not ranking, is the claim:**
Complaints 0/20 → 20/20, Vulnerability 0/20 → 19/20, Retention 1/20 → 16/20, Collections 9/20 →
10/20. **AT-57 29/50** (the corpus stopped leaking, not the agent improving) · **AT-58 27/48, worse**
(the `complaints` row is empty) · **AT-52: keep all four mechanisms** · **239/485 entries are worth
more now than at write; 0/485 under a plain count.**

One deployment (Northwind), nine seams, five the client's own. **CDK does not work here** (D-024).
`boto3` optional; a fresh clone runs keyless.

## Traps no test can catch

- **NEVER point two model runs at one cache path.** `ResponseCache` loads its file once in
  `__init__` (`llm/cache.py:66-85`). On 2026-08-30 a broken liveness check (`pgrep` **does not exist
  here** and reports every process dead) launched a second sweep over a live one: **$12.33 spent,
  $4.60 wasted, 39 cache lines torn**, permanently unreplayable. *(The first post-mortem blamed
  `prompt_sha` drift and was wrong — a duplicate key proves the key was STABLE.)*
- **`CachingProvider` never prints its hit/miss counters** (`llm/cache.py:127-128`). A 47% miss rate
  hid for 3,275 paid calls. Print them before spending.
- **One cache file per provider AND model AND measurement.** `config_hash` does **not** cover the
  code; manifests carry `pipeline_sha`. Land generator changes *before* spending.
- **A hanging AWS call is usually credential resolution, and `botocore.Config` timeouts do NOT cover
  it.** Diagnose cheapest-first: read `expiresAt` from `~/.aws/sso/cache/*.json` locally (instant, no
  network), *then* one short-timeout call. Never re-run a 200s command to find out.
- **Redirecting Python's stdout to a file makes it block-buffered**, so a killed run leaves an EMPTY
  log and hides where it stopped. Use `python -u` on anything you might kill.
- **Patch scripts in this shell need RAW strings (`r'''...'''`) for any text containing a backslash**
  — a `\n` in a quoted heredoc reaches Python as an escape and matches nothing. Five failed patches
  on 2026-09-03. Always assert the match count.
- **A wrapper that hides an exit code turns failure into false success.** `timeout … | tail` under-ran
  a 17-min job and let the kill return 0. Twice, ~$1.15. Echo `${PIPESTATUS[0]}`.
- **A green test can coexist with contradicting infrastructure.** `test_ingest.py` proved poison-record
  isolation while the queue had no DLQ; EMF was well-formed and produced **zero** metrics for want of
  `_aws.Timestamp`, and `notBreaching` made four alarms read **OK**. Ask what the deployed thing did.
- **Worktree isolation is BROKEN here.** `isolation: "worktree"` either refuses or checks out commit
  `4b71039` — the obsolete ideation tree, no `src/` or `tools/`. One locked worktree is parked at
  `.claude/worktrees/agent-ae208d8d4e6645e39` (a live `claude` pid holds it; do not kill it). Until
  fixed: implement directly, never two file-writing agents at once.
- **A replay at the wrong sample size looks like a broken cache and is not.** Match the published
  invocation exactly — it sits in `README.md` beside the figure.
- **Two thresholds disagree on purpose** — stream/`aws/ingest.py` use a fixed cut, `investigate` a
  budget-derived top-K. Never merge them.
- **Quote nothing at 10 seeds** — not re-measured on the widened corpus.
- **Narration must never share the ledger reader's extractor**; a warm cache makes "live" a replay.
- **`outcome is not None` is always true** · a case id contains `#`, percent-encode every link ·
  never delete an `__init__.py` · verify `pwd` before committing · the account tool takes
  `risk_signal`, never `latent_risk`.
- **AWS/deploy traps live in `aws-infrastructure.md`**, not copied here.
