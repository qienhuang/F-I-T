from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TrainedModel:
    feature_names: list[str]
    impute_values: list[float]
    standardize: bool
    mean: list[float] | None
    std: list[float] | None
    coef: list[float]  # intercept first, then weights aligned to feature_names


def _sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-z))


def _impute_fit(X: np.ndarray, strategy: str) -> np.ndarray:
    if strategy == "median":
        return np.nanmedian(X, axis=0)
    if strategy == "mean":
        return np.nanmean(X, axis=0)
    if strategy == "zero":
        return np.zeros((X.shape[1],), dtype=np.float64)
    raise ValueError(f"Unsupported impute_strategy: {strategy} (supported: median|mean|zero)")


def _impute_apply(X: np.ndarray, impute_values: np.ndarray) -> np.ndarray:
    X2 = np.asarray(X, dtype=np.float64).copy()
    mask = np.isnan(X2)
    if mask.any():
        X2[mask] = np.take(impute_values, np.where(mask)[1])
    return X2


def _standardize_fit(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std <= 1e-12, 1.0, std)
    return mean, std


def _standardize_apply(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (X - mean) / std


def _class_weights(y: np.ndarray, mode: str | None) -> np.ndarray:
    if mode is None:
        return np.ones_like(y, dtype=np.float64)
    if mode != "balanced":
        raise ValueError(f"Unsupported class_weight: {mode} (supported: balanced|None)")
    y = y.astype(int)
    n = int(len(y))
    pos = int(y.sum())
    neg = int(n - pos)
    if pos == 0 or neg == 0:
        return np.ones_like(y, dtype=np.float64)
    w_pos = n / (2.0 * pos)
    w_neg = n / (2.0 * neg)
    return np.where(y == 1, w_pos, w_neg).astype(np.float64)


def _train_logreg_irls(
    X: np.ndarray,
    y: np.ndarray,
    sample_weight: np.ndarray,
    l2_lambda: float,
    max_iter: int,
    tol: float,
) -> np.ndarray:
    y = y.astype(np.float64).reshape(-1)
    n, d = X.shape
    Xd = np.concatenate([np.ones((n, 1), dtype=np.float64), X.astype(np.float64)], axis=1)
    w = np.zeros((d + 1,), dtype=np.float64)

    reg = np.zeros((d + 1,), dtype=np.float64)
    reg[1:] = float(l2_lambda)

    for _ in range(int(max_iter)):
        z = Xd @ w
        p = _sigmoid(z)
        r = (p * (1.0 - p)) * sample_weight
        r = np.clip(r, 1e-12, None)

        # Gradient: X^T (p - y) + lambda*w
        g = Xd.T @ ((p - y) * sample_weight) + reg * w

        # Hessian: X^T R X + lambda*I
        XR = Xd * r[:, None]
        H = Xd.T @ XR
        H[np.diag_indices_from(H)] += reg

        step = np.linalg.solve(H, g)
        w_new = w - step

        if float(np.max(np.abs(step))) < float(tol):
            w = w_new
            break
        w = w_new

    return w


def train_logreg(
    X: pd.DataFrame,
    y: np.ndarray,
    standardize: bool,
    impute_strategy: str,
    params: Dict[str, Any],
) -> TrainedModel:
    feature_names = list(X.columns)
    Xnp = np.asarray(X.to_numpy(), dtype=np.float64)

    impute_values = _impute_fit(Xnp, str(impute_strategy))
    Xnp = _impute_apply(Xnp, impute_values)

    mean = std = None
    if standardize:
        mean, std = _standardize_fit(Xnp)
        Xnp = _standardize_apply(Xnp, mean, std)

    C = float(params.get("C", 1.0))
    l2_lambda = 1.0 / max(C, 1e-12)
    max_iter = int(params.get("max_iter", 200))
    tol = float(params.get("tol", 1e-6))

    cw = params.get("class_weight", None)
    if isinstance(cw, dict):
        raise ValueError("class_weight dict not supported; use null or 'balanced'")
    sample_weight = _class_weights(np.asarray(y, dtype=int), mode=str(cw) if cw is not None else None)

    coef = _train_logreg_irls(
        X=Xnp, y=np.asarray(y, dtype=np.float64), sample_weight=sample_weight, l2_lambda=l2_lambda, max_iter=max_iter, tol=tol
    )

    return TrainedModel(
        feature_names=feature_names,
        impute_values=[float(x) for x in impute_values.tolist()],
        standardize=bool(standardize),
        mean=[float(x) for x in mean.tolist()] if mean is not None else None,
        std=[float(x) for x in std.tolist()] if std is not None else None,
        coef=[float(x) for x in coef.tolist()],
    )


def predict_proba(model: TrainedModel, X: pd.DataFrame) -> np.ndarray:
    feats = model.feature_names
    Xnp = np.asarray(X[feats].to_numpy(), dtype=np.float64)
    impute_values = np.asarray(model.impute_values, dtype=np.float64)
    Xnp = _impute_apply(Xnp, impute_values)
    if model.standardize:
        if model.mean is None or model.std is None:
            raise ValueError("Model is marked standardize=true but mean/std are missing")
        Xnp = _standardize_apply(Xnp, np.asarray(model.mean), np.asarray(model.std))
    coef = np.asarray(model.coef, dtype=np.float64)
    z = coef[0] + Xnp @ coef[1:]
    return _sigmoid(z)


def coefficients(model: TrainedModel) -> Optional[Dict[str, float]]:
    try:
        coef = np.asarray(model.coef, dtype=np.float64).reshape(-1)
        w = coef[1:]
        return {n: float(c) for n, c in zip(model.feature_names, w)}
    except Exception:
        return None


def to_dict(model: TrainedModel) -> Dict[str, Any]:
    return {
        "format": "fit_proxy_alarm_kit_logreg_v0",
        "feature_names": list(model.feature_names),
        "impute_values": list(model.impute_values),
        "standardize": bool(model.standardize),
        "mean": list(model.mean) if model.mean is not None else None,
        "std": list(model.std) if model.std is not None else None,
        "coef": list(model.coef),
    }


def from_dict(d: Dict[str, Any]) -> TrainedModel:
    if str(d.get("format")) != "fit_proxy_alarm_kit_logreg_v0":
        raise ValueError("Unsupported model format")
    return TrainedModel(
        feature_names=[str(x) for x in d["feature_names"]],
        impute_values=[float(x) for x in d["impute_values"]],
        standardize=bool(d["standardize"]),
        mean=[float(x) for x in d["mean"]] if d.get("mean") is not None else None,
        std=[float(x) for x in d["std"]] if d.get("std") is not None else None,
        coef=[float(x) for x in d["coef"]],
    )
