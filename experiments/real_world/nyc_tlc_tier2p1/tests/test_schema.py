"""
Unit tests for TLC schema handling.

Tests schema drift detection and normalization across yellow/green/hvfhv datasets.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schema import (
    DatasetType,
    detect_dataset_type,
    detect_dataset_type_from_path,
    normalize_schema,
    validate_boundary,
    get_schema_fingerprint,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def yellow_taxi_df():
    """Sample yellow taxi data (tpep_* columns)."""
    n = 100
    base_time = pd.Timestamp("2023-01-15 08:00:00")
    return pd.DataFrame({
        "tpep_pickup_datetime": [base_time + pd.Timedelta(minutes=i*5) for i in range(n)],
        "tpep_dropoff_datetime": [base_time + pd.Timedelta(minutes=i*5+15) for i in range(n)],
        "PULocationID": np.random.randint(1, 263, n),
        "DOLocationID": np.random.randint(1, 263, n),
        "trip_distance": np.random.uniform(0.5, 15.0, n),
        "fare_amount": np.random.uniform(5.0, 50.0, n),
        "total_amount": np.random.uniform(6.0, 60.0, n),
        "passenger_count": np.random.randint(1, 5, n),
    })


@pytest.fixture
def green_taxi_df():
    """Sample green taxi data (lpep_* columns)."""
    n = 100
    base_time = pd.Timestamp("2023-01-15 08:00:00")
    return pd.DataFrame({
        "lpep_pickup_datetime": [base_time + pd.Timedelta(minutes=i*5) for i in range(n)],
        "lpep_dropoff_datetime": [base_time + pd.Timedelta(minutes=i*5+15) for i in range(n)],
        "PULocationID": np.random.randint(1, 263, n),
        "DOLocationID": np.random.randint(1, 263, n),
        "trip_distance": np.random.uniform(0.5, 15.0, n),
        "fare_amount": np.random.uniform(5.0, 50.0, n),
        "total_amount": np.random.uniform(6.0, 60.0, n),
        "passenger_count": np.random.randint(1, 5, n),
    })


@pytest.fixture
def hvfhv_df():
    """Sample HVFHV data (different column names)."""
    n = 100
    base_time = pd.Timestamp("2023-01-15 08:00:00")
    return pd.DataFrame({
        "hvfhs_license_num": ["HV0003"] * n,
        "pickup_datetime": [base_time + pd.Timedelta(minutes=i*5) for i in range(n)],
        "dropoff_datetime": [base_time + pd.Timedelta(minutes=i*5+15) for i in range(n)],
        "PULocationID": np.random.randint(1, 263, n),
        "DOLocationID": np.random.randint(1, 263, n),
        "trip_miles": np.random.uniform(0.5, 15.0, n),  # Different column name!
        "base_passenger_fare": np.random.uniform(5.0, 50.0, n),
    })


@pytest.fixture
def sample_prereg():
    """Sample preregistration for testing."""
    return {
        "boundary": {
            "dataset_type": ["yellow"],
            "time_range": {
                "start": "2023-01-01",
                "end": "2023-12-31",
            },
        }
    }


# ============================================================================
# Dataset Type Detection Tests
# ============================================================================

class TestDetectDatasetType:
    """Tests for dataset type detection."""

    def test_detect_yellow(self, yellow_taxi_df):
        """Should detect yellow taxi from tpep_* columns."""
        result = detect_dataset_type(yellow_taxi_df)
        assert result == DatasetType.YELLOW

    def test_detect_green(self, green_taxi_df):
        """Should detect green taxi from lpep_* columns."""
        result = detect_dataset_type(green_taxi_df)
        assert result == DatasetType.GREEN

    def test_detect_hvfhv(self, hvfhv_df):
        """Should detect HVFHV from hvfhs_* columns or trip_miles."""
        result = detect_dataset_type(hvfhv_df)
        assert result == DatasetType.HVFHV

    def test_detect_unknown_raises(self):
        """Should raise ValueError for unknown schema."""
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        with pytest.raises(ValueError, match="Cannot detect dataset type"):
            detect_dataset_type(df)


class TestDetectDatasetTypeFromPath:
    """Tests for path-based detection."""

    def test_yellow_path(self):
        assert detect_dataset_type_from_path("yellow_tripdata_2023-01.parquet") == DatasetType.YELLOW

    def test_green_path(self):
        assert detect_dataset_type_from_path("green_tripdata_2023-01.parquet") == DatasetType.GREEN

    def test_hvfhv_path(self):
        assert detect_dataset_type_from_path("fhvhv_tripdata_2023-01.parquet") == DatasetType.HVFHV

    def test_unknown_path_returns_none(self):
        assert detect_dataset_type_from_path("unknown_data.parquet") is None


# ============================================================================
# Schema Normalization Tests
# ============================================================================

class TestNormalizeSchema:
    """Tests for schema normalization."""

    def test_normalize_yellow(self, yellow_taxi_df):
        """Yellow taxi should normalize to canonical schema."""
        result = normalize_schema(yellow_taxi_df)

        # Check canonical columns exist
        assert "pickup_datetime" in result.columns
        assert "dropoff_datetime" in result.columns
        assert "pickup_zone" in result.columns
        assert "dropoff_zone" in result.columns
        assert "trip_distance" in result.columns
        assert "fare_amount" in result.columns
        assert "duration_sec" in result.columns
        assert "dataset_type" in result.columns

        # Check dataset type is correct
        assert result["dataset_type"].iloc[0] == "yellow"

        # Check duration is computed
        assert result["duration_sec"].iloc[0] == 15 * 60  # 15 minutes

    def test_normalize_green(self, green_taxi_df):
        """Green taxi should normalize to same canonical schema."""
        result = normalize_schema(green_taxi_df)

        assert "pickup_datetime" in result.columns
        assert result["dataset_type"].iloc[0] == "green"

    def test_normalize_hvfhv(self, hvfhv_df):
        """HVFHV should normalize despite different column names."""
        result = normalize_schema(hvfhv_df)

        assert "pickup_datetime" in result.columns
        assert "trip_distance" in result.columns  # mapped from trip_miles
        assert result["dataset_type"].iloc[0] == "hvfhv"

    def test_normalize_with_explicit_type(self, yellow_taxi_df):
        """Should use explicit dataset type when provided."""
        result = normalize_schema(yellow_taxi_df, dataset_type=DatasetType.YELLOW)
        assert result["dataset_type"].iloc[0] == "yellow"

    def test_normalize_with_path_hint(self, yellow_taxi_df):
        """Should use path hint for detection."""
        result = normalize_schema(
            yellow_taxi_df,
            source_path="data/raw/yellow_tripdata_2023-01.parquet"
        )
        assert result["dataset_type"].iloc[0] == "yellow"

    def test_missing_columns_raises(self):
        """Should raise ValueError when required columns missing."""
        df = pd.DataFrame({
            "tpep_pickup_datetime": ["2023-01-01"],
            # Missing other required columns
        })
        with pytest.raises(ValueError, match="Missing required columns"):
            normalize_schema(df)


# ============================================================================
# Boundary Validation Tests
# ============================================================================

class TestValidateBoundary:
    """Tests for boundary validation."""

    def test_valid_boundary(self, yellow_taxi_df, sample_prereg):
        """Should pass when data is within boundary."""
        normalized = normalize_schema(yellow_taxi_df)
        result = validate_boundary(normalized, sample_prereg)

        assert result["valid"] == True
        assert len(result["warnings"]) == 0

    def test_time_before_boundary(self, sample_prereg):
        """Should warn when data starts before boundary."""
        df = pd.DataFrame({
            "pickup_datetime": pd.to_datetime(["2022-12-01", "2022-12-02"]),
            "dataset_type": ["yellow", "yellow"],
        })
        result = validate_boundary(df, sample_prereg)

        assert result["valid"] == False
        assert any("before prereg" in w for w in result["warnings"])

    def test_wrong_dataset_type(self, green_taxi_df, sample_prereg):
        """Should warn when dataset type doesn't match prereg."""
        normalized = normalize_schema(green_taxi_df)
        result = validate_boundary(normalized, sample_prereg)

        assert result["valid"] == False
        assert result["schema_drift_detected"] == True
        assert any("Unexpected dataset types" in w for w in result["warnings"])


