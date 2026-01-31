from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
from .utils_hash import sha256_hex, stable_hash_order

def uncertainty_from_prob(p: np.ndarray) -> np.ndarray:
    return (0.5 - np.abs(p - 0.5)) / 0.5

def stable_tiebreak(ids: List[str], seed: str) -> np.ndarray:
    keys = np.array([int(sha256_hex(seed + "::tb::" + i)[:16], 16) for i in ids], dtype=np.uint64)
    return keys

def select_candidate_pool(ids: List[str], probs: np.ndarray, basis: str, K: int, seed: str) -> List[int]:
    n = len(ids)
    if K <= 0 or K >= n:
        return list(range(n))
    if basis == "uncertainty":
        u = uncertainty_from_prob(probs)
        tb = stable_tiebreak(ids, seed + "::pool")
        order = np.lexsort((tb, -u))
        return order[:K].tolist()
    if basis == "high_score":
        tb = stable_tiebreak(ids, seed + "::pool")
        order = np.lexsort((tb, -probs))
        return order[:K].tolist()
    if basis == "random_hash":
        ordered = stable_hash_order(ids, seed_string=seed + "::poolhash")
        idx_map = {s:i for i,s in enumerate(ids)}
        return [idx_map[s] for s in ordered[:K]]
    raise ValueError(f"Unknown candidate_pool_basis: {basis}")

def novelty_min_dist(candidate_z: np.ndarray, ref_z: np.ndarray) -> np.ndarray:
    if ref_z.shape[0] == 0:
        return np.full((candidate_z.shape[0],), np.inf, dtype=float)
    N = candidate_z.shape[0]
    dmin = np.full((N,), np.inf, dtype=float)
    block = 4096
    for i in range(0, N, block):
        X = candidate_z[i:i+block]
        dist2 = ((X[:, None, :] - ref_z[None, :, :]) ** 2).sum(axis=2)
        dmin[i:i+block] = np.sqrt(np.min(dist2, axis=1))
    return dmin

def normalize01(x: np.ndarray) -> np.ndarray:
    x = x.astype(float)
    finite = np.isfinite(x)
    if not finite.any():
        return np.zeros_like(x, dtype=float)
    lo = np.min(x[finite])
    hi = np.max(x[finite])
    if abs(hi - lo) < 1e-12:
        out = np.zeros_like(x, dtype=float)
        out[finite] = 0.0
        return out
    out = np.zeros_like(x, dtype=float)
    out[finite] = (x[finite] - lo) / (hi - lo)
    return out

@dataclass(frozen=True)
class SelectionResult:
    selected_indices: List[int]
    per_item: List[Dict[str, float]]

def select_batch_composite_ff(
    ids: List[str],
    probs: np.ndarray,
    Xz: np.ndarray,
    ref_z: np.ndarray,
    q: int,
    K: int,
    basis: str,
    alpha: float,
    seed: str,
) -> SelectionResult:
    n = len(ids)
    if q <= 0 or n == 0:
        return SelectionResult([], [])
    pool_idx = select_candidate_pool(ids, probs, basis=basis, K=K, seed=seed)
    cand_ids = [ids[i] for i in pool_idx]
    cand_probs = probs[pool_idx]
    cand_z = Xz[pool_idx]

    unc = uncertainty_from_prob(cand_probs)
    dmin_to_labeled = novelty_min_dist(cand_z, ref_z)

    unc_norm = normalize01(unc)
    current_dmin = dmin_to_labeled.copy()

    tb = stable_tiebreak(cand_ids, seed + "::rank")

    selected_pool_positions: List[int] = []
    per_item: List[Dict[str, float]] = []

    for _ in range(min(q, len(pool_idx))):
        nov_norm = normalize01(current_dmin)
        comp = float(alpha) * unc_norm + (1.0 - float(alpha)) * nov_norm
        order = np.lexsort((tb, -comp))
        pick_pos = None
        for j in order:
            if int(j) not in selected_pool_positions:
                pick_pos = int(j)
                break
        if pick_pos is None:
            break

        selected_pool_positions.append(pick_pos)
        per_item.append({
            "predicted_prob": float(cand_probs[pick_pos]),
            "uncertainty_norm": float(unc_norm[pick_pos]),
            "novelty": float(current_dmin[pick_pos]),
            "novelty_norm": float(nov_norm[pick_pos]),
            "composite_score": float(comp[pick_pos]),
        })

        # update novelty with the newly selected sample (batch diversity)
        z_new = cand_z[pick_pos][None, :]
        dist_new = np.sqrt(((cand_z - z_new) ** 2).sum(axis=1))
        current_dmin = np.minimum(current_dmin, dist_new)
        current_dmin[pick_pos] = -np.inf

    selected_indices = [pool_idx[pos] for pos in selected_pool_positions]
    return SelectionResult(selected_indices=selected_indices, per_item=per_item)

def rank_by_uncertainty(ids: List[str], probs: np.ndarray, seed: str) -> List[int]:
    u = uncertainty_from_prob(probs)
    tb = stable_tiebreak(ids, seed + "::unc")
    order = np.lexsort((tb, -u))
    return order.tolist()

def rank_by_random_hash(ids: List[str], seed: str) -> List[int]:
    ordered = stable_hash_order(ids, seed_string=seed + "::hash")
    idx_map = {s:i for i,s in enumerate(ids)}
    return [idx_map[s] for s in ordered]

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

def allocate_by_gap(q_total: int, g_pae: float, g_msa: float) -> Tuple[int, int]:
    denom = float(g_pae + g_msa)
    if denom <= 0:
        return q_total // 2, q_total - (q_total // 2)
    q_pae = int(round(q_total * (g_pae / denom)))
    q_pae = max(0, min(q_total, q_pae))
    q_msa = q_total - q_pae
    return q_pae, q_msa
