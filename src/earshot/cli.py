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
import statistics
import subprocess
import sys
import time
from dataclasses import asdict, replace
from pathlib import Path

from .agent import InvestigationDecision, InvestigationTrace, ToolContext, investigate
from .agent.prompts import investigator_prompts
from .arms import demo_ledger, mechanism_ablations, run_all_arms
from .aws.transcripts import to_payload
from .case_record import case_record
from .config import DEFAULT, RunConfig
from .corpus import generate, smallest_fragment_pool
from .evals import corpus_diagnostics, evaluate_all, evaluate_arm, extraction_fidelity
from .extract import Extractor, OfflineLexiconExtractor, extract_all
from .llm import ProviderError, build_provider, cache_mode
from .memory import ScoreBreakdown
from .schema import Case, Outcome, Stratum
from .read_live import narrate, narration_totals
from .stream import StreamError, narration_targets, run_stream, stream_payload
from .tenants import Tenant, resolve as resolve_tenants

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
    """The commit a run came from, suffixed `-dirty` if the tree had uncommitted changes.

    Without the suffix a manifest names a commit that cannot reproduce it, which is worse than
    naming nothing: a committed artifact stamped with a clean SHA is read as provenance.
    """
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"
    try:
        changed = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return sha
    return f"{sha}-dirty" if changed else sha


def _offline_extractor(run: RunConfig) -> OfflineLexiconExtractor:
    return OfflineLexiconExtractor(
        miss_rate=run.offline_miss_rate, false_fire_rate=run.offline_false_fire_rate
    )


def build_extractor(name: str, run: RunConfig) -> Extractor:
    """Offline by default, always. `model` is opt-in and is the only path that needs a key.

    D-004: everything runs with zero keys, so nothing here may reach for the network unless the
    caller asked for it by name.
    """
    if name != "model":
        return _offline_extractor(run)

    from .extract_model import model_extractor

    return model_extractor()


def _extraction_telemetry(extractor: Extractor) -> dict | None:
    telemetry = getattr(extractor, "telemetry", None)
    return telemetry.to_dict() if telemetry is not None else None


def _print_extraction_telemetry(extractor: Extractor) -> None:
    """What the reader cost and how often it had to be corrected. Printed only when a model read.

    Cost per 1,000 conversations is a named deliverable, so it comes from this counter rather
    than from a price list.
    """
    payload = _extraction_telemetry(extractor)
    if payload is None:
        return
    print("\nMODEL READER — cost and latency, measured on this run")
    for key, value in payload.items():
        print(f"  {key:38s} {value}")
    if cache_mode() == "replay":
        print("  NOTE: replay. Cost and latency are the RECORDED figures from the keyed run.")


def _pipeline(run: RunConfig, extractor: Extractor | None = None):
    corpus = generate(run)
    extractor = _offline_extractor(run) if extractor is None else extractor
    signals = extract_all(extractor, corpus.conversations)
    return corpus, extractor, signals


