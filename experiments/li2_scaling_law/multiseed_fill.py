#!/usr/bin/env python3
"""
Targeted multi-seed fill for beta confirmation.

Why:
  The dense M sweep so far is mostly single-seed. That makes r_crit noisy (0/1 crossing),
  which can distort beta estimates.

What:
  Run a small set of (M, ratio) points with multiple seeds, skipping existing JSONs.
  Designed to work with analyze_beta_transition.py (needs at least one below and multiple above r_crit).

Example:
  python multiseed_fill.py --spec "30:0.515,0.535,0.555,0.575;45:0.461,0.501,0.521,0.541" --seeds 42,123,456 --output_dir results/beta_multiseed
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


def _format_ratio(r: float) -> str:
    return f"{r:.3f}"


def _result_path(output_dir: Path, M: int, ratio: float, seed: int) -> Path:
    return output_dir / f"M{M}_ratio{_format_ratio(ratio)}_seed{seed}.json"


def _parse_spec(spec: str) -> dict[int, list[float]]:
    out: dict[int, list[float]] = {}
    parts = [p.strip() for p in spec.split(";") if p.strip()]
    for part in parts:
        if ":" not in part:
            raise SystemExit(f"Invalid --spec segment (missing ':'): {part}")
        m_str, ratios_str = part.split(":", 1)
        M = int(m_str.strip())
        ratios = [float(x.strip()) for x in ratios_str.split(",") if x.strip()]
        if not ratios:
            raise SystemExit(f"No ratios for M={M} in --spec")
        # de-dup + sort
        ratios = sorted({float(round(r, 3)) for r in ratios})
        out[M] = ratios
    if not out:
        raise SystemExit("Empty --spec")
    return out


@dataclass(frozen=True)
class RunCfg:
    M: int
    ratio: float
    seed: int


def _run_one(cfg: RunCfg, output_dir: Path, hidden_dim: int, activation: str, lr: float, weight_decay: float, epochs: int) -> bool:
    cmd = [
        sys.executable,
        "train.py",
        "--M",
        str(cfg.M),
        "--ratio",
        str(float(_format_ratio(cfg.ratio))),
        "--seed",
        str(cfg.seed),
        "--hidden_dim",
        str(hidden_dim),
        "--activation",
        str(activation),
        "--lr",
        str(lr),
        "--weight_decay",
        str(weight_decay),
        "--epochs",
        str(epochs),
        "--output_dir",
        str(output_dir),
    ]
    r = subprocess.run(cmd, capture_output=False)
    return r.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=str, required=True, help='Example: "30:0.515,0.535;45:0.461,0.501"')
    parser.add_argument("--seeds", type=str, default="42,123,456", help="Comma-separated seeds.")
    parser.add_argument("--output_dir", type=Path, default=Path("results/beta_multiseed"))
    parser.add_argument("--hidden_dim", type=int, default=2048)
    parser.add_argument("--activation", type=str, default="quadratic", choices=["quadratic", "relu", "gelu", "silu"])
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--weight_decay", type=float, default=0.001)
    parser.add_argument("--epochs", type=int, default=25000)
    args = parser.parse_args()

    plan = _parse_spec(args.spec)
    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    if not seeds:
        raise SystemExit("Empty --seeds")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    todo: list[RunCfg] = []
    skipped = 0
    for M in sorted(plan.keys()):
        for ratio in plan[M]:
            for seed in seeds:
                out_path = _result_path(args.output_dir, M, ratio, seed)
                if out_path.exists():
                    skipped += 1
                    continue
                todo.append(RunCfg(M=M, ratio=ratio, seed=seed))

    total = sum(len(plan[M]) for M in plan) * len(seeds)
    print("Multi-seed fill plan")
    print(f"- output_dir: {args.output_dir}")
    print(f"- Ms: {sorted(plan.keys())}")
    print(f"- seeds: {seeds}")
    for M in sorted(plan.keys()):
        print(f"  - M={M}: ratios={[_format_ratio(r) for r in plan[M]]}")
    print(f"- total runs: {total}")
    print(f"- skipped (already present): {skipped}")
    print(f"- pending: {len(todo)}")

    failed: list[RunCfg] = []
    for idx, cfg in enumerate(todo, start=1):
        print(f"\n[{idx}/{len(todo)}] M={cfg.M} ratio={cfg.ratio:.3f} seed={cfg.seed}")
        ok = _run_one(
            cfg,
            output_dir=args.output_dir,
            hidden_dim=args.hidden_dim,
            activation=args.activation,
            lr=args.lr,
            weight_decay=args.weight_decay,
            epochs=args.epochs,
        )
        if not ok:
            failed.append(cfg)

    print("\nDone.")
    if failed:
        print(f"Failed: {[(f.M, f.ratio, f.seed) for f in failed]}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

