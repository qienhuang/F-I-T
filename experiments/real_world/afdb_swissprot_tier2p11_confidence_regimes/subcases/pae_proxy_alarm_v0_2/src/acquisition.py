from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
from .utils_hash import stable_hash_order, sha256_hex

def _tie_break(ids: List[str], seed: str) -> List[str]:
    # deterministic tie-breaker
    return stable_hash_order(ids, seed_string=seed + "::tie")

def select_batch(
    policy: str,
    unlabeled_ids: List[str],
    unlabeled_scores: np.ndarray,
    batch_size: int,
    seed: str,
) -> List[str]:
    if len(unlabeled_ids) == 0:
        return []

    n = min(int(batch_size), len(unlabeled_ids))

    if policy == "random_hash":
        ordered = stable_hash_order(unlabeled_ids, seed_string=seed + "::random_hash")
        return ordered[:n]

    if policy == "uncertainty":
        # smaller |p-0.5| is more uncertain
        u = np.abs(unlabeled_scores - 0.5)
        # stable ranking: sort by (u, hash)
        hashes = np.array([sha256_hex(seed + "::uncertainty::" + i) for i in unlabeled_ids])
        order = np.lexsort((hashes, u))
        return [unlabeled_ids[i] for i in order[:n]]

    if policy == "high_score":
        # higher p first
        neg_scores = -unlabeled_scores
        hashes = np.array([sha256_hex(seed + "::high_score::" + i) for i in unlabeled_ids])
        order = np.lexsort((hashes, neg_scores))
        return [unlabeled_ids[i] for i in order[:n]]

    raise ValueError(f"Unknown policy: {policy}")
