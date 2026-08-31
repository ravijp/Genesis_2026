# Path to production — Ear on Every Call

**Implementation spec (deliverable ③ of three).** Zenon Genesis 2026, Track A, team Agentic Trio.
What is deployed today, what is blocked and on whom, and what a first client deployment costs.

---

## 1. What is deployed right now

Account `859430413223`, **us-east-1**, provisioned 2026-08-28 by `tools/provision.py` and
`tools/deploy.py` — plain boto3 scripts, not CDK (D-024: CDK does not work in this account).

| Resource | State |
|---|---|
| 3 DynamoDB tables — ledger, cases, reviews | On-demand, **PITR on**, no TTL, **no delete path on the ledger** |
| 2 SQS queues + DLQ | FIFO for transcripts; redrive to DLQ at 3 receives |
| 3 Lambdas — ingest, investigate, api | python3.13, one zip (`8323ff7cd3ca`), offline provider by default |
| Reviewer API | Function URL, `AuthType=AWS_IAM`. `GET /health` **200 in 1.4 s cold** |
| 6 CloudWatch alarms | Created over EMF metrics |
| Source of record | AWS CodeCommit, current with HEAD |

**The ledger has no delete method and a test scans the class surface for one.** Append-only is
enforced by absence, not by policy — which is what makes the audit guarantee checkable rather than
promised.

## 2. What is blocked, and on whom

**One IAM policy. That is the whole blocker.**

`zenon-poc-lambda-execution` has no SQS, DynamoDB, Bedrock **or CloudWatch Logs** permission. So:

- Every endpoint touching a store returns **500**. `GET /health` is the only route that works.
- Neither queue is wired to its consumer.
- **The Lambdas are unobservable, not merely inert** — no log group exists despite 4 invocations on
  2026-08-27. A failure today leaves no trace to read.
- The 6 alarms have **no actions**: no SNS on this account, so they go red in a console and page
  nobody.

`iam:PutRolePolicy` was attempted and denied. **Policy JSON is written and ready to paste into a
ticket** — `docs/ops/aws-infrastructure.md`. Owner: IT. Same `iam:CreateRole` gap blocks CodeBuild
and CodePipeline (W9).

**Honest read: the deployed path is a correct diagram, not a running system.** One policy converts it.

## 3. How it integrates with a bank

**Nine pipeline stages. Five are the client's existing systems, unchanged.** The `#/deployment`
screen counts them rather than asserting it.

**We do no speech recognition.** Not disabled, not stubbed — no code path could add one. Banks at
this size already transcribe for QA and compliance; we consume that output. `manifest.asr` is
`"none"` on every artifact and a build check fails if it ever says otherwise.

**How the UI ships into a client console.** Research across five vendors found one mechanism in four
of them: a **sandboxed iframe scoped to a conversation or case id**. Genesys interpolates
`{{gcConversationId}}`; Amazon Connect hands a third-party app `context.scope.contactId`; Dynamics
CIF loads the vendor as a sandboxed iframe web resource; NICE does the same. Salesforce is the
exception and wants a native Lightning component. So the integration surface is a bounded rectangle
inside someone else's chrome — which is exactly what the demo shows.

**Integration is deliberately thin:** read the conversation feeds the bank already produces, write
cases into a queue each team already works. It adds a memory on top of the tools a bank already runs
rather than replacing any of them.

## 4. What it costs to run

From measured figures, not a price list.

| | measured 2026-08-31 | at 1M conversations/year |
|---|---|---|
| Reader | **$1.58 / 1,000 conversations** | ~$1,580 |
| Investigation | **$0.0306 / case** | at a 10% review budget on 1M convs, ~$3,060 per 100k cases |
| Ledger update | **no model call at all** | storage only |

Both are keyed Claude Haiku 4.5 on Bedrock: the reader over 282 conversations ($0.445562), the
investigator over 50 cases ($1.5305, p95 $0.0361, max $0.0384). The reader figure is corroborated
independently at **$1.5256 / 1,000** over the 130 conversations of the streamed deployment demo,
re-recorded the same day. Neither is a projection from a price list.

**Batch, not real-time — and that is the choice that makes the economics work.** The cost that
matters is per conversation, not latency on a live call. Updating a ledger costs nothing in model
spend; re-reading a customer's whole history through a model nightly would cost one call per
customer per night.

*(The ledger re-scores a customer from scratch today rather than incrementally. The saving is the
absent model call, not an O(1) update — an incremental path is not built.)*

## 5. Human-in-the-loop, enforced by absence

**No outbound contact surface exists anywhere in the system.** No button, route, form or handler
emails, calls or messages a customer — not in the product, not in the demo server. HITL is not a
policy that could be relaxed by a config change; it is the absence of the capability.

**The decision surface is a specialist reviewer's queue, not a live-call nudge.** EU AI Act Art.
14(4)(b) names automation bias explicitly for systems giving recommendations to humans. A prompt
fired at an agent working to an average-handle-time target is that failure mode; a queue worked by a
specialist with time to open the evidence is not. Nothing is preselected in the decision bar and the
primary button is not focused on load — deliberate friction, for the same reason.

