from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from .utils_hash import hash_to_unit_interval


@dataclass(frozen=True)
class Split:
    holdout: np.ndarray
    pool: np.ndarray


def holdout_split(ids: np.ndarray, seed_string: str, holdout_frac: float) -> Split:
    u = np.array([hash_to_unit_interval(str(i), seed_string + "::holdout") for i in ids], dtype=float)
    hold = np.where(u < float(holdout_frac))[0]
    pool = np.where(u >= float(holdout_frac))[0]
    return Split(holdout=hold, pool=pool)


@dataclass(frozen=True)
class LabeledSplit:
    train: np.ndarray
    val: np.ndarray


def labeled_train_val_split(ids: np.ndarray, seed_string: str, train_frac: float, val_frac: float) -> LabeledSplit:
    s = float(train_frac + val_frac)
    if abs(s - 1.0) > 1e-6:
        raise ValueError(f"train_frac + val_frac must sum to 1.0. Got {s}")
    u = np.array([hash_to_unit_interval(str(i), seed_string + "::labeled") for i in ids], dtype=float)
    train = np.where(u < float(train_frac))[0]
    val = np.where(u >= float(train_frac))[0]
    return LabeledSplit(train=train, val=val)

