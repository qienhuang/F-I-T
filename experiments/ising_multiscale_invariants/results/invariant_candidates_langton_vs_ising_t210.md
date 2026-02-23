# Invariant Candidates: Langton vs Ising (T=2.10)

Independent estimators only (`C_frozen`, `H_2x2`). `C_activity` is intentionally excluded as it is deterministically derived from `C_frozen`.

## Candidate Table (isotonic bootstrap)

| System | Scheme | Estimator | Pair | Saturation | x* mean [CI] | |slope| mean [CI] | Slope label |
|---|---|---|---|---|---|---|---|
| Ising_T2.10 | average | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7013 [1.3462, 2.8632] | unstable |
| Langton | average | C_frozen | 1->2 | TESTABLE | 0.0000 [0.0000, 0.0000] | 0.9886 [0.9842, 1.0018] | unknown |
| Ising_T2.10 | average | H_2x2 | 1->2 | TESTABLE | 0.1357 [0.0788, 0.2627] | 0.0000 [0.0000, 0.0000] | stable |
| Langton | average | H_2x2 | 1->2 | TESTABLE | 0.1007 [0.0727, 0.2381] | 0.8040 [0.0000, 1.4674] | unknown |
| Ising_T2.10 | majority | C_frozen | 1->2 | SCOPE_LIMITED_SATURATION | 0.0000 [0.0000, 0.0000] | 2.7013 [1.3462, 2.8632] | unstable |
| Langton | majority | C_frozen | 1->2 | TESTABLE | 0.0000 [0.0000, 0.0000] | 0.9886 [0.9842, 1.0018] | unknown |
| Ising_T2.10 | majority | H_2x2 | 1->2 | TESTABLE | 0.1357 [0.0788, 0.2627] | 0.0000 [0.0000, 0.0000] | stable |
| Langton | majority | H_2x2 | 1->2 | TESTABLE | 0.1007 [0.0727, 0.2381] | 0.8040 [0.0000, 1.4674] | unknown |
| Ising_T2.10 | average | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 5.5745 [3.9222, 6.1475] | unstable |
| Langton | average | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 1.0345 [1.0198, 1.0402] | unstable |
| Ising_T2.10 | average | H_2x2 | 2->4 | TESTABLE | 0.0374 [0.0349, 0.0598] | 0.0000 [0.0000, 0.0000] | stable |
| Langton | average | H_2x2 | 2->4 | TESTABLE | 0.0184 [0.0184, 0.0184] | 0.0000 [0.0000, 0.0000] | stable |
| Ising_T2.10 | majority | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 5.5745 [3.9222, 6.1475] | unstable |
| Langton | majority | C_frozen | 2->4 | TESTABLE | 0.0000 [0.0000, 0.0000] | 1.0345 [1.0198, 1.0402] | unstable |
| Ising_T2.10 | majority | H_2x2 | 2->4 | TESTABLE | 0.0374 [0.0349, 0.0598] | 0.0000 [0.0000, 0.0000] | stable |
| Langton | majority | H_2x2 | 2->4 | TESTABLE | 0.0184 [0.0184, 0.0184] | 0.0000 [0.0000, 0.0000] | stable |

## Cross-System CI Overlap

| Scheme | Estimator | Pair | x* CI overlap | |slope| CI overlap |
|---|---|---|---|---|
| average | C_frozen | 1->2 | True | False |
| average | H_2x2 | 1->2 | True | True |
| majority | C_frozen | 1->2 | True | False |
| majority | H_2x2 | 1->2 | True | True |
| average | C_frozen | 2->4 | True | False |
| average | H_2x2 | 2->4 | False | True |
| majority | C_frozen | 2->4 | True | False |
| majority | H_2x2 | 2->4 | False | True |

Notes:
- This is a candidate-level comparison, not a universality claim.
- Interpretation remains conditioned on non-saturated labels and preregistered gates.