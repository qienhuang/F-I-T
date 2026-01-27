# Offline References Manifest (fit-lab-est-session-guide)

This folder is the minimal offline pack so users can understand the discipline without browsing the whole repo.
It is not a replacement for the runnable engines in `github/F-I-T/`.

## Files

- `CORE_CONTRACT_ONEPAGER.md`
  - One-page contract: boundary, window, estimator tuple, failure semantics, phase context.
- `PREREG_TEMPLATE.md`
  - Copy/paste prereg template (Phase A vs Phase B discipline).
- `ARTIFACT_CONTRACT_ALARMS.md`
  - Minimum reporting requirements for low-FPR alarm claims.
- `NARRATIVE_INTAKE_TEMPLATE.md`
  - Stage 0 "reader first" intake template (explicitly NOT EVIDENCE).

## Canonical runnable engines (repo paths)

- Path layout note:
  - If you are at the FIT repo root, use `tools/...`, `examples/...`, `experiments/...`.
  - If the FIT repo is nested in a larger workspace, prefix with `github/F-I-T/`.

- Low-FPR alarms / monitorability:
  - `tools/fit_proxy_alarm_kit/README.md`
  - `examples/dr_one_demo/README.md`
- Constrained exploration:
  - `tools/fit_constrained_explorer_kit/README.md`
- EWBench / governance executability:
  - `tools/fit_ewbench_kit/README.md`
- Toy phase labs:
  - `tools/fit_hopfield_lab_kit/README.md`

## Version note

- This references pack is intended to be stable; the runnable engines evolve faster.
- When making claims, cite the engine README and the exact command + artifact paths used.
