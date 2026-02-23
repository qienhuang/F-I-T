from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def saturation_row(sub: pd.DataFrame, eps: float, ratio: float) -> dict:
    values = sub["value"].astype(float).to_numpy()
    n = len(values)
    near0 = int(np.sum(values <= eps))
    near1 = int(np.sum(values >= (1.0 - eps)))
    near0_ratio = float(near0 / n) if n else 0.0
    near1_ratio = float(near1 / n) if n else 0.0
    sat_ratio = near0_ratio + near1_ratio
    return {
        "n": int(n),
        "near0_ratio": near0_ratio,
        "near1_ratio": near1_ratio,
        "saturation_ratio": sat_ratio,
        "saturated": bool(sat_ratio >= ratio),
        "eps": eps,
        "ratio_threshold": ratio,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out_csv", default="results/saturation_matrix.csv")
    ap.add_argument("--out_json", default="results/saturation_summary.json")
    ap.add_argument("--eps", type=float, default=0.10)
    ap.add_argument("--ratio", type=float, default=0.90)
    args = ap.parse_args()

    df = load_table(Path(args.input))
    required_cols = {"scheme", "estimator", "b", "value"}
    missing = sorted(required_cols - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns in input: {missing}")

    rows = []
    for (scheme, estimator, b), sub in df.groupby(["scheme", "estimator", "b"], dropna=False):
        r = saturation_row(sub, eps=args.eps, ratio=args.ratio)
        r["scheme"] = str(scheme)
        r["estimator"] = str(estimator)
        r["b"] = int(b)
        rows.append(r)

    out_df = pd.DataFrame(rows).sort_values(by=["scheme", "estimator", "b"]).reset_index(drop=True)
    out_csv = Path(args.out_csv)
    out_json = Path(args.out_json)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_csv, index=False)

    summary = {
        "input": args.input,
        "eps": args.eps,
        "ratio_threshold": args.ratio,
        "groups_total": int(len(out_df)),
        "groups_saturated": int(out_df["saturated"].sum()),
        "groups_non_saturated": int((~out_df["saturated"]).sum()),
        "non_saturated_by_estimator": (
            out_df.loc[~out_df["saturated"]]
            .groupby("estimator")["scheme"]
            .count()
            .astype(int)
            .to_dict()
        ),
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(out_df.to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

