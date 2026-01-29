# Phase-Conditioned Constraint Coherence in a Real-World Mobility System

## An EST-Compliant Tier-2 Evaluation on NYC TLC (2019–2023)

---

## Abstract

Real-world socio-technical systems are rarely stationary.
This poses a fundamental challenge for empirical evaluation of structural indicators that assume estimator coherence across time.

We present a Tier-2 empirical study applying the Force–Information–Time (FIT) framework with Estimator Selection Theory (EST) to New York City Taxi & Limousine Commission (TLC) trip data from 2019–2023. We evaluate whether a family of constraint estimators exhibits sufficient coherence to support interpretation of Information/Constraint (I/C) regime signals (P11).

We find that **pooled evaluation across the full period fails the coherence gate**, while **all per-year windows pass**, as do preregistered **pre-COVID and post-COVID macro windows**. This pattern is consistent with **structural regime shifts** and a Simpson’s-paradox–like level shift, rather than estimator noise.

We formalize this outcome as a **scope-limited success** (`OK_PER_YEAR`, `OK_PER_WINDOW`), preserving the negative pooled result. The study demonstrates that, under EST discipline, *failure of pooled coherence is itself an interpretable signal of regime heterogeneity*, and that meaningful structural interpretation requires explicit phase conditioning.

---

## 1. Introduction

Many empirical analyses of complex systems implicitly assume that structural indicators are stable under aggregation. In non-stationary systems—such as urban mobility across the COVID-19 shock—this assumption often fails silently.

The FIT framework proposes that regime changes can be detected via interactions between **Information** and **Constraint**, but only when estimators form a coherent family under an explicit scope. Estimator Selection Theory (EST) makes this requirement operational by enforcing preregistered coherence gates and explicit failure labeling.

This paper asks a narrow but fundamental question:

> *Under what temporal scopes does a constraint estimator family remain coherent in a real-world, regime-shifting system?*

We deliberately treat coherence failure as a first-class outcome, not an error to be patched.

---

## 2. Data and System Boundary

### 2.1 Dataset

* **Source**: NYC Taxi & Limousine Commission (TLC) Yellow Taxi Trip Records
* **Format**: Monthly Parquet files
* **Coverage**: January 2019 – December 2023
* **Scale**: ~60 files, several billion trips aggregated daily

### 2.2 Aggregation

Raw trips are aggregated into **daily system states**, computing spatial distributions and operational metrics. No trip-level causal inference is attempted.

### 2.3 Boundary Declaration

* **Included**: Yellow taxi operations within NYC
* **Excluded**: Ride-hailing platforms, policy intent, demographic attribution
* **Interpretation domain**: structural dynamics only (not demand forecasting)

---

## 3. Estimator Specification (Pre-registered)

All estimators, thresholds, and evaluation rules were preregistered and frozen prior to analysis.

### 3.1 Information Estimator (I)

* **Pickup entropy**
  Shannon entropy of pickup-zone distribution
  Interpreted as spatial dispersion of demand

### 3.2 Constraint Estimator Family (C)

* **Congestion**: `log1p(minutes_per_mile)`
* **Scarcity**: `-log(trip_count)`
* **Concentration**: top-5 pickup zone share

These estimators are intended to capture complementary aspects of operational constraint.

### 3.3 Coherence Gate (EST)

* **Metric**: Spearman rank correlation
* **Threshold**: ρ ≥ 0.6
* **Rule**:

  * If coherence fails → label `ESTIMATOR_UNSTABLE`
  * Interpretation is forbidden under that scope

No estimator substitution or threshold adjustment is permitted post-hoc.

---

## 4. Evaluation Protocol

We evaluate coherence under three **explicitly declared scopes**:

### 4.1 Pooled Scope (2019–2023)

All data treated as a single regime.

### 4.2 Year-Windowed Scope (v1.5)

Independent coherence tests for each calendar year.

### 4.3 Macro-Windowed Scope (v1.6)

Two preregistered macro regimes:

* **Pre-COVID**
* **Post-COVID**

These windows are declared as *structural regime candidates*, not statistical convenience slices.

---

## 5. Results

### 5.1 Pooled Evaluation

* **Observed**: Spearman ρ = 0.543
* **Threshold**: ρ ≥ 0.6
* **Outcome**: **FAIL**

**Label**: `ESTIMATOR_UNSTABLE (pooled)`

No P11-level interpretation is permitted under pooled aggregation.

---

### 5.2 Year-Windowed Evaluation

* **Observed**: All individual years pass coherence gate
* **Outcome**: **PASS per year**

**Label**: `OK_PER_YEAR`

Interpretation is valid **within-year only**.

---

### 5.3 Macro-Windowed Evaluation

| Window     | Spearman ρ | Result |
| ---------- | ---------- | ------ |
| Pre-COVID  | 0.928      | PASS   |
| Post-COVID | 0.601      | PASS   |
| Pooled     | 0.543      | FAIL   |

**Label**: `OK_PER_WINDOW`

Each macro regime is internally coherent; cross-regime aggregation is invalid.

---

## 6. Interpretation

### 6.1 Why pooled coherence fails

The 2019–2023 period spans distinct macro regimes with different constraint structures. Aggregation across these regimes induces a level shift analogous to Simpson’s paradox.

Under EST, pooled coherence failure is therefore **diagnostic**, not pathological.

### 6.2 Meaning of scope-limited success

The `OK_PER_YEAR` and `OK_PER_WINDOW` labels indicate:

* Constraint estimators form a coherent ordinal family **within a regime**
* The same estimators do **not** form a single family across regimes
* Interpretation must be phase-conditional

This is not post-hoc rescue, but explicit scope declaration.

### 6.3 Implications for FIT P11

These results support a refined reading of P11:

> Information/Constraint regime signals are interpretable within phase-consistent windows, and coherence failure under aggregation can itself signal regime heterogeneity.

---

## 7. Non-Claims and Limits

This study does **not** claim:

* causal explanation of COVID impacts
* predictive regime forecasting
* universal validity of the estimator family
* cross-year monotonic constraint dynamics

All claims are strictly scope-bound.

---

## 8. Reproducibility

All pipelines, preregistration files, outputs, and negative results are publicly archived. Outcome labels are explicit and machine-readable.

---

## 9. Conclusion

The NYC TLC system does not admit a single coherent constraint family over 2019–2023.
It does admit coherent families within declared temporal regimes.

This demonstrates that **EST-compliant failure handling** enables real-world systems to be interpreted without overreach, and that phase conditioning is essential for structural analysis of non-stationary data.


