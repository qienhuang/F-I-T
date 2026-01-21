# Monitorability-Preserving Control Loop
## A FIT Control Loop That Keeps Systems in a Monitorable Regime

**Status:** Core algorithmic artifact  
**Depends on:** [`monitorability.md`](./monitorability.md), [`monitorability_control.md`](./monitorability_control.md)  
**Canonical example:** [`examples/monitorability_grokking.md`](../../examples/monitorability_grokking.md)

---

## 1. Purpose

This control loop prevents a system from entering regimes where:

- signals may retain ranking information (AUC > 0.5),
- but alarms become unusable due to calibration failure (e.g., FPR floors).

The objective is to keep the system inside a **monitorable regime**, where operationality \(O(t)\) remains non-degenerate.

---

## 2. Control Objects and Interfaces

### 2.1 System Under Control

The loop applies to any evolving system with:

- a state trajectory (learning dynamics, organizational dynamics, agent behavior),
- a generator/actor that changes the system (training updates, policy updates),
- an observer that produces signals.

Examples:
- LLM training (grokking),
- self-evolving agents (Dr. Zero-style loops),
- organizations under transformation.

---

### 2.2 Inputs (Observations)

At discrete checkpoints \(t\), we assume the availability of:

1. **State signals** \(Y(t)\): continuous metrics (loss, accuracy, gaps, etc.)
2. **Event definition** \(E\): a regime-shift event (e.g., jump-based grokking event)
3. **Candidate detectors** \(S_k(t)\): indicator time series (e.g., CSD = critical slowing down / lag-1 autocorr; VEI = variance explosion index)
4. **Operationality probes** \(O(t)\):
   - FPR controllability (achieved FPR vs target FPR)
   - coverage@FPR
   - lead-time stability

We treat FPR controllability as a **validity gate**.

---

### 2.3 Outputs (Control Actions)

The control loop emits actions that change the system trajectory:

- **Constraint slope limiting**: slow updates / tighten constraints more gradually
- **Information injection**: increase diversity / noise / exploration
- **Time-scale separation**: slow proposer updates relative to solver
- **Event-aware throttling**: apply conservative modes near monitorability risk

Actions must be bounded.

---

## 3. Control State and Core Variables

We define:

- Information proxy \(I(t)\) (task diversity, entropy, etc.)
- Constraint proxy \(C(t)\) (solvability/verifiability/consistency, etc.)
- Operationality \(O(t)\) (alarm usability vector)

Monitorability is:

\[
M(t) = (I(t), C(t), O(t))
\]

The key invariant we aim to preserve is:

\[
O(t) \succ 0 \quad \text{(non-degenerate)}
\]

---

## 4. Validity Gate: Operationality First

Before any indicator is used for alarm or decision-making, it must pass:

### 4.1 FPR Controllability Test

Given a target FPR set \(\mathcal{F}=\{0.05,0.10,0.15\}\), define:

- For each \(f \in \mathcal{F}\), calibrate threshold \(\theta_f\) on negative windows.
- Compute achieved FPR \(\hat{f}\).

A detector is **valid** if at least \(m\) targets satisfy:

\[
|\hat{f}-f| \le \epsilon
\]

and if the detector does not exhibit an FPR floor:

\[
\min_f \hat{f} \le f_{\max}
\]

If invalid, the detector is forbidden for alarm usage.

---

## 5. Event-Aware Monitorability Control Policy

Monitorability loss often precedes visible phase transitions.

We define monitorability-risk events:

- **FPR floor detected** (calibration degeneracy)
- **CSD spike** (lag-1 autocorr surge)
- **VEI spike** (variance ratio surge)
- **trajectory curvature jump** (rapid \(dC/dt\) or \(d^2C/dt^2\))

These events trigger **preemptive control modes**.

---

## 6. Algorithm 1: Monitorability-Preserving Control Loop

### 6.1 High-level Procedure

1. Observe system at checkpoint \(t\).
2. Compute \(I(t)\), \(C(t)\), and candidate detector series \(S_k(t)\).
3. Probe operationality \(O(t)\) via FPR controllability and coverage estimates.
4. If monitorability risk is detected, apply preemptive control actions.
5. Otherwise, proceed with normal updates.
6. Repeat.

---

### 6.2 Pseudocode (implementation-oriented)

