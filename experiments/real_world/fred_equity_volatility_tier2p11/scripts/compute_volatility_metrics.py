#!/usr/bin/env python3
"""
Compute volatility regime metrics and coherence for FRED equity volatility demo.

Usage:
    python compute_volatility_metrics.py --datadir ../data/raw --outdir ../outputs/run001

Outputs:
    - metrics_daily.csv: Daily metrics time series
    - coherence_report.json: EST coherence gate results
    - regime_events.json: Detected regime events
    - run_diagnostics.md: Human-readable summary
"""

import argparse
import json
import os
from datetime import datetime

import pandas as pd
import numpy as np
from scipy import stats


def load_and_align_data(datadir: str, start: str, end: str) -> pd.DataFrame:
    """Load FRED series and align to common daily index."""

    # Load individual series
    series = {}

    # Primary volatility
    emv_path = os.path.join(datadir, "EMVFINCRISES.csv")
    if os.path.exists(emv_path):
        df = pd.read_csv(emv_path, index_col=0, parse_dates=True)
        series["V_emv"] = df.iloc[:, 0]

    vix_path = os.path.join(datadir, "VIXCLS.csv")
    if os.path.exists(vix_path):
        df = pd.read_csv(vix_path, index_col=0, parse_dates=True)
        series["V_vix"] = df.iloc[:, 0]

    # Constraint proxies
    ted_path = os.path.join(datadir, "TEDRATE.csv")
    if os.path.exists(ted_path):
        df = pd.read_csv(ted_path, index_col=0, parse_dates=True)
        series["C_ted"] = df.iloc[:, 0]

    hy_path = os.path.join(datadir, "BAMLH0A0HYM2.csv")
    if os.path.exists(hy_path):
        df = pd.read_csv(hy_path, index_col=0, parse_dates=True)
        series["C_hy"] = df.iloc[:, 0]

    # Recession indicator
    rec_path = os.path.join(datadir, "USREC.csv")
    if os.path.exists(rec_path):
        df = pd.read_csv(rec_path, index_col=0, parse_dates=True)
        series["recession"] = df.iloc[:, 0]

    # Combine into single DataFrame
    combined = pd.DataFrame(series)

    # Filter to date range
    combined = combined.loc[start:end]

    # Forward-fill missing values (up to 5 days)
    combined = combined.ffill(limit=5)

    return combined


def compute_rolling_coherence(df: pd.DataFrame, col1: str, col2: str,
                              window: int = 252) -> pd.Series:
    """Compute rolling Spearman correlation between two columns."""

    def spearman_corr(x, y):
        valid = ~(np.isnan(x) | np.isnan(y))
        if valid.sum() < 10:
            return np.nan
        return stats.spearmanr(x[valid], y[valid])[0]

    result = []
    for i in range(len(df)):
        if i < window - 1:
            result.append(np.nan)
        else:
            x = df[col1].iloc[i-window+1:i+1].values
            y = df[col2].iloc[i-window+1:i+1].values
            result.append(spearman_corr(x, y))

    return pd.Series(result, index=df.index)


def detect_high_volatility_regimes(df: pd.DataFrame, percentile: int = 75,
                                   min_sustained: int = 21) -> pd.DataFrame:
    """Detect high-volatility regime periods."""

    if "V_vix" not in df.columns:
        return pd.DataFrame()

    # Rolling percentile threshold
    threshold = df["V_vix"].rolling(252, min_periods=63).quantile(percentile / 100)

    # High volatility flag
    df = df.copy()
    df["high_vol"] = df["V_vix"] > threshold

    # Sustained high volatility (min_sustained consecutive days)
    df["sustained_high"] = False
    count = 0
    for i in range(len(df)):
        if df["high_vol"].iloc[i]:
            count += 1
            if count >= min_sustained:
                df.iloc[i, df.columns.get_loc("sustained_high")] = True
        else:
            count = 0

    return df


def compute_period_coherence(df: pd.DataFrame, col1: str, col2: str,
                             start: str, end: str) -> dict:
    """Compute coherence for a specific period."""

    mask = (df.index >= start) & (df.index <= end)
    subset = df.loc[mask, [col1, col2]].dropna()

    if len(subset) < 10:
        return {"rho": None, "n": len(subset), "status": "INSUFFICIENT_DATA"}

    rho, pval = stats.spearmanr(subset[col1], subset[col2])

    return {
        "rho": float(rho),
        "n": len(subset),
        "pval": float(pval),
        "status": "PASS" if abs(rho) >= 0.4 else "FAIL"
    }


