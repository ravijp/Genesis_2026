# Ideas — Generator G3 (raw)

- **Generator id:** G3
- **Persona:** Compliance / audit analyst who signs things nervously — prepares attestations, responds to exam requests, chases evidence across departments that don't answer email, and puts their name on documents whose underlying data they can only partially verify. Thinks in control frameworks, sampling, audit trails, findings, and the gap between what the procedure says and what the team actually does.
- **Direction A:** The supervision interface between institution and regulator (regulatory reporting, attestations, exam preparation, evidence production, SupTech).
- **Direction B:** Explainable decisioning under uncertainty at origination (credit underwriting, insurance risk acceptance, limits/pricing — defensible, individually-explained decisions at volume).
- **Date:** 2026-07-15
- **Input diet:** exactly one repo file — `01_research/finance.md` (2026-07-14 pass-2 version) — plus generator's own knowledge. No other repo files, no git, no web. Deliberate bias quarantine.

---

## G3-1 — The Evidence Chaser *(Direction A)*

**The problem.** A first-day letter lands with 180 request items and a three-week clock. Half the items live in systems I don't have access to; the other half live with people who don't answer email. I spend the exam prep period being a human ticketing system — forwarding requests, translating examiner language into department language, re-asking, and then hand-assembling whatever comes back into folders, praying nothing contradicts anything else. The examiners get a production set that reflects who answered email, not what the truth is.

**Who has it.** The regulatory-exam coordinator / compliance analyst who owns the request-item tracker at any examined institution; secondarily the department SMEs who get ambushed by requests.

**What the agent does.** Ingests the exam request list, decomposes each item into the specific artifacts that satisfy it (policy doc, system report, transaction extract, committee minutes), then goes and *gets* them: queries the systems it has connectors to, opens tracked tasks against named owners for the rest, escalates non-responses on a schedule, and re-asks in the owner's own vocabulary. As evidence arrives it checks internal consistency (does the policy version produced match the version referenced in the procedures also being produced?), flags contradictions before the examiner sees them, and assembles a production set where every artifact carries a provenance line: where it came from, who provided it, when, and what request item it satisfies. Produces the gap report I currently build by hand at 11pm.

**Why newly possible now.** Agents can now hold an entire request list plus the firm's document estate in working context, operate enterprise systems through tool interfaces (the MCP-style connector wave hit financial data platforms in 2025-26), and do the cross-document contradiction checking that used to require a human who had read everything. The Mills Review's "AI-enabled supervisory model" recommendation (2026-07-06) means the examiner side is about to speed up — the institution side has to match it or drown.

---

## G3-2 — Signature Support Memo (the "what am I actually signing?" agent) *(Direction A)*

**The problem.** I sign attestations — 302 sub-certifications, compliance attestations, responsible-person declarations — that compress hundreds of underlying assertions into one signature. Nobody decomposes what the signature actually asserts. I get a two-page summary from each department saying "no issues noted," and my name goes on the line. When something later turns out to be wrong, the question is "what did you do to satisfy yourself?" and the honest answer is "I trusted the summaries."

**Who has it.** Every named signer: sub-certifying officers, MLROs, SMF holders under the UK's Senior Managers regime (where signature = personal regulatory liability), CFO-delegates on regulatory returns.

**What the agent does.** Takes the attestation text and decomposes it into its atomic assertions ("all reconciliations were performed," "no unremediated control failures exist," "training was completed by all in-scope staff"). For each assertion it goes looking for supporting evidence in the systems of record — reconciliation logs, issue trackers, LMS completion data — and returns a **signature support memo**: assertion by assertion, here is the evidence found, here is its freshness, here is what could NOT be verified and why, here is what changed since you last signed. I sign with a documented basis, or I push back with a specific list instead of a vague bad feeling. The memo itself is the audit trail of my due diligence.

**Why newly possible now.** Decomposing legal/attestation language into checkable assertions is exactly what current frontier models do well; connecting each assertion to heterogeneous evidence systems requires agentic tool use that only became enterprise-practical in 2025-26. And the accountability-regime trend (SM&CR-style personal liability spreading across jurisdictions) makes "documented basis for signature" a product a nervous signer will pay for personally.

---

## G3-3 — Cell-to-Source: the regulatory-return lineage tracer *(Direction A)*

**The problem.** A regulatory return is thousands of cells. Each cell is an aggregation of aggregations, adjusted by spreadsheets that live on a shared drive, owned by people who inherited them from people who left. When an examiner asks "walk me back cell C14 to source," the walk takes three analysts two weeks and dies at an EUC spreadsheet with a hardcoded plug from 2023. I attest to the return anyway, because the deadline doesn't move.