```python
# Algorithm 1: Monitorability-Preserving Control Loop
#
# Inputs:
#   - system: evolving system (trainer / agent loop / organization simulator)
#   - detectors: list of detector objects producing score series
#   - fpr_targets: list of target FPRs for calibration tests
#   - validity: FPR controllability thresholds (eps, fpr_floor)
# Outputs:
#   - controlled system trajectory
#   - monitorability logs (I, C, O, actions)

def monitorability_control_loop(system, detectors, fpr_targets=(0.05, 0.10, 0.15),
                                eps=0.01, fpr_floor=0.20, min_targets_ok=2,
                                control_params=None):

    state = init_control_state()
    logs = []

    for t in range(system.max_checkpoints):

        # --- 1) Observe ---
        obs = system.observe(t)  # e.g., test_loss, test_acc, train_loss, task stats

        # --- 2) Compute I, C proxies (domain-specific) ---
        I_t = compute_information_proxy(obs, state)
        C_t = compute_constraint_proxy(obs, state)

        # --- 3) Update detectors (score series) ---
        scores = {}
        for det in detectors:
            scores[det.name] = det.score(obs, state)  # scalar at t (or None)

        # --- 4) Probe operationality O(t) ---
        # O1: FPR controllability on a rolling negative window
        validity_report = {}
        for det in detectors:
            achieved = []
            ok = 0
            for fpr in fpr_targets:
                theta = det.calibrate_threshold(state.neg_window(det), target_fpr=fpr)
                fpr_hat = det.estimate_fpr(state.neg_window(det), theta)
                achieved.append((fpr, fpr_hat))
                if abs(fpr_hat - fpr) <= eps:
                    ok += 1

            fpr_min = min(fpr_hat for _, fpr_hat in achieved) if achieved else 1.0
            valid = (ok >= min_targets_ok) and (fpr_min <= fpr_floor)
            validity_report[det.name] = {
                "valid": valid,
                "achieved_fpr": achieved,
                "fpr_min": fpr_min,
                "ok_targets": ok,
            }

        # O2/O3: coverage and lead-time stability (estimated / tracked)
        O_t = compute_operationality(validity_report, state)

        # --- 5) Detect monitorability risk events ---
        risk = detect_monitorability_risk(
            I_t=I_t,
            C_t=C_t,
            scores=scores,
            validity=validity_report,
            state=state
        )

        # --- 6) Choose control mode ---
        if risk["fpr_floor_detected"] or risk["degenerate_detector"]:
            # Preemptive: prevent alarm invalidation
            actions = {
                "mode": "monitorability_recovery",
                "slow_hardening": True,
                "inject_diversity": True,
                "increase_observation_resolution": True,
                "throttle_irreversible_updates": True,
            }
        elif risk["near_phase_transition"]:
            # Preemptive: smooth curvature and slow updates
            actions = {
                "mode": "pre_transition_smoothing",
                "limit_dC_dt": True,
                "limit_d2C_dt2": True,
                "reduce_update_gain": True,
                "increase_eval_frequency": True,
            }
        else:
            # Normal operation
            actions = {"mode": "normal"}

        # --- 7) Apply actions to system ---
        system.apply_control(actions, control_params)

        # --- 8) Step system forward ---
        system.step()

        # --- 9) Update control state and logs ---
        state.update(obs=obs, I=I_t, C=C_t, scores=scores, validity=validity_report, actions=actions)
        logs.append({
            "t": t,
            "I": I_t,
            "C": C_t,
            "scores": scores,
            "validity": validity_report,
            "O": O_t,
            "actions": actions
        })

    return system, logs
```

---

## 7. Notes on Practical Instantiation

### 7.1 What counts as “negative windows”?

For calibration, we define “negative” as checkpoints sufficiently far from the event horizon:

* For grokking: checkpoints before the jump window (pre-event)
* For agents: states before irreversible actions
* For organizations: periods without identified regime-shift events

This definition must be frozen in preregistration.

---

### 7.2 Why this loop is FIT-consistent

* It treats **monitorability** as an explicit control objective.
* It controls **trajectory-level dynamics** (constraint slope, curvature, timescales).
* It enforces temporal discipline (probe → decide → act) and avoids retrospective tuning.

---

## 8. Minimal Acceptance Criteria (DoD)

A system is considered “monitorability-preserving” if:

1. No detector used for alarms violates FPR controllability in Phase B.
2. Coverage@FPR=0.10 is materially higher than baseline (under same boundary).
3. Lead-time distribution remains non-trivial and stable across seeds.
4. Monitorability risk events reduce in frequency over training (or are bounded).

---

## 9. Summary

This loop formalizes a core FIT principle:

> **Control creates monitorability.**
> Alarms operate within a regime; control determines whether that regime exists.

By explicitly probing operationality and acting preemptively to preserve it, the system avoids monitorability boundaries that would otherwise make correction too late.

---
