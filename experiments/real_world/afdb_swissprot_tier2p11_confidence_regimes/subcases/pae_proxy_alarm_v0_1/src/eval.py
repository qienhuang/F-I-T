from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve, precision_recall_curve

@dataclass(frozen=True)
class OperatingPoint:
    fpr_target: float
    threshold: float
    fpr: float
    tpr: float
    precision: float
    flagged_rate: float
    miss_rate: float
    usable: bool

def _confusion_at_threshold(y_true: np.ndarray, scores: np.ndarray, thr: float) -> Tuple[int, int, int, int]:
    y_pred = (scores >= thr).astype(int)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    return tp, fp, tn, fn

def _fpr_tpr_prec(y_true: np.ndarray, scores: np.ndarray, thr: float) -> Tuple[float, float, float, float, float]:
    tp, fp, tn, fn = _confusion_at_threshold(y_true, scores, thr)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    flagged_rate = (tp + fp) / len(y_true) if len(y_true) > 0 else 0.0
    miss_rate = fn / len(y_true) if len(y_true) > 0 else 0.0
    return fpr, tpr, precision, flagged_rate, miss_rate

def choose_threshold_max_tpr_under_fpr(
    y_val: np.ndarray,
    s_val: np.ndarray,
    fpr_cap: float,
) -> float:
    # Use candidate thresholds from unique sorted scores (descending)
    uniq = np.unique(s_val)
    # Add +inf threshold (flags nothing)
    candidates = np.concatenate([uniq, np.array([np.inf])])
    best_thr = np.inf
    best_tpr = -1.0
    for thr in candidates:
        fpr, tpr, _, _, _ = _fpr_tpr_prec(y_val, s_val, float(thr))
        if fpr <= fpr_cap and tpr > best_tpr:
            best_tpr = tpr
            best_thr = float(thr)
    return best_thr

def evaluate_binary_classifier(
    y_train: np.ndarray, s_train: np.ndarray,
    y_val: np.ndarray, s_val: np.ndarray,
    y_test: np.ndarray, s_test: np.ndarray,
    fpr_targets: List[float],
) -> Dict[str, object]:
    out: Dict[str, object] = {}

    # Global metrics (test)
    out["test_roc_auc"] = float(roc_auc_score(y_test, s_test)) if len(np.unique(y_test)) > 1 else float("nan")
    out["test_pr_auc"] = float(average_precision_score(y_test, s_test)) if len(np.unique(y_test)) > 1 else float("nan")

    # Curves (test)
    fpr, tpr, thr = roc_curve(y_test, s_test)
    out["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "thresholds": thr.tolist()}

    prec, rec, thr_pr = precision_recall_curve(y_test, s_test)
    out["pr_curve"] = {"precision": prec.tolist(), "recall": rec.tolist(), "thresholds": thr_pr.tolist()}

    # Coverage vs FPR curve (test) from ROC curve
    out["coverage_vs_fpr"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}

    # Operating points
    ops: List[OperatingPoint] = []
    for cap in fpr_targets:
        thr_sel = choose_threshold_max_tpr_under_fpr(y_val, s_val, fpr_cap=float(cap))
        fpr_t, tpr_t, precision_t, flagged_rate_t, miss_rate_t = _fpr_tpr_prec(y_test, s_test, thr_sel)
        ops.append(
            OperatingPoint(
                fpr_target=float(cap),
                threshold=float(thr_sel),
                fpr=float(fpr_t),
                tpr=float(tpr_t),
                precision=float(precision_t),
                flagged_rate=float(flagged_rate_t),
                miss_rate=float(miss_rate_t),
                usable=bool(tpr_t > 0.0),
            )
        )
    out["operating_points"] = [op.__dict__ for op in ops]
    return out
