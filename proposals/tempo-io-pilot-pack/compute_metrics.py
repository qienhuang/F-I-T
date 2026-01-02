from __future__ import annotations

import csv
import datetime as dt
import os
import statistics
from dataclasses import dataclass
from typing import Iterable


def _parse_ts(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return dt.datetime.fromisoformat(value)


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return float("nan")
    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return d0 + d1


@dataclass(frozen=True)
class Change:
    change_id: str
    effective_ts: dt.datetime
    closure_ts: dt.datetime | None
    is_io: bool
    io_category: str
    bypass: bool


@dataclass(frozen=True)
class Drill:
    drill_id: str
    change_id: str
    date_utc: str
    rto_minutes: int
    rpo_minutes: int
    success: bool


def _read_changes(path: str) -> list[Change]:
    items: list[Change] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            effective_ts = _parse_ts(row.get("effective_ts_utc"))
            if effective_ts is None:
                raise ValueError(f"Missing effective_ts_utc for change_id={row.get('change_id')}")
            items.append(
                Change(
                    change_id=(row.get("change_id") or "").strip(),
                    effective_ts=effective_ts,
                    closure_ts=_parse_ts(row.get("closure_ts_utc")),
                    is_io=(row.get("is_io") or "0").strip() == "1",
                    io_category=(row.get("io_category") or "").strip(),
                    bypass=(row.get("bypass") or "0").strip() == "1",
                )
            )
    return items


def _read_drills(path: str) -> list[Drill]:
    items: list[Drill] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(
                Drill(
                    drill_id=(row.get("drill_id") or "").strip(),
                    change_id=(row.get("change_id") or "").strip(),
                    date_utc=(row.get("date_utc") or "").strip(),
                    rto_minutes=int((row.get("rto_minutes") or "0").strip()),
                    rpo_minutes=int((row.get("rpo_minutes") or "0").strip()),
                    success=(row.get("success") or "0").strip() == "1",
                )
            )
    return items


def _vl_hours(changes: Iterable[Change]) -> list[float]:
    vls: list[float] = []
    for c in changes:
        if c.closure_ts is None:
            continue
        delta = c.closure_ts - c.effective_ts
        vls.append(delta.total_seconds() / 3600.0)
    return vls


def main() -> None:
    here = os.path.dirname(__file__)
    changes_path = os.path.join(here, "changes.example.csv")
    drills_path = os.path.join(here, "rollback_drills.example.csv")

    changes = _read_changes(changes_path)
    drills = _read_drills(drills_path)

    io_changes = [c for c in changes if c.is_io]
    io_relevant_changes = [c for c in changes if c.is_io]

    vl_all = sorted(_vl_hours(changes))
    vl_io = sorted(_vl_hours(io_changes))

    bypass_events = sum(1 for c in io_relevant_changes if c.bypass)
    gbr = (bypass_events / len(io_relevant_changes)) if io_relevant_changes else float("nan")

    rdpr = (sum(1 for d in drills if d.success) / len(drills)) if drills else float("nan")

    def _fmt(x: float) -> str:
        if x != x:
            return "n/a"
        return f"{x:.2f}"

    print("=== Tempo & IO Pilot Metrics (example) ===")
    print(f"Changes total: {len(changes)}")
    print(f"IO-relevant changes: {len(io_relevant_changes)}")
    print(f"Bypass events (IO): {bypass_events}")
    print(f"GBR: {_fmt(gbr * 100)}%")
    print("")
    print(f"Drills: {len(drills)}")
    print(f"RDPR: {_fmt(rdpr * 100)}%")
    print("")

    if vl_all:
        print("Validation Lag (VL) — all changes (hours)")
        print(f"  median: {_fmt(statistics.median(vl_all))}")
        print(f"  p90:    {_fmt(_percentile(vl_all, 90))}")
        print(f"  p99:    {_fmt(_percentile(vl_all, 99))}")
        print("")

    if vl_io:
        print("Validation Lag (VL) — IO changes only (hours)")
        print(f"  median: {_fmt(statistics.median(vl_io))}")
        print(f"  p90:    {_fmt(_percentile(vl_io, 90))}")
        print(f"  p99:    {_fmt(_percentile(vl_io, 99))}")
        print("")

    missing_closure = sum(1 for c in changes if c.is_io and c.closure_ts is None)
    if missing_closure:
        print(f"IO changes missing closure timestamp: {missing_closure} (treat as red flag)")


if __name__ == "__main__":
    main()

