# ACTION ITEMS — resume when quota is available

Session 2026-07-14 hit usage limits mid-research-fleet. This file is the resume point.

## ⚠️ Token discipline for next session (learned the hard way)

- Use **sonnet or haiku at LOW effort** for remaining research; opus only if Ravi explicitly approves.
- Every agent prompt MUST include: **"Do NOT spawn sub-agents."** (The media agent recursively spawned 10+ children and consumed most of the budget; the landscape agent alone used ~437k tokens.)
- Cap searches per agent (≤12) and require a single output file, no interim reporting.
- Completed-agent raw transcripts from this session exist under the session tasks dir (`...\Temp\claude\...\82179033-...\tasks\*.output`) but are JSONL and context-heavy — prefer the digests already saved in `01_research/`.

## P0 — Finance brief (top-priority domain; agent died before writing the file)

Re-run as **one sonnet agent, low effort, no sub-agents**, output `01_research/finance.md`. Scope (condensed from the original prompt — full version in PLAN/kickoff context):
1. Named bank/payments agentic deployments (JPM, Goldman, Morgan Stanley, Capital One, Visa Intelligent Commerce, Mastercard Agent Pay — status July 2026, numbers)
2. Ops value-chain nodes with Zenon hooks: **collections & recoveries (Barclays, UK FCA/Consumer Duty)**, consumer lending servicing (Lendmark), SMB virtual RM + **HOA banking (WAB)**, KYC/AML & screening, disputes, wealth (MS/Invesco), payroll money-ops (ADP), loyalty (ampliFI) — pain metrics, vendors, 6-week demo credibility per node
3. Regulatory posture 2026 (Fed/OCC/CFPB, EU AI Act — note high-risk deadline moved to 2027-12-02; FCA) framed as what makes a demo credible
4. Public ROI benchmarks (cost-to-collect, cost per KYC review, servicing call costs)
Note: much of the deployment/data-provider layer is ALREADY captured in `01_research/media-findings-digest.md` (Moody's/S&P/FactSet/LSEG agentic products, compliance-vendor map) — tell the agent to read it first and not duplicate.

## P0 — Retail brief completion

`retail-agentic-commerce.md` (salvaged) covers protocols/threat numbers. One **sonnet low, no sub-agents** agent for the remainder, output appended or `01_research/retail-internal-ops.md`:
retailer-internal agent deployments (Walmart Sparky/Wallaby, Home Depot Magic Apron, Lowe's Mylow, Target, Sephora), merchandising/pricing/markdown + inventory agents, customer care/returns, **Kohl's 2025-26 situation** and where an agentic pilot plausibly helps, retail agent-startup map.

## P1 — Verify pharma.md completeness

`pharma.md` was written moments before its agent died — skim for truncation (does it end with a Sources section + use-case seeds?). Patch gaps with a small haiku pass if needed.

## P1 — Media: use the digest, skip full re-research

All media child research COMPLETED; essentials preserved in `01_research/media-findings-digest.md`. A full `media.md` synthesis is **P3/optional** — the digest is sufficient for ideation. Do not re-run media research.

## P2 — Ideation prep (cheap)

1. Haiku pass: collate all "Candidate use-case seeds" sections from `01_research/*.md` into `02_ideas/backlog.md` (verbatim collation, no invention).
2. Then Phase 2 divergence sprint per `02_ideas/METHOD.md` (3 ideation agents — sonnet is fine — + Ravi + Claude; igupta catalog only AFTER Round-1 lock).

## P3 — Deferred / nice-to-have (log only, run on demand)

- Full media.md synthesis from digest + task transcripts
- Deep-dive: ADP/HCM payroll-exception vertical; Dow Jones Risk & Compliance white space (no agentic product as of Jul 2026 — strong originality angle)
- Fix cosmetic markdown-lint warnings (MD060/MD022) across docs
- `rtk` is referenced in global CLAUDE.md but not installed — install or keep ignoring

## Open questions for Ravi (blocking idea targeting)

1. HNB = Huntington or Hatton National Bank?
2. Team roster (2–3 people) and skills?
3. GC status: is our validation checkpoint handled? API budget/AWS access?
4. Confirm ADP + Lendmark are fair game as idea targets.
