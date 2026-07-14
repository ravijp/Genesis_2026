# T7 Verification Pack — Human Review Checklist (assembled 2026-07-14)

One consolidated, prioritized checklist for the T7 human review pass (Ravi/Ishant/Namit). Collates every brief's open-verification items, the ideation weakest-claims, cross-brief discrepancies found during the 2026-07-14 scrutiny pass, and the north-star red-team's evidence gaps. **Work top-down: Tier 1 items are load-bearing for likely pitches; a wrong one sinks a deck.** Check the box, note the verdict inline, and correct the source brief in the same commit.

## Tier 1 — load-bearing for likely pitches (verify before anything enters a deck)

- [ ] **Mills Review "agentic finance" wording** — pull the FCA PDF directly and confirm the recommendation's exact language before it anchors N-001 or any collections pitch. (finance.md §Open items)
- [ ] **x402 transaction volume — cross-brief discrepancy**: agentic-ai-landscape.md §3 says "165M+ agent txns by May 2026"; startup-landscape.md §3 says ">100M payments since May 2025". Resolve to a primary (Chainalysis / x402 Foundation) and fix the losing brief + R-024 + N-002. Until then use the conservative >100M.
- [ ] **Basis round lead — cross-brief discrepancy**: startup-landscape.md says a16z-led ($100M @ $1.15B, w/ Tiger, Sequoia, YC); lessons-from-prior-work.md fact-check says **Accel-led** (via Businesswire). One of our two briefs is wrong; resolve via the primary press release.
- [ ] **UiPath / Automation Anywhere / Blue Prism agentic-computer-use status (2025-26)** — never researched in any brief; N-005's F2 freshness claim is "one incumbent press release away from collapsing to F3" (red-team). Hard gate before N-005 is carded.
- [ ] **Loyalty/points-fraud dollar-loss figure** — no dollar cost for loyalty fraud exists anywhere in our evidence; N-003's impact story needs one primary-sourced number (or the pitch leads with offer-abuse avoidance only). (red-team, N-003)
- [ ] **GC ruling: is an eval/certification product Track A or Track C?** — written answer required before N-006 can be carded (kickoff lists "eval frameworks" under Track C). Fold into T8's questions.
- [ ] **R-028 suitability-assurance anchor** — asserted "finance.md wealth section covers Reg BI/suitability" is FALSE as written (the wealth section covers Debrief/AskResearchGPT/MCP only). Re-anchor with real Reg-BI supervision evidence or park R-028. (backlog weakest-claims #1)
- [ ] **Salient/Kastle 20-30% payment lift, Vantaca $300M @ $1.25B, HUMAN Security 7,851%, Visa fee ladder, Taktile $110M, Klarna reversal** — the agent-cited stats backing the top clusters, all relayed from briefs marked unreviewed; spot-check each against its primary before any appears on a slide. (backlog weakest-claims #3)

## Tier 2 — brief hygiene (correct-the-record items)

- [ ] **KYC cost figures** — deepidv is a KYC vendor self-computing averages; pull LexisNexis Risk Solutions "True Cost of Compliance" as the independent replacement. (finance.md)
- [ ] **Amex ACE Developer Kit detail** — primary newsroom page was thin on fetch; corroborated mainly via secondary coverage. Re-fetch primary before N-002 cites the protection program's mechanics. (finance.md)
- [ ] **Pacific Premier Bank vs. Columbia Bank naming** (possible 2025-26 rebrand/merger) — verify before naming in any HOA competitive table. (finance.md)
- [ ] **InDebted CEO search** — single aggregator mention; check InDebted's press room. (finance.md)
- [ ] **HOA national delinquency rate** — no primary figure found; the FCAR Statistical Review PDF may contain one. (finance.md)
- [ ] **"Barclays research" vulnerable-customer AI quote** — circulates in aggregators, untraceable to a Barclays primary. **Do NOT use.** (finance.md)
- [ ] **pharma.md unverified block** — pharma.md was not fully adversarially verified; the flagged items stand: "40% PV capacity reclaimed," "73% of orgs deploying agentic AI," "19 of top 20 pharma" vendor stats, Roche 50%-efficiency target, Novartis AWS/Accenture metrics — all SEO/self-replicating or single-sourced. Do not cite without independent confirmation. Additionally spot-check the 3-4 claims a pitch would lean on (Purolea warning letter; BMS-Anthropic scope; Veeva Falcon MLR date; FDA-EMA principles date).
- [ ] **media.md do-not-cite list** — three fabricated claims caught in verification: a "Big Five joint AI framework," Getty "Content Genome," BMI "96% ML accuracy." Confirm they stay quarantined; also Whip Media's "Bedrock/Claude" tech detail and CES-2026 showing are unverified.
- [ ] **Agentforce ARR/deal counts, Sierra/Glean ARR** — secondary/analyst-sourced in both landscape briefs; treat as directional on any slide, or re-source. (agentic-ai-landscape.md §6 caveat)
- [ ] **R-041's Invesco SEC-Marketing-Rule variant** — pattern-transfer with no direct brief evidence; needs a research spot-check before it can be revived as a card. (backlog weakest-claims #2)

## Tier 3 — context/nice-to-verify

- [ ] **METR TH1.1 figures** (~5.3 hr @50%, doubling ~89 days P50) — already corrected once from SEO noise; re-confirm against metr.org if used in a pitch framing. (landscape §5)
- [ ] **EU AI Act dates** — Art-50 transparency 2026-08-02 (NOT postponed) vs. high-risk 2027-12-02/2028-08-02 (postponed) — re-verify the day either enters a deck; this hook has moved once already. (finance.md §3, PLAN risk table)
- [ ] **Gretel/NVIDIA open-source status** — lessons file notes NVIDIA re-open-sourced Gretel's synthesizers into NeMo in 2026; verify current state before any "build-our-own-synthetic-data" argument. (lessons §6)
- [ ] **DJ × Perplexity docket** — pretrial conference was scheduled for 2026-07-14 (today, per media.md); check the outcome before any DJ pitch cites litigation posture.

## Standing rules while reviewing (from METHOD/PLAN)

Time-sensitive hooks get re-verified the day they enter a pitch; every corrected figure updates the source brief in the same commit; "not found in a time-boxed search" ≠ "confirmed absent" — label accordingly.
