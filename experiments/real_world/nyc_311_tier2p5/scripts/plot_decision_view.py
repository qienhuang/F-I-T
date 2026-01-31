from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class Series:
    days: list[date]
    rho: list[float]
    backlog: list[float]


def _parse_day(text: str) -> date:
    return datetime.fromisoformat(text.strip()).date()


def _read_metrics(path: Path) -> Series:
    days: list[date] = []
    rho: list[float] = []
    backlog: list[float] = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = _parse_day(row["day"])
            days.append(d)
            rho_raw = (row.get("rho") or "").strip()
            rho.append(float(rho_raw) if rho_raw else float("nan"))
            backlog.append(float(row["backlog"]))

    return Series(days=days, rho=rho, backlog=backlog)


def _find_markers(series: Series) -> tuple[Optional[int], int]:
    first_over_one: Optional[int] = None
    for i, v in enumerate(series.rho):
        if v == v and v > 1.0:  # not NaN and > 1
            first_over_one = i
            break
    peak_backlog_i = max(range(len(series.backlog)), key=lambda i: series.backlog[i])
    return first_over_one, peak_backlog_i


def _shade(ax: plt.Axes, x0: date, x1: date, *, color: str, label: str) -> None:
    ax.axvspan(x0, x1, color=color, alpha=0.08, linewidth=0)
    y0, y1 = ax.get_ylim()
    ax.text(x0, y1 - (y1 - y0) * 0.08, label, fontsize=9, color="#333", va="top")


def plot_decision_view(
    *,
    series: Series,
    out_png: Optional[Path],
    out_svg: Optional[Path],
    created_end: Optional[date],
    title: str,
) -> None:
    fig, (ax_rho, ax_b) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    xs = [datetime.combine(d, datetime.min.time()) for d in series.days]
    ax_rho.plot(xs, series.rho, color="#1f77b4", linewidth=1.8, label="rho (window-normalized)")
    ax_rho.axhline(1.0, color="#ff7f0e", linestyle="--", linewidth=1.0, alpha=0.8, label="rho = 1")
    ax_rho.axhline(3.0, color="#d62728", linestyle="--", linewidth=1.0, alpha=0.7, label="rho = 3")
    ax_rho.set_ylabel("rho")
    ax_rho.set_title(title)
    ax_rho.legend(loc="upper left", ncol=3, fontsize=9)

    ax_b.plot(xs, series.backlog, color="#2ca02c", linewidth=1.8, label="backlog")
    ax_b.set_ylabel("backlog")
    ax_b.legend(loc="upper left", fontsize=9)

    # Mark the boundary: after created_end, arrivals are zero by construction (if boundary was by created_date).
    if created_end is not None:
        x_end = datetime.combine(created_end, datetime.min.time())
        for ax in (ax_rho, ax_b):
            ax.axvline(x_end, color="#555", linestyle=":", linewidth=1.0, alpha=0.8)
        ax_b.text(
            x_end,
            ax_b.get_ylim()[1],
            " created_end ",
            fontsize=9,
            color="#555",
            va="top",
            ha="left",
            rotation=0,
        )

    # Add three light “story windows” (illustrative only, not part of prereg inference).
    start = series.days[0]
    end = series.days[-1]
    boundaries: list[tuple[date, date, str]] = []

    if created_end is not None and start <= created_end < end:
        boundaries.append((start, created_end, "within created boundary (in-scope)"))
        boundaries.append((created_end, end, "closure tail (out of scope)"))
    else:
        first_over_one, peak_i = _find_markers(series)
        peak = series.days[peak_i]

        if first_over_one is None:
            # Fall back to equal thirds if rho never crosses 1.
            n = len(series.days)
            a = series.days[n // 3]
            b = series.days[(2 * n) // 3]
            boundaries = [(start, a, "early"), (a, b, "middle"), (b, end, "late")]
        else:
            cross = series.days[first_over_one]
            boundaries = [(start, cross, "pre-mismatch"), (cross, peak, "mismatch + buildup"), (peak, end, "unwind / tail")]

    palette = ["#4c78a8", "#f58518", "#54a24b"]
    for ax in (ax_rho, ax_b):
        ylims = ax.get_ylim()
        ax.set_ylim(*ylims)
        for i, (x0, x1, label) in enumerate(boundaries):
            color = palette[i % len(palette)]
            _shade(ax, x0, x1, color=color, label=label)

    locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
    ax_b.xaxis.set_major_locator(locator)
    ax_b.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax_b.set_xlabel("date")

    fig.tight_layout()
    if out_png is not None:
        out_png.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_png, dpi=200)
    if out_svg is not None:
        out_svg.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_svg)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a decision-maker view (rho + backlog) from metrics_daily.csv.")
    parser.add_argument("--metrics", type=str, required=True, help="Path to metrics_daily.csv")
    parser.add_argument("--outdir", type=str, required=True, help="Output directory for figures")
    parser.add_argument("--created-end", type=str, default="", help="Optional created-date boundary end (YYYY-MM-DD)")
    parser.add_argument("--title", type=str, default="NYC 311 Tier-2.5 (demo): rho and backlog", help="Plot title")
    args = parser.parse_args()

    metrics_path = Path(args.metrics).expanduser().resolve()
    out_dir = Path(args.outdir).expanduser().resolve()
    created_end = date.fromisoformat(args.created_end) if args.created_end.strip() else None

    series = _read_metrics(metrics_path)
    plot_decision_view(
        series=series,
        out_png=out_dir / "decision_view.png",
        out_svg=out_dir / "decision_view.svg",
        created_end=created_end,
        title=str(args.title),
    )
    print(f"Wrote: {out_dir / 'decision_view.png'}")
    print(f"Wrote: {out_dir / 'decision_view.svg'}")


if __name__ == "__main__":
    main()
