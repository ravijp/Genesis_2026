# Working agreements

Every rule here was bought with a mistake made on this project, most of them on 2026-08-09. They are
written as rules because the same errors kept recurring in different disguises. Read this before
changing anything; add to it when something new bites.

Jira specifics live in [jira-conventions.md](jira-conventions.md).

---

## 1. Evaluation

**Never publish a number from a single dataset.** One 400-customer run has ~50 outcome customers, so
every recall is an integer over 50 and arms one or two customers apart look different but are not. We
published "our thesis fails" off a difference of **one customer**, and it went into the README and a
committee brief before anyone did the arithmetic. Use `earshot sweep`; `earshot run` prints its own
warning and exists for debugging.

**Always show the denominator.** A rate without its integers hides its own sample size. Every table we
publish carries `hits / outcomes`.

**Pre-register the headline, then respect it.** We run 14 pairwise comparisons with no multiplicity
correction. One landing just under `p=0.05` is a hint. The diffuse-stratum comparison is the declared
headline; everything else is exploratory and gets labelled that way.

**Never tune until it wins.** If a mechanism does not earn its place in an ablation, remove it or
justify it — do not search parameters until the number turns. Our decay, corroboration and channel
weighting still contribute nothing over a plain count, and that is written down rather than tuned away.

**The baseline must be the strongest fair version.** Same model, same prompt, same thresholds; ablate
one thing. A strawman comparison invalidates everything downstream, and it is the first thing a
technical judge probes.

---

## 2. Ground truth and honesty guards

**Author the answer key before the text.** Deterministic code decides what is true; generation only
writes prose around it. The key never comes from a model.

**Guard the answer key at two levels, because one is not enough.**

- *Imports* — nothing on the path from conversation to decision may import the generator, its lexicon,
  or a ground-truth type. `tests/test_separation.py`.
- *Data* — nothing may receive a **value** that encodes a ground-truth field.
  `tests/test_no_answer_key_leak.py`.

The second exists because the leak we actually had walked straight past the first: a customer's risk
was exactly `0.0` for everyone who was fine and `≥0.55` for everyone who was not, handed to the agent's
tools as a plain float. No import, no failure, and the agent could separate real cases from decoys
without reading a word.

**A value that correlates with the answer is fine. A value that recovers it is not.** Real distress
should show up in an account — that is signal. The test asserts separability stays near the base rate,
not at it.

**Keep the offline path deliberately weaker, and publish how much weaker.** "It misses 32% of planted
signals and the result holds anyway" is a stronger position than a matcher that scores itself
perfectly. Never align the extractor's vocabulary to the generator's.

---

## 3. Demos

**Never derive a threshold from the answer.** Our demo computed the alert threshold from the final
score, which guaranteed the dramatic moment for any customer we picked. Thresholds come from the same
operating point the evaluation uses.

**Run the comparison; do not narrate it.** We printed a claim about what a per-call tool "would have
done" beside an arm that was never executed.

**Beware the tautology.** After fixing the above, the demo *selected* customers where the comparison
never fires and then announced that the comparison never fired. If a filter guarantees your conclusion,
the conclusion is not a result — report the population ratio instead.

**Say so when the beat fails.** A demo that cannot report its own failure is a slideshow.

---

## 4. Documents

**A number lives in exactly one place, and everywhere else points at it.** We corrected the README and
left the committee brief contradicting it — twice. When a number changes, `grep` the repo for the old
one before committing.

**Retract in writing; never quietly overwrite.** Two retractions are in the README with what was wrong
and why. That is worth more than a clean-looking document.

**Every claim must be enforced by something.** If a doc says "enforced", "always", "never" or "O(1)",
either a test or the code makes it true, or the sentence changes. We claimed a cost cap that was never
passed, a groundedness metric that was zero by construction, and character-level evidence spans that
the schema does not carry.

**Check the commands in your own README run.** Ours referenced a package name that no longer existed
and a `.env.example` that did not.

**No arguing with the reader.** Architecture docs describe the system; they do not cite the rubric,
congratulate the authors, or re-litigate a decision. If a sentence exists to persuade, cut it.

---

## 5. Tests

**Assert the property, not the label.** A test checked `stopped_because == "cost_cap"` while the run
had spent $0.30 against a $0.25 cap — it locked the breach in as correct. Assert the money.

**A test that would pass with the feature deleted is worse than no test**, because it buys false
confidence.

**Every fix gets a test that fails without it.** Reverting one token reopened the answer-key leak with
87 of 87 tests green.

**Guards discover their surface, they do not list it.** A hand-maintained list of files to check is one
forgotten line from a hole. Glob for them, and assert the discovery is non-empty so it cannot pass
vacuously.

---

## 6. Bulk and scripted changes

**Read the full output of every bulk operation.** A Jira script printed only its tail; 37 delete calls
had failed with 403 and the board carried two complete parallel backlogs, with conflicting statuses on
the same work, for hours.

**Verify the end state, not the intent.** Count what is there afterwards and print the counts.

**Prefer updating to creating** where deletion needs a permission you do not have. On this project
neither the token nor the account can delete a Jira issue.

**Run a script once.** Paging its output by running it twice created duplicate tickets we then could
not remove.

---

## 7. Delegation and review

**Red team the things that would be expensive to get wrong** — the core experiment, the honesty
guards, anything that will be on screen. Give the reviewer permission to conclude the work is wrong,
and ask it to *verify empirically* rather than by reading.

**Do not delegate judgement-heavy authoring.** Sweeps, searches and adversarial review parallelise
well; design decisions and the numbers we stand behind do not.

**Reviewers are wrong sometimes — verify before acting.** One review reported that every Jira
description was empty; the search endpoint simply does not return description bodies. Another was
right about the direction of a result but wrong about its significance. Check the claim, then act.

**Re-review after fixing.** The pass that verified six fixes found four new problems, including that
the module written to fix the worst one was unreachable from any command.

---

## 8. What we do not chase

Originality is 15% of the score and impact × depth × feasibility is 75%. Time spent proving nobody has
ever built something adjacent is time not spent on the things that carry the entry. When a novelty
claim turns out to be inaccurate — as ours did, against a product that shipped before our submission —
narrow the claim honestly, put the surviving mechanic on screen, and move on.

Corpus realism, statistical machinery beyond what supports the headline, and UI polish all feel
productive and score close to nothing before the demo. Deliverables the competition names explicitly do
score.
