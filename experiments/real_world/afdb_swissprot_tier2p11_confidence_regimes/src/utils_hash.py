from __future__ import annotations
import hashlib
from typing import Iterable, List

def sha256_hex(s: str) -> str:
    h = hashlib.sha256()
    h.update(s.encode("utf-8"))
    return h.hexdigest()

def stable_hash_order(items: Iterable[str], seed_string: str) -> List[str]:
    # Deterministic ordering based on sha256(seed + item).
    pairs = []
    for it in items:
        digest = sha256_hex(seed_string + "::" + it)
        pairs.append((digest, it))
    pairs.sort(key=lambda x: x[0])
    return [it for _, it in pairs]
