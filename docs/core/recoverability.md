# Recoverability (Core-Adjacent Artifact, v2.x Compatible)

Status: core-adjacent operational lens (non-breaking)  
Primitives used: `F / I / T / C / Phase (Phi)` only  
Depends on: EST discipline, Phase-II no-return framing  
Purpose: operationalize practical irreversibility as recoverability under bounded resources.

---

## 1) One-line definition

Recoverability is the bounded-resource feasibility of reconstructing a target structural state (or equivalence class) from the current state under a declared boundary and estimator tuple.

This is a control/diagnostics claim, not a metaphysical claim.

---

## 2) EST scope (required)

All recoverability statements are scoped to a declared tuple:

`E = (S_t, B, {F_hat, C_hat, I_hat}, W)`

Every claim must declare:

- Target structure: `Sigma*` (what counts as "the same")
- Equivalence relation: `~` (ordinal / metric / topological)
- Budget: `B` (time, compute, authority, intervention scope)
- Recovery protocol family: `Pi_rec`

No declaration -> no recoverability claim.

---

## 3) Minimal formalization

### 3.1 Recovery condition

Recovery to `Sigma*` holds if:

`exists S' in Pi_rec(S_t; B) such that S' ~ Sigma*`

Task typing for `~`:

- Ordinal: order/rank preserved
- Metric: value/threshold within tolerance
- Topological: event/regime structure preserved

### 3.2 Recoverability score

Primary quantities:

- `P_recover(B)`: success probability over seeds/perturbations
- `T_recover`: time to recovery (conditional on success)
- `D_drift`: drift depth before recovery (e.g., writeback propagation depth)

Preregistered composite score (illustrative but executable):

`R(B) = P_recover(B) * exp(-lambda * T_recover) * exp(-mu * D_drift)`

Interpretation:

- `R ~ 1`: robustly recoverable under declared budget
- `R ~ 0`: practically irrecoverable under declared budget

---

## 4) Recoverability and irreversibility

Separate three layers:

1. Microscopic reversibility (physics-level)
2. Bounded recoverability (operations-level)
3. Deployable accessibility (governance/control-level)

Operational irreversibility in FIT means: `R(B)` declines or remains near zero under fixed, realistic budget.

---

## 5) Relation to constraint `C`

Constraint can affect recoverability in opposite directions depending on target:

- High `C` can improve `R_to_attractor` (faster return to stable basin)
- High `C` can reduce `R_to_prior_structure` (fewer reverse paths)

Therefore recoverability is target-relative and must name `Sigma*`.

---

## 6) Integration with no-return diagnosis

Tempo inequalities can show correction lag is too large. Recoverability adds a second gate:

- Even with adequate correction latency, a structure may already be practically irrecoverable under budget.

Optional no-return extension:

- If `R(B) < R_min` (preregistered), label `IRRECOVERABLE_UNDER_SCOPE`.
- See operational template extension: `docs/core/no_return_memo_recoverability_extension.md`.

---

## 7) Monitorability requirement

Any detector used to trigger recovery control must pass FPR controllability checks.

If FPR is not controllable at declared operating points, detector output is diagnostic-only and must not trigger automatic control actions.

This prevents "ranking looks good but operations fail" misuse.

---

## 8) Empirical snapshot (toy, reproducible)

Source experiment: `experiments/self_reference_recoverability_v0_1`

Boundary: synthetic agent loop with memory writeback and optional control window.  
Groups: `G0` baseline, `G1` no-writeback, `G2` controlled window.

From `outputs/report.md` (200 episodes/group):

| Group | R | P_recover | Lock-in rate | Non-recovered rate |
|---|---:|---:|---:|---:|
| G0 | 0.0158 | 0.305 | 0.840 | 0.695 |
| G1 | 0.6401 | 1.000 | 0.000 | 0.000 |
| G2 | 0.1583 | 0.760 | 0.835 | 0.240 |

Interpretation (scope-limited):

- Removing self-writeback eliminates lock-in in this toy boundary.
- Control window improves recoverability vs baseline but does not remove lock-in onset.
- This is structural evidence under toy dynamics, not a real-agent generalization.

---

## 9) Failure labels

- `ESTIMATOR_UNSTABLE`: verdict flips across admissible estimator family
- `SCHEME_DEPENDENT`: verdict flips across admissible recovery protocol family
- `BUDGET_SENSITIVE`: small budget changes flip verdict
- `TARGET_AMBIGUOUS`: equivalence relation under-specified
- `MONITORABILITY_INADEQUATE`: detector cannot satisfy FPR controllability

---

## 10) Non-goals / guardrails

This document does **not** claim:

- subjective consciousness measurement
- ontology of information
- observer-independent recoverability
- universal reversibility laws

It claims only:

Under declared scope and bounded resources, recoverability is measurable and useful for practical irreversibility and control design.

---

## 11) Repro links

- Experiment package: `experiments/self_reference_recoverability_v0_1/README.md`
- Prereg: `experiments/self_reference_recoverability_v0_1/EST_PREREG.yaml`
- Repo-safe results snapshot: `experiments/self_reference_recoverability_v0_1/RESULTS.md`
- Full local run artifact: `experiments/self_reference_recoverability_v0_1/outputs/report.md`
