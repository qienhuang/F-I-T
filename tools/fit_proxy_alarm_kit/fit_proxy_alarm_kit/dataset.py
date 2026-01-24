from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Dataset:
    ids: np.ndarray
    X: pd.DataFrame
    y_oracle: np.ndarray  # oracle labels (hidden until queried; offline store in this kit)
    meta: Dict[str, str]


def build_dataset(
    df: pd.DataFrame,
    id_field: str,
    feature_whitelist: List[str],
    label_field: str,
    tau_label: float,
    drop_na_features: bool,
    drop_na_label: bool,
) -> Dataset:
    # Guardrail: label field must not appear in feature list.
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

    ids = work[id_field].astype(str).to_numpy()
    X = work[feature_whitelist].copy()

    y = (work[label_field].astype(float).to_numpy() >= float(tau_label)).astype(int)

    meta = {
        "n": str(len(work)),
        "tau_label": str(tau_label),
        "pos_rate": f"{float(y.mean()):.6f}",
    }
    return Dataset(ids=ids, X=X, y_oracle=y, meta=meta)

