"""Reader coverage — does the model reader find the planted evidence the lexicon misses,
and does that change who the ledger surfaces? Not yet ticketed.

    uv run python tools/reader_coverage.py                                   # free, keyless
    uv run python tools/reader_coverage.py --reader both --per-trajectory 8 --yes
    EARSHOT_CACHE_MODE=replay uv run python tools/reader_coverage.py --reader both

**The question, and why it is worth a tool.** The offline lexicon is a 26-regex keyless fallback
and every published extraction figure measures it. On the shipped 2,400-customer corpus it picks
up churn evidence in 1.35 of the 3.42 conversations that carry it (0.40) against 0.70-0.77 for
the other three families. Corroboration in `memory.py` is CROSS-conversation -- `1 + 0.35 *
(n_conversations - 1)` -- so a family read in a third of its conversations cannot reach the
multiplier the others get. Churn-trajectory customers top out at 0.6455 against a 0.6747
threshold and **none of the 325 of them ever crosses**: under the keyless fallback the Retention
desk receives no case at all, ever.

Fragment strengths in `corpus_lexicon.py` are comparable across families and churn's maximum is
the highest of the four, so the gap is in authoring pass B -- the extractor cues -- not in the
corpus. That is a statement about a fallback, not about the system: the deployed reader is a
model. So the question this answers is whether a route that is dead under the fallback is alive
under the reader the system actually runs.

**Two measurements, and the second is the point.** Coverage alone ("the model found more") is a
detection number, and detection is the framing this entry does not compete in. What matters is
what the ledger then does with the extra conversations, so both readers' signals go through the
SAME `SignalLedger` at the SAME scoring config and the same threshold, and the report ends on how
many customers clear it per reader.

**Where the threshold comes from, and which of the two it is.** `cli._queue` at
`INVESTIGATION_BUDGET`: a **budget-derived top-K** cut over the whole corpus, ranked on
`ledger.best(customer, last_day)`. It is NOT the fixed cut `stream.py` and `aws/ingest.py` use --
a streaming consumer has no population to rank against, so the two disagree on purpose and are
never merged. Nothing here invents a threshold.

**The threshold is derived from the OFFLINE reader's population, and that biases in one
direction.** Ranking all 8,359 conversations with a model to get a model-derived threshold costs
about $14, so the offline threshold is held fixed across both arms. A reader that finds more
would raise every customer's score, so a fixed 10% budget would settle at a HIGHER cut. Model-arm
crossings at this threshold are therefore an upper bound on what that budget would actually
surface, and the output says so rather than leaving it to be discovered.

**Sampling.** Even across the four trajectories, first N by `customer_id`. Not the top of the
ledger queue: that would select customers the offline reader already read well, which is the
quantity under test -- the same "a measurement drawn from the top of the queue cannot be wrong in
the direction that matters" failure `verdict_accuracy.py` exists to avoid. Customers are
generated independently and in id order, so first-N is an unbiased draw, it reproduces from the
seed alone, and a larger N is a superset of a smaller one -- so growing the sample re-reads
nothing already in the cache.

**Denominators are planted counts, never found counts.** A reader that fires on conversations
carrying no plant cannot improve its own ratio; those fires are counted and reported in their own
column, never folded in.
"""

from __future__ import annotations

import argparse
import json
import time
import warnings
from collections import defaultdict
from dataclasses import replace
from typing import Any

from earshot.arms import demo_ledger
from earshot.cli import ARTIFACTS, INVESTIGATION_BUDGET, _git_sha, _queue, build_extractor
from earshot.config import DEFAULT, RunConfig
from earshot.corpus import ArcCeilingWarning, check_arc_ceiling, pipeline_fingerprint
from earshot.extract import extract_all
from earshot.llm import cache_mode
from earshot.schema import Conversation, CustomerTruth, ExtractedSignal, SignalType

# Measured, not quoted from a price list: `ExtractionTelemetry.cost_per_1000_conversations` over
# the committed Haiku 4.5 reads behind this repo's published reader figures. Any other model
# makes this projection wrong, and `--model` says so on screen.
MEASURED_USD_PER_1000_CONVERSATIONS = 1.6563

TRAJECTORIES: tuple[str, ...] = tuple(sorted(t.value for t in SignalType))


# -- sampling ---------------------------------------------------------------------------------


