#!/usr/bin/env python3
"""
Download MTA Subway Hourly Ridership data from NY Open Data portal.

Data source: MTA Subway Hourly Ridership: Beginning 2020
URL: https://data.ny.gov/Transportation/MTA-Subway-Hourly-Ridership-Beginning-February-202/wujg-7c2s

Usage:
    python download_mta_data.py --outdir ../data/raw --sample
"""

import argparse
import os
from pathlib import Path
from urllib.parse import quote

import pandas as pd


def download_date_range(base_url: str, start_date: str, end_date: str, limit: int = 1000000) -> pd.DataFrame:
    """Download MTA data for a specific date range."""
    # Socrata SoQL query with date filter - URL encode the where clause
    where_clause = f"transit_timestamp >= '{start_date}' AND transit_timestamp < '{end_date}'"
    encoded_where = quote(where_clause, safe='')
    url = f"{base_url}?$where={encoded_where}&$limit={limit}&$order=transit_timestamp"
    print(f"  Fetching {start_date} to {end_date}...")

    try:
        df = pd.read_csv(url)
        print(f"    Got {len(df)} rows")
        return df
    except Exception as e:
        print(f"    Error: {e}")
        return pd.DataFrame()


def download_mta_hourly_sampled(outdir: str) -> Path:
    """Download MTA data with strategic sampling for key periods."""

    base_url = "https://data.ny.gov/resource/wujg-7c2s.csv"

    # Continuous quarterly chunks for 2023-2024
    # This gives full daily coverage for coherence analysis
    periods = [
        ("2023-01-01", "2023-04-01"),
        ("2023-04-01", "2023-07-01"),
        ("2023-07-01", "2023-10-01"),
        ("2023-10-01", "2024-01-01"),
        ("2024-01-01", "2024-04-01"),
        ("2024-04-01", "2024-07-01"),
        ("2024-07-01", "2024-10-01"),
    ]

    all_dfs = []
    for start, end in periods:
        df = download_date_range(base_url, start, end, limit=500000)
        if len(df) > 0:
            all_dfs.append(df)

    if not all_dfs:
        raise ValueError("No data downloaded")

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\nCombined: {len(combined)} rows")
    print(f"Date range: {combined['transit_timestamp'].min()} to {combined['transit_timestamp'].max()}")

    # Keep only needed columns
    needed_cols = ["transit_timestamp", "station_complex_id", "ridership"]
    available_cols = [c for c in needed_cols if c in combined.columns]
    combined = combined[available_cols].copy()

    # Sort by timestamp
    combined = combined.sort_values("transit_timestamp").reset_index(drop=True)

    # Save
    os.makedirs(outdir, exist_ok=True)
    out_path = Path(outdir) / "mta_subway_hourly.csv"
    combined.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    return out_path


def download_mta_hourly(outdir: str, limit: int = None) -> Path:
    """Download MTA subway hourly ridership data via Socrata API."""

    base_url = "https://data.ny.gov/resource/wujg-7c2s.csv"

    if limit:
        url = f"{base_url}?$limit={limit}&$order=transit_timestamp"
    else:
        url = f"{base_url}?$limit=10000000&$order=transit_timestamp"

    print(f"Downloading from: {url}")
    print("This may take several minutes for the full dataset...")

    df = pd.read_csv(url)

    print(f"Downloaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['transit_timestamp'].min()} to {df['transit_timestamp'].max()}")

    # Keep only needed columns
    needed_cols = ["transit_timestamp", "station_complex_id", "ridership"]
    available_cols = [c for c in needed_cols if c in df.columns]
    df = df[available_cols].copy()

    os.makedirs(outdir, exist_ok=True)
    out_path = Path(outdir) / "mta_subway_hourly.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Download MTA Subway Hourly Ridership data")
    parser.add_argument("--outdir", default="../data/raw", help="Output directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit rows (for testing)")
    parser.add_argument("--sample", action="store_true", help="Download strategic samples of key periods")
    args = parser.parse_args()

    if args.sample:
        download_mta_hourly_sampled(args.outdir)
    else:
        download_mta_hourly(args.outdir, args.limit)
    print("Done!")


if __name__ == "__main__":
    main()
