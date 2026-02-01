from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PreregPaths:
    processed_cells_parquet: Path
    metrics_log_parquet: Path
    prereg_locked_yaml: Path
    coherence_report_json: Path
    fail_windows_md: Path
    regime_report_md: Path
    tradeoff_onepage_png: Path
    tradeoff_onepage_pdf: Path


def load_prereg(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Prereg YAML must be a mapping")
    return data


def prereg_paths(prereg: dict[str, Any], workdir: Path) -> PreregPaths:
    outputs = prereg.get("outputs", {})
    if not isinstance(outputs, dict):
        raise ValueError("outputs must be a mapping")

    def _p(key: str) -> Path:
        v = outputs.get(key)
        if not isinstance(v, str) or not v:
            raise ValueError(f"Missing outputs.{key}")
        return (workdir / v).resolve()

    return PreregPaths(
        processed_cells_parquet=_p("processed_cells_parquet"),
        metrics_log_parquet=_p("metrics_log_parquet"),
        prereg_locked_yaml=_p("prereg_locked_yaml"),
        coherence_report_json=_p("coherence_report_json"),
        fail_windows_md=_p("fail_windows_md"),
        regime_report_md=_p("regime_report_md"),
        tradeoff_onepage_png=_p("tradeoff_onepage_png"),
        tradeoff_onepage_pdf=_p("tradeoff_onepage_pdf"),
    )


def write_locked_prereg(prereg_path: Path, locked_path: Path) -> None:
    locked_path.parent.mkdir(parents=True, exist_ok=True)
    locked_path.write_text(prereg_path.read_text(encoding="utf-8"), encoding="utf-8")

