# FIT-Math Discovery Engine v0.1.1 Patch Notes
**Date**: 2026-01-27

This patch responds to the main actionable points raised in external feedback:

- Clarify **Explorer vs Verifier** interface and trust boundary.
- Replace the oversimplified “FPR=0” phrasing with a precise statement about **kernel soundness** vs **discovery heuristics**.
- Add a concrete **Actuator Selection Policy** so the Synth Loop is executable (not “random mutation + narrative”).
- Define a minimal, automatable **Representation Sweep** suite so `REPRESENTATION_UNSTABLE` is testable.
- Update templates to require evidence-chain linking from `SUPPORTED` to verifier artifacts.

Files added/updated in this patch pack:

- `docs/math_discovery/explorer_verifier_interface_v0.1.1.md` (NEW)
- `docs/math_discovery/actuator_selection_policy_v0.1.1.md` (NEW)
- `docs/math_discovery/representation_sweeps_v0.1.1.md` (NEW)
- `docs/math_discovery/gates_and_labels_v0.1.1.md` (UPDATED replacement)
- `docs/explorers/fit_explorer/loop/fit_math_prereg_template_v0.1.1.yaml` (UPDATED template)
- `reports/templates/fit_math_failure_map_template_v0.1.1.md` (UPDATED template)

Merge strategy:
- Add the NEW files.
- Replace `gates_and_labels_v0.1.md` with `gates_and_labels_v0.1.1.md` (or keep both, but update links).
- Prefer the v0.1.1 prereg and report templates for new runs.
