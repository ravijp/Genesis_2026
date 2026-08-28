"""The deployment profile: how this system is configured for one client's stack.

**This is not a product with customers of its own.** It is a layer that goes *into* a bank's
existing infrastructure — their telephony, their transcript store, their case management, their
reviewers. So a "tenant" here is a **deployment**: the client's book of business, the decay
half-lives their risk appetite implies, the alert threshold their review capacity can absorb, and
the names their org actually uses for the four routing destinations.

**One profile ships.** There was briefly a portfolio of three invented banks; it demonstrated the
configuration layer and nothing else, and three fake logos is a weaker claim than one deployment
described honestly. The machinery is unchanged — `resolve()`, the id lookup, the team map — because
that machinery *is* the per-client seam, and a second client is a second entry in `TENANTS`.

**Why the team map is display-only.** Widening `agent.schemas.OwningTeam` per client would put a
client-supplied string inside the model's decision contract, and the closed `Literal` plus
`extra="forbid"` is what stops a model inventing a routing destination that no queue drains. So
the contract is fixed at four slots and each deployment supplies the local label for each slot.
Onboarding a client is a dictionary, never a schema change.

**Why the threshold is a fixed cut.** A streaming consumer sees one conversation at a time and has
no population to rank against, so it cannot take the top 10% of anything. This mirrors
`aws/ingest.py`, which is the deployed path. `cli._queue`'s budget-derived threshold answers a
different question and the two disagree about who crossed; that is a property of streaming, and
both numbers are labelled wherever they appear.

**The book is synthetic.** The client below is invented and its conversations are generated, per
competition rules. Every screen that shows it says so.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .config import CorpusConfig, RunConfig, ScoringConfig
from .schema import SignalType

# The canonical routing slots: `agent.schemas.OwningTeam` minus "none", which is the no-route
# value and never a team a case lands on.
CANONICAL_TEAMS = ("retention", "collections", "vulnerability", "complaints")


@dataclass(frozen=True)
class Seam:
    """One stage of the deployed pipeline, and who owns it.

    The integration screen is built from these rather than from a drawing, so what is on stage
    cannot drift from what the code does. `ours=False` marks a system we do not build, do not
    replace and do not store a second copy of — which is most of the diagram, and is the point.
    """

    stage: str
    system: str
    ours: bool
    note: str


@dataclass(frozen=True)
class Tenant:
    """One client deployment: a book, a tuning, a threshold, local team names, and its seams."""

    tenant_id: str
    name: str
    industry: str
    book: str
    run: RunConfig
    threshold: float
    teams: dict[str, str]
    # How many crossings this deployment's demo investigates with a model. Bounded so a keyed
    # re-record costs a predictable amount rather than however many customers happened to cross.
    investigate: int = 6
    # How many conversations are read turn-by-turn for the narration screen. Bounded for the same
    # reason and reported separately: narration is the cost of showing the working, not of
    # reading the book.
    narrate: int = 6
    accent: str = "#4f7cff"
    integration: tuple[Seam, ...] = ()

    def team_label(self, canonical: str | None) -> str:
        """The local name for a canonical slot, or the canonical string if there is no mapping.

        Falls back rather than raising: `owning_team` can be `"none"`, and a decision that routed
        nowhere must still render.
        """
        if not canonical or canonical == "none":
            return "unrouted"
        return self.teams.get(canonical, canonical)

    def public(self) -> dict:
        """What a browser is allowed to know. No seed, no corpus parameters.

        The seed is withheld here because nothing tenant-shaped needs it. The run *manifest* does
        carry it, deliberately, as provenance a judge can reproduce from — see `ui/README.md`,
        which states the narrower guarantee that actually holds.
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
            "integration": [
                {"stage": s.stage, "system": s.system, "ours": s.ours, "note": s.note}
                for s in self.integration
            ],
        }


def _corpus(**overrides) -> CorpusConfig:
    return replace(CorpusConfig(), **overrides)


def _scoring(**overrides) -> ScoringConfig:
    return replace(ScoringConfig(), **overrides)


