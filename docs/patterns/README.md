# Structural Archetypes (Patterns)

Goal: make FIT reusable as an *analysis tool* without requiring readers to adopt the full theory stack.

These patterns sit **between**:
- **Core** (MCC / Phase Algebra / PT-MSS): definitions and minimal commitments
- **Cases**: concrete, story-like applications for non-specialists

Patterns are **not** quantitative predictors. They are reusable structural templates:
- 1 structure diagram
- 1 page description (trigger, boundary conditions, common failure modes)
- 1 positive example + 1 negative example (to prevent over-generalization)

## How to use patterns (recommended)

1. Pick the pattern that best matches your system’s failure mode.
2. Map your system onto the diagram (nodes/edges).
3. Check the qualitative signature (PT-MSS-style minimal signals).
4. Apply *minimal interventions* (do not overfit; prefer reversible changes).
5. If the signature does not match, treat it as a negative example and switch patterns.

## Index

- [PATTERN_01: Φ₃ Trap](PATTERN_01_Phi3_Trap.md)
- [PATTERN_02: Feedback Dominance](PATTERN_02_Feedback_Dominance.md)
- [PATTERN_03: Constraint Saturation](PATTERN_03_Constraint_Saturation.md)
- [PATTERN_04: Hierarchical Escape](PATTERN_04_Hierarchical_Escape.md)

## Related entry points

- Core Card: `docs/core/fit_core_card.md`
- Phase Algebra + PT-MSS: `docs/core/phase_algebra.md`
- Φ₃ stability criteria: `docs/core/phi3_stability.md`
- Case studies: `docs/cases/README.md`
