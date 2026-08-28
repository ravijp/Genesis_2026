"""The deployment profile: a per-client configuration layer with no per-client code.

One profile ships. The claim these tests protect is therefore *not* "look, three banks" — it is
that onboarding a second client is configuration: a corpus, a tuning, a threshold, a team map, and
a description of where the seams are. So the tests exercise the mechanism rather than counting
entries, and one of them builds a second deployment on the spot to prove the layer actually varies
what it says it varies.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from earshot.agent.schemas import OwningTeam
from earshot.config import RunConfig, ScoringConfig
from earshot.schema import SignalType
from earshot.tenants import CANONICAL_TEAMS, DEFAULT_TENANT, TENANTS, Tenant, resolve, tenant

# The canonical routing slots, taken from the decision contract itself rather than retyped. If
# `OwningTeam` gains a value, this test tells the deployment profiles about it.
CONTRACT_TEAMS = set(OwningTeam.__args__) - {"none"}


def test_at_least_one_deployment_ships() -> None:
    assert TENANTS
    assert DEFAULT_TENANT in TENANTS


def test_deployment_ids_are_unique() -> None:
    ids = [t.tenant_id for t in TENANTS]
    assert len(set(ids)) == len(ids)


def test_the_configuration_layer_actually_varies_the_scoring() -> None:
    """A second client is configuration, not code — proved by building one and scoring differently.

    This is the load-bearing claim behind "we integrate into your stack". If two deployments with
    different half-lives produced the same ledger behaviour, the per-client layer would be a label
    and the honest thing would be to delete it. So the test constructs a second deployment and
    asserts the tuning reaches the scorer.
    """
    from earshot.memory import SignalLedger
    from earshot.schema import Channel, ExtractedSignal

    base = DEFAULT_TENANT
    impatient = replace(
        base,
        tenant_id="impatient",
        name="Second Client",
        run=replace(
            base.run,
            scoring=ScoringConfig(
                half_life_days={
                    SignalType.CHURN_INTENT.value: 5.0,
                    SignalType.FINANCIAL_DISTRESS.value: 5.0,
                    SignalType.COMPLAINT_ESCALATION.value: 5.0,
                    SignalType.LIFE_EVENT.value: 5.0,
                }
            ),
        ),
    )
    signal = ExtractedSignal(
        customer_id="C1",
        conversation_id="C1-C0",
        signal_type=SignalType.COMPLAINT_ESCALATION,
        confidence=0.8,
        evidence_quote="this has been going on for months",
        turn_index=1,
        day=0,
        channel=Channel.CALL,
    )
    scores = []
    for deployment in (base, impatient):
        ledger = SignalLedger(deployment.run.scoring)
        ledger.append(signal)
        scores.append(ledger.score("C1", SignalType.COMPLAINT_ESCALATION, as_of_day=90).score)
    assert scores[0] > scores[1], (
        "a five-day half-life scored the same 90-day-old signal as a ninety-day one — the "
        f"per-client tuning is not reaching the scorer: {scores}"
    )


@pytest.mark.parametrize("t", TENANTS, ids=lambda t: t.tenant_id)
def test_team_map_covers_every_slot_in_the_decision_contract(t: Tenant) -> None:
    """A slot with no local name renders as the raw canonical string on a client screen."""
    assert set(t.teams) == CONTRACT_TEAMS == set(CANONICAL_TEAMS)


@pytest.mark.parametrize("t", TENANTS, ids=lambda t: t.tenant_id)
def test_team_names_are_unique_within_a_deployment(t: Tenant) -> None:
    assert len(set(t.teams.values())) == len(t.teams)


def test_team_label_falls_back_rather_than_raising() -> None:
    """`owning_team` can be `"none"`. A decision that routed nowhere must still render."""
    t = DEFAULT_TENANT
    assert t.team_label("none") == "unrouted"
    assert t.team_label(None) == "unrouted"
    assert t.team_label("not_a_team") == "not_a_team"


@pytest.mark.parametrize("t", TENANTS, ids=lambda t: t.tenant_id)
def test_integration_seams_describe_a_layer_not_a_platform(t: Tenant) -> None:
    """Most stages must be the client's own systems, or the integration story is not true.

    The screen says "this is a layer, not a platform" and counts the seams to prove it. If we ever
    own more of the pipeline than the client does, that sentence becomes false and this test is
    what says so before a slide does.
    """
    assert t.integration, f"{t.tenant_id} describes no seams, so the deployment screen is empty"
    ours = [s for s in t.integration if s.ours]
    theirs = [s for s in t.integration if not s.ours]
    assert theirs, "every stage is ours; that is a platform, not an integration"
    assert len(theirs) >= len(ours), (
        f"{t.tenant_id}: we own {len(ours)} of {len(t.integration)} stages. The claim on the "
        f"deployment screen is that most of the pipeline is the client's existing systems."
    )


@pytest.mark.parametrize("t", TENANTS, ids=lambda t: t.tenant_id)
def test_the_transcription_seam_is_theirs_and_says_so(t: Tenant) -> None:
    """There is no speech recognition in this system, and the seam list must not imply one.

    Asserted rather than trusted because this is the single most tempting thing to fudge on a
    stage: a diagram with an unlabelled "transcription" box reads as though we do it.
    """
    speech = [s for s in t.integration if "speech" in s.stage.lower()]
    assert speech, f"{t.tenant_id} does not name where speech becomes text"
    for seam in speech:
        assert not seam.ours, "the transcription stage is marked as ours; we do not build one"


@pytest.mark.parametrize("t", TENANTS, ids=lambda t: t.tenant_id)
def test_public_payload_withholds_the_seed(t: Tenant) -> None:
    """Nothing tenant-shaped carries the seed.

    The run *manifest* does, deliberately, as provenance a judge can reproduce from — see
    `ui/README.md`, which states the narrower guarantee that actually holds. What must not happen
    is the seed arriving twice, in a shape nobody is checking.
    """
    public = t.public()
    assert "seed" not in public
    assert str(t.run.seed) not in repr(public)
    assert public["synthetic"] is True
    assert public["integration"], "the deployment screen reads its seams from public()"


def test_resolve_all_returns_declaration_order() -> None:
    assert [t.tenant_id for t in resolve("all")] == [t.tenant_id for t in TENANTS]


def test_resolve_takes_a_list_in_the_order_given() -> None:
    """The multi-deployment path stays exercised with one profile shipping.

    Kept because this is the seam a second client arrives through: an untested `resolve()` is one
    that breaks on the first day of the second engagement.
    """
    ids = [t.tenant_id for t in TENANTS]
    wanted = ",".join(reversed(ids))
    assert [t.tenant_id for t in resolve(wanted)] == list(reversed(ids))


def test_unknown_tenant_names_the_known_ones() -> None:
    """A typo surfaces as the fix, not as a KeyError three frames later."""
    with pytest.raises(KeyError, match="known:"):
        tenant("nrothwind")


def test_a_run_config_is_all_a_deployment_needs() -> None:
    """`Tenant` must stay constructible from plain configuration, with no code hook.

    The moment a deployment needs a callback or a subclass, onboarding stops being configuration
    and the integration claim gets more expensive than the screen says it is.
    """
    minimal = Tenant(
        tenant_id="x",
        name="X",
        industry="Y",
        book="Z",
        run=RunConfig(),
        threshold=0.5,
        teams={slot: slot.title() for slot in CANONICAL_TEAMS},
    )
    assert minimal.team_label("retention") == "Retention"
    assert minimal.public()["integration"] == []
