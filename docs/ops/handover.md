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

**2026-09-09** · `build/ear-on-every-call` · **908 tests** (903 pass, 5 skip) · ruff clean ·
separation guard over 45 modules + `tools/` · 30 UI routes · **~$2.45 of $12 spent**

## First turn

1. Say where the build stands and the next action, in two lines. Then start it.
2. **`export AWS_PROFILE=genesis`** or boto3 finds no credentials and fails looking exactly like a
   dead token. Every keyed figure replays free with `EARSHOT_CACHE_MODE=replay` (a miss raises).
3. `progress.md` for status, `decisions.md` before arguing, `state-of-play.md` for the numbers.

## Next action — the 2026-09-11 cut round, and one decision only Ravi makes

**The build is done. The work is presentation, and one fork in the road.**

**The gate is 2026-09-11, 20:30-21:00 IST.** Both 09-07 and 09-10 are dead (moved by Ravi on
2026-09-09). **Venkat (CEO) and Farhan (COO) judge it and it decides the shortlist** for the Final Dry
Run and Finals. They want: how strong the product is · **dollar value impact** · *could I pitch this
to a company and win a project*.

**① THE FORK — two scripts exist for this meeting and they disagree on market. Ravi decides.**

| | `docs/gates/2026-09-11-sprint-review.md` | `docs/credit-card/` (7 files) |
|---|---|---|
| market | **UK** | **US** |
| money lead | **£650 Ombudsman case fee** — a published tariff | a value chain with an admitted hole |
| depth | one script | two red-team passes, KS-1..KS-16 |

**Neither is deleted.** The US folder is the later and far deeper work and every instruction since
2026-09-08 has been about it — but it threw away the best number in the repo to get there, because
the US has no Ombudsman-tariff equivalent. **Do not start work on either until this is settled.**

**② The gen-AI reframe is done** (Ravi, 2026-09-09: *stop letting the keyless lexicon drive
numbers*). Evidence already bought and unused — same 282 conversations, same planted truth: Haiku 4.5
finds complaint escalation **60/65** vs the lexicon's **1/65**, churn **40/77** vs **16/77**, life
event **50/68** vs **9/68**, and **loses distress 27/72 vs 33/72**, published. Keylessness is an
auditor's reproducibility property, **never a product claim**.

**③ A keyed 10-seed run is in flight** — `earshot run --seed 1..10 --customers 200 --extractor model`,
Haiku 4.5, ~$1.06/seed, **~$10.6**, cache `artifacts/cache/extractor-cardstory-haiku.jsonl`. **It cannot test whether
accumulation survives a model reader, and a free control proved that**: at this scale (200 customers,
K=20) the *offline* reader scores `full-ledger` vs `window3-top2` at **4-3-3, p=1.00** against its
published **30-0-0** at 1500 customers. The scale is the confound, not the reader. **A powered keyed
version is blocked by wall-clock, not money** (~52,000 sequential model calls). **30-0-0 stands.**
What the run does buy: reader quality at ten seeds (**extraction recall 0.68 model vs 0.24 lexicon**),
quote fidelity, cost, latency, and keyed mechanism ablations.

**Then: the dry runs. Two committed, zero done** — still the highest-value remaining work. Book
**09-09 and 09-10**, and **record the demo on 09-10** so a room with no wifi cannot break Beat 3.

**Declined 2026-09-03, do not re-propose:** the $10 10-seed sweep *against the chance gate*. The gate
stays published as a failure (18-8-4, `p=0.076`). *(The keyed run above is a different measurement
for a different purpose and Ravi authorised it on 2026-09-09.)*

**Settled, do not reopen:** UI stays read-only and labelled · alarms get no action.

## State

**2026-09-09: four claims in the card folder were wrong and are corrected in place.** **SR 11-7 is
rescinded** (superseded 2026-04-17 by **SR 26-2**, joint OCC/Fed/FDIC, over **$30bn**) · **"distress
signals are structurally blocked from feeding an offer — a branch in code" is FALSE**, there is no
offer surface to block, only `TRAJECTORY_TEAM` (`schema.py:35-40`) plus absence · **charge-offs 3.82%**
(CORCCACBS; **G.19 publishes none**) · **$6,610 is per borrower**, $1.263T ÷ 608M = **$2,077**.

**The confidence float is load-bearing and uncalibrated** — `memory.py:99` makes it a direct
multiplier, sharing a field with the lexicon's constants. Over 30 offline datasets, removing it moves
**20% of the top-150**; **escalation is inert (100.0% on all 30)**. Fix: **bucket to three tiers, ~1
day**. **CFPB gold set is 55/150 card narratives** — reader fires **29/29** on marked card documents
but **churn intent 1 of 8**; say both together. **Pre-delinquency withdrawn and settled** (3-9x not
7-10x; its T3 was backwards — hardship is opt-in). Detail: `docs/credit-card/06-DEFENDING-THE-SCORE.md`
and `00-READ-THIS-FIRST.md`.

**Arm B done** ($0.027705), comparison-model obligation retired on evidence. **D-031** primary is
`full-ledger` vs `window3-top2` (**30-0-0 offline — being re-measured keyed**). **AT-57 29/50** ·
**AT-58 27/48** · **AT-52 keep all four** · **239/485 entries worth more now than at write, 0/485
under a plain count.** One deployment (Northwind), nine seams, five the client's. **CDK does not work
here** (D-024). `boto3` optional; a fresh clone runs keyless.

*(This file is ~30 lines over its 60-line budget. The overage is the live 09-11 fork and the in-flight
keyed run — both resolve by 09-11. **Reclaim it then**, rather than letting the budget rot.)*

## Traps no test can catch

- **NEVER point two model runs at one cache path.** `ResponseCache` loads its file once in
  `__init__` (`llm/cache.py:66-85`). On 2026-08-30 a broken liveness check (`pgrep` **does not exist
  here** and reports every process dead) launched a second sweep over a live one: **$12.33 spent,
  $4.60 wasted, 39 cache lines torn**, permanently unreplayable. *(The first post-mortem blamed
  `prompt_sha` drift and was wrong — a duplicate key proves the key was STABLE.)*
- **`config_hash` does not include the EXTRACTOR, so an offline run and a model run at the same seed
  and customer count write the SAME artifact filename and silently overwrite each other.** Cost me
  keyed seeds 1-3 on 2026-09-09: an offline control launched while a paid keyed sweep was mid-flight
  overwrote `run-1..3-<hash>.json` with offline results. **No money was lost** — the paid reads were
  in the extractor cache, so `EARSHOT_CACHE_MODE=replay` regenerated them for $0 — but the artifacts
  were gone and the aggregate silently reported 5 datasets instead of 8. **Check `manifest.provider`
  after any run you did not watch, and copy keyed artifacts somewhere safe before running anything
  else at the same seed/customer count.** This is the artifact-level twin of the one-cache-per-run
  rule below.
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
