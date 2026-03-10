from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model import Params, gamma_star


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results")
    ap.add_argument("--N", type=float, default=30.0)
    ap.add_argument("--nx", type=int, default=35)
    ap.add_argument("--nr", type=int, default=35)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    p = Params(N=args.N)

    x = np.linspace(0.0, 1.0, args.nx)
    R = np.linspace(0.0, p.K, args.nr)
    X, RR = np.meshgrid(x, R)

    G = np.vectorize(lambda r: gamma_star(float(r), p))(RR)
    MU = p.d * RR - p.P * G
    dX = X * (1.0 - X) * MU
    dR = p.r * RR * (1.0 - RR / p.K) * (RR / p.A - 1.0) - p.h * X * RR

    speed = np.sqrt(dX**2 + dR**2) + 1e-9
    dXn = dX / speed
    dRn = dR / speed

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.streamplot(X, RR, dXn, dRn, color=MU, cmap="coolwarm", density=1.1, linewidth=1)
    ax.axhline(p.A, color="tab:red", ls="--", lw=1.2, label="R=A")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, p.K)
    ax.set_xlabel("x (extraction fraction)")
    ax.set_ylabel("R (resource stock)")
    ax.set_title(f"Phase portrait (slow manifold gamma*=max((aR-bN)/c,0), N={p.N:.2f})")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(out / "phase_portrait.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
