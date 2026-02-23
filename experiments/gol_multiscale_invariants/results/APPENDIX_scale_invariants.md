# Appendix: Scale-Invariant Signatures (Path-4 v0.1)

## Setup

- System: Conway's Game of Life (reused locked multiscale dataset)
- Scales: `b in {1,2,4,8}`
- Schemes: `majority`, `threshold_low`, `threshold_high`, `average`
- Estimators: `C_frozen`, `C_activity`, `H_2x2`
- Split: seed-level hold-out (`train=70%`, `test=30%`)
- Saturation gate: `eps=0.10`, ratio threshold `>=0.90`

## Gates and Labels

- `PASS`: closure testable and closure RMSE below threshold (`tau=0.05`)
- `SCOPE_LIMITED_SATURATION`: closure blocked by saturation gate
- `ESTIMATOR_UNSTABLE`: testable but closure fails threshold or inconsistent behavior

## Core Outputs

- Scale-map metrics: `scale_maps.json`
- Fixed points and slope CI: `fixed_points.json`
- Closure decisions: `closure_tests.json`
- Matrix summary: `invariant_matrix.csv`, `invariant_matrix.md`

## Result Snapshot

From `invariant_matrix.csv`:

- 12 scheme-estimator cells total
- 9 `PASS`
- 3 `SCOPE_LIMITED_SATURATION`
- 0 `ESTIMATOR_UNSTABLE`

Pattern:

- `majority`, `threshold_low`, `average`: at least one testable closure triple (`1->2->4`) passes.
- `threshold_high`: saturation gate blocks closure claims across estimators.

## Figures

- Closure heatmap: `figures/closure_heatmap.png`
- Scatter+fit panels: `figures/scatter_fits/*.png` (36 panels)

## Interpretation Discipline

- Saturation cells are not interpreted as success.
- Claims are bounded to non-saturated testable regions.
- Complementary estimator (`C_activity = 1 - C_frozen`) is treated as consistency channel, not independent evidence.

