from __future__ import annotations
import numpy as np

def robust_scale_0_1(x: np.ndarray, lower_q: float = 0.05, upper_q: float = 0.95) -> np.ndarray:
    xv = x.astype(float)
    lo = np.nanquantile(xv, lower_q)
    hi = np.nanquantile(xv, upper_q)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return np.clip(xv, 0.0, 1.0)
    y = (xv - lo) / (hi - lo)
    return np.clip(y, 0.0, 1.0)

def geometric_mean(arrs: list[np.ndarray], eps: float = 1e-12) -> np.ndarray:
    prod = np.ones_like(arrs[0], dtype=float)
    for a in arrs:
        prod *= np.clip(a.astype(float), eps, None)
    return prod ** (1.0 / len(arrs))
