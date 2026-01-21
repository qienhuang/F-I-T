# Monitorability in the FIT Framework
## When Information Exists but Observation Fails

**Status:** Core concept (derived from empirical diagnosis)  
**Applies to:** Learning systems, self-evolving agents, organizational and governance dynamics  
**Primary evidence:** [`experiments/grokking_hard_indicators_v0_2/RESULTS_v0.2_v0.2.1.md`](../../experiments/grokking_hard_indicators_v0_2/RESULTS_v0.2_v0.2.1.md)

---

## 1. Motivation

The FIT framework emphasizes **Information (I)** and **Constraint (C)** as the primary drivers of system evolution.  
However, empirical results from grokking experiments reveal a critical missing dimension:

> Systems may contain usable information while being **operationally unmonitorable**.

In such regimes, signals can rank states correctly (high AUC) yet cannot be converted into actionable alarms under realistic risk constraints (e.g., low false-positive rates).

This document formalizes this phenomenon as **monitorability** and integrates it into the FIT core.

---

## 2. Definition: Monitorability

**Monitorability** refers to the ability to convert internal signals into **operationally valid interventions** under explicit risk constraints.

We treat monitorability as a third axis alongside Information and Constraint, operationalized via **operationality** \(O(t)\).

\[
M(t) = (I(t), C(t), O(t))
\]

where:

- \(I(t)\): Information — discriminative signal content (e.g., ranking ability).
- \(C(t)\): Constraint — system solvability, coherence, and consistency.
- \(O(t)\): Operationality — the feasibility of thresholded action under risk bounds.

A system is **monitorable** at time \(t\) if and only if \(O(t)\) is non-degenerate (i.e., the alarm objective has at least one feasible operating point under the stated risk budget).

---

## 3. Operationality \(O(t)\)

Operationality is not a scalar but a **minimal vector of necessary conditions** for monitoring.

### 3.1 Components of Operationality

We define three operational sub-criteria:

1. **FPR Controllability**
   - Does there exist a threshold \(\theta\) such that:
     \[
     \Pr(\text{alarm} \mid \text{no event}) \approx \text{target FPR}
     \]
   - Empirically: achieved FPR tracks target FPR within tolerance.

2. **Coverage under Risk Budget**
   - At a fixed FPR (e.g., 0.05 or 0.10), what fraction of true events are detected?
   - Zero or near-zero coverage implies operational failure.

3. **Lead-Time Stability**
   - Conditional on detection, is the warning window non-trivial and stable across runs?

We write:

\[
O(t) = \big(\text{FPR-control},\ \text{coverage@FPR},\ \text{lead-time stability}\big)
\]

Failure of any component renders the signal **operationally invalid**, regardless of \(I(t)\).

---

## 4. Monitorability Boundary

### 4.1 Definition

A **monitorability boundary** is a region in system evolution where:

- Information exists: \(I(t) > 0\)
- But operationality collapses: \(O(t) \to \text{degenerate}\)

In this regime:
- Scores may achieve high AUC (ranking signal present),
- Yet no threshold yields acceptable false-positive behavior.

This boundary is **not noise** and **not lack of data**.  
It is a structural property of the system’s trajectory.

---

### 4.2 Empirical Evidence (Grokking)

In grokking experiments:

- Certain indicators achieved higher AUC with inverted sign.
- However, achieved FPR was fixed at ~0.44 for all thresholds.
- Coverage appeared high but was entirely driven by false positives.

See also the explicit tradeoff sweep: [`experiments/grokking_hard_indicators_v0_2/results/v0.3_A2_fpr_tradeoff.md`](../../experiments/grokking_hard_indicators_v0_2/results/v0.3_A2_fpr_tradeoff.md).

Formally:

\[
\exists\, s(t): \text{AUC}(s) > 0.5 \quad \wedge \quad \nexists\, \theta: \text{FPR}(\theta) < \epsilon
\]

This constitutes **monitorability failure**.

---

## 5. AUC ≠ Alarm Usability

The grokking results establish a general decoupling:

> **Ranking performance does not imply alarm usability.**

AUC measures discriminative ordering, not operational feasibility.  
Alarm systems require **calibratable monotonicity** under constraint.

Thus:

- AUC is a sufficient statistic for ranking tasks,
- but an **insufficient statistic** for monitoring and governance.

This distinction is central for FIT applications in safety, governance, and control.

---

## 6. Monitorability and Hardening

### 6.1 Hardening Beyond State Space

Traditional notions of hardening focus on:

- Reduced flexibility in state transitions,
- Increased constraint accumulation.

Monitorability adds a second-order effect:

> **As systems harden, the space of valid observations can collapse before the space of actions does.**

That is, the system becomes:
- difficult to correct **and**
- difficult to observe in time.

---

### 6.2 Consequence for Governance

In governance-oriented systems (AI agents, organizations, institutions):

- Control depends on timely observation.
- Loss of monitorability implies loss of corrective leverage.

Thus, preventing premature hardening is not only about adaptability, but also about preserving **observability**.

---

## 7. Methodological Implications

### 7.1 Evaluation Discipline

The grokking experiments suggest a general evaluation order:

1. **Evaluability** — are events well-defined and observable?
2. **Operationality** — can signals be used under risk constraints?
3. **Performance** — only then compare accuracy or AUC.

Skipping step (2) leads to false confidence.

---

### 7.2 Research Protocol

We recommend a three-phase discipline for monitoring research:

- **Explore**: search indicators and parameters freely.
- **Lock**: freeze definitions, thresholds, and operating points.
- **Evaluate**: assess on held-out trajectories only.

This enforces temporal separation and prevents retrospective tuning.

---

## 8. Implications for FIT-Controlled Systems

The existence of monitorability boundaries implies:

- Improving indicators alone is insufficient.
- Systems must be **controlled** to remain in monitorable regimes.

This motivates FIT-guided control strategies that:
- regulate information–constraint balance,
- slow hardening near phase transitions,
- and preserve operational observability.

---

## 9. Summary

**Key Claim (FIT Core):**

> Monitorability is a fundamental property of evolving systems, distinct from information and constraint.  
> Systems can cross monitorability boundaries where information persists but operational observation fails.

Preserving monitorability is therefore a first-class objective in the design, control, and governance of complex adaptive systems.

---

## 10. Relation to FIT Propositions

This document supports and refines existing FIT propositions:

- **P7 (Information Saturation):** Monitorability may collapse before information saturates.
- **P11 (Phase Transitions):** Monitorability boundaries often precede or coincide with phase transitions.

We recommend treating monitorability as a derived but essential axis in all FIT-based analyses.

---
