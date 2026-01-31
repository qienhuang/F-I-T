#!/usr/bin/env python3
"""
Download FRED data for recession cycles demo.

Usage:
    python download_recession_data.py --start 1990-01-01 --end 2024-12-31 --outdir ../data/raw
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


# FRED series for recession cycles
SERIES = {
    # Primary recession indicators
    "RECPROUSM156N": "Smoothed Recession Probabilities (Markov-switching)",
    "USREC": "NBER Recession Indicator",
    "USSLIND": "Leading Index for US",

    # Constraint proxies
    "ICSA": "Initial Jobless Claims (weekly)",
    "FEDFUNDS": "Federal Funds Rate",
    "T10Y2Y": "10Y-2Y Treasury Spread (yield curve)",

    # Information/confidence proxies
    "UMCSENT": "Consumer Sentiment",
    "UNRATE": "Unemployment Rate",
    "INDPRO": "Industrial Production Index",
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
    parser = argparse.ArgumentParser(description="Download FRED recession data")
    parser.add_argument("--start", default="1990-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2024-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--outdir", default="../data/raw", help="Output directory")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    os.makedirs(args.outdir, exist_ok=True)

    print(f"Downloading FRED recession data: {args.start} to {args.end}")
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


if __name__ == "__main__":
    main()
