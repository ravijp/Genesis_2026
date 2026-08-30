# Phase 4 — the phased plan

Phased by **what it costs**, not by what is nicest. The dividing line is measured, not assumed
(Phase 2 §4.2–4.3, harness in the session scratchpad: `snapshot.py` + `compare.py`).

---

## The cost rule, stated exactly

`src/earshot/extract.py` iterates `for turn in conversation.turns: if turn.speaker != "customer": continue`.
The extractor never reads an agent turn. One `random.Random(run.seed)` drives the whole generator, so
the **RNG call sequence** is part of the artifact.

Therefore:

| Change | Cost | Verified |
|---|---|---|
| Agent turn **text**, with `rng.choice(FILLER_AGENT)` still executing on a length-10 tuple | **free** | 3 seeds × 400 customers, everything identical |
| Same, with text chosen from the **preceding customer turn and the channel** | **free** | 3 seeds × 400, everything identical |
| Resize `FILLER_AGENT` 10 → 14 | **moves everything** | 11,371 / 11,378 customer turns differ; conversation count 1,400 → 1,435 |
| Remove the `rng.choice` and pick deterministically | **moves everything** | 11,096 / 11,378 customer turns differ; count 1,400 → 1,393 |
| Any change to customer text, turn counts, tuple sizes, channel mix, plant policy | **moves everything** | by construction |

So the constraint is **not** "ten agent lines". It is: **one `rng.choice` on a length-10 tuple must
still execute per agent-filler turn, one on a length-3 tuple per opening and per closing.** Everything
downstream of the draw is free.

**What "free" does not cover.** `pipeline_fingerprint()` hashes the *source bytes* of five modules
including `corpus_lexicon.py`, so it moves on any edit — by design ("deliberately over-sensitive").
Today it is `fd58c7642e12`, and `artifacts/runs/sweep-30x1500-9ddd6674c388.json` carries that exact
value at `manifest.pipeline_sha`. After Phase A that artifact's stamp will not match, and
`tools/routing_accuracy.py:121-133` will print its "corpus moved under it" warning. **The numbers in
it are still correct** — that is precisely the false-stale the docstring says it prefers. The fix is
one offline re-run (33 seconds measured, see below), not a re-derivation.

**Measured re-run costs**, so nobody guesses:

- `uv run earshot sweep --seeds 10 --customers 400` — **32.6 s** wall.
- Extrapolated 30 seeds × 1,500 customers — **≈ 6 minutes**. Offline republish is trivially cheap.
- Keyed artifacts are the expensive half: AT-57 verdict accuracy cost **$1.4733** for 50 cases,
  AT-58 routing rides on that artifact, reader-coverage extension is quoted at ~$0.45. A full
  republish including keyed arms is roughly **$2–5 and half a day**, and it is the real cost of
  Phase C.

---

## Phase A — free wins. Zero published numbers move.

**What changes:** every agent utterance in the corpus. **Which files:** `src/earshot/corpus_lexicon.py`
(the strings and the reply maps) and `src/earshot/corpus.py` (six lines of selection).
**Hours: ~4.** **What breaks: nothing.** **Re-run: the offline sweep, to restamp `pipeline_sha`.**

### A1 — the three tuples, at their exact current lengths

`FILLER_AGENT` **must have exactly 10 entries**, `OPENINGS` **exactly 3**, `CLOSINGS` **exactly 3**.
`FILLER_CUSTOMER` must keep all 15 entries **and their exact text** — it is customer speech.

These 16 are the *fallback*: what fires when no responsive reply is mapped. Every one must therefore
be true regardless of what preceded it. The design rule, taken from the FCA's March 2025 good-practice
findings and Taskmaster-1's operator move types: **a fallback line may acknowledge, note, clarify or
check. It may never claim an action was completed, never be channel-specific, and never be a closing
move.** That single rule kills five of the current ten.

**`FILLER_AGENT` — 10 entries:**

```python
FILLER_AGENT: tuple[str, ...] = (
    "Right, let me take a look at that for you.",
    "Bear with me a moment, I'm just bringing that up.",
    "Thanks — I've put a note on the account so you don't have to say it twice.",
    "Yes, I can see that here.",
    "Let me just check I've got that right before I do anything.",
    "I'll need to check that with the team who look after it — give me a second.",
    "Sorry, can I take you back a step? I want to make sure I've got this right.",
    "Okay, I've made a note of that.",
    "I'm sorry to hear that. Let's see what we can do.",
    "Let me find out for you rather than guess.",
)
```

