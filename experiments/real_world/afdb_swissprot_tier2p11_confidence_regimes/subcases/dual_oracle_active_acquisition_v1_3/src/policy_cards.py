from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import pandas as pd

def write_policy_cards(
    run_dir: Path,
    dataset_snapshot: Dict[str, Any],
    boundary_snapshot: Dict[str, Any],
    policy_table: pd.DataFrame,
    leakage_audit: Dict[str, Any],
    series_by_policy: Dict[str, Any],
    primary_cap: float,
    tpr_min: float,
) -> None:
    out_dir = run_dir / "policy_cards"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_rows: List[Dict[str, Any]] = []

    for _, row in policy_table.iterrows():
        policy = str(row["policy"])
        card_path = out_dir / f"{policy}.md"

        leak_pass = bool(row.get("leakage_pass", False))
        leak_detail = (leakage_audit.get("by_policy", {}) or {}).get(policy, {})

        # Provide pointers to trace files for audit
        decision_trace = "decision_trace.csv"
        allocation_trace = "allocation_trace.csv"

        # Grab event dictionary if available
        events = None
        try:
            events = series_by_policy.get(policy, {}).get("events", None)
        except Exception:
            events = None

        text = []
        text.append(f"# Policy Card — `{policy}`\n\n")
        text.append("## Boundary & operating point\n\n")
        text.append(f"- primary cap (FPR target): `{primary_cap}`\n")
        text.append(f"- tpr_min_for_usable: `{tpr_min}`\n")
        text.append(f"- tau_pae: `{dataset_snapshot.get('tau_pae')}`\n")
        text.append(f"- tau_msa_depth: `{dataset_snapshot.get('tau_msa_depth')}`\n")
        text.append(f"- universe_mode: `{dataset_snapshot.get('universe_mode')}`\n\n")

        text.append("## Policy parameters\n\n")
        text.append(f"- allocation_policy: `{row.get('allocation_policy')}`\n")
        text.append(f"- ranking_base: `{row.get('ranking_base')}`\n")
        text.append(f"- alpha_used: `{row.get('alpha_used')}`\n")
        text.append(f"- K_used: `{row.get('K_used')}`\n\n")

        text.append("## Regime / event markers (holdout)\n\n")
        text.append("| marker | round |\n|---|---:|\n")
        text.append(f"| r_floor_pae | {int(row.get('r_floor_pae'))} |\n")
        text.append(f"| r_floor_msa | {int(row.get('r_floor_msa'))} |\n")
        text.append(f"| r_floor_max | {int(row.get('r_floor_max'))} |\n")
        text.append(f"| r_enter_usable_pae | {int(row.get('r_enter_usable_pae'))} |\n")
        text.append(f"| r_enter_usable_msa | {int(row.get('r_enter_usable_msa'))} |\n")
        text.append(f"| r_joint_usable | {int(row.get('r_joint_usable'))} |\n")
        text.append(f"| delta_lag | {int(row.get('delta_lag'))} |\n\n")

        text.append("## Final operating stats (holdout @ primary cap)\n\n")
        text.append("| metric | value |\n|---|---:|\n")
        text.append(f"| final_pae_tpr_at_cap | {float(row.get('final_pae_tpr_at_cap')):.6f} |\n")
        text.append(f"| final_msa_tpr_at_cap | {float(row.get('final_msa_tpr_at_cap')):.6f} |\n")
        text.append(f"| final_pae_fpr_floor_at_tpr_min | {float(row.get('final_pae_fpr_floor_at_tpr_min')):.6f} |\n")
        text.append(f"| final_msa_fpr_floor_at_tpr_min | {float(row.get('final_msa_fpr_floor_at_tpr_min')):.6f} |\n")
        text.append(f"| final_mae_c3_hat | {float(row.get('final_mae_c3_hat')):.6f} |\n\n")

        text.append("## Leakage / boundary audit\n\n")
        text.append(f"- leakage_pass: `{leak_pass}`\n")
        if leak_detail:
            text.append(f"- holdout_overlap_with_queries: `{leak_detail.get('holdout_overlap_with_queries')}`\n")
            text.append(f"- duplicate_queries: `{leak_detail.get('duplicate_queries')}`\n\n")

        text.append("## Where to audit the decision trace\n\n")
        text.append(f"- decision trace: `{decision_trace}` (filter by this policy)\n")
        text.append(f"- allocation trace: `{allocation_trace}` (filter by this policy)\n\n")

        if events is not None:
            text.append("## Raw event payload (for audit)\n\n")
            text.append("```json\n")
            text.append(json.dumps(events, ensure_ascii=False, indent=2))
            text.append("\n```\n")

        card_path.write_text("".join(text), encoding="utf-8")

        index_rows.append({
            "policy": policy,
            "r_joint_usable": int(row.get("r_joint_usable")),
            "delta_lag": int(row.get("delta_lag")),
            "leakage_pass": bool(leak_pass),
            "card_path": f"policy_cards/{policy}.md",
        })

    # Index file
    idx = pd.DataFrame(index_rows).sort_values(by=["r_joint_usable", "delta_lag", "policy"])
    idx_path = run_dir / "policy_cards_index.md"
    lines = []
    lines.append("# Policy cards index\n\n")
    lines.append("| policy | r_joint_usable | delta_lag | leakage_pass | card |\n")
    lines.append("|---|---:|---:|---|---|\n")
    for _, r in idx.iterrows():
        policy = r["policy"]
        lines.append(f"| `{policy}` | {int(r['r_joint_usable'])} | {int(r['delta_lag'])} | {bool(r['leakage_pass'])} | [{policy}]({r['card_path']}) |\n")
    idx_path.write_text("".join(lines), encoding="utf-8")
