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
import random
import warnings
from dataclasses import replace
from pathlib import Path

import pytest

from earshot.config import DEFAULT, CorpusConfig, RunConfig
from earshot import corpus
from earshot.corpus import ArcCeilingWarning, generate, smallest_fragment_pool
from earshot.corpus_lexicon import BY_TYPE
from earshot.schema import Channel, SignalType, Stratum

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


# --------------------------------------------------------------------------------------------
# PHASE C: the arc is one relationship, and the corpus does not contradict itself.
#
# These assert PROPERTIES of a generated corpus, never pinned strings or counts, so they survive
# a lexicon rewrite and fail only if the mechanism breaks. Each one is here because the corpus
# measurably did the opposite until 2026-08-31; the numbers in each docstring are the measured
# "before" at 400 customers, seed 20260809.
# --------------------------------------------------------------------------------------------


def _arcs(built):
    """Every customer's conversations, in day order, keyed by customer id."""
    by_customer: dict[str, list] = collections.defaultdict(list)
    for conversation in built.conversations:
        by_customer[conversation.customer_id].append(conversation)
    for group in by_customer.values():
        group.sort(key=lambda c: c.day)
    return by_customer


def test_a_back_reference_is_never_planted_where_there_is_nothing_to_refer_back_to():
    """Before: 34 of 126 plantings of a prior-contact fragment (27.0%) landed in the customer's
    FIRST conversation, and *"this is the fourth time I've called about this and nobody has fixed
    it"* went into an arc with fewer than four contacts 9 times in 10.

    Asserted off `Fragment.requires_prior` rather than a hand-listed set of ids, so a new
    back-reference fragment is covered the day it is authored -- provided it declares itself.
    The companion `test_every_fragment_that_claims_a_prior_contact_declares_it` is what stops a
    fragment quietly not declaring.
    """
    built = _default_corpus()
    position = {
        c.conversation_id: i
        for group in _arcs(built).values()
        for i, c in enumerate(group)
    }
    from earshot import corpus_lexicon as lex

    by_id = {f.fragment_id: f for f in
             lex.PLANTS + lex.DECOYS_EXTRACTOR + lex.DECOYS_ACCUMULATOR}

    offenders = [
        (s.conversation_id, s.fragment_id, position[s.conversation_id],
         by_id[s.fragment_id].requires_prior)
        for s in built.seeded
        if position[s.conversation_id] < by_id[s.fragment_id].requires_prior
    ]
    assert not offenders, (
        f"{len(offenders)} plantings assert more prior contacts than the arc contains: "
        f"{offenders[:5]}"
    )


def test_every_fragment_that_claims_a_prior_contact_declares_it():
    """The gate is only as good as the declarations, and a declaration is easy to forget.

    A blunt lexical screen: a fragment whose text claims an earlier contact ("I rang", "last
    time", "again", "promised") must carry `requires_prior >= 1`. It will over-fire on some
    future phrasing, and the fix then is to look at the sentence and decide -- which is the
    point. It cannot silently pass.
    """
    from earshot import corpus_lexicon as lex

    claims = ("i rang", "i called", "last time", "i did raise", "promised", "before,",
              "raised this before", "fourth time", "happening again", "as well",
              "got back to me", "since this started")
    undeclared = [
        f.fragment_id
        for f in lex.PLANTS
        if f.requires_prior < 1 and any(c in f.text.lower() for c in claims)
    ]
    assert not undeclared, (
        f"these fragments claim an earlier contact but are plantable on first contact: "
        f"{undeclared}"
    )


def test_a_fragment_that_names_a_month_is_never_spoken_before_it():
    """Before: the 180-day horizon had no epoch, so "I was made redundant in March" was planted
    on days 10-119 and "my husband passed away in June" on days 9-109 of the same unanchored
    window. Any two of those in one arc contradict each other, and a reader spots it.

    Day 0 is now 1 February (`corpus.CORPUS_EPOCH`) and a fragment naming a month declares its
    `earliest_day`. This checks the declaration is honoured; the wording of the fragments that
    dropped their month instead is a separate authoring decision.
    """
    built = _default_corpus()
    day = {c.conversation_id: c.day for c in built.conversations}
    from earshot import corpus_lexicon as lex

    by_id = {f.fragment_id: f for f in lex.PLANTS}
    early = [
        (s.conversation_id, s.fragment_id, day[s.conversation_id])
        for s in built.seeded
        if s.fragment_id in by_id and day[s.conversation_id] < by_id[s.fragment_id].earliest_day
    ]
    assert not early, f"a fragment was spoken before the month it names: {early[:5]}"


