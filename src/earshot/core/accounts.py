"""Synthetic account state and a 90-day transaction history.

**The separation rule, stated where it is easiest to break.** This module sits on the path from
conversation to decision, so it must never see the answer key. Everything below is derived from
four primitives the caller hands in — `(customer_id, latent_risk, seed, as_of_day)` — and from
nothing else. Latent risk is a legitimate generative parameter: real financial stress does show
up in a current account, so a bank's transactions genuinely correlate with it. `outcome` is the
answer key, and a tool that let the agent read it would make the evaluation worthless — which is
why `tests/test_separation.py` discovers this file by glob rather than by a maintained list.

**Why the numbers are deliberately noisy.** If transactions were a clean readout of latent risk,
the investigator's job would be a threshold check and the whole experiment would measure nothing.
So latent risk is observed through three partially independent channels — income regularity,
discretionary spend, and balance buffer — each with its own noise. The channels disagree with one
another, a fifth of customers run a thin buffer regardless of risk, and a calm-looking account
sometimes belongs to a genuinely distressed customer. That overlap is the point: the agent has to
weigh conflicting evidence rather than read an answer off one field.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

WINDOW_DAYS = 90
DAYS_PER_MONTH = 30

# The generator picks a limit from this ladder and `_overdraft_limit()` recovers it by asking
# how deep the account was allowed to go. Both ends must read the same tuple: when they were
# two separate literals, changing one silently made the tool report a limit the account never
# had, with nothing failing.
OVERDRAFT_LADDER = (0.0, 250.0, 500.0, 1000.0, 1500.0)

# Categories the agent sees. Split into essential vs discretionary so belt-tightening is
# visible without the tool having to editorialise about it.
ESSENTIAL_CATEGORIES = frozenset({"housing", "utilities", "groceries", "transport", "credit"})
DISCRETIONARY_CATEGORIES = frozenset({"discretionary"})

_GROCERS = ("Tesco", "Sainsburys", "Aldi", "Lidl", "Co-op", "Morrisons")
_DISCRETIONARY = (
    ("Deliveroo", 9.0, 42.0),
    ("Amazon", 8.0, 90.0),
    ("Spotify", 10.99, 10.99),
    ("Cineworld", 11.0, 28.0),
    ("Pub - The Crown", 12.0, 55.0),
    ("ASOS", 18.0, 120.0),
    ("Nandos", 14.0, 46.0),
)
_UTILITIES = (("Octopus Energy", 55.0, 180.0), ("Thames Water", 22.0, 60.0), ("Vodafone", 12.0, 45.0))


@dataclass(frozen=True)
class Transaction:
    day: int  # days since corpus epoch, same clock as conversations
    description: str
    category: str
    amount: float  # negative = debit
    balance_after: float


@dataclass(frozen=True)
class AccountSnapshot:
    """What a servicing agent would see on the account screen, as of `as_of_day`."""

    customer_id: str
    as_of_day: int
    product: str
    tenure_months: int
    current_balance: float
    overdraft_limit: float
    days_in_overdraft: int
    lowest_balance: float
    balance_trend: float  # closing minus opening over the window
    salary_credits: int
    expected_salary_credits: int
    median_salary_credit: float
    salary_change_pct: float  # last salary vs first, as a percentage
    returned_direct_debits: int
    fee_charges: int
    essential_spend: float
    discretionary_spend: float
    savings_balance: float


@dataclass(frozen=True)
class PriorCase:
    """A case a human already worked on this customer. Investigations do not start blank."""

    case_id: str
    opened_on_day: int
    signal_type: str
    owning_team: str
    resolution: str  # dismissed | resolved | referred | open
    note: str


def _rng(customer_id: str, seed: int, *parts: str) -> random.Random:
    """Deterministic per-(customer, purpose) stream.

    Seeded from a digest rather than `hash()`, which is salted per process and would make the
    same customer look different from one run to the next.
    """
    key = "|".join((customer_id, str(seed), *parts)).encode()
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def generate_history(
    customer_id: str,
    latent_risk: float,
    seed: int,
    as_of_day: int,
    window_days: int = WINDOW_DAYS,
) -> list[Transaction]:
    """A window of current-account activity ending on `as_of_day`, oldest first."""
    rng = _rng(customer_id, seed, "accounts")
    latent = _clamp(latent_risk)

    # Three noisy readings of the same latent state. Independent noise is what stops the
    # account from being a lookup table: indicators routinely disagree.
    #
    # The floors are load-bearing, not cosmetic. Clamping to [0, 1] lets `latent + gauss` land
    # on exactly 0.0 for a large share of zero-risk customers, and a population of identical
    # zero-stress accounts is a "perfectly clean" signature that picks decoys out on its own.
    # Every customer carries some noise.
    income_stress = _clamp(latent + rng.gauss(0.0, 0.30), 0.05, 0.95)
    spend_stress = _clamp(latent + rng.gauss(0.0, 0.30), 0.05, 0.95)
    buffer_stress = _clamp(latent + rng.gauss(0.0, 0.32), 0.05, 0.95)

    # ~1 in 5 customers runs a thin buffer whatever their risk — gig income, chaotic but
    # solvent. These are the honest false positives; without them the tool is a risk oracle.
    if rng.random() < 0.20:
        buffer_stress = max(buffer_stress, rng.uniform(0.55, 0.90))

    monthly_income = round(rng.uniform(1500.0, 3600.0), 2)
    rent = round(monthly_income * rng.uniform(0.28, 0.45), 2)
    overdraft_limit = rng.choice(OVERDRAFT_LADDER)
    balance = round(monthly_income * rng.uniform(0.05, 0.90) * (1.0 - 0.6 * buffer_stress), 2)

    payday = rng.randrange(DAYS_PER_MONTH)
    rent_day = (payday + rng.randint(1, 4)) % DAYS_PER_MONTH
    utility_days = tuple((payday + off) % DAYS_PER_MONTH for off in (6, 11, 17))

    start = as_of_day - window_days + 1
    out: list[Transaction] = []

    def post(day: int, description: str, category: str, amount: float) -> None:
        nonlocal balance
        balance = round(balance + amount, 2)
        out.append(Transaction(day, description, category, round(amount, 2), balance))

    for day in range(start, as_of_day + 1):
        slot = day % DAYS_PER_MONTH

        if slot == payday:
            # Income stress shows up three ways, and only sometimes: reduced pay (statutory
            # sick/maternity), a missed run, or a late one. None is conclusive on its own.
            roll = rng.random()
            if roll < 0.30 * income_stress:
                pass  # missed entirely this cycle
            elif roll < 0.55 * income_stress:
                post(day, "Statutory pay", "salary", round(monthly_income * rng.uniform(0.35, 0.6), 2))
            else:
                drift = 1.0 - 0.12 * income_stress * rng.random()
                post(day, "Salary", "salary", round(monthly_income * drift, 2))

        if slot == rent_day:
            if balance - rent < -overdraft_limit and rng.random() < 0.7:
                post(day, "Rent - RETURNED unpaid", "fees", -12.0)
            else:
                post(day, "Rent", "housing", -rent)

        for i, udx in enumerate(utility_days):
            if slot == udx:
                name, lo, hi = _UTILITIES[i]
                amount = -round(rng.uniform(lo, hi), 2)
                if balance + amount < -overdraft_limit and rng.random() < 0.6:
                    post(day, f"{name} DD - RETURNED unpaid", "fees", -12.0)
                else:
                    post(day, name, "utilities", amount)

        if rng.random() < 0.42:
            basket = rng.uniform(9.0, 62.0) * (1.0 - 0.25 * spend_stress)
            post(day, rng.choice(_GROCERS), "groceries", -round(basket, 2))

        if rng.random() < 0.18:
            post(day, "TfL / fuel", "transport", -round(rng.uniform(3.0, 48.0), 2))

        # Discretionary spend contracts under stress — but only on average. Some stressed
        # customers keep spending, which is exactly the ambiguity a human reviewer argues over.
        if rng.random() < 0.30 * (1.0 - 0.55 * spend_stress) + 0.06:
            name, lo, hi = rng.choice(_DISCRETIONARY)
            post(day, name, "discretionary", -round(rng.uniform(lo, hi), 2))

        # Informal support: a transfer in from family. Reads as distress to some reviewers and
        # as ordinary household plumbing to others.
        if rng.random() < 0.02 + 0.05 * buffer_stress:
            post(day, "Transfer in - family", "transfer", round(rng.uniform(20.0, 400.0), 2))

        if slot == (payday + 2) % DAYS_PER_MONTH and rng.random() > 0.35 * buffer_stress:
            post(day, "Savings standing order", "savings", -round(rng.uniform(25.0, 250.0), 2))

        if balance < 0 and slot == (payday + DAYS_PER_MONTH - 1) % DAYS_PER_MONTH:
            post(day, "Arranged overdraft usage fee", "fees", -round(rng.uniform(3.0, 18.0), 2))

    return out


def account_snapshot(
    customer_id: str,
    latent_risk: float,
    seed: int,
    as_of_day: int,
    window_days: int = WINDOW_DAYS,
    transactions: list[Transaction] | None = None,
) -> AccountSnapshot:
    """Aggregate the window into the fields a reviewer actually reads."""
    txns = (
        transactions
        if transactions is not None
        else generate_history(customer_id, latent_risk, seed, as_of_day, window_days)
    )
    rng = _rng(customer_id, seed, "profile")

    salaries = [t.amount for t in txns if t.category == "salary"]
    balances = [t.balance_after for t in txns]
    opening = balances[0] - txns[0].amount if txns else 0.0
    closing = balances[-1] if balances else opening

    # "Days in overdraft" is counted as distinct days on which the balance closed negative --
    # what an account screen shows, not a continuous-time integral.
    negative_days = sorted({t.day for t in txns if t.balance_after < 0})

    essential = sum(-t.amount for t in txns if t.category in ESSENTIAL_CATEGORIES)
    discretionary = sum(-t.amount for t in txns if t.category in DISCRETIONARY_CATEGORIES)

    salary_change = 0.0
    if len(salaries) >= 2 and salaries[0] > 0:
        salary_change = 100.0 * (salaries[-1] - salaries[0]) / salaries[0]

    ordered = sorted(salaries)
    median_salary = ordered[len(ordered) // 2] if ordered else 0.0

    return AccountSnapshot(
        customer_id=customer_id,
        as_of_day=as_of_day,
        product=rng.choice(("Everyday Current", "Reward Current", "Basic Current")),
        tenure_months=rng.randint(7, 260),
        current_balance=round(closing, 2),
        overdraft_limit=_overdraft_limit(txns),
        days_in_overdraft=len(negative_days),
        lowest_balance=round(min(balances), 2) if balances else 0.0,
        balance_trend=round(closing - opening, 2),
        salary_credits=len(salaries),
        expected_salary_credits=max(1, window_days // DAYS_PER_MONTH),
        median_salary_credit=round(median_salary, 2),
        salary_change_pct=round(salary_change, 1),
        returned_direct_debits=sum(1 for t in txns if "RETURNED" in t.description),
        fee_charges=sum(1 for t in txns if t.category == "fees"),
        essential_spend=round(essential, 2),
        discretionary_spend=round(discretionary, 2),
        savings_balance=round(sum(-t.amount for t in txns if t.category == "savings"), 2),
    )


def _overdraft_limit(txns: list[Transaction]) -> float:
    """Recover the limit the generator used, from how deep the account was allowed to go."""
    worst = min((t.balance_after for t in txns), default=0.0)
    for limit in OVERDRAFT_LADDER:
        if worst >= -limit:
            return limit
    return OVERDRAFT_LADDER[-1]


def synthesize_prior_cases(
    customer_id: str, latent_risk: float, seed: int, as_of_day: int
) -> tuple[PriorCase, ...]:
    """Cases a human already worked. Investigations rarely start on a blank customer.

    Deliberately weak on latent risk — it nudges *how many* prior cases exist and nothing else.
    Resolutions are drawn from the seed, so a dismissed case is not a coded outcome.
    """
    rng = _rng(customer_id, seed, "prior-cases")
    n = 0
    if rng.random() < 0.25 + 0.25 * _clamp(latent_risk):
        n = rng.choice((1, 1, 2))

    families = ("churn_intent", "financial_distress", "complaint_escalation", "life_event")
    teams = {
        "churn_intent": "retention",
        "financial_distress": "collections",
        "complaint_escalation": "complaints",
        "life_event": "vulnerability",
    }
    notes = {
        "dismissed": "Reviewer judged the signal isolated; no action taken.",
        "resolved": "Payment plan agreed and completed; case closed.",
        "referred": "Referred to specialist team; awaiting their disposition.",
        "open": "Still open with the owning team.",
    }

    cases: list[PriorCase] = []
    for i in range(n):
        family = rng.choice(families)
        resolution = rng.choice(("dismissed", "dismissed", "resolved", "referred", "open"))
        opened = max(0, as_of_day - rng.randint(60, 540))
        cases.append(
            PriorCase(
                case_id=f"{customer_id}-PC{i}",
                opened_on_day=opened,
                signal_type=family,
                owning_team=teams[family],
                resolution=resolution,
                note=notes[resolution],
            )
        )
    return tuple(sorted(cases, key=lambda c: c.opened_on_day))
