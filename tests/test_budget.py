"""The spend ceiling — W4, the guardrail we could not delegate to AWS.

`budgets:*` and `ce:*` are denied on this account, so the ceiling lives in the repository instead.
That makes it testable, which an AWS Budget would not have been, and these are the properties worth
holding:

* it refuses **before** the call, so it is a control and not a report;
* it inherits D-011's limitation honestly — cumulative spend, never a single anomalous call;
* it sits **outside** the cache, so a keyless replay run can never be exhausted;
* `0` disables it, and disabling it is something you have to type.
"""

from __future__ import annotations

import pytest

from earshot.llm import build_provider, cache_mode
from earshot.llm.base import Completion, ModelConfig, Usage
from earshot.llm.budget import (
    DEFAULT_SPEND_CAP_USD,
    BudgetExhausted,
    CappedProvider,
    SpendCeiling,
    spend_cap_usd,
)


class Meter:
    """A provider that charges a fixed amount per call and counts how often it was reached."""

    name = "meter"

    def __init__(self, cost_usd: float = 1.0) -> None:
        self.cost_usd = cost_usd
        self.calls = 0

    def complete(self, messages, tools, model_cfg) -> Completion:
        self.calls += 1
        return Completion(
            content="ok",
            model="meter-1",
            usage=Usage(prompt_tokens=1, completion_tokens=1),
            cost_usd=self.cost_usd,
            latency_ms=1.0,
        )


def call(provider) -> Completion:
    return provider.complete([{"role": "user", "content": "hi"}], [], ModelConfig())


# ---- the ceiling itself ---------------------------------------------------------------------


def test_the_ceiling_refuses_before_the_call_not_after_it() -> None:
    """Raising afterwards would mean the money is already spent and the cap is a report."""
    inner = Meter(cost_usd=0.60)
    provider = CappedProvider(inner, SpendCeiling(1.00))

    call(provider)
    call(provider)  # total 1.20, over the cap -- but each call was allowed when it started
    assert inner.calls == 2

    with pytest.raises(BudgetExhausted, match="spend ceiling reached"):
        call(provider)
    assert inner.calls == 2, "a refused call still reached the provider"


def test_it_bounds_cumulative_spend_and_says_so_rather_than_bounding_one_call() -> None:
    """D-011, unchanged and inherited: nothing can know a call's price before making it, and a cap
    that pretends otherwise is worse than one that states the gap."""
    inner = Meter(cost_usd=99.0)
    ceiling = SpendCeiling(1.00)
    provider = CappedProvider(inner, ceiling)

    call(provider)  # one anomalous call lands in full
    assert ceiling.spent_usd == 99.0
    with pytest.raises(BudgetExhausted):
        call(provider)


def test_the_error_says_what_to_do_about_it() -> None:
    provider = CappedProvider(Meter(cost_usd=2.0), SpendCeiling(1.00))
    call(provider)
    with pytest.raises(BudgetExhausted) as caught:
        call(provider)
    message = str(caught.value)
    assert "EARSHOT_SPEND_CAP_USD" in message
    assert "$1.00" in message and "calls" in message


def test_the_running_total_is_readable_for_a_manifest() -> None:
    ceiling = SpendCeiling(10.0)
    provider = CappedProvider(Meter(cost_usd=0.25), ceiling)
    call(provider)
    call(provider)
    assert ceiling.to_dict() == {
        "cap_usd": 10.0,
        "spent_usd": 0.5,
        "remaining_usd": 9.5,
        "calls": 2,
    }


def test_a_free_call_still_counts_as_a_call_but_not_as_spend() -> None:
    """A replayed or unpriced completion must not silently consume budget — `bedrock.py` returns
    0.0 for a model with no price row rather than guessing."""
    ceiling = SpendCeiling(1.0)
    provider = CappedProvider(Meter(cost_usd=0.0), ceiling)
    for _ in range(5):
        call(provider)
    assert ceiling.spent_usd == 0.0 and ceiling.calls == 5


def test_no_cap_means_no_ceiling_object_in_the_way() -> None:
    ceiling = SpendCeiling(None)
    ceiling.record(1000.0)
    ceiling.check()  # must not raise
    assert ceiling.remaining_usd is None


# ---- resolving the cap ------------------------------------------------------------------------


def test_the_default_cap_applies_when_nothing_is_set(monkeypatch) -> None:
    monkeypatch.delenv("EARSHOT_SPEND_CAP_USD", raising=False)
    assert spend_cap_usd() == DEFAULT_SPEND_CAP_USD


def test_zero_disables_the_ceiling_deliberately(monkeypatch) -> None:
    """Turning off a spend guardrail should require typing something, not just omitting it."""
    monkeypatch.setenv("EARSHOT_SPEND_CAP_USD", "0")
    assert spend_cap_usd() is None


def test_an_unparseable_cap_is_refused_rather_than_ignored(monkeypatch) -> None:
    """Silently falling back to the default would mean `EARSHOT_SPEND_CAP_USD=1O.00` (letter O)
    runs at $5 while its author believes it runs at $10."""
    monkeypatch.setenv("EARSHOT_SPEND_CAP_USD", "ten dollars")
    with pytest.raises(ValueError, match="must be a number"):
        spend_cap_usd()


def test_an_explicit_argument_beats_the_environment(monkeypatch) -> None:
    monkeypatch.setenv("EARSHOT_SPEND_CAP_USD", "5")
    assert spend_cap_usd(0.25) == 0.25


# ---- how it is wired into provider selection ------------------------------------------------


def test_every_paid_provider_is_capped_by_default(monkeypatch, tmp_path) -> None:
    """Wrapping the provider rather than each caller is the point: a new call site cannot forget
    to opt in."""
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")
    monkeypatch.delenv("EARSHOT_SPEND_CAP_USD", raising=False)
    for name in ("bedrock", "openrouter"):
        provider = build_provider(name, "sha")
        assert "cap:$" in provider.name, f"{name} is not capped"


def test_the_offline_rule_engine_is_never_capped(monkeypatch) -> None:
    """It cannot spend, and a ceiling in front of the one keyless path is a way to break it."""
    monkeypatch.delenv("EARSHOT_SPEND_CAP_USD", raising=False)
    assert "cap:" not in build_provider("offline", "sha").name


def test_the_ceiling_sits_outside_the_cache(monkeypatch) -> None:
    """`CappedProvider(CachingProvider(live))`, in that order. Inverting them would make a keyless
    replay run exhaustible, which is the one thing that must never happen."""
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")
    monkeypatch.delenv("EARSHOT_SPEND_CAP_USD", raising=False)
    provider = build_provider("bedrock", "sha")
    assert isinstance(provider, CappedProvider)
    assert provider.name.index("cache:") < provider.name.index("cap:")
    assert cache_mode() == "replay"


def test_several_providers_can_share_one_budget(monkeypatch) -> None:
    """A sweep runs a reader and an investigator; two independent ceilings would let it spend
    twice what its author asked for."""
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")
    shared = SpendCeiling(1.0)
    reader = build_provider("bedrock", "sha", ceiling=shared)
    judge = build_provider("bedrock", "sha", ceiling=shared)
    assert reader.ceiling is judge.ceiling is shared


def test_a_disabled_cap_leaves_the_provider_unwrapped(monkeypatch) -> None:
    monkeypatch.setenv("EARSHOT_CACHE_MODE", "replay")
    monkeypatch.setenv("EARSHOT_SPEND_CAP_USD", "0")
    assert "cap:" not in build_provider("bedrock", "sha").name
