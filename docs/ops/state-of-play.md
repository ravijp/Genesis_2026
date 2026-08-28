# State of play

**Updated 2026-08-28 (late).** Rewritten in place every working session — **never appended to**. If
something will not fit, it belongs in `decisions.md` (a choice), `working-agreements.md` (a rule), or
Jira (work). Anything historical belongs in git.

**Fresh session, read in this order:** this file → `decisions.md` → `working-agreements.md` →
`../../README.md` → `../architecture/architecture.md`. Then `../architecture/infrastructure.md` for the
AWS design and `aws-infrastructure.md` for what is actually provisioned.

---

## Where we are

The system runs end to end with **zero API keys**: dataset generation → extraction → per-customer
ledger → investigator agent producing case files with cited evidence → a UI that opens from disk.
**774 tests**, ruff clean, separation guard over **44 modules** across `src/` and `tools/`.
Next gate **2026-09-07**.

**A red team of four ran against the whole entry on 2026-08-28** — code correctness, architecture
invariants, story-versus-evidence, and demo/UI/AWS honesty. It found one defect that was
manufacturing the entry's core mechanism, eight guards that were green while the thing they guard was
broken, and six document statements that were false. All are fixed; the numbers moved and are
republished. That session is the reason most of this file changed.

**The corpus was manufacturing corroboration (fixed, `08b20cc`).** The planter re-used an
already-planted fragment once a trajectory's pool ran out, so the same sentence appeared in two
conversations, the reader emitted two signals with different `conversation_id`s, and the ledger paid a
**cross-conversation corroboration bonus for one utterance copied twice** — at the shipped default,
120 / 822 arc customers at sweep size. Every published number was regenerated.

**What that cost, stated rather than buried.** The pre-registered diffuse win **survives at 30 seeds**
(26–2–2, `p=0.000`, gap 0.068 → 0.073) and **stops clearing 0.05 at 10** (8–0–2 `p=0.008` →
7–2–1 `p=0.180`). The loss to `window3-top2` on diffuse got **worse** (`p=0.013` → `0.002`), and the
ledger's compensating win on concentrated arcs over `stateless-top2` did not survive (`p=0.017` →
`0.230`). Quote nothing from this page at 10 seeds.

**The agent is a router, not a filter — both halves now measured.** AT-57 at n=50 keyed
(25 with an outcome, 25 without): **22 / 50** overall, caught 19/25, dismissed **3 / 25**, one
abstention, mean confidence 0.92 on the wrong answers. The 4/10 direction held at five times the
sample. AT-58, measured for the first time and free (it scores the artifact AT-57 already wrote):
**41 / 49 routed to the right team, 0 wrong, 8 declined.** When it commits to a team it is never
wrong; it refuses to route in `complaints` (5 of 12) and `collections` (2 of 7), and `retention` never
appears as a truth team in the sample at all.

**`config_hash` does not cover the code, and that cost $1.50.** The corpus fix changed who crosses
(25 with an outcome → 17, threshold 0.7246 → 0.6655) with the config hash **identical on both sides**,
so the "refuse a mismatched corpus" guard would have blessed it. Manifests now carry `pipeline_sha`
from `corpus.pipeline_fingerprint()`. A run where every case ends `provider_error` now refuses to
write an artifact, and cache mode is in the filename — a failed replay overwrote the keyed AT-57
artifact once, same seed, same hash, same path.

**AWS is real, correct, and inert.** 3 DynamoDB tables with PITR, 3 SQS queues with DLQ redrive, 3
Lambdas on python3.13 from one zip (`8323ff7cd3ca`), a Function URL at `AuthType=AWS_IAM`. `GET
/health` returns 200 in 1.4s cold; everything touching a store returns 500 and neither queue is wired.
Account `859430413223`, **us-east-1**, bucket `s3://agentic-trio`. Coordinates and the IAM ask:
`aws-infrastructure.md`.

**The UI is the product in use, not a dashboard of it.** `#/desk` renders our panel inside a
clearly-labelled stand-in of the client's case-management console — a sandboxed iframe scoped to a
case id is the mechanism four of five real vendors actually ship, so a bounded rectangle with a
visible seam is accurate, not stylistic. The primary user is the **specialist reviewer** (D-030). No
vendor logo, wordmark, brand hex or icon set anywhere; verified.

**One deployment (Northwind), framed as an integration.** Nine pipeline seams, **five of them the
client's own systems** — the screen counts them rather than asserting it. (The prose said "six of
nine" everywhere for weeks; the rendered screen was always right.)

