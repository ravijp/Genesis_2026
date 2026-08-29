"""The separation guard: the extractor cannot see the answer key.

The obvious objection to this build is that the conversations are sub-threshold for a matcher we
also wrote, so nothing on the path from a conversation to a decision may reach the corpus
generator, its fragment lexicon, or a ground-truth type.

**Two trees are guarded.** The package is the decision path. `tools/` is the second one:
`ui_fixture.py` and `stream_fixture.py` build the exact JSON that ships to `ui/data.js` and
`ui/stream.js`, so a corpus import there puts `stratum` and `latent_risk` one object away from a
browser. `ui_fixture.py`'s docstring has always said "This file does not import the corpus";
until discovery reached `tools/`, that was a promise with nothing behind it.

**Four nets, because no one of them is complete.**

1. *Imports* — the module or the imported name is a corpus-side module or a ground-truth type.
2. *Star-imports* — `from .schema import *` names nothing at all: the alias is `*`, so
   `SeededSignal` arrives with no forbidden spelling in any import node. A star-import from a
   module that defines a ground-truth type is refused outright, because it is the one import
   form that makes net 1 structurally blind.
3. *Exact tokens* — every identifier, attribute and dotted string segment in executable code,
   matched exactly. This catches `import earshot` followed by `earshot.corpus.generate`, which
   reaches the generator with no forbidden module in any import node and works at runtime
   because `cli.py` is exempt and imports `corpus`, so `earshot.corpus` is a populated attribute
   in every real run. It also covers `sys.modules["earshot.corpus"]` and
   `getattr(earshot, "corpus")`.
4. *Substrings* — names distinctive enough (`PLANTS`, `BY_TYPE`, `import_module`) that any
   identifier containing them is a reach.

**And none of the four is the guarantee.** They catch import statements, literal identifiers and
literal strings, which is what an accident looks like. They do not catch a determined route: a
name assembled from fragments at runtime, or reading `corpus.py` as text, reach the answer key
with no forbidden spelling anywhere. That is a property of static analysis, not a bug to be fixed
by lengthening the list — and believing otherwise is what let a review lift published recall from
0.66 to 0.93 with the whole suite green.

So the guarantee that actually holds is `test_published_extraction_recall_stays_in_its_measured
_band`: reaching the answer key raises recall, and recall is pinned to the band it was measured
in. The scans are the cheap first net; the band is the guard.

Do not relax any of them. A matcher that catches everything it planted proves nothing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import earshot

# Resolved from the INSTALLED package, not from a path walk — survives any repo layout change.
EAR = Path(earshot.__file__).resolve().parent

# `tools/` has no import anchor, so it is resolved from this file. The scripts there are not
# importable modules; they are the build step between a run artifact and a browser payload.
TOOLS = Path(__file__).resolve().parents[1] / "tools"

# The guarded surface is DISCOVERED, not listed: everything under the package that is neither
# the corpus side nor the evaluation side. A hand-maintained list is one forgotten line away
# from a hole, and the hole is invisible until someone goes looking. Anything new is covered
# the moment the file exists.
#
# The agent's tools are the sharpest edge of that surface. A tool deriving a customer's
# transactions or account state from a ground-truth field hands the agent the answer key
# through the back door; tools may derive from a risk figure and the seed only.

# The corpus side AUTHORS the answer key. Capped for the same reason `_EVALUATION_SIDE` is:
# every entry here is a file the scans skip entirely, so moving `agent/tools.py`, `stream.py`
# and `read_live.py` in shrinks the guarded surface from 34 modules to 31 with nothing failing.
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

# The same exemption, for the `tools/` tree. These are measurement harnesses, not payload
# builders: they read the seeded key because comparing an agent's verdict, its routing slot or a
# reader's coverage to the truth is the whole job (D-009). Nothing they write reaches a browser.
# Capped for the same reason — a blanket pass for `tools/` would re-open the hole this discovery
# closes. The test that owns each one is named, because an exemption whose scorer nobody tests
# is an exemption with nothing behind it.
_TOOLS_EVALUATION_SIDE = {
    "verdict_accuracy.py",   # scores the agent's genuine/false-alarm verdict against truth
    "routing_accuracy.py",   # scores owning_team against the seeded trajectory
    "reader_coverage.py",    # scores a reader's coverage against what was planted
}


def _is_danger(rel: str) -> bool:
    """Everything that turns a conversation into a decision. Not the authors of truth, and
    not the scorers of it.

    Membership is decided by the path relative to the package root, not by the bare filename:
    the exemptions name specific top-level modules, so a future `agent/config.py` or
    `llm/schema.py` is guarded rather than silently inheriting a root module's exemption.
    """
    return rel not in _CORPUS_SIDE and rel not in _EVALUATION_SIDE


def _is_danger_tool(rel: str) -> bool:
    """The same rule for `tools/`, against its own exemption list and its own path-relative
    match, so a future `tools/jira/verdict_accuracy.py` does not inherit the root exemption."""
    return rel not in _TOOLS_EVALUATION_SIDE


def test_evaluation_exemptions_stay_small() -> None:
    """The exemption list is the guard's weakest point. Keep it short and deliberate."""
    assert len(_EVALUATION_SIDE) <= 3, (
        f"the evaluation exemption list has grown to {sorted(_EVALUATION_SIDE)} — every entry "
        f"is a module allowed to see the answer key, so each one needs a reason"
    )


