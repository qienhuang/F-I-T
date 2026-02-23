# Ising Scale-Invariant Extraction Report (Path-4 v0.1 Full Run)

## Objective

Apply the same scale-consistency gates (used for GoL and Langton) to 2D Ising dynamics, without changing semantics.

## Method

- Long-table schema identical to other Path-4 packages
- Saturation gate: `eps=0.10`, ratio threshold `0.90`
- Fit + closure pipeline:
  - isotonic and polynomial scale maps
  - fixed-point and slope bootstrap
  - semigroup closure labels (`PASS`, `SCOPE_LIMITED_SATURATION`, `ESTIMATOR_UNSTABLE`)

## Key Outcome

From `invariant_matrix.csv`:

- `PASS`: `1 / 12` (`threshold_high + H_2x2`)
- `SCOPE_LIMITED_SATURATION`: `8 / 12`
- `ESTIMATOR_UNSTABLE`: `3 / 12`

From `saturation_summary.json`:

- Saturated groups: `24 / 48`
- Non-saturated groups: `24 / 48`

## Closure Detail (H_2x2)

- `average`: `1->2->4` unstable (RMSE `0.0985`), `2->4->8` pass (RMSE `0.0191`)
- `majority`: `1->2->4` unstable (RMSE `0.0985`), `2->4->8` pass (RMSE `0.0191`)
- `threshold_low`: `1->2->4` unstable (RMSE `0.0526`), `2->4->8` pass (RMSE `0.0124`)
- `threshold_high`: both triples pass (`0.0362`, `0.0134`)

## Interpretation Discipline

- The gate is behaving as intended: no forced claims when channels saturate.
- Under the current Ising setup (`T=2.269`), C-family channels are mostly saturated at finer scales.
- `H_2x2` carries most of the testable signal; closure is scheme-sensitive for the required triple (`1->2->4`).

## Immediate Follow-up

If needed, increase non-saturated coverage before stronger claims:

1. Lower saturation pressure via alternative temperature points (e.g., `T=2.1`, `T=2.4`).
2. Keep the same gates and compare only matrix-level labels across temperatures.
3. Promote to cross-system note only after `1->2->4` stabilizes in at least two schemes.
