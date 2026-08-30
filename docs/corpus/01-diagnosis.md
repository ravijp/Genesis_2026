# Phase 1 — independent diagnosis of the synthetic corpus

**Written blind on 2026-08-31, before reading any prior findings.** Not revised afterwards.

Method: generated the shipped corpus at the default seed (`RunConfig(seed=20260809)`, 400 customers,
1,400 conversations, 22,114 turns, 973 seeded signals), dumped every arc in day order, read ~60
complete transcripts across all four trajectories and all three channels, then wrote measurement
scripts for every claim below. Counts reproduce with
`uv run python <script>` against `earshot.corpus.generate`.

Denominators used throughout: **1,400 conversations · 22,114 turns · 11,378 customer turns ·
10,736 agent turns · 973 planted signals · 400 customers**.

---

## The one-line verdict

The *plan* is good and the *prose* is not written — it is sampled. Ten agent sentences are dealt at
random into 10,736 agent turns with no reference to what the customer just said, which is why 864 of
973 planted signals (88.8%) are answered with a non-sequitur. Nothing in the generator looks at the
previous conversation, so an arc is N independent scenes, not one relationship.

---

## Ranked by demo damage

### 1. The agent replies to distress with a non-sequitur — 864 / 973 planted signals (88.8%)

`_render_conversation` builds every agent turn as `rng.choice(FILLER_AGENT)`. FILLER_AGENT holds
**10 strings**. It cannot see the customer turn it follows.

Measured: **864 / 973 (88.8%)** of planted signals are followed by an agent line drawn from the nine
generic fillers. Restricting to the loudest evidence — the quotes that end up on a case screen —
**77 / 85 (90.6%)** of plants with mass ≥ 0.80 get a generic reply.

The three that will end a demo:

```
CUST-0333-C0  (life_event, mass 0.85)
  customer: My husband passed away in June and I'm sorting out the accounts.
  agent   : Let me check that with the relevant team, bear with me.
  customer: I've lost the card, I think it's in the car actually.
  agent   : Thanks for holding, I appreciate your patience.
  agent   : Glad we got that sorted, take care.

CUST-0238-C1  (life_event, mass 0.85)
  customer: My husband passed away in June and I'm sorting out th- accounts.
  agent   : Just so you know, this call may be recorded for training purposes.

CUST-0000-C4  (churn_intent, mass 0.95)
  customer: I want to close the account, this week.
  agent   : That's now updated on our side.
```

The bereavement one is not merely unrealistic. In a UK retail-banking room it reads as a **Consumer
Duty / vulnerable-customer failure** — a bereavement disclosure met with the recording notice and
closed with "Glad we got that sorted, take care." Any judge with FCA exposure will stop the demo
there and the conversation will be about our agent handling, not our accumulation thesis.

These lines are already on screen: `ui/data.js` contains "That's now updated on our side." 21 times,
"Thanks for holding, I appreciate your patience." 25 times, and the recording notice 27 times.

### 2. Sixteen distinct agent sentences across 10,736 agent turns

| pool | size | turns it fills | share |
|---|---|---|---|
| FILLER_AGENT | 10 | 8,856 | 82.5% of agent turns |
| OPENINGS | 3 | 940 | 8.8% |
| CLOSINGS | 3 | 940 | 8.8% |
| **distinct agent surface strings, whole corpus** | **16** | **10,736** | — |

Each of the ten fillers lands 841–921 times — a flat 7.8%–8.6% each, exactly as uniform sampling
predicts. **1,082 / 1,400 conversations (77.3%)** repeat an agent line verbatim inside the same
conversation; the worst says one line five times (`CUST-0267-C2`: the recording notice ×5).

Customer filler is thinner than it looks: 15 base strings, and the 742 distinct customer surface
strings are almost all ASR-mangled variants of those 15. **899 / 1,400 conversations (64.2%)** repeat
a customer line verbatim; **166 / 1,400** say one line three or more times. `CUST-0388-C1` asks
"Can you read me the last three transactions?" four times in one call.

### 3. Channel is decorative — the three channels are the same object with a label

`_render_conversation` branches on channel exactly once, to decide whether to add an opening and a
closing. Everything else is identical.

- **129 / 450 chat conversations (28.7%)** open with *"Thank you for calling, you're speaking with
  Sam, how can I help?"*
- *"this call may be recorded for training purposes"* appears **591 times inside chat and complaint**.
- *"Thanks for holding, I appreciate your patience."* appears **575 times inside chat and complaint** —
  there is no hold in a web chat.
- **460 / 460 complaint documents** have interleaved agent turns and more than one customer turn. A
  written complaint is being rendered as a live two-party dialogue with no greeting.
- ASR noise (word drops and clipping) is applied at the same 2% rate to typed channels:
  **1,428 / 7,453 (19.2%)** of chat and complaint customer turns are ASR-mangled, versus
  **814 / 3,925 (20.7%)** in call. A *typed* chat message reading `"D- I need to tell you if I'm going
  abroad these days?"` is self-evidently machine-made.

### 4. ASR noise mangles the evidence quotes the product exists to show

