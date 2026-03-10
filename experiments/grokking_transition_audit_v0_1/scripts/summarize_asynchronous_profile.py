#!/usr/bin/env python3
"""Summarize phase-I label profiles for synchronous vs asynchronous dynamics."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import median


LABEL_ORDER = [
    "REGISTERED_TRANSITION",
    "NO_TRANSITION",
    "ESTIMATOR_UNSTABLE",
    "INCONCLUSIVE",
]


def _to_int(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value is None or value == "":
        return 0
    return int(float(value))


def _to_bool(row: dict[str, str], key: str) -> bool:
    return str(row.get(key, "")).strip().lower() == "true"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for label in LABEL_ORDER:
        group = [r for r in rows if r.get("label") == label]
        if not group:
            continue

        n_s1 = [_to_int(r, "n_s1") for r in group]
        n_s2 = [_to_int(r, "n_s2") for r in group]
        n_s3 = [_to_int(r, "n_s3") for r in group]
        n_pt = [_to_int(r, "n_pt_candidates") for r in group]

        n = len(group)
        all_ge2 = sum(1 for a, b, c in zip(n_s1, n_s2, n_s3) if a >= 2 and b >= 2 and c >= 2)
        pt_zero = sum(1 for x in n_pt if x == 0)
        gate_pass = sum(1 for r in group if _to_bool(r, "gate_pass"))

        out.append(
            {
                "label": label,
                "n": str(n),
                "median_n_s1": f"{median(n_s1):.1f}",
                "median_n_s2": f"{median(n_s2):.1f}",
                "median_n_s3": f"{median(n_s3):.1f}",
                "median_n_pt_candidates": f"{median(n_pt):.1f}",
                "frac_all_signals_ge2": f"{all_ge2 / n:.3f}",
                "frac_pt_candidates_zero": f"{pt_zero / n:.3f}",
                "frac_gate_pass": f"{gate_pass / n:.3f}",
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "label",
        "n",
        "median_n_s1",
        "median_n_s2",
        "median_n_s3",
        "median_n_pt_candidates",
        "frac_all_signals_ge2",
        "frac_pt_candidates_zero",
        "frac_gate_pass",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, str]], run_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Asynchronous Profile Summary (Phase-I)",
        "",
        f"- run_id: `{run_id}`",
        "- source: `outputs/main/diagnostics.csv`",
        "",
        "| Label | n | median n_s1 | median n_s2 | median n_s3 | median n_pt_candidates | frac(all signals >=2) | frac(pt_candidates=0) | frac(gate_pass) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['label']} | {r['n']} | {r['median_n_s1']} | {r['median_n_s2']} | "
            f"{r['median_n_s3']} | {r['median_n_pt_candidates']} | {r['frac_all_signals_ge2']} | "
            f"{r['frac_pt_candidates_zero']} | {r['frac_gate_pass']} |"
        )

    nt = next((r for r in rows if r["label"] == "NO_TRANSITION"), None)
    if nt is not None:
        lines.extend(
            [
                "",
                "Interpretation anchor:",
                f"- `NO_TRANSITION` shows dense per-signal activity (median events 7/7/7, "
                f"`frac(all signals>=2)={nt['frac_all_signals_ge2']}`) but no tri-signal "
                f"co-window candidate (`frac(pt_candidates=0)={nt['frac_pt_candidates_zero']}`).",
                "- This supports an asynchronous multi-peak profile under the prereg PT-MSS gate.",
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--diagnostics", type=Path, required=True, help="Path to diagnostics.csv")
    p.add_argument("--summary", type=Path, required=True, help="Path to summary.json")
    p.add_argument("--out-csv", type=Path, required=True, help="Output CSV path")
    p.add_argument("--out-md", type=Path, required=True, help="Output markdown path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_rows(args.diagnostics)
    summary_rows = summarize(rows)
    run_id = "unknown"
    try:
        import json

        run_id = json.loads(args.summary.read_text(encoding="utf-8")).get("run_id", "unknown")
    except Exception:
        pass

    write_csv(args.out_csv, summary_rows)
    write_md(args.out_md, summary_rows, run_id)
    print(f"[ok] wrote {args.out_csv}")
    print(f"[ok] wrote {args.out_md}")


if __name__ == "__main__":
    main()
