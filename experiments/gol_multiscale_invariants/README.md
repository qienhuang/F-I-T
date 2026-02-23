# GoL Multiscale Invariants (Path 4)

This experiment package operationalizes the Path-4 plan for scale-invariant extraction:

- schema-locked long table (`seed,t,scheme,b,estimator,value`)
- saturation gate audit per `(scheme, estimator, b)`
- prereg-locked thresholds and labels

The package starts from existing GoL RG lens data and converts it into a stricter, auditable format.

## Layout

- `prereg/gol_scale_invariants_v0_1.yaml`
- `scripts/prepare_long_table.py`
- `scripts/validate_schema.py`
- `scripts/saturation_gate.py`
- `data/MANIFEST.json`
- `results/saturation_matrix.csv`

## Quick Start

```powershell
cd experiments/gol_multiscale_invariants
python scripts/prepare_long_table.py
python scripts/validate_schema.py --input data/multiscale_long.parquet --out results/schema_validation.json
python scripts/saturation_gate.py --input data/multiscale_long.parquet --out_csv results/saturation_matrix.csv --out_json results/saturation_summary.json
powershell -ExecutionPolicy Bypass -File scripts/run_semigroup_start.ps1
python scripts/fit_scale_invariants.py --input data/multiscale_long.parquet --saturation_csv results/saturation_matrix.csv --results_dir results --bootstrap_resamples 200
python scripts/render_invariant_matrix_md.py --input_csv results/invariant_matrix.csv --output_md results/invariant_matrix.md
python scripts/plot_path4_figures.py --input data/multiscale_long.parquet --fixed_points_json results/fixed_points.json --saturation_csv results/saturation_matrix.csv --invariant_csv results/invariant_matrix.csv --out_dir results/figures
```

If `pyarrow` is not available, use CSV fallback:

```powershell
python scripts/validate_schema.py --input data/multiscale_long.csv --out results/schema_validation.json
python scripts/saturation_gate.py --input data/multiscale_long.csv --out_csv results/saturation_matrix.csv --out_json results/saturation_summary.json
```

## Current Scope

- This commit implements Path-4 data prep and gates (PLAN sections A1/A3).
- Path-4 semigroup hard-gate has been started and recorded under `results/closure/`.
- Path-4 fitting and invariant extraction now run through `scripts/fit_scale_invariants.py`.
- Main outputs:
- `results/scale_maps.json`
- `results/fixed_points.json`
- `results/closure_tests.json`
- `results/invariant_matrix.csv`
- `results/figures/closure_heatmap.png`
- `results/figures/scatter_fits/*.png`
- `results/APPENDIX_scale_invariants.md`
