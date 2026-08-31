# Orientation — start here if you know nothing about this project

**Who this is for:** anyone opening this repository for the first time — a new teammate, a judge, a
reviewer, or you in three months. It assumes **no prior context whatsoever**. Read it top to bottom
in about fifteen minutes and you will understand what was built, why, what is true, what is not, and
where to look next.

Every other document in this repo assumes you already know things. This one does not.

**Last updated 2026-08-30.** Where this page and [`../README.md`](../README.md) disagree about a
number, the README is right — it is the source of record and this page is an explainer.

---

## 1. What is this?

A competition entry for **Zenon Genesis 2026, Track A** (client-facing agentic AI), by a team of
three called **Agentic Trio**. The entry is named **Ear on Every Call**.

It is a working software system, not a slide deck. It runs on your laptop with no API keys.

### The problem it addresses

A bank has millions of customer conversations a year — phone calls, chats, written complaints. A
customer usually tells you something is wrong long before they act on it. Today that signal is scored
inside a single call and then archived.

So a customer can be mildly frustrated in a March chat, raise a complaint in May, and ring in July
about moving their money — and the bank treats all three as unrelated events. **The bank reads every
conversation and remembers no customer.**

### What was built

A **conversation signal layer**:

1. **Read** every conversation (not a sample) and extract risk signals, each with the exact quote
   behind it.
2. **Accumulate** those signals in a standing per-customer ledger that **never discards a weak
   signal** and **re-scores the past** when new conversations arrive.
3. When a customer's accumulated score crosses a review threshold, an **agent investigates** —
   pulling transactions, account state and prior cases through tools — and writes a case file with a
   verdict, an owning team, a recommendation, and cited evidence.
4. A **human decides**. The system has no way to contact a customer at all.

### The one-sentence design rule

> **Code counts and remembers. The model reads and judges.**

Arithmetic — accumulation, decay, thresholds — is plain deterministic Python, unit-tested and
reproducible. Reading natural language and weighing ambiguous evidence is the model's job. A test
enforces the boundary. This is the most important thing to understand about the codebase.

---

## 2. See it working in five minutes

```bash
# Requires uv (https://docs.astral.sh/uv/). It installs Python 3.13 for you.
git clone <repo-url> && cd Genesis_2026
uv sync                                     # install dependencies

uv run pytest                               # the whole test suite (~70s)
uv run earshot demo --customers 3000        # the accumulation story, narrated in your terminal
uv run earshot sweep --seeds 10 --customers 1500   # the evaluation numbers
```

**Why 3,000 and not 400.** The demo needs at least one customer the ledger catches while per-call
detection stays silent throughout. The offline lexicon finds 617 of 2,700 planted signals, so at 400
customers **no such customer exists** and the command says so twice rather than showing you a
near-miss and letting you assume. At 3,000 there are **7 of 132** such customers — and, printed
beside it, **10 of 132** going the other way, which per-call detection catches and the ledger misses.
That honesty branch is deliberate (`cli.py`, and `tests/test_cli.py` pins it) — but it means the small
demo is not a demo any more.

Then open **`ui/index.html`** in a browser. No server, no npm, no network. That is the product:
a reviewer's queue, a case with its evidence, and a live stream showing the ledger filling up.

**Everything above runs with zero API keys and no internet.** That is deliberate — the model
responses behind every published figure are committed to the repo and replayed.

---

## 3. The vocabulary you need

This repo uses precise internal terms everywhere. Learn these eight and the rest of the
documentation opens up.

| Term | What it means |
|---|---|
| **Signal** | One risk indication extracted from one conversation — a type, a confidence, and the verbatim quote it came from |
| **Ledger** | The per-customer store of every signal ever seen. Append-only; nothing is deleted or superseded |
| **Arc** | A customer's storyline across several conversations — evidence deliberately planted so it accumulates |
| **Trajectory** | Which *kind* of arc: `churn_intent`, `financial_distress`, `complaint_escalation`, `life_event`. Each maps to a team |
| **Stratum** | How an arc's evidence is spread. **Diffuse** = thin evidence across many conversations (the case for memory). **Concentrated** = one loud conversation (the case against it) |
| **Crossing** | The moment a customer's accumulated score passes the review threshold — this is what triggers the agent |
| **Plant** | A fragment of text deliberately inserted into a conversation, recorded in the answer key before the text is written |
| **Decoy** | A fragment that *looks* like a signal but is not one. Two kinds: one to fool the extractor, one to fool the accumulator |