def test_tools_evaluation_exemptions_stay_small() -> None:
    """A second exemption set needs a second cap, or it becomes the way around the first.

    A `tools/` script earns a place here only if reading the seeded key IS its job — scoring
    something against what was planted — and only if nothing it writes reaches a browser. A
    script that merely finds the corpus convenient does not qualify; it goes on the surface and
    gets scanned. The paired pin is `test_the_two_ui_fixtures_can_never_be_exempted`.
    """
    assert len(_TOOLS_EVALUATION_SIDE) <= 3, (
        f"the tools exemption list has grown to {sorted(_TOOLS_EVALUATION_SIDE)} — a script in "
        f"here may read the answer key, so each one needs a reason"
    )


def test_the_two_ui_fixtures_can_never_be_exempted() -> None:
    """The cap alone lets the list grow to its limit with the wrong files in it.

    `ui_fixture.py` and `stream_fixture.py` build the exact JSON that ships to a browser, so a
    corpus import in either puts `stratum` and `latent_risk` one object away from a viewer.
    They are the reason the `tools/` tree is scanned at all, and no cap raise may quietly move
    one of them across.
    """
    exempted = _TOOLS_EVALUATION_SIDE & {"ui_fixture.py", "stream_fixture.py"}
    assert not exempted, (
        f"{sorted(exempted)} build a browser payload and have been exempted from the scans"
    )


def test_corpus_side_exemptions_stay_small() -> None:
    """An uncapped exemption set is a way to shrink the guarded surface without failing anything.

    `_CORPUS_SIDE` names the four modules that AUTHOR the key. Adding a fifth is how a reader
    stops being scanned, and `test_every_reader_is_on_the_guarded_surface` is the paired check
    naming the readers that may never leave.
    """
    assert len(_CORPUS_SIDE) <= 4, (
        f"the corpus-side exemption list has grown to {sorted(_CORPUS_SIDE)} — every entry is a "
        f"file the scans skip entirely, so each one needs a reason"
    )


def _surface() -> dict[str, Path]:
    """Every module on the path from a conversation to a decision or to a browser payload,
    discovered recursively across both trees.

    Keyed by the path a person would say out loud: package modules by their path from the
    package root, `tools/` scripts with their directory on the front. `__init__.py` is
    INCLUDED, because it can re-export anything.
    """
    found = {
        rel: EAR / rel
        for rel in (p.relative_to(EAR).as_posix() for p in EAR.rglob("*.py"))
        if _is_danger(rel)
    }
    found.update(
        {
            f"tools/{rel}": TOOLS / rel
            for rel in (p.relative_to(TOOLS).as_posix() for p in TOOLS.rglob("*.py"))
            if _is_danger_tool(rel)
        }
    )
    return found


