# The reviewer UI — three screens, no build step

Open `ui/index.html`. That is the whole instruction.

No npm, no bundler, no dev server, no network. Three static files plus a generated `data.js`, so a
judging room with no wifi and a laptop with no toolchain can still see the product (D-004). It is
also the only shape that is deployable today: CodeBuild is blocked on IT (W9), and `aws s3 sync
ui/ s3://agentic-trio/ui/` needs nothing we do not have.

## The three beats

| Screen | Route | What it is for |
|---|---|---|
| **Ranked queue** | `#/queue` | Who a review team should look at *today*. Ranked on the current score, with the opening-day score beside it, because decay makes them differ |
| **Case** | `#/case/<id>` | The agent's verdict, the quotes it cited, the whole evidence chain, and the run that produced it — cost, tool calls, why it stopped |
| **Retro re-score** | `#/case/<id>/retro` | The same earlier conversations, re-read in light of the last one: what each quote supported when it arrived against what it supports now, and whether the case collapses without it |

A fourth route, `#/conversation/<id>`, shows the transcript behind a cited quote with the cited turn
highlighted — the reviewer's check that the model did not invent it.

## Regenerating the data

`ui/data.js` is generated and **committed**, so a fresh clone works with no Python run. Rebuild it
after any change to the case shape:

```bash
uv run earshot investigate --customers 400 --limit 8
uv run python tools/ui_fixture.py
node ui/smoke.mjs          # renders every route against a stub DOM; also run by uv run pytest
```

The fixture reformats and never computes: queue rows come from `api._queue_row`, the same function
the deployed `GET /cases` uses, and the cases are copied out of the artifact untouched. So this page
renders the identical objects whether it is fed a recorded run or a live API.

## What it deliberately does not do

- **It never contacts anyone.** There is no button, route or form here that emails, calls or
  messages a customer. HITL in this system is enforced by the absence of an outbound surface, and
  adding one here would end that claim.
- **It never computes a score.** Every number on screen is read off the data. `memory.py` is the one
  scorer in the system and a browser is not going to become the second.
- **It never hides its provenance.** The banner names the provider, seed, config hash and git SHA on
  every screen, and says plainly when the run came from `offline-rules` — a rule engine, not a
  model, whose verdicts are a floor rather than a result. A screenshot outlives the caveat someone
  said out loud beside it.
- **It never regenerates the corpus.** The artifact carries its own transcripts precisely so nothing
  here has to reach for `manifest.seed`, which would put `stratum`, `outcome` and `latent_risk` one
  object away from a client-facing screen.

## Not built yet

The **write** path. `aws/api.py` serves `POST /cases/{id}/reviews` (approve · dismiss · route, with a
reason required on a dismissal), and the audit trail behind it exists in `ReviewStore`. This page is
read-only until the deployed API is reachable from a browser — its Function URL is
`AuthType=AWS_IAM`, which a static page cannot sign, and the execution role is currently missing the
DynamoDB and SQS permissions anyway (see `docs/ops/aws-infrastructure.md`).
