#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

STATUS_RE = re.compile(r"- status: \*\*(?P<status>[^*]+)\*\*")
BIN_RE = re.compile(r"- (?P<k>C_primary|C1_low_conf_frac|C2_pae_offdiag|C3_msa_deficit): `(?P<v>[^`]+)`")
N_RE = re.compile(r"- selected_n: `(?P<n>\d+)`")


def parse_regime_report(report_path: Path) -> dict:
    text = report_path.read_text(encoding="utf-8", errors="replace")
    row = {
        "run_id": report_path.parent.name,
        "status": "UNKNOWN",
        "selected_n": "",
        "C_primary": "",
        "C1_low_conf_frac": "",
        "C2_pae_offdiag": "",
        "C3_msa_deficit": "",
        "offset_C3_minus_C2": "",
    }

    m = STATUS_RE.search(text)
    if m:
        row["status"] = m.group("status").strip()

    m = N_RE.search(text)
    if m:
        row["selected_n"] = m.group("n")

    for bm in BIN_RE.finditer(text):
        row[bm.group("k")] = bm.group("v").strip()

    try:
        c3 = int(row["C3_msa_deficit"])
        c2 = int(row["C2_pae_offdiag"])
        row["offset_C3_minus_C2"] = str(c3 - c2)
    except Exception:
        row["offset_C3_minus_C2"] = ""

    return row


def render_markdown(rows: list[dict], title: str) -> str:
    lines: list[str] = []
    lines.append(f"# {title}\n")
    lines.append("| Run | Status | N | C_primary | C1 | C2 | C3 | C3-C2 offset |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        lines.append(
            f"| {r['run_id']} | {r['status']} | {r['selected_n'] or '-'} | "
            f"{r['C_primary'] or '-'} | {r['C1_low_conf_frac'] or '-'} | "
            f"{r['C2_pae_offdiag'] or '-'} | {r['C3_msa_deficit'] or '-'} | "
            f"{r['offset_C3_minus_C2'] or '-'} |"
        )

    offsets = [int(r["offset_C3_minus_C2"]) for r in rows if str(r["offset_C3_minus_C2"]).strip() not in {"", "-"}]
    if offsets:
        stable = len(set(offsets)) == 1
        lines.append("\n## Split-stability summary")
        lines.append(f"- offsets: `{offsets}`")
        lines.append(f"- stable offset across runs: **{'yes' if stable else 'no'}**")
        if stable:
            lines.append("- interpretation: persistent channel disagreement suggests structural mismatch, not sampling noise.")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize B2 split-stability from regime_report.md files")
    ap.add_argument("--runs", nargs="+", required=True, help="Run directories under out/, e.g. B2_taxon9606_N1000_split_a")
    ap.add_argument("--out_csv", default="out/B2_split_stability.csv")
    ap.add_argument("--out_md", default="out/B2_split_stability.md")
    args = ap.parse_args()

    rows: list[dict] = []
    for run_id in args.runs:
        report = Path("out") / run_id / "regime_report.md"
        if not report.exists():
            raise FileNotFoundError(f"Missing report: {report}")
        rows.append(parse_regime_report(report))

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "run_id",
                "status",
                "selected_n",
                "C_primary",
                "C1_low_conf_frac",
                "C2_pae_offdiag",
                "C3_msa_deficit",
                "offset_C3_minus_C2",
            ],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(rows, "AFDB B2 Split-Stability Summary"), encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
