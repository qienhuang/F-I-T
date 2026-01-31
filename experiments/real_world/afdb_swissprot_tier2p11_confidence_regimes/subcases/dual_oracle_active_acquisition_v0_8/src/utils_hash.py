from __future__ import annotations
import hashlib
from typing import Iterable, List

def sha256_hex(s: str) -> str:
    h = hashlib.sha256()
    h.update(s.encode("utf-8"))
    return h.hexdigest()

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def stable_hash_order(items: Iterable[str], seed_string: str) -> List[str]:
    pairs = []
    for it in items:
        d = sha256_hex(seed_string + "::" + str(it))
        pairs.append((d, str(it)))
    pairs.sort(key=lambda x: x[0])
    return [it for _, it in pairs]

def hash_to_unit_interval(item: str, seed_string: str) -> float:
    d = sha256_hex(seed_string + "::" + str(item))
    x = int(d[:16], 16)
    return x / float(2**64 - 1)
