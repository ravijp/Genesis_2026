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

    # The contradiction this guards is narrating "would flag" for a customer the demo SELECTED
    # for the property that per-call detection never alerts on them. When no such customer
    # exists in the dataset, the demo takes its fallback path and says so loudly -- "NOT an
    # instance of the claim" -- and `test_demo_reports_a_real_instance_or_says_it_has_none`
    # holds it to that. Showing the nearest arc AND disclosing that it is not an instance is the
    # honest branch; forbidding "would flag" there would make the demo suppress evidence about
    # an arc it is openly telling the audience is not an instance.
    #
    # This started mattering on 2026-08-30: with the widened fragment pools `clean == 0`, so the
    # fallback is the live path rather than a rare branch.
    if "NOT an instance of the claim" not in out:
        assert "would flag" not in out, (
            "the demo narrated 'would flag' for a customer it selected because per-call "
            "detection never alerts on them — selection and narration are asking different "
            "questions:\n\n"
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


def test_demo_does_not_unsay_its_own_disclaimer_when_the_beat_fails(cli, capsys) -> None:
    """On a dataset with no instance of the claim, the demo warned honestly and then closed with
    "this is one instance of it" — and the closing line is the one an audience keeps.

    Seed 20260812 at 200 customers is a dataset where the count is genuinely zero.
    """
    assert cli.cmd_demo(replace(SMALL, seed=20260812, corpus=replace(SMALL.corpus, n_customers=200))) == 0
    out = capsys.readouterr().out

    if "NOT an instance of the claim" in out:
        assert "this is one instance of it" not in out, (
            "the demo warned that it has no instance of the claim and then asserted it had one"
        )


def test_demo_never_calls_the_baseline_flagged_below_its_own_threshold(cli, capsys) -> None:
    """A "would flag" printed beside a score under the threshold on the line above hands the
    audience the counter-argument. Queue membership alone is not enough to print it."""
    assert cli.cmd_demo(replace(SMALL, seed=20260812, corpus=replace(SMALL.corpus, n_customers=200))) == 0
    out = capsys.readouterr().out

    cut = float(next(li for li in out.splitlines() if "per-call threshold" in li).split()[-1])
    for line in out.splitlines():
        if line.strip().startswith("per-call ") and "would flag" in line:
            score = float(line.split()[1])
            assert score >= cut, (
                f"demo printed 'would flag' at {score} against its own threshold of {cut}: {line}"
            )


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


# ---- the persisted case (W1) ------------------------------------------------------------------


ANSWER_KEY_FIELDS = {
    "stratum",
    "outcome",
    "outcome_day",
    "latent_risk",
    "financial_state",
    "seeded",
    "seeded_signals",
    "lead_days",
}


def _all_keys(obj) -> set[str]:
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in _all_keys(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in _all_keys(v)}
    return set()


def test_the_investigate_artifact_carries_the_whole_case_not_just_the_verdict(
    cli, tmp_path
) -> None:
    """Until W1 the artifact held `decision` and `trace` only, so the score, the signal type, the
    threshold and every retro field died with the process — and all three reviewer-UI beats
    (ranked list, evidence chain, retro re-score) had nothing on disk to render.

    This asserts the artifact is sufficient on its own. The shortcut it rules out is a UI that
    regenerates the corpus from `manifest.seed` to recover the missing fields, which would put
    the answer key behind a client-facing screen.
    """
    import json

    assert cli.cmd_investigate(SMALL, "offline", limit=1) == 0
    written = list((tmp_path / "runs").glob("investigate-*.json"))
    assert len(written) == 1, f"expected one artifact, found {written}"
    cases = json.loads(written[0].read_text(encoding="utf-8"))["cases"]
    assert cases, "the run investigated nothing, so this test proves nothing"

    for case in cases:
        missing = {
            "case_id",
            "customer_id",
            "signal_type",
            "score",
            "score_at_open",
            "threshold",
            "opened_on_day",
            "as_of_day",
            "opened_by_conversation",
            "evidence",
            "status",
            "decision",
            "trace",
        } - set(case)
        assert not missing, f"the reviewer UI cannot render this case from disk: {missing}"
        assert case["evidence"], "no evidence chain — the middle beat has nothing to show"
        for row in case["evidence"]:
            assert {"score_at_write", "score_now", "retro_delta", "load_bearing"} <= set(row), (
                "an evidence row without its retro fields; the retro re-score beat is dead"
            )
        assert [r["day"] for r in case["evidence"]] == sorted(r["day"] for r in case["evidence"])

    leaked = _all_keys(cases) & ANSWER_KEY_FIELDS
    assert not leaked, f"answer-key fields on a client-facing artifact: {sorted(leaked)}"


def test_the_investigate_artifact_carries_the_transcripts_behind_its_quotes(cli, tmp_path) -> None:
    """A reviewer checks a cited quote by reading the turn around it. Deployed those transcripts
    come from S3; the artifact carries them in the same wire format so the UI has one code path.

    They come from the `ToolContext` the agent saw — never from regenerating the corpus, which is
    what would put `stratum`, `outcome` and `latent_risk` behind a client-facing screen.
    """
    import json

    from earshot.aws.transcripts import parse_conversation

    assert cli.cmd_investigate(SMALL, "offline", limit=1) == 0
    written = next(iter((tmp_path / "runs").glob("investigate-*.json")))
    artifact = json.loads(written.read_text(encoding="utf-8"))
    conversations = artifact["conversations"]
    assert conversations, "no transcripts, so no quote can be read in context"

    cited = {
        row["conversation_id"] for case in artifact["cases"] for row in case["evidence"]
    }
    assert cited <= set(conversations), (
        f"cited conversations with no transcript: {sorted(cited - set(conversations))}"
    )
    for payload in conversations.values():
        parse_conversation(payload)  # the S3 wire format, or the UI has two code paths

    leaked = _all_keys(conversations) & ANSWER_KEY_FIELDS
    assert not leaked, f"answer-key fields on a transcript: {sorted(leaked)}"
