"""A spend ceiling in our own code, because the account will not give us one.

**Why this is not an AWS Budget.** `budgets:*` and `ce:*` are denied on this account and asking for
them is not on the critical path (`docs/ops/progress.md`). So the ceiling lives where a judge reads
it — beside `COST_CAP_PER_CASE_USD`, in a repository — which is the A9 argument applied to money:
the guardrail we refuse to delegate is the one we can show.

**What it bounds, exactly.** `SpendCeiling` counts every dollar a provider reports and refuses the
call *before* the one that would cross the line. It is a **pre-flight** check against a running
total, so it inherits D-011's honest limitation unchanged: it bounds **cumulative** spend, not a
single anomalous call. A call that costs wildly more than every prior one still lands, and the next
one is refused. There is no way to know a call's price before making it, and a cap that pretends
otherwise is worse than one that states the gap.

**What it does not bound.** The counter lives in a process. On a laptop that is a whole `earshot
sweep`, which is the case that matters — one command, one ceiling. In Lambda a process is one
container, reused across invocations but not shared between them, so the deployed ceiling is
per-container and **not** account-wide. Nothing here stops a thousand concurrent containers each
spending up to the cap. What actually bounds the deployed spend is the reserved concurrency on the
function plus `maxReceiveCount: 3` on the DLQ redrive; this makes a runaway *loop* cheap, not a
runaway *fleet*. Say that rather than implying an account guarantee.

It composes with, and does not replace, the investigator's own `cost_cap_usd`. That one bounds a
single case; this one bounds everything the process does, including the reader.
"""

from __future__ import annotations

import os
import threading

from .base import Completion, LLMProvider, Message, ModelConfig, ProviderError, ToolSpec

# Deliberately generous next to `COST_CAP_PER_CASE_USD` ($0.25): this is a runaway stop, not a
# throttle. A sweep of 30 seeds x 400 customers is ~12,000 reader calls, and the point is to catch
# a loop that will never terminate, not to interrupt an expensive-but-intended run at 80%.
DEFAULT_SPEND_CAP_USD = 5.00


class BudgetExhausted(ProviderError):
    """The ceiling was reached. A `ProviderError` subclass on purpose: every caller in this
    codebase already handles that, and the investigator's loop degrades to a decision rather than
    crashing — so hitting the ceiling produces a case file that says why, not a traceback."""


def spend_cap_usd(explicit: float | None = None) -> float | None:
    """`explicit`, else `$EARSHOT_SPEND_CAP_USD`, else the default. `0` disables the ceiling, and
    disabling it is a thing you have to type."""
    if explicit is not None:
        return explicit if explicit > 0 else None
    raw = os.environ.get("EARSHOT_SPEND_CAP_USD")
    if raw is None:
        return DEFAULT_SPEND_CAP_USD
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"EARSHOT_SPEND_CAP_USD must be a number, got {raw!r}") from exc
    return value if value > 0 else None


class SpendCeiling:
    """A running total and a limit. Thread-safe, because `sweep` fans out."""

    def __init__(self, cap_usd: float | None) -> None:
        self.cap_usd = cap_usd
        self._spent = 0.0
        self._calls = 0
        self._lock = threading.Lock()

    @property
    def spent_usd(self) -> float:
        return round(self._spent, 6)

    @property
    def calls(self) -> int:
        return self._calls

    @property
    def remaining_usd(self) -> float | None:
        return None if self.cap_usd is None else round(max(0.0, self.cap_usd - self._spent), 6)

    def check(self) -> None:
        """Refuse before the call, not after it. Raising afterwards would mean the money is
        already spent and the ceiling is a report rather than a control."""
        if self.cap_usd is None:
            return
        with self._lock:
            spent = self._spent
        if spent >= self.cap_usd:
            raise BudgetExhausted(
                f"spend ceiling reached: ${spent:.4f} of ${self.cap_usd:.2f} after "
                f"{self._calls} calls. Raise EARSHOT_SPEND_CAP_USD, or set it to 0 to disable it "
                f"deliberately."
            )

    def record(self, cost_usd: float) -> None:
        if cost_usd and cost_usd > 0:
            with self._lock:
                self._spent += cost_usd
        with self._lock:
            self._calls += 1

    def to_dict(self) -> dict[str, float | int | None]:
        return {
            "cap_usd": self.cap_usd,
            "spent_usd": self.spent_usd,
            "remaining_usd": self.remaining_usd,
            "calls": self._calls,
        }


class CappedProvider:
    """Any provider, with a spend ceiling in front of it.

    Wrapping the provider rather than each caller is the whole point: every dollar this system can
    spend goes through exactly one method, so one decorator covers the CLI, the sweep, the reader
    and both Lambda handlers, and a new call site cannot forget to opt in.

    Placed **outside** the cache, so a replayed response costs nothing and does not count. That is
    correct and worth stating: the ceiling exists to bound money, and replay spends none.
    """

    def __init__(self, inner: LLMProvider, ceiling: SpendCeiling) -> None:
        self.inner = inner
        self.ceiling = ceiling
        cap = "off" if ceiling.cap_usd is None else f"${ceiling.cap_usd:.2f}"
        self.name = f"{inner.name}+cap:{cap}"

    def complete(
        self, messages: list[Message], tools: list[ToolSpec], model_cfg: ModelConfig
    ) -> Completion:
        self.ceiling.check()
        completion = self.inner.complete(messages, tools, model_cfg)
        self.ceiling.record(completion.cost_usd)
        return completion
