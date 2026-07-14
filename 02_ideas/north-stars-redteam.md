# North-Star Red-Team — Verbatim Verdicts + Adjudication (2026-07-14)

Two adversarial agents, adversarial by instruction, evidence-base-only (no web), non-independent of the evidence base but independent of the author. Agent E = freshness/narrowness attack; Agent F = feasibility/depth/demo attack. Full verdicts below, then the session's adjudication (what was accepted into `north-stars.md`, what was rejected and why).

## Adjudication summary (read this first)

| Concept | E (freshness) | F (feasibility/demo) | Accepted outcome |
|---|---|---|---|
| N-001 Decision Assurance Stack | WEAKENED | BORDERLINE / FRAGILE | **Revised**: feature-to-platform pitch vs Salient UDAAP adopted; 88%-security stat removed from why-now (category mismatch); slice descoped — counterfactual replay pre-computed for demo, blocking gate = deterministic-checks-only (resolves the <500ms contradiction); judge-calibration plan made explicit (~150 team labels, agreement stats published) |
| N-002 Mandate Fabric | HOLDS | BORDERLINE / FRAGILE | **Revised**: x402 figure double-cited (landscape 165M vs startup >100M — cross-brief discrepancy → T7); demo scope pinned to 2 live protocol parsers (AP2 + Agentic Tokens) with ACP/TAP as narrated adapters; mandate-scope ground truth = designed seed labels + human-escalation threshold |
| N-003 Loyalty as a Financial System | WEAKENED | BORDERLINE / STAGEABLE (ranked most buildable) | **Revised**: F-tier corrected to F2 (bundle-F1 claim dropped — tier-laundering charge accepted); Capillary/Kognitiv/Bloomreach/Eagle Eye/Salesforce vendor row now cited with explicit differentiation; attacker fleet constrained to 3-4 named exploit classes; no loyalty-fraud dollar figure exists in evidence → T7 item |
| N-004 Exception-Operations Platform | WEAKENED | BORDERLINE / FRAGILE | **Revised**: F1-platform claim downgraded to F2-with-demo-mechanic (platform earned, not asserted); pharma citation relabeled as cross-domain analogy; promotion statistics specified (min-n + CI lower bound, CUSUM-style demotion; seeded-stream determinism disclosed on stage); data axis re-sized to M, UI trimmed to S |
| N-005 Zero-Integration Autonomy | HOLDS | BORDERLINE / FRAGILE | **Revised**: sizing honesty — fake legacy terminal counted as UI **L** (1L+1M, still fits ceiling); pass^k-on-own-terminal dry-run measurement committed (20 runs, failure rate published); UiPath/Automation-Anywhere agentic-RPA verification → T7 hard item |
| N-006 Agent Underwriting Bureau | WEAKENED | **BREAKS on track fit** / FRAGILE | **Conditional**: GC written Track-A confirmation is now a hard precondition before carding; evals axis honestly counted L (at ceiling, zero slack — noted); reproducibility re-run pinned to deterministic scoring path |
| N-007 Agent-Ready Enterprise | **REFUTED** | BORDERLINE / FRAGILE | **Parked for competition** (retained as Zenon-asset concept). Both its own pre-mortem and both red-teamers converge: nearest to the commodity floor, semantic-layer verification story missing. Not in the Track-A scoring pool. |

**Red-team claims rejected by the session (with evidence):**

1. Agent E called N-002's "165M+ agent transactions" an *invented* figure. Wrong — `agentic-ai-landscape.md` §3 states "165M+ agent txns by May 2026" for x402. E only cross-checked `startup-landscape.md` (">100M payments since May 2025"). The correct finding is a **cross-brief discrepancy**, now logged for T7. Both figures are now cited in N-002.
2. Agent E's N-004 attack ("pharma citation transplanted across verticals") is accepted directionally, but the citation was labeled as pattern evidence, not domain evidence; fixed by explicit relabeling rather than deletion.
3. Agent F's N-001 sizing attack ("5M") partially double-counts: ledger + packet generator are conventional plumbing, not M-tier integrations. Accepted in substance though — the slice was descoped (replay pre-computed, gate deterministic-only) rather than re-argued.

**Set-level blind spots both agents surfaced (accepted, standing rules):**

