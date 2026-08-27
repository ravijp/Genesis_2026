# INDEX — repo map (branch `build/ear-on-every-call`)

> **Maintenance rule:** any commit that adds, moves, or removes a file MUST update this index in the
> same commit. One line per file: what it is + status.
> Status legend: `[stable]` authored & reviewed · `[skeleton]` structure awaiting content ·
> `[source]` external input, do not edit · `[generated]` produced by a command, never hand-edited.
>
> *Broken by three commits on 2026-08-09, including the one that added the conventions documents.
> Run `git show --stat` against this file before committing.*

**This branch is scoped to the build.** The research and ideation phases were pruned 2026-08-09 and the
build promoted to a `src/` layout. Nothing is lost — all of it is on `main`:
`git checkout main -- <path>`.

## Reading order for a fresh session

1. `ops/state-of-play.md` — **start here.** Current state, in one screen
2. `ops/decisions.md` — what is settled and what was rejected
3. `ops/working-agreements.md` — the disciplines, each bought with a mistake
4. `../README.md` — what this is, and the current numbers
5. `architecture/architecture.md` — the shape of the system, with diagrams

Paths below are relative to this file's home, `docs/`, except the Root section.

## Root

Code and config only, plus the two `.md` files that must live here (D-023).

- `README.md` — front door: quick start, the numbers with their denominators, model access, repo map `[stable]`
- `CLAUDE.md` — LLM session instructions and the load-bearing build rules. **Stays at root**: Claude Code auto-loads it from the project root, and in `docs/` it silently stops being read `[stable]`
- `pyproject.toml` / `uv.lock` / `.python-version` — uv-managed Python 3.13, hatchling build, `earshot` installed editable, console script `earshot` `[stable]`
- `.env.example` — every `EARSHOT_*` variable with dummy values; the real `.env` is gitignored `[stable]`
- `.aws.config.example` — template for `~/.aws/config`: the `[sso-session]` + `[profile]` form, with placeholders for the start URL, account and role. Names where credentials come from, never a credential `[stable]`
- `.gitignore` — ignores regenerable output and secrets; deliberately KEEPS `artifacts/cache/` and `artifacts/runs/pinned/` tracked so a judge can replay without keys `[stable]`
- `.markdownlint.json` — config for a linter nothing in this repo invokes; presumably an editor extension reads it `[stable]`
- `.claude/settings.json` — **enforces the edit-approval tiers** that CLAUDE.md states in prose: `docs/sources/` is denied outright, and `decisions.md`, `working-agreements.md`, `CLAUDE.md`, `docs/architecture/`, the frozen benchmark protocols and the committed artifacts all prompt before an edit. Read-only commands are pre-allowed so routine work does not prompt. Committed deliberately — it is team policy, not personal config; `settings.local.json` is the per-developer file and is gitignored `[stable]`
- `Dockerfile` — one image for all three Lambdas and the sweep task; which handler runs is a CMD override, never a separate build. Carries `prompts/` and pins `EARSHOT_PROMPTS`/`EARSHOT_ARTIFACTS` rather than relying on path fallbacks that break in a wheel install `[skeleton]`
- `.dockerignore` — keeps `prompts/`, `src/`, `uv.lock` in; everything regenerable or judge-facing out `[stable]`
- `buildspec.yml` — CodeBuild: ruff → pytest → image → ECR → `cdk deploy`. Lint and tests run *before* the image build so a broken commit fails fast. Deploys the immutable digest, never the tag `[skeleton]`

## src/earshot/ — the product

Commands: `earshot sweep` (the only source of quotable numbers) · `earshot demo` · `earshot investigate` · `earshot run` (single dataset, debugging only)

