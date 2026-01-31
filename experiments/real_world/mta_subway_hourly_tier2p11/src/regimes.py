"""
Diagnostic change-point detection and report export.

Hard rule: interpretation is coherence-gated.
If coherence status is not OK / OK_PER_WINDOW, this module only reports diagnostics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def load_prereg(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def robust_zscore_peak(series: pd.Series, *, rolling_window: int, zscore_threshold: float, min_peak_distance: int) -> list[int]:
    x = series.astype(float)
    med = x.rolling(rolling_window, min_periods=max(10, rolling_window // 5)).median()
    mad = (x - med).abs().rolling(rolling_window, min_periods=max(10, rolling_window // 5)).median()
    z = (x - med) / (mad.replace(0.0, np.nan) * 1.4826)
    z = z.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    peaks = np.where(z.abs() >= zscore_threshold)[0].tolist()
    selected: list[int] = []
    last = -10**9
    for p in peaks:
        if p - last >= min_peak_distance:
            selected.append(int(p))
            last = p
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Export MTA regime diagnostics")
    parser.add_argument("--prereg", default="EST_PREREG_v0.1_hourly.yaml", help="Preregistration YAML")
    parser.add_argument("--input", default="outputs/metrics_log.parquet", help="Input metrics parquet")
    parser.add_argument("--coherence", default="outputs/coherence_report.json", help="Coherence report json")
    parser.add_argument("--output", default="outputs/regime_report.md", help="Output markdown report")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)
    df = pd.read_parquet(args.input)
    df["t"] = pd.to_datetime(df["t"])
    coh = json.loads(Path(args.coherence).read_text(encoding="utf-8"))
    status = coh.get("status", "UNKNOWN")

    signal = df["dR_ic"].astype(float)
    params = prereg.get("regime_detection", {}).get("parameters", {})
    peaks = robust_zscore_peak(
        signal,
        rolling_window=int(params.get("rolling_window", 336)),
        zscore_threshold=float(params.get("zscore_threshold", 2.5)),
        min_peak_distance=int(params.get("min_peak_distance", 24)),
    )

    cp = []
    for idx in peaks[:200]:
        cp.append({"t": df.loc[idx, "t"].isoformat(), "score": float(signal.iloc[idx])})

    out_dir = Path(args.output).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "change_points.json").write_text(json.dumps({"method": "robust_zscore_peak", "points": cp}, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Regime diagnostics (EST-gated)")
    lines.append("")
    lines.append(f"- Coherence status: `{status}`")
    lines.append(f"- Change points detected (diagnostic only): {len(cp)}")
    lines.append("")
    if status not in {"OK", "OK_PER_WINDOW", "OK_PER_YEAR"}:
        lines.append("Interpretation is **forbidden** at this scope due to coherence gating.")
        lines.append("")

    if cp:
        lines.append("## Top change points (by |score|; diagnostic)")
        lines.append("")
        lines.append("| t | score |")
        lines.append("|---|---:|")
        for p in sorted(cp, key=lambda d: abs(d["score"]), reverse=True)[:10]:
            lines.append(f"| {p['t']} | {p['score']:.3f} |")
    else:
        lines.append("No change points recorded.")

    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