- *Cross-file citation discipline:* every concept's freshness claim must be checked against ALL briefs, not just its anchor brief (N-003 missed the retail-internal-ops vendor row).
- *Platform claims need a transfer artifact:* any concept claiming platform/infrastructure status must carry at least a paper adapter-sketch for a second instance ("show me the second queue"), or soften the claim at carding.
- *Self-flagging is not mitigation:* a pre-mortem that says "this may not belong here" is a verdict — N-007 parked, N-006 made conditional, per exactly that rule.

---

## Agent E — freshness/narrowness attack (verbatim)

## N-001 — The Decision Assurance Stack

**Verdict: WEAKENED**

- **STALE, partially.** The concept's own text admits Salient ships "automated UDAAP monitoring of both AI and human agents" as a feature (finance.md §2a, "Salient... named customers Westlake Financial, Exeter Finance, Consumer Portfolio Services... automated UDAAP monitoring of both AI and human agents"). N-001 tries to wave this off as "a feature of its own collector, not an independent layer over heterogeneous agents" (north-stars.md line 30), but nothing in finance.md or startup-landscape.md establishes that framework-agnostic ingestion is actually hard to bolt on — that's asserted, not evidenced. A judge could reasonably see this as "Salient's UDAAP monitor, generalized" rather than a new category.
- **NARROW-IN-A-TRENCH-COAT.** Strip the "supervision layer for any agent" framing and the competition slice is: ingest one synthetic collections agent's traces, run a rules engine + LLM judge against a seeded-violation corpus, produce a report. That is functionally a compliance-monitoring dashboard with an LLM judge bolted on — the very shape the pre-mortem itself flags as the risk ("Reads as 'a compliance dashboard' if the demo leads with reports," line 35). The tell is that the demo's own escape hatch is "audit a black-box agent... not our own" — an admission that the natural default build *is* indistinguishable from a single-workflow compliance tool.
- **EVIDENCE ABUSE.** The applicability line "88% of orgs reported agent security incidents (landscape §7)" is used to support the case for a *decision-conduct* supervision product, but agentic-ai-landscape.md §7 is about prompt-injection/security incidents ("Security is the enterprise gate... 88% of orgs reported an agent security incident in the past year" — line 18), not about regulatory-conduct violations (Reg-F, UDAAP, vulnerable-customer harms). That's a different failure mode than the one N-001 is built to catch; citing it as motivating evidence for *this* product is a category mismatch.
- **F-TIER check holds better than the others.** F1 is defensible: LangSmith/Braintrust genuinely lack conduct semantics, and no file names a cross-agent conduct-supervision product. This is the strongest part of the concept.

The single change that would most strengthen it: drop the "any agent" universality claim in the pitch and lead explicitly with "we generalize Salient's own UDAAP-monitoring feature into a standalone, agent-agnostic product" — turning the closest-comparable's existence into a feature-to-platform thesis instead of hoping the judge doesn't notice it.

## N-002 — The Mandate Fabric

**Verdict: HOLDS**

- **Best-defended F1 claim in the set.** finance.md §2e is explicit and current: "neither framework resolves liability when the agent errs rather than defrauds" and "no actual agent-initiated dispute-volume data exists yet (rails are <15 months old)" — this is a real, dated gap, not an inference.
- **NARROW-IN-A-TRENCH-COAT attack (partial bite).** The competition slice — "50 disputed agent transactions, 10 seeded ambiguous... reconstructs the mandate chain live, renders a ruling" — is, mechanically, a document-parsing + rules-classification + LLM-adjudication pipeline over structured logs. That's a single-workflow claims-adjudication agent wearing "cryptographic-plus-reasoning" language. The "four liability buckets" is a decision tree with an LLM in the loop for edge cases, not obviously different in shape from the dispute-evidence-assembly agents finance.md §2e itself calls "well-trodden (Chargebacks911, Chargeflow, Chargeback Gurus are mature)."
- **EVIDENCE ABUSE, minor.** The claim "x402 at 165M+ agent transactions" (north-stars.md line 43) inflates startup-landscape.md's figure: that brief says x402 "processed >100M payments since May 2025" (§3) — 165M does not appear anywhere in the evidence base and looks like an invented uptick. This is a fabricated-number risk a fact-checker would catch immediately. *(Session adjudication: rejected — the figure is in agentic-ai-landscape.md §3; real finding = cross-brief discrepancy, logged for T7.)*
- **Volume risk is self-flagged but real.** finance.md confirms "Visa... 'hundreds' of live agent-initiated transactions" (§1) — the pre-mortem admits this, but it undercuts the "impact 25" pillar hard: this is a product for a problem that, by the evidence base's own numbers, barely exists yet in production volume.

