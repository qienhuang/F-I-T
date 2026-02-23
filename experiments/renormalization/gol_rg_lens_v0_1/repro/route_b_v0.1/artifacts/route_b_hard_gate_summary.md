# Route B Hard-Gate Summary (Semigroup Closure)

- Verdict: **SUPPORTED_WITH_SCOPE_LIMITS**
- Rationale: No challenged cells; semigroup closure holds on evaluated non-saturated cells.

## Decision Table

| N | N_eval | N_sat | rmse_th | near_bound_th | sat_frac_gate | min_non_sat_pairs |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 7 | 5 | 0.050 | 0.100 | 0.900 | 2 |

- Counts: supported=7, scope_limited_saturation=5, challenged=0, missing=0

## Matrix

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

## Decision Rule (v0.1)

- Any `CHALLENGED` cell => `NONCLOSURE_OR_CHALLENGED`.
- No `CHALLENGED` and >=1 `SUPPORTED` cell => `SUPPORTED` (or `SUPPORTED_WITH_SCOPE_LIMITS` if saturation exists).
- Otherwise => `INCONCLUSIVE`.

