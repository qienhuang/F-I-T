from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score, average_precision_score

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
    return {"fpr": float(fpr), "tpr": float(tpr), "precision": float(precision), "flagged_rate": float(flagged_rate), "miss_rate": float(miss_rate)}

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

def evaluate_binary_classifier(
    y_val: np.ndarray,
    s_val: np.ndarray,
    y_test: np.ndarray,
    s_test: np.ndarray,
    fpr_targets: List[float],
) -> Dict[str, object]:
    out: Dict[str, object] = {}
    if len(np.unique(y_test)) > 1:
        out["roc_auc"] = float(roc_auc_score(y_test, s_test))
        out["pr_auc"] = float(average_precision_score(y_test, s_test))
    else:
        out["roc_auc"] = float("nan")
        out["pr_auc"] = float("nan")
    fpr, tpr, thr = roc_curve(y_test, s_test)
    out["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "thresholds": thr.tolist()}
    ops = []
    for cap in fpr_targets:
        thr_sel = choose_threshold_max_tpr_under_fpr(y_val, s_val, fpr_cap=float(cap))
        m = _metrics_at_thr(y_test, s_test, thr_sel)
        ops.append({
            "fpr_target": float(cap),
            "threshold": float(thr_sel),
            "fpr": m["fpr"],
            "tpr": m["tpr"],
            "precision": m["precision"],
            "flagged_rate": m["flagged_rate"],
            "miss_rate": m["miss_rate"],
            "usable": bool(m["tpr"] > 0.0),
        })
    out["operating_points"] = ops
    return out
