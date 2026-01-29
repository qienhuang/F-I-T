"""
NYC TLC Data Cleaning Pipeline

Cleans raw TLC data according to preregistered boundary.
Outputs: cleaned parquet ready for estimator computation.
"""

import argparse
import json
from pathlib import Path
from glob import glob
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import yaml

from .schema import SCHEMAS, detect_dataset_type_from_path, normalize_schema


def load_prereg(path: str) -> dict:
    """Load preregistration YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def _normalize_date_series(dt_series: pd.Series, tz: str) -> pd.Series:
    """
    Normalize pickup datetimes into a day bucket in the declared timezone.

    TLC datetimes are typically timezone-naive but represent local time.
    """
    dt_series = pd.to_datetime(dt_series)
    if getattr(dt_series.dt, "tz", None) is None:
        # Treat naive timestamps as local in the declared timezone.
        dt_series = dt_series.dt.tz_localize(tz, ambiguous="NaT", nonexistent="shift_forward")
    else:
        dt_series = dt_series.dt.tz_convert(tz)
    return dt_series.dt.floor("D").dt.tz_localize(None)


def list_raw_files(prereg: dict, *, max_files: Optional[int] = None) -> List[str]:
    """List raw TLC parquet files matching prereg boundary (optionally truncated for smoke tests)."""
    boundary = prereg["boundary"]
    raw_glob = boundary["raw_glob"]

    files = sorted(glob(raw_glob))
    if not files:
        raise FileNotFoundError(f"No files found matching: {raw_glob}")

    if max_files is not None:
        files = files[: int(max_files)]

    return files


def iter_clean_daily_parts(
    prereg: dict,
    *,
    files: List[str],
) -> Iterable[Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]]:
    """
    Stream raw parquet files and emit per-file daily aggregates.

    Returns tuples:
    - daily_scalar: per-day sums/counts
    - daily_zone_counts: per-day pickup zone counts
    - meta: per-file validation metadata
    """
    boundary = prereg["boundary"]
    tz = boundary["aggregation"].get("timezone", "America/New_York")
    time_range = boundary.get("time_range", {})

    start = pd.Timestamp(time_range.get("start")) if time_range else None
    end = pd.Timestamp(time_range.get("end")) if time_range else None

    for path in files:
        # Load minimal columns only; schema normalization will rename to canonical names.
        # We intentionally do not load `total_amount` because v1 estimators do not need it.
        # (If needed later, extend schema selection here.)
        try:
            ds_type = detect_dataset_type_from_path(path)
            schema = SCHEMAS[ds_type]
            cols = [
                schema.pickup_datetime,
                schema.dropoff_datetime,
                schema.pickup_zone,
                schema.dropoff_zone,
                schema.trip_distance,
                schema.fare_amount,
            ]
            df = pd.read_parquet(path, columns=cols)
        except Exception:
            # Fallback: load full file and let schema normalization/detection handle it.
            df = pd.read_parquet(path)

        df = normalize_schema(df, dataset_type=None, source_path=path)

        # Filter by time range (boundary)
        if start is not None:
            df = df[df["pickup_datetime"] >= start]
        if end is not None:
            df = df[df["pickup_datetime"] <= end]

        # Clean trip-level validity checks
        df = df[(df["duration_sec"] > 0) & (df["duration_sec"] <= 24 * 3600)]
        df = df[(df["trip_distance"] > 0) & (df["trip_distance"] <= 500)]
        df = df[df["fare_amount"] > 0]
        df = df[df["pickup_zone"].notna() & df["dropoff_zone"].notna()]
        df = df[(df["pickup_zone"] > 0) & (df["dropoff_zone"] > 0)]

        # Day bucket
        df["date"] = _normalize_date_series(df["pickup_datetime"], tz=tz)
        df = df[df["date"].notna()]

        # Daily scalar aggregates
        daily_scalar = (
            df.groupby("date", as_index=False)
            .agg(
                trip_count=("pickup_datetime", "count"),
                total_duration_sec=("duration_sec", "sum"),
                total_distance_miles=("trip_distance", "sum"),
                total_fare=("fare_amount", "sum"),
            )
        )

        # Daily pickup zone counts
        daily_zone_counts = (
            df.groupby(["date", "pickup_zone"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )

        meta = {
            "path": str(path),
            "dataset_type": df["dataset_type"].iloc[0] if "dataset_type" in df.columns and len(df) else None,
            "n_rows": int(len(df)),
            "date_min": str(df["date"].min()) if len(df) else None,
            "date_max": str(df["date"].max()) if len(df) else None,
        }

        yield daily_scalar, daily_zone_counts, meta


def aggregate_daily_from_files(prereg: dict, files: List[str]) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """
    Aggregate daily state variables without loading all trips into memory.

    Returns:
    - daily_state: per-day state with `pickup_zone_counts` as JSON string (for parquet friendliness)
    - meta: aggregated boundary validation metadata
    """
    # Accumulators
    scalar_parts: List[pd.DataFrame] = []
    zone_parts: List[pd.DataFrame] = []

    record_total = 0
    date_min: Optional[pd.Timestamp] = None
    date_max: Optional[pd.Timestamp] = None
    dataset_types: set[str] = set()

    for daily_scalar, daily_zone, meta in iter_clean_daily_parts(prereg, files=files):
        scalar_parts.append(daily_scalar)
        zone_parts.append(daily_zone)

        record_total += int(meta.get("n_rows") or 0)
        if meta.get("dataset_type"):
            dataset_types.add(str(meta["dataset_type"]))

        if meta.get("date_min"):
            d0 = pd.Timestamp(meta["date_min"])
            date_min = d0 if date_min is None else min(date_min, d0)
        if meta.get("date_max"):
            d1 = pd.Timestamp(meta["date_max"])
            date_max = d1 if date_max is None else max(date_max, d1)

    if not scalar_parts:
        raise ValueError("No input files produced any rows after cleaning/boundary filters.")

    # Combine daily scalars (sum over files)
    daily_scalar = (
        pd.concat(scalar_parts, ignore_index=True)
        .groupby("date", as_index=False)
        .agg(
            trip_count=("trip_count", "sum"),
            total_duration_sec=("total_duration_sec", "sum"),
            total_distance_miles=("total_distance_miles", "sum"),
            total_fare=("total_fare", "sum"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Combine zone counts and convert to dict per day
    zones = (
        pd.concat(zone_parts, ignore_index=True)
        .groupby(["date", "pickup_zone"], as_index=False)
        .agg(count=("count", "sum"))
    )

    # Avoid DataFrameGroupBy.apply() to keep pandas warnings quiet and behavior stable.
    zones = zones.copy()
    zones["pickup_zone"] = zones["pickup_zone"].astype(int)
    zones["count"] = zones["count"].astype(int)
    zone_agg = (
        zones.groupby("date", as_index=False)
        .agg(pickup_zone=("pickup_zone", list), count=("count", list))
    )
    zone_agg["pickup_zone_counts"] = [
        dict(zip(zs, cs)) for zs, cs in zip(zone_agg["pickup_zone"], zone_agg["count"])
    ]
    zone_dicts = zone_agg[["date", "pickup_zone_counts"]]

    daily = daily_scalar.merge(zone_dicts, on="date", how="left")

    # Parquet friendliness: store dict as JSON string (estimators already accept both str/dict)
    daily["pickup_zone_counts"] = daily["pickup_zone_counts"].apply(lambda d: json.dumps(d, sort_keys=True))

    meta = {
        "valid": True,
        "warnings": [],
        "schema_drift_detected": False,
        "actual_range": {"start": str(date_min) if date_min is not None else None, "end": str(date_max) if date_max is not None else None},
        "record_count": int(record_total),
        "dataset_types": sorted(dataset_types),
        "n_files": len(files),
    }

    # Respect prereg dataset_type boundary if set
    allowed_types = prereg.get("boundary", {}).get("dataset_type", [])
    if allowed_types:
        unexpected = [t for t in meta["dataset_types"] if t not in allowed_types]
        if unexpected:
            meta["warnings"].append(f"Unexpected dataset types: {unexpected}")
            meta["schema_drift_detected"] = True
            meta["valid"] = False

    return daily, meta


def clean_trips(df: pd.DataFrame, prereg: dict) -> pd.DataFrame:
    """
    Clean trip data according to EST boundary rules.

    Filters:
    - Remove trips with invalid duration (<=0 or >24h)
    - Remove trips with invalid distance (<=0 or >500 miles)
    - Remove trips with invalid fare (<=0)
    - Remove trips outside time range
    - Remove trips with missing zone IDs
    """
    boundary = prereg["boundary"]
    time_range = boundary.get("time_range", {})

    n_before = len(df)

    # Normalize schema
    df = normalize_schema(df)

    # Filter by time range
    if time_range:
        start = pd.Timestamp(time_range.get("start"))
        end = pd.Timestamp(time_range.get("end"))
        df = df[(df["pickup_datetime"] >= start) & (df["pickup_datetime"] <= end)]

    # Remove invalid duration
    df = df[(df["duration_sec"] > 0) & (df["duration_sec"] <= 24 * 3600)]

    # Remove invalid distance
    df = df[(df["trip_distance"] > 0) & (df["trip_distance"] <= 500)]

    # Remove invalid fare
    df = df[df["fare_amount"] > 0]

    # Remove missing zones
    df = df[df["pickup_zone"].notna() & df["dropoff_zone"].notna()]
    df = df[(df["pickup_zone"] > 0) & (df["dropoff_zone"] > 0)]

    n_after = len(df)
    print(f"Cleaned: {n_before:,} -> {n_after:,} trips ({100*n_after/n_before:.1f}% retained)")

    return df


def aggregate_daily(df: pd.DataFrame, prereg: dict) -> pd.DataFrame:
    """
    Aggregate trip data to daily state variables.

    State variables (from prereg):
    - trip_count
    - total_duration_sec
    - total_distance_miles
    - total_fare
    - pickup_zone_counts (as JSON string)
    """
    boundary = prereg["boundary"]
    tz = boundary["aggregation"].get("timezone", "America/New_York")

    # Convert to local timezone and extract date
    df["date"] = df["pickup_datetime"].dt.tz_localize(None).dt.date

    # Aggregate scalar metrics
    daily = df.groupby("date").agg(
        trip_count=("pickup_datetime", "count"),
        total_duration_sec=("duration_sec", "sum"),
        total_distance_miles=("trip_distance", "sum"),
        total_fare=("fare_amount", "sum"),
    ).reset_index()

    # Aggregate zone counts
    zone_counts = (
        df.groupby(["date", "pickup_zone"])
        .size()
        .reset_index(name="count")
    )

    # Convert to dict per day
    zone_dicts = (
        zone_counts.groupby("date")
        .apply(lambda g: dict(zip(g["pickup_zone"].astype(int), g["count"])))
        .reset_index(name="pickup_zone_counts")
    )

    # Merge
    daily = daily.merge(zone_dicts, on="date")

    # Convert date to datetime for consistency
    daily["date"] = pd.to_datetime(daily["date"])

    return daily.sort_values("date").reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Clean TLC data")
    parser.add_argument("--prereg", default="EST_PREREG.yaml", help="Preregistration file")
    parser.add_argument("--output", default="data/cleaned/daily_state.parquet", help="Output path")
    parser.add_argument("--max_files", type=int, default=None, help="Optional: limit number of raw files (smoke test only)")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)

    files = list_raw_files(prereg, max_files=args.max_files)
    print(f"Found {len(files)} raw files.")

    # Aggregate without loading full trips into memory
    daily, validation = aggregate_daily_from_files(prereg, files)
    print(f"Boundary validation: {validation}")

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    daily.to_parquet(output_path, index=False)
    print(f"Saved: {output_path} ({len(daily)} days)")


if __name__ == "__main__":
    main()
