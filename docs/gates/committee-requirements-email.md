# DRAFT — tooling & access requirements

**Send:** immediately after the 2026-08-10 check-in call, so it lands with the CodeCommit conversation
already had rather than ahead of it.

**To:** genesis@zenon.ai
**Cc:** Ishant Gupta; Namit Mittal; Bharti Sahai; Suyash Baderiya; Novnit Kashyap; Riya Gupta
**Subject:** Agentic Trio — tooling & access requirements (overdue, with apologies)

---

Hi Genesis Committee,

Apologies — this is late. You asked for tooling requirements by 24 July and chased on 29 July, and we
didn't come back to you. That one is on us. Here is the list, following on from this morning's check-in.

**Team:** Agentic Trio (Ishant Gupta, Namit Mittal, Ravi Prakash)
**Entry:** Track A — *Ear on Every Call*

## 1. Model API access

| # | What | Why |
|---|---|---|
| 1 | **Claude API key**, with the budget limit you apply | Primary model — signal extraction and the investigator agent |
| 2 | **OpenAI API key** (or a second provider of your choosing), with budget limit | Our submitted brief commits to running a comparison model through the identical eval harness "so the numbers are honest". We can't deliver that on one provider |
| 3 | Confirmation: **direct vendor APIs, or AWS Bedrock?** | The rest of the stack is AWS. If Bedrock is the intended route we'd rather build against it now than migrate in September |
| 4 | The **per-team budget limit**, as a number | We batch-process a synthetic corpus, so we can size eval runs to the budget rather than discover the ceiling mid-sprint |

To be transparent about where we are: rather than stay blocked, we bridged model access on a **personal
OpenRouter account** so the agent layer could be built this week. That is fine for development, but
competition rule 1 says the IP is Zenon's and rule 2 says Zenon provides the keys — so we'd like the
final submission running on Zenon-provided credentials. Our provider layer is model-agnostic, so
switching is a new provider class behind the same interface — an afternoon, not a migration.

## 2. AWS services

| # | What | Why |
|---|---|---|
| 5 | **AWS CodeCommit** repository URL + IAM credentials (or the SSO path) | Per this morning's discussion. Detail below |
| 6 | **S3** bucket | Generated synthetic corpora, model-response caches, per-run eval artifacts |
| 7 | **Bedrock**, if that's the model route (see #3) | — |

Nothing else. The runtime is deliberately a nightly batch job with no always-on infrastructure — if
that changes we'll come back rather than sit on it.

**On CodeCommit specifically.** *"Functional prototype: code in AWS CodeCommit"* is a named required
deliverable and commit/PR discipline is scored in the operating model, so we'd like to resolve this
well before the finals. When the repository is available, could you send the URL, credentials, and
whether you want us on `git-remote-codecommit` or HTTPS Git credentials — whichever the other teams are
using. Our full commit history is intact and we'll push it as history rather than one squashed commit,
so the "meaningful commits" evidence survives the move.

## 3. JIRA — resolved, no action needed

We have board access and have loaded the backlog under project **AT (Agentic Trio)**: 8 epics and 37
tasks covering the dataset, the reading step, the customer memory, the investigator, the review queue,
measurement, the demo, and engineering practice. Nothing is marked resolved yet — none of it has been
reviewed by a second person. Please flag if you'd rather we filed somewhere else.

## 4. Where we are

We aren't blocked on any of the above. The pipeline runs end to end with **no API keys at all** on a
deterministic offline provider — corpus generation, the per-customer signal ledger, the evaluation
harness, and the demo scenario are all working and reproduce from a single command on a fresh machine.
Model access improves extraction quality and unlocks the two-model comparison; it doesn't gate the
project.

Thanks, and again, sorry for the delay on our side.

Ravi
*on behalf of Agentic Trio*

---

## Notes for us — not part of the email

- **Don't soften the apology.** They chased twice. Owning it in one line and moving on reads better
  than an explanation.
- **The comparison-model ask (#2) is a stated deliverable**, not a nice-to-have — the brief promises it
  in writing. Dropping it quietly means shipping less than we said we would.
- **CodeCommit is the real exposure, not the keys.** Keys we routed around in an evening. A named
  required deliverable we cannot satisfy is the thing that costs marks, and the AI judge scores repo
  hygiene directly.
