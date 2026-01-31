from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .utils_hash import hash_to_unit_interval

@dataclass(frozen=True)
class HoldoutPoolSplit:
    holdout: np.ndarray
    pool: np.ndarray

def holdout_split(ids: np.ndarray, seed_string: str, holdout_frac: float, mask: np.ndarray | None = None) -> HoldoutPoolSplit:
    idx = np.arange(len(ids))
    if mask is not None:
        idx = idx[mask]
    u = np.array([hash_to_unit_interval(str(ids[i]), seed_string + "::holdout") for i in idx], dtype=float)
    hold = idx[u < float(holdout_frac)]
    pool = idx[u >= float(holdout_frac)]
    return HoldoutPoolSplit(holdout=hold, pool=pool)

@dataclass(frozen=True)
class LabeledSplit:
    train: np.ndarray
    val: np.ndarray

def labeled_train_val_split(ids: np.ndarray, seed_string: str, train_frac: float, val_frac: float) -> LabeledSplit:
    s = float(train_frac + val_frac)
    if abs(s - 1.0) > 1e-6:
        raise ValueError(f"train_frac + val_frac must sum to 1.0. Got {s}")
    idx = np.arange(len(ids))
    u = np.array([hash_to_unit_interval(str(ids[i]), seed_string + "::labeled") for i in idx], dtype=float)
    train = idx[u < float(train_frac)]
    val = idx[u >= float(train_frac)]
    return LabeledSplit(train=train, val=val)
