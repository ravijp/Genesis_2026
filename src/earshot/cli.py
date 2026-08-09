"""One command reproduces every number (BUILD-PLAN Rule 8).

    uv run python -m earshot.cli run          # full pipeline + scorecard + results/ artifacts
    uv run python -m earshot.cli demo         # the accumulation moment, narrated
    uv run python -m earshot.cli investigate  # the agent works the top threshold crossings

Every run writes a manifest (seed, git SHA, config hash, timestamp) next to its results. The
AI judge scores reproducibility directly and this is the cheapest way to earn it.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

from .agent import InvestigationDecision, InvestigationTrace, ToolContext, investigate
from .agent.prompts import investigator_prompts
from .arms import demo_ledger, mechanism_ablations, run_all_arms
from .config import DEFAULT, RunConfig
from .corpus import generate
from .evals import corpus_diagnostics, evaluate_all, evaluate_arm, extraction_fidelity
from .extract import OfflineLexiconExtractor, extract_all
from .llm import CachingProvider, OfflineProvider, ProviderError, cache_mode
from .memory import ScoreBreakdown
from .schema import Outcome, Stratum

# The review team's capacity, as a share of the portfolio. The investigator works the top of
# the queue, so this is what defines "crossed the threshold" — the same equal-alert-budget
# framing the eval uses, rather than a magic score.
INVESTIGATION_BUDGET = 0.10

# Ceiling on model spend for a single case. A live Sonnet 4.5 investigation measured $0.078,
# so this is ~3x headroom and still stops a runaway loop from being expensive.
COST_CAP_PER_CASE_USD = 0.25

# Anchored to the working directory, not to the package. A package-relative path resolves
# inside site-packages once `ear` is installed rather than run from a checkout.
ARTIFACTS = Path(os.environ.get("EARSHOT_ARTIFACTS", "artifacts")) / "runs"


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

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
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
    out = ARTIFACTS / f"run-{run.seed}-{run.hash()}.json"
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nthroughput {manifest['conversations_per_second']} conversations/sec")
    print(f"results -> {out}")
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
    # Both arms and both thresholds are needed BEFORE choosing who to show, because the whole
    # point is to find a customer the ledger catches and a per-call tool does not. Selecting on
    # "biggest climb" instead picked customers whose final conversation was loud enough to trip
    # a per-call scorer on its own — which is not the claim.
    arms = run_all_arms(signals, run.scoring)
    threshold = evaluate_arm(corpus, arms["full-ledger"], INVESTIGATION_BUDGET).threshold
    stateless_arm = arms["stateless-max"]
    stateless_cut = evaluate_arm(corpus, stateless_arm, INVESTIGATION_BUDGET).threshold

    def per_call_ever_fires(customer_id: str) -> bool:
        timeline = stateless_arm.timelines.get(customer_id)
        return bool(timeline) and any(s >= stateless_cut for _, s in timeline.points)

    # Every customer the ledger catches that a per-call tool misses. Counting them turns
    # "here is a nice example" into a population statistic a judge can check.
    accumulation_only: list[tuple[float, str, object, list]] = []
    for customer_id in ledger.customers():
        t = truth.get(customer_id)
        if t is None or t.stratum is not Stratum.DIFFUSE:
            continue
        for signal_type in {s.signal_type for s in ledger.signals(customer_id)}:
            points = ledger.timeline(customer_id, signal_type)
            if len(points) < 3 or points[-1].score < threshold:
                continue
            if per_call_ever_fires(customer_id):
                continue
            accumulation_only.append(
                (points[-1].score - points[0].score, customer_id, signal_type, points)
            )

    # Prefer an arc that actually ended in an outcome, then a longer arc, then a bigger climb.
    # A real outcome lets the demo close on lead time instead of trailing off.
    best = max(
        accumulation_only,
        default=None,
        key=lambda b: (truth[b[1]].outcome is not Outcome.NONE, len(b[3]), b[0]),
    )
    if best is None:
        # Say so rather than quietly showing a weaker case as though it were the strong one.
        for customer_id in ledger.customers():
            t = truth.get(customer_id)
            if t is None or t.stratum is not Stratum.DIFFUSE:
                continue
            for signal_type in {s.signal_type for s in ledger.signals(customer_id)}:
                points = ledger.timeline(customer_id, signal_type)
                if len(points) < 3:
                    continue
                climb = points[-1].score - points[0].score
                if best is None or climb > best[0]:
                    best = (climb, customer_id, signal_type, points)

    if best is None:
        print("No multi-conversation arc in this corpus. Increase n_customers and re-run.")
        return 1

    _, customer_id, signal_type, points = best
    t = truth[customer_id]
    print(f"\n{'=' * 78}")
    print(f"THE ACCUMULATION MOMENT — {customer_id}  ({signal_type.value})")
    print(f"{'=' * 78}")
    print(f"stratum={t.stratum.value}  outcome={t.outcome.value}  outcome_day={t.outcome_day}\n")

    # The threshold comes from the SAME equal-alert-budget operating point the eval uses, and
    # the comparison arm is actually run.
    #
    # This used to be `threshold = points[-1].score - 1e-9`, which derived the threshold from
    # the answer and so guaranteed the crossing on the last conversation for any customer
    # whatsoever, next to a hardcoded line asserting what a per-call tool "would have done".
    # That is the one beat the entry leans on for originality, and it was theatre. If the beat
    # fails on a given customer now, that is information we need before a judge finds it.
    stateless_points = dict(stateless_arm.timelines[customer_id].points)

    print(f"review budget {INVESTIGATION_BUDGET:.0%} of the portfolio  ->  "
          f"ledger threshold {threshold:.3f} · per-call threshold {stateless_cut:.3f}")
    print(f"{len(accumulation_only)} customer(s) in this corpus cross on accumulation alone "
          f"— caught by the ledger, missed by a per-call tool. Showing one.\n")

    for i, breakdown in enumerate(points, start=1):
        newest = max(breakdown.entries, key=lambda e: e.signal.day)
        day = breakdown.as_of_day
        verdict = "CASE OPENED" if breakdown.score >= threshold else "no action"
        alone = max((s for d, s in stateless_points.items() if d <= day), default=0.0)
        alone_verdict = "would flag" if alone >= stateless_cut else "silent"
        print(f"--- conversation {i}   day {day}   [{newest.signal.channel.value}] ---")
        print(f'    heard: "{newest.signal.evidence_quote.strip()}"')
        print(f"    extractor confidence {newest.signal.confidence:.2f} (cue {newest.signal.cue_id})")
        print(f"    LEDGER   {breakdown.score:.3f}  ->  {verdict}")
        print(f"    per-call {alone:.3f}  ->  {alone_verdict}")
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

    crossed = final.score >= threshold
    ever_alone = any(s >= stateless_cut for s in stateless_points.values())
    if crossed and not ever_alone:
        print("\nThe per-call arm scored every one of these conversations on its own and never")
        print("crossed its threshold. The ledger did. That is the whole claim, measured rather")
        print("than asserted.")
    elif crossed and ever_alone:
        print("\nHonest note: the per-call arm also crosses on this customer, so this one is not")
        print("a clean example of the accumulation-only case.")
    else:
        print("\nHonest note: the ledger does not cross the review-budget threshold for this")
        print("customer, so no case would open. Shown because it is the clearest accumulation")
        print("arc in the corpus, not because it wins.")

    if t.outcome is not Outcome.NONE and t.outcome_day is not None:
        opened = final.as_of_day
        print(f"\nOutcome ({t.outcome.value}) landed on day {t.outcome_day} — "
              f"{t.outcome_day - opened} days after the ledger crossed.")
    return 0


def _queue(run: RunConfig, budget: float = INVESTIGATION_BUDGET):
    """Rank customers by their ledger score and cut at the review team's capacity.

    Returns `(corpus, ledger, ranked, threshold)`. `ranked` is `(customer_id, breakdown)` in
    descending score order, restricted to customers at or above the cut.
    """
    corpus, _, signals = _pipeline(run)
    ledger = demo_ledger(signals, run.scoring)

    scored: list[tuple[str, ScoreBreakdown]] = []
    for customer in corpus.customers:
        conversations = corpus.conversations_for(customer.customer_id)
        if not conversations:
            continue
        as_of = max(c.day for c in conversations)
        breakdown = ledger.best(customer.customer_id, as_of)
        if breakdown.score > 0:
            scored.append((customer.customer_id, breakdown))

    scored.sort(key=lambda pair: (-pair[1].score, pair[0]))
    k = max(1, round(budget * len(corpus.customers)))
    cut = scored[:k]
    threshold = min((b.score for _, b in cut), default=0.0)
    return corpus, ledger, cut, threshold


def _context(corpus, customer_id: str, breakdown: ScoreBreakdown, threshold: float, seed: int):
    """Assemble the agent's view of one customer.

    The one line that matters for honesty: `latent_risk` is passed as a float and the truth
    object stays here. Nothing downstream can reach `outcome` — see tests/test_separation.py.
    """
    truth = next(c for c in corpus.customers if c.customer_id == customer_id)
    conversations = tuple(corpus.conversations_for(customer_id))
    return ToolContext(
        customer_id=customer_id,
        as_of_day=breakdown.as_of_day,
        seed=seed,
        # financial_state, NOT latent_risk. latent_risk is a function of how much evidence was
        # planted in this customer's conversations, so handing it to a tool let the agent
        # recover the stratum -- the answer key -- without reading anything.
        latent_risk=truth.financial_state,
        signal_type=breakdown.signal_type.value,
        score=breakdown.score,
        threshold=threshold,
        conversations=conversations,
        breakdown=breakdown,
    )


def _provider(name: str, prompt_sha: str):
    """Offline by default and always keyless.

    Only the network provider is wrapped in the response cache. The offline provider is already
    deterministic, and wrapping it would let `EARSHOT_CACHE_MODE=replay` turn a cache miss into a
    failure on the one path that must never need anything.
    """
    if name != "openrouter":
        return OfflineProvider()

    from .llm import OpenRouterProvider

    inner = OpenRouterProvider()
    return inner if cache_mode() == "off" else CachingProvider(inner, prompt_sha)


def _print_case(
    n: int, decision: InvestigationDecision, trace: InvestigationTrace, ctx: ToolContext
) -> None:
    quote_by_ref = {
        (c.conversation_id, t.index): (c.day, c.channel.value, t.text)
        for c in ctx.conversations
        for t in c.turns
    }

    print(f"\n{'=' * 78}")
    print(f"CASE {n} - {decision.customer_id}   [{ctx.signal_type}]   "
          f"score {ctx.score:.3f} / threshold {ctx.threshold:.3f}")
    print("=" * 78)
    print(f"  VERDICT           {decision.verdict.upper()}   "
          f"(confidence {decision.confidence:.2f})")
    print(f"  OWNING TEAM       {decision.owning_team}")
    print(f"  RECOMMENDED       {decision.recommended_action}")
    print(f"\n  WHY\n    {decision.rationale}")
    print(f"\n  WHAT WOULD CHANGE MY MIND\n    {decision.what_would_change_my_mind}")

    print("\n  EVIDENCE CITED")
    for ref in decision.evidence:
        found = quote_by_ref.get((ref.conversation_id, ref.turn_index))
        where = f"day {found[0]}, {found[1]}" if found else "UNRESOLVED"
        print(f'    [{ref.conversation_id} turn {ref.turn_index} - {where}]')
        print(f'      "{ref.quote.strip()}"')

    print(f"\n  TRACE  provider={trace.provider}  model={trace.model}  "
          f"prompt={trace.prompt_version}@{trace.prompt_sha[:8]}")
    print(f"         {trace.model_calls} model calls, {trace.tool_calls} tool calls, "
          f"{trace.schema_retries} schema retries, stopped: {trace.stopped_because}")
    print(f"         {trace.prompt_tokens} in + {trace.completion_tokens} out tokens, "
          f"${trace.cost_usd:.4f}, {trace.latency_ms:.0f} ms")
    for step in trace.steps:
        print(f"           {step.index}. {step.kind:<5} {step.name:<28} {step.detail}")


def cmd_investigate(run: RunConfig, provider_name: str, limit: int) -> int:
    # A model writes the rationale, so the output contains whatever punctuation it chose. On a
    # Windows console redirected to a file that means cp1252, and one curly apostrophe would
    # take the demo down with a UnicodeEncodeError. Degrade the character, not the run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    started = time.time()
    corpus, _, cut, threshold = _queue(run)
    system, _, prompt_sha = investigator_prompts()
    provider = _provider(provider_name, prompt_sha)

    print(f"\n{'=' * 78}\nEAR ON EVERY CALL - investigator\n{'=' * 78}")
    print(f"provider={getattr(provider, 'name', provider_name)}   seed={run.seed}   "
          f"config={run.hash()}   git={_git_sha()}")
    print(f"prompt=investigator/{system.version} sha={prompt_sha[:12]}   "
          f"cache_mode={cache_mode()}")
    print(f"{len(cut)} of {len(corpus.customers)} customers crossed at a "
          f"{INVESTIGATION_BUDGET:.0%} review budget (threshold {threshold:.3f}); "
          f"investigating the top {min(limit, len(cut))}.")
    if provider_name == "offline":
        print("NOTE: the offline provider is a rule engine, not a model. Its verdicts are a "
              "floor, not a result.")

    records: list[dict] = []
    for i, (customer_id, breakdown) in enumerate(cut[:limit], start=1):
        ctx = _context(corpus, customer_id, breakdown, threshold, run.seed)
        try:
            # A cost cap the shipped path never passes is not a cap. "Bounded spend per case"
            # is a production-readiness claim, so it has to hold in the command people run,
            # not only in the function signature.
            decision, trace = investigate(ctx, provider, cost_cap_usd=COST_CAP_PER_CASE_USD)
        except ProviderError as exc:
            # Only reachable if the provider fails before the loop can record a step.
            print(f"\nCASE {i} - {customer_id}: provider unavailable ({exc})")
            return 1
        _print_case(i, decision, trace, ctx)
        records.append({"decision": decision.model_dump(), "trace": trace.to_dict()})

    elapsed = time.time() - started
    total_cost = sum(r["trace"]["cost_usd"] for r in records)
    unresolved = sum(
        1
        for r in records
        for ref in r["decision"]["evidence"]
        if not any(
            c.conversation_id == ref["conversation_id"]
            for c in corpus.conversations_for(r["decision"]["customer_id"])
        )
    )
    print(f"\n{'-' * 78}")
    print(f"{len(records)} investigations in {elapsed:.1f}s   "
          f"total ${total_cost:.4f}   unresolved evidence refs: {unresolved}")

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    out = ARTIFACTS / f"investigate-{run.seed}-{run.hash()}.json"
    out.write_text(
        json.dumps(
            {
                "manifest": {
                    "seed": run.seed,
                    "config_hash": run.hash(),
                    "git_sha": _git_sha(),
                    "provider": getattr(provider, "name", provider_name),
                    "prompt_version": system.version,
                    "prompt_sha": prompt_sha,
                    "cache_mode": cache_mode(),
                    "budget": INVESTIGATION_BUDGET,
                    "threshold": round(threshold, 4),
                    "elapsed_seconds": round(elapsed, 2),
                    "total_cost_usd": round(total_cost, 6),
                },
                "cases": records,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"case files -> {out}")
    return 0


def main() -> int:
    # Windows pipes stdout as cp1252, so redirecting output to a file crashed on the "Δ" in
    # the ablation table and on the £ and curly quotes in model-authored rationales. Capturing
    # a run to a file is exactly what someone does when recording evidence, and a demo must
    # never die on an encoding error.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # type: ignore[union-attr]

    parser = argparse.ArgumentParser(prog="earshot", description="Ear on Every Call")
    parser.add_argument("command", choices=["run", "demo", "investigate"])
    parser.add_argument("--seed", type=int, default=DEFAULT.seed)
    parser.add_argument("--customers", type=int, default=None)
    parser.add_argument(
        "--provider",
        choices=["offline", "openrouter"],
        default="offline",
        help="investigate only. Offline needs no key and no network.",
    )
    parser.add_argument(
        "--limit", type=int, default=3, help="investigate only: how many cases to work."
    )
    args = parser.parse_args()

    run = DEFAULT
    if args.seed != DEFAULT.seed or args.customers:
        corpus_cfg = run.corpus
        if args.customers:
            corpus_cfg = replace(corpus_cfg, n_customers=args.customers)
        run = replace(run, seed=args.seed, corpus=corpus_cfg)

    if args.command == "run":
        return cmd_run(run)
    if args.command == "demo":
        return cmd_demo(run)
    return cmd_investigate(run, args.provider, args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
