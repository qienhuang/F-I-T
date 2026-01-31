from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
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


def _plot_learning_curve_cost(
    out_png: Path,
    policy: str,
    pae_cost: List[float],
    pae_tpr: List[float],
    msa_cost: List[float],
    msa_tpr: List[float],
    cap: float,
) -> None:
    fig = plt.figure(figsize=(6.0, 3.6))
    ax = fig.add_subplot(111)

    if len(pae_cost) and len(pae_tpr):
        ax.plot(pae_cost, pae_tpr, marker="o", linewidth=1.5, label="PAE: TPR@cap (holdout)")
    if len(msa_cost) and len(msa_tpr):
        ax.plot(msa_cost, msa_tpr, marker="o", linewidth=1.5, label="MSA: TPR@cap (holdout)")

    ax.set_xlabel("Cumulative oracle cost (budget)")
    ax.set_ylabel("TPR at primary cap (holdout)")
    ax.set_title(f"Cost-aware learning curves @ cap={cap} — {policy}")
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def _plot_allocation_cost_share(
    out_png: Path,
    policy: str,
    pae_cost_share: List[float],
) -> None:
    fig = plt.figure(figsize=(6.0, 3.2))
    ax = fig.add_subplot(111)

    if len(pae_cost_share):
        x = np.arange(1, len(pae_cost_share) + 1)
        ax.plot(x, pae_cost_share, marker="o", linewidth=1.5)
    ax.set_xlabel("Acquisition round (r>=1)")
    ax.set_ylabel("PAE share of per-round cost")
    ax.set_title(f"Allocation dynamics (cost share) — {policy}")
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


def _plot_joint_cov_round(out_png: Path, policy: str, cov_joint: List[float], r_covjump: int | None) -> None:
    x = np.arange(len(cov_joint))
    y = np.array([float(v) for v in cov_joint], dtype=float)
    plt.figure(figsize=(6, 2.5))
    plt.plot(x, y, label="cov_joint (usable-at-cap)")
    if r_covjump is not None and 0 <= int(r_covjump) < len(cov_joint):
        plt.axvline(int(r_covjump), linestyle="--", label="E_covjump_joint")
    plt.ylim(0, 1)
    plt.xlabel("round")
    plt.ylabel("joint coverage")
    plt.title(f"{policy}: joint coverage timeline (by round)")
    plt.legend(fontsize=7)
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close()


