from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np


def _roc_auc_score(y_true: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y_true, dtype=int).reshape(-1)
    s = np.asarray(scores, dtype=np.float64).reshape(-1)
    n = int(len(y))
    pos = int(y.sum())
    neg = n - pos
    if pos == 0 or neg == 0:
        return float("nan")

    order = np.argsort(s, kind="mergesort")
    s_sorted = s[order]
    y_sorted = y[order]

    ranks = np.empty((n,), dtype=np.float64)
    i = 0
    r = 1
    while i < n:
        j = i + 1
        while j < n and s_sorted[j] == s_sorted[i]:
            j += 1
        r_low = r
        r_high = r + (j - i) - 1
        r_avg = 0.5 * (r_low + r_high)
        ranks[i:j] = r_avg
        r += j - i
        i = j

    sum_ranks_pos = float((ranks * y_sorted).sum())
    auc = (sum_ranks_pos - (pos * (pos + 1) / 2.0)) / (pos * neg)
    return float(auc)


def _average_precision_score(y_true: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y_true, dtype=int).reshape(-1)
    s = np.asarray(scores, dtype=np.float64).reshape(-1)
    pos = int(y.sum())
    if pos == 0:
        return float("nan")
    order = np.argsort(-s, kind="mergesort")
    y_sorted = y[order]
    tp = np.cumsum(y_sorted == 1)
    k = np.arange(1, len(y_sorted) + 1)
    precision = tp / k
    ap = float(precision[y_sorted == 1].sum() / pos)
    return ap


def _roc_curve(y_true: np.ndarray, scores: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    y = np.asarray(y_true, dtype=int).reshape(-1)
    s = np.asarray(scores, dtype=np.float64).reshape(-1)
    pos = int(y.sum())
    neg = int(len(y) - pos)
    if pos == 0 or neg == 0:
        return np.asarray([0.0]), np.asarray([0.0]), np.asarray([float("inf")])

    order = np.argsort(-s, kind="mergesort")
    s_sorted = s[order]
    y_sorted = y[order]

    tp = np.cumsum(y_sorted == 1)
    fp = np.cumsum(y_sorted == 0)

    distinct = np.r_[True, s_sorted[1:] != s_sorted[:-1]]
    idx = np.where(distinct)[0]

    tpr = tp[idx] / pos
    fpr = fp[idx] / neg
    thr = s_sorted[idx]

    fpr = np.r_[0.0, fpr]
    tpr = np.r_[0.0, tpr]
    thr = np.r_[np.inf, thr]
    return fpr.astype(np.float64), tpr.astype(np.float64), thr.astype(np.float64)


def _precision_recall_curve(y_true: np.ndarray, scores: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    y = np.asarray(y_true, dtype=int).reshape(-1)
    s = np.asarray(scores, dtype=np.float64).reshape(-1)
    pos = int(y.sum())
    if pos == 0:
        return np.asarray([1.0]), np.asarray([0.0]), np.asarray([])

    order = np.argsort(-s, kind="mergesort")
    s_sorted = s[order]
    y_sorted = y[order]

    tp = np.cumsum(y_sorted == 1)
    fp = np.cumsum(y_sorted == 0)

    distinct = np.r_[True, s_sorted[1:] != s_sorted[:-1]]
    idx = np.where(distinct)[0]

    prec = tp[idx] / (tp[idx] + fp[idx])
    rec = tp[idx] / pos
    thr = s_sorted[idx]

    # Match sklearn-ish convention: start at (recall=0, precision=1)
    prec = np.r_[1.0, prec]
    rec = np.r_[0.0, rec]
    return prec.astype(np.float64), rec.astype(np.float64), thr.astype(np.float64)


def _confusion(y_true: np.ndarray, scores: np.ndarray, thr: float) -> Tuple[int, int, int, int]:
    y_pred = (scores >= thr).astype(int)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    return tp, fp, tn, fn


def _metrics_at_thr(y_true: np.ndarray, scores: np.ndarray, thr: float) -> Dict[str, float]:
    tp, fp, tn, fn = _confusion(y_true, scores, thr)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    flagged_rate = (tp + fp) / len(y_true) if len(y_true) else 0.0
    miss_rate = fn / len(y_true) if len(y_true) else 0.0
    return {
        "fpr": float(fpr),
        "tpr": float(tpr),
        "precision": float(precision),
        "flagged_rate": float(flagged_rate),
        "miss_rate": float(miss_rate),
    }


def choose_threshold_max_tpr_under_fpr(y_val: np.ndarray, s_val: np.ndarray, fpr_cap: float) -> float:
    uniq = np.unique(s_val)
    candidates = np.concatenate([uniq, np.array([np.inf])])
    best_thr = float(np.inf)
    best_tpr = -1.0
    for thr in candidates:
        m = _metrics_at_thr(y_val, s_val, float(thr))
        if m["fpr"] <= fpr_cap and m["tpr"] > best_tpr:
            best_tpr = m["tpr"]
            best_thr = float(thr)
    return best_thr


def evaluate_holdout(
    y_val: np.ndarray,
    s_val: np.ndarray,
    y_test: np.ndarray,
    s_test: np.ndarray,
    fpr_targets: List[float],
) -> Dict[str, object]:
    out: Dict[str, object] = {}
    out["roc_auc"] = float(_roc_auc_score(y_test, s_test)) if len(np.unique(y_test)) > 1 else float("nan")
    out["pr_auc"] = float(_average_precision_score(y_test, s_test)) if len(np.unique(y_test)) > 1 else float("nan")

    fpr, tpr, thr = _roc_curve(y_test, s_test)
    out["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "thresholds": thr.tolist()}

    prec, rec, thr_pr = _precision_recall_curve(y_test, s_test)
    out["pr_curve"] = {"precision": prec.tolist(), "recall": rec.tolist(), "thresholds": thr_pr.tolist()}

    ops = []
    for cap in fpr_targets:
        thr_sel = choose_threshold_max_tpr_under_fpr(y_val, s_val, fpr_cap=float(cap))
        m = _metrics_at_thr(y_test, s_test, thr_sel)
        ops.append(
            {
                "fpr_target": float(cap),
                "threshold": float(thr_sel),
                "fpr": m["fpr"],
                "tpr": m["tpr"],
                "precision": m["precision"],
                "flagged_rate": m["flagged_rate"],
                "miss_rate": m["miss_rate"],
                "usable": bool(m["tpr"] > 0.0),
            }
        )
    out["operating_points"] = ops
    return out


def monitorability_gate(operating_points: list[dict], primary_fpr_target: float, fpr_tolerance: float) -> dict:
    # Declares whether a score is usable as an alarm at the primary operating point.
    op = None
    for x in operating_points:
        if float(x["fpr_target"]) == float(primary_fpr_target):
            op = x
            break
    if op is None:
        return {"status": "INVALID_CONFIG", "reason": "missing primary fpr op"}

    achieved = float(op["fpr"])
    tpr = float(op["tpr"])

    if achieved > float(primary_fpr_target) + float(fpr_tolerance):
        return {
            "status": "INVALID_ALARM",
            "reason": f"FPR_uncontrollable: achieved={achieved:.4f} target={primary_fpr_target:.4f}",
        }
    if tpr <= 0.0:
        return {"status": "WEAK_ALARM", "reason": "zero_tpr_at_primary_fpr"}
    return {"status": "USABLE", "reason": f"achieved_fpr={achieved:.4f} tpr={tpr:.4f}"}
