"""The reviewer UI's data, and every screen rendering it.

Two halves. `ui_fixture.build()` is pure Python and is tested directly. The page itself is checked
by `ui/smoke.mjs`, which renders all seven routes against a stub DOM in node — a route that throws,
a field renamed in `case_record()` that the page still reads, or a placeholder leaking into the
markup all fail there and nowhere else. It is invoked from here so `uv run pytest` covers it, and
skipped when node is absent so a fresh clone with no toolchain still runs green.

The claim that matters most: **nothing reaches the browser that a client must not see.** It is
checked in three places on purpose — the fixture refuses to write it, this file asserts it, and the
smoke test greps the generated file — because this is the last hop before a screen someone
demonstrates to a bank.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import ui_fixture
from ui_fixture import FixtureError, build

from earshot.aws.api import _queue_row

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def artifact(tmp_path_factory) -> dict:
    """A real `earshot investigate` run — the only input this tool has. Module-scoped because
    generating a 400-customer corpus is the slow part and every test below reads the same one."""
    import importlib
    import os

    out = tmp_path_factory.mktemp("artifacts")
    os.environ["EARSHOT_ARTIFACTS"] = str(out)
    import earshot.cli as cli_module

    cli = importlib.reload(cli_module)
    from dataclasses import replace

    from earshot.config import DEFAULT

    run = replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=400))
    assert cli.cmd_investigate(run, "offline", limit=4) == 0
    written = next(iter((out / "runs").glob("investigate-*.json")))
    os.environ.pop("EARSHOT_ARTIFACTS", None)
    importlib.reload(cli_module)
    return json.loads(written.read_text(encoding="utf-8"))


def test_the_queue_rows_are_the_apis_own_rows(artifact: dict) -> None:
    """The offline screen and the deployed screen must render identical objects, so the fixture
    calls the same `_queue_row` the API does rather than building its own summary."""
    payload = build(artifact)
    for row, case in zip(payload["queue"]["cases"], sorted(
        artifact["cases"], key=lambda c: (-c["score"], c["case_id"])
    ), strict=True):
        assert row == _queue_row(case)


def test_the_queue_is_ranked_by_the_score_today(artifact: dict) -> None:
    """Same order `CaseStore.list_queue` returns off the GSI, and the same question `cli.py:_queue`
    asks: who should someone look at today, not who looked worst when their case opened."""
    scores = [row["score"] for row in build(artifact)["queue"]["cases"]]
    assert scores == sorted(scores, reverse=True)


def test_the_cases_are_passed_through_untouched(artifact: dict) -> None:
    """The fixture reformats; it never computes. If it ever starts adjusting a score or a delta,
    there are two scorers in the system and one of them is a build script."""
    payload = build(artifact)
    for case in artifact["cases"]:
        assert payload["cases"][case["case_id"]] == case


def test_no_answer_key_field_reaches_the_browser(artifact: dict) -> None:
    payload = build(artifact)
    leaked = ui_fixture.all_keys(payload) & ui_fixture.ANSWER_KEY_FIELDS
    assert not leaked, f"answer-key fields bound for a browser: {sorted(leaked)}"


def test_the_fixture_refuses_an_artifact_whose_quotes_have_no_transcript(artifact: dict) -> None:
    """"Read in context" is the affordance that makes a citation checkable. A dead link there is
    worse than no link, so this fails the build rather than the reviewer."""
    crippled = {**artifact, "conversations": {}}
    with pytest.raises(FixtureError, match="no transcript"):
        build(crippled)


def test_the_fixture_refuses_an_empty_run(artifact: dict) -> None:
    with pytest.raises(FixtureError, match="investigated nothing"):
        build({**artifact, "cases": []})


def test_the_rendered_file_is_a_script_not_json(artifact: dict) -> None:
    """The SPA has to load over `file://`, where a `fetch()` of a sibling JSON is blocked by the
    browser and a `<script src>` is not. A judging room with no wifi is the scenario."""
    text = ui_fixture.render(build(artifact))
    assert text.startswith("// GENERATED")
    assert "window.EARSHOT_DATA = {" in text
    assert "GENERATED" in text.splitlines()[0], "the file must say it is generated"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_every_screen_renders() -> None:
    """`ui/smoke.mjs` against the committed `ui/data.js`. Renders all seven routes, including the
    two that must degrade to 'not found' rather than throwing."""
    result = subprocess.run(
        [shutil.which("node"), str(ROOT / "ui" / "smoke.mjs")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "smoke OK" in result.stdout


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_every_colour_pair_on_screen_is_readable() -> None:
    """`ui/contrast.mjs`: the same screens, cascaded through the real stylesheets, with a WCAG
    ratio computed for every foreground/background pair the markup actually produces — in both
    themes, and with the tenant's inline accent override in place.

    It is a build gate rather than a review note because "sophisticated" is unfalsifiable and
    "4.5:1" is not. It also carries one rule that is ours rather than WCAG's: a sub-threshold
    ledger row renders at the panel's primary ink, because dimming retained evidence would draw
    the incumbent behaviour this product inverts (D-030)."""
    result = subprocess.run(
        [shutil.which("node"), str(ROOT / "ui" / "contrast.mjs")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "contrast OK" in result.stdout


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_committed_data_file_is_in_step_with_the_page() -> None:
    """`ui/data.js` is committed so the demo works from a fresh clone with no Python run. That only
    holds if it stays loadable and non-empty; a stale or truncated one fails the smoke test above,
    and this asserts the file is actually there to be stale."""
    data_js = ROOT / "ui" / "data.js"
    assert data_js.exists(), "ui/data.js is missing; run tools/ui_fixture.py"
    assert data_js.stat().st_size > 1000
