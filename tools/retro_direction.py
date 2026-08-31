"""Retro re-scoring, measured rather than asserted: can a past conversation be worth MORE?

The build rules require retro re-scoring to be observable. This is the observation, and it is the
structural argument for the four mechanisms in `memory.py` that the recall sweep cannot make.

`LedgerEntry` records each signal's marginal value on the day it landed
(`contribution_at_write`) and its marginal value today (`contribution_now`). Under an unweighted
count the score is `1 - exp(-saturation * n)`, which is concave, so an entry's marginal
contribution can only SHRINK as more evidence arrives -- *"March is worth more because of June"*
cannot happen at all. Corroboration, cross-channel weighting and escalation are what make it
possible, and this script prints how often each configuration actually does it.

Offline, free, no API key. Evaluation side: it reads the ledger, never the answer key.

    uv run python tools/retro_direction.py --customers 1500
"""

from __future__ import annotations

import argparse

from earshot.arms import _dumb_config, demo_ledger
from earshot.cli import _pipeline
from earshot.config import DEFAULT, sized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--customers", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=DEFAULT.seed)
    args = parser.parse_args()

    run = sized(args.customers, seed=args.seed)
    dataset, _, signals = _pipeline(run)

    print("=" * 78)
    print("RETRO RE-SCORE DIRECTION - is a past conversation worth more now than at write?")
    print("=" * 78)
    print(f"seed={run.seed}  customers={args.customers}  "
          f"conversations={len(dataset.conversations)}")
    print("Denominator is multi-signal ledger entries: an arc of one signal has no past to re-read.")
    print()
    print(f"  {'config':<14}{'entries':>9}{'MORE now':>10}{'less':>7}{'unchanged':>11}{'max gain':>11}")

    for label, scoring in (("full-ledger", run.scoring), ("dumb-ledger", _dumb_config(run.scoring))):
        ledger = demo_ledger(signals, scoring)
        more = less = same = 0
        best = 0.0
        for customer_id in ledger.customers():
            for signal_type in {s.signal_type for s in ledger.signals(customer_id)}:
                timeline = ledger.timeline(customer_id, signal_type)
                if len(timeline) < 2:
                    continue
                for entry in timeline[-1].entries:
                    delta = round(entry.contribution_now - entry.contribution_at_write, 9)
                    if delta > 0:
                        more += 1
                    elif delta < 0:
                        less += 1
                    else:
                        same += 1
                    best = max(best, delta)
        print(
            f"  {label:<14}{more + less + same:>9}{more:>10}{less:>7}{same:>11}{best:>11.4f}"
        )

    print()
    print("  An entry is 'unchanged' when no later evidence of its family arrived for that customer.")
    print("  0 of anything under `dumb-ledger` is structural, not a parameter: with every")
    print("  multiplier off the score function is concave, so marginal value can only fall.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
