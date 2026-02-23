# Ising Path-4 Full-Run Summary (v0.1)

## Run (latest)

- Script: `scripts/run_full_ising_path4.ps1`
- Seeds: `6` (start `13000`)
- Steps: `4000`
- Burn-in: `500`
- Measure interval: `20`
- Grid size: `128`
- Temperature: `2.269`

## Gates

- Schema validation: `PASS`
- Saturation matrix generated for all `(scheme, estimator, b)` cells

From `saturation_summary.json`:

- Groups total: `48`
- Saturated groups: `24`
- Non-saturated groups: `24`

## Invariant Matrix Snapshot

From `invariant_matrix.csv`:

- `PASS`: `1/12` cells
- `SCOPE_LIMITED_SATURATION`: `8/12` cells
- `ESTIMATOR_UNSTABLE`: `3/12` cells

Interpretation:

- `C_frozen`/`C_activity` are heavily saturated at `b=1,2,4` in this Ising setup, so most closure claims are correctly withheld.
- `H_2x2` is the primary non-saturated channel; it passes under `threshold_high` but is unstable for `1->2->4` under `average/majority/threshold_low`.
- A pilot temperature sweep is available at `results/temp_sweep/temperature_sweep_summary.md` and `results/TEMPERATURE_SWEEP_NOTE.md`.

## Temperature-Control Follow-up (full budget)

See:

- `results/temp_compare_full/temperature_compare_full_summary.md` (seed block A: `15000..15005`)
- `results/temp_compare_full_block_b/temperature_compare_full_block_b_summary.md` (seed block B: `17000..17005`)
- `results/temp_compare_blocks/temperature_compare_blocks_summary.md` (A/B consistency)
- `results/temp_compare_blocks/invariant_candidates_t210_block_ab.md` (`x*`, `|f'(x*)|` A/B CI audit at `T=2.10`)

Readout: under fixed gates, `T=2.10` consistently increases non-saturated coverage and required-triple (`1->2->4`) closure quality versus `T=2.269`, across both seed blocks.
At `T=2.10`, required-pair candidate consistency (`x*` CI overlap + `|f'(x*)|` CI overlap) is `12/12` on testable rows.

## Artifacts

- `data/MANIFEST.json`
- `results/schema_validation.json`
- `results/saturation_matrix.csv`
- `results/scale_maps.json`
- `results/fixed_points.json`
- `results/closure_tests.json`
- `results/invariant_matrix.csv`
- `results/invariant_matrix.md`
- `results/figures/closure_heatmap.png`
- `results/figures/scatter_fits/*.png` (36 panels)
