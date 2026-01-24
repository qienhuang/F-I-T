from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class Event:
    found: bool
    round_index: Optional[int]
    reason: str


def detect_covjump(tpr_series: List[float], W_jump: int, delta_tpr: float) -> Event:
    if len(tpr_series) <= W_jump:
        return Event(False, None, "too short")
    for i in range(W_jump, len(tpr_series)):
        if (tpr_series[i] - tpr_series[i - W_jump]) >= float(delta_tpr):
            return Event(True, i, f"jump >= {delta_tpr} at round {i} vs {i-W_jump}")
    return Event(False, None, "no jump")

