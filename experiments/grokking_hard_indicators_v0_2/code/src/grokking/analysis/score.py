from __future__ import annotations

from typing import Any

import numpy as np


def moving_average(x: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return x.copy()
    out = np.empty_like(x, dtype=np.float64)
    for i in range(len(x)):
        lo = max(0, i - window + 1)
        out[i] = float(np.mean(x[lo : i + 1]))
    return out


def compute_scores(
    checkpoints: list[dict[str, Any]],
    *,
    h_spec_layer: str,
    window_w: int,
    eps_hspec: float,
    theta_corr: float,
    w_hspec: float,
    w_corr: float,
    score_sign: float = 1.0,
) -> tuple[list[int], list[float]]:
    steps = np.asarray([int(r["step"]) for r in checkpoints], dtype=np.int64)
    h_spec = np.asarray(
        [float(r.get("H_spec_by_layer", {}).get(h_spec_layer, 0.0)) for r in checkpoints],
        dtype=np.float64,
    )
    corr = np.asarray([float(r.get("correction_rate", 0.0)) for r in checkpoints], dtype=np.float64)

    dh = np.diff(h_spec, prepend=h_spec[0])
    ma_dh = moving_average(dh, window=window_w)

    s_h = np.maximum(0.0, (-ma_dh) / max(eps_hspec, 1e-12))
    s_c = np.maximum(0.0, (corr - theta_corr) / max(1.0 - theta_corr, 1e-12))
    score = score_sign * (w_hspec * s_h + w_corr * s_c)
    return steps.tolist(), score.astype(float).tolist()
