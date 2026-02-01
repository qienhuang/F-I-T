from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .prereg import load_prereg, prereg_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a one-page summary plot")
    parser.add_argument("--prereg", required=True, help="Preregistration YAML")
    args = parser.parse_args()

    workdir = Path(__file__).resolve().parents[1]
    prereg = load_prereg(Path(args.prereg).resolve())
    paths = prereg_paths(prereg, workdir)

    metrics = pd.read_parquet(paths.metrics_log_parquet)
    if metrics.empty:
        # Nothing to plot.
        return

    if paths.coherence_report_json.exists():
        coh = json.loads(paths.coherence_report_json.read_text(encoding="utf-8"))
        rho = coh.get("rho_across_windows", None)
        verdict = coh.get("verdict", "UNKNOWN")
    else:
        rho = None
        verdict = "UNKNOWN"

    t_mid = 0.5 * (metrics["t_min"].to_numpy(dtype=float) + metrics["t_max"].to_numpy(dtype=float))
    c1 = metrics["C_dim_collapse"].to_numpy(dtype=float)
    c2 = metrics["C_mixing"].to_numpy(dtype=float)

    fig = plt.figure(figsize=(10.5, 7.2), dpi=140)
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t_mid, c1, color="#2a6fbb", linewidth=1.5)
    ax1.set_title("(A) C_dim_collapse (higher = more constrained)", fontsize=10)
    axis_spec = prereg.get("windowing", {}).get("axis", "pseudotime")
    ax1.set_xlabel(f"axis ({axis_spec})")
    ax1.set_ylabel("1 / effective_dim")
    ax1.grid(True, alpha=0.25)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t_mid, c2, color="#d77b00", linewidth=1.5)
    ax2.set_title("(B) C_mixing (higher = less mixing)", fontsize=10)
    ax2.set_xlabel(f"axis ({axis_spec})")
    ax2.set_ylabel("1 - mixing_fraction")
    ax2.grid(True, alpha=0.25)

    ax3 = fig.add_subplot(gs[1, 0])
    ax3.scatter(c1, c2, s=18, alpha=0.75, color="#444444")
    ax3.set_title("(C) Tradeoff space (windowed points)", fontsize=10)
    ax3.set_xlabel("C_dim_collapse")
    ax3.set_ylabel("C_mixing")
    ax3.grid(True, alpha=0.25)

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")
    lines = [
        "scRNA commitment (Tier-2 / EST-gated)",
        "",
        f"dataset: {prereg.get('boundary', {}).get('dataset')}",
        f"windows: {int(len(metrics))}",
        "",
        f"coherence rho (across windows): {rho}",
        f"verdict: {verdict}",
        "",
        "Note: v0.1 uses a conservative global coherence gate.",
    ]
    ax4.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=9)

    fig.suptitle("FIT / EST One-page Summary: scRNA Commitment (v0.1)", fontsize=12, y=0.98)

    paths.tradeoff_onepage_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(paths.tradeoff_onepage_png, bbox_inches="tight")
    fig.savefig(paths.tradeoff_onepage_pdf, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
