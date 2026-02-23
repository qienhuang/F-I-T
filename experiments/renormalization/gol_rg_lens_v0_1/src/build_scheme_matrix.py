from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd


def classify(summary: Dict, rmse_th: float = 0.05) -> Dict[str, str]:
    gate = summary.get("saturation_gate", {})
    tests = summary.get("semigroup_tests", {})

    evaluated = []
    for k, v in tests.items():
        if v.get("skipped_due_to_saturation", False):
            continue
        rmse = v.get("rmse_composed_vs_direct", None)
        if rmse is not None:
            evaluated.append((k, float(rmse)))

    if len(evaluated) == 0:
        return {"label": "SCOPE_LIMITED_SATURATION", "reason": "no non-saturated evaluated semigroup triple"}

    failed = [k for k, rmse in evaluated if rmse >= rmse_th]
    if failed:
        return {"label": "CHALLENGED", "reason": f"rmse>=threshold on {failed}"}

    if gate.get("pass", True) is False:
        return {"label": "SCOPE_LIMITED_SATURATION", "reason": "saturation gate failed"}

    return {"label": "SUPPORTED", "reason": "all evaluated triples pass rmse threshold"}


def load_cell(out_root: Path, scheme: str, estimator: str, rmse_th: float) -> Dict[str, object]:
    p = out_root / f"{scheme}_{estimator}" / "semigroup_summary.json"
    if not p.exists():
        return {
            "scheme": scheme,
            "estimator": estimator,
            "status": "MISSING",
            "label": "MISSING",
            "reason": "missing semigroup_summary.json",
            "path": str(p.as_posix()),
        }
    data = json.loads(p.read_text(encoding="utf-8"))
    decision = classify(data, rmse_th=rmse_th)

    best_rmse = None
    for _, v in data.get("semigroup_tests", {}).items():
        if v.get("skipped_due_to_saturation", False):
            continue
        rmse = v.get("rmse_composed_vs_direct", None)
        if rmse is None:
            continue
        best_rmse = rmse if best_rmse is None else min(best_rmse, rmse)

    return {
        "scheme": scheme,
        "estimator": estimator,
        "status": "OK",
        "label": decision["label"],
        "reason": decision["reason"],
        "best_rmse_composed_vs_direct": best_rmse,
        "saturation_gate_pass": data.get("saturation_gate", {}).get("pass", None),
        "n_non_saturated_adjacent_pairs": data.get("saturation_gate", {}).get("n_non_saturated_adjacent_pairs", None),
        "n_evaluated_semigroup_triples": data.get("saturation_gate", {}).get("n_evaluated_semigroup_triples", None),
        "path": str(p.as_posix()),
    }


def to_markdown(df: pd.DataFrame, out_md: Path):
    lines: List[str] = []
    lines.append("# Scheme-Estimator Matrix (v0.1)")
    lines.append("")
    lines.append("| Scheme | Estimator | Label | Best RMSE | Non-sat pairs | Evaluated triples |")
    lines.append("|---|---|---|---:|---:|---:|")
    for _, r in df.iterrows():
        rmse = "" if pd.isna(r["best_rmse_composed_vs_direct"]) else f"{float(r['best_rmse_composed_vs_direct']):.6f}"
        n1 = "" if pd.isna(r["n_non_saturated_adjacent_pairs"]) else str(int(r["n_non_saturated_adjacent_pairs"]))
        n2 = "" if pd.isna(r["n_evaluated_semigroup_triples"]) else str(int(r["n_evaluated_semigroup_triples"]))
        lines.append(f"| {r['scheme']} | {r['estimator']} | {r['label']} | {rmse} | {n1} | {n2} |")
    lines.append("")
    lines.append("## Notes")
    lines.append("- `SUPPORTED`: evaluated non-saturated triples all pass RMSE threshold.")
    lines.append("- `SCOPE_LIMITED_SATURATION`: saturation gate blocks interpretation at this configuration.")
    lines.append("- `CHALLENGED`: at least one evaluated triple exceeds RMSE threshold.")
    lines.append("- `MISSING`: result artifact not found.")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_root", default="out/scheme_audit_full")
    ap.add_argument("--schemes", nargs="+", default=["majority", "threshold_low", "threshold_high", "average"])
    ap.add_argument("--estimators", nargs="+", default=["C_frozen", "C_activity", "H"])
    ap.add_argument("--rmse_threshold", type=float, default=0.05)
    ap.add_argument("--out_csv", default="out/scheme_matrix_v0_1.csv")
    ap.add_argument("--out_md", default="out/scheme_matrix_v0_1.md")
    args = ap.parse_args()

    out_root = Path(args.out_root)
    rows = []
    for s in args.schemes:
        for e in args.estimators:
            rows.append(load_cell(out_root=out_root, scheme=s, estimator=e, rmse_th=args.rmse_threshold))

    df = pd.DataFrame(rows)
    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    to_markdown(df, out_md)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
