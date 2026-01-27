#!/usr/bin/env python3
"""
Feature + detector utilities for the toy world traces.

We treat a detector candidate as:
- pick a base observable y(t): magnetization, density, activity
- compute a rolling score: var_y, ac1_y, trend_y, activity_mean, activity_trend
- optional smoothing (EMA)

This module is intentionally minimal and deterministic.
"""
from typing import List, Dict, Any, Optional, Tuple
import math

def ema(xs: List[float], alpha: float) -> List[float]:
    if alpha <= 0:
        return xs[:]
    out = []
    s = None
    for x in xs:
        s = x if s is None else (alpha*x + (1-alpha)*s)
        out.append(s)
    return out

def rolling_window(xs: List[float], W: int, t: int) -> List[float]:
    if W <= 1:
        return [xs[t]]
    lo = max(0, t - W + 1)
    return xs[lo:t+1]

def roll_var(xs: List[float]) -> float:
    n = len(xs)
    if n <= 1:
        return 0.0
    mu = sum(xs)/n
    return sum((x-mu)**2 for x in xs)/(n-1)

def roll_ac1(xs: List[float]) -> float:
    # lag-1 autocorr
    n = len(xs)
    if n <= 2:
        return 0.0
    x0 = xs[:-1]
    x1 = xs[1:]
    mu0 = sum(x0)/len(x0)
    mu1 = sum(x1)/len(x1)
    num = sum((a-mu0)*(b-mu1) for a,b in zip(x0,x1))
    den0 = sum((a-mu0)**2 for a in x0)
    den1 = sum((b-mu1)**2 for b in x1)
    den = math.sqrt(den0*den1) if den0>0 and den1>0 else 0.0
    return (num/den) if den>0 else 0.0

def roll_trend(xs: List[float]) -> float:
    # simple slope via least squares on indices 0..n-1
    n = len(xs)
    if n <= 2:
        return 0.0
    t = list(range(n))
    mt = (n-1)/2.0
    mx = sum(xs)/n
    num = sum((ti-mt)*(xi-mx) for ti,xi in zip(t,xs))
    den = sum((ti-mt)**2 for ti in t)
    return num/den if den>0 else 0.0

def compute_score(series: List[float], score: str, W: int, smoothing_alpha: float) -> List[float]:
    y = ema(series, smoothing_alpha)
    out = []
    for t in range(len(y)):
        w = rolling_window(y, W, t)
        if score == "const_1":
            out.append(1.0)
        elif score == "const_0":
            out.append(0.0)
        elif score == "var_y":
            out.append(roll_var(w))
        elif score == "ac1_y":
            out.append(roll_ac1(w))
        elif score == "trend_y":
            out.append(roll_trend(w))
        elif score == "activity_mean":
            out.append(sum(w)/len(w))
        elif score == "activity_trend":
            out.append(roll_trend(w))
        else:
            raise ValueError(f"Unknown score: {score}")
    return out
