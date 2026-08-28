# The UI — five screens, two data sources, no build step

Open `ui/index.html`. That is the whole instruction.

No npm, no bundler, no dev server, no network. Static files plus two generated data files, so a
judging room with no wifi and a laptop with no toolchain can still see the product (D-004). It is
also the only shape that is deployable today: CodeBuild is blocked on IT (W9), and `aws s3 sync
ui/ s3://agentic-trio/ui/` needs nothing we do not have.

## The screens

| Screen | Route | What it is for |
|---|---|---|
| **Deployments** | `#/portfolio` | Three enterprises on one engine: what each book is, what differs between them, and where their cases were routed. The front door when stream data is present |
| **Live stream** | `#/stream/<tenant>` | Conversations arriving in day order across the whole book. The reader flags turns, the ledger accumulates, the queue re-ranks, a customer crosses, a case opens |
| **Ranked queue** | `#/queue` | Who a review team should look at *today*. Ranked on the current score, with the opening-day score beside it, because decay makes them differ |
| **Case** | `#/case/<id>` | The agent's verdict, the quotes it cited, the whole evidence chain, and the run that produced it — cost, tool calls, why it stopped |
| **Retro re-score** | `#/case/<id>/retro` | The same earlier conversations, re-read in light of the last one: what each quote supported when it arrived against what it supports now, and whether the case collapses without it |

`#/conversation/<id>` shows the transcript behind a cited quote with the cited turn highlighted —
the reviewer's check that the model did not invent it.

A streamed case has the same three screens under its tenant:
`#/stream/<tenant>/case/<id>`, `.../retro`, `.../conversation/<id>`. **Same renderers**, because
`case_record()` builds a streamed case and a recorded one identically. Adding the demo added
routes, not a second copy of the evidence chain.

## The live-stream demo, and exactly what is real about it

**There is no speech recognition in this system.** Not disabled, not stubbed — it does not exist
and no code path could add one. The transcripts were generated as text. What the stream reproduces
faithfully is the **arrival pattern**: the order conversations land in across the whole book, the
days between them, the channel mix. At `1×` each frame is held for the reader's *own measured
latency on that conversation*, so "real time" is a number from the run rather than an animation
speed someone picked. `manifest.asr` is `"none"` on every tenant, the banner prints it, and
`ui/smoke.mjs` fails the build if it ever says anything else.

**Everything downstream of the transcript is real.** A Bedrock Haiku 4.5 call read every one of the
460 conversations. `memory.py` scored them. The investigator agent worked twelve crossings with its
five tools and a bounded loop. The costs and latencies on screen are measured, not modelled.

**The threshold is a fixed cut, and that is not the same number the reviewer queue uses.** A
streaming consumer sees one conversation at a time and has no population to rank against, so it
cannot use the budget-derived top-10% threshold `earshot investigate` reports. This mirrors
`aws/ingest.py`, which is the deployed path. The two disagree about who crossed. Both are labelled
on their own screen; do not let them merge on stage.

**Not every crossing is investigated.** Each tenant works a bounded number so a keyed re-record has
a predictable cost. The rest are listed as unworked *with the reason* under the decided cases,
because showing four worked cases out of nine crossings without saying so claims a precision
nothing measured.

## Three deployments, and what "multi-tenant" actually means here

A tenant is **one configuration of one engine**: its own corpus, its own decay half-lives, its own
fixed threshold, and its own names for the four canonical routing teams. There is no per-tenant
scorer, prompt or code path, and `InvestigationDecision.owning_team` stays the closed five-value
`Literal` it always was — each tenant supplies the local *label* for each fixed slot, never a new
slot. A new enterprise is a dictionary in `src/earshot/tenants.py`.

The differences are risk-book differences, not decoration. A card issuer's complaint half-life is
45 days and a mortgage servicer's hardship half-life is 320; a servicer with four reviewers on a
book of 38 cannot accept a card issuer's alert rate. `tests/test_tenants.py` fails if the three
ever collapse into the same tuning.

