from __future__ import annotations
import numpy as np

def frac_ge(x: np.ndarray, thr: float) -> float:
    return float(np.mean(x >= thr))

def frac_lt(x: np.ndarray, thr: float) -> float:
    return float(np.mean(x < thr))

def mean(x: np.ndarray) -> float:
    return float(np.mean(x))

def hist4_entropy(plddt: np.ndarray) -> float:
    # 4 bins: [0,50), [50,70), [70,90), [90,101)
    bins = [0, 50, 70, 90, 101]
    counts, _ = np.histogram(plddt, bins=bins)
    s = counts.sum()
    if s <= 0:
        return 0.0
    p = counts / s
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())
