"""
Schema handling for MTA subway ridership exports.

Design goal: accept a small set of common column aliases, normalize to a canonical schema,
and fail fast if the boundary drifts.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CanonicalColumns:
    timestamp: str = "timestamp"
    station_id: str = "station_id"
    ridership: str = "ridership"


TIMESTAMP_ALIASES = (
    "transit_timestamp",
    "timestamp",
    "datetime",
    "date_time",
    "time",
)
STATION_ID_ALIASES = (
    "station_complex_id",
    "complex_id",
    "station_id",
    "station",
)
RIDERSHIP_ALIASES = (
    "ridership",
    "entries",
    "total",
    "count",
)


def _find_col(df: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for a in aliases:
        if a.lower() in cols:
            return cols[a.lower()]
    return None


def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    ts_col = _find_col(df, TIMESTAMP_ALIASES)
    st_col = _find_col(df, STATION_ID_ALIASES)
    rd_col = _find_col(df, RIDERSHIP_ALIASES)

    missing = [name for name, col in (("timestamp", ts_col), ("station_id", st_col), ("ridership", rd_col)) if col is None]
    if missing:
        raise ValueError(f"Missing required columns (or aliases): {missing}. Columns: {list(df.columns)}")

    out = df[[ts_col, st_col, rd_col]].copy()
    out.columns = [CanonicalColumns.timestamp, CanonicalColumns.station_id, CanonicalColumns.ridership]

    out[CanonicalColumns.timestamp] = pd.to_datetime(out[CanonicalColumns.timestamp], errors="coerce", utc=False)
    if out[CanonicalColumns.timestamp].isna().any():
        bad = int(out[CanonicalColumns.timestamp].isna().sum())
        raise ValueError(f"Failed to parse {bad} timestamps")

    out[CanonicalColumns.station_id] = out[CanonicalColumns.station_id].astype(str)
    out[CanonicalColumns.ridership] = pd.to_numeric(out[CanonicalColumns.ridership], errors="coerce").fillna(0.0).astype(float)
    out = out[out[CanonicalColumns.ridership] >= 0].copy()

    return out
