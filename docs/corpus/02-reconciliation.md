# Phase 2 — reconciliation with `bucket2-data.md`

**2026-08-31.** My Phase 1 was written blind and is not revised. This file compares it with the
prior report and says where I think that report is wrong.

**Headline: we agree on the diagnosis, and on several numbers we agree to the digit.** Two people
measuring independently got 1,210 / 1,400 and 109 / 973 from different scripts. That is about as
strong a confirmation as this kind of review can produce. The prior report is better than mine on
external anchoring and on the recall-by-fragment-cohort measurement. Mine adds a live correctness
defect it missed, and — more usefully — an empirical result that changes what "free" means.

---

## 1. Where we agree, independently

| Finding | Prior report | Mine | Match |
|---|---|---|---|
| Distinct agent utterances corpus-wide | 16 | 16 | exact |
| Conversations repeating a line verbatim | 1,210 / 1,400 = 0.864 | 1,210 / 1,400 = 0.864 (I re-ran their definition to check) | exact |
| Plants followed by a loosely responsive agent line | 109 / 973 = 0.112 | 864 / 973 non-responsive = 0.888, i.e. **109 responsive** | exact, from opposite directions |
| Chat opening "Thank you for calling…" | 129 / 450 = 0.287 | 129 / 450 = 0.287 | exact |
| Arc conversations carrying a plant | 344/344 + 386/386 = 1.000 | 730 / 730 = 1.000 | exact |
| `decoy_extractor` conversations carrying a plant | 153 / 257 = 0.595 | 104 / 257 silent = 0.405 | exact complement |
| Turns per conversation | mean 15.6 (n=200) | mean 15.8, median 16, max 26 (n=400) | consistent |
| Channel is decorative | yes | yes | same |
| ASR noise in typed channels is impossible | yes | yes | same |
| Complaint is not a complaint | yes | 460 / 460 have interleaved agent turns | same |
| No inter-conversation coherence at all | yes | 0 hits for "I called" / "as I said" / "you said" in 22,114 turns | same |
| The 56 planted fragments are genuinely good | yes | yes | same |
| The fix is nearly free because `extract.py` reads only customer turns | yes | yes | same, and I have now proved it three ways |
| Demo prints "NOT an instance of the claim" on screen | "0 of 23" at n=400 | I reproduced "0 of 23" at `--customers 400` | exact |

We also independently reached the same top recommendation: rewrite the agent lines, keep the tuple
at length 10, because `rng.choice` consumes a length-dependent number of bits.

---

## 2. What only the prior report found — and it matters

1. **Recall split by fragment cohort: 151 / 234 = 0.645 on the original 24 fragments versus
   15 / 496 = 0.030 on the 32 blind-authored ones.** This is the best measurement in either
   document. I did not think to cut recall that way and I should have. It converts the CFPB result
   (4 / 112 = 0.036) from "genre mismatch" into "the lexicon only reads prose it was co-developed
   with", from a second direction, on in-genre spoken UK banking text. Keep it and put it on a slide.
2. **`benchmarks/pool-widening/` has 32 / 56 fragment ids colliding with shipped ids, with different
   text and different strengths.** A live foot-gun. I never opened that folder.
3. **The realised outcome rate is 63 / 400 = 0.1575 per 180 days**, against a docstring that says
   "~3% background attrition". A judge with a calculator is the risk. I read the config and took the
   docstring at face value; that was a miss.
4. **All of section 6 — the external anchoring.** CASS 1,054,521 switches in 2025 against ~100m PCAs;
   FCA Financial Lives 49% / 26.4m with a vulnerability characteristic and only 4 in 10 ever
   disclosing; FCA aggregate complaints 2025 H1; FOS 305,918. The 49% × 40% ≈ 20% ≈ the
   CONCENTRATED stratum mapping is genuinely good and I had nothing like it.
5. **NatWest AI Research arXiv:2605.16268** as the closest prior art. That is a real find and it
   should be read before 2026-09-07.
6. **Temporal escalation is absent**: in CONCENTRATED arcs the loudest fragment is last 33.7% of the
   time and first 30.6% — a coin flip. I noticed arcs have no reversals; I did not measure placement.
