from __future__ import annotations
from pathlib import Path
import pandas as pd

def load_metrics(path: str | Path, fallback: str = "csv") -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input metrics file not found: {p}")

    if p.suffix.lower() == ".parquet":
        try:
            return pd.read_parquet(p)
        except Exception as e:
            if fallback.lower() != "csv":
                raise
            csv_path = p.with_suffix(".csv")
            if csv_path.exists():
                return pd.read_csv(csv_path)
            raise RuntimeError(f"Failed to read parquet and no csv fallback exists: {p}") from e

    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)

    try:
        return pd.read_parquet(p)
    except Exception:
        return pd.read_csv(p)

def require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

def apply_basic_filters(df: pd.DataFrame, min_len: int, max_len: int, id_field: str) -> pd.DataFrame:
    out = df.copy()
    if "length" not in out.columns:
        raise ValueError("Expected 'length' column in metrics file.")
    out = out[(out["length"] >= min_len) & (out["length"] <= max_len)]
    out = out.dropna(subset=[id_field])
    out[id_field] = out[id_field].astype(str)
    return out.reset_index(drop=True)
