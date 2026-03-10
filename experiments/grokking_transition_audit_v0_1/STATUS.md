# Status (2026-02-23)

## Completed

- Created prereg skeleton (`EST_PREREG.v0_1.yaml`).
- Implemented audit runner (`src/run_pipeline.py`).
- Added per-seed output schema and report template.
- Smoke pipeline validated end-to-end (`EST_PREREG.smoke.yaml`).
- Real data conversion script (`scripts/convert_logs_to_csv.py`).
- **Real run completed** (40 seeds, runs_v0_5 holdout).
- **Structural A/B/C screen completed** on the shared held-out block (`40/40` each).
- **Phase-II v1.0 pilot completed** with verdict `ATTRACTOR_SUPPORTED`.

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
- `outputs/main/asynchronous_profile.csv`
- `outputs/main/asynchronous_profile.md`
- `outputs/main/per_seed/*.json`
- `outputs/main/audit_cards/seed_159.md`
- `outputs/main/audit_cards/seed_168.md`

## March 2026 live follow-up

### Phase-II v1.0 pilot

- artifact: `phase_ii/results/main_v1_0/summary.json`
- verdict: `ATTRACTOR_SUPPORTED`
- design: within-seed matched (`grokked=step_300000`, `pregrok=step_5000`)
- separating metrics: `t90`, `AUC`, `unrecovered`

### Phase-II v1.0 final 40-seed run (active)

- PowerShell chain PID: `32840`
- training process PID: `28032`
- target artifact: `phase_ii/results/final_v1_0_40/summary.json`
- scope: `40+40` within-seed matched, seeds `140–179`

Operational note:

- previous relaunch failed because `$ErrorActionPreference = "Stop"` treated a
  PyTorch warning on `stderr` as fatal;
- runner now uses `Continue` plus explicit `$LASTEXITCODE` checks.

Next pending steps after `final_v1_0_40/summary.json` lands:

- update `experiments/_registry/runs.jsonl` verdict for
  `grokking_phase2_v1_0_final_40_2026-02-26`
- rebuild `experiments/_registry/runs_index.md`

## Audit hardening added

- Diagnostics now include:
  - quantile lock (`q_force/q_info/q_constraint`)
  - concrete thresholds (`tau_*`)
  - event density (`p_*`)
  - signal counts (`n_s1/n_s2/n_s3`)
  - PT candidate count (`n_pt_candidates`)
- Per-seed JSON includes threshold lock, event counts, and candidate steps.
- Replay manifest gate enabled and passed (`compared=40`, `stable=40`).
- Added quantitative asynchronous profile summary from diagnostics:
  - `NO_TRANSITION`: `median n_s1/n_s2/n_s3 = 7/7/7`
  - `frac(all signals>=2)=1.000`, `frac(pt_candidates=0)=1.000`

## CPU robustness audit (2026-02-24)

Window-radius sensitivity sweep completed on fixed Phase-I dataset:

- radii tested: `10, 20, 40, 80`
- output: `outputs/window_radius_sensitivity/window_radius_sensitivity.md`

Result: all four runs are identical in label composition and divergence:

- `REGISTERED=2`, `NO_TRANSITION=35`, `ESTIMATOR_UNSTABLE=3`
- `fit_transition_rate=0.05`, `divergence_rate=0.95`

Interpretation: within this prereg signal family, PT-MSS synchronous/asynchronous
separation is robust to substantial changes in `window_radius_steps`.

## CPU threshold audit (2026-02-24)

Signal-quantile sensitivity sweep completed (`q in {0.98, 0.99, 0.995}`):

- output: `outputs/quantile_sensitivity/quantile_sensitivity.md`

Readout:

- `q=0.98`: `INCONCLUSIVE=40` (`n_valid=0`) due to density-gate invalidation.
- `q=0.99`: baseline pattern (`REGISTERED=2`, `NO_TRANSITION=35`,
  `ESTIMATOR_UNSTABLE=3`, divergence `0.95`).
- `q=0.995`: still `SUPPORTED_FOR_INCREMENTAL_DISTINGUISHABILITY` with
  (`REGISTERED=2`, `NO_TRANSITION=38`, `UNSTABLE=0`, divergence `0.95`).

Interpretation: divergence claim is stable within admissible quantiles; lower
quantiles can violate density admissibility and are correctly rejected as
scope-limited.

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

## Phase-II status (2026-02-24 — COMPLETE)

### Final verdict: INCONCLUSIVE (pass_count=1 / required=2)

| Criterion | Registered | Control | Status |
|---|---|---|---|
| C1: median acc-drop at eps=3e-4 | 0.000 | q25=0.000 | **FAIL** (ceiling — both groups drop to 0) |
| C2: max t_recover | 100 steps | median=100 steps | **FAIL** (ceiling — both groups recover in ≤100 steps) |
| C3: median plateau variance | **2.32e-6** | 1.31e-5 | **PASS** (registered more stable) |

**Root cause of C1/C2 failure**: eps=3e-4 is too small for a fully-grokked model — all seeds (registered and control) absorb the noise trivially within the minimum 100 recovery steps. The perturbation does not stress-test the attractor in a regime where groups are separable.

**C3 signal is real**: registered seeds show lower H_spec variance in the post-transition plateau window (5× lower than control), which is consistent with a more stable representational attractor.

**Boundary-safe wording**:
> Under eps=3e-4 and recover_steps=2000 (eval every 100), the Phase-II pre-registered criteria are not fulfilled (1/3 pass). The C3 evidence is consistent with attractor stability but insufficient under the 2/3 decision rule.

### Next options for Phase-II v0.2

- **A (recommended)**: Increase `epsilon` to `[1e-3, 3e-3]` — stress-test in regime where acc actually drops
- **B**: Increase `recover_steps` to 10 000 to expose divergence between groups
- **C**: Accept INCONCLUSIVE and proceed to v0_6_structural A/B/C sweep (different hypothesis branch)

### Artifacts

- `phase_ii/results/main/summary.json` — full metrics
- `phase_ii/results/main/report.md` — human-readable report
- `phase_ii/results/main/per_seed_metrics.csv` — per-seed detail

## GPU scheduling note

The audit stage itself is CPU-light. Running it concurrently with one active GPU
trainer is safe. Running another heavy trainer concurrently can slow both jobs
and increase variance in wall-time.
