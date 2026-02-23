# Phase-II GPU Start

## 1) Prepare inputs (already idempotent)

```powershell
cd github/F-I-T/experiments/grokking_transition_audit_v0_1/phase_ii
python scripts/prepare_phase2_inputs.py --prereg EST_PREREG.phase_ii.yaml
```

## 2) Pilot first (recommended if another GPU job is active)

```powershell
powershell -ExecutionPolicy Bypass -File results/run_phase2_gpu_pilot.ps1
```

## 3) Full run

```powershell
powershell -ExecutionPolicy Bypass -File results/run_phase2_gpu.ps1
```

## Outputs

- `results/main/per_seed_metrics.csv`
- `results/main/summary.json`
- `results/main/report.md`

## Note

If only pilot seeds were rerun, summary will report missing seeds and should be
treated as connectivity/smoke evidence, not final Phase-II verdict.

