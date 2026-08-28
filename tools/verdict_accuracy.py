"""AT-57 — does the investigator tell a real crossing from a false alarm?

    uv run --extra aws python tools/verdict_accuracy.py --provider bedrock --per-arm 4
    EARSHOT_CACHE_MODE=replay uv run python tools/verdict_accuracy.py   # keyless, from the cache

**Why `earshot investigate` cannot answer this.** It works the TOP of the queue, and the top of the
queue is nearly all true positives. The first keyed run returned `genuine` 8 times out of 8, which
looks like perfect accuracy and is a statement about the sample: with no negative in it, the run
could not have been wrong in the one direction that matters. An accuracy figure needs both arms.

**So this samples deliberately.** Customers who crossed the review threshold, split by whether they
went on to have a real outcome, and drawn evenly from each side. The split reads `CustomerTruth
.outcome` — the answer key — which is what the **evaluation** side is allowed to do and nothing
else is (D-009). The agent still sees only `cli._context`, the same audited assembly the product
path uses; nothing about the sampling reaches the model.

**What "correct" means here, exactly, and what it does not.** A crossing is scored against the
customer's eventual outcome:

  * outcome present, verdict `genuine`                          -> caught
  * outcome absent, verdict `false_alarm`                       -> correctly dismissed
  * anything else, including `insufficient_evidence`            -> wrong

The verdict vocabulary is `genuine` / `false_alarm` / `insufficient_evidence`
(`agent/schemas.py:22`). Written out here because the first draft of this file scored against
`false_positive`, a value the schema does not contain — every correct dismissal would have been
counted as an error, understating the agent and doing it silently.

`insufficient_evidence` counts as wrong on both arms deliberately. It is an honest answer and a
useless one for a reviewer, and folding it into "not a false positive" would let a model that never
commits score well. It is reported separately so the abstention rate is visible rather than buried.

**This is not the recall table and must never be quoted beside it.** Recall asks whether the LEDGER
surfaced the right customers, over many seeds. This asks whether the AGENT judged the crossings the
ledger surfaced, on one dataset, at whatever N was affordable. Different question, different
denominator, one dataset.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from typing import Any

from earshot.agent import investigate
from earshot.agent.prompts import investigator_prompts
from earshot.cli import ARTIFACTS, COST_CAP_PER_CASE_USD, _context, _git_sha, _queue
from earshot.config import DEFAULT, RunConfig
from earshot.corpus import pipeline_fingerprint
from earshot.evals import _outcome_customers
from earshot.llm import build_provider, cache_mode
from earshot.llm.base import ProviderError


def _percentile(values: list[float], q: float) -> float:
    """Nearest-rank, no interpolation: at these sample sizes an interpolated p95 reports a latency
    no case actually had."""
    if not values:
        return 0.0
    ordered = sorted(values)
    return round(ordered[max(1, math.ceil(q * len(ordered))) - 1], 1)


def sample(run: RunConfig, per_arm: int) -> tuple[list[tuple[str, Any, bool]], dict[str, int]]:
    """Crossing customers, balanced across outcome/no-outcome. Returns the sample and the
    population it was drawn from, because a rate without its denominator is not a result."""
    corpus, ledger, cut, threshold = _queue(run)
    # `evals._outcome_customers` rather than a predicate written here: "has an outcome" is
    # `outcome is not Outcome.NONE`, and the obvious `is not None` is always true because every
    # customer carries an `Outcome`. Writing it out a second time is how the recall table and this
    # table would end up disagreeing about who counts.
    outcomes = _outcome_customers(corpus)

    positives, negatives = [], []
    for customer_id, breakdown in cut:
        # The answer key. Read here, on the evaluation side, and never passed to the agent.
        has_outcome = customer_id in outcomes
        (positives if has_outcome else negatives).append((customer_id, breakdown, has_outcome))

    population = {
        "crossed": len(cut),
        "crossed_with_outcome": len(positives),
        "crossed_without_outcome": len(negatives),
        "customers": len(corpus.customers),
    }
    # Highest-scoring first within each arm, so the sample is deterministic and reproduces from
    # the seed alone. Ranking within an arm cannot bias the comparison between arms.
    drawn = positives[:per_arm] + negatives[:per_arm]
    return drawn, population | {"threshold": round(threshold, 4)}


# The verdicts the schema actually permits. Asserted against, not assumed: scoring for a value
# the model can never emit fails silently and in the flattering direction.
GENUINE = "genuine"
FALSE_ALARM = "false_alarm"
ABSTAIN = "insufficient_evidence"
VERDICTS = (GENUINE, FALSE_ALARM, ABSTAIN)


def score_verdict(verdict: str, has_outcome: bool) -> str:
    """Result buckets are named after what the AGENT did, never after a verdict string, so a
    result never reads like a verdict in the same column."""
    if verdict not in VERDICTS:
        raise ValueError(f"unknown verdict {verdict!r}; schemas.py permits {VERDICTS}")
    if has_outcome:
        return "caught" if verdict == GENUINE else "missed"
    return "dismissed" if verdict == FALSE_ALARM else "escalated_anyway"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--provider", default="bedrock", choices=["bedrock", "openrouter", "offline"])
    parser.add_argument("--per-arm", type=int, default=4, help="cases drawn from EACH arm")
    parser.add_argument("--customers", type=int, default=400)
    parser.add_argument("--seed", type=int, default=DEFAULT.seed)
    args = parser.parse_args()

    from dataclasses import replace

    run = replace(
        DEFAULT, seed=args.seed, corpus=replace(DEFAULT.corpus, n_customers=args.customers)
    )
    system, _, prompt_sha = investigator_prompts()
    provider = build_provider(args.provider, prompt_sha)

    drawn, population = sample(run, args.per_arm)
    positives = sum(1 for *_, has in drawn if has)

    print(f"\n{'=' * 78}\nAT-57 — investigator verdict accuracy\n{'=' * 78}")
    print(f"provider={getattr(provider, 'name', args.provider)}   seed={run.seed}   "
          f"config={run.hash()}   git={_git_sha()}   cache={cache_mode()}")
    print(f"{population['crossed']} of {population['customers']} customers crossed at threshold "
          f"{population['threshold']}: {population['crossed_with_outcome']} with an outcome, "
          f"{population['crossed_without_outcome']} without.")
    print(f"sampling {positives} with an outcome and {len(drawn) - positives} without.\n")
    if args.provider == "offline":
        print("NOTE: the offline provider is a rule engine, not a model. Its verdicts are a "
              "floor, not a result.\n")

    started = time.time()
    rows: list[dict[str, Any]] = []
    # The corpus is rebuilt once, not once per case: `_queue` regenerates it, and calling it inside
    # the loop would be eight corpus generations for eight investigations.
    corpus, _, _, threshold = _queue(run)
    for i, (customer_id, breakdown, has_outcome) in enumerate(drawn, start=1):
        ctx = _context(corpus, customer_id, breakdown, threshold, run.seed)
        try:
            decision, trace = investigate(ctx, provider, cost_cap_usd=COST_CAP_PER_CASE_USD)
        except ProviderError as exc:
            print(f"case {i} {customer_id}: provider unavailable ({exc})")
            return 1
        outcome = score_verdict(decision.verdict, has_outcome)
        rows.append(
            {
                "customer_id": customer_id,
                "has_outcome": has_outcome,
                "verdict": decision.verdict,
                "confidence": decision.confidence,
                "owning_team": decision.owning_team,
                "result": outcome,
                "cost_usd": trace.cost_usd,
                "latency_ms": trace.latency_ms,
                "model_calls": trace.model_calls,
                "stopped_because": trace.stopped_because,
                "evidence_repairs": trace.evidence_repairs,
            }
        )
        print(f"  {i:>2}. {customer_id:<12} outcome={'yes' if has_outcome else 'no ':<3}  "
              f"verdict={decision.verdict:<21} {outcome:<17} "
              f"conf {decision.confidence:.2f}  ${trace.cost_usd:.4f}")

    elapsed = time.time() - started
    counts = {k: sum(1 for r in rows if r["result"] == k) for k in
              ("caught", "missed", "dismissed", "escalated_anyway")}
    n_pos = counts["caught"] + counts["missed"]
    n_neg = counts["dismissed"] + counts["escalated_anyway"]
    abstained = sum(1 for r in rows if r["verdict"] == ABSTAIN)
    correct = counts["caught"] + counts["dismissed"]

    print(f"\n{'-' * 78}")
    print("CONFUSION — the agent's verdict against the customer's eventual outcome")
    print(f"  outcome present, called genuine        {counts['caught']:>3} / {n_pos}")
    print(f"  outcome present, called anything else  {counts['missed']:>3} / {n_pos}")
    print(f"  outcome absent, called false_alarm     {counts['dismissed']:>3} / {n_neg}")
    print(f"  outcome absent, called anything else   {counts['escalated_anyway']:>3} / {n_neg}")
    print(f"\n  overall {correct}/{len(rows)}   abstained (insufficient_evidence) {abstained}/{len(rows)}")
    if n_neg == 0 or n_pos == 0:
        print("  NOT AN ACCURACY FIGURE: one arm is empty, so nothing here could have been wrong "
              "in that direction.")

    costs = [r["cost_usd"] for r in rows]
    lats = [r["latency_ms"] for r in rows]
    print(f"\n  cost ${sum(costs):.4f} total, ${statistics.mean(costs):.4f} per case")
    print(f"  model time p50 {_percentile(lats, 0.5):.0f} ms   p95 {_percentile(lats, 0.95):.0f} ms"
          f"   wall clock {elapsed:.0f}s")
    print(f"  stopped: {dict((k, sum(1 for r in rows if r['stopped_because'] == k)) for k in {r['stopped_because'] for r in rows})}")
    print(f"  evidence repairs {sum(r['evidence_repairs'] for r in rows)}/{len(rows)}")

    # A replay that missed every key used to overwrite the keyed run it was replaying: same
    # seed, same config hash, same provider, so the same filename. On 2026-08-28 a $1.50
    # measured artifact was replaced by a file whose 42 cases all read `provider_error`.
    # Two independent stops, because either alone still loses the run:
    if all(r["stopped_because"] == "provider_error" for r in rows):
        print("\n  NOT WRITING AN ARTIFACT: every case ended in provider_error, so this run "
              "measured nothing. In replay mode that means the cache does not cover this "
              "sample -- most likely the corpus moved under it (see pipeline_sha).")
        return 1

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    # The cache mode is part of the identity of the measurement, not a detail: a recorded run
    # and a replayed one are different evidence and must not share a path.
    out = (
        ARTIFACTS
        / f"verdict-accuracy-{run.seed}-{run.hash()}-{args.provider}-{cache_mode()}.json"
    )
    out.write_text(
        json.dumps(
            {
                "manifest": {
                    "seed": run.seed,
                    "config_hash": run.hash(),
                    # `config_hash` covers configuration values only. This covers the code that
                    # turns them into a queue, so a later reader can tell a stale artifact from
                    # a current one -- see `corpus.pipeline_fingerprint`.
                    "pipeline_sha": pipeline_fingerprint(),
                    "git_sha": _git_sha(),
                    "provider": getattr(provider, "name", args.provider),
                    "prompt_version": system.version,
                    "prompt_sha": prompt_sha,
                    "cache_mode": cache_mode(),
                    "per_arm": args.per_arm,
                    "population": population,
                    "elapsed_seconds": round(elapsed, 2),
                },
                "counts": counts,
                "abstained": abstained,
                "cost_usd_total": round(sum(costs), 6),
                "cost_usd_per_case": round(statistics.mean(costs), 6),
                "latency_p50_ms": _percentile(lats, 0.5),
                "latency_p95_ms": _percentile(lats, 0.95),
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
