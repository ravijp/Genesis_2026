# Phase 5 — Phase A implemented and verified

**2026-08-31 · worktree `/c/tmp/real-transcripts`, branch `wp/real-transcripts`.**
Files changed: `src/earshot/corpus_lexicon.py`, `src/earshot/corpus.py`, `tests/test_corpus.py`.
Zero API spend. Nothing outside the worktree touched.

---

## What was built

Two things, not one.

**1. The three tuples rewritten at their exact current lengths.** `FILLER_AGENT` 10 → 10,
`OPENINGS` 3 → 3, `CLOSINGS` 3 → 3. `FILLER_CUSTOMER` untouched — it is customer speech and one
character would move every published number.

**2. A responsive selection layer, which turned out to be free.** The prior report concluded the
ceiling was "ten rewritten strings". It is not. I tested three variants against a full invariance
harness and the real constraint is narrower and much more useful:

| variant | customer turns moved (3 seeds × 400) |
|---|---|
| rewrite the 10 strings, keep the draw | **0 / 33,663** |
| **arbitrary text from the preceding customer turn + channel, keep the draw** | **0 / 33,663** |
| resize the tuple 10 → 14 | 11,371 / 11,378 at seed 1, plus 1,400 → 1,435 conversations |
| replace the draw with a deterministic pick | 11,096 / 11,378, plus 1,400 → 1,393 conversations |

So the rule is: **`rng.choice(FILLER_AGENT)` must still execute on a length-10 tuple.** What you do
with the value afterwards is unconstrained. `_render_conversation` already had `channel` and `plant`
in scope, so the reply can be keyed on the exact fragment that was planted.

What shipped:

- `AGENT_REPLIES_TO_SIGNAL` — **67 / 67 fragments** (56 plants + 6 extractor decoys + 5 accumulator
  decoys), two authored variants each.
- `AGENT_REPLIES_TO_FILLER` — all **15** filler lines, two variants each, keyed on the *pre-ASR*
  string (the draw is hoisted in `corpus.py` so the clean text reaches the map).
- `COMPLAINT_REPLIES_BY_TYPE` — a written case-handler voice, used on the signal turn of a complaint
  when the fragment's strength is ≥ 0.50.
- `CHAT_OPENINGS` / `CHAT_CLOSINGS` — index-matched to the call pools, selected by the *position* of
  the already-drawn value, so the draw picks and the channel decides the wording.
- Variety comes from `_variant()`, which indexes on the burned draw. Ten filler lines over two
  variants is an exact 5/5 split and consumes no randomness.

### What the wording is grounded in

Cited inline in `corpus_lexicon.py`, all read 2026-08-31:

- **FCA, "Delivering good outcomes for customers in vulnerable circumstances"**, 2025-03-07
  (updated 2025-12-03), OGL v3.
  Documented *good* practice — record the disclosure so the customer is not asked twice; keep a
  consistent named person; do not restart a standard process over a disclosed need. Documented
  *poor* practice — failing to record an accessibility need so the customer repeats it; rigid
  process adherence after disclosure; a seven-month delay contacting a bereaved customer. The
  bereavement reply is written directly against that last one.
- **FCA Financial Lives 2024** (2025-05-16): 49% of UK adults (26.4m) have a vulnerability
  characteristic and only ~4 in 10 have ever disclosed it. Every distress and life-event reply
  thanks the customer for saying it, because rewarding the disclosure is the only thing that moves
  that second number.
- **Taskmaster-1** spoken half (CC BY 4.0): 5,507 dialogues where trained call-centre operators
  played the agent, disfluencies transcribed as spoken. Turn mechanics — one move per turn,
  acknowledge → clarify → act → confirm — follow it.

**No sentence is copied from any source.** What crossed is a documented behaviour or a turn pattern.

---

## Verification — pasted output

### 1. `uv run ruff check src tests tools`

```
All checks passed!
```

### 2. `uv run pytest -p no:warnings`

```
........................................                                 [100%]
827 passed, 5 skipped in 68.01s (0:01:08)
```

823 before, 827 after — the four new guards. Nothing was modified to make anything pass.

### 3. The byte-identical proof, 3 seeds × 400 customers

`snapshot.py` captures every customer turn keyed by (conversation, index); every `SeededSignal`
field; every `CustomerTruth` field; each conversation's channel, day and **speaker sequence**; every
`ExtractedSignal` the offline reader emits; and every customer's ledger score with its per-entry
`contribution_now` and `score_at_write`. `compare.py` exits non-zero on any movement.

