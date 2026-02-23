#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import itertools
import re
from pathlib import Path

import pandas as pd

STATUS_RE = re.compile(r"- status: \*\*(?P<status>[^*]+)\*\*")
N_RE = re.compile(r"- selected_n: `(?P<n>\d+)`")
BIN_RE = re.compile(
    r"- (?P<k>C_primary|C1_low_conf_frac|C2_pae_offdiag|C3_msa_deficit): `(?P<v>[^`]+)`"
)

CHANNELS = ["C_primary", "C1_low_conf_frac", "C2_pae_offdiag", "C3_msa_deficit"]


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
    }

    m = STATUS_RE.search(text)
    if m:
        row["status"] = m.group("status").strip()

    m = N_RE.search(text)
    if m:
        row["selected_n"] = m.group("n")

    for bm in BIN_RE.finditer(text):
        row[bm.group("k")] = bm.group("v").strip()

    return row


def sign_relation(v: float) -> str:
    if pd.isna(v):
        return "na"
    if v > 0:
        return "same-sign"
    if v < 0:
        return "opposite-sign"
    return "neutral"


def compare_one_run(run_id: str) -> list[dict]:
    out_dir = Path("out") / run_id
    report = parse_regime_report(out_dir / "regime_report.md")
    df = pd.read_parquet(out_dir / "metrics_per_bin.parquet")

    rows: list[dict] = []
    for a, b in itertools.combinations(CHANNELS, 2):
        rho = df[a].corr(df[b], method="spearman")
        try:
            event_a = int(report[a])
            event_b = int(report[b])
            event_offset = abs(event_a - event_b)
        except Exception:
            event_a = None
            event_b = None
            event_offset = None

        rows.append(
            {
                "run_id": run_id,
                "status": report["status"],
                "selected_n": report["selected_n"],
                "channel_a": a,
                "channel_b": b,
                "rho_signed": f"{float(rho):.6f}",
                "rho_abs": f"{abs(float(rho)):.6f}",
                "sign_relation": sign_relation(float(rho)),
                "event_a": "" if event_a is None else str(event_a),
                "event_b": "" if event_b is None else str(event_b),
                "event_offset_abs": "" if event_offset is None else str(event_offset),
            }
        )

    return rows


def render_markdown(rows: list[dict], title: str) -> str:
    lines: list[str] = [f"# {title}\n"]

    lines.append("## Pairwise sign-aware audit (per run)\n")
    lines.append(
        "| Run | Pair | rho_signed | |rho| | Sign relation | Event bins | |offset| | Status |"
    )
    lines.append("|---|---|---:|---:|---|---|---:|---|")
    for r in rows:
        pair = f"{r['channel_a']} vs {r['channel_b']}"
        bins = (
            f"{r['event_a']} vs {r['event_b']}"
            if r["event_a"] and r["event_b"]
            else "-"
        )
        lines.append(
            f"| {r['run_id']} | {pair} | {float(r['rho_signed']):.3f} | {float(r['rho_abs']):.3f} | "
            f"{r['sign_relation']} | {bins} | {r['event_offset_abs'] or '-'} | {r['status']} |"
        )

    key_rows = [
        r
        for r in rows
        if (r["channel_a"], r["channel_b"]) == ("C2_pae_offdiag", "C3_msa_deficit")
    ]
    if key_rows:
        offsets = [int(r["event_offset_abs"]) for r in key_rows if r["event_offset_abs"]]
        rhos = [float(r["rho_signed"]) for r in key_rows]
        key_rows_n1000 = []
        for r in key_rows:
            try:
                if int(r["selected_n"]) >= 900:
                    key_rows_n1000.append(r)
            except Exception:
                pass
        offsets_n1000 = [int(r["event_offset_abs"]) for r in key_rows_n1000 if r["event_offset_abs"]]
        lines.append("\n## Key pair summary: C2_pae_offdiag vs C3_msa_deficit\n")
        lines.append(
            f"- rho_signed range: `{min(rhos):.3f} .. {max(rhos):.3f}` (all {'negative' if max(rhos) < 0 else 'mixed'})"
        )
        lines.append(
            f"- |rho| range: `{min(abs(x) for x in rhos):.3f} .. {max(abs(x) for x in rhos):.3f}`"
        )
        lines.append(f"- event offsets: `{offsets}`")
        if offsets:
            stable = len(set(offsets)) == 1
            lines.append(f"- stable nonzero offset: **{'yes' if stable and offsets[0] != 0 else 'no'}**")
        if offsets_n1000:
            stable_n1000 = len(set(offsets_n1000)) == 1 and offsets_n1000[0] != 0
            lines.append(
                f"- stable nonzero offset (N~1000 + splits): **{'yes' if stable_n1000 else 'no'}**, offsets=`{offsets_n1000}`"
            )
        lines.append(
            "- interpretation: persistent opposite-sign correlation with stable nonzero event-bin offset supports structural channel mismatch under B2."
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Sign-aware B2 channel comparison from existing run artifacts")
    ap.add_argument(
        "--runs",
        nargs="+",
        required=True,
        help="Run IDs under out/, e.g. B2_taxon9606_N1000 B2_taxon9606_N1000_split_a",
    )
    ap.add_argument("--out_csv", default="out/B2_sign_aware.csv")
    ap.add_argument("--out_md", default="out/B2_sign_aware.md")
    args = ap.parse_args()

    rows: list[dict] = []
    for run_id in args.runs:
        out_dir = Path("out") / run_id
        if not out_dir.exists():
            raise FileNotFoundError(f"Missing run directory: {out_dir}")
        rows.extend(compare_one_run(run_id))

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "run_id",
                "status",
                "selected_n",
                "channel_a",
                "channel_b",
                "rho_signed",
                "rho_abs",
                "sign_relation",
                "event_a",
                "event_b",
                "event_offset_abs",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(rows, "AFDB B2 Sign-Aware Audit Summary"), encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
