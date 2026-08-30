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
from .evals import evaluate_arm, tie_break_seed_for
from .extract import Extractor, OfflineLexiconExtractor, extract_all


@dataclass
class ArmSample:
    """One arm's result on one seed, with the integers behind the rate.

    Both arc strata are carried, not just the headline one: the ledger wins on diffuse arcs and
    loses on concentrated ones, and reporting only the stratum we win on would be picking the
    result out of a comparison the code already computes in full.
    """

    arm: str
    seed: int
    recall: float
    hits: int
    outcomes: int
    flagged: int
    diffuse_recall: float
    diffuse_hits: int = 0
    diffuse_outcomes: int = 0
    concentrated_recall: float = 0.0
    concentrated_hits: int = 0
    concentrated_outcomes: int = 0
    distinct_scores: int = 0
    tie_decided: int = 0


@dataclass
class ArmSummary:
    """Pooled and mean-of-rates statistics are BOTH carried, under names that say which is which.

    They differ (seeds have different denominators), and publishing one while an artifact stores
    the other under a shared name is how a reader checking the table finds a third number.
    """

    arm: str
    n_seeds: int
    mean_recall: float
    stdev: float
    lo: float
    hi: float
    total_hits: int
    total_outcomes: int
    mean_diffuse: float
    total_diffuse_hits: int = 0
    total_diffuse_outcomes: int = 0
    mean_concentrated: float = 0.0
    total_concentrated_hits: int = 0
    total_concentrated_outcomes: int = 0

    @staticmethod
    def _pooled(hits: int, outcomes: int) -> float:
        return hits / outcomes if outcomes else 0.0

    @property
    def pooled_recall(self) -> float:
        """Recall over every outcome customer across every seed, not a mean of rates."""
        return self._pooled(self.total_hits, self.total_outcomes)

    @property
    def pooled_diffuse(self) -> float:
        return self._pooled(self.total_diffuse_hits, self.total_diffuse_outcomes)

    @property
    def pooled_concentrated(self) -> float:
        return self._pooled(self.total_concentrated_hits, self.total_concentrated_outcomes)


def _one_seed(
    base: RunConfig,
    seed: int,
    budget: float,
    extractor: Extractor | None = None,
    randomise_ties: bool = False,
) -> list[ArmSample]:
    run = replace(base, seed=seed)
    corpus = generate(run)
    # Built per seed when it is the offline lexicon, because its simulated rates come from the
    # seed's own config. A caller-supplied reader is reused across seeds instead: it is stateless
    # per conversation, and one instance is what accumulates cost and latency over the whole sweep.
    if extractor is None:
        extractor = OfflineLexiconExtractor(
            miss_rate=run.offline_miss_rate, false_fire_rate=run.offline_false_fire_rate
        )
    signals = extract_all(extractor, corpus.conversations)
    # `random-rank`'s own RNG is seeded from the corpus seed directly -- it needs only to be
    # reproducible per seed, not independent of the corpus draw the way the TIE-BREAK seed below
    # must be (a random-rank arm ignoring the corpus is the whole point of it; the tie-break
    # question is a different one, about arms that DO read the evidence).
    arms = run_all_arms(signals, run.scoring, seed=seed)
    # `None` unless the caller opted in, so every existing call site (including this function's
    # own default) keeps the deterministic customer_id tie-break and every published number
    # keeps reproducing exactly. `tie_break_seed_for` hashes into its own namespace so the
    # tie-break draw and the corpus's own `random.Random(seed)` stream never correlate.
    tie_break_seed = tie_break_seed_for(seed) if randomise_ties else None
    out: list[ArmSample] = []
    for name, arm in arms.items():
        r = evaluate_arm(corpus, arm, budget, tie_break_seed)
        # Indexed, not .get() -- a renamed stratum must fail loudly rather than silently
        # reporting the pre-registered headline as 0/780.
        out.append(
            ArmSample(
                arm=name,
                seed=seed,
                recall=r.recall,
                hits=r.n_hits,
                outcomes=r.n_outcomes,
                flagged=r.n_flagged,
                diffuse_recall=r.recall_by_stratum["diffuse"],
                diffuse_hits=r.stratum_hits["diffuse"],
                diffuse_outcomes=r.stratum_outcomes["diffuse"],
                concentrated_recall=r.recall_by_stratum["concentrated"],
                concentrated_hits=r.stratum_hits["concentrated"],
                concentrated_outcomes=r.stratum_outcomes["concentrated"],
                distinct_scores=r.n_distinct_scores,
                tie_decided=r.n_tie_decided,
            )
        )
    return out


def sweep(
    base: RunConfig,
    seeds: list[int],
    budget: float = 0.10,
    extractor: Extractor | None = None,
    randomise_ties: bool = False,
) -> tuple[dict[str, ArmSummary], dict[str, list[ArmSample]]]:
    by_arm: dict[str, list[ArmSample]] = {}
    for seed in seeds:
        for sample in _one_seed(base, seed, budget, extractor, randomise_ties):
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
            total_diffuse_hits=sum(s.diffuse_hits for s in samples),
            total_diffuse_outcomes=sum(s.diffuse_outcomes for s in samples),
            mean_concentrated=statistics.mean([s.concentrated_recall for s in samples]),
            total_concentrated_hits=sum(s.concentrated_hits for s in samples),
            total_concentrated_outcomes=sum(s.concentrated_outcomes for s in samples),
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
