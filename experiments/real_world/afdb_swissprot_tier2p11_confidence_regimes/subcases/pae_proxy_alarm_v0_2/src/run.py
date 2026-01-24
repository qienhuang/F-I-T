from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import joblib

from .config import load_prereg
from .utils_hash import sha256_hex, sha256_file, stable_hash_order
from .io_dataset import load_metrics, require_columns, apply_basic_filters
from .dataset import build_dataset, Dataset
from .split import holdout_split, labeled_train_val_split
from .modeling import train_logreg, predict_proba
from .eval import evaluate_holdout
from .acquisition import select_batch
from .event import detect_covjump
from .plot_onepager import plot_onepage_active

def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def _subset(dataset: Dataset, idx: np.ndarray) -> Dataset:
    return Dataset(ids=dataset.ids[idx], X=dataset.X.iloc[idx].reset_index(drop=True), y_oracle=dataset.y_oracle[idx], meta=dataset.meta)

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
    in_path = Path(in_path_cfg)
    if not in_path.is_absolute():
        in_path = (case_dir / in_path_cfg).resolve()
    df = load_metrics(in_path, fallback=cfg["data"].get("input_format_fallback", "csv"))
    id_field = cfg["data"]["id_field"]

    # Filters
    fmin = int(cfg["boundary"]["data_filters"]["min_length"])
    fmax = int(cfg["boundary"]["data_filters"]["max_length"])
    df = apply_basic_filters(df, min_len=fmin, max_len=fmax, id_field=id_field)

    feat = list(cfg["boundary"]["feature_whitelist"])
    label_field = cfg["boundary"]["label_field"]
    required = [id_field] + feat + [label_field]
    require_columns(df, required)

    dataset = build_dataset(
        df=df,
        id_field=id_field,
        feature_whitelist=feat,
        label_field=label_field,
        tau_pae=float(cfg["boundary"]["tau_pae"]),
        drop_na_features=bool(cfg["boundary"]["data_filters"]["drop_na_features"]),
        drop_na_label=bool(cfg["boundary"]["data_filters"]["drop_na_label"]),
    )

    # Dataset snapshot
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
        "pos_rate_total": float(dataset.y_oracle.mean()),
        "tau_pae": float(cfg["boundary"]["tau_pae"]),
        "feature_whitelist": feat,
        "feature_whitelist_sha256": feature_hash,
    })

    # Boundary snapshot
    _write_json(run_dir / "boundary_snapshot.json", {
        "train_boundary": cfg["boundary"]["train_boundary"],
        "deploy_boundary": cfg["boundary"]["deploy_boundary"],
        "feature_whitelist": feat,
        "label_field": label_field,
        "tau_pae": float(cfg["boundary"]["tau_pae"]),
        "oracle_cost_accounting": cfg["evaluation"]["holdout_role"],
    })

    # Split: holdout vs pool
    seed = cfg["data"]["seed_string"]
    holdout_frac = float(cfg["evaluation"]["holdout_frac"])
    sp = holdout_split(dataset.ids, seed_string=seed, holdout_frac=holdout_frac)

    ds_hold = _subset(dataset, sp.holdout)
    ds_pool = _subset(dataset, sp.pool)

    # Policies
    policies: List[str] = list(cfg["acquisition"]["policies"])
    init_n = int(cfg["acquisition"]["init_labeled_n"])
    rounds = int(cfg["acquisition"]["rounds"])
    batch_size = int(cfg["acquisition"]["batch_size"])
    fpr_targets = [float(x) for x in cfg["monitorability"]["fpr_targets"]]
    primary_fpr = float(cfg["monitorability"]["primary_fpr_target"])
    if primary_fpr not in fpr_targets:
        raise ValueError("primary_fpr_target must be included in monitorability.fpr_targets")

    train_frac = float(cfg["split_labeled"]["train_frac"])
    val_frac = float(cfg["split_labeled"]["val_frac"])

    # Decision trace rows
    decision_rows = []

    round_metrics: Dict[str, List[Dict[str, Any]]] = {p: [] for p in policies}
    final_models_dir = run_dir / "models"
    final_models_dir.mkdir(parents=True, exist_ok=True)

    series_for_plot: Dict[str, Dict[str, Any]] = {}

    for policy in policies:
        # Deterministic initial seed from pool ids
        pool_ids = list(ds_pool.ids.tolist())
        pool_order = stable_hash_order(pool_ids, seed_string=seed + f"::{policy}::init")
        init_ids = pool_order[:min(init_n, len(pool_order))]

        labeled_set = set(init_ids)
        unlabeled_set = set(pool_order[min(init_n, len(pool_order)):])

        # Log initial queries as round 0
        for acc in init_ids:
            idx = int(np.where(ds_pool.ids == acc)[0][0])
            y = int(ds_pool.y_oracle[idx])
            decision_rows.append({
                "policy": policy,
                "round": 0,
                "accession": acc,
                "selected_by": "init_seed",
                "score": float("nan"),
                "predicted_prob": float("nan"),
                "revealed_label": y,
            })

        # Loop
        queried_counts = []
        tpr_primary_series = []
        fpr_primary_series = []
        batch_pos_rate_series = []
        round_index_series = []

        for r in range(0, rounds + 1):
            # Build labeled dataframe
            labeled_ids = sorted(list(labeled_set))
            labeled_idx = np.array([int(np.where(ds_pool.ids == acc)[0][0]) for acc in labeled_ids], dtype=int)
            X_lab = ds_pool.X.iloc[labeled_idx].reset_index(drop=True)
            y_lab = ds_pool.y_oracle[labeled_idx]
            ids_lab = ds_pool.ids[labeled_idx]

            # Train/val split within labeled
            lv = labeled_train_val_split(ids_lab, seed_string=seed + f"::{policy}::round{r}", train_frac=train_frac, val_frac=val_frac)
            if len(lv.train) == 0 or len(lv.val) == 0:
                # too small; skip
                break

            mcfg = cfg["model"]
            model = train_logreg(
                X=X_lab.iloc[lv.train],
                y=y_lab[lv.train],
                standardize=bool(mcfg["standardize"]),
                impute_strategy=str(mcfg["impute_strategy"]),
                params=mcfg["params"],
            )

            # Scores for val and holdout
            s_val = predict_proba(model, X_lab.iloc[lv.val])
            y_val = y_lab[lv.val]
            s_hold = predict_proba(model, ds_hold.X)
            y_hold = ds_hold.y_oracle

            ev = evaluate_holdout(y_val=y_val, s_val=s_val, y_test=y_hold, s_test=s_hold, fpr_targets=fpr_targets)

            # Extract primary operating point
            op_primary = None
            for op in ev["operating_points"]:
                if float(op["fpr_target"]) == primary_fpr:
                    op_primary = op
                    break
            assert op_primary is not None

            queried = len(labeled_set)
            queried_counts.append(int(queried))
            tpr_primary_series.append(float(op_primary["tpr"]))
            fpr_primary_series.append(float(op_primary["fpr"]))
            round_index_series.append(int(r))

            # batch positive rate from last queried batch (for r=0 use init seed)
            if r == 0:
                batch_pos = float(np.mean([row["revealed_label"] for row in decision_rows if row["policy"] == policy and row["round"] == 0])) if init_ids else float("nan")
            else:
                last_batch = [row["revealed_label"] for row in decision_rows if row["policy"] == policy and row["round"] == r]
                batch_pos = float(np.mean(last_batch)) if last_batch else float("nan")
            batch_pos_rate_series.append(batch_pos)

            # Store round metrics
            round_metrics[policy].append({
                "round": int(r),
                "queried_labels": int(queried),
                "holdout_n": int(len(y_hold)),
                "roc_auc": float(ev["roc_auc"]),
                "pr_auc": float(ev["pr_auc"]),
                "operating_points": ev["operating_points"],
            })

            if r == rounds:
                # Save final model for policy
                joblib.dump({"pipeline": model.pipeline, "feature_names": model.feature_names}, final_models_dir / f"{policy}.joblib")
                break

            # Select next batch from unlabeled pool
            unlabeled_ids = sorted(list(unlabeled_set))
            if len(unlabeled_ids) == 0:
                joblib.dump({"pipeline": model.pipeline, "feature_names": model.feature_names}, final_models_dir / f"{policy}.joblib")
                break

            unlabeled_idx = np.array([int(np.where(ds_pool.ids == acc)[0][0]) for acc in unlabeled_ids], dtype=int)
            X_unlab = ds_pool.X.iloc[unlabeled_idx].reset_index(drop=True)
            s_unlab = predict_proba(model, X_unlab)

            batch = select_batch(
                policy=policy,
                unlabeled_ids=unlabeled_ids,
                unlabeled_scores=s_unlab,
                batch_size=batch_size,
                seed=seed + f"::{policy}::round{r+1}",
            )

            # Log + reveal labels + update sets
            for acc in batch:
                # predicted prob at selection time
                j = unlabeled_ids.index(acc)
                p_sel = float(s_unlab[j])
                idx = int(np.where(ds_pool.ids == acc)[0][0])
                y = int(ds_pool.y_oracle[idx])
                # acquisition score: policy-specific
                if policy == "uncertainty":
                    score = float(abs(p_sel - 0.5))
                elif policy == "high_score":
                    score = float(p_sel)
                else:
                    score = float("nan")
                decision_rows.append({
                    "policy": policy,
                    "round": int(r+1),
                    "accession": acc,
                    "selected_by": policy,
                    "score": score,
                    "predicted_prob": p_sel,
                    "revealed_label": y,
                })
                labeled_set.add(acc)
                unlabeled_set.discard(acc)

        # Event detection on primary series
        evcfg = cfg["event"]
        W_jump = int(evcfg["W_jump_rounds"])
        delta_tpr = float(evcfg["delta_tpr"])
        event = detect_covjump(tpr_primary_series, W_jump=W_jump, delta_tpr=delta_tpr)

        series_for_plot[policy] = {
            "queried_labels": queried_counts,
            "tpr_primary": tpr_primary_series,
            "fpr_primary": fpr_primary_series,
            "batch_pos_rate": batch_pos_rate_series,
            "round_index": round_index_series,
            "event": event.__dict__,
        }

    # Save decision trace
    df_trace = pd.DataFrame(decision_rows)
    df_trace.to_csv(run_dir / "decision_trace.csv", index=False)

    # Save round metrics
    _write_json(run_dir / "round_metrics.json", {
        "subcase_id": cfg["preregistration"]["case_id"],
        "run_id": run_id,
        "primary_fpr_target": primary_fpr,
        "metrics_by_policy": round_metrics,
        "series_by_policy": series_for_plot,
    })

    # Write eval report
    lines = []
    lines.append("# Eval report — Active Acquisition (PAE Proxy Alarm v0.2)\n\n")
    lines.append(f"- run_id: `{run_id}`\n")
    lines.append(f"- parent_case_id: `{cfg['preregistration']['parent_case_id']}`\n")
    lines.append(f"- tau_pae: `{float(cfg['boundary']['tau_pae'])}`\n")
    lines.append(f"- primary FPR cap: `{primary_fpr}`\n")
    lines.append(f"- prereg_sha256: `{prereg_sha}`\n")
    lines.append(f"- input_metrics_sha256: `{input_hash}`\n\n")

    lines.append("## Policy summary (final round)\n\n")
    lines.append("| policy | final queried labels | final TPR@cap | final achieved FPR | event E_covjump? | event round |\n")
    lines.append("|---|---:|---:|---:|:---:|---:|\n")
    for policy, ser in series_for_plot.items():
        if len(ser["queried_labels"]) == 0:
            continue
        tpr_final = ser["tpr_primary"][-1]
        fpr_final = ser["fpr_primary"][-1]
        ev = ser["event"]
        lines.append(f"| {policy} | {ser['queried_labels'][-1]} | {tpr_final:.6f} | {fpr_final:.6f} | {'yes' if ev['found'] else 'no'} | {ev['round_index'] if ev['round_index'] is not None else ''} |\n")
    lines.append("\n")

    lines.append("## Interpretation rule\n\n")
    lines.append("- Allowed claims are **budgeted learning curves** and **low‑FPR alarm usability** under the locked boundary.\n")
    lines.append("- Do not treat policy differences as causal mechanisms; treat them as protocol-level differences.\n\n")
    _write_text(run_dir / "eval_report.md", "".join(lines))

    # Plot onepager
    footer = (
        f"subcase=pae_proxy_alarm_v0_2 | parent=afdb_swissprot_tier2p11_confidence_regimes | "
        f"run={run_id} | tau_pae={float(cfg['boundary']['tau_pae'])} | cap={primary_fpr} | seed={seed} | feat_sha={feature_hash[:10]}"
    )
    plot_onepage_active(out_pdf=run_dir / "tradeoff_onepage.pdf", series_by_policy=series_for_plot, primary_fpr_target=primary_fpr, meta_footer=footer)

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
            "decision_trace.csv": str((run_dir / "decision_trace.csv").resolve()),
            "round_metrics.json": str((run_dir / "round_metrics.json").resolve()),
            "eval_report.md": str((run_dir / "eval_report.md").resolve()),
            "tradeoff_onepage.pdf": str((run_dir / "tradeoff_onepage.pdf").resolve()),
            "models_dir": str(final_models_dir.resolve()),
        },
    }
    _write_json(run_dir / "run_manifest.json", manifest)

    print(f"Run complete. Outputs in: {run_dir}")

if __name__ == "__main__":
    main()
