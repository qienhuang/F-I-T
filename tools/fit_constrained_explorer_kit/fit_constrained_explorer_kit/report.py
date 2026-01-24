from __future__ import annotations

import json
from typing import Any, Dict


def render_report(run_id: str, cfg: dict, best: dict, constraints: dict, summary: dict) -> str:
    lines = []
    lines.append("# Eval report - FIT Constrained Explorer Kit")
    lines.append("")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- case_id: `{cfg.get('preregistration', {}).get('case_id', 'UNKNOWN')}`")
    lines.append(f"- domain: `{cfg.get('domain', {}).get('name', 'UNKNOWN')}`")
    lines.append(f"- budget.oracle_evals_max: `{cfg.get('budget', {}).get('oracle_evals_max')}`")
    lines.append("")
    lines.append("## Constraints (declared)")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(constraints, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for k, v in summary.items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append("## Best feasible candidate")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(best, indent=2, ensure_ascii=False))
    lines.append("```")
    return "\n".join(lines) + "\n"

