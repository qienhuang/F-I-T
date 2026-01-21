from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from grokking.analysis.evaluate_detector import evaluate_run


def compute_fpr_coverage_lead(*, run_summaries: list[dict], threshold: float) -> tuple[float, float, str, float]:
    neg_total = 0
    neg_fp = 0

    n_grok = 0
    n_covered = 0
    lead_times: list[int] = []

    for r in run_summaries:
        t_grok = r["t_grok"]
        steps = r["steps"]
        scores = r["scores"]
        y = r["y"]

        # FPR over negative checkpoints
        for yi, sc in zip(y, scores):
            if int(yi) == 0:
                neg_total += 1
                if float(sc) >= float(threshold):
                    neg_fp += 1

        # Coverage/lead: earliest trigger within positive horizon
        if t_grok is None:
            continue
        n_grok += 1
        triggered_step = None
        for yi, step, sc in zip(y, steps, scores):
            if int(yi) == 1 and float(sc) >= float(threshold):
                triggered_step = int(step)
                break
        if triggered_step is not None:
            n_covered += 1
            lead_times.append(int(t_grok) - int(triggered_step))

    fpr = neg_fp / max(neg_total, 1)
    coverage = (n_covered / n_grok) if n_grok else float("nan")
    lead = float(np.mean(lead_times)) if lead_times else float("nan")
    covered = f"{n_covered}/{n_grok}" if n_grok else "0/0"
    return float(fpr), float(coverage), covered, float(lead)


def select_threshold_by_target_fpr(*, run_summaries: list[dict], fpr_target: float) -> tuple[float, float]:
    all_scores: list[float] = []
    for r in run_summaries:
        all_scores.extend([float(s) for s in r["scores"]])
    if not all_scores:
        return float("nan"), float("nan")
    thresholds = np.unique(np.asarray(all_scores, dtype=np.float64))[::-1]

    best_thr = float(thresholds[0])
    best_fpr = float("inf")
    best_abs = float("inf")
    for thr in thresholds:
        fpr, _, _, _ = compute_fpr_coverage_lead(run_summaries=run_summaries, threshold=float(thr))
        abs_err = abs(float(fpr) - float(fpr_target))
        if abs_err < best_abs:
            best_abs = abs_err
            best_thr = float(thr)
            best_fpr = float(fpr)
            continue
        if abs_err == best_abs and float(fpr) < float(best_fpr):
            best_thr = float(thr)
            best_fpr = float(fpr)
    return best_thr, best_fpr


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs_dir", required=True, help="Directory containing seed_*/ run folders")
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
    parser.add_argument(
        "--fprs",
        type=float,
        nargs="+",
        default=[0.01, 0.02, 0.05, 0.10, 0.15, 0.20],
        help="Target FPR values to sweep",
    )
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

    print(f"runs={len(summaries)} dir={runs_dir}")
    print("FPR (target)   FPR (actual)   Coverage     N Covered    Mean Lead Time")
    print("-" * 85)
    for target in [float(x) for x in args.fprs]:
        thr, _ = select_threshold_by_target_fpr(run_summaries=summaries, fpr_target=target)
        fpr, coverage, covered, lead = compute_fpr_coverage_lead(run_summaries=summaries, threshold=thr)
        cov_pct = (coverage * 100.0) if np.isfinite(coverage) else float("nan")
        lead_str = f"{int(round(lead))} steps" if np.isfinite(lead) else "N/A"
        print(f"{target:0.3f}          {fpr:0.4f}         {cov_pct:6.1f}%   {covered:>7s}     {lead_str}")


if __name__ == "__main__":
    main()
