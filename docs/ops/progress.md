# Build progress

**The build log.** One line per unit of work, newest section first. Append here; do not rewrite
history. `state-of-play.md` says where we are *now*; this says what has actually been done.

Status: `TODO` · `WIP` · `DONE` · `BLOCKED (who owns it)` · `DROPPED (why)`

---

## Deployment approach — settled 2026-08-25

**CDK is not usable. We deploy with boto3 scripts.** This is forced, not preferred.

`cdk bootstrap` needs three permissions we do not have, all tested:

| Needs | Result | Why it matters |
|---|---|---|
| `s3:CreateBucket` | DENIED | Our S3 grant is scoped to `agentic-trio` only; CDK wants its own assets bucket |
| `iam:CreateRole` | DENIED | CDK creates 4-5 deploy roles |
| `ecr:CreateRepository` | DENIED | ECR PowerUser gives push/pull to existing repos, not creation |

**What works instead, all verified by creating and deleting the real resource:**

- **Lambda deploy** by passing the existing role `arn:aws:iam::859430413223:role/zenon-poc-lambda-execution`.
  Created and deleted a function with it. This is the unlock — no new role needed.
- **DynamoDB** create + delete.
- **SQS** create + delete.
- **S3** put + get + delete objects in `agentic-trio`.
- **Bedrock** Haiku 4.5, Nova Lite, Nova Micro, Llama 3 8B all invocable.

**Consequences to carry forward:**

- **Zip deploys, not container images.** No ECR repo we can create; the two that exist belong to
  someone else. `Dockerfile` stays for local runs and for when ECR opens up, but the deployed artifact
  is a zip. This drops §3.5's "promote the same image digest" claim — say so rather than implying it.
- **One shared Lambda role**, not one role per function. §A.1's per-function least privilege becomes
  target-state. Name it on stage.
- **`infrastructure.md` §3.5's CDK commitment is now wrong.** Do not edit it yet; supersede it in
  `decisions.md` when the provisioning script lands.

---

## Work packages

| # | What | Status | Notes |
|---|---|---|---|
| W3 | Bedrock provider (`llm/bedrock.py`) | **DONE** | Converse both ways, Haiku 4.5 default, computed-not-charged cost, lazy client. 33 stub tests |
| W1 | Persist case fields | **DONE** | `case_record.py` — one serializer for the disk artifact and the DynamoDB item. Unblocks W10 |
| W4 | Spend cap in our own code | **DONE** | `llm/budget.py`. `CappedProvider` wraps every paid provider, refuses before the call, outside the cache. 15 tests |
| W5 | First keyed reader run | **DONE** | 150 CFPB docs on Haiku 4.5. Strict recall 0.8214 (92 / 112) vs the lexicon's 0.0357, at 8x the false-positive rate. That run's rate was $1.66 per 1,000; **superseded — the published rate is $1.58**, measured 2026-08-31 over 282 conversations. The recall figures are external-gold-set and unaffected |
| W6 | Ledger + case DynamoDB stores | **DONE (code); tables not created** | `aws/stores.py` + `tools/provision.py`. Conditional writes, no delete path on the ledger, scoring delegated. 39 stub tests. Dry-run verified against the real account |
| W7 | Ingest path (SQS FIFO → handler) | **DONE** | `aws/ingest.py`. Partial batch failure, conditional append, scoring delegated. 18 tests, no AWS |
| W8 | Investigate path | **DONE (code)** | `aws/investigate.py` + `aws/transcripts.py`. Loop unchanged, score recomputed not trusted, account data labelled synthetic. 29 tests |
| W9 | CI/CD | BLOCKED (IT) | CodeBuild + CodePipeline denied. `buildspec.yml` is written and parked, ready to run |
| W10 | Reviewer UI, 3 screens | **DONE (read-only)** | `ui/`, no build step. All three beats render from a committed artifact with zero AWS. The write path waits on the API being reachable. Extended to five screens by W13; same renderers, new routes |
| W11 | Observability (EMF) | **DONE (emit side)** | `aws/metrics.py`, wired into all three handlers. Alarms/dashboard still to create; no SNS, so they target EventBridge → Lambda |
| W12 | Sweep runner | DROPPED for now | Fargate needs VPC subnets; keep the sweep local |
| W13 | Live-stream demo + turn-by-turn read | **DONE** | `stream.py` + `read_live.py` + `tenants.py` + `ui/live.js`. One deployment framed as an integration; 133 conversations read by Haiku 4.5 on Bedrock, 6 read turn-by-turn, 6 crossings worked, $0.469. `--serve --narrate-live` does the turn-by-turn live. 73 tests |
| W14 | UI as the client's console | **DONE** | `ui/console.js` + `console.css`. Our panel inside a stand-in desktop; reviewer-first, live-call view labelled illustrative. Research brief drove it; the design agent was cancelled and its worktree is unmerged. Customer-360 header via `cli.stream_inputs`, `financial_state` only |

## Blocked, and who owns it

| Item | Owner | Ask |
|---|---|---|
| **SQS/DynamoDB/Bedrock on `zenon-poc-lambda-execution`** | **IT (Vikash)** | **NEW 2026-08-28, and now the blocker.** One inline policy on that role. Without it the three deployed Lambdas are inert and neither queue can be wired. Exact actions in `aws-infrastructure.md` |
| CodeBuild + CodePipeline | **IT (Vikash)** | Scope to `earshot-*`, or he creates the project + pipeline |
| Bedrock invocation logging | IT (Vikash) | In progress, not blocking |
| S3 Object Lock | IT, Support case | Off, unchangeable now. Evidence write-once degrades to IAM. Accept and state it |

**Do NOT ask for these — we do not need them:**

