# Ising Temperature Sweep Note (Pilot)

This note summarizes a lightweight boundary check under fixed Path-4 gates.

- Script: `scripts/run_temperature_sweep.ps1`
- Temperatures: `2.10`, `2.269`, `2.40`
- Config per temperature: `3 seeds`, `2500 steps`, `burn_in=400`, `measure_interval=20`, `window=30`

## Matrix-Level Outcome

| T | PASS cells | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |
|---:|---:|---:|---:|---:|---:|
| 2.100 | 8 | 0 | 4 | 0 | 48 |
| 2.269 | 4 | 8 | 0 | 22 | 26 |
| 2.400 | 4 | 8 | 0 | 32 | 16 |

## Interpretation

1. Saturation pressure is strongly temperature-dependent under the same gates.
2. Near/above critical (`2.269`, `2.40`), C-family channels saturate heavily.
3. Lower temperature (`2.10`) restores testability (0 saturated groups) but introduces estimator instability in part of the matrix.
4. For required triple `1->2->4`, pilot pass-rates among testable cells are:
   - `T=2.10`: `8/12` (`0.667`)
   - `T=2.269`: `4/4` (`1.000`, but only 4 testable due to saturation)
   - `T=2.40`: `4/4` (`1.000`, but only 4 testable due to saturation)

This supports a boundary diagnosis reading: Ising outcomes are sensitive to thermodynamic regime, and gate labels correctly separate saturation-limited from unstable cells.
