"""
NYC TLC Regime Detection

Detects regime-change signatures in dR/dt using pluggable methods.
Core P11 analysis: change points in I/C ratio derivative.

Supported detection methods:
- robust_zscore_peak: Peak detection via robust z-score
- rolling_mean_shift: Mean-shift detection via rolling windows
"""

import argparse
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

import numpy as np
import pandas as pd
import yaml


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ChangePoint:
    """Detected change point with metadata."""
    index: int
    date: str
    value: float
    score: float  # z-score or shift magnitude
    direction: str  # "positive" or "negative"
    method: str  # detection method used

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "date": self.date,
            "value": self.value,
            "score": self.score,
            "direction": self.direction,
            "method": self.method,
        }


# ============================================================================
# Detector Interface
# ============================================================================

class ChangePointDetector(ABC):
    """Abstract base class for change point detectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Detector name for reporting."""
        pass

    @abstractmethod
    def detect(
        self,
        signal: np.ndarray,
        dates: np.ndarray,
        **params
    ) -> list[ChangePoint]:
        """Detect change points in signal."""
        pass


# ============================================================================
# Detector Implementations
# ============================================================================

class RobustZScorePeakDetector(ChangePointDetector):
    """
    Detect peaks using robust z-score (median + MAD).

    Parameters:
    - zscore_threshold: Z-score threshold for peak detection (default: 2.5)
    - min_peak_distance: Minimum days between peaks (default: 7)
    - rolling_window: Rolling window for z-score computation (default: 21)
    """

    @property
    def name(self) -> str:
        return "robust_zscore_peak"

    def detect(
        self,
        signal: np.ndarray,
        dates: np.ndarray,
        zscore_threshold: float = 2.5,
        min_peak_distance: int = 7,
        rolling_window: int = 21,
        **kwargs
    ) -> list[ChangePoint]:
        # Remove NaN
        valid_mask = ~np.isnan(signal)
        valid_signal = signal[valid_mask]
        valid_dates = dates[valid_mask]

        if len(valid_signal) < rolling_window:
            return []

        # Compute robust z-score
        zscore = self._robust_zscore(valid_signal, rolling_window)

        # Find peaks (both positive and negative)
        peaks = []
        for i in range(1, len(zscore) - 1):
            if np.isnan(zscore[i]):
                continue

            # Check if local maximum or minimum
            is_local_max = (
                zscore[i] > zscore[i - 1] and
                zscore[i] > zscore[i + 1] and
                zscore[i] > zscore_threshold
            )
            is_local_min = (
                zscore[i] < zscore[i - 1] and
                zscore[i] < zscore[i + 1] and
                zscore[i] < -zscore_threshold
            )

            if is_local_max or is_local_min:
                date_str = self._format_date(valid_dates[i])
                peaks.append(ChangePoint(
                    index=i,
                    date=date_str,
                    value=float(valid_signal[i]),
                    score=float(zscore[i]),
                    direction="positive" if is_local_max else "negative",
                    method=self.name,
                ))

        # Filter by minimum distance
        return self._filter_by_distance(peaks, min_peak_distance)

    def _robust_zscore(self, x: np.ndarray, window: int) -> np.ndarray:
        """Compute robust z-score using rolling median and MAD."""
        x = pd.Series(x)
        median = x.rolling(window=window, center=True, min_periods=1).median()
        mad = (x - median).abs().rolling(window=window, center=True, min_periods=1).median()
        scaled_mad = 1.4826 * mad.replace(0, np.nan)
        return ((x - median) / scaled_mad).values

    def _format_date(self, date) -> str:
        if hasattr(date, "strftime"):
            return date.strftime("%Y-%m-%d")
        return str(date)[:10]

    def _filter_by_distance(self, peaks: list[ChangePoint], min_distance: int) -> list[ChangePoint]:
        if len(peaks) <= 1:
            return peaks

        filtered = [peaks[0]]
        for peak in peaks[1:]:
            days_diff = self._days_between(filtered[-1].date, peak.date)
            if days_diff >= min_distance:
                filtered.append(peak)
            elif abs(peak.score) > abs(filtered[-1].score):
                filtered[-1] = peak

        return filtered

    def _days_between(self, date1: str, date2: str) -> int:
        d1 = pd.Timestamp(date1)
        d2 = pd.Timestamp(date2)
        return abs((d2 - d1).days)


