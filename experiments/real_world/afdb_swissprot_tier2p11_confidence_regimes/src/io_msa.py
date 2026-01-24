from __future__ import annotations
from pathlib import Path

def msa_depth_a3m(path: str | Path) -> int:
    # Approximate MSA depth by counting sequence headers in A3M.
    # Includes the query sequence.
    p = Path(path)
    n = 0
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith(">"):
                n += 1
    return n
