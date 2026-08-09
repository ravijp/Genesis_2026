"""The import guard: the extractor cannot see the answer key.

The obvious objection to this build is that the conversations are sub-threshold for a matcher
we also wrote. The answer has to be mechanical rather than a promise, so nothing on the path
from a conversation to a decision may import the corpus generator, its fragment lexicon, or a
ground-truth type. "Fixing" the extractor's miss rate by reaching into the corpus fails here.

Do not relax these. A matcher that catches everything it planted proves nothing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import earshot

# Resolved from the INSTALLED package, not from a path walk — survives any repo layout change.
EAR = Path(earshot.__file__).resolve().parent

# The guarded surface is DISCOVERED, not listed: everything under the package that is neither
# the corpus side nor the evaluation side. A hand-maintained list is one forgotten line away
# from a hole, and the hole is invisible until someone goes looking. Anything new is covered
# the moment the file exists.
#
# The agent's tools are the sharpest edge of that surface. A tool deriving a customer's
# transactions or account state from a ground-truth field hands the agent the answer key
# through the back door; tools may derive from a risk figure and the seed only.

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


def _is_danger(rel: str) -> bool:
    """Everything that turns a conversation into a decision. Not the authors of truth, and
    not the scorers of it.

    Membership is decided by the path relative to the package root, not by the bare filename:
    the exemptions name specific top-level modules, so a future `agent/config.py` or
    `llm/schema.py` is guarded rather than silently inheriting a root module's exemption.
    """
    return rel not in _CORPUS_SIDE and rel not in _EVALUATION_SIDE


def test_evaluation_exemptions_stay_small() -> None:
    """The exemption list is the guard's weakest point. Keep it short and deliberate."""
    assert len(_EVALUATION_SIDE) <= 3, (
        f"the evaluation exemption list has grown to {sorted(_EVALUATION_SIDE)} — every entry "
        f"is a module allowed to see the answer key, so each one needs a reason"
    )


def _danger_surface() -> list[str]:
    """Every module on the path from a conversation to a decision, discovered recursively.

    `__init__.py` is INCLUDED, because it can re-export anything.
    """
    return sorted(
        rel
        for rel in (p.relative_to(EAR).as_posix() for p in EAR.rglob("*.py"))
        if _is_danger(rel)
    )


EXTRACTOR_MODULES = _danger_surface()


def test_danger_surface_is_not_empty() -> None:
    """If the globs stop matching, every test below passes vacuously and the guard is gone."""
    assert len(EXTRACTOR_MODULES) >= 2, (
        f"discovery found only {EXTRACTOR_MODULES} — the separation guard has silently "
        f"stopped covering anything"
    )

FORBIDDEN_MODULES = {"corpus", "corpus_lexicon"}
# A forbidden module can arrive as the module OR as the imported name: `from earshot import
# corpus` puts "earshot" in modules and "corpus" in names. Both sets are checked against
# FORBIDDEN_MODULES for that reason -- see `test_guard_catches_every_known_bypass`, which
# pins each bypass form that has to stay closed.
#
# The identifier scan below is a separate net, for reaches that are not imports at all: a lazy
# `importlib.import_module`, or a hard-coded fragment table name.
FORBIDDEN_IDENTIFIERS = ("corpus_lexicon", "PLANTS", "DECOYS_EXTRACTOR",
                        "DECOYS_ACCUMULATOR", "BY_TYPE", "Fragment", "import_module",
                        "__import__")
FORBIDDEN_NAMES = {"SeededSignal", "CustomerTruth", "Corpus", "Stratum", "Outcome", "Fragment"}


def _imports_from_source(source: str) -> tuple[set[str], set[str]]:
    tree = ast.parse(source)
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


def _imports(path: Path) -> tuple[set[str], set[str]]:
    return _imports_from_source(path.read_text(encoding="utf-8"))


# Every import form that has reached the corpus side, written as source so the guard is tested
# against them directly rather than only against whatever the package happens to contain today.
_BYPASS_ATTEMPTS = {
    "plain import": "import earshot.corpus\n",
    "aliased plain import": "import earshot.corpus as c\n",
    "from-package import": "from earshot import corpus\n",
    "from-package import, aliased": "from earshot import corpus as c\n",
    "from-package lexicon": "from earshot import corpus_lexicon\n",
    "relative package import": "from . import corpus\n",
    "relative module import": "from .corpus import generate\n",
    "absolute module import": "from earshot.corpus import generate\n",
    "relative lexicon import": "from ..corpus_lexicon import BY_TYPE\n",
}


@pytest.mark.parametrize("form", sorted(_BYPASS_ATTEMPTS))
def test_guard_catches_every_known_bypass(form: str) -> None:
    """The guard is only worth what it catches, so every known route is pinned here.

    `from earshot import corpus` is the form a person would most naturally write, and it puts
    the forbidden module in `names` rather than `modules` -- checking only one of the two sets
    lets it straight through.
    """
    modules, names = _imports_from_source(_BYPASS_ATTEMPTS[form])
    assert (modules | names) & FORBIDDEN_MODULES, (
        f"{form!r} reaches the corpus side and the guard does not see it: "
        f"modules={sorted(modules)} names={sorted(names)}"
    )


def test_guard_covers_files_in_subpackages() -> None:
    """Exemptions name top-level modules; a same-named file in a subpackage is still guarded."""
    assert _is_danger("agent/config.py"), "a subpackage config.py inherited the root exemption"
    assert _is_danger("llm/schema.py"), "a subpackage schema.py inherited the root exemption"
    assert not _is_danger("config.py"), "the root config.py should stay exempt"


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_cannot_import_the_corpus_side(module: str) -> None:
    modules, names = _imports(EAR / module)
    leaked = (modules | names) & FORBIDDEN_MODULES
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

    Docstrings are excluded deliberately: the guarded modules *describe* the separation rule
    in prose, and a naive text scan would flag that prose. What matters is that no executable
    code reaches for the corpus side — a lazy `importlib.import_module`, say, or a hard-coded
    fragment id.
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
