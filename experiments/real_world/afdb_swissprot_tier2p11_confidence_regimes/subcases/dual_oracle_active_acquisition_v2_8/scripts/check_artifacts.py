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
    "policy_cards/claims_overlay.json",
    "policy_cards/assets_manifest.json",
    "leakage_audit.json",
    "event_summary.json",
    "eval_report.md",
    "tradeoff_onepage.pdf",
    "run_manifest.json",
]


def q_tag(q: float) -> str:
    x = float(q) * 100.0
    if abs(x - round(x)) < 1e-9:
        return f"q{int(round(x)):02d}"
    return f"q{str(x).replace('.','p')}"


def a_tag(a: float) -> str:
    x = float(a) * 100.0
    if abs(x - round(x)) < 1e-9:
        return f"a{int(round(x)):02d}"
    return f"a{str(x).replace('.','p')}"


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

    summary = json.loads((rd / "bilevel_bootstrap_summary.json").read_text(encoding="utf-8"))
    tail_qs = summary.get("tail_quantiles", None)
    cvar_alphas = summary.get("cvar_alphas", None)

    if not isinstance(tail_qs, list) or not tail_qs:
        raise SystemExit("bilevel_bootstrap_summary.json missing tail_quantiles list.")
    if not isinstance(cvar_alphas, list) or not cvar_alphas:
        raise SystemExit("bilevel_bootstrap_summary.json missing cvar_alphas list.")

    gate = json.loads((rd / "claims_gate_report.json").read_text(encoding="utf-8"))
    if gate.get("mode") != "bilevel_bootstrap_two_key_gate":
        raise SystemExit("claims_gate_report.json mode != bilevel_bootstrap_two_key_gate (v2.7 expects two-key gate).")
    if gate.get("gate_metric") != "bilevel_two_key_min_ci_low":
        raise SystemExit("claims_gate_report.json gate_metric != bilevel_two_key_min_ci_low.")
    comps = gate.get("gate_components", None)
    if not isinstance(comps, list) or set(comps) != {"bilevel_cvar_gate_margin_ci_low", "bilevel_tail_min_margin_ci_low"}:
        raise SystemExit("claims_gate_report.json gate_components mismatch (expected CVaR gate + tail_min gate).")

    bi = pd.read_csv(rd / "frontier_bilevel_robust_table.csv")
    base_need = {
        "bilevel_cvar_gate_margin_ci_low",
        "bilevel_tail_min_margin_ci_low",
        "bilevel_two_key_min_ci_low",
        "bilevel_two_key_min_ci_high",
        "gate_pass_cvar",
        "gate_pass_tail_min",
        "claim_level",
        "claim_outperforms_random_allowed",
        "gate_metric",
    }
    if not base_need.issubset(set(bi.columns)):
        raise SystemExit("frontier_bilevel_robust_table.csv missing v2.7 two-key gate columns.")

    # Per-q tail audit columns
    for q in tail_qs:
        tag = q_tag(float(q))
        need = {f"bilevel_tail_{tag}_margin_ci_low", f"bilevel_tail_{tag}_margin_ci_high"}
        if not need.issubset(set(bi.columns)):
            raise SystemExit(f"frontier_bilevel_robust_table.csv missing tail columns for {tag} (q={q}).")

    # Per-a CVaR audit columns
    for a in cvar_alphas:
        tag = a_tag(float(a))
        need = {f"bilevel_cvar_{tag}_margin_ci_low", f"bilevel_cvar_{tag}_margin_ci_high"}
        if not need.issubset(set(bi.columns)):
            raise SystemExit(f"frontier_bilevel_robust_table.csv missing CVaR columns for {tag} (alpha={a}).")

    # Gate consistency: allowed => both component ci_low > 0 AND min ci low > 0
    bad = []
    for pol, g in (gate.get("by_policy", {}) or {}).items():
        lo_c = g.get("bilevel_cvar_gate_margin_ci_low", None)
        lo_t = g.get("bilevel_tail_min_margin_ci_low", None)
        lo_m = g.get("bilevel_two_key_min_ci_low", None)
        allowed = bool(g.get("allowed", False))

        if allowed:
            if lo_c is None or lo_t is None or lo_m is None:
                bad.append(pol)
                continue
            if float(lo_c) <= 0 or float(lo_t) <= 0 or float(lo_m) <= 0:
                bad.append(pol)

    if bad:
        raise SystemExit("Claims gate inconsistency (allowed but two-key condition not met):\n" + "\n".join(f"- {p}" for p in bad))

# v2.8: ensure claims overlay applied to all policy cards
overlay_path = rd / "policy_cards" / "claims_overlay.json"
if not overlay_path.exists():
    raise SystemExit("Missing policy_cards/claims_overlay.json (claims overlay not applied).")
try:
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
except Exception:
    raise SystemExit("policy_cards/claims_overlay.json is not valid JSON.")
pt = pd.read_csv(rd / "policy_table.csv")
for pol in pt["policy"].astype(str).tolist():
    card = rd / "policy_cards" / f"{pol}.md"
    if not card.exists():
        raise SystemExit(f"Missing policy card markdown: {card}")
    md = card.read_text(encoding="utf-8")
    if "## Claims & gate status (generated)" not in md:
        raise SystemExit(f"Policy card missing claims overlay section: {card}")
    if pol not in (overlay.get("by_policy", {}) or {}):
        raise SystemExit(f"claims_overlay.json missing policy entry: {pol}")

    print("OK: v2.8 artifacts + leakage pass + bilevel two-key gate + audit columns + graded claims present.")


if __name__ == "__main__":
    main()
