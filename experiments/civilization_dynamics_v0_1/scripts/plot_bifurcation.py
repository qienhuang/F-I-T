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

from model import Params, n_flip, n_max_star


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results")
    ap.add_argument("--n_min", type=float, default=5.0)
    ap.add_argument("--n_max", type=float, default=80.0)
    ap.add_argument("--n_points", type=int, default=300)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    p0 = Params()
    Ns = np.linspace(args.n_min, args.n_max, args.n_points)

    gamma_star_k = (p0.a * p0.K - p0.b * Ns) / p0.c
    mu_at_coop = p0.d * p0.K - p0.P * gamma_star_k

    df = pd.DataFrame({"N": Ns, "mu_at_cooperation_eq": mu_at_coop})
    df.to_csv(out / "bifurcation_scan.csv", index=False)

    nflip = n_flip(p0)
    nmax = n_max_star(p0)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(Ns, mu_at_coop, color="tab:blue", lw=2, label="mu at cooperation equilibrium")
    ax.axhline(0.0, color="black", lw=1)
    ax.axvline(nflip, color="tab:red", ls="--", lw=1.2, label=f"N_flip={nflip:.2f}")
    if np.isfinite(nmax):
        ax.axvline(nmax, color="tab:green", ls=":", lw=1.2, label=f"N_max*={nmax:.2f}")
    ax.set_xlabel("N (system scale)")
    ax.set_ylabel("mu")
    ax.set_title("Transcritical threshold scan")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "bifurcation_mu_vs_N.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
