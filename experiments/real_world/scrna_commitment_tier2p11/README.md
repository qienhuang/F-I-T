# scRNA Commitment (Tier-2 / P11-style, EST-gated)

This experiment is a **repo-runnable** Tier-2 case for single-cell data.

Goal: demonstrate an **auditable** workflow that can return:

- a phase-conditional interpretation (`OK_PER_WINDOW`), or
- an explicit non-interpretability verdict (`ESTIMATOR_UNSTABLE`, `SCOPE_LIMITED`, `INCONCLUSIVE`)

without drifting into expression-first narrative.

## Current results (auditable)

See `RESULTS.md` for the current run portfolio and the corresponding evidence bundles under `outputs_runs/`.

## Quick start

This case uses a small built-in Scanpy dataset by default (`paul15`), so you can run it without downloading data.

```bash
python run_pipeline.py --prereg EST_PREREG.yaml
```

Outputs are written into `outputs/` by default (see below).

## A more "commitment-like" builtin option (still no downloads)

The `scanpy:paul15` dataset is a hematopoiesis differentiation dataset and ships with a dataset-provided label:

- `adata.obs["paul15_clusters"]`

You can use it as the mixing label (more fate-like than Leiden) via:

```bash
python run_pipeline.py --prereg EST_PREREG_paul15_commitment.yaml
```

## Using a more "fate commitment" dataset (recommended)

To make the case more representative of fate commitment, use a dataset that includes:

- a **fate / cell type** label in `adata.obs` (for the mixing proxy), and
- ideally a **timepoint / stage** column in `adata.obs` (so windowing is not purely inferred).

Place your dataset as an `.h5ad` file, for example:

- `data/raw/hematopoiesis_commitment.h5ad`

Then edit `EST_PREREG.yaml`:

- set `boundary.dataset` to `file:data/raw/hematopoiesis_commitment.h5ad`
- set `boundary.mixing_label_key` to `obs:<your_fate_label_key>`
- optionally set `windowing.axis` to `obs:<your_time_key>` (otherwise keep `pseudotime`)

Example:

```yaml
boundary:
  dataset: "file:data/raw/hematopoiesis_commitment.h5ad"
  mixing_label_key: "obs:cell_type"

windowing:
  axis: "obs:day"
```

## Phase A (minimal): pick a coherent estimator pair

This case supports a small Phase A: try 2-3 estimator pairs, then lock one for any external writeup.

Two repo-ready, real-data preregs you can run as-is (both use `C_dim_collapse` vs `C_label_purity`):

- `EST_PREREG_endocrinogenesis_day15_purity.yaml` (Pancreas endocrine differentiation; window axis = pseudotime)
- `EST_PREREG_gastrulation_e75_purity.yaml` (Mouse gastrulation E6.5-E8.5; window axis = `obs:stage`)
- `EST_PREREG_moignard15_exporder_leidenfixed_purity.yaml` (Moignard15; explicit stage surrogate axis from `exp_groups`)
- `EST_PREREG_nestorowa16_zenodo_purity.yaml` (Nestorowa16 hematopoiesis; Zenodo `.h5ad`; explicit axis from dataset PCA)
- `EST_PREREG_dentategyrus_age_purity.yaml` (Dentate gyrus; explicit but coarse axis from `obs:age(days)`)

Each prereg writes artifacts to `outputs_runs/<run_id>/...` so runs do not overwrite each other.

### Input space (`boundary.input_space`)

By default the pipeline assumes **count-like inputs** and applies `normalize_total` + `log1p` during cleaning. For datasets already in a log/normalized space (or small panel datasets), set:

- `boundary.input_space: log`
- `boundary.min_counts: 0`

This prevents double-normalization and avoids NaN failures in PCA.

### Moignard15 explicit stage surrogate (optional)

Moignard15 does not ship an explicit timepoint column. For a small "explicit axis" variant we preregister an ordinal mapping over `obs:exp_groups` and store it as `obs:exp_order`. We also store a deterministic clustering label as `obs:leiden_fixed`.

```bash
python scripts/prepare_moignard15_exporder_h5ad.py
python run_pipeline.py --prereg EST_PREREG_moignard15_exporder_leidenfixed_purity.yaml
```

### Nestorowa16 (Zenodo `.h5ad`; explicit axis from dataset PCA)

Download the dataset file (once):

```bash
python scripts/download_nestorowa16_hsc_h5ad.py
```

Then run the prereg:

```bash
python run_pipeline.py --prereg EST_PREREG_nestorowa16_zenodo_purity.yaml
```

## Packaging an evidence bundle (ZIP)

After you have:

- a sanity run (`scanpy:paul15`), and
- a main run (your `.h5ad`),

you can package both into a single zip for citation/supplementary materials:

```bash
# Sanity-only
python package_evidence.py --sanity_dir outputs

# Sanity + main (example: main outputs kept under outputs_main/)
python package_evidence.py --sanity_dir outputs --main_dir outputs_main
```

## What this pipeline does

1. **Clean / preprocess**
   - load a dataset (default: `scanpy:paul15`)
   - compute PCA + kNN graph
   - compute a pseudotime-like ordering (Diffusion Pseudotime) when `windowing.axis: pseudotime`
   - write a per-cell table (`data/processed/cells.parquet`)

2. **Estimators**
   - window cells along the preregistered axis (`windowing.axis`)
   - compute a small **constraint estimator family** per window:
     - `C_dim_collapse`: inverse effective dimension (PCA variance participation ratio)
     - `C_mixing`: inverse label mixing in the kNN graph (labels from `boundary.mixing_label_key`)
     - `C_label_entropy_inv`: inverse normalized label entropy (higher = less mixed composition)
     - `C_label_purity`: max label mass (higher = more single-label composition)
     - `D_eff`: effective dimension (participation ratio; inverse of `C_dim_collapse`)
   - write a windowed metrics log (`outputs/metrics_log.parquet`)

3. **Coherence gate + verdict**
   - compute windowed Spearman correlations between the constraint estimators
   - apply the preregistered coherence gate
   - write a coherence report (`outputs/coherence_report.json`) and a human-readable verdict (`outputs/regime_report.md`)

4. **Plots**
   - write a one-page PNG/PDF summary (`outputs/tradeoff_onepage.*`)

## Reproducibility artifacts

This run produces the minimal artifacts needed for audit:

- `outputs/PREREG.locked.yaml` (copy of prereg used for the run)
- `outputs/metrics_log.parquet` (per-window estimator values)
- `outputs/coherence_report.json` (per-window coherence results + pass/fail)
- `outputs/fail_windows.md` (which windows failed and why)
- `outputs/regime_report.md` (verdict with failure semantics)
- `outputs/tradeoff_onepage.png` and `outputs/tradeoff_onepage.pdf`

## Install

```bash
python -m pip install -r requirements.txt
```

If you already have `scanpy` installed elsewhere, that is fine; this case only depends on its core pipeline.

## Notes on interpretation

- A **pooled** correlation is never sufficient for interpretation.
- Windowing is treated as a **diagnostic**, not a "rescue patch".
- If the estimator family is not coherent under the prereg boundary, the correct outcome is a failure label, not a narrative.
