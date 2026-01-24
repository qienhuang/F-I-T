from __future__ import annotations
from pathlib import Path
from typing import Any, List, Optional
import json
import numpy as np

def _extract_pae_matrix(obj: Any) -> Optional[List[List[float]]]:
    # Try common AF/AFDB JSON shapes.
    if isinstance(obj, dict):
        # Fixture support: compact constant-matrix encoding.
        #
        # This is used only for tiny repo-included smoke-test fixtures and is not an AF/AFDB format.
        if "fixture_constant_pae" in obj and isinstance(obj["fixture_constant_pae"], dict):
            spec = obj["fixture_constant_pae"]
            n = int(spec.get("n", 0))
            v = float(spec.get("value", 0.0))
            if n > 0:
                return [[v] * n for _ in range(n)]
        for k in ("predicted_aligned_error", "pae", "PAE"):
            if k in obj:
                return obj[k]
        if "data" in obj:
            return _extract_pae_matrix(obj["data"])
    if isinstance(obj, list):
        if obj and isinstance(obj[0], dict):
            return _extract_pae_matrix(obj[0])
        if obj and isinstance(obj[0], list):
            return obj
    return None

def load_pae_offdiag_median(path: str | Path, band_k: int = 32) -> float:
    # Compute median PAE where |i-j| >= band_k.
    p = Path(path)
    obj = json.loads(p.read_text(encoding="utf-8"))
    mat = _extract_pae_matrix(obj)
    if mat is None:
        raise ValueError(f"Could not extract PAE matrix from {p.name}")

    arr = np.asarray(mat, dtype=float)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError(f"PAE matrix is not square in {p.name}: shape={arr.shape}")

    n = arr.shape[0]
    ii, jj = np.indices((n, n))
    mask = np.abs(ii - jj) >= band_k
    vals = arr[mask]
    if vals.size == 0:
        return float(np.nan)
    return float(np.nanmedian(vals))