class RollingMeanShiftDetector(ChangePointDetector):
    """
    Detect mean shifts using rolling window comparison.

    Compares mean of left window vs right window at each point.
    Change point if shift exceeds threshold.

    Parameters:
    - shift_threshold: Minimum shift magnitude (default: auto from std)
    - window_size: Size of comparison windows (default: 14)
    - min_peak_distance: Minimum days between detections (default: 7)
    """

    @property
    def name(self) -> str:
        return "rolling_mean_shift"

    def detect(
        self,
        signal: np.ndarray,
        dates: np.ndarray,
        shift_threshold: float = None,
        window_size: int = 14,
        min_peak_distance: int = 7,
        **kwargs
    ) -> list[ChangePoint]:
        # Remove NaN
        valid_mask = ~np.isnan(signal)
        valid_signal = signal[valid_mask]
        valid_dates = dates[valid_mask]

        if len(valid_signal) < 2 * window_size:
            return []

        # Auto-threshold if not specified
        if shift_threshold is None:
            shift_threshold = 2.0 * np.nanstd(valid_signal)

        # Compute mean shift at each point
        shifts = []
        for i in range(window_size, len(valid_signal) - window_size):
            left_mean = np.mean(valid_signal[i - window_size:i])
            right_mean = np.mean(valid_signal[i:i + window_size])
            shift = right_mean - left_mean
            shifts.append((i, shift))

        # Find significant shifts
        peaks = []
        for i, shift in shifts:
            if abs(shift) > shift_threshold:
                date_str = self._format_date(valid_dates[i])
                peaks.append(ChangePoint(
                    index=i,
                    date=date_str,
                    value=float(valid_signal[i]),
                    score=float(shift),
                    direction="positive" if shift > 0 else "negative",
                    method=self.name,
                ))

        # Filter by minimum distance and keep strongest
        return self._filter_by_distance(peaks, min_peak_distance)

    def _format_date(self, date) -> str:
        if hasattr(date, "strftime"):
            return date.strftime("%Y-%m-%d")
        return str(date)[:10]

    def _filter_by_distance(self, peaks: list[ChangePoint], min_distance: int) -> list[ChangePoint]:
        if len(peaks) <= 1:
            return peaks

        # Sort by absolute score descending
        sorted_peaks = sorted(peaks, key=lambda p: abs(p.score), reverse=True)

        filtered = []
        for peak in sorted_peaks:
            # Check distance to all already-selected peaks
            too_close = False
            for existing in filtered:
                days_diff = self._days_between(existing.date, peak.date)
                if days_diff < min_distance:
                    too_close = True
                    break
            if not too_close:
                filtered.append(peak)

        # Sort back by date
        return sorted(filtered, key=lambda p: p.date)

    def _days_between(self, date1: str, date2: str) -> int:
        d1 = pd.Timestamp(date1)
        d2 = pd.Timestamp(date2)
        return abs((d2 - d1).days)


# ============================================================================
# Detector Registry
# ============================================================================

DETECTORS = {
    "robust_zscore_peak": RobustZScorePeakDetector,
    "rolling_mean_shift": RollingMeanShiftDetector,
}


def get_detector(method: str) -> ChangePointDetector:
    """Get detector instance by method name."""
    if method not in DETECTORS:
        raise ValueError(f"Unknown detection method: {method}. Available: {list(DETECTORS.keys())}")
    return DETECTORS[method]()


# ============================================================================
# Report Generation
# ============================================================================

