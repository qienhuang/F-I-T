from __future__ import annotations
from typing import List, Tuple
import numpy as np
from .utils_hash import stable_hash_order, sha256_hex

def rank_by_uncertainty(ids: List[str], probs: np.ndarray, seed: str) -> List[str]:
    u = np.abs(probs - 0.5)
    hashes = np.array([sha256_hex(seed + "::uncertainty::" + i) for i in ids])
    order = np.lexsort((hashes, u))
    return [ids[i] for i in order]

def rank_by_high_score(ids: List[str], probs: np.ndarray, seed: str) -> List[str]:
    neg = -probs
    hashes = np.array([sha256_hex(seed + "::high_score::" + i) for i in ids])
    order = np.lexsort((hashes, neg))
    return [ids[i] for i in order]

def rank_by_random_hash(ids: List[str], seed: str) -> List[str]:
    return stable_hash_order(ids, seed_string=seed + "::random_hash")

def allocate_fixed_split(q_total: int, q_pae_fixed: int, q_msa_fixed: int) -> Tuple[int, int]:
    q_pae = min(int(q_pae_fixed), int(q_total))
    q_msa = min(int(q_msa_fixed), int(q_total - q_pae))
    rem = int(q_total - q_pae - q_msa)
    if rem > 0:
        q_msa += rem
    return q_pae, q_msa

def allocate_by_uncertainty_mass(q_total: int, u_pae: float, u_msa: float) -> Tuple[int, int]:
    denom = float(u_pae + u_msa)
    if denom <= 0:
        return q_total // 2, q_total - (q_total // 2)
    q_pae = int(round(q_total * (u_pae / denom)))
    q_pae = max(0, min(q_total, q_pae))
    q_msa = q_total - q_pae
    return q_pae, q_msa
