# Ising Full Two-Temperature Compare (Same Seeds)

Run script:

- `scripts/run_temperature_compare_full.ps1`

Run settings:

- temperatures: `2.10`, `2.269`
- seeds: `6` (same seed block, `15000..15005`)
- steps: `4000`
- burn-in: `500`
- measure interval: `20`
- window: `40`

## Matrix-level labels

| T | PASS cells | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |
|---:|---:|---:|---:|---:|---:|
| 2.100 | 10 | 0 | 2 | 8 | 40 |
| 2.269 | 2 | 8 | 2 | 24 | 24 |

## Required triple `1->2->4`

| T | PASS | SCOPE_LIMITED | UNSTABLE | Testable (PASS+UNSTABLE) | PASS rate (testable) | Median RMSE (testable) |
|---:|---:|---:|---:|---:|---:|---:|
| 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.02175 |
| 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.04506 |

Definition:

- `testable` = triples not excluded by saturation gate (`PASS + ESTIMATOR_UNSTABLE`).

UNSTABLE cells by temperature:

- `T=2.10`: `threshold_high + C_activity`, `threshold_high + C_frozen` (both unstable on `2->4->8`, RMSE `~0.0542`).
- `T=2.269`: `average + H_2x2`, `majority + H_2x2` (both unstable on `1->2->4`, RMSE `~0.0578`).

Interpretation:

- Under identical gates and seed budget, lowering temperature from `2.269` to `2.10` materially improves testable closure quality and reduces saturation pressure.
- The result supports a regime-conditional reading for Ising within Path-4.

Seed-scope note:

- This is a paired fixed-seed comparison (`15000..15005`).
- Independent block-B (`17000..17005`) and A/B comparison are now available at:
  - `results/temp_compare_full_block_b/temperature_compare_full_block_b_summary.md`
  - `results/temp_compare_blocks/temperature_compare_blocks_summary.md`
- `C_activity` is treated as an implementation-consistency channel (`1 - C_frozen`), not independent evidence.
