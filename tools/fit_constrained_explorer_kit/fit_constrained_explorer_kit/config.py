from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass(frozen=True)
class Prereg:
    raw: Dict[str, Any]


def load_prereg(path: str | Path) -> Prereg:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("PREREG must be a dict at top level.")
    return Prereg(raw=data)


def require(cfg: dict, dotted: str) -> Any:
    cur: Any = cfg
    for k in dotted.split("."):
        if not isinstance(cur, dict) or k not in cur:
            raise ValueError(f"Missing required config: {dotted}")
        cur = cur[k]
    return cur


def validate_prereg(cfg: dict) -> None:
    require(cfg, "domain.name")
    require(cfg, "domain.n_bits")
    require(cfg, "domain.constraint.type")
    require(cfg, "domain.oracle.type")
    require(cfg, "budget.oracle_evals_max")
    require(cfg, "search.seed_string")
    require(cfg, "search.init_random")
    require(cfg, "search.batch_size")
    require(cfg, "search.rounds")
    require(cfg, "search.policies")

    n_bits = int(cfg["domain"]["n_bits"])
    if n_bits <= 0:
        raise ValueError("domain.n_bits must be positive")

    max_evals = int(cfg["budget"]["oracle_evals_max"])
    if max_evals <= 0:
        raise ValueError("budget.oracle_evals_max must be positive")

