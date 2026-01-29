"""
NYC TLC Estimator Computation

Computes Information (I), Constraint (C), and Force (F) estimators
according to preregistered definitions.

Information estimators:
- I_entropy_pu: Pickup zone Shannon entropy
- I_entropy_od: OD pair Shannon entropy (optional)
- I_temporal_entropy: Hourly distribution entropy (optional)

Constraint estimators:
- C_congestion: log1p(minutes per mile)
- C_scarcity: -log(trip_count)
- C_concentration: Spatial concentration (top-k share or Gini)
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def load_prereg(path: str) -> dict:
    """Load preregistration YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


# ============================================================================
# Entropy and Concentration Functions
# ============================================================================

def shannon_entropy(counts: dict) -> float:
    """
    Compute Shannon entropy from count dictionary.

    H = -sum(p_i * log(p_i))

    Returns entropy in nats (natural log).
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0

    probs = np.array(list(counts.values())) / total
    probs = probs[probs > 0]  # filter zeros

    return -np.sum(probs * np.log(probs))


def topk_share(counts: dict, k: int = 5) -> float:
    """
    Compute top-k concentration (share of top-k categories).

    C_conc = sum of top-k shares
    Range: [k/n, 1] where n is number of categories
    Higher = more concentrated
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0

    sorted_counts = sorted(counts.values(), reverse=True)
    topk_sum = sum(sorted_counts[:k])

    return topk_sum / total


def gini_coefficient(counts: dict) -> float:
    """
    Compute Gini coefficient for spatial concentration.

    Range: [0, 1] where 0 = perfect equality, 1 = perfect concentration
    """
    values = np.array(list(counts.values()), dtype=float)
    if len(values) == 0 or np.sum(values) == 0:
        return 0.0

    # Sort values
    values = np.sort(values)
    n = len(values)

    # Compute Gini using the formula: G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
    cumsum = np.cumsum(values)
    total = cumsum[-1]
    if total == 0:
        return 0.0

    gini = (2 * np.sum((np.arange(1, n + 1) * values))) / (n * total) - (n + 1) / n
    return max(0.0, min(1.0, gini))  # Clamp to [0, 1]


# ============================================================================
# Information Estimators
# ============================================================================

def compute_information_estimators(df: pd.DataFrame, prereg: dict) -> pd.DataFrame:
    """
    Compute Information estimators (I).

    Available estimators:
    - I_entropy_pu: Shannon entropy of pickup zone distribution
    - I_entropy_od: Shannon entropy of OD pair distribution
    - I_temporal_entropy: Shannon entropy of hourly distribution
    """
    estimators_config = prereg["estimators"]["information"]
    results = []

    for _, row in df.iterrows():
        result = {"date": row["date"]}

        # Get zone counts
        zone_counts = row.get("pickup_zone_counts", {})
        if isinstance(zone_counts, str):
            zone_counts = json.loads(zone_counts)

        # I_entropy_pu: Pickup zone entropy
        if estimators_config.get("I_entropy_pu", {}).get("enabled", False):
            result["I_entropy_pu"] = shannon_entropy(zone_counts)

        # I_entropy_od: OD pair entropy (if available)
        if estimators_config.get("I_entropy_od", {}).get("enabled", False):
            od_counts = row.get("od_pair_counts", {})
            if isinstance(od_counts, str):
                od_counts = json.loads(od_counts)
            if od_counts:
                result["I_entropy_od"] = shannon_entropy(od_counts)
            else:
                result["I_entropy_od"] = np.nan

        # I_temporal_entropy: Hourly distribution entropy (if available)
        if estimators_config.get("I_temporal_entropy", {}).get("enabled", False):
            hourly_counts = row.get("hourly_counts", {})
            if isinstance(hourly_counts, str):
                hourly_counts = json.loads(hourly_counts)
            if hourly_counts:
                result["I_temporal_entropy"] = shannon_entropy(hourly_counts)
            else:
                result["I_temporal_entropy"] = np.nan

        results.append(result)

    return pd.DataFrame(results)


# ============================================================================
# Constraint Estimators
# ============================================================================

