from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Any, Dict, List

import numpy as np
import joblib

from .config import load_prereg
from .utils_hash import sha256_hex, sha256_file
from .io_dataset import load_metrics, require_columns, apply_basic_filters
from .dataset import build_dataset
from .split import split_ids
from .modeling import train_ridge, predict
from .eval import regression_metrics, monitorability_operating_points
from .plot_onepager import plot_onepage

def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--run_id", default=None)
    args = ap.parse_args()

    cfg = load_prereg(args.prereg).raw
    case_dir = Path(__file__).resolve().parents[1]
    out_root = case_dir / cfg["outputs"]["out_root"]
    out_root.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Lock prereg
    locked = run_dir / "PREREG.locked.yaml"
    _write_text(locked, Path(args.prereg).read_text(encoding="utf-8"))
    prereg_sha = sha256_hex(locked.read_text(encoding="utf-8"))

    # Load input
    in_path_cfg = cfg["data"]["input_metrics_path"]
    in_path = (case_dir / in_path_cfg).resolve() if not str(in_path_cfg).startswith("/") else Path(in_path_cfg)
    df = load_metrics(in_path, fallback=cfg["data"].get("input_format_fallback", "csv"))
    id_field = cfg["data"]["id_field"]

    # Filters
    fmin = int(cfg["boundary"]["data_filters"]["min_length"])
    fmax = int(cfg["boundary"]["data_filters"]["max_length"])
    df = apply_basic_filters(df, min_len=fmin, max_len=fmax, id_field=id_field)

    feat = list(cfg["boundary"]["feature_whitelist"])
    msa_field = cfg["boundary"]["label_fields"]["msa_depth"]
    c3_field = cfg["boundary"]["label_fields"]["c3_deficit"]
    required = [id_field] + feat + [msa_field]
    # c3 field optional
    require_columns(df, required)

    dataset = build_dataset(
        df=df,
        id_field=id_field,
        feature_whitelist=feat,
        msa_depth_field=msa_field,
        c3_field=c3_field,
        compute_c3_from_depth_if_missing=bool(cfg["boundary"]["targets"]["fallback_compute_from_msa_depth_if_missing"]),
        drop_na_features=bool(cfg["boundary"]["data_filters"]["drop_na_features"]),
        drop_na_label=bool(cfg["boundary"]["data_filters"]["drop_na_label"]),
    )

    # Split
    seed = cfg["data"]["seed_string"]
    sp = cfg["split"]
    split = split_ids(dataset.ids, seed_string=seed, train_frac=float(sp["train_frac"]), val_frac=float(sp["val_frac"]), test_frac=float(sp["test_frac"]))

    X_train = dataset.X.iloc[split.train]
    y_train = dataset.y_reg[split.train]

    X_val = dataset.X.iloc[split.val]
    y_val_reg = dataset.y_reg[split.val]

    X_test = dataset.X.iloc[split.test]
    y_test_reg = dataset.y_reg[split.test]

    # Train model
    mcfg = cfg["model"]
    if mcfg["family"] != "ridge_regression":
        raise ValueError("v0.1 supports ridge_regression only.")
    model = train_ridge(
        X=X_train,
        y=y_train,
        standardize=bool(mcfg["standardize"]),
        impute_strategy=str(mcfg["impute_strategy"]),
        params=mcfg["params"],
    )

    # Predict
    pred_val = predict(model, X_val)
    pred_test = predict(model, X_test)

    # Regression eval
    reg = regression_metrics(y_test_reg, pred_test)

    # Monitorability event
    tau_depth = int(cfg["boundary"]["event"]["tau_msa_depth"])
    y_val_evt = (dataset.msa_depth[split.val] <= tau_depth).astype(int)
    y_test_evt = (dataset.msa_depth[split.test] <= tau_depth).astype(int)

    # Use score = predicted C3_hat (higher => more deficit => more likely sparse MSA)
    mon = monitorability_operating_points(
        y_val=y_val_evt,
        s_val=pred_val,
        y_test=y_test_evt,
        s_test=pred_test,
        fpr_targets=[float(x) for x in cfg["monitorability"]["fpr_targets"]],
    )

    # Save model
    model_path = run_dir / "model.joblib"
    joblib.dump({"pipeline": model.pipeline, "feature_names": model.feature_names}, model_path)

    # Snapshots
    input_hash = sha256_file(str(in_path))
    feature_hash = sha256_hex(",".join(feat))
    _write_json(run_dir / "dataset_snapshot.json", {
        "subcase_id": cfg["preregistration"]["case_id"],
        "parent_case_id": cfg["preregistration"]["parent_case_id"],
        "run_id": run_id,
        "input_metrics_path": str(in_path),
        "input_metrics_sha256": input_hash,
        "prereg_sha256": prereg_sha,
        "n_total": int(len(dataset.ids)),
        "n_train": int(len(split.train)),
        "n_val": int(len(split.val)),
        "n_test": int(len(split.test)),
        "tau_msa_depth": tau_depth,
        "event_pos_rate_test": float(y_test_evt.mean()) if len(y_test_evt) else float("nan"),
        "reg_target": "C3",
        "feature_whitelist": feat,
        "feature_whitelist_sha256": feature_hash,
    })

    _write_json(run_dir / "boundary_snapshot.json", {
        "train_boundary": cfg["boundary"]["train_boundary"],
        "deploy_boundary": cfg["boundary"]["deploy_boundary"],
        "feature_whitelist": feat,
        "label_fields": {"msa_depth": msa_field, "c3_deficit": c3_field},
        "tau_msa_depth": tau_depth,
        "notes": "This run trains a proxy C3_hat under B0-only features and evaluates alarm usability for E_msa_sparse.",
    })

    # Eval report
    lines = []
    lines.append("# Eval report — MSA Deficit Proxy (v0.1)\n\n")
    lines.append(f"- run_id: `{run_id}`\n")
    lines.append(f"- parent_case_id: `{cfg['preregistration']['parent_case_id']}`\n")
    lines.append(f"- tau_msa_depth: `{tau_depth}`\n")
    lines.append(f"- prereg_sha256: `{prereg_sha}`\n")
    lines.append(f"- input_metrics_sha256: `{input_hash}`\n\n")

    lines.append("## Regression quality (test)\n\n")
    lines.append(f"- MAE: `{reg['mae']}`\n")
    lines.append(f"- RMSE: `{reg['rmse']}`\n")
    lines.append(f"- Spearman: `{reg['spearman']}`\n")
    lines.append(f"- R2: `{reg['r2']}`\n\n")

    lines.append("## Monitorability operating points for E_msa_sparse (test)\n\n")
    lines.append("| target FPR cap | threshold (val-selected) | achieved FPR (test) | TPR/coverage (test) | precision (test) | flagged per 10k | missed per 10k | usable? |\n")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|:---:|\n")
    for op in mon["operating_points"]:
        flagged_10k = float(op["flagged_rate"]) * 10000.0
        missed_10k = float(op["miss_rate"]) * 10000.0
        lines.append(
            f"| {op['fpr_target']:.4f} | {op['threshold']:.6f} | {op['fpr']:.6f} | {op['tpr']:.6f} | {op['precision']:.6f} | {flagged_10k:.2f} | {missed_10k:.2f} | {'OK' if op['usable'] else 'UNUSABLE'} |\n"
        )
    lines.append("\n")

    lines.append("## Interpretation rule\n\n")
    lines.append("- This case yields a proxy estimator channel $ \\widehat{C3} $ under B0-only features.\n")
    lines.append("- Treat monitorability at low FPR as the operational gate for using $ \\widehat{C3} $ as an alarm.\n")
    lines.append("- Do not make biological claims; stay within the locked boundary.\n")
    _write_text(run_dir / "eval_report.md", "".join(lines))

    # Save eval json
    _write_json(run_dir / "eval_metrics.json", {"regression": reg, "monitorability": mon})

    # Onepager
    footer = (
        f"subcase=msa_deficit_proxy_v0_1 | parent=afdb_swissprot_tier2p11_confidence_regimes | "
        f"run={run_id} | tau_msa_depth={tau_depth} | seed={seed} | feat_sha={feature_hash[:10]}"
    )
    plot_onepage(out_pdf=run_dir / "tradeoff_onepage.pdf", y_true=y_test_reg, y_pred=pred_test, roc=mon["roc_curve"], ops=mon["operating_points"], meta_footer=footer)

    # Manifest
    manifest = {
        "subcase_id": cfg["preregistration"]["case_id"],
        "run_id": run_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "git_commit": os.environ.get("GIT_COMMIT", "UNKNOWN"),
        "prereg_sha256": prereg_sha,
        "input_metrics_sha256": input_hash,
        "artifacts": {
            "PREREG.locked.yaml": str(locked.resolve()),
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
