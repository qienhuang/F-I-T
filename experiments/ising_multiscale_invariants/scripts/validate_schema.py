from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="results/schema_validation.json")
    ap.add_argument("--scales", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--required_estimators", nargs="+", default=["C_frozen", "H_2x2"])
    args = ap.parse_args()

    input_path = Path(args.input)
    out_path = Path(args.out)

    df = load_table(input_path)
    required_cols = ["seed", "t", "scheme", "b", "estimator", "value"]
    missing_cols = [c for c in required_cols if c not in df.columns]

    issues: list[str] = []
    if missing_cols:
        issues.append(f"missing_columns={missing_cols}")

    if not missing_cols:
        null_counts = {c: int(df[c].isna().sum()) for c in required_cols}
        null_issues = {k: v for k, v in null_counts.items() if v > 0}
        if null_issues:
            issues.append(f"null_values={null_issues}")

        dup_count = int(
            df.duplicated(subset=["seed", "t", "scheme", "b", "estimator"], keep=False).sum()
        )
        if dup_count > 0:
            issues.append(f"duplicate_rows={dup_count}")

        invalid_scale = int((~df["b"].isin(args.scales)).sum())
        if invalid_scale > 0:
            issues.append(f"invalid_scale_rows={invalid_scale}")

        for est in ["C_frozen", "C_activity", "H_2x2"]:
            mask = df["estimator"] == est
            if mask.any():
                out_range = int(((df.loc[mask, "value"] < 0.0) | (df.loc[mask, "value"] > 1.0)).sum())
                if out_range > 0:
                    issues.append(f"value_out_of_range_{est}={out_range}")

        present_estimators = sorted(df["estimator"].dropna().astype(str).unique().tolist())
        for req_est in args.required_estimators:
            if req_est not in present_estimators:
                issues.append(f"missing_required_estimator={req_est}")

    report = {
        "input": str(input_path),
        "rows": int(len(df)),
        "required_columns": required_cols,
        "present_columns": sorted(df.columns.tolist()),
        "scales_expected": args.scales,
        "required_estimators": args.required_estimators,
        "issues": issues,
        "pass": len(issues) == 0,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

