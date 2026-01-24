from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt

def area_under_curve(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return 0.0
    return float(np.trapz(y, x))

def plot_onepage_dual_oracle(
    out_pdf: Path,
    series_by_policy: Dict[str, Dict[str, Any]],
    primary_fpr_target: float,
    meta_footer: str,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

    # Panel A: PAE learning curve
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["pae"]["queried_labels"], dtype=float)
        y = np.asarray(ser["pae"]["tpr_primary"], dtype=float)
        axA.plot(x, y, label=policy)
    axA.set_title("(A) PAE alarm learning curve (TPR@cap vs PAE budget)")
    axA.set_xlabel("PAE queried labels (count)")
    axA.set_ylabel(f"TPR at FPR cap={primary_fpr_target:.2f}")
    axA.set_ylim(0, 1)
    axA.legend()

    # Panel B: MSA learning curve
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["msa"]["queried_labels"], dtype=float)
        y = np.asarray(ser["msa"]["tpr_primary"], dtype=float)
        axB.plot(x, y, label=policy)
    axB.set_title("(B) MSA alarm learning curve (TPR@cap vs MSA budget)")
    axB.set_xlabel("MSA queried labels (count)")
    axB.set_ylabel(f"TPR at FPR cap={primary_fpr_target:.2f}")
    axB.set_ylim(0, 1)
    axB.legend()

    # Panel C: allocation per round (fraction PAE)
    for policy, ser in series_by_policy.items():
        r = np.asarray(ser["round_index"], dtype=float)
        frac = np.asarray(ser["frac_pae_per_round"], dtype=float)
        axC.plot(r, frac, label=policy)
    axC.set_title("(C) Oracle allocation over time")
    axC.set_xlabel("round")
    axC.set_ylabel("frac PAE in round")
    axC.set_ylim(0, 1)
    axC.legend()

    # Panel D: stacked AUTC
    policies = list(series_by_policy.keys())
    autc_pae = []
    autc_msa = []
    for policy in policies:
        x_p = np.asarray(series_by_policy[policy]["pae"]["queried_labels"], dtype=float)
        y_p = np.asarray(series_by_policy[policy]["pae"]["tpr_primary"], dtype=float)
        x_m = np.asarray(series_by_policy[policy]["msa"]["queried_labels"], dtype=float)
        y_m = np.asarray(series_by_policy[policy]["msa"]["tpr_primary"], dtype=float)
        autc_pae.append(area_under_curve(x_p, y_p))
        autc_msa.append(area_under_curve(x_m, y_m))

    x = np.arange(len(policies))
    axD.bar(x, autc_pae, label="AUTC_PAE")
    axD.bar(x, autc_msa, bottom=autc_pae, label="AUTC_MSA")
    axD.set_xticks(x)
    axD.set_xticklabels(policies, rotation=20)
    axD.set_title("(D) Efficiency summary (stacked AUTC)")
    axD.set_xlabel("policy")
    axD.set_ylabel("AUTC (TPR vs queried labels)")
    axD.legend()

    fig.suptitle(meta_footer, y=0.98)
    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
