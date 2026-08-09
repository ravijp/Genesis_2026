"""Prompts as versioned files on disk, so a prompt change is a reviewable diff.

The sha256 of each file goes into the response-cache key and into the run manifest. That is
what makes "this recorded run was produced by this prompt" checkable rather than asserted — edit
`system.md` and every cached response for the old prompt stops being served.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_VERSION = "v1"


@dataclass(frozen=True)
class Prompt:
    name: str
    text: str
    version: str
    sha256: str


def prompts_root() -> Path:
    """`EARSHOT_PROMPTS`, else ./prompts, else the repo checkout this package was installed from.

    The last fallback matters: `uv run pytest` from any directory must still find the prompts,
    and a cwd-relative path alone would make that a coin toss.
    """
    # Both spellings are honoured: an override that is silently not read points the loader at
    # nothing, with no error to say why.
    override = (
        os.environ.get("EARSHOT_PROMPTS") or os.environ.get("EAR_PROMPTS") or ""
    ).strip()
    if override:
        return Path(override)
    cwd = Path("prompts")
    if cwd.is_dir():
        return cwd
    return Path(__file__).resolve().parents[3] / "prompts"


@lru_cache(maxsize=None)
def load_prompt(name: str, version: str = DEFAULT_VERSION) -> tuple[str, str, str]:
    """Returns `(text, version, sha256)` for `prompts/investigator/<version>/<name>.md`."""
    path = prompts_root() / "investigator" / version / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(
            f"prompt not found: {path}. Set EARSHOT_PROMPTS to the directory holding "
            f"investigator/{version}/."
        )
    text = path.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, version, sha


def prompt(name: str, version: str = DEFAULT_VERSION) -> Prompt:
    text, resolved, sha = load_prompt(name, version)
    return Prompt(name=name, text=text, version=resolved, sha256=sha)


def investigator_prompts(version: str = DEFAULT_VERSION) -> tuple[Prompt, Prompt, str]:
    """System prompt, task template, and a combined sha covering both."""
    system = prompt("system", version)
    task = prompt("task", version)
    combined = hashlib.sha256(f"{system.sha256}:{task.sha256}".encode()).hexdigest()
    return system, task, combined


def render(template: str, **slots: object) -> str:
    """Fill `{{slot}}` placeholders. Deliberately not str.format — the templates contain JSON
    braces, and a format-string collision in a prompt is a silent, ugly failure."""
    out = template
    for key, value in slots.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out
