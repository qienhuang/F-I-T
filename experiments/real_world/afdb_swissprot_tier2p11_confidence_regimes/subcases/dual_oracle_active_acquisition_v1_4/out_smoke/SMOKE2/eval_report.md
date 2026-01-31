# Eval report — Dual‑Oracle + Δ‑Lag + Leakage Audit (v1.3)

- run_id: `SMOKE2`
- parent_case_id: `afdb_swissprot_tier2p11_confidence_regimes`
- universe_mode: `union`
- tau_pae: `1.0`
- tau_msa_depth: `16.0`
- primary FPR cap: `0.01`
- tpr_min_for_usable: `0.01`
- W_jump: `3` | delta_tpr: `0.05`
- policy_diag_split: `labeled_val`
- prereg_sha256: `ee7c9250d968092c9a489ec25c0aa809fd50b9d9bf054dd2cbe8c1a118452dd7`
- input_metrics_sha256: `59f184808783d644267acd08e2464a3e7bdbb060302776b15b07fa61771a7554`
- leakage_audit.overall_pass: `True`

## Event summary (primary)

| policy | alloc | base | alpha | K | floor_pae | floor_msa | floor=max | joint | Δ (joint-floor) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| adaptive_joint_gap__composite_batch_ff_uK__a0.7__K5000 | adaptive_joint_gap | composite_batch_ff_uK | 0.70 | 5000 | 4 | 4 | 4 | 4 | 0 |
| adaptive_joint_gap__composite_batch_ff_rK__a0.7__K5000 | adaptive_joint_gap | composite_batch_ff_rK | 0.70 | 5000 | 4 | 4 | 4 | 4 | 0 |

## Final operating‑point summary (holdout @ primary cap)

| policy | PAE TPR@cap | PAE FPR | PAE FPR_floor@TPRmin | MSA TPR@cap | MSA FPR | MSA FPR_floor@TPRmin | final MAE(C3_hat) |
|---|---:|---:|---:|---:|---:|---:|---:|
| adaptive_joint_gap__composite_batch_ff_uK__a0.7__K5000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0.000000 | 1.000000 | 0.555374 |
| adaptive_joint_gap__composite_batch_ff_rK__a0.7__K5000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0.000000 | 1.000000 | 0.553042 |

## Interpretation rules

- Acquisition decisions are driven by labeled validation diagnostics only (no holdout leakage).
- A run is invalid if `leakage_audit.overall_pass` is false.
- `FPR_floor@TPRmin` is a hardness metric: if it exceeds cap, the alarm is unusable at that cap.
- Δ‑lag interprets stabilization after floors resolve; it is protocol‑dependent.

