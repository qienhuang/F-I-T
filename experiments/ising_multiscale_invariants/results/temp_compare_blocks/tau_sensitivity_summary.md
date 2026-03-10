# Ising Required-Triple Tau Sensitivity (Block A/B)

This audit recomputes pass rates for the required triple (`1->2->4`) using fixed non-skipped RMSE values under alternative closure thresholds.

| Block | T | tau | Testable | PASS under tau | PASS rate | Median RMSE |
|---|---:|---:|---:|---:|---:|---:|
| A | 2.100 | 0.02 | 4 | 1 | 0.250 | 0.02175 |
| A | 2.100 | 0.05 | 4 | 4 | 1.000 | 0.02175 |
| A | 2.100 | 0.08 | 4 | 4 | 1.000 | 0.02175 |
| B | 2.100 | 0.02 | 4 | 3 | 0.750 | 0.01982 |
| B | 2.100 | 0.05 | 4 | 4 | 1.000 | 0.01982 |
| B | 2.100 | 0.08 | 4 | 4 | 1.000 | 0.01982 |
| A | 2.269 | 0.02 | 4 | 0 | 0.000 | 0.04506 |
| A | 2.269 | 0.05 | 4 | 2 | 0.500 | 0.04506 |
| A | 2.269 | 0.08 | 4 | 4 | 1.000 | 0.04506 |
| B | 2.269 | 0.02 | 4 | 0 | 0.000 | 0.06845 |
| B | 2.269 | 0.05 | 4 | 2 | 0.500 | 0.06845 |
| B | 2.269 | 0.08 | 4 | 2 | 0.500 | 0.06845 |

Readout:
- This is a threshold-sensitivity audit, not a new prereg verdict replacement.
- If `T=2.10` remains consistently above `T=2.269` across tau values, regime-conditioned separation is robust to reasonable tau perturbations.
