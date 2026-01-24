from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt


def _area_under_curve(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return 0.0
    return float(np.trapezoid(y, x))


def plot_onepage_active(
    out_pdf: Path,
    series_by_policy: Dict[str, Dict[str, Any]],
    primary_fpr_target: float,
    meta_footer: str,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    # Panel A: TPR@primaryFPR vs queried labels
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["queried_labels"], dtype=float)
        y = np.asarray(ser["tpr_primary"], dtype=float)
        axA.plot(x, y, label=policy)
    axA.set_title("(A) Coverage (TPR) at low FPR vs oracle budget")
    axA.set_xlabel("queried labels (count)")
    axA.set_ylabel(f"TPR at FPR cap={primary_fpr_target:.2f}")
    axA.set_ylim(0, 1)
    axA.legend()

    # Panel B: achieved FPR vs budget (primary operating point)
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["queried_labels"], dtype=float)
        y = np.asarray(ser["fpr_primary"], dtype=float)
        axB.plot(x, y, label=policy)
    axB.axhline(primary_fpr_target)
    axB.set_title("(B) Constraint satisfaction (achieved FPR vs budget)")
    axB.set_xlabel("queried labels (count)")
    axB.set_ylabel("achieved FPR (holdout)")
    axB.set_ylim(0, max(primary_fpr_target * 3, 0.2))
    axB.legend()

    # Panel C: positive discovery rate in queried batches
    for policy, ser in series_by_policy.items():
        r = np.asarray(ser["round_index"], dtype=float)
        y = np.asarray(ser["batch_pos_rate"], dtype=float)
        axC.plot(r, y, label=policy)
    axC.set_title("(C) Positive discovery rate in queried batches")
    axC.set_xlabel("round")
    axC.set_ylabel("pos rate in queried batch")
    axC.set_ylim(0, 1)
    axC.legend()

    # Panel D: AUTC bars (efficiency summary)
    policies = list(series_by_policy.keys())
    autc = []
    for policy in policies:
        x = np.asarray(series_by_policy[policy]["queried_labels"], dtype=float)
        y = np.asarray(series_by_policy[policy]["tpr_primary"], dtype=float)
        autc.append(_area_under_curve(x, y))
    axD.bar(np.arange(len(policies)), autc)
    axD.set_xticks(np.arange(len(policies)))
    axD.set_xticklabels(policies, rotation=20)
    axD.set_title("(D) Efficiency summary (AUTC)")
    axD.set_xlabel("policy")
    axD.set_ylabel("AUTC (TPR vs queried labels)")

    fig.suptitle(meta_footer, y=0.98)
    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
