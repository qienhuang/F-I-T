from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .utils_hash import hash_to_unit_interval

@dataclass(frozen=True)
class SplitIdx:
    train: np.ndarray
    val: np.ndarray
    test: np.ndarray

def split_ids(ids: np.ndarray, seed_string: str, train_frac: float, val_frac: float, test_frac: float) -> SplitIdx:
    s = float(train_frac + val_frac + test_frac)
    if abs(s - 1.0) > 1e-6:
        raise ValueError(f"Split fractions must sum to 1.0. Got {s}")
    u = np.array([hash_to_unit_interval(str(i), seed_string) for i in ids], dtype=float)
    idx = np.arange(len(ids))
    train = idx[u < train_frac]
    val = idx[(u >= train_frac) & (u < train_frac + val_frac)]
    test = idx[u >= train_frac + val_frac]
    return SplitIdx(train=train, val=val, test=test)
