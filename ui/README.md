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
| **In use** | `#/desk/team/<slot>` | The same queue scoped to one routing destination, plus `none` for the cases the agent declined to route. The slot is in the route, so a team view is a link you can send |
| **In use** | `#/desk/call` | The same console during a live call, with the reader's turn-by-turn output. Labelled illustrative |
| **How it works** | `#/stream` | The whole book arriving in day order: the ledger accumulating, the queue re-ranking, cases opening |
| **How it works** | `#/deployment` | The nine pipeline stages and who owns each. Five of nine are the client's existing systems |

The console is dense chrome someone works in all day and nothing in it animates. The stream
deliberately moves, because the motion *is* the argument. Keeping them visually distinct is the
framing: one is the product, the other is why its numbers are true.

`#/case/<id>`, `#/case/<id>/retro` and `#/conversation/<id>` still render the recorded
`earshot investigate` run as standalone documents — the retro re-score in particular stays a full
screen rather than a panel row, because it is the proof and the panel's ledger table is only the
teaser.

## The team-scoped queue

The submitted brief promises that **three teams read the same feed**
(`docs/sources/submission-ear-on-every-call.md:75-79`, and `:124` makes it a Sprint 3
deliverable). The shipped set is four and different, so `#/desk/team/<slot>` is a filter over
`owning_team` — a field every case row already carries, graded at **36 / 49 correct, 2 wrong, 11
declined** (`tools/routing_accuracy.py`). It is a view over a measured field, not new inference.
(This read 41 / 49 with 0 wrong until 2026-08-30; that figure was measured on the pre-fix corpus
and did not survive the corpus fix. See `docs/architecture/build-plan.md` §4.)

Four things about it are load-bearing:

- **The filter is in the route**, `#/desk/team/retention` and `#/desk/team/<slot>/case/<id>`, so
  it survives a reload and a team view is a link someone sends a colleague. The **slot** is what
  goes in the URL — it is the model's stable vocabulary; the **label** a reviewer reads comes from
  the tenant's display-only map (D-029) and never the other way round.
- **Every count carries its denominator** on the control itself: "Retention Desk — 1 of 6 cases".
- **`none` is a bucket, not an empty state.** It means the agent declined to choose, not that no
  team exists, and the control says so. It is listed at zero for the same reason
  `stream._team_rollup` lists it: a dashboard that drops the row reads as "the agent always picks
  a team", and a declined route is the case a reviewer most needs to see.
- **A team with zero cases still appears and still opens.** Hiding it would tell a reviewer their
  queue is complete when it is not, and an empty destination is a finding — it is how a model
  that escalates instead of discriminating shows up.

The buckets are counted in the browser from `block.cases`, the same array the rows below the
control come from, rather than read off the recorded `block.teams` rollup. Two sources is how a
control ends up printing a number the visible rows contradict. Counting an array is not scoring
one; `memory.py` is still the only scorer here.

**What the brief promised and what shipped** is on the screen, in two sentences under the filter:
Retention survives by name, Risk and Compliance splits across Collections, the Vulnerable Customer
Unit and Complaints, and **Commercial has no equivalent** — the ledger never modelled an upsell or
value read, and inventing a team to match the brief would be worse than saying so. Logged as delta
7 in `docs/architecture/build-plan.md` §8.

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

## The design system, and the gate that keeps it honest

Three stylesheets, one system. `styles.css` holds the tokens and the document screens, `demo.css`
the stream, `console.css` the reviewer console. **`demo.css` and `console.css` define no colour, no
size and no spacing value of their own** — they index tokens declared once.

**The neutral ramp is generated, not chosen.** Sixteen steps at a fixed hue (255°) and a low, near
constant chroma (0.012, tapered to zero at pure white), with OKLCH lightness stepping evenly from
0.150 to 1.000: `L(i) = 0.15 + i × 0.85/15`. Even steps in OKLCH are even steps to the eye, which
arbitrary greys are not — `#171b21` beside `#1e242c`, which is what this file used to hold, is two
colours picked on two different afternoons and it reads that way. **Both themes index the same
ramp**: light takes 15/14/13 for surfaces and 01/05/06 for inks, dark takes 00/01/02 and 14/11/09.
That is what makes them one design rather than a design and its inversion. The hexes are emitted
rather than left as `oklch()` because this page opens from `file://` on a laptop nobody controls.

**Semantic colours are generated the same way** and share one lightness per theme — 0.475 light,
0.780 dark — across all four hues (accent 255°, ok 155°, warn 72°, bad 27°), so no state shouts
over another. `--x-soft` is the same hue at L 0.960 / 0.262.

