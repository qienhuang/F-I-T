# Renormalization Lens for FIT (RG-Compatible, v2.x)

Status: core-adjacent lens (non-breaking)

Scope: multiscale evolving systems with explicit estimator tuples (EST)

Primitives used: F / I / T / C / Phase (Phi) only

Goal: treat “scale” as an explicit transformation, so that cross-scale claims become auditable (and falsifiable), not metaphorical.

---

## 0. One-sentence claim

> In FIT/EST, changing the level of description must be represented as an explicit **coarse-graining operator** acting on the estimator tuple; any claim about **phase**, **phase transition**, or **irreversibility** is valid only to the extent that it passes a pre-registered **scale-consistency audit** across an admissible coarse-graining family.

This document does not add primitives. It adds a discipline: **scale as an operator**.

---

## 0.1 Guardrails

This lens is intentionally modest. It does **not** claim:

- that every system has RG fixed points,
- that FIT can (by default) compute field-theoretic critical exponents,
- that coarse-graining is unique,
- that the RG scale parameter is the same thing as FIT time,
- that any specific physics (e.g., FRG, holography) is required for FIT v2.x.

It claims only:

- scale transforms must be declared and versioned,
- invariants must be tested across admissible families,
- failures must be recorded as such (scope-limited, saturated, estimator-unstable, etc.).

---

## 1. Why FIT needs a renormalization lens

FIT is explicitly level-aware: every claim is scoped to an estimator tuple


$$
\mathcal{E} = (S_t, \mathcal{B}, \{\hat{F}, \hat{C}, \hat{I}\}, W).
$$


But “level-aware” can still be read as a reminder (“don’t confuse levels”), while leaving a structural gap:

- What is the relationship between levels?
- When two levels disagree, is it a real multiscale phenomenon, or an estimator artifact?

Renormalization theory upgrades the stance:

- a change of level is an operator on the description,
- invariants are what survive an admissible set of such operators,
- “universality” is the stable structure that persists under repeated coarse-graining.

FIT already contains the slots for this:

- Phase is a regime type (not a time segment),
- PT-MSS makes transitions registrable,
- EST requires robustness across admissible families.

This lens turns those into **scale-consistency tests**.

---

## 2. Two axes: time evolution vs scale transformation

A recurring confusion (and a source of over-claiming) is to treat “RG scale” as if it were “time”.

This lens enforces a strict separation:

- **Time axis:** physical or simulated evolution, $t \mapsto S_t$
- **Scale axis:** change of description, $b \mapsto \mathcal{E}^{(b)}$

You may introduce a scale coordinate $\ell = \ln b$ for convenience, but $\ell$ is **not** FIT time.

Cross-scale claims are about consistency in $\ell$ at fixed $t$, or about invariance of **event structure** when the same trajectory is observed through multiple $\mathcal{G}_b$.

---

## 3. Coarse-graining as an operator

### 3.1 Definition: coarse-graining operator

Let


$$
\mathcal{G}_b : \mathcal{S} \rightarrow \mathcal{S}^{(b)}
$$


be a coarse-graining operator at scale factor $b>1$.

- Input: fine state representation $S_t \in \mathcal{S}$
- Output: coarse state representation $S_t^{(b)} \in \mathcal{S}^{(b)}$

Example (cellular automata):

- $b=2$ : map a $2\times 2$ block to a single macro-cell
- $b=4$ : map a $4\times 4$ block to a single macro-cell

**Requirement:** $\mathcal{G}_b$ must be declared and versioned.

### 3.2 Pushforward of estimator tuples

Given a base estimator tuple


$$
\mathcal{E} = (S_t, \mathcal{B}, \{\hat{F}, \hat{C}, \hat{I}\}, W),
$$


define its scale-transformed tuple