7. **The dead arithmetic at `corpus.py:256`** (`k / max(1, k)` ≡ 1.0). Correct, cosmetic.
8. **`ui/data.js` and `ui/stream.js` specifics** — 30 / 36 and 114 / 133 transcripts repeat a line.
   I confirmed the agent lines reach the UI (21 occurrences of "That's now updated on our side." in
   `ui/data.js`) but did not count transcripts.

---

## 3. What only I found

### 3.1 The re-plant defect is NOT fixed. It is live on both decoy paths. (the important one)

The prior report's §3.2 describes the `or list(pool)` re-plant defect, explains correctly that it made
`memory._raw()` count `n_conversations = 2` and pay a cross-conversation corroboration bonus for one
utterance copied twice, and concludes: **"Now 0."**

That is true for `CONCENTRATED` and `DIFFUSE`, which go through `_nearest_fragment` and its `used`
set. It is **false for the two decoy strata**, which still draw with replacement:

```python
elif stratum is Stratum.DECOY_EXTRACTOR:
    ...  plants[i] = rng.choice(DECOYS_EXTRACTOR)      # corpus.py, with replacement
elif stratum is Stratum.DECOY_ACCUMULATOR:
    plants[i] = rng.choice(DECOYS_ACCUMULATOR)          # corpus.py, with replacement
```

Measured at n=400, seed 20260809: **33 / 400 customers carry the same fragment twice or more in one
arc — 38 duplicate plantings, 17 `decoy_accumulator` and 16 `decoy_extractor`, 0 on real arcs.**
`CUST-0002` says *"Cashflow's a bit lumpy this quarter, it always is."* verbatim on day 175 and again
on day 178, three days apart, and the ledger treats those as two independent corroborating
conversations.

The pools make this unavoidable, not unlucky: `DECOYS_ACCUMULATOR` holds 5 fragments and
`decoy_accumulator` plants in **every** conversation of an arc of up to 5, drawn with replacement.

