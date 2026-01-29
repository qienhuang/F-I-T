"""
NYC TLC Data Schema Definition

Handles schema normalization across TLC data versions and dataset types.
EST boundary: schema changes require new preregistration.

Supported dataset types:
- yellow: Yellow Taxi (tpep_* columns)
- green: Green Taxi (lpep_* columns)
- hvfhv: High Volume For-Hire Vehicle (hvfhs_* columns)
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import pandas as pd


class DatasetType(Enum):
    """TLC dataset types with different schemas."""
    YELLOW = "yellow"
    GREEN = "green"
    HVFHV = "hvfhv"


@dataclass
class TLCSchema:
    """Normalized column names for TLC trip data."""

    # Dataset type
    dataset_type: DatasetType

    # Timestamp columns
    pickup_datetime: str
    dropoff_datetime: str

    # Location columns
    pickup_zone: str
    dropoff_zone: str

    # Trip metrics
    trip_distance: str

    # Fare columns
    fare_amount: str
    total_amount: str

    # Canonical output names
    CANONICAL_COLUMNS = [
        "pickup_datetime",
        "dropoff_datetime",
        "pickup_zone",
        "dropoff_zone",
        "trip_distance",
        "fare_amount",
        "total_amount",
        "dataset_type",  # added for multi-dataset support
    ]


# Schema definitions for each dataset type
SCHEMAS = {
    DatasetType.YELLOW: TLCSchema(
        dataset_type=DatasetType.YELLOW,
        pickup_datetime="tpep_pickup_datetime",
        dropoff_datetime="tpep_dropoff_datetime",
        pickup_zone="PULocationID",
        dropoff_zone="DOLocationID",
        trip_distance="trip_distance",
        fare_amount="fare_amount",
        total_amount="total_amount",
    ),
    DatasetType.GREEN: TLCSchema(
        dataset_type=DatasetType.GREEN,
        pickup_datetime="lpep_pickup_datetime",
        dropoff_datetime="lpep_dropoff_datetime",
        pickup_zone="PULocationID",
        dropoff_zone="DOLocationID",
        trip_distance="trip_distance",
        fare_amount="fare_amount",
        total_amount="total_amount",
    ),
    DatasetType.HVFHV: TLCSchema(
        dataset_type=DatasetType.HVFHV,
        pickup_datetime="pickup_datetime",
        dropoff_datetime="dropoff_datetime",
        pickup_zone="PULocationID",
        dropoff_zone="DOLocationID",
        trip_distance="trip_miles",  # different column name!
        fare_amount="base_passenger_fare",
        total_amount="base_passenger_fare",  # hvfhv doesn't have total_amount
    ),
}


def detect_dataset_type(df: pd.DataFrame) -> DatasetType:
    """
    Detect TLC dataset type from DataFrame columns.

    Returns:
        DatasetType enum value

    Raises:
        ValueError if dataset type cannot be determined
    """
    cols = set(df.columns)

    # Check for yellow taxi (tpep_*)
    if "tpep_pickup_datetime" in cols:
        return DatasetType.YELLOW

    # Check for green taxi (lpep_*)
    if "lpep_pickup_datetime" in cols:
        return DatasetType.GREEN

    # Check for hvfhv
    if "hvfhs_license_num" in cols or "trip_miles" in cols:
        return DatasetType.HVFHV

    raise ValueError(
        f"Cannot detect dataset type. Columns: {sorted(cols)[:10]}..."
    )


def detect_dataset_type_from_path(path: str) -> DatasetType:
    """
    Detect TLC dataset type from file path.

    Examples:
        yellow_tripdata_2023-01.parquet -> YELLOW
        green_tripdata_2023-01.parquet -> GREEN
        fhvhv_tripdata_2023-01.parquet -> HVFHV
    """
    filename = Path(path).stem.lower()

    if filename.startswith("yellow"):
        return DatasetType.YELLOW
    elif filename.startswith("green"):
        return DatasetType.GREEN
    elif filename.startswith("fhvhv") or filename.startswith("hvfhv"):
        return DatasetType.HVFHV

    return None  # Will need to detect from data


def normalize_schema(
    df: pd.DataFrame,
    dataset_type: Optional[DatasetType] = None,
    source_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Normalize TLC data to canonical schema.

    Args:
        df: Raw TLC DataFrame
        dataset_type: Dataset type (auto-detected if None)
        source_path: Source file path (helps with detection)

    Returns:
        DataFrame with normalized column names

    Raises:
        ValueError if required columns are missing
    """
    # Auto-detect dataset type
    if dataset_type is None:
        if source_path:
            dataset_type = detect_dataset_type_from_path(source_path)
        if dataset_type is None:
            dataset_type = detect_dataset_type(df)

    schema = SCHEMAS[dataset_type]

    # Check required columns exist
    required = [
        schema.pickup_datetime,
        schema.dropoff_datetime,
        schema.pickup_zone,
        schema.dropoff_zone,
        schema.trip_distance,
        schema.fare_amount,
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns for {dataset_type.value}: {missing}"
        )

    # Select columns (handle optional total_amount)
    columns_to_select = [
        schema.pickup_datetime,
        schema.dropoff_datetime,
        schema.pickup_zone,
        schema.dropoff_zone,
        schema.trip_distance,
        schema.fare_amount,
    ]

    # Add total_amount if exists, otherwise use fare_amount
    if schema.total_amount in df.columns:
        columns_to_select.append(schema.total_amount)
        has_total = True
    else:
        has_total = False

    result = df[columns_to_select].copy()

    # Rename to canonical names
    canonical_names = [
        "pickup_datetime",
        "dropoff_datetime",
        "pickup_zone",
        "dropoff_zone",
        "trip_distance",
        "fare_amount",
    ]
    if has_total:
        canonical_names.append("total_amount")

    result.columns = canonical_names

    # If no total_amount, duplicate fare_amount
    if not has_total:
        result["total_amount"] = result["fare_amount"]

    # Add dataset type column
    result["dataset_type"] = dataset_type.value

    # Compute derived columns
    result["pickup_datetime"] = pd.to_datetime(result["pickup_datetime"])
    result["dropoff_datetime"] = pd.to_datetime(result["dropoff_datetime"])
    result["duration_sec"] = (
        result["dropoff_datetime"] - result["pickup_datetime"]
    ).dt.total_seconds()

    return result


