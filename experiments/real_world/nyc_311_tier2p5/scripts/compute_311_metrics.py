from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import StatisticsError, correlation, median
from typing import Any, Optional

try:
    import matplotlib.pyplot as plt  # type: ignore
    import matplotlib.dates as mdates  # type: ignore
except Exception:  # pragma: no cover
    plt = None
    mdates = None


@dataclass(frozen=True)
class RunConfig:
    input_csv: Path
    out_dir: Path
    window_days: int
    horizon_days: int
    agency: Optional[str]
    top_k_types: int
    rho_mode: str
    plot: str
    created_start: Optional[date]
    created_end: Optional[date]
    plot_tail_days: int
    coherence_rho_min: float


def _resolve_default_input() -> Path:
    here = Path(__file__).resolve()
    root = here.parents[1]  # .../nyc_311_tier2p5
    return root / "data" / "sample_311.csv"


def _parse_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "nat"}:
        return None

    # Common NYC Open Data exports: ISO8601 with or without "Z"
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    for candidate in (
        text,
        text.replace(" ", "T", 1),
    ):
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass

    # Fallback formats
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            dt = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None


def _parse_day(value: Any) -> Optional[date]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def _days_range(start: datetime.date, end: datetime.date) -> list[datetime.date]:
    days: list[datetime.date] = []
    cur = start
    while cur <= end:
        days.append(cur)
        cur = (datetime.combine(cur, datetime.min.time()) + timedelta(days=1)).date()
    return days


def _rolling_median(values: list[Optional[float]], window: int, min_valid: int) -> list[Optional[float]]:
    out: list[Optional[float]] = [None] * len(values)
    for i in range(len(values)):
        left = i - window + 1
        if left < 0:
            continue
        chunk = [v for v in values[left : i + 1] if v is not None]
        if len(chunk) < min_valid:
            continue
        out[i] = float(median(chunk))
    return out


def _forward_sum(arr: list[int], horizon_days: int) -> list[Optional[int]]:
    # sum_{i=t..t+horizon_days} arr[i]  (inclusive)
    out: list[Optional[int]] = [None] * len(arr)
    window_len = horizon_days + 1
    if window_len <= 0:
        return out

    running = 0
    for i, v in enumerate(arr):
        running += int(v)
        if i >= window_len:
            running -= int(arr[i - window_len])
        if i >= window_len - 1:
            start = i - (window_len - 1)
            out[start] = running
    return out


def _ranks(values: list[float]) -> list[float]:
    pairs = sorted((v, i) for i, v in enumerate(values))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for _, idx in pairs[i:j]:
            ranks[idx] = avg_rank
        i = j
    return ranks


def _spearman_rho(xs: list[float], ys: list[float]) -> Optional[float]:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx = _ranks(xs)
    ry = _ranks(ys)
    try:
        return float(correlation(rx, ry))
    except (StatisticsError, ZeroDivisionError):
        return None


@dataclass(frozen=True)
class Event:
    created_day: datetime.date
    closed_day: Optional[datetime.date]
    lag_days: Optional[float]
    agency: Optional[str]
    complaint_type: Optional[str]