| Not asking for | Why not |
|---|---|
| `iam:CreateRole` | **We never needed it.** Lambdas deploy by *passing* the existing role `zenon-poc-lambda-execution`; verified by creating and deleting a real function. Asking for role creation is a broad grant to avoid a script we can write in a day. |
| `s3:CreateBucket` | `s3://agentic-trio` is the team's provisioned bucket and object read/write works. Prefixes (`dev/`, `demo/`, `evidence/`, `artifacts/`) do the rest. |
| `ecr:CreateRepository` | Zip deploys instead of container images (D-024). Costs us the "same digest promoted" claim, which we retire honestly. |
| Claude Sonnet 4.5 / the Anthropic form | **No longer blocking** (D-025). Haiku 4.5 does both jobs and is already invocable. Worth filing eventually; nothing waits on it. |

## Log

**2026-09-03** · **The deployed pipeline runs end to end, and four defects were found by running it.**
Commits `b9df104` → `3f40bab`, plus Arm B. ~$2.45 of $12 (Arm B was $0.027705; everything else free).

**The pipeline is connected and verified against the local answer.** Both event source mappings are
Enabled with `ReportBatchItemFailures`. `tools/feed.py` pushed the whole Northwind book through:
**130 messages in 44 FIFO groups → 34 ledger entries → 1 case → `GET /cases` 200**, matching the
local prediction exactly, deployed score `0.6526618648909545` against local `0.652662`. The case
carries three pieces of evidence and `CUST-0006-C0` is the entry's claim in a deployed record:
scored **0.1306 at write** on day 21, a fifth of the cut, never discarded, and 73 days later
load-bearing with `retro_delta 0.5220`. Fed twice: 260 messages, still 34 entries and 1 case.

**Four defects, each found only by running the thing.**

1. **Both mappings failed to create.** Not IAM — `provision.py` set no `VisibilityTimeout`, so both
   queues sat at the SQS default 30s while the functions were 60s and 300s, and AWS refuses a mapping
   below the function timeout. The constraint spanned two files with nothing connecting them. Now
   derived as 6× `deploy.FUNCTIONS[...]["timeout"]`.
2. **`_ensure_queue` was create-only**, so the fix above would have been *silently inert* on an
   account where the queues already existed. It reconciles now, and proved the repair path on live
   AWS: `RedrivePolicy (unset) -> {...}`.
3. **EMF had never produced a single metric.** `_aws.Timestamp` is required and was omitted on the
   theory that CloudWatch would fall back to the log event's time. It does not — it stores the line
   and drops the metrics. 130 well-formed records, `list_metrics` empty. Worse than a gap: with
   `TreatMissingData=notBreaching`, the four alarms on the `Earshot` namespace read **OK** while
   guarding nothing. 12 metrics now flow; `DuplicateDeliveries 34` with `SignalsWritten 0` is the
   second feed's own proof that at-least-once cannot double-count.
4. **The transcripts queue had no DLQ**, while `aws/ingest.py` documented that a bad transcript
   "eventually reaches the DLQ". On FIFO that is a stalled customer, not a lost message: the group is
   the customer id, so a poison transcript blocks their whole stream for the 4-day retention while
   re-invoking ingest, and under `EARSHOT_EXTRACTOR=bedrock` each retry is a paid call `budget.py`
   cannot stop. `earshot-dev-transcripts-dlq.fifo` now exists, redriving at 3.

**Arm B closes the last "not measured" item, and it is a frontier rather than a winner.** Nova Lite on
the same 282 conversations: coverage **181 / 282 against Haiku's 177 / 282** at **$0.0982 per 1,000
against $1.58** and p50 873 ms against 1,333 ms — and only **60 / 80 customers crossing against
65 / 80**. It fixes the `financial_distress` desk where Haiku loses to the lexicon (0.375 → 0.583 vs
0.458), so that published loss is Haiku's, not the model reader's. It is also measurably worse at
citing: **10 quotes rejected as not verbatim, 9 relocated, 1 too short, against Haiku's 0/0/0** on
identical text, with 0 unparsable on both — the cheaper model paraphrases evidence it was told to
quote, and the verbatim guard caught all 20. D-025 stands on evidence now instead of convenience.

**Tests 850 → 899** (5 skipped): `test_provision.py` (19), `test_feed.py` (21), 4 in
`test_metrics.py`. Every one pins a property that was actually violated in production, not a label.

**2026-08-31 (late)** · **All four keyed figures re-measured on the shipping corpus and published
across every document** (`9da4169`, then the docs commits on `wp/final-numbers`). ~$2.42 of $12.

**Reader coverage is the result the entry rests on, and it is now measured on both arms.** Same 282
planted arc conversations, same `SignalLedger`, same threshold, same scoring config; one variable, who
reads. Crossings: **complaints 0 / 20 → 20 / 20, vulnerability 0 / 20 → 19 / 20**, retention
1 / 20 → 16 / 20, collections 9 / 20 → 10 / 20. Coverage 59 / 282 → 177 / 282. Reader **$1.58 per
1,000**, p50 1,333 ms, p95 2,162 ms, 272 signals, **0 unparsable, 0 relocated quotes**. Stated with it
because the tool states it: the model arm is an **UPPER BOUND** — the threshold is a top-K cut over the
OFFLINE reader's ranking, held fixed across arms, and the model's own cut costs $13.96, not spent.
Published against us on the same run: distress coverage **0.38 vs the lexicon's 0.46**, and 3 churn /
6 distress customers crossing on the wrong signal family.

**AT-57 22 / 50 → 29 / 50, dismissals 4 / 25 → 13 / 25, and it is not our agent improving.** Not one
line of it changed. The Phase C corpus stopped leaking the answer through surface form: decoys
paraphrase instead of repeating verbatim, quotes are no longer ASR-mangled, arcs cohere. So "the agent
escalates rather than filters" — the honest read at 4 / 25 — is **retracted**, with the reason attached
everywhere it was published. New finding worth as much as the number: **confidence is not diagnostic**,
0.837 mean on the 21 wrong verdicts against 0.852 on the 29 right ones.

**AT-58 36 / 49 → 27 / 48 (2 wrong, 19 declined). Worse, published as worse.** The confusion matrix is
the explanation: the `complaints` row is **entirely empty**, because no complaint customer ever crossed
under the offline reader, so no complaint case existed to route. 43 of the 48 scorable cases are one
desk and all 19 declines sit in it. The same coverage failure as above, arriving through a second door
— it will not improve by leaving the reader alone.

