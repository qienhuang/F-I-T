#!/usr/bin/env python3
"""
Compute recession cycle metrics and coherence for FRED economic data demo.

Usage:
    python compute_recession_metrics.py --datadir ../data/raw --outdir ../outputs/run001
"""

import argparse
import json
import os
from datetime import datetime

import pandas as pd
import numpy as np
from scipy import stats


def load_monthly_data(datadir: str, start: str, end: str) -> pd.DataFrame:
    """Load FRED series and resample to monthly."""

    series = {}

    # Recession probability (already monthly)
    rec_prob_path = os.path.join(datadir, "RECPROUSM156N.csv")
    if os.path.exists(rec_prob_path):
        df = pd.read_csv(rec_prob_path, index_col=0, parse_dates=True)
        series["P_rec"] = df.iloc[:, 0]

    # NBER indicator (already monthly)
    usrec_path = os.path.join(datadir, "USREC.csv")
    if os.path.exists(usrec_path):
        df = pd.read_csv(usrec_path, index_col=0, parse_dates=True)
        series["R_nber"] = df.iloc[:, 0]

    # Leading index (already monthly)
    lead_path = os.path.join(datadir, "USSLIND.csv")
    if os.path.exists(lead_path):
        df = pd.read_csv(lead_path, index_col=0, parse_dates=True)
        series["L_idx"] = df.iloc[:, 0]

    # Initial claims (weekly -> monthly mean)
    icsa_path = os.path.join(datadir, "ICSA.csv")
    if os.path.exists(icsa_path):
        df = pd.read_csv(icsa_path, index_col=0, parse_dates=True)
        monthly = df.resample("M").mean()
        series["C_claims"] = monthly.iloc[:, 0]

    # Fed funds (already monthly)
    ff_path = os.path.join(datadir, "FEDFUNDS.csv")
    if os.path.exists(ff_path):
        df = pd.read_csv(ff_path, index_col=0, parse_dates=True)
        series["C_ff"] = df.iloc[:, 0]

    # Yield curve (daily -> monthly mean)
    yc_path = os.path.join(datadir, "T10Y2Y.csv")
    if os.path.exists(yc_path):
        df = pd.read_csv(yc_path, index_col=0, parse_dates=True)
        monthly = df.resample("M").mean()
        series["C_yield_curve"] = monthly.iloc[:, 0]

    # Consumer sentiment
    sent_path = os.path.join(datadir, "UMCSENT.csv")
    if os.path.exists(sent_path):
        df = pd.read_csv(sent_path, index_col=0, parse_dates=True)
        series["I_sent"] = df.iloc[:, 0]

    # Unemployment rate
    unrate_path = os.path.join(datadir, "UNRATE.csv")
    if os.path.exists(unrate_path):
        df = pd.read_csv(unrate_path, index_col=0, parse_dates=True)
        series["unrate"] = df.iloc[:, 0]

    # Industrial production
    indpro_path = os.path.join(datadir, "INDPRO.csv")
    if os.path.exists(indpro_path):
        df = pd.read_csv(indpro_path, index_col=0, parse_dates=True)
        series["indpro"] = df.iloc[:, 0]

    # Combine
    combined = pd.DataFrame(series)
    combined = combined.loc[start:end]

    return combined


def compute_coherence(df: pd.DataFrame, col1: str, col2: str) -> dict:
    """Compute Spearman coherence between two columns."""

    subset = df[[col1, col2]].dropna()

    if len(subset) < 10:
        return {"rho": None, "n": len(subset), "status": "INSUFFICIENT_DATA"}

    rho, pval = stats.spearmanr(subset[col1], subset[col2])

    return {
        "rho": float(rho),
        "n": len(subset),
        "pval": float(pval),
        "status": "PASS" if abs(rho) >= 0.3 else "FAIL"
    }


def compute_period_coherence(df: pd.DataFrame, col1: str, col2: str,
                             start: str, end: str) -> dict:
    """Compute coherence for a specific period."""

    mask = (df.index >= start) & (df.index <= end)
    return compute_coherence(df.loc[mask], col1, col2)


