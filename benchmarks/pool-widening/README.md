# Pool widening — authored, measured, and deliberately not wired in

56 new corpus fragments that bring all four `PLANTS` pools from 8/8/4/4 to 20/20/20/20. They are
**not** spliced into `src/earshot/corpus_lexicon.py`. Splicing them is a one-line operation and it is
blocked on the extractor, for the reason measured below.

## Why they exist

Fragments are planted **without replacement** within a customer's arc (`corpus.py`, the `used` set),
so the scarcest pool is a hard ceiling on how many signals any arc can carry however long it gets.
With `complaint_escalation` and `life_event` at 4 fragments, a customer with 20 conversations still
carries at most 4 signals. That ceiling — not corpus realism — is what makes the history-length
question unaskable: *does never-discard buy anything over a cheap bounded window as arcs lengthen?*
(`stateless-top2` and `window3-top2` currently beat the full ledger on its own pre-registered stratum,
`7-21-2`, `p=0.013`.)

## How they were authored, and why not by the main session

By a separate author with **no sight of `extract_lexicon.py`**. This is not ceremony. The project's
honest miss rate depends on the corpus vocabulary (pass A) and the extractor's cue vocabulary (pass B)
having been written independently, so that their overlap is accidental. The session driving this work
had read pass B in detail while running AT-43 and was therefore disqualified from writing pass A. Two
fragments the author itself flagged as sitting too high in the weak band (`le-w3`, `le-w6`) were left
**unedited** for the same reason: a pass-B-contaminated editor tuning pass A text reintroduces exactly
the coupling the blind authoring existed to prevent.

## What splicing them measured — the reason they are parked

At 400 customers, with the extractor and rates the published pipeline uses:

| fragment set | caught | rate |
|---|---|---|
| the original 24 | 82 / 154 | **0.5325** |
| the new 56, blind-authored | 22 / 624 | **0.0353** |
| overall extraction recall | | 0.1337 (was 0.681) |

**0.0353 here against 0.0357 on real CFPB narratives** (`benchmarks/cfpb/`). The same number, from two
completely different directions.

That matters more than the pool widening does. AT-43 left genre mismatch open as an alternative
explanation — written regulator complaints are not spoken calls. These fragments *are* spoken UK
retail-bank utterances in exactly the target genre, written to the same four construct definitions,
and the extractor reads 3.5% of them. **Genre is not the explanation.** The explanation is that a
lexicon of 26 literal regexes only reads prose it was co-developed with, and the published 0.681
measures that co-development rather than the extractor's ability to read a customer.

Consequence, and the reason nothing is wired in: at 0.13 overall recall there is too little extracted
signal for the comparison arms to differentiate — `stateless-top2` collapses into `stateless-max` on
every seed, which `tests/test_sweep.py` catches. Splicing today would invalidate every published
number and produce a null history-length result caused by the reader rather than by the ledger.

## To resume

1. Fix the reader first. `benchmarks/cfpb/out/results.json` names the 24 cues that never fired, and
   `benchmarks/cfpb/out/gold.jsonl` is a 150-document marked development set. Do **not** tune cues
   against either of those alone — that is fitting the test set, and these 56 fragments are the
   held-out check that catches it.
2. Splice `fragments.py` into the `PLANTS` tuple in `corpus_lexicon.py`.
3. Re-measure extraction recall and move `RECALL_BAND` in `tests/test_separation.py` **deliberately,
   after measuring** — never widen it to make a test pass.
4. Re-run everything: every published number moves, and both answer-key guards need re-validating.
5. Then `earshot sweep --conversations-per-customer` at `(2,5)` / `(4,9)` / `(8,20)`, 30 seeds, and
   publish the curve. The CLI already refuses a range wider than the scarcest pool.
