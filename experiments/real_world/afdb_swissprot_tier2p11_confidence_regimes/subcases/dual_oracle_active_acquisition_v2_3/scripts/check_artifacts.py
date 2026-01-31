from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

REQUIRED_FILES = [
    "PREREG.locked.yaml",
    "dataset_snapshot.json",
    "boundary_snapshot.json",
    "holdout_snapshot.json",
    "decision_trace.csv",
    "allocation_trace.csv",
    "round_metrics.json",
    "regime_timeline.csv",
    "regime_summary.json",
    "policy_table.csv",
    "cost_summary.json",
    "baseline_band.json",
    "policy_band.json",
    "frontier_onepage.pdf",
    "frontier_table.csv",
    "frontier_robust_table.csv",
    "frontier_policy_robust_table.csv",
    "frontier_bilevel_robust_table.csv",
    "bilevel_bootstrap_summary.json",
    "jump_type_sensitivity.json",
    "jump_robustness.json",
    "claims_gate_report.json",
    "Claims.md",
    "claims_templates.json",
    "policy_grid_manifest.json",
    "policy_cards_index.md",
    "policy_cards/assets_manifest.json",
    "leakage_audit.json",
    "event_summary.json",
    "eval_report.md",
    "tradeoff_onepage.pdf",
    "run_manifest.json",
]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    args = ap.parse_args()
    rd = Path(args.run_dir)

    if not rd.exists():
        raise SystemExit(f"run_dir does not exist: {rd}")

    missing = [f for f in REQUIRED_FILES if not (rd / f).exists()]
    if not (rd / "policy_cards").exists():
        missing.append("policy_cards/")
    if missing:
        raise SystemExit("Missing required artifacts:\n" + "\n".join(f"- {m}" for m in missing))

    leak = json.loads((rd / "leakage_audit.json").read_text(encoding="utf-8"))
    if not leak.get("overall_pass", False):
        raise SystemExit("Leakage audit failed (overall_pass=false).")

    bi = pd.read_csv(rd / "frontier_bilevel_robust_table.csv")
    need = {"bilevel_margin_ci_low", "bilevel_margin_ci_high", "claim_outperforms_random_allowed"}
    if not need.issubset(set(bi.columns)):
        raise SystemExit("frontier_bilevel_robust_table.csv missing bilevel CI gate columns.")

    gate = json.loads((rd / "claims_gate_report.json").read_text(encoding="utf-8"))
    if gate.get("mode") != "bilevel_bootstrap":
        raise SystemExit("claims_gate_report.json mode != bilevel_bootstrap (v2.3 expects bilevel).")

    # gate consistency: allowed => ci_low > 0
    bad = []
    for pol, g in (gate.get("by_policy", {}) or {}).items():
        lo = g.get("bilevel_margin_ci_low", None)
        allowed = bool(g.get("allowed", False))
        if lo is not None and allowed and float(lo) <= 0:
            bad.append(pol)
    if bad:
        raise SystemExit("Claims gate inconsistency (allowed but ci_low<=0):\n" + "\n".join(f"- {p}" for p in bad))

    print("OK: v2.3 artifacts + leakage pass + bilevel CI gate + claims pack present.")

if __name__ == "__main__":
    main()
