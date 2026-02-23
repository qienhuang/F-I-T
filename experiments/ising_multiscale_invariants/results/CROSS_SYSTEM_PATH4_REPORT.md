# Path-4 Cross-System Report (GoL / Langton / Ising)

## Scope And Definitions

- `testable` means triples not excluded by saturation gate (`PASS + ESTIMATOR_UNSTABLE`).
- Gate constants are fixed across systems (`eps=0.10`, `saturation_ratio_threshold=0.90`, closure `tau=0.05`).
- `C_activity` is treated as implementation-consistency (`1 - C_frozen`), not as an independent estimator family.

## Table 1: Matrix Labels

| System | Cells | PASS | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |
|---|---:|---:|---:|---:|---:|---:|
| GoL | 12 | 9 | 3 | 0 | 15 | 33 |
| Langton | 12 | 11 | 1 | 0 | 4 | 44 |
| Ising | 12 | 1 | 8 | 3 | 24 | 24 |

## Table 2: Required Triple `1->2->4`

| System | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |
|---|---:|---:|---:|---:|---:|---:|
| GoL | 9 | 3 | 0 | 9 | 1.000 | 0.00289 |
| Langton | 11 | 1 | 0 | 11 | 1.000 | 0.00177 |
| Ising | 1 | 8 | 3 | 4 | 0.250 | 0.07555 |

## Table 3: Optional Triple `2->4->8`

| System | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |
|---|---:|---:|---:|---:|---:|---:|
| GoL | 0 | 12 | 0 | 0 | n/a | n/a |
| Langton | 9 | 3 | 0 | 9 | 1.000 | 0.00326 |
| Ising | 4 | 8 | 0 | 4 | 1.000 | 0.01626 |

## Interpretation

- Langton is currently the strongest cross-system positive case (high PASS, low saturation).
- Ising under current boundary is regime-sensitive: high saturation and reduced required-triple stability.
- The gate stack is functioning as intended: no forced claims under saturation; instability is surfaced explicitly.