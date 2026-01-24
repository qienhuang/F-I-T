from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import joblib

from .config import load_prereg
from .utils_hash import sha256_hex, sha256_file, stable_hash_order
from .io_dataset import load_metrics, require_columns, apply_basic_filters
from .dataset import build_dual_oracle_dataset
from .split import holdout_split, labeled_train_val_split
from .modeling import (
    train_logreg_safe, predict_proba_safe,
    train_ridge_safe, predict_reg_safe,
)
from .eval import evaluate_binary_classifier, regression_metrics
from .acquisition import (
    uncertainty_from_probs, novelty_min_dist, minmax_norm, rank_ids,
)
from .event import detect_covjump
from .plot_onepager import plot_onepage_v0_5

def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def _zscore_matrix(X: pd.DataFrame) -> np.ndarray:
    A = X.to_numpy().astype(float)
    mu = np.nanmean(A, axis=0)
    sd = np.nanstd(A, axis=0)
    sd = np.where(sd <= 1e-12, 1.0, sd)
    return (A - mu) / sd

def _uncertainty_mass(probs: np.ndarray) -> float:
    u = uncertainty_from_probs(probs)
    return float(np.mean(u)) if len(u) else 0.0

def _parse_policy(policy: str) -> Tuple[str, str]:
    if "__" in policy:
        a, r = policy.split("__", 1)
        return a.strip(), r.strip()
    return policy.strip(), "uncertainty"

def _allocate_fixed_split(q_total: int, q_pae_fixed: int, q_msa_fixed: int) -> Tuple[int, int]:
    q_pae = min(int(q_pae_fixed), int(q_total))
    q_msa = min(int(q_msa_fixed), int(q_total - q_pae))
    rem = int(q_total - q_pae - q_msa)
    if rem > 0:
        q_msa += rem
    return q_pae, q_msa

