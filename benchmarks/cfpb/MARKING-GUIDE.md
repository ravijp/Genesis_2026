# Marking guide — CFPB narratives, four signal types

**Frozen 2026-08-09, before any narrative was read.** Written from the construct definitions in
`src/earshot/schema.py` and `sources/submission-ear-on-every-call.md` line 58 — *"intent to leave,
money stress, a life event, a repeated complaint"* — and **not** from the extractor's cue vocabulary.
Every worked example below is invented for this document. None comes from the sample, which had not
been drawn when this was written.

If you are the second marker: mark from **this file only**. Do not open
`src/earshot/extract_lexicon.py` or `src/earshot/extract.py`. Marking against the thing being measured
is the one mistake that would make the whole benchmark worthless.

---

## 1. The unit and the output

One CFPB narrative is one document. For each document, record **which of the four types it expresses**
— zero, one, or several. The types are **not mutually exclusive**: a narrative about being made
redundant and falling behind on a mortgage expresses two.

For every type you mark present, record the **verbatim span** that made you mark it. One span is
enough; quote the strongest. A mark without a span is not a mark.

```json
{"complaint_id": "12345678",
 "marks": {"financial_distress": true, "churn_intent": false,
           "complaint_escalation": true, "life_event": false},
 "spans": {"financial_distress": "I have been unable to make the minimum payment since XXXX",
           "complaint_escalation": "this is the fourth time I have contacted them about this"},
 "notes": "borderline: see rule 2.3"}
```

## 2. The four constructs

### 2.1 `churn_intent` — the customer signalling they may leave or reduce the relationship

**Mark present when the customer expresses, about themselves,** an intent or active consideration to
end, reduce or move the relationship: closing their account, moving money or a direct deposit
elsewhere, switching provider, comparing competitors with intent, refinancing away, or saying they
will not use the product again.

**Do not mark when:**

- **The firm closed or restricted the account.** De-banking, "they closed my account with no notice",
  account freezes. This is the *opposite* of the customer choosing to leave, and it is common in this
  data. Expect to reject many of these.
- The account being closed is one the customer **never opened** — fraud, identity theft, an
  unauthorised account.
- Closure is purely administrative with no dissatisfaction and no alternative provider — e.g. a
  request to close a duplicate account or a deceased relative's account.
- The customer is only threatening to complain further (that is 2.3), or expressing anger without any
  reference to the relationship ending.

> Invented example — **mark**: *"After thirty years I am moving my direct deposit to a credit union
> next month."*
> Invented example — **do not mark**: *"They closed my checking account without warning and mailed me
> a cheque for the balance."*

### 2.2 `financial_distress` — money stress affecting the customer's ability to meet obligations

**Mark present when the customer describes** difficulty paying, missed or late payments driven by
shortage of money, income loss or reduction, being overdrawn or out of funds, borrowing to cover
essentials, juggling bills, hardship-programme requests, or fear of default, repossession or
foreclosure.

**Do not mark when:**

- The complaint is about a **charge being wrong**, not about being unable to afford it. A disputed fee,
  an unexpected interest rate, or a billing error is not distress on its own.
- The customer is describing **someone else's** money trouble.
- The hardship is entirely in the past **and explicitly resolved** — "I was out of work in 2019 but
  I've been steady since."
- The inability to pay is a **deliberate withholding** in protest rather than a shortage of money —
  "I refuse to pay this until they fix it."

> Invented example — **mark**: *"The overdraft fees took my balance to negative XXXX and I could not
> buy groceries that week."*
> Invented example — **do not mark**: *"They charged me a $35 fee that I do not believe I owe."*

### 2.3 `complaint_escalation` — a problem the customer has raised before and that is still unresolved

**Mark present when the narrative shows repeat contact with the firm about the same problem:** an
explicit count ("the third time I've called"), a prior reference or case number, a promised callback
that did not come, a prior complaint that was closed without a fix, or being passed between
departments over the same issue.

**Do not mark when:**

- The only escalation is **the CFPB complaint itself.** Every document in this corpus is a complaint
  to a regulator. If filing counted, this type would be trivially present everywhere and the mark
  would carry no information. **The escalation must be to the firm, and prior to this filing.**
