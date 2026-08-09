"""The investigator's prompt files.

Loading, hashing and `{{slot}}` rendering all live in `earshot.prompt_files`, which the model
extractor uses too. This module is the investigator's view of it: the family name in one place,
so a caller cannot address the wrong prompt directory by typo.
"""

from __future__ import annotations

from ..prompt_files import DEFAULT_VERSION, Prompt, pair_sha, prompts_root, render
from ..prompt_files import load_prompt as _load_prompt

FAMILY = "investigator"

__all__ = [
    "DEFAULT_VERSION",
    "FAMILY",
    "Prompt",
    "investigator_prompts",
    "load_prompt",
    "prompt",
    "prompts_root",
    "render",
]


def load_prompt(name: str, version: str = DEFAULT_VERSION) -> tuple[str, str, str]:
    """Returns `(text, version, sha256)` for `prompts/investigator/<version>/<name>.md`."""
    return _load_prompt(FAMILY, name, version)


def prompt(name: str, version: str = DEFAULT_VERSION) -> Prompt:
    text, resolved, sha = load_prompt(name, version)
    return Prompt(name=name, text=text, version=resolved, sha256=sha)


def investigator_prompts(version: str = DEFAULT_VERSION) -> tuple[Prompt, Prompt, str]:
    """System prompt, task template, and a combined sha covering both."""
    system = prompt("system", version)
    task = prompt("task", version)
    return system, task, pair_sha(system, task)
