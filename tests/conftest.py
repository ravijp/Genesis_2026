"""`tools/` on the import path, so the scripts that touch AWS and the UI can be tested.

`tools/` is deliberately not a package -- these are scripts, run by path, and giving them an
`__init__.py` would invite `earshot` to import them. But "not importable" is how `provision.py`
shipped two bugs that only reality caught (see docs/ops/progress.md, 2026-08-25), so the pure
parts get tested even though the AWS calls cannot be.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
