# Eval report — PAE Proxy Alarm (v0.1)

- run_id: `MAIN`
- parent_case_id: `afdb_swissprot_tier2p11_confidence_regimes`
- tau_pae: `0.8`
- prereg_sha256: `e9a08c54c0ad73ec2f6dc43c59e4ae551afe0d8e022594c98532cfe1bc010b45`
- input_metrics_sha256: `ed1c5549410b076897ac3a4d89fd9dcf6a7e74cbcb93c3088cb1f3a3e27c9cf9`

## Global metrics (test)

- ROC-AUC: `1.0`
- PR-AUC: `1.0`

## Operating points (monitorability gate)

| target FPR cap | threshold (val-selected) | achieved FPR (test) | TPR/coverage (test) | precision (test) | flagged per 10k | missed per 10k | usable |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 0.0100 | 0.965309 | 0.000000 | 1.000000 | 1.000000 | 163.93 | 0.00 | OK |
| 0.0500 | 0.914423 | 0.016667 | 1.000000 | 0.500000 | 327.87 | 0.00 | OK |

## Coefficients (logistic regression; proxy correlations)

| feature | coef |
|---|---:|
| length | 1.918339 |
| C1_low_conf_frac | 1.347610 |
| I2_mean_plddt | -0.732124 |
| I1_hi_conf_frac | 0.141755 |
| I3_plddt_entropy | 0.026967 |

## Interpretation rule

- This is a proxy alarm case. Only claims allowed are about **alarm usability at low FPR** under the locked boundary.
- If an operating point is UNUSABLE (TPR=0 at target FPR), treat that as a negative result for that operating point.
