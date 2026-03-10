# Grokking Transition Audit Summary

## Run metadata

- `run_id`: GROKKING_TRANSITION_AUDIT_V0_1_Q0p98_SENS
- `prereg_id`: GROKKING_TRANSITION_AUDIT_V0_1_Q0p98
- `n_seeds`: 40

## Label counts

| Label | Count |
|---|---:|
| REGISTERED_TRANSITION | 0 |
| NO_TRANSITION | 0 |
| ESTIMATOR_UNSTABLE | 0 |
| INCONCLUSIVE | 40 |

## Primary outcomes

- Baseline transition rate: `0.000`
- FIT transition rate: `0.000`
- Divergence rate: `0.000`
- C1 threshold: `0.150`
- C1 status: `FAIL`
- Replay status: `not_required`
- Replay compared: `0`
- Replay stable: `0`
- Replay interpretation: label-stability audit (not retraining-level reproducibility by itself).

## Notes

- Keep all gate failures in report; do not drop unstable seeds.
- If `INCONCLUSIVE > 0`, include a short incident note with affected seed IDs.