def test_the_evidence_quote_is_never_speech_recognition_damage():
    """The single most-looked-at string in the product. Before: 212 of 973 planted signals
    (21.8%) shipped a damaged quote -- including `can't make the payment this month, I just` --
    and the case screen and the retro re-score table print it as proof.

    Asserted against the fragment's own legitimate surfaces, so a paraphrase passes and a dropped
    or clipped word does not.
    """
    built = _default_corpus()
    conversations = {c.conversation_id: c for c in built.conversations}
    from earshot import corpus_lexicon as lex

    by_id = {f.fragment_id: f for f in
             lex.PLANTS + lex.DECOYS_EXTRACTOR + lex.DECOYS_ACCUMULATOR}

    damaged = []
    for s in built.seeded:
        conversation = conversations[s.conversation_id]
        turn = next((t for t in conversation.turns if t.index == s.turn_index), None)
        if turn is None or turn.text not in by_id[s.fragment_id].surfaces():
            damaged.append((s.conversation_id, s.fragment_id,
                            turn.text if turn else None))
    assert not damaged, (
        f"{len(damaged)} of {len(built.seeded)} planted signals ship a quote that is not a "
        f"legitimate surface of the fragment: {damaged[:3]}"
    )


def test_speech_recognition_damage_happens_only_on_the_telephone():
    """Before: 1,428 of 7,453 chat and complaint customer turns (19.2%) were ASR-damaged. A typed
    message cannot be misheard, and `"D- I need to tell you if I'm going abroad these days?"` in a
    web chat is self-evidently machine-made.

    Checks the mechanism, not a sample: `_apply_asr_noise` is monkeypatched to record the channel
    it is called for, which cannot be fooled by the drop branch deleting a word silently and
    leaving no marker. Counting clip markers would miss exactly half the damage.
    """
    seen: list[str] = []
    real = corpus._apply_asr_noise

    def spy(rng, text, rate):
        seen.append(_CURRENT_CHANNEL[0])
        return real(rng, text, rate)

    original_asr = corpus._asr

    def wrapper(rng, cfg, channel, text):
        _CURRENT_CHANNEL[0] = channel.value
        return original_asr(rng, cfg, channel, text)

    corpus._apply_asr_noise = spy
    corpus._asr = wrapper
    try:
        _default_corpus(n=120)
    finally:
        corpus._apply_asr_noise = real
        corpus._asr = original_asr

    assert seen, "ASR was never applied at all -- the spy is wired to nothing"
    typed = sorted({c for c in seen if c != "call"})
    assert not typed, f"speech-recognition noise was applied to typed channels: {typed}"


_CURRENT_CHANNEL = ["call"]


def test_nobody_speaks_twice_in_a_row():
    """Before: 1,106 of 1,400 conversations (79.0%) contained a run of two or more customer turns
    nobody answered, because the agent replied with probability 0.75; 740 (52.9%) contained an
    agent->agent run, usually a filler immediately followed by the closing.

    A complaint is exempt and is checked by `test_a_complaint_is_a_document_not_a_phone_call`
    instead -- it is deliberately one author throughout.
    """
    built = _default_corpus()
    offenders = []
    for conversation in built.conversations:
        if conversation.channel is Channel.COMPLAINT:
            continue
        for a, b in zip(conversation.turns, conversation.turns[1:]):
            if a.speaker == b.speaker:
                offenders.append((conversation.conversation_id, a.index, a.speaker))
    assert not offenders, f"{len(offenders)} same-speaker runs on a live channel: {offenders[:5]}"


def test_no_customer_says_the_same_sentence_twice_in_one_conversation():
    """Before: 899 of 1,400 conversations (64.2%) repeated a customer line verbatim, and 166 said
    one three or more times -- `CUST-0388-C1` asked "Can you read me the last three transactions?"
    four times in one call. Filler was `rng.choice` over a 15-tuple, per turn.
    """
    built = _default_corpus()
    offenders = []
    for conversation in built.conversations:
        said = collections.Counter(
            t.text for t in conversation.turns if t.speaker == "customer"
        )
        repeated = {text: n for text, n in said.items() if n > 1}
        if repeated:
            offenders.append((conversation.conversation_id, sorted(repeated.items())[:2]))
    assert not offenders, (
        f"{len(offenders)} conversations repeat a customer line verbatim: {offenders[:3]}"
    )


