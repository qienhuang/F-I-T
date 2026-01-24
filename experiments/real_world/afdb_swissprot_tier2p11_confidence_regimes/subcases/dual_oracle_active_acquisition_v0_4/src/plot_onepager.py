from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import matplotlib.pyplot as plt

def plot_onepage_v0_4(
    out_pdf: Path,
    series_by_policy: Dict[str, Dict[str, Any]],
    rounds: int,
    meta_footer: str,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

    # Panel A: PAE learning curve (TPR@cap vs PAE labels)
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["pae"]["queried_labels"], dtype=float)
        y = np.asarray(ser["pae"]["tpr_primary"], dtype=float)
        axA.plot(x, y, label=policy)
    axA.set_title("(A) PAE alarm learning curve (TPR@cap vs PAE budget)")
    axA.set_xlabel("PAE queried labels (count)")
    axA.set_ylabel("TPR at primary FPR cap")
    axA.set_ylim(0, 1)
    axA.legend()

    # Panel B: MSA classification learning curve
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["msa_cls"]["queried_labels"], dtype=float)
        y = np.asarray(ser["msa_cls"]["tpr_primary"], dtype=float)
        axB.plot(x, y, label=policy)
    axB.set_title("(B) MSA alarm learning curve (TPR@cap vs MSA budget)")
    axB.set_xlabel("MSA queried labels (count)")
    axB.set_ylabel("TPR at primary FPR cap")
    axB.set_ylim(0, 1)
    axB.legend()

    # Panel C: MSA regression MAE curve
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["msa_reg"]["queried_labels"], dtype=float)
        y = np.asarray(ser["msa_reg"]["mae_holdout"], dtype=float)
        axC.plot(x, y, label=policy)
    axC.set_title("(C) MSA proxy channel quality (MAE of C3_hat)")
    axC.set_xlabel("MSA queried labels (count)")
    axC.set_ylabel("MAE on MSA holdout")
    axC.legend()

    # Panel D: joint gate frontier (earliest joint usable round vs final MAE)
    policies = list(series_by_policy.keys())
    x = []
    y = []
    for policy in policies:
        jr = int(series_by_policy[policy]["joint"]["joint_usable_round"])
        mae_final = float(series_by_policy[policy]["msa_reg"]["mae_holdout"][-1]) if len(series_by_policy[policy]["msa_reg"]["mae_holdout"]) else float("nan")
        x.append(jr)
        y.append(mae_final)
    axD.scatter(x, y)
    for i, policy in enumerate(policies):
        axD.text(x[i], y[i], policy, fontsize=8)
    axD.set_title("(D) Joint gate frontier: speed vs proxy quality")
    axD.set_xlabel("joint_usable_round (rounds; lower is better)")
    axD.set_ylabel("final MAE(C3_hat) (lower is better)")
    axD.set_xlim(0, rounds + 2)

    fig.suptitle(meta_footer, y=0.98)
    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
