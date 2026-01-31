import pandas as pd
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schema import normalize_schema


def test_normalize_schema_accepts_aliases():
    df = pd.DataFrame(
        {
            "transit_timestamp": ["2020-01-01T00:00:00", "2020-01-01T01:00:00"],
            "station_complex_id": ["S001", "S002"],
            "ridership": [10, 20],
        }
    )
    out = normalize_schema(df)
    assert set(out.columns) == {"timestamp", "station_id", "ridership"}


def test_missing_columns_raises():
    df = pd.DataFrame({"a": [1], "b": [2]})
    with pytest.raises(ValueError):
        normalize_schema(df)
