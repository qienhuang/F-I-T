# Li² Scaling Law Verification Report

Generated: 2026-01-07T04:01:05

## Summary
- M values tested: [23, 41, 59]
- Ratio range: 0.42 to 0.60

## Critical Ratios (50% Grokking Probability)
| M | Critical Ratio | Critical n (≈ ratio·M²) | M·log(M) | c_implied (= n / (M log M)) |
|---|----------------|------------------------|----------|-----------------------------|
| 23 | 0.5700 | 301.5 | 72.1 | 4.18 |
| 41 | 0.4900 | 823.7 | 152.3 | 5.41 |
| 59 | 0.4500 | 1566.5 | 240.6 | 6.51 |

## Scaling Law Fit
- Fitted constant c: 6.075 ± 0.481
- R^2 score (n-space): 0.9506

Fitted model: `n = c * M * log(M)` (Li2 Thm 4 form)

## Conclusion
OK: Strong support for Li2 scaling law (R^2 > 0.9 in n-space).