"""Prompts as versioned files on disk, so a prompt change is a reviewable diff.

Two families live here: `investigator/` (the agent that works a flagged case) and `extractor/`
(the model that reads one conversation). Both load through the same code because both put a
prompt sha into the response-cache key and into a run manifest — that is what makes "this
recorded response was produced by this prompt" checkable rather than asserted. Edit a prompt
file and every cached response for the old text stops being served.

Nothing here may import the corpus side. See tests/test_separation.py.
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
    return Path(__file__).resolve().parents[2] / "prompts"


@lru_cache(maxsize=None)
def load_prompt(
    family: str, name: str, version: str = DEFAULT_VERSION
) -> tuple[str, str, str]:
    """Returns `(text, version, sha256)` for `prompts/<family>/<version>/<name>.md`."""
    path = prompts_root() / family / version / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(
            f"prompt not found: {path}. Set EARSHOT_PROMPTS to the directory holding "
            f"{family}/{version}/."
        )
    text = path.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, version, sha


def prompt(family: str, name: str, version: str = DEFAULT_VERSION) -> Prompt:
    text, resolved, sha = load_prompt(family, name, version)
    return Prompt(name=name, text=text, version=resolved, sha256=sha)


def pair_sha(*prompts: Prompt) -> str:
    """One sha covering several prompt files, for the cache key and the manifest."""
    return hashlib.sha256(":".join(p.sha256 for p in prompts).encode()).hexdigest()


def render(template: str, **slots: object) -> str:
    """Fill `{{slot}}` placeholders. Deliberately not str.format — the templates contain JSON
    braces, and a format-string collision in a prompt is a silent, ugly failure."""
    out = template
    for key, value in slots.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out
