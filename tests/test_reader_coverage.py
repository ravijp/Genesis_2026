"""`tools/reader_coverage.py` — the sampling, the denominators, and the consequence step.

The measurement it exists for needs a keyed reader. What is testable without one is everything
that decides what the numbers MEAN, and each of these is a way the tool could report a confident
wrong answer:

* a sample that is not balanced, or that moves between runs, makes two arms incomparable;
* a denominator taken from what the reader FOUND rather than from what was PLANTED turns a
  reader that fires everywhere into a reader with perfect coverage;
* and the whole payoff rests on one property of `memory.py` — that evidence spread over more
  distinct conversations scores strictly higher — which is asserted here rather than assumed,
  because if it did not hold, "the model found more conversations" would imply nothing at all
  about who crosses.

**No test here reaches a network.** The model arm is exercised with `StubReader`, which
implements the `Extractor` protocol and holds no provider.
"""

from __future__ import annotations

import warnings
from dataclasses import replace

import pytest
import reader_coverage as rc

from earshot.config import DEFAULT, ScoringConfig
from earshot.corpus import ArcCeilingWarning, generate
from earshot.extract import OfflineLexiconExtractor, extract_all
from earshot.schema import Channel, Conversation, ExtractedSignal, SignalType

CUSTOMERS = 240


class StubReader:
    """Fires a caller-chosen signal type in a caller-chosen set of conversations, and nothing
    else. Same `Extractor` protocol surface as both real readers, no provider behind it."""

    name = "stub"

    def __init__(self, fire_in: set[str], signal_type: SignalType, confidence: float = 0.9):
        self.fire_in = fire_in
        self.signal_type = signal_type
        self.confidence = confidence

    def extract(self, conversation: Conversation) -> list[ExtractedSignal]:
        if conversation.conversation_id not in self.fire_in:
            return []
        return [
            ExtractedSignal(
                customer_id=conversation.customer_id,
                conversation_id=conversation.conversation_id,
                signal_type=self.signal_type,
                confidence=self.confidence,
                evidence_quote="stub",
                turn_index=0,
                day=conversation.day,
                channel=conversation.channel,
                cue_id="stub",
            )
        ]


@pytest.fixture(scope="module")
def corpus():
    run = replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=CUSTOMERS))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ArcCeilingWarning)
        return generate(run)


# -- sampling ---------------------------------------------------------------------------------


def test_the_sample_is_balanced_and_reproduces_from_the_seed(corpus) -> None:
    """Two arms are only comparable if they read the same conversations, and a sample that moves
    between runs cannot be compared with itself either."""
    first = rc.sample(corpus, 5)
    second = rc.sample(corpus, 5)
    assert [c.customer_id for c in first] == [c.customer_id for c in second]

    counts: dict[str, int] = {}
    for customer in first:
        counts[customer.trajectory.value] = counts.get(customer.trajectory.value, 0) + 1
    assert counts == dict.fromkeys(rc.TRAJECTORIES, 5)


def test_a_larger_sample_contains_the_smaller_one(corpus) -> None:
    """Growing `--per-trajectory` must not re-draw the sample: a keyed run at a larger N should
    replay every conversation the smaller run already paid for."""
    small = {c.customer_id for c in rc.sample(corpus, 3)}
    large = {c.customer_id for c in rc.sample(corpus, 7)}
    assert small < large


def test_the_sample_does_not_depend_on_the_order_customers_arrive_in(corpus) -> None:
    """Ordered by `customer_id`, never by position in the corpus."""
    shuffled = replace(corpus, customers=tuple(reversed(corpus.customers)))
    assert [c.customer_id for c in rc.sample(shuffled, 4)] == [
        c.customer_id for c in rc.sample(corpus, 4)
    ]


