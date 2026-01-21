from __future__ import annotations

import argparse
from pathlib import Path

from grokking.runner.train import train_one_run
from grokking.utils.config import load_yaml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--phase", choices=["explore", "eval"], default="explore")
    parser.add_argument("--limit", type=int, default=0, help="If >0, run only first N seeds")
    args = parser.parse_args()

    spec = load_yaml(args.spec)
    seeds = list(spec.get("seeds", {}).get(args.phase, []))
    if args.limit and args.limit > 0:
        seeds = seeds[: args.limit]
    if not seeds:
        raise SystemExit(f"No seeds found for phase={args.phase} in spec")

    out_dir = Path(args.out) / args.phase
    for seed in seeds:
        train_one_run(spec=spec, out_dir=out_dir, seed=int(seed))


if __name__ == "__main__":
    main()

