"""One command reproduces every number.

    uv run python -m earshot.cli run          # full pipeline + scorecard + results/ artifacts
    uv run python -m earshot.cli demo         # the accumulation moment, narrated
    uv run python -m earshot.cli investigate  # the agent works the top threshold crossings
    uv run python -m earshot.cli sweep        # many seeds; the only source of publishable numbers

Every run writes a manifest (seed, git SHA, config hash, timestamp) next to its results, so any
figure we publish traces back to the run that produced it.
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

# Ceiling on model spend for a single case. The two committed live Sonnet 4.5 investigations cost
# $0.089 and $0.097, so this is ~2.6x headroom and still stops a runaway loop from being expensive.
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
    n_outcomes = sum(1 for c in corpus.customers if c.outcome is not Outcome.NONE)
    print("NOTE: offline provider. These are plumbing-and-memory numbers, not headline accuracy.")
    print(f"NOTE: ONE dataset, {n_outcomes} outcome customers. Every recall below is an integer")
    print(f"      over {n_outcomes}, so arms one or two customers apart are indistinguishable.")
    print("      Nothing here should be published. Use `earshot sweep` for anything quotable.\n")

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
    """The accumulation moment, with the retro re-score visible on screen rather than asserted
    in prose."""
    corpus, _, signals = _pipeline(run)
    ledger = demo_ledger(signals, run.scoring)
    truth = {c.customer_id: c for c in corpus.customers}

    # Both arms and both thresholds are needed BEFORE choosing who to show, because the
    # customer we want is one the ledger catches and a per-call tool never does. Selecting on
    # "biggest climb" alone admits customers whose final conversation is loud enough to trip a
    # per-call scorer on its own, which is a different claim.
    #
    # Outcomes are drawn stochastically, so a diffuse arc may legitimately not churn; there is
    # a fallback below to any diffuse arc, labelled as such.
    arms = run_all_arms(signals, run.scoring)
    threshold = evaluate_arm(corpus, arms["full-ledger"], INVESTIGATION_BUDGET).threshold
    stateless_arm = arms["stateless-max"]
    stateless_result = evaluate_arm(corpus, stateless_arm, INVESTIGATION_BUDGET)
    stateless_cut = stateless_result.threshold

    def per_call_catches(customer_id: str) -> bool:
        """Membership in the baseline's actual alert queue -- the same set the published table
        scores. Comparing against `score >= cut` instead would credit the baseline with the
        whole tie cluster at the cut, making the demo's opponent stronger than the one in the
        results table and the two numbers incomparable."""
        return customer_id in stateless_result.flagged_ids

    # Customers the ledger catches that a per-call tool misses AND who went on to have a real
    # outcome. The outcome filter is what makes the count meaningful: without it, customers
    # who were never at risk are counted as caught, over a population that mostly had nothing
    # to catch.
    accumulation_only: list[tuple[float, str, object, list]] = []
    for customer_id in ledger.customers():
        t = truth.get(customer_id)
        if t is None or t.stratum is not Stratum.DIFFUSE or t.outcome is Outcome.NONE:
            continue
        for signal_type in {s.signal_type for s in ledger.signals(customer_id)}:
            points = ledger.timeline(customer_id, signal_type)
            if len(points) < 3 or points[-1].score < threshold:
                continue
            if per_call_catches(customer_id):
                continue
            accumulation_only.append(
                (points[-1].score - points[0].score, customer_id, signal_type, points)
            )

    # The honest denominator: thin-evidence customers who actually had an outcome to catch.
    catchable = [
        c for c in corpus.customers
        if c.stratum is Stratum.DIFFUSE and c.outcome is not Outcome.NONE
    ]

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

    # The threshold comes from the SAME equal-alert-budget operating point the evaluation uses,
    # so the demo and the published numbers agree. Deriving it from the customer's own final
    # score would guarantee a crossing on the last conversation for any customer whatsoever.
    # The comparison arm is run rather than narrated, so the beat is allowed to fail.
    stateless_points = dict(stateless_arm.timelines[customer_id].points)

    print(f"review budget {INVESTIGATION_BUDGET:.0%} of the portfolio  ->  "
          f"ledger threshold {threshold:.3f} · per-call threshold {stateless_cut:.3f}")
    clean = len(accumulation_only)
    print(f"{clean} of {len(catchable)} thin-evidence customers with a real outcome are caught by")
    print("the ledger while per-call detection NEVER fires for them, at any point.")
    if clean == 0:
        print("\n*** No such customer exists in this dataset. What follows is the clearest")
        print("*** accumulation arc available and is NOT an instance of the claim. Try a")
        print("*** larger --customers, and see the README for the population result.")
    print()

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

    # No triumphant closing line. The selection above filters to customers where the per-call
    # arm never fires, so announcing that the per-call arm never fired would be a tautology
    # dressed as a result. The population ratio is the honest form of the same claim, so it is
    # what closes.
    print(f"\nChosen from {len(accumulation_only)} of {len(catchable)} thin-evidence customers who")
    print("went on to have a real outcome, where the ledger opens a case and per-call detection")
    print("does not. That ratio is the claim, and this is one instance of it.")
    print("\nIt is a DIFFERENT quantity from the recall table: this counts customers the ledger")
    print("catches and the baseline misses, on one dataset, while the table compares each arm's")
    print("recall across ten. Both are in `earshot sweep`; neither is the other. Per-call")
    print("detection here means the same top-ranked alert queue the table scores, at the same")
    print("review budget — not a threshold comparison, which would credit the baseline with")
    print("every customer tied at the cut.")

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

    The truth object stays in this function. Only primitives cross into `ToolContext`, and
    nothing downstream can reach `outcome` — see tests/test_separation.py.
    """
    truth = next(c for c in corpus.customers if c.customer_id == customer_id)
    conversations = tuple(corpus.conversations_for(customer_id))
    return ToolContext(
        customer_id=customer_id,
        as_of_day=breakdown.as_of_day,
        seed=seed,
        # financial_state, and only ever financial_state. The corpus-side risk figure is a
        # function of how much evidence was planted in this customer's conversations, so a
        # tool given it recovers the stratum -- the answer key -- without reading anything.
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

    # In replay mode the network is never touched, so a key must not be required to get here.
    # Construction is deferred so the cache serves first and the live client is built only if
    # something actually misses; building it eagerly makes replay depend on a key it will
    # never use.
    if cache_mode() == "replay":
        return CachingProvider(_LazyOpenRouter(), prompt_sha)

    inner = OpenRouterProvider()
    return inner if cache_mode() == "off" else CachingProvider(inner, prompt_sha)


class _LazyOpenRouter:
    """Constructs the real client on first use, so replay never needs a key."""

    name = "openrouter"

    def __init__(self) -> None:
        self._inner = None

    def complete(self, *args, **kwargs):
        if self._inner is None:
            from .llm import OpenRouterProvider

            self._inner = OpenRouterProvider()
        return self._inner.complete(*args, **kwargs)


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
    # A model writes the rationale, so the output carries whatever punctuation it chose. A
    # Windows console redirected to a file encodes cp1252, where one curly apostrophe is a
    # UnicodeEncodeError. Degrade the character, not the run.
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
            # The cap is passed here, not just available on the signature: bounded spend per
            # case has to hold in the command people actually run.
            decision, trace = investigate(ctx, provider, cost_cap_usd=COST_CAP_PER_CASE_USD)
        except ProviderError as exc:
            # Only reachable if the provider fails before the loop can record a step.
            print(f"\nCASE {i} - {customer_id}: provider unavailable ({exc})")
            return 1
        _print_case(i, decision, trace, ctx)
        records.append({"decision": decision.model_dump(), "trace": trace.to_dict()})

    elapsed = time.time() - started
    total_cost = sum(r["trace"]["cost_usd"] for r in records)
    # The FIRST-attempt failure rate, not the post-retry one. A decision whose citations do not
    # resolve is rejected inside the loop and never reaches here, so counting unresolved refs on
    # the returned decisions would report zero however badly the model behaved.
    first_attempt_failures = sum(r["trace"]["evidence_repairs"] for r in records)
    print(f"\n{'-' * 78}")
    print(f"{len(records)} investigations in {elapsed:.1f}s   "
          f"total ${total_cost:.4f}   "
          f"cases needing an evidence repair: {first_attempt_failures}/{len(records)}")

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    # Provider, cache mode and limit are all in the filename, so two runs that differ only in
    # which provider served them do not overwrite each other.
    slug = f"{provider_name}-{cache_mode()}-{limit}"
    out = ARTIFACTS / f"investigate-{run.seed}-{run.hash()}-{slug}.json"
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


def cmd_sweep(run: RunConfig, n_seeds: int) -> int:
    """Many seeds, paired comparison, and the integers behind every rate.

    `run` reports one draw, and on a single 400-customer corpus every arm's recall is an
    integer over roughly 50 outcome customers, so arms one or two customers apart look
    different and are not. Nothing published comes from `run` alone.
    """
    from .sweep import paired_record, sign_test_p, sweep

    seeds = [run.seed + i for i in range(n_seeds)]
    started = time.time()
    summaries, by_arm = sweep(run, seeds, budget=INVESTIGATION_BUDGET)
    elapsed = time.time() - started

    print(f"\n{'=' * 86}\nEAR ON EVERY CALL — multi-seed evaluation\n{'=' * 86}")
    print(f"{n_seeds} seeds x {run.corpus.n_customers} customers   "
          f"review budget {INVESTIGATION_BUDGET:.0%}   git={_git_sha()}   ({elapsed:.0f}s)")
    print(f"seeds: {seeds[0]}..{seeds[-1]}\n")

    print(f"{'arm':<18} {'recall':>8} {'stdev':>7} {'hits/outcomes':>16} "
          f"{'diffuse':>9} {'diffuse hits/n':>15} {'conc':>7} {'conc hits/n':>15}")
    print("-" * 110)
    for name, s in sorted(summaries.items(), key=lambda kv: -kv[1].pooled_diffuse):
        print(f"{name:<18} {s.pooled_recall:>8.3f} {s.stdev:>7.3f} "
              f"{f'{s.total_hits}/{s.total_outcomes}':>16} "
              f"{s.pooled_diffuse:>9.3f} "
              f"{f'{s.total_diffuse_hits}/{s.total_diffuse_outcomes}':>15} "
              f"{s.pooled_concentrated:>7.3f} "
              f"{f'{s.total_concentrated_hits}/{s.total_concentrated_outcomes}':>15}")

    comparisons: list[dict[str, object]] = []

    def _matrix(title: str, metric: str, note: str) -> int:
        """Every pairing on one metric. Printing a subset is how a published p-value ends up
        with no command behind it, and how a multiplicity count ends up understated."""
        print(f"\n{title}")
        print(f"  {note}")
        names = sorted(summaries)
        count = 0
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                count += 1
                w, lost, tied = paired_record(by_arm, a, b, metric=metric)
                p = sign_test_p(w, lost)
                mark = "  <-- p<0.05" if p < 0.05 else ""
                print(f"  {a:<18} vs {b:<18} {w}-{lost}-{tied}  p={p:.3f}{mark}")
                comparisons.append(
                    {"metric": metric, "a": a, "b": b,
                     "wins": w, "losses": lost, "ties": tied, "p": round(p, 4)}
                )
        return count

    # The pre-registered headline is full-ledger vs stateless-max on DIFFUSE. It is printed
    # first and named, so that everything else reads as the exploratory space it is.
    w, lost, tied = paired_record(
        by_arm, "full-ledger", "stateless-max", metric="diffuse_recall"
    )
    print("\nPRE-REGISTERED HEADLINE — full-ledger vs stateless-max on diffuse arcs")
    print(f"  {w}-{lost}-{tied}  p={sign_test_p(w, lost):.3f}   "
          f"(declared before the run; everything below is exploratory)")

    n_diffuse = _matrix(
        "DIFFUSE ARCS — evidence spread thin, every pairing, paired by seed",
        "diffuse_recall",
        "the stratum the ledger is built for",
    )
    n_conc = _matrix(
        "CONCENTRATED ARCS — one loud conversation, every pairing, paired by seed",
        "concentrated_recall",
        "the stratum a per-call maximum is built for, where the ledger LOSES",
    )
    n_overall = _matrix(
        "OVERALL RECALL — every pairing, paired by seed",
        "recall",
        "whole portfolio",
    )

    n_tests = n_diffuse + n_conc + n_overall
    print(f"\nNOTE: {n_tests} pairwise tests here, with no multiplicity correction. Only the")
    print("headline above was declared in advance; a single p just under 0.05 among the rest")
    print("is a hint, not a result. Every number published anywhere is in this output.")

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    out = ARTIFACTS / f"sweep-{n_seeds}x{run.corpus.n_customers}-{run.hash()}.json"
    out.write_text(
        json.dumps(
            {
                "manifest": {
                    "seeds": seeds,
                    "n_customers": run.corpus.n_customers,
                    "budget": INVESTIGATION_BUDGET,
                    "config_hash": run.hash(),
                    "git_sha": _git_sha(),
                    "elapsed_seconds": round(elapsed, 2),
                },
                "arms": {
                    k: {
                        **asdict(v),
                        # Pooled rates are what the console and the README quote; `mean_*` is a
                        # mean of per-seed rates. Both are stored, named for which is which.
                        "pooled_recall": round(v.pooled_recall, 4),
                        "pooled_diffuse": round(v.pooled_diffuse, 4),
                        "pooled_concentrated": round(v.pooled_concentrated, 4),
                    }
                    for k, v in summaries.items()
                },
                "comparisons": comparisons,
                "samples": {k: [asdict(s) for s in v] for k, v in by_arm.items()},
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"\nresults -> {out}")
    return 0


def main() -> int:
    # Windows pipes stdout as cp1252, which cannot encode the "Δ" in the ablation table or the
    # £ and curly quotes in model-authored rationales. Capturing a run to a file is exactly
    # what someone does when recording evidence, so a run must not die on an encoding error.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # type: ignore[union-attr]

    parser = argparse.ArgumentParser(prog="earshot", description="Ear on Every Call")
    parser.add_argument("command", choices=["run", "demo", "investigate", "sweep"])
    parser.add_argument(
        "--seeds",
        type=int,
        default=10,
        help="sweep only: how many independent datasets to run. Nothing should be published "
        "from a single seed.",
    )
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
    if args.command == "sweep":
        return cmd_sweep(run, args.seeds)
    return cmd_investigate(run, args.provider, args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
