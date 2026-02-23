# Scheme-Estimator Matrix (v0.1)

| Scheme | Estimator | Label | Best RMSE | Non-sat pairs | Evaluated triples |
|---|---|---|---:|---:|---:|
| majority | C_frozen | SUPPORTED | 0.002395 | 2 | 1 |
| majority | C_activity | SUPPORTED | 0.002395 | 2 | 1 |
| majority | H | SCOPE_LIMITED_SATURATION |  | 0 | 0 |
| threshold_low | C_frozen | SUPPORTED | 0.002821 | 2 | 1 |
| threshold_low | C_activity | SUPPORTED | 0.002821 | 2 | 1 |
| threshold_low | H | SCOPE_LIMITED_SATURATION |  | 1 | 0 |
| threshold_high | C_frozen | SCOPE_LIMITED_SATURATION |  | 1 | 0 |
| threshold_high | C_activity | SCOPE_LIMITED_SATURATION |  | 1 | 0 |
| threshold_high | H | SUPPORTED | 0.004289 | 2 | 1 |
| average | C_frozen | SUPPORTED | 0.002395 | 2 | 1 |
| average | C_activity | SUPPORTED | 0.002395 | 2 | 1 |
| average | H | SCOPE_LIMITED_SATURATION |  | 0 | 0 |

## Notes
- `SUPPORTED`: evaluated non-saturated triples all pass RMSE threshold.
- `SCOPE_LIMITED_SATURATION`: saturation gate blocks interpretation at this configuration.
- `CHALLENGED`: at least one evaluated triple exceeds RMSE threshold.
- `MISSING`: result artifact not found.
