from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_required_rmse(closure_obj: dict) -> list[float]:
    vals: list[float] = []
    for scheme, est_map in closure_obj.items():
        for estimator, triple_map in est_map.items():
            rec = triple_map.get("1->2->4")
            if rec is None or rec.get("skipped", False):
                continue
            v = rec.get("rmse_composed_vs_direct")
            if v is not None:
                vals.append(float(v))
    return vals


def summarize_one(block: str, temp_tag: str, closure_path: Path, taus: list[float]) -> list[dict]:
    obj = json.loads(closure_path.read_text(encoding="utf-8"))
    rmse = load_required_rmse(obj)
    rows: list[dict] = []
    for tau in taus:
        if rmse:
            pass_count = sum(1 for v in rmse if v < tau)
            n_testable = len(rmse)
            pass_rate = pass_count / n_testable
            rmse_median = float(pd.Series(rmse).median())
        else:
            pass_count = 0
            n_testable = 0
            pass_rate = float("nan")
            rmse_median = float("nan")
        rows.append(
            {
                "block": block,
                "temp_tag": temp_tag,
                "temperature": 2.10 if temp_tag == "T2p10" else 2.269 if temp_tag == "T2p269" else None,
                "tau": tau,
                "required124_testable": n_testable,
                "required124_pass_under_tau": pass_count,
                "required124_pass_rate_under_tau": pass_rate,
                "required124_rmse_median": rmse_median,
            }
        )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block_a_root", default="results/temp_compare_full")
    ap.add_argument("--block_b_root", default="results/temp_compare_full_block_b")
    ap.add_argument("--temps", nargs="+", default=["T2p10", "T2p269"])
    ap.add_argument("--taus", nargs="+", type=float, default=[0.02, 0.05, 0.08])
    ap.add_argument("--out_csv", default="results/temp_compare_blocks/tau_sensitivity_summary.csv")
    ap.add_argument("--out_md", default="results/temp_compare_blocks/tau_sensitivity_summary.md")
    args = ap.parse_args()

    rows: list[dict] = []
    for block_name, root in [("A", Path(args.block_a_root)), ("B", Path(args.block_b_root))]:
        for temp in args.temps:
            closure = root / temp / "closure_tests.json"
            if not closure.exists():
                continue
            rows.extend(summarize_one(block_name, temp, closure, args.taus))

    df = pd.DataFrame(rows).sort_values(["temperature", "block", "tau"]).reset_index(drop=True)
    out_csv = Path(args.out_csv)
    out_md = Path(args.out_md)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    lines = [
        "# Ising Required-Triple Tau Sensitivity (Block A/B)",
        "",
        "This audit recomputes pass rates for the required triple (`1->2->4`) using fixed non-skipped RMSE values under alternative closure thresholds.",
        "",
        "| Block | T | tau | Testable | PASS under tau | PASS rate | Median RMSE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df.iterrows():
        pr = "n/a" if pd.isna(r["required124_pass_rate_under_tau"]) else f"{float(r['required124_pass_rate_under_tau']):.3f}"
        med = "n/a" if pd.isna(r["required124_rmse_median"]) else f"{float(r['required124_rmse_median']):.5f}"
        lines.append(
            f"| {r['block']} | {r['temperature']:.3f} | {r['tau']:.2f} | {int(r['required124_testable'])} | "
            f"{int(r['required124_pass_under_tau'])} | {pr} | {med} |"
        )

    lines.extend(
        [
            "",
            "Readout:",
            "- This is a threshold-sensitivity audit, not a new prereg verdict replacement.",
            "- If `T=2.10` remains consistently above `T=2.269` across tau values, regime-conditioned separation is robust to reasonable tau perturbations.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()