def _allocate_by_ratio(q_total: int, w_pae: float, w_msa: float) -> Tuple[int, int]:
    denom = float(w_pae + w_msa)
    if denom <= 0:
        return q_total // 2, q_total - (q_total // 2)
    q_pae = int(round(q_total * (w_pae / denom)))
    q_pae = max(0, min(q_total, q_pae))
    q_msa = q_total - q_pae
    return q_pae, q_msa

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
    pae_field = cfg["boundary"]["oracle_fields"]["pae_value"]
    msa_field = cfg["boundary"]["oracle_fields"]["msa_depth"]
    required = [id_field] + feat + [pae_field, msa_field]
    require_columns(df, required)

    ds = build_dual_oracle_dataset(
        df=df,
        id_field=id_field,
        feature_whitelist=feat,
        pae_field=pae_field,
        msa_field=msa_field,
        tau_pae=float(cfg["boundary"]["thresholds"]["tau_pae"]),
        tau_msa_depth=float(cfg["boundary"]["thresholds"]["tau_msa_depth"]),
        drop_na_features=bool(cfg["boundary"]["data_filters"]["drop_na_features"]),
        drop_na_oracles=bool(cfg["boundary"]["data_filters"]["drop_na_oracles"]),
    )

    # Z-scored feature space for novelty (B0-only; allowed)
    Xz_all = _zscore_matrix(ds.X)

    # Snapshot
    input_hash = sha256_file(str(in_path))
    feature_hash = sha256_hex(",".join(feat))
    _write_json(run_dir / "dataset_snapshot.json", {
        "subcase_id": cfg["preregistration"]["case_id"],
        "parent_case_id": cfg["preregistration"]["parent_case_id"],
        "run_id": run_id,
        "input_metrics_path": str(in_path),
        "input_metrics_sha256": input_hash,
        "prereg_sha256": prereg_sha,
        "n_total": int(len(ds.ids)),
        "tau_pae": float(cfg["boundary"]["thresholds"]["tau_pae"]),
        "tau_msa_depth": float(cfg["boundary"]["thresholds"]["tau_msa_depth"]),
        "feature_whitelist": feat,
        "feature_whitelist_sha256": feature_hash,
        "pae_available_rate": float(ds.pae_available.mean()) if len(ds.ids) else float("nan"),
        "msa_available_rate": float(ds.msa_available.mean()) if len(ds.ids) else float("nan"),
    })

    _write_json(run_dir / "boundary_snapshot.json", {
        "train_boundary": cfg["boundary"]["train_boundary"],
        "deploy_boundary": cfg["boundary"]["deploy_boundary"],
        "feature_whitelist": feat,
        "oracle_fields": {"pae_value": pae_field, "msa_depth": msa_field},
        "thresholds": cfg["boundary"]["thresholds"],
        "holdout_role": cfg["evaluation"]["holdout_role"],
        "novelty_space": cfg["acquisition"]["ranking"]["composite"]["novelty_space"],
    })

    seed = cfg["data"]["seed_string"]
    holdout_frac = float(cfg["evaluation"]["holdout_frac"])

    sp_pae = holdout_split(ds.ids, seed_string=seed + "::pae", holdout_frac=holdout_frac, mask=ds.pae_available)
    sp_msa = holdout_split(ds.ids, seed_string=seed + "::msa", holdout_frac=holdout_frac, mask=ds.msa_available)

    hold_pae = sp_pae.holdout
    pool_pae = sp_pae.pool
    hold_msa = sp_msa.holdout
    pool_msa = sp_msa.pool

    # Config
    rounds = int(cfg["acquisition"]["rounds"])
    budgets = cfg["acquisition"]["oracle_budgets"]
    pae_budget_total = int(budgets["pae_total"])
    msa_budget_total = int(budgets["msa_total"])

    init_pae_n = int(cfg["acquisition"]["init_labeled"]["pae_n"])
    init_msa_n = int(cfg["acquisition"]["init_labeled"]["msa_n"])

    batch_cfg = cfg["acquisition"]["batch"]
    batch_mode = str(batch_cfg["mode"])
    q_total = int(batch_cfg.get("total_per_round", 0))
    q_pae_fixed = int(batch_cfg.get("fixed_split", {}).get("pae_per_round", 0))
    q_msa_fixed = int(batch_cfg.get("fixed_split", {}).get("msa_per_round", 0))

    policies = list(cfg["acquisition"]["policies"])
    fallback_no_model = str(cfg["acquisition"]["selection"]["fallback_if_no_model"])

    train_frac = float(cfg["split_labeled"]["train_frac"])
    val_frac = float(cfg["split_labeled"]["val_frac"])

    fpr_targets = [float(x) for x in cfg["monitorability"]["fpr_targets"]]
    primary_fpr = float(cfg["monitorability"]["primary_fpr_target"])
    eps_fpr = float(cfg["monitorability"].get("usable_epsilon_fpr", 0.0))

    comp_cfg = cfg["acquisition"]["ranking"]["composite"]
    alpha_unc = float(comp_cfg["alpha_uncertainty"])

    # model configs
    pae_mcfg = cfg["model"]["pae_classifier"]
    msa_clf_cfg = cfg["model"]["msa_classifier"]
    msa_reg_cfg = cfg["model"]["msa_regressor"]

    # event config
    W_jump = int(cfg["event"]["W_jump_rounds"])
    delta_tpr = float(cfg["event"]["delta_tpr"])

    decision_rows = []
    round_metrics: Dict[str, List[Dict[str, Any]]] = {p: [] for p in policies}
    series_by_policy: Dict[str, Dict[str, Any]] = {}

    models_dir = run_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    pool_pae_ids = ds.ids[pool_pae].tolist()
    pool_msa_ids = ds.ids[pool_msa].tolist()
    init_order_pae = stable_hash_order(pool_pae_ids, seed_string=seed + "::init_pae")
    init_order_msa = stable_hash_order(pool_msa_ids, seed_string=seed + "::init_msa")

    # Holdout evaluation sets
    X_pae_hold = ds.X.iloc[hold_pae].reset_index(drop=True)
    y_pae_hold = ds.y_pae[hold_pae]
    X_msa_hold = ds.X.iloc[hold_msa].reset_index(drop=True)
    y_msa_hold = ds.y_msa[hold_msa]
    c3_hold = ds.c3[hold_msa]

    for policy in policies:
        alloc_policy, rank_policy = _parse_policy(policy)

        labeled_pae = set(init_order_pae[:min(init_pae_n, len(init_order_pae), pae_budget_total)])
        labeled_msa = set(init_order_msa[:min(init_msa_n, len(init_order_msa), msa_budget_total)])

        pae_used = len(labeled_pae)
        msa_used = len(labeled_msa)

        unlabeled_pae = set(pool_pae_ids) - labeled_pae
        unlabeled_msa = set(pool_msa_ids) - labeled_msa

        # series containers
        pae_series = {"queried_labels": [], "tpr_primary": [], "fpr_primary": [], "event": None}
        msa_cls_series = {"queried_labels": [], "tpr_primary": [], "fpr_primary": [], "event": None}
        msa_reg_series = {"queried_labels": [], "mae_holdout": [], "rmse_holdout": [], "spearman_holdout": [], "r2_holdout": []}
        alloc_series = {"round": [0], "frac_pae": [float("nan")]}
        joint = {"joint_usable_round": rounds + 1}

        joint_achieved = False

        # log init labels
        for acc in sorted(list(labeled_pae)):
            idx = int(np.where(ds.ids == acc)[0][0])
            decision_rows.append({
                "policy": policy,
                "allocation_policy": alloc_policy,
                "ranking_policy": rank_policy,
                "round": 0,
                "oracle_type": "PAE",
                "accession": acc,
                "selected_by": "init_seed",
                "predicted_prob": float("nan"),
                "uncertainty": float("nan"),
                "novelty": float("nan"),
                "novelty_norm": float("nan"),
                "composite_score": float("nan"),
                "revealed_value": float(ds.pae_value[idx]),
                "revealed_label": int(ds.y_pae[idx]),
            })
        for acc in sorted(list(labeled_msa)):
            idx = int(np.where(ds.ids == acc)[0][0])
            decision_rows.append({
                "policy": policy,
                "allocation_policy": alloc_policy,
                "ranking_policy": rank_policy,
                "round": 0,
                "oracle_type": "MSA",
                "accession": acc,
                "selected_by": "init_seed",
                "predicted_prob": float("nan"),
                "uncertainty": float("nan"),
                "novelty": float("nan"),
                "novelty_norm": float("nan"),
                "composite_score": float("nan"),
                "revealed_value": float(ds.msa_depth[idx]),
                "revealed_label": int(ds.y_msa[idx]),
            })

        for r in range(0, rounds + 1):
            # Build labeled arrays
            pae_ids_lab = sorted(list(labeled_pae))
            msa_ids_lab = sorted(list(labeled_msa))
            pae_idx_lab = np.array([int(np.where(ds.ids == acc)[0][0]) for acc in pae_ids_lab], dtype=int) if len(pae_ids_lab) else np.array([], dtype=int)
            msa_idx_lab = np.array([int(np.where(ds.ids == acc)[0][0]) for acc in msa_ids_lab], dtype=int) if len(msa_ids_lab) else np.array([], dtype=int)

            # PAE train/val split
            X_pae = ds.X.iloc[pae_idx_lab].reset_index(drop=True) if len(pae_idx_lab) else ds.X.iloc[[]].reset_index(drop=True)
            y_pae = ds.y_pae[pae_idx_lab] if len(pae_idx_lab) else np.array([], dtype=int)
            ids_pae = ds.ids[pae_idx_lab] if len(pae_idx_lab) else np.array([], dtype=str)

            lv_pae = labeled_train_val_split(ids_pae, seed_string=seed + f"::{policy}::pae::round{r}", train_frac=train_frac, val_frac=val_frac) if len(ids_pae) else None
            X_pae_train = X_pae.iloc[lv_pae.train] if lv_pae and len(lv_pae.train) else X_pae
            y_pae_train = y_pae[lv_pae.train] if lv_pae and len(lv_pae.train) else y_pae
            X_pae_val = X_pae.iloc[lv_pae.val] if lv_pae and len(lv_pae.val) else X_pae
            y_pae_val = y_pae[lv_pae.val] if lv_pae and len(lv_pae.val) else y_pae

            model_pae = train_logreg_safe(
                X=X_pae_train,
                y=y_pae_train,
                standardize=bool(pae_mcfg["standardize"]),
                impute_strategy=str(pae_mcfg["impute_strategy"]),
                params=pae_mcfg["params"],
                min_labeled=int(pae_mcfg["min_labeled_to_train"]),
            )

            s_pae_val = predict_proba_safe(model_pae, X_pae_val, fallback_prob=float(y_pae.mean()) if len(y_pae) else 0.5)
            s_pae_hold = predict_proba_safe(model_pae, X_pae_hold, fallback_prob=float(y_pae.mean()) if len(y_pae) else 0.5)

            ev_pae = evaluate_binary_classifier(y_pae_val, s_pae_val, y_pae_hold, s_pae_hold, fpr_targets=fpr_targets)
            op_pae_primary = next(op for op in ev_pae["operating_points"] if float(op["fpr_target"]) == primary_fpr)
            pae_ok = bool((op_pae_primary["fpr"] <= (primary_fpr + eps_fpr)) and (op_pae_primary["tpr"] > 0.0))

            # MSA classifier train/val split
            X_msa = ds.X.iloc[msa_idx_lab].reset_index(drop=True) if len(msa_idx_lab) else ds.X.iloc[[]].reset_index(drop=True)
            y_msa = ds.y_msa[msa_idx_lab] if len(msa_idx_lab) else np.array([], dtype=int)
            ids_msa = ds.ids[msa_idx_lab] if len(msa_idx_lab) else np.array([], dtype=str)
            c3_msa = ds.c3[msa_idx_lab] if len(msa_idx_lab) else np.array([], dtype=float)

            lv_msa = labeled_train_val_split(ids_msa, seed_string=seed + f"::{policy}::msa::round{r}", train_frac=train_frac, val_frac=val_frac) if len(ids_msa) else None
            X_msa_train = X_msa.iloc[lv_msa.train] if lv_msa and len(lv_msa.train) else X_msa
            y_msa_train = y_msa[lv_msa.train] if lv_msa and len(lv_msa.train) else y_msa
            X_msa_val = X_msa.iloc[lv_msa.val] if lv_msa and len(lv_msa.val) else X_msa
            y_msa_val = y_msa[lv_msa.val] if lv_msa and len(lv_msa.val) else y_msa

            model_msa_cls = train_logreg_safe(
                X=X_msa_train,
                y=y_msa_train,
                standardize=bool(msa_clf_cfg["standardize"]),
                impute_strategy=str(msa_clf_cfg["impute_strategy"]),
                params=msa_clf_cfg["params"],
                min_labeled=int(msa_clf_cfg["min_labeled_to_train"]),
            )

            s_msa_val = predict_proba_safe(model_msa_cls, X_msa_val, fallback_prob=float(y_msa.mean()) if len(y_msa) else 0.5)
            s_msa_hold = predict_proba_safe(model_msa_cls, X_msa_hold, fallback_prob=float(y_msa.mean()) if len(y_msa) else 0.5)

            ev_msa = evaluate_binary_classifier(y_msa_val, s_msa_val, y_msa_hold, s_msa_hold, fpr_targets=fpr_targets)
            op_msa_primary = next(op for op in ev_msa["operating_points"] if float(op["fpr_target"]) == primary_fpr)
            msa_ok = bool((op_msa_primary["fpr"] <= (primary_fpr + eps_fpr)) and (op_msa_primary["tpr"] > 0.0))

            # MSA regressor
            y_c3_train = c3_msa[lv_msa.train] if lv_msa and len(lv_msa.train) else c3_msa
            model_msa_reg = train_ridge_safe(
                X=X_msa_train,
                y=y_c3_train,
                standardize=bool(msa_reg_cfg["standardize"]),
                impute_strategy=str(msa_reg_cfg["impute_strategy"]),
                params=msa_reg_cfg["params"],
                min_labeled=int(msa_reg_cfg["min_labeled_to_train"]),
            )
            pred_c3_hold = predict_reg_safe(model_msa_reg, X_msa_hold, fallback_value=float(np.mean(c3_msa)) if len(c3_msa) else 0.0)
            reg_hold = regression_metrics(c3_hold, pred_c3_hold)

            # record series (round r)
            pae_series["queried_labels"].append(int(pae_used))
            pae_series["tpr_primary"].append(float(op_pae_primary["tpr"]))
            pae_series["fpr_primary"].append(float(op_pae_primary["fpr"]))

            msa_cls_series["queried_labels"].append(int(msa_used))
            msa_cls_series["tpr_primary"].append(float(op_msa_primary["tpr"]))
            msa_cls_series["fpr_primary"].append(float(op_msa_primary["fpr"]))

            msa_reg_series["queried_labels"].append(int(msa_used))
            msa_reg_series["mae_holdout"].append(float(reg_hold["mae"]))
            msa_reg_series["rmse_holdout"].append(float(reg_hold["rmse"]))
            msa_reg_series["spearman_holdout"].append(float(reg_hold["spearman"]))
            msa_reg_series["r2_holdout"].append(float(reg_hold["r2"]))

            if (not joint_achieved) and pae_ok and msa_ok:
                joint["joint_usable_round"] = int(r)
                joint_achieved = True

            # round metrics record
            round_metrics[policy].append({
                "round": int(r),
                "policy": policy,
                "allocation_policy": alloc_policy,
                "ranking_policy": rank_policy,
                "pae": {
                    "queried_labels": int(pae_used),
                    "model_trained": bool(model_pae.trained),
                    "note": model_pae.note,
                    "holdout_n": int(len(y_pae_hold)),
                    "roc_auc": float(ev_pae.get("roc_auc", float("nan"))),
                    "pr_auc": float(ev_pae.get("pr_auc", float("nan"))),
                    "operating_points": ev_pae["operating_points"],
                    "usable_at_primary_cap": bool(pae_ok),
                },
                "msa_cls": {
                    "queried_labels": int(msa_used),
                    "model_trained": bool(model_msa_cls.trained),
                    "note": model_msa_cls.note,
                    "holdout_n": int(len(y_msa_hold)),
                    "roc_auc": float(ev_msa.get("roc_auc", float("nan"))),
                    "pr_auc": float(ev_msa.get("pr_auc", float("nan"))),
                    "operating_points": ev_msa["operating_points"],
                    "usable_at_primary_cap": bool(msa_ok),
                },
                "msa_reg": {
                    "queried_labels": int(msa_used),
                    "model_trained": bool(model_msa_reg.trained),
                    "note": model_msa_reg.note,
                    "holdout_n": int(len(c3_hold)),
                    "metrics_holdout": reg_hold,
                },
                "joint": {
                    "usable_now": bool(pae_ok and msa_ok),
                    "joint_usable_round_so_far": int(joint["joint_usable_round"]),
                }
            })

            # stop if last round
            if r == rounds:
                joblib.dump({"pipeline": model_pae.pipeline, "feature_names": model_pae.feature_names, "trained": model_pae.trained, "note": model_pae.note}, models_dir / f"{policy}_PAE_CLS.joblib")
                joblib.dump({"pipeline": model_msa_cls.pipeline, "feature_names": model_msa_cls.feature_names, "trained": model_msa_cls.trained, "note": model_msa_cls.note}, models_dir / f"{policy}_MSA_CLS.joblib")
                joblib.dump({"pipeline": model_msa_reg.pipeline, "feature_names": model_msa_reg.feature_names, "trained": model_msa_reg.trained, "note": model_msa_reg.note}, models_dir / f"{policy}_MSA_REG.joblib")
                break

            # Determine remaining budgets
            pae_rem = pae_budget_total - pae_used
            msa_rem = msa_budget_total - msa_used
            if pae_rem <= 0 and msa_rem <= 0:
                break

            # total batch size
            if batch_mode == "fixed_split":
                q_round_total = int(q_pae_fixed + q_msa_fixed)
            else:
                q_round_total = int(q_total)
            q_round_total = min(q_round_total, pae_rem + msa_rem, len(unlabeled_pae) + len(unlabeled_msa))
            if q_round_total <= 0:
                break

            # allocation weights
            if alloc_policy == "fixed_split":
                q_pae, q_msa = _allocate_fixed_split(q_round_total, q_pae_fixed, q_msa_fixed)
            elif alloc_policy == "random_hash":
                q_pae = q_round_total // 2
                q_msa = q_round_total - q_pae
            else:
                # compute uncertainty mass on unlabeled for each oracle (cheap proxy)
                unl_pae_list = sorted(list(unlabeled_pae))
                unl_msa_list = sorted(list(unlabeled_msa))

                u_pae = 0.0
                u_msa = 0.0
                if len(unl_pae_list):
                    idx_unl_pae = np.array([int(np.where(ds.ids == acc)[0][0]) for acc in unl_pae_list], dtype=int)
                    X_unl_pae = ds.X.iloc[idx_unl_pae].reset_index(drop=True)
                    p_unl_pae = predict_proba_safe(model_pae, X_unl_pae, fallback_prob=float(y_pae.mean()) if len(y_pae) else 0.5)
                    u_pae = _uncertainty_mass(p_unl_pae)
                if len(unl_msa_list):
                    idx_unl_msa = np.array([int(np.where(ds.ids == acc)[0][0]) for acc in unl_msa_list], dtype=int)
                    X_unl_msa = ds.X.iloc[idx_unl_msa].reset_index(drop=True)
                    p_unl_msa = predict_proba_safe(model_msa_cls, X_unl_msa, fallback_prob=float(y_msa.mean()) if len(y_msa) else 0.5)
                    u_msa = _uncertainty_mass(p_unl_msa)

                if alloc_policy == "adaptive_uncertainty":
                    q_pae, q_msa = _allocate_by_ratio(q_round_total, w_pae=u_pae, w_msa=u_msa)
                elif alloc_policy == "adaptive_joint_minimax":
                    # risk weight: penalize the bottleneck oracle more strongly until joint gate is reached
                    # (protocol-level heuristic; preregistered)
                    tpr_pae = float(op_pae_primary["tpr"])
                    tpr_msa = float(op_msa_primary["tpr"])
                    risk_pae = (1.0 - tpr_pae) + (1.0 if not pae_ok else 0.0)
                    risk_msa = (1.0 - tpr_msa) + (1.0 if not msa_ok else 0.0)
                    q_pae, q_msa = _allocate_by_ratio(q_round_total, w_pae=risk_pae, w_msa=risk_msa)
                else:
                    raise ValueError(f"Unknown allocation policy: {alloc_policy}")

            # enforce budgets/pool sizes
            q_pae = min(q_pae, pae_rem, len(unlabeled_pae))
            q_msa = min(q_msa, msa_rem, len(unlabeled_msa))

            spill = q_round_total - (q_pae + q_msa)
            if spill > 0:
                add_pae = min(spill, pae_rem - q_pae, len(unlabeled_pae) - q_pae)
                q_pae += add_pae
                spill -= add_pae
                add_msa = min(spill, msa_rem - q_msa, len(unlabeled_msa) - q_msa)
                q_msa += add_msa
                spill -= add_msa

            # record allocation fraction for round r+1
            denom = q_pae + q_msa
            frac_pae = (q_pae / denom) if denom > 0 else float("nan")
            alloc_series["round"].append(int(r+1))
            alloc_series["frac_pae"].append(float(frac_pae))

            # selection within each oracle
            def select_for_oracle(oracle: str, unl_set: set[str], q: int, model, y_lab: np.ndarray, labeled_set: set[str]) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
                if q <= 0 or len(unl_set) == 0:
                    return [], {}
                unl_list = sorted(list(unl_set))
                idx_unl = np.array([int(np.where(ds.ids == acc)[0][0]) for acc in unl_list], dtype=int)
                X_unl = ds.X.iloc[idx_unl].reset_index(drop=True)

                probs = predict_proba_safe(model, X_unl, fallback_prob=float(np.mean(y_lab)) if len(y_lab) else 0.5)
                unc = uncertainty_from_probs(probs)
                unc_norm = np.clip(unc / 0.5, 0.0, 1.0)

                # novelty
                idx_lab = np.array([int(np.where(ds.ids == acc)[0][0]) for acc in sorted(list(labeled_set))], dtype=int) if len(labeled_set) else np.array([], dtype=int)
                cand_z = Xz_all[idx_unl, :]
                lab_z = Xz_all[idx_lab, :] if len(idx_lab) else np.zeros((0, cand_z.shape[1]), dtype=float)

                nov = novelty_min_dist(cand_z, lab_z)
                nov_norm = minmax_norm(nov)

                comp = alpha_unc * unc_norm + (1.0 - alpha_unc) * nov_norm

                # determine ranking mode
                if not model.trained:
                    mode = fallback_no_model
                else:
                    mode = rank_policy

                ranked = rank_ids(unl_list, probs=probs, novelty_norm=nov_norm, composite=comp, mode=mode, seed=seed + f"::{policy}::{oracle}::round{r+1}")

                # package per-id components for logging
                comp_map: Dict[str, Dict[str, float]] = {}
                for i, acc in enumerate(unl_list):
                    comp_map[acc] = {
                        "predicted_prob": float(probs[i]),
                        "uncertainty": float(unc[i]),
                        "novelty": float(nov[i]),
                        "novelty_norm": float(nov_norm[i]),
                        "composite_score": float(comp[i]),
                        "rank_mode": mode,
                    }
                return ranked[:q], comp_map

            sel_pae, pae_comp = select_for_oracle("PAE", unlabeled_pae, q_pae, model_pae, y_pae, labeled_pae)
            sel_msa, msa_comp = select_for_oracle("MSA", unlabeled_msa, q_msa, model_msa_cls, y_msa, labeled_msa)

            for acc in sel_pae:
                idx = int(np.where(ds.ids == acc)[0][0])
                c = pae_comp.get(acc, {})
                decision_rows.append({
                    "policy": policy,
                    "allocation_policy": alloc_policy,
                    "ranking_policy": rank_policy,
                    "round": int(r+1),
                    "oracle_type": "PAE",
                    "accession": acc,
                    "selected_by": c.get("rank_mode", fallback_no_model),
                    "predicted_prob": float(c.get("predicted_prob", float("nan"))),
                    "uncertainty": float(c.get("uncertainty", float("nan"))),
                    "novelty": float(c.get("novelty", float("nan"))),
                    "novelty_norm": float(c.get("novelty_norm", float("nan"))),
                    "composite_score": float(c.get("composite_score", float("nan"))),
                    "revealed_value": float(ds.pae_value[idx]),
                    "revealed_label": int(ds.y_pae[idx]),
                })
                labeled_pae.add(acc)
                unlabeled_pae.discard(acc)
                pae_used += 1

            for acc in sel_msa:
                idx = int(np.where(ds.ids == acc)[0][0])
                c = msa_comp.get(acc, {})
                decision_rows.append({
                    "policy": policy,
                    "allocation_policy": alloc_policy,
                    "ranking_policy": rank_policy,
                    "round": int(r+1),
                    "oracle_type": "MSA",
                    "accession": acc,
                    "selected_by": c.get("rank_mode", fallback_no_model),
                    "predicted_prob": float(c.get("predicted_prob", float("nan"))),
                    "uncertainty": float(c.get("uncertainty", float("nan"))),
                    "novelty": float(c.get("novelty", float("nan"))),
                    "novelty_norm": float(c.get("novelty_norm", float("nan"))),
                    "composite_score": float(c.get("composite_score", float("nan"))),
                    "revealed_value": float(ds.msa_depth[idx]),
                    "revealed_label": int(ds.y_msa[idx]),
                })
                labeled_msa.add(acc)
                unlabeled_msa.discard(acc)
                msa_used += 1

        # events
        ev_pae_jump = detect_covjump(pae_series["tpr_primary"], W_jump=W_jump, delta_tpr=delta_tpr)
        ev_msa_jump = detect_covjump(msa_cls_series["tpr_primary"], W_jump=W_jump, delta_tpr=delta_tpr)
        pae_series["event"] = ev_pae_jump.__dict__
        msa_cls_series["event"] = ev_msa_jump.__dict__

        series_by_policy[policy] = {
            "pae": pae_series,
            "msa_cls": msa_cls_series,
            "msa_reg": msa_reg_series,
            "alloc": alloc_series,
            "joint": joint,
            "policy_parts": {"allocation": alloc_policy, "ranking": rank_policy},
        }

    # Save artifacts
    pd.DataFrame(decision_rows).to_csv(run_dir / "decision_trace.csv", index=False)
    _write_json(run_dir / "round_metrics.json", {
        "subcase_id": cfg["preregistration"]["case_id"],
        "run_id": run_id,
        "primary_fpr_target": primary_fpr,
        "series_by_policy": series_by_policy,
        "metrics_by_policy": round_metrics,
    })

    # Eval report summary
    lines = []
    lines.append("# Eval report — Dual‑Oracle Active Acquisition (v0.5)\n\n")
    lines.append(f"- run_id: `{run_id}`\n")
    lines.append(f"- parent_case_id: `{cfg['preregistration']['parent_case_id']}`\n")
    lines.append(f"- tau_pae: `{float(cfg['boundary']['thresholds']['tau_pae'])}`\n")
    lines.append(f"- tau_msa_depth: `{float(cfg['boundary']['thresholds']['tau_msa_depth'])}`\n")
    lines.append(f"- primary FPR cap: `{primary_fpr}`\n")
    lines.append(f"- alpha_uncertainty (composite): `{alpha_unc}`\n")
    lines.append(f"- prereg_sha256: `{prereg_sha}`\n")
    lines.append(f"- input_metrics_sha256: `{input_hash}`\n\n")

    lines.append("## Policy summary (final)\n\n")
    lines.append("| policy | alloc | rank | joint_usable_round | PAE queried | PAE TPR@cap | PAE achieved FPR | PAE covjump? | MSA queried | MSA TPR@cap | MSA achieved FPR | MSA covjump? | final MAE(C3_hat) |\n")
    lines.append("|---|---|---|---:|---:|---:|---:|:---:|---:|---:|---:|:---:|---:|\n")
    for policy, ser in series_by_policy.items():
        pae_q = ser["pae"]["queried_labels"][-1] if ser["pae"]["queried_labels"] else 0
        msa_q = ser["msa_cls"]["queried_labels"][-1] if ser["msa_cls"]["queried_labels"] else 0
        pae_tpr = ser["pae"]["tpr_primary"][-1] if ser["pae"]["tpr_primary"] else float("nan")
        msa_tpr = ser["msa_cls"]["tpr_primary"][-1] if ser["msa_cls"]["tpr_primary"] else float("nan")
        pae_fpr = ser["pae"]["fpr_primary"][-1] if ser["pae"]["fpr_primary"] else float("nan")
        msa_fpr = ser["msa_cls"]["fpr_primary"][-1] if ser["msa_cls"]["fpr_primary"] else float("nan")
        evp = ser["pae"]["event"]
        evm = ser["msa_cls"]["event"]
        mae_final = ser["msa_reg"]["mae_holdout"][-1] if ser["msa_reg"]["mae_holdout"] else float("nan")
        jr = int(ser["joint"]["joint_usable_round"])
        parts = ser["policy_parts"]
        lines.append(
            f"| {policy} | {parts['allocation']} | {parts['ranking']} | {jr} | {pae_q} | {pae_tpr:.6f} | {pae_fpr:.6f} | {'yes' if evp['found'] else 'no'} | "
            f"{msa_q} | {msa_tpr:.6f} | {msa_fpr:.6f} | {'yes' if evm['found'] else 'no'} | {mae_final:.6f} |\n"
        )
    lines.append("\n")

    lines.append("## Interpretation rule\n\n")
    lines.append("- Allowed claims are budgeted learning curves, the joint gate outcome, and MSA proxy regression quality under the locked boundary.\n")
    lines.append("- Policy differences are protocol comparisons; do not interpret them as mechanistic causes.\n\n")
    _write_text(run_dir / "eval_report.md", "".join(lines))

    # Plot onepager
    footer = (
        f"subcase=dual_oracle_active_acquisition_v0_5 | parent=afdb_swissprot_tier2p11_confidence_regimes | "
        f"run={run_id} | tau_pae={float(cfg['boundary']['thresholds']['tau_pae'])} | tau_msa={float(cfg['boundary']['thresholds']['tau_msa_depth'])} | "
        f"cap={primary_fpr} | seed={seed} | feat_sha={feature_hash[:10]} | alpha_unc={alpha_unc}"
    )
    plot_onepage_v0_5(out_pdf=run_dir / "tradeoff_onepage.pdf", series_by_policy=series_by_policy, rounds=rounds, meta_footer=footer)

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
            "models_dir": str(models_dir.resolve()),
        },
    }
    _write_json(run_dir / "run_manifest.json", manifest)

    print(f"Run complete. Outputs in: {run_dir}")

if __name__ == "__main__":
    main()
