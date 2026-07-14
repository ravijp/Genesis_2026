# Research Basis for the Ideation-v2 Protocol (2026-07-15)

Scoped web-research pass (sonnet, 14 searches/fetches) on maximizing LLM ideation creativity/diversity and preventing anchoring — the evidence behind `PROTOCOL.md`'s design choices. Verbatim findings below; each protocol rule cites its evidence.

## 1. Design fixation & anchoring

- Jansson & Smith (1991, replicated since): designers shown an example reproduce its features — even its flaws — in "original" work ([recap 2024](https://www.goedel.io/p/design-fixation-why-your-first-idea); [ASME JMD on provided vs self-generated examples](https://asmedigitalcollection.asme.org/mechanicaldesign/article/142/10/101402/1074761/Design-Fixation-From-Initial-Examples-Provided)).
- LLM-era replication: models converge to familiar solution spaces when shown examples ([CHI 2024](https://dl.acm.org/doi/full/10.1145/3613904.3642919)).
- **IDEAFix ([arXiv 2606.00875, 2026](https://arxiv.org/pdf/2606.00875)):** "avoid X" instructions alone = weak (model still orbits the named concept); withholding examples = mixed; what worked = keyword-surprise + incubation-style phase breaks, combined (~15-25% diversity gain); combining defixation mechanisms beats any single one. Explicit "think outside the box" framing gives consistent novelty gains.
- **Barriers to LLM idea diversity ([arXiv 2602.20408, 2026](https://arxiv.org/html/2602.20408)):** LLMs lack knowledge partitioning — first ideas already less diverse than humans' (8.37 vs 14.51 unique categories, p<.001); seeding with human first-ideas gave NO downstream diversity improvement — fixation lives in the generation trajectory, not the starting point.

## 2. Diversity techniques, by measured effect

- **Persona diversity — largest measured lever:** diverse *ordinary* personas beat "creative entrepreneur" personas (24.02 vs 22.98 unique categories vs ~18.45 default); CoT reduces LLM fixation slopes (p<.001); LLM + ordinary personas + CoT beat the human baseline by ~20-26% ([arXiv 2602.20408](https://arxiv.org/html/2602.20408)). Sequential multi-persona beats parallel/collective persona prompting ([Cambridge Design Science](https://www.cambridge.org/core/journals/design-science/article/enhancing-design-concept-diversity-multipersona-prompting-strategies-for-large-language-models/3B346E253508337A4EE899499BE49D9B)).
- **Semantic-direction stratification — best diversity-per-token (2026):** one planning call proposes N broad semantic directions, generation slots distributed across them; outperformed independent parallel sampling, ~2x diversity-per-token vs regeneration methods; the anchorless "stand out from other responses that might be generated" instruction works at ~1.1x token cost with no cross-agent visibility ([arXiv 2605.30150](https://arxiv.org/html/2605.30150), tested on 3 frontier models).
- **Temperature: weak** — brief novelty gain, fast quality decay ([arXiv 2504.09389](https://arxiv.org/html/2504.09389v2)).
- **Overgeneration ceiling:** of 4,000 seed ideas/topic, only ~5% survived semantic dedup at 0.8 cosine ([Si et al., arXiv 2409.04109](https://arxiv.org/html/2409.04109v1) — the 100+-researcher study where AI ideas scored *more novel* than expert ideas, 5.64 vs 4.84/10).
- **Homogenization is the dominant failure mode:** AI-assisted ideas individually better but collectively 10.7% more similar (Doshi & Hauser 2024, [summary](https://www.sciencedirect.com/science/article/pii/S294988212500091X)); creative homogeneity replicates across LLM families ([arXiv 2501.19361](https://arxiv.org/html/2501.19361v1); [ACM C&C 2024](https://dl.acm.org/doi/10.1145/3635636.3656204)).
- Forced-analogy/TRIZ/SCAMPER: works, moderately evidenced ([AutoTRIZ, arXiv 2403.13002](https://arxiv.org/html/2403.13002v2); [Design Science analogical-reasoning benchmark](https://www.cambridge.org/core/journals/design-science/article/analogical-reasoning-with-large-language-models-a-cocreative-framework-and-benchmarking-of-llms-in-design-ideation/0B8149CCF53C45E1E1B78C4CA93E5BDC)).

## 3. Multi-agent architecture

- **Nominal groups beat interacting groups** (classic, heavily replicated — production blocking + evaluation apprehension); structured brainwriting variants can match on quantity ([NGT summary](https://www.mycoted.com/Nominal_Group_Technique); [Springer brainwriting chapter](https://link.springer.com/chapter/10.1007/978-0-85729-224-7_22)).
- **Diversity collapse via structural coupling** in multi-agent LLM systems: agents building sequentially on each other's outputs converge; prompt-only fixes give partial recovery; the real fix is reducing sequential dependency — independent-then-merge ([arXiv 2604.18005, 2026](https://arxiv.org/pdf/2604.18005)).
- Homogeneous-agent debate ≈ martingale: cannot exceed majority-vote accuracy in expectation ([arXiv 2601.19921](https://arxiv.org/pdf/2601.19921); [stance homogenization, arXiv 2606.03032](https://arxiv.org/pdf/2606.03032)). Heterogeneous-persona dialogue can enrich diversity ([SIGDIAL 2025, arXiv 2507.08350](https://arxiv.org/html/2507.08350)) — but only with engineered heterogeneity.
- **Panels systematically select intermediate novelty and discount high novelty** — Criscuolo, Dahlander, Grohsjean & Salter, AMJ 2017 ([journals.aom.org](https://journals.aom.org/doi/10.5465/amj.2014.0861)). Strongly evidenced for human panels; design against the analog in LLM judges.

## 4. Input diets

- Heterogeneous grounding per generator: practitioner-consistent with the structural-coupling and knowledge-partitioning findings, not directly RCT-tested — flagged lower-confidence.
- Retrieval improves factual acceptability substantially; closed-book generation trades factuality for potential novelty → two-stage generate-then-verify (Si et al. pipeline: RAG grounding → overgenerate → dedup → rerank).

## 5. Selection without killing novelty

- Score novelty and feasibility as separate dimensions — they genuinely dissociate ([TrustResearcher, arXiv 2510.20844](https://arxiv.org/pdf/2510.20844); [arXiv 2605.18661](https://arxiv.org/pdf/2605.18661)).
- **LLM-as-judge is unreliable for final idea selection:** best LLM ranker 53.3% pairwise accuracy (human-consistency baseline 56.1%); human experts re-ranking AI ideas chose different tops in 32/49 cases (Si et al.). Judges carry positional/verbosity/self-enhancement biases, worst on subjective/creative tasks ([BiasScope, arXiv 2602.09383](https://arxiv.org/pdf/2602.09383); [survey, arXiv 2511.07448](https://arxiv.org/pdf/2511.07448)).
- Assigned devil's-advocate helps vs groupthink but **authentic minority frames beat performed dissent** (Nemeth line, via [arXiv 2502.06251](https://arxiv.org/html/2502.06251v1); [Lunenburg 2012](http://www.nationalforum.com/Electronic%20Journal%20Volumes/Lunenburg,%20Fred%20C.%20Devil's%20Advocacy%20&%20Dialectical%20Inquiry%20IJSAID%20V14%20N1%202012.pdf)) → prefer architectural diversity over a scripted advocate role.

## Protocol mapping

| Protocol rule | Evidence |
|---|---|
| Independent parallel generation, no debate | §3 nominal groups + structural coupling (strong) |
| Ordinary practitioner personas + CoT | §2 persona study (strong, largest effect) |
| Stage-1 direction stratification | §2 anchorless diversification (strong, 2026, 3 models) |
| "Stand out" line per generator | §2 (strong, cheap) |
| No "avoid X" warnings; quotas at selection instead | §1 IDEAFix (evidenced weak alone) |
| No prior-idea seeding; full quarantine | §1 fixation + no-benefit-from-seeding (strong) |
| Moderate per-generator quantity; budget to dedup/verify | §2 duplication ceiling (strong) |
| Closed-book generators + Stage-4 verification | §4 (moderate) |
| Separate novelty judge; novelty-outlier auto-advance; human final call | §5 + Criscuolo (strong for panels; LLM-judge unreliability measured) |
| Heterogeneous input diets | §4 (practitioner-level, lower confidence) |