SURFACE = _surface()
EXTRACTOR_MODULES = sorted(SURFACE)


def test_danger_surface_is_not_empty() -> None:
    """If the globs stop matching, every test below passes vacuously and the guard is gone."""
    assert len(EXTRACTOR_MODULES) >= 2, (
        f"discovery found only {EXTRACTOR_MODULES} — the separation guard has silently "
        f"stopped covering anything"
    )


def test_the_tools_tree_is_actually_being_discovered() -> None:
    """Two trees, two vacuity checks. `TOOLS` is resolved from this file's location rather than
    from an import, so a repo re-layout would leave it pointing at nothing — and every `tools/`
    scan below would then pass by finding no files at all."""
    scanned = [m for m in EXTRACTOR_MODULES if m.startswith("tools/")]
    assert len(scanned) >= 2, f"discovery found only {scanned} under {TOOLS}"


def _aws_handler_modules() -> set[str]:
    """The deployed Lambda entry points, discovered by looking for a module-level `handler`.

    Discovered rather than listed so a fourth handler is pinned the day it is written. Read off
    disk, not off `EXTRACTOR_MODULES`, so moving one into an exemption set is caught by the
    check below rather than hidden by it.
    """
    found: set[str] = set()
    for path in (EAR / "aws").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if any(
            isinstance(node, ast.FunctionDef) and node.name == "handler" for node in tree.body
        ):
            found.add(f"aws/{path.name}")
    return found


def test_the_aws_handler_discovery_finds_the_deployed_entry_points() -> None:
    """The pin below is worth something only if this finds the handlers; three are deployed."""
    assert len(_aws_handler_modules()) >= 3, (
        f"handler discovery found {sorted(_aws_handler_modules())} — the pin covers nothing"
    )


def test_every_reader_is_on_the_guarded_surface() -> None:
    """Discovery is by glob, so a new reader is covered the moment its file exists — but a
    reader the guard silently skips is worse than no reader at all, so every module that must
    never leave the surface is named here as a check on the discovery itself.

    Not just the two `Extractor` implementations: anything carrying a conversation, a ledger
    entry or a case record toward a decision or a screen. `agent/tools.py` is the agent's whole
    view of a customer; `stream.py` and `read_live.py` read conversations live; `case_record.py`
    is the shape a reviewer screen renders; the `aws/` handlers are the deployed path; the two
    fixtures in `tools/` are the last step before a browser.
    """
    readers = {
        "extract.py",                # the offline lexicon reader
        "extract_model.py",          # the model reader
        "agent/tools.py",            # everything the investigator may see about one customer
        "stream.py",                 # the live read, and the third case_record() producer
        "read_live.py",              # turn-by-turn narration of one conversation
        "case_record.py",            # the persisted case shape, artifact and DynamoDB alike
        "tools/ui_fixture.py",       # builds ui/data.js
        "tools/stream_fixture.py",   # builds ui/stream.js
    } | _aws_handler_modules()
    missing = readers - set(EXTRACTOR_MODULES)
    assert not missing, (
        f"{sorted(missing)} carry conversations toward a decision or a screen and are not "
        f"being scanned"
    )


FORBIDDEN_MODULES = {"corpus", "corpus_lexicon"}
# A forbidden module can arrive as the module OR as the imported name: `from earshot import
# corpus` puts "earshot" in modules and "corpus" in names. Both sets are checked against
# FORBIDDEN_MODULES for that reason -- see `test_guard_catches_every_known_bypass`, which
# pins each bypass form that has to stay closed.
#
# The scans below are separate nets, for reaches that are not import statements at all.

# SUBSTRING scan: names distinctive enough that any identifier containing them is a reach for
# the corpus side -- a lazy `importlib.import_module`, or a hard-coded fragment table name.
FORBIDDEN_IDENTIFIERS = ("corpus_lexicon", "PLANTS", "DECOYS_EXTRACTOR",
                        "DECOYS_ACCUMULATOR", "BY_TYPE", "Fragment", "import_module",
                        "__import__")