**Streamed demo re-recorded:** 130 conversations, 103 signals, 9 crossings, 6 worked, **$0.4792**,
$1.5256 / 1,000, p50 1,230 / p95 1,786. Its turn-by-turn movement counts were recomputed from
`ui/stream.js` rather than carried over, which caught a claim that had gone stale: the old recording's
**3 withdrawals** were the README's evidence that every movement type occurs in real output, and the
re-record has **0**. Withdrawn with its reason; 6 conversations cannot support the converse either.

**Nine documents updated; no superseded figure survives outside a labelled retraction** (README,
ORIENTATION, three one-pagers, architecture, build-plan, infrastructure, state-of-play, handover,
INDEX). Two corrections found while doing it, both pre-existing: state-of-play still called
`ui/data.js` an offline rule engine when `4ec34cd` had keyed its verdicts hours earlier (what is
actually offline is the READER under them, because `--extractor` does not reach `earshot investigate`);
and `infrastructure.md`'s $/mo tables are left at the old $0.0301 mean investigation cost with the
1.7% bias named above them, rather than hand-retyping every arithmetic string.

**2026-08-29 (late)** · **Every keyed measurement re-taken on the shipping corpus, and a design
system** (`1a91e46`, `7359427`, `a459ee0`, `bcbcd8b`, `33c213c`, `74536fc`).

**AT-57 22 / 50 and AT-58 36 / 49**, both on the post-fix corpus, both replaying — verified before
publishing, which is the whole point of the README paragraph deleted a day earlier. The agent
escalates: 18/25 caught, 4/25 dismissed. Routing is harder post-fix (41→36) and its two wrong routes
are unmoored from the evidence rather than near-misses. *(Both figures superseded 2026-08-31 by
29 / 50 and 27 / 48 on the Phase C corpus — see the entry at the top of this log. Nothing here is
current; it is the record of what was true on this date.)*

**A dead route, found and then explained.** The offline lexicon finds churn evidence in 0.43 of the
conversations where it was planted, against 0.67–0.86 elsewhere; corroboration is cross-conversation,
so **0 of 325 churn customers ever crossed** and the brief's lead team received nothing. `tools/
reader_coverage.py` measured both readers over the same 288 conversations ($0.4260): the model reader
takes churn coverage to **0.79** and **9 of 20** churn customers reach Retention — **and drops
Collections coverage to 0.42, crossings 4 → 1**. Choosing a reader is an operational decision about
which desk you under-serve. Published at equal size.

**The cost cap is finally derived from measurement** ($0.25 → $0.10), which D-025 asked for and never
got. Two existing guards fired on the change: the deployed Lambda's deliberate copy of the constant,
and a CloudWatch alarm sitting at a literal $0.20 while its own comment claimed it was `cap * 0.8` —
at the new cap that is an alarm at twice the ceiling, which could only fire after the cap had already
stopped the run.

**A hazard closed before it fired.** `extractor_cache_path()` returned one file for every model, so
arm B would have appended Nova Lite completions into the committed cache behind 0.8214 recall and
$1.6563 per 1,000. No collision, no error, just two models in one file. Now per-model, with the
default keeping its historical filename so a judge's keyless replay still works.

**The UI got a design system, not a repaint.** Generated neutral ramp (one hue, one chroma, even
OKLCH lightness steps) indexed by both themes; semantic colours at one lightness per theme; elevation
by surface rather than by border. It found a live bug: the tenant accent was rendering as body text
at **3.71:1**, so `--accent` (any client hex, no words), `--accent-ink` (ours) and `--accent-edge`
(corrected mark) are now three tokens. `ui/contrast.mjs` gates **634** rendered pairs across both
themes, discovers its own surface, and enforces D-030 — dimming a retained ledger row by one step
fails the build even at 7.9:1.

**The streamed demo was re-recorded** with both arms keyed. The first attempt had the reader on Haiku
and the investigator on the offline rule engine; the artifact's own filename (`model-offline`) is the
only reason it was caught.

**2026-08-29 (small hours)** · **A four-agent red team, and the numbers it moved** (`d46bf02`,
`40e5f7f`, `a03c02b`, `08b20cc`, `660dca4`, `dd3c50e`, `4430f8b`, `0a7c2e4`). Four reviewers ran
against code correctness, architecture invariants, story-versus-evidence, and demo/UI/AWS honesty.
Every finding below was reproduced by executing something, not by reading.

**One defect was manufacturing the mechanism the entry is scored on.** `_nearest_fragment` re-used an
already-planted fragment once a trajectory's pool ran out, so the same sentence landed in two
conversations and the ledger paid a cross-conversation corroboration bonus for one utterance copied
twice — 120 / 822 arc customers at sweep size, at the shipped default. Fixed; **every published number
regenerated**. The pre-registered diffuse win survives at 30 seeds (26–2–2, `p=0.000`) and **stops
clearing 0.05 at 10** (was 8–0–2 `p=0.008`, now 7–2–1 `p=0.180`). The loss to `window3-top2` got
worse. The guard that should have caught it only ran when a CLI flag was passed; it lives in
`generate()` now.

**Eight guards were green while the thing they guard was broken.** The answer-key wiring guard was a
source-string match, defeated by `getattr(truth, "latent_" + "risk")` with 583 tests passing and the
answer key inside `ToolContext`. The separation guard missed `from .schema import *` and
`import earshot` + attribute walk. `_CORPUS_SIDE` was an uncapped second exemption set. `tools/` was
outside discovery entirely while two files there build the browser payload. Each fix ships with a test
proven to fail on the attacked code. Suite 559 → **774**, guarded surface 34 → **44 modules**.

**Two numbers stopped being directions.** AT-57 re-run keyed at n=50 balanced: **22 / 50** (caught
19/25, dismissed 3/25, one abstention, $1.50, p50 18.4s). AT-58 routing measured for the first time and
free, by scoring the artifact AT-57 already wrote: **41 / 49 correct, 0 wrong, 8 declined** — when it
commits to a team it is never wrong. Together: the investigator is a **router and an audit trail, not
a filter**. *(Both superseded twice since; current is 29 / 50 and 27 / 48, and the "router not a
filter" reading no longer rests on the agent escalating everything. Historical record only.)*

**`config_hash` does not cover the code, and it cost $1.50.** The corpus fix changed who crosses with
the hash identical on both sides. Manifests carry `pipeline_sha` now, a failed run refuses to write an
artifact, and cache mode is in the filename — a replay had already overwritten the keyed AT-57
artifact with 42 empty cases.

**Six document statements were false**, including a README paragraph inviting a judge to run a replay
command that had been failing for 19 days, and a sweep table that never named the reader producing its
numbers. `infrastructure.md` was repriced off Sonnet: monthly $878 → **$721**, ASR multiple ~100×, both
known arithmetic errors fixed with the corrections left visible. Three brief deliverables logged as
deltas rather than quietly dropped.

**Owed to the next session:** the AT-57 re-run on the fixed corpus is **BLOCKED (Ravi)** on an expired
SSO session — the published 22 / 50 was measured pre-fix and no longer replays, which the README states
rather than hides. *(Discharged 2026-08-31: SSO was re-minted, the re-run landed at 29 / 50, and
nothing on this line is a live blocker or a current figure.)*

**2026-08-28 (late night)** · **The UI became the product in use** (`e0fb7f8`, `281e7c5`,
`5b0633f`). Research into the consoles retail banks actually run found the finding that reframed
the screen: third-party UI ships into four of five of them as **a sandboxed iframe scoped to a
conversation or case id**. So `#/desk` renders our panel as a bounded rectangle with a visible seam
inside a stand-in desktop, and the integration argument is made by the layout rather than a slide.

