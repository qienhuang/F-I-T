from __future__ import annotations

import hashlib
from typing import Iterable


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def stable_hash_order(items: Iterable[str], seed_string: str) -> list[str]:
    pairs = [(sha256_hex(seed_string + "::" + str(x)), str(x)) for x in items]
    pairs.sort(key=lambda t: t[0])
    return [x for _, x in pairs]

