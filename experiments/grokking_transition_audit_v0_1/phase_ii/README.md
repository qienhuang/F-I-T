# Phase-II: Attractor Stability Test

This package implements the second-stage audit for `grokking_transition_audit_v0_1`.

Phase-I established **incremental distinguishability** (baseline jump vs PT-MSS registration).
Phase-II tests whether `REGISTERED_TRANSITION` seeds are also more stable/recoverable.

## Why this matters

If Phase-II passes, the interpretation upgrades from:

- "stricter detector"

to:

- "dynamical regime distinction (attractor-supporting vs asynchronous reorganization)"

If Phase-II fails, that is still informative: PT-MSS may capture synchrony without attractor shift.

## Tests

- `A` Weight noise stability
- `B` Perturb-and-recover (primary)
- `C` Representation plateau variance (post-transition window)

## Files

- `EST_PREREG.phase_ii.yaml`: prereg and decision rule
- `scripts/prepare_phase2_inputs.py`: seed grouping + checkpoint spec + GPU command scaffold
- `scripts/run_attractor_stability.py`: executes A/B/C and emits Phase-II verdict
- `results/`: output directory
- `results/START_HERE.md`: concise run checklist for local GPU

## Quick start

1. Prepare seed manifest + checkpoint-enabled upstream spec

```powershell
cd github/F-I-T/experiments/grokking_transition_audit_v0_1/phase_ii
python scripts/prepare_phase2_inputs.py --prereg EST_PREREG.phase_ii.yaml
```

2. Run generated GPU command script (checkpoint reruns + Phase-II analysis)

```powershell
powershell -ExecutionPolicy Bypass -File results/run_phase2_gpu.ps1
```

Optional pilot (4 seeds first):

```powershell
powershell -ExecutionPolicy Bypass -File results/run_phase2_gpu_pilot.ps1
```

## Current boundary caveat

Existing `runs_v0_5` were produced with `save_checkpoints: false`, so Phase-II requires
checkpoint-preserving reruns for selected seeds. This package automates that bridge.