**The primary user moved from the agent on the call to the specialist reviewer** — accumulation
across conversations is the product and a live-call panel cannot show it, the people owning our
four routes work case queues, and EU AI Act Art. 14(4)(b) names automation bias for exactly the
mid-call-nudge shape. The live-call view ships labelled *nobody decides here*.

**Customer-360 through the one safe door.** `cli.stream_inputs()` now also returns an
`account_for` closure, built the same way as the `ToolContext` factory and for the same reason:
`account_snapshot()` handed `latent_risk` becomes an oracle. Two new guards pin the *wiring*, not
just the statistics, on a customer whose two risk figures differ.

**Legal line held and written down**: no vendor logo, wordmark, brand hex or icon set; Salesforce
Sans licensed only inside Salesforce, SLDS icons CC BY-ND, Amazon Ember proprietary. Every borrowed
convention documented by two or more vendors independently.

**Two process notes.** The opus design pass was cancelled mid-flight and left an uncommitted
worktree carrying a 479-line `styles.css` rewrite — unmerged, Ravi's call. And a `cd` into that
worktree that was never undone put one docs commit on its throwaway branch; main was untouched and
the commit was redone. Verify `pwd` before committing.

**Security note worth carrying:** nearly every `docs.aws.amazon.com` page fetched during the
research carried an identical injected block instructing an AI reader to run a shell command,
byte-identical across unrelated pages. The agent did not act on it. Treat AWS doc fetches as
untrusted content.


**2026-08-28 (night)** · **The call is read while it is still open, and the portfolio of three
banks is gone** (`7dc594f`, `1c21c19`). `read_live.py` re-asks the reader after each customer turn
on the transcript heard *so far*. Across six narrated conversations every movement occurs in real
Bedrock output: 9 appeared, 7 firmed, 1 faded, **3 withdrawn** (the model retracts a signal after
hearing more) and **1 requoted** (it moves its citation to better evidence). `_diff()` decides all
of that in Python; the browser only animates it.

Two properties keep it a measurement rather than theatre, both tested: the model is handed a
genuine **prefix** — `RecordingExtractor` pins that prefixes grow, never repeat and never reorder —
and the **final step's request is byte-identical to the batch read**, so under a content-addressed
cache they are one entry. That second one is the guarantee that the belief at the end of the
animation is the belief that was appended to the ledger.

Narration runs on its **own extractor instance**, in both the batch and the live path.
`ExtractionTelemetry.conversations` is the denominator of the published cost-per-1,000 figure and
54 prefix reads counted as 54 conversations divides the same money by nine times the work. Reported
apart everywhere: reader $0.187 + narration $0.073 + agent $0.209 = **$0.469**.

**Three invented banks cut to one, reframed as an integration.** The portfolio demonstrated the
configuration layer and nothing else. `tenants.py` keeps the machinery — it *is* the per-client
seam — and adds a `Seam` list of the nine pipeline stages with who owns each. Six of nine are the
client's existing systems and the screen counts them rather than asserting it. `test_tenants.py`
now builds a second deployment in-test to prove the layer varies what it claims to, and pins that
the speech-to-text seam is marked **theirs** — the single most tempting thing to fudge on a stage.

`--serve --narrate-live` narrates inline, verified against real Bedrock with
`EARSHOT_CACHE_MODE=off`: `churn_intent` 0.60 surfacing at six turns heard, three genuinely new
calls while the HTTP request was open.

**Open:** `handover.md` is at 119 lines against its own ~60-line cap and needs a trim at the next
handover. Two agents in flight: a UI design pass and desktop-conventions research (W14).


**2026-08-28 (late)** · **The demo layer, and real Bedrock behind all of it** (`1275f95`).
`earshot stream` walks a book in **global day order across all customers** and emits one frame per
conversation — what the reader found, the score before and after, the re-ranked board, per-call cost
and latency. `tenants.py` turns that into three deployments: **a tenant is a configuration**, never
a fork — own corpus, own half-lives, own fixed threshold, own names for the four canonical
`OwningTeam` slots, with the team map display-only so the model's decision contract stays a closed
`Literal`. Two new UI screens (`#/portfolio`, `#/stream/<tenant>`) plus `--serve`, which runs the
same `run_stream()` over SSE on 127.0.0.1 so a stage demo makes real calls while a room watches.

