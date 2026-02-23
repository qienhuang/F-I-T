# Path-4 Report (v0.1, Locked-Data Run)

## Scope

This report summarizes the first full Path-4 pass on a schema-locked multiscale table derived from:

- `experiments/renormalization/gol_rg_lens_v0_1/out/multiscale_scheme_audit.csv`

with long schema:

- `(seed, t, scheme, b, estimator, value)`

## Gates

- Schema gate: `PASS`
- Saturation gate matrix: generated for all `(scheme, estimator, b)` cells
- Semigroup hard-gate: evaluated where saturation allows

## Main Results

- Scale-map fits: `36`
- Scheme × estimator rows: `12`
- Overall labels:
  - `PASS`: `9`
  - `SCOPE_LIMITED_SATURATION`: `3`
  - `ESTIMATOR_UNSTABLE`: `0`

## Interpretation Boundary

- Saturation is treated as a scope limit, not as a positive result.
- In this run, `threshold_high` is consistently saturation-limited.
- Non-saturated configurations provide the actionable evidence for closure and invariant extraction.

## Output Artifacts

- `scale_maps.json`, `scale_maps.csv`
- `fixed_points.json`
- `closure_tests.json`
- `invariant_matrix.csv`
- `fit_summary.json`
- `figures/closure_heatmap.png`
- `figures/scatter_fits/*.png` (36 panels)
