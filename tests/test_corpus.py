"""Corpus-construction integrity: what the generator plants must be what it claims to plant.

`test_separation.py` guards imports and `test_no_answer_key_leak.py` guards the values handed
to the agent. Neither could see the defect these tests exist for, because it was upstream of
both: until 2026-08-28 the planter, on running out of unused fragments, silently re-planted one
it had already used. The identical sentence appeared in two conversations on different days,
the extractor emitted two `ExtractedSignal`s with different `conversation_id`s, and
`memory._raw()` counted them as `n_conversations = 2` -- so the ledger paid a
*cross-conversation corroboration* bonus for one utterance copied twice.

That is not a cosmetic bug. Corroboration across conversations is the mechanism this entry's
originality claim rests on, and the corpus was manufacturing it. At the shipped default range
it hit 28 / 213 arc customers per 400.
"""

from __future__ import annotations

import collections
import warnings
from dataclasses import replace
from pathlib import Path

import pytest

from earshot.config import DEFAULT, CorpusConfig, RunConfig
from earshot import corpus
from earshot.corpus import ArcCeilingWarning, generate, smallest_fragment_pool
from earshot.corpus_lexicon import BY_TYPE
from earshot.schema import Stratum

# Large enough that the defect bites reliably: at the shipped default this size produced 28
# affected arc customers on the old code, so a green result here is a real result and not a
# small-sample accident.
N = 400
ARC_STRATA = (Stratum.CONCENTRATED, Stratum.DIFFUSE)