## Blocked, and on what

- **The IAM policy — one inline policy, and the end-to-end path closes.** `zenon-poc-lambda-execution`
  has no SQS, DynamoDB, Bedrock **or CloudWatch Logs** permission, so the deployed Lambdas are not
  merely inert, they are **unobservable**: no log group exists despite 4 invocations on 2026-08-27.
  `iam:PutRolePolicy` was attempted and denied. Policy JSON and the reproducible error lines are in
  `aws-infrastructure.md`, written to be pasted into a ticket.
- **The SSO session expired mid-session and needs a browser.** That is the only thing blocking the
  AT-57 re-run on the fixed corpus (~$1.50, 50 balanced cases at 2,400 customers).
- CodeBuild/CodePipeline blocked by the same `iam:CreateRole` gap. Object Lock on `agentic-trio` is
  OFF and needs an AWS Support case — **A6's ledger guarantee is unaffected**, that is DynamoDB with
  no TTL and no delete path. No SNS, no Budgets, no VPC subnets, so the sweep stays local.

## Next, in order

1. **Re-run AT-57 keyed on the fixed corpus.** Needs `aws sso login` in a browser. The published
   22 / 50 was measured at `47a2be8`, before the corpus fix, and **no longer replays** — that
   provenance is stated in the README rather than hidden, but it should not stay true.
2. **The IAM ticket.** One policy, and the deployed path stops being a diagram.
3. **The team-scoped queue view**, in flight — the last cheap deliverable from the brief.
4. **Arm B**, now priced honestly: **$0.01** on Nova Lite for the reader arm alone, $0.28 to re-run
   both. It is the only item left on `build-plan.md`'s "not measured" list.
5. **Observability (W11, EMF) and the spend ceiling in our own code (W4).** `COST_CAP_PER_CASE_USD`
   is still $0.25, derived from two Sonnet cases; it is now 7.1× the measured Haiku p95.
6. **The UI's write path** — needs a decision about how a static page authenticates against an
   `AuthType=AWS_IAM` Function URL, not just the IAM fix.

## Known-weak, stated rather than hidden

- **Two cheaper arms beat us on the pre-registered stratum**: `stateless-top2` (6–18–6, `p=0.023`) and
  `window3-top2` (5–21–4, `p=0.002`) at 30 seeds. The pattern across everything is that **selectivity
  beats volume** — the arms that beat us keep the best two of what they see. What never-discard buys
  over a three-conversation window is **unproven**, and the honest claim is *aggregation beats no
  aggregation*, not *memory beats detection*.
- **The ledger loses on concentrated arcs** (2–28–0 at 30 seeds). Published; it is a trade.
- **The ledger hands the agent a queue that is 90% false alarm** — 25 of 240 crossings at a 10% budget
  have a real outcome. The recall table never reports this.
- **The lexicon barely works on language it did not write** — 0.0357 strict recall (4 / 112) on real
  CFPB narratives. The **model reader** scores 0.8214 (92 / 112) on the identical gold set at 8× the
  false-positive rate (0.1598 vs 0.0205). `earshot sweep` now prints `reader=offline-lexicon` and
  stamps it into the manifest; the arm comparison is internally valid because every arm eats the
  identical stream, and the README says so above the table.
- **Two of four trajectories can never carry more than 4 signals.** `check_arc_ceiling()` now warns on
  every run rather than only when the flag is passed. Widening the pools moves pass A / pass B overlap
  and therefore the published recall, so it is a deliberate act.
- **The decoys are still planted with replacement**, deliberately: a recurring accumulator decoy makes
  the trap harder, which is biased *against* the ledger. Not a bug; possibly a `decisions.md` entry.
- **The Sonnet investigation figures are provider-historical and no longer replay** (`prompt_sha`
  moved twice). The README says so instead of offering a command that fails.
- **`infrastructure.md` has twelve further contradictions** listed in the 2026-08-28 work-package
  report — §3.4's OpenAI provider section, Appendix A's Sonnet ARNs, the CDK and container-image
  sections against D-024. Each belongs to its own pass.
- **The comparison model is an open delta again**, not retired: the brief asked for a comparison
  *model*, not two vendors, and $0.01 closes it. `build-plan.md` §8 is now the record.
- **No AT ticket covers any of W1–W11.** 45 issues live, 28 In Progress, 0 Resolved.
