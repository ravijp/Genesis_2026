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

## Next action — the 2026-09-10 cut round, then rehearse

**The build is done for now; the work is presentation.** Everything Ravi asked for on 2026-09-03 is
delivered except the $10 sweep, which he declined. Both stages are deployed and fed and the alarm has
fired.

**A meeting invite arrived 2026-09-03 that reframes the next gate:** **Thu 2026-09-10, 20:00–20:30**,
**Venkat (CEO) and Farhan (COO) judging**, and it **determines the shortlist** for the Final Dry Run
and Finals. Their ask is narrow — *committed vs what's actually done*. Script:
**`docs/gates/2026-09-10-sprint-review.md`** (business-first, exec audience, Q&A prep in §8).
`2026-09-07-sprint-3-demo.md` is the product-demo script and stays valid for whichever slot is a demo.

**Confirm the calendar before the 8th:** `CLAUDE.md` and `sources/genesis-committee-comms.md` both
record the Sprint 3 gate as frozen on **09-07**; the invite is **09-10**. Either it moved or these are
two events. Ravi owns that question — do not silently rewrite the frozen date.

**The one committed item that is missed: dry runs. Two committed, zero done** (checked — every
"dry-run" in the repo is a tooling flag, not a rehearsal). The script has Ravi owning it and booking
both for 09-08 and 09-09, with the demo recorded 09-09 so a room with no wifi cannot break it. **That
is now the highest-value remaining work.**

**Two live stages, same book, same infrastructure, one variable — this is the demo's spine:**

| | `dev` — keyless lexicon | `demo` — Haiku 4.5 |
|---|---|---|
| ledger entries | 34 | **103** |
| cases opened | 1 | **9** |
| desks receiving work | Collections only | **Complaints, 9 of 9** |

`dev` also agrees with the local pipeline to the last digit (`0.6526618648909545` vs `0.652662`) and
survived a double feed (260 messages → still 34 entries, 1 case). `earshot-dev-ingest-failures` went
**OK → ALARM** on one malformed transcript while the other five alarms stayed OK.

**Do these before 09-07, in order:**

1. **Rehearse Beat 2 and Beat 4 end to end (§7 of the script).** Beat 4 is the only beat with a live
   dependency and it carries 25 rubric points. **Record it on 09-06** so a room with no wifi cannot
   break it.
2. **Verify the two flagged-unverified claims** in the script, or drop them: the poison message
   reaching `earshot-dev-transcripts-dlq.fifo` (it was still retrying when last checked — redrive is
   configured at 3, so allow ~18 min), and the exact deployed spend from the `Earshot`/`CostUsd`
   metric on the `demo` stage. **They are marked in place; do not quietly promote them.**
3. **Re-login the morning of, and again before walking in.** The SSO token expires in hours.

**Optional, ~$0.90, Ravi has NOT approved it:** the `demo` stage reads with Haiku but *investigates*
with the offline rule engine, because `--extractor bedrock` sets the reader and `--provider` still
defaults to offline. So **8 of its 9 cases come back `insufficient_evidence` with `team=none`** — the
verdicts are the documented floor, not a result. `--provider bedrock` plus a re-feed would give real
verdicts, but a re-feed re-fires every crossing customer's conversations (~30 investigations). Decide
whether the demo needs it; the reader story does not depend on it.

**Declined 2026-09-03, do not re-propose:** the **$10 10-seed sweep** against the co-primary chance
gate the entry FAILS (18–8–4, `p=0.076`). The gate stays published as a failure.

**Settled 2026-09-03, do not reopen:** the UI write path **stays read-only and labelled** (a static
page cannot sign an IAM Function URL, and HITL-by-absence being literally true is an asset) · the
alarms get **no action** (EventBridge → Lambda would be the first outward-reaching thing here, and
CloudWatch already keeps two weeks of alarm history).

## State

**Arm B done** ($0.027705). `build-plan.md` §4 and §8's delta 8 are both updated — the brief's
comparison-model obligation is **retired on evidence**, not on an argument about wording. Nova Lite vs
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
