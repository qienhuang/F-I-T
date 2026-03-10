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

## Main-run audit artifacts

For the current real run (`outputs/main/`):

- `summary.json`: aggregate verdict and replay gate status
- `diagnostics.csv`: per-seed locked thresholds/densities/event counts
- `report.md`: bounded interpretation
- `asynchronous_profile.csv` + `asynchronous_profile.md`: quantitative
  summary of synchronous vs asynchronous patterns by label

Regenerate asynchronous profile from diagnostics:

```powershell
cd experiments/grokking_transition_audit_v0_1
python scripts/summarize_asynchronous_profile.py `
  --diagnostics outputs/main/diagnostics.csv `
  --summary outputs/main/summary.json `
  --out-csv outputs/main/asynchronous_profile.csv `
  --out-md outputs/main/asynchronous_profile.md
```

## CPU audit: window-radius sensitivity

To test robustness of PT-MSS simultaneity assumptions, run a fixed-dataset sweep
over multiple `window_radius_steps` values:

```powershell
cd experiments/grokking_transition_audit_v0_1
python scripts/run_window_radius_sensitivity.py `
  --base-prereg EST_PREREG.v0_1.yaml `
  --radii 10 20 40 80
```

Outputs:

- `outputs/window_radius_sensitivity/window_radius_sensitivity.csv`
- `outputs/window_radius_sensitivity/window_radius_sensitivity.md`

Current readout (`10/20/40/80`): label counts and divergence rate are identical
across radii (`REGISTERED=2`, `NO_TRANSITION=35`, `UNSTABLE=3`,
`divergence_rate=0.95`), supporting robust synchronous/asynchronous separation
under this gate family.

## CPU audit: signal-quantile sensitivity

To test threshold-lock dependence, run a shared quantile sweep for F/I/C:

```powershell
cd experiments/grokking_transition_audit_v0_1
python scripts/run_signal_quantile_sensitivity.py `
  --base-prereg EST_PREREG.v0_1.yaml `
  --quantiles 0.98 0.99 0.995
```

Outputs:

- `outputs/quantile_sensitivity/quantile_sensitivity.csv`
- `outputs/quantile_sensitivity/quantile_sensitivity.md`

Current readout:

- `q=0.98`: all seeds `INCONCLUSIVE` (`n_valid=0`) due to density-gate overflow
  (scope-limited setting).
- `q=0.99`: baseline main-run pattern (`2/35/3`, divergence `0.95`).
- `q=0.995`: verdict remains supported; composition shifts to (`2/38/0`) with
  unchanged divergence (`0.95`).

Interpretation: key divergence claim is stable for valid quantiles (`0.99`,
`0.995`), while lower quantile (`0.98`) violates prereg density admissibility.

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
