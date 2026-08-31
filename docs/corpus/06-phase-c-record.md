# Phase 6 — what Phase C actually changed

**2026-08-31.** Items 1–7 of `04-plan.md`'s Phase C, landed in the generator. Item 8 was built,
measured, and **deliberately not shipped** — the measurement is in §6.

Everything here is offline and free. **No keyed run was spent**, which is the sequencing
`04-plan.md` calls a recorded trap: land every generator change before a single keyed pound.

Branch `wp/phase-c`, six commits, `5948326`..`36395f6`. Suite green, ruff clean, corpus
byte-identical across two runs at the same seed.

---

## 1. The one-line verdict

**Yes, an arc now reads as one relationship.** Conversation 2 opens by naming conversation 1, how
long ago it was, in which month, over which channel, and whether what the agent undertook actually
happened. A broken undertaking is chased in the next contact, by both parties, and it is what earns
a complaint escalation. Read end to end, the arcs are recognisably one customer's year.

What it is not: **long**. Every live conversation takes one of six lengths - 9, 11, 13, 15, 17 or 19 turns, and 411 of 933 are 15 - and is strictly
alternating. The old corpus was disordered; this one is tidy, and tidy is its own tell. §7.

---

## 2. Every defect count, before and after

400 customers, seed 20260809 — the denominators `01-diagnosis.md` uses. Script:
session scratchpad `measure.py`.

| measure | before | after |
|---|---|---|
| **item 6 — the evidence quote** | | |
| planted signals shipping a damaged quote | 212 / 973 = 0.218 | **0 / 947 = 0.000** |
| …of the high-mass ones (mass ≥ 0.80) | 19 / 85 = 0.224 | **0 / 86 = 0.000** |
| **item 3 — back-references that are true** | | |
| back-reference planted in the customer's FIRST conversation | 34 / 126 = 0.270 | **0 / 77** |
| *"this is the fourth time I've called"* in an arc with < 4 contacts | 9 / 10 = 0.900 | **0 / 1** |
| **item 2 — inter-conversation coherence** | | |
| later conversations referring to the previous contact | 0 / 1000 = 0.000 | **980 / 980 = 1.000** |
| "I rang" · "you said" · "promised" · "couple of months" | 12 · 0 · 5 · 0 | **302 · 91 · 78 · 83** |
| **item 4 — choreography** | | |
| conversations with an agent→agent run | 740 / 1400 = 0.529 | **0 / 1380** |
| conversations with a customer→customer run | 1106 / 1400 = 0.790 | 447 / 1380 = 0.324 † |
| conversations repeating a customer line verbatim | 899 / 1400 = 0.642 | **0 / 1380** |
| …saying one customer line three or more times | 166 / 1400 = 0.119 | **0 / 1380** |
| conversations repeating an agent line verbatim | 543 / 1400 = 0.388 | **0 / 1380** |
| verification asked, and at turn ≤ 2 | 0, 0 ‡ | 477, **477 / 477** |
| verification asked twice in one conversation | 0 ‡ | **0** |
| verification outside a call or chat | 0 ‡ | **0** |
| recording notice, and at turn ≤ 1 | 0, 0 ‡ | 163, **163 / 163** |
| recording notice outside a call | 0 ‡ | **0** |
| **item 5 — channel is real** | | |
| typed customer turns carrying a speech-clip marker | 616 / 7453 = 0.083 | **0 / 5214** |
| complaint documents with interleaved agent turns | 459 / 460 = 0.998 | **0 / 447** |
| complaint narrative length, median customer words | 84 | **139** (CFPB sample: 155) |
| telephone language inside a typed channel | 0 ‡ | **0** |
| **item 7 — decoys** | | |
| customers carrying the same fragment id twice | 33 / 400 = 0.083 | **0 / 400** |
| duplicate plantings | 38 | **0** |
| the identical planted sentence twice in one arc | 25 | **0** |
| **item 8 — fragment variety (NOT shipped, see §6)** | | |
| customers sharing their flagship quote with another | 222 / 303 = 0.733 | 286 / 291 = 0.983 †† |
| **shape** | | |
| distinct agent surface strings | 175 | **719** |
| distinct customer surface strings | 742 | **1528** |
| turns per conversation, median / max | 16 / 26 | 11 / 19 |
| total turns | 22,114 | 15,124 |

