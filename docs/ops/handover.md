# Handover

**Imported by `CLAUDE.md`, so every conversation already has this.** Nobody pastes anything.
Rewritten in place at each handover. **Keep it under ~60 lines.** It is a baton, not a history:
next action, live blockers, traps already paid for. History goes in `progress.md` or git.

**2026-09-03** · branch `build/ear-on-every-call` · **904 tests** (899 pass, 5 skip), separation
guard over 45 modules + `tools/`, contrast gate over 674 colour pairs / 17 routes, ruff clean,
**30 UI routes**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. **`export AWS_PROFILE=genesis` before any AWS call.** Without it boto3 finds no credentials and
   fails looking exactly like a dead SSO token. A genuinely dead token is
   `TokenRetrievalError`; fix with `source tools/aws-login.sh --force`. **~$2.45 of $12 spent.**
   Every keyed figure replays free with `EARSHOT_CACHE_MODE=replay` — a miss raises, so a replay
   cannot spend.
3. `progress.md` for work-package status. `decisions.md` before arguing.

## Next action

**The deployed pipeline runs end to end and agrees with the local one.** `tools/feed.py`: 130
messages → 34 ledger entries → 1 case → `GET /cases` 200, deployed score `0.6526618648909545`
against local `0.652662`. Both mappings Enabled, four queues, both consumed ones with a DLQ, 12 EMF
metrics flowing. **That was the missing feasibility evidence and it now exists.**

In order:

1. **The UI write path — the largest open item, and it needs a decision, not code.** A static page
   cannot sign an `AuthType=AWS_IAM` Function URL. The buttons print the body they *would* send and
   say so. Options: a signing proxy · `AuthType=NONE` behind a shared secret (bad) · stay honestly
   read-only. Ask Ravi; do not pick silently.
2. **Deploy the model reader and re-run the feed.** `deploy.py --extractor bedrock` has never run on
   AWS. Today's 1-crossing-in-44 is the *keyless lexicon's* real rate, so the deployed figures and
   the published reader figures come from different readers and **must not be quoted together**.
   Costs real money per conversation — price it before running.
3. **Prove an alarm fires.** No alarm has ever transitioned to ALARM, so all six thresholds are
   reasoned, not observed. Free. Do this before item 4, which is worth less.
4. **Give the alarms an action, or decide not to.** No SNS; the EventBridge → Lambda route would be
   the first outward-reaching thing in a system whose HITL guarantee is absence. `alarms.py`'s
   docstring argues both sides. A decision, not a task.
5. **`GET /cases/{id}` leaks `pk` / `gsi1pk` / `gsi1sk`** into the client body. The list route does
   not. Not an answer-key leak, so `test_api.py` is right to pass.

**Priced and unspent, ~$9.5 of $12 left:** the model reader's own threshold ($13.96 — until then
every model-arm crossing figure is an **upper bound**, and the tool says so itself) and the 10-seed
keyed sweep (~$10, the one measurement that would settle the chance gate).

## State

**Arm B is done and `build-plan.md` §4's last "not measured" item is closed** — but **§4 still says
otherwise and needs your edit** (ask first; it is an architecture doc). Nova Lite, same 282
conversations, $0.027705: coverage **181/282 vs Haiku's 177/282** at **$0.0982/1,000 vs $1.58**, p50
873 vs 1,333 ms — and **60/80 crossings vs 65/80**. It repairs the one desk Haiku loses to the
lexicon (`financial_distress` 27/72 → 42/72 vs 33/72), so *that published loss is Haiku's, not the
model reader's*. Against it: **10 quotes not verbatim, 9 relocated, vs Haiku's 0 and 0** on
identical text, 0 unparsable both. D-025 stands on evidence now: the 16× buys quote fidelity.

**The corpus was rebuilt 2026-08-31 and the pre-registered headline died.** **D-031** re-registers
the primary as `full-ledger` vs `window3-top2` (**30–0–0**) bound to a **co-primary chance gate the
entry FAILS** (18–8–4, `p=0.076`). The dead row keeps its place forever.

