from __future__ import annotations

import argparse
from pathlib import Path

from grokking.analysis.evaluate_detector import evaluate_run
from grokking.analysis.metrics import mean_lead_time_at_fpr


def _fmt(x: object) -> str:
    if x is None:
        return "None"
    if isinstance(x, float):
        if x != x:  # NaN
            return "nan"
        return f"{x:.6g}"
    return str(x)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs_dir", required=True, help="Directory containing seed_*/ run folders")
    parser.add_argument("--event", choices=["plateau", "jump"], default=None)
    parser.add_argument("--theta_grok", type=float, default=None)
    parser.add_argument("--hold_k", type=int, default=None)
    parser.add_argument("--horizon_steps", type=int, default=None)
    parser.add_argument("--grok_metric", type=str, default=None)
    parser.add_argument("--score_sign", type=float, default=None, help="Override score sign (+1 or -1; else from config)")
    parser.add_argument("--fpr", type=float, default=0.05)
    parser.add_argument("--w_jump", type=int, default=None)
    parser.add_argument("--delta_jump", type=float, default=None)
    parser.add_argument("--theta_floor", type=float, default=None)
    parser.add_argument("--delta_back", type=float, default=None)
    parser.add_argument("--out", type=str, default=None, help="Write Markdown table to this path")
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    run_dirs = sorted([p for p in runs_dir.iterdir() if p.is_dir() and p.name.startswith("seed_")])
    if not run_dirs:
        raise SystemExit(f"No run dirs found under: {runs_dir}")

    rows = []
    for run_dir in run_dirs:
        summary = evaluate_run(
            run_dir,
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
        row = {
            "seed": run_dir.name.replace("seed_", ""),
            "event": summary.get("event", ""),
            "t_grok": summary["t_grok"],
            "n_pos": summary.get("n_pos"),
            "score_sign": summary.get("score_sign"),
            "roc_auc": summary["roc_auc"],
            "average_precision": summary["average_precision"],
            "lead_time": lead,
        }
        rows.append(row)

    md_lines = []
    md_lines.append(f"# Grokking Hard Indicators Report")
    md_lines.append("")
    md_lines.append(f"- runs_dir: `{runs_dir.as_posix()}`")
    if args.event is not None:
        md_lines.append(f"- event (override): `{args.event}`")
    if args.grok_metric is not None:
        md_lines.append(f"- grok_metric (override): `{args.grok_metric}`")
    if args.score_sign is not None:
        md_lines.append(f"- score_sign (override): `{args.score_sign}`")
    if args.theta_grok is not None:
        md_lines.append(f"- theta_grok (override): `{args.theta_grok}`")
    if args.hold_k is not None:
        md_lines.append(f"- hold_k (override): `{args.hold_k}`")
    if args.horizon_steps is not None:
        md_lines.append(f"- horizon_steps (override): `{args.horizon_steps}`")
    if args.w_jump is not None:
        md_lines.append(f"- w_jump (override): `{args.w_jump}`")
    if args.delta_jump is not None:
        md_lines.append(f"- delta_jump (override): `{args.delta_jump}`")
    if args.theta_floor is not None:
        md_lines.append(f"- theta_floor (override): `{args.theta_floor}`")
    if args.delta_back is not None:
        md_lines.append(f"- delta_back (override): `{args.delta_back}`")
    md_lines.append("")
    md_lines.append("| seed | t_event | n_pos | score_sign | ROC-AUC | Avg Precision | Lead@FPR |")
    md_lines.append("|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md_lines.append(
            f"| {r['seed']} | {_fmt(r['t_grok'])} | {_fmt(r['n_pos'])} | {_fmt(r['score_sign'])} | {_fmt(r['roc_auc'])} | {_fmt(r['average_precision'])} | {_fmt(r['lead_time'])} |"
        )

    md = "\n".join(md_lines) + "\n"
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
    else:
        print(md, end="")


if __name__ == "__main__":
    main()
