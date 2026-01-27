# GMB v0.4 — Grokking Monitorability Benchmark
*A monitorability-first benchmark for early warning under risk budgets*

**Status**: draft-final (repo-ready)  
**Version**: v0.4  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0

---

## 0. Why this benchmark exists

Most “hard indicators” for grokking-like transitions are evaluated as **ranking signals** (AUC/AP).  
But in governance / safety / intervention settings, ranking is insufficient:

> An indicator is useful only if it admits **operational alarm thresholds** under explicit risk budgets.

GMB v0.4 operationalizes this as **FPR controllability** and treats failure modes (e.g., **FPR floors**) as first-class outcomes.

---

## 1. Core objects

### 1.1 System boundary (must be declared)

- Task definition (e.g., modular arithmetic grokking)
- Model family (architecture, width/depth, optimizer, regularization)
- Training schedule and checkpoint cadence
- Seed sets (explore seeds vs held-out eval seeds)

### 1.2 Event definition (evaluability first)

Choose *one* primary event type (pre-registered):

- **E_jump**: test accuracy (or other generalization metric) exhibits a jump within a window.
- **E_plateau**: entry into a stable Φ₃-like regime (SC-1 persistence).
- **E_regime**: phase transition registered by PT-MSS (force/info/constraint co-occur within window).

**Default in v0.4**: `E_jump` (highest evaluability / least interpretive).

#### E_jump (default)

Let `m(t)` be a scalar metric (default: `test_acc`). Define a window size `W_event` and jump threshold `Δ_min`.

An event time `t*` is registered if:

- `m(t* + W_event) - m(t*) >= Δ_min`, and
- `t*` is the **first** time this holds (earliest detection rule).

---

## 2. Positive/negative labeling (must be pre-registered)

You are *not* classifying points; you are classifying **windows**.

### 2.1 Positive windows (early-warning horizon)

Define a warning horizon `H_pos` and a lead-time target `L_target`.

A window ending at time `t` is **positive** if:

- `t < t*` and `t* - t <= H_pos`.

Optional: “lead-time success” is counted only if alarm occurs at least `L_target` steps before `t*`.

### 2.2 Negative windows (safe gap)

Define a safe gap `Δ_safe`.

A window ending at time `t` is **negative** if:

- `t <= t* - Δ_safe`.

This prevents accidental “near-event negatives” from contaminating calibration.

---

## 3. Indicator interface

An indicator produces a scalar score per checkpoint (or per window):

- `s(t)` where higher means “higher risk” (orientation fixed in prereg).

Indicators may be:
- **dynamics** (CSD, VEI, curvature, autocorr),
- **process** (self-consistency disagreement, step instability),
- **judge/meta** (LLM-as-judge outputs, but must pass the same operational gates).
- **hierarchical_convergence** (HRM-inspired; requires internal-state observables; see addendum: `docs/benchmarks/gmb_v0_4/gmb_v0.4_addendum_hrm_indicator_family.md`).

---

## 4. Metric basket (the benchmark outputs)

GMB evaluates each indicator in **four layers** and then assigns a unified label.

### 4.1 Layer A — Discriminative content (ranking only)

Report:
- AUC
- AP (Average Precision)

**Rule**: Layer A never implies deployability.

### 4.2 Layer B — Operationality gate (hard requirement)

Define target FPR set:

- `F = {0.01, 0.05, 0.10}` (default)

For each target `f`:

1. Calibrate a threshold `τ_f` **only on negative windows**.
2. Compute achieved FPR `f_hat` on negative windows.

Pass criteria (default):

1. **FPR controllability**: at least `m_ok` targets satisfy

$$
|\hat{f} - f| \le \epsilon
$$

2. **No FPR floor**: the minimum achievable FPR is below `f_floor_max`:

$$
\min_{f \in F} \hat{f} \le f_{\text{floor\_max}}
$$

If Layer B fails, the indicator is **invalid for alarm** regardless of AUC/AP.

### 4.3 Layer C — Utility at operating points

For operating points (typically `f = 0.05` and `0.10`) report:

- `coverage@f`: fraction of events that receive at least one alarm in positive windows.
- `lead_time` distribution: first alarm time relative to `t*` (median/IQR and tails).
- `lead_time_success@f`: fraction of events warned at least `L_target` steps early.

### 4.4 Layer D — Robustness

Report sensitivity over:

- seeds (held-out eval seeds),
- window sizes `W` (small perturbations),
- smoothing parameters,
- sign flips (if the score orientation is ambiguous, declare and test both in **Explore**, but only one is allowed in **Lock**).

Robustness outputs:
- pass rate over the admissible family
- flip-rate (how often the final label changes under small perturbations)

---

## 5. Unified decision labels

Each indicator receives exactly one label:

- `SUPPORTED_FOR_ALARM`: Layer B passes, Layer C materially non-trivial, Layer D stable.
- `RANK_ONLY`: Layer A good, Layer B fails (e.g., FPR floor / uncontrollable calibration).
- `ESTIMATOR_UNSTABLE`: Layer B/C outcomes flip under small admissible perturbations.
- `INCONCLUSIVE`: insufficient event count or insufficient power under prereg boundary.
- `SCOPE_LIMITED`: works only under an explicit boundary condition; must state it.

---

## 6. Protocol discipline (Explore → Lock → Evaluate)

### 6.1 Explore
- Allowed: free feature search, window tuning, sign checks.
- Forbidden: claims about deployability.

### 6.2 Lock (preregistration)
Freeze:
- boundary, event definition, positive/negative windows,
- FPR targets + tolerances,
- operating points, reporting tables, success thresholds.

### 6.3 Evaluate
- Run only on held-out eval seeds.
- Report *all* indicators and all failures (including FPR floors).

---

## 7. Minimal “definition of done” (DoD)

A v0.4 run is acceptable only if:

1. Event count ≥ `N_event_min` (pre-registered; suggest ≥ 30 across seeds).
2. For each indicator, Layer B is computed and reported (even if it fails).
3. Coverage and lead-time are reported for each operating point (even if zero).
4. A single summary table exists (see result schema file).

---

## 8. Recommended tables (paper-ready)

### Table 1 — Operationality Gate Summary

| indicator | AUC | AP | controllability_pass | fpr_floor | ok_targets | label |
|---|---:|---:|:---:|---:|---:|---|

### Table 2 — Utility @ Operating Points

| indicator | FPR | coverage | lead_time_median | lead_time_IQR | lead_time_success |
|---|---:|---:|---:|---:|---:|

### Table 3 — Robustness

| indicator | family_size | pass_rate | label_flip_rate | notes |
|---|---:|---:|---:|---|

---

## 9. Notes for integrating Controlled Nirvana

GMB is a measurement benchmark. In a control setting (e.g., Emptiness Window), **only** indicators with `SUPPORTED_FOR_ALARM` are eligible to trigger authority suspension.

Recommended runtime behavior:
- If calibration health degrades (Layer B drift), switch to `ABSTAIN` / conservative gating rather than “trusting a broken ruler”.
