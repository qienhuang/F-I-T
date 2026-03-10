# Window-Radius Sensitivity (Phase-I PT-MSS)

- base_prereg: `D:/FIT Lab/github/F-I-T/experiments/grokking_transition_audit_v0_1/EST_PREREG.v0_1.yaml`
- radii: `[10, 20, 40, 80]`
- replay gate: disabled for this sensitivity sweep (label-logic only)

| radius | n_valid | REGISTERED | NO_TRANSITION | ESTIMATOR_UNSTABLE | INCONCLUSIVE | fit_transition_rate | divergence_rate | verdict |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 10 | 40 | 2 | 35 | 3 | 0 | 0.0500 | 0.9500 | SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY |
| 20 | 40 | 2 | 35 | 3 | 0 | 0.0500 | 0.9500 | SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY |
| 40 | 40 | 2 | 35 | 3 | 0 | 0.0500 | 0.9500 | SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY |
| 80 | 40 | 2 | 35 | 3 | 0 | 0.0500 | 0.9500 | SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY |

Interpretation:
- Stable `REGISTERED` counts and divergence rates across radii indicate robust synchronous/asynchronous separation.
- Large shifts suggest sensitivity to PT-MSS simultaneity assumptions.
