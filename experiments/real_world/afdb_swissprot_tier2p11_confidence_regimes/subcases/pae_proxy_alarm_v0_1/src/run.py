from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Dict, Any

import numpy as np
import pandas as pd
import yaml
import joblib

from .config import load_prereg
from .utils_hash import sha256_hex, sha256_file
from .io_dataset import load_metrics, require_columns, apply_basic_filters
from .features import build_xy
from .split import split_ids
from .modeling import train_logistic_regression, extract_logreg_coefficients
from .eval import evaluate_binary_classifier
from .plot_onepager import plot_onepage

def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True, help="path to PREREG.yaml")
    ap.add_argument("--run_id", default=None)
    args = ap.parse_args()

    cfg = load_prereg(args.prereg).raw

    # Resolve this subcase directory
    case_dir = Path(__file__).resolve().parents[1]
    out_root = case_dir / cfg["outputs"]["out_root"]
    out_root.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Lock prereg
    locked_path = run_dir / "PREREG.locked.yaml"
    _write_text(locked_path, Path(args.prereg).read_text(encoding="utf-8"))
    prereg_sha = sha256_hex(locked_path.read_text(encoding="utf-8"))

    # Load input metrics
    in_path = (case_dir / cfg["data"]["input_metrics_path"]).resolve() if not str(cfg["data"]["input_metrics_path"]).startswith("/") else Path(cfg["data"]["input_metrics_path"])
    df = load_metrics(in_path, fallback=cfg["data"].get("input_format_fallback", "csv"))
    id_field = cfg["data"]["id_field"]

    # Basic filters
    fmin = int(cfg["boundary"]["data_filters"]["min_length"])
    fmax = int(cfg["boundary"]["data_filters"]["max_length"])
    df = apply_basic_filters(df, min_len=fmin, max_len=fmax, id_field=id_field)

    # Required columns
    feature_whitelist = cfg["boundary"]["feature_whitelist"]
    label_field = cfg["boundary"]["label_field"]
    required = [id_field] + feature_whitelist + [label_field]
    require_columns(df, required)

    # Build dataset
    dxy = build_xy(
        df=df,
        id_field=id_field,
        feature_whitelist=feature_whitelist,
        label_field=label_field,
        tau_pae=float(cfg["boundary"]["tau_pae"]),
        drop_na_features=bool(cfg["boundary"]["data_filters"]["drop_na_features"]),
        drop_na_label=bool(cfg["boundary"]["data_filters"]["drop_na_label"]),
    )

    X, y, ids = dxy.X, dxy.y, dxy.ids

    # Split
    seed_string = cfg["data"]["seed_string"]
    sp = cfg["split"]
    split = split_ids(ids, seed_string=seed_string, train_frac=float(sp["train_frac"]), val_frac=float(sp["val_frac"]), test_frac=float(sp["test_frac"]))

    X_train, y_train = X.iloc[split.train], y[split.train]
    X_val, y_val = X.iloc[split.val], y[split.val]
    X_test, y_test = X.iloc[split.test], y[split.test]

    # Train
    mcfg = cfg["model"]
    if mcfg["family"] != "logistic_regression":
        raise ValueError("v0.1 only supports logistic_regression (expand in later versions).")

    model = train_logistic_regression(
        X=X_train,
        y=y_train,
        standardize=bool(mcfg["standardize"]),
        impute_strategy=str(mcfg["impute_strategy"]),
        params=mcfg["params"],
    )

    # Scores
    s_train = model.pipeline.predict_proba(X_train.to_numpy())[:, 1]
    s_val = model.pipeline.predict_proba(X_val.to_numpy())[:, 1]
    s_test = model.pipeline.predict_proba(X_test.to_numpy())[:, 1]

    # Evaluate
    eval_obj = evaluate_binary_classifier(
        y_train=y_train, s_train=s_train,
        y_val=y_val, s_val=s_val,
        y_test=y_test, s_test=s_test,
        fpr_targets=[float(x) for x in cfg["monitorability"]["fpr_targets"]],
    )

    # Save model
    model_path = run_dir / "model.joblib"
    joblib.dump({"pipeline": model.pipeline, "feature_names": model.feature_names}, model_path)

    # Coefficients (optional)
    coefs = extract_logreg_coefficients(model)

    # Dataset snapshot
    input_hash = sha256_file(str(in_path))
    feature_hash = sha256_hex(",".join(feature_whitelist))
    snapshot = {
        "subcase_id": cfg["preregistration"]["case_id"],
        "parent_case_id": cfg["preregistration"]["parent_case_id"],
        "run_id": run_id,
        "input_metrics_path": str(in_path),
        "input_metrics_sha256": input_hash,
        "prereg_sha256": prereg_sha,
        "n_total": int(len(X)),
        "n_train": int(len(X_train)),
        "n_val": int(len(X_val)),
        "n_test": int(len(X_test)),
        "tau_pae": float(cfg["boundary"]["tau_pae"]),
        "pos_rate_total": float(y.mean()),
        "pos_rate_train": float(y_train.mean()) if len(y_train) else float("nan"),
        "pos_rate_val": float(y_val.mean()) if len(y_val) else float("nan"),
        "pos_rate_test": float(y_test.mean()) if len(y_test) else float("nan"),
        "feature_whitelist": feature_whitelist,
        "feature_whitelist_sha256": feature_hash,
    }
    _write_json(run_dir / "dataset_snapshot.json", snapshot)

    # Boundary snapshot (train vs deploy)
    boundary_snapshot = {
        "B_train": cfg["boundary"]["B_train"],
        "B_deploy": cfg["boundary"]["B_deploy"],
        "feature_whitelist": feature_whitelist,
        "label_field": label_field,
        "tau_pae": float(cfg["boundary"]["tau_pae"]),
        "notes": "Alarm is trained with PAE labels but must be deployable with coord-only (B0) features.",
    }
    _write_json(run_dir / "boundary_snapshot.json", boundary_snapshot)

    # Eval report (markdown)
    lines = []
    lines.append("# Eval report — PAE Proxy Alarm (v0.1)\n\n")
    lines.append(f"- run_id: `{run_id}`\n")
    lines.append(f"- parent_case_id: `{cfg['preregistration']['parent_case_id']}`\n")
    lines.append(f"- tau_pae: `{float(cfg['boundary']['tau_pae'])}`\n")
    lines.append(f"- prereg_sha256: `{prereg_sha}`\n")
    lines.append(f"- input_metrics_sha256: `{input_hash}`\n\n")

    lines.append("## Global metrics (test)\n\n")
    lines.append(f"- ROC-AUC: `{eval_obj['test_roc_auc']}`\n")
    lines.append(f"- PR-AUC: `{eval_obj['test_pr_auc']}`\n\n")

    lines.append("## Operating points (monitorability gate)\n\n")
    lines.append("| target FPR cap | threshold (val-selected) | achieved FPR (test) | TPR/coverage (test) | precision (test) | flagged per 10k | missed per 10k | usable? |\n")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|:---:|\n")
    for op in eval_obj["operating_points"]:
        flagged_10k = float(op["flagged_rate"]) * 10000.0
        missed_10k = float(op["miss_rate"]) * 10000.0
        lines.append(
            f"| {op['fpr_target']:.4f} | {op['threshold']:.6f} | {op['fpr']:.6f} | {op['tpr']:.6f} | {op['precision']:.6f} | {flagged_10k:.2f} | {missed_10k:.2f} | {'OK' if op['usable'] else 'UNUSABLE'} |\n"
        )
    lines.append("\n")

    lines.append("## Coefficients (logistic regression; proxy correlations)\n\n")
    if coefs is None:
        lines.append("- (coefficients unavailable)\n")
    else:
        # show sorted by abs value
        items = sorted(coefs.items(), key=lambda kv: abs(kv[1]), reverse=True)
        lines.append("| feature | coef |\n|---|---:|\n")
        for k, v in items:
            lines.append(f"| {k} | {v:.6f} |\n")
    lines.append("\n")

    lines.append("## Interpretation rule\n\n")
    lines.append("- This is a proxy alarm case. Only claims allowed are about **alarm usability at low FPR** under the locked boundary.\n")
    lines.append("- If an operating point is UNUSABLE (TPR=0 at target FPR), treat that as a negative result for that operating point.\n")

    _write_text(run_dir / "eval_report.md", "".join(lines))

    # Save eval json
    _write_json(run_dir / "eval_metrics.json", eval_obj)

    # One-page plot
    footer = (
        f"subcase=pae_proxy_alarm_v0_1 | parent=afdb_swissprot_tier2p11_confidence_regimes | "
        f"run={run_id} | tau_pae={float(cfg['boundary']['tau_pae'])} | seed={seed_string} | feat_sha={feature_hash[:10]}"
    )
    plot_onepage(out_pdf=run_dir / "tradeoff_onepage.pdf", eval_obj=eval_obj, y_test=y_test, s_test=s_test, meta_footer=footer)

    # Run manifest
    manifest = {
        "subcase_id": cfg["preregistration"]["case_id"],
        "run_id": run_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "git_commit": os.environ.get("GIT_COMMIT", "UNKNOWN"),
        "prereg_sha256": prereg_sha,
        "input_metrics_sha256": input_hash,
        "artifacts": {
            "PREREG.locked.yaml": str(locked_path.resolve()),
            "dataset_snapshot.json": str((run_dir / "dataset_snapshot.json").resolve()),
            "boundary_snapshot.json": str((run_dir / "boundary_snapshot.json").resolve()),
            "model.joblib": str(model_path.resolve()),
            "eval_report.md": str((run_dir / "eval_report.md").resolve()),
            "tradeoff_onepage.pdf": str((run_dir / "tradeoff_onepage.pdf").resolve()),
            "eval_metrics.json": str((run_dir / "eval_metrics.json").resolve()),
        },
    }
    _write_json(run_dir / "run_manifest.json", manifest)

    print(f"Run complete. Outputs in: {run_dir}")

if __name__ == "__main__":
    main()