**Who has it.** Regulatory reporting teams (the people who produce FR Y-9C / call reports / COREP / FINREP-class returns) and the officers who attest to them; the examiners who receive them feel the mirror-image pain.

**What the agent does.** For any cell in the return, the agent traverses the actual production chain — extracts, transformation code, the EUC spreadsheets, manual adjustment journals — and builds the lineage graph *by reading the artifacts*, not by trusting the documented data dictionary. It flags where documented lineage and actual lineage diverge, identifies plugs/overrides and hunts for their justification, recomputes cells independently from source as a check, and produces per-cell defense packs before filing. Over time it maintains a living lineage map so the two-week walk becomes a two-minute query. The attestation stops being a leap of faith over a canyon of spreadsheets.

**Why newly possible now.** Reading and reasoning over heterogeneous artifacts — SQL, spreadsheet formulas, adjustment memos, prose procedures — in one pass is a frontier-model capability that didn't exist at usable accuracy before; classic data-lineage tools only trace what's in governed pipelines and go blind exactly where the risk is (the EUC layer). Agentic traversal follows the chain wherever it actually goes.

---

## G3-4 — Drift Witness: procedure-vs-practice divergence auditor *(Direction A)*

**The problem.** The procedure says the analyst checks four databases and documents the rationale. What the team actually does is check one database and paste a template rationale, because volumes doubled and headcount didn't. Everyone on the floor knows; the procedure doesn't. I find out when I test a sample of 25 — or worse, when the examiner tests theirs. Every finding I've ever been named in was a procedure/practice gap that had been true for months.

**Who has it.** First-line team leads (who own the drift), second-line compliance testers (who find it late), internal audit (who find it later), and the institution when the regulator finds it last.

**What the agent does.** Reads the written procedures, then continuously observes actual practice through system exhaust — case-management timestamps, query logs, which screens were opened, what the disposition notes actually say versus the template — and detects divergence: steps skipped, sequences inverted, rationales copy-pasted, timings impossible if the step were really performed. Instead of a sample of 25, it witnesses the full population. It distinguishes benign workarounds from control-defeating ones, drafts either a procedure update (when practice is right and the document is stale) or a remediation flag (when practice is the problem), and timestamps everything so the institution can show a regulator it detects its own drift. Self-reporting with evidence beats being caught, every time.

**Why newly possible now.** The raw exhaust always existed; what's new is a model that can read a prose procedure and *understand what its execution should look like in logs* — mapping normative text to behavioral telemetry. That cross-modal reasoning became reliable only with current-generation models, and the regulatory vacuum around agentic AI (OCC Bulletin 2026-13 explicitly excludes it from MRM scope, 2026-04-17) means voluntary self-surveillance is currently the strongest governance signal a firm can send.

---

## G3-5 — The Standing Exam: a two-sided machine-examinable interface *(Direction A — big swing)*

**The problem.** An exam is a batch process built on distrust: the regulator asks for documents because it cannot see operations, and we reconstruct evidence after the fact because we never built operations to be examinable. Both sides pay armies. The absurdity: I spend weeks producing evidence that a control operated in March, when the system that operated the control could have attested to it in March.