**Measured, keyed:** Haiku 4.5 read all 460 conversations for **$0.653** (p50 ~1.1 s, **0 unparsable
replies, 0 dropped quotes**) and worked 12 of 33 crossings for **$0.412**. Cached per provider, so a
fresh clone replays every screen with no key. 539 tests (was 479), guard at 114, ruff clean.

**The ASR question, answered honestly rather than faked.** There is no speech recognition in this
system. What the stream reproduces is the *arrival pattern*, and at 1× each frame is held for the
reader's own measured latency on that conversation — so "real time" is a number from the run.
`manifest.asr` is `"none"`, every screen prints it, and `smoke.mjs` fails the build if it changes.

**Four things bought the hard way and now pinned:** a second threshold exists (fixed cut for the
stream, budget-derived for `investigate`) and they disagree on purpose; `stream.py` stays on the
separation-guarded surface only because `cli.stream_inputs()` hands it the corpus and the context
factory; a warm reader cache turns a "live" run into a replay, so the LIVE badge names the cache
mode; and a case id contains `#`, so every link now percent-encodes it.

**One doc claim corrected within the hour it was written.** `ui/README.md` said neither fixture
ships the seed. It does — in `manifest.seed`, as provenance, exactly as `data.js` always has. The
narrower true guarantee (no answer-key field present, no code path regenerates anything) is what
the docs now say.


**2026-08-28 (evening)** · **Redeployed** (zip sha `8323ff7cd3ca`) and **six CloudWatch alarms
created for real**. `cloudwatch:PutMetricAlarm` turned out to be granted, which the permission probe
had never tested. The deployed API emits EMF correctly — verified by invoking it and reading the log
tail — and still returns 500 on anything touching DynamoDB, which remains the one IAM gap.

Both handlers are deployed with the **offline** provider: keyless, no spend, and
`deploy.py --provider bedrock` flips it without a redeploy. Bedrock itself is proven from the laptop
(the keyed runs went through it); it is only the execution role that cannot reach it.

The alarms have **no actions**. There is no SNS here, so they go red in a console and page nobody,
and `tools/alarms.py` prints that as a PARKED row rather than implying coverage. Wiring EventBridge
to a notifier Lambda would be the first thing in this system that looks like an outbound surface —
an operator notifier is not a customer contact surface, but it is close enough that it should be
built deliberately rather than as a side effect of wanting alerts.

**2026-08-28 (W4, W11, and the reason no keyed run was possible)** · 457 tests (+41), guard 96 →
105, ruff clean.

**The finding: the model reader could not reach Bedrock at all.** `model_extractor()` was hardwired
to OpenRouter, whose key D-022 retired three days earlier. The Bedrock provider existed, was tested,
and nothing could select it — so "run the keyed benchmark" had been sitting on the list as an
unblocked task while being impossible. Three call sites (`cli.py:_provider`,
`extract_model.model_extractor`, the two handlers) had each decided provider selection separately
and drifted. `llm/select.py` is now the one place: `$EARSHOT_LLM`, default **bedrock**, explicit
`if`/`elif`, never a registry. Two reader tests were pinned to `openrouter` explicitly rather than
relying on it being the default.

**W4 — the spend ceiling.** `llm/budget.py`. `CappedProvider` wraps every paid provider inside
`build_provider`, so a new call site cannot forget to opt in. Four things worth carrying:

- It refuses **before** the call. Raising afterwards means the money is already spent and the cap
  is a report.
- It inherits **D-011 unchanged**: cumulative spend, never a single anomalous call. Nothing can
  know a call's price before making it, and a cap that pretends otherwise is worse.
- It sits **outside** the cache, so a replayed response costs nothing and does not count. Inverting
  the layers would make a keyless replay run exhaustible.
- It is **per-process** — in Lambda, per-container, not account-wide. What bounds the deployed
  fleet is reserved concurrency plus `maxReceiveCount: 3`. Said plainly rather than implying an
  account guarantee.

**W11 — EMF, not `PutMetricData`.** One JSON line per event that CloudWatch reads as metrics and a
human reads as a log, so the two can never disagree; no API call on the hot path, and no
`cloudwatch:PutMetricData` on the role (which does not have it). `stopped_because` is the one
non-Stage dimension, because its cardinality is bounded by the loop's exits and the distribution
across them is the earliest signal of the agent degrading. `customer_id` and `case_id` stay
properties — a dimension per customer is one CloudWatch metric per customer.

**2026-08-28 (W10)** · **The reviewer UI, three screens, no build step.** `ui/index.html` +
`styles.css` + `app.js` + a generated, committed `data.js`. 416 tests (+10), ruff clean.

**No npm, no bundler, no dev server, and that is the design.** CodeBuild is blocked (W9) so there is
nothing to build with, and D-004's lesson is that a judging room with no wifi must not be able to
break the demo. `aws s3 sync ui/ s3://agentic-trio/ui/` deploys it with permissions we already have.
`data.js` is a `<script src>` rather than a JSON fetch specifically so `file://` works — a fetch of a
sibling JSON is blocked by the browser and a script tag is not.

**One code path, offline or live.** `tools/ui_fixture.py` builds the queue rows with
`api._queue_row`, the same function the deployed `GET /cases` uses, and copies the cases out of the
artifact untouched. So the page renders identical objects whichever it is fed, and a test asserts
row-for-row equality rather than trusting that.

**`cmd_investigate` now also persists the transcripts behind its quotes**, in `transcripts
.to_payload`'s wire format at the artifact's top level — mirroring the deployed split where they
live in S3 rather than in the case item. That is what lets "read the quote in context" work offline
**without** regenerating the corpus from `manifest.seed`, which is the shortcut that would put
`stratum`, `outcome` and `latent_risk` one object away from a client-facing screen. They come from
the `ToolContext` the agent saw, which `test_separation.py` already guarantees is clean.

