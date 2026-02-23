# Status (2026-02-23)

## Completed

- Created prereg skeleton (`EST_PREREG.v0_1.yaml`).
- Implemented audit runner (`src/run_pipeline.py`).
- Added per-seed output schema and report template.
- Smoke pipeline validated end-to-end (`EST_PREREG.smoke.yaml`).
- Real data conversion script (`scripts/convert_logs_to_csv.py`).
- **Real run completed** (40 seeds, runs_v0_5 holdout).

## Real run snapshot (2026-02-23)

- **n_seeds**: 40
- **label_counts**: `REGISTERED_TRANSITION=2`, `NO_TRANSITION=35`, `ESTIMATOR_UNSTABLE=3`
- **baseline_transition_rate**: 1.0 (all seeds have acc jump)
- **fit_transition_rate**: 0.05 (only 2/40 satisfy PT-MSS)
- **divergence_rate**: 0.95
- **verdict**: `SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY`
- **c1_replay_mode**: `manifest`
- **replay.status**: `pass` (40/40 stable, 100% consistency)
- **replay semantics**: manifest-based **label stability check** (not a retraining reproducibility claim)

### Key finding

FIT PT-MSS detects structural phase transitions (requires co-occurrence of force/info/constraint signals within a window), which is **stricter** than baseline acc_jump detection. Most grokking "transitions" are performance jumps without structural reorganization.

Boundary-safe wording for external write-up:

> Under this preregistered PT-MSS signal family and threshold-locking rule, most
> baseline acc_jump events do not pass tri-signal co-window registration.

## Output artifacts

- `outputs/main/summary.json`
- `outputs/main/diagnostics.csv`
- `outputs/main/report.md`
- `outputs/main/per_seed/*.json`
- `outputs/main/audit_cards/seed_159.md`
- `outputs/main/audit_cards/seed_168.md`

## Audit hardening added

- Diagnostics now include:
  - quantile lock (`q_force/q_info/q_constraint`)
  - concrete thresholds (`tau_*`)
  - event density (`p_*`)
  - signal counts (`n_s1/n_s2/n_s3`)
  - PT candidate count (`n_pt_candidates`)
- Per-seed JSON includes threshold lock, event counts, and candidate steps.
- Replay manifest gate enabled and passed (`compared=40`, `stable=40`).

## Next hardening step (optional)

- Upgrade replay provenance from label-stability to independent rerun trace:
  - add `replay_run_id` and `config_hash` per seed in replay manifest
  - archive replay run artifact path
  - report seed-level label flip rate under independent replay run

## Phase-II prepared (2026-02-23)

Added attractor-stability package under `phase_ii/`:

- `phase_ii/EST_PREREG.phase_ii.yaml`
- `phase_ii/scripts/prepare_phase2_inputs.py`
- `phase_ii/scripts/run_attractor_stability.py`

Generated prep artifacts:

- `phase_ii/results/seed_manifest.json`
- `phase_ii/results/specs/estimator_spec.phase2_checkpoints.yaml`
- `phase_ii/results/run_phase2_gpu.ps1`

Phase-II now has a runnable bridge from Phase-I labels to checkpoint-enabled reruns
for perturb-and-recover analysis.

## Phase-II GPU pilot running (2026-02-22)

- **Terminal**: `4c9ee0ab-cf36-40c8-b114-cafb2f0b5d03`
- **Seeds**: eval=[141, 142, 143, 144] (4-seed pilot, `--limit 4`)
- **Mode**: checkpoint-enabled retrain (300k steps, save_checkpoints=true) + perturb-recover analysis
- **Output**: `phase_ii/results/main/`
- **Log**: `phase_ii/results/pilot_run.log`
- **Concurrent with**: `grokking_v0_6_control` (PID 5240, seeds 140–179) — no conflict (TinyTransformer < 500 MiB VRAM each)
- **Next after pilot**: run full Phase-II sweep (`run_phase2_gpu.ps1`) on all 13 eval seeds

## GPU scheduling note

The audit stage itself is CPU-light. Running it concurrently with one active GPU
trainer is safe. Running another heavy trainer concurrently can slow both jobs
and increase variance in wall-time.