Why each of the ten it replaces had to go: *"That's now updated on our side."* and *"You should receive
that within three to five working days."* claim completed actions that never happened. *"Just so you
know, this call may be recorded for training purposes."* fired 893 times, only 15.1% of them in the
first three turns, and 591 of them inside chat or complaint. *"Thanks for holding, I appreciate your
patience."* appeared 575 times in typed channels. *"Can I take the first and third character of your
memorable word?"* fired 869 times, 10.1% of them at turn ≤ 2, twice or more in 161 conversations.
*"Is there anything else I can help you with today?"* is a closing move that fired mid-conversation.

**`OPENINGS` — 3 entries, selected per channel from the burned draw:**

```python
OPENINGS: tuple[str, ...] = (
    "Thanks for calling, you're through to Priya — can I take your name?",
    "Good afternoon, you're speaking with Daniel. How can I help?",
    "Hello, Marcus here. What can I do for you today?",
)
CHAT_OPENINGS: tuple[str, ...] = (
    "Hi, you're chatting with Priya. How can I help today?",
    "Hello — Daniel here on chat. What can I help you with?",
    "Hi there, thanks for messaging. Marcus here — what's happened?",
)
```

Three agent names instead of one (`Sam` named 299 conversations). Names are UK-contact-centre
plausible and are not real people.

**`CLOSINGS` — 3 entries, per channel:**

```python
CLOSINGS: tuple[str, ...] = (
    "That's everything from me — you'll see my note on the account if you ring back.",
    "Thanks for your patience with that one. Take care.",
    "If it happens again, ring us and quote today's date — it'll be on the record.",
)
CHAT_CLOSINGS: tuple[str, ...] = (
    "I've saved this chat to your record, so you won't have to start again.",
    "Thanks for bearing with me. I'll leave the chat open a minute in case.",
    "If it comes back, message us and mention today — it's all logged.",
)
```

The closings now assert the one thing the product is about: **the contact is on the record and will be
there next time.** That is free narrative reinforcement on 940 conversations.

### A2 — responsive selection (the part that actually fixes the demo)

`_render_conversation` already has `channel` and `plant` in scope, and `plant.fragment_id` identifies
exactly which of the 67 fragments was planted. So both agent-filler sites can be fully responsive:

```python
# site 1 — the reply to a PLANTED signal
_ = rng.choice(FILLER_AGENT)                      # burn the draw; the stream must not move
turns.append(Turn(idx, "agent", reply_to_signal(plant.fragment_id, channel, _)))

# site 2 — the reply to a FILLER turn
_ = rng.choice(FILLER_AGENT)
turns.append(Turn(idx, "agent", reply_to_filler(picked_filler, channel, _)))
```

Two maps in `corpus_lexicon.py`: `AGENT_REPLIES_TO_SIGNAL` keyed by `fragment_id` (67 keys × 2
variants) and `AGENT_REPLIES_TO_FILLER` keyed by the un-mangled `FILLER_CUSTOMER` string (15 keys × 2
variants). Variety comes free from the burned draw's index — `FILLER_AGENT.index(drawn) % 2` is a
uniform bit.

The three that end a demo today, and what they become:

| planted customer turn | today | Phase A |
|---|---|---|
| "My husband passed away in June and I'm sorting out the accounts." | "Just so you know, this call may be recorded for training purposes." | "I'm very sorry. Let me stop what I'm doing — I'll take the details once and pass you to the bereavement team, so you don't have to go through it again." |
| "I want to close the account, this week." | "That's now updated on our side." | "Okay. Before I start that — can I ask what's prompted it? If there's something we've got wrong I'd rather try to fix it." |
| "I can't make the payment this month, I just can't." | "Of course, let me pull that up for you." | "Thank you for telling me — that's the right call. Nothing happens today. Let me go through what we can do." |

The last one is written straight off the FCA finding that only 4 in 10 customers with a vulnerability
characteristic ever disclose it; an agent who rewards the disclosure is the documented good practice.

### A3 — verification

`snapshot.py` captures, for 3 seeds × 400 customers: every customer turn keyed by
(conversation, index); every `SeededSignal` field; every `CustomerTruth` field; each conversation's
channel, day and **speaker sequence**; every `ExtractedSignal` the offline reader produces; and every
customer's ledger score, entry count, per-entry `contribution_now` and `score_at_write`.
`compare.py` diffs before against after and exits non-zero on any movement.

