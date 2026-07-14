# Ideation v2 Protocol (T16) — fresh-lens redo of the idea portfolio

**Why this exists (Ravi, 2026-07-15):** the v1 ideation chain (`02_ideas/`) carried accumulating bias — each pass anchored on the previous pass's conclusions and on Zenon's live engagement areas. This protocol regenerates the idea portfolio from scratch with bias controls designed from evidence (research summary: `RESEARCH-BASIS.md` in this folder). `02_ideas/` is **retained untouched** as the coverage-check corpus (same role as the igupta catalog): it is consulted only at Stage 7, never as input.

**Goal:** one file — `02_ideas_v2/ideas.md` — containing the competition idea portfolio: ~80% ideas that earn their keep in the present state of financial-services AI adoption (production slice: competition MVP → client pitch → ~3-week fit into client infrastructure → 1-year engagement POC/P1/P2 → production → handover) and ~20% far-future north stars, every idea carrying BOTH horizons as fields of a single card.

## Non-negotiable bias rules (from the evidence + standing repo rules)

1. **The orchestrator session never generates ideas.** It plans, launches, merges, verifies, and adjudicates. (Generation-trajectory fixation lives in whoever generates; the orchestrator has unavoidable ambient context.)
2. **Quarantine:** no generator or judge agent may read anything in `02_ideas/`, `02_ideas_v2/ideas-raw-*.md` of another agent, the igupta branch, or this folder's outputs from later stages. The orchestrator does not open `02_ideas/` until Stage 7. Do not paste prior idea names/summaries into any prompt.
3. **No "avoid X" instructions** naming prior ideas or engagement domains — evidenced weak (IDEAFix 2026: the model orbits the named concept). Diversity comes from structure (rules 4-6); portfolio balance comes from quotas at selection (Stage 6), not generation-time warnings.
4. **Independent parallel generation only** — no agent sees another's ideas, no debate/discussion stage (nominal-group evidence + structural-coupling diversity collapse, arXiv 2604.18005).
5. **Client mapping is late-stage.** Generators never see the client roster or engagement context. Ideas are problem-space products; clients become a lens at Stage 5.
6. **Every generator gets:** a distinct **ordinary practitioner persona** (evidenced strongest diversity lever — ordinary beats "creative visionary"), an assigned **semantic direction** (Stage 1), chain-of-thought instruction, and the anchorless-diversity line: *"produce ideas that would stand out from what other capable teams would generate for this task."*
7. **Standing repo rules still bind:** synthetic data with seeded ground truth; dated citations for claims (or explicit UNVERIFIED tags for closed-book output, cleared at Stage 4); ≤3 concurrent agents; sonnet default with fable reserved for generation/judging-critical steps and opus for deep scrutiny; RUNSTATE.md manifest in this folder so any stage is resumable.

## Stages

### Stage 1 — Semantic-direction stratification (1 fable agent)

One planning agent produces **10-12 mutually-distant semantic directions** for "where agentic AI can create value in and around financial services." Directions are problem-space regions, not ideas — each ~2 sentences. Instruction: span the full value chain (front/middle/back office; retail, commercial, payments, wealth, market infrastructure), the full stakeholder set (institution, customer, counterparty, regulator, vendor, employee), and the full verb set (do, decide, watch, prove, repair, negotiate, teach, insure...). Directions must be pairwise semantically distant — the agent must self-check and replace any two that are close. Inputs: `01_research/agentic-ai-landscape.md` + own knowledge. **Not** finance.md (its engagement-flavored salience is a bias source at this stage), **not** client files.
Orchestrator validates spread; if ≥2 directions collapse into one theme, send back once.

### Stage 2 — Independent generation (6 generators, ≤3 concurrent; fable)

Each generator gets: 2 assigned directions · 1 ordinary persona · 1 input diet · the standing instructions (rule 6) · a quantity target of **10-12 ideas across its two directions** (dedup ceiling evidence: more sampling ≠ more unique ideas; budget goes to later stages). Generation is **unbounded by competition constraints** (no 6-week/synthetic-data/rubric self-censoring — vision-first, per the standing two-stage decoupling rule); each idea states the problem, who has it, what the agent does, and why it's newly possible now.

| Gen | Persona (ordinary practitioner) | Input diet |
|---|---|---|
| G1 | back-office operations supervisor, 20 years in | `01_research/finance.md` |
| G2 | bank IT/integration engineer who inherits every vendor system | `01_research/agentic-ai-landscape.md` |
| G3 | compliance/audit analyst who signs things nervously | `01_research/finance.md` |
| G4 | small-business owner who banks (customer side) | **closed-book** (no repo files) |
| G5 | fintech product manager who reads funding announcements | `01_research/startup-landscape.md` |
| G6 | contact-centre team lead / front-line servicing supervisor | **closed-book** (no repo files) |

