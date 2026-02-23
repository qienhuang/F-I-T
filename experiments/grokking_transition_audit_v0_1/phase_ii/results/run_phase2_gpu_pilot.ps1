$ErrorActionPreference = "Stop"
Set-Location "D:\FIT Lab\grokking"

# Pilot: first 4 eval seeds from the generated phase-II checkpoint spec.
python -m grokking.runner.sweep --spec "D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\results\specs\estimator_spec.phase2_checkpoints.yaml" --out "D:\FIT Lab\grokking\runs_v0_6_structural_phase2" --phase eval --limit 4

python "D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\scripts\run_attractor_stability.py" `
  --prereg "D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\EST_PREREG.phase_ii.yaml" `
  --manifest "D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\results\seed_manifest.json" `
  --runs-root "D:\FIT Lab\grokking\runs_v0_6_structural_phase2" `
  --grokking-root "D:\FIT Lab\grokking" `
  --diagnostics "D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\outputs\main\diagnostics.csv" `
  --out-dir "D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\results\main"
