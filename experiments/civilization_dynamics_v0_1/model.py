"""Core ODE model for civilization dynamics v0.1.

State: y = [x, R, gamma]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

import numpy as np


@dataclass(frozen=True)
class Params:
    r: float = 0.8
    K: float = 1.0
    A: float = 0.35
    h: float = 0.45
    d: float = 0.9
    P: float = 1.2
    a: float = 1.0
    b: float = 0.015
    c: float = 0.25
    N: float = 30.0


def gamma_star(R: float, p: Params) -> float:
    """Slow-manifold approximation for governance bandwidth."""
    return max((p.a * R - p.b * p.N) / p.c, 0.0)


def mu(x: float, R: float, gamma: float, p: Params) -> float:
    del x
    return p.d * R - p.P * gamma


def dynamics(_t: float, y: np.ndarray, p: Params) -> np.ndarray:
    x, R, gamma = y
    x = float(np.clip(x, 0.0, 1.0))
    R = float(max(R, 0.0))
    gamma = float(max(gamma, 0.0))

    m = mu(x, R, gamma, p)
    dx = x * (1.0 - x) * m

    growth = p.r * R * (1.0 - R / p.K) * (R / p.A - 1.0)
    dR = growth - p.h * x * R

    dgamma_raw = p.a * R - p.b * p.N - p.c * gamma
    # Projected dynamics to keep gamma non-negative.
    dgamma = max(dgamma_raw, 0.0) if gamma <= 0.0 else dgamma_raw
    return np.array([dx, dR, dgamma], dtype=float)


def rk4_step(
    f: Callable[[float, np.ndarray, Params], np.ndarray],
    t: float,
    y: np.ndarray,
    dt: float,
    p: Params,
) -> np.ndarray:
    k1 = f(t, y, p)
    k2 = f(t + 0.5 * dt, y + 0.5 * dt * k1, p)
    k3 = f(t + 0.5 * dt, y + 0.5 * dt * k2, p)
    k4 = f(t + dt, y + dt * k3, p)
    y_next = y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    y_next[0] = float(np.clip(y_next[0], 0.0, 1.0))
    y_next[1] = float(max(y_next[1], 0.0))
    y_next[2] = float(max(y_next[2], 0.0))
    return y_next


def simulate(
    y0: Tuple[float, float, float],
    p: Params,
    t_max: float = 400.0,
    dt: float = 0.1,
) -> Tuple[np.ndarray, np.ndarray]:
    n_steps = int(t_max / dt) + 1
    t = np.linspace(0.0, t_max, n_steps)
    y = np.zeros((n_steps, 3), dtype=float)
    y[0] = np.array(y0, dtype=float)
    for i in range(1, n_steps):
        y[i] = rk4_step(dynamics, t[i - 1], y[i - 1], dt, p)
    return t, y


def collapse_time(t: np.ndarray, y: np.ndarray, A: float) -> float:
    """First time where R <= A, np.nan if no collapse."""
    R = y[:, 1]
    idx = np.where(R <= A)[0]
    if idx.size == 0:
        return float("nan")
    return float(t[idx[0]])


def n_flip(p: Params) -> float:
    """Closed-form transcritical threshold from the essay."""
    return p.K * (p.P * p.a - p.c * p.d) / (p.P * p.b)


def n_max_star(p: Params) -> float:
    """Closed-form max sustainable scale under barrier conditions."""
    if p.r <= p.h:
        return float("nan")
    return ((p.P * p.a - p.c * p.d - p.d * p.h) * p.K * (1.0 - p.h / p.r)) / (p.P * p.b)

