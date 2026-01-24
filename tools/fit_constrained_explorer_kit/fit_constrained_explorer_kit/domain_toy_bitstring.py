from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from .utils_hash import sha256_hex


@dataclass(frozen=True)
class DomainConfig:
    n_bits: int
    max_ones: int
    noise_std: float
    seed_string: str


def _rng(seed_string: str) -> np.random.Generator:
    # deterministic across machines
    h = sha256_hex(seed_string)
    seed = int(h[:16], 16) % (2**32)
    return np.random.default_rng(seed)


def sample_random(cfg: DomainConfig, n: int, seed_tag: str) -> np.ndarray:
    rng = _rng(cfg.seed_string + "::" + seed_tag)
    X = np.zeros((int(n), int(cfg.n_bits)), dtype=np.int8)
    # Sample feasible-by-construction (sparse) for the toy max_ones constraint.
    for i in range(int(n)):
        k = int(rng.integers(0, int(cfg.max_ones) + 1))
        if k > 0:
            idx = rng.choice(cfg.n_bits, size=k, replace=False)
            X[i, idx] = 1
    return X


def is_feasible(cfg: DomainConfig, X: np.ndarray) -> np.ndarray:
    ones = X.sum(axis=1)
    return (ones <= int(cfg.max_ones)).astype(bool)


def mutate(cfg: DomainConfig, parents: np.ndarray, n_children: int, flip_k: int, seed_tag: str) -> np.ndarray:
    rng = _rng(cfg.seed_string + "::" + seed_tag)
    n_par = parents.shape[0]
    kids = np.empty((int(n_children), int(cfg.n_bits)), dtype=np.int8)
    for i in range(int(n_children)):
        p = parents[int(rng.integers(0, n_par))]
        child = p.copy()
        idx = rng.choice(cfg.n_bits, size=int(flip_k), replace=False)
        child[idx] = 1 - child[idx]
        # Repair to satisfy max_ones if needed (toy constraint).
        ones = int(child.sum())
        if ones > int(cfg.max_ones):
            on_idx = np.where(child == 1)[0]
            drop = rng.choice(on_idx, size=ones - int(cfg.max_ones), replace=False)
            child[drop] = 0
        kids[i] = child
    return kids


def oracle_reward(cfg: DomainConfig, X: np.ndarray) -> np.ndarray:
    # Hidden linear reward with deterministic weights.
    rng = _rng(cfg.seed_string + "::oracle_weights")
    w = rng.normal(0.0, 1.0, size=(cfg.n_bits,))
    base = X.astype(np.float64) @ w
    if cfg.noise_std > 0:
        rng2 = _rng(cfg.seed_string + "::oracle_noise")
        base = base + rng2.normal(0.0, cfg.noise_std, size=base.shape)
    return base.astype(np.float64)


def fingerprint_bits(x: np.ndarray) -> str:
    return sha256_hex("".join(map(str, x.astype(int).tolist())))


def decode_cfg(prereg: dict) -> DomainConfig:
    n_bits = int(prereg["domain"]["n_bits"])
    max_ones = int(prereg["domain"]["constraint"]["max_ones"])
    noise_std = float(prereg["domain"]["oracle"].get("noise_std", 0.0))
    seed_string = str(prereg["search"]["seed_string"])
    return DomainConfig(n_bits=n_bits, max_ones=max_ones, noise_std=noise_std, seed_string=seed_string)


def summarize_constraints(cfg: DomainConfig) -> Dict[str, object]:
    return {"type": "max_ones", "max_ones": int(cfg.max_ones), "n_bits": int(cfg.n_bits)}