def cmd_run(run: RunConfig, extractor: Extractor | None = None) -> int:
    started = time.time()
    corpus, extractor, signals = _pipeline(run, extractor)
    arms = run_all_arms(signals, run.scoring)
    results = evaluate_all(corpus, arms)
    fidelity = extraction_fidelity(corpus.seeded, signals)
    diagnostics = corpus_diagnostics(corpus, arms)
    ablations = mechanism_ablations(signals, run.scoring)
    elapsed = time.time() - started

    print(f"\n{'=' * 78}\nEAR ON EVERY CALL — eval run\n{'=' * 78}")
    print(f"provider={extractor.name}   seed={run.seed}   config={run.hash()}   git={_git_sha()}")
    n_outcomes = sum(1 for c in corpus.customers if c.outcome is not Outcome.NONE)
    if _extraction_telemetry(extractor) is None:
        print(
            "NOTE: offline provider. These are plumbing-and-memory numbers, not headline accuracy."
        )
    else:
        print(f"NOTE: model reader ({extractor.name}). Every conversation was one model call.")
    print(f"NOTE: ONE dataset, {n_outcomes} outcome customers. Every recall below is an integer")
    print(f"      over {n_outcomes}, so arms one or two customers apart are indistinguishable.")
    print("      Nothing here should be published. Use `earshot sweep` for anything quotable.\n")

    print("CORPUS")
    for k, v in diagnostics.items():
        print(f"  {k:38s} {v}")

    print("\nEXTRACTION FIDELITY (published, not hidden)")
    for k, v in fidelity.items():
        print(f"  {k:38s} {v}")

    _print_extraction_telemetry(extractor)

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
        "extraction_telemetry": _extraction_telemetry(extractor),
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
    # Distinct CUSTOMERS, matching the denominator. `accumulation_only` holds one entry per
    # (customer, signal type), so a customer crossing on two families would be counted twice
    # against a population counted once.
    clean = len({customer_id for _, customer_id, _, _ in accumulation_only})
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
        # The same question the queue asks, not `>= cut`. This customer was selected BECAUSE
        # the baseline never alerts on them, and the baseline's scores cluster heavily at the
        # cut -- so a threshold comparison here prints "would flag" directly underneath the
        # line saying per-call detection never fires, on the customer chosen for that property.
        # Both conditions, and in this order. Queue membership alone printed "would flag" beside
        # a score well under the threshold on the line above, because the fallback customer IS in
        # the baseline's queue -- which handed the audience the counter-argument.
        if alone < stateless_cut:
            alone_verdict = "silent"
        elif per_call_catches(customer_id):
            alone_verdict = "would flag"
        else:
            alone_verdict = "at the cut, but ranked out of the queue"
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
    print(f"\nChosen from {clean} of {len(catchable)} thin-evidence customers who")
    print("went on to have a real outcome, where the ledger opens a case and per-call detection")
    if clean:
        print("does not. That ratio is the claim, and this is one instance of it.")
    else:
        # Saying the beat failed and then closing on "this is one instance of it" unsays it, and
        # the closing line is the one an audience keeps.
        print("does not. On this dataset that count is ZERO, so the arc above is the clearest")
        print("accumulation available and is NOT an instance of the claim. The ratio is the")
        print("result; a single customer never was.")
    print("\nIt is a DIFFERENT quantity from the recall table: this counts customers the ledger")
    print("catches and the baseline misses, on one dataset, while the table compares each arm's")
    print("recall across ten. The recall table is in `earshot sweep`; this ratio is from this")
    print("dataset only. Per-call")
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

    # Ranks on `ledger.best(cid, as_of=last day)` -- the max across signal FAMILIES on the
    # customer's most recent day. A reviewer queue asks "who should someone look at today", so
    # a faded score should rank low even if it once peaked.
    #
    # `evals.evaluate_arm()` ranks on the PEAK across the timeline instead, because it is
    # answering the recall question. The two orders diverge under decay, so this threshold and
    # that one can disagree about who crossed at the same budget. That is intended; see the
    # longer note in evals.py before changing either.
    scored.sort(key=lambda pair: (-pair[1].score, pair[0]))
    k = max(1, round(budget * len(corpus.customers)))
    cut = scored[:k]
    threshold = min((b.score for _, b in cut), default=0.0)
    return corpus, ledger, cut, threshold


def _context(
    corpus,
    customer_id: str,
    breakdown: ScoreBreakdown,
    threshold: float,
    seed: int,
    cutoff_day: int | None = None,
):
    """Assemble the agent's view of one customer.

    The truth object stays in this function. Only primitives cross into `ToolContext`, and
    nothing downstream can reach `outcome` — see tests/test_separation.py.

    `cutoff_day` drops conversations that had not arrived yet. `None` (the batch path) hands over
    the whole arc, which is right when the queue was cut from a finished corpus. The stream path
    passes the crossing day, because a live consumer cannot hand the agent a transcript that has
    not happened — and a demo that does is showing a batch with a clock painted on it.
    """
    truth = next(c for c in corpus.customers if c.customer_id == customer_id)
    conversations = tuple(
        c
        for c in corpus.conversations_for(customer_id)
        if cutoff_day is None or c.day <= cutoff_day
    )
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