```
wrote after_V5.json: 3 seeds, 33663 customer turns, 3049 seeded signals, 998 extracted signals
seed 20260809:
  OK   config_hash     identical (1 items)
  OK   n_conversations identical (1 items)
  OK   customer_turns  identical (11378 items)
  OK   speaker_seqs    identical (1400 items)
  OK   conv_meta       identical (1400 items)
  OK   seeded          identical (973 items)
  OK   truths          identical (400 items)
  OK   extracted       identical (304 items)
  OK   scores          identical (400 items)
seed 20260810:
  OK   customer_turns  identical (10913 items)   [... all nine OK ...]
seed 20260811:
  OK   customer_turns  identical (11372 items)   [... all nine OK ...]

RESULT: IDENTICAL - nothing that must not move has moved
```

### 4. `uv run earshot sweep --seeds 10 --customers 400`

```
reader=offline-lexicon   10 seeds x 400 customers   review budget 10%   (6s)
arm                  recall   stdev  min seed  max seed    hits/outcomes   diffuse  diffuse hits/n
dumb-ledger           0.104   0.040     0.051     0.179           53/509     0.147          30/204
random-rank           0.116   0.043     0.071     0.179           59/509     0.142          29/204
full-ledger           0.088   0.033     0.048     0.128           45/509     0.108          22/204
stateless-top3        0.086   0.039     0.016     0.161           44/509     0.093          19/204
stateless-max         0.128   0.040     0.058     0.191           65/509     0.078          16/204
long-context-3        0.083   0.033     0.040     0.143           42/509     0.078          16/204
hybrid                0.084   0.053     0.016     0.188           43/509     0.074          15/204
stateless-top2        0.084   0.030     0.032     0.143           43/509     0.069          14/204
window3-top2          0.084   0.030     0.032     0.143           43/509     0.069          14/204

SWEEP DIFF vs pre-change: before=238 lines after=238 lines differing=0
>>> EVERY SWEEP NUMBER IDENTICAL <<<
```

The pre-change sweep was captured before a line was edited and diffed after, normalising only the
git-sha and elapsed-time strings. 238 non-blank lines, zero differ.

### The one thing that did move

`pipeline_fingerprint()`: `fd58c7642e12` → `3da5f8449b25`. Expected and correct — it hashes source
bytes and is deliberately over-sensitive. `artifacts/runs/sweep-30x1500-9ddd6674c388.json` carries
the old stamp at `manifest.pipeline_sha`, so `tools/routing_accuracy.py` will now warn on it. **Its
numbers are still right**; it needs a re-stamp, which is a 6-minute offline re-run, not a
re-derivation.

---

## Measured before / after

| | before | after |
|---|---|---|
| Distinct agent surface strings | **16** | **175** |
| Most frequent agent line, share of agent turns | 8.6% | **2.7%** |
| Planted signals answered with a generic non-sequitur | **864 / 973 = 88.8%** | **0 / 973 = 0.0%** |
| High-mass plants (≥0.80) answered generically | 77 / 85 = 90.6% | 0 / 85 |
| Conversations repeating an agent line verbatim | 1,082 / 1,400 = 77.3% | **543 / 1,400 = 38.8%** |
| …of which the customer also repeated (agent correctly repeating an answer) | — | 477 / 543 |
| …genuine agent-side repetition | — | **66 / 1,400 = 4.7%** |
| Chat opening with call language | 129 / 450 = 28.7% | **0 / 450** |
| Telephone wording in a typed channel | 1,166 occurrences | **0** (guarded by a test) |
| Named agents | Sam ×299 | Priya 299 / Daniel 320 / Marcus 321 |
| Complaint plants answered with a written case-handler voice | 0 | 324 (strength ≥ 0.50 only) |

### The three demo-killers

```
CUST-0333-C0   customer: My husband passed away in June and I'm sorting out the accounts.
  before  agent : Let me check that with the relevant team, bear with me.
  after   agent : I'm so sorry for your loss. There's no rush from our side. I'll note it now so
                  nobody asks you to explain it twice.

CUST-0000-C4   customer: I want to close the account, this week.
  before  agent : That's now updated on our side.
  after   agent : I can do that. I'd rather not until I understand why, though. What's happened?

CUST-0015-C0   customer: This is the fourth time I've called about this and nobody has fixed it.
  before  agent : Of course, let me pull that up for you.
  after   agent : Then I'm not passing you on again. I'll own this one and come back to you myself
                  with an answer.
```

And the decoys are handled correctly, which matters more than it looks — an agent who escalates a
non-signal argues against the product on our own screen:

```
CUST-0009-C0   customer: A friend of mine lost her job and the bank wa- awful to her.   [DECOY]
  after   agent : I'm sorry to hear that. It's not how it should go.
```

### Two flaws I introduced and then fixed

Reporting these because both were mine and both were found by measuring rather than by reading.

