# METHOD — From Evidence to 3 Competition-Grade Ideas

## Principles (several learned from the prior attempt's autopsy)

1. **Research before ideation.** Ideas are generated FROM the evidence base, never from model priors. (The prior attempt did the inverse; its own later research contradicted its shortlist.)
2. **Traceability.** Every idea cites the research finding(s) that motivate it.
3. **Assurance beats replacement.** An agent that *audits/verifies* an existing human workflow ("check the forecast" not "be the forecaster") is usually the same client story with a smaller, lower-risk build and an easier trust story. Prefer this shape when sizing is tight.
4. **Proprietary domain layer.** Free templates (Anthropic/OpenAI cookbooks, OSS agent demos) define the commodity floor. Every idea must name the domain logic — semantics, policies, calculations, regulatory constraints — that a generic template cannot replicate. That layer IS the pitch.
5. **No false precision.** Integer scores with an evidence line and a confidence tag; never decimal theater.
6. **Unknowns stay visible.** Write "UNKNOWN — get from [person/source]", never plausible filler.
7. **Anchoring quarantine.** The igupta idea catalog (34 ideas) is consulted ONLY after our Round-1 list locks — as an overlap/coverage cross-check, never as a seed.

## Pipeline

```
Stage 0            Stage 1              Stage 2            Stage 3             Stage 4
Evidence base  →   Divergence 50+   →   Anti-slop gate  →  Idea cards top~20 → Score → top 10
(01_research)      (matrix + agents)    (kill/rework)      (full template)     diligence → TOP 3
```

## Stage 1 — Divergence to 50+

**Matrix sweep:** value-chain nodes (rows) × agentic patterns (columns). Nodes come from `00_sources/zenon-client-context.md` + the research briefs' seed sections. Patterns:

| # | Pattern | Essence |
|---|---|---|
| P1 | Autonomous case worker | Owns a case end-to-end: gathers, decides, acts, escalates |
| P2 | Multi-agent operations cell | Specialist agents + coordinator running one workflow |
| P3 | Agentic research/diligence | Multi-source investigation → verified, cited brief |
| P4 | **Verifier / assurance agent** | Audits human or system output: QC, compliance, reconciliation *(privileged — best wow-per-build-week ratio)* |
| P5 | Ambient monitor | Watches streams, intervenes on triggers, escalates with evidence |
| P6 | Cross-party coordinator | Negotiates/coordinates between orgs or parties (customer↔bank, merchant↔network) |
| P7 | Self-improving ops loop | Evals in production drive prompt/policy updates with HITL |
| P8 | Legacy workflow modernizer | Agent wraps a manual SOP / green-screen process into a governed API |

**Protocol:** 3 independent ideation agents with distinct lenses — (a) operator-pain-first, (b) startup-thesis-first, (c) demo-first — plus me plus Ravi. No shared context between agents. Each idea is one line: `[node] × [pattern] × [client]: the 10-second story` + evidence link. Target: **≥50 pre-dedup, ≥50% finance.** Then dedupe/cluster.

**Round-1 lock**, then and only then: igupta catalog cross-check (what did we both find = probably obvious; what did only he find = evaluate fresh; what did only we find = potential originality).

## Stage 2 — Anti-slop gate

**Auto-kill list** (no rework, just kill): generic RAG chatbot over documents · "chat with your X" · meeting/email summarizer · generic customer-support bot · code assistant · anything whose demo is a text box answering questions.

**Ten tests — all must pass:**
1. Names the workflow it changes and the persona who does it today (title, team)
2. Produces an **artifact of record** (memo, case decision, filing, updated system state) — not just an answer
3. Touches a system of record (real or faithfully simulated)
4. **Needs agency:** multi-step + tool use + decisions under uncertainty; a single prompt demonstrably can't do it
5. Verification story: how does anyone know the output is right? (deterministic checks, judge agents, HITL gates, evals)
6. Proprietary domain layer named explicitly
7. Anchored to ≥1 real deployment / funded startup / regulation from `01_research/`
8. SME nod test: a practitioner would say "yes, that's the real pain"
9. Demo moment describable in one sentence
10. Differentiation line vs 2 named alternatives (vendor, startup, or status quo)

## Stage 3 — Idea cards (top ~20)

```markdown
### IDEA-NNN — <name>
- One-liner:
- Client hook & value-chain node:
- Persona & workflow today (volumes/costs; UNKNOWN — get from [X] where missing):
- Agentic core: pattern(s) · autonomy level · tools · HITL gates
- Verification & evals plan:
- Synthetic data plan (incl. seeded ground truth):
- Demo moment (the 30 seconds that wins):
- Differentiation vs 2 named alternatives:
- Evidence anchors:
- Build size: agents [S/M/L] · tools [S/M/L] · UI [S/M/L] · data [S/M/L] · evals [S/M/L] → overall
- Pre-mortem headline (the most likely way this dies):
- Gate: 10/10 with notes
```

## Stage 4 — Scoring & diligence

Score per `RUBRIC.md`: 3 independent opus judge agents (client-buyer lens · CTO lens · competition-judge lens; no shared context) + Ravi + me. Integer 1–5 per axis + one-line evidence + confidence H/M/L. Axis spread >2 → adjudicate with evidence, never average away.
Top 10 → diligence sprints: competitor scan, synthetic-data feasibility spike, sizing check. Top 3 → pre-mortem, 5-minute demo script, build plan. Ravi picks the build + a fallback.

## Sizing model (the ≤6-week reality test)

| Axis | S | M | L |
|---|---|---|---|
| Agent roles | 1 | 2–3 | 4+ |
| Tools/integrations (incl. MCP servers) | ≤3 | 4–6 | 7+ |
| UI surface | CLI/notebook | single dashboard | multi-view app |
| Synthetic data | 1 corpus | 2–3 linked corpora | full simulation |
| Eval harness | golden set | + auto-scoring | + adversarial suite |

**Rule:** 2–3 people × 6 weeks supports at most **one L and two M axes**. Bigger → descope or kill. Sprint shape: wk 1–2 walking skeleton end-to-end · wk 3–4 depth + evals · wk 5 polish + metrics · wk 6 demo hardening + one-pagers. (Assurance-shaped ideas usually land S/M — that's why P4 is privileged.)

## Synthetic data playbook (competition rule: synthetic/anonymized only)

1. **Seed ground truth:** plant N known anomalies/violations/target cases in generated data so we can report precision/recall to the AI judge. The demo's "agent caught #17" moment comes from here.
2. **Realism:** domain-calibrated distributions (amounts, dates, statuses), correlated fields, edge cases, natural noise (typos, missing values, format drift).
3. **Scale:** large enough that the agent's work is non-trivial (100s–1000s of records), small enough to demo live.
4. **Provenance one-pager:** how generated, what's seeded, what a client swaps in for production — this doubles as path-to-production evidence.
5. Tooling: LLM-generated narratives for texture; Faker/SDV-style generators via the uv env for structure.

## Gaps companion

Every stage output ends with a **"Weakest claims & how to verify"** section. Time-sensitive hooks (deadlines, vendor stats, funding rounds) are re-verified the day they enter a pitch.
