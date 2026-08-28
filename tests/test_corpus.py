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

import pytest

from earshot.config import DEFAULT, CorpusConfig, RunConfig
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
    """
    corpus = _default_corpus()
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


def test_the_shipped_default_warns_rather_than_raising() -> None:
    """The default range breaches the ceiling by one and has done so for every number published
    to date. Raising on it would break `sweep`, `demo`, the whole suite and the reproduction of
    every figure in the README -- an outage in place of a documented corpus limitation.

    So it warns, through a real `warnings.warn` a programmatic caller sees rather than a
    `print` only the CLI reached. Pinning this stops someone "tidying" it into a raise, and
    stops the warning being quietly dropped.
    """
    _scarcest, pool_size = smallest_fragment_pool()
    assert DEFAULT.corpus.conversations_per_customer[1] > pool_size, (
        "the shipped default no longer breaches the ceiling -- good, but this test is now "
        "asserting nothing. Delete it, and re-check whether the warning should become a raise."
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        generate(replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=3)))

    assert any(issubclass(w.category, ArcCeilingWarning) for w in caught), (
        "generate() did not warn about the fragment-pool ceiling at the shipped default"
    )
