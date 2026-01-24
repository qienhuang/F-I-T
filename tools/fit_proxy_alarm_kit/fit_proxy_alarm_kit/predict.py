from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .io_dataset import load_metrics, require_columns
from .modeling import from_dict, predict_proba


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="Path to alarm_model.json")
    ap.add_argument("--metrics", required=True, help="CSV/Parquet file with deploy-boundary features")
    ap.add_argument("--out", required=True, help="Output CSV with probabilities")
    ap.add_argument("--id_field", default="item_id", help="ID column name in metrics")
    ap.add_argument("--feature_whitelist", default=None, help="Optional JSON list of features (else infer from model)")
    args = ap.parse_args()

    model_obj = json.loads(Path(args.model).read_text(encoding="utf-8"))
    model = from_dict(model_obj)
    feature_names = list(model.feature_names)

    df = load_metrics(Path(args.metrics), fallback="csv")

    if args.feature_whitelist:
        feats = json.loads(args.feature_whitelist)
    else:
        feats = feature_names

    require_columns(df, [args.id_field] + feats)
    X = df[feats]
    p = predict_proba(model, X)

    out = pd.DataFrame({args.id_field: df[args.id_field].astype(str), "predicted_prob": p})
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)


if __name__ == "__main__":
    main()
