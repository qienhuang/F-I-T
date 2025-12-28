# EST Equivalence & Coherence Report (Template)

This file is a fill-in template for declaring **estimator equivalence requirements** (ordinal / metric / topological) and reporting **P10-style coherence** results under FIT v2.4 Estimator Selection Theory (EST).

Use together with `est_preregistration_template.yaml`. If this report conflicts with the preregistration, treat it as a deviation and document it in **Section 7**.

---

## 0) Quick Checklist

- [ ] Study metadata filled (ID, system, repo commit).
- [ ] Task types declared (ordinal / metric / topological).
- [ ] Equivalence requirement declared per estimator used for each task.
- [ ] Coherence gate thresholds pre-registered (or explicitly marked as exploratory).
- [ ] Pairwise coherence results reported (including failures).
- [ ] Gate decision recorded (pass/fail) and interpretation policy applied.
- [ ] Deviations and negative results recorded.

---

## 1) Study Metadata

- **Study ID**: `TODO` (must match preregistration)
- **Title**: TODO
- **FIT version(s)**: TODO (e.g., v2.3; v2.4-draft EST)
- **System / dataset**: TODO
- **Boundary / closure** $ \mathcal{B} $ : TODO
- **State representation** $ S_t $ : TODO
- **Measurement window** $ W $ : TODO (window, stride, burn-in)
- **Repository URL**: TODO
- **Repository commit**: TODO (git SHA)
- **Preregistration file**: `TODO` (path)
- **Report date (UTC)**: `YYYY-MM-DDTHH:MM:SSZ`
- **Authors / analysts**: TODO

---

## 2) Task Typing (What Structure Must Be Preserved?)

In EST, *the same estimator may be admissible for one task type but inadmissible for another*. Declare each claim as one of:

- **Ordinal**: trend / monotonicity / ranking claims
- **Metric**: threshold / critical-point / scale-stability claims
- **Topological**: regime structure / morphology / phase-transition signature claims

### 2.1 Task Inventory

| Task ID | Task type | Claim (one sentence) | Primary outcome(s) | Notes |
|---|---|---|---|---|
| T1 | ordinal \| metric \| topological | TODO | TODO | TODO |

### 2.2 Required Equivalence Level Per Task

| Task type | Minimum equivalence requirement | Typical gate(s) |
|---|---|---|
| ordinal | ordinal (order-preserving) | Spearman $ \rho $ , Kendall $ \tau $ |
| metric | metric (threshold / slope stability) | event-time alignment, calibrated residuals |
| topological | topological (event/morphology stability) | change-point agreement, regime consistency; optional TDA |

---

## 3) Equivalence Declarations (A8)

Declare equivalence requirements for each estimator used in the study. If you use multiple estimators for the same primitive (e.g., multiple $ \hat{C} $ ), declare each one and the equivalence requirement between them.

### 3.1 Equivalence Notions (Reference)

#### (E1) Ordinal equivalence (order-preserving)

Two estimators $ \hat{X}_1(t) $ and $ \hat{X}_2(t) $ are ordinally equivalent if there exists a strictly monotone function $ f $ such that:

$$
\hat{X}_2(t) \approx f(\hat{X}_1(t))
$$

up to declared noise tolerance and within the declared regime of interest.

#### (E2) Metric equivalence (threshold / scale stability)

For threshold claims (e.g., "transition at ( $ C = C^\* $ )"), monotone rescaling is insufficient. A practical MVP definition: after a pre-registered calibration map $ g $ (often affine or monotone regression), threshold event-times and local slopes agree within tolerance:

$$
|t^\*_1 - t^\*_2| \le \Delta t_{\max},
\quad
\left|\frac{d}{dt}g(\hat{X}_2(t)) - \frac{d}{dt}\hat{X}_1(t)\right| \le \epsilon
$$

in the declared regime.

#### (E3) Topological equivalence (event / morphology preservation)

For morphology / regime-structure claims, what must be preserved is the event structure (regime partition, ordering, and transition locations) rather than numeric scale.

MVP operational definition: under pre-registered smoothing + segmentation rules, the detected regime partition agrees within tolerance across estimators.

Optional stronger definition: compare sublevel-set filtrations induced by $ \hat{X} $ via persistent homology and require barcode similarity under declared metrics.

---

### 3.2 Estimator Declaration: Force $ \hat{F} $

- **Estimator ID**: TODO
- **Operational definition**: TODO
- **Implementation reference**: TODO (file / function / version)
- **Used for tasks**: TODO (e.g., T1, T3)
- **Equivalence requirement level**: ordinal \| metric \| topological
- **Invariances claimed**: TODO (e.g., translation, rotation, monotone transform invariance)
- **Allowed transformations**: TODO (e.g., strictly monotone $ f $ only; affine only; bi-Lipschitz)
- **Calibration map (if any)** $ g $ : TODO
- **Tolerance(s)**: TODO (e.g., $ \epsilon $ , $ \Delta t_{\max} $ )
- **Notes / scope limits**: TODO

### 3.3 Estimator Declaration: Constraint $ \hat{C} $