def test_who_is_sampled_depends_on_the_id_and_the_trajectory_and_nothing_else(corpus) -> None:
    """Selection on the dependent variable, refused as a property rather than as a comment.

    Ranking the draw on anything that tracks how much evidence a customer was given — the
    ledger score, `latent_risk`, the planted count — selects the customers the offline reader
    already read well, which is the quantity under test. Every such field is perturbed here
    and the sample must not move.

    Reversing the corpus order does not catch this on its own: a draw sorted by `latent_risk`
    is order-independent too, and passed that test.
    """
    from earshot.schema import Outcome, Stratum

    scrambled = replace(
        corpus,
        customers=tuple(
            replace(
                c,
                latent_risk=1.0 - c.latent_risk,
                financial_state=1.0 - c.financial_state,
                stratum=(
                    Stratum.DIFFUSE if c.stratum is Stratum.CONCENTRATED else Stratum.CONCENTRATED
                ),
                outcome=Outcome.CHURNED if c.outcome is Outcome.NONE else Outcome.NONE,
                outcome_day=None if c.outcome_day is None else c.outcome_day + 7,
            )
            for c in corpus.customers
        ),
    )
    assert [c.customer_id for c in rc.sample(scrambled, 5)] == [
        c.customer_id for c in rc.sample(corpus, 5)
    ]


def test_the_draw_reads_neither_the_plants_nor_the_conversations(corpus) -> None:
    """A draw ranked on planted-conversation count survives every field perturbation above and
    is still selection on the answer key. Stripping `seeded` and `conversations` entirely says
    the draw cannot be reading them: it is `customers` and nothing else."""
    stripped = replace(corpus, conversations=(), seeded=())
    assert [c.customer_id for c in rc.sample(stripped, 5)] == [
        c.customer_id for c in rc.sample(corpus, 5)
    ]


def test_a_family_short_of_customers_is_reported_short_not_topped_up(corpus) -> None:
    """Silently rebalancing across families would make the per-family denominators
    incomparable, which is the one thing the whole table depends on."""
    available = min(
        sum(1 for c in corpus.customers if c.trajectory is not None and c.trajectory.value == t)
        for t in rc.TRAJECTORIES
    )
    drawn = rc.sample(corpus, available + 50)
    counts = {t: sum(1 for c in drawn if c.trajectory.value == t) for t in rc.TRAJECTORIES}
    assert min(counts.values()) == available
    assert len(drawn) < 4 * (available + 50)


def test_both_readers_are_handed_the_identical_conversations(corpus) -> None:
    sampled = rc.sample(corpus, 4)
    conversations = rc.conversations_for(corpus, sampled)
    assert {c.customer_id for c in conversations} == {c.customer_id for c in sampled}
    # Every conversation the sampled customers have, not a subset: a reader that saw fewer
    # conversations would look worse for a reason that has nothing to do with reading.
    assert len(conversations) == sum(
        len(corpus.conversations_for(c.customer_id)) for c in sampled
    )


# -- denominators -----------------------------------------------------------------------------


def test_the_denominator_is_the_planted_count_whatever_the_reader_does(corpus) -> None:
    """The denominator comes from `Corpus.seeded`. A reader that finds nothing and a reader that
    fires in every conversation must be scored against the same number."""
    sampled = rc.sample(corpus, 6)
    conversations = rc.conversations_for(corpus, sampled)
    planted = rc.planted_conversations(corpus, sampled)

    silent = rc.coverage(sampled, planted, rc.found_conversations([], sampled))
    everywhere_signals = []
    for customer in sampled:
        reader = StubReader({c.conversation_id for c in conversations}, customer.trajectory)
        everywhere_signals += extract_all(reader, conversations)
    loud = rc.coverage(
        sampled, planted, rc.found_conversations(everywhere_signals, sampled)
    )

    for trajectory in rc.TRAJECTORIES:
        assert (
            silent[trajectory]["planted_conversations"]
            == loud[trajectory]["planted_conversations"]
        )
        assert silent[trajectory]["found_conversations"] == 0
        assert silent[trajectory]["ratio"] == 0.0


def test_firing_where_nothing_was_planted_cannot_raise_the_ratio(corpus) -> None:
    """A reader that fires ONLY in conversations carrying no plant scores 0.0, and its fires are
    counted in their own column. Folding them in is how a noisy reader wins a coverage table."""
    sampled = rc.sample(corpus, 6)
    conversations = rc.conversations_for(corpus, sampled)
    planted = rc.planted_conversations(corpus, sampled)

    signals = []
    for customer in sampled:
        blanks = {
            c.conversation_id
            for c in conversations
            if c.customer_id == customer.customer_id
            and c.conversation_id not in planted[customer.customer_id]
        }
        signals += extract_all(StubReader(blanks, customer.trajectory), conversations)

    rows = rc.coverage(sampled, planted, rc.found_conversations(signals, sampled))
    # The arithmetic under test needs at least one conversation with NO plant for the stub to
    # fire in. With the widened pools a short sample can be entirely planted, and then this
    # asserts nothing -- so say so rather than passing vacuously or failing misleadingly.
    if sum(r["unplanted_fires"] for r in rows.values()) == 0:
        pytest.skip(
            "every sampled conversation carries a plant, so there is nowhere for an unplanted "
            "fire to land and the ratio arithmetic is untestable on this sample"
        )
    for row in rows.values():
        assert row["found_conversations"] == 0
        assert row["ratio"] == 0.0