Answer-key discipline is checked three times on the way to the browser: the fixture refuses to write
one, `test_ui.py` asserts it, and `ui/smoke.mjs` greps the generated file. Three because this is the
last hop before a screen someone demonstrates to a bank.

`ui/smoke.mjs` renders all seven routes against a stub DOM in node — including the two that must
degrade to "not found" rather than throwing — and `uv run pytest` runs it when node is present,
skipping when it is not so a fresh clone with no toolchain stays green.

**Read-only for now.** `POST /cases/{id}/reviews` exists in `aws/api.py`; the page cannot call it
until the API is reachable from a browser (the Function URL is `AuthType=AWS_IAM`, which a static
page cannot sign, and the execution role is missing its permissions anyway).

**2026-08-28 (AWS is real)** · **Provisioned and deployed, on Ravi's go-ahead.** 3 DynamoDB tables
(PITR on, no TTL), 3 SQS queues with DLQ redrive, and all three Lambdas live on python3.13 from one
zip (sha `532a888f9bf4`), each passing `zenon-poc-lambda-execution`. Reviewer API on a Function URL
with `AuthType=AWS_IAM`. `tools/deploy.py` is the deploy path, same shape as `provision.py`.

**Two real bugs, both invisible to any stub test:**

1. **PITR silently did not enable.** `create_table` + the `table_exists` waiter returns while the
   continuous-backups subsystem is still catching up, and DynamoDB says
   `ContinuousBackupsUnavailableException` — which reads exactly like a permission problem. The first
   real run left all three tables with PITR **DISABLED** while reporting the tables created. Fixed
   with a bounded retry on that one error code; a second run converged 13/13.
2. **A Windows-built zip cannot run on Lambda.** `pydantic-core` is a compiled extension, so the
   naive `uv pip install --target` vendors a `.pyd`. The build now cross-compiles
   (`--python-platform x86_64-manylinux2014 --python-version 3.13 --only-binary :all:`).

