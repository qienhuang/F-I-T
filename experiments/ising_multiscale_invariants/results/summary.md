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

### CPU audit sign-off (2026-02-23)

From `results/temp_compare_blocks/temperature_compare_blocks_summary.md`:

| Block | T | PASS cells | SCOPE_LIMITED | UNSTABLE | Saturated groups | Non-saturated groups |
|---|---:|---:|---:|---:|---:|---:|
| A | 2.100 | 10 | 0 | 2 | 8 | 40 |
| B | 2.100 | 10 | 0 | 2 | 8 | 40 |
| A | 2.269 | 2 | 8 | 2 | 24 | 24 |
| B | 2.269 | 2 | 8 | 2 | 24 | 24 |

Required triple (`1->2->4`) across seed blocks:

| Block | T | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.02175 |
| B | 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.01982 |
| A | 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.04506 |
| B | 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.06845 |

Bounded interpretation:
- Under fixed gates and paired block design, `T=2.10` is a **regime-conditioned positive zone** for Path-4 closure.
- `T=2.269` remains **mixed / scope-limited**, not a universal failure.
- This is a gate-conditioned, estimator-level statement; it is not a universality claim.

### Tau-sensitivity audit (`tau in {0.02, 0.05, 0.08}`)

See: `results/temp_compare_blocks/tau_sensitivity_summary.md`

Snapshot:
- At prereg baseline `tau=0.05`, required-triple pass rate is `1.0` at `T=2.10` in both blocks, versus `0.5` at `T=2.269`.
- Under stricter `tau=0.02`, `T=2.10` remains above `T=2.269` (`0.25/0.75` vs `0.0/0.0` across A/B).
- Under looser `tau=0.08`, separation weakens in block A (`1.0` vs `1.0`) but persists in block B (`1.0` vs `0.5`).

Interpretation:
- Regime-conditioned separation is robust around the prereg threshold (`tau=0.05`), but expectedly sensitive under very loose/strict tau values.

### Permutation negative control (`1->2->4`)

See: `results/temp_compare_blocks/permutation_negative_control.md`

Readout:
- `T=2.10`: negative control passes in both blocks (`4/4`, `4/4` on testable rows), i.e., observed closure quality is not reproduced by shuffled direct-map labels.
- `T=2.269`: block A passes `4/4`, but block B passes only `1/4`; several rows show real RMSE not better than permutation baseline.

Interpretation:
- This supports the same bounded conclusion as above: `T=2.10` is a more stable regime-conditioned closure zone.
- Under `T=2.269`, the control is less stable across seed blocks, reinforcing mixed/scope-limited status under fixed gates.

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
- `results/temp_compare_blocks/temperature_compare_blocks_summary.csv`
- `results/temp_compare_blocks/temperature_compare_blocks_summary.md`
- `results/temp_compare_blocks/invariant_candidates_t210_block_ab.csv`
- `results/temp_compare_blocks/invariant_candidates_t210_block_ab.md`
- `results/temp_compare_blocks/tau_sensitivity_summary.csv`
- `results/temp_compare_blocks/tau_sensitivity_summary.md`
- `results/temp_compare_blocks/permutation_negative_control.csv`
- `results/temp_compare_blocks/permutation_negative_control.md`
