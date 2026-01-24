from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Dataset:
    ids: np.ndarray
    X: pd.DataFrame
    y_reg: np.ndarray
    msa_depth: np.ndarray
    meta: Dict[str, str]

def build_dataset(
    df: pd.DataFrame,
    id_field: str,
    feature_whitelist: List[str],
    msa_depth_field: str,
    c3_field: str,
    compute_c3_from_depth_if_missing: bool,
    drop_na_features: bool,
    drop_na_label: bool,
) -> Dataset:
    if msa_depth_field not in df.columns:
        raise ValueError(f"msa_depth_field '{msa_depth_field}' not found")
    # Guardrail: label fields must not appear in features
    for lf in [msa_depth_field, c3_field]:
        if lf in feature_whitelist:
            raise ValueError("Boundary violation: label field included as a feature.")

    missing_feats = [c for c in feature_whitelist if c not in df.columns]
    if missing_feats:
        raise ValueError(f"Missing feature columns: {missing_feats}")

    cols = [id_field] + feature_whitelist + [msa_depth_field]
    has_c3 = c3_field in df.columns
    if has_c3:
        cols.append(c3_field)

    work = df[cols].copy()

    if drop_na_label:
        work = work.dropna(subset=[msa_depth_field])
        if has_c3:
            # allow c3 missing if we can compute from depth
            pass
    if drop_na_features:
        work = work.dropna(subset=feature_whitelist)

    ids = work[id_field].astype(str).to_numpy()
    X = work[feature_whitelist].copy()
    msa_depth = work[msa_depth_field].astype(float).to_numpy()

    if has_c3:
        c3 = work[c3_field].astype(float)
        # If c3 has NaN and we can compute from depth, fill
        if compute_c3_from_depth_if_missing:
            c3 = c3.fillna(-np.log1p(msa_depth))
        y_reg = c3.to_numpy(dtype=float)
    else:
        if not compute_c3_from_depth_if_missing:
            raise ValueError("C3 field missing and compute-from-depth disabled.")
        y_reg = (-np.log1p(msa_depth)).astype(float)

    # Drop any remaining NaNs in y_reg if requested
    if drop_na_label:
        m = np.isfinite(y_reg)
        ids = ids[m]
        X = X.iloc[m].reset_index(drop=True)
        msa_depth = msa_depth[m]
        y_reg = y_reg[m]

    meta = {
        "n": str(len(ids)),
        "pos_rate_placeholder": "n/a",
    }
    return Dataset(ids=ids, X=X, y_reg=y_reg, msa_depth=msa_depth, meta=meta)