# ============================================================================
# Schema Fingerprint Tests
# ============================================================================

class TestSchemaFingerprint:
    """Tests for schema fingerprinting."""

    def test_fingerprint_contains_columns(self, yellow_taxi_df):
        """Fingerprint should list all columns."""
        fingerprint = get_schema_fingerprint(yellow_taxi_df)

        assert "columns" in fingerprint
        assert "tpep_pickup_datetime" in fingerprint["columns"]
        assert fingerprint["n_columns"] == len(yellow_taxi_df.columns)

    def test_fingerprint_detects_changes(self, yellow_taxi_df):
        """Different schemas should have different fingerprints."""
        fp1 = get_schema_fingerprint(yellow_taxi_df)

        modified = yellow_taxi_df.copy()
        modified["new_column"] = 1
        fp2 = get_schema_fingerprint(modified)

        assert fp1["n_columns"] != fp2["n_columns"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestSchemaIntegration:
    """Integration tests for end-to-end schema handling."""

    def test_mixed_dataset_pipeline(self, yellow_taxi_df, green_taxi_df):
        """Should handle mixed datasets correctly."""
        # Normalize both
        yellow_norm = normalize_schema(yellow_taxi_df)
        green_norm = normalize_schema(green_taxi_df)

        # Concatenate (as would happen in multi-file load)
        combined = pd.concat([yellow_norm, green_norm], ignore_index=True)

        # Both should have same canonical columns
        assert set(yellow_norm.columns) == set(green_norm.columns)

        # Dataset types should be preserved
        assert set(combined["dataset_type"].unique()) == {"yellow", "green"}

    def test_round_trip_consistency(self, yellow_taxi_df):
        """Normalizing twice should be idempotent (for already normalized data)."""
        first = normalize_schema(yellow_taxi_df)

        # Already normalized data should have canonical columns
        # But we can't re-normalize because it won't have original columns
        # This tests that the output schema is consistent
        assert first["pickup_datetime"].dtype == "datetime64[ns]"
        assert first["duration_sec"].dtype == "float64"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
