from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("PyYAML is required to run suite_report.py. Install via: pip install pyyaml") from e


def _read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _safe_rel(from_dir: Path, target: Path) -> str:
    try:
        return str(target.relative_to(from_dir))
    except Exception:
        try:
            return str(target.resolve().relative_to(from_dir.resolve()))
        except Exception:
            return str(target)


def _pick_run_dir(subcase_dir: Path, run_id: str, roots: List[str]) -> Optional[Path]:
    for root in roots:
        cand = subcase_dir / root / run_id
        if cand.exists():
            return cand
    return None


def _extract_numeric_summary(d: Dict[str, Any], preferred_keys: List[str], max_fallback: int = 6) -> List[Tuple[str, float]]:
    out: List[Tuple[str, float]] = []
    for k in preferred_keys:
        v = d.get(k, None)
        if isinstance(v, (int, float)) and v == v:  # not NaN
            out.append((k, float(v)))
    if out:
        return out[:max_fallback]

    # fallback: first N numeric keys at top level
    for k, v in d.items():
        if isinstance(v, (int, float)) and v == v:
            out.append((k, float(v)))
        if len(out) >= max_fallback:
            break
    return out


def _render_kv(kv: List[Tuple[str, float]]) -> str:
    if not kv:
        return "—"
    return ", ".join([f"`{k}`={v:.4g}" for k, v in kv])


def _summarize_pae(run_dir: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"status": "FOUND"}
    em = run_dir / "eval_metrics.json"
    if em.exists():
        obj = _read_json(em)
        # common keys in this repo family
        kv = _extract_numeric_summary(
            obj,
            preferred_keys=["roc_auc", "pr_auc", "accuracy", "f1", "tpr_at_fpr", "fpr_at_tpr", "n_test"],
        )
        out["metrics_summary"] = _render_kv(kv)
    else:
        out["metrics_summary"] = "—"
    return out


def _summarize_msa(run_dir: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"status": "FOUND"}
    em = run_dir / "eval_metrics.json"
    if em.exists():
        obj = _read_json(em)
        # this subcase stores {"regression": ..., "monitorability": ...}
        mon = obj.get("monitorability", {}) if isinstance(obj, dict) else {}
        reg = obj.get("regression", {}) if isinstance(obj, dict) else {}

        kv_mon = _extract_numeric_summary(
            mon if isinstance(mon, dict) else {},
            preferred_keys=["roc_auc", "pr_auc", "fpr_at_tpr", "tpr_at_fpr", "n_test"],
        )
        kv_reg = _extract_numeric_summary(
            reg if isinstance(reg, dict) else {},
            preferred_keys=["mae", "rmse", "r2"],
        )
        out["metrics_summary"] = f"monitorability: {_render_kv(kv_mon)}; regression: {_render_kv(kv_reg)}"
    else:
        out["metrics_summary"] = "—"
    return out


