"""
Generate a tiny synthetic hourly ridership dataset for smoke testing.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic MTA hourly fixture")
    parser.add_argument("--out_dir", required=True, help="Output directory")
    parser.add_argument("--days", type=int, default=14, help="Number of days")
    parser.add_argument("--stations", type=int, default=25, help="Number of stations")
    parser.add_argument("--seed", type=int, default=1337, help="RNG seed")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    start = pd.Timestamp("2020-01-01 00:00:00")
    hours = args.days * 24
    ts = [start + pd.Timedelta(hours=i) for i in range(hours)]
    station_ids = [f"S{idx:03d}" for idx in range(args.stations)]

    rows = []
    for t in ts:
        base = 1000 + 250 * np.sin(2 * np.pi * (t.hour / 24.0))
        for sid in station_ids:
            w = float(rng.lognormal(mean=0.0, sigma=0.6))
            rid = max(0.0, base * w / args.stations + float(rng.normal(0, 5.0)))
            rows.append({"transit_timestamp": t.isoformat(), "station_complex_id": sid, "ridership": float(rid)})

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "subway_hourly_fixture.csv", index=False)
    print(f"Wrote fixture: {out_dir / 'subway_hourly_fixture.csv'} (rows={len(df)})")


if __name__ == "__main__":
    main()
