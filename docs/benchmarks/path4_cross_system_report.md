# Path-4 Cross-System Report (GoL / Langton / Ising)

Source pipelines:

- `experiments/gol_multiscale_invariants`
- `experiments/langton_multiscale_invariants`
- `experiments/ising_multiscale_invariants`

Generated summary source:

- `experiments/ising_multiscale_invariants/results/CROSS_SYSTEM_PATH4_REPORT.md`
- `experiments/ising_multiscale_invariants/results/cross_system_path4_summary.csv`

## Scope And Definitions

- `testable` means triples **not excluded by saturation gate** (`PASS + ESTIMATOR_UNSTABLE`).
- Gate constants are fixed across systems (`eps=0.10`, `saturation_ratio_threshold=0.90`, closure `tau=0.05`).
- `C_activity` is treated as an implementation-consistency channel (`1 - C_frozen`), not an independent estimator family.

## Table 1: Matrix Labels

| System | Cells | PASS | SCOPE_LIMITED_SATURATION | ESTIMATOR_UNSTABLE | Saturated groups | Non-saturated groups |
|---|---:|---:|---:|---:|---:|---:|
| GoL | 12 | 9 | 3 | 0 | 15 | 33 |
| Langton | 12 | 11 | 1 | 0 | 4 | 44 |
| Ising | 12 | 1 | 8 | 3 | 24 | 24 |

## Table 2: Required Triple `1->2->4`

| System | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |
|---|---:|---:|---:|---:|---:|---:|
| GoL | 9 | 3 | 0 | 9 | 1.000 | 0.00289 |
| Langton | 11 | 1 | 0 | 11 | 1.000 | 0.00177 |
| Ising | 1 | 8 | 3 | 4 | 0.250 | 0.07555 |

## Table 3: Optional Triple `2->4->8`

| System | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |
|---|---:|---:|---:|---:|---:|---:|
| GoL | 0 | 12 | 0 | 0 | n/a | n/a |
| Langton | 9 | 3 | 0 | 9 | 1.000 | 0.00326 |
| Ising | 4 | 8 | 0 | 4 | 1.000 | 0.01626 |

## Interpretation

- Langton is currently the strongest cross-system positive case: high PASS coverage and low saturation.
- Ising under the default boundary (`T=2.269`) is regime-sensitive: high saturation and low required-triple stability.
- The gate stack behaves as intended: saturation and instability are surfaced explicitly, and strong claims are blocked outside testable regions.

## Ising Full Two-Temperature Control

Full-budget, same-seed comparison:

- `experiments/ising_multiscale_invariants/scripts/run_temperature_compare_full.ps1`
- outputs under `experiments/ising_multiscale_invariants/results/temp_compare_full`

Key outcomes:

| Temperature | PASS cells | SCOPE_LIMITED | UNSTABLE | Saturated groups | Non-saturated groups | Required `1->2->4` PASS rate (testable) |
|---:|---:|---:|---:|---:|---:|---:|
| 2.100 | 10 | 0 | 2 | 8 | 40 | 1.000 |
| 2.269 | 2 | 8 | 2 | 24 | 24 | 0.500 |

This supports a bounded claim: Ising closure quality is strongly regime-dependent under fixed Path-4 gates.

### Unstable cells (full compare details)

- At `T=2.10`:  
  `threshold_high + C_activity` and `threshold_high + C_frozen` are unstable on optional triple `2->4->8` (RMSE `~0.0542`).
- At `T=2.269`:  
  `average + H_2x2` and `majority + H_2x2` are unstable on required triple `1->2->4` (RMSE `~0.0578`).

## Seed Robustness Note

Two paired fixed-seed blocks are now available:

- Block A: `15000..15005` (`results/temp_compare_full`)
- Block B: `17000..17005` (`results/temp_compare_full_block_b`)

Block-comparison output:

- `experiments/ising_multiscale_invariants/results/temp_compare_blocks/temperature_compare_blocks_summary.md`

Current bounded readout: regime effect (`T=2.10` vs `T=2.269`) is consistent across both blocks under fixed gates. Claims remain scoped to audited blocks unless pooled criteria are preregistered.

| Block | T | PASS | SCOPE_LIMITED | UNSTABLE | Required `1->2->4` PASS rate (testable) |
|---|---:|---:|---:|---:|---:|
| A (`15000..15005`) | 2.100 | 10 | 0 | 2 | 1.000 |
| A (`15000..15005`) | 2.269 | 2 | 8 | 2 | 0.500 |
| B (`17000..17005`) | 2.100 | 10 | 0 | 2 | 1.000 |
| B (`17000..17005`) | 2.269 | 2 | 8 | 2 | 0.500 |

### Fixed-Point / Slope Candidate Consistency (T=2.10, A/B)

Audit output:

- `experiments/ising_multiscale_invariants/results/temp_compare_blocks/invariant_candidates_t210_block_ab.md`
- `docs/benchmarks/path4_invariant_candidates_ising_t210_block_ab.md`

Key readout (required pairs `1->2`, `2->4`):

- testable rows: `12`
- rows with both `x*` CI overlap and `|f'(x*)|` CI overlap: `12`
- consistency rate: `1.000`

This upgrades the claim from closure consistency to block-consistent invariant candidates under fixed gates.

## Invariant Candidate Add-on

A candidate-level comparison (`x*`, `|f'(x*)|`) for independent estimators is available at:

- `docs/benchmarks/path4_invariant_candidates_langton_vs_ising_t210.md`

This add-on compares Langton vs Ising (`T=2.10`) for selected schemes (`average`, `majority`) and pairs (`1->2`, `2->4`).
