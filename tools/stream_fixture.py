"""Turn `earshot stream` artifacts into the demo UI's data file.

    uv run python tools/stream_fixture.py                    # newest per tenant -> ui/stream.js
    uv run python tools/stream_fixture.py --tenant northwind,meridian
    uv run python tools/stream_fixture.py --artifact A.json --artifact B.json --out ui/stream.js

**Why this exists.** Same reason as `tools/ui_fixture.py`: the demo must run from `file://` with
no server, no key and no network, because a judging room without wifi cannot be allowed to break
it (D-004). A `<script src>` assigning `window.EARSHOT_STREAM` loads over `file://` where a
`fetch()` of a sibling JSON does not.

**It reformats; it never computes.** Every score, delta, board position and crossing in a frame
was produced by `memory.py` inside `earshot stream`. Nothing here scores, re-ranks, or fills in a
missing field. If a number is wrong on screen it is wrong in the artifact, which is the only way
a discrepancy stays findable.

**One artifact per tenant, kept apart in the output.** A tenant is a deployment. Concatenating
three books into one array would let a screen sum across enterprises, which is a number no
customer of this system would ever be shown.

**The answer key must not reach a browser.** Checked here as well as in `earshot.stream`, because
this tool is the last thing standing between an artifact and a page, and a fixture is exactly
where someone would one day add "just the stratum, for colour".
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from earshot.stream import ANSWER_KEY_FIELDS, _all_keys
from earshot.tenants import BY_ID

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "ui" / "stream.js"
ARTIFACT_GLOB = "artifacts/runs/stream-*.json"

# The keys a tenant block must carry for the demo screens to render. Checked by name rather than
# trusted, because the failure mode of a missing key is a blank panel with no error -- which on
# stage reads as "the product has nothing to show" rather than "the fixture is stale".
REQUIRED = ("manifest", "tenant", "frames", "cases", "conversations", "teams", "totals")


class FixtureError(RuntimeError):
    """Something about the artifacts makes them unusable as demo data. Named, not a traceback."""


def newest_per_tenant(root: Path = ROOT, wanted: list[str] | None = None) -> list[Path]:
    """The most recent stream artifact for each tenant, in `tenants.py` declaration order.

    Declaration order, not modification order: the portfolio screen reads left to right and the
    tenants should not reshuffle because one of them was re-recorded this afternoon.
    """
    found = sorted(root.glob(ARTIFACT_GLOB), key=lambda p: p.stat().st_mtime, reverse=True)
    if not found:
        raise FixtureError(
            f"no artifact matching {ARTIFACT_GLOB}. Run: uv run earshot stream --tenant all"
        )
    best: dict[str, Path] = {}
    for path in found:
        try:
            tenant_id = json.loads(path.read_text(encoding="utf-8"))["tenant"]["tenant_id"]
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            raise FixtureError(f"{path.name} is not a stream artifact: {exc}") from exc
        best.setdefault(tenant_id, path)
    order = [tid for tid in BY_ID if tid in best]
    if wanted is not None:
        missing = [tid for tid in wanted if tid not in best]
        if missing:
            raise FixtureError(
                f"no stream artifact for {missing}. Run: "
                f"uv run earshot stream --tenant {','.join(missing)}"
            )
        order = [tid for tid in wanted]
    return [best[tid] for tid in order]


def build(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    """The demo's data, one block per tenant, in the shapes `earshot stream` wrote them."""
    if not artifacts:
        raise FixtureError("no artifacts to build from")
    blocks = []
    for artifact in artifacts:
        missing = [key for key in REQUIRED if key not in artifact]
        if missing:
            raise FixtureError(
                f"artifact is missing {missing} -- it predates the current stream shape. "
                "Re-run `earshot stream`."
            )
        if not artifact["frames"]:
            raise FixtureError(
                f"{artifact['tenant']['tenant_id']} streamed nothing; there is no demo to render"
            )
        blocks.append(artifact)

    ids = [b["tenant"]["tenant_id"] for b in blocks]
    if len(set(ids)) != len(ids):
        raise FixtureError(f"two artifacts for the same tenant: {ids}")

    payload = {
        "tenants": blocks,
        # Deliberately NOT a portfolio total. Costs are per deployment because each tenant is a
        # separate customer of this system; a summed figure across three banks is a number that
        # would never appear on anyone's invoice.
        "index": [
            {
                "tenant_id": b["tenant"]["tenant_id"],
                "name": b["tenant"]["name"],
                "industry": b["tenant"]["industry"],
                "accent": b["tenant"]["accent"],
                "reader": b["manifest"].get("reader"),
                "provider": b["manifest"].get("provider"),
                "totals": b["totals"],
            }
            for b in blocks
        ],
    }

    leaked = _all_keys(payload) & ANSWER_KEY_FIELDS
    if leaked:
        raise FixtureError(f"answer-key fields would reach the browser: {sorted(leaked)}")

    for block in blocks:
        cited = {
            row["conversation_id"]
            for case in block["cases"].values()
            for row in case.get("evidence", [])
        }
        gap = cited - set(block["conversations"])
        if gap:
            raise FixtureError(
                f"{block['tenant']['tenant_id']}: cited conversations with no transcript: "
                f"{sorted(gap)}"
            )
    return payload


def render(payload: dict[str, Any]) -> str:
    """A `.js` assignment, not a `.json` file, so the page loads over `file://`.

    No indentation: this file is generated, never hand-read, and three books of transcripts
    pretty-printed is several megabytes of whitespace a browser has to parse on every open.
    """
    body = json.dumps(payload, separators=(",", ":"), default=str)
    return (
        "// GENERATED by tools/stream_fixture.py -- do not edit by hand.\n"
        "// Recorded runs replayed on a wall clock. No audio was transcribed: see manifest.asr.\n"
        f"window.EARSHOT_STREAM = {body};\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--artifact", type=Path, action="append", default=None, help="repeatable; default: the "
        "newest artifact for each tenant"
    )
    parser.add_argument(
        "--tenant", default=None, help="comma-separated tenant ids to include; default: all found"
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    try:
        wanted = [p.strip() for p in args.tenant.split(",")] if args.tenant else None
        paths = args.artifact or newest_per_tenant(wanted=wanted)
        payload = build([json.loads(p.read_text(encoding="utf-8")) for p in paths])
    except FixtureError as exc:
        print(f"stream_fixture: {exc}")
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(payload), encoding="utf-8")

    print(f"wrote {args.out}  ({args.out.stat().st_size / 1000:.0f} kB)")
    for block, path in zip(payload["tenants"], paths):
        totals = block["totals"]
        manifest = block["manifest"]
        print(
            f"  {block['tenant']['name']:<26} {totals['conversations']:>4} conversations  "
            f"{totals['crossings']:>2} crossings  {totals['investigated']:>2} investigated  "
            f"${totals['total_cost_usd']:.4f}  reader={manifest.get('reader')}"
        )
        print(f"  {'':<26} {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
