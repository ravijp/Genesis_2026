"""Unit tests for the ledger and re-scorer — the one piece the submission promises is
"plain code, not the model, so that logic is testable and reproducible".
"""

from __future__ import annotations

from dataclasses import replace

from earshot.config import ScoringConfig
from earshot.memory import SignalLedger
from earshot.schema import Channel, ExtractedSignal, SignalType


def sig(
    day: int,
    conversation: str,
    confidence: float = 0.3,
    channel: Channel = Channel.CALL,
    signal_type: SignalType = SignalType.FINANCIAL_DISTRESS,
) -> ExtractedSignal:
    return ExtractedSignal(
        customer_id="C1",
        conversation_id=conversation,
        signal_type=signal_type,
        confidence=confidence,
        evidence_quote="...",
        turn_index=1,
        day=day,
        channel=channel,
    )


def test_ledger_never_discards() -> None:
    """Never-discard. Nothing may delete or supersede an entry — that is the design inversion
    against reconcile-to-current-truth."""
    ledger = SignalLedger()
    for i in range(5):
        ledger.append(sig(day=i * 10, conversation=f"K{i}"))
    assert len(ledger.signals("C1")) == 5

    # A much later, much louder signal must not evict the weak early ones.
    ledger.append(sig(day=200, conversation="K9", confidence=0.95))
    assert len(ledger.signals("C1")) == 6
    assert any(s.confidence == 0.3 for s in ledger.signals("C1"))


def test_weak_signals_accumulate_across_conversations() -> None:
    """The entry's core claim: three individually-unalarming conversations jointly cross a
    threshold none of them crosses alone."""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(30, "B"), sig(60, "C")])

    alone = SignalLedger()
    alone.extend([sig(60, "C")])

    combined = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 60).score
    single = alone.score("C1", SignalType.FINANCIAL_DISTRESS, 60).score
    assert combined > single, "accumulation produced no lift — the whole idea is broken"


def test_repetition_inside_one_conversation_is_not_corroboration() -> None:
    """Saying the same thing twice in one call is not two pieces of evidence."""
    same = SignalLedger()
    same.extend([sig(10, "A"), sig(10, "A")])
    spread = SignalLedger()
    spread.extend([sig(10, "A"), sig(10, "B")])

    assert (
        spread.score("C1", SignalType.FINANCIAL_DISTRESS, 10).score
        > same.score("C1", SignalType.FINANCIAL_DISTRESS, 10).score
    )


def test_retro_rescoring_moves_the_conclusion_the_early_evidence_supports() -> None:
    """Retro re-scoring, and the demo beat. The March conversation is re-read in light of July:
    the conclusion it supports moves, even though its own marginal value does not grow."""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])

    breakdown = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 40)
    first = min(breakdown.entries, key=lambda e: e.signal.day)

    assert first.contribution_at_write > 0
    assert first.score_at_write < first.score_now
    assert first.retro_delta > 0, (
        "the picture did not move as corroboration arrived — retro re-scoring is not working, "
        "and it is the one mechanic no incumbent ships"
    )


def _earliest(ledger: SignalLedger, as_of: int):
    return min(
        ledger.score("C1", SignalType.FINANCIAL_DISTRESS, as_of).entries,
        key=lambda e: e.signal.day,
    )


def test_corroboration_is_super_additive_and_concavity_opposes_it() -> None:
    """Two forces act on an early quote's marginal value, and they pull opposite ways.

    Corroboration multiplies the whole evidence base, which RAISES what every existing signal
    is worth — that is the mechanism, not a side effect. Saturation is concave, which LOWERS
    it. Which one wins depends on the operating range, so neither direction is safe to assert
    on its own and this test does not assert one.

    What is structural, and what this pins down: turning corroboration off must remove the
    super-additivity. If a future change makes the no-corroboration path grow marginal value
    too, something is compounding that should not be.
    """
    with_corroboration = SignalLedger()
    with_corroboration.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    first_with = _earliest(with_corroboration, 40)

    plain = SignalLedger(
        replace(
            ScoringConfig(),
            corroboration_enabled=False,
            cross_channel_enabled=False,
            escalation_enabled=False,
            decay_enabled=False,
        )
    )
    plain.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    first_plain = _earliest(plain, 40)

    assert first_with.contribution_now > first_with.contribution_at_write, (
        "corroboration did not raise the value of earlier evidence — the mechanism is inert"
    )
    assert first_plain.contribution_now <= first_plain.contribution_at_write + 1e-9, (
        "with corroboration off, marginal value still grew — something is compounding that "
        "should not be, and the ablation arms are no longer measuring what they claim"
    )