def compute_constraint_estimators(df: pd.DataFrame, prereg: dict) -> pd.DataFrame:
    """
    Compute Constraint estimators (C).

    Available estimators:
    - C_congestion: log1p(minutes per mile) - travel friction
    - C_scarcity: -log(trip_count) - supply/demand constraint
    - C_concentration: Spatial concentration (top-k share or Gini)
    - C_price_pressure: log1p(fare per mile) - cost/price proxy
    """
    estimators_config = prereg["estimators"]["constraint"]
    results = []

    for _, row in df.iterrows():
        result = {"date": row["date"]}

        # C_congestion: log1p(duration_min / miles)
        if estimators_config.get("C_congestion", {}).get("enabled", False):
            duration_min = row["total_duration_sec"] / 60
            miles = row["total_distance_miles"]
            if miles > 0:
                result["C_congestion"] = np.log1p(duration_min / miles)
            else:
                result["C_congestion"] = np.nan

        # C_scarcity: -log(trip_count)
        if estimators_config.get("C_scarcity", {}).get("enabled", False):
            trip_count = row["trip_count"]
            if trip_count > 0:
                result["C_scarcity"] = -np.log(trip_count)
            else:
                result["C_scarcity"] = np.nan

        # C_price_pressure: log1p(total_fare / miles)
        if estimators_config.get("C_price_pressure", {}).get("enabled", False):
            miles = row["total_distance_miles"]
            total_fare = row["total_fare"]
            if miles > 0 and total_fare >= 0:
                result["C_price_pressure"] = np.log1p(total_fare / miles)
            else:
                result["C_price_pressure"] = np.nan

        # C_concentration: Spatial concentration
        if estimators_config.get("C_concentration", {}).get("enabled", False):
            zone_counts = row.get("pickup_zone_counts", {})
            if isinstance(zone_counts, str):
                zone_counts = json.loads(zone_counts)

            conc_config = estimators_config["C_concentration"]
            conc_type = conc_config.get("type", "topk_share")

            if conc_type == "topk_share":
                k = conc_config.get("k", 5)
                result["C_concentration"] = topk_share(zone_counts, k)
            elif conc_type == "gini":
                result["C_concentration"] = gini_coefficient(zone_counts)
            else:
                # Default to top-k
                k = conc_config.get("k", 5)
                result["C_concentration"] = topk_share(zone_counts, k)

        results.append(result)

    return pd.DataFrame(results)


# ============================================================================
# Force Estimators
# ============================================================================

def compute_force_estimators(df: pd.DataFrame, prereg: dict) -> pd.DataFrame:
    """
    Compute Force estimators (F).

    Force estimators are drift proxies computed as rolling differences.
    - F_fare_drift: Change in fare per mile
    - F_congestion_drift: Change in congestion
    """
    window_config = prereg["window"]
    window = window_config.get("smoothing", 7)

    results = df[["date"]].copy()

    # Compute fare per mile
    results["fare_per_mile"] = df["total_fare"] / df["total_distance_miles"].replace(0, np.nan)

    # F_fare_drift: rolling diff of fare_per_mile
    results["F_fare_drift"] = (
        results["fare_per_mile"]
        .rolling(window=window, min_periods=1)
        .mean()
        .diff()
    )

    # Compute C_congestion for drift calculation
    duration_min = df["total_duration_sec"] / 60
    miles = df["total_distance_miles"]
    results["_congestion"] = np.log1p(duration_min / miles.replace(0, np.nan))

    # F_congestion_drift
    results["F_congestion_drift"] = (
        results["_congestion"]
        .rolling(window=window, min_periods=1)
        .mean()
        .diff()
    )

    # Clean up intermediate columns
    results = results.drop(columns=["fare_per_mile", "_congestion"])

    return results


# ============================================================================
# Ratio and Derivative
# ============================================================================

def compute_ratio_and_derivative(
    I_df: pd.DataFrame,
    C_df: pd.DataFrame,
    prereg: dict
) -> pd.DataFrame:
    """
    Compute I/C ratio and its derivative (core P11 signal).

    R(t) = I(t) / C(t)
    dR/dt = rolling mean then diff
    """
    window_config = prereg["window"]
    window = window_config.get("smoothing", 7)

    # Merge I and C
    merged = I_df.merge(C_df, on="date")

    # Use primary estimators
    I_col = "I_entropy_pu"
    C_col = "C_congestion"

    # Compute ratio (handle division carefully)
    # Note: C_congestion is positive, so ratio makes sense
    merged["R_I_over_C"] = merged[I_col] / merged[C_col].replace(0, np.nan)

    # Smooth and differentiate
    merged["R_smoothed"] = (
        merged["R_I_over_C"]
        .rolling(window=window, min_periods=1)
        .mean()
    )
    merged["dR_dt"] = merged["R_smoothed"].diff()

    return merged[["date", "R_I_over_C", "R_smoothed", "dR_dt"]]


