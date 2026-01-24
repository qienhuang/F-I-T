from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt

def _hist(ax, x: np.ndarray, label: str, bins: int = 30):
    x = x[np.isfinite(x)]
    if x.size == 0:
        return
    ax.hist(x, bins=bins, alpha=0.5, label=label, density=True)

def plot_onepage(
    out_pdf: Path,
    eval_obj: Dict[str, Any],
    y_test: np.ndarray,
    s_test: np.ndarray,
    meta_footer: str,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

    # Panel A: ROC
    roc = eval_obj["roc_curve"]
    axA.plot(roc["fpr"], roc["tpr"])
    axA.set_title("(A) ROC + operating points")
    axA.set_xlabel("FPR")
    axA.set_ylabel("TPR")
    axA.set_xlim(0, 1)
    axA.set_ylim(0, 1)

    for op in eval_obj["operating_points"]:
        axA.scatter([op["fpr"]], [op["tpr"]])
        axA.text(op["fpr"], op["tpr"], f"FPR≤{op['fpr_target']:.2f}", fontsize=8)

    # Panel B: coverage vs FPR
    cov = eval_obj["coverage_vs_fpr"]
    axB.plot(cov["fpr"], cov["tpr"])
    axB.set_title("(B) Coverage vs FPR (usability curve)")
    axB.set_xlabel("FPR")
    axB.set_ylabel("TPR")
    axB.set_xlim(0, 0.2)  # zoom into low-FPR region
    axB.set_ylim(0, 1)

    for op in eval_obj["operating_points"]:
        axB.scatter([op["fpr"]], [op["tpr"]])
        tag = "OK" if op["usable"] else "UNUSABLE"
        axB.text(op["fpr"], op["tpr"], tag, fontsize=8)

    # Panel C: score distributions
    s_pos = s_test[y_test == 1]
    s_neg = s_test[y_test == 0]
    _hist(axC, s_neg, "neg (no event)")
    _hist(axC, s_pos, "pos (PAE event)")
    axC.set_title("(C) Score distributions (neg vs pos)")
    axC.set_xlabel("predicted probability")
    axC.set_ylabel("density")
    axC.legend()

    # Panel D: budget view
    labels = []
    flagged = []
    missed = []
    for op in eval_obj["operating_points"]:
        labels.append(f"{op['fpr_target']:.2f}")
        flagged.append(op["flagged_rate"] * 10000.0)
        missed.append(op["miss_rate"] * 10000.0)
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
