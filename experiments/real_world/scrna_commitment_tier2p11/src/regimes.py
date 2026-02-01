from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .prereg import load_prereg, prereg_paths


@dataclass(frozen=True)
class WindowRow:
    window_id: int
    n_cells: int
    t_min: float
    t_max: float
    c1: float | None
    c2: float | None
    valid: bool


def _safe_spearman(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    m = np.isfinite(x) & np.isfinite(y)
    if int(np.sum(m)) < 3:
        return float("nan"), float("nan")
    rho, p = spearmanr(x[m], y[m])
    return float(rho), float(p)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply coherence gate and write verdict")
    parser.add_argument("--prereg", required=True, help="Preregistration YAML")
    args = parser.parse_args()

    workdir = Path(__file__).resolve().parents[1]
    prereg_path = Path(args.prereg).resolve()
    prereg = load_prereg(prereg_path)
    paths = prereg_paths(prereg, workdir)

    est_cfg = prereg.get("estimators", {})
    expected_sign = int(est_cfg.get("expected_sign", +1))
    rho_thr = float(est_cfg.get("coherence_threshold_rho", 0.2))
    c1 = str(est_cfg.get("c1_name", "C_dim_collapse"))
    c2 = str(est_cfg.get("c2_name", "C_mixing"))

    metrics = pd.read_parquet(paths.metrics_log_parquet)
    if metrics.empty:
        verdict = "INCONCLUSIVE"
        report = {
            "case_id": prereg.get("case_id"),
            "verdict": verdict,
            "reason": "Too few valid windows to evaluate.",
        }
        paths.coherence_report_json.parent.mkdir(parents=True, exist_ok=True)
        paths.coherence_report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        paths.regime_report_md.parent.mkdir(parents=True, exist_ok=True)
        paths.regime_report_md.write_text(f"# Verdict: {verdict}\n\nToo few valid windows to evaluate.\n", encoding="utf-8")
        return

    # Window-level coherence: for scalar window metrics, Spearman is computed across windows.
    rho, p = _safe_spearman(metrics[c1].to_numpy(dtype=float), metrics[c2].to_numpy(dtype=float))
    if np.isfinite(rho):
        pass_sign = (rho >= 0) if expected_sign >= 0 else (rho <= 0)
        pass_thr = abs(rho) >= rho_thr if rho_thr >= 0 else True
        pass_gate = bool(pass_sign and pass_thr)
    else:
        pass_gate = False

    window_rows: list[WindowRow] = []
    for _, row in metrics.iterrows():
        c1v = float(row[c1])
        c2v = float(row[c2])
        valid = bool(np.isfinite(c1v) and np.isfinite(c2v))
        window_rows.append(
            WindowRow(
                window_id=int(row["window_id"]),
                n_cells=int(row["n_cells"]),
                t_min=float(row["t_min"]),
                t_max=float(row["t_max"]),
                c1=c1v if np.isfinite(c1v) else None,
                c2=c2v if np.isfinite(c2v) else None,
                valid=valid,
            )
        )

    # Verdict semantics: a single global gate for v0.1 (conservative).
    verdict = "OK_PER_WINDOW" if pass_gate else "ESTIMATOR_UNSTABLE"

    coherence_report: dict[str, Any] = {
        "case_id": prereg.get("case_id"),
        "expected_sign": expected_sign,
        "coherence_threshold_rho": rho_thr,
        "c1_name": c1,
        "c2_name": c2,
        "n_windows": int(len(metrics)),
        "rho_across_windows": rho,
        "p_value_across_windows": p,
        "window_metric_note": "Window entries record per-window estimator values; coherence is assessed across windows.",
        "controllability_note": "Not an alarm case; FPR fields are not applicable.",
        "pass_gate": pass_gate,
        "verdict": verdict,
        "windows": [asdict(w) for w in window_rows],
    }

    paths.coherence_report_json.parent.mkdir(parents=True, exist_ok=True)
    paths.coherence_report_json.write_text(json.dumps(coherence_report, indent=2, allow_nan=False), encoding="utf-8")

    if expected_sign > 0:
        thr_text = f"rho >= {rho_thr:.3f}"
    elif expected_sign < 0:
        thr_text = f"rho <= {-rho_thr:.3f}"
    else:
        thr_text = f"|rho| >= {rho_thr:.3f}"

    md_lines = [
        "# scRNA commitment (EST-gated) - Regime report",
        "",
        f"**Verdict:** `{verdict}`",
        "",
        "## Coherence gate (across windows)",
        "",
        f"- Estimators: `{c1}` vs `{c2}`",
        f"- Expected sign: `{expected_sign:+d}`",
        f"- Threshold: `{thr_text}`",
        f"- Observed rho: `{rho:.3f}` (p={p:.3g})",
        f"- Gate pass: `{pass_gate}`",
        "",
        "## Notes",
        "",
        "- This v0.1 run uses a single coherence test across windows (conservative).",
        "- Window entries record per-window estimator values (not per-window rho/p-values).",
        "- A future v0.2 can add per-window gates and a stability grid (window size sensitivity).",
        "",
    ]
    paths.regime_report_md.parent.mkdir(parents=True, exist_ok=True)
    paths.regime_report_md.write_text("\n".join(md_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
