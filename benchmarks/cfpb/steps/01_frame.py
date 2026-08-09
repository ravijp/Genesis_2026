"""Step 01 — establish and verify the pre-registered sampling frame.

Confirms three things and writes them to `out/frame.json`:

  1. the frame total, and that it equals the sum of its per-product parts (if it does not, the
     product filter is not doing what the protocol says it does);
  2. what the frame EXCLUDES and how large those exclusions are -- published, because the
     restriction to retail-banking products is the single most contestable design choice here;
  3. the `issue` buckets measured WITHIN the frame, which is where Panel B's strata come from.

Metadata only. No narrative text is fetched by this step.

    uv run python benchmarks/cfpb/steps/01_frame.py [run-date]
"""

from __future__ import annotations

import datetime as dt
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    FRAME_PRODUCTS,
    PANEL_B_STRATA,
    WINDOW_MAX,
    WINDOW_MIN,
    api,
    call_count,
    frame_params,
    log,
    total_for,
    write_json,
)

EXCLUDED = (
    ("Credit reporting or other personal consumer reports", "a dispute with a bureau, not a bank conversation"),
    ("Debt collection", "usually a third-party collector, not the bank's own customer relationship"),
    ("Money transfer, virtual currency, or money service", "payment apps and crypto, not a banking relationship"),
    ("Debt or credit management", "debt-settlement firms"),
)


def main() -> None:
    run_date = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    window = [("has_narrative", "true"), ("date_received_min", WINDOW_MIN), ("date_received_max", WINDOW_MAX)]

    all_narratives = total_for(window)
    frame_total = total_for(frame_params())

    per_product = {p: total_for([*window, ("product", p)]) for p in FRAME_PRODUCTS}
    per_excluded = {p: total_for([*window, ("product", p)]) for p, _ in EXCLUDED}

    parts_sum = sum(per_product.values())
    if parts_sum != frame_total:
        raise SystemExit(
            f"frame total {frame_total} != sum of parts {parts_sum}. The product filter is not "
            f"selecting what PROTOCOL.md section 2 says it selects; stop and diagnose."
        )

    payload = api([("size", "0"), *frame_params()])
    issue_buckets = [
        {"issue": b["key"], "count": b["doc_count"]}
        for b in payload["aggregations"]["issue"]["issue"]["buckets"]
    ]
    issue_sum = sum(b["count"] for b in issue_buckets)
    if issue_sum != frame_total:
        raise SystemExit(
            f"issue buckets sum to {issue_sum} but the frame holds {frame_total}. The issue "
            f"aggregation is not scoped to the frame; Panel B's strata sizes would be wrong."
        )

    # Every Panel B stratum bucket must actually exist in the frame. A silent typo in a bucket
    # name would produce an empty stratum and a recall over n=0, which reads as a result.
    by_issue = {b["issue"]: b["count"] for b in issue_buckets}
    strata_sizes: dict[str, dict[str, int]] = {}
    for target, buckets, n in PANEL_B_STRATA:
        missing = [b for b in buckets if b not in by_issue]
        if missing:
            raise SystemExit(f"Panel B stratum {target!r} names issue buckets absent from the frame: {missing}")
        strata_sizes[target] = {"pool": sum(by_issue[b] for b in buckets), "n_drawn": n}

    meta = payload.get("_meta", {})
    frame = {
        "run_date": run_date,
        "cfpb_last_updated": meta.get("last_updated"),
        "cfpb_licence": meta.get("license"),
        "cfpb_total_record_count": meta.get("total_record_count"),
        "window": {"date_received_min": WINDOW_MIN, "date_received_max": WINDOW_MAX},
        "all_narratives_in_window": all_narratives,
        "frame_total": frame_total,
        "frame_products": per_product,
        "excluded_products": {p: {"count": per_excluded[p], "reason": r} for p, r in EXCLUDED},
        "frame_share_of_all_narratives": round(frame_total / all_narratives, 4),
        "issue_buckets_in_frame": issue_buckets,
        "panel_b_strata": strata_sizes,
        "example_url": payload["_url"],
    }
    path, digest = write_json("frame.json", frame)

    log(
        "01_frame",
        run_date,
        [
            f"CFPB `_meta.last_updated` **{meta.get('last_updated')}**, licence `{meta.get('license')}`",
            f"all narrative complaints in window: **{all_narratives:,}**",
            f"frame (7 retail-banking products): **{frame_total:,}** "
            f"({frame['frame_share_of_all_narratives']:.1%} of all narratives in window)",
            f"per-product parts sum to {parts_sum:,} — matches the frame total",
            f"issue buckets within frame: **{len(issue_buckets)}**, summing to {issue_sum:,}",
            "Panel B pools: "
            + " · ".join(f"{k} {v['pool']:,} (draw {v['n_drawn']})" for k, v in strata_sizes.items()),
            f"API calls: {call_count()}",
            f"`out/frame.json` sha256 `{digest}`",
        ],
    )


if __name__ == "__main__":
    main()
