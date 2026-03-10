# Grokking Transition Audit Summary

## Run metadata

- `run_id`: GROKKING_TRANSITION_AUDIT_V0_1_WR10_SENS
- `prereg_id`: GROKKING_TRANSITION_AUDIT_V0_1_WR10
- `n_seeds`: 40

## Label counts

| Label | Count |
|---|---:|
| REGISTERED_TRANSITION | 2 |
| NO_TRANSITION | 35 |
| ESTIMATOR_UNSTABLE | 3 |
| INCONCLUSIVE | 0 |

## Primary outcomes

- Baseline transition rate: `1.000`
- FIT transition rate: `0.050`
- Divergence rate: `0.950`
- C1 threshold: `0.150`
- C1 status: `PASS`
- Replay status: `not_required`
- Replay compared: `0`
- Replay stable: `0`
- Replay interpretation: label-stability audit (not retraining-level reproducibility by itself).

## Notes

- Keep all gate failures in report; do not drop unstable seeds.
- If `INCONCLUSIVE > 0`, include a short incident note with affected seed IDs.
