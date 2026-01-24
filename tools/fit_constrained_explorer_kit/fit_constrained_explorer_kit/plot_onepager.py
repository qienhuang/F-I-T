from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import numpy as np
import matplotlib.pyplot as plt


def plot_onepage(out_pdf: Path, trace: list[dict], meta_footer: str) -> None:
    if not trace:
        return

    df_policy = {}
    for row in trace:
        df_policy.setdefault(row["policy"], []).append(row)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axA, axB, axC, axD = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    for policy, rows in df_policy.items():
        x = np.asarray([r["eval_index"] for r in rows], dtype=float)
        y = np.asarray([r["best_reward_so_far"] for r in rows], dtype=float)
        axA.plot(x, y, label=policy)
    axA.set_title("(A) Best feasible reward vs oracle evals")
    axA.set_xlabel("oracle eval index")
    axA.set_ylabel("best reward so far")
    axA.legend()

    for policy, rows in df_policy.items():
        x = np.asarray([r["eval_index"] for r in rows], dtype=float)
        y = np.asarray([r["feasible"] for r in rows], dtype=float)
        # running feasibility rate
        rate = np.cumsum(y) / np.arange(1, len(y) + 1)
        axB.plot(x, rate, label=policy)
    axB.set_title("(B) Feasible rate vs oracle evals")
    axB.set_xlabel("oracle eval index")
    axB.set_ylabel("feasible rate")
    axB.set_ylim(0, 1)
    axB.legend()

    for policy, rows in df_policy.items():
        x = np.asarray([r["eval_index"] for r in rows], dtype=float)
        y = np.asarray([r["reward"] if r["feasible"] else np.nan for r in rows], dtype=float)
        axC.plot(x, y, ".", label=policy, alpha=0.7)
    axC.set_title("(C) Reward samples (feasible only)")
    axC.set_xlabel("oracle eval index")
    axC.set_ylabel("reward (feasible)")
    axC.legend()

    # Policy share
    labels = list(df_policy.keys())
    sizes = [len(df_policy[k]) for k in labels]
    axD.pie(sizes, labels=labels, autopct="%1.0f%%")
    axD.set_title("(D) Eval allocation by policy")

    fig.suptitle(meta_footer, y=0.98)
    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf)
    plt.close(fig)

