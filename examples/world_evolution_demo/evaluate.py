#!/usr/bin/env python3
"""
Evaluation for world-evolution traces under FIT-style gates.

We define per-run event time t* as first t where magnetization <= theta.
Negative window: t <= t* - delta_safe
Positive window: t* - H_pos <= t < t*

Detector:
- compute score time series s(t)
- calibrate threshold tau_f on NEG windows via quantile (1-f) pooling all neg points
- compute achieved FPR on NEG windows
- compute coverage on POS windows
- compute lead time: first alarm time in [0, t*) (or None)

This is a minimal, deterministic implementation for demo purposes.
"""
import argparse, json, os, math, statistics
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict
from features import compute_score

def load_traces(path: str) -> Dict[str, List[Dict[str, Any]]]:
    runs = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            runs[row["run_id"]].append(row)
    # ensure sorted by t
    for k in runs:
        runs[k].sort(key=lambda r: r["t"])
    return runs

def find_t_star(run: List[Dict[str, Any]], theta: float) -> Optional[int]:
    for row in run:
        if row["magnetization"] <= theta:
            return int(row["t"])
    return None

def quantile(xs: List[float], q: float) -> float:
    if not xs:
        return float("inf")
    xs_sorted = sorted(xs)
    # q in [0,1], return xs at ceil(q*(n-1))
    n = len(xs_sorted)
    idx = int(math.ceil(q*(n-1)))
    idx = max(0, min(n-1, idx))
    return xs_sorted[idx]

def eval_candidate(
    runs: Dict[str, List[Dict[str, Any]]],
    base_series: str,
    score: str,
    W: int,
    smoothing_alpha: float,
    theta: float,
    delta_safe: int,
    H_pos: int,
    fpr_targets: List[float],
    eps: float,
    floor_max: float,
    min_targets_ok: int,
) -> Dict[str, Any]:
    # Build pooled NEG scores and POS scores per target
    neg_scores = []
    pos_scores = []
    tstars = {}
    # Per-run series
    for run_id, run in runs.items():
        t_star = find_t_star(run, theta)
        tstars[run_id] = t_star
        if t_star is None:
            continue
        series = [float(r[base_series]) for r in run]
        s = compute_score(series, score=score, W=W, smoothing_alpha=smoothing_alpha)
        for t, st in enumerate(s):
            if t <= t_star - delta_safe:
                neg_scores.append(st)
            if (t_star - H_pos) <= t < t_star:
                pos_scores.append(st)

    # If no event, inconclusive
    if len(neg_scores) < 50 or len(pos_scores) < 20:
        return {
            "label": "INCONCLUSIVE",
            "t_star_by_run": tstars,
            "gate": {"passed": False, "reason": "insufficient neg/pos samples"},
        }

    achieved_table = []
    ok_targets = 0
    f_min = 1.0
    taus = {}
    for f in fpr_targets:
        tau = quantile(neg_scores, 1.0 - f)
        taus[f] = tau
        # achieved fpr on neg
        achieved = sum(1 for x in neg_scores if x >= tau) / len(neg_scores)
        achieved_table.append({"target": f, "achieved": achieved, "tau": tau})
        f_min = min(f_min, achieved)
        if abs(achieved - f) <= eps:
            ok_targets += 1

    gate_pass = (ok_targets >= min_targets_ok) and (f_min <= floor_max)
    label = "RANK_ONLY"
    util = {}
    if gate_pass:
        # pick an operating fpr (use first: 0.05 if exists else first)
        # compute coverage + lead time per run at that tau
        op = 0.05 if 0.05 in fpr_targets else fpr_targets[0]
        tau = taus[op]
        # coverage on pooled pos
        coverage = sum(1 for x in pos_scores if x >= tau) / len(pos_scores)
        # lead time per run: first t where s(t) >= tau
        leads = []
        for run_id, run in runs.items():
            t_star = tstars.get(run_id)
            if t_star is None:
                continue
            series = [float(r[base_series]) for r in run]
            s = compute_score(series, score=score, W=W, smoothing_alpha=smoothing_alpha)
            t_alarm = None
            for t, st in enumerate(s[:t_star]):
                if st >= tau:
                    t_alarm = t
                    break
            if t_alarm is not None:
                leads.append(t_star - t_alarm)
        if leads:
            util = {
                "operating_fpr": op,
                "coverage": coverage,
                "lead_time_median": statistics.median(leads),
                "lead_time_iqr": (statistics.quantiles(leads, n=4)[2] - statistics.quantiles(leads, n=4)[0]) if len(leads) >= 4 else None,
            }
            label = "SUPPORTED_FOR_ALARM"
        else:
            util = {"operating_fpr": op, "coverage": coverage, "lead_time_median": None, "lead_time_iqr": None}
            label = "SCOPE_LIMITED"

    return {
        "label": label,
        "t_star_by_run": tstars,
        "gate": {
            "passed": gate_pass,
            "achieved_fpr": achieved_table,
            "fpr_min": f_min,
            "ok_targets": ok_targets,
            "params": {"eps": eps, "floor_max": floor_max, "min_targets_ok": min_targets_ok},
        },
        "utility": util,
        "counts": {"neg_n": len(neg_scores), "pos_n": len(pos_scores)},
    }