1. **A new, worse monoculture.** Routing every complaint filler turn to the written acknowledgement
   produced **1,290 copies of one sentence — 12.0% of every agent turn in the corpus**, against 8.6%
   for the worst offender before. Fixed by using the substantive filler replies in all three
   channels and reserving the written voice for the signal turn. Top line fell to 2.7%.
2. **The agent over-reacted to weak signals.** Keying the written acknowledgement on signal *type*
   alone made the case handler answer *"I mentioned it to someone on the online chat too, not sure
   if that went anywhere"* (strength 0.25) with *"I've logged this as a formal complaint."* That hit
   **261 complaint plants, 84 of them decoys** — an agent formally escalating
   *"the app is a nightmare, but I'm not complaining"*. Fixed with a
   `FORMAL_ACKNOWLEDGEMENT_FLOOR = 0.50` gate. This one mattered beyond realism: the entry's claim is
   that quiet signals go unactioned at the time, and an over-reacting agent contradicts it on screen.

---

## Honest judgement after reading ~25 fresh transcripts

**The agent is fixed. The conversation is not.**

Before, the agent was the most distracting thing on the page. Now it is the most competent thing on
the page, and that has an unwelcome side effect: **it throws the customer side into relief.**

Concretely, `CUST-0024-C3`, a call I read end to end:

```
[ 9] customer: I want to set up a new payee, a plumber.
[10] agent   : Yes - I'll need their details, and I'll confirm them back to you before it saves.
[11] customer: I wan- to set up a new payee, a plumber.
[12] agent   : I can do that. Do you have the sort code and account number?
...
[17] customer: I want to set up a new payee, a plumber.
[18] agent   : Yes - I'll need their details, and I'll confirm them back to you before it saves.
```

The agent asks for the details three times and the customer never supplies them. Before, three
non-sequiturs read as noise. Now three sensible requests that go unanswered read as *broken*. **On
this specific axis Phase A made the transcript worse**, and the cause is `FILLER_CUSTOMER` being
sampled with replacement — 899 / 1,400 conversations repeat a customer line, 166 say one three or
more times. That is customer text, so it is frozen until Phase C.

Still wrong, and none of it fixable for free:

1. **No reason for contact, no resolution.** Every conversation is still a bag of unrelated service
   requests. The agent now handles each one well and nothing ever concludes.
2. **Zero inter-conversation coherence.** Nothing refers to anything. Across 22,114 turns: `"I
   called"` 0, `"as I said"` 0, `"you said"` 0. Unchanged, and it is the thing the owner most wants.
3. **Turn structure is frozen.** 79.0% of conversations still contain consecutive customer turns
   with no reply; 52.9% end on two agent turns.
4. **I removed the security check and did not replace it.** *"Can I take the first and third
   character of your memorable word?"* had to go — it fired 869 times and only 10.1% of them at turn
   ≤ 2. But that leaves **no call in the corpus authenticating the caller at all**, which a
   contact-centre reader will also notice. The call openings now ask "Who am I speaking with?",
   which is the start of verification and not the whole of it. Putting it back correctly means
   adding a turn at a fixed position, which changes turn counts. Phase C.
5. **Customer-side ASR damage is untouched** — 19.2% of typed-channel customer turns carry
   speech-recognition artefacts, and 212 / 973 evidence quotes are mangled, including
   *"can't make the payment this month, I just"*.
6. **A complaint is still a two-party dialogue.** The agent's *voice* is now a written case
   handler's; its *shape* is still a phone call. We have 150 real CC0 examples of the target shape
   committed in `benchmarks/cfpb/out/sample.jsonl` and are not yet using them.
7. **98.3% of customers still share their flagship quote with another customer.** Customer-side.

**Would a UK banking judge now believe these are real transcripts? No.** They would believe the
*agent* is real. They would still see, within about thirty seconds, that the customer is a random
sampler and that nothing in conversation 4 knows conversation 1 happened.

**Is it worth shipping? Yes, without hesitation.** It removes the only thing in the corpus that was
actively damaging rather than merely thin — a bereavement disclosure met with the call-recording
notice, on the recorded demo screen — and it costs nothing. But it should be described as *"the
agent now responds"*, never as *"the transcripts are realistic"*. Phase C is where that claim
becomes available, and Phase C moves every published number.

---

## Next

1. **`tools/ui_fixture.py` and `tools/stream_fixture.py`** — regenerate. `ui/data.js` still carries
   21 copies of "That's now updated on our side." Free, offline, ~10 minutes. This is the surface
   `ui/README.md` calls "the proof".
2. **Re-stamp the sweep artifact** so `pipeline_sha` matches. ~6 minutes offline.
3. **Phase C**, as one pre-registered batch. See `phase4-plan.md`.
