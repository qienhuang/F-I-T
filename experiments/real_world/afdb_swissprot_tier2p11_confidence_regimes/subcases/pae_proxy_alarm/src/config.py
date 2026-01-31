from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import yaml

@dataclass(frozen=True)
class Prereg:
    raw: Dict[str, Any]

    def get(self, *keys: str, default=None):
        cur: Any = self.raw
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

def load_prereg(path: str | Path) -> Prereg:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("PREREG.yaml must be a mapping/dict at top level.")
    return Prereg(raw=data)
