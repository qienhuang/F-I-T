from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class DualOracleDataset:
    ids: np.ndarray
    X: pd.DataFrame
    pae_value: np.ndarray
    msa_depth: np.ndarray
    y_pae: np.ndarray
    y_msa: np.ndarray
    c3: np.ndarray
    pae_available: np.ndarray
    msa_available: np.ndarray
    meta: Dict[str, str]

def build_dual_oracle_dataset(
    df: pd.DataFrame,
    id_field: str,
    feature_whitelist: List[str],
    pae_field: str,
    msa_field: str,
    tau_pae: float,
    tau_msa_depth: float,
    drop_na_features: bool,
    drop_na_oracles: bool,
) -> DualOracleDataset:
    # Guardrails: oracle fields must not be features
    if pae_field in feature_whitelist or msa_field in feature_whitelist:
        raise ValueError("Boundary violation: oracle field included as a feature.")

    work_cols = [id_field] + feature_whitelist + [pae_field, msa_field]
    for c in work_cols:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")

    work = df[work_cols].copy()
    if drop_na_features:
        work = work.dropna(subset=feature_whitelist)

    # Determine oracle availability
    pae_available = np.isfinite(work[pae_field].astype(float).to_numpy())
    msa_available = np.isfinite(work[msa_field].astype(float).to_numpy())

    if drop_na_oracles:
        work = work[np.isfinite(work[pae_field].astype(float)) & np.isfinite(work[msa_field].astype(float))]

    # Recompute availability after filtering
    pae_available = np.isfinite(work[pae_field].astype(float).to_numpy())
    msa_available = np.isfinite(work[msa_field].astype(float).to_numpy())

    ids = work[id_field].astype(str).to_numpy()
    X = work[feature_whitelist].copy()

    pae_value = work[pae_field].astype(float).to_numpy()
    msa_depth = work[msa_field].astype(float).to_numpy()

    y_pae = (pae_value >= float(tau_pae)).astype(int)
    y_msa = (msa_depth <= float(tau_msa_depth)).astype(int)
    c3 = (-np.log1p(msa_depth)).astype(float)

    meta = {
        "n_total": str(len(ids)),
        "tau_pae": str(tau_pae),
        "tau_msa_depth": str(tau_msa_depth),
        "pae_available_rate": f"{float(pae_available.mean()):.6f}" if len(pae_available) else "nan",
        "msa_available_rate": f"{float(msa_available.mean()):.6f}" if len(msa_available) else "nan",
    }
    return DualOracleDataset(
        ids=ids,
        X=X,
        pae_value=pae_value,
        msa_depth=msa_depth,
        y_pae=y_pae,
        y_msa=y_msa,
        c3=c3,
        pae_available=pae_available,
        msa_available=msa_available,
        meta=meta,
    )
