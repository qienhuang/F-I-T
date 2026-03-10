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

from model import Params, mu, simulate


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results")
    ap.add_argument("--N", type=float, default=30.0)
    ap.add_argument("--x0", type=float, default=0.05)
    ap.add_argument("--R0", type=float, default=0.95)
    ap.add_argument("--g0", type=float, default=1.0)
    ap.add_argument("--t_max", type=float, default=400.0)
    ap.add_argument("--dt", type=float, default=0.1)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    p = Params(N=args.N)
    t, y = simulate((args.x0, args.R0, args.g0), p, t_max=args.t_max, dt=args.dt)

    m = np.array([mu(row[0], row[1], row[2], p) for row in y])
    df = pd.DataFrame(
        {
            "t": t,
            "x": y[:, 0],
            "R": y[:, 1],
            "gamma": y[:, 2],
            "mu": m,
        }
    )
    df.to_csv(out / "trajectory.csv", index=False)

    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax[0].plot(t, y[:, 0], label="x (extraction fraction)")
    ax[0].plot(t, y[:, 1], label="R (resource stock)")
    ax[0].plot(t, y[:, 2], label="gamma (governance)")
    ax[0].axhline(p.A, color="tab:red", ls="--", lw=1, label="A threshold")
    ax[0].legend(loc="best")
    ax[0].set_ylabel("state")
    ax[0].set_title(f"Civilization ODE trajectory (N={p.N:.2f})")

    ax[1].plot(t, m, color="tab:purple", label="mu=dR-Pgamma")
    ax[1].axhline(0.0, color="black", lw=1)
    ax[1].legend(loc="best")
    ax[1].set_ylabel("mu")
    ax[1].set_xlabel("time")
    fig.tight_layout()
    fig.savefig(out / "trajectory.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
