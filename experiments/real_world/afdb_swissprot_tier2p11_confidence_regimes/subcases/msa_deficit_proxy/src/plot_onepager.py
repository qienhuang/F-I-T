from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import matplotlib.pyplot as plt

def plot_onepage(
    out_pdf: Path,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    roc: Dict[str, Any],
    ops: List[Dict[str, Any]],
    meta_footer: str,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

    # Panel A: calibration scatter
    axA.scatter(y_true, y_pred, s=6, alpha=0.6)
    lo = float(np.nanmin([y_true.min(), y_pred.min()]))
    hi = float(np.nanmax([y_true.max(), y_pred.max()]))
    axA.plot([lo, hi], [lo, hi])
    axA.set_title("(A) Regression calibration (test)")
    axA.set_xlabel("true C3")
    axA.set_ylabel("predicted C3_hat")

    # Panel B: residual histogram
    resid = (y_true - y_pred)
    axB.hist(resid[np.isfinite(resid)], bins=40, alpha=0.8)
    axB.set_title("(B) Residual distribution (test)")
    axB.set_xlabel("C3 - C3_hat")
    axB.set_ylabel("count")

    # Panel C: TPR vs FPR curve with operating points
    axC.plot(roc["fpr"], roc["tpr"])
    axC.set_title("(C) Alarm usability (TPR vs FPR)")
    axC.set_xlabel("FPR")
    axC.set_ylabel("TPR")
    axC.set_xlim(0, 0.2)
    axC.set_ylim(0, 1)
    for op in ops:
        axC.scatter([op["fpr"]], [op["tpr"]])
        tag = "OK" if op["usable"] else "UNUSABLE"
        axC.text(op["fpr"], op["tpr"], f"{op['fpr_target']:.2f}:{tag}", fontsize=8)

    # Panel D: budget view (flagged/missed per 10k)
    labels = [f"{op['fpr_target']:.2f}" for op in ops]
    flagged = [op["flagged_rate"] * 10000.0 for op in ops]
    missed = [op["miss_rate"] * 10000.0 for op in ops]
    x = np.arange(len(labels))
    width = 0.35
    axD.bar(x - width/2, flagged, width, label="flagged per 10k")
    axD.bar(x + width/2, missed, width, label="missed per 10k")
    axD.set_title("(D) Budget trade-off at target FPR")
    axD.set_xlabel("target FPR cap")
    axD.set_ylabel("count per 10k")
    axD.set_xticks(x)
    axD.set_xticklabels(labels)
    axD.legend()

    fig.suptitle(meta_footer, y=0.98)
    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
