# Ising Two-Temperature Full Compare: Seed-Block Consistency

## Matrix Labels

| Block | T | PASS cells | SCOPE_LIMITED | UNSTABLE | Saturated groups | Non-saturated groups |
|---|---:|---:|---:|---:|---:|---:|
| A | 2.100 | 10 | 0 | 2 | 8 | 40 |
| B | 2.100 | 10 | 0 | 2 | 8 | 40 |
| A | 2.269 | 2 | 8 | 2 | 24 | 24 |
| B | 2.269 | 2 | 8 | 2 | 24 | 24 |

## Required Triple `1->2->4`

| Block | T | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.02175 |
| B | 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.01982 |
| A | 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.04506 |
| B | 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.06845 |

## Readout

- Compare within each block (`2.10` vs `2.269`) for regime effect.
- Compare across blocks (A vs B) for seed-block sensitivity under fixed gates.
- Keep claims bounded to fixed gate semantics; do not pool blocks without preregistering pooled criteria.