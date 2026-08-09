"""Atlassian Document Format builder.

Jira descriptions are ADF, not markdown, so hand-writing them produces walls of flat prose —
which is exactly what our board had. This turns a small markdown subset into real rich text:
bold headings, bullets, and paragraph breaks that survive being read on a laptop in a meeting.

Supported:
    **Heading**              a line that is entirely bold  -> bold paragraph acting as a heading
    - item                   bullet list (consecutive lines group into one list)
    plain text               paragraph
    **bold** inline          strong marks anywhere in a line
    ---                      horizontal rule
    blank line               paragraph break

Deliberately no tables, panels or code blocks: they render badly in the issue-detail sidebar,
which is where these are actually read.
"""

from __future__ import annotations

import re

_BOLD = re.compile(r"\*\*(.+?)\*\*")


def _inline(text: str) -> list[dict]:
    """Split a line into text nodes, applying strong marks to **bold** runs."""
    nodes: list[dict] = []
    cursor = 0
    for match in _BOLD.finditer(text):
        if match.start() > cursor:
            nodes.append({"type": "text", "text": text[cursor:match.start()]})
        nodes.append(
            {"type": "text", "text": match.group(1), "marks": [{"type": "strong"}]}
        )
        cursor = match.end()
    if cursor < len(text):
        nodes.append({"type": "text", "text": text[cursor:]})
    return nodes or [{"type": "text", "text": " "}]


def _paragraph(text: str) -> dict:
    return {"type": "paragraph", "content": _inline(text)}


def adf(source: str) -> dict:
    """Render the markdown subset above into an ADF document."""
    content: list[dict] = []
    bullets: list[dict] = []

    def flush_bullets() -> None:
        nonlocal bullets
        if bullets:
            content.append({"type": "bulletList", "content": bullets})
            bullets = []

    for raw in source.split("\n"):
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_bullets()
            continue

        if stripped == "---":
            flush_bullets()
            content.append({"type": "rule"})
            continue

        if stripped.startswith("- "):
            bullets.append(
                {
                    "type": "listItem",
                    "content": [_paragraph(stripped[2:].strip())],
                }
            )
            continue

        flush_bullets()
        content.append(_paragraph(stripped))

    flush_bullets()
    if not content:
        content = [_paragraph(" ")]
    return {"type": "doc", "version": 1, "content": content}


def description(
    why: str = "",
    doing: list[str] | None = None,
    done_when: list[str] | None = None,
    notes: str = "",
) -> dict:
    """Build a description in the house structure (docs/ops/jira-conventions.md).

    Empty blocks are omitted rather than rendered as headings with nothing under them.
    """
    parts: list[str] = []
    if why:
        parts += ["**Why this matters**", "", why, ""]
    if doing:
        parts += ["**What we're doing**", ""] + [f"- {d}" for d in doing] + [""]
    if done_when:
        parts += ["**Done when**", ""] + [f"- {d}" for d in done_when] + [""]
    if notes:
        parts += ["**Notes**", "", notes]
    return adf("\n".join(parts).strip())
