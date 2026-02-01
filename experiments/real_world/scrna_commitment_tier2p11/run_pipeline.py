"""
Run the scRNA commitment Tier-2 (EST-gated) pipeline end-to-end.

This is a convenience wrapper around:
  - python -m src.clean
  - python -m src.estimators
  - python -m src.export_fail_windows
  - python -m src.regimes
  - python -m src.plots

The wrapper is intentionally deterministic and does not mutate the prereg in-place.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run scRNA commitment pipeline end-to-end")
    parser.add_argument("--prereg", default="EST_PREREG.yaml", help="Preregistration YAML")
    args = parser.parse_args()

    workdir = Path(__file__).resolve().parent
    prereg_path = (workdir / args.prereg).resolve()
    if not prereg_path.exists():
        raise SystemExit(f"Prereg not found: {prereg_path}")

    python = sys.executable

    _run([python, "-m", "src.clean", "--prereg", str(prereg_path)])
    _run([python, "-m", "src.estimators", "--prereg", str(prereg_path)])
    _run([python, "-m", "src.export_fail_windows", "--prereg", str(prereg_path)])
    _run([python, "-m", "src.regimes", "--prereg", str(prereg_path)])
    _run([python, "-m", "src.plots", "--prereg", str(prereg_path)])


if __name__ == "__main__":
    main()

