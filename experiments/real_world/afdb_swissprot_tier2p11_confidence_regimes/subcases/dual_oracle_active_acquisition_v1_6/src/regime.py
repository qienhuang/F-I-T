from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class RegimeResult:
    label: str
    reason: str

def regime_label(
    trained: bool,
    fpr_floor_at_tpr_min: float,
    fpr: float,
    tpr: float,
    cap: float,
    tpr_min: float,
) -> RegimeResult:
    if not trained:
        return RegimeResult("UNTRAINED", "model not trained")
    if fpr_floor_at_tpr_min > cap:
        return RegimeResult("FPR_FLOOR", "FPR floor blocks cap at TPR>=tpr_min")
    if (fpr <= cap) and (tpr >= tpr_min):
        return RegimeResult("USABLE", "meets operating point at cap")
    return RegimeResult("UNUSABLE", "trained, no floor, but fails operating point")
