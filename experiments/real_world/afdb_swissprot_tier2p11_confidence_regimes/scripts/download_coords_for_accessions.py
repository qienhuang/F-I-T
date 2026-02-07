#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import time
import requests

AFDB_PREDICTION_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"


def _resolve_cif_url_from_api(acc: str) -> str | None:
    r = requests.get(AFDB_PREDICTION_API.format(acc=acc), timeout=60)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        return None
    item = data[0]
    cif_url = item.get("cifUrl")
    if not isinstance(cif_url, str) or not cif_url:
        return None
    return cif_url


def download(url: str, out_path: Path, sleep_s: float = 0.2) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    time.sleep(sleep_s)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--accessions", required=True, help="path to a file containing UniProt accessions, one per line")
    ap.add_argument("--out_coords_dir", default="data/coords")
    ap.add_argument("--sleep_s", type=float, default=0.2)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    out_coords = Path(args.out_coords_dir)
    accs = [
        a.strip()
        for a in Path(args.accessions).read_text(encoding="utf-8").splitlines()
        if a.strip() and not a.strip().startswith("#")
    ]

    for acc in accs:
        cif_url = None
        try:
            cif_url = _resolve_cif_url_from_api(acc)
        except Exception:
            continue
        if not cif_url:
            continue

        filename = cif_url.split("/")[-1]
        if not filename.lower().endswith(".cif"):
            continue
        out_path = out_coords / filename
        if out_path.exists() and not args.overwrite:
            continue
        try:
            download(cif_url, out_path, sleep_s=args.sleep_s)
        except Exception:
            pass


if __name__ == "__main__":
    main()