The single change that would most strengthen it: replace the ["165M+"] figure with the verified x402 number [session: cite both + flag discrepancy], and reframe the competition slice around the one thing the classic dispute-automation vendors structurally cannot do — parsing and cross-referencing signed mandate chains from four *different* protocols simultaneously — rather than a generic ruling engine that merely reads like Chargeflow-with-crypto.

## N-003 — Loyalty as a Financial System

**Verdict: WEAKENED**

- **STALE, meaningfully.** N-003 claims "no pure-play loyalty-ops agent winner exists (startup-landscape §2l — named open white space)" and cites Eagle Eye "naming the gap without an agent-native product." But retail-internal-ops.md §2 already lists a live vendor field for exactly this: "Loyalty & offers ops (ampliFI crossover)... Vendors: Capillary, Kognitiv, Bloomreach, Eagle Eye, Salesforce" with the demo-shape explicitly named ("Y — direct ampliFI crossover"). The concept's "no dominant winner" framing is defensible only if you squint past an entire named vendor row in the sibling brief — this is a coverage gap in N-003's own citation, not a gap in the market.
- **NARROW-IN-A-TRENCH-COAT.** The competition slice is two features — a red-team-the-promo simulator and a fraud/authenticity scorer — bolted together with a shared dataset. Each piece, alone, matches an existing single-workflow category: promo red-teaming is adversarial-simulation-as-a-service (a QA/pentest pattern), and the authenticity scorer is fraud-ring detection (a pattern retail-internal-ops.md's own returns-fraud and card-linked-offer-fraud seeds already describe as "Domo has a named product... Riskified"). Gluing two single-workflow agents together under a "financial system" label is architecture-by-naming, not a genuine reframe.
- **EVIDENCE ABUSE.** "Loyalty programs... 'secured like marketing databases, not financial systems' (finance.md §2g)" is quoted faithfully — but finance.md §2g immediately follows this with "This is a forward-looking, defensively-framed opportunity... it's an emerging threat rather than a live cost center — judge on impact score may rate it as forward-looking rather than urgent." N-003's pre-mortem tries to route around exactly this self-admitted weakness by "pairing the futures... with a bleeding today-cost," but the evidence base itself never actually supplies a bleeding-today loyalty-fraud cost figure — no dollar loss number for loyalty/points fraud appears anywhere in finance.md or retail-internal-ops.md. The "today-cost" pairing is asserted, not evidenced.
- **F-tier is soft.** F1 is claimed for "the integrated architecture" while conceding "components F1/F2" — this is a common tactic (claim F1 for the bundle, concede F2 for the parts) that a skeptical judge could read as tier-laundering: three F2 components don't sum to an F1 whole just because they share a dataset.

The single change that would most strengthen it: cite retail-internal-ops.md's Capillary/Kognitiv/Eagle Eye/Salesforce vendor row honestly and argue differentiation against them specifically (none combine red-teaming + authenticity scoring + points-liability reconciliation as one system) rather than asserting "no pure-play winner" as if the field were empty.

## N-004 — The Exception-Operations Platform

**Verdict: WEAKENED**

- **STALE on the anchor claim's own evidence.** N-004's single most load-bearing citation — "'autonomous QC gate, human at exceptions only' is flagged in pharma.md §4 as aspiration-not-proven" — is quoted accurately (pharma.md: "Autonomous QC gates with human review only at exceptions... still more aspiration than proven pattern"). But that's a pharma manufacturing citation being used to support a claim about *financial-services back-office autonomy graduation* — a different domain entirely. This is evidence transplanted across verticals to prop up a claim the finance/HOA evidence base doesn't itself make about autonomy-tier novelty.
- **NARROW-IN-A-TRENCH-COAT — the most vulnerable concept on this axis.** Strip the "graduation machinery" framing and the ≤6wk competition slice is: "HOA lockbox cash-application... 500 synthetic remittances stream through." That is literally seed #3 from finance.md's own candidate list ("HOA lockbox-to-cash-application agent... Western Alliance") — a single-workflow reconciliation agent. The "autonomy-graduation controller" is described as "deliberately deterministic code, not an agent" (line 107) — i.e., the actual novel IP is a threshold-based state machine promoting/demoting a trust score, demoed once, live, on stage. That is a genuinely clever demo beat, but it is one control-flow gadget wrapped around an otherwise-ordinary cash-application agent, not a platform. The concept's own sizing admits "agents S (one case-worker; the controller is deterministic code)" — by its own accounting, this is the smallest agent-count build in the entire set.
- **F-TIER MISLABEL.** N-004 claims "F2 on any single queue... F1 on the graduation platform." But the competition slice never demos more than one queue (HOA cash-application) — the "platform" claim rests entirely on the applicability matrix (ADP, Visa/Capital One, Invesco/Morgan Stanley) being *asserted* as transferable, not built or evaluated. An F1 claim for a platform that is demoed as exactly one queue, with transfer-to-other-queues unverified even in the eval harness, is a tier claimed on the strength of a sales pitch, not the strength of the artifact.
- **EVIDENCE ABUSE.** "Sonnet-5-class pricing (intro $2/$10) makes per-exception economics work" borrows a pricing figure from agentic-ai-landscape.md's model table without that brief ever connecting Sonnet pricing to exception-economics viability — the inference ("makes the economics work") is the concept's own arithmetic, not a sourced claim, and no per-exception cost-of-service number is computed anywhere to check it against.

The single change that would most strengthen it: cut the pharma citation (wrong vertical) and either (a) actually demo a second queue transfer in the ≤6wk slice to earn the platform claim, or (b) honestly downgrade to F2-with-a-strong-demo-mechanic rather than claiming F1 on an unbuilt generalization.

## N-005 — Zero-Integration Autonomy

**Verdict: HOLDS** (weakest F-tier in the set, but honestly labeled)

- **The concept self-labels F2, which is correct and disarms the staleness attack somewhat** — but the gap between F2 and "narrow workflow" is thinner than the write-up admits. agentic-ai-landscape.md is blunt: "computer use is now a first-class agent capability across all three frontier vendors" (§1) and OSWorld agents are "in the low-80s" exceeding the human ceiling of ~72% — meaning the core capability claim ("computer-use models now exceed the human ceiling") is true but *commoditized*, exactly as N-005 itself concedes ("computer-use capability is commodity").
- **NARROW-IN-A-TRENCH-COAT.** The competition slice is one agent working one payment-reversal exception on one synthetic screen, with a scripted drift-injection moment. That is a single-workflow RPA-replacement demo. The "governance harness" (session isolation, allowed-screen manifest, visual audit ledger) is real differentiated engineering, but none of it is demoed as reusable infrastructure across a second workflow within the ≤6wk slice — it's asserted as generalizable, not shown to be.
- **EVIDENCE ABUSE, notable.** The pre-mortem itself flags the exact problem: "Note for carding: UiPath-class 'agentic automation' marketing exists — verify what they actually ship before the pitch (T7 item)." This is the concept honestly admitting it has NOT verified its own closest-incumbent claim — the freshness tier is asserted without having checked the one class of vendor (RPA-with-agentic-branding) most likely to already ship something adjacent. That's a self-confessed evidence gap on the single most load-bearing claim (F2 novelty).
- **Brief coverage gap (flagged honestly, not invented):** no file in the evidence base actually researched UiPath, Automation Anywhere, or Blue Prism's 2025-26 agentic roadmaps. This is a real hole — N-005's freshness claim rests on the *absence* of evidence about the incumbents most likely to contest it, which is a weaker foundation than the concept's confident F2 label implies.

The single change that would most strengthen it: do the T7 verification the concept itself flags as outstanding — check UiPath/Automation Anywhere's actual 2026 agentic-computer-use shipping status — before carding, since an unverified "commodity capability, open governance wedge" claim is one incumbent press release away from collapsing to F3.

## N-006 — The Agent Underwriting Bureau

**Verdict: WEAKENED**

- **STALE, and the concept knows it.** N-006's own freshness line concedes F2 with "closest: AIUC — insurance + audit framing, thin published evaluation depth." But AIUC is not thin on ambition: startup-landscape.md's funding table describes it as "$15M seed... AIUC-1 certification + insurance; predicts a $500B agent-insurance market by 2030" — a funded, named, live certification product. N-006's differentiation ("evaluation-deep" vs. AIUC's "insurance-first") is a real distinction but a narrow one; a judge could reasonably ask why a from-scratch certification harness beats partnering with or displacing an already-funded certification incumbent.
- **NARROW-IN-A-TRENCH-COAT — self-admitted.** The concept's own pre-mortem states the kickoff materials list "eval frameworks" under **Track C**, and that this "must be framed as a client-facing procurement/model-risk workflow... confirmed with the GC before carding." This is the concept flagging, in its own text, that its natural home is a *different competition track* — about as strong a narrowness admission as exists in this file. Strip the "certification scorecard for buyers" framing and the ≤6wk slice is: run an eval harness against two agents and print a scorecard. That is literally what AgentCore Evaluations and Braintrust already do as components (conceded in the "why a platform template can't do it" section itself: "Evaluation *components* are everywhere").
- **F-TIER MISLABEL risk.** Claiming F2 while the closest incumbent (AIUC) is well-funded, named, and squarely targeting the same buyer ("procurement, model-risk... insurers") is generous. AWS AgentCore Evaluations shipping "13 evaluators... GA 2026-03-31" as productionized components further narrows the gap between "evaluation depth" and "assemble AgentCore's own evaluators into a report" — the concept doesn't establish that its scenario-compiler + adversarial battery is meaningfully harder to replicate from AgentCore components than it claims.
- **EVIDENCE ABUSE, structural.** "HAL-grade methodology (landscape §5), productized for buyers" invokes HAL's academic rigor to justify commercial productization — but HAL is a research framework with no buyer-facing productization anywhere in the evidence base; claiming to productize its "grade" of methodology in 6 weeks is an aspiration presented as an inherited credential.

