"""Layer 1 additions: synthetic account and transaction state for the investigator's tools.

Nothing in this package may import the corpus generator or a ground-truth type — see
`tests/test_separation.py`, whose danger-surface glob covers `core/*.py` automatically.
"""

from __future__ import annotations

from .accounts import (
    WINDOW_DAYS,
    AccountSnapshot,
    PriorCase,
    Transaction,
    account_snapshot,
    generate_history,
    synthesize_prior_cases,
)

__all__ = [
    "WINDOW_DAYS",
    "AccountSnapshot",
    "PriorCase",
    "Transaction",
    "account_snapshot",
    "generate_history",
    "synthesize_prior_cases",
]