def main():
    parser = argparse.ArgumentParser(description="FRED Volatility Coherence Analysis")
    parser.add_argument("--datadir", default="../data/raw", help="Data directory")
    parser.add_argument("--outdir", default="../outputs/run001", help="Output directory")
    parser.add_argument("--start", default="2005-01-01", help="Start date")
    parser.add_argument("--end", default="2024-12-31", help="End date")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print(f"Loading data from {args.datadir}")
    df = load_and_align_data(args.datadir, args.start, args.end)
    print(f"Loaded {len(df)} days of data")
    print(f"Columns: {list(df.columns)}")
    print()

    # Compute rolling coherence
    print("Computing rolling coherence (252-day window)...")
    if "C_ted" in df.columns and "C_hy" in df.columns:
        df["coherence_constraint"] = compute_rolling_coherence(df, "C_ted", "C_hy", window=252)
    if "V_emv" in df.columns and "V_vix" in df.columns:
        df["coherence_info"] = compute_rolling_coherence(df, "V_emv", "V_vix", window=252)

    # Detect regimes
    print("Detecting high-volatility regimes...")
    df = detect_high_volatility_regimes(df)

    # Validation periods
    validation_periods = [
        {"name": "GFC", "start": "2008-09-01", "end": "2009-03-31"},
        {"name": "COVID", "start": "2020-03-01", "end": "2020-06-30"},
        {"name": "Dot-com", "start": "2001-03-01", "end": "2001-11-30"},
    ]

    print()
    print("Computing validation period coherence...")
    validation_results = {}
    for period in validation_periods:
        if period["start"] >= args.start:
            result = compute_period_coherence(
                df, "C_ted", "C_hy", period["start"], period["end"]
            )
            validation_results[period["name"]] = result
            rho_str = f"{result['rho']:.3f}" if result['rho'] is not None else 'N/A'
            print(f"  {period['name']}: rho={rho_str}, n={result['n']}, status={result['status']}")

    # Pooled coherence
    print()
    print("Computing pooled coherence...")
    pooled_constraint = compute_period_coherence(df, "C_ted", "C_hy", args.start, args.end)
    pooled_info = compute_period_coherence(df, "V_emv", "V_vix", args.start, args.end) if "V_emv" in df.columns else None

    print(f"  Constraint family (C_ted vs C_hy): rho={pooled_constraint['rho']:.3f}, "
          f"n={pooled_constraint['n']}, status={pooled_constraint['status']}")
    if pooled_info:
        print(f"  Information family (V_emv vs V_vix): rho={pooled_info['rho']:.3f}, "
              f"n={pooled_info['n']}, status={pooled_info['status']}")

    # Coherence gate
    all_validation_pass = all(
        v["status"] == "PASS" or v["status"] == "INSUFFICIENT_DATA"
        for v in validation_results.values()
    )
    coherence_label = "OK_TO_INTERPRET" if all_validation_pass else "ESTIMATOR_UNSTABLE"

    print()
    print(f"Coherence gate: {coherence_label}")

    # Save outputs
    print()
    print("Saving outputs...")

    # Metrics CSV
    metrics_path = os.path.join(args.outdir, "metrics_daily.csv")
    df.to_csv(metrics_path)
    print(f"  Saved: {metrics_path}")

    # Coherence report
    coherence_report = {
        "boundary": {"start": args.start, "end": args.end},
        "pooled": {
            "constraint_family": pooled_constraint,
            "information_family": pooled_info
        },
        "validation_periods": validation_results,
        "coherence_gate": {
            "label": coherence_label,
            "threshold": 0.4,
            "rule": "All validation periods must have rho >= 0.4 or insufficient data"
        }
    }
    coherence_path = os.path.join(args.outdir, "coherence_report.json")
    with open(coherence_path, "w") as f:
        json.dump(coherence_report, f, indent=2, default=str)
    print(f"  Saved: {coherence_path}")

    # Regime events
    regime_events = {
        "high_vol_days": int(df["high_vol"].sum()) if "high_vol" in df.columns else 0,
        "sustained_high_days": int(df["sustained_high"].sum()) if "sustained_high" in df.columns else 0,
    }
    regime_path = os.path.join(args.outdir, "regime_events.json")
    with open(regime_path, "w") as f:
        json.dump(regime_events, f, indent=2)
    print(f"  Saved: {regime_path}")

    # Diagnostics markdown
    diag_md = f"""# FRED Equity Volatility - Run Diagnostics

## Run Config
- Data directory: `{args.datadir}`
- Output directory: `{args.outdir}`
- Boundary: {args.start} to {args.end}
- Days loaded: {len(df)}

## Coherence Gate
- **Status: {coherence_label}**
- Threshold: rho >= 0.4

### Pooled Coherence
- Constraint family (C_ted vs C_hy): rho = {pooled_constraint['rho']:.3f}, n = {pooled_constraint['n']}
- Information family (V_emv vs V_vix): rho = {f"{pooled_info['rho']:.3f}" if pooled_info else 'N/A'}, n = {pooled_info['n'] if pooled_info else 'N/A'}

### Validation Periods
| Period | rho | n | Status |
|--------|-----|---|--------|
"""
    for name, result in validation_results.items():
        rho_str = f"{result['rho']:.3f}" if result['rho'] else "N/A"
        diag_md += f"| {name} | {rho_str} | {result['n']} | {result['status']} |\n"

    diag_md += f"""
## Regime Detection
- High volatility days (VIX > 75th pct): {regime_events['high_vol_days']}
- Sustained high volatility days (21+ consecutive): {regime_events['sustained_high_days']}

## Interpretation
"""
    if coherence_label == "OK_TO_INTERPRET":
        diag_md += "Coherence gate PASSED. Proceed with regime analysis.\n"
    else:
        diag_md += "Coherence gate FAILED. Do NOT interpret regime transitions as FIT-consistent.\n"

    diag_path = os.path.join(args.outdir, "run_diagnostics.md")
    with open(diag_path, "w") as f:
        f.write(diag_md)
    print(f"  Saved: {diag_path}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
