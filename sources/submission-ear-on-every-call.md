# SUBMISSION — Ear on Every Call (verbatim)

`[source]` — **Do not edit.** Verbatim text of `Ear-on-Every-Call-Idea-Overview.docx`, the finalized
Track A idea sent by Ishant Gupta to the Genesis Committee on **2026-07-24 22:40**, cc Ravi Prakash,
Namit Mittal, Bharti Sahai. This document is the contract with the committee. The covering email
reserved room for refinement: *"the attached overview is the first version of our solution approach.
As we build over the next 6 weeks, we expect the solution to be refined, so some details may differ a
little from what is described in the attachment."*

Deltas between this document and what we actually build are logged in
[`04_architecture/BUILD-PLAN.md`](../04_architecture/BUILD-PLAN.md) §10.

---

## Ear on Every Call

*A conversation signal layer that remembers every customer, across every conversation.*

Genesis 2026, Track A (client-facing agentic AI). A horizontal capability for banks, card issuers,
lenders, credit unions, insurers, and wealth firms. Built and shown on synthetic data.

### Problem statement

Every financial institution runs millions of customer conversations a year: phone calls, chats, and
complaints. These conversations are the first place a customer tells you something is wrong. "I am
thinking of moving my money." "This is the third time I have called about this fee." "I just lost my
job." It is the earliest and richest warning the institution ever gets.

Today almost none of that signal reaches anyone who can act. Quality teams listen to a tiny sample of
calls to score agents. The rest is transcribed, filed, and forgotten. The bank paid to record the
conversation and then threw away the part that mattered.

The tools banks already own make this worse, because of how they are built. Call analytics,
agent-assist, and complaint systems all work inside a single call, a single chat, or a single channel.
When a call ends and gets a score, the signal is archived. It is not carried forward to the next call,
the next channel, or the next agent. So a customer can show frustration in a chat in March, raise a
complaint in May, and call to threaten leaving in July, and the bank treats all three as separate
events. It never notices they are the same customer, getting closer to the door.

This is not a call-center problem or a single-team problem. It is a gap in how the whole institution
listens. Retention, complaints, product, and risk teams all need the same signal from the same
conversations, and none of them get it in a usable form. The bank reads every conversation but
remembers no customer.

This is worth solving now for three reasons. Call volumes in financial services are rising fast, so
sampling falls further behind every quarter. Most contact-center leaders now have AI budget approved,
with better customer insight their top priority. And modern AI can finally read every conversation
cheaply, instead of keyword-spotting a small sample. The money and the technology are both here.

### Proposed solution

A shared "conversation signal layer" that sits over all customer conversations and turns them into a
living, per-customer memory that any team can use. Four parts:

**Listen.** Read 100% of conversations (calls as text, chats, complaints), not a sample. It runs as an
overnight batch, so the cost that matters is cost per conversation, not speed on a live call.

**Extract the signal.** Pull out what the customer told us (intent to leave, money stress, a life
event, a repeated complaint) with a confidence score and the exact quote and timestamp behind it.

**Remember and re-score (the heart of it).** Keep a running record for each customer that adds up
signals across conversations, channels, and time, and re-scores them as new conversations arrive. A
weak signal today plus a weak signal next month can add up to a strong one. This standing,
cross-channel memory is the part that does not exist today.

**Serve and act.** One queryable feed that many teams read at once. A person always decides what to do.
The system never contacts a customer on its own.

**What is new here, said honestly.** Reading a call and tagging its sentiment or compliance risk is a
solved, commodity job that several vendors already do well. We are not reinventing that. What none of
them keep is a customer-level memory that accumulates and re-scores signals across every conversation
over time. They score the call and archive it. We remember the customer. That is our wedge, and we
treat it as a capability gap we close first, not as something no one could ever copy.

**How we prove it.** To show this is a horizontal layer and not a single tool, three teams read the
same feed in the demo: a Retention view (the lead), a Risk and Compliance view, and a Commercial view,
all lit up for the same customers. The key moment: one customer has three ordinary-looking
conversations weeks apart, none alarming on its own. Only after the third does the running score cross
into "high churn risk," something no single-conversation tool would catch.

**Technical approach and evals.** Ground truth comes from a synthetic multi-channel corpus (calls,
chats, complaints) with signals seeded in before the text is written, so the answer key is known
(synthetic data only, per competition rules). The number that proves the idea is signal recall against
a per-call baseline: how many of the seeded signals the memory surfaces versus a tool that scores each
call alone and forgets it. We also report the false-positive rate on deliberately seeded throwaway
remarks, plus cost per 1,000 conversations and batch latency. Claude does the reading and re-scoring; a
comparison model runs through the same harness so the numbers are honest. Plain code, not the model,
does the customer matching and the re-score math, so that logic is testable and reproducible.

### Target user and client

**Users:** the teams that read the feed and act on it: retention, complaints and compliance, product,
and risk. Each gets a ranked queue of decision-ready cases with the conversations that built them.

**Lead buyer:** the VP or SVP of Contact Center Operations, or the Chief Customer Experience Officer.
They own the contact-center and CX budget and are measured on retention and complaint-driven risk. One
feed serves several teams, so it is one purchase with many owners.

**Co-signer:** the Chief Compliance Officer, who signs off on anything that touches 100% of
conversations, so the coverage and privacy story is built in from day one.

**Clients:** retail banks and card issuers first (highest conversation volume and regulatory exposure),
then credit unions and regional banks. The same capability extends to lenders, insurers, and wealth
firms, because every one of them loses customers and hears it first in a conversation.

**Anchor metric:** signals surfaced and acted on before the outcome, measured as the retention lift in
the flagged group against a matched control.

**One layer, many teams.** The same feed can serve retention, compliance, early product signals, risk
and early-warning, collections, and quality review of every call. None of these is the headline; the
layer is.

### Sprint plan (three sprints)

**Sprint 1 — Data, extraction, and the proof scenario.** Build the synthetic multi-channel corpus with
seeded ground truth. Build the signal-extraction pipeline and run it at full volume. Show first recall
and precision numbers. Build and rehearse the three-conversation accumulation scenario early, since it
is the whole story.

**Sprint 2 — The memory and the reviewer screen.** Build the per-customer ledger and the re-scoring
logic as a pure, tested function. Stand up the human-review queue with approve, dismiss, and route
actions. Get two of the three team views working. Show cost and latency next to accuracy.

**Sprint 3 — Horizontal proof and readiness.** All three team views live on the same feed. The
accumulation demo rehearsed and recorded as a fallback. Full eval numbers (accuracy, cost, latency) in
the README. Two dry runs done. Write the path-to-production plan.

**Path to production.** The layer reads existing conversation feeds, writes signals into a queue each
team already uses, and keeps a human in front of every action. It adds a memory on top of tools banks
already run, rather than replacing them, which keeps integration light.
