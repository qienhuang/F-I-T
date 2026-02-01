# Evidence note (template)

This folder contains an EST-gated Tier-2 run for scRNA commitment.

## What this is

This is **not** a claim that fate commitment has been "explained" from expression. It is a claim that:

1) a preregistered estimator family was evaluated under declared boundaries, and  
2) the run either produced a phase-conditional interpretation or an explicit non-interpretability verdict.

## Run identity

- Case: `scrna_commitment_tier2p11`
- Prereg: `outputs/PREREG.locked.yaml`
- Primary artifacts:
  - `outputs/coherence_report.json`
  - `outputs/regime_report.md`
  - `outputs/tradeoff_onepage.png`
  - `outputs/metrics_log.parquet`

## Summary (fill after run)

- Dataset: `<dataset>`
- Window axis: `<axis>`
- Mixing label: `<label>`
- n_windows: `<n>`
- rho_across_windows: `<rho>`
- Verdict: `<OK_PER_WINDOW | ESTIMATOR_UNSTABLE | INCONCLUSIVE>`

## Interpretation rule

- If verdict is `OK_PER_WINDOW`: interpretation is allowed only under the preregistered boundary and windowing.
- If verdict is `ESTIMATOR_UNSTABLE` or `INCONCLUSIVE`: interpretation is disallowed; the correct outcome is a failure label.
