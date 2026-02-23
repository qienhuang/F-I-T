# Ising Multiscale Invariants (Path-4 Cross-System)

This package mirrors the Path-4 gate pipeline used in GoL/Langton, but on 2D Ising (Glauber/Metropolis dynamics near critical temperature).

Goal: test whether scale-map closure and saturation-aware invariants are reproducible in a third discrete system under the same audit discipline.

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
cd experiments/ising_multiscale_invariants
powershell -ExecutionPolicy Bypass -File scripts/run_full_ising_path4.ps1
```

Smoke run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_ising_path4_smoke.ps1
```

Temperature sweep (pilot):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_temperature_sweep.ps1
```

Two-temperature full compare (same seed block):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_temperature_compare_full.ps1
```

Two-temperature full compare (independent seed block B):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_temperature_compare_full_block_b.ps1
```

Block consistency summary (A vs B):

```powershell
python scripts/compare_temperature_blocks.py --block_a_root results/temp_compare_full --block_b_root results/temp_compare_full_block_b --out_csv results/temp_compare_blocks/temperature_compare_blocks_summary.csv --out_md results/temp_compare_blocks/temperature_compare_blocks_summary.md
```

Invariant candidate A/B CI audit (`x*`, `|f'(x*)|`, `T=2.10`):

```powershell
python scripts/summarize_invariant_candidates_blocks.py --block_a_fixed results/temp_compare_full/T2p10/fixed_points.json --block_b_fixed results/temp_compare_full_block_b/T2p10/fixed_points.json --out_csv results/temp_compare_blocks/invariant_candidates_t210_block_ab.csv --out_md results/temp_compare_blocks/invariant_candidates_t210_block_ab.md
```

## Prereg

- `prereg/ising_scale_invariants_v0_1.yaml`

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
- `results/temp_sweep/temperature_sweep_summary.md`
- `results/CROSS_SYSTEM_PATH4_REPORT.md`
- `results/temp_compare_full/temperature_compare_full_summary.md`
- `results/temp_compare_full_block_b/temperature_compare_full_block_b_summary.md`
- `results/temp_compare_blocks/temperature_compare_blocks_summary.md`
- `results/temp_compare_blocks/invariant_candidates_t210_block_ab.md`

## Notes

- This is a cross-system reproducibility scaffold.
- It keeps the same gates (`SCOPE_LIMITED_SATURATION`, closure RMSE threshold) to avoid moving-target evaluation.
