from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from grokking.analysis.evaluate_detector import evaluate_run
from grokking.analysis.metrics import average_precision, mean_lead_time_at_fpr, roc_auc_score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs_dir", required=True, help="Directory containing seed_*/ run folders")
    parser.add_argument("--fpr", type=float, default=0.05)
    parser.add_argument("--event", choices=["plateau", "jump"], default=None, help="Override event type (else from each config)")
    parser.add_argument("--theta_grok", type=float, default=None, help="Override grok threshold (else from each config)")
    parser.add_argument("--hold_k", type=int, default=None, help="Override consecutive checkpoints (else from each config)")
    parser.add_argument("--horizon_steps", type=int, default=None, help="Override prediction horizon in steps (else from each config)")
    parser.add_argument("--grok_metric", type=str, default=None, help="Override grok metric key (else from each config)")
    parser.add_argument("--score_sign", type=float, default=None, help="Override score sign (+1 or -1; else from each config)")
    parser.add_argument("--w_jump", type=int, default=None, help="Override jump window W_jump (checkpoints)")
    parser.add_argument("--delta_jump", type=float, default=None, help="Override jump threshold delta_jump")
    parser.add_argument("--theta_floor", type=float, default=None, help="Override jump floor theta_floor")
    parser.add_argument("--delta_back", type=float, default=None, help="Override jump backslide tolerance delta_back")
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    run_dirs = sorted([p for p in runs_dir.iterdir() if p.is_dir() and p.name.startswith("seed_")])
    if not run_dirs:
        raise SystemExit(f"No run dirs found under: {runs_dir}")

    summaries = [
        evaluate_run(
            p,
            event=args.event,
            theta_grok=args.theta_grok,
            hold_k=args.hold_k,
            horizon_steps=args.horizon_steps,
            grok_metric=args.grok_metric,
            score_sign=args.score_sign,
            w_jump=args.w_jump,
            delta_jump=args.delta_jump,
            theta_floor=args.theta_floor,
            delta_back=args.delta_back,
        )
        for p in run_dirs
    ]
    aucs = np.asarray([s["roc_auc"] for s in summaries], dtype=np.float64)
    aps = np.asarray([s["average_precision"] for s in summaries], dtype=np.float64)
    lead_global = mean_lead_time_at_fpr(run_summaries=summaries, fpr_target=float(args.fpr))
    per_run_leads = []
    for s in summaries:
        if s["t_grok"] is None:
            continue
        lt = mean_lead_time_at_fpr(run_summaries=[s], fpr_target=float(args.fpr))
        if np.isfinite(lt):
            per_run_leads.append(float(lt))
    lead_per_run = float(np.mean(per_run_leads)) if per_run_leads else float("nan")

    y_all = np.asarray([yi for s in summaries for yi in s["y"]], dtype=np.int64)
    scores_all = np.asarray([sc for s in summaries for sc in s["scores"]], dtype=np.float64)
    auc_all = roc_auc_score(y_all, scores_all)
    ap_all = average_precision(y_all, scores_all)
    n_grok = sum(1 for s in summaries if s["t_grok"] is not None)

    aucs_finite = aucs[np.isfinite(aucs)]
    aps_finite = aps[np.isfinite(aps)]
    auc_mean = float(np.mean(aucs_finite)) if aucs_finite.size else float("nan")
    auc_std = float(np.std(aucs_finite)) if aucs_finite.size else float("nan")
    ap_mean = float(np.mean(aps_finite)) if aps_finite.size else float("nan")
    ap_std = float(np.std(aps_finite)) if aps_finite.size else float("nan")

    print(f"runs={len(summaries)} dir={runs_dir}")
    print(f"grok_runs={n_grok}/{len(summaries)} (runs with t_grok)")
    print(f"ROC_AUC pooled={auc_all} mean={auc_mean} std={auc_std}")
    print(f"AveragePrecision pooled={ap_all} mean={ap_mean} std={ap_std}")
    print(f"MeanLeadTimeAtFPR(global)={args.fpr} => {lead_global}")
    print(f"MeanLeadTimeAtFPR(per-run mean)={args.fpr} => {lead_per_run} (coverage={len(per_run_leads)}/{n_grok})")


if __name__ == "__main__":
    main()
