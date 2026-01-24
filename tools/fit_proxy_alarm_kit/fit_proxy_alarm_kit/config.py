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
        raise ValueError("PREREG.yaml must be a mapping/dict at top level.")
    return Prereg(raw=data)


def require(cfg: dict, dotted: str) -> Any:
    cur: Any = cfg
    for k in dotted.split("."):
        if not isinstance(cur, dict) or k not in cur:
            raise ValueError(f"Missing required config: {dotted}")
        cur = cur[k]
    return cur


def validate_prereg(cfg: dict) -> None:
    # Minimal structural validation (Layer 0 guardrails).
    require(cfg, "boundary.feature_whitelist")
    require(cfg, "boundary.label_field")
    require(cfg, "boundary.tau_label")
    require(cfg, "data.input_metrics_path")
    require(cfg, "data.id_field")
    require(cfg, "data.seed_string")
    require(cfg, "evaluation.holdout_frac")
    require(cfg, "monitorability.fpr_targets")
    require(cfg, "monitorability.primary_fpr_target")
    require(cfg, "acquisition.init_labeled_n")
    require(cfg, "acquisition.rounds")
    require(cfg, "acquisition.batch_size")
    require(cfg, "acquisition.policies")

    fpr_targets = [float(x) for x in cfg["monitorability"]["fpr_targets"]]
    primary = float(cfg["monitorability"]["primary_fpr_target"])
    if primary not in fpr_targets:
        raise ValueError("monitorability.primary_fpr_target must be included in monitorability.fpr_targets")

