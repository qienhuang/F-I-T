# Cross-System Note: GoL vs Langton vs Ising (Path-4 Gates)

This note compares the latest locked runs under identical Path-4 semantics.

## Gate Summary

| System | Cells (scheme x estimator) | PASS | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE |
|---|---:|---:|---:|---:|
| GoL | 12 | 9 | 3 | 0 |
| Langton | 12 | 11 | 1 | 0 |
| Ising | 12 | 1 | 8 | 3 |

## Saturation Summary

| System | Groups total | Saturated | Non-saturated |
|---|---:|---:|---:|
| GoL | 48 | 15 | 33 |
| Langton | 48 | 4 | 44 |
| Ising | 48 | 24 | 24 |

## Interpretation

- GoL/Langton show broad closure support under non-saturated conditions.
- Ising is substantially more saturation-limited under the current setup (`T=2.269`), with additional instability in `H_2x2` for the required triple `1->2->4` under multiple schemes.
- This is a useful boundary result: the same gate stack distinguishes robust closure regimes from saturation-dominated regimes.

## Scope Discipline

This is an audit-level comparison, not a universality claim. Stronger cross-system claims must remain bounded to:

- declared scheme family,
- declared estimator set,
- declared saturation gate,
- declared system dynamics and control parameters (e.g., temperature).
