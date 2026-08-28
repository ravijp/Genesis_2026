"""Tenant profiles: the same engine, on its own corpus, tuned to its own book of business.

**What a tenant is, precisely.** One `RunConfig` (corpus mix + scoring constants), one fixed
alert threshold, and one mapping from the four canonical owning teams onto the names that
enterprise actually uses. That is all. There is no per-tenant code path, no per-tenant scorer and
no per-tenant prompt -- `memory.py` scores all three, `agent/` investigates all three, and
`InvestigationDecision.owning_team` stays the closed five-value literal it has always been.

**Why the team map is display-only.** Widening `OwningTeam` per tenant would put an
enterprise-supplied string inside the model's decision contract, and `extra="forbid"` plus a
`Literal` is the thing that stops a model inventing a routing destination. So the contract is
fixed and each tenant supplies the local label for each fixed slot. A new enterprise is a
dictionary, never a schema change.

**Why the threshold is a fixed cut and not the budget-derived one.** A streaming handler has no
population to rank against -- it sees one conversation at a time and must decide immediately.
This mirrors `aws/ingest.py` exactly, which is the deployed path. `cli._queue`'s budget-derived
threshold answers a different question (who are the top 10% today) and the two numbers will
disagree about who crossed. Keeping them apart is deliberate; see `docs/ops/state-of-play.md`.

**The differences between the three profiles are risk-book differences, not decoration.** A card
issuer's complaint half-life is genuinely shorter than a mortgage servicer's hardship half-life,
and a servicer genuinely reviews fewer, larger cases. If the three tenants scored identically the
multi-enterprise claim would be a skin, and a judge would be right to say so.

**Every tenant is synthetic.** These are invented companies over generated conversations. The
names exist so three deployments are distinguishable on screen, and every surface that shows one
also says so.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .config import CorpusConfig, RunConfig, ScoringConfig
from .schema import SignalType

# The canonical routing slots. Fixed, because they are `agent.schemas.OwningTeam` minus "none",
# which is the no-route value and is never a team a case lands on.
CANONICAL_TEAMS = ("retention", "collections", "vulnerability", "complaints")


@dataclass(frozen=True)
class Tenant:
    """One enterprise deployment: a corpus, a tuning, a threshold, and local team names."""

    tenant_id: str
    name: str
    industry: str
    # What this book of business is, in the one line a demo audience needs before the numbers
    # mean anything. Displayed above the stream.
    book: str
    run: RunConfig
    # Fixed alert cut. Per-tenant because a servicer with four reviewers and a card issuer with
    # forty do not accept the same alert rate, and that is the real reason thresholds differ.
    threshold: float
    # canonical slot -> the name this enterprise calls it. Display only; see the module docstring.
    teams: dict[str, str]
    # How many crossings this tenant's demo investigates with a model. Bounded per tenant so a
    # keyed re-record costs a predictable amount rather than however many customers crossed.
    investigate: int = 4
    accent: str = "#4f7cff"

    def team_label(self, canonical: str | None) -> str:
        """The local name for a canonical team, or the canonical string if there is no mapping.

        Falls back rather than raising: `owning_team` can be `"none"`, and a decision that routed
        nowhere must still render.
        """
        if not canonical or canonical == "none":
            return "unrouted"
        return self.teams.get(canonical, canonical)

    def public(self) -> dict:
        """What a browser is allowed to know about a tenant. No seed, no corpus parameters.

        The seed is withheld on purpose: it is the one value from which `stratum`, `outcome` and
        `latent_risk` can be regenerated, and `tools/ui_fixture.py` exists because putting it
        behind a client-facing screen is the shortcut that must not be taken.
        """
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "industry": self.industry,
            "book": self.book,
            "threshold": round(self.threshold, 4),
            "teams": dict(self.teams),
            "accent": self.accent,
            "synthetic": True,
        }


def _corpus(**overrides) -> CorpusConfig:
    return replace(CorpusConfig(), **overrides)


def _scoring(**overrides) -> ScoringConfig:
    return replace(ScoringConfig(), **overrides)


# -- the three profiles -----------------------------------------------------------------------

NORTHWIND = Tenant(
    tenant_id="northwind",
    name="Northwind Retail Bank",
    industry="Retail banking",
    book=(
        "Current accounts and overdrafts. Mixed channels, long relationships, and attrition is "
        "the expensive failure."
    ),
    run=RunConfig(
        seed=20260828,
        corpus=_corpus(
            n_customers=44,
            conversations_per_customer=(2, 4),
            horizon_days=180,
        ),
        scoring=_scoring(),
    ),
    threshold=0.60,
    teams={
        "retention": "Retention Desk",
        "collections": "Collections",
        "vulnerability": "Vulnerable Customer Unit",
        "complaints": "Complaints & Redress",
    },
    accent="#4f7cff",
)

MERIDIAN = Tenant(
    tenant_id="meridian",
    name="Meridian Card Services",
    industry="Card issuing",
    book=(
        "Credit cards and disputes. High contact volume over a short horizon; complaints go "
        "stale fast, so a grievance from four months ago is not live risk."
    ),
    run=RunConfig(
        # A different seed is not cosmetic: two tenants on one seed would be the same customers
        # under two brands, which is exactly the fake diversity this is meant to avoid.
        seed=20260829,
        corpus=_corpus(
            n_customers=52,
            conversations_per_customer=(3, 5),
            # Short horizon + more conversations = the dense contact pattern a card book has.
            horizon_days=110,
            stratum_weights={
                "concentrated": 0.22,
                "diffuse": 0.26,
                "decoy_extractor": 0.20,
                "decoy_accumulator": 0.14,
                "null": 0.18,
            },
        ),
        scoring=_scoring(
            # A card complaint decays in weeks, not a quarter. This is the substantive tuning
            # difference: the same evidence chain scores lower here than at Harborline.
            half_life_days={
                SignalType.CHURN_INTENT.value: 90.0,
                SignalType.FINANCIAL_DISTRESS.value: 150.0,
                SignalType.COMPLAINT_ESCALATION.value: 45.0,
                SignalType.LIFE_EVENT.value: 240.0,
            },
        ),
    ),
    # More reviewers, so a lower bar. The alert rate a team accepts IS the threshold.
    threshold=0.52,
    teams={
        "retention": "Loyalty & Save",
        "collections": "Credit Operations",
        "vulnerability": "Financial Support",
        "complaints": "Disputes & Complaints",
    },
    accent="#c46bd8",
)

HARBORLINE = Tenant(
    tenant_id="harborline",
    name="Harborline Lending",
    industry="Mortgage servicing",
    book=(
        "Secured lending. Few conversations per customer over a long horizon, and hardship is "
        "the signal that matters -- a job loss stays relevant for a year."
    ),
    run=RunConfig(
        seed=20260830,
        corpus=_corpus(
            n_customers=38,
            conversations_per_customer=(2, 4),
            horizon_days=300,
            stratum_weights={
                "concentrated": 0.20,
                "diffuse": 0.34,
                "decoy_extractor": 0.12,
                "decoy_accumulator": 0.10,
                "null": 0.24,
            },
            # A servicer's book turns over slowly; the background rate is lower and the risk
            # gradient steeper, because arrears on a secured loan really do predict the outcome.
            outcome_base_rate=0.02,
            outcome_risk_gain=0.22,
        ),
        scoring=_scoring(
            half_life_days={
                SignalType.CHURN_INTENT.value: 150.0,
                SignalType.FINANCIAL_DISTRESS.value: 320.0,
                SignalType.COMPLAINT_ESCALATION.value: 120.0,
                SignalType.LIFE_EVENT.value: 400.0,
            },
        ),
    ),
    # Four reviewers on a book of 38. A high bar is the honest consequence, and it is why this
    # tenant's queue is short and its cases are heavy.
    threshold=0.68,
    teams={
        "retention": "Portfolio Retention",
        "collections": "Arrears Management",
        "vulnerability": "Hardship Team",
        "complaints": "Complaints Handling",
    },
    accent="#3fae8f",
)

TENANTS: tuple[Tenant, ...] = (NORTHWIND, MERIDIAN, HARBORLINE)
BY_ID: dict[str, Tenant] = {t.tenant_id: t for t in TENANTS}


def tenant(tenant_id: str) -> Tenant:
    """Look one up, or say which ones exist. A typo should not surface as a KeyError."""
    try:
        return BY_ID[tenant_id]
    except KeyError:
        known = ", ".join(BY_ID)
        raise KeyError(f"unknown tenant {tenant_id!r}; known: {known}") from None


def resolve(names: str) -> list[Tenant]:
    """`"all"`, or a comma-separated list of tenant ids, in the order given."""
    if names.strip() == "all":
        return list(TENANTS)
    return [tenant(part.strip()) for part in names.split(",") if part.strip()]
