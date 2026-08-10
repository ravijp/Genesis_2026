# Access request emails — ready to send

Two separate emails. Short and direct on purpose: these are requests, not status reports.

---

## 1 · Model APIs and infrastructure

**To:** genesis@zenon.ai
**Cc:** Ishant Gupta; Namit Mittal; Bharti Sahai; Suyash Baderiya; Novnit Kashyap; Riya Gupta
**Subject:** Agentic Trio — tooling and access requirements

Hi Genesis Committee,

Our tooling and access requirements for Track A (*Ear on Every Call*):

**Model APIs**

1. **Claude API key** — primary model, for signal extraction and the investigator agent.
2. **OpenAI API key** — the comparison model. Our brief commits to running a second model through the
   same eval harness, which needs two providers.
3. **Direct vendor APIs or AWS Bedrock?** Please confirm which route you intend, so we build against
   the right one.
4. **The per-team budget limit, as a number** — we batch-process a conversation corpus and want to size
   our eval runs to the budget.

**AWS**

5. **S3 bucket** — generated corpora, model-response caches, and per-run eval artifacts.
6. **Bedrock access**, if that is the model route (see 3).

Nothing else. The runtime is a nightly batch job with no always-on infrastructure; if that changes we
will come back.

Thanks,
Ravi

---

## 2 · CodeCommit credentials and Jira delete permission

**Send as a reply to:** Ashwani Kaushik (Zenon Helpdesk), thread *"Team Agentic Trio – GenAI Competition
| Jira Project & Git Repository"*, 2026-07-10
**Cc:** Abhishek Pradhan; Ishant Gupta; Namit Mittal
**Subject:** RE: Team Agentic Trio – GenAI Competition | Jira Project & Git Repository

Hi Ashwani,

Two access requests, both on the project and repository below.

**1. AWS CodeCommit credentials.** We have the repository URL but no credentials, so we cannot push.
Could you provide:

- HTTPS Git credentials for CodeCommit, or an IAM user/role we can configure with
  `git-remote-codecommit`
- Whichever of the two the other teams are using, so we match

Repository: `https://git-codecommit.us-east-1.amazonaws.com/v1/repos/agentic-trio`

**2. Delete permission on Jira project AT.** We can create, edit and transition issues but not delete
them. We have some duplicate issues to clear out and cannot remove them. Could you grant delete
permission to Ishant Gupta, Namit Mittal and me?

While you are in the project settings — could you also **enable Sprints** on board 209? It is currently
a Kanban-style board that does not support sprints, and our milestones are Sprint 1/2/3.

Thanks,
Ravi

---

## Notes for us — not part of either email

- **CodeCommit has existed since 2026-07-10**, provisioned by Zenon Helpdesk in the same email that gave
  us the Jira board. Only credentials are missing. Our full commit history is intact and pushes as
  history, not as one squashed commit.
- **The comparison model is a stated deliverable**, not a nice-to-have — the submitted brief promises a
  second model through the same harness in writing.
- Model access is currently bridged on a personal OpenRouter account. That is fine for development and
  wrong for the final submission: competition rule 1 puts the IP with Zenon and rule 2 says Zenon
  supplies the keys. Switching providers is a new provider class behind the existing interface.
