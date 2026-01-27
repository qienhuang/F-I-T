# GMB v0.4 Addendum - HRM-Inspired Indicator Family
*Hierarchical-convergence observables as monitorability-friendly alarm candidates*

**Status**: draft-final (repo-ready)  
**Addendum to**: `docs/benchmarks/gmb_v0_4/gmb_v0.4_spec.md`  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0

---

## 0. Purpose

This addendum introduces a new **indicator family** for GMB v0.4:

> **`hierarchical_convergence`** - metrics derived from **multi-timescale convergence structure** inside a recurrent / implicit-depth model.

Motivation: in grokking and other phase-transition dynamics, output metrics (loss/acc) and many "hard indicators" can exhibit **monitorability failure** (e.g., **FPR floors**) despite good ranking performance. GMB formalizes this via **Layer-B FPR controllability**.

HRM-style architectures provide a concrete mechanism that suggests a new class of signals more likely to be **calibratable** under low-FPR budgets:

- a fast subsystem repeatedly converges within cycles,
- a slow subsystem updates less frequently,
- cycle updates produce structured "reset" events and residual spikes,
- representational capacity shows hierarchical dimensionality separation (high-level higher PR than low-level).

These signals are closer to the system's *internal state of computation* than to task performance and often have richer negative-class support (reducing saturation/ties), improving FPR controllability **in principle**. This addendum defines candidate estimators without assuming HRM specifically.

Reference inspiration: **Hierarchical Reasoning Model** (HRM), arXiv:2211.04325.

---

## 1. Scope and prerequisites

This family is applicable when **any** of the following is available:

1. **Multi-timescale loop**: identifiable "fast" and "slow" update rhythms (explicit H/L modules, ACT segments, recurrent depth blocks, DEQ iterations, etc.).
2. **Residual / update magnitudes**: per-step update size is measurable (hidden-state delta, forward residual norm, or equivalent).
3. **State trajectories**: hidden states can be sampled over time (or per cycle/segment) to compute covariance-based dimensionality proxies.

If you cannot observe internal states, you can still use GMB v0.4 (dynamics/process/judge families), but this addendum does not apply.

---

## 2. Notation

We assume a nested loop structure (conceptual, not necessarily architectural):

- High-level cycles indexed by `k = 1,...,N`
- Low-level steps within a cycle indexed by `j = 1,...,T`

Let:

- `z_H(k)`: high-level state at end of cycle `k`
- `z_L(k,j)`: low-level state within cycle `k` at step `j`

Let "residual / update magnitude" proxies be:

- `r_L(k,j) := || z_L(k,j) - z_L(k,j-1) ||`
- `r_H(k)   := || z_H(k) - z_H(k-1) ||`

(Any norm is acceptable if declared; L2 is the default.)

---

## 3. Candidate estimators (indicator definitions)

Each candidate yields a scalar score `s(t)` per checkpoint/window (GMB interface). All are **alarm candidates only if Layer-B passes**.

### 3.1 HC-1: Low-level relaxation time (per cycle)

**Idea**: how quickly the fast subsystem reaches a local equilibrium within each cycle.

Define a per-cycle relaxation time:

$$
\tau_L(k;\epsilon) := \min\{ j : r_L(k,j) \le \epsilon \}
$$

Aggregate into a window score (examples):

- `median_tau_L` over cycles within the window
- `p90_tau_L` (tail sensitivity)
- `mean_tau_L` (less robust; use only if justified)

**Interpretation**:
- rising $\tau_L$ can indicate impending regime change (slowing down),
- collapsing $\tau_L$ can indicate premature convergence / saturation (risk of score discretization).

### 3.2 HC-2: Cycle reset spike rate

**Idea**: hierarchical convergence often creates structured residual spikes at cycle boundaries due to context updates/reset.

Define boundary spikes:

$$
\Delta r(k) := r_L(k,1) - r_L(k,T)
$$

Score options:

- `spike_rate`: fraction of cycles with $\Delta r(k) \ge \theta$
- `spike_strength`: median of $\Delta r(k)$

