from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_pair(root: Path, temp_tag: str) -> dict:
    inv = pd.read_csv(root / temp_tag / "invariant_matrix.csv")
    sat = json.loads((root / temp_tag / "saturation_summary.json").read_text(encoding="utf-8"))
    closure = json.loads((root / temp_tag / "closure_tests.json").read_text(encoding="utf-8"))

    vc = inv["overall_label"].value_counts().to_dict()
    req_pass = 0
    req_scope = 0
    req_unstable = 0
    req_rmse = []
    for scheme, est_map in closure.items():
        for estimator, triples in est_map.items():
            rec = triples.get("1->2->4")
            if rec is None:
                continue
            lbl = rec.get("label", "ESTIMATOR_UNSTABLE")
            if lbl == "PASS":
                req_pass += 1
            elif lbl == "SCOPE_LIMITED_SATURATION":
                req_scope += 1
            else:
                req_unstable += 1
            if not rec.get("skipped", False):
                v = rec.get("rmse_composed_vs_direct")
                if v is not None:
                    req_rmse.append(float(v))
    req_testable = req_pass + req_unstable
    return {
        "pass_cells": int(vc.get("PASS", 0)),
        "scope_limited_cells": int(vc.get("SCOPE_LIMITED_SATURATION", 0)),
        "unstable_cells": int(vc.get("ESTIMATOR_UNSTABLE", 0)),
        "groups_saturated": int(sat.get("groups_saturated", 0)),
        "groups_non_saturated": int(sat.get("groups_non_saturated", 0)),
        "req124_pass": req_pass,
        "req124_scope_limited": req_scope,
        "req124_unstable": req_unstable,
        "req124_testable": req_testable,
        "req124_pass_rate_testable": (req_pass / req_testable) if req_testable > 0 else None,
        "req124_rmse_median_testable": float(pd.Series(req_rmse).median()) if req_rmse else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block_a_root", default="results/temp_compare_full")
    ap.add_argument("--block_b_root", default="results/temp_compare_full_block_b")
    ap.add_argument("--out_csv", default="results/temp_compare_blocks/temperature_compare_blocks_summary.csv")
    ap.add_argument("--out_md", default="results/temp_compare_blocks/temperature_compare_blocks_summary.md")
    args = ap.parse_args()

    rows = []
    for block_name, root in [("A", Path(args.block_a_root)), ("B", Path(args.block_b_root))]:
        for temp_tag in ["T2p10", "T2p269"]:
            rec = load_pair(root, temp_tag)
            rec["block"] = block_name
            rec["temp_tag"] = temp_tag
            rec["temperature"] = 2.10 if temp_tag == "T2p10" else 2.269
            rows.append(rec)

    df = pd.DataFrame(rows).sort_values(["temperature", "block"]).reset_index(drop=True)
    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    lines = [
        "# Ising Two-Temperature Full Compare: Seed-Block Consistency",
        "",
        "## Matrix Labels",
        "",
        "| Block | T | PASS cells | SCOPE_LIMITED | UNSTABLE | Saturated groups | Non-saturated groups |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['block']} | {r['temperature']:.3f} | {int(r['pass_cells'])} | {int(r['scope_limited_cells'])} | {int(r['unstable_cells'])} | {int(r['groups_saturated'])} | {int(r['groups_non_saturated'])} |"
        )
    lines.extend(
        [
            "",
            "## Required Triple `1->2->4`",
            "",
            "| Block | T | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, r in df.iterrows():
        pr = "n/a" if pd.isna(r["req124_pass_rate_testable"]) else f"{float(r['req124_pass_rate_testable']):.3f}"
        rm = "n/a" if pd.isna(r["req124_rmse_median_testable"]) else f"{float(r['req124_rmse_median_testable']):.5f}"
        lines.append(
            f"| {r['block']} | {r['temperature']:.3f} | {int(r['req124_pass'])} | {int(r['req124_scope_limited'])} | {int(r['req124_unstable'])} | {int(r['req124_testable'])} | {pr} | {rm} |"
        )

    lines.extend(
        [
            "",
            "## Readout",
            "",
            "- Compare within each block (`2.10` vs `2.269`) for regime effect.",
            "- Compare across blocks (A vs B) for seed-block sensitivity under fixed gates.",
            "- Keep claims bounded to fixed gate semantics; do not pool blocks without preregistering pooled criteria.",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
