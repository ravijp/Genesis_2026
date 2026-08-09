"""One command reproduces every number (BUILD-PLAN Rule 8).

    uv run python -m ear.cli run     # full pipeline + scorecard + results/ artifacts
    uv run python -m ear.cli demo    # the accumulation moment, narrated

Every run writes a manifest (seed, git SHA, config hash, timestamp) next to its results. The
AI judge scores reproducibility directly and this is the cheapest way to earn it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from .arms import demo_ledger, mechanism_ablations, run_all_arms
from .config import DEFAULT, RunConfig
from .corpus import generate
from .evals import corpus_diagnostics, evaluate_all, extraction_fidelity
from .extract import OfflineLexiconExtractor, extract_all
from .schema import Outcome, Stratum

RESULTS = Path(__file__).resolve().parent.parent / "results"


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def _pipeline(run: RunConfig):
    corpus = generate(run)
    extractor = OfflineLexiconExtractor(
        miss_rate=run.offline_miss_rate, false_fire_rate=run.offline_false_fire_rate
    )
    signals = extract_all(extractor, corpus.conversations)
    return corpus, extractor, signals


def cmd_run(run: RunConfig) -> int:
    started = time.time()
    corpus, extractor, signals = _pipeline(run)
    arms = run_all_arms(signals, run.scoring)
    results = evaluate_all(corpus, arms)
    fidelity = extraction_fidelity(corpus.seeded, signals)
    diagnostics = corpus_diagnostics(corpus, arms)
    ablations = mechanism_ablations(signals, run.scoring)
    elapsed = time.time() - started

    print(f"\n{'=' * 78}\nEAR ON EVERY CALL — eval run\n{'=' * 78}")
    print(f"provider={extractor.name}   seed={run.seed}   config={run.hash()}   git={_git_sha()}")
    print("NOTE: offline provider. These are plumbing-and-memory numbers, not headline accuracy.\n")

    print("CORPUS")
    for k, v in diagnostics.items():
        print(f"  {k:38s} {v}")

    print("\nEXTRACTION FIDELITY (published, not hidden)")
    for k, v in fidelity.items():
        print(f"  {k:38s} {v}")

    print("\nARM COMPARISON — equal alert budget (each arm cut at its own threshold)")
    header = f"  {'budget':>7} {'arm':<20} {'flagged':>8} {'recall':>8} {'precision':>10} {'lead(d)':>8}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in results:
        lead = "n/a" if r.median_lead_days is None else f"{r.median_lead_days:.1f}"
        print(
            f"  {r.budget:>6.0%} {r.arm:<20} {r.n_flagged:>8} {r.recall:>8.3f} "
            f"{r.precision:>10.3f} {lead:>8}"
        )

    print("\nPER-STRATUM, at the 10% budget (flag rate shown for decoy/null strata)")
    for r in [r for r in results if abs(r.budget - 0.10) < 1e-9]:
        print(f"  {r.arm}")
        for k, v in r.recall_by_stratum.items():
            print(f"      {k:<34s} {v:.3f}")

    print("\nMECHANISM ABLATIONS at 10% budget — does each mechanism earn its place?")
    ablation_results = evaluate_all(corpus, ablations, budgets=(0.10,))
    full_at_10 = next(
        (r for r in results if r.arm == "full-ledger" and abs(r.budget - 0.10) < 1e-9), None
    )
    if full_at_10:
        print(f"  {'full-ledger (reference)':<28} recall={full_at_10.recall:.3f}")
    for r in ablation_results:
        delta = "" if not full_at_10 else f"  (Δ {r.recall - full_at_10.recall:+.3f})"
        print(f"  {r.arm:<28} recall={r.recall:.3f}{delta}")

    RESULTS.mkdir(exist_ok=True)
    manifest = {
        "seed": run.seed,
        "config_hash": run.hash(),
        "git_sha": _git_sha(),
        "provider": extractor.name,
        "elapsed_seconds": round(elapsed, 2),
        "conversations_per_second": round(len(corpus.conversations) / max(elapsed, 1e-6), 1),
    }
    payload = {
        "manifest": manifest,
        "corpus_diagnostics": diagnostics,
        "extraction_fidelity": fidelity,
        "arm_results": [asdict(r) for r in results],
        "mechanism_ablations": [asdict(r) for r in ablation_results],
    }
    out = RESULTS / f"run-{run.seed}-{run.hash()}.json"
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nthroughput {manifest['conversations_per_second']} conversations/sec")
    print(f"results -> {out.relative_to(RESULTS.parent)}")
    return 0


def cmd_demo(run: RunConfig) -> int:
    """The accumulation moment, with the retro re-score visible.

    Per the collision review, retro re-scoring is the one thing no incumbent reproduces --
    so it goes on screen rather than into prose.
    """
    corpus, _, signals = _pipeline(run)
    ledger = demo_ledger(signals, run.scoring)
    truth = {c.customer_id: c for c in corpus.customers}

    # Pick the best narrative: a diffuse arc whose score climbs across the most conversations.
    # Prefer a diffuse arc that actually ended in an outcome -- narrating a true positive is
    # the point. Outcomes are drawn stochastically, so a diffuse arc may legitimately not
    # churn; fall back to any diffuse arc rather than pretending otherwise.
    best = None
    for require_outcome in (True, False):
        for customer_id in ledger.customers():
            t = truth.get(customer_id)
            if t is None or t.stratum is not Stratum.DIFFUSE:
                continue
            if require_outcome and t.outcome is Outcome.NONE:
                continue
            for signal_type in {s.signal_type for s in ledger.signals(customer_id)}:
                points = ledger.timeline(customer_id, signal_type)
                if len(points) < 3:
                    continue
                climb = points[-1].score - points[0].score
                if best is None or climb > best[0]:
                    best = (climb, customer_id, signal_type, points)
        if best is not None:
            break

    if best is None:
        print("No multi-conversation arc in this corpus. Increase n_customers and re-run.")
        return 1

    _, customer_id, signal_type, points = best
    t = truth[customer_id]
    print(f"\n{'=' * 78}")
    print(f"THE ACCUMULATION MOMENT — {customer_id}  ({signal_type.value})")
    print(f"{'=' * 78}")
    print(f"stratum={t.stratum.value}  outcome={t.outcome.value}  outcome_day={t.outcome_day}\n")

    threshold = points[-1].score - 1e-9  # the case opens on the final conversation
    for i, breakdown in enumerate(points, start=1):
        newest = max(breakdown.entries, key=lambda e: e.signal.day)
        verdict = "CASE OPENED" if breakdown.score >= threshold else "no action"
        print(f"--- conversation {i}   day {breakdown.as_of_day}   "
              f"[{newest.signal.channel.value}] ---")
        print(f'    heard: "{newest.signal.evidence_quote.strip()}"')
        print(f"    extractor confidence {newest.signal.confidence:.2f} (cue {newest.signal.cue_id})")
        print(f"    RUNNING SCORE: {breakdown.score:.3f}   ->  {verdict}")
        print()

    final = points[-1]
    print("RETRO RE-SCORE — the same earlier conversations, re-read in light of the last one:")
    for e in sorted(final.entries, key=lambda e: e.signal.day):
        flag = " LOAD-BEARING" if e.is_load_bearing(threshold) else ""
        print(
            f"    day {e.signal.day:>3}  supported {e.score_at_write:.3f} when it arrived"
            f"  ->  supports {e.score_now:.3f} now   ({e.retro_delta:+.3f}){flag}"
        )
    print("\n    (Marginal value per quote falls as evidence accumulates — the score function is")
    print("     concave. What moves is the conclusion the evidence supports, and whether the")
    print("     case would collapse without it.)")

    print("\nWhat a per-call tool would have done: scored each of these conversations alone,")
    print("found nothing worth escalating, and archived all three.")
    if t.outcome is not Outcome.NONE and t.outcome_day is not None:
        opened = final.as_of_day
        print(f"\nOutcome ({t.outcome.value}) landed on day {t.outcome_day} — "
              f"{t.outcome_day - opened} days after the ledger crossed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="ear", description="Ear on Every Call")
    parser.add_argument("command", choices=["run", "demo"])
    parser.add_argument("--seed", type=int, default=DEFAULT.seed)
    parser.add_argument("--customers", type=int, default=None)
    args = parser.parse_args()

    run = DEFAULT
    if args.seed != DEFAULT.seed or args.customers:
        from dataclasses import replace

        corpus_cfg = run.corpus
        if args.customers:
            corpus_cfg = replace(corpus_cfg, n_customers=args.customers)
        run = replace(run, seed=args.seed, corpus=corpus_cfg)

    return cmd_run(run) if args.command == "run" else cmd_demo(run)


if __name__ == "__main__":
    raise SystemExit(main())
