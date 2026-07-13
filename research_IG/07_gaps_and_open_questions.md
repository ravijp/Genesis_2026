# Gaps & Open Questions

*Synthesis date: 13 Jul 2026 · Companion to [06_idea_catalog.md](06_idea_catalog.md). What the sweep couldn't nail down, the tensions it had to resolve, and where a focused deeper dive would most change the decision.*

## TL;DR

The research is strong enough to shortlist from, but three things need a verification pass before anything goes into the Weeks 2–3 brief as a load-bearing claim: (1) the **fraud/AML dollar economics** lean heavily on a single vendor blog (FluxForce); (2) several **funding and vendor-market-size figures** are unverified or from secondary aggregators; and (3) the **regulatory dates/scope** that make the timing ideas (I14, I18, I25) compelling should be confirmed against primary regulator text. None of this changes the *ranking* — it changes which numbers are safe to quote to a judge. Strategically, the sweep **confirms rather than displaces I1**; its real contribution is a lower-risk I1 hedge (I13) and two genuinely fresh, well-timed plays (I14, I15).

---

## 1. What the research couldn't answer (verify before citing)

**Single-source or vendor-sourced quantifications (highest priority to corroborate):**
- **Fraud/AML false-positive economics** — the headline "$510K–850K/month wasted," "$6–50/alert," "92–97% false positives," "~25 analyst-hours/day" all trace to **FluxForce** (a vendor with a product to sell). The *direction* is corroborated by PwC/LexisNexis/Celent at the macro level ($61B US/Canada FCC cost; ~$190B global), but the *per-alert unit economics* should be re-sourced to a neutral party (PwC, LexisNexis True Cost of Compliance, or a regulator) before appearing in a pitch. Affects I36, I37, I24, I30.
- **DORA steady-state cost (£350K–£700K/mid-size entity)** — explicitly a vendor (CrunchSpark) illustrative estimate, not official. Affects I25.
- **"70% of FIs lost clients to slow onboarding"** and the 49-day EMEA figure — single-source (Fenergo, who sells onboarding software). Strong narrative, but flag the source's interest. Affects I34.
- **Covenant "200+ → <30 hours/month"** — a single Aloan.ai case study; treat as illustrative, not a benchmark. Affects I16.

**Unverified funding / market figures (noted as such in the workstream files):**
- Arva AI (~$3M), KredosAi ($7M) — from secondary aggregators, not primary announcements.
- Corlytics and Regology funding scale — not independently verified; Regology's "AI Compliance Agents" is marketing copy of unproven technical depth.
- Regulatory-reporting vendor market share (AxiomSL/Adenza, Wolters Kluwer OneSumX, Vermeg) — named from domain knowledge, specific share/funding **unverified**. Directly affects the white-space claim for **I11** (the top idea) — see §3.
- Precedence Research market sizing ($1.79B→$6.5B) and CB Insights "200+ fraud companies" — secondary market-research aggregators; fine as directional color, not as hard facts.

**Thinly-sourced areas:**
- **Academic existence-proofs for regtech NLP** (ComplianceNLP arXiv 2604.23585, RAGulating Compliance 2508.09893) underpin I19's feasibility. arXiv IDs and F1 numbers should be confirmed to exist and say what's claimed before leaning on "87.7 F1 gap detection" in a feasibility slide.
- **BlackRock "Aladdin Wealth Auto Commentary" (Jun 2026)** cited for I23 has no linked primary source in WS5 — confirm it shipped before using it as a competitive precedent.
- **The exact per-idea competitor set** — for most ideas the sweep found the *category* incumbents but did not confirm that none of them ships the specific agentic+explainable slice proposed. "No funded player found" means "not found in a time-boxed sweep," not "confirmed absent."

## 2. Contradictions & tensions across workstreams — and how the catalog resolved them

