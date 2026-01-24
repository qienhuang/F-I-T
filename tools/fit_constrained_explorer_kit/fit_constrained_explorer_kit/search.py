from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from .domain_toy_bitstring import DomainConfig, sample_random, mutate, is_feasible
from .surrogate_ridge import fit_ridge, predict_mean_var


@dataclass(frozen=True)
class Proposal:
    X: np.ndarray
    policy: str


def propose(
    policy: str,
    cfg: DomainConfig,
    batch_size: int,
    rng_tag: str,
    evaluated_X: np.ndarray | None,
    evaluated_y: np.ndarray | None,
    policy_cfg: dict,
) -> Proposal:
    if policy == "random":
        X = sample_random(cfg, n=batch_size, seed_tag=rng_tag + "::random")
        return Proposal(X=X, policy=policy)

    if policy == "evo_mutate_best":
        if evaluated_X is None or evaluated_y is None or len(evaluated_y) == 0:
            X = sample_random(cfg, n=batch_size, seed_tag=rng_tag + "::fallback_random")
            return Proposal(X=X, policy=policy)

        top_k = int(policy_cfg["evo"]["parents_top_k"])
        flip_k = int(policy_cfg["evo"]["mutate_bits_per_child"])
        idx = np.argsort(-evaluated_y)[: min(top_k, len(evaluated_y))]
        parents = evaluated_X[idx]
        X = mutate(cfg, parents=parents, n_children=batch_size, flip_k=flip_k, seed_tag=rng_tag + "::evo")
        return Proposal(X=X, policy=policy)

    if policy == "surrogate_ucb":
        if evaluated_X is None or evaluated_y is None or len(evaluated_y) < 5:
            X = sample_random(cfg, n=batch_size, seed_tag=rng_tag + "::fallback_random")
            return Proposal(X=X, policy=policy)

        lam = float(policy_cfg["surrogate"]["ridge_lambda"])
        beta = float(policy_cfg["surrogate"]["ucb_beta"])
        m = fit_ridge(evaluated_X.astype(np.float64), evaluated_y.astype(np.float64), lam=lam)

        # candidate pool (oversample then take top)
        pool = sample_random(cfg, n=batch_size * 20, seed_tag=rng_tag + "::ucb_pool")
        feas = is_feasible(cfg, pool)
        pool = pool[feas]
        if len(pool) == 0:
            pool = sample_random(cfg, n=batch_size * 20, seed_tag=rng_tag + "::ucb_pool2")

        mean, var = predict_mean_var(m, pool.astype(np.float64))
        ucb = mean + beta * np.sqrt(var + 1e-12)
        pick = np.argsort(-ucb)[: min(batch_size, len(pool))]
        X = pool[pick]
        if len(X) < batch_size:
            pad = sample_random(cfg, n=batch_size - len(X), seed_tag=rng_tag + "::ucb_pad")
            X = np.concatenate([X, pad], axis=0)
        return Proposal(X=X, policy=policy)

    raise ValueError(f"Unknown policy: {policy}")

