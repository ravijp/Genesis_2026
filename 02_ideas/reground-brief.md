# Re-grounding Brief (T14) — from Ravi's v2 review, 2026-07-15

**Status: OPEN — this brief is the executable spec for the next working session.** Round-1 lock is HOLD until this pass lands. Kickoff prompt at the bottom.

## Why (Ravi's review, distilled)

1. **Schedule truth:** Jul-20 demo date is defunct. Plan = 6 build-weeks from idea-freeze to a heavily-scoped MVP; scoping must not cap the use-case capability story.
2. **The gap in v2:** the north stars are second-order agentic — they supervise, arbitrate, or negotiate with agents. **Our clients have zero agents in production.** Slices that presuppose agentic infrastructure are 2-3 years ahead of Barclays/HNB/WAB/ampliFI reality; the felt need is absent, and where the need eventually appears, the solutions may be quick for others to replicate. The vision layers are directionally right; the *entry points* are wrong.
3. **Client-check fails as written:** the named anchors would not pay for the current slices as POCs today.
4. **Demo-check:** impressive in theory, but the *surface these demos run on* doesn't exist at our clients — the demo must not presuppose a world the audience doesn't live in.
5. **Appetite gate:** the team is at 100% core utilization; a concept earns the 6-week sleep loss only if it has a visible **aha / sales / winner** moment.
6. **Judge model:** the panel is SaaS-minded leadership just learning agentic. Expect basic-then-suddenly-hard questions. Every finalist concept must have ready, grounded answers to the **standing question checklist**: user story · what it takes to run it · infrastructure required · will the client pay (and what) · how it scales · vision (dreamy vs. realistic) · evals · guardrails · failure handling + logging · cost · latency · dollar impact (or hard proxy metric).

## The rules this pass must apply

- **Two-horizon rule.** Every concept carries BOTH: (a) a **DAY-1 STORY** — works at a client with **no agents in production**: named persona, trigger, end-to-end user story, artifact produced, who pays, dollar-impact path, and "runs on what" (data/systems actually available at that client today); (b) the **VISION ARC** (keep from v2 — this is the 2-3 year story that shows we see where it goes). A concept with no honest day-1 story re-tiers as a **horizon bet** — kept for vision/originality color, never the lead pitch.
- **Balance requirement.** The portfolio must pair grounded first-order use cases with the visionary ones. Resurrect/re-examine the grounded R-clusters for the day-1 track — strongest candidates: R-001 (collections case worker — live Barclays engagement), R-004/R-005 (HOA cash-application + lien, WAB white space), R-009 (KYC/AML disposition QC), R-017/R-027 (fraud-ring investigation), R-032 (returns fraud, if scope ever widens). The likely winning shape: **one grounded doer workflow + exactly one second-order differentiator layered on it** (e.g., N-004 already is this: a first agent + earned-autonomy machinery; or R-001 + an N-001-lite audit ledger). The differentiator answers "why is this not just SaaS"; the doer answers "why would my client pay this quarter."
- **Day-1 reframes to apply (already identified):** N-004 survives nearly as-is (it *introduces* the first agent; presupposes nothing). N-008 reframes from "agent remediation" to **remediation of any automated decision** (rules engines, models, policies — decades of installed base; the Klarna/fee-waiver story works without a single agent). N-005 and N-012 are day-1 real by construction. N-001's day-1 entry = supervise the client's *existing* automated decisions and human ops (collections QA), or ship as the audit layer of our own doer build. N-002/N-009 = horizon bets unless a day-1 wedge is found (their visions stay; Visa's own rails momentum is the one possible near-term surface). N-003's day-1 entry = offer red-teaming on today's promotions (no agents required); the agent-authenticity half is the horizon layer.
- **Appetite gate:** every proposed lead concept names its aha/sales/winner moment in one sentence. If the author can't, it doesn't lead.
- **Question checklist:** every carded concept gets the §Why-6 checklist answered in the card (this becomes the T6 card template addition — T13).
- **Standing constraints:** evidence-based with dated citations; igupta branch stays quarantined (lock not declared); synthetic data with seeded ground truth; agent policy — ≤3 concurrent, sonnet default, fable only for the make-or-break judging/vision steps, opus for deep scrutiny; resumable via a RUNSTATE manifest if agents are used.

## Deliverables of the re-grounding session

1. **`north-stars.md` v3:** every concept restructured to two-horizon form (DAY-1 STORY + VISION ARC + user story + checklist answers); re-tiered honestly (grounded leads vs. horizon bets); ELI5 lines kept.
2. **A "grounded track" section or file:** the resurrected first-order use cases with day-1 stories, and 2-3 **combined pitches** (doer + one differentiator layer) as the likely build candidates.
3. **Revised scoreboard** reflecting the corrected judge model (SaaS-minded leadership), with the appetite-gate one-liners.
4. **Updated board:** T12 lock decision re-armed with the new pool; T6 card template gains the question checklist (T13).
5. Everything committed; INDEX + worklogs updated same commit.

## Kickoff prompt for the fresh session (paste as-is)

> Read `CLAUDE.md`, `INDEX.md`, then `PLAN.md` (decision log, 2026-07-15 entries) and `02_ideas/reground-brief.md` — the brief is your executable spec; follow its rules exactly (two-horizon rule, balance requirement, judge model, appetite gate, question checklist, standing constraints). Inputs to read before writing: `02_ideas/north-stars.md` (v2 — vision layers to keep, slices to re-ground), `02_ideas/backlog.md` (finance clusters incl. review notes — the grounded-track source), `00_sources/zenon-client-context.md`, `01_research/finance.md`. The 2026-07-15 temp workdir `C:\tmp\genesis-review-2026-07-15\` has supporting analysis if needed (judge reports, collision scan, kill-pass). Deliver the brief's five deliverables. Work main-session-first; use agents only where the brief's agent policy allows and only if they genuinely add contrast (e.g., one fable pass to pressure-test the combined pitches through the SaaS-minded-leadership judge lens). Do not read the igupta/ideation-and-research branch. When done, present the revised scoreboard + the 2-3 combined pitches and ask Ravi for the lock call.
