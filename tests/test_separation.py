"""The guard that keeps the entry honest (the build planule 5 / R2).

The most likely way this build embarrasses us on stage is a judge asking:

    "So the cumulative conversations are sub-threshold for your own matcher,
     which you also wrote?"

The answer has to be mechanical, not a promise. The extractor must be unable to see the answer
key: no import of the corpus generator, its fragment lexicon, or any ground-truth type. If
someone later "fixes" the extractor's miss rate by reaching into the corpus, these tests fail.

Do not relax them. A matcher that catches everything it planted proves nothing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import earshot

# Resolved from the INSTALLED package, not from a path walk — survives any repo layout change.
EAR = Path(earshot.__file__).resolve().parent

# Every module on the path from raw conversation to a decision. None of them may see the
# corpus side.
#
# The agent's tools are the dangerous new members of this list. A tool that derives a
# customer's transactions or account state from `CustomerTruth.outcome` would be handing the
# agent the answer key through the back door, and the whole experiment dies with it. Tools
# must derive from `latent_risk` and the seed only. Add every new tool module here.
# DISCOVERED, not listed. A hand-maintained list is one forgotten line away from a hole, and
# the hole is invisible until a judge finds it. Anything matching these globs is covered the
# moment it exists.
# Recursive, and it covers the whole decision path -- not just the obvious modules. A review
# found memory.py, arms.py, evals.py, cli.py and sweep.py all outside the old globs while
# sitting squarely between a conversation and a decision. Anything under the package that is
# not the corpus side belongs here.
# The corpus side AUTHORS the answer key.
_CORPUS_SIDE = {"corpus.py", "corpus_lexicon.py", "config.py", "schema.py"}

# The evaluation side is allowed to READ the answer key, because scoring is exactly what it
# does — you cannot measure recall without knowing what was planted. It is deliberately a
# short, named list rather than a pattern, and `test_evaluation_exemptions_stay_small`
# fails if it grows: every module added here is one more place a leak could hide.
_EVALUATION_SIDE = {
    "evals.py",   # computes recall/precision against seeded truth
    "sweep.py",   # runs evals across seeds
    "cli.py",     # orchestrates; builds ToolContext from truth (guarded separately, see
                  # tests/test_no_answer_key_leak.py, which checks it passes financial_state)
}


def _is_danger(path) -> bool:
    """Everything that turns a conversation into a decision. Not the authors of truth, and
    not the scorers of it."""
    rel = path.relative_to(EAR).as_posix()
    del rel  # membership is the only criterion; see below
    return path.name not in _CORPUS_SIDE and path.name not in _EVALUATION_SIDE


def test_evaluation_exemptions_stay_small() -> None:
    """The exemption list is the guard's weakest point. Keep it short and deliberate."""
    assert len(_EVALUATION_SIDE) <= 3, (
        f"the evaluation exemption list has grown to {sorted(_EVALUATION_SIDE)} — every entry "
        f"is a module allowed to see the answer key, so each one needs a reason"
    )


def _danger_surface() -> list[str]:
    """Every module on the path from a conversation to a decision, discovered recursively.

    `__init__.py` is INCLUDED: it can re-export anything, and excluding it was an open
    evasion route.
    """
    return sorted(
        path.relative_to(EAR).as_posix()
        for path in EAR.rglob("*.py")
        if _is_danger(path)
    )


EXTRACTOR_MODULES = _danger_surface()


def test_danger_surface_is_not_empty() -> None:
    """If the globs stop matching, every test below passes vacuously and the guard is gone."""
    assert len(EXTRACTOR_MODULES) >= 2, (
        f"discovery found only {EXTRACTOR_MODULES} — the separation guard has silently "
        f"stopped covering anything"
    )

FORBIDDEN_MODULES = {"corpus", "corpus_lexicon"}
# Lowercase module names and dynamic import were both open evasion routes: a bare
# `from .. import corpus` leaves node.module empty, and importlib bypasses the AST check
# entirely unless the name itself is forbidden.
FORBIDDEN_IDENTIFIERS = ("corpus_lexicon", "PLANTS", "DECOYS_EXTRACTOR",
                        "DECOYS_ACCUMULATOR", "BY_TYPE", "Fragment", "import_module",
                        "__import__")
FORBIDDEN_NAMES = {"SeededSignal", "CustomerTruth", "Corpus", "Stratum", "Outcome", "Fragment"}


def _imports(path: Path) -> tuple[set[str], set[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[-1])
            for alias in node.names:
                names.add(alias.name)
    return modules, names


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_cannot_import_the_corpus_side(module: str) -> None:
    modules, _ = _imports(EAR / module)
    leaked = modules & FORBIDDEN_MODULES
    assert not leaked, (
        f"{module} imports {leaked}. The extractor must not be able to see the corpus "
        f"generator or its fragment lexicon — that is the whole basis of the honesty claim."
    )


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_cannot_import_ground_truth_types(module: str) -> None:
    _, names = _imports(EAR / module)
    leaked = names & FORBIDDEN_NAMES
    assert not leaked, f"{module} imports ground-truth type(s) {leaked}."


def _code_identifiers(path: Path) -> set[str]:
    """Every identifier and non-docstring string literal in the module.

    Docstrings are excluded deliberately: this file's own modules *describe* the separation
    rule in prose, and a naive text scan would flag that prose. What matters is that no
    executable code reaches for the corpus side — e.g. a lazy `importlib.import_module` or a
    hard-coded fragment id.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))

    # Identify docstring nodes by identity — `ast.get_docstring` returns cleaned text, which
    # never compares equal to the raw Constant value.
    docstring_nodes: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstring_nodes.add(id(body[0].value))

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.alias):
            found.add(node.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstring_nodes:
                found.add(node.value)
    return found


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_code_never_reaches_for_the_answer_key(module: str) -> None:
    """Belt and braces: catch a lazy `importlib` or a hard-coded fragment table name."""
    identifiers = _code_identifiers(EAR / module)
    for forbidden in FORBIDDEN_IDENTIFIERS:
        assert not any(forbidden in i for i in identifiers), (
            f"{module} has executable code referencing {forbidden!r}"
        )


def test_offline_extractor_is_measurably_imperfect() -> None:
    """If the extractor were perfect, the corpus would be tuned to it and the eval would be
    self-referential. It must genuinely miss things."""
    from earshot.config import RunConfig
    from earshot.corpus import generate
    from earshot.evals import extraction_fidelity
    from earshot.extract import OfflineLexiconExtractor, extract_all

    run = RunConfig()
    corpus = generate(run)
    signals = extract_all(OfflineLexiconExtractor(), corpus.conversations)
    fidelity = extraction_fidelity(corpus.seeded, signals)

    assert fidelity["planted_genuine"] > 0, "corpus planted nothing to measure against"
    assert fidelity["extraction_recall"] < 1.0, (
        "the offline extractor caught 100% of planted signals — that means its cue vocabulary "
        "has been aligned to the corpus fragments, which invalidates the experiment"
    )
