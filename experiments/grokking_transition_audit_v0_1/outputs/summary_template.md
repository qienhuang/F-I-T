# Grokking Transition Audit Summary

## Run metadata

- `run_id`: {{run_id}}
- `prereg_id`: {{prereg_id}}
- `n_seeds`: {{n_seeds}}

## Label counts

| Label | Count |
|---|---:|
| REGISTERED_TRANSITION | {{count_registered}} |
| NO_TRANSITION | {{count_no_transition}} |
| ESTIMATOR_UNSTABLE | {{count_unstable}} |
| INCONCLUSIVE | {{count_inconclusive}} |

## Primary outcomes

- Baseline transition rate: `{{baseline_transition_rate}}`
- FIT transition rate: `{{fit_transition_rate}}`
- Divergence rate: `{{divergence_rate}}`
- C1 threshold: `{{c1_threshold}}`
- C1 status: `{{c1_status}}`
- Replay status: `{{replay_status}}`
- Replay compared: `{{replay_compared_count}}`
- Replay stable: `{{replay_stable_count}}`
- Replay interpretation: label-stability audit (not retraining-level reproducibility by itself).

## Notes

- Keep all gate failures in report; do not drop unstable seeds.
- If `INCONCLUSIVE > 0`, include a short incident note with affected seed IDs.