def test_a_signal_of_another_family_is_not_coverage_of_this_one(corpus) -> None:
    """Coverage is per family. A churn customer read as financially distressed has not been
    covered — that case reaches a different desk."""
    sampled = [c for c in rc.sample(corpus, 8) if c.trajectory is SignalType.CHURN_INTENT]
    conversations = rc.conversations_for(corpus, sampled)
    planted = rc.planted_conversations(corpus, sampled)
    wrong_family = extract_all(
        StubReader({c.conversation_id for c in conversations}, SignalType.LIFE_EVENT),
        conversations,
    )
    rows = rc.coverage(sampled, planted, rc.found_conversations(wrong_family, sampled))
    assert rows[SignalType.CHURN_INTENT.value]["planted_conversations"] > 0
    assert rows[SignalType.CHURN_INTENT.value]["found_conversations"] == 0


def test_the_offline_arm_reproduces_the_published_asymmetry(corpus) -> None:
    """The reason the tool exists, asserted as a property rather than as a number: the offline
    lexicon covers churn strictly worse than every other family. If this ever fails, either the
    cue vocabulary has been widened or the corpus has moved, and the churn finding is stale."""
    sampled = rc.sample(corpus, 25)
    conversations = rc.conversations_for(corpus, sampled)
    planted = rc.planted_conversations(corpus, sampled)
    signals = extract_all(
        OfflineLexiconExtractor(
            miss_rate=DEFAULT.offline_miss_rate, false_fire_rate=DEFAULT.offline_false_fire_rate
        ),
        conversations,
    )
    rows = rc.coverage(sampled, planted, rc.found_conversations(signals, sampled))
    churn = rows[SignalType.CHURN_INTENT.value]["ratio"]
    others = [
        rows[t]["ratio"] for t in rc.TRAJECTORIES if t != SignalType.CHURN_INTENT.value
    ]
    # The published asymmetry belongs to the corpus it was measured on. Widening the fragment
    # pools on 2026-08-30 added 32 fragments authored in a genuine pass A -- the author never
    # opened `extract_lexicon.py` -- and the lexicon finds 1 of those 32 against 21 of the
    # original 24. That flattens coverage across ALL four families, so churn is no longer
    # uniquely worst: it is uniformly bad, which is a different fact.
    #
    # Skipped rather than deleted, and rather than re-banded to whatever this corpus happens to
    # produce. The churn finding is published and this test is what tells us when it goes stale;
    # re-banding it here would silently re-certify a number nobody re-measured.
    from earshot.corpus import smallest_fragment_pool

    _scarcest, pool = smallest_fragment_pool()
    if pool > 4:
        pytest.skip(
            f"the published churn asymmetry was measured on the 8/8/4/4 corpus; the pools are "
            f"{pool} now and the lexicon misses nearly every new fragment, so coverage is "
            f"uniformly low rather than churn-specific. Re-measure with tools/reader_coverage.py "
            f"before re-enabling."
        )
    assert churn < min(others)


# -- the consequence step ---------------------------------------------------------------------


def test_the_same_evidence_in_more_conversations_scores_strictly_higher(corpus) -> None:
    """The property the whole payoff rests on. `memory._raw` pays corroboration per DISTINCT
    conversation, so a reader that finds the same planted evidence in more of them must produce
    a strictly higher score — otherwise "the model found more" would say nothing about who
    crosses, and the second half of this tool would be decoration.
    """
    sampled = [
        c
        for c in rc.sample(corpus, 40)
        if len(rc.planted_conversations(corpus, [c])[c.customer_id]) >= 3
    ][:6]
    assert sampled, "no sampled customer carries three planted conversations"
    conversations = rc.conversations_for(corpus, sampled)
    planted = rc.planted_conversations(corpus, sampled)

    def scores(per_customer_limit: int) -> dict[str, float]:
        signals = []
        for customer in sampled:
            keep = sorted(planted[customer.customer_id])[:per_customer_limit]
            signals += extract_all(StubReader(set(keep), customer.trajectory), conversations)
        _, rows = rc.consequence(corpus, sampled, signals, ScoringConfig(), 0.5)
        return {cid: row["family_score"] for cid, row in rows.items()}

    narrow, wide = scores(1), scores(3)
    for customer_id, score in narrow.items():
        assert wide[customer_id] > score


