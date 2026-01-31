"""
Clean + aggregate raw MTA ridership exports into a canonical bucketed state table.

Output schema (parquet):
- t: bucket timestamp
- ridership_total: sum ridership per bucket
- station_active_count: number of stations with ridership > 0
- station_ridership_counts: JSON dict station_id -> ridership per bucket
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

from src.schema import CanonicalColumns, normalize_schema


def load_prereg(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def list_raw_files(prereg: dict, *, max_files: Optional[int] = None) -> list[str]:
    raw_glob = prereg["boundary"]["raw_glob"]
    files = sorted(str(p) for p in Path(".").glob(raw_glob))
    if max_files is not None:
        files = files[: int(max_files)]
    if not files:
        raise FileNotFoundError(f"No raw files matched: {raw_glob}")
    return files


def read_raw(path: str) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() == ".parquet":
        df = pd.read_parquet(p)
    else:
        df = pd.read_csv(p)
    return normalize_schema(df)


def aggregate(df: pd.DataFrame, *, bucket: str, tz: str) -> pd.DataFrame:
    out = df.copy()
    out[CanonicalColumns.timestamp] = pd.to_datetime(out[CanonicalColumns.timestamp])
    if tz:
        try:
            out[CanonicalColumns.timestamp] = out[CanonicalColumns.timestamp].dt.tz_localize(tz, nonexistent="shift_forward", ambiguous="NaT")
        except TypeError:
            out[CanonicalColumns.timestamp] = out[CanonicalColumns.timestamp].dt.tz_convert(tz)

    # Pandas deprecates uppercase "H"; accept YAML bucket but normalize for floor().
    floor_bucket = bucket.lower() if bucket.upper() == "H" else bucket
    out["t"] = out[CanonicalColumns.timestamp].dt.floor(floor_bucket)

    grouped = (
        out.groupby(["t", CanonicalColumns.station_id], observed=True)[CanonicalColumns.ridership]
        .sum()
        .reset_index()
    )
    total = grouped.groupby("t", observed=True)[CanonicalColumns.ridership].sum().rename("ridership_total")
    active = grouped[grouped[CanonicalColumns.ridership] > 0].groupby("t", observed=True)[CanonicalColumns.station_id].nunique().rename("station_active_count")

    counts = (
        grouped.groupby("t", observed=True)
        .apply(
            lambda g: json.dumps(dict(zip(g[CanonicalColumns.station_id], g[CanonicalColumns.ridership]))),
            include_groups=False,
        )
        .rename("station_ridership_counts")
    )

    state = pd.concat([total, active, counts], axis=1).reset_index()
    state["station_active_count"] = state["station_active_count"].fillna(0).astype(int)
    return state.sort_values("t").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean + aggregate MTA ridership exports")
    parser.add_argument("--prereg", default="EST_PREREG_v0.1_hourly.yaml", help="Preregistration YAML")
    parser.add_argument("--output", default="data/cleaned/bucket_state.parquet", help="Output parquet")
    parser.add_argument("--max_files", type=int, default=None, help="Optional: limit number of raw files (smoke test only)")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)
    bucket = prereg["boundary"]["aggregation"]["bucket"]
    tz = prereg["boundary"]["aggregation"].get("timezone", "")
    start = pd.Timestamp(prereg["boundary"]["time_range"]["start"])
    end = pd.Timestamp(prereg["boundary"]["time_range"]["end"])

    files = list_raw_files(prereg, max_files=args.max_files)
    parts: list[pd.DataFrame] = []
    for f in files:
        df = read_raw(f)
        df = df[(df[CanonicalColumns.timestamp] >= start) & (df[CanonicalColumns.timestamp] <= end)].copy()
        parts.append(df)

    raw = pd.concat(parts, ignore_index=True)
    state = aggregate(raw, bucket=bucket, tz=tz)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    state.to_parquet(out_path, index=False)
    print(f"Saved bucketed state: {out_path} (n={len(state)})")


if __name__ == "__main__":
    main()
