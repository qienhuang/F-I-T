#!/usr/bin/env python3
"""Run PT-MSS window-radius sensitivity on the fixed Phase-I dataset."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-prereg", type=Path, required=True, help="Base prereg yaml path")
    p.add_argument(
        "--radii",
        type=int,
        nargs="+",
        default=[10, 20, 40, 80],
        help="Window radius values to test",
    )
    p.add_argument(
        "--out-root",
        type=Path,
        default=Path("outputs/window_radius_sensitivity"),
        help="Output root for sensitivity artifacts",
    )
    return p.parse_args()


def run_one(base_cfg: dict, radius: int, out_root: Path, exp_root: Path) -> dict:
    cfg = json.loads(json.dumps(base_cfg))
    cfg["id"] = f"{base_cfg['id']}_WR{radius}"
    cfg["ptmss"]["window_radius_steps"] = int(radius)
    cfg["replay"]["enabled"] = False
    cfg["replay"]["manifest"] = None

    run_dir = out_root / f"r{radius}"
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = run_dir / "EST_PREREG.yaml"
    cfg["outputs"]["out_dir"] = str(run_dir).replace("\\", "/")
    cfg["outputs"]["per_seed_json_dir"] = str((run_dir / "per_seed")).replace("\\", "/")
    cfg["outputs"]["summary_json"] = str((run_dir / "summary.json")).replace("\\", "/")
    cfg["outputs"]["diagnostics_csv"] = str((run_dir / "diagnostics.csv")).replace("\\", "/")
    cfg["outputs"]["report_md"] = str((run_dir / "report.md")).replace("\\", "/")
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")

    run_id = f"{cfg['id']}_SENS"
    cmd = [sys.executable, "src/run_pipeline.py", "--prereg", str(cfg_path), "--run_id", run_id]
    subprocess.run(cmd, cwd=exp_root, check=True)

    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    labels = summary.get("label_counts", {})
    return {
        "radius": radius,
        "run_id": summary.get("run_id"),
        "n_valid": int(summary.get("n_valid", 0)),
        "registered": int(labels.get("REGISTERED_TRANSITION", 0)),
        "no_transition": int(labels.get("NO_TRANSITION", 0)),
        "unstable": int(labels.get("ESTIMATOR_UNSTABLE", 0)),
        "inconclusive": int(labels.get("INCONCLUSIVE", 0)),
        "fit_transition_rate": float(summary.get("fit_transition_rate", 0.0)),
        "divergence_rate": float(summary.get("divergence_rate", 0.0)),
        "verdict": summary.get("verdict"),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "radius",
        "run_id",
        "n_valid",
        "registered",
        "no_transition",
        "unstable",
        "inconclusive",
        "fit_transition_rate",
        "divergence_rate",
        "verdict",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            row = dict(r)
            row["fit_transition_rate"] = f"{row['fit_transition_rate']:.4f}"
            row["divergence_rate"] = f"{row['divergence_rate']:.4f}"
            w.writerow(row)


def write_md(path: Path, rows: list[dict], base_prereg: Path) -> None:
    lines = [
        "# Window-Radius Sensitivity (Phase-I PT-MSS)",
        "",
        f"- base_prereg: `{base_prereg.as_posix()}`",
        f"- radii: `{[r['radius'] for r in rows]}`",
        "- replay gate: disabled for this sensitivity sweep (label-logic only)",
        "",
        "| radius | n_valid | REGISTERED | NO_TRANSITION | ESTIMATOR_UNSTABLE | INCONCLUSIVE | fit_transition_rate | divergence_rate | verdict |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['radius']} | {r['n_valid']} | {r['registered']} | {r['no_transition']} | "
            f"{r['unstable']} | {r['inconclusive']} | {r['fit_transition_rate']:.4f} | "
            f"{r['divergence_rate']:.4f} | {r['verdict']} |"
        )
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- Stable `REGISTERED` counts and divergence rates across radii indicate robust synchronous/asynchronous separation.")
    lines.append("- Large shifts suggest sensitivity to PT-MSS simultaneity assumptions.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    exp_root = Path(__file__).resolve().parents[1]
    base_prereg = args.base_prereg
    if not base_prereg.is_absolute():
        base_prereg = (exp_root / base_prereg).resolve()
    base_cfg = yaml.safe_load(base_prereg.read_text(encoding="utf-8"))

    out_root = args.out_root
    if not out_root.is_absolute():
        out_root = (exp_root / out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for radius in args.radii:
        rows.append(run_one(base_cfg, int(radius), out_root, exp_root))
    rows = sorted(rows, key=lambda x: x["radius"])

    write_csv(out_root / "window_radius_sensitivity.csv", rows)
    write_md(out_root / "window_radius_sensitivity.md", rows, base_prereg)
    print(f"[ok] wrote {(out_root / 'window_radius_sensitivity.csv').as_posix()}")
    print(f"[ok] wrote {(out_root / 'window_radius_sensitivity.md').as_posix()}")


if __name__ == "__main__":
    main()
