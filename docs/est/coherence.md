
# EST Coherence Semantics (v2.5)

This document formalizes **coherence gating** as used in FIT v2.4-v2.5.
Coherence is not a single scalar test, but a *typed, preregistered gate*
that controls interpretability of downstream hypotheses.

---

## 1. Definition

**Estimator coherence** evaluates whether multiple admissible estimators
for the same theoretical construct (e.g., constraint C) behave consistently
*within a declared scope*.

Failure of coherence blocks interpretation under EST.

---

## 2. Coherence Taxonomy

### 2.1 COH_SIGNED

Coherence evaluated against a preregistered expected sign.

PASS iff:
- sign(rho) == expected_sign
- |rho| >= rho_min   (or rho >= rho_min for positive-only gates)

FAIL implies: **SIGN_MISMATCH** or **ESTIMATOR_UNSTABLE**.

---

### 2.2 COH_LOCAL

Coherence evaluated within a declared window or phase.

- Windowed PASS + pooled FAIL -> **SCOPE_LIMITED**
- Windowed FAIL -> **ESTIMATOR_UNSTABLE**

---

### 2.3 COH_TASK

Coherence gate depends on task type:

- Ordinal: rank correlation stability
- Metric: scale-sensitive correlation / agreement
- Topological: invariant-preserving agreement

Thresholds must not be mixed across task types.

---

### 2.4 COH_REGIME_DEPENDENT

Coherence holds in some regimes but not others.

This is a **diagnostic finding**, not an estimator defect.

---

## 3. Interpretation Rules

| Coherence Result | Interpretation Status |
|-----------------|----------------------|
| FAIL            | ESTIMATOR_UNSTABLE   |
| PASS (local)    | SCOPE_LIMITED        |
| PASS (global)   | SUPPORTED / CHALLENGED |
| PASS + no events| INCONCLUSIVE         |

---

## 4. Relationship to Phase Algebra

Coherence is **phase-conditional**.

- Pooling across heterogeneous phases is invalid unless explicitly modeled.
- Coherence discontinuities may propose *candidate* phase boundaries,
  but registration requires PT-MSS (S1+S2+S3).

---

## 5. Rationale

Real-world systems are non-stationary.
Coherence locality is a feature, not a bug.

This document codifies coherence as an *epistemic gate*,
not a statistical convenience.

## 6. Related prereg template

See `docs/core/est_prereg_v2.5.md` for a copy/paste preregistration template that makes expected sign, window grids, and boundary exclusions explicit.