**Why the data is synthetic.** Competition rules require it, but there is a stronger reason: the
ground truth is authored *before* the prose is generated, so we know exactly what should have been
found. You cannot measure a miss rate against real data you have not labelled.

---

## 4. How it fits together

```
conversations ──▶ extractor ──▶ ledger ──▶ threshold? ──▶ agent ──▶ case ──▶ human
   (synthetic)     (reads)     (counts)    (plain code)  (judges)  (cited)  (decides)
                      │            │
                 model OR      never discards;
                 26 regexes    re-scores the past
```

**Layer 1 — deterministic, no model, ever.** `corpus.py` generates the data, `memory.py` (183 lines)
does all the accumulation and scoring maths. Reproducible bit-for-bit.

**Layer 2 — the model.** `extract_*.py` reads conversations; `agent/` investigates crossings using
five tools (ledger summary, conversation, transactions, account state, prior cases).

**Layer 3 — the human.** A reviewer queue in `ui/`. Approve, dismiss, or route.

### Two readers, and the difference matters enormously

| Reader | Needs a key? | Finds real signal | False positives |
|---|---|---|---|
| **Offline lexicon** (26 regexes) | No | **0.0357** (4 / 112) | 0.0205 (10 / 488) |
| **Claude Haiku 4.5** on Bedrock | Yes | **0.8214** (92 / 112) | 0.1598 (78 / 488) |

Measured on 112 real customer complaints from the US CFPB public database. The regex reader exists so
the repo runs with no keys — it is **not** a serious reader, and every table says which one produced
it.

---

## 5. What is actually true — the results

**This is the part most projects get wrong, so read it carefully. This one publishes its losses.**

The evaluation runs 9 different "arms" — competing strategies for deciding which customers to review
— over 30 independent datasets, paired seed by seed, with an exact statistical test. All arms eat the
identical signal stream, so the comparison is fair regardless of which reader produced it.

### The good news

On **diffuse arcs** — evidence spread thin, nothing alarming in any single conversation, which is
exactly the case memory exists for — the full ledger beats **both** bounded-memory arms **30–0–0** at
`p<0.001`, under both tie-break rules. The two arms that never discard a weak signal (`full-ledger`
and `dumb-ledger`) rank **first and second of nine** on this stratum. That is never-discard earning
its place, and it is the entry's originality claim measured rather than asserted.

### The bad news, and it is more important

One of the nine arms is **`random-rank`**: it ignores every signal and ranks customers by a random
number generator. It exists to answer *"does any of this beat chance?"*

**On diffuse arcs, the full ledger versus random ranking is 18–8–4, `p=0.076`.** The ledger is
**not statistically distinguishable from chance** on the stratum it was built for.

Across the whole customer population the ledger ranks **8th of 9 arms** at the 10% budget, with recall
0.115 (665 / 5796) against chance at 0.113 (657 / 5796). On **concentrated arcs** (one loud
conversation) it loses 0–30–0 to three different arms and does not beat chance there either
(16–12–2, `p=0.572`) — accumulating dilutes a single decisive signal.

**The pre-registered headline died.** `full-ledger` vs `stateless-max` on diffuse recall was 29–0–1
`p<0.001`; on the rebuilt corpus it is **15–13–2, `p=0.851`**. The cause is measured: the old corpus
had crippled that opponent. It is re-registered against `window3-top2` and bound to a chance gate the
entry currently fails — D-031, and the dead row stays in every table permanently.

### What that means, honestly

- **Won on diffuse: unbounded memory beats a cheap three-conversation window.** 30–0–0, `p<0.001`,
  both tie-break rules. This page called it *unproven* for weeks; it is proven on this stratum.
- **Lost on concentrated: 1–28–1** to the same bounded window, and **not proven whole-portfolio**
  (9–17–4, `p=0.169`). The honest summary is all three directions, not the first one.
- **Retracted: "aggregating a few conversations beats aggregating one."** The arm that aggregates one
  now ties us on diffuse and beats us on the whole portfolio. The rebuilt corpus refutes it.