FORBIDDEN_NAMES = {"SeededSignal", "CustomerTruth", "Corpus", "Stratum", "Outcome", "Fragment"}

# EXACT scan, over identifiers and over the dotted segments of string literals. `corpus` cannot
# join the substring set -- `tenants._corpus` is an honest local helper that builds a
# `CorpusConfig` -- but it has to be caught exactly, because `import earshot` followed by
# `earshot.corpus.generate(run)` reaches the generator with nothing forbidden in any import
# node. This is also where FORBIDDEN_NAMES is checked against executable code rather than only
# against import nodes, which is the hole a star-import leaves behind.
FORBIDDEN_TOKENS = FORBIDDEN_MODULES | FORBIDDEN_NAMES


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


def _star_imports_from_source(source: str) -> set[str]:
    """Which modules this source star-imports, by their last dotted segment.

    Split out from `_imports_from_source` because a star-import is the one form whose `names`
    set carries no information at all: the alias is literally `*`.
    """
    tree = ast.parse(source)
    return {
        (node.module or "").split(".")[-1]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and any(alias.name == "*" for alias in node.names)
    }


def _modules_defining_ground_truth_types() -> set[str]:
    """Which package modules DEFINE a ground-truth type, found by parsing them.

    Discovered rather than listed so that moving `Stratum` to a new module does not quietly make
    a star-import of it legal again.
    """
    found: set[str] = set()
    for path in EAR.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        defined = {
            node.name for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        }
        for node in tree.body:
            if isinstance(node, ast.Assign):
                defined |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        if defined & FORBIDDEN_NAMES:
            found.add(path.stem)
    return found


ANSWER_KEY_MODULES = _modules_defining_ground_truth_types()


def test_answer_key_module_discovery_is_not_empty() -> None:
    """`schema.py` defines five of the six; if this finds nothing, the star-import net is off."""
    assert "schema" in ANSWER_KEY_MODULES, (
        f"discovery found {sorted(ANSWER_KEY_MODULES)} — the star-import check covers nothing"
    )


def _imports(path: Path) -> tuple[set[str], set[str]]:
    return _imports_from_source(path.read_text(encoding="utf-8"))


def _code_identifiers_from_source(source: str) -> set[str]:
    """Every identifier and non-docstring string literal in the module.

    Docstrings are excluded deliberately: the guarded modules *describe* the separation rule
    in prose, and a naive text scan would flag that prose. What matters is that no executable
    code reaches for the corpus side — a lazy `importlib.import_module`, say, or a hard-coded
    fragment id.
    """
    tree = ast.parse(source)

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


def _code_identifiers(path: Path) -> set[str]:
    return _code_identifiers_from_source(path.read_text(encoding="utf-8"))


def _code_tokens(identifiers: set[str]) -> set[str]:
    """The same identifiers, plus the dotted segments inside them.

    `"earshot.corpus"` as a `sys.modules` key and `earshot.corpus` as an attribute walk are one
    reach written two ways; splitting on the dot collapses them into a single token to match.
    `_corpus` does not split, so an honest local helper of that name stays legal — which is why
    this is an exact match and not a substring one.
    """
    tokens = set(identifiers)
    for identifier in identifiers:
        tokens |= set(identifier.split("."))
    return tokens


def _reaches_the_corpus_side(source: str) -> set[str]:
    """Every net, run over one piece of source.

    The bypass table uses this rather than a single net, so adding an attack tests the guard as
    a whole instead of whichever net the author of the attack had in mind.
    """
    modules, names = _imports_from_source(source)
    identifiers = _code_identifiers_from_source(source)
    hits = (modules | names) & FORBIDDEN_MODULES
    hits |= names & FORBIDDEN_NAMES
    hits |= {
        f"from {m} import *" for m in _star_imports_from_source(source) & ANSWER_KEY_MODULES
    }
    hits |= _code_tokens(identifiers) & FORBIDDEN_TOKENS
    hits |= {f for f in FORBIDDEN_IDENTIFIERS if any(f in i for i in identifiers)}
    return hits


