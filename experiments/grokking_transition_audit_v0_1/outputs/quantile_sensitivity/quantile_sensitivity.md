# Signal-Quantile Sensitivity (Phase-I PT-MSS)

- base_prereg: `D:/FIT Lab/github/F-I-T/experiments/grokking_transition_audit_v0_1/EST_PREREG.v0_1.yaml`
- quantiles: `[0.98, 0.99, 0.995]` (shared across F/I/C)
- replay gate: disabled for this sensitivity sweep (label-logic only)

| quantile | n_valid | REGISTERED | NO_TRANSITION | ESTIMATOR_UNSTABLE | INCONCLUSIVE | fit_transition_rate | divergence_rate | verdict |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0.980 | 0 | 0 | 0 | 0 | 40 | 0.0000 | 0.0000 | SCOPE_LIMITED_GROKKING_TRANSITION_DETECTION |
| 0.990 | 40 | 2 | 35 | 3 | 0 | 0.0500 | 0.9500 | SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY |
| 0.995 | 40 | 2 | 38 | 0 | 0 | 0.0500 | 0.9500 | SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY |

Interpretation:
- Quantile(s) 0.980 are `SCOPE_LIMITED` here: density gate invalidated all seeds (`n_valid=0`).
- Across non-scope-limited quantiles, verdict remains stable but class composition shifts (notably `UNSTABLE` vs `NO_TRANSITION`).
- Read this as a gate-conditioned robustness profile, not a universal quantile-independence claim.