def _plot_joint_cov_cost(out_png: Path, policy: str, cov_joint: List[float], total_cost: List[float], r_covjump: int | None) -> None:
    x = np.array([float(v) for v in total_cost], dtype=float)
    y = np.array([float(v) for v in cov_joint], dtype=float)
    if len(x) != len(y):
        # fall back: align by min length
        n = min(len(x), len(y))
        x = x[:n]
        y = y[:n]

    plt.figure(figsize=(6, 2.5))
    plt.plot(x, y, label="cov_joint (usable-at-cap)")
    if r_covjump is not None and 0 <= int(r_covjump) < len(x):
        plt.axvline(float(x[int(r_covjump)]), linestyle="--", label="E_covjump_joint (cost)")
    plt.ylim(0, 1)
    plt.xlabel("total cumulative cost")
    plt.ylabel("joint coverage")
    plt.title(f"{policy}: joint coverage timeline (by cost)")
    plt.legend(fontsize=7)
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=160)
    plt.close()


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
    pae_unit_cost: float,
    msa_unit_cost: float,
    jump_sensitivity: Optional[Dict[str, Any]] = None,
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
        joint_ser = (ser.get("joint") or {})

        # --- Cost curves (preferred) ---
        pae_cost = _safe_float_list(pae_ser.get("queried_cost", []))
        msa_cost = _safe_float_list(msa_ser.get("queried_cost", []))
        if not pae_cost:
            pae_q = [int(v) for v in pae_ser.get("queried_labels", [])]
            pae_cost = [float(v) * float(pae_unit_cost) for v in pae_q]
        if not msa_cost:
            msa_q = [int(v) for v in msa_ser.get("queried_labels", [])]
            msa_cost = [float(v) * float(msa_unit_cost) for v in msa_q]

        total_cost = _safe_float_list(joint_ser.get("total_cost", []))
        if not total_cost and pae_cost and msa_cost and len(pae_cost) == len(msa_cost):
            total_cost = [float(a) + float(b) for a, b in zip(pae_cost, msa_cost)]

        # --- Plot inputs ---
        pae_tpr = _safe_float_list(pae_ser.get("tpr_primary", []))
        msa_tpr = _safe_float_list(msa_ser.get("tpr_primary", []))

        # Cost share per round
        pae_cost_share = _safe_float_list(alloc_ser.get("pae_cost_share", []))
        if not pae_cost_share:
            # compute from cost deltas if possible
            if len(pae_cost) >= 2 and len(msa_cost) >= 2:
                dpae = np.diff(np.array(pae_cost, dtype=float))
                dmsa = np.diff(np.array(msa_cost, dtype=float))
                denom = dpae + dmsa
                share = np.where(denom > 0, dpae / denom, 0.5)
                pae_cost_share = [float(v) for v in share.tolist()]

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

        learning_png = assets_dir / f"{policy}_learning_cost.png"
        alloc_png = assets_dir / f"{policy}_allocation_cost.png"
        sweep_png = assets_dir / f"{policy}_tpr_vs_fpr.png"
        floor_png = assets_dir / f"{policy}_fpr_floor.png"
        joint_round_png = assets_dir / f"{policy}_joint_cov_round.png"
        joint_cost_png = assets_dir / f"{policy}_joint_cov_cost.png"

        _plot_learning_curve_cost(learning_png, policy, pae_cost, pae_tpr, msa_cost, msa_tpr, cap=primary_cap)
        _plot_allocation_cost_share(alloc_png, policy, pae_cost_share)
        _plot_tpr_vs_fpr(sweep_png, policy, fpr_targets=fpr_targets, pae_tprs=pae_tpr_sweep, msa_tprs=msa_tpr_sweep)
        _plot_fpr_floor(floor_png, policy, cap=primary_cap, tpr_min=tpr_min, pae_floor=pae_floor, msa_floor=msa_floor)

        r_covjump = None
        try:
            if row.get("covjump_joint_found", False):
                r_covjump = int(row.get("r_covjump_joint"))
        except Exception:
            r_covjump = None

        _plot_joint_cov_round(joint_round_png, policy, cov_joint=_safe_float_list(joint_ser.get("cov_joint_usable", [])), r_covjump=r_covjump)
        _plot_joint_cov_cost(joint_cost_png, policy, cov_joint=_safe_float_list(joint_ser.get("cov_joint_usable", [])), total_cost=total_cost, r_covjump=r_covjump)

        for p in [learning_png, alloc_png, sweep_png, floor_png, joint_round_png, joint_cost_png]:
            assets_manifest["files"].append({
                "path": f"policy_cards/assets/{p.name}",
                "sha256": _sha256_file(p),
                "bytes": int(p.stat().st_size),
            })

        # --- Card markdown ---
        jump_type = str(row.get("jump_type", "unknown"))
        jump_delay = row.get("jump_delay_rounds", None)

        text: List[str] = []
        text.append(f"# Policy Card — `{policy}`\n\n")

        text.append("## Boundary & operating point\n\n")
        text.append(f"- primary cap (FPR target): `{primary_cap}`\n")
        text.append(f"- tpr_min_for_usable: `{tpr_min}`\n")
        text.append(f"- tau_pae: `{dataset_snapshot.get('tau_pae')}`\n")
        text.append(f"- tau_msa_depth: `{dataset_snapshot.get('tau_msa_depth')}`\n")
        text.append(f"- universe_mode: `{dataset_snapshot.get('universe_mode')}`\n")
        text.append(f"- pae_unit_cost: `{pae_unit_cost}`\n")
        text.append(f"- msa_unit_cost: `{msa_unit_cost}`\n\n")

        text.append("## Policy parameters\n\n")
        text.append(f"- allocation_policy: `{row.get('allocation_policy')}`\n")
        text.append(f"- ranking_base: `{row.get('ranking_base')}`\n")
        text.append(f"- alpha_used: `{row.get('alpha_used')}`\n")
        text.append(f"- K_used: `{row.get('K_used')}`\n\n")

        text.append("## Regime / event markers (holdout)\n\n")
        text.append("| marker | value |\n|---|---:|\n")
        text.append(f"| r_floor_pae | {int(row.get('r_floor_pae'))} |\n")
        text.append(f"| r_floor_msa | {int(row.get('r_floor_msa'))} |\n")
        text.append(f"| r_floor_max | {int(row.get('r_floor_max'))} |\n")
        text.append(f"| r_joint_usable | {int(row.get('r_joint_usable'))} |\n")
        text.append(f"| r_covjump_joint | {int(row.get('r_covjump_joint'))} |\n")
        if jump_delay is not None and str(jump_delay) != "nan":
            text.append(f"| jump_delay_rounds | {int(jump_delay)} |\n")
        text.append(f"| jump_type | `{jump_type}` |\n")
        text.append(f"| delta_lag | {int(row.get('delta_lag'))} |\n\n")

        
        text.append("## Jump-type sensitivity (preregistered grid)\n\n")
        if jump_sensitivity is not None:
            grid = jump_sensitivity.get("availability_delay_grid", [])
            byp = (jump_sensitivity.get("by_policy", {}) or {}).get(policy, {}) or {}
            jmap = byp.get("jump_type_by_delay", {}) or {}
            text.append("| availability_delay_max_rounds | jump_type |\n|---:|---|\n")
            for d in grid:
                jt = str(jmap.get(str(d), "unknown"))
                text.append(f"| {int(d)} | `{jt}` |\n")
        else:
            text.append("_No sensitivity object provided._\n")
        text.append("\n")


        text.append("## Cost markers\n\n")
        text.append("| metric | value |\n|---|---:|\n")
        for k in ["cost_to_joint_usable", "cost_to_covjump_joint", "total_cost_final", "auc_cov_joint_per_cost"]:
            v = row.get(k, None)
            try:
                if v is None or str(v) == "nan":
                    continue
                text.append(f"| {k} | {float(v):.6f} |\n")
            except Exception:
                continue
        text.append("\n")

        text.append("## Final operating stats (holdout @ primary cap)\n\n")
        text.append("| metric | value |\n|---|---:|\n")
        text.append(f"| final_pae_tpr_at_cap | {float(row.get('final_pae_tpr_at_cap')):.6f} |\n")
        text.append(f"| final_msa_tpr_at_cap | {float(row.get('final_msa_tpr_at_cap')):.6f} |\n")
        text.append(f"| final_cov_joint_at_cap | {float(row.get('final_cov_joint_at_cap')):.6f} |\n")
        text.append(f"| final_pae_fpr_floor_at_tpr_min | {float(row.get('final_pae_fpr_floor_at_tpr_min')):.6f} |\n")
        text.append(f"| final_msa_fpr_floor_at_tpr_min | {float(row.get('final_msa_fpr_floor_at_tpr_min')):.6f} |\n")
        text.append(f"| final_mae_c3_hat | {float(row.get('final_mae_c3_hat')):.6f} |\n\n")

        text.append("## Evidence plots\n\n")
        text.append(f"![Cost-aware learning curve](assets/{learning_png.name})\n\n")
        text.append(f"![Allocation cost share](assets/{alloc_png.name})\n\n")
        text.append(f"![Holdout TPR vs FPR target](assets/{sweep_png.name})\n\n")
        text.append(f"![FPR-floor dynamics](assets/{floor_png.name})\n\n")
        text.append(f"![Joint coverage timeline (round)](assets/{joint_round_png.name})\n\n")
        text.append(f"![Joint coverage timeline (cost)](assets/{joint_cost_png.name})\n\n")

        text.append("## Leakage / boundary audit\n\n")
        text.append(f"- leakage_pass: `{bool(leak_pass)}`\n")
        if leak_detail:
            text.append(f"- holdout_overlap_with_queries: `{leak_detail.get('holdout_overlap_with_queries')}`\n")
            text.append(f"- duplicate_queries: `{leak_detail.get('duplicate_queries')}`\n\n")

        text.append("## Where to audit the decision trace\n\n")
        text.append(f"- decision trace: `{decision_trace}` (filter by this policy)\n")
        text.append(f"- allocation trace: `{allocation_trace}` (filter by this policy)\n\n")

        # Raw event payload (keep below plots)
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
            "r_covjump_joint": int(row.get("r_covjump_joint")),
            "jump_type": jump_type,
            "delta_lag": int(row.get("delta_lag")),
            "leakage_pass": bool(leak_pass),
            "card_path": f"policy_cards/{policy}.md",
        })

    # Index file
    idx = pd.DataFrame(index_rows).sort_values(by=["r_joint_usable", "delta_lag", "policy"])
    idx_path = run_dir / "policy_cards_index.md"
    lines: List[str] = []
    lines.append("# Policy cards index\n\n")
    lines.append("| policy | r_joint_usable | r_covjump_joint | jump_type | delta_lag | leakage_pass | card |\n")
    lines.append("|---|---:|---:|---|---:|---|---|\n")
    for _, r in idx.iterrows():
        policy = r["policy"]
        lines.append(
            f"| `{policy}` | {int(r['r_joint_usable'])} | {int(r.get('r_covjump_joint', -1))} | `{r.get('jump_type','')}` | {int(r['delta_lag'])} | {bool(r['leakage_pass'])} | [{policy}]({r['card_path']}) |\n"
        )
    idx_path.write_text("".join(lines), encoding="utf-8")

    (out_dir / "assets_manifest.json").write_text(
        json.dumps(assets_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
