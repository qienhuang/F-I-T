from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt

def plot_onepage_v0_5(
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
    axA.legend(fontsize=7)

    # Panel B: MSA learning curve
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["msa_cls"]["queried_labels"], dtype=float)
        y = np.asarray(ser["msa_cls"]["tpr_primary"], dtype=float)
        axB.plot(x, y, label=policy)
    axB.set_title("(B) MSA alarm learning curve (TPR@cap vs MSA budget)")
    axB.set_xlabel("MSA queried labels (count)")
    axB.set_ylabel("TPR at primary FPR cap")
    axB.set_ylim(0, 1)
    axB.legend(fontsize=7)

    # Panel C: allocation over time (fraction PAE per round)
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["alloc"]["round"], dtype=float)
        y = np.asarray(ser["alloc"]["frac_pae"], dtype=float)
        axC.plot(x, y, label=policy)
    axC.set_title("(C) Oracle allocation over time (fraction PAE per round)")
    axC.set_xlabel("Round index")
    axC.set_ylabel("frac_pae")
    axC.set_ylim(0, 1)
    axC.set_xlim(0, rounds)
    axC.legend(fontsize=7)

    # Panel D: joint gate frontier (joint_usable_round vs final MAE)
    policies = list(series_by_policy.keys())
    xs = []
    ys = []
    for policy in policies:
        jr = int(series_by_policy[policy]["joint"]["joint_usable_round"])
        mae_final = float(series_by_policy[policy]["msa_reg"]["mae_holdout"][-1]) if len(series_by_policy[policy]["msa_reg"]["mae_holdout"]) else float("nan")
        xs.append(jr)
        ys.append(mae_final)
    axD.scatter(xs, ys)
    for i, policy in enumerate(policies):
        axD.text(xs[i], ys[i], policy, fontsize=7)
    axD.set_title("(D) Joint gate frontier: speed vs proxy quality")
    axD.set_xlabel("joint_usable_round (rounds; lower is better)")
    axD.set_ylabel("final MAE(C3_hat) (lower is better)")
    axD.set_xlim(0, rounds + 2)

    fig.suptitle(meta_footer, y=0.98)
    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
