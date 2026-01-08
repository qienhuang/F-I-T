#!/usr/bin/env python3
"""
Optional follow-up sweep to characterize time-to-grok above r_crit.

Why:
  The band_sweep used for n_crit verification typically has too few points above r_crit
  (often only 2), making "exponential vs power-law" non-identifiable.

What this does:
  - Estimates r_crit(M) from an existing results_dir via p_grok crossing 0.5
  - Builds a dense ratio grid above r_crit: r_crit + delta for delta in {0.01..0.10}
  - Runs train.py for each (M, ratio, seed), skipping already-existing JSON files

Run from: experiments/li2_scaling_law/
  # preview the plan
  python grok_speed_sweep.py --dry_run

  # actually run (can take hours on CPU)
  python grok_speed_sweep.py --run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def _parse_filename(stem: str) -> tuple[int, float, int] | None:
    parts = stem.split("_")
    if len(parts) < 3 or not parts[0].startswith("M") or not parts[1].startswith("ratio") or not parts[2].startswith("seed"):
        return None
    M = int(parts[0][1:])
    ratio = float(parts[1][5:])
    seed = int(parts[2][4:])
    return M, ratio, seed


def _load_results(results_dir: Path) -> dict[tuple[int, float], list[dict]]:
    out: dict[tuple[int, float], list[dict]] = defaultdict(list)
    for json_file in sorted(results_dir.glob("M*.json")):
        parsed = _parse_filename(json_file.stem)
        if parsed is None:
            continue
        M, ratio, seed = parsed
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        out[(M, ratio)].append(
            {
                "seed": seed,
                "grok_happened": bool(data.get("grok_happened", False)),
                "grok_epoch": data.get("grok_epoch", None),
            }
        )
    return out


def _grok_probability(runs: list[dict]) -> float:
    if not runs:
        return 0.0
    return sum(1 for r in runs if r["grok_happened"]) / len(runs)


def _estimate_rcrit_50(ratios: list[float], probs: list[float]) -> float | None:
    for i in range(len(ratios) - 1):
        p0, p1 = probs[i], probs[i + 1]
        r0, r1 = ratios[i], ratios[i + 1]
        if (p0 < 0.5 <= p1) or (p0 > 0.5 >= p1):
            if p1 == p0:
                return float((r0 + r1) / 2)
            t = (0.5 - p0) / (p1 - p0)
            return float(r0 + t * (r1 - r0))
    return None


def _format_ratio(r: float) -> str:
    # Keep filenames stable with 3 decimals (matches existing band_sweep naming).
    return f"{r:.3f}"


def _result_path(output_dir: Path, M: int, ratio: float, seed: int) -> Path:
    return output_dir / f"M{M}_ratio{_format_ratio(ratio)}_seed{seed}.json"


def _run_one(M: int, ratio: float, seed: int, output_dir: Path, epochs: int, weight_decay: float) -> bool:
    cmd = [
        sys.executable,
        "train.py",
        "--M",
        str(M),
        "--ratio",
        str(float(_format_ratio(ratio))),
        "--seed",
        str(seed),
        "--epochs",
        str(epochs),
        "--weight_decay",
        str(weight_decay),
        "--output_dir",
        str(output_dir),
    ]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline_results_dir", type=Path, default=Path("results/band_sweep"))
    parser.add_argument("--output_dir", type=Path, default=Path("results/grok_speed_sweep"))
    parser.add_argument("--Ms", type=str, default="23,41,59", help="Comma-separated M values.")
    parser.add_argument("--seeds", type=str, default="42,123,456", help="Comma-separated seeds.")
    parser.add_argument("--deltas", type=str, default="0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10")
    parser.add_argument("--epochs", type=int, default=25000)
    parser.add_argument("--weight_decay", type=float, default=0.001)
    parser.add_argument("--max_ratio", type=float, default=0.70)
    parser.add_argument("--dry_run", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()

    Ms = [int(x.strip()) for x in args.Ms.split(",") if x.strip()]
    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    deltas = [float(x.strip()) for x in args.deltas.split(",") if x.strip()]

    baseline = _load_results(args.baseline_results_dir)
    by_M: dict[int, dict[float, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for (M, ratio), runs in baseline.items():
        by_M[M][ratio].extend(runs)

    planned: list[tuple[int, float]] = []
    rcrit_map: dict[int, float] = {}
    for M in Ms:
        ratios = sorted(by_M[M].keys()) if M in by_M else []
        probs = [_grok_probability(by_M[M][r]) for r in ratios] if ratios else []
        rcrit = _estimate_rcrit_50(ratios, probs) if ratios else None
        if rcrit is None:
            print(f"M={M}: cannot estimate r_crit from {args.baseline_results_dir} (missing or no crossing).")
            continue
        rcrit_map[M] = float(rcrit)
        for d in deltas:
            r = float(rcrit) + float(d)
            if r >= float(args.max_ratio):
                continue
            planned.append((M, float(round(r, 3))))

    planned = sorted(set(planned))
    if not planned:
        print("No planned runs.")
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Grok speed sweep plan")
    print(f"- baseline_results_dir: {args.baseline_results_dir}")
    print(f"- output_dir: {args.output_dir}")
    print(f"- epochs: {args.epochs}, weight_decay: {args.weight_decay}")
    print(f"- seeds: {seeds}")
    print("- r_crit (estimated):")
    for M in sorted(rcrit_map.keys()):
        print(f"  - M={M}: r_crit~{rcrit_map[M]:.4f}")

    total = len(planned) * len(seeds)
    skipped = 0
    todo: list[tuple[int, float, int]] = []
    for M, ratio in planned:
        for seed in seeds:
            out_path = _result_path(args.output_dir, M, ratio, seed)
            if out_path.exists():
                skipped += 1
                continue
            todo.append((M, ratio, seed))

    print(f"- planned configs (unique M,ratio): {len(planned)}")
    print(f"- total runs (with seeds): {total}")
    print(f"- already present: {skipped}")
    print(f"- pending: {len(todo)}")

    if args.dry_run or not args.run:
        print("\n(dry run) First 10 pending runs:")
        for item in todo[:10]:
            M, ratio, seed = item
            print(f"  M={M} ratio={ratio:.3f} seed={seed}")
        if len(todo) > 10:
            print(f"  ... and {len(todo) - 10} more")
        print("\nTo run: add --run (and optionally omit --dry_run).")
        return

    # Run
    done = 0
    failed: list[tuple[int, float, int]] = []
    for (M, ratio, seed) in todo:
        done += 1
        print(f"\n[{done}/{len(todo)}] M={M} ratio={ratio:.3f} seed={seed}")
        ok = _run_one(M, ratio, seed, args.output_dir, epochs=args.epochs, weight_decay=args.weight_decay)
        if not ok:
            failed.append((M, ratio, seed))

    print("\nDone.")
    if failed:
        print(f"Failed: {failed}")
    else:
        print("All runs completed successfully.")


if __name__ == "__main__":
    main()