**Elevation is surface, not outline.** Three surfaces one ramp step apart, plus `--edge`: an inset
one-pixel top highlight in dark (a raised thing in a dark room catches light on its lip), a
barely-there shadow in light. Cards lost their borders. Hairlines separate rows *inside* one
surface; they are not how a box proves it is a box.

| Token family | What it is |
|---|---|
| `--n-00 … --n-15` | the ramp. Nothing else defines a neutral |
| `--bg` `--panel` `--panel-2` `--hi` | the three surfaces plus the hover/selection fill |
| `--ink` `--ink-2` `--ink-3` | three text strengths, all ≥ 4.5:1 on every surface they land on |
| `--line` / `--line-strong` | a rule between rows of one surface / a boundary that identifies something |
| `--fs-1 … --fs-10` | one type scale, both halves. 13px console body, 13.5px document body, 10.5px floor |
| `--s-0 … --s-8` | one 4px rhythm. There are no ad-hoc pixel paddings left |
| `--radius-sm/--radius/--radius-lg` | 2 / 4 / 6px, shared — `--c-radius` is an alias, not a fork |
| `--tr-tight` `--tr-caps` | large text pulls in, small caps open out |

**`--accent` and `--accent-ink` are two different things, and the split is load-bearing.**
`console.js` and `live.js` re-point `--accent` per deployment with the tenant's own hex, so it can
be any colour a client hands us. It therefore never carries a word: it is identity, drawn as seams,
stripes, fills and marks. `--accent-ink` is ours, defined per theme, and is every accent-coloured
word on the screen. `--accent-edge` is the tenant colour pushed 80% toward black in light and
toward white in dark — a *monotone* correction, always away from the ground, so it works for any
hex — and it draws every boundary and every graphical mark rendered in the client's colour. The
raw tenant hex clears 3:1 against white and fails it against the workspace grey; a client's brand
colour cannot be asked to be accessible, so the system corrects it instead of hoping.

The host chrome is now **entirely neutral**. Painting a stand-in of someone else's product in our
accent was what made the seam hard to see: if the whole desktop is blue, a blue rectangle inside it
is not a boundary. The only saturated edge in the client's console is ours.

### `node ui/contrast.mjs` — the gate

"Sophisticated" is unfalsifiable, so it is not what gets checked. This script renders every screen
against the same stub DOM `smoke.mjs` uses, parses the three real stylesheets, runs a small cascade
of one over the other, and computes a WCAG ratio for **every foreground/background pair the markup
actually produces** — in both themes, with the tenant's inline `--accent` override in place.

    node ui/contrast.mjs          # the table, non-zero exit on any failure
    node ui/contrast.mjs --all    # include the pairs it reports but does not gate

    text   >= 4.5:1   body copy (WCAG 2.2 AA, 1.4.3)
    large  >= 3.0:1   >= 24px, or >= 18.66px bold
    ui     >= 3.0:1   a border or a graphical mark that identifies a control, a region or a state
    decor  reported   a hairline between rows of ONE surface, which identifies nothing

**Nothing in it is listed.** The routes come from the fixtures, the markup from running the
application, the rules from parsing the stylesheets, and the pairs fall out of the cascade — so it
cannot be one forgotten line away from a hole (working-agreements §6). That cuts both ways, so the
discovery is asserted: the run fails if it finds no pairs, if either theme produces none, if the
two themes resolve identically, if the tenant's corrected accent never reaches a `--c-seam` pair,
or if any of nine sentinel classes — the stand-in label, the illustrative banner, the decision
buttons, the confidence number, the ledger, both provenance strips, a queue row, a board row —
stops appearing.

It also enforces one rule that is ours rather than WCAG's: **a sub-threshold ledger cell must be
inked with the panel's primary ink**, discovered as whichever ink reaches the highest contrast on
`--c-panel` anywhere in the run. Holding a retained row back one step is the natural way someone
would "de-emphasise a secondary row", it would still clear 4.5:1 on its own, and it fails here —
because dimming retained evidence draws exactly the incumbent behaviour this product inverts
(D-030). `opacity` below 1 on anything carrying text fails for the same reason.

Three attacks were run against it on 2026-08-28 and all three were caught: dimming the
sub-threshold ledger row, cutting the tenant override out of the seam, and lightening the console's
secondary ink. `tests/test_ui.py` runs the gate, so it is part of `uv run pytest` when node is on
PATH.

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
and says plainly that it was not. **That is not the only reason it would not work.** The Lambda
execution role is still missing its SQS, DynamoDB and Bedrock permissions (`aws-infrastructure.md`),
so the endpoint returns 500 on anything touching a store regardless of who signs the request —
signing the request would only trade one failure for another. A button that silently does nothing
is worse than one that explains itself.

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
node ui/contrast.mjs     # WCAG ratios for every colour pair on screen; also run by uv run pytest
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
