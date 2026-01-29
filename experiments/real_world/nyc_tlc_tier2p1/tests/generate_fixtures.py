"""
Generate sample parquet fixtures for testing.

Creates small parquet files that mimic TLC data structure.

Two modes:
- default: single-day fixtures (small; committed to repo; schema tests)
- multi-day: spread timestamps across N days (lets coherence gate run)
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _random_datetimes(
    n_rows: int,
    *,
    start: pd.Timestamp,
    n_days: int,
    rng: np.random.Generator,
) -> pd.Series:
    """Sample datetimes uniformly across [start, start + n_days)."""
    day_offsets = rng.integers(0, max(1, int(n_days)), size=n_rows)
    minute_offsets = rng.integers(0, 60 * 24, size=n_rows)
    return start + pd.to_timedelta(day_offsets, unit="D") + pd.to_timedelta(minute_offsets, unit="m")


def generate_yellow_sample(
    n_rows: int = 1000,
    *,
    seed: int = 42,
    start: str = "2023-01-15",
    n_days: int = 1,
) -> pd.DataFrame:
    """Generate sample yellow taxi data."""
    rng = np.random.default_rng(seed)
    start_ts = pd.Timestamp(f"{start} 00:00:00")

    pickup = _random_datetimes(n_rows, start=start_ts, n_days=n_days, rng=rng)
    duration_min = rng.integers(3, 60, size=n_rows)
    dropoff = pickup + pd.to_timedelta(duration_min, unit="m")

    return pd.DataFrame({
        "VendorID": rng.integers(1, 3, size=n_rows),
        "tpep_pickup_datetime": pickup,
        "tpep_dropoff_datetime": dropoff,
        "passenger_count": rng.integers(1, 6, size=n_rows),
        "trip_distance": np.abs(rng.normal(3.0, 2.5, size=n_rows)),
        "RatecodeID": rng.integers(1, 7, size=n_rows),
        "store_and_fwd_flag": rng.choice(["Y", "N"], size=n_rows),
        "PULocationID": rng.integers(1, 263, size=n_rows),
        "DOLocationID": rng.integers(1, 263, size=n_rows),
        "payment_type": rng.integers(1, 5, size=n_rows),
        "fare_amount": np.abs(rng.normal(15.0, 10.0, size=n_rows)),
        "extra": rng.choice([0.0, 0.5, 1.0, 2.5], size=n_rows),
        "mta_tax": [0.5] * n_rows,
        "tip_amount": np.abs(rng.normal(2.0, 2.0, size=n_rows)),
        "tolls_amount": rng.choice([0.0, 0.0, 0.0, 6.55, 12.50], size=n_rows),
        "improvement_surcharge": [0.3] * n_rows,
        "total_amount": np.abs(rng.normal(20.0, 12.0, size=n_rows)),
        "congestion_surcharge": rng.choice([0.0, 2.5], size=n_rows),
        "airport_fee": rng.choice([0.0, 1.25], size=n_rows),
    })


def generate_green_sample(
    n_rows: int = 1000,
    *,
    seed: int = 43,
    start: str = "2023-01-15",
    n_days: int = 1,
) -> pd.DataFrame:
    """Generate sample green taxi data."""
    rng = np.random.default_rng(seed)
    start_ts = pd.Timestamp(f"{start} 00:00:00")

    pickup = _random_datetimes(n_rows, start=start_ts, n_days=n_days, rng=rng)
    duration_min = rng.integers(3, 60, size=n_rows)
    dropoff = pickup + pd.to_timedelta(duration_min, unit="m")

    return pd.DataFrame({
        "VendorID": rng.integers(1, 3, size=n_rows),
        "lpep_pickup_datetime": pickup,
        "lpep_dropoff_datetime": dropoff,
        "store_and_fwd_flag": rng.choice(["Y", "N"], size=n_rows),
        "RatecodeID": rng.integers(1, 7, size=n_rows),
        "PULocationID": rng.integers(1, 263, size=n_rows),
        "DOLocationID": rng.integers(1, 263, size=n_rows),
        "passenger_count": rng.integers(1, 6, size=n_rows),
        "trip_distance": np.abs(rng.normal(3.5, 3.0, size=n_rows)),
        "fare_amount": np.abs(rng.normal(12.0, 8.0, size=n_rows)),
        "extra": rng.choice([0.0, 0.5, 1.0], size=n_rows),
        "mta_tax": [0.5] * n_rows,
        "tip_amount": np.abs(rng.normal(1.5, 1.5, size=n_rows)),
        "tolls_amount": rng.choice([0.0, 0.0, 0.0, 5.76], size=n_rows),
        "improvement_surcharge": [0.3] * n_rows,
        "total_amount": np.abs(rng.normal(16.0, 10.0, size=n_rows)),
        "payment_type": rng.integers(1, 5, size=n_rows),
        "trip_type": rng.integers(1, 3, size=n_rows),
        "congestion_surcharge": rng.choice([0.0, 2.5], size=n_rows),
    })


def generate_hvfhv_sample(
    n_rows: int = 1000,
    *,
    seed: int = 44,
    start: str = "2023-01-15",
    n_days: int = 1,
) -> pd.DataFrame:
    """Generate sample HVFHV (Uber/Lyft) data."""
    rng = np.random.default_rng(seed)
    start_ts = pd.Timestamp(f"{start} 00:00:00")

    request = _random_datetimes(n_rows, start=start_ts, n_days=n_days, rng=rng)
    on_scene = request + pd.to_timedelta(rng.integers(1, 10, size=n_rows), unit="m")
    pickup = on_scene + pd.to_timedelta(rng.integers(1, 10, size=n_rows), unit="m")
    dropoff = pickup + pd.to_timedelta(rng.integers(3, 60, size=n_rows), unit="m")

    return pd.DataFrame({
        "hvfhs_license_num": rng.choice(["HV0003", "HV0005"], size=n_rows),
        "dispatching_base_num": rng.choice(["B02764", "B02510", "B02884"], size=n_rows),
        "originating_base_num": rng.choice(["B02764", "B02510", "B02884", None], size=n_rows),
        "request_datetime": request,
        "on_scene_datetime": on_scene,
        "pickup_datetime": pickup,
        "dropoff_datetime": dropoff,
        "PULocationID": rng.integers(1, 263, size=n_rows),
        "DOLocationID": rng.integers(1, 263, size=n_rows),
        "trip_miles": np.abs(rng.normal(4.0, 3.0, size=n_rows)),
        "trip_time": rng.integers(300, 3600, size=n_rows),
        "base_passenger_fare": np.abs(rng.normal(18.0, 12.0, size=n_rows)),
        "tolls": rng.choice([0.0, 0.0, 0.0, 6.55], size=n_rows),
        "bcf": np.abs(rng.normal(0.5, 0.2, size=n_rows)),
        "sales_tax": np.abs(rng.normal(1.5, 0.5, size=n_rows)),
        "congestion_surcharge": rng.choice([0.0, 2.75], size=n_rows),
        "airport_fee": rng.choice([0.0, 2.50], size=n_rows),
        "tips": np.abs(rng.normal(2.0, 2.0, size=n_rows)),
        "driver_pay": np.abs(rng.normal(15.0, 8.0, size=n_rows)),
        "shared_request_flag": rng.choice(["Y", "N"], size=n_rows),
        "shared_match_flag": rng.choice(["Y", "N"], size=n_rows),
        "access_a_ride_flag": rng.choice([" ", "Y"], size=n_rows, p=[0.99, 0.01]),
        "wav_request_flag": rng.choice(["Y", "N"], size=n_rows),
        "wav_match_flag": rng.choice(["Y", "N"], size=n_rows),
    })


def main():
    """Generate and save sample parquet fixtures."""
    parser = argparse.ArgumentParser(description="Generate TLC parquet fixtures")
    parser.add_argument("--out_dir", default=str(Path(__file__).parent / "fixtures"), help="Output directory")
    parser.add_argument("--n_rows", type=int, default=1000, help="Rows per dataset")
    parser.add_argument("--start", default="2023-01-15", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--n_days", type=int, default=1, help="Spread timestamps across N days")
    parser.add_argument("--name_suffix", default="", help="Optional suffix for output filenames (e.g., _45d)")
    args = parser.parse_args()

    fixtures_dir = Path(args.out_dir)
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Generate samples
    print("Generating yellow taxi sample...")
    yellow = generate_yellow_sample(n_rows=args.n_rows, seed=42, start=args.start, n_days=args.n_days)
    yellow_path = fixtures_dir / f"yellow_tripdata_sample{args.name_suffix}.parquet"
    yellow.to_parquet(yellow_path, index=False)
    print(f"  Saved: {yellow_path} ({len(yellow)} rows)")

    print("Generating green taxi sample...")
    green = generate_green_sample(n_rows=args.n_rows, seed=43, start=args.start, n_days=args.n_days)
    green_path = fixtures_dir / f"green_tripdata_sample{args.name_suffix}.parquet"
    green.to_parquet(green_path, index=False)
    print(f"  Saved: {green_path} ({len(green)} rows)")

    print("Generating HVFHV sample...")
    hvfhv = generate_hvfhv_sample(n_rows=args.n_rows, seed=44, start=args.start, n_days=args.n_days)
    hvfhv_path = fixtures_dir / f"fhvhv_tripdata_sample{args.name_suffix}.parquet"
    hvfhv.to_parquet(hvfhv_path, index=False)
    print(f"  Saved: {hvfhv_path} ({len(hvfhv)} rows)")

    print("\nFixtures generated successfully!")
    print("Run tests with: pytest tests/test_schema.py -v")
    if args.n_days > 1:
        print("Multi-day fixtures generated. You can now run the pipeline and expect >1 day of outputs.")


if __name__ == "__main__":
    main()
