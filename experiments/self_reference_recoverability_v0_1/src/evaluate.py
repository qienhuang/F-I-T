from __future__ import annotations

import json
from typing import Dict

import numpy as np
import pandas as pd


def summarize_episode(episode_df: pd.DataFrame, episode_meta: pd.Series, cfg: Dict) -> Dict:
    rec_cfg = cfg["recoverability"]
    perturb_step = int(cfg["simulation"]["perturb_step"])
    n_steps = int(cfg["simulation"]["n_steps"])

    recovery_window = int(rec_cfg["recovery_window"])
    success_th = float(rec_cfg["success_ratio_threshold"])
    mem_th = float(rec_cfg["memory_threshold"])
    drift_mem_th = float(rec_cfg["drift_memory_threshold"])

    post = episode_df[episode_df["t"] >= perturb_step].copy()

    recovered = False
    t_recover = n_steps
    for t in range(perturb_step, n_steps - recovery_window + 1):
        win = post[(post["t"] >= t) & (post["t"] < t + recovery_window)]
        if len(win) < recovery_window:
            continue
        success_ratio = float(win["task_success"].mean())
        mem_mean = float(win["memory_bias"].mean())
        if success_ratio >= success_th and mem_mean <= mem_th:
            recovered = True
            t_recover = t
            break

    drift_depth = int((post["memory_bias"] >= drift_mem_th).sum())
    non_recovered = int(not recovered)

    return {
        "episode_id": int(episode_meta["episode_id"]),
        "group": str(episode_meta["group"]),
        "lockin_triggered": int(episode_meta["lockin_triggered"]),
        "lockin_first_t": int(episode_meta["lockin_first_t"]),
        "max_detector_score": float(episode_meta["max_detector_score"]),
        "recovered": int(recovered),
        "t_recover": int(t_recover),
        "drift_depth": int(drift_depth),
        "non_recovered": int(non_recovered),
    }


def build_episode_summary(episodes_df: pd.DataFrame, meta_df: pd.DataFrame, cfg: Dict) -> pd.DataFrame:
    rows = []
    for _, m in meta_df.iterrows():
        ep = episodes_df[
            (episodes_df["group"] == m["group"]) & (episodes_df["episode_id"] == m["episode_id"])
        ]
        rows.append(summarize_episode(ep, m, cfg))
    return pd.DataFrame(rows)


def compute_recoverability(summary_df: pd.DataFrame, cfg: Dict) -> Dict:
    rec_cfg = cfg["recoverability"]
    lam = float(rec_cfg["lambda_time"])
    mu = float(rec_cfg["mu_drift"])

    out = {"groups": {}, "formula": "R = P_recover * exp(-lambda*T_recover) * exp(-mu*D_drift)"}

    for group, gdf in summary_df.groupby("group"):
        p_recover = float(gdf["recovered"].mean())
        t_rec = float(gdf.loc[gdf["recovered"] == 1, "t_recover"].mean()) if p_recover > 0 else float(cfg["simulation"]["n_steps"])
        d_drift = float(gdf["drift_depth"].mean())

        r = p_recover * np.exp(-lam * t_rec) * np.exp(-mu * d_drift)
        out["groups"][group] = {
            "P_recover": p_recover,
            "T_recover_mean": t_rec,
            "D_drift_mean": d_drift,
            "R": float(r),
            "n": int(len(gdf)),
            "lockin_rate": float(gdf["lockin_triggered"].mean()),
            "non_recovered_rate": float(gdf["non_recovered"].mean()),
        }

    return out


def write_recoverability_json(path: str, obj: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
