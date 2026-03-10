# Ising Temperature Sweep Summary (Pilot)

## Matrix Labels

| T | PASS cells | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |
|---:|---:|---:|---:|---:|---:|
| 2.100 | 8 | 0 | 4 | 0 | 48 |
| 2.269 | 4 | 8 | 0 | 22 | 26 |
| 2.400 | 4 | 8 | 0 | 32 | 16 |

## Required Triple `1->2->4`

| T | PASS | SCOPE_LIMITED | UNSTABLE | Testable (PASS+UNSTABLE) | PASS rate (testable) | Median RMSE (testable) |
|---:|---:|---:|---:|---:|---:|---:|
| 2.100 | 8 | 0 | 4 | 12 | 0.667 | 0.03005 |
| 2.269 | 4 | 8 | 0 | 4 | 1.000 | 0.02663 |
| 2.400 | 4 | 8 | 0 | 4 | 1.000 | 0.00742 |

Notes:
- Same gate thresholds are used across temperatures (`eps=0.10`, `saturation_ratio_threshold=0.90`, closure `tau=0.05`).
- `testable` means triples not excluded by saturation gate (PASS + ESTIMATOR_UNSTABLE).
- Pilot boundary diagnosis only; use full block-A/B compare for publish claims.