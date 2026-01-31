"""
Export rolling-window coherence failures into a small, repo-safe Markdown index.

This is a deterministic post-processor over `coherence_report.json`.
It exists to make "windowing is diagnostic" auditable without re-reading plots.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WindowRow:
    name: str
    start: str
    end: str
    status: str
    rho: float | None
    passed: bool | None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_rho(win: dict[str, Any]) -> tuple[float | None, bool | None]:
    pairs = win.get("pairs") or []
    if not pairs:
        return None, None
    pr = pairs[0]
    rho = pr.get("rho")
    passed = pr.get("passed")
    return (float(rho) if rho is not None else None), (bool(passed) if passed is not None else None)


def _as_rows(window_results: list[dict[str, Any]]) -> list[WindowRow]:
    rows: list[WindowRow] = []
    for w in window_results:
        rho, passed = _extract_rho(w)
        rows.append(
            WindowRow(
                name=str(w.get("name", "")),
                start=str(w.get("start", "")),
                end=str(w.get("end", "")),
                status=str(w.get("status", "")),
                rho=rho,
                passed=passed,
            )
        )
    return rows


def _fmt_rho(rho: float | None) -> str:
    if rho is None:
        return "-"
    return f"{rho:.3f}"


def _write_md(out_path: Path, coherence: dict[str, Any]) -> None:
    windowing = coherence.get("windowing") or {}
    wtype = str(windowing.get("type") or "")
    pooled_status = str(windowing.get("pooled_status") or coherence.get("status") or "")

    pooled_pair = (coherence.get("pairs") or [{}])[0] if coherence.get("pairs") else {}
    pooled_rho = pooled_pair.get("rho")
    pooled_rho_s = _fmt_rho(float(pooled_rho)) if pooled_rho is not None else "-"

    lines: list[str] = []
    lines.append("# Rolling-window coherence: FAIL window index")
    lines.append("")
    lines.append("This file is generated from `coherence_report.json`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Windowing type: `{wtype}`")
    lines.append(f"- Pooled status: `{pooled_status}`")
    lines.append(f"- Pooled rho: `{pooled_rho_s}`")
    lines.append("")

    results = windowing.get("results") or []
    if not isinstance(results, list) or not results:
        lines.append("No window results present.")
        lines.append("")
        out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return

    rows = _as_rows(results)
    n_total = len(rows)
    n_pass = sum(1 for r in rows if r.status == "OK")
    n_fail = sum(1 for r in rows if r.status != "OK")

    lines.append("## Counts")
    lines.append("")
    lines.append(f"- Windows total: `{n_total}`")
    lines.append(f"- Windows PASS: `{n_pass}`")
    lines.append(f"- Windows FAIL: `{n_fail}`")
    lines.append("")

    failing = [r for r in rows if r.status != "OK"]
    if not failing:
        lines.append("## FAIL windows")
        lines.append("")
        lines.append("None.")
        lines.append("")
        out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return

    lines.append("## FAIL windows")
    lines.append("")
    lines.append("| Window | Start | End | Status | rho |")
    lines.append("|---|---|---|---|---|")
    for r in failing:
        lines.append(f"| `{r.name}` | `{r.start}` | `{r.end}` | `{r.status}` | `{_fmt_rho(r.rho)}` |")
    lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export FAIL window index from coherence_report.json")
    parser.add_argument("--coherence", default="outputs/coherence_report.json", help="Path to coherence_report.json")
    parser.add_argument("--output", default="outputs/fail_windows.md", help="Output Markdown path")
    args = parser.parse_args()

    coherence_path = Path(args.coherence)
    out_path = Path(args.output)

    coherence = _load_json(coherence_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _write_md(out_path, coherence)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

