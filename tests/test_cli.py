"""The commands themselves, and the demo's internal consistency.

`cmd_demo` is the artefact that goes on screen at a gate, and until round 5 nothing tested it — which
is how it came to print "would flag" four lines under "per-call detection NEVER fires for them". The
tests here are about what the output *claims*, not about formatting: a demo that contradicts itself is
a presentation failure that no unit test of the ledger can catch.

Every command writes under `EARSHOT_ARTIFACTS`, redirected to a tmp path so a test run never touches
the committed artifacts.
"""

from __future__ import annotations

import importlib
from dataclasses import replace

import pytest

from earshot.config import DEFAULT

SMALL = replace(DEFAULT, corpus=replace(DEFAULT.corpus, n_customers=400))


@pytest.fixture
def cli(tmp_path, monkeypatch):
    """`earshot.cli` with its artifact directory redirected, reloaded so ARTIFACTS re-reads env."""
    monkeypatch.setenv("EARSHOT_ARTIFACTS", str(tmp_path))
    import earshot.cli as cli_module

    return importlib.reload(cli_module)


def test_demo_never_contradicts_its_own_headline_claim(cli, capsys) -> None:
    """The demo selects a customer BECAUSE per-call detection never alerts on them, so no line in
    the narration may then say the per-call arm would have flagged them.

    Selection asked the alert queue while the narration asked `score >= threshold`; the baseline's
    scores cluster hard at the cut, so the two disagreed on the chosen customer at every corpus
    size. The claim and the evidence under it have to come from one question.
    """
    assert cli.cmd_demo(SMALL) == 0
    out = capsys.readouterr().out

    assert "NEVER fires" in out, "the demo no longer states the claim this test is about"
    assert "would flag" not in out, (
        "the demo narrated 'would flag' for a customer it selected because per-call detection "
        "never alerts on them — selection and narration are asking different questions:\n\n"
        + "\n".join(line for line in out.splitlines() if "per-call" in line)
    )


def test_demo_reports_a_real_instance_or_says_it_has_none(cli, capsys) -> None:
    """A demo that shows a customer who is not an instance of the claim must say so.

    The honest failure mode is announcing it; the dishonest one is showing the nearest thing and
    letting the audience assume.
    """
    assert cli.cmd_demo(SMALL) == 0
    out = capsys.readouterr().out

    if "NOT an instance of the claim" in out:
        assert "No such customer exists" in out, "the disclaimer is half-printed"
    else:
        assert "outcome=none" not in out, (
            "the demo presented a customer with no outcome as the accumulation moment without "
            "printing the disclaimer that says it is not an instance of the claim"
        )


def test_demo_denominator_is_customers_not_customer_signal_pairs(cli, capsys) -> None:
    """`N of M` must count the same kind of thing on both sides.

    The numerator is built per (customer, signal type) and the denominator per customer, so a
    customer crossing on two signal types would make the ratio exceed 1.
    """
    assert cli.cmd_demo(SMALL) == 0
    out = capsys.readouterr().out

    line = next(li for li in out.splitlines() if " of " in li and "thin-evidence" in li)
    numerator, denominator = (int(tok) for tok in line.split() if tok.isdigit())
    assert numerator <= denominator, f"demo printed {numerator} of {denominator}: {line}"


def test_run_warns_that_a_single_dataset_is_not_publishable(cli, capsys) -> None:
    """`run` exists for debugging and has to say so itself — the rule cannot live only in prose."""
    assert cli.cmd_run(SMALL) == 0
    out = capsys.readouterr().out
    assert "sweep" in out and "publish" in out.lower(), (
        "`earshot run` no longer warns that its numbers are not quotable"
    )


def test_a_dirty_tree_is_recorded_in_the_run_manifest(cli) -> None:
    """A manifest naming a commit that cannot reproduce it is worse than naming nothing."""
    sha = cli._git_sha()
    assert sha, "no provenance recorded at all"
    if sha != "unknown":
        import subprocess

        changed = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert sha.endswith("-dirty") == bool(changed), (
            f"manifest SHA {sha!r} does not reflect whether the tree is dirty"
        )