**Every case cites its evidence.** A decision must carry at least one reference resolving to a
conversation id, turn index and a verbatim run of **four or more consecutive words** of that turn. A
decision that cannot point at real words fails validation and is retried. Measured groundedness:
**0 repairs in 50 keyed investigations** — every citation resolved first try.

## 6. What a first client deployment needs

**Ready now:** ingest → ledger → threshold → investigator → case queue, all deployed as code and
tested (817 tests). Reader and investigator both run against Bedrock. The UI opens from disk with no
build step and deploys with `aws s3 sync`.

**Needed from the client:**
1. A conversation transcript feed (they already produce it for QA/compliance).
2. Read access to account state and transactions for the investigator's tools.
3. A destination for cases — their existing case-management queue.
4. A decision on model residency and data-processing terms.

**Needed from us, in order:**
1. **The IAM policy** — unblocks everything and has the longest external lead time.
2. Wire the queues to their consumers, and give the alarms an action (EventBridge → Lambda; there is
   no SNS on this account).
3. A signing path for the UI's write route — a static page cannot sign an `AuthType=AWS_IAM`
   Function URL. Currently the decision buttons show the exact request body that *would* be sent and
   say plainly that it was not.
4. CI/CD, once `iam:CreateRole` lands. `buildspec.yml` is parked and has never run; the suite is
   gated today by GitHub Actions.

**Not built, and not pretended otherwise:** multi-tenant isolation beyond a display-only tenant
config, retention/deletion policy for the ledger, SSO/RBAC for the reviewer UI, and an incremental
re-scoring path.

## 7. The honest risk

**The mechanism is not yet proven to beat chance.** On the stratum the entry is built for, the full
ledger vs a seeded-RNG control is **18-8-4, p=0.076** — and it is no better on the other strata
(13-11-6, p=0.839 whole-portfolio; 16-12-2, p=0.572 concentrated). Whole-portfolio it is **8th of 9
arms**, two thousandths above chance (0.115 vs 0.113). The headline pre-registered on 2026-08-09
**died** when the corpus was rebuilt on 2026-08-31 (29-0-1 to 15-13-2, p=0.851), and our own ablation
floor beats us on diffuse arcs under the default tie-break (7-18-5, p=0.043). These records have now
reversed twice across two corpus rebuilds; they describe the corpus at least as much as the mechanism.

**What that means for a deployment.** The value proposition that is **measured** is coverage and
triage: read 100% of conversations instead of a sample, assemble cited evidence, route to a desk. That
is the claim to sell, and the sharpest number behind it is what the reader decides on its own — the
same 282 planted conversations through the same ledger at the same threshold:

| Desk | keyless lexicon | model reader |
|---|---|---|
| **Complaints** | **0 / 20** | **20 / 20** |
| **Vulnerability** | **0 / 20** | **19 / 20** |
| **Retention** | **1 / 20** | **16 / 20** |
| Collections | 9 / 20 | 10 / 20 |

Two of four review desks receive **no case at all** under the keyless reader. Corroborated on external
data: on real complaint narratives the model reader recovers 0.8214 (92 / 112) against the lexicon's
0.0357 (4 / 112). **The model column is an upper bound** — the threshold is a top-K cut over the
offline reader's ranking held fixed across arms, and deriving the model's own cut costs $13.96, not
spent. **Read it as a deployment risk in both directions:** a reader this much stronger changes who
lands in the queue, so a first deployment has to size the desks for the reader it actually runs, and
the model reader is *worse* than the lexicon on `financial_distress` coverage (0.38 vs 0.46).

**Routing accuracy is a caveat on the "route to a desk" half of that claim, and it moved against us:**
**27 / 48 correct, 2 wrong, 19 declined**, down from 36 / 49 on the previous corpus. The cause is the
coverage gap above, arriving from the other side — no complaint customer crossed under the keyless
reader, so the confusion matrix's `complaints` row is empty and 43 of the 48 scorable cases are a
single desk. A first deployment that fixes the reader is measuring routing on a distribution this
figure has never seen.

**What is now measured that this page previously called unproven:** unbounded memory *does* beat a
cheap three-conversation window on diffuse arcs — **30-0-0, p<0.001**, under both tie-break rules. It
**loses** on concentrated arcs (1-28-1) and is unproven whole-portfolio (9-17-4, p=0.169). Sell the
first, disclose the other two, and instrument a first deployment to test all three on real
conversation histories, which are longer than any synthetic corpus we have built.

*Every figure on this page — sweep, reader coverage, cost, latency, routing — was measured on
**2026-08-31** against the corpus that ships, and the keyed ones replay from committed model responses
with no API key. Infrastructure coordinates and the reproducible error lines:
`docs/ops/aws-infrastructure.md`.*