# ============================================================================
# Coherence Gate
# ============================================================================

def compute_coherence(C_df: pd.DataFrame, prereg: dict) -> dict:
    """
    Compute coherence gate for constraint estimator family.

    Tests whether constraint estimators agree in their rankings.
    Uses Spearman correlation between enabled constraint pairs.

    If coherence fails:
    - Status = ESTIMATOR_UNSTABLE
    - Change points are NOT interpretable

    If coherence passes:
    - Status = OK
    - Change points can be interpreted as regime signatures
    """
    from scipy import stats

    coherence_config = prereg.get("coherence", {})
    threshold = coherence_config.get("threshold", 0.6)
    min_points = coherence_config.get("min_points", 30)
    windowing = coherence_config.get("windowing")

    # Get enabled constraint columns
    c_cols = [c for c in C_df.columns if c.startswith("C_") and c != "date"]

    if len(c_cols) < 2:
        return {
            "status": "SKIPPED",
            "reason": "Less than 2 constraint estimators enabled",
            "pairs": [],
            "threshold": threshold,
            "min_points": min_points,
        }

    # Check each pair defined in prereg
    pairs = coherence_config.get("pairs", [])

    # If no pairs defined, test all combinations
    if not pairs:
        pairs = [[c_cols[i], c_cols[j]] for i in range(len(c_cols)) for j in range(i+1, len(c_cols))]

    def _compute_pair(df: pd.DataFrame, c1: str, c2: str) -> dict:
        if c1 not in df.columns or c2 not in df.columns:
            return {
                "pair": [c1, c2],
                "status": "COLUMN_MISSING",
                "reason": f"Column not found: {c1 if c1 not in df.columns else c2}",
            }

        valid = df[[c1, c2]].dropna()
        if len(valid) < min_points:
            return {
                "pair": [c1, c2],
                "status": "DATA_MISSING",
                "n_points": int(len(valid)),
                "min_required": int(min_points),
            }

        rho, pvalue = stats.spearmanr(valid[c1], valid[c2])
        passed = bool(rho >= threshold)
        return {
            "pair": [c1, c2],
            "rho": float(rho),
            "pvalue": float(pvalue),
            "n_points": int(len(valid)),
            "threshold": float(threshold),
            "passed": passed,
        }

    results = [_compute_pair(C_df, c1, c2) for c1, c2 in pairs]

    # Overall status
    valid_results = [r for r in results if "passed" in r]
    all_passed = all(r["passed"] for r in valid_results) if valid_results else False
    any_missing = any(r.get("status") in ["DATA_MISSING", "COLUMN_MISSING"] for r in results)

    if not valid_results:
        status = "SKIPPED"
    elif any_missing and not all_passed:
        status = "DATA_MISSING"
    elif all_passed:
        status = "OK"
    else:
        status = "ESTIMATOR_UNSTABLE"

    report: dict = {
        "status": status,
        "pairs": results,
        "threshold": threshold,
        "min_points": min_points,
        "n_constraint_estimators": len(c_cols),
    }

    def _summarize_status(pair_results: list[dict]) -> str:
        valid = [r for r in pair_results if "passed" in r]
        all_passed_local = all(r["passed"] for r in valid) if valid else False
        any_missing_local = any(r.get("status") in ["DATA_MISSING", "COLUMN_MISSING"] for r in pair_results)
        if not valid:
            return "SKIPPED"
        if any_missing_local and not all_passed_local:
            return "DATA_MISSING"
        if all_passed_local:
            return "OK"
        return "ESTIMATOR_UNSTABLE"

    # v1.5+ (optional): year-by-year coherence windowing.
    if windowing and windowing.get("type") == "yearly":
        if "date" not in C_df.columns:
            report["windowing"] = {"status": "ERROR", "reason": "Missing date column for yearly windowing"}
            return report

        df = C_df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["year"] = df["date"].dt.year.astype(int)

        yearly_results: list[dict] = []
        for year, g in df.groupby("year", sort=True):
            y_pairs = [_compute_pair(g, c1, c2) for c1, c2 in pairs]
            y_status = _summarize_status(y_pairs)
            yearly_results.append({"year": int(year), "status": y_status, "pairs": y_pairs})

        aggregate = windowing.get("aggregate", "all_pass")
        allow_pooled_fail = bool(windowing.get("allow_pooled_fail", False))

        if aggregate != "all_pass":
            report["windowing"] = {"status": "UNSUPPORTED", "type": "yearly", "aggregate": aggregate}
            return report

        all_years_ok = all(r["status"] == "OK" for r in yearly_results) if yearly_results else False
        pooled_status = report["status"]

        if all_years_ok:
            if pooled_status == "OK":
                report["status"] = "OK"
            elif allow_pooled_fail:
                report["status"] = "OK_PER_YEAR"
            else:
                report["status"] = pooled_status

        report["windowing"] = {
            "type": "yearly",
            "aggregate": "all_pass",
            "allow_pooled_fail": allow_pooled_fail,
            "pooled_status": pooled_status,
            "results": yearly_results,
        }

    # v1.6+ (optional): arbitrary date windows (e.g., pre/post-COVID) and rolling windows.
    if windowing and windowing.get("type") in {"date_ranges", "rolling"}:
        if "date" not in C_df.columns:
            report["windowing"] = {"status": "ERROR", "reason": "Missing date column for windowed coherence"}
            return report

        df = C_df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])

        aggregate = windowing.get("aggregate", "all_pass")
        allow_pooled_fail = bool(windowing.get("allow_pooled_fail", False))
        if aggregate != "all_pass":
            report["windowing"] = {
                "status": "UNSUPPORTED",
                "type": windowing.get("type"),
                "aggregate": aggregate,
            }
            return report

        windows: list[dict] = []
        wtype = windowing.get("type")

        if wtype == "date_ranges":
            for w in windowing.get("windows", []) or []:
                name = str(w.get("name") or "window")
                start = pd.to_datetime(w.get("start"), errors="coerce")
                end = pd.to_datetime(w.get("end"), errors="coerce")
                if pd.isna(start) or pd.isna(end):
                    windows.append(
                        {
                            "name": name,
                            "status": "ERROR",
                            "reason": "Invalid start/end",
                            "start": str(w.get("start")),
                            "end": str(w.get("end")),
                            "pairs": [],
                        }
                    )
                    continue
                mask = (df["date"] >= start) & (df["date"] <= end)
                g = df.loc[mask]
                w_pairs = [_compute_pair(g, c1, c2) for c1, c2 in pairs]
                w_status = _summarize_status(w_pairs)
                windows.append(
                    {
                        "name": name,
                        "start": start.strftime("%Y-%m-%d"),
                        "end": end.strftime("%Y-%m-%d"),
                        "status": w_status,
                        "pairs": w_pairs,
                    }
                )

        if wtype == "rolling":
            window_days = int(windowing.get("window_days", 180))
            step_days = int(windowing.get("step_days", 30))
            start = pd.to_datetime(windowing.get("start"), errors="coerce")
            end = pd.to_datetime(windowing.get("end"), errors="coerce")
            if pd.isna(start):
                start = df["date"].min()
            if pd.isna(end):
                end = df["date"].max()

            if pd.isna(start) or pd.isna(end) or window_days <= 0 or step_days <= 0:
                report["windowing"] = {
                    "status": "ERROR",
                    "type": "rolling",
                    "reason": "Invalid rolling window parameters",
                }
                return report

            idx = 0
            cur = start
            while True:
                win_start = cur
                win_end = win_start + pd.Timedelta(days=window_days)
                if win_end > end:
                    break
                mask = (df["date"] >= win_start) & (df["date"] <= win_end)
                g = df.loc[mask]
                w_pairs = [_compute_pair(g, c1, c2) for c1, c2 in pairs]
                w_status = _summarize_status(w_pairs)
                windows.append(
                    {
                        "name": f"win_{idx:03d}",
                        "start": win_start.strftime("%Y-%m-%d"),
                        "end": win_end.strftime("%Y-%m-%d"),
                        "status": w_status,
                        "pairs": w_pairs,
                    }
                )
                idx += 1
                cur = cur + pd.Timedelta(days=step_days)

        pooled_status = report["status"]
        all_windows_ok = all(w.get("status") == "OK" for w in windows) if windows else False
        any_missing = any(w.get("status") in {"DATA_MISSING", "COLUMN_MISSING", "SKIPPED"} for w in windows)
        any_error = any(w.get("status") == "ERROR" for w in windows)

        if any_error:
            report["status"] = pooled_status
        elif all_windows_ok:
            if pooled_status == "OK":
                report["status"] = "OK"
            elif allow_pooled_fail:
                report["status"] = "OK_PER_WINDOW"
            else:
                report["status"] = pooled_status
        else:
            report["status"] = "DATA_MISSING" if any_missing else "ESTIMATOR_UNSTABLE"

        report["windowing"] = {
            "type": wtype,
            "aggregate": "all_pass",
            "allow_pooled_fail": allow_pooled_fail,
            "pooled_status": pooled_status,
            "results": windows,
        }
        if wtype == "rolling":
            report["windowing"]["window_days"] = int(windowing.get("window_days", 180))
            report["windowing"]["step_days"] = int(windowing.get("step_days", 30))

    return report


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Compute TLC estimators")
    parser.add_argument("--prereg", default="EST_PREREG.yaml", help="Preregistration file")
    parser.add_argument("--input", default="data/cleaned/daily_state.parquet", help="Input data")
    parser.add_argument("--output", default="outputs/metrics_log.parquet", help="Output path")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)

    # Load cleaned data
    df = pd.read_parquet(args.input)
    print(f"Loaded {len(df)} days of data")

    # Compute estimators
    print("Computing Information estimators...")
    I_df = compute_information_estimators(df, prereg)
    i_cols = [c for c in I_df.columns if c.startswith("I_")]
    print(f"  Enabled: {i_cols}")

    print("Computing Constraint estimators...")
    C_df = compute_constraint_estimators(df, prereg)
    c_cols = [c for c in C_df.columns if c.startswith("C_")]
    print(f"  Enabled: {c_cols}")

    print("Computing Force estimators...")
    F_df = compute_force_estimators(df, prereg)

    print("Computing I/C ratio and derivative...")
    R_df = compute_ratio_and_derivative(I_df, C_df, prereg)

    # Merge all
    metrics = df[["date", "trip_count"]].copy()
    metrics = metrics.merge(I_df, on="date")
    metrics = metrics.merge(C_df, on="date")
    metrics = metrics.merge(F_df, on="date")
    metrics = metrics.merge(R_df, on="date")

    # Compute coherence
    print("Computing coherence gate...")
    coherence = compute_coherence(C_df, prereg)
    print(f"Coherence status: {coherence['status']}")
    for pair_result in coherence.get("pairs", []):
        if "rho" in pair_result:
            passed = "PASS" if pair_result["passed"] else "FAIL"
            print(f"  {pair_result['pair']}: rho={pair_result['rho']:.3f} [{passed}]")

    windowing = coherence.get("windowing", {})
    if windowing.get("type") == "yearly":
        yearly = windowing.get("results", [])
        if yearly:
            print("Yearly coherence (diagnostic):")
            for yr in yearly:
                yr_year = yr.get("year", "?")
                yr_status = yr.get("status", "UNKNOWN")
                parts = []
                for pr in yr.get("pairs", []):
                    if "rho" in pr:
                        parts.append(f"{pr['pair'][0]}~{pr['pair'][1]} rho={pr['rho']:.3f}")
                suffix = ("; " + ", ".join(parts)) if parts else ""
                print(f"  {yr_year}: {yr_status}{suffix}")

    # Save metrics
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(output_path, index=False)
    print(f"Saved metrics: {output_path}")

    # Save coherence report
    coherence_path = output_path.parent / "coherence_report.json"
    with open(coherence_path, "w") as f:
        json.dump(coherence, f, indent=2)
    print(f"Saved coherence: {coherence_path}")


if __name__ == "__main__":
    main()