The single change that would most strengthen it: resolve the Track C boundary question *before* scoring, since a concept that flags its own likely track-mismatch in its pre-mortem is fighting the rubric, not just the market — no amount of demo polish fixes a track-eligibility problem.

## N-007 — The Agent-Ready Enterprise

**Verdict: REFUTED** (weakest of the seven — even the concept says so)

- **STALE — the concept's own text confirms this is a playbook copy, not a reframe.** Freshness is self-labeled F2 with "playbook proven at data-giant scale; the mid-market productization... is open" — but read the evidence: S&P/Kensho, Moody's, FactSet, and LSEG have already built "governed agent surfaces" including semantic layers and entitlement rules at production scale (media-findings-digest.md). The only "new" ingredient is a code-generation agent that automates the *building* of the surface — but the digest itself flags that "'We support MCP' is explicitly table stakes" and doesn't establish that the semantic/entitlement layer generation step is itself novel versus, e.g., FactSet's Mercury knowledge-agent line, which the digest already describes as productized.
- **NARROW-IN-A-TRENCH-COAT — the concept explicitly self-diagnoses this and does not resolve it.** The pre-mortem is unusually candid: "Highest risk in this file of reading as plumbing ('you built an MCP server')... If the demo can't make governance *visceral* in 30 seconds, this concept belongs in the Zenon-asset track rather than the competition shortlist — flag honestly at scoring." This is the concept's author recommending its own disqualification from the competition shortlist. Stripped of the "builder agent" framing, the ≤6wk slice is: generate an MCP server + policy pack from a schema, then have a red-team agent try to break the entitlements. That is a codegen-agent-plus-pentest-agent pair — two single workflows, not an enterprise reframe.
- **EVIDENCE ABUSE.** "Dow Jones R&C ships no agentic product on its screening data (confirmed absence)" is accurately cited, but the concept then leverages this *absence* at Dow Jones to justify an *architecture pattern* whose hard part (semantic + entitlement layer) is explicitly proven and productized elsewhere in the same brief (S&P/Moody's/FactSet). The absence at one client doesn't establish novelty of the underlying technical approach — it only establishes that DJ hasn't bought a version of something three competitors already ship.
- **F-TIER MISLABEL.** F2 is claimed, but given that (a) the semantic-layer + entitlement-gateway + red-team-before-go-live pattern is described as proven at "data-giant scale" in the same paragraph, and (b) YC's own Summer-2026 RFS names "Software for Agents" as a live, funded category, this reads closer to F3 (validated category, no client-specific twist) than F2. The one genuinely fresh angle — an agent that *builds* the governed surface rather than a vendor manually engineering it — is asserted but never differentiated from FactSet's or Moody's own internal tooling, which the brief doesn't claim is manual.

Nothing modest saves this one: the concept's own pre-mortem already concludes it "belongs in the Zenon-asset track rather than the competition shortlist" — the honest fix is to withdraw it from the Track-A slate rather than polish the pitch, unless the team can find a client-specific technical wrinkle (e.g., a genuinely hard semantic-mapping problem unique to one client's data) that none of the media brief's four named incumbents already solved.

