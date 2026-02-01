from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .prereg import load_prereg, prereg_paths, write_locked_prereg


def _load_scanpy_dataset(name: str):
    import scanpy as sc

    if name == "paul15":
        return sc.datasets.paul15()
    if name == "moignard15":
        return sc.datasets.moignard15()
    raise SystemExit(f"Unsupported scanpy dataset: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load + preprocess scRNA dataset into a per-cell table")
    parser.add_argument("--prereg", required=True, help="Preregistration YAML")
    args = parser.parse_args()

    workdir = Path(__file__).resolve().parents[1]
    prereg_path = Path(args.prereg).resolve()
    prereg = load_prereg(prereg_path)
    paths = prereg_paths(prereg, workdir)

    boundary = prereg.get("boundary", {})
    dataset = str(boundary.get("dataset", "scanpy:paul15"))

    n_hvg = int(boundary.get("n_hvg", 2000))
    n_pcs = int(boundary.get("n_pcs", 30))
    n_neighbors = int(boundary.get("n_neighbors", 15))
    leiden_resolution = float(boundary.get("leiden_resolution", 1.0))
    mixing_label_key = str(boundary.get("mixing_label_key", "leiden"))
    min_counts = int(boundary.get("min_counts", 1))
    hvg_flavor = str(boundary.get("hvg_flavor", "seurat"))
    input_space = str(boundary.get("input_space", "counts")).lower().strip()
    use_precomputed_pca = bool(boundary.get("use_precomputed_pca", False))

    windowing_cfg = prereg.get("windowing", {}) or {}
    axis_spec = str(windowing_cfg.get("axis", "pseudotime"))

    if dataset.startswith("scanpy:"):
        ds_name = dataset.split(":", 1)[1].strip()
        adata = _load_scanpy_dataset(ds_name)
    elif dataset.startswith("file:") or dataset.endswith(".h5ad"):
        import scanpy as sc

        raw = dataset.split("file:", 1)[1] if dataset.startswith("file:") else dataset
        raw = raw.strip()
        p = Path(raw)
        if not p.is_absolute():
            p = (workdir / raw).resolve()
        if not p.exists():
            raise SystemExit(f"h5ad not found: {p}")
        adata = sc.read_h5ad(str(p))
    else:
        raise SystemExit("Only scanpy:* datasets are supported in v0.1 (use scanpy:paul15).")

    import scanpy as sc

    if input_space == "counts":
        if min_counts > 0:
            sc.pp.filter_cells(adata, min_counts=min_counts)
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
    elif input_space == "log":
        # Dataset is assumed to already be in a log / normalized space.
        # Do not apply normalize_total/log1p again (can introduce NaNs if values are non-positive).
        pass
    else:
        raise SystemExit(f"Unsupported boundary.input_space: {input_space} (expected 'counts' or 'log')")

    # Ensure numerical stability for downstream PCA / kNN.
    if hasattr(adata.X, "toarray"):
        X = adata.X.toarray()
    else:
        X = np.asarray(adata.X)
    adata.X = np.nan_to_num(np.asarray(X, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)

    # Highly variable genes (HVG) selection:
    # - For low-dimensional panels (few genes), skip HVG and keep all genes.
    # - For typical scRNA, use a stable flavor ("seurat") unless the prereg overrides it.
    if hvg_flavor.lower() == "none" or n_hvg >= adata.n_vars or adata.n_vars < 200:
        pass
    else:
        sc.pp.highly_variable_genes(
            adata,
            n_top_genes=min(n_hvg, adata.n_vars),
            flavor=hvg_flavor,
            subset=True,
        )

    if use_precomputed_pca:
        if "X_pca" not in adata.obsm:
            raise SystemExit("boundary.use_precomputed_pca=true but adata.obsm['X_pca'] is missing")
        # Ensure downstream steps do not assume we recomputed PCA.
        if "pca" not in adata.uns:
            adata.uns["pca"] = {}
        n_pcs_eff = int(min(n_pcs, adata.obsm["X_pca"].shape[1]))
    else:
        sc.pp.scale(adata, max_value=10)
        sc.tl.pca(adata, n_comps=n_pcs, svd_solver="arpack")
        n_pcs_eff = int(min(n_pcs, adata.obsm["X_pca"].shape[1]))

    sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs_eff)
    # Use igraph backend when available (faster; also avoids leidenalg dependency issues).
    sc.tl.leiden(adata, resolution=leiden_resolution, flavor="igraph", n_iterations=2, directed=False)
    sc.tl.diffmap(adata)

    # Only compute DPT if we need pseudotime as the window axis.
    if axis_spec == "pseudotime":
        root_cell = int(np.argmin(adata.obsm["X_pca"][:, 0]))
        adata.uns["iroot"] = root_cell
        sc.tl.dpt(adata, n_dcs=10)

    # Create per-cell table.
    X_pca = adata.obsm["X_pca"]
    obs = adata.obs.copy()
    obs["cell_id"] = np.arange(adata.n_obs)
    obs["cluster"] = obs["leiden"].astype(str)

    # Window axis (numeric):
    if axis_spec == "pseudotime":
        axis = obs["dpt_pseudotime"].astype(float)
    elif axis_spec.startswith("obs:"):
        k = axis_spec.split("obs:", 1)[1].strip()
        if k not in obs.columns:
            raise SystemExit(f"windowing.axis refers to missing obs key: {k}")
        v = obs[k]
        # pandas categorical dtypes can break np.issubdtype; rely on pandas' dtype helpers instead.
        if pd.api.types.is_numeric_dtype(v):
            axis = v.astype(float)
        else:
            # Deterministic ordinal encoding for non-numeric / categorical timepoints.
            cats = sorted(pd.unique(v.astype(str)))
            mapping = {c: i for i, c in enumerate(cats)}
            axis = v.astype(str).map(mapping).astype(float)
    elif axis_spec.startswith("obsm:"):
        # Explicit axis from a precomputed embedding stored in the dataset.
        # Format: obsm:<key>:<col_index>
        rest = axis_spec.split("obsm:", 1)[1].strip()
        parts = [p for p in rest.split(":") if p != ""]
        if len(parts) != 2:
            raise SystemExit(f"Unsupported obsm axis spec (expected obsm:<key>:<col>): {axis_spec}")
        key, col_s = parts
        if key not in adata.obsm:
            raise SystemExit(f"windowing.axis refers to missing obsm key: {key}")
        try:
            col = int(col_s)
        except ValueError as e:
            raise SystemExit(f"Invalid obsm col index in axis spec: {axis_spec}") from e
        X = np.asarray(adata.obsm[key])
        if X.ndim != 2 or col < 0 or col >= X.shape[1]:
            raise SystemExit(f"obsm axis col out of range: {axis_spec} (shape={X.shape})")
        axis = pd.Series(X[:, col]).astype(float)
    else:
        raise SystemExit(f"Unsupported windowing.axis: {axis_spec}")

    # Mixing label:
    if mixing_label_key == "leiden":
        label = obs["cluster"].astype(str)
    elif mixing_label_key.startswith("obs:"):
        k = mixing_label_key.split("obs:", 1)[1].strip()
        if k not in obs.columns:
            raise SystemExit(f"boundary.mixing_label_key refers to missing obs key: {k}")
        label = obs[k].astype(str)
    else:
        raise SystemExit(f"Unsupported mixing_label_key: {mixing_label_key}")

    df = pd.DataFrame(
        {
            "cell_id": obs["cell_id"].to_numpy(),
            "label": label.to_numpy(),
            "axis": axis.to_numpy(),
            "axis_spec": axis_spec,
            "mixing_label_key": mixing_label_key,
        }
    )
    for i in range(X_pca.shape[1]):
        df[f"pc{i+1:02d}"] = X_pca[:, i]

    # Store PCA explained variance as a constant row field (duplicated per cell for simplicity/audit).
    pca_var = adata.uns.get("pca", {}).get("variance", None)
    if pca_var is None:
        pca_var = np.var(X_pca, axis=0)
    pca_var = np.asarray(pca_var, dtype=float)[: X_pca.shape[1]]
    # Avoid repeated frame.insert (fragmentation warning); attach all PCA variance columns in one concat.
    pca_var_cols = {f"pca_var_{i+1:02d}": float(v) for i, v in enumerate(pca_var)}
    df = pd.concat([df, pd.DataFrame([pca_var_cols] * df.shape[0])], axis=1)

    paths.processed_cells_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(paths.processed_cells_parquet, index=False)

    # Copy prereg for audit.
    write_locked_prereg(prereg_path, paths.prereg_locked_yaml)


if __name__ == "__main__":
    main()
