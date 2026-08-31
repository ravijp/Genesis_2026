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

0. `ORIENTATION.md` — **if you have never seen this project.** What it is, the vocabulary every
   other document assumes, what is true and what is not, in fifteen minutes. Written for a
   newcomer, a judge, or yourself in three months `[stable]`
1. `ops/state-of-play.md` — **start here** once oriented. Current state, in one screen
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
- `.github/workflows/ci.yml` — **the CI that actually runs.** ruff → pytest → `ui/smoke.mjs` → `ui/contrast.mjs` → a 3-seed keyless sweep, on every push. Installs node on purpose: `test_ui.py` skips both UI gates when node is absent, so a green suite can have them silently off `[stable]`
- `buildspec.yml` — **parked, has never run, cannot run as written.** CodeBuild is blocked on the W9 IAM denial, and the file predates D-024: it calls `cdk deploy`, `cd infra` (no such directory) and `npm run build` in a build-step-free UI. Header says so. Left as a dated record of a superseded design rather than rewritten into a second unrunnable file `[skeleton]`

## src/earshot/ — the product

Commands: `earshot sweep` (the only source of quotable numbers) · `earshot demo` · `earshot investigate` · `earshot run` (single dataset, debugging only)

- `schema.py` — core types. `SeededSignal` (answer key) and `ExtractedSignal` (belief) are separate types on purpose. `CustomerTruth` keeps `latent_risk` and `financial_state` apart `[stable]`
- `config.py` — every tunable parameter; records that saturation cannot affect equal-budget rankings `[stable]`
- `corpus_lexicon.py` — **authoring pass A**: the utterance fragments that get planted `[stable]`
- `extract_lexicon.py` — **authoring pass B**: extractor cues, authored without reference to pass A. The partial overlap is the source of the honest miss rate — do not "fix" it `[stable]`
- `corpus.py` — dataset generation. Strata labelled from generation parameters; outcomes drawn from latent risk `[stable]`
- `extract.py` — stateless extraction + the offline lexicon provider `[stable]`
- `extract_model.py` — **the model reader**: the second implementation of the `Extractor` protocol. One conversation per call, no customer id in the prompt, verbatim quotes or the signal is dropped, cost and latency per call. **Scored 2026-08-28**: 0.8214 strict recall (92 / 112) on real CFPB narratives against the lexicon's 0.0357, at 8x the false-positive rate. Named after the model that ANSWERED, not the one requested `[stable]`
- `prompt_files.py` — versioned prompt loading and hashing, shared by the investigator and the model reader `[stable]`
- `memory.py` — **the heart**: append-only ledger + pure-code re-scorer. `score()` returns copies and never mutates the ledger `[stable]`
- `arms.py` — **nine** comparison arms through one code path + per-mechanism ablations. The ninth, **`random-rank`**, is a negative control that ranks customers by a seeded RNG and ignores every signal — the chance floor the other eight are measured against, not a competitor. `stateless-top2` and `window3-top2` beat the ledger on the pre-widening corpus and lose to it on the widened one (2026-08-30) `[stable]`
- `evals.py` — equal-alert-budget comparison by top-K ranking, per-stratum breakdown, extraction fidelity, corpus diagnostics. `evaluate_arm()` also returns **`precision`** (hits / flagged at the budget), which `sweep.py` pairs seed-by-seed like every other metric `[stable]`
- `sweep.py` — **multi-seed evaluation**: paired seed-by-seed comparison on any metric, exact sign test, and the integers behind every rate. `randomise_ties=True` breaks ties with an independent seeded RNG instead of `customer_id`, to test whether a headline record depends on the tie-break rule. `sweep_budgets()` reuses one corpus and one extraction per seed across several review budgets (1%/2%/5%/10%), so a recall/precision curve costs the same generation work as a single-budget sweep `[stable]`
- `cli.py` — the four commands, run manifests, artifacts `[stable]`
- `case_record.py` — **the persisted case, one shape for two destinations.** `earshot investigate`'s artifact on disk and the DynamoDB `CASES` item are both built by `case_record()`, so the reviewer UI renders either. boto3-free by construction, which is what lets the keyless CLI share it. Carries **two moments**: `score_at_open`/`opened_on_day` from the crossing, and `score`/`as_of_day`/`evidence` from the customer today — merging them either ranks a faded case at its opening-day seat or freezes the retro chain at the day the case opened `[stable]`
- `__init__.py` (package root, and in `agent/`, `aws/`, `core/`, `llm/`) — package markers, **all on the guarded surface because an `__init__.py` can re-export anything** (`test_separation.py:75-84`). Their re-export bodies are largely unused — every consumer imports from the submodule — but **deleting a file drops the guard from 20 modules to 19 and the suite from 75 tests to 72 with everything still green.** Empty the body if you must; never remove the file `[stable]`
- `tenants.py` — **the per-client configuration layer.** A deployment is one `RunConfig` (its own corpus and decay half-lives), one fixed alert threshold, one map from the four canonical `OwningTeam` slots onto the names that client's org uses, and a `Seam` list describing the nine pipeline stages and who owns each. **One profile ships**; the machinery stays general because that machinery *is* the seam a second client arrives through. The team map is display-only on purpose: widening `OwningTeam` per client would put a client string inside the model's decision contract, and the closed `Literal` is what stops a model inventing a destination no queue drains. Six of nine seams are `ours=False` — the deployment screen counts them rather than asserting that this is a layer `[stable]`
- `read_live.py` — **reading a call while it is still open.** Re-asks the reader after each customer turn on the transcript heard *so far*, so a belief is watched forming instead of arriving finished, and `_diff()` names the five ways it can move (appeared, firmed, faded, withdrawn, requoted). Two properties make it a measurement rather than theatre: the model gets a genuine **prefix**, never the whole transcript with a smaller number attached; and the final step's request is byte-identical to the batch read, so under a content-addressed cache they are one entry — which is the guarantee that the belief at the end of the animation is the belief that was appended. Runs on its **own** extractor instance, because prefix reads landing in `ExtractionTelemetry.conversations` would divide the same money by nine times the work and report a cost-per-conversation that is fiction `[stable]`
- `stream.py` — **the arrival stream**: conversations walked in global day order across the whole book, one frame per conversation, each carrying what the reader found, the customer's score before and after, the re-ranked board, and the per-call cost and latency. Frames are computed by `memory.py` here so the browser can be a dumb player. **It never generates a corpus and never builds a `ToolContext`** — both are handed in by `cli.stream_inputs()`, which is what lets it sit on the separation-guarded surface with every other reader rather than needing an exemption. The threshold is a **fixed cut**, mirroring `aws/ingest.py`, not the budget-derived one `earshot investigate` reports `[stable]`
- `stream_server.py` — `earshot stream --serve`: the same `run_stream()` over Server-Sent Events on 127.0.0.1, so a demo can make real Bedrock calls while a room watches. **Credentials never leave the process**; the browser holds an EventSource and nothing else. No write route exists at all and a test asserts it. The LIVE badge names the cache mode, because once the reader cache is warm a "live" run serves recorded completions `[stable]`
- `core/accounts.py` — synthetic account state and transactions behind the agent's tools. Derives from `(customer_id, financial_state, seed, as_of_day)` and **never** from a truth object `[stable]`
- `agent/schemas.py` · `tools.py` · `investigator.py` · `prompts.py` — the investigator: strict decision schema with mandatory evidence, five pure tools, a bounded loop, versioned prompt loading `[stable]`
- `llm/select.py` — **which provider, in one place.** `build_provider()` resolves a name (`$EARSHOT_LLM`, default **bedrock** since D-022 retired the OpenRouter key), applies the cache mode, and wraps the result in the spend ceiling. Explicit `if`/`elif`, never a registry. It exists because three call sites had each decided this separately and drifted — the reader could not reach Bedrock at all, which is why no keyed run was possible until 2026-08-28 `[stable]`
- `llm/budget.py` — **the spend ceiling (W4)**, in our own code because `budgets:*` and `ce:*` are denied. `CappedProvider` refuses the call *before* the one that would cross the line, so it is a control and not a report. Layered **outside** the cache, so a keyless replay run can never be exhausted. Inherits D-011 honestly: it bounds cumulative spend, never a single anomalous call, and it is per-process — which in Lambda is per-container, not account-wide `[stable]`
- `llm/base.py` · `openrouter.py` · `offline.py` · `cache.py` · `bedrock.py` — provider abstraction, cost and latency capture, content-addressed response cache with record/replay. `LazyOpenRouterProvider` builds its client on first use so replay needs no key `[stable]`
- `aws/__init__.py` — AWS entrypoints. Inside the package **so the separation guard covers the deployed decision path**: adding it took the guard 72 → 75 tests with no edit to the test. Handlers (`ingest`, `investigate`, `api`) and DynamoDB `stores.py` land here `[skeleton]`
- `llm/bedrock.py` — **the Bedrock provider.** Converse translation both ways, default Haiku 4.5 (D-025), `normalize_model_id()` adds the `us.` inference-profile prefix Anthropic ids require and leaves Nova/Llama bare. Cost is **computed from a dated price table, never charged** (G1); an unpriced id returns 0.0 rather than a guess. Client built on first use, so replay and the tests need no credentials `[stable]`
- `aws/metrics.py` — **observability by printing (W11).** CloudWatch EMF: one JSON line that is both a metric and a structured log, so an alarm and an Insights query can never disagree about what happened — and a handler that cannot reach CloudWatch still leaves a complete record. No `PutMetricData` call, which the execution role does not have anyway. `customer_id` is a property, never a dimension: unbounded cardinality is one CloudWatch metric per customer `[stable]`
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
- `test_bedrock.py` — 75 tests against a stubbed `converse()`. Passes whether or not boto3 is installed, and that is itself under test `[stable]`
- `test_stores.py` — 39 tests against a hand-rolled fake table. Duplicate-delivery no-op, Decimal round-trip, the absent delete surface, and score delegation `[stable]`
- `test_ingest.py` — 18 tests over the real path (fake DynamoDB, fake SQS, no model): a sub-threshold signal is retained and still counts later, two conversations cross where neither alone would, the online score equals `memory.py`'s bit for bit, redelivery changes nothing, one poison record fails alone `[stable]`
- `test_verdict_accuracy.py` — 11 tests on what "correct" means. The first draft scored against `false_positive`, a verdict `schemas.py` does not permit, so every correct dismissal would have been counted an error — silently. The permitted set is now read off the schema `[stable]`
- `test_routing_accuracy.py` — 24 tests on AT-58's scorer: a trajectory-None customer (no correct team exists) is always `unscored` and never enters the accuracy denominator whatever it was routed to; the prior-case generator and the scorer are pinned to read the same `TRAJECTORY_TEAM` map; a config-hash mismatch against the rebuilt corpus aborts loudly `[stable]`
- `test_reader_coverage.py` — 28 tests on the sampling and the denominators, with a stub reader and no network. Who is sampled is a function of the customer id and the trajectory and nothing else — every answer-key field is perturbed and the draw must not move, because reversing the corpus order does not catch a draw ranked on `latent_risk` and that attack passed until it did. The denominator stays the planted count whatever the reader does, and evidence in more distinct conversations must score strictly higher — the property the whole payoff rests on `[stable]`
- `test_alarms.py` — 8 tests on the alarm set as data: no alarm watches a metric no handler emits, nothing alarms on missing data, and the set stays small enough that someone reads it `[stable]`
- `test_budget.py` — 15 tests on the spend ceiling: it refuses before the call, it states rather than hides that one anomalous call still lands, `0` disables it deliberately, an unparseable cap is refused rather than ignored, and the ceiling sits outside the cache so replay can never be exhausted `[stable]`
- `test_metrics.py` — 14 tests on EMF and the handlers that emit it. Checks the shape CloudWatch silently drops (a declared metric whose value is a string), and two cost properties that are easy to regress: no unbounded dimension, and exactly one dimension set `[stable]`
- `test_ui.py` — 10 tests: the fixture's rows are the API's own rows, the queue ranks on the score today, cases pass through untouched, no answer-key field reaches a browser, a citation without a transcript fails the build, every screen renders (via `ui/smoke.mjs`), and every colour pair on screen clears WCAG AA in both themes (via `ui/contrast.mjs`); both skipped with no node `[stable]`
- `test_api.py` — 34 tests over the real routing and the real stores: no answer-key field reaches a response body, no route contacts anyone, a review annotates without mutating evidence, a truncated queue says so, and a 500 carries no stack trace `[stable]`
- `test_transcripts.py` — 12 tests against a fake S3: lossless round trip (a lost turn index breaks every citation), a redelivery refused by the precondition rather than silently applied, and a customer with more than one page of history read in full rather than truncated at page one `[stable]`
- `test_investigate_handler.py` — 17 tests on the crossing→case path with the offline rule engine: the score of record is recomputed and drift is reported, a missing archive fails loudly, re-investigation overwrites one case, and a customer who no longer crosses produces none `[stable]`
- `test_case_record.py` — 7 tests on the persisted case: disk and DynamoDB carry the same fields (drift here surfaces on stage, not in CI), every quote keeps its then-vs-now score, the queue ranks on today, and no answer-key field reaches a client-facing record `[stable]`
- `test_corpus.py` — **construction guard**: 8 tests on what the generator actually plants, upstream of both guards above. No fragment may appear in two conversations of one arc (a fallback that re-planted a used fragment fabricated cross-conversation corroboration for 28 / 213 arc customers per 400 until 2026-08-28), an over-long arc really is padded with empty conversations rather than repeated ones, and the fragment-pool ceiling is enforced on a **programmatic** `RunConfig` rather than only when the CLI flag is typed `[stable]`
- `test_no_answer_key_leak.py` — **data guard**: nothing may receive a value that *encodes* a ground-truth field. The one that would have caught the leak we actually had. Discovers `AccountSnapshot`'s numeric fields rather than listing them — a hand-written list once named a field that did not exist and silently skipped `[stable]`
- `test_read_live.py` — 18 tests on the turn-by-turn read. The two that matter: a `RecordingExtractor` pins that prefixes genuinely grow, never repeat and never reorder (a model shown the whole transcript at every step would make the animation a lie), and the final step's messages are asserted equal to the batch read's, which is what makes narration and the ledger the same belief `[stable]`
- `test_stream.py` — 19 tests on the arrival stream as **properties, not pinned outputs**: frames agree with `memory.py`, the order is genuinely interleaved across customers (grouped-by-customer would still animate and would still be a batch), `score_before` is taken on the same day so a delta cannot fold in decay, `ledger_size` is monotonic (never-discard, asserted mechanically), a customer opens at most one case, and the payload guard fires on a nested answer-key field `[stable]`
- `test_tenants.py` — 13 tests on the configuration layer, exercising the mechanism rather than counting entries now that one profile ships. It **builds a second deployment in-test** and proves a five-day half-life scores a 90-day-old signal differently from a ninety-day one, so the layer varies what it claims to; asserts most seams are the client's own systems (every stage being ours is a platform, not an integration); and pins that the speech-to-text seam is marked **theirs**, which is the single most tempting thing to fudge on a stage `[stable]`
- `test_stream_server.py` — 9 tests on the demo server's three safety properties: `do_GET` is the only handler (the routes are unauthenticated on purpose, which is safe only while they are all reads), no outbound contact surface, loopback binding read off the AST, and four path-traversal forms driven through the real `_static` rather than inferred from the source `[stable]`
- `test_stream_fixture.py` — 11 tests on the last hop to the browser: blocks pass through untouched, costs are never summed across deployments, the answer-key guard is shown firing, and the **committed** `ui/stream.js` is parsed to check it covers every tenant `tenants.py` defines — a tenant added without a re-record is a pill on screen leading to an empty player `[stable]`
- `test_memory.py` — ledger invariants: never-discard, accumulation, retro re-score, decay, determinism `[stable]`
- `test_tools.py` — every agent tool, in-memory, no network `[stable]`
- `test_agent.py` — decision schema, bounded loop, the cost cap holding under a rising cost curve (and the documented spike case where it cannot), a crashing tool being contained `[stable]`
- `test_sweep.py` — the multi-seed harness: sign test vs hand computation, pairing on seed, denominators present and identical across arms, equal alert budget, determinism, counted-not-reconstructed integers, artifact reproducibility `[stable]`
- `test_cli.py` — the commands, and the demo's internal consistency: its narration may not contradict the claim it selected on, and its denominator must count customers. Also that the `investigate` artifact is **sufficient on its own** — the reviewer UI must never regenerate the corpus from `manifest.seed` to fill in missing fields `[stable]`
- `test_extract_model.py` — the model reader against a stub provider: statelessness (no customer id in the prompt), verbatim quotes or nothing, the offline path's grain and floor, record-then-replay, and that the default reader stays keyless `[stable]`

