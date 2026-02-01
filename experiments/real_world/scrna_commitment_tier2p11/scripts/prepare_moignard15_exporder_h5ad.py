from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc


def main() -> None:
    out_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "moignard15_exporder_leiden_fixed.h5ad"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    adata = sc.datasets.moignard15()

    exp_groups = adata.obs.get("exp_groups", None)
    if exp_groups is None:
        raise SystemExit("moignard15 dataset missing obs['exp_groups']")

    # Preregistered ordinal mapping (explicit-time surrogate).
    # This is intentionally written into the exported h5ad so that downstream
    # runs can use `windowing.axis: obs:exp_order` without relying on implicit
    # string sorting.
    order = ["NP", "PS", "4SG", "4SFG", "HF"]
    mapping = {k: i for i, k in enumerate(order)}
    missing = sorted(set(exp_groups.astype(str).unique()) - set(mapping))
    if missing:
        raise SystemExit(f"Unexpected exp_groups values: {missing}")

    adata.obs["exp_order"] = exp_groups.astype(str).map(mapping).astype(np.float64)
    adata.obs["exp_groups"] = pd.Categorical(exp_groups.astype(str), categories=order, ordered=True)

    # Create a deterministic label for mixing/purity proxies.
    # We store it as a stable obs column and use it as `boundary.mixing_label_key`.
    #
    # Note: moignard15 is a small panel dataset and may not be raw-count space.
    # Avoid applying normalize/log1p blindly (can introduce NaNs if values are non-positive).
    if hasattr(adata.X, "toarray"):
        X = adata.X.toarray()
    else:
        X = np.asarray(adata.X)
    X = np.asarray(X, dtype=np.float64)
    adata.X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    sc.pp.scale(adata, max_value=10)
    sc.tl.pca(adata, n_comps=15, svd_solver="arpack")
    sc.pp.neighbors(adata, n_neighbors=15, n_pcs=15)
    sc.tl.leiden(adata, resolution=1.0, flavor="igraph", n_iterations=2, directed=False, random_state=0)
    adata.obs["leiden_fixed"] = adata.obs["leiden"].astype(str)

    adata.write_h5ad(out_path)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