Output: `ideas-raw-G<n>.md` per agent (verbatim, preserved). Personas may be adjusted for coverage, but keep them ordinary, occupational, and mutually distant. Closed-book agents tag every factual claim UNVERIFIED.

### Stage 3 — Mechanical merge + semantic dedup (orchestrator + optionally 1 sonnet/haiku)

Pool all raw ideas; cluster near-duplicates (report the collapse rate — expect heavy); **no synthesis-flattening**: a cluster keeps its most specific member as the card seed, variants noted. Preserve provenance (generator, direction). Apply the content-neutral anti-slop kills only (chatbot-wrapper, dashboard-only, no-artifact-of-record, single-prompt-suffices) — **do not** apply any shape preference (the v1 "assurance-shapes-privileged" lean is retired as a generation-side bias).

### Stage 4 — Verification & freshness (1-2 sonnet agents + web, ≤15 searches each)

For each surviving cluster: verify load-bearing claims (dated sources), clear UNVERIFIED tags from closed-book output, and run the freshness test — name the closest shipped product/funded startup and tag F1/F2/F3 (F3 parks with a note). This stage exists because closed-book generation trades factuality for novelty (evidence: RAG improves factual acceptability; novelty needs the verify stage rather than grounded generation everywhere).

### Stage 5 — Grounding & client mapping (orchestrator, main-session)

Now — and only now — read `01_research/client-ai-state-map.md` + `00_sources/zenon-client-context.md`. For each survivor add: the **production slice** (3-week-fit story: integration surface, runs-on-what, HITL, the number that moves; 1-year engagement arc POC→P1→P2→handover; competition-MVP slice with sizing per `02_ideas/METHOD.md` sizing table — the sizing model and anti-slop tests carry over as content-neutral machinery), the **applicability line** (anchor client + ≥2 transfers; single-client caps impact at 3), and the **vision arc** kept from generation. Ideas with no honest production slice are tagged HORIZON (kept — they are the 20%).

### Stage 6 — Judging with novelty protection (3 independent judges + orchestrator)

Independent contexts, randomized presentation order, integer scores with per-score citations (per `02_ideas/RUBRIC.md`, which carries over):
- **Novelty judge (fable):** scores novelty/originality ONLY — no feasibility contamination.
- **Buyer judge (fable):** would a financial institution pay for the 1-year engagement this quarter, given its adoption state?
- **Architect judge (opus):** MVP buildability, 3-week-fit credibility, demo strength.

Selection rules: novelty and feasibility are **never averaged into one number**; the **top-3 novelty outliers auto-advance to the human shortlist regardless of aggregate score** (panels systematically under-select high novelty — Criscuolo et al. 2017); one credible kill objection forces rework, never averaged away; **portfolio quota at selection:** the final list is ~80% production-track / ~20% horizon, and ideas in domains where Zenon already has active engagements are capped at ~1/3 of the shortlist (balance enforced here, not by generation-time warnings). LLM judging is screening, not selection: **the final call is Ravi's.**

### Stage 7 — Coverage cross-check (orchestrator; only after Stage 6 shortlist exists)

Open `02_ideas/` (backlog, north-stars, grounded-track, production-track) and — after Round-1 lock only — the igupta catalog. Question: *what did the fresh pass miss that prior work had, and what did it independently reproduce?* Reproductions are convergence signal (note them); misses are flagged for Ravi to decide import — anything imported is tagged `legacy-import`, never silently merged. Harvest prior verification work (freshness scans, fact-checks, withdrawn-claims) for any overlapping idea.

### Stage 8 — Deliverable & stop

`02_ideas_v2/ideas.md`: single file, one card per idea — name · ELI5 · problem/persona · vision arc · production slice (3-week fit, engagement arc, MVP sizing) · applicability · freshness tag · novelty/buyer/architect scores + flags · provenance (generator/direction) · tier (PRODUCTION / HORIZON / legacy-import). Plus the shortlist table and the Stage-7 coverage report. Update `RUNSTATE.md`, INDEX, worklogs, board (T16 → REVIEW); commit; present the shortlist to Ravi and **stop for the lock call**.

## Kickoff prompt for the fresh conversation (paste as-is)

> Read `CLAUDE.md`, then `02_ideas_v2/PROTOCOL.md`, and execute the protocol exactly. Skip the usual INDEX.md reading step and do not open anything in `02_ideas/` or on the igupta branch until the stage that explicitly calls for it — this is a deliberate bias quarantine; the protocol overrides the default reading order. You are the orchestrator and judge only: you never generate ideas yourself. Maintain `02_ideas_v2/RUNSTATE.md` so any stage is resumable. Work stage by stage, committing after each stage lands. At the end, present the shortlist and stop for Ravi's lock call.
