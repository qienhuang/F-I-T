from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model import Params, collapse_time, gamma_star, simulate


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n_grid_min", type=float, default=10.0)
    ap.add_argument("--n_grid_max", type=float, default=75.0)
    ap.add_argument("--n_grid_points", type=int, default=18)
    ap.add_argument("--trials_per_n", type=int, default=24)
    ap.add_argument("--t_max", type=float, default=400.0)
    ap.add_argument("--dt", type=float, default=0.2)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    Ns = np.linspace(args.n_grid_min, args.n_grid_max, args.n_grid_points)

    rows = []
    for N in Ns:
        p = Params(N=float(N))
        for trial in range(args.trials_per_n):
            x0 = float(rng.uniform(0.02, 0.18))
            R0 = float(rng.uniform(p.A + 0.10, p.K))
            g_star = gamma_star(R0, p)
            g0 = float(rng.uniform(0.6 * g_star, 1.1 * max(g_star, 0.05)))

            t, y = simulate((x0, R0, g0), p, t_max=args.t_max, dt=args.dt)
            tc = collapse_time(t, y, p.A)
            rows.append(
                {
                    "N": float(N),
                    "trial": trial,
                    "x0": x0,
                    "R0": R0,
                    "gamma0": g0,
                    "collapse_time": tc,
                    "collapsed": bool(np.isfinite(tc)),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(out / "collapse_time_scan.csv", index=False)

    agg = (
        df.assign(collapse_time_filled=df["collapse_time"].fillna(args.t_max))
        .groupby("N", as_index=False)
        .agg(
            collapse_rate=("collapsed", "mean"),
            median_time=("collapse_time_filled", "median"),
            p25_time=("collapse_time_filled", lambda s: float(np.percentile(s, 25))),
            p75_time=("collapse_time_filled", lambda s: float(np.percentile(s, 75))),
        )
    )
    agg.to_csv(out / "collapse_time_summary_by_N.csv", index=False)

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(agg["N"], agg["collapse_rate"], color="tab:red", lw=2, label="collapse rate")
    ax1.set_ylabel("collapse rate", color="tab:red")
    ax1.set_ylim(-0.02, 1.02)
    ax1.set_xlabel("N (system scale)")

    ax2 = ax1.twinx()
    ax2.plot(agg["N"], agg["median_time"], color="tab:blue", lw=2, label="median collapse time")
    ax2.fill_between(agg["N"], agg["p25_time"], agg["p75_time"], color="tab:blue", alpha=0.2)
    ax2.set_ylabel("collapse time (t units)", color="tab:blue")

    ax1.set_title("Collapse-time distribution scan across N")
    fig.tight_layout()
    fig.savefig(out / "collapse_time_scan.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
