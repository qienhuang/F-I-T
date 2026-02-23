# Langton Scale-Invariant Extraction Report (Path-4 v0.1 Full Run)

## Objective

Replicate the same scale-consistency gates used in GoL on a second system (Langton's Ant) without changing evaluation semantics.

## Method

- Long-table schema identical to GoL Path-4 package
- Saturation gate: `eps=0.10`, ratio threshold `0.90`
- Fit + closure pipeline:
  - isotonic and polynomial maps
  - fixed-point and slope CI
  - semigroup closure labels

## Key Outcome (latest run)

From `invariant_matrix.csv`:

- `PASS`: 11 / 12 scheme-estimator cells
- `SCOPE_LIMITED_SATURATION`: 1 / 12 (`threshold_high + H_2x2`)

From `saturation_summary.json`:

- Saturated groups: 4 / 48
- Non-saturated groups: 44 / 48

This is consistent with the audit discipline:

- no forced interpretation under saturation
- explicit scope-limited labels
- cross-system comparability retained by identical gates

## Next Recommended Step

Compare GoL vs Langton in a single matrix-level note:

- non-saturated triple count
- closure pass ratio
- estimator-specific saturation profiles

then decide whether to start Ising/percolation with the same pipeline.
