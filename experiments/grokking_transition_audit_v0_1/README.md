# Grokking Transition Audit v0.1

This experiment package operationalizes a **PT-MSS + topological coherence gate**
audit for grokking transition claims.

The design goal is not to force positive findings. The audit emits failure labels
(`NO_TRANSITION`, `ESTIMATOR_UNSTABLE`, `INCONCLUSIVE`) when transition evidence
is not structurally coherent.

## Scope

- Task family: modular arithmetic grokking runs (small transformer)
- Input: per-seed time series of precomputed signal proxies
- Output: per-seed labels + gate diagnostics + aggregate verdict

This package focuses on the **audit layer**. It expects signal columns from
upstream training logs and does not prescribe one specific training stack.

## Directory layout

- `EST_PREREG.v0_1.yaml`: main prereg template (quantile thresholds)
- `EST_PREREG.smoke.yaml`: smoke config on synthetic data
- `src/run_pipeline.py`: audit runner
- `scripts/make_smoke_data.py`: synthetic data generator
- `outputs/schema.json`: output artifact schema
- `outputs/summary_template.md`: report template
- `outputs/*/audit_cards/`: auto-generated cards for registered seeds
- `docs/conceptual_diagram_synchronous_vs_asynchronous.md`: conceptual figure note
- `docs/synchronous_locking_vs_asynchronous_reorganization.md`: interpretation memo
- `docs/conceptual_diagram_synchronous_vs_asynchronous.zh_cn.md`: conceptual diagram (Chinese)
- `docs/synchronous_locking_vs_asynchronous_reorganization.zh_cn.md`: interpretation memo (Chinese)

## Labels

- `REGISTERED_TRANSITION`: PT-MSS co-window satisfied and family gate passed
- `NO_TRANSITION`: PT-MSS co-window not satisfied
- `ESTIMATOR_UNSTABLE`: PT-MSS satisfied but family alignment/order gate failed
- `INCONCLUSIVE`: density gate violation or malformed/missing data

## Quick start (smoke)

```powershell
cd experiments/grokking_transition_audit_v0_1
python scripts/make_smoke_data.py
python src/run_pipeline.py --prereg EST_PREREG.smoke.yaml
```

Expected smoke behavior:

- mix of `REGISTERED_TRANSITION`, `NO_TRANSITION`, `ESTIMATOR_UNSTABLE`,
  and `INCONCLUSIVE` labels
- generated outputs under `outputs/smoke/`
- `diagnostics.csv` includes locked thresholds/densities/event counts
- audit cards are generated for any `REGISTERED_TRANSITION` seeds

## Replay evidence (optional hardening)

Set `replay.enabled: true` in prereg and provide `replay.manifest` JSON to
enforce label-stability replay checks. When disabled, `c1_min_replay_count` is
used as count fallback for backward compatibility.

Important interpretation boundary:

- Replay manifest mode verifies **label stability** under the declared audit
  setup.
- It should not be interpreted as a full retraining-level reproducibility claim
  unless replay run IDs/config hashes and independent rerun artifacts are also
  provided.

## GPU scheduling note

This audit script is CPU-light. It can run while a GPU training job is active,
as long as it reads completed logs and does not launch another heavy trainer.

## Phase-II (attractor stability)

Phase-I established incremental distinguishability. Phase-II asks whether
`REGISTERED_TRANSITION` seeds also show stronger stability/recoverability.

- package: `phase_ii/`
- prereg: `phase_ii/EST_PREREG.phase_ii.yaml`
- prep: `phase_ii/scripts/prepare_phase2_inputs.py`
- runner: `phase_ii/scripts/run_attractor_stability.py`

```powershell
cd experiments/grokking_transition_audit_v0_1/phase_ii
python scripts/prepare_phase2_inputs.py --prereg EST_PREREG.phase_ii.yaml
powershell -ExecutionPolicy Bypass -File results/run_phase2_gpu.ps1
```
