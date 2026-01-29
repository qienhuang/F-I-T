# FIT Case Study (Tier 2 / P11): NYC TLC Trip Records  
## Regime-Shift Signatures in  \( I/C \)  with EST Coherence Gates (v1.1)

**Case ID:** `nyc_tlc_tier2p11`  
**Status:** **v1.1 (refined, EST-aligned)**  
**Date:** 2026-01-23  
**Audience:** FIT/EST learners; regime detection in real-world systems  
**Primary focus:** **P11** (regime-change signatures in  \( I/C \) )  
**Secondary focus:** EST discipline (pre-registration, estimator-family coherence, failure labels)

---

## What changed in v1.1 (compared to v1.0)

This revision tightens **EST rigor and cross-case consistency** with your existing NYC 311 case.

Note: the active prereg file in this folder is `EST_PREREG.yaml` (currently version 1.2, dated 2026-01-28). Where this doc says an estimator is "optional", treat the prereg as the source of truth; changing enabled estimators requires a new prereg version under EST.

Update (2026-01-28): a full 2019-2023 Yellow Taxi run completed under `EST_PREREG.yaml` and produced a coherent EST failure (coherence gate: `ESTIMATOR_UNSTABLE`). The archived artifacts are in `results_runs/nyc_yellow_2019_2023_v1/`.

1) **Unified failure semantics**
   - Explicit, consistent use of `ESTIMATOR_UNSTABLE` and `SCOPE_LIMITED`.
   - Clear instruction: *no interpretation if coherence fails*.

2) **Trade-off figure semantics clarified**
   - Panel purposes are now normative (what each panel is allowed to claim).
   - Added guidance for annotating detected change points (vertical lines) **without implying causality**.

3) **Estimator-family extension points**
   - Added a third optional constraint estimator (`C_concentration`) with a precise definition and when to enable it.
   - Documented how to swap/extend estimators without invalidating preregistration.

4) **Schema-drift handling made explicit**
   - Boundary section now treats TLC schema/version changes as first-class boundary events (EST-relevant).
   - Clear rule: schema changes ⇒ boundary change ⇒ new preregistration.

5) **Cross-case alignment**
   - Terminology and structure aligned with `nyc_311_tier2p5` (Tier labeling, output artifacts, reading rules).

---

## Epistemic status (unchanged, restated)

- This is a **signature-detection case**, not a causal analysis.
- Claims are **conditional on the preregistered estimator tuple**.
- Reproducibility > narrative fit.

---

## 1. Why TLC remains a strong FIT P11 case

The rationale is unchanged, but v1.1 emphasizes **measurement discipline**:

- TLC data are large and structured, *but not measurement-invariant*.
- FIT value here is learning to distinguish:
  - real regime shifts **vs**
  - estimator drift / schema effects.

This mirrors exactly the lesson from the 311 case, now in a different domain.

---

## 2. FIT/EST formalization (v1.1 clarification)

### 2.1 Estimator tuple (canonical)

\[
\mathcal{E} = (S_t, \mathcal{B}, \{\hat{F},\hat{C},\hat{I}\}, W)
\]

**Key clarification (v1.1):**

- Any change to **schema mapping**, **zone definitions**, or **dataset mix**  
  ⇒ **change in boundary \( \mathcal{B} \)**  
  ⇒ **new preregistration required**.

This is non-negotiable under EST.

---

## 3. Estimator definitions (v1.1)

### 3.1 Information estimators  \( \hat{I} \)

Unchanged:
- `I_entropy_pu`
- optional `I_entropy_od`

### 3.2 Constraint estimators  \( \hat{C} \)  (family)

**Primary (required):**

- `C_congestion`: log1p(duration / mile)
- `C_scarcity`: -log(trip_count)

**Optional extension (new in v1.1):**

- **`C_concentration` (spatial concentration proxy)**  
  Definition (pickup zones):

  \[
  \hat{C}_{conc}(t) = \sum_{i \in \text{Top-}k} p_i(t)
  \]

  where \( p_i(t) \) are pickup-zone shares, and \( k \) is preregistered (e.g., top-5).

**Rules:**
- Adding `C_concentration` is allowed **only** if:
  - it is declared in `EST_PREREG.yaml`, and
  - coherence is re-evaluated across *all* active \( \hat{C} \).

### 3.3 Force estimators  \( \hat{F} \)

Unchanged (drift proxies), but v1.1 clarifies interpretation:

- \( \hat{F} \) indicates **pressure or drift**, not directionality of cause.

---

## 4. EST coherence gate (v1.1 emphasis)

**Gate definition (unchanged):**
- Spearman rho ≥ 0.6
- min_points ≥ 30

**Interpretation rules (v1.1):**

- **Fail ⇒ hard stop.**  
  You may still *report* change points, but they must be labeled:
  > *“Detected under ESTIMATOR_UNSTABLE; not interpretable.”*

- **Pass ⇒ conditional proceed.**  
  You may discuss signatures, but must state:
  > *“Conditional on estimator family coherence.”*

---

## 5. One-page trade-off figure (v1.1 norms)

The four panels are **normative**, not illustrative:

- **(A) Information panel**  
  Allowed claim: diversity/coverage changes over time.

- **(B) Constraint-family panel**  
  Allowed claim: whether multiple \( \hat{C} \) agree in ordering and trend.

- **(C) Ratio + derivative panel (P11 core)**  
  Allowed claim: presence/absence of regime-change *signatures*.

- **(D) Trade-off scatter**  
  Allowed claim: empirical feasible region under the chosen boundary.

**Disallowed:** causal narratives, policy attribution, “explanation by event” without separate analysis.

---

## 6. Interpretation workflow (v1.1 checklist)

1) Check schema version and boundary declaration.
2) Check coherence gate.
3) Inspect \( d(I/C)/dt \) peaks.
4) Run at least one window-size sensitivity check.
5) Only then annotate known events (optional).

---

## 7. Known limitations (updated)

- TLC data lack explicit capacity constraints; all \( \hat{C} \) are proxies.
- Fare-based drift is confounded by pricing rules; interpret as pressure, not incentive.
- Hourly aggregation may reveal different signatures; v1.1 remains daily by default.

---

## 8. Next upgrades (v1.2 candidates)

- Add hourly (`H`) bucket preregistration as a *separate boundary*.
- Introduce Bayesian online change-point detection as an alternative method.
- Cross-plot TLC vs 311 signatures to study cross-system synchrony (Tier 3).

---

## Appendix: Required artifacts (v1.1)

- `README.md`
- `EST_PREREG.yaml`
- `src/schema.py`
- `src/clean.py`
- `src/estimators.py`
- `src/regimes.py`
- `src/plots.py`
- `outputs/tradeoff_onepage.pdf`
- `outputs/regime_report.md`
