from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from src.evaluate import build_episode_summary, compute_recoverability, write_recoverability_json
from src.monitorability import build_tradeoff, summarize_main_findings
from src.simulator import run_all


def render_report(cfg: dict, rec_obj: dict, trade_df: pd.DataFrame, findings: dict) -> str:
    lines = []
    lines.append("# Self-Reference Recoverability Report (v0.1)")
    lines.append("")
    lines.append("## Boundary")
    lines.append(f"- System: {cfg['boundary']['system']}")
    lines.append(f"- Groups: {', '.join(g['id'] for g in cfg['groups'])}")
    lines.append("")

    lines.append("## Recoverability (R)")
    lines.append("")
    lines.append("| Group | P_recover | T_recover_mean | D_drift_mean | R | lockin_rate | non_recovered_rate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for g, v in rec_obj["groups"].items():
        lines.append(
            f"| {g} | {v['P_recover']:.3f} | {v['T_recover_mean']:.2f} | {v['D_drift_mean']:.2f} | {v['R']:.4f} | {v['lockin_rate']:.3f} | {v['non_recovered_rate']:.3f} |"
        )
    lines.append("")

    lines.append("## Monitorability Tradeoff")
    lines.append("")
    lines.append("| Group | FPR target | FPR achieved | Coverage | Abstain |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, r in trade_df.sort_values(["group", "fpr_target"]).iterrows():
        lines.append(
            f"| {r['group']} | {r['fpr_target']:.2f} | {r['fpr_achieved']:.3f} | {r['coverage']:.3f} | {r['abstain_rate']:.3f} |"
        )
    lines.append("")

    lines.append("## Main Findings")
    lines.append("")
    lines.append(f"- Best R group: {findings['best_R_group']}")
    lines.append("- R by group: " + json.dumps(findings["R_by_group"], ensure_ascii=False))
    lines.append("- Coverage@FPR=0.05 by group: " + json.dumps(findings["coverage_at_fpr_0_05"], ensure_ascii=False))
    lines.append("")
    lines.append("## Interpretation Discipline")
    lines.append("")
    lines.append("- This is a structural recoverability experiment, not a phenomenology claim.")
    lines.append("- If detector cannot control FPR, no control action should be automated from that signal.")

    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", default="EST_PREREG.yaml")
    args = ap.parse_args()

    prereg_path = Path(args.prereg)
    with prereg_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    out = cfg["outputs"]
    out_dir = Path(out["episodes_csv"]).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    episodes_df, meta_df = run_all(cfg)
    summary_df = build_episode_summary(episodes_df, meta_df, cfg)
    rec_obj = compute_recoverability(summary_df, cfg)
    trade_df = build_tradeoff(summary_df, cfg)
    findings = summarize_main_findings(rec_obj, trade_df)

    episodes_df.to_csv(out["episodes_csv"], index=False)
    summary_df.to_csv(out["episode_summary_csv"], index=False)
    trade_df.to_csv(out["monitorability_csv"], index=False)
    write_recoverability_json(out["recoverability_json"], rec_obj)

    report_text = render_report(cfg, rec_obj, trade_df, findings)
    Path(out["report_md"]).write_text(report_text, encoding="utf-8")

    print("Done")
    print(f"- Episodes: {out['episodes_csv']}")
    print(f"- Summary: {out['episode_summary_csv']}")
    print(f"- Recoverability: {out['recoverability_json']}")
    print(f"- Monitorability: {out['monitorability_csv']}")
    print(f"- Report: {out['report_md']}")


if __name__ == "__main__":
    main()
