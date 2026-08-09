"""The guard that keeps the entry honest (BUILD-PLAN Rule 5 / R2).

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

EAR = Path(__file__).resolve().parent.parent / "ear"

# Modules that make up the extraction path. None of them may see the corpus side.
EXTRACTOR_MODULES = ("extract.py", "extract_lexicon.py")

FORBIDDEN_MODULES = {"corpus", "corpus_lexicon"}
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
    for forbidden in ("corpus_lexicon", "PLANTS", "DECOYS_EXTRACTOR", "DECOYS_ACCUMULATOR"):
        assert not any(forbidden in i for i in identifiers), (
            f"{module} has executable code referencing {forbidden!r}"
        )


def test_offline_extractor_is_measurably_imperfect() -> None:
    """If the extractor were perfect, the corpus would be tuned to it and the eval would be
    self-referential. It must genuinely miss things."""
    from ear.config import RunConfig
    from ear.corpus import generate
    from ear.evals import extraction_fidelity
    from ear.extract import OfflineLexiconExtractor, extract_all

    run = RunConfig()
    corpus = generate(run)
    signals = extract_all(OfflineLexiconExtractor(), corpus.conversations)
    fidelity = extraction_fidelity(corpus.seeded, signals)

    assert fidelity["planted_genuine"] > 0, "corpus planted nothing to measure against"
    assert fidelity["extraction_recall"] < 1.0, (
        "the offline extractor caught 100% of planted signals — that means its cue vocabulary "
        "has been aligned to the corpus fragments, which invalidates the experiment"
    )
