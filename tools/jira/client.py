"""Minimal Jira client for project AT.

Every write reports its own result. A previous bulk script printed only the tail of its output
and silently swallowed 37 permission failures, leaving a duplicate backlog on the board — so
`Jira.failures` is checked and printed by every caller.

Credentials: `JIRA_EMAIL` / `JIRA_TOKEN`, or `JIRA_TOKEN_FILE` pointing at a file containing
the token. Never hard-code a token and never print one.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = os.environ.get("JIRA_BASE", "https://zenonai.atlassian.net")
PROJECT = os.environ.get("JIRA_PROJECT", "AT")

# Transition ids for this project's workflow. There is no "Done" — the terminal state is
# "Resolved" (see docs/ops/jira-conventions.md §5).
TODO = "11"
IN_PROGRESS = "21"
WAITING = "31"
RESOLVED = "41"


def _token() -> str:
    if os.environ.get("JIRA_TOKEN"):
        return os.environ["JIRA_TOKEN"].strip()
    path = os.environ.get("JIRA_TOKEN_FILE", "C:/tmp/atlassianAPIToken.txt")
    return Path(path).read_text(encoding="utf-8").strip()


class Jira:
    def __init__(self, email: str | None = None) -> None:
        email = email or os.environ.get("JIRA_EMAIL", "rprakash@zenon.ai")
        auth = base64.b64encode(f"{email}:{_token()}".encode()).decode()
        self._headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.failures: list[str] = []

    # -- plumbing ---------------------------------------------------------------
    def _call(self, method: str, path: str, body: dict | None = None, label: str = ""):
        req = urllib.request.Request(
            f"{BASE}{path}",
            method=method,
            data=json.dumps(body).encode() if body else None,
            headers=self._headers,
        )
        try:
            with urllib.request.urlopen(req) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read()[:200].decode(errors="replace")
            self.failures.append(f"{label or path}: {exc.code} {detail}")
            return None

    # -- reads ------------------------------------------------------------------
    def search(self, jql: str, fields: str = "summary,status,issuetype,parent") -> list[dict]:
        query = urllib.parse.urlencode(
            {"jql": jql, "maxResults": 100, "fields": fields}
        )
        result = self._call("GET", f"/rest/api/3/search/jql?{query}", label="search")
        return (result or {}).get("issues", [])

    def issue(self, key: str, fields: str = "summary,description,status") -> dict | None:
        """Fetch one issue. The search endpoint does not reliably return description bodies —
        always come here for real content."""
        return self._call("GET", f"/rest/api/3/issue/{key}?fields={fields}", label=f"get {key}")

    # -- writes -----------------------------------------------------------------
    def set_summary(self, key: str, summary: str) -> None:
        self._call("PUT", f"/rest/api/3/issue/{key}", {"fields": {"summary": summary}},
                   f"summary {key}")

    def set_description(self, key: str, doc: dict) -> None:
        self._call("PUT", f"/rest/api/3/issue/{key}", {"fields": {"description": doc}},
                   f"description {key}")

    def set_due(self, key: str, date: str) -> None:
        self._call("PUT", f"/rest/api/3/issue/{key}", {"fields": {"duedate": date}},
                   f"duedate {key}")

    def transition(self, key: str, transition_id: str) -> None:
        self._call("POST", f"/rest/api/3/issue/{key}/transitions",
                   {"transition": {"id": transition_id}}, f"transition {key}")

    def comment(self, key: str, doc: dict) -> None:
        self._call("POST", f"/rest/api/3/issue/{key}/comment", {"body": doc}, f"comment {key}")

    def link(self, blocker: str, blocked: str, kind: str = "Blocks") -> None:
        """`blocker` blocks `blocked`.

        Jira's naming is the trap here: for the "Blocks" type the OUTWARD issue is the one
        that *is blocked*, and the INWARD issue is the blocker. Getting this backwards produced
        six links that all pointed the wrong way — a write-up blocking the experiment that
        produced it, and a demo recording blocking the demo. Verify direction after creating.
        """
        self._call(
            "POST",
            "/rest/api/3/issueLink",
            {
                "type": {"name": kind},
                "inwardIssue": {"key": blocker},
                "outwardIssue": {"key": blocked},
            },
            f"link {blocker} blocks {blocked}",
        )

    def delete_link(self, link_id: str) -> None:
        self._call("DELETE", f"/rest/api/3/issueLink/{link_id}", label=f"unlink {link_id}")

    # -- reporting --------------------------------------------------------------
    def report(self) -> None:
        if self.failures:
            print(f"\n{len(self.failures)} FAILURES:")
            for failure in self.failures:
                print("  !!", failure)
        else:
            print("\nNo failures.")
