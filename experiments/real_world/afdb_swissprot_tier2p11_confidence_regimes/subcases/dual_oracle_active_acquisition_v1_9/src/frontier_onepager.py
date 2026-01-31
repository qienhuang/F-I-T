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


def _envelope_value_at_cost(env_x: np.ndarray, env_y: np.ndarray, cost: float) -> float:
    if env_x is None or env_y is None or len(env_x) == 0 or len(env_y) == 0:
        return float("nan")
    c = float(cost)
    if not np.isfinite(c):
        return float("nan")
    idx = np.searchsorted(env_x, c, side="right") - 1
    if idx < 0:
        return float("nan")
    idx = min(idx, len(env_y) - 1)
    return float(env_y[idx])


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

    v1.9 updates:
      - baseline envelope (random-policy family) vs post-hoc envelope (all policies)
      - jump_type layering (marker shapes)
      - headroom/gain scalars exported to frontier_table.csv
    '''
    out_pdf = run_dir / "frontier_onepage.pdf"
    out_csv = run_dir / "frontier_table.csv"

    df = policy_df.copy()

    def _num(col: str) -> np.ndarray:
        v = pd.to_numeric(df[col], errors="coerce").values.astype(float)
        v = np.where(np.isfinite(v), v, np.nan)
        return v

    # Extract key columns (may contain NaNs)
    x_joint = _num("cost_to_joint_usable")
    x_jump = _num("cost_to_covjump_joint")
    y_cov = _num("final_cov_joint_at_cap")
    final_cost = _num("total_cost_final")

    # Baseline policy selector (audit-friendly and explicit)
    baseline_mask = np.zeros(len(df), dtype=bool)
    if "allocation_policy" in df.columns:
        baseline_mask |= (df["allocation_policy"].astype(str).str.lower() == "random").values
    baseline_mask |= df["policy"].astype(str).str.lower().str.contains("random").values
    df["is_baseline_random_family"] = baseline_mask

    # Pareto flags (cost vs final cov)
    pareto_joint = np.zeros(len(df), dtype=bool)
    mask = np.isfinite(x_joint) & np.isfinite(y_cov)
    if np.any(mask):
        pareto_joint[mask] = _pareto_flags_min_x_max_y(x_joint[mask], y_cov[mask])

    pareto_jump = np.zeros(len(df), dtype=bool)
    mask2 = np.isfinite(x_jump) & np.isfinite(y_cov)
    if np.any(mask2):
        pareto_jump[mask2] = _pareto_flags_min_x_max_y(x_jump[mask2], y_cov[mask2])

    df["pareto_cost_to_joint_vs_cov"] = pareto_joint
    df["pareto_cost_to_covjump_vs_cov"] = pareto_jump

    # Build curves
    curves_all: List[Tuple[np.ndarray, np.ndarray]] = []
    curves_base: List[Tuple[np.ndarray, np.ndarray]] = []

    for ps, obj in (cost_summary.get("by_policy") or {}).items():
        c = np.asarray(obj.get("total_cost_curve") or [], dtype=float)
        m = np.asarray(obj.get("cov_joint_curve") or [], dtype=float)
        if len(c) and len(m):
            n = min(len(c), len(m))
            c = c[:n]
            m = m[:n]
            curves_all.append((c, m))
            # baseline family?
            if any((df["policy"].astype(str) == str(ps)) & (df["is_baseline_random_family"] == True)):
                curves_base.append((c, m))

    env_x, env_y = _posthoc_envelope(curves_all)
    base_x, base_y = _posthoc_envelope(curves_base)

    # Headroom / gain scalars at each policy's final cost
    env_at_final = []
    base_at_final = []
    headroom = []
    gain_base = []
    for i in range(len(df)):
        c = float(final_cost[i]) if np.isfinite(final_cost[i]) else float("nan")
        e = _envelope_value_at_cost(env_x, env_y, c)
        b = _envelope_value_at_cost(base_x, base_y, c)
        env_at_final.append(e)
        base_at_final.append(b)
        hc = e - float(y_cov[i]) if (np.isfinite(e) and np.isfinite(y_cov[i])) else float("nan")
        gb = float(y_cov[i]) - b if (np.isfinite(b) and np.isfinite(y_cov[i])) else float("nan")
        headroom.append(hc)
        gain_base.append(gb)

    df["envelope_cov_at_final_cost"] = env_at_final
    df["baseline_env_cov_at_final_cost"] = base_at_final
    df["headroom_to_envelope_at_final_cost"] = headroom
    df["gain_over_baseline_env_at_final_cost"] = gain_base

    # Export frontier table
    df_out_cols = [
        "policy",
        "allocation_policy",
        "ranking_base",
        "jump_type",
        "is_baseline_random_family",
        "cost_to_joint_usable",
        "cost_to_covjump_joint",
        "total_cost_final",
        "final_cov_joint_at_cap",
        "auc_cov_joint_per_cost",
        "envelope_cov_at_final_cost",
        "baseline_env_cov_at_final_cost",
        "headroom_to_envelope_at_final_cost",
        "gain_over_baseline_env_at_final_cost",
        "pareto_cost_to_joint_vs_cov",
        "pareto_cost_to_covjump_vs_cov",
        "regret_cost_to_joint_usable",
        "regret_cost_to_covjump_joint",
    ]
    existing = [c for c in df_out_cols if c in df.columns]
    df[existing].to_csv(out_csv, index=False)

    # Marker mapping by jump_type (avoid explicit colors; use marker shapes only)
    jt = df.get("jump_type", pd.Series(["unknown"] * len(df))).astype(str).str.lower()
    marker_map = {
        "availability_driven": "o",
        "learning_driven": "^",
        "none": "s",
        "unknown": "x",
    }

    def _scatter_by_jump_type(ax, x: np.ndarray, y: np.ndarray, annotate_pareto_col: str | None = None, xlabel: str = "", ylabel: str = "", title: str = ""):
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_ylim(0.0, 1.0)
        ax.grid(True, alpha=0.25)

        for key, mk in marker_map.items():
            maskk = (jt.values == key) & np.isfinite(x) & np.isfinite(y)
            if np.any(maskk):
                ax.scatter(x[maskk], y[maskk], marker=mk, alpha=0.8, label=key)

        if annotate_pareto_col is not None and annotate_pareto_col in df.columns:
            for i, row in df.iterrows():
                if bool(row.get(annotate_pareto_col, False)):
                    try:
                        ax.annotate(str(row["policy"]), (float(row[xlabel]), float(row[ylabel])), fontsize=7)
                    except Exception:
                        # fallback: try numeric columns directly
                        pass

        ax.legend(loc="lower right", fontsize=8)

    # --- Plot one page (4 panels) ---
    fig = plt.figure(figsize=(11, 8.5))
    gs = fig.add_gridspec(2, 2)

    # Panel A: cov_joint vs cost for all policies + baseline envelope + post-hoc envelope
    axA = fig.add_subplot(gs[0, 0])
    for c, m in curves_all:
        axA.plot(c, m, linewidth=1.0, alpha=0.55)
    if len(base_x) and len(base_y):
        axA.plot(base_x, base_y, linestyle=":", linewidth=2.0, label="baseline envelope (random family)")
    if len(env_x) and len(env_y):
        axA.plot(env_x, env_y, linestyle="--", linewidth=2.0, label="post-hoc envelope (policy family)")
    axA.set_xlabel("Total cumulative cost")
    axA.set_ylabel("cov_joint@cap (usable gate)")
    axA.set_title("Panel A: Joint coverage vs cost (envelopes)")
    axA.set_ylim(0.0, 1.0)
    axA.grid(True, alpha=0.25)
    axA.legend(loc="lower right", fontsize=8)

    # Panel B: cost_to_joint_usable vs final cov (layered)
    axB = fig.add_subplot(gs[0, 1])
    for key, mk in marker_map.items():
        maskk = (jt.values == key) & np.isfinite(x_joint) & np.isfinite(y_cov)
        if np.any(maskk):
            axB.scatter(x_joint[maskk], y_cov[maskk], marker=mk, alpha=0.8, label=key)
    # annotate pareto_joint points
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
    axB.legend(loc="lower right", fontsize=8)

    # Panel C: cost_to_covjump vs final cov (layered)
    axC = fig.add_subplot(gs[1, 0])
    for key, mk in marker_map.items():
        maskk = (jt.values == key) & np.isfinite(x_jump) & np.isfinite(y_cov)
        if np.any(maskk):
            axC.scatter(x_jump[maskk], y_cov[maskk], marker=mk, alpha=0.8, label=key)
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
    axC.legend(loc="lower right", fontsize=8)

    # Panel D: headroom vs gain (at final cost)
    axD = fig.add_subplot(gs[1, 1])
    ddf = df.copy()
    ddf["total_cost_final_num"] = pd.to_numeric(ddf["total_cost_final"], errors="coerce")
    ddf = ddf.sort_values(by=["total_cost_final_num", "policy"])
    x = np.arange(len(ddf))

    h = pd.to_numeric(ddf.get("headroom_to_envelope_at_final_cost", np.nan), errors="coerce").values
    g = pd.to_numeric(ddf.get("gain_over_baseline_env_at_final_cost", np.nan), errors="coerce").values

    axD.bar(x - 0.2, h, width=0.4, label="headroom_to_envelope@final_cost")
    axD.bar(x + 0.2, g, width=0.4, label="gain_over_baseline_env@final_cost")
    axD.set_xticks(x)
    axD.set_xticklabels([str(p) for p in ddf["policy"]], rotation=90, fontsize=7)
    axD.set_ylabel("Δ cov_joint")
    axD.set_title("Panel D: Headroom vs baseline gain (final cost)")
    axD.grid(True, alpha=0.25, axis="y")
    axD.legend(loc="upper right", fontsize=8)

    fig.suptitle(f"Dual-Oracle Active Acquisition — Frontier/Envelope/Baseline {title_suffix}".strip())
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
