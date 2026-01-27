# Monitorability Boundary — Toy Theorem + Diagnostics (v0.4 companion)

**Status**: draft-final (paper-ready)  
**Version**: v0.4  
**Date**: 2026-01-27

---

## 1. Problem statement

In early-warning settings, an indicator score may contain **ranking information** (AUC > 0.5) while being **operationally unusable** as an alarm under low-FPR budgets.

This document provides:
1) a toy proposition explaining **FPR floors** as a structural calibration failure, and  
2) practical diagnostics to classify failures as `RANK_ONLY` vs `ESTIMATOR_UNSTABLE`.

---

## 2. Definitions

Let each evaluation unit be a window ending at time `t` with label `y(t) ∈ {0,1}` (negative/positive).  
An indicator produces a scalar score `s(t)`.

For a threshold `τ`, define alarm `a(t) = 1[s(t) ≥ τ]`.

Define:

- Achieved false positive rate (FPR):

$$
\mathrm{FPR}(\tau) := \Pr(a(t)=1 \mid y(t)=0)
$$

- AUC: ranking-based discriminative content (does not involve a fixed operating point).

---

## 3. Toy proposition (sufficient condition for FPR floors)

### Proposition (two-level score degeneracy ⇒ FPR floor)

Assume that on **negative windows**, the score takes only two values:

- `s(t) ∈ {s_L, s_H}` with `s_H > s_L`,
- and let `p := Pr(s(t)=s_H | y(t)=0)`.

Then for any threshold `τ`:

- If `τ > s_H`, FPR(τ)=0,
- If `s_L < τ ≤ s_H`, FPR(τ)=p,
- If `τ ≤ s_L`, FPR(τ)=1.

Therefore, unless `p` is already below your risk budget, **no threshold can achieve low target FPR**. The achievable FPR set is discrete: `{0, p, 1}`.

#### Interpretation

- AUC can still be > 0.5 if positives also tend to have higher scores.
- But alarm usability collapses if `p` is large (e.g., `p ≈ 0.44`), producing an **FPR floor**.

This is the minimal formal skeleton of “ranking exists but alarm does not”.

---

## 4. Practical diagnostics for real (non-binary) scores

Real scores are not exactly two-valued, but FPR floors often come from **effective quantization / saturation** in the negative class.

### Diagnostic D1 — effective support size

Compute the number of unique score values (or bins) on negatives:

- `K_eff = exp(H_bin)` where `H_bin` is entropy of binned scores.

Very small `K_eff` is a warning sign for discrete achievable FPR steps.

### Diagnostic D2 — achieved FPR vs target FPR curve

For targets `f ∈ {0.01, 0.05, 0.10}`, calibrate `τ_f` and report achieved `f_hat`.

- If `f_hat` is nearly constant across targets, you likely have a floor.
- If `min f_hat` is much larger than the risk budget, the alarm objective is ill-posed.

### Diagnostic D3 — tie/cluster dominance

Compute the fraction of negatives within the top-k quantiles that share the same score (ties), or the within-cluster variance if score comes from a model.

High tie-dominance implies threshold movement cannot smoothly control alarm rate.

---

## 5. Repair patterns (what counts as a “real fix”)

A fix is only real if it **restores Layer B controllability** (not merely improves AUC).

Typical repair strategies (benchmark-neutral):

1. Change the estimator family to increase negative-class score resolution (reduce saturation).
2. Redefine the evaluation unit (windowing) to reduce pathological autocorrelation in negatives.
3. Add calibration health monitoring and allow `ABSTAIN` when calibration degenerates.
4. Apply trajectory control (slow hardening / increase observation resolution) to keep the system in a monitorable regime.

---

## 6. What to claim in papers (safe wording)

- If a detector has high AUC but fails Layer B: label `RANK_ONLY` and state **monitorability boundary**.
- If outcomes flip under small perturbations: label `ESTIMATOR_UNSTABLE` (measurement instability).
- Only when Layer B passes and Layer C is non-trivial should you claim “usable alarm”.

