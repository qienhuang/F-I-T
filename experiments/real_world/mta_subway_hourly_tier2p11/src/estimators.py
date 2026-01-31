"""
Compute MTA (Tier-2 / P11) estimators and write:
- outputs/metrics_log.parquet
- outputs/coherence_report.json

This module is intentionally scoped:
- It computes a small estimator family.
- It implements the EST coherence gate with optional windowing.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def load_prereg(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def shannon_entropy(counts: dict[str, float]) -> float:
    total = float(sum(counts.values()))
    if total <= 0:
        return 0.0
    probs = np.asarray(list(counts.values()), dtype=float) / total
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs)))


def topk_share(counts: dict[str, float], k: int) -> float:
    total = float(sum(counts.values()))
    if total <= 0:
        return 0.0
    vals = sorted((float(v) for v in counts.values()), reverse=True)
    return float(sum(vals[:k]) / total)


def _parse_counts(x: object) -> dict[str, float]:
    if isinstance(x, dict):
        return {str(k): float(v) for k, v in x.items()}
    if isinstance(x, str) and x.strip():
        d = json.loads(x)
        return {str(k): float(v) for k, v in d.items()}
    return {}


def compute_metrics(state: pd.DataFrame, prereg: dict) -> pd.DataFrame:
    df = state.copy()
    df["t"] = pd.to_datetime(df["t"])
    df["station_counts"] = df["station_ridership_counts"].map(_parse_counts)

    info_cfg = prereg["estimators"]["information"]["I_entropy_station"]
    con_load_cfg = prereg["estimators"]["constraint"]["C_load"]
    con_conc_cfg = prereg["estimators"]["constraint"]["C_concentration"]
    k = int(con_conc_cfg.get("k", 10))

    df["I_entropy_station"] = df["station_counts"].map(shannon_entropy) if info_cfg.get("enabled", True) else np.nan
    df["C_load"] = np.log1p(df[con_load_cfg.get("source", "ridership_total")].astype(float)) if con_load_cfg.get("enabled", True) else np.nan
    df["C_concentration"] = df["station_counts"].map(lambda d: topk_share(d, k)) if con_conc_cfg.get("enabled", True) else np.nan

    df["R_ic"] = df["I_entropy_station"] / df["C_load"].replace(0.0, np.nan)
    df["dR_ic"] = df["R_ic"].diff()

    force_cfg = prereg.get("estimators", {}).get("force", {}).get("F_load_drift", {})
    if force_cfg.get("enabled", False):
        w = int(force_cfg.get("window", 168))
        df["F_load_drift"] = df["ridership_total"].astype(float).diff().rolling(w, min_periods=max(2, w // 10)).mean()
    else:
        df["F_load_drift"] = np.nan

    keep = [
        "t",
        "ridership_total",
        "station_active_count",
        "I_entropy_station",
        "C_load",
        "C_concentration",
        "R_ic",
        "dR_ic",
        "F_load_drift",
    ]
    return df[keep].sort_values("t").reset_index(drop=True)


@dataclass(frozen=True)
class PairResult:
    pair: tuple[str, str]
    rho: float | None
    passed: bool | None
    n: int
    status: str


def spearman_pair(x: pd.Series, y: pd.Series, *, min_points: int, threshold: float) -> PairResult:
    z = pd.DataFrame({"x": x, "y": y}).dropna()
    n = int(len(z))
    if n < min_points:
        return PairResult(pair=("x", "y"), rho=None, passed=None, n=n, status="DATA_MISSING")
    rho = float(z["x"].corr(z["y"], method="spearman"))
    passed = bool(rho >= threshold)
    return PairResult(pair=("x", "y"), rho=rho, passed=passed, n=n, status="OK" if passed else "FAIL")


def _coherence_on_df(df: pd.DataFrame, pairs: list[list[str]], *, threshold: float, min_points: int) -> dict:
    pair_results = []
    all_ok = True
    any_missing = False
    for a, b in pairs:
        res = spearman_pair(df[a], df[b], min_points=min_points, threshold=threshold)
        res = PairResult(pair=(a, b), rho=res.rho, passed=res.passed, n=res.n, status=res.status)
        pair_results.append(
            {"pair": [a, b], "rho": res.rho, "passed": res.passed, "n": res.n, "status": res.status}
        )
        if res.status == "DATA_MISSING":
            any_missing = True
            all_ok = False
        elif res.status != "OK":
            all_ok = False

    status = "OK" if all_ok else ("DATA_MISSING" if any_missing else "ESTIMATOR_UNSTABLE")
    return {"status": status, "pairs": pair_results}


def compute_coherence(metrics: pd.DataFrame, prereg: dict) -> dict:
    coh = prereg["coherence"]
    threshold = float(coh["threshold"])
    min_points = int(coh.get("min_points", 30))
    pairs = coh["pairs"]

    pooled = _coherence_on_df(metrics, pairs, threshold=threshold, min_points=min_points)
    report: dict = {"status": pooled["status"], "pairs": pooled["pairs"]}

    windowing = coh.get("windowing", {})
    wtype = windowing.get("type")
    if not wtype:
        return report

    tz = getattr(pd.Series(metrics["t"]).dt, "tz", None)

    def _coerce(ts: str) -> pd.Timestamp:
        t = pd.Timestamp(ts)
        if tz is None:
            return t
        if t.tzinfo is None:
            return t.tz_localize(tz)
        return t.tz_convert(tz)

    allow_pooled_fail = bool(windowing.get("allow_pooled_fail", False))
    windows: list[dict] = []
    if wtype == "date_ranges":
        for r in windowing.get("ranges", []):
            r_id = r["id"]
            start = _coerce(r["start"])
            end = _coerce(r["end"])
            wdf = metrics[(metrics["t"] >= start) & (metrics["t"] <= end)].copy()
            wrep = _coherence_on_df(wdf, pairs, threshold=threshold, min_points=min_points)
            windows.append({"id": r_id, "start": r["start"], "end": r["end"], "status": wrep["status"], "pairs": wrep["pairs"]})
    else:
        raise ValueError(f"Unsupported windowing.type: {wtype}")

    pooled_status = report["status"]
    all_windows_ok = all(w.get("status") == "OK" for w in windows) if windows else False
    any_window_fail = any(w.get("status") == "FAIL" for w in windows)

    if all_windows_ok:
        report["status"] = "OK" if pooled_status == "OK" else ("OK_PER_WINDOW" if allow_pooled_fail else pooled_status)
    elif pooled_status == "OK" and any_window_fail:
        report["status"] = "STRUCTURE_MISMATCH"
    else:
        report["status"] = "ESTIMATOR_UNSTABLE"

    report["windowing"] = {
        "type": wtype,
        "aggregate": "all_pass",
        "allow_pooled_fail": allow_pooled_fail,
        "pooled_status": pooled_status,
        "results": windows,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute MTA estimators (Tier-2 / P11)")
    parser.add_argument("--prereg", default="EST_PREREG_v0.1_hourly.yaml", help="Preregistration YAML")
    parser.add_argument("--input", default="data/cleaned/bucket_state.parquet", help="Input parquet")
    parser.add_argument("--output", default="outputs/metrics_log.parquet", help="Output parquet")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)
    state = pd.read_parquet(args.input)
    metrics = compute_metrics(state, prereg)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(out_path, index=False)

    coherence = compute_coherence(metrics, prereg)
    coh_path = out_path.parent / "coherence_report.json"
    coh_path.write_text(json.dumps(coherence, indent=2), encoding="utf-8")

    print(f"Saved metrics: {out_path} (n={len(metrics)})")
    print(f"Saved coherence: {coh_path} (status={coherence.get('status')})")


if __name__ == "__main__":
    main()
