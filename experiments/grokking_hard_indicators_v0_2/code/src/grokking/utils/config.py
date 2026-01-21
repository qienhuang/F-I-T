from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(data: dict[str, Any], path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    checkpoints_dir: Path
    logs_path: Path
    resolved_config_path: Path


def make_run_paths(out_dir: str | Path, seed: int) -> RunPaths:
    out_dir = Path(out_dir)
    run_dir = out_dir / f"seed_{seed}"
    checkpoints_dir = run_dir / "checkpoints"
    return RunPaths(
        run_dir=run_dir,
        checkpoints_dir=checkpoints_dir,
        logs_path=run_dir / "logs.jsonl",
        resolved_config_path=run_dir / "config.resolved.yaml",
    )