def _summarize_dual(run_dir: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {"status": "FOUND"}

    gate = run_dir / "claims_gate_report.json"
    if gate.exists():
        g = _read_json(gate)
        out["gate_mode"] = g.get("mode", "—")
        out["gate_metric"] = g.get("gate_metric", "—")
    else:
        out["gate_mode"] = "—"
        out["gate_metric"] = "—"

    overlay = run_dir / "policy_cards" / "claims_overlay.json"
    if overlay.exists():
        ov = _read_json(overlay)
        # expects {policy: {...}} or {"by_policy":{...}} depending on implementation
        by_policy = ov.get("by_policy", ov) if isinstance(ov, dict) else {}
        counts: Dict[str, int] = {}
        strong_pols: List[str] = []
        for pol, rec in (by_policy.items() if isinstance(by_policy, dict) else []):
            if not isinstance(rec, dict):
                continue
            level = str(rec.get("claim_level", "unknown"))
            counts[level] = counts.get(level, 0) + 1
            if level == "strong":
                strong_pols.append(str(pol))
        out["claims_distribution"] = ", ".join([f"`{k}`={v}" for k, v in sorted(counts.items())]) if counts else "—"
        out["strong_policies"] = ", ".join(sorted(strong_pols)[:12]) if strong_pols else "—"
    else:
        out["claims_distribution"] = "—"
        out["strong_policies"] = "—"

    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite_dir", default=".", help="Path to suite_v3_0 directory")
    ap.add_argument("--out", default="SUITE_REPORT.md", help="Output markdown path (relative to suite_dir unless absolute)")
    ap.add_argument("--run_id", default="MAIN", help="Run ID to summarize (default: MAIN)")
    ap.add_argument("--roots", default="out_smoke,out", help="Comma-separated run roots to search in each subcase")
    args = ap.parse_args()

    suite_dir = Path(args.suite_dir).resolve()
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (suite_dir / out_path).resolve()

    roots = [r.strip() for r in str(args.roots).split(",") if r.strip()]
    prereg_path = suite_dir / "SUITE_PREREG.yaml"
    if not prereg_path.exists():
        raise SystemExit(f"Missing SUITE_PREREG.yaml at: {prereg_path}")

    suite_cfg = yaml.safe_load(prereg_path.read_text(encoding="utf-8")) or {}
    suite_meta = suite_cfg.get("suite", {}) if isinstance(suite_cfg, dict) else {}
    subcases = suite_cfg.get("subcases", []) if isinstance(suite_cfg, dict) else []
    if not isinstance(subcases, list) or not subcases:
        raise SystemExit("SUITE_PREREG.yaml missing `subcases` list.")

    now = datetime.utcnow().isoformat() + "Z"
    title = "SUITE_REPORT — AFDB Non‑LLM Small‑Models Suite (v3.2)"
    lines: List[str] = []
    lines.append(f"# {title}\n")
    lines.append(f"- Generated (UTC): `{now}`\n")
    lines.append(f"- Suite ID: `{suite_meta.get('suite_id', '—')}`\n")
    lines.append(f"- Pack version: `{suite_meta.get('pack_version', suite_meta.get('pack_version', 'v3.2'))}`\n")
    lines.append("\n")
    lines.append("## How to reproduce\n")
    lines.append("From `suite_v3_0/`:\n")
    lines.append("```bash\nmake smoke\nmake report\n```\n")
    lines.append("\n")

    # Summary table header
    lines.append("## Summary\n")
    lines.append("| Track | Subcase | Run dir | Status | Key metrics / gate |\n")
    lines.append("|---|---|---|---|---|\n")

    # Detailed sections collector
    details: List[str] = []
    details.append("## Details\n")

    for rec in subcases:
        if not isinstance(rec, dict):
            continue
        sid = str(rec.get("id", "unknown"))
        track = "—"
        # prefer per-subcase track; otherwise infer
        if "pae" in sid:
            track = "A"
        elif "msa" in sid:
            track = "B"
        elif "dual" in sid:
            track = "C"

        rel_path = str(rec.get("path", ""))
        subcase_dir = (suite_dir / rel_path).resolve()
        run_dir = _pick_run_dir(subcase_dir, args.run_id, roots)
        status = "MISSING"
        metrics_summary = "—"

        if run_dir is not None:
            status = "FOUND"
            if track == "A":
                s = _summarize_pae(run_dir)
                metrics_summary = s.get("metrics_summary", "—")
            elif track == "B":
                s = _summarize_msa(run_dir)
                metrics_summary = s.get("metrics_summary", "—")
            else:
                s = _summarize_dual(run_dir)
                # render as gate mode + claims dist
                gate_mode = s.get("gate_mode", "—")
                claims_dist = s.get("claims_distribution", "—")
                metrics_summary = f"`gate`={gate_mode}; {claims_dist}"

        # Summary table row
        run_dir_display = _safe_rel(suite_dir, run_dir) if run_dir is not None else "—"
        lines.append(f"| {track} | `{sid}` | `{run_dir_display}` | {status} | {metrics_summary} |\n")

        # Details
        details.append(f"### Track {track} — `{sid}`\n")
        details.append(f"- Subcase path: `{_safe_rel(suite_dir, subcase_dir)}`\n")
        if run_dir is None:
            details.append("- Run dir: — (not found; run `make smoke` first)\n")
            details.append("\n")
            continue

        details.append(f"- Run dir: `{_safe_rel(suite_dir, run_dir)}`\n")

        # Common artifacts
        key_files = [
            ("eval_report.md", run_dir / "eval_report.md"),
            ("eval_metrics.json", run_dir / "eval_metrics.json"),
            ("tradeoff_onepage.pdf", run_dir / "tradeoff_onepage.pdf"),
            ("run_manifest.json", run_dir / "run_manifest.json"),
        ]
        # Dual-oracle extras
        if track == "C":
            key_files.extend([
                ("Claims.md", run_dir / "Claims.md"),
                ("claims_gate_report.json", run_dir / "claims_gate_report.json"),
                ("policy_cards_index.md", run_dir / "policy_cards_index.md"),
                ("policy_cards/claims_overlay.json", run_dir / "policy_cards" / "claims_overlay.json"),
                ("frontier_onepage.pdf", run_dir / "frontier_onepage.pdf"),
            ])

        details.append("\n**Key artifacts**\n\n")
        for label, p in key_files:
            if p.exists():
                details.append(f"- {label}: `{_safe_rel(suite_dir, p)}`\n")
            else:
                details.append(f"- {label}: (missing)\n")

        # Track-specific metrics
        if track == "C":
            s = _summarize_dual(run_dir)
            details.append("\n**Claims & gates (quick view)**\n\n")
            details.append(f"- gate mode: `{s.get('gate_mode','—')}`\n")
            details.append(f"- gate metric: `{s.get('gate_metric','—')}`\n")
            details.append(f"- claims distribution: {s.get('claims_distribution','—')}\n")
            details.append(f"- strong policies (first 12): {s.get('strong_policies','—')}\n")
        else:
            if track == "A":
                s = _summarize_pae(run_dir)
            else:
                s = _summarize_msa(run_dir)
            details.append("\n**Metrics (quick view)**\n\n")
            details.append(f"- {s.get('metrics_summary','—')}\n")

        details.append("\n---\n\n")

    # Combine
    lines.append("\n")
    lines.extend(details)

    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"Suite report written: {out_path}")


if __name__ == "__main__":
    main()