def _case_record(
    ledger,
    ctx: ToolContext,
    breakdown: ScoreBreakdown,
    threshold: float,
    decision: InvestigationDecision,
    trace: InvestigationTrace,
) -> dict:
    """The case as it is persisted: the reviewer's three beats, plus the agent's verdict.

    Until this existed the artifact carried `decision` and `trace` only, so `ctx.score`,
    `ctx.signal_type`, `ctx.threshold` and every retro field died with the process — which left
    all three reviewer-UI beats (ranked list, evidence chain, retro re-score) unrenderable from
    disk. The tempting shortcut, regenerating the corpus from `manifest.seed` to recover them,
    is the one thing that must not happen: it puts `stratum`, `outcome` and `latent_risk`
    behind a client-facing screen. So the record is written here, from primitives, at the one
    point where they are all in hand.

    `case_record()` is shared with `CaseStore.put_case`, so the artifact and the DynamoDB item
    are the same shape by construction — the reviewer UI reads either.

`open_case()` supplies the crossing facts (`opened_on_day`, `opened_by_conversation`,
    `score_at_open`) — the ledger's own definition of when a case opened, not a second one
    written here. It can return None only if the current score clears the threshold while no
    point on the timeline ever did; under decay that cannot happen, so the fallback is a guard
    against a future scoring change, not an expected path.
    """
    opened = ledger.open_case(ctx.customer_id, breakdown.signal_type, threshold)
    if opened is None:
        opened = Case(
            customer_id=ctx.customer_id,
            signal_type=breakdown.signal_type,
            score=breakdown.score,
            opened_on_day=breakdown.as_of_day,
            opened_by_conversation=max(
                breakdown.entries, key=lambda e: e.signal.day
            ).signal.conversation_id,
            evidence=list(breakdown.entries),
        )
    # `breakdown` is the customer TODAY — the score `_queue` cut on, and the whole evidence
    # chain including everything that arrived after the case opened. `opened` contributes only
    # the crossing facts. Passing `opened.evidence` instead would freeze the retro chain at the
    # opening day and empty the beat for every customer who kept accumulating.
    return case_record(
        opened,
        threshold=threshold,
        now=breakdown,
        decision=decision.model_dump(),
        trace=trace.to_dict(),
    )


def _provider(name: str, prompt_sha: str):
    """Offline unless asked otherwise, and offline is always keyless.

    Selection and cache-mode handling live in `llm/select.py`, shared with the model reader and
    the two Lambda handlers, so the three cannot drift about what a provider name means. What
    stays here is only the default: this CLI is the thing a judge runs, and it must work with no
    credentials of any kind.
    """
    return build_provider(name or "offline", prompt_sha)


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
    corpus, ledger, cut, threshold = _queue(run)
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
    # The transcripts behind the cited quotes, so the artifact is sufficient for a reviewer screen
    # on its own. Deployed these live in S3, not in the case item, and this mirrors that split
    # exactly: a top-level map, keyed by conversation id, in `transcripts.to_payload`'s wire
    # format. Taken from the ToolContext the agent actually saw — which `test_separation.py`
    # already guarantees is answer-key-free — and NEVER by regenerating the corpus from the seed,
    # which is the shortcut that would put `stratum`, `outcome` and `latent_risk` behind a
    # client-facing screen.
    transcripts: dict[str, dict] = {}
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
        records.append(
            _case_record(ledger, ctx, breakdown, threshold, decision, trace)
        )
        for conversation in ctx.conversations:
            transcripts[conversation.conversation_id] = to_payload(conversation)

    elapsed = time.time() - started
    total_cost = sum(r["trace"]["cost_usd"] for r in records)
    # The FIRST-attempt failure rate, not the post-retry one. A decision whose citations do not
    # resolve is rejected inside the loop and never reaches here, so counting unresolved refs on
    # the returned decisions would report zero however badly the model behaved.
    #
    # CASES, not attempts: `evidence_repairs` counts rejected attempts and can reach 3 for a
    # single case, which printed against a denominator of cases would read "3/1".
    needed_repair = sum(1 for r in records if r["trace"]["evidence_repairs"])
    # The offline rule engine builds its citations from ledger entries it has already read, so
    # it cannot produce an unresolvable one. Saying so keeps a structural zero from reading as a
    # measurement of the model's honesty.
    caveat = (
        "  (offline rule engine — citations are built from the ledger, so this cannot be "
        "non-zero)"
        if provider_name == "offline"
        else ""
    )
    # Model time and wall clock are different quantities and in replay they differ by ~50x, so
    # printing one number labelled neither invites a judge to quote "2 investigations in 1.2s"
    # beside the per-case 33.4s the same screen already printed. Under replay both the cost and
    # the latency are RECORDED figures from the original live run, and are labelled as such.
    model_ms = sum(r["trace"]["latency_ms"] for r in records)
    replayed = cache_mode() == "replay" and provider_name != "offline"
    stamp = "recorded" if replayed else "measured"
    print(f"\n{'-' * 78}")
    print(f"{len(records)} investigations   {stamp} model time {model_ms / 1000:.1f}s   "
          f"{stamp} cost ${total_cost:.4f}   wall clock {elapsed:.1f}s"
          + ("  (replay, no network)" if replayed else ""))
    print(f"cases needing an evidence repair: {needed_repair}/{len(records)}{caveat}")

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
                "conversations": transcripts,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print(f"case files -> {out}")
    return 0


