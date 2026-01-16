# Definitions and Assumptions

## FIT–Markov Sandbox Specialization

**Author**: Qien Huang
**Framework**: F-I-T (Force–Information–Time)
**Scope**: Finite-State Markov Chains
**License**: CC BY 4.0

---

## Purpose of This Document

This document serves three explicit purposes:

1. To **separate FIT primitives from their Markov-specialized realizations**.
2. To **state all mathematical assumptions explicitly**, preventing hidden condition shifts.
3. To provide a **reviewer-facing reference** clarifying what is claimed, what is proven, and what is *not* claimed.

This file is normative for the Markov sandbox and should be read alongside
`fit_markov_sandbox_short.md`.

---

## 1. Mathematical Setting

### 1.1 State Space

* $ \mathcal{S} $ denotes a **finite** state space.
* Cardinality: $ |\mathcal{S}| = n < \infty $.
* Time is discrete: $ t \in \mathbb{Z}_{\ge 0} $.

No continuous-state or continuous-time results are claimed in this specialization.

---

### 1.2 Markov Chain Definition

A (time-homogeneous) Markov chain $ { X_t } $ is defined by a transition matrix $ P $ such that:

$$
P(i,j) = \Pr(X_{t+1} = j \mid X_t = i)
$$

with the following assumptions:

* **Row-stochasticity**: $ \sum_j P(i,j) = 1 $ for all $ i $.
* **Irreducibility**: every state is reachable from every other state.
* **Aperiodicity**: the chain admits no deterministic cycling.

These assumptions ensure:

* existence of a **unique stationary distribution**,
* well-defined entropy rate and mixing time.

---

## 2. Hardening Path (Lazy Transition Family)

### 2.1 Definition

We define a one-parameter family of transition matrices:

$$
P_{\alpha} = (1 - \alpha) P + \alpha I
$$

where:

* $ \alpha \in [0,1) $ is the **hardening parameter**,
* $ I $ is the identity matrix.

---

### 2.2 Interpretation (Non-Normative)

* Increasing $ \alpha $ increases **self-transition probability**.
* This corresponds to increasing inertia, conservatism, or resistance to change.
* $ \alpha \to 1 $ represents a **frozen limit**, not an ergodic Markov chain.

No physical or ontological claim is made beyond this mathematical construction.

---

### 2.3 Preserved Properties

For all $ \alpha < 1 $:

* irreducibility is preserved,
* aperiodicity is preserved,
* the chain admits a unique stationary distribution $ \pi_{\alpha} $.

---

## 3. FIT Primitive Mapping (Specialization Layer)

This section defines how FIT primitives are instantiated **only within this sandbox**.

### 3.1 State (S)

**FIT primitive**: system configuration.

**Markov specialization**:

* Random variable $ X_t \in \mathcal{S} $,
* Together with the stationary distribution $ \pi_{\alpha} $ satisfying:

$$
\pi_{\alpha} = \pi_{\alpha} P_{\alpha}
$$

No claim is made that all FIT states are Markovian in general.

---

### 3.2 Information (I)

**FIT primitive**: uncertainty or information production per update.

**Markov specialization**: **entropy rate**.

$$
I(\alpha) := h(\alpha)
$$

with

$$
h(\alpha)
= H(X_{t+1} \mid X_t)
= \sum_{i \in \mathcal{S}} \pi_{\alpha}(i)\, H(P_{\alpha}(i,\cdot))
$$

Interpretation:

* $ h(\alpha) $ quantifies how much new uncertainty the system generates per step.
* Lower values indicate more constrained, predictable evolution.

---

### 3.3 Constraint (C)

**FIT primitive**: accumulated structural restriction on evolution.

**Markov specialization**: **predictive mutual information**.

$$
C(\alpha) := I(X_t ; X_{t+1})
$$

Under stationarity:

$$
C(\alpha) = H(\pi_{\alpha}) - h(\alpha)
$$

Notes:

* $ C(\alpha) $ is **not** an externally imposed constraint.
* It is an *emergent informational dependency* between consecutive states.

---

### 3.4 Time (T)

**FIT primitive**: characteristic temporal scale.

**Markov specialization**: **mixing time**.

$$
T(\alpha) := t_{\mathrm{mix}}(\varepsilon; P_{\alpha})
$$

Definition:

* $ t_{\mathrm{mix}} $ is the smallest $ t $ such that total variation distance to $ \pi_{\alpha} $ is below $ \varepsilon $.

In experiments, spectral quantities (e.g. SLEM) are used as proxies.

---

## 4. Special Structural Assumptions

### 4.1 Stationary Invariance vs. Monotonicity

For the lazy hardening family
$
P_{\alpha} = (1-\alpha)P + \alpha I
$
the stationary distribution is invariant for any finite, irreducible, aperiodic chain:
$\pi_{\alpha}=\pi$ for all $\alpha \in [0,1)$.
No doubly-stochastic assumption is required for this invariance.

However, monotonicity along the hardening path (e.g., $h(\alpha)$ non-increasing and $C(\alpha)$ non-decreasing for all $\alpha$) is **not guaranteed in general**.
The Markov papers therefore isolate monotonicity claims behind an explicit sufficient condition.

### 4.2 A Sufficient Condition (Self-Dominance)

If each row is self-dominant (for every $i$, $P(i,i) \ge P(i,j)$ for all $j$), then row entropies $H(P_{\alpha}(i,\cdot))$ are non-increasing in $\alpha$ (by majorization and Schur concavity), which implies monotone entropy-rate suppression and monotone constraint accumulation.

---

### 4.3 What Is *Not* Assumed

The following are **not required**:

* reversibility (unless stated),
* detailed balance,
* continuous-time limits,
* infinite or continuous state spaces,
* optimal control or reward structure.

---

## 5. Nirvana (Specialized Definition)

Within this Markov sandbox, **nirvana** is defined *purely mathematically*.

### Definition (Markov-Specialized Nirvana)

A system approaches nirvana if, along the hardening path:

$$
h(\alpha) \to 0
\quad \text{and} \quad
T(\alpha) \to \infty
$$

Interpretation:

* no new information is generated,
* the system becomes effectively frozen,
* initial conditions are never forgotten in finite time.

No metaphysical or normative interpretation is implied.

---

## 6. Scope and Non-Claims

This specialization **does not claim** that:

* FIT universally reduces to Markov dynamics,
* all real systems admit a lazy hardening path,
* nirvana is desirable or optimal,
* entropy minimization is a global law.

The sole claim is:

> **Within a standard, well-defined Markovian sandbox, FIT-style constraint accumulation can be rigorously formalized and partially proven.**

---

## 7. Relationship to the Full FIT Framework

This document provides:

* a **proof-of-possibility**, not a proof of universality,
* a **structural anchor**, not a full theory,
* a **calibration point** for future generalizations.

All extensions beyond this sandbox must restate assumptions explicitly.

---

## 8. Recommended Citation Practice

When citing results from this sandbox, authors should specify:

> “FIT, specialized to finite-state Markov chains under lazy hardening, as defined in Q. Huang (2026).”

This avoids overgeneralization beyond the proven scope.

---

## Closing Remark

This definitions file is intentionally conservative.

Its function is not to persuade, but to **prevent category errors**.

The FIT framework can only harden if its boundaries are explicit.


