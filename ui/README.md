# The UI — two halves, no build step

Open `ui/index.html`. That is the whole instruction.

No npm, no bundler, no dev server, no network. Static files plus two generated data files, so a
judging room with no wifi and a laptop with no toolchain can still see the product (D-004). It is
also the only shape that is deployable today: CodeBuild is blocked on IT (W9), and `aws s3 sync
ui/ s3://agentic-trio/ui/` needs nothing we do not have.

## The two halves, and why they look different

| | Route | What it is |
|---|---|---|
| **In use** | `#/desk` | The reviewer's console: a ranked queue, a case, and a disposition — **our panel inside a stand-in of the client's own case-management desktop** |
| **In use** | `#/desk/call` | The same console during a live call, with the reader's turn-by-turn output. Labelled illustrative |
| **How it works** | `#/stream` | The whole book arriving in day order: the ledger accumulating, the queue re-ranking, cases opening |
| **How it works** | `#/deployment` | The nine pipeline stages and who owns each. Six of nine are the client's existing systems |

The console is dense chrome someone works in all day and nothing in it animates. The stream
deliberately moves, because the motion *is* the argument. Keeping them visually distinct is the
framing: one is the product, the other is why its numbers are true.

`#/case/<id>`, `#/case/<id>/retro` and `#/conversation/<id>` still render the recorded
`earshot investigate` run as standalone documents — the retro re-score in particular stays a full
screen rather than a panel row, because it is the proof and the panel's ledger table is only the
teaser.

## The console, and exactly what is a mock

**The chrome is a stand-in and says so, permanently and non-collapsibly.** It is not any real
vendor's product and carries no vendor logo, wordmark, brand colour or icon set.

Why it is shaped the way it is: research into how third-party UI actually ships into the consoles
retail banks run found **one mechanism in four of five vendors — a sandboxed iframe scoped to a
conversation or case id**. Genesys interpolates `{{gcConversationId}}` into an admin-configured
URL; Amazon Connect hands a 3P app `context.scope.contactId`; Dynamics CIF loads the vendor "as an
iframe web resource in sandbox mode"; NICE does the same under Custom Workspace. Salesforce is the
exception and wants a native Lightning component. So **a bounded rectangle inside someone else's
chrome, with a visible seam and a provenance footer, is the literally accurate depiction** of how
this ships — not a stylistic choice.

Everything borrowed from the category is borrowed because two or more vendors document it
independently: a workspace tab strip for open work items, a split-view list beside a record
region, a docked bottom utility bar whose items pop panels upward and persist across tabs, status
pills coloured by state, 4px severity stripes on alert rows, 13px body type with a 12px floor, and
tabular numerals.

Everything deliberately avoided is avoided for a stated reason: **Salesforce Sans** is licensed
only "to create applications with the Salesforce Lightning Design System that run in Salesforce",
**SLDS icon SVGs are CC BY-ND** so recolouring one is plausibly a derivative, **Amazon Ember** is
proprietary, and no vendor brand hex appears anywhere. Type is a system stack and the marks are
text glyphs.

## Why the reviewer, and not the person on the phone

The primary surface is the specialist reviewer's case triage. Three reasons, in order of weight:

1. **Accumulation across conversations is the whole product, and a live-call panel structurally
   cannot show it.** It only knows the call in front of you — that is single-call detection, the
   framing this project already judged a loser.
2. **The decision-maker is not the agent on the call.** Retention, collections, vulnerability and
   complaints are staffed by specialists working case queues.
3. **EU AI Act Art. 14(4)(b) names automation bias explicitly** for systems providing
   recommendations to humans. A nudge fired at someone working to an average-handle-time target is
   that failure mode; a queue worked by a specialist with time to open the evidence is not.

The live-call view ships anyway, because the turn-by-turn read is the most striking thing we own.
It says **"Illustrative … nobody decides here"** on the screen, with the reason.

## Four deliberate choices in our panel

- **Confidence is always a number**, never a word alone.
- **Sub-threshold ledger rows render at full contrast.** Dimming them would draw exactly the
  incumbent behaviour this product inverts: they are retained, and they still count.
- **Nothing is preselected in the decision bar and the primary button is not focused on load.**
  That is deliberate friction, for the reason in Art. 14(4)(b) above.
- **"What would change my mind" is a first-class row**, not a tooltip.