$$
\mathcal{E}^{(b)} := \mathrm{PushForward}_b(\mathcal{E})
= (S_t^{(b)}, \mathcal{B}^{(b)}, \{\hat{F}^{(b)}, \hat{C}^{(b)}, \hat{I}^{(b)}\}, W^{(b)}).
$$


Minimum requirements:

- $S_t^{(b)} = \mathcal{G}_b(S_t)$
- $\mathcal{B}^{(b)}$ is declared (often inherited; sometimes changes)
- estimators are recomputed on the coarse representation
- windowing updates are explicit (e.g., $W^{(b)} = W/b$ or fixed-by-task)

---

## 4. Scale-consistency as an EST gate

We define three levels of scale-consistency, aligned with EST task types.

### 4.1 Ordinal scale-consistency

A claim is **ordinally scale-consistent** if the ordering of phases or monotone trends is preserved across $b \in \mathcal{B}_{\text{adm}}$.

Operational (typical):

- require rank-correlation of $\hat{C}^{(b)}(t)$ across scales to exceed a pre-registered threshold,
- allow brief deviations inside declared transition windows.

### 4.2 Metric scale-consistency

A claim is **metrically scale-consistent** if threshold-crossing events align across scales after a pre-registered calibration map.

Examples:

- plateau entry time,
- critical threshold crossing,
- “time-to-lock-in” tasks.

Metric equivalence is stronger than ordinal equivalence.

### 4.3 Topological scale-consistency

A claim is **topologically scale-consistent** if the *event structure* is preserved across scales.

In FIT terms, PT-MSS should be scale-consistent:

- number and ordering of phases,
- existence of a transition,
- co-occurrence of PT-MSS signals.

This is the most important form for Phase Algebra.

---

## 5. Scheme audit: coarse-graining families and estimator families

Renormalization teaches a methodological fact: approximate analyses can be **scheme-dependent**.

In FIT/EST terms:

- your conclusions may depend on your estimator family,
- and (crucially) on your coarse-graining family.

The lens therefore elevates **scheme audit** to a first-class requirement.

### 5.1 Admissibility for coarse-graining families

To prevent “scale hacking”, treat coarse-graining operators as part of admissibility.

A coarse-graining family $\{\mathcal{G}_b\}$ is admissible if:

1) **Scope declared:** state representation + boundary + implementation version
2) **Locality:** macro-states depend on bounded neighborhoods (when appropriate)
3) **Stability:** small perturbations do not catastrophically change macro-states
4) **Monotone information loss:** coarse states do not increase micro distinguishability
5) **Pre-registered:** the set of $b$ values is locked before evaluation

### 5.2 What counts as “universal” in this lens

Within FIT v2.x, use an operational definition:

> A quantity is “universal” (in the lens sense) if it remains stable across an admissible estimator family **and** an admissible coarse-graining family.

This is an audit statement, not a metaphysical one.

---

## 6. Empirical scale maps for scalar estimators

Many FIT estimators are scalar time series. For such estimators, the lens encourages a very specific test:

> Does there exist a (pre-registered) function $f_{b\to 2b}$ such that $\hat{C}^{(2b)}(t) \approx f_{b\to 2b}(\hat{C}^{(b)}(t))$?

### 6.1 Empirical RG map (terminology)

When such a mapping is observed, call it an **empirical scale map** (or “empirical RG map”):


$$
\hat{C}^{(2b)} \approx f_{b\to 2b}(\hat{C}^{(b)}).
$$


Avoid calling polynomial coefficients “beta functions” unless you also establish a semigroup property (next section).

A cautious “beta-like” object can be defined as:


$$
\beta_{\hat{C}}(x) := \frac{f_{b\to 2b}(x) - x}{\ln 2}.
$$


Fixed points (in this lens) are values $x^*$ such that $f(x^*) = x^*$. Stability can be probed via $f'(x^*)$.

### 6.2 Saturation warning

Very coarse scales can produce **saturation** (dynamic range collapse): the coarse estimator becomes nearly constant.

