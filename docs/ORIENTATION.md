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
detection stays silent throughout. After the fragment pools were widened on 2026-08-30 the offline
lexicon finds only 1 of the 32 new fragments, so at 400 customers **no such customer exists** and the
command says so twice rather than showing you a near-miss and letting you assume. At 3,000 it finds
6 of 150. That honesty branch is deliberate (`cli.py`, and `tests/test_cli.py` pins it) — but it
means the small demo is not a demo any more.

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
exactly the case memory exists for — the full ledger beats every competing strategy, most at
`p<0.001`. That includes two cheap strategies that had beaten it on an earlier version of the corpus.

### The bad news, and it is more important

One of the nine arms is **`random-rank`**: it ignores every signal and ranks customers by a random
number generator. It exists to answer *"does any of this beat chance?"*

**On diffuse arcs, the full ledger versus random ranking is 17–11–2, `p=0.345`.** The ledger is
**not statistically distinguishable from chance** on the stratum it was built for.

Across the whole customer population the ledger ranks **7th of 9 arms**, with recall 0.119 against
chance at 0.109. On **concentrated arcs** (one loud conversation) it loses 0–30–0 to four different
arms — accumulating dilutes a single decisive signal.

### What that means, honestly

- **Aggregating a few conversations beats aggregating one**, when evidence is genuinely spread out.
  That is supported.
- **That *unbounded* memory beats a cheap three-conversation window is unproven.** On the previous
  corpus, the cheap window was *better*.
- **The binding constraint is the reader, not the ranking.** The regex reader finds 1 of 32 fragments
  written without sight of its vocabulary. With a reader that weak, every arm crowds between 0.109
  and 0.138 — a chance floor and a ceiling three points above it. No ranking strategy escapes that.
- **These numbers moved when the corpus changed shape** on 2026-08-30, in both directions. They
  describe the corpus at least as much as the mechanism, and the README says so.

### The agent, measured

| | measured |
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
screen against a stub DOM and crawls the links it emits, another computes WCAG contrast for all 650
colour pairs in both themes.

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
