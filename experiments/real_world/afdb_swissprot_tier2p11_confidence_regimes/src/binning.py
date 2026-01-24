from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Bins:
    edges: np.ndarray
    mids: np.ndarray

def make_length_bins(min_len: int, max_len: int, bin_width: int) -> Bins:
    edges = np.arange(min_len, max_len + bin_width, bin_width, dtype=int)
    if edges[-1] < max_len:
        edges = np.append(edges, max_len + bin_width)
    mids = (edges[:-1] + edges[1:]) / 2.0
    return Bins(edges=edges, mids=mids)

def assign_bins(lengths: np.ndarray, bins: Bins) -> np.ndarray:
    idx = np.digitize(lengths, bins.edges, right=False) - 1
    idx = np.where((idx >= 0) & (idx < len(bins.mids)), idx, -1)
    return idx

def aggregate_by_bin(df: pd.DataFrame, bin_col: str, metrics: List[str], min_items_per_bin: int) -> pd.DataFrame:
    rows = []
    for b, sub in df.groupby(bin_col):
        if int(b) < 0:
            continue
        n = len(sub)
        if n < min_items_per_bin:
            continue
        row = {"bin_id": int(b), "bin_n": int(n)}
        for m in metrics:
            row[m] = float(sub[m].median())
        rows.append(row)
    out = pd.DataFrame(rows).sort_values("bin_id").reset_index(drop=True)
    return out