## Overall summary — biggest blind spots in the set (Agent E)

- **Cross-file citation blindness is systemic.** Three separate concepts (N-003, N-005, N-006) build their freshness claims while failing to cite a directly-relevant vendor list sitting in a sibling research file (retail-internal-ops.md's loyalty-vendor row for N-003; the UiPath/RPA-agentic gap N-005 itself flags as unverified; AIUC's funded scale for N-006). The seven concepts were evidently checked against their *primary* anchor brief but not cross-referenced against the other six — a coverage discipline gap, not a research gap.
- **The "platform" claim is the set's load-bearing weak joint.** N-001, N-004, N-006, and N-007 all claim to be platforms/infrastructure rather than single workflows, but every one of their ≤6wk competition slices demos exactly one workflow instance; the platform/generalization claim is uniformly carried by the applicability matrix (prose) rather than by anything the eval harness actually measures across more than one case-class. If a judge asks "show me the second queue," four of seven concepts have nothing to show.
- **Self-aware pre-mortems are being treated as mitigations rather than as verdicts.** N-006 and N-007 both contain pre-mortems that amount to "this might not belong in this competition" — that is the strongest possible internal signal to kill or substantially rework a concept, yet both are carried forward into the north-star set at full F1/F2 billing rather than being downgraded or cut.

