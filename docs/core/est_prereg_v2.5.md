
# EST Preregistration Template (v2.5)

This document extends EST preregistration with explicit coherence,
boundary, and phase-context declarations.

Related: `docs/est/coherence.md` (coherence gate semantics and failure labels).

---

## 1. Coherence Specification

```yaml
coherence_spec:
  metric: spearman
  rho_min: 0.6
  expected_sign: +1        # +1 or -1 (required). If the intended family is inverse-coupled, preregister -1.
  task_type: ordinal       # ordinal | metric | topological

  window_grid_days: [30, 60, 90, 180, 365]

  pooled_failure_handling: OK_PER_WINDOW
  # OK_PER_WINDOW | ESTIMATOR_UNSTABLE

  outputs:
    - coherence_radius
    - coherence_landscape
    - scale_stability_matrix
```

---

## 2. Boundary Specification

```yaml
boundary_spec:
  warmup_exclusion: "first 30d"
  edge_exclusion: "last 30d"
  undefined_metric_policy: SCOPE_LIMITED
  # SCOPE_LIMITED | INCONCLUSIVE
```

---

## 3. Phase Context

```yaml
phase_context:
  known_boundaries: []

  candidate_detection:
    method: coherence_split_max
    role: candidate_only

  registration:
    protocol: PT_MSS
    requires: [S1, S2, S3]
```

---

## 4. Failure Label Semantics

| Label | Meaning |
|------|--------|
| SUPPORTED | Hypothesis supported within declared scope |
| CHALLENGED | Hypothesis contradicted within scope |
| ESTIMATOR_UNSTABLE | Coherence failure |
| SCOPE_LIMITED | Valid only within declared window/phase |
| INCONCLUSIVE | Insufficient events or undefined metrics |

---

## 5. Versioning

This template is **non-breaking** with EST v2.4.

It clarifies interpretability conditions without changing core FIT primitives.
