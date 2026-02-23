# Ising Two-Temperature Full Compare Summary

## Matrix Labels

| T | PASS cells | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |
|---:|---:|---:|---:|---:|---:|
| 2.100 | 10 | 0 | 2 | 8 | 40 |
| 2.269 | 2 | 8 | 2 | 24 | 24 |

## Required Triple `1->2->4`

| T | PASS | SCOPE_LIMITED | UNSTABLE | Testable (PASS+UNSTABLE) | PASS rate (testable) | Median RMSE (testable) |
|---:|---:|---:|---:|---:|---:|---:|
| 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.02175 |
| 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.04506 |

Notes:
- Same gate thresholds are used across temperatures (`eps=0.10`, `saturation_ratio_threshold=0.90`, closure `tau=0.05`).
- `testable` means triples not excluded by saturation gate (PASS + ESTIMATOR_UNSTABLE).
- This is a paired full-compare audit on a fixed seed block 15000..15005, not yet a cross-block pooled claim.