Noise is applied to the planted fragment too. **212 / 973 (21.8%)** of planted signals ship a mangled
evidence quote; **19 / 85 (22.4%)** of the high-mass ones do. These are the strings the case screen
and the retro re-score table print as the load-bearing quote:

```
seeded : I can't make the payment this month, I just can't.
shipped: can't make the payment this month, I just                     (CUST-0020-C0)

seeded : I'm retiring at the end of the month, so I need to talk through what happens to the pension payments.
shipped: I'm retiring at the end of so I need to talk through what happens to the pension payments.   (CUST-0146-C4)
```

Noise on filler is defensible realism. Noise on the quote we hold up as proof reads as a bug.

### 5. Turn structure is not conversation shape

- **1,106 / 1,400 (79.0%)** conversations contain a run of 2+ consecutive customer turns with no agent
  reply (1,790 such runs). Cause: the agent reply is emitted with probability 0.75.
- **740 / 1,400 (52.9%)** contain 2+ consecutive agent turns — usually a filler immediately followed
  by the closing.
- The security question — *"Can I take the first and third character of your memorable word?"* — fires
  869 times and is at turn index ≤ 2 only **88 times (10.1%)**. **161 / 1,400** conversations ask it
  twice or more. Verification happens once, at the start, in every contact centre on earth.
- The recording notice fires 893 times and is in the first three turns only **135 times (15.1%)**.
- The customer never states a reason for contact. Every conversation opens with the agent, then the
  customer asks an unrelated question, and nothing is ever resolved.
- Median 16 turns, max 26, median 10 words per turn — long enough that the emptiness is obvious.

### 6. The planted text contradicts the arc it is planted into

Twelve fragments assert a prior contact with the bank. **43 / 152 (28.3%)** of their plantings land in
the customer's **first** conversation, where no prior contact exists.

- *"This is the fourth time I've called about this and nobody has fixed it."* — planted **9 / 10** times
  into an arc where the customer has had fewer than four conversations. `CUST-0015` says it in
  conversation 1 of 2.
- *"I've been passed to four different people today"* — 5 plantings; no conversation in the corpus has
  more than one agent.
- Seasonal words have no calendar anchor: *"back in the spring"* is planted on days 40–142, *"passed
  away in June"* on days 9–109, *"made redundant in March"* on days 10–119, of a 180-day horizon with
  no epoch date. Any two of these in one arc will contradict each other.

### 7. The same sentence is the flagship evidence for many customers

56 planted fragments cover 973 plantings. **298 / 303 customers (98.3%)** whose arc carries any signal
share their highest-mass quote with at least one other customer. The most-reused:

| fragment | plantings | text |
|---|---|---|
| `le-w7` | 47 | "Just updating a few details, nothing major, my circumstances have shifted a bit this year." |
| `ci-w7` | 40 | "No, nothing wrong, just tidying up which accounts I actually still use." |
| `le-w6` | 34 | "I've been going back and forth to appointments with my dad a lot lately..." |
| `ce-w7` | 34 | "I did post something about it, just venting really, on the socials." |

A judge scrolling the queue sees the identical quote on two different cases. That reads as a
copy-paste bug even though it is a small-pool artefact.

### 8. There is no inter-conversation coherence, at all

`_render_conversation(rng, cfg, conversation_id, customer_id, channel, day, plant)` takes no prior
conversation and no arc state. Nothing can reference anything.

Cross-reference vocabulary across all 22,114 turns: `"I called"` 0 · `"when I rang"` 0 · `"as I said"`
0 · `"you said"` 0 · `"last time"` 12 · `"last week"` 12 · `"reference number"` 12 · `"promised"` 5.
Every one of those 41 hits is inside a planted fragment's fixed text, not a generated reference.

Consequence: an arc reads as N unrelated scenes with the same customer id. No promise is made and
broken. No agent picks up where the last one left off. Nothing gets worse. The gap between
conversations (median 30 days, mean 37, 20.3% of gaps ≥ 60 days) is never acknowledged — which is
exactly the thing the entry's whole thesis is about.

### 9. A correctness defect, not just a realism one: duplicate fragments on the decoy paths

`_nearest_fragment` was fixed on 2026-08-28 to plant without replacement, because a repeated sentence
made `memory._raw()` count `n_conversations = 2` and pay a **cross-conversation corroboration bonus for
one utterance copied twice**. The docstring in `corpus.py` calls this "manufacturing the exact
mechanism this system claims to measure."

The two decoy paths still use `rng.choice(...)` **with replacement**:

```python
elif stratum is Stratum.DECOY_EXTRACTOR:
    ...  plants[i] = rng.choice(DECOYS_EXTRACTOR)
elif stratum is Stratum.DECOY_ACCUMULATOR:
    plants[i] = rng.choice(DECOYS_ACCUMULATOR)
```

Measured: **33 / 400 customers** carry the same fragment twice or more in one arc — 38 duplicate
plantings, **17 decoy_accumulator and 16 decoy_extractor, 0 on the real arcs**. `CUST-0002` says
*"Cashflow's a bit lumpy this quarter, it always is."* verbatim on day 175 and again on day 178.

