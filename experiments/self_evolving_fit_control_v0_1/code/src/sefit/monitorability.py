from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class AlarmPoint:
    t: int
    score: float
    is_positive_window: bool


@dataclass(frozen=True)
class AlarmFeasibilityResult:
    target_fpr: float
    achieved_fpr: float
    threshold: float
    has_any_true_trigger: bool


def _achieved_fpr(points: List[AlarmPoint], threshold: float) -> float:
    negatives = [p for p in points if not p.is_positive_window]
    if not negatives:
        return 0.0
    fp = sum(1 for p in negatives if p.score >= threshold)
    return float(fp / len(negatives))


def _has_any_tp(points: List[AlarmPoint], threshold: float) -> bool:
    positives = [p for p in points if p.is_positive_window]
    return any(p.score >= threshold for p in positives)


def _nextafter_up(x: float) -> float:
    try:
        return float(math.nextafter(x, math.inf))
    except AttributeError:
        return float(x + 1e-12 * (abs(x) + 1.0))


def _candidate_thresholds(scores: List[float]) -> List[float]:
    xs = sorted(set(float(x) for x in scores))
    # Include just-above each unique score to allow strict exclusion under >=.
    eps = [_nextafter_up(x) for x in xs]
    return sorted(set(xs + eps + [math.inf]))


def calibrate_threshold_to_target_fpr(neg_scores: List[float], target_fpr: float) -> float:
    """
    Pick the smallest threshold (under a >= rule) whose achieved FPR is <= target_fpr.
    """
    if not neg_scores:
        return math.inf
    candidates = _candidate_thresholds(neg_scores)
    for theta in candidates:
        # achieved FPR for negatives only
        fp = sum(1 for x in neg_scores if float(x) >= theta)
        achieved = float(fp / len(neg_scores))
        if achieved <= target_fpr:
            return float(theta)
    return math.inf


def check_alarm_feasibility(points: List[AlarmPoint], target_fpr: float) -> AlarmFeasibilityResult:
    neg_scores = [p.score for p in points if not p.is_positive_window]
    theta = calibrate_threshold_to_target_fpr(neg_scores, target_fpr=target_fpr)
    achieved = _achieved_fpr(points, threshold=theta)
    tp = _has_any_tp(points, threshold=theta)
    return AlarmFeasibilityResult(
        target_fpr=target_fpr,
        achieved_fpr=achieved,
        threshold=theta,
        has_any_true_trigger=tp,
    )


def fpr_floor(points: List[AlarmPoint]) -> float:
    """
    Minimal achievable FPR among thresholds that still yield any true trigger.

    This matches the practical "alarm feasibility" notion:
    you may be able to drive FPR to 0 by setting an infinite threshold, but then you trigger nothing.
    """
    neg_scores = [p.score for p in points if not p.is_positive_window]
    all_scores = [p.score for p in points]
    if not neg_scores or not all_scores:
        return 0.0

    floor: Optional[float] = None
    for theta in _candidate_thresholds(all_scores):
        if not _has_any_tp(points, threshold=theta):
            continue
        achieved = _achieved_fpr(points, threshold=theta)
        floor = achieved if floor is None else min(floor, achieved)

    return float(floor if floor is not None else 1.0)


def monitorability_loss(points: List[AlarmPoint], target_fpr: float) -> Tuple[bool, AlarmFeasibilityResult, float]:
    """
    E_lock proxy:
    - if no threshold can drive achieved FPR <= target_fpr while still allowing any TP, we consider alarms infeasible.
    v0.1 uses a calibrated threshold and a floor diagnostic.
    """
    result = check_alarm_feasibility(points, target_fpr=target_fpr)
    floor = fpr_floor(points)
    infeasible = (floor > target_fpr) or (not result.has_any_true_trigger)
    return infeasible, result, floor
