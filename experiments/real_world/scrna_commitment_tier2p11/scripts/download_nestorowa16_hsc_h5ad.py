from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

import scanpy as sc


URL_H5AD = "https://zenodo.org/records/6110279/files/adata_nestorowa.h5ad?download=1"


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as r, tmp.open("wb") as f:
        shutil.copyfileobj(r, f)
    tmp.replace(dest)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "data" / "raw"
    out_h5ad = raw_dir / "nestorowa16_hsc_2016.h5ad"

    _download(URL_H5AD, out_h5ad)

    # Basic sanity print to help users pick axis/label keys.
    adata = sc.read_h5ad(out_h5ad)
    print(f"Wrote: {out_h5ad}")
    print(f"Shape: {adata.n_obs} cells x {adata.n_vars} genes")
    print("obs columns:", list(adata.obs.columns)[:30])


if __name__ == "__main__":
    main()