## ui/ — two halves, no build step

Open `ui/index.html`. No npm, no bundler, no dev server, no network — static files plus two
generated, committed data files, so a judging room with no wifi still sees the product (D-004), and
`aws s3 sync` deploys it today while CodeBuild is blocked (W9). Details in `ui/README.md`.

**In use:** `#/desk` (the reviewer's console) and `#/desk/call` (the same console during a call).
**How it works:** `#/stream` (the whole book arriving) and `#/deployment` (the nine seams). The
console is dense chrome that never animates; the stream deliberately moves, because the motion is
the argument. `case_record()` builds a streamed case and a recorded one identically, so the
document screens serve both sources through one set of renderers.

- `index.html` — the page and the script order, which is load-bearing: `util.js` first, the two data files, `live.js`, `console.js`, then `app.js` last because it renders on evaluation `[stable]`
- `util.js` — escaping and number formatting, shared. There is **one `esc()` in this UI**; the day two copies diverge is the day one screen escapes a quote and the other does not `[stable]`
- `app.js` — the router and the document screens (queue, case, retro, transcript). Computes nothing; escapes all customer speech `[stable]`
- `console.js` — **the product surface**: our panel inside a stand-in of the client's case-management desktop. Shaped by what third-party UI actually is in these consoles — a sandboxed iframe scoped to a case id in four of five vendors — so it renders as **a bounded rectangle with a visible seam and its own provenance footer**, which is the integration argument made visible. Primary user is the specialist reviewer, not the agent on the call: accumulation across conversations is what the product is for and a live-call panel structurally cannot show it, and EU AI Act Art. 14(4)(b) names automation bias for exactly the mid-call-nudge shape. The live-call view ships anyway, labelled *nobody decides here*. Decision buttons are honest about being inert — they print the `POST /cases/{id}/reviews` body that would be sent and say it was not `[stable]`
- `live.js` — the explanatory screens: the arrival player and the deployment map. **Steps an index through pre-computed frames and paints.** Board rows move by `transform` rather than re-render, because re-ranking is the beat and an innerHTML swap makes it invisible. Also holds live mode: served from `--serve` it attaches an EventSource to localhost `[stable]`
- `styles.css` · `demo.css` · `console.css` — **the design system** and the document screens · the stream (the one screen that animates) · the console. The other two files define no colour, size or spacing of their own. Neutrals are a **generated 16-step OKLCH ramp** at one hue, indexed by both themes, so the steps are perceptually even rather than picked; semantic colours share one lightness per theme so no state shouts. Elevation is layered surface plus a lit top edge in dark, not a border on every box. One type scale, one 4px radius, one 4px spacing rhythm across all three; `prefers-reduced-motion` honoured wherever something moves. **`--accent` is the tenant's hex and never carries text** (`--accent-ink` does, and `--accent-edge` is the tenant colour corrected until it clears its ground). **No vendor logo, wordmark, brand hex or icon set anywhere**: Salesforce Sans is licensed only for use inside Salesforce, SLDS icons are CC BY-ND so recolouring one is plausibly a derivative, Amazon Ember is proprietary `[stable]`
- `data.js` — **generated and committed** by `tools/ui_fixture.py` so a fresh clone works with no Python run. A `<script src>` rather than a JSON fetch, which is what makes `file://` work `[generated]`
- `stream.js` — **generated and committed** by `tools/stream_fixture.py`: 133 frames, every transcript behind them, 6 worked cases, 6 turn-by-turn read series, and 9 customer-360 headers `[generated]`
- `smoke.mjs` — renders all 21 routes against a stub DOM, checks both fixtures for answer-key fields, and asserts `manifest.asr` is `"none"`, that narration is non-empty and in transcript order, that the final read saw the whole transcript, that at least one belief moves, and that every case has a synthetic-stamped account header. Run by `uv run pytest` when node is on PATH `[stable]`
- `contrast.mjs` — **the colour gate**: renders every screen against the same stub DOM, parses the three stylesheets, cascades one over the other, and computes a WCAG ratio for every foreground/background pair the markup actually produces — both themes, tenant accent override in place. Fails below 4.5:1 for text and 3:1 for a boundary or a graphical mark, and fails if a sub-threshold ledger cell is inked anything but the panel's primary ink (D-030: retained evidence is never dimmed). Discovers its own surface and asserts the discovery — no pair list, nine sentinel classes that must still render. Run by `uv run pytest` when node is on PATH `[stable]`

## benchmarks/cfpb/ — AT-43, the extractor on real complaint narratives

Self-contained and replicable end to end: pre-registration, marking guide, one script per step, every
API call and output hash logged. Run `steps/05_score.py` alone to reproduce the numbers offline.

- `README.md` — how to replicate, in order; what is in the folder; data provenance and licence `[stable]`
- `PROTOCOL.md` — **the pre-registration**, frozen before any narrative was read: frame, panels, wrapping rule, interpretation thresholds, freeze rules, and an amendment log. Carries a dated 2026-08-31 note at the top only, flagging that the synthetic recall it compares against (0.681) is from a corpus rebuilt twice since; §1–§7 are untouched `[stable]`
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
- `verdict_accuracy.py` — **AT-57**: does the investigator tell a real crossing from a false alarm? Samples crossings evenly from both arms, because the top of the queue is nearly all true positives and a run drawn from it cannot be wrong in the direction that matters. Reads the answer key, which is what the evaluation side is allowed to do (D-009); the agent still sees only `cli._context` `[stable]`
- `routing_accuracy.py` — **AT-58**: when the investigator routes a case to an owning team, is it the right one? Scores an existing `verdict_accuracy.py` artifact with **zero model calls** — rebuilds the corpus from `manifest.seed`/`population.customers` and asserts the rebuilt `RunConfig.hash()` against `manifest.config_hash` before scoring anything. Trajectory-present and trajectory-None customers never share a denominator (the latter has no correct team to be right about); reports the full truth-team x routed-team confusion matrix and splits each miss by whether it matches the ledger's own dominant signal at the crossing or neither `[stable]`
- `retro_direction.py` — **can a past conversation be worth MORE?** Compares each ledger entry's marginal contribution on the day it landed against its contribution today, under the full ledger and under an unweighted count. Offline, free, no key. This is the structural argument for the four mechanisms in `memory.py` that the recall sweep cannot make: 239 / 485 entries rise under the full ledger, **0 / 485** under a plain count, because a concave score with no multipliers can only shrink an earlier entry `[stable]`
- `reader_coverage.py` — **does the model reader find what the lexicon misses, and does it change who crosses?** Samples evenly across the four trajectories (first N by `customer_id`, never off the ledger queue — that would select the customers the offline reader already read well, which is the quantity under test), runs both readers over the identical conversations, then feeds each reader's signals through the **same** `SignalLedger` at the same threshold. Denominators are planted counts; unplanted fires get their own column and can never raise a ratio. Threshold is `cli._queue`'s budget-derived top-K, which is offline-derived, so model-arm crossings are labelled an **upper bound**. Defaults to the free arm and gates the keyed one behind a printed projection and `--yes` `[stable]`
- `alarms.py` — six CloudWatch alarms over the EMF metrics, **created with no actions**: there is no SNS here, so they go red in a console and page nobody, and the script prints that rather than implying coverage `[stable]`
- `stream_fixture.py` — turns `earshot stream` artifacts into `ui/stream.js`, one block per tenant. Reformats, never computes. Refuses an answer-key field, a duplicate tenant, a citation with no transcript, or an artifact that predates the current frame shape. **Costs are never summed across deployments** — each tenant is a separate customer of this system `[stable]`
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
- `ORIENTATION.md` — **the zero-context door.** What the project is, the eight-term vocabulary every other document assumes (arc, stratum, diffuse, crossing, plant, decoy…), the results including the chance floor, and where to read next. Written so a newcomer, a judge or a returning teammate needs nothing else first. Explainer only — the README stays the source of record `[stable]`
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
- `corpus/01-diagnosis.md` — a blind read of the generated transcripts, written BEFORE seeing any prior report, so its agreement with one is evidence rather than echo. Counts and quoted examples `[stable]`
- `corpus/02-reconciliation.md` — where the blind diagnosis agreed, differed, and **corrected** the earlier one; includes the decoy re-plant measurement and a rejected implementation that would have moved 11,096 customer turns `[stable]`
- `corpus/03-public-sources.md` — real, licence-checked public conversation data (CFPB, Financial Ombudsman, Taskmaster-1, regulator reviews) and exactly how each may be used under the synthetic-only competition rule `[stable]`
- `corpus/04-plan.md` — **the forward plan.** Phase A free / Phase B contained / Phase C the real thing, each costed by what it forces to be republished. Phase C is 23–32 h `[stable]`
- `corpus/05-phase-a-record.md` — what Phase A actually changed, its measured before/after, and the two flaws the author introduced and then caught by measuring `[stable]`
- `corpus/06-phase-c-record.md` — **what Phase C changed**, every defect count before and after, the two bugs it introduced and caught, and the pre-registered diffuse headline collapsing from 29–0–1 to 15–13–2 with the mechanism measured. Twenty arcs read end to end in §8 `[stable]`
- `corpus/07-framing-decision.md` — **what the entry claims after Phase C**, and why. The dead pre-registered headline and its re-registration (D-031), the AT-52 answer on whether decay/corroboration/cross-channel/escalation survive, the demo beat order, and a kill list of the sentences the rebuild made unsupportable `[stable]`
- `impact/onepager-use-case.md` — **required deliverable ① of three** (kickoff-notes.md:43): client-ready use case and impact. The accumulation moment as the real `CUST-2688` trace `earshot demo` prints — not a written-for-the-page table — who reads the feed, and the known limits stated rather than buried `[stable]`
- `impact/onepager-accuracy-cost-latency.md` — **required deliverable ②**: the internal evidence page. Every figure with its denominator and the command that reproduces it keylessly; a "what is not measured" section that names the four open gaps `[stable]`
- `impact/onepager-path-to-production.md` — **required deliverable ③**: what is deployed, the single IAM policy blocking it, how it integrates into a bank console, run cost from measured figures, and the honest risk `[stable]`

## artifacts/

- `runs/pinned/` — one committed run + manifest `[generated]`
- `runs/sweep-30x1500-9ddd6674c388.json` · `sweep-10x1500-9ddd6674c388.json` — the two committed `earshot sweep` artifacts the README publishes from (30 seeds = the quotable numbers, 10 seeds = the "quote nothing at 10 seeds" companion). Committed so a judge sees the exact run behind every figure without spending the ~70s to regenerate it `[generated]`
- `cache/investigator-demo.jsonl` — committed model responses so the streamed demo replays with no keys `[generated]`
- `cache/investigator-bedrock.jsonl` — AT-57/AT-58's cache: 50 verdict-loop investigations keyed Haiku 4.5 on Bedrock, replayed by `tools/verdict_accuracy.py` and scored free by `tools/routing_accuracy.py` `[generated]`
- `cache/extractor.jsonl` — the model reader's cache behind the CFPB benchmark (0.8214 strict recall) and the streamed-demo reads: one file per model by `extractor_cache_path()`, this is the default (Haiku 4.5) path `[generated]`
- `cache/extractor-coverage.jsonl` — `tools/reader_coverage.py`'s cache: both readers over the same 288 sampled conversations, behind the "model reader revives retention, loses collections" measurement `[generated]`
- `cache/extractor-widened-arcs.jsonl` — the 2026-08-30 widened-corpus keyed run's cache. 5,494 unique reads banked from a run that spent $12.33 and produced no sweep artifact (hit the spend ceiling; the resume re-bought 3,275 reads because TWO processes raced one cache path -- not `prompt_sha` drift, which the duplicates themselves disprove). 39 lines torn and unreplayable `[generated]`
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