def validate_boundary(df: pd.DataFrame, prereg: dict) -> dict:
    """
    Validate data against preregistered boundary.

    Checks:
    - Time range
    - Dataset types
    - Schema drift (column presence)

    Returns:
        dict with validation status, warnings, and metadata
    """
    boundary = prereg.get("boundary", {})
    warnings = []
    schema_drift_detected = False

    # Check time range
    time_range = boundary.get("time_range", {})
    if time_range:
        start = pd.Timestamp(time_range.get("start"))
        end = pd.Timestamp(time_range.get("end"))

        actual_start = df["pickup_datetime"].min()
        actual_end = df["pickup_datetime"].max()

        if actual_start < start:
            warnings.append(f"Data starts before prereg: {actual_start} < {start}")
        if actual_end > end:
            warnings.append(f"Data ends after prereg: {actual_end} > {end}")

    # Check dataset types
    allowed_types = boundary.get("dataset_type", [])
    if allowed_types and "dataset_type" in df.columns:
        actual_types = df["dataset_type"].unique().tolist()
        unexpected = [t for t in actual_types if t not in allowed_types]
        if unexpected:
            warnings.append(f"Unexpected dataset types: {unexpected}")
            schema_drift_detected = True

    # Build result
    result = {
        "valid": len(warnings) == 0,
        "warnings": warnings,
        "schema_drift_detected": schema_drift_detected,
        "actual_range": {
            "start": str(df["pickup_datetime"].min()),
            "end": str(df["pickup_datetime"].max()),
        },
        "record_count": len(df),
    }

    if "dataset_type" in df.columns:
        result["dataset_types"] = df["dataset_type"].unique().tolist()

    return result


def get_schema_fingerprint(df: pd.DataFrame) -> dict:
    """
    Generate a schema fingerprint for drift detection.

    Use this to detect when TLC changes their data format.
    """
    return {
        "columns": sorted(df.columns.tolist()),
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "n_columns": len(df.columns),
    }