† **Complaints only.** A complaint is one author by construction, so every one of them is a
"customer run". On `call` and `chat` it is **0 / 933** — `test_nobody_speaks_twice_in_a_row`.

‡ **Zero because Phase A deleted them**, not because they were right. Phase A removed the security
question (869 fires, only 88 at turn ≤ 2) and the recording notice (893 fires, 591 of them inside a
typed channel) rather than placing them correctly. Phase C puts them back where a contact centre
actually has them: once, at the top, on the channel that has them.

†† **This got worse on the surface and did not move underneath.** The before-number was flattered by
the very defect item 6 fixed: 212 damaged quotes were 212 accidentally-unique strings. Measured on
the **fragment id** rather than the rendered text — the honest comparison — it was **1165 / 1168 =
0.997** before and 0.983 after. Nothing improved and nothing regressed; §6 says why we did not fix it.

**One integrity check that came out clean.** The generator now emits ~1,500 new authored customer
sentences (topic follow-ups, chase questions, continuity openings, complaint scaffolding). With both
extractor honesty knobs at zero, at 800 customers: **565 extracted signals, 565 of them on a planted
turn, 0 unseeded.** The new prose puts no evidence into a conversation the answer key says is empty.
Same measurement on the pre-Phase-C corpus: 587 / 587 / 0. Both clean.

---

## 3. What was built

**Inter-conversation coherence (item 2).** `_render_conversation` takes an `ArcContext`: the
conversation's position in the arc, the reason for this contact, and a `PriorContact` holding the
previous conversation's day, channel, topic, and whether the undertaking given then was kept.
`corpus.CORPUS_EPOCH` anchors day 0 to 1 February, so a generated back-reference names a real month.
Gap phrasing is bucketed off the shipped gap distribution (median 30 days, mean 37, 20.3% ≥ 60):
under 10 days "the other day", under 25 "a couple of weeks back", under 60 "about a month ago",
under 120 "a couple of months ago", beyond that "months ago now".

**The promise schedule is plan, not prose.** `_promise_schedule` runs inside `generate()` before a
word exists. A `complaint_escalation` arc makes an undertaking at every contact and keeps it 15% of
the time; every other arc makes one about half the time and keeps it 85%. A broken undertaking makes
the next contact chase **the same topic**, and both parties say so. This is what makes the escalation
earned instead of asserted.

**Back-references that are true (item 3).** `Fragment` gained `requires_prior`,
`requires_broken_promise` and `earliest_day`; `_nearest_fragment` filters on them. Eleven of the
complaint-escalation fragments assert a prior contact, which left only three plantable on a first
contact, so **five new fragments were authored for what a *first* complaint sounds like**
(`ce-s4`..`ce-w9`) — the pool is 19. Six fragments were reworded rather than gated, because their
claim was about a calendar the corpus had no epoch for: *"passed away in June"* became *"passed away
earlier this year"*, *"back in the spring"* became *"last time"*, and *"passed to four different
people today"* became *"passed round three departments since this started"* (no conversation in this
corpus has more than one agent — that sentence was never true).

**Reason for contact (item 1).** Fifteen `Topic`s, one per existing `FILLER_CUSTOMER` line, promoted
from filler to reason. Each carries three topic-consistent follow-ups with authored agent replies,
two declarative narrative paragraphs for the written channel, an undertaking, resolved and promised
closings, and chase phrasings. Intent ids follow the Bitext retail-banking taxonomy (CDLA-Sharing-1.0,
read 2026-08-31) — **the taxonomy only**; that dataset's own card says its text is NLG-generated.
All fifteen reasons are operational and none is a signal, deliberately: a reason like "I want to
close my savings account" would put unplanted churn evidence into conversations the key calls empty.

**Choreography (item 4).** Strict alternation on live channels. Agent opening (recording notice
folded in on a call, so it cannot be a second agent turn), customer states the reason, one security
check, the answer, verified-plus-acknowledgement, then alternating body, then a closing appended to
the last reply. Body turns are sampled without replacement and prefer what the customer has not said
before; off-topic turns are marked as asides ("While I've got you —") and capped at two, interior only.