**And one finding that changes the critical path: D-024 verified that the shared role can be
*passed*, not that it can *do* anything.** `zenon-poc-lambda-execution` has one attached policy,
`zenon-poc-s3-lambda`, and no inline policies — so no SQS, no DynamoDB, no Bedrock. Neither event
source mapping could be created (*"the function execution role does not have permissions to call
ReceiveMessage on SQS"*) and `GET /cases` on the deployed API returns 500 with `ClientError`.
`GET /health` returns 200, which proves the artifact and the code are fine. **The deployment is
correct and inert.** New IT ask, small and precise; exact actions in `aws-infrastructure.md`.

Incidentally proved in production: the API's "a 500 carries no stack trace" guarantee. The first
real error returned `{"error": "internal error"}` and put the detail in the log.

**2026-08-28 (end of session)** · **`aws/api.py` — the reviewer API.** Five reads (ranked queue,
one case, its reviews, a customer's standing ledger, the transcript behind a quote) and one write.
406 tests (+27), ruff clean. **All three Lambda handlers now exist**; the end-to-end path closes in
code, with nothing created in AWS.

Four choices the tests hold rather than the prose:

- **The write annotates and cannot mutate evidence.** infrastructure.md Q3 — reduce the score,
  suppress the customer, or only annotate — is answered "only annotate". A test reads the case
  before and after a dismissal and compares the evidence chain.
- **No endpoint contacts anyone, and a test asserts the absence.** HITL here is enforced by there
  being no outbound surface. If that test ever has to change, the entry's central safety claim has
  changed with it.
- **CORS is off unless `EARSHOT_ALLOWED_ORIGIN` is set.** A default of `*` publishes a reviewer's
  case queue to any page a browser loads, and a default nobody set is a default nobody reviews.
- **A 500 carries no stack trace.** A traceback in a response body names the tables.

The action set is closed (`approve`/`dismiss`/`route`) because `update_status` writes straight into
the GSI partition key — a free-text status would silently create a queue nothing lists. A dismissal
with no reason is refused: those are the rows anyone will actually want to read later.

**2026-08-28 (later still)** · **W8 done — `aws/investigate.py`, plus `aws/transcripts.py`.**
379 tests (+35), ruff clean. Three things surfaced that the work package did not name:

1. **W7 had a hole: the investigator had nothing to read.** The ledger stores signals, not
   conversations, and `unresolved_evidence()` rejects any decision whose citations do not resolve
   against a transcript. Deployed, the loop would have burned its whole retry budget rejecting its
   own decisions and landed a case saying "insufficient evidence" about a customer with plenty. So
   `transcripts.py` owns the wire format and an S3 archive, and ingest now archives **before** it
   extracts — a signal whose transcript is missing is unrecoverable, a transcript with no signal
   costs kilobytes.
2. **Write-once degrades and the code says so.** A.1 line 13 wants Object Lock in compliance mode;
   it must be enabled at bucket creation and `s3://agentic-trio` was not. The substitute is a
   conditional put (`IfNoneMatch="*"`), which stops overwrite and redelivery but not a deliberate
   `DeleteObject`. Say the smaller thing on stage. **The ledger's A6 guarantee is untouched** and
   must not be merged with this one.
3. **There is no bank core feed, so the account tools are fiction — and each case now says so.**
   `core/accounts.py` needs a `latent_risk`; locally that is the corpus's `financial_state`.
   Deployed it is a SHA-256 draw from the customer id (stable per customer, derived from nothing
   real) and every case carries `account_data: "synthetic"`. A single constant instead would make
   every customer's account identical, which is a worse thing to put on a screen. **This is the
   seam a real feed replaces.**

Also: the queue message's score is never trusted. A conversation can land between the crossing and
the investigation, so the score is recomputed from the ledger and the message's copy is used only
to report drift.

**2026-08-28 (later)** · **W7 done — `aws/ingest.py`.** SQS record → `Conversation` → `extract()` →
conditional append → reload → unchanged `SignalLedger` → threshold → enqueue. 344 tests (+18), ruff
clean. Three choices worth carrying:

- **`batchItemFailures`, not a raised exception.** A raise redelivers the whole batch and re-runs
  every extraction in it — with a model reader that is real money spent to punish one malformed
  neighbour.
- **The online threshold is a fixed cut (`EARSHOT_THRESHOLD`, default 0.60), not the local one.**
  `cli.py:_queue` derives its threshold from a review budget over a whole population; a streaming
  handler has no population snapshot. The two are different quantities and will disagree about
  whether a given customer crossed. Stated in the module docstring rather than smoothed over.
- **A crossing that stays crossed re-investigates on every later conversation.** Bounded by
  conversation volume, one investigation each time. It does not multiply cases — `make_case_id`
  keys on the first crossing day — but it is a cost the demo should not pretend away.

The tests assert the design claims on the deployed path, not just the plumbing: never-discard
(a sub-threshold signal is retained and still counts later), accumulation (0.270 and 0.146 alone,
0.459 together, cut at 0.35), and no second scorer (the handler's number equals an in-memory
`SignalLedger` over the same signals, bit for bit).

**2026-08-28** · **W1 done.** `src/earshot/case_record.py`: one `case_record()` builds both the
`earshot investigate` artifact and the DynamoDB `CASES` item, so the reviewer UI renders either and
neither can drift from the other. `cli.py` was writing `decision` and `trace` only. 323 tests
(315 → +7 unit, +1 end-to-end on the artifact), guard 81 → 84 by glob, ruff clean.

Two defects the ticket's own wording would have shipped:

1. **The evidence chain must come from the customer TODAY, not from `open_case()`.** A `Case` carries
   the evidence known at the crossing, so building the record from it freezes the retro chain on the
   opening day — the "we re-read March in light of July" beat would render empty for exactly the
   customers who kept accumulating, which are the ones the entry is about. Caught by a test asserting
   three evidence rows and getting one, not by review.
2. **A case has two scores and they are not interchangeable.** The crossing-day score and the score
   today differ under decay. One field for both either ranks a faded case at its opening-day seat
   forever, or loses the crossing. The record carries `score` (today, what the GSI ranks on) and
   `score_at_open`, named apart. `CaseStore.put_case` now ranks the queue on the current score,
   matching what `cli.py:_queue` already documented as the question it asks.

Verified against a real artifact rather than asserted: `CUST-0006#life_event#000123` renders four
evidence rows, day 39 supporting 0.100 when it arrived and 0.875 now (+0.775), all load-bearing.

**2026-08-25 (late)** · W3 and W6 built by two parallel subagents: `llm/bedrock.py`, `aws/stores.py`,
`tools/provision.py`, 72 new stub tests. Suite 236 → 312; separation guard 75 → 81 by glob discovery,
with no edit to the test. Provisioner dry-run verified against the live account: 3 tables, 3 queues
with DLQ redrive, 4 PARKED rows.

Three defects found by review rather than by the tests, all worth remembering:
(1) SQS reports an absent queue with a wire code that differs from botocore's exception class name, so
the most ordinary first-run case crashed; (2) PITR was probed on tables dry-run had not created,
printing FAILED TableNotFoundException three times — which reads exactly like a permission problem;
(3) the missing-boto3 test *assumed* boto3 was absent and flipped to failing once `uv sync --extra aws`
ran. All three lived where stubs are blind.

**Process failure:** the two agents shared one working tree. One ran `git stash -u` for a clean
baseline and swept the other's three untracked, half-written files back to HEAD. Both recovered, by
luck. Rule now in CLAUDE.md and working-agreements §8: any agent that writes files gets
`isolation: "worktree"`.

**2026-08-25** · Branch prepared for the AWS build. Repo reorg (D-023), build scaffolding,
`.claude/settings.json` approval tiers, duplication and dead-code pass, one-command AWS login.
IT fixed S3 object ARNs, CloudFormation, ECR, X-Ray, ECS: probe went 23/34 → 30/34.
`build/ear-on-every-call` pushed to CodeCommit. CDK ruled out; boto3 deploy path proven.

## 2026-08-30 · The widened corpus, and a keyed run that did not finish

**Spent: $12.32 on Bedrock Haiku 4.5. No sweep artifact was produced.** Recorded here rather than
quietly absorbed, because the failure is reusable knowledge and the reads are still on disk.

**What was being tested.** `build-plan.md` §5.1 and D-020 (2026-08-09) predicted that the shipped
corpus cannot pose the history-length question: customers average ~3.5 conversations, so
`stateless-top2` — keep the best two — discards almost nothing, and two of four fragment pools hold
4 fragments so a long arc exhausts its pool. The remedy was written down three weeks ago: widen the
pools, lengthen histories, re-run. This was that run.

**The corpus work landed.** Pools 8/8/4/4 → 14/14/14/14, 32 new fragments authored in a genuine
pass A (the author never opened `extract_lexicon.py`). The arc ceiling is gone: the shipped default
no longer breaches the scarcest pool, and `test_the_shipped_default_no_longer_breaches_the_ceiling`
now pins the *absence* of the warning that used to fire on every run.

**What it cost in measured recall, and why that is not a regression.** The offline lexicon finds
**1 of the 32 new fragments against 21 of the original 24** — 0.03 against 0.88. Published
extraction recall falls 0.55–0.78 → **0.2125–0.2525** (six seeds, 400 customers), and the band in
`test_published_extraction_recall_stays_in_its_measured_band` was moved deliberately with the
reasoning in the file. Recall falling is the safe direction: only a rise indicates a leak. The gap
is itself the sharpest measurement this repo has of *the lexicon only reads language it was written
beside* — sharper than the 0.0357 CFPB figure, because these fragments are in-domain.

**Why the keyed run failed. CORRECTED 2026-08-31 — the first post-mortem below was wrong.**

The run hit the built-in $5.00 spend ceiling half way (3,561 of 7,035 conversations), and the cache
holds **5,494 distinct keys against 8,769 billed calls — 3,275 duplicates**.

**The original diagnosis was `prompt_sha` drift, and the cache file itself disproves it.** If the
prompt hash had moved between the two halves, every second-run key would have been *new*: 8,769
distinct keys and **zero** duplicates. Duplicates can only exist if the key was **stable** and the
cache failed to serve a hit it already held.

**The real cause was two readers running concurrently against one cache path** — my own error, and a
compounding one. The first sweep was launched with `nohup ... &`; the liveness check used `pgrep`,
which **does not exist on this machine** (`pgrep: command not found`), so the monitor reported "SWEEP
NOT RUNNING" for a process that was still alive, and a second sweep was launched against the same
`EARSHOT_EXTRACTOR_CACHE_PATH`. `ResponseCache` loads its file once in `__init__` and never re-reads
it (`llm/cache.py:66-85`), so each process was permanently blind to everything the other wrote.

The evidence is unambiguous:

- Duplication starts at record **185**, not at the 3,561 resume boundary.
- It runs at a flat **~47%** for the first 6,836 records, then **exactly 0%** for the last 1,933 —
  two processes racing, then one alone.
- `latency_ms` differs in 3,274 of 3,275 duplicate pairs: two separate live calls, not a double-write.

**Waste was $4.60 of $12.33 (37%), not half.** And the recorded remedy — "pin `prompt_sha`" — would
have saved nothing at all.

**The actual lessons, which are different:**

1. **Never point two model runs at one cache path.** The cache is read once at construction; it is
   not a shared store and cannot be used as one.
2. **`pgrep` does not exist here.** Any liveness check built on it silently reports "dead". Check
   for the tool before trusting the check.
3. **`CachingProvider` counts `hits`/`misses` (`llm/cache.py:127-128`) and never prints them.** A 47%
   miss rate was invisible across 3,275 paid calls. Surfacing that counter would have caught this in
   the first minute.
4. **39 lines in the cache file are torn** — interleaved partial writes from the two processes.
   `_load()` swallows them silently (`llm/cache.py:79-82`), so 39 paid-for completions are
   permanently unreplayable and will `CacheMiss`. Not previously recorded.

**What the reads do support, from the cache alone and independent of the sweep:** over **5,494
unique keyed reads on the widened corpus, the model reader emitted at least one signal on 2,390 —
0.4350 — and produced zero unparseable responses.** Cache committed at
`artifacts/cache/extractor-widened-arcs.jsonl` (3.4 MB).

**Directional, NOT publishable — 6 seeds, n=300, offline reader.** On the widened corpus the ledger
stops losing to `stateless-top2` on diffuse arcs: 4-1-1, 3-0-3, 1-1-4 at alpha 2.0 / 6.0 / 20.0,
against 3-5-2, 1-7-2, 2-5-3 on the shipped corpus. None significant. Quote none of it: D-007, and
6 seeds cannot clear 0.05.

**One thing settled and now pinned.** The tautology objection — *"your diffuse stratum is defined by
the Dirichlet alpha, so an aggregator winning there is arithmetic"* — is answered by measurement
rather than argument: a tenfold change in `alpha_diffuse` does not swing the comparison, on either
corpus. `test_the_diffuse_result_is_not_a_restatement_of_the_dirichlet_alpha`.

**Open:** the widened corpus is committed but nothing is published from it. The 10-seed keyed sweep
that would decide adoption costs ~$10 with a pinned `prompt_sha`, and has not been run.

## 2026-08-31 (late) · The IAM blocker cleared, and every keyed figure re-measured

**W9's sibling blocker is gone.** IT attached `zenon-poc-lambda-inline` to
`zenon-poc-lambda-execution`. Verified rather than assumed: all four requested statements present
(SQS 5 actions, DynamoDB 5 actions, `bedrock:InvokeModel`, CloudWatch Logs 3 actions), plus S3
read/write that was not asked for. **`dynamodb:DeleteItem` is correctly absent** — the never-discard
guarantee is now enforced by the deployed role's own permissions, not only by a test scanning
`LedgerStore` for a delete method. That is a materially stronger claim than the one the entry made
yesterday: the role *cannot* delete a signal even if the code tried.

Proof of function, not of policy: `GET /cases` — which touches DynamoDB and had returned **500** on
every call since 2026-08-28 — returns **200** with a well-formed empty queue. `earshot-dev-ingest`
returns `batchItemFailures: []`. `count: 0` is honest, not an error; the tables are empty because
nothing has been ingested.

**CodeBuild was declined, deliberately.** IT offered to create the project. `buildspec.yml` calls
`npx cdk deploy`, `cd infra` and `npm run build` in `ui/`, and none of those exist — D-024 replaced
CDK with boto3 and the UI is build-step-free by design (D-004). A project created today fails on its
first command, and CI already runs on GitHub Actions. `iam:CreateRole` now passes, so if CodeBuild is
ever wanted the service role is self-serve; the blocker is our stale buildspec, not a permission.
Declining a favour is cheaper than accepting it and having it fail in someone else's name.

**All four keyed figures re-measured on the shipping corpus, ~$2.42 of a $12 budget.** Reader coverage
is the result: complaints **0/20 → 20/20**, vulnerability **0/20 → 19/20**, retention 1/20 → 16/20,
collections 9/20 → 10/20, at **$1.58 / 1,000** with zero unparsable replies. AT-57 improved to 29/50
with dismissals 4/25 → 13/25 — *the agent is unchanged*, the corpus stopped leaking the answer
through surface form. AT-58 regressed to 27/48 and publishes as worse, because no complaint customer
crosses under the offline reader so its `complaints` row is empty. Both demo fixtures re-recorded, so
the screens finally show the Phase C prose.

**~$1.15 of that spend was waste, and the cause is a reusable lesson.** AT-57 was wrapped in
`timeout 590 … | tail`, which both under-ran a 17-minute job and let the kill return exit 0 — a
truncated run looked clean, twice. Same family as the `pgrep` mistake: a wrapper that hides an exit
code turns a failure into a false success. The cache meant the rerun re-bought only 16 calls.
