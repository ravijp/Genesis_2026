"""`tools/stream_fixture.py`: the last hop between a stream artifact and a browser.

The same claim as `test_ui.py` makes about the reviewer fixture, checked in the same three places:
`earshot.stream` refuses to build a leaking payload, this file asserts the tool refuses one too,
and `ui/smoke.mjs` greps the generated file. Three checks because this is the last thing standing
before a screen someone demonstrates to a bank.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import stream_fixture
from stream_fixture import FixtureError, build, render

from earshot.cli import stream_inputs
from earshot.extract import OfflineLexiconExtractor
from earshot.stream import run_stream, stream_payload
from earshot.tenants import NORTHWIND, TENANTS

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def artifact() -> dict:
    """One offline stream artifact. Keyless, so this file needs no credentials and no network."""
    t = NORTHWIND
    conversations, context_for = stream_inputs(t)
    run = run_stream(
        t,
        conversations,
        OfflineLexiconExtractor(),
        provider=None,
        context_for=context_for,
        investigate_limit=0,
    )
    return stream_payload(
        run,
        {
            "tenant_id": t.tenant_id,
            "reader": "offline-lexicon",
            "provider": "offline-rules",
            "asr": "none",
        },
    )


def test_blocks_are_passed_through_untouched(artifact: dict) -> None:
    """The fixture reformats; it never computes. If it starts adjusting a score there are two
    scorers in the system and one of them is a build script."""
    payload = build([artifact])
    assert payload["tenants"] == [artifact]


def test_the_index_names_every_tenant(artifact: dict) -> None:
    payload = build([artifact])
    assert [row["tenant_id"] for row in payload["index"]] == [artifact["tenant"]["tenant_id"]]


def test_costs_are_never_summed_across_deployments(artifact: dict) -> None:
    """Each tenant is a separate customer of this system. A portfolio total is a number that
    would never appear on anyone's invoice, so the payload must not carry one."""
    payload = build([artifact])
    assert "totals" not in payload
    assert all("totals" in row for row in payload["index"])


def test_two_artifacts_for_one_tenant_are_refused(artifact: dict) -> None:
    with pytest.raises(FixtureError, match="same tenant"):
        build([artifact, artifact])


def test_an_artifact_that_streamed_nothing_is_refused(artifact: dict) -> None:
    with pytest.raises(FixtureError, match="streamed nothing"):
        build([{**artifact, "frames": []}])


def test_an_artifact_missing_the_current_shape_is_refused(artifact: dict) -> None:
    """A missing key renders as a blank panel with no error, which on stage reads as "the product
    has nothing to show" rather than "the fixture is stale"."""
    crippled = {k: v for k, v in artifact.items() if k != "teams"}
    with pytest.raises(FixtureError, match="missing"):
        build([crippled])


def test_no_answer_key_field_reaches_the_browser(artifact: dict) -> None:
    payload = build([artifact])
    leaked = stream_fixture._all_keys(payload) & stream_fixture.ANSWER_KEY_FIELDS
    assert not leaked, f"answer-key fields bound for a browser: {sorted(leaked)}"


def test_the_guard_actually_fires(artifact: dict) -> None:
    """A guard nobody has seen fail is a guard nobody knows works."""
    poisoned = json.loads(json.dumps(artifact))
    poisoned["frames"][0]["reader"]["latent_risk"] = 0.9
    with pytest.raises(FixtureError, match="answer-key"):
        build([poisoned])


def test_a_dead_citation_fails_the_build(artifact: dict) -> None:
    """"Read in context" is what makes a citation checkable; a dead link there is worse than
    no link, so it fails the build rather than the reviewer."""
    with pytest.raises(FixtureError, match="no transcript"):
        build([{**artifact, "conversations": {}, "cases": {
            "C": {"evidence": [{"conversation_id": "GONE"}]}
        }}])


def test_the_rendered_file_is_a_script_not_json(artifact: dict) -> None:
    text = render(build([artifact]))
    assert text.startswith("// GENERATED")
    assert "window.EARSHOT_STREAM = {" in text
    assert "No audio was transcribed" in text


def test_the_committed_stream_file_covers_every_tenant() -> None:
    """`ui/stream.js` is committed so the demo runs from a fresh clone with no Python and no key.

    Checked by parsing the committed file rather than by regenerating: what a judge opens is that
    file, and a tenant added to `tenants.py` without a re-record is a pill on screen that leads
    to an empty player.
    """
    path = ROOT / "ui" / "stream.js"
    assert path.exists(), "ui/stream.js is missing; run tools/stream_fixture.py"
    text = path.read_text(encoding="utf-8")
    body = text.split("window.EARSHOT_STREAM = ", 1)[1].rsplit(";", 1)[0]
    payload = json.loads(body)
    shipped = {block["tenant"]["tenant_id"] for block in payload["tenants"]}
    assert shipped == {t.tenant_id for t in TENANTS}, (
        f"ui/stream.js ships {sorted(shipped)} but tenants.py defines "
        f"{sorted(t.tenant_id for t in TENANTS)} — re-record and rebuild the fixture"
    )
    for block in payload["tenants"]:
        assert block["manifest"]["asr"] == "none"
        assert block["cases"], f"{block['tenant']['tenant_id']} ships no worked case"