**Channel realism (item 5).** ASR damage on `call` only. A complaint is one author, no turn-taking,
with a single written response at the end — which is what the CFPB records as a field of its own, not
a turn in a conversation. Length is drawn independently: 30% short (no detail, no impact), 45%
medium, 25% long.

**Decoys (item 7).** Drawn without replacement, and `_surface()` renders a paraphrase if a fragment
recurs anyway. Both halves are needed, and the reasoning in `state-of-play.md` is respected: a
recurring decoy earns a corroboration bonus it does not deserve, which makes the trap *harder* and
biases against the ledger. A different decoy of the same type in the next conversation corroborates
exactly as hard, because the ledger counts conversations of a type, not identical strings. **One
honest side effect:** `DECOYS_ACCUMULATOR` holds 3 financial-distress and 2 churn fragments, so
without-replacement makes an arc's decoy types slightly more mixed, which very slightly weakens the
trap. Measured: accumulator decoy fire rate 0.4786 → 0.4871, extractor decoy fire rate 0.0274 →
0.0191.

---

## 4. Two bugs this work introduced and then caught by measuring

**A fragment the plan allocated was silently never spoken.** `_body_turns` caps its output at the
topic's follow-ups plus two asides, so a long `body_turns` draw returned fewer pairs than asked for
while `plant_at` was drawn against the number *asked for*. The loop never reached it. Measured at 600
customers: **69 arc conversations across all four trajectories carried no evidence the planner had
allocated to them.** Invisible from outside — nothing is seeded that was not placed, so the answer key
stayed self-consistent and only the arcs were diluted.

It moved a real result, and `tests/test_sweep.py` is what caught it. With the bug, the ledger's
diffuse record against `stateless-top2` swung from **+4 to +15** across a tenfold change in
`alpha_diffuse` (20 seeds, n=300) — i.e. the stratum looked substantially like a restatement of its
own generating parameter. Fixed: **+4 / +8 / +9**, a swing of 5, against the pre-Phase-C corpus's 6.
`test_every_allocated_fragment_is_actually_spoken` drives `_render_live` over every body length the
config can draw, on both live channels, for all fifteen topics.

**Speech recognition was eating the load-bearing sentence.** *"I rang about the lost card about a
month ago and nothing has come of it"* shipped as *"I about a month ago and nothing has come of it"*.
The reason for contact and the security answer now bypass ASR for the same reason the planted quote
does: damage may not fall on a sentence the product reads a claim off.

---

## 5. The published numbers, and the one that collapsed

`uv run earshot sweep --seeds 30 --customers 1500`, `git=36395f6`, 129 s,
`artifacts/runs/sweep-30x1500-2d916ad3ceb0.json`.

### The pre-registered headline is gone

| diffuse arcs, paired by seed | published | Phase C |
|---|---|---|
| `full-ledger` vs `stateless-max` **(pre-registered)** | **29–0–1, p<0.001** | **15–13–2, p=0.851** |
| …randomised tie-break | 28–0–2 | 17–9–4, p=0.169 |
| `full-ledger` vs `stateless-top2` | 26–2–2, p<0.001 | **30–0–0, p<0.001** |
| `full-ledger` vs `window3-top2` | 26–2–2, p<0.001 | **30–0–0, p<0.001** |
| `full-ledger` vs `stateless-top3` | — | 21–1–8, p<0.001 |
| `full-ledger` vs `random-rank` | 17–11–2, p=0.345 | 18–8–4, p=0.076 |
| `full-ledger` vs `dumb-ledger` | 15–8–7 | **7–18–5, p=0.043 (a loss)** |

Pooled recall, 30 × 1500, 10% budget:

