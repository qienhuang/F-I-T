from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ConstraintEstimatorResult:
    c_dim_collapse: float
    c_mixing: float
    c_label_entropy_inv: float
    c_label_purity: float
    d_eff: float


def effective_dimension_from_pca_variance(pca_var: np.ndarray) -> float:
    """
    Participation ratio of PCA variance.
    - If variance is concentrated in few PCs -> low effective dimension.
    - If variance is spread -> high effective dimension.
    """
    v = np.asarray(pca_var, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return float("nan")
    s1 = float(np.sum(v))
    s2 = float(np.sum(v * v))
    if s1 <= 0 or s2 <= 0:
        return float("nan")
    return (s1 * s1) / s2


def mixing_fraction_from_edges(edges: pd.DataFrame, label_col: str = "label") -> float:
    """
    Fraction of kNN edges that connect different labels (e.g., fate/celltype bins).
    Higher => more mixing (less constraint).
    """
    if edges.empty:
        return float("nan")
    a = edges[f"{label_col}_src"].to_numpy()
    b = edges[f"{label_col}_dst"].to_numpy()
    return float(np.mean(a != b))


def label_entropy_inv(window_cells: pd.DataFrame, label_col: str = "label") -> float:
    """
    1 - (normalized label entropy) within a window.
    - 0 means maximally mixed labels (least constrained).
    - 1 means single-label window (most constrained).
    """
    if window_cells.empty or label_col not in window_cells.columns:
        return float("nan")
    labels = window_cells[label_col].astype(str)
    counts = labels.value_counts(dropna=False).to_numpy(dtype=float)
    if counts.size == 0:
        return float("nan")
    p = counts / float(np.sum(counts))
    p = p[p > 0]
    if p.size == 0:
        return float("nan")
    h = float(-np.sum(p * np.log(p)))
    k = int(len(counts))
    if k <= 1:
        return 1.0
    h_norm = h / float(np.log(k))
    return float(1.0 - h_norm)


def label_purity(window_cells: pd.DataFrame, label_col: str = "label") -> float:
    """
    Max label mass within a window.
    - 1 means single-label window (most constrained).
    - Lower values mean more mixed composition.
    """
    if window_cells.empty or label_col not in window_cells.columns:
        return float("nan")
    labels = window_cells[label_col].astype(str)
    counts = labels.value_counts(dropna=False).to_numpy(dtype=float)
    if counts.size == 0:
        return float("nan")
    return float(np.max(counts) / float(np.sum(counts)))


def compute_constraint_estimators(window_cells: pd.DataFrame, edges_in_window: pd.DataFrame) -> ConstraintEstimatorResult:
    # Proxy 1: inverse effective dimension within window (higher => more constrained).
    #
    # IMPORTANT: this must be computed *per window*.
    # Using global PCA variance (constant across all windows) makes the estimator constant and
    # produces undefined rank correlation (Spearman rho = NaN).
    pc_cols = [c for c in window_cells.columns if c.startswith("pc")]
    if not pc_cols or len(window_cells) < 3:
        c_dim_collapse = float("nan")
        d_eff = float("nan")
    else:
        X = window_cells[pc_cols].to_numpy(dtype=float)
        v = np.nanvar(X, axis=0, ddof=1)
        d_eff = effective_dimension_from_pca_variance(v)
        c_dim_collapse = 1.0 / d_eff if d_eff and math.isfinite(d_eff) and d_eff > 0 else float("nan")

    # Proxy 2: inverse mixing fraction (higher => more constrained).
    mix = mixing_fraction_from_edges(edges_in_window)
    c_mixing = 1.0 - mix if math.isfinite(mix) else float("nan")

    c_label_entropy_inv = label_entropy_inv(window_cells, label_col="label")
    c_label_purity = label_purity(window_cells, label_col="label")

    return ConstraintEstimatorResult(
        c_dim_collapse=c_dim_collapse,
        c_mixing=c_mixing,
        c_label_entropy_inv=c_label_entropy_inv,
        c_label_purity=c_label_purity,
        d_eff=float(d_eff) if math.isfinite(d_eff) else float("nan"),
    )
