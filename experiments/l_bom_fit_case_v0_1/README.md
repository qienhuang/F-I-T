# L-BOM (Bicontinuous Multiscale Inverse Design) — FIT Case Utilities (v0.1)

This folder is a small, **dataset-local** utility for the Case 05 write-up:

- `docs/cases/CASE_05_Data_Driven_Inverse_Design_Bicontinuous_Multiscale.md`

It does **not** include the dataset. You point the script at your local copy.

## What this produces (why it helps FIT readers)

- A concrete boundary object (what files are assumed; what dimensions exist).
- A minimal estimator lens over the static “phase catalog” (coverage / nearest-to-target / density).
- A basic sanity check that the voxel files are consistent with the last scalar in the property vector (correlation).

This is intentionally “hard” and auditable, not a new theory.

## Run

```bash
python analyze_l_bom_dataset.py --dataset_dir "<path-to-your-local-dataset-dir>"
```

Outputs:

- `out/report.md`
- `out/summary.json`

## Expected dataset layout

`--dataset_dir` should contain:

- `count.json` (raw 4D property vectors per sample id)
- `ncount.json` (normalized vectors + `min`/`max` for raw normalization)
- `countT.json` (often a column-wise transpose: `C1..C4` arrays, not necessarily target vectors)
- `img.zip` (voxel files under `img/<id>voxel`)

## Notes

- Voxel payload size suggests `32^3` bytes per sample.
- Target vectors (if present) are typically stored as 4-vectors in `ncount.json` (e.g. `C4`), and the script will auto-detect them.
- The four raw scalars are likely the three independent elastic constants under cubic symmetry + a porosity/volume-fraction-like scalar, but this script treats them as unnamed `d0..d3` to avoid over-claiming.