def generate_regime_report(
    change_points: list[ChangePoint],
    coherence: dict,
    prereg: dict,
    detection_method: str,
    params: dict,
) -> str:
    """
    Generate enhanced markdown regime report.

    Includes:
    - Top 5 peaks with values
    - Window parameters
    - Failure label explanations
    """
    lines = []

    # Header
    lines.append("# Regime Detection Report")
    lines.append("")
    lines.append(f"**Case ID:** {prereg['meta']['case_id']}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Proposition:** {prereg['meta']['proposition']}")
    lines.append(f"**Detection Method:** `{detection_method}`")
    lines.append("")

    # Coherence status
    lines.append("---")
    lines.append("")
    lines.append("## 1. Coherence Gate")
    lines.append("")
    status = coherence.get("status", "UNKNOWN")

    if status == "OK":
        lines.append("> **Status: OK** - Estimator family is coherent.")
        lines.append("> Change points below are interpretable as regime-change signatures.")
    elif status == "OK_PER_YEAR":
        lines.append("> **Status: OK_PER_YEAR** - Coherence passes within yearly windows.")
        lines.append("> ")
        lines.append("> Interpretation rule: interpret signatures within each year; pooled level shifts can break pooled coherence.")
    elif status == "OK_PER_WINDOW":
        lines.append("> **Status: OK_PER_WINDOW** - Coherence passes within preregistered date windows.")
        lines.append("> ")
        lines.append("> Interpretation rule: interpret signatures within each window; pooled level shifts can break pooled coherence.")
    elif status == "ESTIMATOR_UNSTABLE":
        lines.append("> **Status: ESTIMATOR_UNSTABLE** - Coherence gate FAILED.")
        lines.append("> ")
        lines.append("> **WARNING:** Change points below are NOT interpretable.")
        lines.append("> They are reported for diagnostic purposes only.")
    elif status == "DATA_MISSING":
        lines.append("> **Status: DATA_MISSING** - Insufficient data for coherence test.")
    else:
        lines.append(f"> **Status: {status}**")

    lines.append("")

    # Coherence details
    lines.append("### Coherence Test Results")
    lines.append("")
    for pair_result in coherence.get("pairs", []):
        pair = pair_result.get("pair", ["?", "?"])
        if "rho" in pair_result:
            passed_str = "PASS" if pair_result["passed"] else "FAIL"
            lines.append(
                f"- `{pair[0]}` vs `{pair[1]}`: "
                f"rho = {pair_result['rho']:.3f} (n={pair_result['n_points']}) **[{passed_str}]**"
            )
        else:
            lines.append(f"- `{pair[0]}` vs `{pair[1]}`: {pair_result.get('status', 'N/A')}")

    lines.append("")

    windowing = coherence.get("windowing", {})
    if windowing.get("type") in {"yearly", "date_ranges", "rolling"}:
        windows = windowing.get("results", [])
        if windows:
            header = "Yearly Coherence (Diagnostic)" if windowing.get("type") == "yearly" else "Windowed Coherence (Diagnostic)"
            lines.append(f"### {header}")
            lines.append("")
            lines.append("| Window | Status | Pair | rho | n | Pass |")
            lines.append("|--------|--------|------|-----|---|------|")
            for w in windows:
                if windowing.get("type") == "yearly":
                    w_name = str(w.get("year", "?"))
                else:
                    label = w.get("name", "window")
                    start = w.get("start")
                    end = w.get("end")
                    w_name = f"{label} ({start}..{end})" if start and end else str(label)
                w_status = w.get("status", "UNKNOWN")
                for pr in w.get("pairs", []):
                    pair = pr.get("pair", ["?", "?"])
                    if "rho" in pr:
                        lines.append(
                            f"| {w_name} | {w_status} | `{pair[0]}` vs `{pair[1]}` | {pr['rho']:.3f} | {pr['n_points']} | {'PASS' if pr['passed'] else 'FAIL'} |"
                        )
                    else:
                        p_status = pr.get("status", "UNKNOWN")
                        lines.append(f"| {w_name} | {w_status} | `{pair[0]}` vs `{pair[1]}` | - | - | {p_status} |")
            lines.append("")

    # Method parameters
    lines.append("---")
    lines.append("")
    lines.append("## 2. Detection Parameters")
    lines.append("")
    lines.append("| Parameter | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| Method | `{detection_method}` |")
    for key, value in params.items():
        lines.append(f"| {key} | {value} |")

    lines.append("")

    # Top 5 peaks
    lines.append("---")
    lines.append("")
    lines.append("## 3. Top 5 Change Points (by magnitude)")
    lines.append("")

    if not change_points:
        lines.append("*No change points detected above threshold.*")
    else:
        # Sort by absolute score
        top5 = sorted(change_points, key=lambda p: abs(p.score), reverse=True)[:5]
        lines.append("| Rank | Date | Score | dR/dt Value | Direction |")
        lines.append("|------|------|-------|-------------|-----------|")
        for rank, cp in enumerate(top5, 1):
            lines.append(
                f"| {rank} | {cp.date} | {cp.score:+.3f} | {cp.value:.6f} | {cp.direction} |"
            )

    lines.append("")

    # All change points (chronological)
    lines.append("---")
    lines.append("")
    lines.append("## 4. All Change Points (chronological)")
    lines.append("")

    if not change_points:
        lines.append("*No change points detected.*")
    else:
        lines.append(f"**Total detected:** {len(change_points)}")
        lines.append("")
        lines.append("| Date | Score | dR/dt Value | Direction |")
        lines.append("|------|-------|-------------|-----------|")
        for cp in sorted(change_points, key=lambda p: p.date):
            lines.append(
                f"| {cp.date} | {cp.score:+.3f} | {cp.value:.6f} | {cp.direction} |"
            )

    lines.append("")

    # Interpretation guidance
    lines.append("---")
    lines.append("")
    lines.append("## 5. Interpretation")
    lines.append("")

    if status == "OK":
        lines.append("These change points represent **regime-change signatures** in the I/C ratio.")
        lines.append("")
        lines.append("**Direction meanings:**")
        lines.append("- **Positive**: I/C increased sharply (information grew faster than constraint)")
        lines.append("- **Negative**: I/C decreased sharply (constraint grew faster than information)")
        lines.append("")
        lines.append("**Allowed claims:**")
        lines.append("- Statistical structure of the system changed detectably at these times")
        lines.append("- The change is robust to the estimator family (coherence passed)")
        lines.append("")
        lines.append("**Disallowed claims:**")
        lines.append("- Causal attribution to specific events")
        lines.append("- Policy recommendations without separate analysis")
    elif status == "OK_PER_YEAR":
        lines.append("Coherence passes **within yearly windows**, but may fail when pooling years (level shifts).")
        lines.append("")
        lines.append("**Interpretation rule:** treat signatures as interpretable **within each year**.")
        lines.append("Pooled change points are still reported, but should be treated as diagnostic unless they also appear consistently within-year.")
        lines.append("")
        lines.append("Recommended practice: run year-by-year change-point detection and report per-year tables alongside any pooled plot.")
    else:
        lines.append("**Due to coherence failure, no interpretation is permitted.**")
        lines.append("")
        lines.append("Recommended actions:")
        lines.append("- Review estimator definitions")
        lines.append("- Check data quality")
        lines.append("- Consider alternative constraint proxies")

    lines.append("")

    # Failure labels explanation
    lines.append("---")
    lines.append("")
    lines.append("## 6. Failure Labels (EST Reference)")
    lines.append("")
    failure_labels = prereg.get("failure_labels", {})
    if failure_labels:
        lines.append("| Label | Meaning |")
        lines.append("|-------|---------|")
        for label, meaning in failure_labels.items():
            marker = " (current)" if label == status else ""
            lines.append(f"| `{label}` | {meaning}{marker} |")
    else:
        lines.append("*No failure labels defined in preregistration.*")

    lines.append("")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def load_prereg(path: str) -> dict:
    """Load preregistration YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Detect regime changes in TLC data")
    parser.add_argument("--prereg", default="EST_PREREG.yaml", help="Preregistration file")
    parser.add_argument("--input", default="outputs/metrics_log.parquet", help="Metrics input")
    parser.add_argument("--coherence", default="outputs/coherence_report.json", help="Coherence report")
    parser.add_argument("--output", default="outputs/regime_report.md", help="Output report")
    parser.add_argument("--method", default=None, help="Override detection method")
    args = parser.parse_args()

    prereg = load_prereg(args.prereg)

    # Load metrics
    metrics = pd.read_parquet(args.input)
    print(f"Loaded {len(metrics)} days of metrics")

    # Load coherence
    with open(args.coherence) as f:
        coherence = json.load(f)
    print(f"Coherence status: {coherence['status']}")

    # Get detection configuration
    regime_config = prereg.get("regime_detection", {})
    method = args.method or regime_config.get("method", "robust_zscore_peak")
    params = regime_config.get("parameters", {})

    print(f"Detection method: {method}")

    # Get detector
    detector = get_detector(method)

    # Detect change points in dR/dt
    print("Detecting change points...")
    signal = metrics["dR_dt"].values
    dates = pd.to_datetime(metrics["date"]).values

    change_points = detector.detect(signal, dates, **params)
    print(f"Detected {len(change_points)} change points")

    # Run alternative methods if specified
    alt_methods = regime_config.get("alternative_methods", [])
    alt_results = {}
    for alt_method in alt_methods:
        if alt_method in DETECTORS:
            print(f"Running alternative: {alt_method}")
            alt_detector = get_detector(alt_method)
            alt_cps = alt_detector.detect(signal, dates, **params)
            alt_results[alt_method] = [cp.to_dict() for cp in alt_cps]
            print(f"  {alt_method}: {len(alt_cps)} change points")

    # Generate report
    report = generate_regime_report(
        change_points=change_points,
        coherence=coherence,
        prereg=prereg,
        detection_method=method,
        params=params,
    )

    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Saved report: {output_path}")

    # Save change points as JSON
    cp_path = output_path.parent / "change_points.json"

    # Optional: windowed change points when coherence is OK_PER_YEAR / OK_PER_WINDOW and prereg requests windowing.
    by_year = None
    by_window = None
    windowing = coherence.get("windowing", {})
    if coherence.get("status") == "OK_PER_YEAR" and windowing.get("type") == "yearly":
        by_year = {}
        dt = pd.to_datetime(metrics["date"], errors="coerce")
        years = dt.dt.year.astype("Int64")
        for year in sorted(y for y in years.dropna().unique()):
            mask = years == year
            y_signal = metrics.loc[mask, "dR_dt"].values
            y_dates = pd.to_datetime(metrics.loc[mask, "date"]).values
            y_cps = detector.detect(y_signal, y_dates, **params)
            by_year[str(int(year))] = [cp.to_dict() for cp in y_cps]

    if coherence.get("status") == "OK_PER_WINDOW" and windowing.get("type") in {"date_ranges", "rolling"}:
        by_window = {}
        dt = pd.to_datetime(metrics["date"], errors="coerce")
        for w in windowing.get("results", []) or []:
            name = str(w.get("name") or "window")
            start = pd.to_datetime(w.get("start"), errors="coerce")
            end = pd.to_datetime(w.get("end"), errors="coerce")
            if pd.isna(start) or pd.isna(end):
                continue
            mask = (dt >= start) & (dt <= end)
            w_signal = metrics.loc[mask, "dR_dt"].values
            w_dates = pd.to_datetime(metrics.loc[mask, "date"]).values
            w_cps = detector.detect(w_signal, w_dates, **params)
            by_window[name] = [cp.to_dict() for cp in w_cps]

    result = {
        "method": method,
        "parameters": params,
        "change_points": [cp.to_dict() for cp in change_points],
        "alternative_results": alt_results,
    }
    if by_year is not None:
        result["by_year"] = by_year
    if by_window is not None:
        result["by_window"] = by_window
    with open(cp_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved change points: {cp_path}")


if __name__ == "__main__":
    main()
