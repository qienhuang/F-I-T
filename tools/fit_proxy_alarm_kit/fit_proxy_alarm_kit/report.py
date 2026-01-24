from __future__ import annotations

from typing import Any, Dict, List


def render_eval_report(
    *,
    run_id: str,
    cfg: dict,
    dataset_snapshot: dict,
    gate_by_policy: Dict[str, dict],
    event_by_policy: Dict[str, dict],
    final_summary_by_policy: Dict[str, dict],
) -> str:
    lines: List[str] = []
    lines.append("# Eval report - FIT Proxy Alarm Kit\n\n")
    lines.append(f"- run_id: `{run_id}`\n")
    lines.append(f"- case_id: `{cfg.get('preregistration', {}).get('case_id', 'UNKNOWN')}`\n")
    lines.append(f"- id_field: `{cfg['data']['id_field']}`\n")
    lines.append(f"- label_field (oracle store): `{cfg['boundary']['label_field']}`\n")
    lines.append(f"- tau_label: `{cfg['boundary']['tau_label']}`\n")
    lines.append(f"- pos_rate_total: `{dataset_snapshot.get('pos_rate_total', 'NA')}`\n\n")

    lines.append("## Monitorability gate (primary operating point)\n\n")
    primary = float(cfg["monitorability"]["primary_fpr_target"])
    tol = float(cfg.get("evaluation", {}).get("fpr_tolerance", 0.0))
    lines.append(f"- primary_fpr_target: `{primary}` (tolerance `{tol}`)\n\n")

    for policy, g in gate_by_policy.items():
        lines.append(f"- {policy}: **{g['status']}** ({g['reason']})\n")
    lines.append("\n")

    lines.append("## Event (optional)\n\n")
    for policy, ev in event_by_policy.items():
        lines.append(f"- {policy}: found=`{ev['found']}` round=`{ev['round_index']}` reason=`{ev['reason']}`\n")
    lines.append("\n")

    lines.append("## Final round summary (holdout)\n\n")
    for policy, s in final_summary_by_policy.items():
        lines.append(f"### {policy}\n\n")
        lines.append(f"- roc_auc: `{s.get('roc_auc')}`\n")
        lines.append(f"- pr_auc: `{s.get('pr_auc')}`\n")
        lines.append(f"- primary_op: `{s.get('primary_op')}`\n\n")

    lines.append("## Interpretation rule\n\n")
    lines.append("- AUC is not sufficient for alarms; the primary criterion is FPR controllability at the locked operating point.\n")
    lines.append("- If a policy is labeled `INVALID_ALARM`, do not interpret its ranking metrics as deployable performance.\n")
    return "".join(lines)