- The customer contacted the firm once and is dissatisfied with the answer.
- Multiple contacts are about **different** problems.

> Invented example — **mark**: *"I called on XXXX and again on XXXX, was given reference XXXX, and
> nobody has called me back."*
> Invented example — **do not mark**: *"I am writing to the CFPB because the bank refused my claim."*

### 2.4 `life_event` — a change in the customer's circumstances outside the banking relationship

**Mark present when the customer mentions** bereavement, divorce or separation, job loss or a change
in employment, serious illness or disability, a new child, a house move, retirement, or military
deployment — **as something happening to them or their household.**

**Do not mark when:** it happened to a third party with no effect on the customer, it is purely
hypothetical, or it is a historical aside with no bearing on the account.

> Invented example — **mark**: *"My husband passed away in XXXX and I am trying to close his account."*
> Invented example — **do not mark**: *"My neighbour went through the same thing when she got
> divorced."*

**Note on overlap, and it matters.** Job loss is *both* a life event and a driver of money stress. Mark
**both** when both are expressed. Do not suppress one to make the taxonomy tidy — §4 explains how the
scoring handles it, and suppressing would be bending the answer key toward the tool.

## 3. Decision rules that cut across all four

1. **Mark what the customer says about themselves, in the present or recent past.** Third-party
   attribution, hypotheticals ("if I were to..."), and explicitly resolved history are not marks.
2. **Mark the construct, not the vocabulary.** If a narrative conveys money trouble without using any
   obvious distress word, it is still a mark. This is the whole point of the exercise.
3. **`XXXX` redactions stay as published.** Do not guess what was removed. If a redaction destroys the
   only evidence for a type, do not mark that type, and note it.
4. **When genuinely undecidable, do not mark, and write why in `notes`.** A false negative in the gold
   set is visible in adjudication; a generous mark silently inflates the extractor's apparent misses.
5. **Read the whole narrative before marking.** Some are long and the decisive sentence is often last.
6. **Never run the extractor on a document before its mark is committed.**

## 4. How marks become numbers, and the one asymmetry to know about

Scoring is per `(document, signal_type)` pair, matching `src/earshot/evals.py:198-200`.

- **Strict recall (primary).** The extractor must fire the **same type** the gold marks. This is the
  identical question the published synthetic number answers, which is why it is primary.
- **Any-type recall (declared secondary).** Did the extractor fire *anything* on a document the gold
  marked positive for *anything*? Reported separately, never as the headline.

The secondary exists because of one known taxonomy disagreement, declared here in advance: our
extractor files **job loss under `financial_distress`**, whereas §2.4 tells a marker to record it as a
`life_event` (and §2.2 as distress too, when the money consequence is stated). Where those diverge, the
strict number will count a miss even though the reader saw the sentence. The gap between strict and
any-type is precisely the size of that class of disagreement, and reporting both separates *"the reader
did not see it"* from *"the reader saw it and called it something else."* Those are different defects
with different fixes, and a single number hides which one you have.

The guide is **not** adjusted to match the extractor's taxonomy. Doing that would be authoring the
answer key from the tool being tested.

## 5. Second marker and adjudication

A random 30 of the 150 are marked independently a second time, blind to the first marks and to the
extractor. Then:

- Cohen's κ is reported **per type** with its denominator, not as one pooled figure.
- Every disagreement is adjudicated in writing against the rule that resolves it, and the adjudicated
  mark is the one used. If no rule resolves it, the rule was missing — record that as a limitation
  rather than inventing the rule after the fact.
- **Adjudication happens before either mark set meets the extractor.**

## 6. Known weaknesses of this scheme

- The first marker has read the extractor's cue vocabulary. See `PROTOCOL.md` §5.
- The second marker is a model instance, not a second person. See `PROTOCOL.md` §5.
- Marking is at document level, so a narrative expressing a type three times counts once. That matches
  how the synthetic number is computed, and it understates nothing that the synthetic side reports.
- `life_event` has no CFPB metadata handle, so its denominator comes from natural occurrence only and
  is expected to be small. It will be reported with its integers however small it is, and never pooled
  away into an average.