**The claim is coverage, not ranking.** Same 282 planted conversations, one variable — who reads:
Complaints 0/20 → 20/20, Vulnerability 0/20 → 19/20, Retention 1/20 → 16/20, Collections 9/20 →
10/20. **AT-57 29/50** (dismissals 13/25) — the agent did not change, the corpus stopped leaking.
**AT-58 27/48, worse**, because the `complaints` row is empty. **AT-52: keep all four mechanisms**;
the `dumb-ledger` "loss" is a tie-break artefact (11–13–6 randomised). **239/485 ledger entries are
worth more now than at write; 0/485 under a plain count.**

One deployment (Northwind), nine seams, five the client's own. **One model, Haiku 4.5** (D-025).
**CDK does not work here** (D-024). `boto3` stays optional; a fresh clone runs keyless.

## Traps already paid for

- **Worktree isolation is BROKEN in this environment.** `Agent` with `isolation: "worktree"` either
  refuses ("git could not be run to resolve it") or checks out **commit `4b71039`, the obsolete
  ideation-phase tree** with no `tools/` or `src/`. One locked worktree is parked at
  `.claude/worktrees/agent-ae208d8d4e6645e39` (a live `claude` pid holds it; do not kill it).
  Until fixed: implement directly, and never run two file-writing agents at once.
- **NEVER point two model runs at one cache path.** `ResponseCache` loads its file once in
  `__init__` (`llm/cache.py:66-85`), so concurrent processes are blind to each other's writes. On
  2026-08-30 a broken liveness check (`pgrep` **does not exist here** and reports every process
  dead) led to a second sweep over a live one: **$12.33 spent, $4.60 wasted, 39 cache lines torn**,
  permanently unreplayable. *(The first post-mortem blamed `prompt_sha` drift and was wrong: a
  duplicate key proves the key was STABLE.)*
- **`CachingProvider` counts hits/misses and never prints them** (`llm/cache.py:127-128`). A 47%
  miss rate stayed invisible for 3,275 paid calls. Print the counter before spending.
- **One cache file per provider AND per model AND per measurement.** `config_hash` does **not** cover
  the code; manifests carry `pipeline_sha`. Land generator changes *before* spending.
- **A replay at the wrong sample size looks like a broken cache and is not.** Match the published
  invocation exactly — it is in `README.md` next to the figure.
- **A wrapper that hides an exit code turns a failure into a false success.** `timeout 590 … | tail`
  under-ran a 17-min AT-57 job and let the kill return 0. Twice, ~$1.15. Echo `$?`.
- **A test can be green while the infrastructure contradicts it.** `test_ingest.py` proved
  `batchItemFailures` isolates a poison record; the transcripts queue had no DLQ, so it retried for
  4 days and — being FIFO — blocked that customer's whole stream. Same shape: EMF was well-formed
  and produced **zero** metrics for want of `_aws.Timestamp`, and `notBreaching` made four alarms
  read **OK** rather than INSUFFICIENT_DATA. **Ask what the deployed thing actually did, not what
  the test asserts.**
- **Two thresholds disagree on purpose** — stream/`aws/ingest.py` use a fixed cut, `investigate` a
  budget-derived top-K. Never merge them.
- **Queue visibility timeout must be ≥ the consumer's function timeout** or AWS refuses the event
  source mapping outright. Derived as 6× from `deploy.FUNCTIONS`; never hand-type a second number.
- **`feed.py` is on the guarded surface and passes structurally** — conversations arrive via
  `cli.stream_inputs()`. Do not request an exemption; the cap is 3 and full.
- **`feed.py`'s crossings are not re-feed-stable** (a complete ledger makes every conversation
  cross); ledger/case/DLQ/API counts are. Never assert crossings == prediction.
- **Quote nothing at 10 seeds** — not re-measured on the widened corpus.
- **`stream.py` stays guarded only because `cli.stream_inputs()` hands it conversations.**
- **The account tool takes `risk_signal`, never `latent_risk`.**
- **Narration must never share the ledger reader's extractor**; a warm cache makes "live" a replay
  (`EARSHOT_CACHE_MODE=off`).
- **`outcome is not None` is always true** · a case id contains `#`, every link percent-encodes it ·
  never delete an `__init__.py` · verify `pwd` before committing.
- **AWS/deploy traps live in `aws-infrastructure.md`**, not copied here.