def load_events(config: RunConfig) -> list[Event]:
    with config.input_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        if "created_date" not in fieldnames:
            raise ValueError("Missing required column: created_date")

        raw_rows = list(reader)

    # Optional boundary filters (done in stages so top-K is computed *within* the boundary).
    # 1) created-date window
    parsed_rows: list[dict[str, Any]] = []
    for r in raw_rows:
        created_dt = _parse_dt(r.get("created_date"))
        if created_dt is None:
            continue
        created_day = created_dt.date()
        if config.created_start and created_day < config.created_start:
            continue
        if config.created_end and created_day > config.created_end:
            continue
        r["_created_dt"] = created_dt
        r["_created_day"] = created_day
        parsed_rows.append(r)

    # 2) agency filter
    if config.agency:
        parsed_rows = [r for r in parsed_rows if (r.get("agency") or "").strip() == config.agency]

    if config.top_k_types > 0 and "complaint_type" in fieldnames:
        counts: dict[str, int] = {}
        for r in parsed_rows:
            t = (r.get("complaint_type") or "").strip()
            if not t:
                continue
            counts[t] = counts.get(t, 0) + 1
        top_types = {t for t, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[: config.top_k_types]}
        parsed_rows = [r for r in parsed_rows if (r.get("complaint_type") or "").strip() in top_types]

    events: list[Event] = []
    for r in parsed_rows:
        created_dt = r.get("_created_dt")
        created_day = r.get("_created_day")
        if not isinstance(created_dt, datetime) or not isinstance(created_day, date):
            continue
        closed_dt = _parse_dt(r.get("closed_date")) if "closed_date" in fieldnames else None

        lag_days: Optional[float] = None
        closed_day: Optional[datetime.date] = None
        if closed_dt is not None:
            lag_days = (closed_dt - created_dt).total_seconds() / 86400.0
            if lag_days < 0:
                continue
            closed_day = closed_dt.date()

        events.append(
            Event(
                created_day=created_day,
                closed_day=closed_day,
                lag_days=lag_days,
                agency=(r.get("agency") or "").strip() or None,
                complaint_type=(r.get("complaint_type") or "").strip() or None,
            )
        )

    return events


