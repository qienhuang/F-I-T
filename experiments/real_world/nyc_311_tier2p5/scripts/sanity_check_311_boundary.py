from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Any, Optional


def _parse_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "nat"}:
        return None

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    for candidate in (text, text.replace(" ", "T", 1)):
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def _days_range(start: date, end: date) -> list[date]:
    out: list[date] = []
    cur = start
    while cur <= end:
        out.append(cur)
        cur = (datetime.combine(cur, datetime.min.time()) + timedelta(days=1)).date()
    return out


def _longest_zero_run(values: list[int]) -> int:
    best = 0
    cur = 0
    for v in values:
        if v == 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


@dataclass(frozen=True)
class Event:
    created_day: date
    closed_day: Optional[date]
    lag_days: Optional[float]
    agency: Optional[str]
    complaint_type: Optional[str]


@dataclass(frozen=True)
class SanitySummary:
    rows_total: int
    rows_with_created: int
    rows_after_agency: int
    rows_after_topk: int
    rows_in_created_window: int
    missing_closed: int
    negative_lag_dropped: int
    created_min: date
    created_max: date
    closed_max: Optional[date]
    tail_days_after_created_end: Optional[int]
    median_lag_days: Optional[float]
    p90_lag_days: Optional[float]
    zero_run_arrivals_inside_window: int
    zero_run_closures_in_tail: Optional[int]


def _p90(values: list[float]) -> float:
    if not values:
        raise ValueError("empty")
    xs = sorted(values)
    # Nearest-rank definition
    k = int((0.9 * (len(xs) - 1)))
    return float(xs[k])


def load_events(
    *,
    input_csv: Path,
    agency: Optional[str],
    top_k_types: int,
) -> tuple[list[Event], SanitySummary]:
    with input_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        if "created_date" not in fieldnames:
            raise ValueError("Missing required column: created_date")
        rows = list(reader)

    rows_total = len(rows)

    parsed: list[dict[str, Any]] = []
    rows_with_created = 0
    for r in rows:
        created_dt = _parse_dt(r.get("created_date"))
        if created_dt is None:
            continue
        rows_with_created += 1
        r["_created_dt"] = created_dt
        r["_agency"] = (r.get("agency") or "").strip() or None
        r["_complaint_type"] = (r.get("complaint_type") or "").strip() or None
        parsed.append(r)

    if agency:
        parsed = [r for r in parsed if (r.get("_agency") or "") == agency]
    rows_after_agency = len(parsed)

    if top_k_types > 0 and any(r.get("_complaint_type") for r in parsed):
        counts: dict[str, int] = {}
        for r in parsed:
            t = r.get("_complaint_type") or ""
            if t:
                counts[t] = counts.get(t, 0) + 1
        top_types = {t for t, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_k_types]}
        parsed = [r for r in parsed if (r.get("_complaint_type") or "") in top_types]
    rows_after_topk = len(parsed)

    negative_lag_dropped = 0
    events: list[Event] = []
    for r in parsed:
        created_dt = r["_created_dt"]
        created_day = created_dt.date()
        closed_dt = _parse_dt(r.get("closed_date")) if "closed_date" in r else _parse_dt(r.get("closed_date"))
        closed_day: Optional[date] = None
        lag_days: Optional[float] = None
        if closed_dt is not None:
            lag_days = (closed_dt - created_dt).total_seconds() / 86400.0
            if lag_days < 0:
                negative_lag_dropped += 1
                continue
            closed_day = closed_dt.date()

        events.append(
            Event(
                created_day=created_day,
                closed_day=closed_day,
                lag_days=lag_days,
                agency=r.get("_agency"),
                complaint_type=r.get("_complaint_type"),
            )
        )

    # Placeholder summary; boundary-aware fields filled later.
    summary = SanitySummary(
        rows_total=rows_total,
        rows_with_created=rows_with_created,
        rows_after_agency=rows_after_agency,
        rows_after_topk=rows_after_topk,
        rows_in_created_window=0,
        missing_closed=0,
        negative_lag_dropped=negative_lag_dropped,
        created_min=min(e.created_day for e in events) if events else date.today(),
        created_max=max(e.created_day for e in events) if events else date.today(),
        closed_max=max((e.closed_day for e in events if e.closed_day is not None), default=None),
        tail_days_after_created_end=None,
        median_lag_days=None,
        p90_lag_days=None,
        zero_run_arrivals_inside_window=0,
        zero_run_closures_in_tail=None,
    )

    return events, summary


