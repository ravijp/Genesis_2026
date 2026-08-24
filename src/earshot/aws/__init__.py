"""AWS entrypoints: the Lambda handlers and the DynamoDB stores behind them.

This lives *inside* the package rather than in a top-level `handlers/` on purpose.
`tests/test_separation.py` discovers its surface by globbing `earshot/**/*.py`, so anything
here is guarded the moment the file exists. In production `ingest.py` IS the conversation-to
-decision path — exactly the surface the guard exists to cover. A handler outside the package
would leave the laptop path guarded and the deployed one unguarded, which is the hole
working-agreements §6 was written against.

Two constraints this imposes, both easy to trip:

1. Nothing here may import the corpus side (`corpus`, `corpus_lexicon`, or a ground-truth
   type). The guard's evaluation exemption list is capped at three modules by a test, so a new
   module here cannot be added to it.
2. No dynamic imports. `import_module` and `__import__` are forbidden identifiers, matched as
   substrings over identifiers and string literals alike — so select a provider with an
   explicit `if`/`elif`, never a registry lookup.
"""