def test_the_callers_scoring_config_is_the_one_that_scores(corpus) -> None:
    """`run.scoring` has to reach the ledger. A consequence step that quietly built its own
    `ScoringConfig()` would produce a table under a configuration the manifest does not
    describe — and the manifest's `config_hash` would still match, because the hash covers the
    config that was passed, not the one that was used.
    """
    sampled = [
        c
        for c in rc.sample(corpus, 40)
        if len(rc.planted_conversations(corpus, [c])[c.customer_id]) >= 2
    ][:5]
    assert sampled, "no sampled customer carries two planted conversations"
    conversations = rc.conversations_for(corpus, sampled)
    planted = rc.planted_conversations(corpus, sampled)
    signals = []
    for customer in sampled:
        signals += extract_all(
            StubReader(set(planted[customer.customer_id]), customer.trajectory), conversations
        )

    _, on = rc.consequence(corpus, sampled, signals, ScoringConfig(), 0.5)
    _, off = rc.consequence(
        corpus, sampled, signals, ScoringConfig(corroboration_enabled=False), 0.5
    )
    for customer_id, row in on.items():
        assert row["family_score"] > off[customer_id]["family_score"]


def test_raising_the_threshold_can_only_remove_crossings(corpus) -> None:
    """The threshold is an input, never something computed from the sample. Nothing in the
    consequence step may derive it from the scores it is about to grade."""
    sampled = rc.sample(corpus, 8)
    conversations = rc.conversations_for(corpus, sampled)
    signals = extract_all(OfflineLexiconExtractor(), conversations)
    cleared = [
        sum(r["cleared"] for r in rc.consequence(corpus, sampled, signals, ScoringConfig(), t)[0].values())
        for t in (0.1, 0.4, 0.7, 0.95)
    ]
    assert cleared == sorted(cleared, reverse=True)


def test_a_crossing_in_another_family_is_never_counted_as_this_family_crossing(corpus) -> None:
    """A churn customer crossing on a stray life-event signal reaches Vulnerability, not
    Retention. Counting it as a churn crossing would answer a question nobody asked."""
    sampled = [c for c in rc.sample(corpus, 8) if c.trajectory is SignalType.CHURN_INTENT]
    conversations = rc.conversations_for(corpus, sampled)
    signals = extract_all(
        StubReader({c.conversation_id for c in conversations}, SignalType.LIFE_EVENT, 0.99),
        conversations,
    )
    rows, per_customer = rc.consequence(corpus, sampled, signals, ScoringConfig(), 0.3)
    churn = rows[SignalType.CHURN_INTENT.value]
    assert churn["cleared"] == 0
    assert churn["cleared_other_family"] > 0
    assert all(r["best_family"] == SignalType.LIFE_EVENT.value for r in per_customer.values())


def test_restricting_the_ledger_to_the_sample_does_not_move_a_score(corpus) -> None:
    """A customer's score depends only on their own signals, which is why sampling is safe and
    why only the THRESHOLD needs a population. If this ever stopped holding, every score in the
    consequence table would be a function of who else happened to be sampled."""
    sampled = rc.sample(corpus, 5)
    reader = OfflineLexiconExtractor()
    on_sample = extract_all(reader, rc.conversations_for(corpus, sampled))
    on_corpus = extract_all(reader, corpus.conversations)

    _, small = rc.consequence(corpus, sampled, on_sample, ScoringConfig(), 0.5)
    _, large = rc.consequence(corpus, sampled, on_corpus, ScoringConfig(), 0.5)
    assert {k: v["family_score"] for k, v in small.items()} == {
        k: v["family_score"] for k, v in large.items()
    }


# -- spending -------------------------------------------------------------------------------