# Every route that has reached the corpus side, written as source so the guard is tested against
# them directly rather than only against whatever the package happens to contain today.
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
    # No forbidden name appears in the import node at all -- the alias is `*`.
    "star import of the schema": (
        "from .schema import *\n\n\ndef f(x):\n    return isinstance(x, SeededSignal)\n"
    ),
    "star import, absolute": (
        "from earshot.schema import *\n\n\ndef f(x):\n    return Stratum(x)\n"
    ),
    # `cli.py` is exempt and imports `corpus`, so `earshot.corpus` is a populated attribute in
    # every real run: this reaches the generator, and no import node names anything forbidden.
    "package attribute walk": (
        "import earshot\n\n\ndef f(run):\n    return earshot.corpus.generate(run)\n"
    ),
    "getattr on the package": (
        "import earshot\n\n\ndef f():\n    return getattr(earshot, 'corpus')\n"
    ),
    "sys.modules lookup": (
        "import sys\n\n\ndef f():\n    return sys.modules['earshot.corpus']\n"
    ),
}


@pytest.mark.parametrize("form", sorted(_BYPASS_ATTEMPTS))
def test_guard_catches_every_known_bypass(form: str) -> None:
    """The guard is only worth what it catches, so every known route is pinned here.

    `from earshot import corpus` is the form a person would most naturally write, and it puts
    the forbidden module in `names` rather than `modules` -- checking only one of the two sets
    lets it straight through. `from .schema import *` and `earshot.corpus.generate` are the two
    that walked past the import scan entirely: neither names anything forbidden in an import
    node, and both reach the answer key at runtime.
    """
    hits = _reaches_the_corpus_side(_BYPASS_ATTEMPTS[form])
    assert hits, f"{form!r} reaches the corpus side and no net in the guard sees it"


def test_guard_covers_files_in_subpackages() -> None:
    """Exemptions name top-level modules; a same-named file in a subpackage is still guarded."""
    assert _is_danger("agent/config.py"), "a subpackage config.py inherited the root exemption"
    assert _is_danger("llm/schema.py"), "a subpackage schema.py inherited the root exemption"
    assert not _is_danger("config.py"), "the root config.py should stay exempt"
    assert _is_danger_tool("jira/verdict_accuracy.py"), "a tools subdirectory inherited it"
    assert not _is_danger_tool("verdict_accuracy.py"), "the evaluation harness stays exempt"


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_cannot_import_the_corpus_side(module: str) -> None:
    modules, names = _imports(SURFACE[module])
    leaked = (modules | names) & FORBIDDEN_MODULES
    assert not leaked, (
        f"{module} imports {leaked}. The extractor must not be able to see the corpus "
        f"generator or its fragment lexicon — that is the whole basis of the honesty claim."
    )


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_cannot_import_ground_truth_types(module: str) -> None:
    _, names = _imports(SURFACE[module])
    leaked = names & FORBIDDEN_NAMES
    assert not leaked, f"{module} imports ground-truth type(s) {leaked}."


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_never_star_imports_a_module_that_defines_the_answer_key(module: str) -> None:
    """Refused outright, not inspected.

    A star-import binds names the import node never spells, so there is nothing for the name
    check to look at: `from .schema import *` followed by a use of `SeededSignal` is a clean
    pass through every other net that reads import statements.
    """
    leaked = (
        _star_imports_from_source(SURFACE[module].read_text(encoding="utf-8"))
        & ANSWER_KEY_MODULES
    )
    assert not leaked, (
        f"{module} star-imports {sorted(leaked)}, which defines ground-truth types — name the "
        f"imports you need so the guard can see them"
    )


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_code_never_reaches_for_the_answer_key(module: str) -> None:
    """Belt and braces: catch a lazy `importlib` or a hard-coded fragment table name."""
    identifiers = _code_identifiers(SURFACE[module])
    for forbidden in FORBIDDEN_IDENTIFIERS:
        assert not any(forbidden in i for i in identifiers), (
            f"{module} has executable code referencing {forbidden!r}"
        )