def compute_daily(
    events: list[Event],
    window_days: int,
    horizon_days: int,
    *,
    rho_mode: str,
) -> list[dict[str, Any]]:
    if not events:
        raise ValueError("Dataset has no usable rows after filtering.")

    min_day = min(e.created_day for e in events)
    max_day = max(max(e.created_day, e.closed_day or e.created_day) for e in events)
    days = _days_range(min_day, max_day)

    arrivals: dict[datetime.date, int] = {}
    closures: dict[datetime.date, int] = {}
    close_lags: dict[datetime.date, list[float]] = {}

    for e in events:
        arrivals[e.created_day] = arrivals.get(e.created_day, 0) + 1
        if e.closed_day is not None:
            closures[e.closed_day] = closures.get(e.closed_day, 0) + 1
            if e.lag_days is not None:
                close_lags.setdefault(e.closed_day, []).append(float(e.lag_days))

    arrivals_series = [int(arrivals.get(d, 0)) for d in days]
    closures_series = [int(closures.get(d, 0)) for d in days]

    backlog_series: list[int] = []
    running = 0
    for a, c in zip(arrivals_series, closures_series, strict=True):
        running += int(a) - int(c)
        backlog_series.append(int(running))

    vl_median_days: list[Optional[float]] = []
    for d in days:
        lags = close_lags.get(d)
        if not lags:
            vl_median_days.append(None)
        else:
            vl_median_days.append(float(median(lags)))

    tau_g_days = vl_median_days

    tau_g_medW = _rolling_median(tau_g_days, window_days, min_valid=max(1, window_days // 2))
    rho_mode_norm = (rho_mode or "").strip().lower().replace("-", "_")
    if rho_mode_norm in {"window", "window_normalized", "window_normalised", "v2"}:
        tau_u_days = [float(window_days) for _ in arrivals_series]
        tau_u_medW = [float(window_days) if i >= window_days - 1 else None for i in range(len(days))]
    else:
        tau_u_days = [1.0 / max(a, 1) for a in arrivals_series]
        tau_u_medW = _rolling_median(tau_u_days, window_days, min_valid=window_days)

    rho: list[Optional[float]] = []
    for u, g in zip(tau_u_medW, tau_g_medW, strict=True):
        if u is None or g is None or u == 0:
            rho.append(None)
        else:
            rho.append(float(g) / float(u))

    # Forward normalized backlog drift: (B_{t+H} - B_t) / sum_{i=t..t+H} A_i
    arrivals_fwd = _forward_sum(arrivals_series, horizon_days)
    drift_norm: list[Optional[float]] = [None] * len(days)
    for i in range(len(days)):
        j = i + horizon_days
        if j >= len(days):
            continue
        denom = arrivals_fwd[i]
        if denom is None or denom == 0:
            continue
        drift = backlog_series[j] - backlog_series[i]
        drift_norm[i] = float(drift) / float(denom)

    # Event flags
    event_rho_gt_1 = [bool(v is not None and v > 1.0) for v in rho]

    event_sustained = [False] * len(days)
    for i in range(len(days)):
        left = i - window_days + 1
        if left < 0:
            continue
        window = rho[left : i + 1]
        if any(v is None for v in window):
            continue
        if all(v > 1.0 for v in window if v is not None):
            event_sustained[i] = True

    # P10-like coherence diagnostic (sign of corr(ΔB, drift_norm))
    dB: list[Optional[float]] = [None] * len(days)
    for i in range(1, len(days)):
        dB[i] = float(backlog_series[i] - backlog_series[i - 1])

    paired_dB: list[float] = []
    paired_drift: list[float] = []
    for a, b in zip(dB, drift_norm, strict=True):
        if a is None or b is None:
            continue
        paired_dB.append(float(a))
        paired_drift.append(float(b))

    rho_spearman = _spearman_rho(paired_dB, paired_drift)
    corr_sign = None
    if rho_spearman is not None:
        corr_sign = 0 if abs(rho_spearman) < 1e-12 else (1 if rho_spearman > 0 else -1)

    rows: list[dict[str, Any]] = []
    for i, d in enumerate(days):
        rows.append(
            {
                "day": d.isoformat(),
                "arrivals": arrivals_series[i],
                "closures": closures_series[i],
                "backlog": backlog_series[i],
                "vl_median_days": vl_median_days[i],
                "tau_u_days": tau_u_days[i],
                "tau_g_days": tau_g_days[i],
                "tau_u_medW": tau_u_medW[i],
                "tau_g_medW": tau_g_medW[i],
                "rho": rho[i],
                "drift_norm": drift_norm[i],
                "event_rho_gt_1": event_rho_gt_1[i],
                "event_rho_gt_1_sustainedW": event_sustained[i],
                "coherence_spearman_rho_dB_vs_drift": rho_spearman,
                "coherence_sign_dB_vs_drift": corr_sign,
            }
        )

    return rows


def _write_svg_stub(rows: list[dict[str, Any]], out_path: Path) -> None:
    # Minimal, dependency-free visualization: rho and backlog over time (two stacked plots).
    xs = list(range(len(rows)))
    rho_vals = [r.get("rho") for r in rows]
    backlog_vals = [r.get("backlog") for r in rows]

    def _minmax(vals: list[Any]) -> tuple[float, float]:
        nums = [float(v) for v in vals if v is not None]
        if not nums:
            return (0.0, 1.0)
        return (min(nums), max(nums))

    rho_min, rho_max = _minmax(rho_vals)
    b_min, b_max = _minmax(backlog_vals)

    def _scale(v: float, vmin: float, vmax: float, height: int) -> float:
        if vmax <= vmin:
            return height / 2.0
        return (1.0 - (v - vmin) / (vmax - vmin)) * height

    width = 900
    height = 400
    pad = 40
    plot_h = (height - pad * 3) / 2

    def _poly(vals: list[Any], vmin: float, vmax: float, y0: float) -> str:
        pts = []
        for i, raw in enumerate(vals):
            if raw is None:
                continue
            x = pad + (i / max(1, len(vals) - 1)) * (width - 2 * pad)
            y = y0 + _scale(float(raw), vmin, vmax, int(plot_h))
            pts.append(f"{x:.1f},{y:.1f}")
        return " ".join(pts)

    rho_poly = _poly(rho_vals, rho_min, rho_max, pad)
    b_poly = _poly(backlog_vals, b_min, b_max, pad * 2 + plot_h)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect x="0" y="0" width="{width}" height="{height}" fill="white"/>
  <text x="{pad}" y="22" font-family="sans-serif" font-size="14" fill="#111">NYC 311 Tier-2.5 (demo): rho and backlog</text>
  <text x="{pad}" y="{pad - 10}" font-family="sans-serif" font-size="12" fill="#111">rho (tempo mismatch)</text>
  <polyline fill="none" stroke="#2a6fdb" stroke-width="2" points="{rho_poly}"/>
  <line x1="{pad}" y1="{pad + plot_h:.1f}" x2="{width - pad}" y2="{pad + plot_h:.1f}" stroke="#ddd"/>
  <text x="{pad}" y="{pad * 2 + plot_h - 10:.1f}" font-family="sans-serif" font-size="12" fill="#111">backlog</text>
  <polyline fill="none" stroke="#0b8f3a" stroke-width="2" points="{b_poly}"/>
  <line x1="{pad}" y1="{pad * 3 + plot_h * 2:.1f}" x2="{width - pad}" y2="{pad * 3 + plot_h * 2:.1f}" stroke="#ddd"/>
</svg>
"""
    out_path.write_text(svg, encoding="utf-8")


def write_outputs(
    rows: list[dict[str, Any]],
    out_dir: Path,
    plot: str,
    *,
    created_end_marker: Optional[date],
    plot_tail_days: int,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / "metrics_daily.csv"

    with metrics_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    # Always produce an SVG (dependency-free), and optionally PNG if matplotlib exists.
    svg_path = out_dir / "overview.svg"
    _write_svg_stub(rows, svg_path)

    fig_path = out_dir / "overview.png"
    plot_mode = plot.lower().strip()
    want_png = plot_mode in {"png", "both"}

    if plot.lower() == "none":
        # Ensure stale PNGs don't survive runs that don't generate them.
        if fig_path.exists():
            try:
                fig_path.unlink()
            except OSError:
                pass
        return

    if plt is None:
        # Ensure stale PNGs don't survive runs when matplotlib isn't available.
        if fig_path.exists():
            try:
                fig_path.unlink()
            except OSError:
                pass
        print("Note: matplotlib not available; wrote overview.svg only (no overview.png).")
        return

    if not want_png:
        # Caller explicitly asked not to generate PNG; remove any previous artifact.
        if fig_path.exists():
            try:
                fig_path.unlink()
            except OSError:
                pass
        return

    plot_rows = rows
    if created_end_marker and plot_tail_days >= 0:
        plot_end = created_end_marker + timedelta(days=int(plot_tail_days))
        plot_rows = [r for r in rows if date.fromisoformat(str(r["day"])) <= plot_end]

    days = [datetime.fromisoformat(str(r["day"])).replace(tzinfo=timezone.utc) for r in plot_rows]
    rho_vals = [float("nan") if r["rho"] is None else float(r["rho"]) for r in plot_rows]
    backlog_vals = [float(r["backlog"]) for r in plot_rows]
    arrivals = [float(r["arrivals"]) for r in plot_rows]
    closures = [float(r["closures"]) for r in plot_rows]
    vl = [float("nan") if r["vl_median_days"] is None else float(r["vl_median_days"]) for r in plot_rows]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    ax = axes[0, 0]
    ax.plot(days, rho_vals, label="rho (median W)")
    ax.axhline(1.0, color="orange", linestyle="--", linewidth=1, label="rho=1")
    if created_end_marker:
        ax.axvline(datetime.combine(created_end_marker, datetime.min.time(), tzinfo=timezone.utc), color="grey", linestyle=":", linewidth=1)
    ax.set_title("Tempo mismatch ratio (rho)")
    # Avoid categorical-axis rendering (which produces unreadable tick labels).
    if mdates is not None:
        locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.legend(loc="upper left")

    ax = axes[0, 1]
    ax.plot(days, backlog_vals, label="backlog")
    if created_end_marker:
        ax.axvline(datetime.combine(created_end_marker, datetime.min.time(), tzinfo=timezone.utc), color="grey", linestyle=":", linewidth=1)
    ax.set_title("Backlog")
    if mdates is not None:
        locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    ax = axes[1, 0]
    ax.plot(days, arrivals, alpha=0.8, label="arrivals", linewidth=1.5)
    ax.plot(days, closures, alpha=0.8, label="closures", linewidth=1.5)
    if created_end_marker:
        ax.axvline(datetime.combine(created_end_marker, datetime.min.time(), tzinfo=timezone.utc), color="grey", linestyle=":", linewidth=1)
    ax.set_title("Arrivals vs closures")
    if mdates is not None:
        locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.legend(loc="upper left")

    ax = axes[1, 1]
    ax.plot(days, vl, label="VL median (days)")
    if created_end_marker:
        ax.axvline(datetime.combine(created_end_marker, datetime.min.time(), tzinfo=timezone.utc), color="grey", linestyle=":", linewidth=1)
    ax.set_title("Validation lag proxy (median close lag)")
    if mdates is not None:
        locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    fig.tight_layout()
    fig.savefig(fig_path, dpi=200)
    plt.close(fig)


def _longest_zero_run(values: list[int]) -> int:
    best = 0
    cur = 0
    for v in values:
        if int(v) == 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def _first_float(rows: list[dict[str, Any]], key: str) -> Optional[float]:
    for r in rows:
        v = r.get(key)
        if v is None:
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return None


def write_run_diagnostics(
    *,
    config: RunConfig,
    rows: list[dict[str, Any]],
    created_end_marker: Optional[date],
) -> None:
    out_dir = config.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    days = [date.fromisoformat(str(r["day"])) for r in rows]
    created_min = min(days)
    created_max = max(date.fromisoformat(str(r["day"])) for r in rows if r.get("arrivals") is not None)

    arrivals_series = [int(r.get("arrivals") or 0) for r in rows]
    closures_series = [int(r.get("closures") or 0) for r in rows]

    created_end = created_end_marker or config.created_end
    if created_end is None:
        created_end = max(days)

    in_window_idxs = [i for i, d in enumerate(days) if d <= created_end]
    arrivals_in_window = [arrivals_series[i] for i in in_window_idxs]

    tail_days = (max(days) - created_end).days if max(days) > created_end else 0

    rho_spearman = _first_float(rows, "coherence_spearman_rho_dB_vs_drift")
    rho_sign = None
    raw_sign = None
    for r in rows:
        raw_sign = r.get("coherence_sign_dB_vs_drift")
        if raw_sign is not None:
            break
    if raw_sign is not None:
        try:
            rho_sign = int(raw_sign)
        except (TypeError, ValueError):
            rho_sign = None

    coherence_status = "UNKNOWN"
    if rho_spearman is None:
        coherence_status = "FAIL"
    elif abs(rho_spearman) < float(config.coherence_rho_min):
        coherence_status = "FAIL"
    else:
        coherence_status = "PASS"

    label = "ESTIMATOR_UNSTABLE" if coherence_status == "FAIL" else "OK_TO_INTERPRET"

    longest_zero_run_arrivals = _longest_zero_run(arrivals_in_window) if arrivals_in_window else 0
    longest_zero_run_closures = _longest_zero_run(closures_series) if closures_series else 0

    n_days = len(rows)
    def _is_true(value: Any) -> bool:
        return str(value).strip().lower() in {"true", "1", "yes", "y"}

    def _is_defined(value: Any) -> bool:
        if value is None:
            return False
        text = str(value).strip()
        if text == "":
            return False
        return text.lower() not in {"none", "nan", "nat"}

    n_event_total = sum(1 for r in rows if _is_true(r.get("event_rho_gt_1_sustainedW")))
    n_defined_drift = sum(1 for r in rows if _is_defined(r.get("drift_norm")))

    event_days = [d for r, d in zip(rows, days) if _is_true(r.get("event_rho_gt_1_sustainedW"))]
    drift_days = [d for r, d in zip(rows, days) if _is_defined(r.get("drift_norm"))]
    overlap_days = sorted(set(event_days).intersection(drift_days))
    n_event_paired = int(len(overlap_days))
    n_non_event_paired = int(len(set(drift_days) - set(event_days)))

    def _range_or_none(day_list: list[date]) -> Optional[dict[str, str]]:
        if not day_list:
            return None
        return {"start": min(day_list).isoformat(), "end": max(day_list).isoformat()}

    drift_range = _range_or_none(drift_days)
    event_range = _range_or_none(event_days)
    overlap_range = _range_or_none(overlap_days)

    drift_rho_values: list[float] = []
    if drift_range is not None:
        drift_start = date.fromisoformat(drift_range["start"])
        drift_end = date.fromisoformat(drift_range["end"])
        for r, d in zip(rows, days):
            if d < drift_start or d > drift_end:
                continue
            if not _is_defined(r.get("rho")):
                continue
            try:
                drift_rho_values.append(float(r["rho"]))
            except (TypeError, ValueError, KeyError):
                continue

    drift_rho_summary: dict[str, Any] = {
        "n_days": int(len(drift_rho_values)),
        "median": None,
        "max": None,
        "days_gt_1": int(sum(1 for v in drift_rho_values if v > 1.0)),
        "days_le_1": int(sum(1 for v in drift_rho_values if v <= 1.0)),
    }
    if drift_rho_values:
        sorted_vals = sorted(drift_rho_values)
        drift_rho_summary["median"] = float(sorted_vals[len(sorted_vals) // 2])
        drift_rho_summary["max"] = float(max(drift_rho_values))

    payload: dict[str, Any] = {
        "input_csv": str(config.input_csv),
        "out_dir": str(out_dir),
        "agency": config.agency,
        "top_k_types": int(config.top_k_types),
        "window_days": int(config.window_days),
        "horizon_days": int(config.horizon_days),
        "rho_mode": config.rho_mode,
        "created_start": config.created_start.isoformat() if config.created_start else None,
        "created_end": created_end.isoformat() if created_end else None,
        "tail_days_after_created_end": int(tail_days),
        "n_days_total": int(n_days),
        "n_days_drift_defined": int(n_defined_drift),
        # Back-compat: "n_event_sustained" historically meant "total sustained event days".
        "n_event_sustained": int(n_event_total),
        "n_event_sustained_total": int(n_event_total),
        # For preregistered H1-style checks, only count events on days where drift_norm is defined.
        "n_event_sustained_paired": int(n_event_paired),
        "n_non_event_paired": int(n_non_event_paired),
        "domain_overlap": {
            "note": (
                "For H1-style checks, event days must overlap with days where drift_norm is defined. "
                "With a created-date boundary, sustained events can appear in the tail where arrivals=0 by construction, "
                "while drift_norm is undefined outside the created window."
            ),
            "event_days_total": int(len(event_days)),
            "drift_days_total": int(len(drift_days)),
            "overlap_days": int(len(overlap_days)),
            "event_days_paired": int(n_event_paired),
            "non_event_days_paired": int(n_non_event_paired),
            "event_range": event_range,
            "drift_range": drift_range,
            "overlap_range": overlap_range,
            "rho_in_drift_range": drift_rho_summary,
        },
        "coherence": {
            "metric": "spearman(dB_t, drift_norm(t;H))",
            "rho": rho_spearman,
            "sign": rho_sign,
            "rho_min": float(config.coherence_rho_min),
            "status": coherence_status,
            "label": label,
        },
        "integrity_hints": {
            "longest_zero_run_arrivals_within_created_window_days": int(longest_zero_run_arrivals),
            "longest_zero_run_closures_over_full_series_days": int(longest_zero_run_closures),
            "note": (
                "If you used a created-date boundary, arrivals after created_end are expected to be 0 by construction; "
                "closures may continue (tail). Large late-time lags can be tail artifacts."
            ),
        },
    }

    (out_dir / "run_diagnostics.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md_lines: list[str] = []
    md_lines.append("# NYC 311 Tier-2.5 run diagnostics")
    md_lines.append("")
    md_lines.append("This file is a run-level summary to make the preregistered demo auditable.")
    md_lines.append("For the decision procedure, see `docs/est/diagnostics.md`.")
    md_lines.append("")
    md_lines.append("## Run config")
    md_lines.append(f"- input: `{config.input_csv}`")
    md_lines.append(f"- out_dir: `{out_dir}`")
    md_lines.append(f"- agency: `{config.agency or 'ALL'}`")
    md_lines.append(f"- top_k_types: `{config.top_k_types}`")
    md_lines.append(f"- W (window_days): `{config.window_days}`")
    md_lines.append(f"- H (horizon_days): `{config.horizon_days}`")
    md_lines.append(f"- rho_mode: `{config.rho_mode}`")
    md_lines.append(f"- created_start: `{config.created_start.isoformat() if config.created_start else 'None'}`")
    md_lines.append(f"- created_end: `{created_end.isoformat() if created_end else 'None'}`")
    md_lines.append(f"- tail_days_after_created_end: `{tail_days}`")
    md_lines.append("")
    md_lines.append("## Counts")
    md_lines.append(f"- days_total: `{n_days}`")
    md_lines.append(f"- days_with_drift_norm: `{n_defined_drift}`")
    md_lines.append(f"- sustained_event_days_total: `{n_event_total}`  (`event_rho_gt_1_sustainedW`)")
    md_lines.append(f"- sustained_event_days_paired: `{n_event_paired}`  (event & drift intersection; use this for prereg H1 counts)")
    md_lines.append("")
    md_lines.append("## Domain overlap (why events may be untestable)")
    md_lines.append(f"- event_days_total: `{len(event_days)}`")
    md_lines.append(f"- drift_days_total: `{len(drift_days)}`  (`drift_norm` defined)")
    md_lines.append(f"- overlap_days: `{len(overlap_days)}`  (event & drift intersection)")
    md_lines.append(f"- non_event_days_paired: `{n_non_event_paired}`  (drift defined, not event)")
    md_lines.append(f"- event_range: `{event_range or 'None'}`")
    md_lines.append(f"- drift_range: `{drift_range or 'None'}`")
    md_lines.append(f"- overlap_range: `{overlap_range or 'None'}`")
    md_lines.append(f"- rho_in_drift_range: `{drift_rho_summary}`")
    if created_end_marker or config.created_end:
        md_lines.append(
            "- note: with a created-date boundary, arrivals after `created_end` are 0 by construction; sustained events can appear in the tail while `drift_norm` is undefined."
        )
    md_lines.append("")
    md_lines.append("## Coherence gate (P10-like)")
    md_lines.append(f"- spearman_rho(dB, drift_norm): `{rho_spearman}`")
    md_lines.append(f"- sign: `{rho_sign}`")
    md_lines.append(f"- threshold (rho_min): `{config.coherence_rho_min}`")
    md_lines.append(f"- status: **{coherence_status}** -> label: **{label}**")
    md_lines.append("")
    md_lines.append("## Integrity hints (non-conclusive)")
    md_lines.append(
        f"- longest_zero_run(arrivals) within created window: `{longest_zero_run_arrivals}` days (large values often indicate export/filter artifacts)"
    )
    md_lines.append(f"- longest_zero_run(closures) over full plotted range: `{longest_zero_run_closures}` days")
    md_lines.append("")
    md_lines.append("## Interpretation guardrails")
    md_lines.append("- Do not treat this demo as 'real-world validation' of FIT; it is a preregistered monitoring-style demonstration.")
    md_lines.append("- If coherence is FAIL (`ESTIMATOR_UNSTABLE`), do not interpret H1 as supported/challenged under this estimator setup.")
    md_lines.append("- Use `scripts/sanity_check_311_boundary.py` to generate the boundary sanity report before narrative interpretation.")
    md_lines.append("")
    (out_dir / "run_diagnostics.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def parse_args() -> RunConfig:
    parser = argparse.ArgumentParser(description="Compute Tier-2.5 metrics from NYC 311-style logs.")
    parser.add_argument("--input", type=str, default=str(_resolve_default_input()), help="CSV path")
    parser.add_argument("--outdir", type=str, default="", help="Output directory (default: ./outputs under demo)")
    parser.add_argument("--window", type=int, default=14, help="Rolling window W (days); recommended default: 14")
    parser.add_argument("--horizon", type=int, default=14, help="Forward horizon H (days) for drift_norm; recommended default: 14")
    parser.add_argument("--agency", type=str, default="", help="Optional: agency filter (exact match)")
    parser.add_argument("--top-k-types", type=int, default=10, help="Keep top-K complaint types (0 disables)")
    parser.add_argument(
        "--rho-mode",
        type=str,
        default="window_normalized",
        help="rho definition: window_normalized (v2, default) | per_ticket (v1)",
    )
    parser.add_argument(
        "--plot",
        type=str,
        default="both",
        help="Plot output: none | svg | png | both (svg is always written; png requires matplotlib)",
    )
    parser.add_argument("--created-start", type=str, default="", help="Optional: created_date start boundary (YYYY-MM-DD)")
    parser.add_argument("--created-end", type=str, default="", help="Optional: created_date end boundary (YYYY-MM-DD)")
    parser.add_argument(
        "--plot-tail-days",
        type=int,
        default=-1,
        help="If created-end is set, cap plots to (created_end + N days). Use -1 for full range.",
    )
    parser.add_argument(
        "--coherence-rho-min",
        type=float,
        default=0.2,
        help="Coherence gate threshold used only for labeling in run_diagnostics (see prereg for official threshold).",
    )
    args = parser.parse_args()

    input_csv = Path(args.input).expanduser().resolve()

    here = Path(__file__).resolve()
    demo_root = here.parents[1]
    out_dir = Path(args.outdir).expanduser().resolve() if args.outdir else (demo_root / "outputs")

    agency = args.agency.strip() or None

    created_start = _parse_day(args.created_start) if str(args.created_start).strip() else None
    created_end = _parse_day(args.created_end) if str(args.created_end).strip() else None
    if (args.created_start and created_start is None) or (args.created_end and created_end is None):
        raise ValueError("created-start/created-end must be YYYY-MM-DD if provided")
    if created_start and created_end and created_start > created_end:
        raise ValueError("created-start must be <= created-end")

    return RunConfig(
        input_csv=input_csv,
        out_dir=out_dir,
        window_days=int(args.window),
        horizon_days=int(args.horizon),
        agency=agency,
        top_k_types=int(args.top_k_types),
        rho_mode=str(args.rho_mode),
        plot=str(args.plot),
        created_start=created_start,
        created_end=created_end,
        plot_tail_days=int(args.plot_tail_days),
        coherence_rho_min=float(args.coherence_rho_min),
    )


def main() -> None:
    config = parse_args()
    if not config.input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {config.input_csv}")

    events = load_events(config)
    created_end_marker = config.created_end or max((e.created_day for e in events), default=None)
    daily = compute_daily(events, window_days=config.window_days, horizon_days=config.horizon_days, rho_mode=config.rho_mode)
    write_outputs(daily, config.out_dir, config.plot, created_end_marker=created_end_marker, plot_tail_days=config.plot_tail_days)
    write_run_diagnostics(config=config, rows=daily, created_end_marker=created_end_marker)
    print(f"Wrote: {config.out_dir / 'metrics_daily.csv'}")
    print(f"Wrote: {config.out_dir / 'overview.svg'}")
    if (config.out_dir / 'overview.png').exists():
        print(f"Wrote: {config.out_dir / 'overview.png'}")
    print(f"Wrote: {config.out_dir / 'run_diagnostics.json'}")
    print(f"Wrote: {config.out_dir / 'run_diagnostics.md'}")


if __name__ == "__main__":
    main()