**If anything moves, stop.** Not "investigate" — stop, because the only thing that can move it is the
RNG stream, and a moved stream invalidates the premise.

### What a judge notices after Phase A

They stop noticing the agent. Which is the point — right now the agent is the most distracting thing
on the screen. The transcripts still will not read as *conversations* (see Phase C), but nothing in
them will be actively wrong, and the bereavement screen stops being a Consumer Duty incident.

---

## Phase B — cheap, contained, moves only clearly-labelled demo artifacts

**Hours: ~2. Re-run: `tools/ui_fixture.py` and `tools/stream_fixture.py`, both offline and free.**

**B1 — regenerate `ui/data.js` and the streamed fixture.** These are recorded screens. `ui/data.js`
carries 21 instances of "That's now updated on our side.", 25 of "Thanks for holding", 27 of the
recording notice. After Phase A the generator produces different agent text at identical customer
turns, so regeneration is a pure refresh with no number movement. `ui/README.md` calls the transcript
screen "the proof" and `ui/console.js` calls that click "the single most important click in the demo";
it is the highest-visibility surface in the entry.

*Caveat carried forward from `handover.md` item 4:* the recorded document screens are still the
**offline rule engine**, not a keyed investigate run. Phase B fixes the *prose* on those screens; it
does not fix their provenance. Say which one is being claimed.