| arm | overall | diffuse | concentrated |
|---|---|---|---|
| `stateless-max` | 0.138 → **0.145** | 0.088 → **0.141** | 0.310 → 0.272 |
| `long-context-3` | 0.129 → 0.137 | 0.127 → 0.131 | 0.215 → 0.249 |
| `hybrid` | 0.129 → 0.135 | 0.113 → 0.119 | 0.232 → 0.260 |
| `stateless-top3` | 0.121 → 0.123 | 0.133 → 0.133 | 0.172 → 0.177 |
| `stateless-top2` | 0.119 → 0.119 | 0.108 → 0.109 | 0.192 → 0.182 |
| `window3-top2` | 0.120 → 0.119 | 0.108 → 0.109 | 0.193 → 0.182 |
| `dumb-ledger` | 0.112 → 0.118 | 0.146 → **0.166** | 0.114 → 0.120 |
| `full-ledger` | 0.119 → **0.115** | 0.154 → 0.151 | 0.138 → 0.133 |
| `random-rank` | 0.108 → 0.113 | 0.128 → 0.132 | 0.118 → 0.122 |

**One arm moved and it is the one that mattered.** `full-ledger` diffuse barely moved
(0.154 → 0.151). `stateless-max` diffuse went **0.088 → 0.141**. The 29–0–1 was against an opponent
that was worse than chance on this stratum, and it no longer is.

### Why, measured — and it is not what I first guessed

First hypothesis: the ASR fix. A per-call maximum lives on the single loudest extracted signal, so
un-damaging 21.8% of quotes should help it most. **Tested and false.** The old generator with
`asr_error_rate=0.0`, 30 seeds × 1500: `stateless-max` diffuse **0.079**, record still 28–1–1. ASR
was not carrying it.

What actually changed, at 1500 customers, diffuse arcs only:

| | before | after |
|---|---|---|
| mean max extracted confidence, **all** diffuse customers | 0.329 | 0.292 |
| mean max extracted confidence, diffuse customers **with an outcome** | 0.320 | **0.341** |

**Before Phase C, a diffuse customer's loudest extracted signal was slightly *anti*-correlated with
their outcome** (0.320 for the outcome group against 0.329 overall). Ranking by it was worse than
useless on that stratum, which is what a 0.088 recall against a 0.132 chance floor means. After, it
is positively correlated (0.341 against 0.292) and the per-call maximum performs like the other arms.

The proximate cause is a change in which fragments the planner reaches for — the complaint pool grew
14 → 19, six fragments were reworded, and eleven are now position-gated — interacting with the
offline reader's very uneven per-fragment coverage, which this repo has already published as its
binding constraint (1 of 32 blind-authored fragments; 4 / 112 on real CFPB text). **I have not proved
that chain end to end.** What is measured is the sign flip in the table above, and that the ASR fix is
not responsible.

**How to say this out loud.** A large part of the pre-registered win was measuring an opponent that
the corpus happened to cripple, and a more realistic corpus removed the crippling. The ledger's
remaining wins are the ones against the other *aggregation* strategies — `stateless-top2` and
`window3-top2` are now **30–0–0** clean sweeps, up from 26–2–2 — and it is now closer to beating
chance on diffuse arcs than it was (p=0.076 against p=0.345), which is the comparison
`state-of-play.md` already flags as the weakest one. It also now **loses to `dumb-ledger` on diffuse
arcs** (7–18–5, p=0.043): unbounded memory with no decay, corroboration or escalation beats the full
mechanism on the stratum the full mechanism is for. That is a new finding and it is not a good one.

### Offline reader, same config, n=1500

| | before | after |
|---|---|---|
| extraction recall (shipped knobs) | 0.2464 (708 / 2873) | 0.2285 (617 / 2700) |
| strict recall, knobs off, n=400 | 197 / 730 = 0.2699 | 184 / 663 = 0.2775 |
| unplanted extractions | 332 | 296 |

---

## 6. Item 8 was built, measured, and not shipped

`Fragment.paraphrases` exists and every one of the 67 fragments has two — 201 surfaces where there
were 67. The shipped policy (`_surface`) is **canonical first, paraphrase on repeat within an arc**,
which is what fixes item 7 and nothing else.

The plan's item 8 wanted the surface varied *across* customers too. That was built: rotate all three
surfaces uniformly. Measured:

| policy | offline strict recall (n=400) | Northwind stream crossings (44 customers) |
|---|---|---|
| canonical first (**shipped**) | 0.2775 (184 / 663) | 0 |
| rotate all three surfaces | **0.1972 (139 / 705)** | **0** |
| — canonical surfaces within that run | 0.31 (69 / 222) | |
| — paraphrase surfaces within that run | **0.145 (70 / 483)** | |

