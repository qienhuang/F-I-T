# Controlling Monitorability in the FIT Framework
## How to Keep Systems in a Monitorable Regime

**Status:** Core control concept  
**Depends on:** [`monitorability.md`](./monitorability.md)  
**Primary evidence:** [`experiments/grokking_hard_indicators_v0_2/RESULTS_v0.2_v0.2.1.md`](../../experiments/grokking_hard_indicators_v0_2/RESULTS_v0.2_v0.2.1.md)

---

## 1. Problem Statement

Monitorability is not guaranteed.

Empirical results show that evolving systems can enter regimes where:

- Information exists (signals discriminate in ranking),
- but alarms are unusable (false positives are uncontrollable).

Once this occurs, **late correction becomes low-leverage**, regardless of downstream decision quality.

Therefore, a central control problem emerges:

> **How can a system be controlled so that it remains monitorable?**

This document formalizes **monitorability-preserving control** as a first-class objective in the FIT framework.

---

## 2. Control Objective

### 2.1 Monitorability as a Control Target

Let:

\[
M(t) = (I(t), C(t), O(t))
\]

where \(O(t)\) denotes operationality (FPR controllability, coverage, lead-time stability).

The control objective is **not** to maximize \(I\) or minimize \(C\) alone, but to ensure:

\[
O(t) \succ 0 \quad \text{for all } t \text{ in the operational horizon}
\]

That is, the system must remain in a regime where signals can be **converted into action under risk constraints**.

---

### 2.2 Control Failure Mode

A system is **control-failed** if:

\[
I(t) > 0 \quad \wedge \quad O(t) \to 0
\]

This corresponds to **late awareness**: the system knows, but cannot act in time.

---

## 3. What Must Be Controlled (Not What Is Observed)

A critical lesson from grokking is:

> **Monitorability does not fail because indicators are bad.  
> It fails because the system trajectory enters a regime where indicators lose calibratability.**

Thus, the object of control is **not the indicator**, but the **system dynamics**.

### 3.1 Control Variables

Across learning and organizational systems, the following variables directly affect monitorability:

1. **Constraint Accumulation Rate**
   - Rapid hardening compresses the space of usable thresholds.
2. **Information Production Rate**
   - Excessively sharp signals produce premature saturation.
3. **Trajectory Curvature**
   - Sudden regime acceleration induces non-monotonic signals.

These correspond to FIT primitives \(C(t)\), \(I(t)\), and their time derivatives.

---

## 4. Monitorability-Preserving Control Laws

### 4.1 First-Order Control: Constraint Slope Limiting

A minimal control law is to bound the rate of constraint accumulation:

\[
\frac{dC}{dt} \le \kappa_C
\]

where \(\kappa_C\) is a system-specific limit beyond which observability degrades.

**Interpretation:**  
Do not allow the system to “lock in” faster than it can be monitored.

---

### 4.2 Second-Order Control: Curvature Smoothing

Near phase transitions, the **second derivative** of system state dominates monitorability loss.

Control target:

\[
\left|\frac{d^2 C}{dt^2}\right| \le \kappa_{C2}
\]

This prevents abrupt regime shifts that cause indicator inversion or FPR floors.

---

### 4.3 Time-Scale Separation

Monitorability requires that **observation adapts faster than structure hardens**.

Formal requirement:

\[
\tau_{\text{observation}} \ll \tau_{\text{hardening}}
\]

If violated, the system becomes opaque before alarms can stabilize.

---

## 5. Event-Aware Control

Monitorability loss often occurs **before** a visible phase transition.

Thus, control must be **event-aware**, not purely reactive.

### 5.1 Monitorability Events

Define monitorability-threatening events:

- Rapid rise in indicator autocorrelation (critical slowing down),
- Variance explosion in state signals,
- FPR floor detection during calibration attempts.

These events trigger **preemptive control**, not alarm issuance.

---

### 5.2 Preemptive Actions

Upon detecting monitorability risk:

- Slow constraint tightening,
- Inject controlled noise or diversity,
- Delay irreversible updates,
- Increase observation window resolution.

These actions **do not optimize performance**, but preserve observability.

---

## 6. Control vs Alarm: A Fundamental Distinction

A key principle:

> **Alarms operate within a regime.  
> Control determines whether such a regime exists.**

Once monitorability is lost, alarms are already too late.

Therefore:

- **Alarm systems require monitorability.**
- **Monitorability requires control.**

---

## 7. Grokking as a Proof-of-Concept (for failure modes)

In grokking:

- We observe regimes where ranking metrics can improve, but alarm operation becomes infeasible under strict low-FPR constraints (FPR floors / calibration degeneracy).
- This provides a clean empirical example that **monitorability can fail structurally**, not merely due to noise or insufficient data.

This motivates monitorability-preserving control as a real requirement to test directly in future controlled trajectories (e.g., explicit hardening-rate limits, “emptiness windows”, or other FIT-guided interventions).

---

## 8. Implications for FIT-Controlled Systems

Monitorability-preserving control implies a shift in design priorities:

| Traditional Objective | Monitorability-Aware Objective |
|----------------------|--------------------------------|
| Maximize performance | Preserve observability |
| Optimize indicators | Regulate system trajectory |
| React to alarms | Prevent alarm invalidation |

This reframes safety, governance, and long-horizon control as **trajectory management problems**.

---

## 9. Summary

**Core Claim:**

> Monitorability is a fragile property that must be actively preserved by control.  
> Systems that harden faster than they can be observed will inevitably outrun their alarms.

In FIT, this elevates monitorability-preserving control to a primary objective alongside performance and efficiency.

---

## 10. Relation to FIT Propositions

This document strengthens and extends existing FIT propositions:

- **P7 (Information Saturation):** Monitorability may collapse before information saturates.
- **P11 (Phase Transitions):** Monitorability loss can precede phase transitions.
- **Derived Control Principle:** Preserve \(O(t)\) by regulating \(dC/dt\) and trajectory curvature.

---

## 11. Design Checklist (Operational Use)

Before deploying any evolving system:

- [ ] Is the system monitorable under target risk budgets?
- [ ] Are constraint growth rates bounded?
- [ ] Are regime shifts smoothed?
- [ ] Are monitorability events tracked?
- [ ] Is control applied before alarms fail?

If any answer is “no”, alarms cannot be trusted.

---