def compute_sanity(
    *,
    events: list[Event],
    base: SanitySummary,
    created_start: Optional[date],
    created_end: Optional[date],
) -> SanitySummary:
    if not events:
        raise ValueError("No usable rows after parsing/filters.")

    created_min_all = min(e.created_day for e in events)
    created_max_all = max(e.created_day for e in events)
    start = created_start or created_min_all
    end = created_end or created_max_all
    if start > end:
        raise ValueError("created_start must be <= created_end")

    in_window = [e for e in events if start <= e.created_day <= end]
    if not in_window:
        raise ValueError("No events remain inside the created-date window after filtering.")

    missing_closed = sum(1 for e in in_window if e.closed_day is None)
    lags = [float(e.lag_days) for e in in_window if e.lag_days is not None]
    med_lag = float(median(lags)) if lags else None
    p90_lag = float(_p90(lags)) if lags else None

    arrivals: dict[date, int] = {}
    for e in in_window:
        arrivals[e.created_day] = arrivals.get(e.created_day, 0) + 1
    days = _days_range(start, end)
    arrivals_series = [int(arrivals.get(d, 0)) for d in days]
    zero_run_arrivals = _longest_zero_run(arrivals_series)

    closed_max = max((e.closed_day for e in in_window if e.closed_day is not None), default=None)
    tail_days = (closed_max - end).days if (closed_max is not None and created_end is not None) else None

    zero_run_closures_in_tail: Optional[int] = None
    if created_end is not None and closed_max is not None and closed_max > end:
        closures: dict[date, int] = {}
        for e in in_window:
            if e.closed_day is not None:
                closures[e.closed_day] = closures.get(e.closed_day, 0) + 1
        tail_days_list = _days_range(end + timedelta(days=1), closed_max)
        closures_series = [int(closures.get(d, 0)) for d in tail_days_list]
        zero_run_closures_in_tail = _longest_zero_run(closures_series) if closures_series else 0

    return SanitySummary(
        **{
            **base.__dict__,
            "rows_in_created_window": len(in_window),
            "missing_closed": missing_closed,
            "created_min": start,
            "created_max": end,
            "closed_max": closed_max,
            "tail_days_after_created_end": tail_days,
            "median_lag_days": med_lag,
            "p90_lag_days": p90_lag,
            "zero_run_arrivals_inside_window": zero_run_arrivals,
            "zero_run_closures_in_tail": zero_run_closures_in_tail,
        }
    )


def format_report(summary: SanitySummary) -> str:
    lines: list[str] = []
    lines.append("NYC 311 Tier-2.5 boundary sanity check")
    lines.append("")
    lines.append("Counts")
    lines.append(f"- rows_total: {summary.rows_total}")
    lines.append(f"- rows_with_created: {summary.rows_with_created}")
    lines.append(f"- rows_after_agency: {summary.rows_after_agency}")
    lines.append(f"- rows_after_topK: {summary.rows_after_topk}")
    lines.append(f"- rows_in_created_window: {summary.rows_in_created_window}")
    lines.append(f"- missing_closed (in window): {summary.missing_closed}")
    lines.append(f"- negative_lag_dropped: {summary.negative_lag_dropped}")
    lines.append("")
    lines.append("Boundary / dates")
    lines.append(f"- created_min: {summary.created_min.isoformat()}")
    lines.append(f"- created_max: {summary.created_max.isoformat()}")
    lines.append(f"- closed_max (for in-window tickets): {summary.closed_max.isoformat() if summary.closed_max else 'None'}")
    if summary.tail_days_after_created_end is not None:
        lines.append(f"- tail_days_after_created_end: {summary.tail_days_after_created_end}")
    lines.append("")
    lines.append("Lag (in-window tickets with closed_date)")
    lines.append(f"- median_lag_days: {summary.median_lag_days if summary.median_lag_days is not None else 'None'}")
    lines.append(f"- p90_lag_days: {summary.p90_lag_days if summary.p90_lag_days is not None else 'None'}")
    lines.append("")
    lines.append("Zero-run diagnostics (helps avoid over-interpretation)")
    lines.append(
        f"- longest_zero_run(arrivals) within [created_min, created_max]: {summary.zero_run_arrivals_inside_window} days"
    )
    if summary.zero_run_closures_in_tail is not None:
        lines.append(f"- longest_zero_run(closures) in tail after created_end: {summary.zero_run_closures_in_tail} days")
    lines.append("")
    lines.append("Interpretation guardrails")
    lines.append(
        "- If you set a created-date boundary, arrivals after created_end are expected to be zero by construction."
    )
    lines.append(
        "- A large median close-lag late in the series can be a closure tail artifact (old tickets closing late), not necessarily a sudden regime change."
    )
    lines.append(
        "- Use this report to check boundary integrity before drawing any narrative conclusions from rho/backlog plots."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanity-check NYC 311 boundaries (stdlib only).")
    parser.add_argument("--input", type=str, default="", help="Input CSV path (default: data/sample_311.csv)")
    parser.add_argument("--agency", type=str, default="", help="Optional agency filter (exact match)")
    parser.add_argument("--top-k-types", type=int, default=10, help="Top-K complaint types within boundary (0 disables)")
    parser.add_argument("--created-start", type=str, default="", help="Created-date boundary start YYYY-MM-DD")
    parser.add_argument("--created-end", type=str, default="", help="Created-date boundary end YYYY-MM-DD")
    parser.add_argument("--out", type=str, default="", help="Optional output path (writes a .txt report)")
    args = parser.parse_args()

    here = Path(__file__).resolve()
    root = here.parents[1]  # .../nyc_311_tier2p5
    input_csv = Path(args.input).expanduser() if args.input.strip() else (root / "data" / "sample_311.csv")
    input_csv = input_csv.resolve()

    created_start = date.fromisoformat(args.created_start) if args.created_start.strip() else None
    created_end = date.fromisoformat(args.created_end) if args.created_end.strip() else None

    events, base = load_events(
        input_csv=input_csv,
        agency=args.agency.strip() or None,
        top_k_types=int(args.top_k_types),
    )
    summary = compute_sanity(events=events, base=base, created_start=created_start, created_end=created_end)
    report = format_report(summary)
    print(report)

    if args.out.strip():
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

