# State of play

**Updated 2026-08-29.** Rewritten in place every working session — **never appended to**. If
something will not fit, it belongs in `decisions.md` (a choice), `working-agreements.md` (a rule), or
Jira (work). Anything historical belongs in git.

**Fresh session, read in this order:** this file → `decisions.md` → `working-agreements.md` →
`../../README.md` → `../architecture/architecture.md`. Then `../architecture/infrastructure.md` for the
AWS design and `aws-infrastructure.md` for what is actually provisioned.

---

## Where we are

The system runs end to end with **zero API keys**: dataset generation → extraction → per-customer
ledger → investigator agent producing case files with cited evidence → a UI that opens from disk.
**817 tests**, ruff clean, separation guard over **44 modules** across `src/` and `tools/`,
**30 UI routes**, and a contrast gate over **634** rendered colour pairs.
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

**The retention desk was dead, and the model reader revives it (2026-08-29).** The offline lexicon
finds churn evidence in 0.43 of the conversations where it was planted against 0.67–0.86 for the
other three families. Corroboration is cross-conversation, so **0 of 325 churn customers ever
crossed** — the brief's *lead* team received nothing, ever. Measured over the same 288 conversations
(`tools/reader_coverage.py`, $0.4260): the model reader takes churn coverage to **0.79** and **9 of
20** churn customers now reach Retention.

**And it costs us collections**: the model finds *less* planted distress evidence than 26 regexes do
(0.42 against 0.74) and Collections crossings fall 4 → 1. Choosing a reader is an operational
decision about which desk you under-serve, not a procurement decision about which model is best. The
model-arm crossings are an **upper bound** — the threshold is a top-K cut over the *offline* reader's
ranking, held fixed across arms because deriving the model's own costs $13.85.

**The agent is a router, not a filter — both halves now measured.** AT-57 at n=50 keyed
(25 with an outcome, 25 without): **22 / 50** overall, caught 18/25, dismissed **4 / 25**, one
abstention, mean confidence 0.86 on the wrong answers. Re-run on the post-fix corpus and **it
replays** — verified before publishing. AT-58 routing, free (it scores the artifact AT-57 already
wrote): **36 / 49 correct, 2 wrong, 11 declined**, both wrong routes unmoored from the evidence on
hand rather than near-misses. `retention` has no row at all, for the reason above.

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

**The brief's three team views ship, as four.** `#/desk/team/<slot>` filters the reviewer queue,
21 routes to 30. The slot is in the URL and the label comes from the tenant map at render (D-029,
display-only). **`none` is a first-class bucket labelled "Not routed", listed at zero** — it is the
agent declining to choose, which it did 8 of 49 times, and those are the cases a reviewer must not
lose. A team with no cases still appears and still opens. Retention survives by name, Risk and
Compliance splits three ways, and **Commercial has no equivalent** — said on the screen rather than
papered over with an invented team.

**One deployment (Northwind), framed as an integration.** Nine pipeline seams, **five of them the
client's own systems** — the screen counts them rather than asserting it. (The prose said "six of
nine" everywhere for weeks; the rendered screen was always right.)

## Blocked, and on what

- **The IAM policy — one inline policy, and the end-to-end path closes.** `zenon-poc-lambda-execution`
  has no SQS, DynamoDB, Bedrock **or CloudWatch Logs** permission, so the deployed Lambdas are not
  merely inert, they are **unobservable**: no log group exists despite 4 invocations on 2026-08-27.
  `iam:PutRolePolicy` was attempted and denied. Policy JSON and the reproducible error lines are in
  `aws-infrastructure.md`, written to be pasted into a ticket.
- **Nothing keyed is blocked.** SSO was re-minted 2026-08-29 and every keyed item on the list ran.
  Note the trap: `aws sts get-caller-identity` succeeds from a cached role credential while the SSO
  token underneath is dead. Probe Bedrock, not STS.
- CodeBuild/CodePipeline blocked by the same `iam:CreateRole` gap. Object Lock on `agentic-trio` is
  OFF and needs an AWS Support case — **A6's ledger guarantee is unaffected**, that is DynamoDB with
  no TTL and no delete path. No SNS, no Budgets, no VPC subnets, so the sweep stays local.

## Next, in order

1. **The IAM ticket** — the only hard blocker left. One inline policy and the deployed path stops
   being a diagram. It now also needs `logs:*`: the Lambdas are unobservable, not merely inert.
2. **Arm B**, priced honestly: **$0.01** on Nova Lite for the reader arm alone, $0.28 to re-run
   both. The last item on `build-plan.md`'s "not measured" list. `extractor_cache_path()` is now
   per-model, so it cannot append into the cache behind the published reader figures.
3. **Extend the reader-coverage sample.** n=20 per trajectory is a direction with denominators;
   samples nest, so `--per-trajectory 40` re-reads nothing and costs only the delta (~$0.45).
   The collections regression is the half most worth a bigger denominator.
4. **Observability (W11, EMF).** The spend ceiling (W4) is done — the cap is re-derived and the
   CloudWatch alarm now derives from it rather than sitting at twice its value.
5. **The UI's write path** — needs a decision about how a static page authenticates against an
   `AuthType=AWS_IAM` Function URL, not just the IAM fix.

## Known-weak, stated rather than hidden

- **The reader choice is a trade between desks, not an upgrade.** The model reader takes Retention
  from 0 crossings to 9 of 20 and drops Collections from 4 to 1. One dataset, n=20 per trajectory.
- **The lexicon's churn coverage (0.43) is a pass-B gap and stays unfixed.** Widening those cues to
  close a gap found by measuring against the answer key is exactly the pass-B-toward-pass-A tuning
  the build rules forbid. It is published instead.
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
- **The recorded document screens (`ui/data.js`) are still the offline rule engine**, printed on
  screen. `#/desk`, `#/desk/call` and `#/stream` are keyed Haiku. Regenerating `data.js` from a keyed
  investigate run is cheap and not yet done.
- **`infrastructure.md` has twelve further contradictions** listed in the 2026-08-28 work-package
  report — §3.4's OpenAI provider section, Appendix A's Sonnet ARNs, the CDK and container-image
  sections against D-024. Each belongs to its own pass.
- **The comparison model is an open delta again**, not retired: the brief asked for a comparison
  *model*, not two vendors, and $0.01 closes it. `build-plan.md` §8 is now the record.
- **No AT ticket covers any of W1–W11.** 45 issues live, 28 In Progress, 0 Resolved.