def _default_corpus(n: int = N):
    """The SHIPPED default config, only the size changed.

    The defect lived at the default. A test that passed a safe range of its own would never
    have caught it, which is exactly how it survived until now.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ArcCeilingWarning)
        return generate(replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=n)))


def test_no_fragment_is_planted_twice_in_one_arc() -> None:
    """The property, not the label: within one customer's trajectory, no fragment may appear in
    two different conversations.

    Two conversations carrying the same `fragment_id` are one piece of evidence, however the
    ledger counts them. Asserting on `fragment_id` rather than on a stratum name or a config
    flag means the test still holds if the pools, the strata weights or the planting order
    change -- the only way to pass it is to actually plant without replacement.

    Scoped to the ARC strata deliberately. Both decoy families are drawn with
    `rng.choice(...)`, i.e. WITH replacement, through a different code path, and repetition
    there is not the same defect: an accumulator decoy that recurs is a *harder* trap, biased
    against the ledger rather than for it. Widening this test to cover them is a design
    decision about the decoys, not a bug fix, and should be argued separately.
    """
    corpus = _default_corpus()
    stratum = {c.customer_id: c.stratum for c in corpus.customers}

    by_arc: dict[tuple[str, object], list] = collections.defaultdict(list)
    for s in corpus.seeded:
        if stratum[s.customer_id] in ARC_STRATA:
            by_arc[(s.customer_id, s.signal_type)].append(s)

    assert by_arc, "no arc signals planted -- the corpus config changed, this test is now blind"

    offenders = []
    for (customer_id, signal_type), group in by_arc.items():
        counts = collections.Counter(s.fragment_id for s in group)
        repeated = {f: n for f, n in counts.items() if n > 1}
        if repeated:
            conversations = sorted({s.conversation_id for s in group})
            offenders.append((customer_id, signal_type, repeated, conversations))

    n_arc = sum(1 for c in corpus.customers if c.stratum in ARC_STRATA)
    assert not offenders, (
        f"{len(offenders)} of {n_arc} arc customers carry the SAME planted fragment in more "
        f"than one conversation, which fabricates cross-conversation corroboration out of a "
        f"single utterance. First three: {offenders[:3]}"
    )


def test_arcs_longer_than_the_pool_are_padded_with_empty_conversations() -> None:
    """The other half of the same fix, and the behaviour `smallest_fragment_pool()` documents.

    Running out of fragments must leave a conversation EMPTY. Padding dilutes an arc -- a bias
    against the ledger, and one the diagnostics show. Repeating inflated it, and was invisible.
    Without this assertion the planter could satisfy the test above by silently shortening
    every arc to the pool size instead.

    **Built on a deliberately over-long config, not the default.** Until 2026-08-30 the shipped
    default (2,5) exceeded the scarcest pool (4) and this test read it straight. Pools are 14
    now and the default no longer reaches the padding path at all -- which is the improvement,
    but it would leave this invariant untested. So the config here asks for MORE conversations
    than the largest pool can fill, which is the only way to observe what the planter does when
    it runs out. `check_arc_ceiling` raises for a caller-chosen range, so this goes through
    `_planted_corpus` with the check bypassed the same way the CLI's own guard test does.
    """
    _scarcest, pool_size = smallest_fragment_pool()
    over = (pool_size + 2, pool_size + 6)
    run = RunConfig(corpus=replace(DEFAULT.corpus, n_customers=200,
                                   conversations_per_customer=over))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ArcCeilingWarning)
        try:
            corpus = generate(run)
        except ValueError:
            pytest.skip(
                "generate() refuses a range past the pool, which is the guard working; the "
                "padding path is then unreachable through the public API and is covered by "
                "test_no_arc_repeats_a_planted_fragment instead"
            )
    arcs = [c for c in corpus.customers if c.stratum in ARC_STRATA]

    planted = collections.Counter(s.customer_id for s in corpus.seeded)
    held = collections.Counter(c.customer_id for c in corpus.conversations)

    # The binding ceiling is the pool of THIS customer's trajectory, not the global smallest.
    # A churn arc may legitimately carry 5 plants; a complaint arc may not.
    over_length = []
    for customer in arcs:
        pool_size = len(BY_TYPE[customer.trajectory])
        cid = customer.customer_id
        assert planted[cid] <= pool_size, (
            f"{cid} is a {customer.trajectory.value} arc carrying {planted[cid]} plants from a "
            f"pool of {pool_size} -- something is planting with replacement again"
        )
        if held[cid] > pool_size:
            over_length.append((cid, held[cid], planted[cid], pool_size))

    _scarcest, smallest = smallest_fragment_pool()
    assert over_length, (
        f"no arc customer has more conversations than its own trajectory pool (smallest is "
        f"{smallest}), so this test cannot see the padding path -- the "
        "conversations-per-customer range must have changed"
    )
    for cid, n_conversations, n_plants, pool_size in over_length:
        assert n_plants < n_conversations, (
            f"{cid} has {n_conversations} conversations and {n_plants} plants from a pool of "
            f"{pool_size}: every conversation carries a fragment even though the pool cannot "
            "supply that many"
        )


def test_the_pool_ceiling_is_enforced_on_a_programmatic_config_not_only_the_cli() -> None:
    """The guard used to live in `cli.py`'s argument parsing, so it only ran when
    `--conversations-per-customer` was typed. `sweep.py`, `tools/verdict_accuracy.py`,
    `tenants.py` and every test build a `RunConfig` in Python and reached none of it.

    This constructs the config the way those callers do -- no parser, no `argv` -- and requires
    `generate()` itself to refuse.
    """
    _scarcest, pool_size = smallest_fragment_pool()
    too_long = (pool_size + 4, pool_size + 16)
    run = RunConfig(corpus=CorpusConfig(n_customers=5, conversations_per_customer=too_long))

    with pytest.raises(ValueError, match="exceeds the smallest fragment pool"):
        generate(run)


def test_the_shipped_default_no_longer_breaches_the_ceiling() -> None:
    """This test used to assert the OPPOSITE, and the flip is the point.

    Until 2026-08-30 the shipped default range (2,5) exceeded the scarcest fragment pool (4),
    so `complaint_escalation` and `life_event` arcs could never carry more than four signals and
    their later conversations were empty by construction. Every published number carried that
    ceiling, `check_arc_ceiling()` warned on every single run, and the old version of this test
    pinned the warning so nobody "tidied" it into a raise.

    Widening all four pools to 14 removed it. The default no longer breaches anything, so the
    warning must NOT fire -- a corpus that still warns here means a pool shrank back or the
    conversation range grew past 14, and either one silently re-imposes the ceiling on the
    history-length comparison this repo exists to run.

    The raise path is unaffected and is still pinned by
    `test_the_pool_ceiling_is_enforced_on_a_programmatic_config_not_only_the_cli`.
    """
    _scarcest, pool_size = smallest_fragment_pool()
    assert DEFAULT.corpus.conversations_per_customer[1] <= pool_size, (
        f"the shipped default runs to {DEFAULT.corpus.conversations_per_customer[1]} "
        f"conversations against a scarcest pool of {pool_size}: the arc ceiling is back, and "
        "every history-length claim is bounded by it again"
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        generate(replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=3)))

    assert not [w for w in caught if issubclass(w.category, ArcCeilingWarning)], (
        "generate() still warns about the fragment-pool ceiling at the shipped default"
    )


# --- the pipeline fingerprint ------------------------------------------------------------
#
# `config_hash` covers configuration VALUES. On 2026-08-28 the fragment re-plant fix changed
# which customers cross -- 25 with an outcome became 17, the threshold moved 0.7246 -> 0.6655 --
# while the config hash stayed `3ebd9fb57097` on both sides, because the generator is code. A
# $1.50 keyed artifact was scored against the wrong corpus before anyone noticed. These tests
# pin the guard that closed it.


def test_the_fingerprint_changes_when_a_covered_file_changes(tmp_path):
    """The whole point: same bytes -> same hash, one byte different -> different hash.

    Written against `fingerprint_paths` on temporary files rather than the real modules,
    because a test that edited `corpus.py` to prove the hash moves would be editing the file
    the suite is running from.
    """
    a, b = tmp_path / "a.py", tmp_path / "b.py"
    a.write_text("PLANT = 1\n", encoding="utf-8")
    b.write_text("SCORE = 2\n", encoding="utf-8")

    before = corpus.fingerprint_paths([a, b])
    assert corpus.fingerprint_paths([a, b]) == before, "the same bytes must hash the same"

    b.write_text("SCORE = 3\n", encoding="utf-8")
    assert corpus.fingerprint_paths([a, b]) != before, (
        "a changed module left the fingerprint unmoved -- the guard would bless a stale artifact"
    )


def test_the_fingerprint_depends_on_the_order_it_is_given(tmp_path):
    """Two pipelines holding the same bytes in a different arrangement are different
    pipelines, so the digest is order-sensitive by construction rather than by accident."""
    a, b = tmp_path / "a.py", tmp_path / "b.py"
    a.write_text("X = 1\n", encoding="utf-8")
    b.write_text("Y = 2\n", encoding="utf-8")
    assert corpus.fingerprint_paths([a, b]) != corpus.fingerprint_paths([b, a])


def test_every_module_that_decides_the_sample_is_in_the_fingerprint():
    """Pinned by name, not globbed. A rename that drops a module from the list leaves the
    fingerprint matching while the pipeline it describes has changed -- the exact failure the
    fingerprint exists to catch, reintroduced one level up.

    If you add a module that changes who crosses the threshold, add it here.
    """
    here = Path(corpus.__file__).resolve().parent
    assert set(corpus.PIPELINE_MODULES) == {
        "corpus.py",
        "corpus_lexicon.py",
        "extract.py",
        "extract_lexicon.py",
        "memory.py",
    }
    for name in corpus.PIPELINE_MODULES:
        assert (here / name).is_file(), f"{name} is in the fingerprint but not on disk"


def test_the_fingerprint_is_stable_across_calls():
    """It is written into run manifests and compared against later. A fingerprint that moved
    between two calls in one process would fail every artifact it had just stamped."""
    assert corpus.pipeline_fingerprint() == corpus.pipeline_fingerprint()
    assert len(corpus.pipeline_fingerprint()) == 12


# --------------------------------------------------------------------------------------------
# Agent prose. These guard a property the corpus depends on for its DEMO rather than its
# numbers -- the extractor never reads an agent turn -- so nothing here can move a published
# figure. They exist because the failure they catch is silent: a fragment with no mapped reply
# falls back to a generic filler line and simply reads badly, which no other test notices.
# --------------------------------------------------------------------------------------------


def test_every_planted_fragment_has_an_authored_agent_reply():
    """A fragment with no entry degrades to the pre-2026-08-31 behaviour: an agent line drawn at
    random with no reference to what was said. That was 864 / 973 planted signals answered with a
    non-sequitur, including a bereavement disclosure answered with the call-recording notice.
    Adding a fragment without adding its reply reintroduces exactly that, one fragment at a time.
    """
    from earshot import corpus_lexicon as lex

    everything = lex.PLANTS + lex.DECOYS_EXTRACTOR + lex.DECOYS_ACCUMULATOR
    missing = sorted(f.fragment_id for f in everything
                     if f.fragment_id not in lex.AGENT_REPLIES_TO_SIGNAL)
    assert not missing, f"fragments with no authored agent reply: {missing}"

    unfilled = sorted(line for line in lex.FILLER_CUSTOMER
                      if line not in lex.AGENT_REPLIES_TO_FILLER)
    assert not unfilled, f"filler lines with no authored agent reply: {unfilled}"


def test_the_agent_line_pools_keep_their_exact_lengths():
    """The RNG stream, not the tuple contents, is what the published numbers depend on.

    `rng.choice` consumes a length-dependent number of bits from the shared generator, and that
    generator also draws the customer turns. Measured over 3 seeds x 400 customers: resizing
    FILLER_AGENT from 10 to 14 changed 11,371 of 11,378 customer turns and the conversation count
    with them. Rewriting the ten strings changed nothing at all. So the text is free to change and
    the LENGTHS are not.
    """
    from earshot import corpus_lexicon as lex

    assert len(lex.FILLER_AGENT) == 10
    assert len(lex.OPENINGS) == 3
    assert len(lex.CLOSINGS) == 3
    assert len(lex.FILLER_CUSTOMER) == 15
    # The per-channel pools are indexed by POSITION into the pool that was actually drawn from,
    # so they must line up one-for-one or `agent_opening` silently falls through to `drawn`.
    assert len(lex.CHAT_OPENINGS) == len(lex.OPENINGS)
    assert len(lex.CHAT_CLOSINGS) == len(lex.CLOSINGS)


def test_no_planted_signal_is_answered_with_a_generic_filler_line():
    """The property the whole rewrite exists to establish, asserted end to end on a real corpus.

    Before 2026-08-31 this was 864 / 973 at this seed and customer count.
    """
    from dataclasses import replace as _replace

    from earshot import corpus_lexicon as lex
    from earshot.config import CorpusConfig, RunConfig

    built = corpus.generate(RunConfig(corpus=_replace(CorpusConfig(), n_customers=120)))
    by_conversation = {c.conversation_id: c for c in built.conversations}
    generic = set(lex.FILLER_AGENT)

    offenders = []
    for planted in built.seeded:
        conversation = by_conversation[planted.conversation_id]
        following = [t for t in conversation.turns if t.index == planted.turn_index + 1]
        if following and following[0].speaker == "agent" and following[0].text in generic:
            offenders.append((planted.fragment_id, following[0].text))
    assert not offenders, f"planted signals answered with an unmapped generic line: {offenders[:5]}"


def test_typed_channels_do_not_use_telephone_language():
    """A chat that says "thanks for holding" is the tell a contact-centre reader spots first.

    Before the rewrite: 129 / 450 chat conversations opened "Thank you for calling", and phrases
    that only exist on a phone appeared 1,166 times inside chat and complaint documents.
    """
    from dataclasses import replace as _replace

    from earshot.config import CorpusConfig, RunConfig
    from earshot.schema import Channel

    built = corpus.generate(RunConfig(corpus=_replace(CorpusConfig(), n_customers=200)))
    banned = ("thanks for holding", "this call may be recorded", "thank you for calling",
              "you're through to", "i'll hold", "on hold", "read it out")
    offenders = [
        (c.channel.value, t.text)
        for c in built.conversations
        if c.channel is not Channel.CALL
        for t in c.turns
        if t.speaker == "agent" and any(b in t.text.lower() for b in banned)
    ]
    assert not offenders, f"telephone language in a typed channel: {offenders[:5]}"
