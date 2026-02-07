#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import time
import requests

AFDB_PREDICTION_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"

def download(url: str, out_path: Path, sleep_s: float = 0.2) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    time.sleep(sleep_s)

def _resolve_urls_from_api(acc: str) -> tuple[str | None, str | None]:
    r = requests.get(AFDB_PREDICTION_API.format(acc=acc), timeout=60)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        return None, None
    item = data[0]
    pae_url = item.get("paeDocUrl")
    msa_url = item.get("msaUrl")
    if not isinstance(pae_url, str):
        pae_url = None
    if not isinstance(msa_url, str):
        msa_url = None
    return pae_url, msa_url

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

    for acc in accs:
        pae_url, msa_url = _resolve_urls_from_api(acc)

        pae_path = out_pae / f"{acc}.json"
        msa_path = out_msa / f"{acc}.a3m"

        if not pae_path.exists():
            try:
                if pae_url:
                    download(pae_url, pae_path, sleep_s=args.sleep_s)
            except Exception:
                # leave missing; run pipeline will count missing artifacts
                pass

        if not msa_path.exists():
            try:
                if msa_url:
                    download(msa_url, msa_path, sleep_s=args.sleep_s)
            except Exception:
                pass

if __name__ == "__main__":
    main()
