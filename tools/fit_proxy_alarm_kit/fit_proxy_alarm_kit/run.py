from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .config import load_prereg, validate_prereg
from .utils_hash import sha256_hex, sha256_file, stable_hash_order
from .io_dataset import load_metrics, require_columns, apply_basic_filters
from .dataset import build_dataset, Dataset
from .split import holdout_split, labeled_train_val_split
from .modeling import train_logreg, predict_proba, coefficients, to_dict
from .eval import evaluate_holdout, monitorability_gate
from .acquisition import select_batch
from .event import detect_covjump
from .plot_onepager import plot_onepage_active
from .report import render_eval_report


def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _subset(dataset: Dataset, idx: np.ndarray) -> Dataset:
    return Dataset(
        ids=dataset.ids[idx],
        X=dataset.X.iloc[idx].reset_index(drop=True),
        y_oracle=dataset.y_oracle[idx],
        meta=dataset.meta,
    )


def _pick_primary_op(operating_points: list[dict], primary_fpr_target: float) -> dict | None:
    for op in operating_points:
        if float(op["fpr_target"]) == float(primary_fpr_target):
            return op
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--run_id", default=None)
    args = ap.parse_args()

    cfg = load_prereg(args.prereg).raw
    validate_prereg(cfg)

    kit_dir = Path(__file__).resolve().parents[1]
    out_root = kit_dir / cfg.get("outputs", {}).get("out_root", "out")
    out_root.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Lock prereg
    locked = run_dir / "PREREG.locked.yaml"
    _write_text(locked, Path(args.prereg).read_text(encoding="utf-8"))
    prereg_sha = sha256_hex(locked.read_text(encoding="utf-8"))

    # Load input metrics
    in_path_cfg = str(cfg["data"]["input_metrics_path"])
    in_path = Path(in_path_cfg)
    if not in_path.is_absolute():
        in_path = kit_dir / in_path
    df = load_metrics(in_path, fallback=cfg["data"].get("input_format_fallback", "csv"))

    id_field = str(cfg["data"]["id_field"])
    feat = list(cfg["boundary"]["feature_whitelist"])
    label_field = str(cfg["boundary"]["label_field"])
    tau_label = float(cfg["boundary"]["tau_label"])

    # Filters
    fmin = int(cfg["boundary"]["data_filters"]["min_length"])
    fmax = int(cfg["boundary"]["data_filters"]["max_length"])
    df = apply_basic_filters(df, min_len=fmin, max_len=fmax, id_field=id_field)

    required = [id_field] + feat + [label_field]
    require_columns(df, required)

    dataset = build_dataset(
        df=df,
        id_field=id_field,
        feature_whitelist=feat,
        label_field=label_field,
        tau_label=tau_label,
        drop_na_features=bool(cfg["boundary"]["data_filters"]["drop_na_features"]),
        drop_na_label=bool(cfg["boundary"]["data_filters"]["drop_na_label"]),
    )

    # Dataset snapshot (store config string; avoid absolute path in the snapshot)
    input_hash = sha256_file(str(in_path))
    feature_hash = sha256_hex(",".join(feat))
    _write_json(
        run_dir / "dataset_snapshot.json",
        {
            "kit_id": cfg.get("preregistration", {}).get("kit_id", "fit_proxy_alarm_kit"),
            "case_id": cfg.get("preregistration", {}).get("case_id", "UNKNOWN"),
            "run_id": run_id,
            "input_metrics_path_cfg": in_path_cfg,
            "input_metrics_sha256": input_hash,
            "prereg_sha256": prereg_sha,
            "n_total": int(len(dataset.ids)),
            "pos_rate_total": float(dataset.y_oracle.mean()),
            "tau_label": tau_label,
            "feature_whitelist": feat,
            "feature_whitelist_sha256": feature_hash,
        },
    )

    _write_json(
        run_dir / "boundary_snapshot.json",
        {
            "train_boundary": cfg["boundary"]["train_boundary"],
            "deploy_boundary": cfg["boundary"]["deploy_boundary"],
            "feature_whitelist": feat,
            "label_field": label_field,
            "tau_label": tau_label,
            "oracle_cost_accounting": cfg.get("evaluation", {}).get("holdout_role", "unspecified"),
        },
    )

    # Split: holdout vs pool
    seed = str(cfg["data"]["seed_string"])
    holdout_frac = float(cfg["evaluation"]["holdout_frac"])
    sp = holdout_split(dataset.ids, seed_string=seed, holdout_frac=holdout_frac)
    ds_hold = _subset(dataset, sp.holdout)
    ds_pool = _subset(dataset, sp.pool)

    # Policies + acquisition config
    policies: List[str] = list(cfg["acquisition"]["policies"])
    init_n = int(cfg["acquisition"]["init_labeled_n"])
    rounds = int(cfg["acquisition"]["rounds"])
    batch_size = int(cfg["acquisition"]["batch_size"])

    fpr_targets = [float(x) for x in cfg["monitorability"]["fpr_targets"]]
    primary_fpr = float(cfg["monitorability"]["primary_fpr_target"])
    fpr_tol = float(cfg.get("evaluation", {}).get("fpr_tolerance", 0.0))

    train_frac = float(cfg["split_labeled"]["train_frac"])
    val_frac = float(cfg["split_labeled"]["val_frac"])

    # Deterministic init labeled set
    pool_ids = list(ds_pool.ids.astype(str))
    init_ids = stable_hash_order(pool_ids, seed_string=seed + "::init")[: min(init_n, len(pool_ids))]

    # Per-policy logs
    decision_rows: list[dict] = []
    round_metrics: Dict[str, list[dict]] = {p: [] for p in policies}
    series_by_policy: Dict[str, Dict[str, Any]] = {}
    gate_by_policy: Dict[str, dict] = {}
    event_by_policy: Dict[str, dict] = {}
    final_summary_by_policy: Dict[str, dict] = {}

    final_models_dir = run_dir / "final_models"
    final_models_dir.mkdir(parents=True, exist_ok=True)

    for policy in policies:
        labeled_set = set(init_ids)
        unlabeled_set = set(pool_ids) - labeled_set

        # log init
        for item_id in init_ids:
            idx = int(np.where(ds_pool.ids == item_id)[0][0])
            y = int(ds_pool.y_oracle[idx])
            decision_rows.append(
                {
                    "policy": policy,
                    "round": 0,
                    "item_id": item_id,
                    "selected_by": "init_seed",
                    "predicted_prob": float("nan"),
                    "revealed_label": y,
                }
            )

        queried_counts: list[int] = []
        tpr_primary_series: list[float] = []
        fpr_primary_series: list[float] = []
        batch_pos_rate_series: list[float] = []
        round_index_series: list[int] = []

        last_model = None
        last_ev = None

        for r in range(0, rounds + 1):
            labeled_ids = sorted(list(labeled_set))
            labeled_idx = np.array([int(np.where(ds_pool.ids == i)[0][0]) for i in labeled_ids], dtype=int)
            X_lab = ds_pool.X.iloc[labeled_idx].reset_index(drop=True)
            y_lab = ds_pool.y_oracle[labeled_idx]
            ids_lab = ds_pool.ids[labeled_idx]

            lv = labeled_train_val_split(
                ids_lab, seed_string=seed + f"::{policy}::round{r}", train_frac=train_frac, val_frac=val_frac
            )
            if len(lv.train) == 0 or len(lv.val) == 0:
                break

            mcfg = cfg["model"]
            model = train_logreg(
                X=X_lab.iloc[lv.train],
                y=y_lab[lv.train],
                standardize=bool(mcfg["standardize"]),
                impute_strategy=str(mcfg["impute_strategy"]),
                params=mcfg["params"],
            )

            s_val = predict_proba(model, X_lab.iloc[lv.val])
            y_val = y_lab[lv.val]
            s_hold = predict_proba(model, ds_hold.X)
            y_hold = ds_hold.y_oracle

            ev = evaluate_holdout(y_val=y_val, s_val=s_val, y_test=y_hold, s_test=s_hold, fpr_targets=fpr_targets)
            op_primary = _pick_primary_op(list(ev["operating_points"]), primary_fpr_target=primary_fpr)
            assert op_primary is not None

            queried = len(labeled_set)
            queried_counts.append(int(queried))
            tpr_primary_series.append(float(op_primary["tpr"]))
            fpr_primary_series.append(float(op_primary["fpr"]))
            round_index_series.append(int(r))

            if r == 0:
                batch_pos = float(
                    np.mean([row["revealed_label"] for row in decision_rows if row["policy"] == policy and row["round"] == 0])
                )
            else:
                last_batch = [row["revealed_label"] for row in decision_rows if row["policy"] == policy and row["round"] == r]
                batch_pos = float(np.mean(last_batch)) if last_batch else float("nan")
            batch_pos_rate_series.append(batch_pos)

            round_metrics[policy].append(
                {
                    "round": int(r),
                    "queried_labels": int(queried),
                    "holdout_n": int(len(y_hold)),
                    "roc_auc": float(ev["roc_auc"]),
                    "pr_auc": float(ev["pr_auc"]),
                    "operating_points": ev["operating_points"],
                    "coefficients": coefficients(model),
                }
            )

            last_model = model
            last_ev = ev

            if r == rounds:
                break

            unlabeled_ids = sorted(list(unlabeled_set))
            if len(unlabeled_ids) == 0:
                break

            unlabeled_idx = np.array([int(np.where(ds_pool.ids == i)[0][0]) for i in unlabeled_ids], dtype=int)
            X_unlab = ds_pool.X.iloc[unlabeled_idx].reset_index(drop=True)
            s_unlab = predict_proba(model, X_unlab)

            batch = select_batch(
                policy=policy,
                unlabeled_ids=unlabeled_ids,
                unlabeled_scores=s_unlab,
                batch_size=batch_size,
                seed=seed + f"::{policy}::round{r+1}",
            )

            for item_id in batch:
                j = unlabeled_ids.index(item_id)
                p_sel = float(s_unlab[j])
                idx = int(np.where(ds_pool.ids == item_id)[0][0])
                y = int(ds_pool.y_oracle[idx])
                decision_rows.append(
                    {
                        "policy": policy,
                        "round": int(r + 1),
                        "item_id": item_id,
                        "selected_by": policy,
                        "predicted_prob": float(p_sel),
                        "revealed_label": y,
                    }
                )
                labeled_set.add(item_id)
                if item_id in unlabeled_set:
                    unlabeled_set.remove(item_id)

        series_by_policy[policy] = {
            "queried_labels": queried_counts,
            "tpr_primary": tpr_primary_series,
            "fpr_primary": fpr_primary_series,
            "batch_pos_rate": batch_pos_rate_series,
            "round_index": round_index_series,
        }

        evcfg = cfg.get("event", {})
        evt = detect_covjump(
            tpr_series=tpr_primary_series,
            W_jump=int(evcfg.get("W_jump_rounds", 3)),
            delta_tpr=float(evcfg.get("delta_tpr", 0.05)),
        )
        event_by_policy[policy] = {"found": evt.found, "round_index": evt.round_index, "reason": evt.reason}

        if last_ev is None:
            gate_by_policy[policy] = {"status": "NO_EVAL", "reason": "no rounds evaluated"}
            final_summary_by_policy[policy] = {}
        else:
            gate_by_policy[policy] = monitorability_gate(
                operating_points=list(last_ev["operating_points"]),
                primary_fpr_target=primary_fpr,
                fpr_tolerance=fpr_tol,
            )
            op_primary = _pick_primary_op(list(last_ev["operating_points"]), primary_fpr_target=primary_fpr)
            final_summary_by_policy[policy] = {
                "roc_auc": last_ev["roc_auc"],
                "pr_auc": last_ev["pr_auc"],
                "primary_op": op_primary,
            }

        if last_model is not None:
            _write_json(final_models_dir / f"{policy}.json", to_dict(last_model))

    pd.DataFrame(decision_rows).to_csv(run_dir / "decision_trace.csv", index=False)
    _write_json(run_dir / "round_metrics.json", round_metrics)

    # Choose default alarm model: best USABLE policy by final-round TPR@primary
    chosen_policy = None
    best_tpr = -1.0
    for policy in policies:
        if gate_by_policy.get(policy, {}).get("status") != "USABLE":
            continue
        op = final_summary_by_policy.get(policy, {}).get("primary_op")
        if not op:
            continue
        tpr = float(op.get("tpr", 0.0))
        if tpr > best_tpr:
            best_tpr = tpr
            chosen_policy = policy
    if chosen_policy is None and policies:
        chosen_policy = policies[0]

    alarm_model_path = run_dir / "alarm_model.json"
    if chosen_policy is not None:
        src = final_models_dir / f"{chosen_policy}.json"
        if src.exists():
            alarm_model_path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    thresholds: Dict[str, Any] = {"chosen_policy": chosen_policy, "by_fpr_target": {}}
    if chosen_policy is not None and round_metrics.get(chosen_policy):
        last_round = round_metrics[chosen_policy][-1]
        for op in last_round.get("operating_points", []):
            thresholds["by_fpr_target"][str(op["fpr_target"])] = {
                "threshold": op["threshold"],
                "achieved_fpr": op["fpr"],
                "tpr": op["tpr"],
            }
    _write_json(run_dir / "alarm_thresholds.json", thresholds)

    plot_onepage_active(
        out_pdf=run_dir / "tradeoff_onepage.pdf",
        series_by_policy=series_by_policy,
        primary_fpr_target=primary_fpr,
        meta_footer=f"kit=fit_proxy_alarm_kit | case={cfg.get('preregistration', {}).get('case_id', 'UNKNOWN')} | primary_fpr={primary_fpr}",
    )

    dataset_snapshot = json.loads((run_dir / "dataset_snapshot.json").read_text(encoding="utf-8"))
    rep = render_eval_report(
        run_id=run_id,
        cfg=cfg,
        dataset_snapshot=dataset_snapshot,
        gate_by_policy=gate_by_policy,
        event_by_policy=event_by_policy,
        final_summary_by_policy=final_summary_by_policy,
    )
    _write_text(run_dir / "eval_report.md", rep)

    _write_json(
        run_dir / "run_manifest.json",
        {
            "kit_id": cfg.get("preregistration", {}).get("kit_id", "fit_proxy_alarm_kit"),
            "case_id": cfg.get("preregistration", {}).get("case_id", "UNKNOWN"),
            "run_id": run_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "git_commit": os.environ.get("GIT_COMMIT", "UNKNOWN"),
            "prereg_sha256": prereg_sha,
            "chosen_policy": chosen_policy,
            "artifacts": {
                "dataset_snapshot": "dataset_snapshot.json",
                "boundary_snapshot": "boundary_snapshot.json",
                "decision_trace": "decision_trace.csv",
                "round_metrics": "round_metrics.json",
                "eval_report": "eval_report.md",
                "tradeoff_onepage": "tradeoff_onepage.pdf",
                "alarm_model": "alarm_model.json",
                "alarm_thresholds": "alarm_thresholds.json",
            },
        },
    )

    print(f"Run complete. Outputs in: {run_dir}")


if __name__ == "__main__":
    main()
