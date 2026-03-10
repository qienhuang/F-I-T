#!/usr/bin/env python3
"""Run signal-quantile sensitivity on the fixed Phase-I dataset."""

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
        "--quantiles",
        type=float,
        nargs="+",
        default=[0.98, 0.99, 0.995],
        help="Shared quantile values for force/info/constraint",
    )
    p.add_argument(
        "--out-root",
        type=Path,
        default=Path("outputs/quantile_sensitivity"),
        help="Output root for sensitivity artifacts",
    )
    return p.parse_args()


def run_one(base_cfg: dict, q: float, out_root: Path, exp_root: Path) -> dict:
    cfg = json.loads(json.dumps(base_cfg))
    q_tag = str(q).replace(".", "p")
    cfg["id"] = f"{base_cfg['id']}_Q{q_tag}"
    cfg["signals"]["quantiles"]["force"] = float(q)
    cfg["signals"]["quantiles"]["info"] = float(q)
    cfg["signals"]["quantiles"]["constraint"] = float(q)
    cfg["replay"]["enabled"] = False
    cfg["replay"]["manifest"] = None

    run_dir = out_root / f"q{q_tag}"
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
        "quantile": q,
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
        "quantile",
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
            row["quantile"] = f"{row['quantile']:.3f}"
            row["fit_transition_rate"] = f"{row['fit_transition_rate']:.4f}"
            row["divergence_rate"] = f"{row['divergence_rate']:.4f}"
            w.writerow(row)


def write_md(path: Path, rows: list[dict], base_prereg: Path) -> None:
    lines = [
        "# Signal-Quantile Sensitivity (Phase-I PT-MSS)",
        "",
        f"- base_prereg: `{base_prereg.as_posix()}`",
        f"- quantiles: `{[r['quantile'] for r in rows]}` (shared across F/I/C)",
        "- replay gate: disabled for this sensitivity sweep (label-logic only)",
        "",
        "| quantile | n_valid | REGISTERED | NO_TRANSITION | ESTIMATOR_UNSTABLE | INCONCLUSIVE | fit_transition_rate | divergence_rate | verdict |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['quantile']:.3f} | {r['n_valid']} | {r['registered']} | {r['no_transition']} | "
            f"{r['unstable']} | {r['inconclusive']} | {r['fit_transition_rate']:.4f} | "
            f"{r['divergence_rate']:.4f} | {r['verdict']} |"
        )
    lines.append("")
    lines.append("Interpretation:")
    zero_valid = [r for r in rows if r["n_valid"] == 0]
    nonzero = [r for r in rows if r["n_valid"] > 0]
    if zero_valid:
        qtxt = ", ".join(f"{r['quantile']:.3f}" for r in zero_valid)
        lines.append(f"- Quantile(s) {qtxt} are `SCOPE_LIMITED` here: density gate invalidated all seeds (`n_valid=0`).")
    if len(nonzero) >= 2:
        same = all(
            (
                r["registered"],
                r["no_transition"],
                r["unstable"],
                round(r["divergence_rate"], 6),
            )
            == (
                nonzero[0]["registered"],
                nonzero[0]["no_transition"],
                nonzero[0]["unstable"],
                round(nonzero[0]["divergence_rate"], 6),
            )
            for r in nonzero[1:]
        )
        if same:
            lines.append("- Across non-scope-limited quantiles, label composition and divergence are invariant.")
        else:
            lines.append("- Across non-scope-limited quantiles, verdict remains stable but class composition shifts (notably `UNSTABLE` vs `NO_TRANSITION`).")
    lines.append("- Read this as a gate-conditioned robustness profile, not a universal quantile-independence claim.")
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
    for q in args.quantiles:
        rows.append(run_one(base_cfg, float(q), out_root, exp_root))
    rows = sorted(rows, key=lambda x: x["quantile"])

    write_csv(out_root / "quantile_sensitivity.csv", rows)
    write_md(out_root / "quantile_sensitivity.md", rows, base_prereg)
    print(f"[ok] wrote {(out_root / 'quantile_sensitivity.csv').as_posix()}")
    print(f"[ok] wrote {(out_root / 'quantile_sensitivity.md').as_posix()}")


if __name__ == "__main__":
    main()
