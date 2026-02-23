from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_temp(tag: str) -> float:
    # T2p269 -> 2.269
    raw = tag.lstrip("T").replace("p", ".")
    return float(raw)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="results/temp_sweep")
    ap.add_argument("--out_csv", default="results/temp_sweep/temperature_sweep_summary.csv")
    ap.add_argument("--out_md", default="results/temp_sweep/temperature_sweep_summary.md")
    ap.add_argument("--title", default="Ising Temperature Sweep Summary (Pilot)")
    ap.add_argument("--note_tail", default="This is a pilot for boundary diagnosis, not a final claim.")
    args = ap.parse_args()

    root = Path(args.root)
    rows: list[dict] = []

    for d in sorted([x for x in root.iterdir() if x.is_dir() and x.name.startswith("T")], key=lambda p: p.name):
        inv_csv = d / "invariant_matrix.csv"
        sat_json = d / "saturation_summary.json"
        closure_json = d / "closure_tests.json"
        if not inv_csv.exists() or not sat_json.exists() or not closure_json.exists():
            continue

        inv = pd.read_csv(inv_csv)
        sat = json.loads(sat_json.read_text(encoding="utf-8"))
        closure = json.loads(closure_json.read_text(encoding="utf-8"))
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
                label = rec.get("label", "ESTIMATOR_UNSTABLE")
                if label == "PASS":
                    req_pass += 1
                elif label == "SCOPE_LIMITED_SATURATION":
                    req_scope += 1
                else:
                    req_unstable += 1
                if not rec.get("skipped", False):
                    v = rec.get("rmse_composed_vs_direct")
                    if v is not None:
                        req_rmse.append(float(v))
        req_testable = req_pass + req_unstable
        req_pass_rate = (req_pass / req_testable) if req_testable > 0 else None
        req_rmse_median = float(pd.Series(req_rmse).median()) if req_rmse else None

        rows.append(
            {
                "temperature": parse_temp(d.name),
                "tag": d.name,
                "pass_cells": int(vc.get("PASS", 0)),
                "scope_limited_cells": int(vc.get("SCOPE_LIMITED_SATURATION", 0)),
                "unstable_cells": int(vc.get("ESTIMATOR_UNSTABLE", 0)),
                "groups_saturated": int(sat.get("groups_saturated", 0)),
                "groups_non_saturated": int(sat.get("groups_non_saturated", 0)),
                "req124_pass": req_pass,
                "req124_scope_limited": req_scope,
                "req124_unstable": req_unstable,
                "req124_testable": req_testable,
                "req124_pass_rate_testable": req_pass_rate,
                "req124_rmse_median_testable": req_rmse_median,
            }
        )

    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        df = pd.DataFrame(
            columns=[
                "temperature",
                "tag",
                "pass_cells",
                "scope_limited_cells",
                "unstable_cells",
                "groups_saturated",
                "groups_non_saturated",
                "req124_pass",
                "req124_scope_limited",
                "req124_unstable",
                "req124_testable",
                "req124_pass_rate_testable",
                "req124_rmse_median_testable",
            ]
        )
    else:
        df = pd.DataFrame(rows).sort_values("temperature").reset_index(drop=True)
    df.to_csv(out_csv, index=False)

    lines = [
        f"# {args.title}",
        "",
        "## Matrix Labels",
        "",
        "| T | PASS cells | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['temperature']:.3f} | {int(r['pass_cells'])} | {int(r['scope_limited_cells'])} | {int(r['unstable_cells'])} | {int(r['groups_saturated'])} | {int(r['groups_non_saturated'])} |"
        )
    lines.extend(
        [
            "",
            "## Required Triple `1->2->4`",
            "",
            "| T | PASS | SCOPE_LIMITED | UNSTABLE | Testable (PASS+UNSTABLE) | PASS rate (testable) | Median RMSE (testable) |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, r in df.iterrows():
        pr = "n/a" if pd.isna(r["req124_pass_rate_testable"]) else f"{float(r['req124_pass_rate_testable']):.3f}"
        rm = "n/a" if pd.isna(r["req124_rmse_median_testable"]) else f"{float(r['req124_rmse_median_testable']):.5f}"
        lines.append(
            f"| {r['temperature']:.3f} | {int(r['req124_pass'])} | {int(r['req124_scope_limited'])} | {int(r['req124_unstable'])} | {int(r['req124_testable'])} | {pr} | {rm} |"
        )
    lines.extend(
        [
            "",
            "Notes:",
            "- Same gate thresholds are used across temperatures (`eps=0.10`, `saturation_ratio_threshold=0.90`, closure `tau=0.05`).",
            "- `testable` means triples not excluded by saturation gate (PASS + ESTIMATOR_UNSTABLE).",
            f"- {args.note_tail}",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
