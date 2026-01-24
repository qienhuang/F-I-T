#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import time
import requests

AFDB_ENTRY_URL = "https://alphafold.ebi.ac.uk/entry/{acc}"

def download(url: str, out_path: Path, sleep_s: float = 0.2) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    time.sleep(sleep_s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--accessions", required=True, help="path to accessions_selected.txt")
    ap.add_argument("--out_pae_dir", default="data/pae")
    ap.add_argument("--out_msa_dir", default="data/msa")
    ap.add_argument("--sleep_s", type=float, default=0.2)
    args = ap.parse_args()

    accs = [a.strip() for a in Path(args.accessions).read_text(encoding="utf-8").splitlines() if a.strip()]

    out_pae = Path(args.out_pae_dir)
    out_msa = Path(args.out_msa_dir)

    # NOTE: AFDB provides download links on the entry page; this script uses common file endpoints.
    # If endpoints change, treat it as a boundary change; update the script and rerun under new prereg.

    for acc in accs:
        # These endpoints may change; validate against AFDB entry page.
        pae_url = f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-predicted_aligned_error_v4.json"
        msa_url = f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-a3m_v4.a3m"

        pae_path = out_pae / f"{acc}.json"
        msa_path = out_msa / f"{acc}.a3m"

        if not pae_path.exists():
            try:
                download(pae_url, pae_path, sleep_s=args.sleep_s)
            except Exception:
                # leave missing; run pipeline will count missing artifacts
                pass

        if not msa_path.exists():
            try:
                download(msa_url, msa_path, sleep_s=args.sleep_s)
            except Exception:
                pass

if __name__ == "__main__":
    main()