# The deployed pipeline, stage by stage. Six of these nine stages are the client's own systems,
# which is the shape of the claim: this is a layer, not a replacement. The two seams that matter
# commercially are the first `ours=True` (a transcript feed we consume, in whatever format they
# already produce) and the last (a case we hand back into the queue their reviewers already work).
_NORTHWIND_SEAMS = (
    Seam(
        "Conversations happen",
        "Client contact centre — telephony, web chat, complaints inbox",
        False,
        "Unchanged. We do not sit in the call path and nothing here depends on how they route "
        "or record a contact.",
    ),
    Seam(
        "Speech becomes text",
        "Client's existing transcription (Genesys, NICE, Verint, AWS Transcribe — whatever they run)",
        False,
        "**We do not do speech recognition and this system contains none.** Banks at this size "
        "already transcribe for QA and compliance; we consume that output. Where a client does "
        "not transcribe, this is the one component they must buy, and it is a commodity.",
    ),
    Seam(
        "Transcripts land",
        "Client transcript store / event bus",
        False,
        "We subscribe. `aws/transcripts.py` defines the wire format we accept; a shim from their "
        "shape to ours is a day of work and is the normal cost of an integration.",
    ),
    Seam(
        "Read every conversation",
        "earshot ingest — Lambda + SQS",
        True,
        "One model call per conversation, or several while a call is still open. Extracts signals "
        "with the verbatim quote behind each; drops anything it cannot quote.",
    ),
    Seam(
        "Accumulate, never discard",
        "earshot ledger — DynamoDB, append-only",
        True,
        "The part that does not exist in their stack today. Sub-threshold signals are retained "
        "and stay summable, so three faint months add up instead of overwriting each other.",
    ),
    Seam(
        "Re-score and threshold",
        "earshot memory.py — deterministic Python",
        True,
        "No model. Decay, corroboration, cross-channel and escalation are plain code, unit-tested "
        "and reproducible bit for bit. This is what makes the score auditable.",
    ),
    Seam(
        "Investigate a crossing",
        "earshot investigator — bounded agent loop, five read-only tools",
        True,
        "Reads the ledger, the transcripts and account state; returns a verdict with mandatory "
        "cited evidence and a routing destination. It cannot write anywhere and cannot contact "
        "anyone.",
    ),
    Seam(
        "Case lands in the queue",
        "Client case management / CRM (Salesforce, Pega, in-house)",
        False,
        "We hand back a case object, not a dashboard nobody logs into. The reviewer screens in "
        "`ui/` are a reference implementation for clients who want one, not the delivery.",
    ),
    Seam(
        "A human decides",
        "Client's own reviewers and their existing outbound policy",
        False,
        "**Every customer-facing action stays theirs.** There is no outbound surface anywhere in "
        "this system — no email, no dialler, no message — and tests assert the absence rather "
        "than a setting enforcing it.",
    ),
)

NORTHWIND = Tenant(
    tenant_id="northwind",
    name="Northwind Retail Bank",
    industry="Retail banking",
    book=(
        "Current accounts and overdrafts across voice, chat and the complaints inbox. Long "
        "relationships, and attrition is the expensive failure."
    ),
    run=RunConfig(
        seed=20260828,
        corpus=_corpus(
            n_customers=44,
            conversations_per_customer=(2, 4),
            horizon_days=180,
        ),
        scoring=_scoring(
            half_life_days={
                SignalType.CHURN_INTENT.value: 120.0,
                SignalType.FINANCIAL_DISTRESS.value: 200.0,
                SignalType.COMPLAINT_ESCALATION.value: 90.0,
                SignalType.LIFE_EVENT.value: 300.0,
            },
        ),
    ),
    threshold=0.60,
    teams={
        "retention": "Retention Desk",
        "collections": "Collections",
        "vulnerability": "Vulnerable Customer Unit",
        "complaints": "Complaints & Redress",
    },
    accent="#4f7cff",
    integration=_NORTHWIND_SEAMS,
)

TENANTS: tuple[Tenant, ...] = (NORTHWIND,)
BY_ID: dict[str, Tenant] = {t.tenant_id: t for t in TENANTS}

DEFAULT_TENANT = NORTHWIND


def tenant(tenant_id: str) -> Tenant:
    """Look one up, or say which ones exist. A typo should not surface as a KeyError."""
    try:
        return BY_ID[tenant_id]
    except KeyError:
        known = ", ".join(BY_ID)
        raise KeyError(f"unknown tenant {tenant_id!r}; known: {known}") from None


def resolve(names: str) -> list[Tenant]:
    """`"all"`, or a comma-separated list of tenant ids, in the order given.

    Kept general with one profile shipping: this is the seam a second client arrives through, and
    collapsing it to a constant now is a refactor someone would have to undo on the first day of
    the second engagement.
    """
    if names.strip() == "all":
        return list(TENANTS)
    return [tenant(part.strip()) for part in names.split(",") if part.strip()]
