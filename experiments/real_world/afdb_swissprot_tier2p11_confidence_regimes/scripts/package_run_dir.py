#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


DEFAULT_FILES = [
    "EST_PREREG.locked.yaml",
    "boundary_snapshot.json",
    "run_manifest.json",
    "regime_report.md",
    "metrics_per_bin.parquet",
    "tradeoff_onepage.pdf",
    "tradeoff_onepage.png",
    "accessions_selected.txt",
    "accessions_selected.sha256",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    ap.add_argument("--out_zip", required=True)
    ap.add_argument("--include_per_protein", action="store_true", help="include metrics_per_protein.parquet")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    out_zip = Path(args.out_zip)
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    files = list(DEFAULT_FILES)
    if args.include_per_protein:
        files.append("metrics_per_protein.parquet")

    missing = []
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            p = run_dir / rel
            if not p.exists():
                missing.append(rel)
                continue
            zf.write(p, arcname=f"{run_dir.name}/{rel}")

    if missing:
        print(f"Warning: missing files (skipped): {missing}")
    print(f"Wrote: {out_zip}")


if __name__ == "__main__":
    main()

