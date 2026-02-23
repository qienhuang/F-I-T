# Langton Multiscale Invariants (Path-4 Cross-System)

This package mirrors the Path-4 gate pipeline used in GoL, but on Langton's Ant.

Goal: verify whether scale-map closure and saturation-aware invariants are reproducible in a second discrete system using the same audit discipline.

## Locked Schema

Long table format:

- `seed`
- `t`
- `scheme`
- `b`
- `estimator` (`C_frozen`, `C_activity`, `H_2x2`)
- `value`

## Quick Start

```powershell
cd experiments/langton_multiscale_invariants
powershell -ExecutionPolicy Bypass -File scripts/run_full_langton_path4.ps1
```

Smoke run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_langton_path4_smoke.ps1
```

## Outputs

- `data/MANIFEST.json`
- `results/schema_validation.json`
- `results/saturation_matrix.csv`
- `results/scale_maps.json`
- `results/fixed_points.json`
- `results/closure_tests.json`
- `results/invariant_matrix.csv`
- `results/invariant_matrix.md`
- `results/figures/closure_heatmap.png`
- `results/summary.md`
- `results/REPORT.md`
- `results/CROSS_SYSTEM_NOTE.md`

## Notes

- This is a cross-system reproducibility scaffold.
- It keeps the same gates (`SCOPE_LIMITED_SATURATION`, closure RMSE threshold) to avoid moving-target evaluation.