def test_load_bearing_identifies_evidence_the_case_depends_on() -> None:
    """The compliance-grade question: would the case collapse without this quote?"""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    breakdown = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 40)

    # Threshold just under the achieved score: every weak signal is then load-bearing.
    tight = breakdown.score - 0.01
    assert all(e.is_load_bearing(tight) for e in breakdown.entries)

    # A threshold the customer never reaches: nothing is load-bearing.
    assert not any(e.is_load_bearing(0.999) for e in breakdown.entries)

    # Both checks above are decided by "did the customer cross at all", so they would still
    # pass if the removal clause were deleted. This one separates the entries: at a threshold
    # placed BETWEEN two entries' contributions, the bigger contributor is what holds the case
    # up and the smaller one is not.
    contributions = sorted(e.contribution_now for e in breakdown.entries)
    assert contributions[0] < contributions[-1], "entries contribute equally; nothing to separate"
    margin = (contributions[0] + contributions[-1]) / 2
    between = breakdown.score - margin

    load_bearing = {
        e.signal.day: e.is_load_bearing(between) for e in breakdown.entries
    }
    by_day = {e.signal.day: e.contribution_now for e in breakdown.entries}
    for day, bearing in load_bearing.items():
        assert bearing == (by_day[day] > margin), (
            f"day {day} contributes {by_day[day]:.4f} against a margin of {margin:.4f} but "
            f"is_load_bearing returned {bearing} — the removal clause is not being applied"
        )
    assert any(load_bearing.values()) and not all(load_bearing.values()), (
        "the threshold failed to separate the entries, so this assertion proves nothing"
    )


def test_decay_reduces_the_weight_of_old_signals() -> None:
    """A job loss mentioned two years ago is not live risk."""
    ledger = SignalLedger()
    ledger.extend([sig(0, "A")])
    fresh = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 0).score
    stale = ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 900).score
    assert stale < fresh


def test_decay_can_be_ablated() -> None:
    cfg = replace(ScoringConfig(), decay_enabled=False)
    ledger = SignalLedger(cfg)
    ledger.extend([sig(0, "A")])
    assert (
        ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 900).score
        == ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 0).score
    )


def test_cross_channel_beats_single_channel() -> None:
    single = SignalLedger()
    single.extend([sig(0, "A", channel=Channel.CALL), sig(20, "B", channel=Channel.CALL)])
    mixed = SignalLedger()
    mixed.extend([sig(0, "A", channel=Channel.CALL), sig(20, "B", channel=Channel.COMPLAINT)])
    assert (
        mixed.score("C1", SignalType.FINANCIAL_DISTRESS, 20).score
        > single.score("C1", SignalType.FINANCIAL_DISTRESS, 20).score
    )


def test_scoring_is_deterministic() -> None:
    """Bit-for-bit reproducibility is one of the three things we claim over long-context."""
    runs = []
    for _ in range(3):
        ledger = SignalLedger()
        ledger.extend([sig(0, "A"), sig(15, "B", channel=Channel.CHAT), sig(45, "C")])
        runs.append(ledger.score("C1", SignalType.FINANCIAL_DISTRESS, 45).score)
    assert len(set(runs)) == 1


def test_case_opens_on_first_crossing_and_carries_evidence() -> None:
    ledger = SignalLedger()
    ledger.extend([sig(0, "A"), sig(20, "B"), sig(40, "C")])
    case = ledger.open_case("C1", SignalType.FINANCIAL_DISTRESS, threshold=0.2)
    assert case is not None
    assert case.evidence, "a case with no evidence chain is not auditable"
    assert case.opened_on_day in (0, 20, 40)
    assert case.lead_days(120) == 120 - case.opened_on_day
