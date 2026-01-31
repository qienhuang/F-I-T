from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class DualOracleDataset:
    ids: np.ndarray
    X: pd.DataFrame
    X_z: np.ndarray  # standardized features (mean/std over all rows)
    pae_value: np.ndarray  # may contain nan
    msa_depth: np.ndarray  # may contain nan
    y_pae: np.ndarray  # 0/1, but meaningful only where pae_available
    y_msa: np.ndarray  # 0/1, meaningful only where msa_available
    c3: np.ndarray  # -log1p(msa_depth); nan where msa unavailable
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
    if pae_field in feature_whitelist or msa_field in feature_whitelist:
        raise ValueError("Boundary violation: oracle field included as a feature.")

    work_cols = [id_field] + feature_whitelist + [pae_field, msa_field]
    for c in work_cols:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")

    work = df[work_cols].copy()
    if drop_na_features:
        work = work.dropna(subset=feature_whitelist)

    # oracles may be missing (union mode)
    pae_value = pd.to_numeric(work[pae_field], errors="coerce").to_numpy(dtype=float)
    msa_depth = pd.to_numeric(work[msa_field], errors="coerce").to_numpy(dtype=float)
    pae_available = np.isfinite(pae_value)
    msa_available = np.isfinite(msa_depth)

    if drop_na_oracles:
        keep = pae_available & msa_available
        work = work[keep].reset_index(drop=True)
        pae_value = pae_value[keep]
        msa_depth = msa_depth[keep]
        pae_available = pae_available[keep]
        msa_available = msa_available[keep]

    ids = work[id_field].astype(str).to_numpy()
    X = work[feature_whitelist].copy()

    y_pae = np.zeros(len(ids), dtype=int)
    y_msa = np.zeros(len(ids), dtype=int)
    y_pae[pae_available] = (pae_value[pae_available] >= float(tau_pae)).astype(int)
    y_msa[msa_available] = (msa_depth[msa_available] <= float(tau_msa_depth)).astype(int)

    c3 = np.full(len(ids), np.nan, dtype=float)
    c3[msa_available] = (-np.log1p(msa_depth[msa_available])).astype(float)

    # Standardize features using all rows (allowed: unlabeled feature stats)
    X_np = X.to_numpy(dtype=float)
    mu = np.nanmean(X_np, axis=0)
    sigma = np.nanstd(X_np, axis=0)
    sigma = np.where(sigma <= 1e-12, 1.0, sigma)
    X_z = (X_np - mu) / sigma

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
        X_z=X_z,
        pae_value=pae_value,
        msa_depth=msa_depth,
        y_pae=y_pae,
        y_msa=y_msa,
        c3=c3,
        pae_available=pae_available,
        msa_available=msa_available,
        meta=meta,
    )
