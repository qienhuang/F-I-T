from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_system(system: str, exp_dir: Path) -> dict:
    inv = pd.read_csv(exp_dir / "results" / "invariant_matrix.csv")
    sat = json.loads((exp_dir / "results" / "saturation_summary.json").read_text(encoding="utf-8"))
    closure = json.loads((exp_dir / "results" / "closure_tests.json").read_text(encoding="utf-8"))

    vc = inv["overall_label"].value_counts().to_dict()
    pass_cells = int(vc.get("PASS", 0))
    scope_cells = int(vc.get("SCOPE_LIMITED_SATURATION", 0))
    unstable_cells = int(vc.get("ESTIMATOR_UNSTABLE", 0))

    req_pass = 0
    req_scope = 0
    req_unstable = 0
    req_rmse = []
    opt_pass = 0
    opt_scope = 0
    opt_unstable = 0
    opt_rmse = []

    for scheme, est_map in closure.items():
        for estimator, triples in est_map.items():
            rec_req = triples.get("1->2->4")
            if rec_req is not None:
                lbl = rec_req.get("label", "ESTIMATOR_UNSTABLE")
                if lbl == "PASS":
                    req_pass += 1
                elif lbl == "SCOPE_LIMITED_SATURATION":
                    req_scope += 1
                else:
                    req_unstable += 1
                if not rec_req.get("skipped", False):
                    rm = rec_req.get("rmse_composed_vs_direct")
                    if rm is not None:
                        req_rmse.append(float(rm))

            rec_opt = triples.get("2->4->8")
            if rec_opt is not None:
                lbl = rec_opt.get("label", "ESTIMATOR_UNSTABLE")
                if lbl == "PASS":
                    opt_pass += 1
                elif lbl == "SCOPE_LIMITED_SATURATION":
                    opt_scope += 1
                else:
                    opt_unstable += 1
                if not rec_opt.get("skipped", False):
                    rm = rec_opt.get("rmse_composed_vs_direct")
                    if rm is not None:
                        opt_rmse.append(float(rm))

    req_testable = req_pass + req_unstable
    opt_testable = opt_pass + opt_unstable

    return {
        "system": system,
        "cells_total": int(len(inv)),
        "pass_cells": pass_cells,
        "scope_limited_cells": scope_cells,
        "unstable_cells": unstable_cells,
        "groups_total": int(sat.get("groups_total", 0)),
        "groups_saturated": int(sat.get("groups_saturated", 0)),
        "groups_non_saturated": int(sat.get("groups_non_saturated", 0)),
        "req124_pass": req_pass,
        "req124_scope_limited": req_scope,
        "req124_unstable": req_unstable,
        "req124_testable": req_testable,
        "req124_pass_rate_testable": (req_pass / req_testable) if req_testable > 0 else None,
        "req124_rmse_median_testable": float(pd.Series(req_rmse).median()) if req_rmse else None,
        "opt248_pass": opt_pass,
        "opt248_scope_limited": opt_scope,
        "opt248_unstable": opt_unstable,
        "opt248_testable": opt_testable,
        "opt248_pass_rate_testable": (opt_pass / opt_testable) if opt_testable > 0 else None,
        "opt248_rmse_median_testable": float(pd.Series(opt_rmse).median()) if opt_rmse else None,
    }


def fmt(x: float | None, nd: int = 3) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{float(x):.{nd}f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gol_dir", default="d:/FIT Lab/github/F-I-T/experiments/gol_multiscale_invariants")
    ap.add_argument("--langton_dir", default="d:/FIT Lab/github/F-I-T/experiments/langton_multiscale_invariants")
    ap.add_argument("--ising_dir", default="d:/FIT Lab/github/F-I-T/experiments/ising_multiscale_invariants")
    ap.add_argument("--out_csv", default="results/cross_system_path4_summary.csv")
    ap.add_argument("--out_md", default="results/CROSS_SYSTEM_PATH4_REPORT.md")
    args = ap.parse_args()

    rows = [
        load_system("GoL", Path(args.gol_dir)),
        load_system("Langton", Path(args.langton_dir)),
        load_system("Ising", Path(args.ising_dir)),
    ]
    df = pd.DataFrame(rows)

    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    lines = [
        "# Path-4 Cross-System Report (GoL / Langton / Ising)",
        "",
        "## Scope And Definitions",
        "",
        "- `testable` means triples not excluded by saturation gate (`PASS + ESTIMATOR_UNSTABLE`).",
        "- Gate constants are fixed across systems (`eps=0.10`, `saturation_ratio_threshold=0.90`, closure `tau=0.05`).",
        "- `C_activity` is treated as implementation-consistency (`1 - C_frozen`), not as an independent estimator family.",
        "",
        "## Table 1: Matrix Labels",
        "",
        "| System | Cells | PASS | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['system']} | {int(r['cells_total'])} | {int(r['pass_cells'])} | {int(r['scope_limited_cells'])} | {int(r['unstable_cells'])} | {int(r['groups_saturated'])} | {int(r['groups_non_saturated'])} |"
        )

    lines.extend(
        [
            "",
            "## Table 2: Required Triple `1->2->4`",
            "",
            "| System | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, r in df.iterrows():
        lines.append(
            f"| {r['system']} | {int(r['req124_pass'])} | {int(r['req124_scope_limited'])} | {int(r['req124_unstable'])} | {int(r['req124_testable'])} | {fmt(r['req124_pass_rate_testable'])} | {fmt(r['req124_rmse_median_testable'], 5)} |"
        )

    lines.extend(
        [
            "",
            "## Table 3: Optional Triple `2->4->8`",
            "",
            "| System | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, r in df.iterrows():
        lines.append(
            f"| {r['system']} | {int(r['opt248_pass'])} | {int(r['opt248_scope_limited'])} | {int(r['opt248_unstable'])} | {int(r['opt248_testable'])} | {fmt(r['opt248_pass_rate_testable'])} | {fmt(r['opt248_rmse_median_testable'], 5)} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Langton is currently the strongest cross-system positive case (high PASS, low saturation).",
            "- Ising under current boundary is regime-sensitive: high saturation and reduced required-triple stability.",
            "- The gate stack is functioning as intended: no forced claims under saturation; instability is surfaced explicitly.",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
