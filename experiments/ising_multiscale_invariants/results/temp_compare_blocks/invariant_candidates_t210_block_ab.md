# Ising T=2.10 Invariant Candidates: Block A vs Block B

Independent estimators only (`C_frozen`, `H_2x2`). `C_activity` is excluded because it is deterministically derived (`1 - C_frozen`).

## Candidate Table (isotonic bootstrap)

| Block | Scheme | Estimator | Pair | Saturation | x* mean [CI] | |slope| mean [CI] | Slope label |
|---|---|---|---|---|---|---|---|
| A | average | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7013 [1.3462, 2.8632] | unstable |
| B | average | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7295 [1.3234, 3.0989] | unstable |
| A | average | H_2x2 | 1->2 | TESTABLE | 0.1357 [0.0788, 0.2627] | 0.0000 [0.0000, 0.0000] | stable |
| B | average | H_2x2 | 1->2 | TESTABLE | 0.1767 [0.0993, 0.2525] | 0.0009 [0.0000, 0.0000] | stable |
| A | majority | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7013 [1.3462, 2.8632] | unstable |
| B | majority | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7295 [1.3234, 3.0989] | unstable |
| A | majority | H_2x2 | 1->2 | TESTABLE | 0.1357 [0.0788, 0.2627] | 0.0000 [0.0000, 0.0000] | stable |
| B | majority | H_2x2 | 1->2 | TESTABLE | 0.1767 [0.0993, 0.2525] | 0.0009 [0.0000, 0.0000] | stable |
| A | threshold_high | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 5.5663 [4.1640, 5.7912] | unstable |
| B | threshold_high | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 5.5777 [4.5923, 6.0637] | unstable |
| A | threshold_high | H_2x2 | 1->2 | TESTABLE | 0.1193 [0.0790, 0.2371] | 0.0000 [0.0000, 0.0000] | stable |
| B | threshold_high | H_2x2 | 1->2 | TESTABLE | 0.1004 [0.0846, 0.2406] | 0.0000 [0.0000, 0.0000] | stable |
| A | threshold_low | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7013 [1.3462, 2.8632] | unstable |
| B | threshold_low | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7295 [1.3234, 3.0989] | unstable |
| A | threshold_low | H_2x2 | 1->2 | TESTABLE | 0.1357 [0.0788, 0.2627] | 0.0000 [0.0000, 0.0000] | stable |
| B | threshold_low | H_2x2 | 1->2 | TESTABLE | 0.1767 [0.0993, 0.2525] | 0.0009 [0.0000, 0.0000] | stable |
| A | average | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 5.5745 [3.9222, 6.1475] | unstable |
| B | average | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 6.6081 [5.0901, 7.0822] | unstable |
| A | average | H_2x2 | 2->4 | TESTABLE | 0.0374 [0.0349, 0.0598] | 0.0000 [0.0000, 0.0000] | stable |
| B | average | H_2x2 | 2->4 | TESTABLE | 0.0334 [0.0257, 0.0528] | 0.0000 [0.0000, 0.0000] | stable |
| A | majority | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 5.5745 [3.9222, 6.1475] | unstable |
| B | majority | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 6.6081 [5.0901, 7.0822] | unstable |
| A | majority | H_2x2 | 2->4 | TESTABLE | 0.0374 [0.0349, 0.0598] | 0.0000 [0.0000, 0.0000] | stable |
| B | majority | H_2x2 | 2->4 | TESTABLE | 0.0334 [0.0257, 0.0528] | 0.0000 [0.0000, 0.0000] | stable |
| A | threshold_high | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 3.7498 [2.2669, 4.7246] | unstable |
| B | threshold_high | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 3.9650 [1.9054, 4.8000] | unstable |
| A | threshold_high | H_2x2 | 2->4 | TESTABLE | 0.0248 [0.0203, 0.0866] | 0.0000 [0.0000, 0.0000] | stable |
| B | threshold_high | H_2x2 | 2->4 | TESTABLE | 0.0247 [0.0092, 0.1170] | 0.0000 [0.0000, 0.0000] | stable |
| A | threshold_low | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 4.4922 [3.2908, 4.9180] | unstable |
| B | threshold_low | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 5.1336 [3.8431, 5.5226] | unstable |
| A | threshold_low | H_2x2 | 2->4 | TESTABLE | 0.0316 [0.0138, 0.0742] | 0.0000 [0.0000, 0.0000] | stable |
| B | threshold_low | H_2x2 | 2->4 | TESTABLE | 0.0340 [0.0181, 0.0802] | 0.0000 [0.0000, 0.0000] | stable |

## A/B CI Overlap And Consistency

| Scheme | Estimator | Pair | Both testable | x* CI overlap | |slope| CI overlap | Candidate consistent (A/B) |
|---|---|---|---|---|---|---|
| average | C_frozen | 1->2 | False | True | True | False |
| average | H_2x2 | 1->2 | True | True | True | True |
| majority | C_frozen | 1->2 | False | True | True | False |
| majority | H_2x2 | 1->2 | True | True | True | True |
| threshold_high | C_frozen | 1->2 | False | True | True | False |
| threshold_high | H_2x2 | 1->2 | True | True | True | True |
| threshold_low | C_frozen | 1->2 | False | True | True | False |
| threshold_low | H_2x2 | 1->2 | True | True | True | True |
| average | C_frozen | 2->4 | True | True | True | True |
| average | H_2x2 | 2->4 | True | True | True | True |
| majority | C_frozen | 2->4 | True | True | True | True |
| majority | H_2x2 | 2->4 | True | True | True | True |
| threshold_high | C_frozen | 2->4 | True | True | True | True |
| threshold_high | H_2x2 | 2->4 | True | True | True | True |
| threshold_low | C_frozen | 2->4 | True | True | True | True |
| threshold_low | H_2x2 | 2->4 | True | True | True | True |

## Required-Pair Readout (`1->2`, `2->4`)

- Testable rows: `12`
- A/B consistent rows (`x*` CI overlap + `|slope|` CI overlap): `12`
- Consistency rate: `1.000`

Interpretation note:
- This is a block-level consistency audit under fixed gates, not a pooled universality claim.