- **Estimator ID**: TODO
- **Operational definition**: TODO
- **Implementation reference**: TODO (file / function / version)
- **Used for tasks**: TODO
- **Equivalence requirement level**: ordinal \| metric \| topological
- **Invariances claimed**: TODO
- **Allowed transformations**: TODO
- **Calibration map (if any)** $ g $ : TODO
- **Tolerance(s)**: TODO
- **Notes / scope limits**: TODO

### 3.4 Estimator Declaration: Information $ \hat{I} $

- **Estimator ID**: TODO
- **Operational definition**: TODO
- **Implementation reference**: TODO (file / function / version)
- **Used for tasks**: TODO
- **Equivalence requirement level**: ordinal \| metric \| topological
- **Invariances claimed**: TODO
- **Allowed transformations**: TODO
- **Calibration map (if any)** $ g $ : TODO
- **Tolerance(s)**: TODO
- **Notes / scope limits**: TODO

---

## 4) Coherence Gate Specification (P10, Task-Typed)

### 4.1 What Is Being Cohered?

- **Primitive(s)**: TODO (e.g., multiple $ \hat{C} $ estimators)
- **Estimator set**: TODO (list each estimator ID)
- **Regime(s) of interest**: TODO (time range, burn-in, plateau window, etc.)

### 4.2 Gate Metrics and Thresholds (Pre-Registered)

Fill the thresholds you committed to in preregistration. If exploratory, mark explicitly.

#### Ordinal gate (rank coherence)

- Spearman $ \rho_{\min} $ : TODO
- Kendall $ \tau_{\min} $ : TODO
- Aggregation rule across pairs: TODO (e.g., median across pairs)

#### Metric gate (event + scale coherence)

- Threshold alignment: $ \Delta t_{\max} $ = TODO
- Slope error tolerance: $ \epsilon $ = TODO
- Calibrated residual (e.g., RMSE) max: TODO

#### Topological gate (event-structure coherence)

- Change-point tolerance: $ \Delta t_{\max} $ = TODO
- Same regime count required: true \| false
- Optional TDA barcode metric + threshold: TODO

### 4.3 Failure Policy

- If gate fails, action: `report_and_stop_interpretation` \| `continue_with_caveats`
- Notes: TODO

---

## 5) Coherence Results (Fill With Numbers)

### 5.1 Data Summary

- **Runs**: TODO (n, seeds)
- **Run length**: TODO
- **Preprocessing**: TODO (smoothing, detrending, segmentation rules)
- **Excluded runs / segments**: TODO (with reasons)

### 5.2 Pairwise Coherence Table (Recommended)

| Primitive | Estimator 1 | Estimator 2 | Task type | Metric | Value | Threshold | Pass? | Notes |
|---|---|---|---|---|---:|---:|---|---|
| C | TODO | TODO | ordinal | Spearman $ \rho $ | TODO | TODO | TODO | TODO |
| C | TODO | TODO | ordinal | Kendall $ \tau $ | TODO | TODO | TODO | TODO |
| C | TODO | TODO | metric | threshold alignment $ \lvert t^\*_1 - t^\*_2\rvert $ | TODO | TODO | TODO | TODO |
| C | TODO | TODO | topological | change-point $ \Delta t $ | TODO | TODO | TODO | TODO |

### 5.3 Gate Decision Summary

- **Ordinal gate**: PASS \| FAIL (rule: TODO)
- **Metric gate**: PASS \| FAIL (rule: TODO)
- **Topological gate**: PASS \| FAIL (rule: TODO)

### 5.4 Minimal Interpretation Note

If coherence gates are used as prerequisites for interpreting other propositions, record the allowed interpretation status:

- Interpretable propositions: TODO
- Blocked (due to failed gate): TODO
- Caveated interpretation: TODO

---

## 6) Machine-Readable Summary (Optional)

If you also maintain a YAML/JSON registry, paste a machine-readable summary here for easy copy into a registry entry.

```yaml
study_id: TODO
commit: TODO
equivalence_requirement:
  tasks:
    - task_id: T1
      task_type: ordinal
      level: ordinal
coherence_gate:
  ordinal:
    spearman_min: TODO
    kendall_min: TODO
  results:
    - primitive: C
      estimator_1: TODO
      estimator_2: TODO
      metric: spearman_rank
      value: TODO
      pass: TODO
gate_decision:
  ordinal: PASS # or FAIL
```

---

## 7) Deviations, Failures, and Negative Results

### 7.1 Deviations From Preregistration

- TODO (what changed, when, and why)

### 7.2 Known Failure Modes / Diagnostics

- TODO (e.g., boundary mismatch, window sensitivity, estimator instability)

### 7.3 Negative Results (Must Report)

- TODO (failed gates, failed propositions, null results)

---

## 8) Attachments (What To Save in Repo)

- `TODO` raw data files / seeds list
- `TODO` derived time series (per estimator)
- `TODO` plots (correlation scatter, residuals, change-point overlays)
- `TODO` logs (stdout/stderr, environment, versions)
