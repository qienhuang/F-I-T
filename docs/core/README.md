# FIT Core Artifacts (v2.4.1+)

Status: **source-of-truth** for the *core artifacts* (compressed entry points) introduced around the v2.4.1 line.

These documents:
- Do **not** add new primitives or new propositions beyond [`docs/v2.4.md`](../v2.4.md).
- Provide a minimal, teachable, handoff-ready interface to the framework.
- Aim to reduce misreadings while keeping EST discipline intact.

## Index

Notation: phases are written as `Φ₁/Φ₂/Φ₃` (ASCII: `Phi1/Phi2/Phi3` in filenames/code).

### Start Here
- [`fit_core_card.md`](./fit_core_card.md) - one-page operational entry
- [`fit_two_page_card.md`](./fit_two_page_card.md) - two-page entry (core + post-Φ₃ bifurcation)
- [`MCC.md`](./MCC.md) - Minimal Coherent Core (6 core assertions)

### Structure
- [`MCC_graph.md`](./MCC_graph.md) - MCC dependency graph (DAG)
- [`phase_algebra.md`](./phase_algebra.md) - Phase Algebra + PT-MSS (operationalization of P11/P13)

### Stability
- [`phi3_stability.md`](./phi3_stability.md) - Φ₃ stability criteria (SC-1/SC-2/SC-3; nirvana operationalized)
- [`flexibility_card.md`](./flexibility_card.md) - Flexibility Card (monitoring schema: reconfiguration vs lock-in vs drift vs estimator instability)

### Extensions and Guardrails
- [`FIT_Core_Extension_Post_Phi3.md`](./FIT_Core_Extension_Post_Phi3.md) - post-Φ₃ bifurcation (two structurally viable paths)
- [`FIT_Misuse_Guard_and_FAQ.md`](./FIT_Misuse_Guard_and_FAQ.md) - misuse guard and FAQ (red lines and boundary conditions)

### Applications
- [`grokking_phase_mapping.md`](./grokking_phase_mapping.md) - Grokking as FIT phase transition (Φ₁→Φ₂→Φ₃ mapping for ML)

### For New Readers
- [`reconstruction_guide.md`](./reconstruction_guide.md) - How to reconstruct FIT from MCC
