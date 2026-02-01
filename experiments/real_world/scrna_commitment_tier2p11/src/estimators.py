from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .estimators_core import compute_constraint_estimators
from .prereg import load_prereg, prereg_paths
from .windowing import WindowSpec, build_rolling_quantile_windows


def _build_knn_edges(df: pd.DataFrame, n_neighbors: int) -> pd.DataFrame:
    """
    Build a simple kNN graph in PCA space.

    Note: This is a deterministic fallback. The clean step already computed Scanpy neighbors,
    but to keep artifacts simple (single parquet), we reconstruct an approximate kNN here.
    """
    from sklearn.neighbors import NearestNeighbors

    pc_cols = [c for c in df.columns if c.startswith("pc")]
    X = df[pc_cols].to_numpy(dtype=float)
    nn = NearestNeighbors(n_neighbors=min(n_neighbors + 1, len(df)), algorithm="auto", metric="euclidean")
    nn.fit(X)
    _, idx = nn.kneighbors(X, return_distance=True)
    # Drop self-edge in position 0
    idx = idx[:, 1:]

    src = np.repeat(np.arange(len(df)), idx.shape[1])
    dst = idx.reshape(-1)

    edges = pd.DataFrame(
        {
            "src": src,
            "dst": dst,
            "label_src": df["label"].to_numpy()[src],
            "label_dst": df["label"].to_numpy()[dst],
        }
    )
    return edges


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute windowed constraint estimator family")
    parser.add_argument("--prereg", required=True, help="Preregistration YAML")
    args = parser.parse_args()

    workdir = Path(__file__).resolve().parents[1]
    prereg_path = Path(args.prereg).resolve()
    prereg = load_prereg(prereg_path)
    paths = prereg_paths(prereg, workdir)

    df = pd.read_parquet(paths.processed_cells_parquet)
    if "axis" not in df.columns:
        raise SystemExit("cells.parquet missing axis column")

    boundary = prereg.get("boundary", {})
    n_neighbors = int(boundary.get("n_neighbors", 15))

    windowing_cfg = prereg.get("windowing", {})
    warmup = prereg.get("estimators", {}).get("boundary_warmup_spec", {}) or {}
    spec = WindowSpec(
        scheme=str(windowing_cfg.get("scheme", "rolling_quantile")),
        window_q=float(windowing_cfg.get("window_q", 0.2)),
        stride_q=float(windowing_cfg.get("stride_q", 0.05)),
        min_cells_per_window=int(windowing_cfg.get("min_cells_per_window", 120)),
        exclude_left_q=float(warmup.get("exclude_left_q", 0.0)),
        exclude_right_q=float(warmup.get("exclude_right_q", 0.0)),
    )

    windows = build_rolling_quantile_windows(df, time_col="axis", spec=spec)
    if len(windows) < 3:
        paths.metrics_log_parquet.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([]).to_parquet(paths.metrics_log_parquet, index=False)
        return

    edges = _build_knn_edges(df, n_neighbors=n_neighbors)

    out_rows: list[dict[str, object]] = []
    for w_idx, idx in enumerate(windows):
        w_df = df.iloc[idx.to_numpy()]
        # Edges restricted to the window by endpoint membership.
        in_window = set(idx.to_numpy().tolist())
        w_edges = edges[edges["src"].isin(in_window) & edges["dst"].isin(in_window)]

        est = compute_constraint_estimators(w_df, w_edges)
        out_rows.append(
            {
                "window_id": w_idx,
                "n_cells": int(len(w_df)),
                "t_min": float(w_df["axis"].min()),
                "t_max": float(w_df["axis"].max()),
                "C_dim_collapse": float(est.c_dim_collapse),
                "C_mixing": float(est.c_mixing),
                "C_label_entropy_inv": float(est.c_label_entropy_inv),
                "C_label_purity": float(est.c_label_purity),
                "D_eff": float(est.d_eff),
            }
        )

    out = pd.DataFrame(out_rows)
    paths.metrics_log_parquet.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(paths.metrics_log_parquet, index=False)


if __name__ == "__main__":
    main()
