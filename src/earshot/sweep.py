"""Multi-seed evaluation. Everything publishable comes through here.

A point estimate from one generator draw is not a result. A 400-customer corpus yields around
40 outcome customers, so every recall is an integer over 40: two arms a single customer apart
differ by 0.025 and read as a finding, while random flagging at a 10% budget already scores
0.100. One draw cannot separate any arm from any other.

So this runs the whole pipeline across many seeds and reports the spread, the paired win/loss
record between arms, and the raw counts behind every rate — a rate is never quoted without the
integers that produced it.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, replace

from .arms import run_all_arms
from .config import RunConfig
from .corpus import generate
from .evals import evaluate_arm
from .extract import OfflineLexiconExtractor, extract_all
from .schema import Outcome, Stratum


@dataclass
class ArmSample:
    """One arm's result on one seed, with the integers behind the rate."""

    arm: str
    seed: int
    recall: float
    hits: int
    outcomes: int
    flagged: int
    diffuse_recall: float
    diffuse_hits: int = 0
    diffuse_outcomes: int = 0


@dataclass
class ArmSummary:
    arm: str
    n_seeds: int
    mean_recall: float
    stdev: float
    lo: float
    hi: float
    total_hits: int
    total_outcomes: int
    mean_diffuse: float

    @property
    def pooled_recall(self) -> float:
        """Recall over every outcome customer across every seed, not a mean of rates."""
        return self.total_hits / self.total_outcomes if self.total_outcomes else 0.0


def _one_seed(base: RunConfig, seed: int, budget: float) -> list[ArmSample]:
    run = replace(base, seed=seed)
    corpus = generate(run)
    extractor = OfflineLexiconExtractor(
        miss_rate=run.offline_miss_rate, false_fire_rate=run.offline_false_fire_rate
    )
    signals = extract_all(extractor, corpus.conversations)
    arms = run_all_arms(signals, run.scoring)
    n_outcomes = sum(1 for c in corpus.customers if c.outcome is not Outcome.NONE)

    # Denominator for the diffuse stratum: outcome customers whose evidence was spread thin.
    # Carried explicitly so the headline rate is never quoted without the integers behind it.
    n_diffuse = sum(
        1
        for c in corpus.customers
        if c.outcome is not Outcome.NONE and c.stratum is Stratum.DIFFUSE
    )

    out: list[ArmSample] = []
    for name, arm in arms.items():
        r = evaluate_arm(corpus, arm, budget)
        # Indexed, not .get() -- a renamed stratum must fail loudly rather than silently
        # reporting the pre-registered headline as 0/780.
        diffuse = r.recall_by_stratum["diffuse"]
        out.append(
            ArmSample(
                arm=name,
                seed=seed,
                recall=r.recall,
                hits=round(r.recall * n_outcomes),
                outcomes=n_outcomes,
                flagged=r.n_flagged,
                diffuse_recall=diffuse,
                diffuse_hits=round(diffuse * n_diffuse),
                diffuse_outcomes=n_diffuse,
            )
        )
    return out


def sweep(
    base: RunConfig, seeds: list[int], budget: float = 0.10
) -> tuple[dict[str, ArmSummary], dict[str, list[ArmSample]]]:
    by_arm: dict[str, list[ArmSample]] = {}
    for seed in seeds:
        for sample in _one_seed(base, seed, budget):
            by_arm.setdefault(sample.arm, []).append(sample)

    summaries: dict[str, ArmSummary] = {}
    for arm, samples in by_arm.items():
        recalls = [s.recall for s in samples]
        summaries[arm] = ArmSummary(
            arm=arm,
            n_seeds=len(samples),
            mean_recall=statistics.mean(recalls),
            stdev=statistics.stdev(recalls) if len(recalls) > 1 else 0.0,
            lo=min(recalls),
            hi=max(recalls),
            total_hits=sum(s.hits for s in samples),
            total_outcomes=sum(s.outcomes for s in samples),
            mean_diffuse=statistics.mean([s.diffuse_recall for s in samples]),
        )
    return summaries, by_arm


def paired_record(
    by_arm: dict[str, list[ArmSample]], a: str, b: str, metric: str = "recall"
) -> tuple[int, int, int]:
    """Seed-by-seed win/loss/tie for arm `a` against arm `b` on `metric`.

    Paired on seed, because the seeds share a corpus and comparing means across independent
    draws throws that pairing away.

    `metric` chooses what the pairing is on. The pre-registered headline is the DIFFUSE-stratum
    comparison rather than overall recall, and anything published has to be reproducible by a
    command in this repo, so both must be reachable from here.
    """
    left = {s.seed: getattr(s, metric) for s in by_arm.get(a, [])}
    right = {s.seed: getattr(s, metric) for s in by_arm.get(b, [])}
    wins = losses = ties = 0
    for seed in sorted(set(left) & set(right)):
        if left[seed] > right[seed]:
            wins += 1
        elif left[seed] < right[seed]:
            losses += 1
        else:
            ties += 1
    return wins, losses, ties


def sign_test_p(wins: int, losses: int) -> float:
    """Two-sided sign test. Ties dropped, which is the conservative choice.

    Not McNemar on individual customers — this pairs at the seed level, which is the unit that
    actually varies. Exact, no dependencies, and honest about how little power a handful of
    seeds buys.
    """
    n = wins + losses
    if n == 0:
        return 1.0

    def comb(nn: int, kk: int) -> int:
        result = 1
        for i in range(kk):
            result = result * (nn - i) // (i + 1)
        return result

    extreme = min(wins, losses)
    tail = sum(comb(n, k) for k in range(extreme + 1))
    return min(1.0, 2 * tail / (2**n))
