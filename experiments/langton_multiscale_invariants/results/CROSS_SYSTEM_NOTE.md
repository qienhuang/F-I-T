# Cross-System Note: GoL vs Langton (Path-4 Gates)

This note compares the latest locked runs under identical Path-4 semantics.

## Gate Summary

| System | Cells (scheme x estimator) | PASS | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE |
|---|---:|---:|---:|---:|
| GoL | 12 | 9 | 3 | 0 |
| Langton | 12 | 11 | 1 | 0 |

## Saturation Summary

| System | Groups total | Saturated | Non-saturated |
|---|---:|---:|---:|
| GoL | 48 | 15 | 33 |
| Langton | 48 | 4 | 44 |

## Interpretation

- Both systems support semigroup closure in non-saturated regions.
- Neither system requires forced interpretation in saturated regions.
- Langton (current full run) shows broader testable coverage than GoL under this gate setup.

## Scope Discipline

This comparison is an audit-level result, not a universality claim. Any stronger cross-system statement should remain bounded to:

- declared scheme family,
- declared estimator set,
- declared saturation gate.

