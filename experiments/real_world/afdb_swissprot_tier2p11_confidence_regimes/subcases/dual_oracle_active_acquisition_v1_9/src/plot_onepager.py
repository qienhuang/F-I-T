from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import matplotlib.pyplot as plt

def plot_onepage_v1_1(
    out_pdf: Path,
    series_by_policy: Dict[str, Dict[str, Any]],
    meta_footer: str,
    rounds: int,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

    # Panel A: PAE learning curve (holdout)
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["pae"].get("queried_cost", ser["pae"]["queried_labels"]), dtype=float)
        y = np.asarray(ser["pae"]["tpr_primary"], dtype=float)
        axA.plot(x, y, label=policy)
    axA.set_title("(A) PAE learning curve (holdout TPR@cap vs PAE cumulative cost)")
    axA.set_xlabel("PAE cumulative cost")
    axA.set_ylabel("TPR at primary FPR cap")
    axA.set_ylim(0, 1)
    axA.legend(fontsize=6)

    # Panel B: MSA learning curve (holdout)
    for policy, ser in series_by_policy.items():
        x = np.asarray(ser["msa_cls"].get("queried_cost", ser["msa_cls"]["queried_labels"]), dtype=float)
        y = np.asarray(ser["msa_cls"]["tpr_primary"], dtype=float)
        axB.plot(x, y, label=policy)
    axB.set_title("(B) MSA learning curve (holdout TPR@cap vs MSA cumulative cost)")
    axB.set_xlabel("MSA cumulative cost")
    axB.set_ylabel("TPR at primary FPR cap")
    axB.set_ylim(0, 1)
    axB.legend(fontsize=6)

    # Panel C: allocation fraction per round (PAE)
    for policy, ser in series_by_policy.items():
        y = np.asarray(ser["alloc"].get("pae_cost_share", ser["alloc"]["pae_fraction"]), dtype=float)
        x = np.arange(len(y))
        axC.plot(x, y, label=policy)
    axC.set_title("(C) Allocation over time (cost share to PAE)")
    axC.set_xlabel("round")
    axC.set_ylabel("PAE cost share")
    axC.set_ylim(0, 1)
    axC.legend(fontsize=6)

    # Panel D: Δ-lag (floor-clear -> joint-usable)
    items: List[Tuple[str, int, int, int, int, int]] = []
    for policy, ser in series_by_policy.items():
        ev = ser["events"]
        r_pae = int(ev["E_floor_resolved_pae"]["round_index"])
        r_msa = int(ev["E_floor_resolved_msa"]["round_index"])
        r_floor = max(r_pae, r_msa)
        r_joint = int(ev["E_joint_usable"]["round_index"])
        r_cov = int((ev.get("E_covjump_joint") or {}).get("round_index") or (rounds + 1))
        items.append((policy, r_pae, r_msa, r_floor, r_joint, r_cov))
    items.sort(key=lambda x: (x[4], x[5], x[0]))  # by joint usable, then covjump, then name

    y_pos = np.arange(len(items))
    labels = [it[0] for it in items]
    x_pae = [it[1] for it in items]
    x_msa = [it[2] for it in items]
    x_floor = [it[3] for it in items]
    x_joint = [it[4] for it in items]
    x_cov = [it[5] for it in items]

    # markers
    axD.scatter(x_pae, y_pos, marker="o", label="PAE floor resolved")
    axD.scatter(x_msa, y_pos, marker="x", label="MSA floor resolved")
    axD.scatter(x_joint, y_pos, marker="^", label="joint usable")
    axD.scatter(x_cov, y_pos, marker="s", label="E_covjump_joint")

    # segments: r_floor -> r_joint
    for i, (rf, rj) in enumerate(zip(x_floor, x_joint)):
        axD.plot([rf, rj], [y_pos[i], y_pos[i]], linewidth=1)

    axD.set_yticks(y_pos)
    axD.set_yticklabels(labels, fontsize=6)
    axD.set_xlabel("round index (never -> rounds+1)")
    axD.set_title("(D) Δ-lag + joint coverage jump marker")
    axD.set_xlim(0, rounds + 1)
    axD.legend(fontsize=6, loc="lower right")

    fig.suptitle(meta_footer, y=0.98, fontsize=9)
    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)