In this regime:

- $R^2$ can remain high,
- while rank information collapses (low Spearman),
- and transition visibility can disappear.

Saturation must be detected and labeled (not celebrated as “more universal”).

---

## 7. Semigroup / composition test (RG-hard gate)

A defining structural feature of RG is composability. In the scalar-map setting, the lens uses this as a “harder” test.

### 7.1 Semigroup criterion

If scale maps are meaningful descriptions of repeated coarse-graining, then


$$
f_{b\to 4b}(x) \;\approx\; \bigl(f_{2b\to 4b} \circ f_{b\to 2b}\bigr)(x).
$$


The most common practical case is:


$$
f_{1\to 4}(x) \;\approx\; \bigl(f_{2\to 4} \circ f_{1\to 2}\bigr)(x).
$$


### 7.2 Interpretation

- **Pass:** $\hat{C}$ is a candidate *closed coordinate* for scale evolution (near-Markov in scale).
- **Fail:** not a failure of FIT; it is information: $\hat{C}$ is not closed, and you likely need a higher-dimensional descriptor (e.g., $(\hat{C}, \hat{I})$ or $(\hat{C}, \hat{A})$ with activity).

### 7.3 Prereg-ready DoD

A minimal preregisterable decision rule:

- fit $f_{1\to 2}$, $f_{2\to 4}$, and $f_{1\to 4}$ on a train subset (seed holdout)
- evaluate on held-out seeds:
  - $\mathrm{MAE}(f_{1\to 4}(x),\; f_{2\to 4}(f_{1\to 2}(x))) \le \tau$
  - plus monotonicity and dynamic-range gates

Where $\tau$ is pre-registered (typical starting point: 0.02–0.03 for $\hat{C}\in[0,1]$, but must be tuned to the estimator noise floor).

### 7.4 Multi-estimator and multi-scheme validation (2026-02-14)

**Experimental validation on Game of Life RG experiment** (10 seeds, 2000 steps, $b\in\{1,2,4,8\}$):

Tested semigroup closure across:
- **Estimators**: $C_{\text{frozen}}$ and $C_{\text{activity}}$ (both FIT constraint metrics)
- **Coarse-graining schemes**: 
  - `majority`: threshold at $\lceil b^2/2 \rceil$
  - `threshold_high`: threshold at $\lceil 0.6 \cdot b^2 \rceil$

**Results** (RMSE of composed vs direct maps, threshold $\tau = 0.05$; gate-aware):

| Scheme | Estimator | 1→2→4 | 2→4→8 | Verdict |
|--------|-----------|--------|--------|---------|
| majority | $C_{\text{frozen}}$ | RMSE = 0.00196 (PASS) | SKIPPED (b=8 saturated) | SUCCESS |
| majority | $C_{\text{activity}}$ | RMSE = 0.00196 (PASS) | SKIPPED (b=8 saturated) | SUCCESS |
| threshold_high | $C_{\text{frozen}}$ | SKIPPED (b=4 saturated) | SKIPPED (b=4/8 saturated) | SCOPE_LIMITED_SATURATION |
| threshold_high | $C_{\text{activity}}$ | SKIPPED (b=4 saturated) | SKIPPED (b=4/8 saturated) | SCOPE_LIMITED_SATURATION |

**Key findings**:
1. **Closure confirmed on non-saturated triples**: where dynamic range is adequate, RMSE remains $\ll 0.05$.
2. **C_activity mirrors C_frozen**: Identical RMSE for both (expected, since $C_{\text{activity}} = 1 - C_{\text{frozen}}$ by definition).
3. **Scheme sensitivity is explicitly labeled**: stricter schemes can induce saturation and become `SCOPE_LIMITED_SATURATION` rather than forcing an artificial PASS.

**Saturation gate implementation**: Added explicit saturation check to prereg (see Section 7.5).

### 7.5 Saturation gate (added 2026-02-14)