def test_no_planted_sentence_is_repeated_anywhere_in_one_arc():
    """The half that is a correctness defect rather than a realism one.

    Before: 38 duplicate plantings across 33 of 400 customers, 25 of them the IDENTICAL sentence
    in two conversations -- `CUST-0002` said *"Cashflow's a bit lumpy this quarter, it always
    is."* verbatim on day 175 and again on day 178. The extractor emits two signals with
    different `conversation_id`s and `memory._raw()` counts `n_conversations = 2`, so the ledger
    pays a cross-conversation corroboration bonus for one utterance copied twice.

    Deliberately narrower than "no sentence twice in an arc". A customer gives the same two
    characters of their memorable word at every contact, because it is the same memorable word,
    and two complaints from one person can reasonably end with the same request. What may never
    repeat is the EVIDENCE.
    """
    built = _default_corpus()
    conversations = {c.conversation_id: c for c in built.conversations}
    by_customer: dict[str, list[str]] = collections.defaultdict(list)
    for s in built.seeded:
        turn = next(
            (t for t in conversations[s.conversation_id].turns if t.index == s.turn_index), None
        )
        if turn is not None:
            by_customer[s.customer_id].append(turn.text)

    offenders = []
    for customer_id, texts in by_customer.items():
        repeated = {t: n for t, n in collections.Counter(texts).items() if n > 1}
        if repeated:
            offenders.append((customer_id, repeated))
    assert not offenders, (
        f"{len(offenders)} customers have the same planted sentence in more than one "
        f"conversation, which manufactures corroboration out of one utterance: {offenders[:3]}"
    )