def stream_inputs(t: Tenant):
    """One tenant's corpus, as `(conversations, context_for)`.

    **This function is why `stream.py` can stay on the separation-guarded surface.** Generating a
    corpus and assembling a `ToolContext` both need the truth objects, and `cli.py` is the one
    module already exempted for exactly that (see the exemption list in
    `tests/test_separation.py`). Handing the stream engine a conversation sequence and a closure
    means it never holds an object carrying `stratum`, `outcome` or `latent_risk` — the guarantee
    is structural rather than a promise not to look.

    Cut at `breakdown.as_of_day`, which for a crossing is the day it happened, so the agent sees
    what a live consumer would have handed it and nothing that arrived afterwards.
    """
    corpus = generate(t.run)

    def context_for(customer_id: str, breakdown: ScoreBreakdown, threshold: float):
        return _context(
            corpus,
            customer_id,
            breakdown,
            threshold,
            t.run.seed,
            cutoff_day=breakdown.as_of_day,
        )

    return corpus.conversations, context_for


def _stream_manifest(t: Tenant, extractor, provider, provider_name: str) -> dict:
    """Provenance for one streamed tenant. The UI prints it on every screen.

    `reader` comes from the extractor's own `name`, which for the model reader is the model that
    ANSWERED rather than the one requested -- `bedrock.py` substitutes its own default by design,
    and the first keyed run in this repo was logged under the wrong model name because of it.

    `asr` is stamped `"none"` unconditionally. There is no speech recognition in this system and
    no code path that could add one, so this is a fact about the build, not a caption someone
    remembered to write. A screenshot outlives the caveat said out loud beside it.
    """
    system, _, prompt_sha = investigator_prompts()
    return {
        "tenant_id": t.tenant_id,
        "seed": t.run.seed,
        "config_hash": t.run.hash(),
        "git_sha": _git_sha(),
        "provider": getattr(provider, "name", provider_name),
        "reader": getattr(extractor, "name", None) or "offline-lexicon",
        "prompt_version": system.version,
        "prompt_sha": prompt_sha,
        "cache_mode": cache_mode(),
        "threshold": round(t.threshold, 4),
        "threshold_kind": "fixed cut, as the deployed ingest handler uses. NOT the "
                          "budget-derived threshold `earshot investigate` reports.",
        "asr": "none",
        "asr_note": "Transcripts are generated text replayed on a wall clock. The arrival "
                    "pattern is reproduced; no audio is transcribed anywhere in this system.",
        "data": "synthetic",
    }


