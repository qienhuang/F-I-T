# Langton Path-4 Full-Run Summary (v0.1)

## Run (latest)

- Script: `scripts/run_full_langton_path4.ps1`
- Seeds: `6` (start `7000`)
- Steps: `12000`
- Burn-in: `800`
- Measure interval: `20`

## Gates

- Schema validation: `PASS`
- Saturation matrix generated for all `(scheme, estimator, b)` cells

From `saturation_summary.json` (latest):

- Groups total: `48`
- Saturated groups: `4`
- Non-saturated groups: `44`

## Invariant Matrix Snapshot (latest)

From `invariant_matrix.csv`:

- `PASS`: `11/12` cells
- `SCOPE_LIMITED_SATURATION`: `1/12` cell (`threshold_high + H_2x2`)

Cross-system signal:

- Closure is broadly testable in Langton under the same gate regime.
- Saturation remains scheme/estimator-dependent (localized to strict scheme + H-channel at coarse scales).

## Artifacts

- `data/MANIFEST.json`
- `results/schema_validation.json`
- `results/saturation_matrix.csv`
- `results/scale_maps.json`
- `results/fixed_points.json`
- `results/closure_tests.json`
- `results/invariant_matrix.csv`
- `results/invariant_matrix.md`
- `results/figures/closure_heatmap.png`
- `results/figures/scatter_fits/*.png` (36 panels)
