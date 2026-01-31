from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import hashlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_float_list(x: Any) -> List[float]:
    try:
        return [float(v) for v in x]
    except Exception:
        return []


def _plot_learning_curve(
    out_png: Path,
    policy: str,
    pae_q: List[int],
    pae_tpr: List[float],
    msa_q: List[int],
    msa_tpr: List[float],
    cap: float,
) -> None:
    fig = plt.figure(figsize=(6.0, 3.6))
    ax = fig.add_subplot(111)

    if len(pae_q) and len(pae_tpr):
        ax.plot(pae_q, pae_tpr, marker="o", linewidth=1.5, label="PAE: TPR@cap (holdout)")
    if len(msa_q) and len(msa_tpr):
        ax.plot(msa_q, msa_tpr, marker="o", linewidth=1.5, label="MSA: TPR@cap (holdout)")

    ax.set_xlabel("Queried labels (budget proxy)")
    ax.set_ylabel("TPR at primary cap (holdout)")
    ax.set_title(f"Learning curve @ cap={cap} — {policy}")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def _plot_allocation(
    out_png: Path,
    policy: str,
    pae_fraction: List[float],
) -> None:
    fig = plt.figure(figsize=(6.0, 3.2))
    ax = fig.add_subplot(111)

    if len(pae_fraction):
        x = np.arange(1, len(pae_fraction) + 1)
        ax.plot(x, pae_fraction, marker="o", linewidth=1.5)
    ax.set_xlabel("Acquisition round (r>=1)")
    ax.set_ylabel("PAE fraction of queries")
    ax.set_title(f"Allocation dynamics — {policy}")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def _plot_tpr_vs_fpr(
    out_png: Path,
    policy: str,
    fpr_targets: List[float],
    pae_tprs: List[float],
    msa_tprs: List[float],
) -> None:
    fig = plt.figure(figsize=(6.0, 3.2))
    ax = fig.add_subplot(111)

    x = np.array([float(v) for v in fpr_targets], dtype=float)
    if len(pae_tprs) == len(x):
        ax.plot(x, pae_tprs, marker="o", linewidth=1.5, label="PAE (holdout)")
    if len(msa_tprs) == len(x):
        ax.plot(x, msa_tprs, marker="o", linewidth=1.5, label="MSA (holdout)")

    ax.set_xlabel("FPR target (preregistered)")
    ax.set_ylabel("TPR (holdout)")
    ax.set_title(f"Holdout TPR vs FPR target — {policy}")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def _plot_fpr_floor(
    out_png: Path,
    policy: str,
    cap: float,
    tpr_min: float,
    pae_floor: List[float],
    msa_floor: List[float],
) -> None:
    fig = plt.figure(figsize=(6.0, 3.2))
    ax = fig.add_subplot(111)

    # Use round index (0..R-1), since both oracles share the same round timeline.
    x = np.arange(0, max(len(pae_floor), len(msa_floor)))

    if len(pae_floor):
        ax.plot(np.arange(len(pae_floor)), pae_floor, marker="o", linewidth=1.5, label="PAE: FPR floor @ TPR_min")
    if len(msa_floor):
        ax.plot(np.arange(len(msa_floor)), msa_floor, marker="o", linewidth=1.5, label="MSA: FPR floor @ TPR_min")

    ax.axhline(float(cap), linestyle="--", linewidth=1.2, label="Primary cap")
    ax.set_xlabel("Round index (r)")
    ax.set_ylabel(f"FPR floor at TPR_min={tpr_min} (holdout)")
    ax.set_title(f"FPR-floor dynamics — {policy}")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def write_policy_cards(
    run_dir: Path,
    dataset_snapshot: Dict[str, Any],
    boundary_snapshot: Dict[str, Any],
    policy_table: pd.DataFrame,
    leakage_audit: Dict[str, Any],
    series_by_policy: Dict[str, Any],
    primary_cap: float,
    tpr_min: float,
    fpr_targets: List[float],
) -> None:
    # Writes:
    #   - out/<run_id>/policy_cards/<policy>.md
    #   - out/<run_id>/policy_cards_index.md
    #   - out/<run_id>/policy_cards/assets/<policy>_*.png
    #   - out/<run_id>/policy_cards/assets_manifest.json
    out_dir = run_dir / "policy_cards"
    assets_dir = out_dir / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    index_rows: List[Dict[str, Any]] = []
    assets_manifest: Dict[str, Any] = {"files": []}

    for _, row in policy_table.iterrows():
        policy = str(row["policy"])
        card_path = out_dir / f"{policy}.md"

        leak_pass = bool(row.get("leakage_pass", False))
        leak_detail = (leakage_audit.get("by_policy", {}) or {}).get(policy, {})

        # Provide pointers to trace files for audit
        decision_trace = "decision_trace.csv"
        allocation_trace = "allocation_trace.csv"

        ser = (series_by_policy.get(policy) or {})
        pae_ser = (ser.get("pae") or {})
        msa_ser = (ser.get("msa_cls") or {})
        alloc_ser = (ser.get("alloc") or {})

        # --- Plot inputs ---
        pae_q = [int(v) for v in pae_ser.get("queried_labels", [])]
        msa_q = [int(v) for v in msa_ser.get("queried_labels", [])]
        pae_tpr = _safe_float_list(pae_ser.get("tpr_primary", []))
        msa_tpr = _safe_float_list(msa_ser.get("tpr_primary", []))
        pae_frac = _safe_float_list(alloc_ser.get("pae_fraction", []))

        pae_floor = _safe_float_list(pae_ser.get("fpr_floor_at_tpr_min", []))
        msa_floor = _safe_float_list(msa_ser.get("fpr_floor_at_tpr_min", []))

        # FPR sweep: use final round if available
        pae_tpr_sweep: List[float] = []
        msa_tpr_sweep: List[float] = []
        try:
            pae_tpr_sweep = _safe_float_list((pae_ser.get("tpr_holdout_by_fpr_target") or [])[-1])
            msa_tpr_sweep = _safe_float_list((msa_ser.get("tpr_holdout_by_fpr_target") or [])[-1])
        except Exception:
            pae_tpr_sweep = []
            msa_tpr_sweep = []

        learning_png = assets_dir / f"{policy}_learning.png"
        alloc_png = assets_dir / f"{policy}_allocation.png"
        sweep_png = assets_dir / f"{policy}_tpr_vs_fpr.png"
        floor_png = assets_dir / f"{policy}_fpr_floor.png"

        _plot_learning_curve(learning_png, policy, pae_q, pae_tpr, msa_q, msa_tpr, cap=primary_cap)
        _plot_allocation(alloc_png, policy, pae_frac)
        _plot_tpr_vs_fpr(sweep_png, policy, fpr_targets=fpr_targets, pae_tprs=pae_tpr_sweep, msa_tprs=msa_tpr_sweep)
        _plot_fpr_floor(floor_png, policy, cap=primary_cap, tpr_min=tpr_min, pae_floor=pae_floor, msa_floor=msa_floor)

        for p in [learning_png, alloc_png, sweep_png, floor_png]:
            assets_manifest["files"].append({
                "path": f"policy_cards/assets/{p.name}",
                "sha256": _sha256_file(p),
                "bytes": int(p.stat().st_size),
            })

        # --- Card markdown ---
        text: List[str] = []
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

        text.append("## Evidence plots\n\n")
        text.append(f"![Learning curve](assets/{learning_png.name})\n\n")
        text.append(f"![Allocation dynamics](assets/{alloc_png.name})\n\n")
        text.append(f"![Holdout TPR vs FPR target](assets/{sweep_png.name})\n\n")
        text.append(f"![FPR-floor dynamics](assets/{floor_png.name})\n\n")

        text.append("## Leakage / boundary audit\n\n")
        text.append(f"- leakage_pass: `{leak_pass}`\n")
        if leak_detail:
            text.append(f"- holdout_overlap_with_queries: `{leak_detail.get('holdout_overlap_with_queries')}`\n")
            text.append(f"- duplicate_queries: `{leak_detail.get('duplicate_queries')}`\n\n")

        text.append("## Where to audit the decision trace\n\n")
        text.append(f"- decision trace: `{decision_trace}` (filter by this policy)\n")
        text.append(f"- allocation trace: `{allocation_trace}` (filter by this policy)\n\n")

        # Raw event payload is still useful, but keep it below plots
        events = None
        try:
            events = ser.get("events", None)
        except Exception:
            events = None
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
    lines: List[str] = []
    lines.append("# Policy cards index\n\n")
    lines.append("| policy | r_joint_usable | delta_lag | leakage_pass | card |\n")
    lines.append("|---|---:|---:|---|---|\n")
    for _, r in idx.iterrows():
        policy = r["policy"]
        lines.append(
            f"| `{policy}` | {int(r['r_joint_usable'])} | {int(r['delta_lag'])} | {bool(r['leakage_pass'])} | [{policy}]({r['card_path']}) |\n"
        )
    idx_path.write_text("".join(lines), encoding="utf-8")

    (out_dir / "assets_manifest.json").write_text(
        json.dumps(assets_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
