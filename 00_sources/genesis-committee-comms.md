# GENESIS COMMITTEE — dates, access, and commitments

`[source]` — extracted from the Genesis email thread screenshots (`Genesis_SS.docx`, 5 images).
Facts only; interpretation lives in [`04_architecture/BUILD-PLAN.md`](../04_architecture/BUILD-PLAN.md).

## Team and entry

- **Team name:** Agentic Trio — Ishant Gupta, Namit Mittal, Ravi Prakash.
- **Entry:** Track A, *"Ear on Every Call"* — finalized and submitted **2026-07-24 22:40** by Ishant
  Gupta to the Genesis Committee (cc Ravi Prakash, Namit Mittal, Bharti Sahai), with a 1-2 page idea
  overview attached. Verbatim text preserved at
  [`submission-ear-on-every-call.md`](submission-ear-on-every-call.md).
- Covering email states the overview is a first version and the solution is expected to be refined over
  the six build weeks, so some details may differ.

## Sprint / demo dates — FROZEN

From Bharti Sahai (Staffing Manager), competition kickoff email, and reaffirmed **2026-08-07**:

| Gate | Date | Status |
|---|---|---|
| Sprint 1 | **2026-08-10** | Downgraded to a **15-minute check-in**, 10:30-10:45, MS Teams |
| Sprint 2 | **2026-08-24** | **Combined Sprint 1 + Sprint 2 demo** |
| Sprint 3 | **2026-09-07** | As scheduled |

**How the Sprint-1 downgrade happened.** Ravi Prakash wrote to the committee **2026-08-07 16:56**: the
group had been tied up with existing client engagements and had not been able to pick up work on the
Genesis idea yet; requested moving the demo to Monday 2026-08-17. Suyash Baderiya replied **2026-08-07
17:04**: *"Given the finals dates are frozen, we cannot move the sprint deadlines. However, keeping
your situation in mind, we can have a check in on the scheduled time for Sprint 1, and have a combined
demo for Sprint 1 + 2 in the next meeting."*

**Consequence:** the 2026-08-24 gate carries **both** sprints' scope. Finals dates are frozen and were
the stated reason the deadlines could not move.

## What the 2026-08-10 check-in expects

From the Sprint Demo-1 invite (Genesis, sent **2026-08-03 12:30**; Mon 2026-08-10 10:30-10:45, MS
Teams; attendees Ishant Gupta, Namit Mittal, Ravi Prakash, Novnit Kashyap, Suyash Baderiya, Riya
Gupta):

- Progress against the sprint plan — **what was committed versus what has been completed**.
- If anything is pending, be ready to walk through **the reasons and next steps**.
- **Flag any roadblocks.**
- Explicitly *not* a Jira-ticket walkthrough: *"this is a check-in, not a detailed audit."*

## Tooling and access

From the kickoff email *"Action Needed by July 24: Tooling Access + Sprint Demo Dates"* (Importance:
High), chased again **2026-07-29 14:08** because several teams had not replied:

- **Already provisioned for all teams:** AWS CodeCommit, JIRA.
- **Available on request, by 2026-07-24:** OpenAI API access · Claude API access · any other AWS
  services (EC2, S3, Lambda, etc.) · any other tools, libraries or services the team anticipates
  needing.
- Stated rationale: *"Once you share your requirements, we will set up the accesses accordingly to
  avoid delays later in the competition."*

**Status as of 2026-08-09:** no model API keys available on the build machine. This is the entry's
top-ranked risk (BUILD-PLAN §8, R1) and the primary roadblock to raise at the 2026-08-10 check-in.

## Judging

Official weights: Zenon impact 25 · technical depth 25 · feasibility & production readiness 25 ·
originality 15 · presentation 10 — plus an AI judge scoring engineering quality (evals,
reproducibility, accuracy/cost/latency evidence). Full detail in
[`kickoff-notes.md`](kickoff-notes.md).
