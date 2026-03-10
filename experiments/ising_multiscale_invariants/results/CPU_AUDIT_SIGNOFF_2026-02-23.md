# Ising Path-4 CPU Audit Sign-off (2026-02-23)

This note locks the temperature-control audit outputs generated on CPU from existing run artifacts.

## Scope

- System: `experiments/ising_multiscale_invariants`
- Gate semantics: unchanged (`eps=0.10`, saturation gate, closure `tau=0.05`)
- Compare sets:
  - Block A: `results/temp_compare_full` (`T2p10`, `T2p269`)
  - Block B: `results/temp_compare_full_block_b` (`T2p10`, `T2p269`)

## Regenerated artifacts

- `results/temp_sweep/temperature_sweep_summary.csv`
- `results/temp_sweep/temperature_sweep_summary.md`
- `results/temp_compare_blocks/temperature_compare_blocks_summary.csv`
- `results/temp_compare_blocks/temperature_compare_blocks_summary.md`
- `results/temp_compare_blocks/invariant_candidates_t210_block_ab.csv`
- `results/temp_compare_blocks/invariant_candidates_t210_block_ab_overlap.csv`
- `results/temp_compare_blocks/invariant_candidates_t210_block_ab.md`
- `results/temp_compare_blocks/tau_sensitivity_summary.csv`
- `results/temp_compare_blocks/tau_sensitivity_summary.md`

## Locked readout

Matrix labels by temperature and block:

| Block | T | PASS cells | SCOPE_LIMITED | UNSTABLE | Saturated groups | Non-saturated groups |
|---|---:|---:|---:|---:|---:|---:|
| A | 2.100 | 10 | 0 | 2 | 8 | 40 |
| B | 2.100 | 10 | 0 | 2 | 8 | 40 |
| A | 2.269 | 2 | 8 | 2 | 24 | 24 |
| B | 2.269 | 2 | 8 | 2 | 24 | 24 |

Required triple (`1->2->4`) quality:

| Block | T | PASS | SCOPE_LIMITED | UNSTABLE | Testable | PASS rate (testable) | Median RMSE (testable) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.02175 |
| B | 2.100 | 4 | 8 | 0 | 4 | 1.000 | 0.01982 |
| A | 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.04506 |
| B | 2.269 | 2 | 8 | 2 | 4 | 0.500 | 0.06845 |

Invariant-candidate A/B consistency at `T=2.10` (testable required pairs): `12/12`.

## Verdict

`T=2.10` is a reproducible regime-conditioned positive zone for Path-4 closure under fixed gates.
`T=2.269` remains mixed/scope-limited under the same gate.

This is an estimator-level, gate-conditioned claim. It is not a universality claim.

## Threshold sensitivity note

`tau` sensitivity (`0.02, 0.05, 0.08`) was audited on the same required-triple RMSE set:

- At prereg baseline `tau=0.05`: `T=2.10` = `1.0` pass rate (A/B), `T=2.269` = `0.5` (A/B).
- At strict `tau=0.02`: `T=2.10` remains above `T=2.269`.
- At loose `tau=0.08`: separation partially collapses in block A but persists in block B.

This supports using `tau=0.05` as an operational threshold for this experiment family while keeping threshold sensitivity explicitly documented.

## Permutation negative-control note

Negative-control audit file:

- `results/temp_compare_blocks/permutation_negative_control.csv`
- `results/temp_compare_blocks/permutation_negative_control.md`

Summary on testable rows (`1->2->4`, direct vs composed):

- `T=2.10`: Block A `4/4` pass, Block B `4/4` pass
- `T=2.269`: Block A `4/4` pass, Block B `1/4` pass

Interpretation:

- At `T=2.10`, closure quality remains far from permutation baseline across both blocks.
- At `T=2.269`, negative-control stability degrades in one block, consistent with mixed/scope-limited behavior.
