from __future__ import annotations

import hashlib
from typing import List


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_to_unit_interval(s: str, seed_string: str) -> float:
    hx = sha256_hex(seed_string + "::" + s)
    return int(hx[:16], 16) / float(16**16)


def stable_hash_order(ids: List[str], seed_string: str) -> List[str]:
    return sorted(ids, key=lambda i: sha256_hex(seed_string + "::order::" + str(i)))