1. **WS3's fraud/AML "$ story" vs WS1's "it's crowded" verdict.** WS3 found the biggest quantified labor sink in all of banking (fraud/AML triage); WS1 found the core workflow is packed with incumbents (NICE, FIS+Anthropic, Oracle) and unicorns (Sardine, Norm AI, Quantifind, Taktile). **Resolved by** scoring the head-on core-workflow ideas (I36 Fraud, I37 AML/SAR) *down* on feasibility (regulated-decisioning path-to-production is weak for a 2–3 person team) and originality (crowded) — they land at 3.45 and are explicitly *not* `[Recommended]` despite the huge $ — while elevating the two differentiated moves: **I24** (the underserved <$10B-bank tier) and **I14** (the assurance layer *above* everyone's agents). The dollar story stays useful as *evidence for the brief*; it does not justify a head-on build.

2. **Raw workstream tags (33 "Recommended") vs the re-scored 12.** The five agents applied visibly different strictness — WS2 tagged 7/10, WS3 only 3/13 — so a raw union would have been meaningless. **Resolved by** discarding all five agents' scores and re-deriving ZI/TD/FR/OR/PR on one scale against fixed anchors (I1 4.60 / I2 4.50 / I3 4.35), then applying the `[Recommended]` rule (all hard filters + ≥4 on each of ZI/TD/FR) strictly. Result: 12 Recommended, dominated by Zenon-DNA reconciliation/forecasting/credit ideas — the intended shrink.

3. **Regtech enthusiasm vs WS4's own "secondary wedge" verdict.** WS4 generated many high-scoring regtech ideas but its own synthesis concluded regtech is *secondary* to Zenon's core domains (no named regtech client; heavily consolidated vendor market — CUBE's 5+ acquisitions, Big-4 billions). **Resolved by** capping regtech Zenon-impact at 3 wherever Zenon genuinely can't name a client and the $ is soft (I19, I20, I25, I26, I38, I41) — so they score 3.40–4.00 (valuable, not primary) — with the single exception of **I18**, whose dated 2 Aug 2026 AI-Act deadline + Barclays explainability DNA justify ZI 4 and a `[Recommended]` tag. This matches WS4's explicit recommendation to carry *one* regtech idea (WS4-F/I18) as a portfolio hedge, not the headline.

4. **Anthropic's free finance templates (WS2) vs the reconciliation ideas.** Anthropic shipping a free GL-reconciler/month-end-closer/KYC-screener (May 2026) commoditizes generic reconciliation. **Resolved by** docking technical-depth on the *generic* recon idea (I27 Month-End Close, TD 3, OR 2 → 3.70, not Recommended) while keeping the *domain-specific* recon ideas high (I11 Regulatory-Reporting, I12 Payments/Settlement) because their proprietary semantics — regulatory-return taxonomies, nostro/vostro and rail-specific break logic — are exactly what the free template lacks. The lesson is baked into scoring: reconciliation only scores well when a visibly proprietary domain layer sits on top.

5. **`[Align with Zenon]` is nearly universal (33/34) — is the tag meaningful?** Because the whole sweep was constrained to finance + Zenon domains, almost everything aligns, so the tag mostly confirms the sweep stayed on-brief rather than discriminating between ideas. **Treat `[Recommended]` (12/34) as the discriminating signal**, and read `[Align with Zenon]` as a floor, not a distinction. (The one un-aligned idea, I41 policy-harmonization, is a useful marker of where the sweep drifted off Zenon's DNA.)

## 3. Deeper-dive candidates (where a focused pass would most change the decision)

These are the ideas whose *rank could move materially* with one more day of targeted research. Each has a specific question to answer.

1. **I11 · Regulatory-Reporting Reconciliation (top-ranked).** Its 4.35 and white-space claim rest on the *unverified* assertion that incumbents (AxiomSL/Adenza, Wolters Kluwer OneSumX, Vermeg) do report *production* but leave explainable-break-reconciliation open. **Question:** Do these incumbents already ship an agentic/explainable GL-to-return break investigator? If yes, I11 drops toward I27's fate; if no, it's confirmed as the strongest pick. *This is the single highest-value verification in the sweep.*

2. **I14 · MRM-for-Agents (most original core-domain play).** **Question:** Does SR 26-2 (Apr 2026) actually exclude agentic AI in the wording claimed, and do Credo AI / Patronus / Galileo already sell a *banking-specific, rules+ML-explainable* version? Confirm the regulatory-vacuum framing against the primary Fed/OCC letter and check the governance-vendor landscape one level deeper than this sweep went.

3. **I15 · AI Content-Licensing Royalty Reconciliation (highest originality).** **Question:** Do publishers currently audit usage-based AI-licensing royalties at all, and is there a budget owner for it? The idea's ZI hinges on this being a real, felt pain at a Dow-Jones-like client — not just a plausible one. A few practitioner conversations would settle it.

4. **Fraud/AML economics (I36/I37, and the brief's headline $ chart).** **Question:** What are the defensible per-alert cost and false-positive figures from a *neutral* primary source (PwC, LexisNexis, a regulator)? Needed whether or not fraud is picked, because the numbers are the most quotable "cost of doing nothing" evidence in the whole sweep and currently rest on one vendor.

5. **I18 · Model-Risk & EU-AI-Act Dossier (best-dated hook).** **Question:** Confirm exactly which Annex III obligations bind credit-scoring/AML/fraud models on 2 Aug 2026, and that the date hasn't shifted. The entire pitch is the deadline; if it's firm and the obligations are as described, I18 is a very strong portfolio hedge.

## 4. Implications for the incumbent pick

**Nothing in this sweep beats I1 Forecast Copilot (4.60).** The 34 new ideas top out at 4.35 (I11), which *ties* I3 — so the honest read is that the sweep **validates the existing shortlist rather than overturning it.** Three things the team should nonetheless look at:

- **I13 (Forecast Assurance / Variance Sentinel, 4.25) is a lower-risk I1.** Same Dow-Jones story, but framed as an independent auditor *over* a client's existing FP&A tool rather than a replacement forecaster — a smaller integration surface, an easier 6-week build (FR 5), and a cleaner buying motion (no need to rip out Anaplan). If the team's risk appetite is lower than I1 demands, I13 is the hedge.
- **I11 and I12 give I3 (Data-Trust Agent) its best verticals.** The reconciliation cluster confirms that I3's real decision is *which vertical to demo*, and regulatory-reporting (I11) and payments/settlement (I12) are the two highest-value, best-anchored answers — both stronger than the generic close-reconciliation (I27) that the free Anthropic template now commoditizes.
- **I14 and I15 are the freshest originality plays** if the team wants to differentiate rather than play the safe forecasting/reconciliation core — I14 rides a dated regulatory vacuum, I15 a brand-new pain on a direct Dow-Jones anchor. Both are genuine finals-differentiators on the 15% originality axis without sacrificing the 75% core.
- **I8 (Synthetic Data Studio) still complements any pick.** WS2's finding that Gretel's OSS is gone (NVIDIA, Feb 2026) and Vanna is archived (Mar 2026) *raises* the value of Zenon owning a proprietary synthetic-data capability — reinforcing the existing recommendation to build a scoped I8 as the data engine behind whichever flagship is chosen.

**Net:** keep I1 as the primary, treat I13 as its lower-risk sibling, use I11/I12 to sharpen I3 if that's the backup, and hold I14/I15 as the originality upgrade. No re-litigation of the full shortlist is warranted on this evidence.
