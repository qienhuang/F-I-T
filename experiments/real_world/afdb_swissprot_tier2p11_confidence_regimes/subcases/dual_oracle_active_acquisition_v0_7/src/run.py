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
    uncertainty_from_prob,
    rank_by_uncertainty, rank_by_random_hash,
    allocate_fixed_split, allocate_by_uncertainty_mass, allocate_by_gap,
    select_batch_composite_ff,
)
from .event import detect_covjump
from .plot_onepager import plot_onepage_v0_7

def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")

def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def _uncertainty_mass(probs: np.ndarray) -> float:
    u = uncertainty_from_prob(probs)
    return float(np.mean(u)) if len(u) else 0.0

def parse_policy_spec(spec: str) -> Tuple[str, str]:
    if "__" not in spec:
        raise ValueError(f"policy spec must be '<allocation>__<ranking>': {spec}")
    a, r = spec.split("__", 1)
    return a, r

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

    locked = run_dir / "PREREG.locked.yaml"
    _write_text(locked, Path(args.prereg).read_text(encoding="utf-8"))
    prereg_sha = sha256_hex(locked.read_text(encoding="utf-8"))

    # Load input
    in_path_cfg = cfg["data"]["input_metrics_path"]
    in_path = (case_dir / in_path_cfg).resolve() if not str(in_path_cfg).startswith("/") else Path(in_path_cfg)
    df = load_metrics(in_path, fallback=cfg["data"].get("input_format_fallback", "csv"))
    id_field = cfg["data"]["id_field"]

    fmin = int(cfg["boundary"]["data_filters"]["min_length"])
    fmax = int(cfg["boundary"]["data_filters"]["max_length"])
    df = apply_basic_filters(df, min_len=fmin, max_len=fmax, id_field=id_field)

    feat = list(cfg["boundary"]["feature_whitelist"])
    pae_field = cfg["boundary"]["oracle_fields"]["pae_value"]
    msa_field = cfg["boundary"]["oracle_fields"]["msa_depth"]
    require_columns(df, [id_field] + feat + [pae_field, msa_field])

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
        "pae_available_rate": float(np.mean(ds.pae_available)) if len(ds.ids) else float("nan"),
        "msa_available_rate": float(np.mean(ds.msa_available)) if len(ds.ids) else float("nan"),
        "universe_mode": cfg["boundary"].get("universe_mode", "union"),
        "policy_diag_split": cfg.get("policy_diagnostics", {}).get("use_split", "labeled_val"),
    })

    _write_json(run_dir / "boundary_snapshot.json", {
        "train_boundary": cfg["boundary"]["train_boundary"],
        "deploy_boundary": cfg["boundary"]["deploy_boundary"],
        "feature_whitelist": feat,
        "oracle_fields": {"pae_value": pae_field, "msa_depth": msa_field},
        "thresholds": cfg["boundary"]["thresholds"],
        "holdout_role": cfg["evaluation"]["holdout_role"],
        "universe_mode": cfg["boundary"].get("universe_mode", "union"),
        "policy_diagnostics": cfg.get("policy_diagnostics", {}),
    })

    seed = cfg["data"]["seed_string"]
    holdout_frac = float(cfg["evaluation"]["holdout_frac"])

    # oracle-specific holdout/pool
    sp_pae = holdout_split(ds.ids, seed_string=seed + "::pae", holdout_frac=holdout_frac, mask=ds.pae_available)
    sp_msa = holdout_split(ds.ids, seed_string=seed + "::msa", holdout_frac=holdout_frac, mask=ds.msa_available)
    hold_pae, pool_pae = sp_pae.holdout, sp_pae.pool
    hold_msa, pool_msa = sp_msa.holdout, sp_msa.pool

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

    policy_specs = list(cfg["acquisition"]["policy_specs"])
    rank_cfg = cfg["acquisition"]["ranking"]
    K_caps = rank_cfg["candidate_pool_cap"]
    K_pae = int(K_caps.get("PAE", 0))
    K_msa = int(K_caps.get("MSA", 0))
    basis = str(rank_cfg.get("candidate_pool_basis", "uncertainty"))
    alpha = float(rank_cfg.get("composite_alpha", 0.7))
    fallback_no_model = str(rank_cfg.get("fallback_if_no_model", "random_hash"))

    train_frac = float(cfg["split_labeled"]["train_frac"])
    val_frac = float(cfg["split_labeled"]["val_frac"])

    fpr_targets = [float(x) for x in cfg["monitorability"]["fpr_targets"]]
    primary_fpr = float(cfg["monitorability"]["primary_fpr_target"])
    eps_fpr = float(cfg["monitorability"].get("usable_epsilon_fpr", 0.0))
    tpr_min = float(cfg["monitorability"].get("tpr_min_for_usable", 0.01))

    # gap weights
    gap_cfg = cfg.get("policy_diagnostics", {}).get("gap_definition", {})
    w_tpr = float(gap_cfg.get("w_tpr", 1.0))
    w_fpr = float(gap_cfg.get("w_fpr", 5.0))

    pae_mcfg = cfg["model"]["pae_classifier"]
    msa_clf_cfg = cfg["model"]["msa_classifier"]
    msa_reg_cfg = cfg["model"]["msa_regressor"]

    W_jump = int(cfg["event"]["W_jump_rounds"])
    delta_tpr = float(cfg["event"]["delta_tpr"])

    decision_rows = []
    alloc_rows = []
    round_metrics: Dict[str, List[Dict[str, Any]]] = {spec: [] for spec in policy_specs}
    series_by_policy: Dict[str, Dict[str, Any]] = {}

    models_dir = run_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    pool_pae_ids = ds.ids[pool_pae].tolist()
    pool_msa_ids = ds.ids[pool_msa].tolist()
    init_order_pae = stable_hash_order(pool_pae_ids, seed_string=seed + "::init_pae")
    init_order_msa = stable_hash_order(pool_msa_ids, seed_string=seed + "::init_msa")

    id_to_idx = {str(a): i for i, a in enumerate(ds.ids.tolist())}

    def gap_score(tpr_val: float, fpr_val: float, cap: float) -> float:
        return float(w_tpr * max(0.0, tpr_min - tpr_val) + w_fpr * max(0.0, fpr_val - cap))

    for spec in policy_specs:
        alloc_policy, rank_policy = parse_policy_spec(spec)

        labeled_pae = set(init_order_pae[:min(init_pae_n, len(init_order_pae), pae_budget_total)])
        labeled_msa = set(init_order_msa[:min(init_msa_n, len(init_order_msa), msa_budget_total)])

        pae_used = len(labeled_pae)
        msa_used = len(labeled_msa)

        unlabeled_pae = set(pool_pae_ids) - labeled_pae
        unlabeled_msa = set(pool_msa_ids) - labeled_msa

        # init log
        for acc in sorted(list(labeled_pae)):
            idx = id_to_idx[acc]
            decision_rows.append({
                "policy": spec, "round": 0, "oracle_type": "PAE", "accession": acc,
                "selected_by": "init_seed",
                "predicted_prob": float("nan"),
                "uncertainty_norm": float("nan"),
                "novelty": float("nan"),
                "novelty_norm": float("nan"),
                "composite_score": float("nan"),
                "revealed_value": float(ds.pae_value[idx]),
                "revealed_label": int(ds.y_pae[idx]),
            })
        for acc in sorted(list(labeled_msa)):
            idx = id_to_idx[acc]
            decision_rows.append({
                "policy": spec, "round": 0, "oracle_type": "MSA", "accession": acc,
                "selected_by": "init_seed",
                "predicted_prob": float("nan"),
                "uncertainty_norm": float("nan"),
                "novelty": float("nan"),
                "novelty_norm": float("nan"),
                "composite_score": float("nan"),
                "revealed_value": float(ds.msa_depth[idx]),
                "revealed_label": int(ds.y_msa[idx]),
            })

        pae_series = {"queried_labels": [], "tpr_primary": [], "fpr_primary": [], "event": None}
        msa_cls_series = {"queried_labels": [], "tpr_primary": [], "fpr_primary": [], "event": None}
        msa_reg_series = {"queried_labels": [], "mae_holdout": []}
        alloc_series = {"pae_fraction": []}
        joint = {"joint_usable_round": rounds + 1}
        joint_achieved = False

        for r in range(0, rounds + 1):
            pae_ids_lab = sorted(list(labeled_pae))
            msa_ids_lab = sorted(list(labeled_msa))
            pae_idx_lab = np.array([id_to_idx[acc] for acc in pae_ids_lab], dtype=int) if len(pae_ids_lab) else np.array([], dtype=int)
            msa_idx_lab = np.array([id_to_idx[acc] for acc in msa_ids_lab], dtype=int) if len(msa_ids_lab) else np.array([], dtype=int)

            # prepare labeled sets
            X_pae = ds.X.iloc[pae_idx_lab].reset_index(drop=True) if len(pae_idx_lab) else ds.X.iloc[[]].reset_index(drop=True)
            y_pae = ds.y_pae[pae_idx_lab] if len(pae_idx_lab) else np.array([], dtype=int)
            ids_pae = ds.ids[pae_idx_lab] if len(pae_idx_lab) else np.array([], dtype=str)

            lv_pae = labeled_train_val_split(ids_pae, seed_string=seed + f"::{spec}::pae::round{r}", train_frac=train_frac, val_frac=val_frac) if len(ids_pae) else None
            X_pae_train = X_pae.iloc[lv_pae.train] if lv_pae and len(lv_pae.train) else X_pae
            y_pae_train = y_pae[lv_pae.train] if lv_pae and len(lv_pae.train) else y_pae
            X_pae_val = X_pae.iloc[lv_pae.val] if lv_pae and len(lv_pae.val) else X_pae
            y_pae_val = y_pae[lv_pae.val] if lv_pae and len(lv_pae.val) else y_pae

            model_pae = train_logreg_safe(
                X=X_pae_train, y=y_pae_train,
                standardize=bool(pae_mcfg["standardize"]),
                impute_strategy=str(pae_mcfg["impute_strategy"]),
                params=pae_mcfg["params"],
                min_labeled=int(pae_mcfg["min_labeled_to_train"]),
            )

            s_pae_val = predict_proba_safe(model_pae, X_pae_val, fallback_prob=float(y_pae.mean()) if len(y_pae) else 0.5)
            X_pae_hold = ds.X.iloc[hold_pae].reset_index(drop=True)
            y_pae_hold = ds.y_pae[hold_pae]
            s_pae_hold = predict_proba_safe(model_pae, X_pae_hold, fallback_prob=float(y_pae.mean()) if len(y_pae) else 0.5)

            ev_pae = evaluate_binary_classifier(y_test=y_pae_hold, s_test=s_pae_hold, y_val=y_pae_val, s_val=s_pae_val, fpr_targets=fpr_targets)
            op_pae_primary = next(op for op in ev_pae["operating_points"] if float(op["fpr_target"]) == primary_fpr)
            pae_val = op_pae_primary["val"]
            pae_test = op_pae_primary["test"]
            pae_ok_val = bool((pae_val["fpr"] <= (primary_fpr + eps_fpr)) and (pae_val["tpr"] >= tpr_min))
            pae_ok_test = bool((pae_test["fpr"] <= (primary_fpr + eps_fpr)) and (pae_test["tpr"] >= tpr_min))

            # MSA
            X_msa = ds.X.iloc[msa_idx_lab].reset_index(drop=True) if len(msa_idx_lab) else ds.X.iloc[[]].reset_index(drop=True)
            y_msa = ds.y_msa[msa_idx_lab] if len(msa_idx_lab) else np.array([], dtype=int)
            ids_msa = ds.ids[msa_idx_lab] if len(msa_idx_lab) else np.array([], dtype=str)
            c3_msa = ds.c3[msa_idx_lab] if len(msa_idx_lab) else np.array([], dtype=float)

            lv_msa = labeled_train_val_split(ids_msa, seed_string=seed + f"::{spec}::msa::round{r}", train_frac=train_frac, val_frac=val_frac) if len(ids_msa) else None
            X_msa_train = X_msa.iloc[lv_msa.train] if lv_msa and len(lv_msa.train) else X_msa
            y_msa_train = y_msa[lv_msa.train] if lv_msa and len(lv_msa.train) else y_msa
            X_msa_val = X_msa.iloc[lv_msa.val] if lv_msa and len(lv_msa.val) else X_msa
            y_msa_val = y_msa[lv_msa.val] if lv_msa and len(lv_msa.val) else y_msa
            c3_train = c3_msa[lv_msa.train] if lv_msa and len(lv_msa.train) else c3_msa

            model_msa_cls = train_logreg_safe(
                X=X_msa_train, y=y_msa_train,
                standardize=bool(msa_clf_cfg["standardize"]),
                impute_strategy=str(msa_clf_cfg["impute_strategy"]),
                params=msa_clf_cfg["params"],
                min_labeled=int(msa_clf_cfg["min_labeled_to_train"]),
            )
            s_msa_val = predict_proba_safe(model_msa_cls, X_msa_val, fallback_prob=float(y_msa.mean()) if len(y_msa) else 0.5)

            X_msa_hold = ds.X.iloc[hold_msa].reset_index(drop=True)
            y_msa_hold = ds.y_msa[hold_msa]
            s_msa_hold = predict_proba_safe(model_msa_cls, X_msa_hold, fallback_prob=float(y_msa.mean()) if len(y_msa) else 0.5)

            ev_msa = evaluate_binary_classifier(y_test=y_msa_hold, s_test=s_msa_hold, y_val=y_msa_val, s_val=s_msa_val, fpr_targets=fpr_targets)
            op_msa_primary = next(op for op in ev_msa["operating_points"] if float(op["fpr_target"]) == primary_fpr)
            msa_val = op_msa_primary["val"]
            msa_test = op_msa_primary["test"]
            msa_ok_val = bool((msa_val["fpr"] <= (primary_fpr + eps_fpr)) and (msa_val["tpr"] >= tpr_min))
            msa_ok_test = bool((msa_test["fpr"] <= (primary_fpr + eps_fpr)) and (msa_test["tpr"] >= tpr_min))

            # MSA regressor (proxy channel)
            model_msa_reg = train_ridge_safe(
                X=X_msa_train,
                y=c3_train[np.isfinite(c3_train)],
                standardize=bool(msa_reg_cfg["standardize"]),
                impute_strategy=str(msa_reg_cfg["impute_strategy"]),
                params=msa_reg_cfg["params"],
                min_labeled=int(msa_reg_cfg["min_labeled_to_train"]),
            )
            c3_hold = ds.c3[hold_msa]
            pred_c3_hold = predict_reg_safe(model_msa_reg, X_msa_hold, fallback_value=float(np.nanmean(c3_msa)) if len(c3_msa) else 0.0)
            reg_hold = regression_metrics(c3_hold[np.isfinite(c3_hold)], pred_c3_hold[np.isfinite(c3_hold)])

            # series (holdout reporting)
            pae_series["queried_labels"].append(int(pae_used))
            pae_series["tpr_primary"].append(float(pae_test["tpr"]))
            pae_series["fpr_primary"].append(float(pae_test["fpr"]))

            msa_cls_series["queried_labels"].append(int(msa_used))
            msa_cls_series["tpr_primary"].append(float(msa_test["tpr"]))
            msa_cls_series["fpr_primary"].append(float(msa_test["fpr"]))

            msa_reg_series["queried_labels"].append(int(msa_used))
            msa_reg_series["mae_holdout"].append(float(reg_hold["mae"]) if reg_hold else float("nan"))

            # joint gate (holdout)
            if (not joint_achieved) and pae_ok_test and msa_ok_test:
                joint["joint_usable_round"] = int(r)
                joint_achieved = True

            # round_metrics (store both val and holdout for transparency)
            round_metrics[spec].append({
                "round": int(r),
                "pae": {
                    "queried": int(pae_used),
                    "val_tpr_primary": float(pae_val["tpr"]), "val_fpr_primary": float(pae_val["fpr"]), "val_usable": bool(pae_ok_val),
                    "holdout_tpr_primary": float(pae_test["tpr"]), "holdout_fpr_primary": float(pae_test["fpr"]), "holdout_usable": bool(pae_ok_test),
                },
                "msa_cls": {
                    "queried": int(msa_used),
                    "val_tpr_primary": float(msa_val["tpr"]), "val_fpr_primary": float(msa_val["fpr"]), "val_usable": bool(msa_ok_val),
                    "holdout_tpr_primary": float(msa_test["tpr"]), "holdout_fpr_primary": float(msa_test["fpr"]), "holdout_usable": bool(msa_ok_test),
                },
                "msa_reg": {"queried": int(msa_used), "mae_holdout": float(reg_hold["mae"]) if reg_hold else float("nan")},
                "joint": {"joint_usable_round_so_far": int(joint["joint_usable_round"])},
            })

            if r == rounds:
                joblib.dump({"pipeline": model_pae.pipeline, "feature_names": model_pae.feature_names, "trained": model_pae.trained}, models_dir / f"{spec}_PAE_CLS.joblib")
                joblib.dump({"pipeline": model_msa_cls.pipeline, "feature_names": model_msa_cls.feature_names, "trained": model_msa_cls.trained}, models_dir / f"{spec}_MSA_CLS.joblib")
                joblib.dump({"pipeline": model_msa_reg.pipeline, "feature_names": model_msa_reg.feature_names, "trained": model_msa_reg.trained}, models_dir / f"{spec}_MSA_REG.joblib")
                break

            pae_rem = pae_budget_total - pae_used
            msa_rem = msa_budget_total - msa_used
            if pae_rem <= 0 and msa_rem <= 0:
                break

            if batch_mode == "fixed_split":
                q_round_total = int(q_pae_fixed + q_msa_fixed)
            else:
                q_round_total = int(q_total)
            q_round_total = min(q_round_total, pae_rem + msa_rem, len(unlabeled_pae) + len(unlabeled_msa))
            if q_round_total <= 0:
                break

            # compute uncertainty masses on unlabeled pools (for certain policies and fallbacks)
            unl_pae_list = sorted(list(unlabeled_pae))
            unl_msa_list = sorted(list(unlabeled_msa))
            if len(unl_pae_list):
                idx_unl_pae = np.array([id_to_idx[a] for a in unl_pae_list], dtype=int)
                X_unl_pae = ds.X.iloc[idx_unl_pae].reset_index(drop=True)
                p_unl_pae = predict_proba_safe(model_pae, X_unl_pae, fallback_prob=float(y_pae.mean()) if len(y_pae) else 0.5)
                u_pae = _uncertainty_mass(p_unl_pae)
            else:
                u_pae = 0.0
            if len(unl_msa_list):
                idx_unl_msa = np.array([id_to_idx[a] for a in unl_msa_list], dtype=int)
                X_unl_msa = ds.X.iloc[idx_unl_msa].reset_index(drop=True)
                p_unl_msa = predict_proba_safe(model_msa_cls, X_unl_msa, fallback_prob=float(y_msa.mean()) if len(y_msa) else 0.5)
                u_msa = _uncertainty_mass(p_unl_msa)
            else:
                u_msa = 0.0

            # compute gaps on labeled VAL (policy diagnostics)
            g_pae = gap_score(float(pae_val["tpr"]), float(pae_val["fpr"]), cap=primary_fpr)
            g_msa = gap_score(float(msa_val["tpr"]), float(msa_val["fpr"]), cap=primary_fpr)

            # allocation
            if alloc_policy == "fixed_split":
                q_pae, q_msa = allocate_fixed_split(q_round_total, q_pae_fixed, q_msa_fixed)
            elif alloc_policy == "random_hash":
                q_pae = q_round_total // 2
                q_msa = q_round_total - q_pae
            elif alloc_policy == "adaptive_uncertainty":
                q_pae, q_msa = allocate_by_uncertainty_mass(q_round_total, u_pae=u_pae, u_msa=u_msa)
            elif alloc_policy == "adaptive_joint_minimax":
                if pae_ok_val and (not msa_ok_val):
                    q_pae, q_msa = 0, q_round_total
                elif msa_ok_val and (not pae_ok_val):
                    q_pae, q_msa = q_round_total, 0
                else:
                    q_pae, q_msa = allocate_by_uncertainty_mass(q_round_total, u_pae=u_pae, u_msa=u_msa)
            elif alloc_policy == "adaptive_joint_gap":
                if (g_pae + g_msa) > 0:
                    q_pae, q_msa = allocate_by_gap(q_round_total, g_pae=g_pae, g_msa=g_msa)
                else:
                    q_pae, q_msa = allocate_by_uncertainty_mass(q_round_total, u_pae=u_pae, u_msa=u_msa)
            else:
                raise ValueError(f"Unknown allocation policy: {alloc_policy}")

            # enforce budgets/pools
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

            alloc_series["pae_fraction"].append(float(q_pae / max(1, (q_pae + q_msa))))

            alloc_rows.append({
                "policy": spec,
                "round": int(r+1),
                "allocation_policy": alloc_policy,
                "ranking_policy": rank_policy,
                "q_total": int(q_round_total),
                "q_pae": int(q_pae),
                "q_msa": int(q_msa),
                "gap_pae": float(g_pae),
                "gap_msa": float(g_msa),
                "tpr_val_pae": float(pae_val["tpr"]),
                "fpr_val_pae": float(pae_val["fpr"]),
                "tpr_val_msa": float(msa_val["tpr"]),
                "fpr_val_msa": float(msa_val["fpr"]),
                "u_mass_pae": float(u_pae),
                "u_mass_msa": float(u_msa),
            })

            # selection per oracle
            def select_for_oracle(oracle: str, q: int, unl_set: set[str], model, y_lab: np.ndarray, K: int) -> Tuple[List[str], List[Dict[str, float]]]:
                if q <= 0 or len(unl_set) == 0:
                    return [], []
                unl_list = sorted(list(unl_set))
                idx_unl = np.array([id_to_idx[a] for a in unl_list], dtype=int)
                X_unl = ds.X.iloc[idx_unl].reset_index(drop=True)
                probs = predict_proba_safe(model, X_unl, fallback_prob=float(np.mean(y_lab)) if len(y_lab) else 0.5)

                if (not model.trained) and fallback_no_model == "random_hash":
                    order = rank_by_random_hash(unl_list, seed=seed + f"::{spec}::{oracle}::r{r+1}")
                    pick_idx = order[:q]
                    per = [{"predicted_prob": float(probs[i]), "uncertainty_norm": float("nan"), "novelty": float("nan"), "novelty_norm": float("nan"), "composite_score": float("nan")} for i in pick_idx]
                    return [unl_list[i] for i in pick_idx], per

                if rank_policy == "uncertainty":
                    order = rank_by_uncertainty(unl_list, probs, seed=seed + f"::{spec}::{oracle}::r{r+1}")
                    pick_idx = order[:q]
                    u = uncertainty_from_prob(probs)
                    per = [{
                        "predicted_prob": float(probs[i]),
                        "uncertainty_norm": float(u[i]),
                        "novelty": float("nan"),
                        "novelty_norm": float("nan"),
                        "composite_score": float("nan"),
                    } for i in pick_idx]
                    return [unl_list[i] for i in pick_idx], per

                if rank_policy == "random_hash":
                    order = rank_by_random_hash(unl_list, seed=seed + f"::{spec}::{oracle}::r{r+1}")
                    pick_idx = order[:q]
                    per = [{"predicted_prob": float(probs[i]), "uncertainty_norm": float("nan"), "novelty": float("nan"), "novelty_norm": float("nan"), "composite_score": float("nan")} for i in pick_idx]
                    return [unl_list[i] for i in pick_idx], per

                if rank_policy == "composite_batch_ff":
                    if oracle == "PAE":
                        ref_ids = sorted(list(labeled_pae))
                    else:
                        ref_ids = sorted(list(labeled_msa))
                    ref_idx = np.array([id_to_idx[a] for a in ref_ids], dtype=int) if len(ref_ids) else np.array([], dtype=int)
                    ref_z = ds.X_z[ref_idx] if len(ref_idx) else np.zeros((0, ds.X_z.shape[1]), dtype=float)

                    res = select_batch_composite_ff(
                        ids=unl_list,
                        probs=probs,
                        Xz=ds.X_z[idx_unl],
                        ref_z=ref_z,
                        q=q,
                        K=K,
                        basis=basis,
                        alpha=alpha,
                        seed=seed + f"::{spec}::{oracle}::r{r+1}",
                    )
                    picked = [unl_list[i] for i in res.selected_indices]
                    return picked, res.per_item

                raise ValueError(f"Unknown ranking policy: {rank_policy}")

            sel_pae, per_pae = select_for_oracle("PAE", q_pae, unlabeled_pae, model_pae, y_pae, K=K_pae)
            sel_msa, per_msa = select_for_oracle("MSA", q_msa, unlabeled_msa, model_msa_cls, y_msa, K=K_msa)

            for acc, meta in zip(sel_pae, per_pae):
                idx = id_to_idx[acc]
                decision_rows.append({
                    "policy": spec, "round": int(r+1), "oracle_type": "PAE", "accession": acc,
                    "selected_by": rank_policy if model_pae.trained else fallback_no_model,
                    "predicted_prob": float(meta.get("predicted_prob", float("nan"))),
                    "uncertainty_norm": float(meta.get("uncertainty_norm", float("nan"))),
                    "novelty": float(meta.get("novelty", float("nan"))),
                    "novelty_norm": float(meta.get("novelty_norm", float("nan"))),
                    "composite_score": float(meta.get("composite_score", float("nan"))),
                    "revealed_value": float(ds.pae_value[idx]),
                    "revealed_label": int(ds.y_pae[idx]),
                })
                labeled_pae.add(acc)
                unlabeled_pae.discard(acc)
                pae_used += 1

            for acc, meta in zip(sel_msa, per_msa):
                idx = id_to_idx[acc]
                decision_rows.append({
                    "policy": spec, "round": int(r+1), "oracle_type": "MSA", "accession": acc,
                    "selected_by": rank_policy if model_msa_cls.trained else fallback_no_model,
                    "predicted_prob": float(meta.get("predicted_prob", float("nan"))),
                    "uncertainty_norm": float(meta.get("uncertainty_norm", float("nan"))),
                    "novelty": float(meta.get("novelty", float("nan"))),
                    "novelty_norm": float(meta.get("novelty_norm", float("nan"))),
                    "composite_score": float(meta.get("composite_score", float("nan"))),
                    "revealed_value": float(ds.msa_depth[idx]),
                    "revealed_label": int(ds.y_msa[idx]),
                })
                labeled_msa.add(acc)
                unlabeled_msa.discard(acc)
                msa_used += 1

        ev_pae_jump = detect_covjump(pae_series["tpr_primary"], W_jump=W_jump, delta_tpr=delta_tpr)
        ev_msa_jump = detect_covjump(msa_cls_series["tpr_primary"], W_jump=W_jump, delta_tpr=delta_tpr)
        pae_series["event"] = ev_pae_jump.__dict__
        msa_cls_series["event"] = ev_msa_jump.__dict__

        series_by_policy[spec] = {
            "policy_spec": spec,
            "allocation_policy": alloc_policy,
            "ranking_policy": rank_policy,
            "pae": pae_series,
            "msa_cls": msa_cls_series,
            "msa_reg": msa_reg_series,
            "alloc": alloc_series,
            "joint": joint,
        }

    # save artifacts
    pd.DataFrame(decision_rows).to_csv(run_dir / "decision_trace.csv", index=False)
    pd.DataFrame(alloc_rows).to_csv(run_dir / "allocation_trace.csv", index=False)

    _write_json(run_dir / "round_metrics.json", {
        "subcase_id": cfg["preregistration"]["case_id"],
        "run_id": run_id,
        "primary_fpr_target": primary_fpr,
        "tpr_min_for_usable": tpr_min,
        "policy_diag_split": cfg.get("policy_diagnostics", {}).get("use_split", "labeled_val"),
        "series_by_policy": series_by_policy,
        "metrics_by_policy": round_metrics,
    })

    # Eval report summary
    lines = []
    lines.append("# Eval report — Dual‑Oracle + Joint‑Gap Allocation (v0.7)\n\n")
    lines.append(f"- run_id: `{run_id}`\n")
    lines.append(f"- parent_case_id: `{cfg['preregistration']['parent_case_id']}`\n")
    lines.append(f"- tau_pae: `{float(cfg['boundary']['thresholds']['tau_pae'])}`\n")
    lines.append(f"- tau_msa_depth: `{float(cfg['boundary']['thresholds']['tau_msa_depth'])}`\n")
    lines.append(f"- primary FPR cap: `{primary_fpr}`\n")
    lines.append(f"- tpr_min_for_usable: `{tpr_min}`\n")
    lines.append(f"- policy_diag_split: `{cfg.get('policy_diagnostics', {}).get('use_split', 'labeled_val')}`\n")
    lines.append(f"- prereg_sha256: `{prereg_sha}`\n")
    lines.append(f"- input_metrics_sha256: `{input_hash}`\n\n")

    lines.append("## Policy summary (final)\n\n")
    lines.append("| policy | alloc | rank | joint_usable_round | PAE queried | PAE TPR@cap | PAE FPR | MSA queried | MSA TPR@cap | MSA FPR | final MAE(C3_hat) |\n")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    for spec, ser in series_by_policy.items():
        pae_q = ser["pae"]["queried_labels"][-1] if ser["pae"]["queried_labels"] else 0
        msa_q = ser["msa_cls"]["queried_labels"][-1] if ser["msa_cls"]["queried_labels"] else 0
        pae_tpr = ser["pae"]["tpr_primary"][-1] if ser["pae"]["tpr_primary"] else float("nan")
        msa_tpr = ser["msa_cls"]["tpr_primary"][-1] if ser["msa_cls"]["tpr_primary"] else float("nan")
        pae_fpr = ser["pae"]["fpr_primary"][-1] if ser["pae"]["fpr_primary"] else float("nan")
        msa_fpr = ser["msa_cls"]["fpr_primary"][-1] if ser["msa_cls"]["fpr_primary"] else float("nan")
        mae_final = ser["msa_reg"]["mae_holdout"][-1] if ser["msa_reg"]["mae_holdout"] else float("nan")
        jr = int(ser["joint"]["joint_usable_round"])
        lines.append(
            f"| {spec} | {ser['allocation_policy']} | {ser['ranking_policy']} | {jr} | {pae_q} | {pae_tpr:.6f} | {pae_fpr:.6f} | "
            f"{msa_q} | {msa_tpr:.6f} | {msa_fpr:.6f} | {mae_final:.6f} |\n"
        )
    lines.append("\n")

    lines.append("## Interpretation rule\n\n")
    lines.append("- Policy decisions were driven by labeled validation diagnostics only (no holdout leakage).\n")
    lines.append("- Report claims in terms of budgeted learning curves and joint gate outcomes.\n\n")
    _write_text(run_dir / "eval_report.md", "".join(lines))

    footer = (
        f"subcase=dual_oracle_active_acquisition_v0_7 | parent=afdb_swissprot_tier2p11_confidence_regimes | "
        f"run={run_id} | tau_pae={float(cfg['boundary']['thresholds']['tau_pae'])} | tau_msa={float(cfg['boundary']['thresholds']['tau_msa_depth'])} | "
        f"cap={primary_fpr} | seed={seed} | feat_sha={feature_hash[:10]}"
    )
    plot_onepage_v0_7(out_pdf=run_dir / "tradeoff_onepage.pdf", series_by_policy=series_by_policy, meta_footer=footer)

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
            "allocation_trace.csv": str((run_dir / "allocation_trace.csv").resolve()),
            "round_metrics.json": str((run_dir / "round_metrics.json").resolve()),
            "eval_report.md": str((run_dir / "eval_report.md").resolve()),
            "tradeoff_onepage.pdf": str((run_dir / "tradeoff_onepage.pdf").resolve()),
            "models_dir": str((run_dir / "models").resolve()),
        },
    }
    _write_json(run_dir / "run_manifest.json", manifest)

    print(f"Run complete. Outputs in: {run_dir}")

if __name__ == "__main__":
    main()
