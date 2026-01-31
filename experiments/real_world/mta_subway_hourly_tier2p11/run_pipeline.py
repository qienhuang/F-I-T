"""
Run the MTA Subway Hourly (Tier-2 / P11) pipeline end-to-end (CPU-friendly).

This is a convenience wrapper around:
  - python -m src.clean
  - python -m src.estimators
  - python -m src.export_fail_windows
  - python -m src.regimes
  - python -m src.plots

It is intentionally deterministic: it does not change the prereg in-place.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MTA Subway Hourly pipeline end-to-end")
    parser.add_argument("--prereg", default="EST_PREREG_v0.1_hourly.yaml", help="Preregistration YAML")
    parser.add_argument("--raw_glob", default=None, help="Override boundary.raw_glob (optional)")
    parser.add_argument("--max_files", type=int, default=None, help="Optional: limit number of raw files (clean step)")
    parser.add_argument("--out_root", default=None, help="Optional: output root folder (creates subfolders)")
    args = parser.parse_args()

    workdir = Path(__file__).resolve().parent
    prereg_path = (workdir / args.prereg).resolve()
    if not prereg_path.exists():
        raise SystemExit(f"Prereg not found: {prereg_path}")

    tmp_prereg_path: Path | None = None
    prereg_for_run = prereg_path
    if args.raw_glob:
        prereg = yaml.safe_load(prereg_path.read_text(encoding="utf-8"))
        prereg.setdefault("boundary", {})["raw_glob"] = args.raw_glob
        fd, tmp_name = tempfile.mkstemp(prefix="mta_prereg_", suffix=".yaml")
        os.close(fd)
        tmp_prereg_path = Path(tmp_name)
        tmp_prereg_path.write_text(yaml.safe_dump(prereg, sort_keys=False), encoding="utf-8")
        prereg_for_run = tmp_prereg_path

    try:
        if args.out_root:
            out_root = (workdir / args.out_root).resolve()
            cleaned = out_root / "data" / "cleaned" / "bucket_state.parquet"
            outputs = out_root / "outputs"
            metrics = outputs / "metrics_log.parquet"
            coherence = outputs / "coherence_report.json"
            change_points = outputs / "change_points.json"
            regime_report = outputs / "regime_report.md"
            fig = outputs / "tradeoff_onepage.pdf"
        else:
            cleaned = workdir / "data" / "cleaned" / "bucket_state.parquet"
            outputs = workdir / "outputs"
            metrics = outputs / "metrics_log.parquet"
            coherence = outputs / "coherence_report.json"
            change_points = outputs / "change_points.json"
            regime_report = outputs / "regime_report.md"
            fig = outputs / "tradeoff_onepage.pdf"

        cleaned.parent.mkdir(parents=True, exist_ok=True)
        outputs.mkdir(parents=True, exist_ok=True)

        python = sys.executable
        clean_cmd = [python, "-m", "src.clean", "--prereg", str(prereg_for_run), "--output", str(cleaned)]
        if args.max_files is not None:
            clean_cmd += ["--max_files", str(args.max_files)]
        _run(clean_cmd)

        _run([python, "-m", "src.estimators", "--prereg", str(prereg_for_run), "--input", str(cleaned), "--output", str(metrics)])
        _run([python, "-m", "src.export_fail_windows", "--coherence", str(coherence), "--output", str(outputs / "fail_windows.md")])
        _run([python, "-m", "src.regimes", "--prereg", str(prereg_for_run), "--input", str(metrics), "--coherence", str(coherence), "--output", str(regime_report)])
        _run([python, "-m", "src.plots", "--prereg", str(prereg_for_run), "--input", str(metrics), "--coherence", str(coherence), "--change-points", str(change_points), "--output", str(fig)])
    finally:
        if tmp_prereg_path and tmp_prereg_path.exists():
            try:
                tmp_prereg_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    main()
