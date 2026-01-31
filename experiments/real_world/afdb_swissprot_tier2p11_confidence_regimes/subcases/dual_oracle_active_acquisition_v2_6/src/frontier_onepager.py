from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _pareto_flags_min_x_max_y(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    '''
    Pareto-optimal for: minimize x, maximize y.
    A point i is dominated if exists j with x_j <= x_i and y_j >= y_i and at least one strict.
    '''
    n = len(x)
    flags = np.ones(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if j == i:
                continue
            if (x[j] <= x[i]) and (y[j] >= y[i]) and ((x[j] < x[i]) or (y[j] > y[i])):
                flags[i] = False
                break
    return flags


def _posthoc_envelope(curves: List[Tuple[np.ndarray, np.ndarray]]) -> Tuple[np.ndarray, np.ndarray]:
    '''
    curves: list of (cost, metric) arrays, nondecreasing cost per curve.
    returns (grid_cost, env_metric) where env_metric(c) = max_i metric_i(cost<=c).
    '''
    if not curves:
        return np.array([]), np.array([])
    costs = [c for c, _ in curves if len(c)]
    if not costs:
        return np.array([]), np.array([])
    all_cost = np.unique(np.concatenate(costs))
    if len(all_cost) == 0:
        return np.array([]), np.array([])
    all_cost = np.sort(all_cost)

    env = []
    for cc in all_cost:
        best = -np.inf
        for c, m in curves:
            if len(c) == 0:
                continue
            idx = np.searchsorted(c, cc, side="right") - 1
            if idx >= 0:
                best = max(best, float(m[idx]))
        if best == -np.inf:
            best = np.nan
        env.append(best)
    return all_cost, np.asarray(env, dtype=float)


def plot_frontier_onepage(
    run_dir: Path,
    policy_df: pd.DataFrame,
    cost_summary: Dict[str, Any],
    title_suffix: str = "",
) -> None:
    '''
    Writes:
      - frontier_onepage.pdf
      - frontier_table.csv
    '''
    out_pdf = run_dir / "frontier_onepage.pdf"
    out_csv = run_dir / "frontier_table.csv"

    df = policy_df.copy()

    def _finite(col: str) -> np.ndarray:
        v = pd.to_numeric(df[col], errors="coerce").values.astype(float)
        v = np.where(np.isfinite(v), v, np.nan)
        return v

    x_joint = _finite("cost_to_joint_usable")
    y_cov = _finite("final_cov_joint_at_cap")

    pareto_joint = np.zeros(len(df), dtype=bool)
    mask = np.isfinite(x_joint) & np.isfinite(y_cov)
    if np.any(mask):
        pareto_joint[mask] = _pareto_flags_min_x_max_y(x_joint[mask], y_cov[mask])

    x_jump = _finite("cost_to_covjump_joint")
    pareto_jump = np.zeros(len(df), dtype=bool)
    mask2 = np.isfinite(x_jump) & np.isfinite(y_cov)
    if np.any(mask2):
        pareto_jump[mask2] = _pareto_flags_min_x_max_y(x_jump[mask2], y_cov[mask2])

    df["pareto_cost_to_joint_vs_cov"] = pareto_joint
    df["pareto_cost_to_covjump_vs_cov"] = pareto_jump

    df_out_cols = [
        "policy",
        "jump_type",
        "cost_to_joint_usable",
        "cost_to_covjump_joint",
        "final_cov_joint_at_cap",
        "auc_cov_joint_per_cost",
        "pareto_cost_to_joint_vs_cov",
        "pareto_cost_to_covjump_vs_cov",
        "regret_cost_to_joint_usable",
        "regret_cost_to_covjump_joint",
    ]
    existing = [c for c in df_out_cols if c in df.columns]
    df[existing].to_csv(out_csv, index=False)

    curves: List[Tuple[np.ndarray, np.ndarray]] = []
    for ps, obj in (cost_summary.get("by_policy") or {}).items():
        c = np.asarray(obj.get("total_cost_curve") or [], dtype=float)
        m = np.asarray(obj.get("cov_joint_curve") or [], dtype=float)
        if len(c) and len(m):
            n = min(len(c), len(m))
            curves.append((c[:n], m[:n]))
    env_x, env_y = _posthoc_envelope(curves)

    fig = plt.figure(figsize=(11, 8.5))
    gs = fig.add_gridspec(2, 2)

    # Panel A: cov_joint vs cost for all policies + envelope
    axA = fig.add_subplot(gs[0, 0])
    for c, m in curves:
        axA.plot(c, m, linewidth=1.0, alpha=0.55)
    if len(env_x) and len(env_y):
        axA.plot(env_x, env_y, linestyle="--", linewidth=2.0, label="post-hoc envelope (hindsight reference)")
        axA.legend(loc="lower right", fontsize=8)
    axA.set_xlabel("Total cumulative cost")
    axA.set_ylabel("cov_joint@cap (usable gate)")
    axA.set_title("Panel A: Joint coverage vs cost (+ post-hoc envelope)")
    axA.set_ylim(0.0, 1.0)
    axA.grid(True, alpha=0.25)

    # Panel B: cost_to_joint_usable vs final cov
    axB = fig.add_subplot(gs[0, 1])
    axB.scatter(x_joint, y_cov, alpha=0.8)
    for i, row in df.iterrows():
        if bool(row.get("pareto_cost_to_joint_vs_cov", False)):
            try:
                axB.annotate(str(row["policy"]), (float(row["cost_to_joint_usable"]), float(row["final_cov_joint_at_cap"])), fontsize=7)
            except Exception:
                pass
    axB.set_xlabel("cost_to_joint_usable")
    axB.set_ylabel("final_cov_joint_at_cap")
    axB.set_title("Panel B: Frontier (cost_to_joint vs final cov)")
    axB.set_ylim(0.0, 1.0)
    axB.grid(True, alpha=0.25)

    # Panel C: cost_to_covjump vs final cov
    axC = fig.add_subplot(gs[1, 0])
    axC.scatter(x_jump, y_cov, alpha=0.8)
    for i, row in df.iterrows():
        if bool(row.get("pareto_cost_to_covjump_vs_cov", False)):
            try:
                axC.annotate(str(row["policy"]), (float(row["cost_to_covjump_joint"]), float(row["final_cov_joint_at_cap"])), fontsize=7)
            except Exception:
                pass
    axC.set_xlabel("cost_to_covjump_joint")
    axC.set_ylabel("final_cov_joint_at_cap")
    axC.set_title("Panel C: Frontier (cost_to_covjump vs final cov)")
    axC.set_ylim(0.0, 1.0)
    axC.grid(True, alpha=0.25)

    # Panel D: regret bars
    axD = fig.add_subplot(gs[1, 1])
    ddf = df.copy()
    ddf["cost_to_joint_usable_num"] = pd.to_numeric(ddf["cost_to_joint_usable"], errors="coerce")
    ddf = ddf.sort_values(by=["cost_to_joint_usable_num", "policy"])
    x = np.arange(len(ddf))
    r1 = pd.to_numeric(ddf.get("regret_cost_to_joint_usable", np.nan), errors="coerce").values
    r2 = pd.to_numeric(ddf.get("regret_cost_to_covjump_joint", np.nan), errors="coerce").values
    axD.bar(x - 0.2, r1, width=0.4, label="regret: cost_to_joint")
    axD.bar(x + 0.2, r2, width=0.4, label="regret: cost_to_covjump")
    axD.set_xticks(x)
    axD.set_xticklabels([str(p) for p in ddf["policy"]], rotation=90, fontsize=7)
    axD.set_ylabel("regret cost (vs best)")
    axD.set_title("Panel D: Cost regret (within policy family)")
    axD.grid(True, alpha=0.25, axis="y")
    axD.legend(loc="upper right", fontsize=8)

    fig.suptitle(f"Dual-Oracle Active Acquisition — Frontier/Envelope {title_suffix}".strip())
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
