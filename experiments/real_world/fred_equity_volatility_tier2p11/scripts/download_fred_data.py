#!/usr/bin/env python3
"""
Download FRED data for equity volatility regime switching demo.

Usage:
    python download_fred_data.py --start 2000-01-01 --end 2024-12-31 --outdir ../data/raw

Dependencies:
    pip install pandas-datareader pandas

Note: Some series may require FRED API key for full access.
Set environment variable FRED_API_KEY if needed.
"""

import argparse
import os
from datetime import datetime

try:
    import pandas as pd
    import pandas_datareader as pdr
except ImportError:
    print("Please install: pip install pandas pandas-datareader")
    exit(1)


# FRED series for this demo
SERIES = {
    # Primary volatility
    "EMVFINCRISES": "Equity Market Volatility: Financial Crises (news-based)",
    "VIXCLS": "CBOE Volatility Index (VIX)",

    # Constraint proxies
    "TEDRATE": "TED Spread (3-month LIBOR minus T-Bill)",
    "BAMLH0A0HYM2": "ICE BofA US High Yield Option-Adjusted Spread",

    # Recession context
    "USREC": "NBER Recession Indicator",
    "RECPROUSM156N": "Smoothed Recession Probabilities",
}


def download_series(series_id: str, start: datetime, end: datetime) -> pd.DataFrame:
    """Download a single FRED series."""
    try:
        df = pdr.DataReader(series_id, "fred", start, end)
        return df
    except Exception as e:
        print(f"  Warning: Could not download {series_id}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Download FRED data for FIT volatility demo")
    parser.add_argument("--start", default="2000-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2024-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--outdir", default="../data/raw", help="Output directory")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    os.makedirs(args.outdir, exist_ok=True)

    print(f"Downloading FRED data: {args.start} to {args.end}")
    print(f"Output directory: {args.outdir}")
    print()

    downloaded = []
    failed = []

    for series_id, description in SERIES.items():
        print(f"Downloading {series_id}: {description}")
        df = download_series(series_id, start, end)

        if df is not None and len(df) > 0:
            outpath = os.path.join(args.outdir, f"{series_id}.csv")
            df.to_csv(outpath)
            print(f"  Saved: {outpath} ({len(df)} rows)")
            downloaded.append(series_id)
        else:
            failed.append(series_id)

    print()
    print(f"Downloaded: {len(downloaded)} series")
    if failed:
        print(f"Failed: {failed}")

    # Create combined dataset
    if downloaded:
        print()
        print("Creating combined dataset...")
        dfs = {}
        for series_id in downloaded:
            path = os.path.join(args.outdir, f"{series_id}.csv")
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            dfs[series_id] = df[series_id]

        combined = pd.DataFrame(dfs)
        combined_path = os.path.join(args.outdir, "fred_combined.csv")
        combined.to_csv(combined_path)
        print(f"Saved combined: {combined_path} ({len(combined)} rows)")


if __name__ == "__main__":
    main()
