from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class GroupConfig:
    group_id: str
    self_writeback: bool
    control_enabled: bool


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))


def clamp01(x: float) -> float:
    return float(min(1.0, max(0.0, x)))


def simulate_episode(
    rng: np.random.Generator,
    group: GroupConfig,
    cfg: Dict,
    episode_id: int,
) -> Tuple[pd.DataFrame, Dict]:
    n_steps = int(cfg["simulation"]["n_steps"])
    perturb_step = int(cfg["simulation"]["perturb_step"])
    perturb_amp = float(cfg["simulation"]["perturb_amplitude"])

    dyn = cfg["state_dynamics"]
    writeback_beta = float(dyn["writeback_beta"])
    correction_gamma = float(dyn["correction_gamma"])
    decay_eta = float(dyn["decay_eta"])
    noise_sigma = float(dyn["noise_sigma"])
    action_gain = float(dyn["action_gain"])
    action_bias = float(dyn["action_bias"])

    det = cfg["lockin_detector"]
    score_th = float(det["score_threshold"])
    mem_th = float(det["memory_threshold"])
    consec_k = int(det["consecutive_steps"])
    roll_w = int(det["rolling_window"])

    ctrl = cfg["controller"]
    ctrl_window = int(ctrl["emptiness_window_steps"])
    block_unsafe_actions = bool(ctrl["block_unsafe_actions"])
    block_self_writeback = bool(ctrl["block_self_writeback"])

    # memory bias near 0 means healthy; near 1 means locked-in wrong memory
    m = clamp01(
        float(rng.normal(dyn["init_memory_bias_mean"], dyn["init_memory_bias_std"]))
    )

    records: List[Dict] = []

    lockin_triggered = False
    lockin_first_t = -1
    high_score_consec = 0
    detector_scores: List[float] = []

    control_timer = 0
    did_perturb = False

    for t in range(n_steps):
        if t == perturb_step:
            m = clamp01(m + perturb_amp)
            did_perturb = True

        self_eval_conf = clamp01(0.35 + 0.55 * m + rng.normal(0.0, 0.04))

        logits_wrong = action_gain * m + action_bias + rng.normal(0.0, 0.2)
        p_wrong = sigmoid(logits_wrong)

        # controller can block unsafe actions during emptiness window
        if control_timer > 0 and block_unsafe_actions:
            p_wrong = min(p_wrong, 0.05)

        action_wrong = bool(rng.random() < p_wrong)
        task_success = float(not action_wrong)

        # external correction intensity is stronger when action is wrong
        ext_corr = correction_gamma * (1.0 if action_wrong else 0.35)

        # self writeback pushes memory toward current self-eval confidence
        allow_writeback = group.self_writeback
        if group.control_enabled and control_timer > 0 and block_self_writeback:
            allow_writeback = False

        self_influence = writeback_beta * self_eval_conf if allow_writeback else 0.0

        # lock-in detector score: self-influence dominates external correction
        score = self_influence - ext_corr + 0.10 * m
        detector_scores.append(score)
        recent = detector_scores[-roll_w:]
        roll_score = float(np.mean(recent))

        if did_perturb and (roll_score >= score_th) and (m >= mem_th):
            high_score_consec += 1
        else:
            high_score_consec = 0

        if (not lockin_triggered) and high_score_consec >= consec_k:
            lockin_triggered = True
            lockin_first_t = t
            if group.control_enabled:
                control_timer = ctrl_window

        # state update
        noise = float(rng.normal(0.0, noise_sigma))
        m = clamp01(m + self_influence - ext_corr - decay_eta * (1.0 - m) + noise)

        if control_timer > 0:
            control_timer -= 1

        records.append(
            {
                "episode_id": episode_id,
                "group": group.group_id,
                "t": t,
                "memory_bias": m,
                "self_eval_conf": self_eval_conf,
                "p_wrong": p_wrong,
                "action_wrong": int(action_wrong),
                "task_success": task_success,
                "self_influence": self_influence,
                "external_correction": ext_corr,
                "detector_score": score,
                "detector_score_roll": roll_score,
                "control_active": int(control_timer > 0),
                "lockin_triggered_so_far": int(lockin_triggered),
            }
        )

    episode_df = pd.DataFrame(records)
    episode_meta = {
        "episode_id": episode_id,
        "group": group.group_id,
        "lockin_triggered": int(lockin_triggered),
        "lockin_first_t": int(lockin_first_t),
        "max_detector_score": float(max(detector_scores) if detector_scores else 0.0),
    }
    return episode_df, episode_meta


def run_all(cfg: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    n_episodes = int(cfg["simulation"]["n_episodes"])
    seed_start = int(cfg["simulation"]["seed_start"])

    group_list = [
        GroupConfig(
            group_id=g["id"],
            self_writeback=bool(g["self_writeback"]),
            control_enabled=bool(g["control_enabled"]),
        )
        for g in cfg["groups"]
    ]

    all_rows: List[pd.DataFrame] = []
    all_meta: List[Dict] = []

    for group_idx, group in enumerate(group_list):
        for ep in range(n_episodes):
            seed = seed_start + ep + 10000 * group_idx
            rng = np.random.default_rng(seed)
            ep_df, ep_meta = simulate_episode(rng=rng, group=group, cfg=cfg, episode_id=ep)
            all_rows.append(ep_df)
            all_meta.append(ep_meta)

    episodes_df = pd.concat(all_rows, ignore_index=True)
    meta_df = pd.DataFrame(all_meta)
    return episodes_df, meta_df