**Who has it.** Both sides of the interface — the institution's exam-management and reporting functions, and the supervisor's examination teams trying to examine hundreds of firms with static headcount. (The Mills Review's "build an AI-enabled supervisory model" recommendation, published 2026-07-06, is the regulator side asking for exactly this.)

**What the agent does.** Two agents, one protocol. The **institution agent** maintains a continuously-updated evidence ledger: every control execution, reconciliation, disposition, and exception is captured at the moment it happens, with cryptographic timestamps, into a queryable attestation store. The **supervisor agent** examines through a governed interface: it formulates supervisory questions ("show me all vulnerable-customer escalations in Q2 where the human override was slower than policy"), negotiates scope with the institution agent (which enforces data-minimization and legal-privilege boundaries — it can *refuse* and log the refusal), runs its own sampling and testing against the ledger, and drafts findings with full evidence citations. Exams become standing queries instead of annual sieges. The vision endpoint: supervision as an API with humans adjudicating disputes, not shuffling PDFs.

**Why newly possible now.** Three lines converged in 2025-26: regulators publicly committed to AI-enabled supervision (Mills Review; FCA AI Lab and Live Testing cohorts running Apr–Dec 2026, evaluation Q1 2027); agent-to-agent interaction acquired real protocol substrates (the MCP-style interface wave, agent identity/attribution rails shipping in payments); and agents became capable of the negotiate-scope/sample/test/draft loop end to end. Nobody has connected the three because it requires building both sides at once — which a demo, unlike a procurement process, can do.

---

## G3-6 — Finding-to-Closure: the remediation lifecycle agent *(Direction A)*

**The problem.** An MRA lands. We write a remediation plan under pressure, promise dates we guess at, and then the finding enters its second life: quarterly status updates written by whoever is available, evidence gathered in a panic the week before each update, and a closure package assembled months later by someone reverse-engineering what was actually done. Regulators notice recycled language in status updates. Repeat findings — the thing that turns an MRA into an MRIA into a consent order — happen because closure was declared on paper, not in the systems.

**Who has it.** The issue-management office / regulatory-affairs team that owns the findings register; the accountable executives whose names are on remediation commitments; the examiners who must judge closure claims they can't independently verify.

**What the agent does.** Owns each finding as a case, end to end. It decomposes the remediation plan into verifiable milestones tied to system-observable outcomes (not "policy updated" but "policy v3.2 published AND training completion >95% AND the new control demonstrably executing in production logs"). It gathers evidence continuously as work happens rather than before deadlines, drafts status updates from that evidence (with deltas, not recycled prose), independently *re-tests the control after closure* on a decaying schedule to catch regression, and assembles a closure package where every claim is backed by an artifact. It also cross-references new findings against the register and flags "this is finding #2019-14 wearing a new hat" before the regulator does.

**Why newly possible now.** The milestone-decomposition step — turning a prose remediation plan into system-checkable conditions — is new-generation model capability; continuous evidence gathering requires the enterprise tool-access layer that matured in 2025-26. And the supervisory climate rewards it: with agentic AI outside formal US guidance scope, demonstrable self-remediation-verification is the strongest "we govern ourselves" evidence a firm can put in front of an examiner.

---

## G3-7 — The Middle-Band Adjudicator: investigating underwriter for the grey zone *(Direction B)*

**The problem.** Origination decisioning is honest at the extremes and dishonest in the middle. Clear approvals and clear declines are cheap. The middle band — thin files, income that doesn't parse, discrepancies between stated and documented — gets one of two lazy treatments: auto-decline (lost good business, and the decline reasons are boilerplate) or escalation to a human queue where an overworked underwriter spends 40 minutes and documents 4 lines. When that decision is challenged later, the file says almost nothing. As the person who samples these files in QA, I can tell you: the middle band is where every indefensible decision lives.

**Who has it.** Consumer and small-business credit underwriting teams (the escalation queue owners); credit-risk officers accountable for both loss rates and decline-rate complaints; compliance officers who must answer for every adverse action.

**What the agent does.** Takes the referred application and *investigates* rather than scores: identifies exactly which uncertainties make the case borderline, then works to resolve each — re-parses documents, reconciles income across sources, requests the specific missing artifact from the applicant (one precise ask, not a document dump demand), checks explanations for consistency. Then it decides within an explicitly delegated authority envelope (or recommends, with the human deciding above threshold), and writes the artifact that today never gets written: an individually-reasoned decision memo — what was uncertain, what was checked, what resolved or didn't, why this outcome, and what specific change in circumstances would change it. Every middle-band decision leaves a file that reads like a senior underwriter had a full day per case.

**Why newly possible now.** The middle band was economically unservable: too ambiguous for scorecards, too voluminous for senior humans. Agents that read messy documents, sustain a multi-step investigation, and produce individually-reasoned prose collapse the cost of diligence per file by orders of magnitude. And the regulatory bar moved to meet it: CFPB's stated expectation that firms articulate *why* an AI system decided, consistently at scale, makes "defensible individual reasoning at volume" the binding requirement — which is precisely what this produces.

---

## G3-8 — Reason-Code Honesty: the counterfactual adverse-action verifier *(Direction B)*

**The problem.** Adverse-action notices are a compliance fiction I help maintain. The model declines; a mapping table converts the top feature attributions into four approved reason-code phrases; the applicant gets a letter that is technically compliant and individually meaningless. Here is the question that keeps me up: if the applicant fixed the stated reason, would the decision actually flip? Mostly, nobody knows. Nobody tests. I sample notices in QA and check that the codes were *generated* correctly — not that they're *true*.

**Who has it.** Fair-lending and compliance officers who own adverse-action processes; model risk teams asked to validate explainability; ultimately the regulator, who currently has no way to test explanation faithfulness at scale either.

**What the agent does.** For each adverse action (sampled continuously, or full population), it *tests the explanation against the decision system*: constructs the counterfactual — the same applicant with the stated deficiency remedied — and re-runs the decision. If the stated reasons are remedied and the answer doesn't change, the explanation was unfaithful, and that notice is flagged with the reasons that *actually* bind. It aggregates patterns (which reason codes are systematically decorative, which segments get unfaithful explanations — a fair-lending signal in itself), drafts corrected notice language, and produces the faithfulness-audit report that currently does not exist anywhere in the industry. It can also sit in-line at generation time: no notice goes out until its reasons pass the counterfactual test.

**Why newly possible now.** Counterfactual testing per applicant was computationally and organizationally unaffordable when explanations were hand-mapped; an agent with API access to the decision engine can generate, perturb, re-run, and interpret thousands of counterfactuals cheaply. Regulator focus made it urgent: explainability-at-scale is CFPB's explicitly monitored area, and "we verify every explanation against the decision itself" is an answer no incumbent can currently give.

---

## G3-9 — Referral-Desk Underwriter's Witness: insurance risk-acceptance files that defend themselves *(Direction B)*

**The problem.** In insurance, the middle band is the referral desk: risks outside the automated appetite box get referred to a human underwriter who accepts, declines, or accepts-with-terms — often deviating from guidelines, which is their job — and documents the deviation in a free-text field, if at all. Two years later, after losses, the same institution asks "why did we write this?" and the file whispers. Reinsurers, auditors, and regulators all sample these files; I've watched an entire book get remediated because acceptance rationale couldn't be reconstructed.

**Who has it.** Commercial/specialty-lines underwriters at the referral desk; chief underwriting officers accountable for guideline discipline; reinsurance treaty auditors; conduct regulators sampling for consistent treatment.

**What the agent does.** Rides alongside every referral. It assembles the complete risk picture (submission docs, loss runs, external exposure data), maps the case against the underwriting guidelines to identify *precisely which* appetite rules the risk breaches and by how much, and then — when the underwriter accepts anyway — interrogates the acceptance: elicits the rationale, tests it against the evidence in the file ("you cited improved loss experience; the loss run shows the improvement is one year — flag?"), prices the deviation, and writes the acceptance memo: guidelines engaged, deviations taken, rationale given, evidence supporting and contradicting, terms applied as mitigation. It also scans the desk's decisions across time for consistency — like risks treated unlike — which is exactly what a conduct examiner will do. The underwriter still judges; the judgment finally leaves a defensible trace.

**Why newly possible now.** Underwriting guidelines are prose; submissions are unstructured document piles; the deviation-mapping between them was human-only work until models could read both sides reliably. The economics flipped in 2025-26: an agent producing a full acceptance memo per referral costs less than the free-text field it replaces. And the defensibility demand is rising on every side — reinsurers tightening treaty audits, conduct regulators extending consistent-outcomes expectations into underwriting.

---

## G3-10 — Override Ledger: real-time justification files for every human exception *(Direction B)*

**The problem.** The most dangerous artifact in origination isn't the model — it's the override. A human overrides the decision engine, types "customer known to branch, income stable" and moves on. Overrides are where discretion, and therefore both flexibility and bias, live. When I audit overrides I sample 30 out of 4,000 per quarter, and the justification field is either empty, template, or unfalsifiable. Fair-lending analytics later show override patterns that skew by demographics, and nobody can reconstruct why any individual override happened.

**Who has it.** Credit policy teams who own override authority matrices; fair-lending officers who must explain override disparity statistics; branch/relationship managers who exercise overrides and get blamed later; auditors who sample and despair.

**What the agent does.** Intercepts every override *at the moment it happens* and builds the justification file in real time: elicits the specific rationale from the overriding officer (structured elicitation, not a free-text box — "what do you know that the engine doesn't? what's your evidence?"), verifies what's checkable immediately (claimed deposit history: pulled and attached; claimed employment stability: verified against payroll data), classifies the override against the policy's permitted-override taxonomy, and refuses to let unfalsifiable rationales pass unexamined — it asks the follow-up a good auditor would ask, at decision time instead of two years later. Population-wide, it monitors override patterns continuously for the disparities fair-lending analytics find annually, and surfaces them while they're still correctable. The override stops being a documentation hole and becomes the best-evidenced decision in the book.

**Why newly possible now.** Structured elicitation-plus-verification in the moment requires an agent that can converse with the officer, query the evidence systems mid-conversation, and judge sufficiency of a rationale — a real-time multi-tool loop that was demo-ware before 2025. Regulator attention to AI decisioning has a blind spot exactly here: everyone instruments the model, nobody instruments the human exception path. That inversion is the originality.

---

## G3-11 — Second-Look Standing Desk: decline re-examination with comparator evidence *(Direction B)*

**The problem.** Declines are the unexamined half of origination. Approvals get monitored (they turn into loans, losses, data); declines get a notice and silence. Default-declined applications in the messy middle include recoverable good business and — the part that frightens me professionally — the raw material of disparate-impact findings. When a fair-lending exam asks "show me that similarly-situated applicants were treated alike," we run regressions on aggregates and hope. No one re-examines individual declines, because there's no one to do it.

**Who has it.** Fair-lending compliance officers (the exam exposure); heads of lending (the lost-volume cost); credit policy teams who set the auto-decline thresholds and never see what those thresholds discard.

**What the agent does.** Runs a standing second-look desk over the decline flow. For each decline in the reviewable band, it (1) re-investigates the file the way G3-7 would — is the decline supported by resolvable uncertainty, or is it real? — and routes recoverable cases back with a documented basis; (2) builds the **comparator file**: finds the most similarly-situated *approved* applicants on legitimate credit factors, and documents either the distinguishing factor that justifies the different outcome or the absence of one — escalating the latter as a potential consistency exception while it's one case, not a pattern in an examiner's regression. Every decline in scope gets either a documented justification or a second chance. The output is the exam artifact that today cannot be produced: individual-level evidence of consistent treatment.

**Why newly possible now.** Individually re-examining declines was pure cost with no owner — the volume economics only work with agents. Comparator matching plus judgment about whether a distinguishing factor is *legitimate* requires reasoning over full applicant files, not feature vectors — new-model territory. And disparate-impact methodology fights (aggregate statistics being contested ground in 2025-26 US fair-lending debates) make individual-level comparator evidence strictly stronger than the regressions both sides currently argue over.

---

## G3-12 — The Time Capsule: as-of-date decision reconstruction and defense *(Direction B, bridging A)*

**The problem.** Decisions are made once but defended years later — in complaints, litigation, and exams — by which time the model has been retrained twice, the policy has three new versions, the data vendors have restated history, and the analyst who handled it has left. Reconstructing "what did we know and what governed us at the moment of decision" takes weeks per case and is never complete. I have signed responses to regulators describing 20-month-old decisions in the present tense of systems that no longer exist. That is the most uncomfortable signature I produce.

**Who has it.** Complaints and disputes teams (individual reconstructions, daily); litigation support (portfolio-scale reconstructions, catastrophically); compliance officers responding to exam and ombudsman requests about historical decisions; model risk teams asked "which decisions did model v4.1's known defect touch?"

**What the agent does.** Two halves. Going forward, it acts as decision archivist: at each origination decision it snapshots the full context — input data as-seen, model version and score, policy version, applicable overrides, the explanation as generated — into a sealed, queryable capsule (the cost is trivial at decision time; it is only ruinous retroactively). Looking backward, where capsules don't exist, it reconstructs: mines archived extracts, deployment logs, policy repositories, and change tickets to rebuild the as-of-date state, explicitly marking what is evidenced vs. inferred vs. unrecoverable. On top of both it acts as defense counsel's investigator: given a challenged decision, it produces the defense memo — decision context, governing policy at the time, consistency with contemporaneous like cases — or, just as valuably, the early honest warning that the decision is *not* defensible and should be remediated before the regulator forces it. Portfolio mode answers the model-defect question ("every decision touched by the v4.1 flaw, with materiality") in hours.

**Why newly possible now.** The forward capsule only became worth building when someone could cheaply *use* it — an agent that reads a capsule and writes a defense memo makes archiving pay. The backward reconstruction — reasoning across logs, tickets, code diffs, and policy prose to rebuild a past state — is exactly the heterogeneous-artifact reasoning that arrived with current models. And decision-defensibility demand is compounding: every AI-made origination decision from the 2024-26 deployment wave is now aging into its challenge window with no reconstruction tooling in existence.

---

*End of G3 raw ideas — 12 cards: 6 Direction A (G3-1..G3-6), 6 Direction B (G3-7..G3-12).*
