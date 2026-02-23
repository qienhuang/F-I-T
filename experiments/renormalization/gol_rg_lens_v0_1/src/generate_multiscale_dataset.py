from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from gol_core import SimConfig, run_seed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--seed_start", type=int, default=1000)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--grid", type=int, default=128)
    ap.add_argument("--burn_in", type=int, default=100)
    ap.add_argument("--measure_interval", type=int, default=10)
    ap.add_argument("--window", type=int, default=50)
    ap.add_argument("--scales", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument(
        "--schemes",
        nargs="+",
        default=["majority", "threshold_low", "threshold_high", "average"],
    )
    ap.add_argument("--out_csv", default="out/multiscale_scheme_audit.csv")
    ap.add_argument("--summary_json", default="out/run_summary.json")
    args = ap.parse_args()

    cfg = SimConfig(
        grid_size=args.grid,
        steps=args.steps,
        burn_in=args.burn_in,
        measure_interval=args.measure_interval,
        window=args.window,
        scales=args.scales,
    )

    rows = []
    for scheme in args.schemes:
        for i in range(args.seeds):
            seed = args.seed_start + i
            rows.extend(run_seed(seed=seed, cfg=cfg, scheme=scheme))

    df = pd.DataFrame(rows)
    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    summary = {
        "rows": int(len(df)),
        "schemes": args.schemes,
        "estimators": ["C_frozen", "C_activity", "H"],
        "config": {
            "grid_size": cfg.grid_size,
            "steps": cfg.steps,
            "burn_in": cfg.burn_in,
            "measure_interval": cfg.measure_interval,
            "window": cfg.window,
            "scales": cfg.scales,
            "seeds": args.seeds,
            "seed_start": args.seed_start,
        },
        "out_csv": str(out_csv.as_posix()),
    }

    summary_json = Path(args.summary_json)
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote {len(df)} rows to {out_csv}")
    print(f"Wrote summary to {summary_json}")


if __name__ == "__main__":
    main()
