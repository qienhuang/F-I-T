from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass(frozen=True)
class RidgeModel:
    # y ~ b + Xw; store (b, w) and covariance for UCB.
    bias: float
    w: np.ndarray
    cov: np.ndarray  # (d+1,d+1) for [1,x] features


def fit_ridge(X: np.ndarray, y: np.ndarray, lam: float) -> RidgeModel:
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    n, d = X.shape
    Phi = np.concatenate([np.ones((n, 1), dtype=np.float64), X], axis=1)
    A = Phi.T @ Phi + float(lam) * np.eye(d + 1)
    b = Phi.T @ y
    theta = np.linalg.solve(A, b)
    cov = np.linalg.inv(A)
    return RidgeModel(bias=float(theta[0]), w=theta[1:].astype(np.float64), cov=cov.astype(np.float64))


def predict_mean_var(m: RidgeModel, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    X = np.asarray(X, dtype=np.float64)
    n = X.shape[0]
    Phi = np.concatenate([np.ones((n, 1), dtype=np.float64), X], axis=1)
    mean = m.bias + X @ m.w
    # var ~ phi^T cov phi (up to sigma^2 scaling; we treat it as relative uncertainty)
    var = np.einsum("nd,dd,nd->n", Phi, m.cov, Phi)
    var = np.clip(var, 0.0, None)
    return mean.astype(np.float64), var.astype(np.float64)