def cmd_stream(
    tenant_names: str,
    provider_name: str,
    extractor_name: str,
    *,
    serve: bool = False,
    port: int = 8765,
    investigate_limit: int | None = None,
    pace_seconds: float = 0.0,
    narrate_live: int = 3,
) -> int:
    """Walk each tenant's book in arrival order and record a frame timeline per conversation.

    One artifact per tenant, because a tenant is a deployment: merging three books into one file
    would make the multi-enterprise view a presentation trick rather than three runs that happen
    to be shown together.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    try:
        tenants = resolve_tenants(tenant_names)
    except KeyError as exc:
        print(f"earshot stream: {exc}", file=sys.stderr)
        return 1
    if not tenants:
        print("earshot stream: no tenants selected", file=sys.stderr)
        return 1

    if serve:
        if len(tenants) != 1:
            print(
                "earshot stream --serve takes exactly one tenant, e.g. --tenant northwind. "
                "A live stream has one clock.",
                file=sys.stderr,
            )
            return 1
        from .stream_server import serve_stream

        return serve_stream(
            tenants[0],
            provider_name=provider_name,
            extractor_name=extractor_name,
            port=port,
            investigate_limit=investigate_limit,
            pace_seconds=pace_seconds,
            narrate_live=narrate_live,
        )

    _, _, prompt_sha = investigator_prompts()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    print(f"\n{'=' * 78}\nEAR ON EVERY CALL - live stream, replayable\n{'=' * 78}")
    print(f"reader={extractor_name}   agent-provider={provider_name}   "
          f"cache_mode={cache_mode()}   git={_git_sha()}")
    print("NO SPEECH RECOGNITION. Transcripts are generated text; what is replayed is the "
          "arrival pattern.")
    if provider_name == "offline":
        print("NOTE: the offline provider is a rule engine, not a model. Its verdicts are a "
              "floor, not a result.")

    grand_total = 0.0
    for t in tenants:
        extractor = build_extractor(extractor_name, t.run)
        provider = _provider(provider_name, prompt_sha)
        conversations, context_for = stream_inputs(t)
        try:
            run = run_stream(
                t,
                conversations,
                extractor,
                provider,
                context_for=context_for,
                investigate_limit=investigate_limit,
            )
            # The narration pass gets its OWN extractor instance. Its prefix reads would
            # otherwise land in `ExtractionTelemetry.conversations`, which is the denominator of
            # the published cost-per-1,000-conversations figure -- nine prefix reads counted as
            # nine conversations divides the same money by nine times the work.
            narrator = build_extractor(extractor_name, t.run)
            targets = narration_targets(run, t.narrate)
            by_id = {c.conversation_id: c for c in conversations}
            reads = narrate(narrator, [by_id[cid] for cid in targets if cid in by_id])
            run.narration_cost_usd = narration_totals(reads)["narration_cost_usd"]
            payload = stream_payload(
                run, _stream_manifest(t, extractor, provider, provider_name), reads
            )
        except (ProviderError, StreamError) as exc:
            print(f"\n{t.name}: {exc}", file=sys.stderr)
            return 1

        totals = payload["totals"]
        grand_total += totals["total_cost_usd"]
        slug = f"{t.tenant_id}-{extractor_name}-{provider_name}-{cache_mode()}"
        out = ARTIFACTS / f"stream-{slug}-{t.run.hash()}.json"
        out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

        print(f"\n{'-' * 78}")
        print(f"{t.name}  ({t.industry})   threshold {t.threshold:.2f} fixed")
        print(f"  {totals['conversations']} conversations from {totals['customers']} customers "
              f"over {totals['horizon_days']} days -> {totals['signals']} signals")
        print(f"  {totals['crossings']} crossings, {totals['investigated']} investigated, "
              f"{totals['not_investigated']} left unworked (recorded, with the reason)")
        for row in payload["teams"]:
            print(f"    {row['label']:<28} {row['cases']} case(s)")
        print(f"  {totals['conversations_narrated']} conversation(s) read turn-by-turn in "
              f"{totals['narration_calls']} calls; the other "
              f"{totals['conversations_read_once']} were read once")
        print(f"  reader ${totals['reader_cost_usd']:.4f} + agent "
              f"${totals['investigation_cost_usd']:.4f} + narration "
              f"${totals['narration_cost_usd']:.4f} = ${totals['total_cost_usd']:.4f}"
              + ("   (replay, recorded figures)" if cache_mode() == "replay" else ""))
        print(f"  -> {out}")
        _print_extraction_telemetry(extractor)

    print(f"\n{'=' * 78}")
    print(f"{len(tenants)} tenant(s), ${grand_total:.4f} total"
          + ("   (replay: these are the RECORDED figures from the keyed run)"
             if cache_mode() == "replay" else ""))
    print("Build the browser fixture:  uv run python tools/stream_fixture.py")
    return 0


def cmd_sweep(run: RunConfig, n_seeds: int, extractor: Extractor | None = None) -> int:
    """Many seeds, paired comparison, and the integers behind every rate.

    `run` reports one draw, and on a single 400-customer corpus every arm's recall is an
    integer over roughly 50 outcome customers, so arms one or two customers apart look
    different and are not. Nothing published comes from `run` alone.
    """
    from .sweep import paired_record, sign_test_p, sweep

    seeds = [run.seed + i for i in range(n_seeds)]
    if _extraction_telemetry(extractor) is not None:
        # A count, not an estimate: the reader is called once per conversation, and a sweep
        # generates corpora it has not built yet. Someone pointing a model at this deserves to
        # see the order of magnitude before it starts spending.
        print(
            f"NOTE: model reader over {n_seeds} seeds x {run.corpus.n_customers} customers. "
            f"Every conversation is one model call; measured cost is printed at the end.",
            file=sys.stderr,
        )
    started = time.time()
    summaries, by_arm = sweep(run, seeds, budget=INVESTIGATION_BUDGET, extractor=extractor)
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

    # How much of each arm's alert queue its score actually decided. An arm with few distinct
    # scores has a big tie cluster at the cut, and the rest of its queue is filled in
    # customer_id order -- which is worth knowing before trusting any comparison it appears in.
    print("\nRANKING RESOLUTION — how much of each queue the score decided, mean per seed")
    print(f"  {'arm':<18} {'distinct scores':>16} {'queue decided alphabetically':>30}")
    for name in sorted(summaries, key=lambda n: statistics.mean(
            [s.tie_decided for s in by_arm[n]])):
        samples = by_arm[name]
        distinct = statistics.mean([s.distinct_scores for s in samples])
        arbitrary = statistics.mean([s.tie_decided / s.flagged if s.flagged else 0.0
                                     for s in samples])
        print(f"  {name:<18} {distinct:>16.0f} {arbitrary:>29.1%}")

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

    if extractor is not None:
        _print_extraction_telemetry(extractor)

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
                    "extraction_telemetry": _extraction_telemetry(extractor),
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
    parser.add_argument(
        "command", choices=["run", "demo", "investigate", "sweep", "stream"]
    )
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
        "--conversations-per-customer",
        type=str,
        default=None,
        metavar="MIN,MAX",
        help="inclusive range of conversations each customer has, e.g. '8,20'. Exists so the "
        "history-length question can be asked: whether never-discard pulls ahead of a bounded "
        "window as arcs lengthen. Fragments are planted WITHOUT replacement, so a range whose "
        "MAX exceeds the smallest fragment pool leaves later conversations empty and the "
        "comparison stops being fair -- the command refuses rather than quietly doing that.",
    )
    parser.add_argument(
        "--provider",
        choices=["offline", "bedrock", "openrouter"],
        default="offline",
        help="investigate only. Offline needs no key and no network, and is the default so a "
             "judge can reproduce every screen with no account. `bedrock` is what the deployed "
             "system runs (D-022, D-025); `openrouter` exists for the committed replay cache "
             "recorded before the move.",
    )
    parser.add_argument(
        "--extractor",
        choices=["offline", "model"],
        default="offline",
        help="run and sweep only: which reader turns conversations into signals. `offline` is "
        "the keyless 26-regex lexicon and is the default, so everything runs with no key and no "
        "network. `model` reads every conversation with a model -- Bedrock unless $EARSHOT_LLM "
        "says otherwise -- and needs credentials, or EARSHOT_CACHE_MODE=replay against a "
        "recorded cache.",
    )
    parser.add_argument(
        "--limit", type=int, default=3, help="investigate only: how many cases to work."
    )
    parser.add_argument(
        "--tenant",
        default="all",
        help="stream only: which enterprise deployment(s) to stream -- 'all', or a "
        "comma-separated list of tenant ids from earshot/tenants.py. Each is the same engine on "
        "its own corpus with its own tuning, threshold and team names.",
    )
    parser.add_argument(
        "--cases",
        type=int,
        default=None,
        help="stream only: how many crossings to investigate with the agent, per tenant. "
        "Defaults to the tenant's own budget. Crossings beyond it are recorded as unworked with "
        "the reason, never silently dropped.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="stream only: serve ui/ on localhost and push frames over SSE as they are computed, "
        "so a demo makes real calls while the room watches. The recorded file:// replay stays the "
        "default because a judging room with no wifi must still see the product (D-004).",
    )
    parser.add_argument(
        "--port", type=int, default=8765, help="stream --serve only: the localhost port."
    )
    parser.add_argument(
        "--narrate-live",
        type=int,
        default=3,
        help="stream --serve only: how many signal-bearing conversations to read turn-by-turn "
        "as they arrive, so a belief can be watched forming on a call happening now. Each costs "
        "a model call per customer turn, so this is deliberately small. 0 turns it off.",
    )
    parser.add_argument(
        "--pace",
        type=float,
        default=0.0,
        help="stream --serve only: seconds to hold each frame. 0 (default) paces at the "
        "reader's own latency -- its live latency on a cold cache, its recorded latency on a "
        "warm one -- so the speed on screen is always a measurement rather than a chosen "
        "animation. Set EARSHOT_CACHE_MODE=off to force genuinely new calls on stage.",
    )
    args = parser.parse_args()

    run = DEFAULT
    conv_range: tuple[int, int] | None = None
    if args.conversations_per_customer:
        try:
            lo, hi = (int(x) for x in args.conversations_per_customer.split(","))
        except ValueError:
            parser.error("--conversations-per-customer takes MIN,MAX, e.g. '8,20'")
        if lo < 1 or hi < lo:
            parser.error(f"--conversations-per-customer needs 1 <= MIN <= MAX, got {lo},{hi}")
        scarcest_type, pool_size = smallest_fragment_pool()
        if hi > pool_size:
            parser.error(
                f"--conversations-per-customer MAX={hi} exceeds the smallest fragment pool "
                f"({scarcest_type.value}, {pool_size} fragments). Fragments are planted without "
                f"replacement, so no arc can carry more than {pool_size} signals however long it "
                f"gets, and a longer-history comparison would measure padding rather than "
                f"accumulation. Widen the pools in corpus_lexicon.py first."
            )
        conv_range = (lo, hi)

    # The same ceiling binds the DEFAULT range, and did so for every number published to date.
    # Warned rather than refused: it is a pre-existing property of the corpus, not something the
    # caller chose, and refusing here would break reproduction of the published figures.
    _scarce_type, _pool = smallest_fragment_pool()
    _default_max = DEFAULT.corpus.conversations_per_customer[1]
    if conv_range is None and _default_max > _pool:
        print(
            f"NOTE: arcs run to {_default_max} conversations but the scarcest fragment pool "
            f"({_scarce_type.value}) holds {_pool}, and fragments are planted without replacement. "
            f"Arcs on that trajectory carry at most {_pool} signals, so their later conversations "
            f"are empty by construction. This bounds what any history-length claim can show.",
            file=sys.stderr,
        )

    if args.seed != DEFAULT.seed or args.customers or conv_range:
        corpus_cfg = run.corpus
        if args.customers:
            corpus_cfg = replace(corpus_cfg, n_customers=args.customers)
        if conv_range:
            corpus_cfg = replace(corpus_cfg, conversations_per_customer=conv_range)
        run = replace(run, seed=args.seed, corpus=corpus_cfg)

    # None means "the offline lexicon, built from this run's config" — the default path, left
    # untouched so every published number reproduces exactly as before.
    extractor: Extractor | None = None
    if args.command in ("run", "sweep", "stream") and args.extractor != "offline":
        try:
            extractor = build_extractor(args.extractor, run)
        except ProviderError as exc:
            # A missing key is a setup problem, not a crash. Say which command still works.
            print(f"cannot build the {args.extractor} reader: {exc}", file=sys.stderr)
            print(
                "The default `--extractor offline` needs no key and no network.", file=sys.stderr
            )
            return 1
    elif args.extractor != "offline":
        parser.error(
            f"--extractor applies to run, sweep and stream, not to {args.command}"
        )

    if args.command == "run":
        return cmd_run(run, extractor)
    if args.command == "demo":
        return cmd_demo(run)
    if args.command == "sweep":
        return cmd_sweep(run, args.seeds, extractor)
    if args.command == "stream":
        return cmd_stream(
            args.tenant,
            args.provider,
            args.extractor,
            serve=args.serve,
            port=args.port,
            investigate_limit=args.cases,
            pace_seconds=args.pace,
            narrate_live=args.narrate_live,
        )
    return cmd_investigate(run, args.provider, args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