To prevent misinterpretation of scale maps in saturated regimes, a saturation check is now required:

```python
def check_saturation(C_values: np.ndarray, threshold: float = 0.1) -> bool:
    """Returns True if >90% of values within threshold of [0,1] bounds."""
    near_zero = np.sum(C_values < threshold)
    near_one = np.sum(C_values > 1 - threshold)
    return (near_zero + near_one) / len(C_values) > 0.9
```

**Prereg rule**:
- If $C^{(b)}$ is saturated, exclude scale pair $b \to 2b$ from semigroup test
- Require at least 2 non-saturated scale pairs for PASS verdict
- Report saturation status in all scale-map analyses

**Rationale**: At high saturation (e.g., 4→8 in some GoL runs), $R^2$ can remain high while Spearman $\rho$ collapses, indicating rank information loss. This does not invalidate the RG lens, but requires explicit documentation.

### 7.6 Comprehensive scheme-estimator matrix (2026-02-14, extended)

**Full validation matrix** with 4 coarse-graining schemes × 3 estimators (10 seeds, 2000 steps, $b\in\{1,2,4,8\}$):

**Coarse-graining schemes**:
- `majority`: $\lceil b^2/2 \rceil$ (original)
- `threshold_high`: $\lceil 0.6 \cdot b^2 \rceil$ (strict survival)
- `threshold_low`: $\lceil 0.4 \cdot b^2 \rceil$ (lenient survival)
- `average`: mean(block) $\geq 0.5$ (continuous threshold)

**Estimators**: $C_{\text{frozen}}$, $C_{\text{activity}}$, $H$ (entropy_2x2)

**Results** (semigroup closure 1→2→4):

| Scheme | $C_{\text{frozen}}$ | $C_{\text{activity}}$ | $H$ |
|--------|----------|------------|---|
| average | ✓ 0.00196 | ✓ 0.00196 | SATURATED |
| majority | ✓ 0.00196 | ✓ 0.00196 | SATURATED |
| threshold_high | SATURATED | SATURATED | ✓ 0.00560 |
| threshold_low | ✓ 0.00246 | ✓ 0.00246 | SATURATED |

**Summary**: 7/12 configurations were testable (non-saturated), and 7/7 of those passed semigroup closure.

**Key findings**:

1. **Complementary saturation patterns**: Constraint estimators (C) and entropy (H) saturate under opposite scheme pressures. At strict thresholds (threshold_high), C saturates (all cells die); at lenient thresholds (average, majority, threshold_low), H saturates (all cells become ordered).

2. **C_frozen/C_activity are operationally robust in this matrix**: they pass under 3/4 schemes with RMSE ∈ [0.00196, 0.00246], all ≪ 0.05 threshold.  
   Note: $C_{\text{activity}} = 1 - C_{\text{frozen}}$ by construction, so this pair is a strong implementation-consistency check but not fully independent estimator evidence.

3. **H requires scheme tuning**: Only passes under threshold_high (RMSE = 0.00560). Still well below threshold, but narrower regime than C.

4. **Saturation gate is essential**: Without it, would incorrectly conclude "H always fails" (wrong: it passes under threshold_high) or "threshold_high preserves all estimators" (wrong: C saturates under it). Gate successfully separates structural failure from dynamic range collapse.

**Interpretation**: Semigroup closure is robust on this tested set **within non-saturated regimes**.  
Different estimators have different "sweet spots" in scheme space; all testable cells passed, while saturated cells are explicitly classified as scope-limited rather than counted as PASS.

---

## 8. Failure modes and labels

This lens treats “failure” as a productive outcome. Common outcomes:

- **ESTIMATOR_UNSTABLE:** mapping / event detection flips under small changes within the admissible family
- **SCHEME_DEPENDENT:** mapping holds under one $\{\mathcal{G}_b\}$ but not another admissible scheme
- **SCOPE_LIMITED:** a transition exists only at certain observational scales
- **SATURATED:** coarse scale collapses dynamic range, invalidating ranking/threshold tasks
- **NONCLOSURE:** no low-dimensional scale map exists for the chosen estimator set; require a larger coordinate set
- **TRUE MULTISCALE:** nested transitions exist, e.g., $\Phi_3(\Phi_2(\Phi_1))$, revealed only after scale separation

These labels are documentation aids. They do not modify FIT core primitives.

---

## 9. Universality (P15) as “surviving directions”

RG’s hardest and most transferable insight is not “self-similar shapes”, but:

> most microscopic degrees of freedom become irrelevant under coarse-graining; only a few directions survive and control macroscopic outcomes.

In FIT language, these are the **reconfiguration channels**: directions in which Force can still restructure constraints.

### 9.1 Practical proxies (v2.x compatible)

Without importing field theory, you can still estimate “how many directions survive” using estimator-friendly proxies:

- effective rank of a covariance spectrum (collapse diagnostics),
- participation-ratio-like measures that are explicitly **scale-normalized**,
- low-dimensional embeddings whose stability is audited across $\{\mathcal{G}_b\}$.

Lens stance:

- do not call a proxy “universal” unless it passes scheme audit,
- prefer proxies that remain meaningful when the representation dimension changes.

---

## 10. Worked example (illustrative): GoL multi-scale constraint mapping

This section is illustrative: it demonstrates how the lens is used, not what FIT “always implies”.

In a GoL multi-scale experiment (128×128, 30 seeds, 3000 steps; $b\in\{1,2,4,8\}$), a constraint estimator $\hat{C}$ showed a strong empirical scale map:

- $b=1\to 2$: poly2 $R^2 \approx 0.9998$, Spearman $\rho \approx 0.9999$
- $b=2\to 4$: poly2 $R^2 \approx 0.9797$, Spearman $\rho \approx 0.9965$
- $b=4\to 8$: poly2 $R^2 \approx 0.9980$, but Spearman $\rho \approx 0.6848$ (saturation warning)

This illustrates two lens points:

1) **Scale-linked structure exists** for some estimator choices (supporting “level-linked” analysis).
2) **Saturation can mimic strength:** very high $R^2$ can coexist with low rank information, and transition visibility can become scope-limited.

The same experiment also illustrates estimator fragility:

- some alternative constraint estimators (e.g., activity-based) can also show strong scale maps,
- while other candidates (e.g., an effective-dimension proxy) can fail cross-scale consistency.

The correct lens conclusion is not “GoL proves RG”. It is:

- scale maps are measurable and auditable,
- some observables saturate at coarse scales,
- admissibility and scheme audit are not optional.

---

## Appendix A: Example coarse-graining operators for CA (sketch)

### A1. Majority block map (GoL-style)

For a $b\times b$ block with sum $s$:

- macro cell = 1 if $s \ge \lceil b^2/2 \rceil$, else 0.

### A2. Density binning map

macro value = bin( density ), e.g. 0/1/2/3 for quartiles.

### A3. Morphology-preserving map (advanced)

macro cell = {still / oscillatory / chaotic} label derived from local temporal variance.

If used:

- must be preregistered,
- must be complexity-penalized under EST (risk of overfitting).

---

## Appendix B: Minimal prereg checklist (copy/paste)

- System + boundary $\mathcal{B}$
- State representation $S_t$
- Coarse-graining family $\{\mathcal{G}_b\}$ with version
- Estimator tuple(s) $\mathcal{E}$ and task type (ordinal/metric/topological)
- Window rules $W^{(b)}$ (how windows scale)
- Scale-consistency thresholds (Spearman / MAE / event tolerances)
- Saturation gate (dynamic range threshold)
- Scheme audit plan (at least 2 admissible coarse-graining schemes)
- Semigroup test plan (direct vs composed map), if claiming “scale flow” structure