Why it matters and why it is not urgent: the bias runs *against* the ledger (decoys score higher, so
the ledger's false-positive count rises), which is the safe direction, and `decoy_accumulator` is only
25 / 400 customers. But it is the exact mechanism the repo has already written a 12-line docstring
about, on 33 customers, and "we fixed the arc path and left the decoy path" is a bad answer to a judge
who reads `corpus.py`. Fixing it moves published numbers, so it belongs in a pre-registered batch.

### 3.2 Back-reference fragments contradict the arcs they land in

Twelve fragments assert a prior contact. **43 / 152 plantings (28.3%) land in the customer's first
conversation.** *"This is the fourth time I've called about this and nobody has fixed it"* is planted
**9 / 10 times into an arc with fewer than four conversations** — `CUST-0015` says it in conversation
1 of 2. *"I've been passed to four different people today"* is planted 5 times into a corpus where no
conversation has more than one agent. Seasonal words have no calendar anchor: "back in the spring" is
planted on days 40–142 of an unanchored 180-day horizon.

This is the failure a judge finds by *reading*, which is exactly the audience this work is for.

### 3.3 ASR noise damages the evidence quotes, quantified

The prior report spots this in one example (§4.4). Measured: **212 / 973 planted signals (21.8%)
ship a mangled evidence quote, and 19 / 85 (22.4%) of the high-mass ones.** These strings are what
the case screen prints as load-bearing evidence:

```
seeded : I can't make the payment this month, I just can't.
shipped: can't make the payment this month, I just
```

Noise on filler is realism. Noise on the quote we hold up as proof reads as a bug, and it is a
one-line fix that costs a re-run.

### 3.4 The same sentence is the flagship evidence for many different customers

**298 / 303 customers with any signal (98.3%) share their highest-mass quote with at least one other
customer.** `le-w7` is planted 47 times, `ci-w7` 40 times. A judge scrolling the queue sees the same
sentence on two cases.

### 3.5 Conversation choreography

The security question fires 869 times and is at turn index ≤ 2 only **88 times (10.1%)**;
**161 / 1,400** conversations ask it twice or more. The recording notice fires 893 times and is in
the first three turns only **135 times (15.1%)**. Both are things a contact-centre person notices in
under ten seconds.

### 3.6 Two smaller ones

- The outcome day is always `days[-1] + randint(10, 60)` — strictly after the last conversation. No
  customer ever churns and then keeps talking to us, so there is no post-outcome contact anywhere.
- **`uv run earshot demo` with no `--customers` runs at the `CorpusConfig` default of 10** and prints
  *"0 of 0 thin-evidence customers"* followed by the "NOT an instance of the claim" banner. Anyone who
  types the bare command in front of judges gets the worst version of that screen.

---

## 4. Where I think the prior report is wrong

### 4.1 "Now 0" for the re-plant defect — wrong, it is 38 plantings across 33 / 400 customers

Covered in §3.1. This is a factual error, not a difference of emphasis.

### 4.2 Its recommended implementation of its own top recommendation would break the thing it says is free

The prior report's item 1 says two things that cannot both be true:

> "Add a reply map keyed on the preceding customer line … and **select at `corpus.py:132` and `:140`
> instead of `rng.choice`**."
> "**Constraint that makes this free: keep every tuple at its current length.**"

The constraint is about tuple length, but the mechanism is the *draw*, not the tuple. Selecting
"instead of `rng.choice`" removes a draw from the stream, and the stream is shared with the customer
turns. I tested it. Replacing `rng.choice(FILLER_AGENT)` with a deterministic content-keyed pick, at
both sites, over 3 seeds × 400 customers:

```
seed 20260809:
  FAIL n_conversations DIFFERS       before: 1400   after: 1393
  FAIL customer_turns  DIFFERS       11096 / 11378 entries differ
```

Anyone following that instruction literally would have moved every published number while believing
they had changed nothing. Given the repo already lost a $1.50 keyed run to exactly this class of
mistake (`config_hash` not covering the code), this is worth stating plainly.

### 4.3 The good news: the correct mechanism is much better than either of us thought

Keep the draw and *override the text*. I tested a fully responsive, **channel-aware** agent line whose
text is a function of the preceding customer turn and the channel — arbitrary text, unbounded
vocabulary, nothing to do with the ten strings:

```python
_drawn = rng.choice(FILLER_AGENT)          # burn the draw, discard the value
turns.append(Turn(idx, "agent", <any text you like, from context + channel>))
```

Result over 3 seeds × 400 customers (33,663 customer turns, 3,049 seeded signals, 998 extracted
signals, 1,200 ledger scores):

```
RESULT: IDENTICAL - nothing that must not move has moved
```

So the constraint is **not** "ten agent lines, rewritten". It is "**one `rng.choice` call on a
length-10 tuple must still execute per agent filler turn**". Everything downstream of that is free:
per-channel agent language, per-signal-type acknowledgement, a reply that answers the question asked,
and as much variety as we care to author. That materially raises the ceiling on Phase A, and it is the
single most useful thing to come out of this reconciliation.

### 4.4 "Customer turns nobody replies to: 4,018 / 11,378 = 0.353" — I cannot reproduce it

Under the natural definition — a customer turn whose next turn is not an agent turn, including the
last turn of a conversation — I measure **2,322 / 11,378 = 0.204**. The prior report does not state
its definition. The finding is right either way; the figure should not be quoted until the definition
is pinned.

### 4.5 "Non-`call` turns carrying an ASR clip marker: 674 / 14,182 = 0.048" understates it

That counts only the clipping marker (`word-`). `_apply_asr_noise` has two branches and the other one
**deletes the word silently**, leaving no marker. Counting any customer turn in a typed channel that
differs from its canonical lexicon string: **1,428 / 7,453 = 19.2%**. A silently dropped word is just
as impossible in a typed chat as a clipped one, and it is harder to spot, which makes it worse.

### 4.6 One framing I would push back on

"Stop calling the third channel 'complaint' and call it 'written contact'" is good advice about the
*rate*. But the corpus also has a `complaint_escalation` signal type and a `complaints` owning team in
`TRAJECTORY_TEAM`, so renaming the channel and keeping the signal type will read as sloppy unless
both move together. Cheaper and more honest: keep the name, reweight the mix, and put one sentence in
the README saying the complaint share is deliberately inflated so the stratum is measurable at
n=1,500. Deliberate over-sampling of a rare stratum is standard practice and defensible out loud;
a wrong rate presented as a real one is not.

---

## 5. Net

Nothing in the prior report changed my ranking of what to fix first. Both of us put the agent-line
rewrite at the top, for the same reason, having verified the same mechanism. The reconciliation
changed one thing that matters: **Phase A is bigger than "ten new strings"** — it can be a genuinely
responsive, channel-aware agent, for exactly zero movement in the published numbers, provided the
draw is burned.
