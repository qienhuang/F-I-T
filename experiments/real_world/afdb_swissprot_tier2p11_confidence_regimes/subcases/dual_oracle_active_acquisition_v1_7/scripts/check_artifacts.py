from __future__ import annotations
import argparse
import json
from pathlib import Path

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
    ap.add_argument("--run_dir", required=True, help="Path to out/<run_id> directory")
    args = ap.parse_args()

    rd = Path(args.run_dir)
    if not rd.exists():
        raise SystemExit(f"run_dir does not exist: {rd}")

    missing = []
    for f in REQUIRED_FILES:
        if not (rd / f).exists():
            missing.append(f)
    if not (rd / "policy_cards").exists():
        missing.append("policy_cards/")

    if missing:
        raise SystemExit("Missing required artifacts:\n" + "\n".join(f"- {m}" for m in missing))

    # leakage audit must pass
    leak = json.loads((rd / "leakage_audit.json").read_text(encoding="utf-8"))
    if not leak.get("overall_pass", False):
        raise SystemExit("Leakage audit failed (overall_pass=false). Refuse to interpret this run.")

    ev = json.loads((rd / "event_summary.json").read_text(encoding="utf-8"))

    # Δ-lag nonnegativity check (if present)
    bad = []
    for ps, e in (ev.get("events_by_policy", {}) or {}).items():
        dl = (e.get("delta_lag") or {}).get("delta_lag", None)
        if dl is not None and int(dl) < 0:
            bad.append(ps)
    if bad:
        raise SystemExit("Negative Δ-lag detected (audit failure) for:\n" + "\n".join(f"- {ps}" for ps in bad))

    # E_covjump_joint must not occur before joint usable (if found)
    bad_cov = []
    for ps, e in (ev.get("events_by_policy", {}) or {}).items():
        cj = (e.get("E_covjump_joint") or {})
        ju = (e.get("E_joint_usable") or {})
        if bool(cj.get("found", False)):
            rc = cj.get("round_index", None)
            rj = ju.get("round_index", None)
            if rc is not None and rj is not None and int(rc) < int(rj):
                bad_cov.append(ps)
    if bad_cov:
        raise SystemExit("E_covjump_joint occurs before joint usable (audit failure) for:\n" + "\n".join(f"- {ps}" for ps in bad_cov))

    # policy card assets manifest should include the new cost-based joint-coverage plot
    am = json.loads((rd / "policy_cards" / "assets_manifest.json").read_text(encoding="utf-8"))
    files = [f.get("path", "") for f in (am.get("files", []) or [])]
    has_joint_cost = any(str(p).endswith("_joint_cov_cost.png") for p in files)
    if not has_joint_cost:
        raise SystemExit("Missing *_joint_cov_cost.png in policy_cards/assets_manifest.json (audit failure).")

    print("OK: artifacts present + leakage_audit pass + Δ-lag audit pass + covjump audit pass + cost-asset audit pass.")

if __name__ == "__main__":
    main()