- `schema.py` — core types. `SeededSignal` (answer key) and `ExtractedSignal` (belief) are separate types on purpose. `CustomerTruth` keeps `latent_risk` and `financial_state` apart `[stable]`
- `config.py` — every tunable parameter; records that saturation cannot affect equal-budget rankings `[stable]`
- `corpus_lexicon.py` — **authoring pass A**: the utterance fragments that get planted `[stable]`
- `extract_lexicon.py` — **authoring pass B**: extractor cues, authored without reference to pass A. The partial overlap is the source of the honest miss rate — do not "fix" it `[stable]`
- `corpus.py` — dataset generation. Strata labelled from generation parameters; outcomes drawn from latent risk `[stable]`
- `extract.py` — stateless extraction + the offline lexicon provider `[stable]`
- `extract_model.py` — **the model reader**: the second implementation of the `Extractor` protocol. One conversation per call, no customer id in the prompt, verbatim quotes or the signal is dropped, cost and latency per call. Never yet run against a real model `[stable]`
- `prompt_files.py` — versioned prompt loading and hashing, shared by the investigator and the model reader `[stable]`
- `memory.py` — **the heart**: append-only ledger + pure-code re-scorer. `score()` returns copies and never mutates the ledger `[stable]`
- `arms.py` — **eight** comparison arms through one code path + per-mechanism ablations. `stateless-top2` and `window3-top2` are the two that currently beat the ledger on its own pre-registered stratum `[stable]`
- `evals.py` — equal-alert-budget comparison by top-K ranking, per-stratum breakdown, extraction fidelity, corpus diagnostics `[stable]`
- `sweep.py` — **multi-seed evaluation**: paired seed-by-seed comparison on any metric, exact sign test, and the integers behind every rate `[stable]`
- `cli.py` — the four commands, run manifests, artifacts `[stable]`
- `case_record.py` — **the persisted case, one shape for two destinations.** `earshot investigate`'s artifact on disk and the DynamoDB `CASES` item are both built by `case_record()`, so the reviewer UI renders either. boto3-free by construction, which is what lets the keyless CLI share it. Carries **two moments**: `score_at_open`/`opened_on_day` from the crossing, and `score`/`as_of_day`/`evidence` from the customer today — merging them either ranks a faded case at its opening-day seat or freezes the retro chain at the day the case opened `[stable]`
- `__init__.py` (package root, and in `agent/`, `aws/`, `core/`, `llm/`) — package markers, **all on the guarded surface because an `__init__.py` can re-export anything** (`test_separation.py:75-84`). Their re-export bodies are largely unused — every consumer imports from the submodule — but **deleting a file drops the guard from 20 modules to 19 and the suite from 75 tests to 72 with everything still green.** Empty the body if you must; never remove the file `[stable]`
- `core/accounts.py` — synthetic account state and transactions behind the agent's tools. Derives from `(customer_id, financial_state, seed, as_of_day)` and **never** from a truth object `[stable]`
- `agent/schemas.py` · `tools.py` · `investigator.py` · `prompts.py` — the investigator: strict decision schema with mandatory evidence, five pure tools, a bounded loop, versioned prompt loading `[stable]`
- `llm/base.py` · `openrouter.py` · `offline.py` · `cache.py` · `bedrock.py` — provider abstraction, cost and latency capture, content-addressed response cache with record/replay. `LazyOpenRouterProvider` builds its client on first use so replay needs no key `[stable]`
- `aws/__init__.py` — AWS entrypoints. Inside the package **so the separation guard covers the deployed decision path**: adding it took the guard 72 → 75 tests with no edit to the test. Handlers (`ingest`, `investigate`, `api`) and DynamoDB `stores.py` land here `[skeleton]`
- `llm/bedrock.py` — **the Bedrock provider.** Converse translation both ways, default Haiku 4.5 (D-025), `normalize_model_id()` adds the `us.` inference-profile prefix Anthropic ids require and leaves Nova/Llama bare. Cost is **computed from a dated price table, never charged** (G1); an unpriced id returns 0.0 rather than a guess. Client built on first use, so replay and the tests need no credentials `[stable]`
- `aws/ingest.py` — **the live path.** One SQS record → `Conversation` → `extract()` → conditional ledger append → reload → **unchanged `SignalLedger`** → threshold. Returns `batchItemFailures`, so one poison transcript fails alone instead of redelivering the batch and re-running every extraction in it. **The online threshold is a fixed cut and is NOT the local budget-derived one** — a streaming handler has no population to rank against, and the two numbers will disagree `[stable]`
- `aws/api.py` — **the reviewer API**: five reads for the three screens (ranked queue, one case, its reviews, a customer's standing ledger, the transcript behind a quote) and **one write** that appends to `ReviewStore` and moves the case's status without ever touching its evidence — infrastructure.md Q3 answered as "only annotate". **No endpoint contacts anyone**, and a test asserts the absence, because that is how HITL is enforced here. CORS is off unless an origin is configured; an unexpected error returns `{"error": "internal error"}` and logs the rest `[stable]`
- `aws/transcripts.py` — the transcript wire format **and** the S3 evidence archive, together so `ingest` and `investigate` cannot drift on what a transcript is. The ledger stores signals, not conversations, so without this the deployed investigator's every citation is unresolvable. **Write-once degrades honestly**: Object Lock needs bucket creation and `s3://agentic-trio` was made without it, so the guarantee is a conditional put (`IfNoneMatch="*"`) — it stops overwrite and redelivery, not a deliberate `DeleteObject` `[stable]`
- `aws/investigate.py` — queue consumer: crossing → ledger → **unchanged `investigate()` loop** → `CaseStore`. The message's score is used only to detect drift; the score of record is recomputed. **The account tools are synthetic** — no bank core feed exists, `latent_risk` is a SHA-256 draw from the customer id, and every case carries `account_data: "synthetic"` so no screen can present it as a record `[stable]`
- `aws/stores.py` — DynamoDB ledger/cases/reviews. Case serialization comes from `case_record.py`; `put_case` adds only `pk`/`gsi1pk`/`gsi1sk` on top, and the ranked queue sorts on the **current** score, not the crossing-day one. Every ledger write conditional on `attribute_not_exists(sk)`, so a duplicate delivery is a no-op and its failure count is the duplicate metric (A7). **No delete method exists on `LedgerStore`**, and a test scans the class surface for anything delete-shaped (A6). Scoring is delegated to the unchanged `SignalLedger` — a test asserts a round-trip is bit-identical `[stable]`

## Not created yet — decided, and where it goes

**`infra/` does not exist.** Empty directories are invisible to git, so creating it before there is
content would put a lie in this file. The placement is settled; the first real file creates the folder.
(`ui/` was in this section until 2026-08-28 and now has its own, below.)

- `infra/` — AWS CDK in Python, two stages (`dev`, `demo`), one account. Named for its role, not its tool: §3.5 records Terraform as the rejected alternative, so the tool is revocable and must not become the directory's name. Wired as the `[dependency-groups] infra` group **already in `pyproject.toml`**, never a second project — a separate venv could not `import earshot` without the PYTHONPATH hack CLAUDE.md forbids

## tests/

- `test_separation.py` — **import guard**: nothing on the decision path may import the generator, its lexicon, or a ground-truth type. Discovers its own surface by glob `[stable]`
- `test_bedrock.py` — 33 tests against a stubbed `converse()`. Passes whether or not boto3 is installed, and that is itself under test `[stable]`
- `test_stores.py` — 39 tests against a hand-rolled fake table. Duplicate-delivery no-op, Decimal round-trip, the absent delete surface, and score delegation `[stable]`
- `test_ingest.py` — 18 tests over the real path (fake DynamoDB, fake SQS, no model): a sub-threshold signal is retained and still counts later, two conversations cross where neither alone would, the online score equals `memory.py`'s bit for bit, redelivery changes nothing, one poison record fails alone `[stable]`
- `test_ui.py` — 9 tests: the fixture's rows are the API's own rows, the queue ranks on the score today, cases pass through untouched, no answer-key field reaches a browser, a citation without a transcript fails the build, and every screen renders (via `ui/smoke.mjs`, skipped with no node) `[stable]`
- `test_api.py` — 24 tests over the real routing and the real stores: no answer-key field reaches a response body, no route contacts anyone, a review annotates without mutating evidence, a truncated queue says so, and a 500 carries no stack trace `[stable]`
- `test_transcripts.py` — 12 tests against a fake S3: lossless round trip (a lost turn index breaks every citation), a redelivery refused by the precondition rather than silently applied, and a customer with more than one page of history read in full rather than truncated at page one `[stable]`
- `test_investigate_handler.py` — 17 tests on the crossing→case path with the offline rule engine: the score of record is recomputed and drift is reported, a missing archive fails loudly, re-investigation overwrites one case, and a customer who no longer crosses produces none `[stable]`
- `test_case_record.py` — 7 tests on the persisted case: disk and DynamoDB carry the same fields (drift here surfaces on stage, not in CI), every quote keeps its then-vs-now score, the queue ranks on today, and no answer-key field reaches a client-facing record `[stable]`
- `test_no_answer_key_leak.py` — **data guard**: nothing may receive a value that *encodes* a ground-truth field. The one that would have caught the leak we actually had. Discovers `AccountSnapshot`'s numeric fields rather than listing them — a hand-written list once named a field that did not exist and silently skipped `[stable]`
- `test_memory.py` — ledger invariants: never-discard, accumulation, retro re-score, decay, determinism `[stable]`
- `test_tools.py` — every agent tool, in-memory, no network `[stable]`
- `test_agent.py` — decision schema, bounded loop, the cost cap holding under a rising cost curve (and the documented spike case where it cannot), a crashing tool being contained `[stable]`
- `test_sweep.py` — the multi-seed harness: sign test vs hand computation, pairing on seed, denominators present and identical across arms, equal alert budget, determinism, counted-not-reconstructed integers, artifact reproducibility `[stable]`
- `test_cli.py` — the commands, and the demo's internal consistency: its narration may not contradict the claim it selected on, and its denominator must count customers. Also that the `investigate` artifact is **sufficient on its own** — the reviewer UI must never regenerate the corpus from `manifest.seed` to fill in missing fields `[stable]`
- `test_extract_model.py` — the model reader against a stub provider: statelessness (no customer id in the prompt), verbatim quotes or nothing, the offline path's grain and floor, record-then-replay, and that the default reader stays keyless `[stable]`

## ui/ — the reviewer SPA, three screens, no build step

Open `ui/index.html`. No npm, no bundler, no dev server, no network — three static files plus a
generated, committed `data.js`, so a judging room with no wifi still sees the product (D-004), and
`aws s3 sync` deploys it today while CodeBuild is blocked (W9). Details in `ui/README.md`.

- `index.html` · `styles.css` · `app.js` — ranked queue (`#/queue`), one case (`#/case/<id>`), the retro re-score (`#/case/<id>/retro`), and the transcript behind a cited quote. Renders the **same objects** the deployed API returns; computes nothing; escapes all customer speech before it reaches innerHTML `[stable]`
- `data.js` — **generated and committed** by `tools/ui_fixture.py` so a fresh clone works with no Python run. A `<script src>` rather than a JSON fetch, which is what makes `file://` work. Carries its manifest, and the page prints provenance in a banner on every screen `[generated]`
- `smoke.mjs` — renders all seven routes against a stub DOM in node. Catches what `node --check` cannot: a route that throws, a field renamed in `case_record()` that the page still reads, a placeholder leaking into the markup. Run by `uv run pytest` when node is on PATH `[stable]`

## benchmarks/cfpb/ — AT-43, the extractor on real complaint narratives

Self-contained and replicable end to end: pre-registration, marking guide, one script per step, every
API call and output hash logged. Run `steps/05_score.py` alone to reproduce the numbers offline.

- `README.md` — how to replicate, in order; what is in the folder; data provenance and licence `[stable]`
- `PROTOCOL.md` — **the pre-registration**, frozen before any narrative was read: frame, panels, wrapping rule, interpretation thresholds, freeze rules, and an amendment log `[stable]`
- `MARKING-GUIDE.md` — how a narrative is marked, derived from the construct definitions and never from the extractor's cues `[stable]`
- `RUNLOG.md` — append-only log of every run: command, date, counts, output SHA-256. Corrections are appended, never edited in `[generated]`
- `steps/_common.py` — API client with logging, the frame constants, hashing, run log `[stable]`
- `steps/01_frame.py` — frame counts via the search API; now an independent cross-check of the archive `[stable]`
- `steps/02_download.py` — the bulk archive (~1.3 GB), verified by size and SHA-256, stored outside the repo `[stable]`
- `steps/03_filter.py` — streams the archive into the 2025 retail-banking frame; fails if it disagrees with the API total `[stable]`
- `steps/04_draw.py` — seeded, exactly uniform draw of Panel A and Panel B from the local frame `[stable]`
- `steps/05_score.py` — a reader against the gold marks. Default: the unmodified offline extractor, offline and keyless, reproducing every published figure. `--extractor model` adds the model reader as a second arm (PROTOCOL §9) and writes `out/results-model.json` `[stable]`
- `steps/mark.py` — the marking tool: shows documents with panel/stratum withheld, validates a mark set (every positive mark's span must appear verbatim in its narrative), picks the second-marker subset from the seed, and reports Cohen's kappa `[stable]`
- `out/frame.json` · `frame_local.json` — frame counts from the search API and from the bulk archive; they agree to the record `[generated]`
- `out/sample.jsonl` · `draw_manifest.json` — the 150 drawn narratives and the seed, indices and ids behind the draw `[generated]`
- `out/gold.jsonl` · `gold_second.jsonl` — the hand marks (150) and the independent second marking (30) `[stable]`
- `out/results.json` · `source_archive.json` — the scored result, and the SHA-256 of the 1.31 GB source archive `[generated]`

## benchmarks/pool-widening/ — authored, measured, parked

- `README.md` — why 56 new fragments exist, how they were authored blind, and the measurement that parked them `[stable]`
- `fragments.py` — the 56 fragments, **not** wired into `corpus_lexicon.py`; splicing is blocked on the extractor `[stable]`

## tools/

- `aws-login.ps1` · `aws-login.sh` — **run first, every session.** Login only if the token is dead, then verify every permission. `-Force`/`--force` reissues the SSO session, which is how a new IAM grant actually takes effect `[stable]`
- `ui_fixture.py` — turns an `earshot investigate` artifact into `ui/data.js`. **Reformats, never computes**: queue rows come from `api._queue_row`, the same function the deployed `GET /cases` uses, so the offline screen and the live screen render identical objects. Refuses to write an answer-key field or a citation with no transcript `[stable]`
- `deploy.py` — **the deploy path** (CDK is unusable, D-024): one zip → S3 → three Lambdas, dry-run by default, idempotent. Deps are **cross-compiled for manylinux cp313** — `pydantic-core` is a compiled extension and a Windows-built zip dies at import inside Lambda. The zip's sha goes in the S3 key and every function's description, so "are all three running the same code?" is readable rather than inferred. Deployed keyless by default (`--extractor` / `--provider` flip to Bedrock) `[stable]`
- `provision.py` — idempotent boto3 provisioning, **dry-run by default**. Three tables, three queues with DLQ redrive. Schema imported from `stores.TABLE_SPECS` so the two cannot drift. Teardown has no code path that can delete the ledger. Known permission gaps print **PARKED** rows naming the gap, the owner and the workaround. PITR is enabled with a bounded retry: a table is ACTIVE seconds before its backups subsystem is, and the gap reports as `ContinuousBackupsUnavailableException`, which reads like a permission problem `[stable]`
- `aws_probe.py` — 34 probes at build depth, each naming the IAM action and what breaks without it. Creates-then-deletes where a write is the only honest test `[stable]`
- `aws_check.py` — shorter pre-flight; leads with the two irreversible questions (S3 Object Lock, CloudFormation) `[stable]`

## tools/jira/

- `adf.py` — renders a markdown subset into Atlassian Document Format so descriptions are readable `[stable]`
- `client.py` — minimal Jira client that records and reports every failure `[stable]`
- `apply_standards.py` — board content for every issue, in one reviewable place `[stable]`

## prompts/

- `investigator/v1/system.md` · `task.md` — prompts as versioned files, so a change is a reviewable diff `[stable]`
- `extractor/v1/system.md` · `task.md` — the model reader's prompt: the four constructs, the evidence rule, the JSON contract. Authored from what each construct *means*, not from the corpus lexicon, the extractor's regexes, or the CFPB marking guide `[stable]`

## docs/

- `INDEX.md` — this map. Moved here from the root by D-023 `[stable]`
- `ops/state-of-play.md` — **the boot file.** Where we are, what is in flight, what is blocked, the next three things. One screen, rewritten in place, never appended `[stable]`
- `ops/decisions.md` — why things are the way they are and what was rejected, so a fresh session does not re-litigate settled ground `[stable]`
- `ops/working-agreements.md` — **read before changing anything.** Evaluation discipline, the two-level answer-key guards, demo honesty, keeping docs in step with code, test discipline, bulk-operation discipline, delegation `[stable]`
- `ops/jira-conventions.md` — how the AT board is written and updated `[stable]`
- `ops/handover.md` — **the resume file.** Paste its path into a fresh conversation and the build continues. Rewritten in place at every handover, one screen max. Carries the next action, the traps already paid for, and when to hand over `[stable]`
- `ops/progress.md` — the build log: work packages with status, blockers with owners, and the evidence table for why CDK was ruled out `[stable]`
- `ops/aws-infrastructure.md` — **the single record of live AWS fact**, as opposed to `architecture/infrastructure.md`'s design: account `859430413223`, permission set, region us-east-1 (confirmed by the CodeCommit host), `s3://agentic-trio`, the CodeCommit URL, and the granted-service list with what its two gaps (no Kinesis, one bucket not two) cost us. Then credentials: SSO-minted short-lived tokens only, no static secret anywhere, the two credentials NOT to use, and the interim static-key path while CLI v2 awaits an admin install `[stable]`
- `architecture/architecture.md` — the shape of the system: three layers, data flow, agent loop, runtime, what is measured `[stable]`
- `architecture/build-plan.md` — **v3.** What is left to build and what is still open: the agent layer, what is measured vs not, four open questions, the 08-24 scope, risks, and the deltas from the submitted brief `[stable]`
- `architecture/infrastructure.md` — **AWS technical design.** §1 architecture (live + batch paths, data model, two-provider model layer, numbered assumptions `A1..A11` and open questions `Q1..Q5` written to be red-teamed) · §2 scope of build (work packages W1-W11, critical path, out of scope) · §3 service selection with a rejected alternative per choice · §4 failure modes · Appendix A provisioning table, one row per SKU, with the Bedrock per-model ARNs needing console opt-in · Appendix B cost model at build and 500k-conversation scale, plus the $200 budget `[stable]`
- `gates/2026-08-10-sprint-1-checkin.md` — Sprint 1 check-in brief `[stable]`
- `gates/committee-requirements-email.md` — the tooling/access emails, **sent and fully answered**: Bedrock was the route, `s3://agentic-trio` and the CodeCommit repo exist. Two of its asks are now things we actively refuse — an OpenAI key (D-022) and HTTPS Git credentials (unusable with SSO). **Kept, not deleted, only because `sources/genesis-committee-comms.md:74` cites it and `sources/` is never-edit** `[stable]`
- `impact/finance-brief.md` — finance value-chain research; feeds the Zenon-impact axis `[stable]`

## artifacts/

- `runs/pinned/` — one committed run + manifest `[generated]`
- `cache/investigator-demo.jsonl` — committed model responses so the demo replays with no keys `[generated]`
- `cache/extractor.jsonl` — the model reader's own cache, written by the first keyed extraction run so the measurement replays keyless. Does not exist yet — no keyed run has happened `[generated]`
- `runs/` (unpinned) — per-run output, gitignored `[generated]`

## sources/ — primary inputs, do not edit

Inside `docs/` since D-023, but still the one folder under it that is **not** ours to rewrite.

- `submission-ear-on-every-call.md` — verbatim finalized Track A idea sent to the committee 2026-07-24 `[source]`
- `genesis-committee-comms.md` — frozen gate dates, the Sprint-1 downgrade, tooling status `[source]`
- `kickoff-notes.md` — competition facts: tracks, deliverables, rules, judging rubric `[stable]`
- `zenon-client-context.md` — client roster; input to the Zenon-impact narrative `[stable]`
- `2026 Zenon Agentic AI Competition Kickoff.pdf` — official kickoff deck `[source]`

## Tracked elsewhere

Sprint backlog: JIRA project **AT (Agentic Trio)**, `https://zenonai.atlassian.net`. Read live
2026-08-25: **45 issues, `AT-38`–`AT-82`, 8 epics + 37 tasks — 28 In Progress, 17 To Do, 0 Resolved.**
No `[DELETE ME]` issues remain in the live set; whether an admin removed them or the note was always
stale is unknown. **Sprints are enabled** — board 209 has `AT Sprint 1` (`id=672`, state `future`,
created 2026-08-11), unstarted and unassigned, so the team is tracking gates by due date instead.
Earlier notes here and in `ops/jira-conventions.md` saying sprints could not be enabled are wrong.

AWS is provisioned — account, region, bucket and CodeCommit URL are in `ops/aws-infrastructure.md`.
**No AT ticket covers any of the eleven AWS work packages `W1`–`W11`** in
`architecture/infrastructure.md` §2.2; the board predates that document.
