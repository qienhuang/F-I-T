from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np

from grokking.analysis.events import compute_t_grok, compute_t_jump, label_grok_within_horizon
from grokking.analysis.metrics import average_precision, mean_lead_time_at_fpr, roc_auc_score
from grokking.analysis.score import compute_scores
from grokking.utils.config import load_yaml
from grokking.utils.jsonl import read_jsonl


def evaluate_run(
    run_dir: str | Path,
    *,
    event: str | None = None,
    theta_grok: float | None = None,
    hold_k: int | None = None,
    horizon_steps: int | None = None,
    grok_metric: str | None = None,
    w_jump: int | None = None,
    delta_jump: float | None = None,
    theta_floor: float | None = None,
    delta_back: float | None = None,
    score_sign: float | None = None,
) -> dict[str, Any]:
    run_dir = Path(run_dir)
    spec = load_yaml(run_dir / "config.resolved.yaml")
    checkpoints = read_jsonl(run_dir / "logs.jsonl")
    checkpoints = sorted(checkpoints, key=lambda r: int(r["step"]))

    eval_cfg = spec.get("evaluation", {})

    if event is None:
        event = str(eval_cfg.get("event", {}).get("type", "plateau"))
    event = str(event).strip().lower()
    if event not in {"plateau", "jump"}:
        raise ValueError(f"Unknown event={event!r} (expected 'plateau' or 'jump')")

    if grok_metric is None:
        if event == "plateau":
            grok_metric = str(eval_cfg.get("grok_event", {}).get("metric", "test_acc"))
        else:
            grok_metric = str(eval_cfg.get("event", {}).get("jump", {}).get("metric", "test_acc"))

    if hold_k is None:
        if event == "plateau":
            hold_k = int(eval_cfg.get("grok_event", {}).get("hold_K_checkpoints", 5))
        else:
            hold_k = int(eval_cfg.get("event", {}).get("jump", {}).get("hold_k", 5))

    if event == "plateau":
        if theta_grok is None:
            theta_grok = float(eval_cfg.get("grok_event", {}).get("theta_grok", 0.95))
    else:
        if w_jump is None:
            w_jump = int(eval_cfg.get("event", {}).get("jump", {}).get("w_jump", 2))
        if delta_jump is None:
            delta_jump = float(eval_cfg.get("event", {}).get("jump", {}).get("delta_jump", 0.04))
        if theta_floor is None:
            theta_floor = float(eval_cfg.get("event", {}).get("jump", {}).get("theta_floor", 0.85))
        if delta_back is None:
            delta_back = float(eval_cfg.get("event", {}).get("jump", {}).get("delta_back", 0.03))

    if horizon_steps is None:
        horizon_steps = int(spec["time"]["prediction_horizon_N_steps"])
    window_w = int(spec["time"]["window_W_checkpoints"])

    matrices = spec.get("state", {}).get("spectral_matrices", ["unembed.weight"])
    h_spec_layer = str(matrices[0])

    score_cfg = spec["decision_rule"]["score"]
    if score_sign is None:
        score_sign = float(score_cfg.get("score_sign", score_cfg.get("sign", 1.0)))
    steps, scores = compute_scores(
        checkpoints,
        h_spec_layer=h_spec_layer,
        window_w=window_w,
        eps_hspec=float(score_cfg["eps_hspec"]),
        theta_corr=float(score_cfg["theta_corr"]),
        w_hspec=float(score_cfg.get("w_hspec", 1.0)),
        w_corr=float(score_cfg.get("w_corr", 1.0)),
        score_sign=float(score_sign),
    )

    if event == "plateau":
        t_event = compute_t_grok(
            checkpoints,
            theta_grok=float(theta_grok),
            hold_k=int(hold_k),
            metric=str(grok_metric),
        )
    else:
        t_event = compute_t_jump(
            checkpoints,
            metric=str(grok_metric),
            w_jump=int(w_jump),
            delta_jump=float(delta_jump),
            theta_floor=float(theta_floor),
            delta_back=float(delta_back),
            hold_k=int(hold_k),
        )

    y = np.asarray(
        [label_grok_within_horizon(step=s, t_grok=t_event, horizon_steps=horizon_steps) for s in steps],
        dtype=np.int64,
    )
    y_score = np.asarray(scores, dtype=np.float64)
    n_pos = int((y == 1).sum())
    n_neg = int((y == 0).sum())

    return {
        "run_dir": str(run_dir),
        "event": str(event),
        "grok_metric": str(grok_metric),
        "hold_k": int(hold_k),
        "horizon_steps": int(horizon_steps),
        "score_sign": float(score_sign),
        "theta_grok": float(theta_grok) if theta_grok is not None else None,
        "w_jump": int(w_jump) if w_jump is not None else None,
        "delta_jump": float(delta_jump) if delta_jump is not None else None,
        "theta_floor": float(theta_floor) if theta_floor is not None else None,
        "delta_back": float(delta_back) if delta_back is not None else None,
        "t_grok": t_event,
        "y": y.tolist(),
        "n_pos": n_pos,
        "n_neg": n_neg,
        "steps": steps,
        "scores": scores,
        "roc_auc": roc_auc_score(y, y_score),
        "average_precision": average_precision(y, y_score),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="Run directory (contains logs.jsonl + config.resolved.yaml)")
    parser.add_argument("--fpr", type=float, default=0.05, help="FPR target for lead time metric")
    parser.add_argument("--event", choices=["plateau", "jump"], default=None, help="Override event type (else from config)")
    parser.add_argument("--theta_grok", type=float, default=None, help="Override grok threshold (else from config)")
    parser.add_argument("--hold_k", type=int, default=None, help="Override consecutive checkpoints (else from config)")
    parser.add_argument("--horizon_steps", type=int, default=None, help="Override prediction horizon in steps (else from config)")
    parser.add_argument("--grok_metric", type=str, default=None, help="Override grok metric key (else from config)")
    parser.add_argument("--score_sign", type=float, default=None, help="Override score sign (+1 or -1; else from config)")
    parser.add_argument("--w_jump", type=int, default=None, help="Override jump window W_jump (checkpoints)")
    parser.add_argument("--delta_jump", type=float, default=None, help="Override jump threshold delta_jump")
    parser.add_argument("--theta_floor", type=float, default=None, help="Override jump floor theta_floor")
    parser.add_argument("--delta_back", type=float, default=None, help="Override jump backslide tolerance delta_back")
    args = parser.parse_args()

    summary = evaluate_run(
        args.run,
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
    lead = mean_lead_time_at_fpr(run_summaries=[summary], fpr_target=float(args.fpr))
    print(f"run={summary['run_dir']}")
    print(
        f"event={summary['event']} grok_metric={summary['grok_metric']} theta_grok={summary['theta_grok']} hold_k={summary['hold_k']} "
        f"w_jump={summary['w_jump']} delta_jump={summary['delta_jump']} theta_floor={summary['theta_floor']} delta_back={summary['delta_back']} "
        f"horizon_steps={summary['horizon_steps']}"
    )
    print(f"score_sign={summary['score_sign']}")
    print(f"t_grok={summary['t_grok']} n_pos={summary['n_pos']} n_neg={summary['n_neg']}")
    print(f"ROC_AUC={summary['roc_auc']}")
    print(f"AveragePrecision={summary['average_precision']}")
    print(f"MeanLeadTimeAtFPR={args.fpr} => {lead}")


if __name__ == "__main__":
    main()
