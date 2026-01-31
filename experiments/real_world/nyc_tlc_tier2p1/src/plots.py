"""
NYC TLC Visualization

Generates the one-page trade-off figure for P11 analysis.
Four normative panels as specified in case study v1.1.

Features:
- Change point vertical lines with annotations
- Coherence status in figure footnote
- Multiple constraint estimators support
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import yaml


def load_prereg(path: str) -> dict:
    """Load preregistration YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def create_tradeoff_figure(
    metrics: pd.DataFrame,
    change_points: list[dict],
    coherence: dict,
    prereg: dict,
    output_path: str,
):
    """
    Create the four-panel trade-off figure.

    Panels:
    (A) Information: I estimators over time
    (B) Constraints: C family over time with coherence indicator
    (C) Ratio + derivative: R(t) and dR/dt with change points
    (D) Trade-off scatter: C vs I, colored by time
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    dates = pd.to_datetime(metrics["date"])
    coherence_status = coherence.get("status", "UNKNOWN")

    # Handle new change_points format (may have nested structure)
    if isinstance(change_points, dict):
        cp_list = change_points.get("change_points", [])
    else:
        cp_list = change_points

    # Color scheme
    color_I = "#2E86AB"  # blue
    color_I2 = "#48A9A6"  # teal (for temporal entropy)
    color_C1 = "#A23B72"  # magenta
    color_C2 = "#F18F01"  # orange
    color_C3 = "#4A4238"  # brown (for concentration)
    color_R = "#C73E1D"  # red
    color_dR = "#3B1F2B"  # dark

    # ========================================================================
    # Panel (A): Information Estimators
    # ========================================================================
    ax_a = axes[0, 0]
    ax_a.plot(dates, metrics["I_entropy_pu"], color=color_I, linewidth=1.5, label="I_entropy_pu")

    # Plot temporal entropy if available
    if "I_temporal_entropy" in metrics.columns:
        # Scale for visual comparison
        i_temp = metrics["I_temporal_entropy"]
        i_temp_scaled = (i_temp - i_temp.min()) / (i_temp.max() - i_temp.min())
        i_pu_range = metrics["I_entropy_pu"].max() - metrics["I_entropy_pu"].min()
        i_temp_scaled = i_temp_scaled * i_pu_range + metrics["I_entropy_pu"].min()
        ax_a.plot(dates, i_temp_scaled, color=color_I2, linewidth=1.2, alpha=0.7, label="I_temporal (scaled)")

    ax_a.set_ylabel("Information (entropy)", fontsize=10)
    ax_a.set_title("(A) Information Estimators", fontsize=11, fontweight="bold")
    ax_a.legend(loc="upper right", fontsize=8)
    ax_a.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax_a.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax_a.xaxis.get_majorticklabels(), rotation=45, ha="right")
    ax_a.grid(True, alpha=0.3)

    # ========================================================================
    # Panel (B): Constraint Family
    # ========================================================================
    ax_b = axes[0, 1]

    # Primary: C_congestion
    ax_b.plot(dates, metrics["C_congestion"], color=color_C1, linewidth=1.5, label="C_congestion")
    c_cong_range = metrics["C_congestion"].max() - metrics["C_congestion"].min()

    # Secondary: C_scarcity or C_price_pressure (normalized for visual comparison)
    if "C_scarcity" in metrics.columns:
        c_scarcity = metrics["C_scarcity"]
        c_scarcity_norm = (c_scarcity - c_scarcity.min()) / (c_scarcity.max() - c_scarcity.min() + 1e-10)
        c_scarcity_scaled = c_scarcity_norm * c_cong_range + metrics["C_congestion"].min()
        ax_b.plot(dates, c_scarcity_scaled, color=color_C2, linewidth=1.2, alpha=0.7, label="C_scarcity (scaled)")

    if "C_price_pressure" in metrics.columns:
        c_price = metrics["C_price_pressure"]
        c_price_norm = (c_price - c_price.min()) / (c_price.max() - c_price.min() + 1e-10)
        c_price_scaled = c_price_norm * c_cong_range + metrics["C_congestion"].min()
        ax_b.plot(dates, c_price_scaled, color=color_C2, linewidth=1.2, alpha=0.7, label="C_price_pressure (scaled)")

    # Tertiary: C_concentration if available
    if "C_concentration" in metrics.columns:
        c_conc = metrics["C_concentration"]
        c_conc_norm = (c_conc - c_conc.min()) / (c_conc.max() - c_conc.min() + 1e-10)
        c_conc_scaled = c_conc_norm * c_cong_range + metrics["C_congestion"].min()
        ax_b.plot(dates, c_conc_scaled, color=color_C3, linewidth=1.2, alpha=0.6, label="C_concentration (scaled)")

    ax_b.set_ylabel("Constraint proxies", fontsize=10)
    ax_b.set_title("(B) Constraint Family", fontsize=11, fontweight="bold")
    ax_b.legend(loc="upper right", fontsize=8)
    ax_b.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax_b.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax_b.xaxis.get_majorticklabels(), rotation=45, ha="right")
    ax_b.grid(True, alpha=0.3)

    # Coherence indicator on panel
    if coherence_status == "OK":
        coh_text = "Coherence: OK"
        coh_color = "green"
        coh_bg = "#e8f5e9"
    else:
        coh_text = f"Coherence: {coherence_status}"
        coh_color = "red"
        coh_bg = "#ffebee"

    ax_b.text(
        0.02, 0.98, coh_text,
        transform=ax_b.transAxes,
        fontsize=9,
        verticalalignment="top",
        color=coh_color,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=coh_bg, edgecolor=coh_color, alpha=0.8),
    )

    # ========================================================================
    # Panel (C): Ratio and derivative (P11 core)
    # ========================================================================
    ax_c = axes[1, 0]
    ax_c2 = ax_c.twinx()

    # Plot R(t)
    ax_c.plot(dates, metrics["R_I_over_C"], color=color_R, linewidth=1.5, alpha=0.7, label="R = I/C")
    ax_c.set_ylabel("R = I/C", color=color_R, fontsize=10)
    ax_c.tick_params(axis="y", labelcolor=color_R)

    # Plot dR/dt
    ax_c2.plot(dates, metrics["dR_dt"], color=color_dR, linewidth=1.0, alpha=0.8, label="dR/dt")
    ax_c2.set_ylabel("dR/dt", color=color_dR, fontsize=10)
    ax_c2.tick_params(axis="y", labelcolor=color_dR)
    ax_c2.axhline(y=0, color="gray", linestyle="--", alpha=0.5)

    n_cp = len(cp_list)
    top_cps = sorted(cp_list, key=lambda x: abs(x.get("score", x.get("zscore", 0))), reverse=True)[:5]
    cp_lines = top_cps if n_cp > 20 else cp_list

    # Mark change points (limit lines to reduce clutter)
    for cp in cp_lines:
        cp_date = pd.to_datetime(cp["date"])
        direction = cp.get("direction", "")

        # Color based on direction
        line_color = "#C62828" if direction == "positive" else "#1565C0"

        ax_c.axvline(x=cp_date, color=line_color, linestyle="--", alpha=0.35, linewidth=1.0)

        if cp in top_cps:
            y_pos = 0.95 - (top_cps.index(cp) * 0.08)
            ax_c.annotate(
                f'{cp["date"][:10]}',
                xy=(cp_date, ax_c.get_ylim()[1]),
                xytext=(cp_date, ax_c.get_ylim()[1] * y_pos),
                fontsize=7,
                color=line_color,
                alpha=0.8,
                rotation=90,
                ha="right",
                va="top",
            )

    ax_c.set_title("(C) I/C Ratio + Derivative (P11 Core)", fontsize=11, fontweight="bold")
    ax_c.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax_c.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax_c.xaxis.get_majorticklabels(), rotation=45, ha="right")
    ax_c.grid(True, alpha=0.3)

    # Change point summary on panel
    n_pos = sum(1 for cp in cp_list if cp.get("direction") == "positive")
    n_neg = n_cp - n_pos

    cp_text = f"{n_cp} CPs ({n_pos}+/{n_neg}-)"
    if n_cp > 20:
        cp_text += "\n(showing top 5 only)"
    if coherence_status != "OK":
        cp_text += "\nNOT INTERPRETABLE"

    ax_c.text(
        0.02, 0.98, cp_text,
        transform=ax_c.transAxes,
        fontsize=9,
        verticalalignment="top",
        color="red" if coherence_status != "OK" else "black",
        fontweight="bold" if coherence_status != "OK" else "normal",
    )

    # ========================================================================
    # Panel (D): Trade-off scatter
    # ========================================================================
    ax_d = axes[1, 1]

    # Color by time (days since start)
    days = (dates - dates.min()).dt.days
    scatter = ax_d.scatter(
        metrics["C_congestion"],
        metrics["I_entropy_pu"],
        c=days,
        cmap="viridis",
        alpha=0.6,
        s=12,
    )

    # Mark change point locations on scatter
    for cp in cp_list[:10]:  # Top 10 only
        cp_date = pd.to_datetime(cp["date"])
        idx = (dates - cp_date).abs().idxmin()
        if idx in metrics.index:
            row = metrics.loc[idx]
            marker = "^" if cp.get("direction") == "positive" else "v"
            ax_d.scatter(
                row["C_congestion"],
                row["I_entropy_pu"],
                marker=marker,
                s=80,
                c="red",
                edgecolors="white",
                linewidths=1,
                zorder=10,
            )

    cbar = plt.colorbar(scatter, ax=ax_d)
    cbar.set_label("Days since start", fontsize=9)

    ax_d.set_xlabel("C_congestion", fontsize=10)
    ax_d.set_ylabel("I_entropy_pu", fontsize=10)
    ax_d.set_title("(D) Trade-off Space (CPs marked)", fontsize=11, fontweight="bold")
    ax_d.grid(True, alpha=0.3)

    # ========================================================================
    # Main title and footnote
    # ========================================================================
    case_id = prereg["meta"]["case_id"]
    proposition = prereg["meta"].get("proposition", "P11")

    fig.suptitle(
        f"FIT {proposition} Trade-off Analysis: {case_id}",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    # Coherence footnote
    coherence_pairs = coherence.get("pairs", [])
    pair_strs = []
    for p in coherence_pairs:
        if "rho" in p:
            pair_strs.append(f"{p['pair'][0]} vs {p['pair'][1]}: ρ={p['rho']:.2f}")

    footnote_lines = [
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Coherence: {coherence_status}" + (f" ({', '.join(pair_strs)})" if pair_strs else ""),
    ]

    if coherence_status != "OK":
        footnote_lines.append("⚠ ESTIMATOR_UNSTABLE: Change points NOT interpretable")

    fig.text(
        0.5, 0.01,
        " | ".join(footnote_lines),
        ha="center",
        fontsize=8,
        color="gray" if coherence_status == "OK" else "red",
        style="italic",
    )

    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Saved figure: {output_path}")

    # Also save PNG version
    png_path = output_path.with_suffix(".png")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    print(f"Saved PNG: {png_path}")

    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Generate TLC trade-off figure")
    parser.add_argument("--prereg", default="EST_PREREG.yaml", help="Preregistration file")
    parser.add_argument("--input", default="outputs/metrics_log.parquet", help="Metrics input")
    parser.add_argument("--coherence", default="outputs/coherence_report.json", help="Coherence report")
    parser.add_argument("--change-points", default="outputs/change_points.json", help="Change points")
    parser.add_argument("--output", default="outputs/tradeoff_onepage.pdf", help="Output figure")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)

    # Load data
    metrics = pd.read_parquet(args.input)
    print(f"Loaded {len(metrics)} days of metrics")

    with open(args.coherence) as f:
        coherence = json.load(f)

    with open(args.change_points) as f:
        change_points = json.load(f)

    # Create figure
    create_tradeoff_figure(
        metrics=metrics,
        change_points=change_points,
        coherence=coherence,
        prereg=prereg,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