def identify_recession_periods(df: pd.DataFrame) -> list:
    """Identify contiguous recession periods from NBER indicator."""

    if "R_nber" not in df.columns:
        return []

    periods = []
    in_recession = False
    start_date = None

    for date, row in df.iterrows():
        if row["R_nber"] == 1 and not in_recession:
            in_recession = True
            start_date = date
        elif row["R_nber"] == 0 and in_recession:
            in_recession = False
            periods.append({
                "start": start_date.strftime("%Y-%m-%d"),
                "end": date.strftime("%Y-%m-%d")
            })

    if in_recession:
        periods.append({
            "start": start_date.strftime("%Y-%m-%d"),
            "end": df.index[-1].strftime("%Y-%m-%d")
        })

    return periods


def main():
    parser = argparse.ArgumentParser(description="FRED Recession Cycles Analysis")
    parser.add_argument("--datadir", default="../data/raw", help="Data directory")
    parser.add_argument("--outdir", default="../outputs/run001", help="Output directory")
    parser.add_argument("--start", default="1990-01-01", help="Start date")
    parser.add_argument("--end", default="2024-12-31", help="End date")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print(f"Loading data from {args.datadir}")
    df = load_monthly_data(args.datadir, args.start, args.end)
    print(f"Loaded {len(df)} months of data")
    print(f"Columns: {list(df.columns)}")
    print()

    # Identify recession periods
    recession_periods = identify_recession_periods(df)
    print(f"Identified {len(recession_periods)} recession periods:")
    for p in recession_periods:
        print(f"  {p['start']} to {p['end']}")
    print()

    # Pooled coherence
    print("Computing pooled coherence...")
    pooled_results = {}

    # Leading index vs recession probability (expect negative)
    if "L_idx" in df.columns and "P_rec" in df.columns:
        result = compute_coherence(df, "L_idx", "P_rec")
        pooled_results["L_idx_vs_P_rec"] = result
        print(f"  L_idx vs P_rec: rho={f"{result['rho']:.3f}" if result['rho'] else 'N/A'}, "
              f"status={result['status']} (expect NEGATIVE)")

    # Claims vs Fed Funds (constraint family)
    if "C_claims" in df.columns and "C_ff" in df.columns:
        result = compute_coherence(df, "C_claims", "C_ff")
        pooled_results["C_claims_vs_C_ff"] = result
        print(f"  C_claims vs C_ff: rho={f"{result['rho']:.3f}" if result['rho'] else 'N/A'}, "
              f"status={result['status']}")

    # Sentiment vs Leading index (information family)
    if "I_sent" in df.columns and "L_idx" in df.columns:
        result = compute_coherence(df, "I_sent", "L_idx")
        pooled_results["I_sent_vs_L_idx"] = result
        print(f"  I_sent vs L_idx: rho={f"{result['rho']:.3f}" if result['rho'] else 'N/A'}, "
              f"status={result['status']}")

    # Yield curve vs recession probability
    if "C_yield_curve" in df.columns and "P_rec" in df.columns:
        result = compute_coherence(df, "C_yield_curve", "P_rec")
        pooled_results["C_yield_curve_vs_P_rec"] = result
        print(f"  Yield curve vs P_rec: rho={f"{result['rho']:.3f}" if result['rho'] else 'N/A'}, "
              f"status={result['status']} (expect NEGATIVE)")

    print()

    # Recession-period coherence
    print("Computing recession-period coherence...")
    recession_coherence = {}
    for i, period in enumerate(recession_periods):
        period_name = f"Recession_{period['start'][:4]}"
        if "C_claims" in df.columns and "C_ff" in df.columns:
            result = compute_period_coherence(df, "C_claims", "C_ff",
                                              period["start"], period["end"])
            recession_coherence[period_name] = result
            print(f"  {period_name}: rho={f"{result['rho']:.3f}" if result['rho'] else 'N/A'}, "
                  f"n={result['n']}, status={result['status']}")

    # Coherence gate
    # H2: Leading index and recession probability should be negatively coherent
    h2_result = pooled_results.get("L_idx_vs_P_rec", {})
    h2_pass = h2_result.get("rho") is not None and h2_result.get("rho") < -0.4

    # Recession validation
    validation_pass = all(
        r.get("status") in ["PASS", "INSUFFICIENT_DATA"]
        for r in recession_coherence.values()
    ) if recession_coherence else True

    coherence_label = "OK_TO_INTERPRET" if (h2_pass or validation_pass) else "ESTIMATOR_UNSTABLE"

    print()
    print(f"H2 (L_idx vs P_rec < -0.4): {'PASS' if h2_pass else 'FAIL'}")
    print(f"Recession validation: {'PASS' if validation_pass else 'FAIL'}")
    print(f"Coherence gate: {coherence_label}")

    # Save outputs
    print()
    print("Saving outputs...")

    # Metrics CSV
    metrics_path = os.path.join(args.outdir, "metrics_monthly.csv")
    df.to_csv(metrics_path)
    print(f"  Saved: {metrics_path}")

    # Coherence report
    coherence_report = {
        "boundary": {"start": args.start, "end": args.end},
        "pooled": pooled_results,
        "recession_periods": recession_coherence,
        "hypotheses": {
            "H2_L_idx_vs_P_rec": {
                "expected": "rho < -0.4",
                "actual": h2_result.get("rho"),
                "status": "PASS" if h2_pass else "FAIL"
            }
        },
        "coherence_gate": {
            "label": coherence_label,
            "h2_pass": h2_pass,
            "validation_pass": validation_pass
        }
    }
    coherence_path = os.path.join(args.outdir, "coherence_report.json")
    with open(coherence_path, "w") as f:
        json.dump(coherence_report, f, indent=2, default=str)
    print(f"  Saved: {coherence_path}")

    # Recession events
    recession_path = os.path.join(args.outdir, "recession_events.json")
    with open(recession_path, "w") as f:
        json.dump(recession_periods, f, indent=2)
    print(f"  Saved: {recession_path}")

    # Diagnostics markdown
    diag_md = f"""# FRED Recession Cycles - Run Diagnostics

## Run Config
- Data directory: `{args.datadir}`
- Output directory: `{args.outdir}`
- Boundary: {args.start} to {args.end}
- Months loaded: {len(df)}

## Coherence Gate
- **Status: {coherence_label}**

### H2: Leading Index vs Recession Probability
- Expected: rho < -0.4 (negative correlation)
- Actual: rho = {f"{h2_result.get('rho'):.3f}" if h2_result.get('rho') else 'N/A'}
- Status: **{'PASS' if h2_pass else 'FAIL'}**

### Pooled Coherence
| Pair | rho | n | Status |
|------|-----|---|--------|
"""
    for name, result in pooled_results.items():
        rho_str = f"{result['rho']:.3f}" if result['rho'] else "N/A"
        diag_md += f"| {name} | {rho_str} | {result['n']} | {result['status']} |\n"

    diag_md += f"""
### Recession Period Coherence (C_claims vs C_ff)
| Period | rho | n | Status |
|--------|-----|---|--------|
"""
    for name, result in recession_coherence.items():
        rho_str = f"{result['rho']:.3f}" if result['rho'] else "N/A"
        diag_md += f"| {name} | {rho_str} | {result['n']} | {result['status']} |\n"

    diag_md += f"""
## Recession Periods Detected
| Start | End |
|-------|-----|
"""
    for p in recession_periods:
        diag_md += f"| {p['start']} | {p['end']} |\n"

    diag_md += """
## Interpretation
"""
    if coherence_label == "OK_TO_INTERPRET":
        diag_md += "Coherence gate PASSED. Proceed with regime analysis.\n"
    else:
        diag_md += "Coherence gate evaluation mixed. See detailed results.\n"

    diag_path = os.path.join(args.outdir, "run_diagnostics.md")
    with open(diag_path, "w") as f:
        f.write(diag_md)
    print(f"  Saved: {diag_path}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
