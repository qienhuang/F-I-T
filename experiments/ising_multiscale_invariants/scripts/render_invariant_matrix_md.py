from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_csv", default="results/invariant_matrix.csv")
    ap.add_argument("--output_md", default="results/invariant_matrix.md")
    args = ap.parse_args()

    df = pd.read_csv(args.input_csv)
    lines: list[str] = []
    lines.append("# Invariant Matrix (Path-4 v0.1)")
    lines.append("")
    lines.append("| Scheme | Estimator | Tested Triples | Pass | Scope-Limited | Unstable | Overall |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    for _, r in df.iterrows():
        lines.append(
            f"| {r['scheme']} | {r['estimator']} | {int(r['closure_tested_triples'])} | "
            f"{int(r['closure_pass_triples'])} | {int(r['closure_scope_limited'])} | "
            f"{int(r['closure_unstable'])} | {r['overall_label']} |"
        )

    out = Path(args.output_md)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

