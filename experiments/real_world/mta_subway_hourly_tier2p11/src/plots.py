"""
Generate a compact 2x2 figure (pdf + png) for the MTA case.

The plot is an index of artifacts; interpretation remains EST-gated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml


def load_prereg(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot MTA tradeoff onepage")
    parser.add_argument("--prereg", default="EST_PREREG_v0.1_hourly.yaml", help="Preregistration YAML")
    parser.add_argument("--input", default="outputs/metrics_log.parquet", help="Input metrics parquet")
    parser.add_argument("--coherence", default="outputs/coherence_report.json", help="Coherence report json")
    parser.add_argument("--change-points", default="outputs/change_points.json", help="Change points json")
    parser.add_argument("--output", default="outputs/tradeoff_onepage.pdf", help="Output PDF")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)
    df = pd.read_parquet(args.input)
    df["t"] = pd.to_datetime(df["t"])
    coh = json.loads(Path(args.coherence).read_text(encoding="utf-8"))
    status = coh.get("status", "UNKNOWN")

    cp = {"points": []}
    cp_path = Path(args.change_points)
    if cp_path.exists():
        cp = json.loads(cp_path.read_text(encoding="utf-8"))
    points = cp.get("points", [])

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)

    ax = axes[0, 0]
    ax.plot(df["t"], df["I_entropy_station"], lw=1)
    ax.set_title("(A) Information estimator")
    ax.set_ylabel("I_entropy_station")

    ax = axes[0, 1]
    ax.plot(df["t"], df["C_load"], lw=1, label="C_load")
    ax.plot(df["t"], df["C_concentration"], lw=1, label="C_concentration")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"(B) Constraint family (coherence={status})")

    ax = axes[1, 0]
    ax.plot(df["t"], df["R_ic"], lw=1, label="R=I/C")
    ax2 = ax.twinx()
    ax2.plot(df["t"], df["dR_ic"], lw=0.8, alpha=0.6, color="tab:red", label="dR")
    ax.set_title("(C) I/C ratio + derivative (P11 core; gated)")
    ax.set_ylabel("R_ic")
    ax2.set_ylabel("dR_ic")

    ax = axes[1, 1]
    ax.scatter(df["C_load"], df["I_entropy_station"], s=3, alpha=0.25)
    ax.set_title("(D) Tradeoff space (diagnostic)")
    ax.set_xlabel("C_load")
    ax.set_ylabel("I_entropy_station")

    # Light change-point marks (cap at 25 to avoid clutter).
    for p in points[:25]:
        try:
            t = pd.Timestamp(p["t"])
        except Exception:
            continue
        axes[1, 0].axvline(t, color="tab:blue", lw=0.5, alpha=0.2)

    fig.suptitle(f"FIT P11 Trade-off Analysis: {prereg['meta']['case_id']} ({prereg['meta']['version']})", fontsize=12)

    out_pdf = Path(args.output)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    out_png = out_pdf.with_suffix(".png")
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
