#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import heapq
import time
from pathlib import Path
from typing import Iterable

import requests

UNIPROT_SEARCH = "https://rest.uniprot.org/uniprotkb/search"
AFDB_PREDICTION_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def stable_key(acc: str, seed_string: str) -> str:
    return sha256_hex(seed_string + "::" + acc)


def iter_uniprot_accessions(query: str, page_size: int = 500) -> Iterable[str]:
    # UniProt REST pagination via Link: <...>; rel="next"
    params = {
        "query": query,
        "format": "tsv",
        "fields": "accession",
        "size": str(page_size),
    }
    url = UNIPROT_SEARCH
    seen_header = False

    while True:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        text = r.text.splitlines()
        for line in text:
            if not line.strip():
                continue
            if not seen_header:
                # first non-empty line is header "Entry"
                seen_header = True
                continue
            yield line.strip()

        link = r.headers.get("Link")
        next_url = None
        if isinstance(link, str):
            for part in link.split(","):
                part = part.strip()
                if 'rel="next"' in part:
                    # <URL>; rel="next"
                    if part.startswith("<") and ">;" in part:
                        next_url = part[1 : part.index(">;")]
                        break

        if not next_url:
            break

        url = next_url
        params = None  # cursor URL already includes parameters


def pick_smallest_by_hash(items: Iterable[str], seed_string: str, n: int) -> list[str]:
    # Keep the n smallest keys.
    heap: list[tuple[str, str]] = []
    for acc in items:
        k = stable_key(acc, seed_string)
        if len(heap) < n:
            heapq.heappush(heap, (k, acc))
        else:
            if k < heap[0][0]:
                heapq.heapreplace(heap, (k, acc))
    return [acc for _, acc in sorted(heap)]


def _resolve_afdb_urls(acc: str) -> tuple[str | None, str | None]:
    r = requests.get(AFDB_PREDICTION_API.format(acc=acc), timeout=60)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or not data:
        return None, None
    item = data[0]
    cif_url = item.get("cifUrl")
    pae_url = item.get("paeDocUrl")
    if not isinstance(cif_url, str) or not cif_url:
        cif_url = None
    if not isinstance(pae_url, str) or not pae_url:
        pae_url = None
    return cif_url, pae_url


def _download(url: str, out_path: Path, timeout_s: int, sleep_s: float) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=timeout_s)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    time.sleep(sleep_s)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_name", required=True, help="data/runs/<run_name>/...")
    ap.add_argument("--query", required=True, help="UniProt query string")
    ap.add_argument("--seed_string", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--sleep_s", type=float, default=0.2)
    ap.add_argument("--timeout_s", type=int, default=120)
    ap.add_argument("--page_size", type=int, default=500)
    args = ap.parse_args()

    case_dir = Path(__file__).resolve().parents[1]
    run_dir = case_dir / "data" / "runs" / args.run_name
    coords_dir = run_dir / "coords"
    pae_dir = run_dir / "pae"
    run_dir.mkdir(parents=True, exist_ok=True)

    all_acc = iter_uniprot_accessions(args.query, page_size=args.page_size)
    selected = pick_smallest_by_hash(all_acc, seed_string=args.seed_string, n=args.n)

    accessions_path = run_dir / "accessions_input.txt"
    accessions_path.write_text("\n".join(selected) + "\n", encoding="utf-8")

    missing_api = 0
    missing_cif = 0
    missing_pae = 0

    for acc in selected:
        try:
            cif_url, pae_url = _resolve_afdb_urls(acc)
        except Exception:
            missing_api += 1
            continue

        if cif_url:
            filename = cif_url.split("/")[-1]
            if filename.lower().endswith(".cif"):
                out_cif = coords_dir / filename
                if not out_cif.exists():
                    try:
                        _download(cif_url, out_cif, timeout_s=args.timeout_s, sleep_s=args.sleep_s)
                    except Exception:
                        missing_cif += 1
        else:
            missing_cif += 1

        if pae_url:
            out_pae = pae_dir / f"{acc}.json"
            if not out_pae.exists():
                try:
                    _download(pae_url, out_pae, timeout_s=args.timeout_s, sleep_s=args.sleep_s)
                except Exception:
                    missing_pae += 1
        else:
            missing_pae += 1

    summary = [
        "# Staging summary\n",
        f"- run_name: `{args.run_name}`\n",
        f"- query: `{args.query}`\n",
        f"- seed_string: `{args.seed_string}`\n",
        f"- target_n: `{args.n}`\n",
        f"- missing_api: `{missing_api}`\n",
        f"- missing_cif: `{missing_cif}`\n",
        f"- missing_pae: `{missing_pae}`\n",
    ]
    (run_dir / "STAGING_SUMMARY.md").write_text("".join(summary), encoding="utf-8")

    print(f"Staging complete: {run_dir}")


if __name__ == "__main__":
    main()