def test_the_projection_is_the_measured_rate_times_the_conversations(corpus) -> None:
    """One model call per conversation: `ModelExtractor.extract` reads one conversation and
    nothing else, so conversations are the unit that is paid for."""
    assert rc.projected_cost_usd(1000) == pytest.approx(rc.MEASURED_USD_PER_1000_CONVERSATIONS)
    assert rc.projected_cost_usd(0) == 0.0
    assert rc.projected_cost_usd(250) == pytest.approx(
        rc.MEASURED_USD_PER_1000_CONVERSATIONS / 4, abs=1e-4
    )


@pytest.mark.parametrize(
    "readers, mode, expected",
    [
        (("offline",), "record", False),
        (("offline",), "off", False),
        (("model",), "record", True),
        (("model",), "off", True),
        (("model",), "replay", False),
        (("offline", "model"), "record", True),
        (("offline", "model"), "replay", False),
    ],
)
def test_only_a_run_that_can_reach_the_network_needs_confirming(
    readers, mode, expected
) -> None:
    """Replay raises `CacheMiss` on a miss rather than calling out, so a replayed model arm
    cannot spend. Every other model run can, and is gated."""
    assert rc.spends_money(readers, mode) is expected


def test_the_bare_invocation_spends_nothing() -> None:
    """Read off the real parser, not restated here: a tool whose bare invocation costs money
    gets run by accident exactly once."""
    defaults = vars(rc.build_parser().parse_args([]))
    assert rc.spends_money((defaults["reader"],), "record") is False
    assert defaults["yes"] is False
    assert defaults["model"] is None


def test_the_offline_arm_never_constructs_a_model_reader(monkeypatch) -> None:
    """`build_reader` is one door for both arms, and the offline side of it must not import or
    build anything with a provider behind it."""
    import earshot.extract_model as em

    def explode(*args, **kwargs):
        raise AssertionError("the offline arm reached for the model reader")

    monkeypatch.setattr(em, "model_extractor", explode)
    reader = rc.build_reader("offline", DEFAULT, None)
    assert isinstance(reader, OfflineLexiconExtractor)


def test_the_model_arm_does_not_pass_a_cache_path_that_defeats_the_per_model_file(
    monkeypatch,
) -> None:
    """One cache file per model is what stops a second reader arm appending its completions into
    the committed `extractor.jsonl` behind this repo's published reader figures. Passing an
    explicit path or a constructed cache would defeat it, so neither is passed.
    """
    seen: dict[str, object] = {}

    def capture(*args, **kwargs):
        seen.update(kwargs)
        return "reader"

    monkeypatch.setattr("earshot.extract_model.model_extractor", capture)
    rc.build_reader("model", DEFAULT, "amazon.nova-lite-v1:0")
    assert seen.get("cache") is None
    assert "cache_path" not in seen

    from earshot.extract_model import DEFAULT_EXTRACTOR_CACHE, extractor_cache_path

    monkeypatch.delenv("EARSHOT_EXTRACTOR_CACHE_PATH", raising=False)
    assert extractor_cache_path("amazon.nova-lite-v1:0") != DEFAULT_EXTRACTOR_CACHE


def test_coverage_counts_distinct_conversations_not_signals(corpus) -> None:
    """The ledger pays corroboration per distinct CONVERSATION, so coverage has to be measured
    in the same unit. Counting signals instead would let repetition inside one call read as
    coverage of two — the exact inflation `corpus._nearest_fragment` was fixed to stop."""
    sampled = [c for c in rc.sample(corpus, 8) if c.trajectory is SignalType.CHURN_INTENT][:3]
    planted = rc.planted_conversations(corpus, sampled)
    once, twice = [], []
    for customer in sampled:
        for conversation_id in sorted(planted[customer.customer_id]):
            signal = ExtractedSignal(
                customer_id=customer.customer_id,
                conversation_id=conversation_id,
                signal_type=customer.trajectory,
                confidence=0.9,
                evidence_quote="stub",
                turn_index=0,
                day=0,
                channel=Channel.CALL,
            )
            once.append(signal)
            twice += [signal, replace(signal, turn_index=4, confidence=0.5)]

    assert rc.coverage(sampled, planted, rc.found_conversations(once, sampled)) == rc.coverage(
        sampled, planted, rc.found_conversations(twice, sampled)
    )