def sample(corpus, per_trajectory: int) -> list[CustomerTruth]:
    """`per_trajectory` customers from each seeded trajectory, first N by `customer_id`.

    Returns fewer for a family the corpus does not hold enough of, rather than topping up from
    another family: a sample that silently rebalances itself is not the sample the caller asked
    for, and the per-family denominators would stop being comparable.
    """
    by_trajectory: dict[str, list[CustomerTruth]] = defaultdict(list)
    for customer in sorted(corpus.customers, key=lambda c: c.customer_id):
        if customer.trajectory is not None:
            by_trajectory[customer.trajectory.value].append(customer)
    drawn: list[CustomerTruth] = []
    for trajectory in TRAJECTORIES:
        drawn.extend(by_trajectory.get(trajectory, [])[:per_trajectory])
    return drawn


def conversations_for(corpus, sampled: list[CustomerTruth]) -> tuple[Conversation, ...]:
    """Every conversation belonging to the sampled customers, in a stable order.

    Both readers are handed this exact tuple. Conversations are what a keyed run pays for, so
    this is also the number the cost gate is computed from.
    """
    wanted = {c.customer_id for c in sampled}
    return tuple(
        sorted(
            (c for c in corpus.conversations if c.customer_id in wanted),
            key=lambda c: (c.customer_id, c.day, c.conversation_id),
        )
    )


def planted_conversations(corpus, sampled: list[CustomerTruth]) -> dict[str, frozenset[str]]:
    """Customer id -> the conversations carrying a genuine plant of THEIR trajectory's family.

    This is the denominator, and it comes from `Corpus.seeded` -- the answer key, authored
    before any prose existed and read here on the evaluation side only. Decoy plants are
    excluded: firing on a lookalike is not coverage of anything.
    """
    trajectory_of = {c.customer_id: c.trajectory for c in sampled}
    out: dict[str, set[str]] = {c.customer_id: set() for c in sampled}
    for seeded in corpus.seeded:
        trajectory = trajectory_of.get(seeded.customer_id)
        if trajectory is None or seeded.is_decoy or seeded.signal_type is not trajectory:
            continue
        out[seeded.customer_id].add(seeded.conversation_id)
    return {cid: frozenset(convs) for cid, convs in out.items()}


def found_conversations(
    signals: list[ExtractedSignal], sampled: list[CustomerTruth]
) -> dict[str, frozenset[str]]:
    """Customer id -> the conversations where the reader emitted THEIR trajectory's family.

    Every conversation the reader fired that family in, including ones with no plant. The split
    into hits and unplanted fires happens in `coverage()`, so the raw fire set stays visible.
    """
    trajectory_of = {c.customer_id: c.trajectory for c in sampled}
    out: dict[str, set[str]] = {c.customer_id: set() for c in sampled}
    for signal in signals:
        trajectory = trajectory_of.get(signal.customer_id)
        if trajectory is None or signal.signal_type is not trajectory:
            continue
        out[signal.customer_id].add(signal.conversation_id)
    return {cid: frozenset(convs) for cid, convs in out.items()}


# -- measurement one: coverage ----------------------------------------------------------------


def coverage(
    sampled: list[CustomerTruth],
    planted: dict[str, frozenset[str]],
    found: dict[str, frozenset[str]],
) -> dict[str, dict[str, Any]]:
    """Per trajectory: conversations planted, conversations the reader found the plant in, ratio.

    `ratio = found / planted`, and `planted` is the only denominator that appears. Unplanted
    fires are counted in their own field and can never raise the ratio -- a reader that emitted
    the family in every conversation of every customer would score exactly 1.0 here and carry a
    large `unplanted_fires`, which is the honest way round.
    """
    rows: dict[str, dict[str, Any]] = {}
    for trajectory in TRAJECTORIES:
        members = [c for c in sampled if c.trajectory.value == trajectory]
        if not members:
            continue
        n_planted = sum(len(planted[c.customer_id]) for c in members)
        n_found = sum(len(found[c.customer_id] & planted[c.customer_id]) for c in members)
        n_unplanted = sum(len(found[c.customer_id] - planted[c.customer_id]) for c in members)
        rows[trajectory] = {
            "customers": len(members),
            "planted_conversations": n_planted,
            "found_conversations": n_found,
            "unplanted_fires": n_unplanted,
            "mean_planted_per_customer": round(n_planted / len(members), 4),
            "mean_found_per_customer": round(n_found / len(members), 4),
            "ratio": round(n_found / n_planted, 4) if n_planted else 0.0,
        }
    return rows


# -- measurement two: the consequence ---------------------------------------------------------