Two thirds of every planting becomes prose the lexicon was not co-developed with, and the reader
finds 14.5% of it. That is the same effect already published as *"the offline lexicon finds 1 of the
32 newly-authored fragments"*, applied to the whole corpus at once. **Not shipped.** The
non-destructive version of item 8 is more fragments, not more wordings of the same ones, and it costs
the same recall on the new ones — that is a call for the owner, priced here rather than made here.

Also worth stating: the Northwind stream produced **1** crossing on the offline reader before Phase C
and **0** after. That surface is recorded with keyed Haiku, so it is not a demo regression, but the
test fixture that depended on it was an `IndexError` away from failing for as long as it had existed;
it now runs at 300 customers.

---

## 7. What is still weak

1. **Live conversations take six discrete lengths (9, 11, 13, 15, 17, 19) and 411 of 933 are 15, and every one is strictly alternating.** Nobody
   interrupts, nobody talks over anybody, nobody says two things in a row. The plan asked for zero
   customer→customer runs and that is what it got; a real corpus has some. The length distribution is
   six discrete values because a topic holds three follow-ups and asides are capped at two. More
   follow-ups per topic is the fix and it is pure authoring.
2. **A planted fragment is spoken register even inside a written complaint.** *"How long does it take
   to get a full statement history exported?"* is a paragraph of a complaint letter in
   `CUST-0008-C4`. The evidence quote must be verbatim, and every fragment was authored for speech.
   Written variants of the 67 fragments would fix it, at the recall cost measured in §6.
3. **`ce-s1` is nearly extinct.** *"This is the fourth time I've called"* needs a fourth contact and a
   broken undertaking, so it is planted **3 times per 1,500 customers**, against 34 before. That is
   the honest rate for that sentence and the loudest complaint fragment is now effectively `ce-s4`
   (0.89). If the demo wants the four-times line, the arc length distribution has to change, not the
   gate.
4. **A synthetic false fire can land on the security answer.** `earshot demo --customers 3000` prints
   `heard: "Postcode's the same one, ends 7QB."` as evidence for a case, because the extractor's
   `false_fire_rate` picks uniformly among customer turns and the verification answer is now one.
   It is *supposed* to be wrong — that is what a false fire is — but it is on the most-looked-at
   string in the product. Teaching `extract.py` to skip it would breach the separation rule; making
   `demo` prefer a customer whose crossing is carried by seeded signals would not. Owner's call.
5. **The complaint length distribution has no tail.** 59–217 words against the CFPB sample's
   11–888 (median 155, p90 354). Median 139 is close; the shape is not.
6. **The channel mix is unchanged at a third complaints.** `02-reconciliation.md` §4.6 recommends
   keeping the name, reweighting the mix, and saying in the README that the complaint share is
   deliberately inflated so the stratum is measurable at n=1,500. Not done — out of the eight items.
7. **Silence is still not in the corpus.** Every arc conversation carries a plant (0 / 663 empty).
   `04-plan.md`'s recommendation is a declared second arm, pre-registered, not a substitution. Not
   done — it is an experiment, not a fix, and it is the owner's to declare.

---

## 8. What the orchestrator has to do next

1. **`benchmarks/cfpb/PROTOCOL.md` is pre-registered and cites the published synthetic recall of
   0.681 (496 / 728), and this change moves it.** I did not edit it, per the working agreement.
   `working-agreements.md` is explicit that a corpus moving under a pre-registered figure is a
   **re-registration, not a refresh**. Same for the pre-registered diffuse headline, which did not
   just move — it disappeared.
2. **Republish, in order:** README's four comparison tables and the reader table → the one-pagers →
   `tools/ui_fixture.py` and `tools/stream_fixture.py` (both offline and free) → then, and only then,
   the keyed arms: AT-57 verdict accuracy (~$1.50) and AT-58 routing, then reader coverage.
3. **`ui/data.js` and the stream fixture carry the old prose** — 21 instances of "That's now updated
   on our side.", 25 of "Thanks for holding", 27 of the recording notice. Regenerating them is free
   and does not need spend; it is Phase B item B1, still outstanding.
4. **Decide item 8 and item 4 (channel mix)** against the prices in §6 and §7.
