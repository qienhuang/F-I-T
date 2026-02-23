from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def build_tradeoff(summary_df: pd.DataFrame, cfg: Dict) -> pd.DataFrame:
    targets: List[float] = [float(x) for x in cfg["monitorability"]["fpr_targets"]]

    rows = []
    for group, gdf in summary_df.groupby("group"):
        y = gdf["non_recovered"].astype(int).to_numpy()
        scores = gdf["max_detector_score"].astype(float).to_numpy()

        neg = scores[y == 0]
        pos = scores[y == 1]
        n_neg = int(len(neg))
        n_pos = int(len(pos))

        for target in targets:
            if n_neg == 0:
                thr = float("inf")
            else:
                q = max(0.0, min(1.0, 1.0 - target))
                thr = float(np.quantile(neg, q))

            pred = scores >= thr
            fp = int(((pred == 1) & (y == 0)).sum())
            tp = int(((pred == 1) & (y == 1)).sum())
            fpr = float(fp / n_neg) if n_neg > 0 else float("nan")
            coverage = float(tp / n_pos) if n_pos > 0 else 0.0
            abstain = float(1.0 - pred.mean())

            rows.append(
                {
                    "group": group,
                    "fpr_target": target,
                    "threshold": thr,
                    "fpr_achieved": fpr,
                    "coverage": coverage,
                    "abstain_rate": abstain,
                    "n_pos": n_pos,
                    "n_neg": n_neg,
                }
            )

    return pd.DataFrame(rows)


def summarize_main_findings(recoverability_obj: Dict, tradeoff_df: pd.DataFrame) -> Dict:
    groups = recoverability_obj["groups"]
    r_by_group = {k: v["R"] for k, v in groups.items()}

    # compare G2 against baseline at FPR target 0.05
    slice_df = tradeoff_df[np.isclose(tradeoff_df["fpr_target"], 0.05)]
    cov = {r["group"]: float(r["coverage"]) for _, r in slice_df.iterrows()}

    return {
        "R_by_group": r_by_group,
        "coverage_at_fpr_0_05": cov,
        "best_R_group": max(r_by_group, key=r_by_group.get) if r_by_group else None,
    }