def consequence(
    corpus,
    sampled: list[CustomerTruth],
    signals: list[ExtractedSignal],
    scoring,
    threshold: float,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """The same signals through the same ledger. Returns (per-trajectory rows, per-customer rows).

    A customer's score depends only on their own signals, so restricting the ledger to the
    sample cannot move any score in it -- only the threshold needs a population, and that comes
    from the full-corpus queue.

    The headline score is the customer's own seeded family (`ledger.score`), because that is the
    route in question: a churn customer crossing on a stray financial-distress signal reaches
    Collections, not Retention, and counting it as a churn crossing would answer a question
    nobody asked. Crossings in some OTHER family are counted separately for exactly that reason.

    `as_of` is the customer's last conversation day, which is how `cli._queue` ranks -- "who
    should someone look at today" rather than "who once peaked".
    """
    ledger = demo_ledger(signals, scoring)
    last_day = {
        c.customer_id: max((cv.day for cv in corpus.conversations_for(c.customer_id)), default=0)
        for c in sampled
    }

    per_customer: dict[str, dict[str, Any]] = {}
    for customer in sampled:
        as_of = last_day[customer.customer_id]
        family = ledger.score(customer.customer_id, customer.trajectory, as_of).score
        best = ledger.best(customer.customer_id, as_of)
        per_customer[customer.customer_id] = {
            "customer_id": customer.customer_id,
            "trajectory": customer.trajectory.value,
            "stratum": customer.stratum.value,
            "as_of_day": as_of,
            "family_score": round(family, 4),
            "best_family": best.signal_type.value,
            "best_score": round(best.score, 4),
            "cleared": family >= threshold,
            "cleared_other_family": family < threshold <= best.score,
        }

    rows: dict[str, dict[str, Any]] = {}
    for trajectory in TRAJECTORIES:
        members = [
            per_customer[c.customer_id] for c in sampled if c.trajectory.value == trajectory
        ]
        if not members:
            continue
        scores = [m["family_score"] for m in members]
        rows[trajectory] = {
            "customers": len(members),
            "best_score": round(max(scores), 4),
            "mean_score": round(sum(scores) / len(scores), 4),
            "cleared": sum(1 for m in members if m["cleared"]),
            "cleared_other_family": sum(1 for m in members if m["cleared_other_family"]),
        }
    return rows, per_customer


# -- cost -------------------------------------------------------------------------------------


def projected_cost_usd(n_conversations: int) -> float:
    """What a keyed pass over this sample costs, from the measured rate. One model call per
    conversation -- `ModelExtractor.extract` reads one conversation and nothing else."""
    return round(n_conversations * MEASURED_USD_PER_1000_CONVERSATIONS / 1000.0, 4)


def spends_money(readers: tuple[str, ...], mode: str) -> bool:
    """Whether this run can reach the network at all.

    Replay raises `CacheMiss` rather than calling out, so a replayed model arm cannot spend --
    that is the guarantee the committed cache exists to give. Everything else that names the
    model reader can, and needs `--yes`.
    """
    return "model" in readers and mode != "replay"


# -- reader construction ----------------------------------------------------------------------


def build_reader(name: str, run: RunConfig, model_id: str | None):
    """One door for both arms.

    No `cache=` and no explicit cache path for the model arm, deliberately:
    `extract_model.extractor_cache_path()` then picks one file per model, so a non-default model
    named with `--model` cannot append its completions into the committed `extractor.jsonl` that
    the published reader figures replay from.
    """
    if name != "model":
        return build_extractor(name, run)
    if model_id is None:
        return build_extractor("model", run)
    from earshot.extract_model import DEFAULT_MAX_TOKENS, model_extractor
    from earshot.llm.base import ModelConfig

    return model_extractor(model_cfg=ModelConfig(model=model_id, max_tokens=DEFAULT_MAX_TOKENS))


# -- printing ---------------------------------------------------------------------------------

_COVERAGE_HEAD = (
    f"  {'trajectory':<22}{'cust':>6}{'planted':>9}{'found':>7}{'ratio':>8}"
    f"{'per customer':>16}{'unplanted':>11}"
)
_CONSEQUENCE_HEAD = (
    f"  {'trajectory':<22}{'cust':>6}{'best':>9}{'mean':>8}{'cleared':>12}{'other family':>15}"
)


def print_coverage(reader_name: str, rows: dict[str, dict[str, Any]]) -> None:
    print(f"\n  reader = {reader_name}")
    print(_COVERAGE_HEAD)
    for trajectory, row in rows.items():
        per_customer = (
            f"{row['mean_planted_per_customer']:.2f} -> {row['mean_found_per_customer']:.2f}"
        )
        print(
            f"  {trajectory:<22}{row['customers']:>6}{row['planted_conversations']:>9}"
            f"{row['found_conversations']:>7}{row['ratio']:>8.2f}{per_customer:>16}"
            f"{row['unplanted_fires']:>11}"
        )


def print_consequence(reader_name: str, rows: dict[str, dict[str, Any]]) -> None:
    print(f"\n  reader = {reader_name}")
    print(_CONSEQUENCE_HEAD)
    for trajectory, row in rows.items():
        cleared = f"{row['cleared']} / {row['customers']}"
        other = f"{row['cleared_other_family']} / {row['customers']}"
        print(
            f"  {trajectory:<22}{row['customers']:>6}{row['best_score']:>9.4f}"
            f"{row['mean_score']:>8.4f}{cleared:>12}{other:>15}"
        )


def build_parser() -> argparse.ArgumentParser:
    """Separate from `main` so a test can read the defaults. A tool whose bare invocation spends
    money gets run by accident exactly once, so `--reader` defaulting to the free arm is a
    property worth pinning rather than a preference."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--reader",
        default="offline",
        choices=["offline", "model", "both"],
        help="offline is the default because it spends nothing",
    )
    parser.add_argument("--per-trajectory", type=int, default=6,
                        help="customers drawn from EACH of the four seeded trajectories")
    parser.add_argument("--customers", type=int, default=2400,
                        help="corpus size; the threshold is a top-K cut over all of it")
    parser.add_argument("--seed", type=int, default=DEFAULT.seed)
    parser.add_argument("--model", default=None,
                        help="a non-default reader model; gets its own cache file")
    parser.add_argument("--yes", action="store_true",
                        help="confirm the projected spend and run the model arm")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.per_trajectory < 1:
        parser.error("--per-trajectory must be at least 1")

    run = replace(
        DEFAULT, seed=args.seed, corpus=replace(DEFAULT.corpus, n_customers=args.customers)
    )
    readers: tuple[str, ...] = ("offline", "model") if args.reader == "both" else (args.reader,)
    mode = cache_mode()

    # Said once here in prose, then silenced for the duplicate `generate()` is about to raise --
    # same handling as `cli.main`, `filterwarnings` so nothing else in the filter list is lost.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ArcCeilingWarning)
        check_arc_ceiling(run.corpus)
    for warning in caught:
        print(f"NOTE: {warning.message}")
    warnings.filterwarnings("ignore", category=ArcCeilingWarning)

    print(f"\n{'=' * 78}\nREADER COVERAGE — planted evidence found, and who then crosses"
          f"\n{'=' * 78}")
    started = time.time()
    corpus, _, cut, threshold = _queue(run)
    sampled = sample(corpus, args.per_trajectory)
    conversations = conversations_for(corpus, sampled)
    trajectory_bearing = sum(1 for c in corpus.customers if c.trajectory is not None)

    print(f"seed={run.seed}   config={run.hash()}   pipeline={pipeline_fingerprint()}   "
          f"git={_git_sha()}   cache={mode}")
    print(f"{len(corpus.customers)} customers, {len(corpus.conversations)} conversations; "
          f"{trajectory_bearing} carry a seeded trajectory.")
    print(f"sample: {args.per_trajectory} per trajectory = {len(sampled)} customers, "
          f"{len(conversations)} conversations — one model call each, per model arm.")
    print(f"threshold {threshold:.4f} — budget-derived top-K ({len(cut)} of "
          f"{len(corpus.customers)} at INVESTIGATION_BUDGET={INVESTIGATION_BUDGET}, ranked by "
          f"cli._queue on the offline reader).")
    print("  NOT the fixed cut stream.py and aws/ingest.py apply. The two disagree on purpose: "
          "a streaming\n  consumer has no population to rank against.")

    if "model" in readers:
        cost = projected_cost_usd(len(conversations))
        print(f"\n  PROJECTED SPEND: {len(conversations)} conversations x "
              f"${MEASURED_USD_PER_1000_CONVERSATIONS} per 1,000 = ${cost:.4f}")
        if args.model:
            print(f"  That rate was measured on the default reader. --model {args.model} is a "
                  f"different price; treat the figure as an order of magnitude.")
        if not spends_money(readers, mode):
            print("  cache=replay: a miss raises rather than calling out, so this run cannot "
                  "spend. Costs below are the RECORDED figures from the keyed run.")
        elif not args.yes:
            print("  Re-run with --yes to spend it. Nothing has been called.")
            return 1

    arms: dict[str, dict[str, Any]] = {}
    planted = planted_conversations(corpus, sampled)
    for reader_name in readers:
        extractor = build_reader(reader_name, run, args.model)
        signals = extract_all(extractor, conversations)
        found = found_conversations(signals, sampled)
        rows, per_customer = consequence(corpus, sampled, signals, run.scoring, threshold)
        telemetry = getattr(extractor, "telemetry", None)
        arms[reader_name] = {
            # Read AFTER the calls, never before: `ModelExtractor.name` is the model that
            # ANSWERED, and the requested id and the served id are routinely different.
            "reader": extractor.name,
            "signals": len(signals),
            "coverage": coverage(sampled, planted, found),
            "consequence": rows,
            "per_customer": per_customer,
            "telemetry": telemetry.to_dict() if telemetry is not None else None,
        }

    print(f"\n{'-' * 78}")
    print("COVERAGE — conversations carrying the trajectory's plant that the reader found.")
    print("Denominator is what was PLANTED. Unplanted fires are counted, never folded in.")
    for arm in arms.values():
        print_coverage(arm["reader"], arm["coverage"])

    print(f"\n{'-' * 78}")
    print(f"CONSEQUENCE — the same signals through the same SignalLedger at {threshold:.4f}.")
    print("Score is the customer's own seeded family: that is the desk the case would reach.")
    for arm in arms.values():
        print_consequence(arm["reader"], arm["consequence"])
    print("\n  'other family' = crossed on a different signal family, so the case exists but "
          "lands at another desk.")
    if "model" in readers:
        print("  UPPER BOUND for the model arm: the threshold is a top-K cut over the OFFLINE "
              "reader's ranking\n  of the whole corpus. A reader that finds more would raise "
              "every score, so the same 10% review\n  budget would settle at a higher cut than "
              f"this one. Measuring that costs a keyed pass over\n  all "
              f"{len(corpus.conversations)} conversations "
              f"(${projected_cost_usd(len(corpus.conversations)):.2f}).")

    for arm in arms.values():
        if arm["telemetry"] is not None:
            print(f"\n  {arm['reader']} — measured on this run")
            for key, value in arm["telemetry"].items():
                print(f"    {key:38s} {value}")

    # A model arm that made no calls measured nothing, and an artifact of zeros is worse than no
    # artifact: it has a manifest on it and reads as evidence. Same stop `verdict_accuracy.py`
    # puts in front of a run whose every case ended in `provider_error`.
    for name, arm in arms.items():
        if name == "model" and arm["telemetry"] and not arm["telemetry"]["model_calls"]:
            print(f"\n  NOT WRITING AN ARTIFACT: the model arm made 0 calls over "
                  f"{len(conversations)} conversations, so it measured nothing "
                  f"({arm['telemetry']['unparsable_replies']} unparsable replies).")
            return 1

    elapsed = time.time() - started
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    # `per_trajectory` is in the filename, not only the manifest: two model runs at different
    # sample sizes are different measurements and one must not overwrite the other. The reader
    # list and the cache mode are there for the same reason -- a free offline run and a keyed
    # one, or a record and a replay, are different evidence and never share a path.
    out = ARTIFACTS / (
        f"reader-coverage-{run.seed}-{run.hash()}-{'-'.join(readers)}"
        f"-pt{args.per_trajectory}-{mode}.json"
    )
    out.write_text(
        json.dumps(
            {
                "manifest": {
                    "seed": run.seed,
                    "config_hash": run.hash(),
                    # `config_hash` covers configuration VALUES only, and the generator is code.
                    # That gap cost a $1.50 keyed run on 2026-08-28 -- see
                    # `corpus.pipeline_fingerprint`.
                    "pipeline_sha": pipeline_fingerprint(),
                    "git_sha": _git_sha(),
                    "cache_mode": mode,
                    "readers": [arm["reader"] for arm in arms.values()],
                    "requested_model": args.model,
                    "per_trajectory": args.per_trajectory,
                    "sampled_customers": len(sampled),
                    "sampled_conversations": len(conversations),
                    "corpus_customers": len(corpus.customers),
                    "corpus_conversations": len(corpus.conversations),
                    "trajectory_bearing_customers": trajectory_bearing,
                    "threshold": round(threshold, 6),
                    "threshold_kind": (
                        f"budget-derived top-K, cli._queue at "
                        f"INVESTIGATION_BUDGET={INVESTIGATION_BUDGET}, offline reader"
                    ),
                    "queue_size": len(cut),
                    "elapsed_seconds": round(elapsed, 2),
                },
                "arms": {
                    name: {
                        "reader": arm["reader"],
                        "signals": arm["signals"],
                        "coverage": arm["coverage"],
                        "consequence": arm["consequence"],
                        "telemetry": arm["telemetry"],
                        "cases": sorted(
                            arm["per_customer"].values(),
                            key=lambda r: (r["trajectory"], r["customer_id"]),
                        ),
                    }
                    for name, arm in arms.items()
                },
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
