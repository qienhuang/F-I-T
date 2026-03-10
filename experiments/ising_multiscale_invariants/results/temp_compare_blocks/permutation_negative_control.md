# Ising Permutation Negative Control (`1->2->4`, direct vs composed)

Goal: verify that observed closure quality is not reproduced by random direct-map alignment.

| Block | T | Scheme | Estimator | Tested | RMSE(real) | RMSE(perm mean) | p_emp (lower-tail) | Effect sigma | Neg-ctrl pass |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| A | 2.100 | average | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | average | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | average | H_2x2 | yes | 0.02175 | 0.17669 | 0.0050 | 40.325 | True |
| A | 2.100 | majority | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | majority | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | majority | H_2x2 | yes | 0.02175 | 0.17669 | 0.0050 | 40.325 | True |
| A | 2.100 | threshold_high | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | threshold_high | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | threshold_high | H_2x2 | yes | 0.03660 | 0.15073 | 0.0050 | 29.528 | True |
| A | 2.100 | threshold_low | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | threshold_low | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.100 | threshold_low | H_2x2 | yes | 0.01703 | 0.17390 | 0.0050 | 39.848 | True |
| B | 2.100 | average | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | average | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | average | H_2x2 | yes | 0.01982 | 0.15462 | 0.0050 | 37.742 | True |
| B | 2.100 | majority | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | majority | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | majority | H_2x2 | yes | 0.01982 | 0.15462 | 0.0050 | 37.742 | True |
| B | 2.100 | threshold_high | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | threshold_high | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | threshold_high | H_2x2 | yes | 0.03570 | 0.13707 | 0.0050 | 27.563 | True |
| B | 2.100 | threshold_low | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | threshold_low | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.100 | threshold_low | H_2x2 | yes | 0.01918 | 0.14930 | 0.0050 | 35.999 | True |
| A | 2.269 | average | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | average | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | average | H_2x2 | yes | 0.05784 | 0.07883 | 0.0050 | 4.281 | True |
| A | 2.269 | majority | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | majority | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | majority | H_2x2 | yes | 0.05784 | 0.07883 | 0.0050 | 4.281 | True |
| A | 2.269 | threshold_high | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | threshold_high | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | threshold_high | H_2x2 | yes | 0.03228 | 0.11684 | 0.0050 | 16.288 | True |
| A | 2.269 | threshold_low | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | threshold_low | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| A | 2.269 | threshold_low | H_2x2 | yes | 0.02974 | 0.10073 | 0.0050 | 13.092 | True |
| B | 2.269 | average | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | average | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | average | H_2x2 | yes | 0.08737 | 0.03062 | 1.0000 | -18.335 | False |
| B | 2.269 | majority | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | majority | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | majority | H_2x2 | yes | 0.08737 | 0.03062 | 1.0000 | -18.335 | False |
| B | 2.269 | threshold_high | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | threshold_high | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | threshold_high | H_2x2 | yes | 0.03629 | 0.09715 | 0.0050 | 13.819 | True |
| B | 2.269 | threshold_low | C_activity | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | threshold_low | C_frozen | no (saturated_required_scales) | - | - | - | - | - |
| B | 2.269 | threshold_low | H_2x2 | yes | 0.04952 | 0.05093 | 0.3234 | 0.366 | False |

## Aggregate readout

| T | Block | Neg-ctrl pass / tested | pass rate |
|---:|---|---:|---:|
| 2.100 | A | 4/4 | 1.000 |
| 2.100 | B | 4/4 | 1.000 |
| 2.269 | A | 4/4 | 1.000 |
| 2.269 | B | 1/4 | 0.250 |

Notes:
- Lower-tail p-value uses permutation baseline on direct-map training labels (`y` shuffled).
- This is a negative-control audit; it does not replace prereg closure verdicts.
- `C_activity` is derived (`1 - C_frozen`), so independent-evidence emphasis should remain on `C_frozen` and `H_2x2`.
