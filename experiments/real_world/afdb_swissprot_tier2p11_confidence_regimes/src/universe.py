from __future__ import annotations
from pathlib import Path
import re
from typing import List, Set

AF_RE = re.compile(r"^AF-([A-Z0-9]+)-")

def scan_accessions(coords_dir: str | Path) -> List[str]:
    # Scan for AF-<ACCESSION>-*.cif or .pdb in coords_dir (recursive).
    d = Path(coords_dir)
    if not d.exists():
        raise FileNotFoundError(f"coords_dir not found: {d}")
    acc: Set[str] = set()
    for p in d.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".cif", ".pdb"):
            continue
        m = AF_RE.match(p.name)
        if m:
            acc.add(m.group(1))
    return sorted(acc)

def is_fragment_name(coords_filename: str) -> bool:
    # Heuristic: treat AFDB fragment naming as fragment if contains '-F' segment.
    return "-F" in coords_filename
