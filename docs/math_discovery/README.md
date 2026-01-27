# FIT-Math Discovery Engine v0.1
*Turning FIT/EST + FIT-Explorer into a constraint-driven, auditable discovery workflow for mathematical definitions, invariants, lemmas, and proof strategies.*

**Status**: repo-ready draft (v0.1.1)
**Date**: 2026-01-27
**Author**: Qien Huang
**License**: CC BY 4.0

---

## Quick start (TL;DR)

Entry points:
- Main spec: [fit_math_discovery_engine_v0.1.md](fit_math_discovery_engine_v0.1.md)
- Roadmap: [roadmap_to_proof_assistants_v0.1.md](roadmap_to_proof_assistants_v0.1.md)
- Failure map template: [reports/templates/fit_math_failure_map_template_v0.1.1.md](../../reports/templates/fit_math_failure_map_template_v0.1.1.md)
- Search space: [docs/explorers/fit_explorer/search_space/fit_math_search_space_v0.1.yaml](../explorers/fit_explorer/search_space/fit_math_search_space_v0.1.yaml)

---

## What this is

**FIT-Math Discovery Engine** applies FIT-Explorer to **mathematical discovery**:

- Search objects: representations (invariants), lemmas, proof strategies
- Hard gates: checkability, budget, robustness, governance
- Output: feasible leaderboard + failure map (method phase diagram)

This is not about replacing proof; it's about replacing **unlogged intuition** with **auditable exploration**.

---

## Directory structure

```text
docs/math_discovery/
  README.md
  CHANGELOG_v0.1.1.md
  fit_math_discovery_engine_v0.1.md
  fit_math_synth_loop_v0.1.md
  gates_and_labels_v0.1.md
  gates_and_labels_v0.1.1.md
  search_spaces_v0.1.md
  mapping_table_v0.1.md
  roadmap_to_proof_assistants_v0.1.md
  actuator_selection_policy_v0.1.1.md
  explorer_verifier_interface_v0.1.1.md
  representation_sweeps_v0.1.1.md
  examples/
    mini_case_study_toy_world_to_invariants.md

docs/explorers/fit_explorer/
  constraints/fit_math_gates_v0.1.md
  loop/fit_math_prereg_template_v0.1.yaml
  loop/fit_math_prereg_template_v0.1.1.yaml
  search_space/fit_math_search_space_v0.1.yaml

reports/templates/
  fit_math_failure_map_template_v0.1.md
  fit_math_failure_map_template_v0.1.1.md
```

---

## Key concepts

| Concept | Description |
|---------|-------------|
| **Checkability gate** | Candidate must be formalizable and proof-checker accepted |
| **Budget gate** | Proof/verification must complete within declared limits |
| **Robustness gate** | Stable under admissible representation changes |
| **HEURISTIC_FLOOR** | Math analog of FPR_FLOOR: search heuristic provides no signal |
| **Failure map** | Phase diagram of method space showing where/why techniques fail |

---

## Integration phases

1. **Phase A — Toy-world invariant discovery**: Use evolving worlds to find effective variables under feasibility gates
2. **Phase B — Formalization interface**: Translate invariants to Lean/Coq/Isabelle
3. **Phase C — Proof search scaling**: Add lemma library growth under admission gates

See [docs/math_discovery/roadmap_to_proof_assistants_v0.1.md](roadmap_to_proof_assistants_v0.1.md) for details.

---

## How to integrate into your repo

If you want to vendor this into another repo, copy:

- docs/math_discovery/
- docs/explorers/fit_explorer/constraints/fit_math_gates_v0.1.md
- docs/explorers/fit_explorer/loop/fit_math_prereg_template_v0.1.1.yaml
- docs/explorers/fit_explorer/search_space/fit_math_search_space_v0.1.yaml
- reports/templates/fit_math_failure_map_template_v0.1.1.md

---

## Related entry points

- FIT-Explorer core: [docs/explorers/fit_explorer/README.md](../explorers/fit_explorer/README.md)
- World-Evolution extension: [docs/world_evolution/fit_explorer_world_evolution_v0.1.md](../world_evolution/fit_explorer_world_evolution_v0.1.md)
- GMB monitorability: [docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md](../benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md)