---

## Agent F — feasibility/depth/demo attack (verbatim)

## N-001 — The Decision Assurance Stack

**Verdict: BORDERLINE (build) / FRAGILE (demo)**

Independent sizing: agents **M** (auditor pipeline + LLM judge panel is real multi-role) · tools **M, not S** (hash-chained ledger, deterministic Cedar-style policy engine, replay/counterfactual engine, packet generator, blocking-gate MCP interception = 5+ integration points — METHOD's own table puts 4-6 tools at M) · UI **M** ("single dashboard" showing live case replay + counterfactual + blocking-gate intercept + exception queue is really 3-4 views compressed into one label) · data **S→M** (must be a *linked* corpus — transcripts + policy-version history + model-version history + HITL state) · evals **M** ("judge-calibration agreement published" requires an actual human-labeled sample, which is the auto-scoring tier, not just a golden set).
**My verdict: 5M, or generously 1L+2M if you fuse tools+data into one "L-scale ledger+policy+replay system." Either reading breaks the ≤1L+2M ceiling.** The stated "2M, fits" undercounts by collapsing five real subsystems into "tools S."

- The replay/counterfactual engine is not a tool, it's a second inference system that must reconstruct decision state under a *different* policy version — a full re-execution harness. Building it to work live, on-demand, for a judge-picked arbitrary case in under 6 weeks alongside a hash-chained ledger and a Cedar-style deterministic engine is at least 2 M-tier tools by itself.
- The two-layer conformance engine assumes Reg-F 7-in-7 counting is "deterministic policies-as-code" over free-text collections transcripts — but Reg-F contact-counting requires correctly parsing call/contact events out of noisy call logs, not clean structured fields. If the synthetic data doesn't pre-structure this, the "deterministic" claim quietly becomes an extraction problem.
- "Judge picks any case, gets full replay + counterfactual in seconds" vs. the async/batch judge design — if a judge picks an adversarial case live, "in seconds" may quietly become 10-30 seconds of visible LLM latency — a stage-visible mismatch.
- Synthetic data: 200 cases with 6 planted defects is achievable — the strongest part of the slice.
- Track/rubric: clean Track A fit; risk is depth-vs-scope.

**Hardest CTO question:** "Walk me through what happens when the judge picks case #17 for counterfactual replay — is that a cached pre-computed result, or are you actually re-invoking the LLM judge live under a different policy version, and if so, why does that not violate your own <500ms blocking-gate budget?"

## N-002 — The Mandate Fabric

**Verdict: BORDERLINE (build) / FRAGILE (demo)**

Independent sizing: agents **M** · tools **M, not S** (parsers for *four* heterogeneous protocol formats — AP2, Mastercard Agentic Tokens, ACP, TAP — plus ledger query plus ruling generator; four distinct protocol parsers alone crosses the S ceiling of ≤3) · UI **M** (fairly sized) · data **S** · evals **S**.
**The tools axis is the quiet break** — each protocol is a distinct signed-artifact schema; that is 4+ integrations before any reasoning logic.

- Building four working *synthetic* signature/consent-artifact formats that a deterministic verifier can actually parse and validate (not just narrate) is real crypto-adjacent plumbing — every protocol needs its own synthetic-signing scheme in the data generator.
- The "agent-exceeded-mandate" bucket requires judging "within scope" for cases like "$99.99 shoes + $12 shipping within a <$100 mandate" — the soft-boundary judgment problem with no stated calibration plan.
- The "honesty moment" depends on the audience understanding what a mandate chain is — the 2-minute protocol primer eats the demo slot.
- Synthetic data: achievable — structured logs suit Faker/SDV generation. The concept's strongest leg.

**Hardest CTO question:** "You're parsing four live, evolving protocol specs — which of those four will actually be implemented for the demo, and are the other three narrated/mocked? Because if three of four are stubs, the 'canonical authorization graph' claim is aspirational, not built."

## N-003 — Loyalty as a Financial System

**Verdict: BORDERLINE (build) / STAGEABLE (demo)**

Independent sizing: agents **M** (but "attacker fleet" could tip to L if taken literally) · tools **S** · UI **M** · data **S** · evals **S**.
**The best-sized of the seven — genuinely close to 2M, fits**, provided "attacker fleet" is descoped to 2-3 named exploit strategies rather than an open-ended adversarial swarm.

- If the red-team is a genuine multi-agent search of an open exploit space (vs. 3-4 pre-scripted exploit patterns), it's an open-ended search problem that consumes disproportionate build time. Constrain it explicitly or it creeps to L.
- The authenticity scorer's "sub-second budget" is a real-time feature-engineering + inference pipeline — where do ground-truth authenticity labels for tuning come from beyond the seeded set?
- Both demo moments depend on the seeded exploit being subtle enough to look "found" rather than scripted — audiences smell a canned reveal.
- Synthetic data: strong playbook fit — the "seed N known anomalies" pattern exactly.

**Hardest CTO question:** "Your adversarial offer red-teamer — is it actually generating novel exploit strategies against a draft offer, or replaying a fixed exploit library? If it's the latter, what happens when a judge proposes a promotion structure you didn't pre-script for?"

## N-004 — The Exception-Operations Platform

**Verdict: BORDERLINE (build) / FRAGILE (demo)**

Independent sizing: agents **S** (honest and correctly scoped) · tools **S** · UI **M** · data **M, understated from S** ("one linked corpus" containing remittances + assessment ledger + bylaws pack is definitionally the 2-3-linked-corpora M tier) · evals **M** (correctly self-labeled).
**= 3M — past the ceiling on the stated rule, though the honest S on agents keeps it plausibly buildable.**

- The mid-demo promotion requires statistical promotion/demotion thresholds genuinely tuned against live accumulated accuracy — a small live statistical-process-control system hiding inside a "tools S" line.
- Promotion needs a statistically defensible sample size and confidence threshold — with no stated minimum n, the promotion could look arbitrary or scripted.
- The most ambitious live-demo sequence in the set: supervised mode → live accuracy accumulation → live promotion → live demotion on planted drift, all in one window; if the drift event doesn't trigger demotion visibly and immediately, the signature moment fails with no fallback described.
- HOA bylaws require encoding lien-threshold/delinquency-escalation rules as structured policy — a policy-authoring exercise as much as data generation.

**Hardest CTO question:** "Show me the exact statistical test and sample-size threshold behind a mid-demo promotion — if I ran your synthetic stream twice with different random seeds, would the promotion happen at the same case number both times, or is the timing effectively scripted?"

## N-005 — Zero-Integration Autonomy

**Verdict: BORDERLINE (build) / FRAGILE (demo)**

Independent sizing: agents **M** · tools **S** · UI **M, arguably L** (a green-screen terminal app with enough surface for a payment-reversal workflow, a UI-layout-change injection, and a screenshot-hashed audit viewer is two full applications) · data **S** · evals **S** (though "drift suite" nudges toward M).
**The concept most likely to secretly cost an extra UI axis** — "we build the fake legacy app — that's the data plan" launders a full mock-application build into the data axis. The most creative sizing sleight-of-hand in the document.

- OSWorld low-80s is on *real, previously-seen* benchmark apps; on a bespoke synthetic terminal, actual reliability is unvalidated and could be materially worse.
- The pre-planned "recorded fallback" is an implicit admission the live path is not trusted — a sophisticated judge panel may notice and discount, hitting feasibility/technical-depth.
- The "data plan" is an app, not a dataset — servicing-account records still need domain-realistic distributions, unelaborated.

**Hardest CTO question:** "What's your measured pass^k on your own synthetic terminal — not OSWorld's benchmark apps — across 20 repeated runs of the same payment-reversal task, and how many of those runs needed the 'recorded fallback' the demo doctrine allows?"

## N-006 — The Agent Underwriting Bureau

**Verdict: BREAKS on Track fit / BORDERLINE on build. FRAGILE (demo)**

Independent sizing: agents **M** · tools **S** · UI **M** · data **M→S** · evals: **the build IS the eval harness — a category error to size at S/M; adversarial battery + pass^k + judge calibration + reproducibility bundle = the full L tier.**
**= 1L+2M, right at the ceiling, no slack** — the tightest fit of the seven once evals is honestly counted, leaving zero margin.

- The "evidence bundle the buyer can re-run" is nontrivial reproducibility engineering, easily M-to-L on its own.
- Same unresolved judge-calibration problem as N-001, except here methodological honesty is the *entire pitch* — an uncalibrated judge directly contradicts the product's core claim.
- **Track fit is the real break:** kickoff notes state "TRACK C: Open Category (eval frameworks, agentic optimization; committee approval required)." Reframing the pitch doesn't change that the underlying build *is* an eval framework wearing a procurement-workflow costume. If the GC hasn't pre-cleared it, this can be scored off-track or disqualified regardless of engineering quality — the single largest risk in the document.
- The judge-re-runs-a-scenario moment is the highest-variance live moment in the set: any nondeterminism in the judge layer and the central "reproducibility" claim visibly fails in front of the panel.

**Hardest CTO question:** "Given the kickoff deck puts eval frameworks under Track C requiring committee approval, and this concept's entire product is a certification/eval harness — has the GC actually approved this as Track A, in writing, and what's the fallback if they haven't by the time you'd need to start building?"

## N-007 — The Agent-Ready Enterprise

**Verdict: BORDERLINE (build) / FRAGILE (demo)**

Independent sizing: agents **M** (three qualitatively different agent jobs — codegen, consumption, adversarial — brushing L) · tools **M, understated from S** (the builder generates 4 artifact types: MCP server, semantic skills layer, policies-as-code, entitlement gateway with metering — each needing its own validation path) · UI **M** · data **S** · evals **S**.
**= 3M, likely breaking the ceiling** once the four generated-artifact types are honestly counted.

- "The part generic codegen gets wrong" (semantic skills) is the concept's own admission of the hard part — with no stated verification for whether the builder's taxonomy output is *correct* rather than plausible; a subtly wrong mapping poisons every downstream citation-grounded answer while still passing the evals.
- The entitlement-bypass-blocked-live moment is the cleanest demo beat in the set — genuinely stageable, no protocol literacy needed.
- If the builder step runs live: visible codegen latency and nondeterminism (will it generate the same server twice?); unspecified whether live or pre-baked-then-narrated.
- MCP is "table stakes" per the team's own landscape research — the core deliverable sits close to an explicitly-named commodity floor.

**Hardest CTO question:** "When the judge asks 'what did your builder agent do that a generic codegen tool wouldn't,' can you point to a specific semantic-taxonomy decision it got right that a naive schema-to-MCP generator would have gotten wrong, live, in the demo?"

## Ranking: most to least buildable in 6 weeks (Agent F)

1. **N-003** — cleanest sizing, one soft spot (attacker-fleet scope creep), no live-latency-sensitive step, no protocol literacy required.
2. **N-004** — honestly scopes agents to S, but the mid-demo promotion/demotion sequence is a real timing risk and the data axis is undercounted.
3. **N-005** — Zenon-shaped and technically legitimate, but the "fake legacy app" hides a real UI-build project and the recorded-fallback plan is a tell.
4. **N-002** — strong synthetic-data fit but four protocol parsers undercounted as "tools S," plus mandate-scope ground-truth and audience-literacy overhead.
5. **N-001** — the most subsystem-dense concept squeezed into a "2M, fits" label optimistic by at least one full axis, with a live-latency contradiction.
6. **N-007** — three agent roles plus four generated-artifact types under "tools S," and the highest self-diagnosed commodity risk with no verification story for the differentiating part.
7. **N-006** — the most rigorously self-aware concept, but carries a live, unresolved Track A/C boundary risk — a build can be excellent and still be scored off-track, making it the least safe bet regardless of engineering merit.