**B2 — a substring guard.** One test asserting no `corpus_lexicon` fragment shares a 6-gram with any
narrative in `benchmarks/cfpb/out/sample.jsonl`. Turns the Phase 3 promise ("we ground on real data,
we never ship it") into something mechanical, in the style this repo already uses for separation.
Offline, free, ~30 minutes.

**B3 — a provenance table in the README.** Which real source informed which generator decision, with
access dates and licences, from `phase3-public-sources.md`. Zero code. This is what converts "it's
synthetic" from an apology into a method.

---

## Phase C — the real thing: transcripts that read as one relationship

**This is what the owner most wants and it is the expensive one. Hours: 20–30. It moves every
published number.**

### What it has to produce

1. **A reason for contact.** Every conversation opens with the customer stating why they are in touch,
   and the conversation resolves it or fails to. Today the customer asks 4–12 unrelated questions.
   Taxonomy from the Bitext retail-banking intent list (26 intents, CDLA) — the taxonomy, not the text.
2. **Inter-conversation coherence.** `_render_conversation` currently takes no prior conversation.
   It must take the arc so far. Then:
   - conversation 2 opens by referring to conversation 1 ("I rang about this at the end of March");
   - the gap is acknowledged the way people acknowledge gaps, and the gap is real — median 30 days,
     20.3% of gaps ≥ 60 days, so "it's been a couple of months" is available and currently unused;
   - an agent promise in one contact is **kept or broken** in the next, and which one it is drives
     whether `complaint_escalation` fragments are earned;
   - the arc reads as one relationship over months.
3. **Back-references that are true.** Today 43 / 152 plantings of a back-reference fragment (28.3%)
   land in the customer's first conversation. "This is the fourth time I've called" is planted 9 / 10
   times into an arc with fewer than four conversations. Gate the fragment on arc position.
4. **Conversation choreography.** Verification once, at the start. Recording notice at turn 0–1 of a
   call and nowhere else. No customer→customer runs (79.0% of conversations have one). No
   agent→agent runs (52.9%). Filler sampled without replacement (64.2% of conversations repeat a
   customer line; 166 say one three or more times).
5. **Channel is real.** ASR noise only on `call`. `complaint` becomes what
   `benchmarks/cfpb/out/sample.jsonl` shows a complaint is: **one author, no turn-taking, median 155
   words** — we have 150 real examples of the target shape, CC0, already committed.
6. **Stop mangling the evidence.** 212 / 973 plants (21.8%) ship a damaged quote, including
   *"can't make the payment this month, I just"*. Apply ASR noise to filler, never to the plant.
7. **Plant decoys without replacement.** 33 / 400 customers currently carry the same fragment twice
   (38 plantings, all on the two decoy paths), which pays the ledger a cross-conversation
   corroboration bonus for one sentence copied twice — the exact defect `_nearest_fragment`'s
   docstring says was fixed. It was fixed on the arc paths only.
8. **More fragments, or generated variation.** 298 / 303 customers with a signal (98.3%) share their
   flagship quote with another customer; `le-w7` is planted 47 times. Two cases in the queue showing
   the identical sentence reads as a bug.

### What it forces to be republished

Everything. In order: the 30 × 1,500 sweep (~6 min) → every table in `README.md` → the one-pagers →
`ui/data.js` and the stream fixture → **AT-57 verdict accuracy (~$1.50) and AT-58 routing, both keyed**
→ reader coverage. Pre-registered protocols under `benchmarks/*/PROTOCOL.md` must be checked before,
not after — `working-agreements.md` is explicit that the ledger's diffuse win is the pre-registered
result and the corpus underneath it moving is a re-registration, not a refresh.

**Sequencing that avoids paying twice**, and it is already a recorded trap: land every generator change
*before* spending on keyed runs. The repo lost $1.50 to exactly this because `config_hash` did not
cover the code. Phase C is one batch, one re-registration, one keyed re-run — not four.

### Honest scoping

| Piece | Hours |
|---|---|
| Reason-for-contact + scripted beats | 6–8 |
| Arc state threaded through `_render_conversation`, back-references, promise kept/broken | 6–8 |
| Choreography (verification, notice, no same-speaker runs, filler without replacement) | 3–4 |
| Channel realism incl. complaint-as-document | 3–4 |
| ASR confined to call, plant never mangled, decoys without replacement | 1–2 |
| Re-run, re-check every table, re-register the protocol | 4–6 |
| **Total** | **23–32** |

**What I would cut if there were only ten hours:** items 2, 3 and 6. Inter-conversation coherence is
the entry's whole thesis made visible; true back-references stop the corpus contradicting itself; and
un-mangling the evidence quote is a one-line change protecting the single most-looked-at string on the
screen. Reason-for-contact is the biggest realism win per line of prose but it does not carry the
argument the way coherence does.

---

## The 100%-signal question, which the owner raised

**Verified independently.** At n=400, seed 20260809: 210 arc customers (concentrated + diffuse), 730
conversations between them, **0 silent (0.0%)**, and **210 / 210 (100.0%)** have a planted signal in
every single conversation. `decoy_accumulator` is the same — 90 / 90 conversations carry a plant. By
contrast `decoy_extractor` is 104 / 257 silent (40.5%, from a `rng.random() < 0.6` gate) and `null` is
323 / 323 silent. So the generator *can* produce silence; the arc path never asks for it.

**So "diffuse" currently means *a weak signal every time*, not *silence between signals*.** The
genuinely hard case — something in March, nothing in May, something in July — is not in the corpus.

**What fixing it costs.** The code is one line: a per-conversation Bernoulli in the
`CONCENTRATED / DIFFUSE` branch. The *consequence* is that it moves every published number and it is
a real experiment, not a fix — it changes what a stratum is, so it changes what the pre-registered
diffuse comparison is a comparison of. Expect the ledger's advantage to move, in an unknown direction:
fewer signals per arc weakens accumulation, but silence is exactly what a per-call baseline cannot
exploit and a ledger can.

**Should it be in scope? Yes, and only inside Phase C, pre-registered.**

Three reasons for it, one against.

For: (1) it is the strongest version of this entry's claim and it is currently **untested**, which is
a gap a technical judge can find; (2) conversation-level signal prevalence is 973 / 1,400 = 69.5%,
which is not a plausible portfolio and is a number a judge can compute from the demo; (3) the
narrative — "she said nothing for four months and the ledger still had March on the books" — is
strictly better theatre than what we have.

Against: it re-opens a pre-registered comparison six days before the 2026-09-07 gate, and
`working-agreements.md` exists because this project has already been burned by moving corpora under
published figures.

**Recommendation: run it as a declared second arm, not a replacement.** Generate both corpora, publish
both columns, and label the new one "silence-permitting, pre-registered 2026-08-31". A stated result
on a harder corpus beside the original buys more technical-depth credit than quietly swapping the
corpus, and it removes the only version of this objection that actually bites: *"your diffuse case
still talks in every conversation, so you never tested silence."*

---

## Recommended order

1. **Phase A now** — free, verified, fixes the worst screen in the entry.
2. **Phase B immediately after** — 2 hours, refreshes the surfaces a judge actually clicks.
3. **Phase C as one pre-registered batch** — every generator change landed before a single keyed
   pound is spent, with the silence arm published as a second column rather than a substitution.
