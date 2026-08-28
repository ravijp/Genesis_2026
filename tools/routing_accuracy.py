"""AT-58 — when the investigator routes a case to an owning team, is it the right team?
Never measured before this.

    uv run python tools/routing_accuracy.py                          # most recent artifact
    uv run python tools/routing_accuracy.py --provider offline        # disambiguate by provider
    uv run python tools/routing_accuracy.py --artifact PATH           # a specific run

**Makes ZERO model API calls.** It scores an artifact `tools/verdict_accuracy.py` (AT-57) already
wrote to disk. It rebuilds the corpus that produced that artifact — from `manifest.seed` and
`manifest.population.customers` only — to recover each sampled customer's seeded `trajectory`
and the ledger's own `owning_team` map. Both rebuild steps run the same offline pipeline
`cli._queue` always uses regardless of which provider answered the investigation, so nothing
here spends money or calls a model even when scoring a `--provider bedrock` artifact.

**The answer key.** `CustomerTruth.trajectory` (`schema.py`) is the seeded signal family for a
customer, or `None` for a decoy-accumulator or null customer that was never given one. The
family -> team map is `schema.TRAJECTORY_TEAM`, hoisted out of `core/accounts.py`'s prior-case
generator so the generator and this scorer cannot end up disagreeing about what "correct" means
— the same failure mode `verdict_accuracy.sample()` avoids by importing `evals._outcome_customers`
instead of re-deriving "has an outcome" a second time.

**Why trajectory-present and trajectory-None never share a denominator.** A customer with a
seeded `trajectory` has one correct team, so a route is either right, wrong, or declined
(`owning_team="none"`). A customer with `trajectory is None` — decoy-accumulator (real weak
signals, seeded to corroborate and never resolve) or null (no trajectory at all) — has NO
correct team: nothing the agent could route to would be "right". Folding those customers into
an accuracy figure either manufactures wrong answers for a population that has none, or quietly
inflates accuracy if a null-safe "always say none" strategy is rewarded as correct on both
populations at once. So the null population gets its own report — how often it was routed
somewhere anyway, and at what confidence — never an accuracy rate.

**Why the confusion matrix, in full.** `docs/ops/state-of-play.md` records a qualitative read
from a streamed run: the agent seems to concentrate its routing on one or two teams and
sometimes declines to route at all. An overall accuracy number averages that away; the matrix
(truth team x routed team) turns the impression into counts a reviewer can act on.

**Why each miss is also classified by what it agrees with.** A "wrong" route can fail two
different ways: the agent may have read the ledger correctly and routed to the team its
*dominant signal at the crossing* implies, which simply was not the customer's true seeded
family (an evidence-consistent miss — the ledger genuinely carried mixed signal, or the
customer's later trajectory diverged from what was loudest at the crossing day); or the agent
may have routed somewhere the ledger's own evidence does not support at all (a misread). The
first calls the routing logic sound and the ledger's signal mix hard; the second calls the
model's team choice unmoored from the evidence it was given. A reviewer needs to know which,
so both are counted separately rather than pooled into one "wrong" bucket.

**Correctness of a decline.** `owning_team="none"` on a trajectory-present customer is scored
`declined`, not `wrong` — the agent chose not to guess rather than guessing incorrectly, which is
the same honest-abstention argument `verdict_accuracy.py` makes for `insufficient_evidence`.
It is reported separately from `correct` and `wrong` so an agent that declines often is visibly
different from one that is simply wrong often, even though neither is "right".
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Any

from earshot.cli import ARTIFACTS, _git_sha, _queue
from earshot.config import DEFAULT
from earshot.corpus import pipeline_fingerprint
from earshot.schema import TRAJECTORY_TEAM
from earshot.tenants import CANONICAL_TEAMS

# The `owning_team` vocabulary the schema actually permits (`agent/schemas.py:23`). Asserted
# against, not assumed: scoring a value the model can never emit fails silently and in the
# flattering direction, same rationale as `verdict_accuracy.VERDICTS`.
OWNING_TEAMS = (*CANONICAL_TEAMS, "none")


def _latest_verdict_artifact(provider: str | None) -> Path:
    """Newest `verdict-accuracy-*.json` in `ARTIFACTS`, optionally restricted to one provider.

    Mtime, not the seed/hash embedded in the filename: a rerun at the same seed overwrites
    nothing (the hash changes if the config does, the provider suffix if the arm does), so the
    newest file on disk is the newest measurement, full stop.
    """
    pattern = f"verdict-accuracy-*-{provider}.json" if provider else "verdict-accuracy-*.json"
    candidates = sorted(ARTIFACTS.glob(pattern), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise SystemExit(
            f"no artifact matching {pattern!r} in {ARTIFACTS} — run "
            f"tools/verdict_accuracy.py first (offline is free and keyless)"
        )
    return candidates[-1]


def rebuild_queue(manifest: dict[str, Any]):
    """Recover the corpus AT-57 investigated, from the seed and population size alone.

    `RunConfig.hash()` is asserted against `manifest.config_hash` before anything downstream
    runs. Scoring against a corpus that is not the one the artifact's investigations actually
    saw is not a wrong measurement, it is a confident one — the hash check is what makes this
    tool safe to trust rather than merely safe to run.
    """
    run = replace(
        DEFAULT,
        seed=manifest["seed"],
        corpus=replace(DEFAULT.corpus, n_customers=manifest["population"]["customers"]),
    )
    got = run.hash()
    want = manifest["config_hash"]
    if got != want:
        raise SystemExit(
            f"config hash mismatch: rebuilt {got!r}, artifact recorded {want!r}. The corpus "
            f"this would score is NOT the corpus AT-57 investigated — refusing to produce a "
            f"number against it. Likely cause: DEFAULT RunConfig (seed, corpus, scoring, "
            f"offline_miss_rate/offline_false_fire_rate in config.py) has changed since the "
            f"artifact was written."
        )
    # The config hash is necessary and NOT sufficient, learned the expensive way on 2026-08-28.
    # Fixing the corpus fragment re-plant defect changed which customers cross — 25 with an
    # outcome became 17, the threshold moved 0.7246 -> 0.6655 — while `config_hash` stayed
    # `3ebd9fb57097` on both sides, because it hashes configuration VALUES and the generator is
    # code. The check above would have passed and this tool would have scored the new corpus
    # against the old artifact's verdicts: a wrong number with a guard's blessing on it.
    stamped = manifest.get("pipeline_sha")
    current = pipeline_fingerprint()
    if stamped is None:
        print(
            f"  WARNING: this artifact predates `pipeline_sha` (current {current}). Its config "
            f"hash matches, but nothing here can tell whether the corpus GENERATOR moved since "
            f"it was written. Treat the numbers below as unverified provenance."
        )
    elif stamped != current:
        raise SystemExit(
            f"pipeline fingerprint mismatch: code is {current!r}, artifact recorded {stamped!r}. "
            f"The corpus this would rebuild is not the corpus the artifact's investigations saw, "
            f"even though the config hash matches — see `corpus.pipeline_fingerprint`. Re-run "
            f"tools/verdict_accuracy.py against the current code rather than scoring this."
        )
    # `_queue` also used the offline extractor when the artifact's OWN investigations ran on
    # `--provider bedrock` -- `cli._pipeline` always builds signals with the offline extractor
    # regardless of which model answers the investigation (`cli._offline_extractor`). Calling
    # it here spends nothing and calls no model, whichever provider is named in the manifest.
    return _queue(run)


def _score(trajectory: str | None, routed_team: str) -> str:
    """`correct` / `wrong` / `declined` for a trajectory-bearing customer; `unscored` for a
    decoy-accumulator or null customer, who has no team a route could be right about."""
    if routed_team not in OWNING_TEAMS:
        raise ValueError(f"unknown owning_team {routed_team!r}; schemas.py permits {OWNING_TEAMS}")
    if trajectory is None:
        return "unscored"
    if routed_team == "none":
        return "declined"
    return "correct" if routed_team == TRAJECTORY_TEAM[trajectory] else "wrong"


def _error_kind(routed_team: str, dominant_team: str) -> str:
    """Only called on `wrong` rows, where `routed_team != TRAJECTORY_TEAM[trajectory]` by
    construction. Splits the miss by whether the route at least agrees with the ledger's own
    dominant signal at the crossing -- an evidence-consistent miss on the wrong customer -- or
    agrees with neither, which is a route the evidence on hand does not explain at all."""
    return "matched_dominant_signal" if routed_team == dominant_team else "matched_neither"


def score_cases(cases: list[dict[str, Any]], corpus, cut) -> dict[str, Any]:
    """Score every case in the artifact against the rebuilt corpus and ledger cut.

    `cut` is `(customer_id, breakdown)` pairs from `cli._queue` — the same customers
    `verdict_accuracy.sample()` drew from, so every case's `customer_id` must appear in it.
    Its absence would mean the rebuilt queue disagrees with the one the artifact's cases were
    actually drawn from despite the hash check passing (e.g. `INVESTIGATION_BUDGET` moved), so
    it aborts rather than silently skipping the case.
    """
    truth_by_id = {c.customer_id: c for c in corpus.customers}
    cut_by_id = dict(cut)

    rows: list[dict[str, Any]] = []
    for case in cases:
        customer_id = case["customer_id"]
        if customer_id not in truth_by_id or customer_id not in cut_by_id:
            raise SystemExit(
                f"{customer_id} is in the artifact but not in the rebuilt queue — the config "
                f"hash matched but the queue still disagrees (check INVESTIGATION_BUDGET in "
                f"cli.py). Refusing to score against a population the artifact did not draw from."
            )
        truth = truth_by_id[customer_id]
        trajectory = truth.trajectory.value if truth.trajectory is not None else None
        dominant_signal = cut_by_id[customer_id].signal_type.value
        dominant_team = TRAJECTORY_TEAM[dominant_signal]
        routed_team = case["owning_team"]

        bucket = _score(trajectory, routed_team)
        correct_team = TRAJECTORY_TEAM[trajectory] if trajectory is not None else None
        error_kind = _error_kind(routed_team, dominant_team) if bucket == "wrong" else None

        rows.append(
            {
                "customer_id": customer_id,
                "trajectory": trajectory,
                "correct_team": correct_team,
                "dominant_signal": dominant_signal,
                "dominant_team": dominant_team,
                "routed_team": routed_team,
                "confidence": case["confidence"],
                "bucket": bucket,
                "error_kind": error_kind,
            }
        )
    return {"rows": rows}


def _confusion_matrix(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Truth team x routed team, trajectory-present rows only. Every truth team gets every
    routed-team column, including zero counts, so a reviewer sees what did NOT happen too."""
    matrix = {team: dict.fromkeys((*CANONICAL_TEAMS, "none"), 0) for team in CANONICAL_TEAMS}
    for row in rows:
        if row["correct_team"] is None:
            continue
        matrix[row["correct_team"]][row["routed_team"]] += 1
    return matrix


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate scored rows into the two separate reports plus the confusion matrix.

    Pulled out of `main()` so the aggregation — in particular, that an `unscored` (trajectory
    -None) row never reaches `with_trajectory` and so never enters `n`, `correct` or `wrong` —
    is a property tests call directly, not something only observable in printed output.
    """
    with_trajectory = [r for r in rows if r["trajectory"] is not None]
    without_trajectory = [r for r in rows if r["trajectory"] is None]

    correct = sum(1 for r in with_trajectory if r["bucket"] == "correct")
    wrong = [r for r in with_trajectory if r["bucket"] == "wrong"]
    declined = sum(1 for r in with_trajectory if r["bucket"] == "declined")

    matched_dominant = sum(1 for r in wrong if r["error_kind"] == "matched_dominant_signal")
    matched_neither = len(wrong) - matched_dominant

    routed_anyway = sum(1 for r in without_trajectory if r["routed_team"] != "none")

    return {
        "with_trajectory": {
            "n": len(with_trajectory),
            "correct": correct,
            "wrong": len(wrong),
            "declined": declined,
        },
        "wrong_error_kind": {
            "matched_dominant_signal": matched_dominant,
            "matched_neither": matched_neither,
            "total_wrong": len(wrong),
        },
        "confusion_matrix": _confusion_matrix(with_trajectory),
        "without_trajectory": {
            "n": len(without_trajectory),
            "routed_anyway": routed_anyway,
            "declined": len(without_trajectory) - routed_anyway,
        },
    }


def _slug(name: str) -> str:
    """Filename-safe provider name: letters, digits and dashes, everything else collapsed."""
    return re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", name)).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--artifact", type=Path, default=None,
                         help="a specific verdict-accuracy-*.json; default is the newest one")
    parser.add_argument("--provider", default=None, choices=["bedrock", "openrouter", "offline"],
                         help="restrict artifact discovery to one provider's runs")
    args = parser.parse_args()

    artifact_path = args.artifact or _latest_verdict_artifact(args.provider)
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    manifest = data["manifest"]

    corpus, _, cut, _ = rebuild_queue(manifest)
    scored = score_cases(data["cases"], corpus, cut)
    rows = scored["rows"]
    summary = summarize(rows)

    traj, wrong_kind, matrix, no_traj = (
        summary["with_trajectory"], summary["wrong_error_kind"],
        summary["confusion_matrix"], summary["without_trajectory"],
    )

    print(f"\n{'=' * 78}\nAT-58 — investigator routing accuracy\n{'=' * 78}")
    print(f"source={artifact_path.name}   provider={manifest['provider']}   "
          f"seed={manifest['seed']}   config={manifest['config_hash']}   git={_git_sha()}")
    print(f"{len(rows)} routed cases scored: {traj['n']} with a seeded trajectory (a correct "
          f"team exists), {no_traj['n']} without (no correct team exists — decoy-accumulator "
          f"or null).\n")
    if manifest["provider"] == "offline-rules":
        print("NOTE: the offline provider is a rule engine, not a model. Its routing is a "
              "floor, not a result.\n")

    for r in rows:
        print(f"  {r['customer_id']:<12} trajectory={str(r['trajectory']):<21} "
              f"routed={r['routed_team']:<12} {r['bucket']:<10} conf {r['confidence']:.2f}"
              + (f"  ({r['error_kind']})" if r["error_kind"] else ""))

    print(f"\n{'-' * 78}")
    print("ROUTING ACCURACY — trajectory-present customers only (a correct team exists)")
    print(f"  routed to the seeded trajectory's team     {traj['correct']:>3} / {traj['n']}")
    print(f"  routed to the wrong team                   {traj['wrong']:>3} / {traj['n']}")
    print(f"  declined to route (owning_team=none)       {traj['declined']:>3} / {traj['n']}")
    if traj["n"] == 0:
        print("  NOT AN ACCURACY FIGURE: no trajectory-present customer was sampled.")

    # Printed only when there is something to split. `0 / 1` reads as a rate whose denominator
    # was invented to dodge a divide-by-zero, which is the one shape this repo refuses.
    n_wrong = wrong_kind["total_wrong"]
    if n_wrong:
        print(f"\n  of the {n_wrong} wrong routes: {wrong_kind['matched_dominant_signal']} / "
              f"{n_wrong} matched the ledger's own dominant signal at the crossing "
              f"(evidence-consistent, wrong customer); {wrong_kind['matched_neither']} / "
              f"{n_wrong} matched neither the dominant signal nor the seeded trajectory "
              f"(unmoored from the evidence on hand).")
    else:
        print("\n  (no wrong routes to classify)")

    print(f"\n{'-' * 78}")
    print("CONFUSION — seeded trajectory's team (row) x routed team (column)")
    header = "  truth\\routed".ljust(16) + "".join(t.ljust(14) for t in (*CANONICAL_TEAMS, "none"))
    print(header)
    for truth_team in CANONICAL_TEAMS:
        counts = matrix[truth_team]
        print(f"  {truth_team:<14}" + "".join(str(counts[t]).ljust(14) for t in (*CANONICAL_TEAMS, "none")))

    print(f"\n{'-' * 78}")
    print("NO-TRAJECTORY CUSTOMERS — no correct team exists; reported separately, never folded "
          "into the accuracy figure above")
    print(f"  routed to a team anyway     {no_traj['routed_anyway']:>3} / {no_traj['n']}")
    print(f"  declined (owning_team=none) {no_traj['declined']:>3} / {no_traj['n']}")
    if no_traj["routed_anyway"]:
        conf = [r["confidence"] for r in rows if r["trajectory"] is None and r["routed_team"] != "none"]
        print(f"  confidence when routed anyway: {', '.join(f'{c:.2f}' for c in conf)}")
    if no_traj["n"] == 0:
        print("  (no trajectory-None customer was sampled in this artifact)")

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    # The provider *display* name carries the cache mode and the cost cap --
    # "bedrock+cache:record+cap:$5.00" -- and `:` and `$` are not legal in a Windows filename,
    # so the artifact write raised OSError after a $1.50 run had already printed its table. The
    # full name still goes in the manifest below; only the filename is slugged.
    out = ARTIFACTS / (
        f"routing-accuracy-{manifest['seed']}-{manifest['config_hash']}"
        f"-{_slug(manifest['provider'])}.json"
    )
    out.write_text(
        json.dumps(
            {
                "manifest": {
                    "source_artifact": artifact_path.name,
                    "source_provider": manifest["provider"],
                    "seed": manifest["seed"],
                    "config_hash": manifest["config_hash"],
                    "git_sha": _git_sha(),
                },
                **summary,
                "cases": rows,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"\n  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
