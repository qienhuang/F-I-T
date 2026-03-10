from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "results"
    py = sys.executable

    run([py, str(root / "scripts" / "simulate.py"), "--out", str(out), "--N", "30"])
    run([py, str(root / "scripts" / "plot_phase_portrait.py"), "--out", str(out), "--N", "30"])
    run([py, str(root / "scripts" / "plot_bifurcation.py"), "--out", str(out)])
    run(
        [
            py,
            str(root / "scripts" / "collapse_time_scan.py"),
            "--out",
            str(out),
            "--n_grid_points",
            "20",
            "--trials_per_n",
            "30",
        ]
    )


if __name__ == "__main__":
    main()