The decision buttons are **honest about being inert**. `aws/api.py` serves
`POST /cases/{id}/reviews` and `ReviewStore` holds the audit trail, but a static page cannot sign
an `AuthType=AWS_IAM` Function URL, so clicking shows the exact request body that *would* be sent
and says plainly that it was not. A button that silently does nothing is worse than one that
explains itself.

## The live-stream demo, and exactly what is real about it

**There is no speech recognition in this system.** Not disabled, not stubbed — it does not exist,
no code path could add one, and the deployment screen marks that seam as the *client's*. Banks at
this size already transcribe for QA and compliance; we consume that output.

What the stream reproduces faithfully is the **arrival pattern**: the order conversations land in
across the whole book, the days between them, the channel mix. At `1×` each frame is held for the
reader's *own measured latency on that conversation*. `manifest.asr` is `"none"`, the banner prints
it, and `ui/smoke.mjs` fails the build if it ever says otherwise.

**Everything downstream of the transcript is real.** A Bedrock Haiku 4.5 call read every one of the
133 conversations; six were read *again after each customer turn* so a belief can be watched
forming; `memory.py` scored them; the investigator worked six crossings with its five tools. Costs
and latencies on screen are measured.

**The threshold is a fixed cut, and it is not the number the recorded investigate run uses.** A
streaming consumer has no population to rank against, so it cannot take the top 10% of anything.
This mirrors `aws/ingest.py`, the deployed path. The two disagree about who crossed; both are
labelled on their own screen.

**Not everything is worked.** 6 of 9 crossings were investigated and 6 of 133 conversations were
read turn-by-turn — the first to bound a re-record's cost, the second because narration costs a
model call per customer turn. Both denominators are on the screen.

## Watching it live against AWS

```bash
# Recorded replay — the default, and what survives a room with no wifi
open ui/index.html

# Live: real Bedrock calls while the room watches, served on localhost
AWS_PROFILE=genesis EARSHOT_CACHE_MODE=off \
  uv run earshot stream --extractor model --provider bedrock --serve --narrate-live 3
# then open http://127.0.0.1:8765/index.html#/stream and press "Go live"
```

The browser never holds an AWS credential — it opens an `EventSource` to `127.0.0.1` and the
server process makes the calls. The socket binds loopback only, which is what makes the
unauthenticated routes safe; `tests/test_stream_server.py` pins that and the absence of any write
route. **The LIVE badge names the cache mode**, because with a warm reader cache a "live" run
serves recorded completions in seconds; `EARSHOT_CACHE_MODE=off` forces genuinely new calls.

## Regenerating the data

Both data files are generated and **committed**, so a fresh clone works with no Python run.

```bash
uv run earshot investigate --customers 400 --limit 8   # the recorded document screens
uv run python tools/ui_fixture.py

uv run earshot stream                                   # the console and the stream
uv run python tools/stream_fixture.py

node ui/smoke.mjs        # renders every route against a stub DOM; also run by uv run pytest
```

Both fixtures reformat and never compute: queue rows come from `api._queue_row`, the same function
the deployed `GET /cases` uses, and every frame's score came from `memory.py`.

## What it deliberately does not do

- **It never contacts anyone.** No button, route or form here — nor in the demo server — emails,
  calls or messages a customer. HITL is enforced by the absence of an outbound surface.
- **It never computes a score.** Counting an array or sorting a list is fine and already happens;
  deriving a score, a share or a rank is not. `memory.py` is the one scorer.
- **It never hides its provenance.** Every screen names the provider, seed, config hash, git SHA
  and ASR status, and says plainly when a run came from `offline-rules` — a rule engine, not a
  model.
- **It never regenerates the corpus.** Both artifacts carry their own transcripts precisely so
  nothing here reaches for `manifest.seed`.

  **The seed is on the page, in `manifest.seed`, and that is a deliberate trade with a real
  limitation.** Provenance a judge cannot reproduce from is worth little. So the guarantee is
  narrower than "the answer key is unreachable" — anyone with this repo and that seed can
  regenerate the corpus. It is: **no answer-key field is present in either fixture, and no code
  path in this UI regenerates anything.** Three checks enforce it. `Tenant.public()` goes further
  and withholds the seed, so nothing tenant-shaped carries it — but the manifest does, on purpose.

- **The customer-360 header is synthetic and stamped so on the object.** It is exactly what the
  investigator's own tools already read, derived from `financial_state` and never from
  `latent_risk` — that distinction is the leak this repo has already got wrong once, and
  `tests/test_no_answer_key_leak.py` now pins the wiring as well as the statistics.
