"""
Export a compact FAIL-window index from coherence_report.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export FAIL window index")
    parser.add_argument("--coherence", default="outputs/coherence_report.json", help="Path to coherence_report.json")
    parser.add_argument("--output", default="outputs/fail_windows.md", help="Output markdown")
    args = parser.parse_args()

    coh = json.loads(Path(args.coherence).read_text(encoding="utf-8"))
    win = coh.get("windowing", {})
    results = win.get("results", []) if isinstance(win, dict) else []

    lines = []
    lines.append("# FAIL windows (auto-export)")
    lines.append("")
    lines.append("This file is generated from `coherence_report.json`.")
    lines.append("")

    fails = [w for w in results if w.get("status") == "FAIL"]
    if not fails:
        lines.append("No FAIL windows recorded.")
    else:
        lines.append("| id | start | end | status |")
        lines.append("|---|---|---|---|")
        for w in fails:
            lines.append(f"| {w.get('id','?')} | {w.get('start','?')} | {w.get('end','?')} | {w.get('status','?')} |")

    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