@pytest.mark.parametrize("module", EXTRACTOR_MODULES)
def test_extractor_code_never_names_the_corpus_side(module: str) -> None:
    """The exact-token net: an attribute walk, a `sys.modules` key, a `getattr` string.

    Separate from the substring scan above because `corpus` is too common a word to match
    loosely -- `tenants._corpus` builds a `CorpusConfig` and is entirely honest -- while
    `earshot.corpus` as an attribute is not honest at all, and reaches the generator.
    """
    leaked = _code_tokens(_code_identifiers(SURFACE[module])) & FORBIDDEN_TOKENS
    assert not leaked, (
        f"{module} has executable code naming {sorted(leaked)} — an attribute walk or a string "
        f"lookup reaches the answer key without importing anything"
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


# The band the extractor's published recall must stay inside. Tight enough that reaching the
# answer key trips it, wide enough that ordinary drift does not.
#
# MOVED DELIBERATELY on 2026-08-30, from (0.55, 0.78). The fragment pools were widened from
# 8/8/4/4 to 14/14/14/14 to lift the arc ceiling, and the 32 new fragments were authored in a
# genuine pass A -- the author never opened `extract_lexicon.py`. The offline lexicon finds
# 1 of those 32 against 21 of the original 24, so recall fell to 0.2125-0.2525 over six seeds
# at 400 customers.
#
# That drop is the guard working, not failing: recall going DOWN means the reader got weaker,
# and only recall going UP indicates a leak. The old band is preserved in git; moving it is
# logged here because a band that moves quietly is not a guard. The gap between 0.88 detection
# on pass-A-adjacent fragments and 0.03 on blind ones is itself the finding -- it is the
# sharpest measurement this repo has of "the lexicon only reads language it was written
# beside", and it is why the history-length experiment runs on the model reader.
RECALL_BAND = (0.16, 0.32)


def test_published_extraction_recall_stays_in_its_measured_band() -> None:
    """The behavioural backstop, and the guard that actually holds.

    The AST scans above catch import statements and literal identifiers. They cannot be made
    complete: a built-up string passed to `__import__`, or reading `corpus.py` as text, reach
    the answer key without an import node or a forbidden spelling anywhere. Treating the static
    scan as the guarantee is what let a reviewer lift published recall from 0.66 to 0.93 with
    the whole suite green.

    So the real guarantee is behavioural: reading the answer key RAISES recall, and recall is
    pinned to the band it was measured in. A leak has to keep the extractor as wrong as it
    already is to go unnoticed, which is not a leak worth having. Measured on the configured
    extractor the pipeline actually builds, on a corpus large enough for the rate to be stable.
    """
    from dataclasses import replace

    from earshot.config import RunConfig
    from earshot.corpus import generate
    from earshot.evals import extraction_fidelity
    from earshot.extract import OfflineLexiconExtractor, extract_all

    base = RunConfig()
    run = replace(base, corpus=replace(base.corpus, n_customers=400))
    corpus = generate(run)
    extractor = OfflineLexiconExtractor(
        miss_rate=run.offline_miss_rate, false_fire_rate=run.offline_false_fire_rate
    )
    fidelity = extraction_fidelity(corpus.seeded, extract_all(extractor, corpus.conversations))

    assert fidelity["planted_genuine"] > 500, "sample too small for the rate to mean anything"
    lo, hi = RECALL_BAND
    recall = fidelity["extraction_recall"]
    assert lo < recall < hi, (
        f"extraction recall is {recall}, outside the measured band {RECALL_BAND}. If it went UP, "
        f"the extractor is seeing something it should not — check for a route to the corpus that "
        f"is not an import. If it went DOWN, the lexicon or the miss rate changed. Either way the "
        f"published miss rate is now wrong; re-measure, then move the band deliberately."
    )
