from __future__ import annotations

from typing import Any


def compute_t_grok(
    checkpoints: list[dict[str, Any]],
    *,
    theta_grok: float,
    hold_k: int,
    metric: str = "test_acc",
) -> int | None:
    """
    t_grok := earliest step such that `metric` is >= theta for hold_k consecutive checkpoints.
    """
    if hold_k <= 0:
        raise ValueError("hold_k must be > 0")
    acc = [float(r.get(metric, 0.0)) for r in checkpoints]
    steps = [int(r["step"]) for r in checkpoints]
    for i in range(0, len(acc) - hold_k + 1):
        if all(a >= theta_grok for a in acc[i : i + hold_k]):
            return steps[i]
    return None


def _moving_average(x: list[float], window: int) -> list[float]:
    if window <= 1:
        return list(x)
    out: list[float] = []
    s = 0.0
    for i, a in enumerate(x):
        s += float(a)
        if i >= window:
            s -= float(x[i - window])
        denom = min(i + 1, window)
        out.append(s / denom)
    return out


def compute_t_jump(
    checkpoints: list[dict[str, Any]],
    *,
    metric: str = "test_acc",
    w_jump: int,
    delta_jump: float,
    theta_floor: float,
    delta_back: float,
    hold_k: int,
) -> int | None:
    """
    Jump / regime-shift event time.

    Define smoothed metric m_smooth(t) as a trailing moving average of length w_jump (in checkpoints).
    Define delta over w_jump checkpoints: Δ(t) = m_smooth(t) - m_smooth(t - w_jump).

    Return the earliest checkpoint step where:
    - Δ(t) >= delta_jump
    - m_smooth(t) >= theta_floor
    - m_smooth does not drop by more than delta_back for the next hold_k checkpoints
    """
    if w_jump <= 0:
        raise ValueError("w_jump must be > 0")
    if hold_k <= 0:
        raise ValueError("hold_k must be > 0")

    values = [float(r.get(metric, 0.0)) for r in checkpoints]
    steps = [int(r["step"]) for r in checkpoints]
    smooth = _moving_average(values, w_jump)

    for i in range(w_jump, len(smooth)):
        delta = float(smooth[i]) - float(smooth[i - w_jump])
        if delta < float(delta_jump):
            continue
        if float(smooth[i]) < float(theta_floor):
            continue
        hi = min(len(smooth), i + hold_k)
        if hi <= i + 1:
            continue
        if min(float(v) for v in smooth[i:hi]) < (float(smooth[i]) - float(delta_back)):
            continue
        return steps[i]
    return None


def label_grok_within_horizon(*, step: int, t_grok: int | None, horizon_steps: int) -> int:
    if t_grok is None or t_grok < step:
        return 0
    return 1 if (t_grok - step) <= horizon_steps else 0