The direction of the bias is against the ledger (decoys score higher, so false positives rise), which
is the safe direction — but it is still a manufactured corroboration bonus on 33 customers, and it is
the defect the codebase has already written a paragraph about fixing elsewhere.

### 10. Cosmetic, but a judge will notice

Every named agent is **Sam** (299 conversations). Real contact-centre transcripts show a different
name per contact, and the name is one of the strongest cheap realism cues.

---

## What is RIGHT — do not throw this away

1. **Plan-before-prose is correct and load-bearing.** The answer key is authored by
   `_dirichlet` → `_nearest_fragment` before a word of text exists. That is the property that makes
   every published number honest, and any rewrite must preserve it exactly.
2. **The planted fragments themselves are good.** They are genuinely British, genuinely retail-banking,
   and the weak ones read as unremarkable in isolation — which is the whole design requirement.
   *"My salary goes into the other one now, it's just easier."* and *"I keep meaning to sort out
   switching, it's just never the week for it."* are better than most hand-written eval data. The
   **strength ladder is calibrated**: 0.20–0.34 weak, 0.50–0.63 medium, 0.83–0.95 strong, and reading
   them in order the ladder feels right.
3. **The two decoy families are a genuinely sophisticated idea.** Extractor-targeted decoys
   (third-party attribution, hypotheticals, past-tense-resolved) and accumulator-targeted decoys
   (real weak signals that never amount to anything) are the two failure modes, separated. Most
   synthetic benchmarks have neither.
4. **Fragments are planted without replacement on the real arcs**, with the failure documented in a
   docstring that explains exactly what it cost. That is the standard the decoy paths should be held to.
5. **Strata are labelled from generation parameters, never from what a baseline detects.** The
   docstring is explicit about why. This is the thing that stops the headline result being circular.
6. **Outcomes are drawn stochastically from latent risk** (base 3%, gain 0.18), so prediction is a real
   task and a few null customers churn by chance. The `financial_state` / `latent_risk` split, so the
   account tool is not an oracle, is a subtle and correct piece of design.
7. **Conversation days are ordered and spread**: median gap 30 days, 20.3% of gaps ≥ 60 days, max 158.
   The *timeline* is realistic even though the *text* does not know about it.
8. **`check_arc_ceiling` and `pipeline_fingerprint` exist and are deliberately over-sensitive.** The
   pool-widening has landed — all four trajectory pools now hold 14 fragments, so the shipped default
   max of 5 is comfortably under the ceiling and the "two of four trajectories cap at 4" warning in
   `handover.md` is now **stale**. `check_arc_ceiling` no longer fires at the shipped default.

---

## Structurally odd things about how arcs unfold

- **Every arc customer has a signal in 100% of their conversations.** Measured: 210 arc customers,
  730 conversations, **0 silent (0.0%)**; **210 / 210 arc customers (100.0%)** are signal-in-every-
  conversation. So "diffuse" means *a weak signal every single time*, never *silence between signals*.
  Real customers go quiet for months. Silence is itself evidence, and the corpus contains none of it.
  - By contrast `decoy_extractor` is 104 / 257 silent (40.5%) — because that path rolls
    `rng.random() < 0.6` — and `null` is 323 / 323 silent (100%). So the generator *can* produce
    silence; the arc path just never asks for it.
  - This also makes the accumulation task easier than reality: every conversation is a scoring event.
- **`decoy_accumulator` is 0 / 90 silent** for the same reason — it plants unconditionally.
- **Arc mass is Dirichlet-split but the fragment is chosen by nearest strength**, so a DIFFUSE arc
  reliably draws four fragments in the 0.20–0.35 band and a CONCENTRATED arc draws one loud one plus
  filler-strength ones. This is exactly as designed, and it means the *evidence ladder* inside an arc
  never has a reversal — nobody gets better and then worse. Real distress arcs oscillate.
- **Signals never escalate in kind, only in strength.** A churn arc is four churn quotes. Real churn
  arcs start as a complaint, become a fee question, then a switching question. Cross-type arcs do not
  exist: `trajectory` is a single `SignalType` for the whole arc.
- **The outcome day is `days[-1] + rng.randint(10, 60)`** — always after the last conversation, never
  between two of them. So no customer ever churns and then keeps talking to us.

---

## What I would fix, in order

1. Make agent lines responsive to the customer turn they follow. Highest damage, and it is free —
   the extractor reads only customer turns.
2. Make channel real: no "Thank you for calling" in chat, no hold in chat, no ASR clipping in typed
   channels, complaint as a single narrative document.
3. Stop applying ASR noise to the planted fragment.
4. Fix conversation shape: verification once at the start, recording notice at turn 0–1, no
   customer-customer runs, a stated reason for contact, fewer turns.
5. Give arcs silence — some conversations with no signal at all.
6. Give arcs memory — a reference to the last contact, a promise made and broken.
7. Plant back-reference fragments only where the arc supports them.
8. Plant decoys without replacement, matching the arc path.