Every enterprise here is invented and every book is synthetic. The names exist so three deployments
are distinguishable on screen.

## Watching it live against AWS

```bash
# Recorded replay — the default, and the one that survives a room with no wifi
open ui/index.html

# Live: real Bedrock calls while the room watches, served on localhost
AWS_PROFILE=genesis EARSHOT_CACHE_MODE=off \
  uv run earshot stream --tenant northwind --extractor model --provider bedrock --serve
# then open http://127.0.0.1:8765/index.html#/stream and press "Go live"
```

The browser never holds an AWS credential. It opens an `EventSource` to `127.0.0.1` and the server
process makes the calls. The socket binds loopback only, which is what makes the unauthenticated
routes safe; `tests/test_stream_server.py` pins that, along with the absence of any write route.

**The LIVE badge names the cache mode**, because with a warm reader cache a "live" run serves
recorded completions in seconds. `EARSHOT_CACHE_MODE=off` is what forces genuinely new calls, and
the badge then reads *every call is new*.

## Regenerating the data

Both data files are generated and **committed**, so a fresh clone works with no Python run.

```bash
# the reviewer screens
uv run earshot investigate --customers 400 --limit 8
uv run python tools/ui_fixture.py

# the demo screens (keyless; add --extractor model --provider bedrock for the keyed version)
uv run earshot stream --tenant all
uv run python tools/stream_fixture.py

node ui/smoke.mjs          # renders every route against a stub DOM; also run by uv run pytest
```

Both fixtures reformat and never compute: queue rows come from `api._queue_row`, the same function
the deployed `GET /cases` uses, and every frame's score came from `memory.py` inside `earshot
stream`. So these pages render identical objects whether fed a recorded run or a live API.

## What it deliberately does not do

- **It never contacts anyone.** There is no button, route or form here that emails, calls or
  messages a customer, and none in the demo server either. HITL in this system is enforced by the
  absence of an outbound surface, and adding one would end that claim.
- **It never computes a score.** Every number on screen is read off the data. `memory.py` is the
  one scorer in the system and a browser is not going to become the second.
- **It never hides its provenance.** The banner names the provider, seed, config hash, git SHA and
  ASR status on every screen, and says plainly when a run came from `offline-rules` — a rule
  engine, not a model, whose verdicts are a floor rather than a result. A screenshot outlives the
  caveat someone said out loud beside it.
- **It never regenerates the corpus.** Both artifacts carry their own transcripts precisely so
  nothing here has to reach for `manifest.seed`, which would put `stratum`, `outcome` and
  `latent_risk` one object away from a client-facing screen.

  **The seed is on the page, and that is a deliberate trade with a real limitation.** It sits in
  `manifest.seed` because provenance is what lets a judge reproduce a run, and a screen that names
  a run it cannot identify is worth little. So the guarantee is *not* "the answer key is
  unreachable" — anyone holding this repo and that seed can regenerate the corpus and read every
  `stratum` and `outcome` in it. The guarantee is narrower and mechanical: **no answer-key field is
  present in either fixture, and no code path in this UI regenerates anything.** Three checks
  enforce it (`earshot.stream`, the fixture tool, `smoke.mjs`). The per-tenant block goes further —
  `Tenant.public()` withholds the seed and every corpus parameter, so nothing tenant-shaped carries
  it — but the manifest does, on purpose, and it is better to say so than to imply a stronger
  claim.

## Not built yet

The **write** path. `aws/api.py` serves `POST /cases/{id}/reviews` (approve · dismiss · route, with
a reason required on a dismissal), and the audit trail behind it exists in `ReviewStore`. These
pages are read-only until the deployed API is reachable from a browser — its Function URL is
`AuthType=AWS_IAM`, which a static page cannot sign, and the execution role is currently missing
the DynamoDB and SQS permissions anyway (see `docs/ops/aws-infrastructure.md`).

`--serve` does **not** close that gap: it serves a demo stream from local state, not the deployed
API, and it has no write route by design.