- **Our own ablation floor beats us on diffuse** — `dumb-ledger`, every mechanism off, 18–7–5
  `p=0.043`. Under a randomised tie-break it is 13–11–6 `p=0.839`, because 70.8% of that arm's queue
  is decided alphabetically. Both records are published, always, and the deterministic one stays the
  default.
- **The binding constraint is the reader, not the ranking.** The regex reader finds **617 of 2,700**
  planted signals, and on our own corpus it leaves two of four desks receiving no case at all. With a
  reader that weak, every arm crowds between 0.113 and 0.145 — a chance floor and a ceiling three
  points above it. No ranking strategy escapes that.
- **These numbers moved when the corpus was rebuilt** on 2026-08-31, in both directions. They
  describe the corpus at least as much as the mechanism, and the README says so.

### The agent, measured — and corpus-historical

**Everything in this table was measured on 2026-08-28 / 2026-08-29, on the corpus that preceded the
2026-08-31 rebuild.** It is stale. It has not been re-measured because the AWS SSO token is expired
and LLM spend is stopped — a decision, not a technical block. Read it as "what the agent did on the
previous corpus", never as current.

| | measured (corpus-historical, pre-rebuild) |
|---|---|
| Verdict accuracy | **22 / 50** — it escalates rather than discriminating |
| Dismissing false alarms | **4 / 25** — and 0.86 mean confidence when wrong |
| Routing to the right team | **36 / 49** correct, 2 wrong, 11 declined |
| Evidence citations resolving first try | **50 / 50** |
| Cost per investigation | **$0.0295** |

So the agent today buys **routing and an audit trail, not filtering**. That is written down rather
than hidden.

---

## 6. Where to look next

Read in this order depending on what you want:

| You want to… | Read |
|---|---|
| See the numbers with full method | [`../README.md`](../README.md) — **the source of record** |
| Understand the system's shape | [`architecture/architecture.md`](architecture/architecture.md) |
| Know why something is the way it is | [`ops/decisions.md`](ops/decisions.md) — every settled choice, and what was rejected |
| Know what state the project is in today | [`ops/state-of-play.md`](ops/state-of-play.md) |
| Know what is left to build | [`architecture/build-plan.md`](architecture/build-plan.md) |
| Understand the disciplines and why they exist | [`ops/working-agreements.md`](ops/working-agreements.md) — each rule was bought with a real mistake |
| Find any file | [`INDEX.md`](INDEX.md) |
| Pitch it | [`impact/onepager-use-case.md`](impact/onepager-use-case.md) and its two siblings |

**Commit messages carry the reasoning.** `git log --grep=<topic>` answers "did we already try this?"
better than any prose file, and it never goes stale.

---

## 7. The parts most likely to surprise you

**The tests are unusually load-bearing.** 827 collected, 817 passing and 10 deliberately
skipped with a stated reason. Several exist because a specific mistake was
made once and must never recur — for example, a test that scans every module to prove the extractor
*cannot* import the answer key, and a test that fails if the UI dims a sub-threshold row, because
dimming retained evidence would draw exactly the behaviour this product inverts.

**The UI has no build step.** Plain HTML/CSS/JS opened from `file://`. A judging room with no wifi and
a laptop with no toolchain can still see the product. Two automated gates check it: one renders every
screen against a stub DOM and crawls the links it emits, another computes WCAG contrast for all **650**
colour pairs across 17 routes in both themes.

**Documented failures are kept, not deleted.** A keyed model run on 2026-08-30 cost **$12.32 and
produced no artifact** — it hit a spend ceiling half way, and the resume re-bought reads because a
code commit between the two halves invalidated the cache keys. It is written up in `ops/progress.md`
with the lesson, because a failure with a cause is reusable and a deleted failure is not.

**The AWS deployment is real but inert.** Tables, queues and Lambdas are deployed and correct. One
missing IAM policy means every endpoint touching a store returns 500 — and the Lambdas have no log
group, so they are unobservable too. The repo says this plainly rather than showing an architecture
diagram and implying it runs.

**Nothing here can contact a customer.** Not disabled — absent. No route, button or handler anywhere
sends anything to anyone. Human-in-the-loop is enforced by the absence of the capability.