**Interpretation**:
- loss of spikes can mean the slow subsystem stops meaningfully re-contextualizing the fast subsystem (computational stalling),
- chaotic spikes (high variance) can indicate unstable coupling.

### 3.3 HC-3: H/L coupling mismatch

**Idea**: the slow module provides context; the fast module converges to a context-conditioned equilibrium. Large mismatch suggests "the fast solver cannot settle" under the current plan.

If you have a projection $g(\cdot)$ mapping both modules to a comparable space, define:

$$
m(k) := \| g_H(z_H(k)) - g_L(z_L(k,T)) \|
$$

Score = `median_mismatch` or `p90_mismatch` within the window.

### 3.4 HC-4: Hierarchical dimensionality ratio (PR-ratio)

**Idea**: learned separation where high-level representations occupy higher effective dimensionality than low-level ones.

Given covariance eigenvalues $\{ \lambda_i \}$:

$$
PR = \frac{(\sum_i \lambda_i)^2}{\sum_i \lambda_i^2}
$$

Compute per window:

- `PR_H` from `z_H(k)` samples
- `PR_L` from `z_L(k,T)` (or a fixed intra-cycle slice)

Define ratio:

$$
\rho_{PR} := \frac{PR_H}{PR_L}
$$

Score options:
- `rho_PR`
- `log_rho_PR`

### 3.5 HC-5: Adaptive compute / halting statistics (if ACT exists)

If adaptive computation exists (segments/halting), define:

- `mean_steps`
- `halt_margin` (halt vs continue value margin, if available)
- `compute_variance`

---

## 4. How these candidates interact with GMB layers

### 4.1 Layer-B is still the gate

All `hierarchical_convergence` candidates must be evaluated under the same:

- target FPR set $\mathcal{F}$,
- achieved-vs-target tolerance $\epsilon$,
- floor limit $f_{\text{floor\_max}}$.

If Layer-B fails, label `RANK_ONLY` regardless of AUC/AP.

### 4.2 Additional diagnostics recommended

Always report:

- effective negative support size (binned entropy or unique counts),
- tie/cluster dominance near the top quantiles,
- stability under small changes to cycle length `T` (if controllable) and window size `W`.

These directly target the main pathology behind FPR floors: score degeneracy in the negative class.

---

## 5. Minimal prereg additions

Add candidate entries, e.g.

```yaml
candidates:
  - name: "HC_tau_L_p90"
    family: "hierarchical_convergence"
    params:
      epsilon_residual: 1e-3
      aggregation: "p90"
      cycle_T: 16
  - name: "HC_rho_PR"
    family: "hierarchical_convergence"
    params:
      sampling: "per_cycle_end"
      pr_method: "cov_eigs"
      aggregation: "log_ratio"
```

Also preregister:

- how internal states are sampled,
- which layers/modules correspond to H vs L,
- the norm used for residuals,
- binning choices for support diagnostics.

---

## 6. Recommended "paper-ready" figure (optional)

A single figure is often enough:

1. achieved-FPR vs target-FPR curve (controllability / floor),
2. HC score time series around event time `t*`,
3. negative-class score histogram / effective support size.

---

## 7. How to fold this into papers (and v0.5 checklist)

If you publish GMB as a spec note, keep this addendum as **supplementary**: it is an indicator family definition, not a benchmark result.

If you publish a "real run" paper (e.g., grokking early warning), this addendum contributes a clean **future-work hook**: "here is a family that is designed to target Layer-B failure modes (FPR floors)."

Minimal v0.5 checklist (distilled from internal review; keep it short):

- **Minimal repair control**: add a "repair" baseline that only reweights/clips one problematic component, and evaluate under the same Layer-B gate.
- **Quantify ABSTAIN**: when an alarm never triggers at target FPR, report the abstain rate explicitly (do not hide it behind AUC).
- **Track effective-n collapse**: report effective support size / tie dominance; treat high tie dominance as a calibration risk indicator.
- **Controlled-Nirvana interface rule**: only indicators labeled `SUPPORTED_FOR_ALARM` are eligible to trigger authority suspension (tool gating). All others are diagnostic-only.

