from __future__ import annotations

import numpy as np


def roc_auc_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    y_true = y_true.astype(np.int64)
    y_score = y_score.astype(np.float64)
    n_pos = int((y_true == 1).sum())
    n_neg = int((y_true == 0).sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    order = np.argsort(-y_score, kind="mergesort")
    y_true_sorted = y_true[order]
    tps = np.cumsum(y_true_sorted == 1)
    fps = np.cumsum(y_true_sorted == 0)
    tpr = tps / n_pos
    fpr = fps / n_neg
    tpr = np.concatenate([[0.0], tpr, [1.0]])
    fpr = np.concatenate([[0.0], fpr, [1.0]])
    try:
        area = np.trapezoid(tpr, fpr)
    except AttributeError:  # numpy<2.0
        area = np.trapz(tpr, fpr)  # type: ignore[attr-defined]
    return float(area)


def average_precision(y_true: np.ndarray, y_score: np.ndarray) -> float:
    y_true = y_true.astype(np.int64)
    y_score = y_score.astype(np.float64)
    n_pos = int((y_true == 1).sum())
    if n_pos == 0:
        return float("nan")
    order = np.argsort(-y_score, kind="mergesort")
    y_true_sorted = y_true[order]
    tp = (y_true_sorted == 1).astype(np.int64)
    fp = (y_true_sorted == 0).astype(np.int64)
    tps = np.cumsum(tp)
    fps = np.cumsum(fp)
    precision = tps / np.maximum(tps + fps, 1)
    recall = tps / n_pos
    ap = 0.0
    prev_recall = 0.0
    for p, r in zip(precision, recall):
        ap += float(p) * float(r - prev_recall)
        prev_recall = float(r)
    return float(ap)


def mean_lead_time_at_fpr(*, run_summaries: list[dict], fpr_target: float) -> float:
    """
    Checkpoint-level FPR: fraction of negative checkpoints with score >= threshold.
    Lead time: for each run with `t_grok`, use the earliest trigger within the positive horizon (i.e. a checkpoint with y==1).

    This keeps the lead-time definition consistent with the binary label “grok within next N steps”.
    """
    all_scores: list[float] = []
    for r in run_summaries:
        all_scores.extend([float(s) for s in r["scores"]])
    if not all_scores:
        return float("nan")
    thresholds = np.unique(np.asarray(all_scores, dtype=np.float64))[::-1]

    best_fpr = None
    best_lead = None
    best_has_leads = False
    for thr in thresholds:
        neg_total = 0
        neg_fp = 0
        lead_times: list[int] = []
        for r in run_summaries:
            t_grok = r["t_grok"]
            steps = r["steps"]
            scores = r["scores"]
            y = r["y"]

            # FPR over negative checkpoints
            for yi, sc in zip(y, scores):
                if int(yi) == 0:
                    neg_total += 1
                    if float(sc) >= float(thr):
                        neg_fp += 1

            # lead time uses earliest true-positive trigger in this run (within horizon)
            if t_grok is None:
                continue
            triggered_step = None
            for yi, step, score in zip(y, steps, scores):
                if int(yi) == 1 and float(score) >= float(thr):
                    triggered_step = int(step)
                    break
            if triggered_step is not None:
                lead_times.append(int(t_grok) - int(triggered_step))

        fpr = neg_fp / max(neg_total, 1)
        if fpr > fpr_target:
            continue

        has_leads = bool(lead_times)
        lead = float(np.mean(lead_times)) if lead_times else float("nan")

        if best_fpr is None:
            best_fpr = float(fpr)
            best_lead = lead
            best_has_leads = has_leads
            continue

        # Prefer operating points that yield any lead-time samples (at least one TP trigger).
        if best_has_leads is False and has_leads is True:
            best_fpr = float(fpr)
            best_lead = lead
            best_has_leads = True
            continue
        if best_has_leads is True and has_leads is False:
            continue

        # Among feasible thresholds, pick the one closest to the target from below (max FPR).
        if float(fpr) > float(best_fpr):
            best_fpr = float(fpr)
            best_lead = lead
            best_has_leads = has_leads
            continue
        if float(fpr) == float(best_fpr) and has_leads and best_lead is not None:
            if np.isfinite(lead) and (not np.isfinite(best_lead) or float(lead) > float(best_lead)):
                best_lead = lead

    return float(best_lead) if best_lead is not None else float("nan")
