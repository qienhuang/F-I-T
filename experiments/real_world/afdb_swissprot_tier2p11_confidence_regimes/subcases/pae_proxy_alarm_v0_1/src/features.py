from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class DatasetXY:
    X: pd.DataFrame
    y: np.ndarray
    ids: np.ndarray
    meta: Dict[str, str]

def build_xy(
    df: pd.DataFrame,
    id_field: str,
    feature_whitelist: List[str],
    label_field: str,
    tau_pae: float,
    drop_na_features: bool,
    drop_na_label: bool,
) -> DatasetXY:
    if id_field not in df.columns:
        raise ValueError(f"id_field '{id_field}' not found")
    if label_field not in df.columns:
        raise ValueError(f"label_field '{label_field}' not found")

    # Guardrail: label field must not appear in feature list
    if label_field in feature_whitelist:
        raise ValueError("Boundary violation: label_field is included as a feature.")

    missing_feats = [c for c in feature_whitelist if c not in df.columns]
    if missing_feats:
        raise ValueError(f"Missing feature columns: {missing_feats}")

    work = df[[id_field] + feature_whitelist + [label_field]].copy()

    if drop_na_label:
        work = work.dropna(subset=[label_field])
    if drop_na_features:
        work = work.dropna(subset=feature_whitelist)

    # Binary label
    y = (work[label_field].astype(float).to_numpy() >= float(tau_pae)).astype(int)
    ids = work[id_field].astype(str).to_numpy()
    X = work[feature_whitelist].copy()

    meta = {
        "n": str(len(work)),
        "tau_pae": str(tau_pae),
        "pos_rate": f"{float(y.mean()):.6f}",
    }
    return DatasetXY(X=X, y=y, ids=ids, meta=meta)
