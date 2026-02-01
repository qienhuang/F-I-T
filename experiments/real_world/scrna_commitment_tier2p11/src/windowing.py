from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class WindowSpec:
    scheme: str
    window_q: float
    stride_q: float
    min_cells_per_window: int
    exclude_left_q: float
    exclude_right_q: float


def _quantile_clip(x: np.ndarray, left_q: float, right_q: float) -> np.ndarray:
    if left_q <= 0 and right_q <= 0:
        return x
    lo = np.quantile(x, left_q) if left_q > 0 else -np.inf
    hi = np.quantile(x, 1.0 - right_q) if right_q > 0 else np.inf
    return np.clip(x, lo, hi)


def build_rolling_quantile_windows(df: pd.DataFrame, time_col: str, spec: WindowSpec) -> list[pd.Index]:
    if spec.scheme != "rolling_quantile":
        raise ValueError(f"Unsupported windowing scheme: {spec.scheme}")

    t = df[time_col].to_numpy(dtype=float)
    t = _quantile_clip(t, spec.exclude_left_q, spec.exclude_right_q)

    t_min, t_max = float(np.nanmin(t)), float(np.nanmax(t))
    if not np.isfinite(t_min) or not np.isfinite(t_max) or t_max <= t_min:
        return []

    # Work in quantile space [0,1] by ranking.
    order = np.argsort(t)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(t))
    q = ranks / max(1, len(t) - 1)

    windows: list[pd.Index] = []
    start = 0.0
    while start <= 1.0 - 1e-12:
        end = start + spec.window_q
        if end > 1.0:
            end = 1.0
        mask = (q >= start) & (q <= end)
        idx = df.index[mask]
        if len(idx) >= spec.min_cells_per_window:
            windows.append(idx)
        if spec.stride_q <= 0:
            break
        start += spec.stride_q
        if end >= 1.0:
            break

    return windows

