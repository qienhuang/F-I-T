from __future__ import annotations
from typing import List
import numpy as np
from sklearn.neighbors import NearestNeighbors
from .utils_hash import sha256_hex, stable_hash_order

def uncertainty_from_probs(probs: np.ndarray) -> np.ndarray:
    # range [0, 0.5], higher = more uncertain
    return 0.5 - np.abs(probs - 0.5)

def minmax_norm(x: np.ndarray) -> np.ndarray:
    if len(x) == 0:
        return x
    lo = float(np.min(x))
    hi = float(np.max(x))
    if hi <= lo + 1e-12:
        return np.zeros_like(x, dtype=float)
    return (x - lo) / (hi - lo)

def novelty_min_dist(cand_z: np.ndarray, labeled_z: np.ndarray) -> np.ndarray:
    """Novelty proxy: min L2 distance to labeled set in z-scored B0 space."""
    if labeled_z is None or len(labeled_z) == 0 or len(cand_z) == 0:
        return np.zeros((len(cand_z),), dtype=float)
    nn = NearestNeighbors(n_neighbors=1, algorithm="auto", metric="euclidean")
    nn.fit(labeled_z)
    dists, _ = nn.kneighbors(cand_z, return_distance=True)
    return dists[:, 0].astype(float)

def stable_tie_hash(ids: List[str], seed: str, tag: str) -> np.ndarray:
    return np.array([sha256_hex(seed + f"::{tag}::" + str(i)) for i in ids])

def rank_ids(
    ids: List[str],
    probs: np.ndarray,
    novelty_norm: np.ndarray,
    composite: np.ndarray,
    mode: str,
    seed: str,
) -> List[str]:
    """Return ids ordered from best to worst according to mode."""
    if mode == "random_hash":
        return stable_hash_order(ids, seed_string=seed + "::random_hash")

    hashes = stable_tie_hash(ids, seed=seed, tag=mode)

    if mode == "high_score":
        key = -probs
        order = np.lexsort((hashes, key))
        return [ids[i] for i in order]

    if mode == "uncertainty":
        u = -(0.5 - np.abs(probs - 0.5))  # maximize uncertainty
        order = np.lexsort((hashes, u))
        return [ids[i] for i in order]

    if mode == "novelty":
        n = -novelty_norm
        order = np.lexsort((hashes, n))
        return [ids[i] for i in order]

    if mode == "composite":
        c = -composite
        order = np.lexsort((hashes, c))
        return [ids[i] for i in order]

    raise ValueError(f"Unknown ranking mode: {mode}")