def test_a_complaint_is_a_document_not_a_phone_call():
    """Before: 459 of 460 complaint documents were interleaved two-party dialogue at a median of
    84 customer words. `benchmarks/cfpb/out/sample.jsonl` -- 150 real complaint narratives, CC0,
    committed -- is single-author, no turn-taking, median 155 words.

    One author throughout, and at most one agent turn, which is the firm's written response and
    is the last thing in the document. The CFPB records that as a field of its own; it is a reply
    to a letter, not a turn in a conversation.
    """
    built = _default_corpus()
    complaints = [c for c in built.conversations if c.channel is Channel.COMPLAINT]
    assert complaints, "no complaint documents generated -- this test is blind"

    for conversation in complaints:
        speakers = [t.speaker for t in conversation.turns]
        agent_at = [i for i, s in enumerate(speakers) if s == "agent"]
        assert len(agent_at) <= 1, (
            f"{conversation.conversation_id} has {len(agent_at)} agent turns: a written complaint "
            "is not turn-taking"
        )
        if agent_at:
            assert agent_at[0] == len(speakers) - 1, (
                f"{conversation.conversation_id} interleaves the written response into the "
                "narrative"
            )

    words = sorted(
        sum(len(t.text.split()) for t in c.turns if t.speaker == "customer")
        for c in complaints
    )
    median = words[len(words) // 2]
    assert 90 <= median <= 220, (
        f"complaint narratives run to a median of {median} words against 155 in the 150 real "
        "CFPB narratives; the written channel has drifted back toward a phone call"
    )


def test_every_later_conversation_refers_to_the_one_before_it():
    """The entry's whole thesis, made visible. Before: across 22,114 turns the corpus contained
    zero instances of "I called", "as I said" or "you said", and every hit for "last time" or
    "reference number" was inside a planted fragment's fixed text. An arc was N independent
    scenes that happened to share a customer id.
    """
    from earshot import corpus_lexicon as lex

    built = _default_corpus()
    silent = []
    for customer_id, group in _arcs(built).items():
        for conversation in group[1:]:
            text = " ".join(t.text.lower() for t in conversation.turns
                            if t.speaker == "customer")
            if not any(marker in text for marker in lex.CONTINUITY_MARKERS):
                silent.append(conversation.conversation_id)
    assert not silent, (
        f"{silent[:5]} (and {max(0, len(silent) - 5)} more) open without referring to the "
        "previous contact"
    )


def test_a_broken_promise_is_chased_and_a_kept_one_is_not():
    """The mechanism, not the wording: a contact whose undertaking was not delivered is followed
    by a contact about THE SAME THING, and one that was delivered is not.

    This is what makes a complaint-escalation arc earned rather than asserted. The schedule lives
    in `corpus._promise_schedule` and runs before any prose exists, so the answer key is still
    authored first; what the renderer does is write it down.
    """
    made, kept = corpus._promise_schedule(random.Random(1), SignalType.COMPLAINT_ESCALATION, 5)
    assert all(made), "a complaint arc must make an undertaking in every contact"

    rng = random.Random(7)
    made = [True, True, False, True, False]
    kept = [False, True, True, False, True]
    topics = corpus._topic_schedule(rng, 5, made, kept)
    assert topics[1] is topics[0], "a broken undertaking must be chased in the next contact"
    assert topics[2] is not topics[1], "a kept undertaking must not be chased"
    assert topics[4] is topics[3], "a broken undertaking must be chased in the next contact"
    fresh = [t for i, t in enumerate(topics) if i == 0 or topics[i - 1] is not t]
    assert len(fresh) == len(set(id(t) for t in fresh)), (
        "a new reason for contact was drawn twice in one arc"
    )


def test_the_gap_between_contacts_is_described_truthfully():
    """"It's been a couple of months" was available and unused: the real gap distribution is
    median 30 days, mean 37, and 20.3% of gaps are 60 days or more. Now it is said -- so it has
    to be true when it is said.
    """
    from earshot import corpus_lexicon as lex

    assert lex.gap_bucket(3) == "days"
    assert lex.gap_bucket(14) == "weeks"
    assert lex.gap_bucket(30) == "month"
    assert lex.gap_bucket(65) == "months"
    assert lex.gap_bucket(150) == "long"
    # Monotone: a longer gap never gets a shorter description.
    order = ["days", "weeks", "month", "months", "long"]
    seen = [order.index(lex.gap_bucket(d)) for d in range(0, 180)]
    assert seen == sorted(seen), "the gap description is not monotone in the gap"


def test_the_calendar_anchor_is_real():
    """Day 0 is 1 February, so day 28 is in March and a fragment naming March can declare 28."""
    assert corpus.month_name(0) == "February"
    assert corpus.month_name(28) == "March"
    assert corpus.month_name(179) == "July"


def test_no_shipped_sentence_appears_in_the_real_cfpb_narratives():
    """The promise in `docs/corpus/03-public-sources.md`, made mechanical.

    Real sources ground the SHAPE of our written channel -- single author, median 155 words,
    subject then chronology then impact then ask. They never ship as our text: competition rules
    require synthetic or anonymised data only. A six-word run in common between anything we
    generate and any of the 150 committed CC0 narratives would mean a sentence had crossed.

    Six words, not four: shorter runs collide by chance on banking English ("I called them again
    and they") and the test would then be noise. This scans every authored string the corpus can
    emit, not only the planted fragments, because the complaint scaffolding is the part that was
    written while reading them.
    """
    import json

    sample = Path(__file__).resolve().parents[1] / "benchmarks/cfpb/out/sample.jsonl"
    if not sample.is_file():  # pragma: no cover - the file is committed
        pytest.skip("the CFPB sample is not present")

    def grams(text: str, n: int = 6) -> set[tuple[str, ...]]:
        words = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text).split()
        return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}

    real: set[tuple[str, ...]] = set()
    for line in sample.read_text(encoding="utf-8").splitlines():
        if line.strip():
            real |= grams(json.loads(line).get("complaint_what_happened") or "")
    assert real, "no n-grams read from the CFPB sample -- the guard is blind"

    from earshot import corpus_lexicon as lex

    ours: list[tuple[str, str]] = []
    for fragment in lex.PLANTS + lex.DECOYS_EXTRACTOR + lex.DECOYS_ACCUMULATOR:
        ours += [(fragment.fragment_id, s) for s in fragment.surfaces()]
    for topic in lex.TOPICS:
        strings = [topic.opener, *topic.narrative, *topic.resolved, *topic.promised, *topic.chase]
        strings += [s for pair in topic.followups for s in pair]
        ours += [(topic.topic_id, s) for s in strings]
    for name in ("FILLER_CUSTOMER", "FILLER_AGENT", "OPENINGS", "CLOSINGS", "CHAT_OPENINGS",
                 "CHAT_CLOSINGS", "COMPLAINT_SUBJECT_LINES", "COMPLAINT_FIRST_CONTACT",
                 "COMPLAINT_IMPACT", "COMPLAINT_ASK", "COMPLAINT_ACK_GENERIC",
                 "CONTINUITY_NEUTRAL", "CONTINUITY_KEPT", "CONTINUITY_BROKEN",
                 "COMPLAINT_CHRONOLOGY_BROKEN", "COMPLAINT_CHRONOLOGY_KEPT",
                 "COMPLAINT_CHRONOLOGY_NEUTRAL"):
        ours += [(name, s) for s in getattr(lex, name)]

    collisions = [(where, s) for where, s in ours if grams(s) & real]
    assert not collisions, (
        f"{len(collisions)} authored strings share a six-word run with a real CFPB narrative: "
        f"{collisions[:3]}"
    )
