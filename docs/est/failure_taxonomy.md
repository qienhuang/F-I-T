# EST Outcome Taxonomy (v2.5)

This page defines the **public-facing outcome labels** used across FIT real-world cases.
It is intentionally compact: the goal is consistent reporting, not narrative.

Related:
- Coherence semantics: `docs/est/coherence.md`
- Prereg template: `docs/core/est_prereg_v2.5.md`

## 1) Core outcome labels (one-page table)

| Label | Meaning (what you may claim) | Common triggers | Required artifacts | Next action |
|---|---|---|---|---|
| SUPPORTED | The preregistered hypothesis is supported **within the declared boundary**. | Coherence PASS (as preregistered); sufficient events; primary metric passes. | `coherence_report.json`, prereg + locked prereg, primary results table/figure. | Replicate on holdout (new seeds, new time period, or a second dataset) without changing the prereg. |
| CHALLENGED | The preregistered hypothesis is contradicted **within the declared boundary**. | Coherence PASS; sufficient events; primary metric fails in the preregistered direction. | Same as SUPPORTED + explicit failure counts. | Treat as a negative result; propose boundary conditions or estimator-family alternatives as new preregs. |
| ESTIMATOR_UNSTABLE | Measurements do not support interpretation under EST at this scope. | Coherence FAIL (wrong sign, too small magnitude, window FAIL under an all-pass rule, or high instability across scales). | `coherence_report.json`, `fail_windows.md` (if windowed), and the prereg. | Redesign the estimator family or narrow the boundary; do not interpret regimes/causality under the failing family. |
| SCOPE_LIMITED | Interpretation is licensed only within preregistered sub-scopes (windows/phases). | Pooled FAIL but all preregistered windows PASS; or metrics are defined only on a sub-interval by construction. | Windowed coherence report + explicit window definitions + per-window outputs. | Report claims as "within-window only"; avoid pooling across heterogeneous regimes unless explicitly modeled. |
| INCONCLUSIVE | The run is auditable but does not answer the primary question. | No events; undefined primary metric in the event region; insufficient data in a preregistered window; or power too low. | Prereg + diagnostics showing the blocking condition (event counts, undefined regions, min-points failures). | Collect missing artifacts or revise the prereg boundary; do not backfill interpretation. |

## 2) Coherence outcomes (typed gate -> reporting label)

Coherence is a preregistered gate; the same rho value can imply different outcomes depending on the preregistered semantics.

| Typed coherence outcome | Typical mapping |
|---|---|
| COH_SIGNED PASS (expected sign + magnitude) | Enables SUPPORTED/CHALLENGED evaluation for downstream hypotheses. |
| COH_SIGNED FAIL (sign-mismatch or too small magnitude) | ESTIMATOR_UNSTABLE (unless the prereg explicitly treats sign as a diagnostic-only dimension). |
| COH_LOCAL PASS (windowed) + pooled FAIL | SCOPE_LIMITED (phase heterogeneity). |
| COH_REGIME_DEPENDENT | Usually SCOPE_LIMITED unless the prereg models regimes explicitly. |

## 3) Reporting rules (anti-hype)

1) Never replace failure labels with softer prose. Use the label and then explain the trigger.
2) Never treat "higher AUC" as evidence of alarm usability. Operating-point constraints (FPR/coverage/floors) are first-class.
3) When a label changes due to a different prereg (e.g., sign-aware coherence), treat it as a new run, not a reinterpretation.
