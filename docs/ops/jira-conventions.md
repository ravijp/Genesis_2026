# How we use Jira

Project **AT (Agentic Trio)** · `https://zenonai.atlassian.net` · board 209

The board is for the three of us. The committee may look at it, but we do not write it for them —
tickets that read as presentation material are worse than tickets that read as work. This file is the
standard; follow it for every issue you touch, and update it here rather than inventing a variant.

---

## 1. What belongs on the board

**On:** anything we will build, decide, measure, write or record. Including decisions and open
questions — a real board carries the things we haven't worked out yet, not only the things we've
agreed to type.

**Off:** anything whose purpose is to manage the committee relationship (chasing access, asking for
keys, explaining ourselves). Those are conversations. A ticket that exists to answer a question
someone might ask is a tell that the board is being written for an audience.

**Never:** a ticket created to look busy, or a status set to look further along than we are.

---

## 2. Titles

Plain English, understandable **without** knowing the architecture. Someone joining the team on
Monday should be able to read the board and know what the project does.

| Instead of | Write |
|---|---|
| Generative difficulty strata via Dirichlet evidence-mass split | Make some customers harder to spot than others |
| Decision schema with mandatory resolvable evidence references | Make every decision quote its evidence |
| Implement HITL write-back with suppression semantics | Feed dismissals back so the same case does not keep returning |

No jargon, no internal codenames, no rubric language, no slogans. Say what changes when the ticket is
finished.

---

## 3. Description structure

Every issue uses the same four blocks, in this order. Skip a block only when it genuinely does not
apply — an empty block is better deleted than filled with filler.

```
**Why this matters**        one or two plain sentences. The reason, not the restatement.

**What we're doing**        bullets. Concrete, and small enough that someone else could pick it up.

**Done when**               bullets, each one checkable. This is the acceptance criterion and it is
                            not optional. If you cannot write it, the ticket is not ready.

**Notes**                   optional. Findings, decisions taken, links to related work.
```

**A description that merely restates the title is worse than no description**, because it looks like
someone filled a field. If there is nothing to add, leave it blank and write a real "Done when".

### Formatting

Use Jira's rich text, not a wall of prose. Bold for the block headings and for the thing that matters
in a sentence. Bullets for anything that is a list. Blank lines between blocks. Short paragraphs.
Descriptions get read on a laptop in a meeting — make them skimmable.

---

## 4. "Done when" — the acceptance criterion

The most important field on the board, and the one that makes a second reviewer possible.

- Write it as something **observable**: a command that runs, a number that appears, a test that fails
  if the behaviour regresses.
- One line per criterion. If there are more than four, the ticket is too big — split it.
- "Works correctly" is not a criterion. "The same seed produces the same output twice" is.

Examples that pass:

- *One command generates the whole dataset from a seed and produces the same thing every time.*
- *A test proves the money actually spent stays under the cap, not just that the code noticed it went
  over.*
- *Someone outside the team reads the one-pager and can explain the idea back.*

---

## 5. Status

Four states, and we mean them literally:

| Status | Means |
|---|---|
| **To Do** | Not started. |
| **In Progress** | Being worked, **or** written but not yet reviewed by a second person. |
| **Waiting for Customer** | Genuinely blocked on someone outside the team. Use it — an empty blocker column tells the reader nothing is blocked, which is usually false. |
| **Resolved** | Built, reviewed by someone who did not write it, and the "Done when" is demonstrably true. |

**Nothing is Resolved because the author thinks it is finished.** We learned this the hard way: a
weekend of work that would have been marked Done contained a rigged demo threshold, an answer-key
leak into the agent's tools, a comparison arm that silently did nothing, and a cost cap that was never
applied. Every one of those was in code its author considered complete.

Do not batch-set statuses to make a sprint look better. A board that overstates is worth less than no
board, because everything else on it stops being believable.

---

## 6. Comments

**Findings live in comments, not in the description.** The description says what we are doing; the
comments record what we learned while doing it. That keeps the ticket readable and preserves the
history.

Comment when:

- an investigation produces a result — put the finding **and the evidence** in, not just the conclusion
- a decision is taken, with the reasoning and what was rejected
- something turns out to be harder, or unnecessary, than we thought
- a defect is found in work this ticket covers

Structure a substantive comment the same way as a description: a bold heading, bullets, a clear
recommendation. Cite sources with URLs and **absolute dates** — "accessed 2026-08-09", never
"recently".

---

## 7. Linking

Link issues rather than repeating context in both.

| Use | When |
|---|---|
| **blocks / is blocked by** | Real sequencing. B genuinely cannot start until A finishes. |
| **relates to** | Same area, no ordering. |
| **duplicates** | Say which one survives, in a comment, before closing the other. |

Every child issue belongs to exactly one epic. If it fits two, the epics are wrong.

---

## 8. Epics

Epics are the shape of the system, one per area of work, each with a plain-English name. A child that
does not obviously belong under its parent is a sign the decomposition has drifted.

An epic's description says what the area is **for**, in a couple of sentences — not a summary of its
children.

---

## 9. Sprints

Sprint boundaries follow the competition gates, not a fixed cadence:

| Sprint | Dates | Ends at |
|---|---|---|
| 2 | 2026-08-11 → 2026-08-24 | Combined Sprint 1+2 demo |
| 3 | 2026-08-25 → 2026-09-07 | Sprint 3 demo |

Everything in the current sprint has an owner and, if it is dated, a due date. Work not in a sprint
sits in the backlog — it is not "in progress by default".

---

## 10. Things that need a project admin

Neither the API token nor Ravi's account can do these. When they matter, ask:

- **Deleting issues** — returns 403. Park unwanted issues in a terminal status with a clear marker
  instead, and get them removed properly later.
- **Enabling sprints** — board 209 is a `simple` board; `/rest/agile/1.0/board/209/sprint` returns
  *"The board does not support sprints"*. Turn it on in Project settings → Features.

---

## 11. For an agent working this board

- **Never create issues to make a point.** Update what exists. Creating is close to irreversible here
  because deletion needs a permission we do not have.
- **Read before you write.** The search endpoint does not reliably return description bodies — fetch
  `/rest/api/3/issue/AT-NN?fields=description` for the real content. A previous review wrongly
  concluded every description was empty because of this.
- **Check the response of every write.** A bulk script that printed only its tail once hid 37 silent
  permission failures and left a duplicate backlog on the board.
- **Descriptions are Atlassian Document Format**, not markdown. Use the helper in
  `tools/jira/` rather than hand-building ADF.
- Verify the end state after any bulk change, and report counts.
