**GMB v0.5 Repairs — Unified comparison summary**

**Goal:** Test whether alternative decision rule parameters can improve grokking alarm performance (coverage at low FPR) without degrading FPR floor.

**Baseline:** v0.5 holdout spec with `theta_corr=0.3, w_hspec=1.0, w_corr=1.0, eps_hspec=0.002` (40 eval seeds 140-179).

---

## Tested repairs (limited seeds: 4-8)

| Repair | Type | Key Changes | Seeds | Purpose |
|--------|------|-------------|-------|---------|
| A | Monotonic | theta_corr: 0.3→0.75 | 4 | Reduce false positives by raising correction threshold |
| B | Monotonic | w_corr: 1.0→0.5, eps_hspec: 0.002→0.005 | 4 | De-weight correction, raise entropy threshold |
| C | Non-monotonic | w_hspec: 1.0→10, w_corr: 1.0→0.5, eps_hspec: 0.002→0.01, theta_corr: 0.3→0.2 | 8 | H_spec-dominant reordering |

---

## Results: Coverage at target FPRs

| FPR Target | Baseline (inferred) | Repair A (4 seeds) | Repair B (4 seeds) | Repair C (8 seeds) | C vs A/B |
|------------|---------------------|-------------------|-------------------|-------------------|----------|
| 0.05       | ~50%                | 50% (2/4)         | 50% (2/4)         | **25% (2/8)**     | **WORSE -50%** |
| 0.10       | ~50%                | 50% (2/4)         | 50% (2/4)         | **25% (2/8)**     | **WORSE -50%** |
| 0.20       | ~50%                | 50% (2/4)         | 50% (2/4)         | **37.5% (3/8)**   | **WORSE -25%** |

---

## Results: Mean ROC AUC (first 4 seeds for fair comparison)

| Repair | Mean ROC AUC | vs Baseline | Change |
|--------|-------------|-------------|--------|
| A/B    | 0.4777      | —           | Baseline (identical) |
| C      | 0.4460      | -0.032      | **-6.7% relative** |

**Key finding:** Repairs A and B produce **identical ROC AUC** and coverage because they only rescale/shift the score without changing example ranking (monotonic transformations).

---

## Why did each repair fail to improve performance?

**Repair A & B (monotonic):**
- Only rescale decision thresholds → same examples selected at matched FPR
- Coverage, ROC AUC, and average precision remain unchanged
- Conclusion: Monotonic parameter changes cannot improve detector performance

**Repair C (non-monotonic H_spec-dominant):**
- Over-weights spectral entropy (H_spec) by 10×, severely de-weights correction rate
- High eps_hspec=0.01 filters out too many checkpoints
- **Result:** Coverage drops by 50% at FPR=0.05/0.10, mean ROC AUC drops 6.7%
- **Root cause:** H_spec and Corr_Rate provide complementary information; extreme imbalance loses complementarity

---

## Diagnostic metrics (Repair C, 8 seeds)

- **n_eff_ratio:** 0.150-0.160 (similar to baseline, ~15-16% effective sample size)
- **k_eff:** 1.14 (very low effective support, dominated by ties)
- **tie_dominance:** 0.036 (3.6% of top quantile are ties)

These metrics suggest the score distribution is highly concentrated with many ties, limiting discrimination ability.

---

## Lessons learned

1. **Monotonic repairs are futile:** Any parameter change that preserves score ordering (rescaling, shifting) cannot improve coverage or ROC AUC. Only the numeric threshold changes.

2. **Naive reordering degrades performance:** Simply over-weighting one estimator loses complementary information and reduces detection quality.

3. **Need principled non-monotonic designs:** Future repairs should:
   - Use additive non-linearities (ReLU gating, piecewise functions)
   - Learn adaptive weights based on training dynamics
   - Apply time-varying thresholds that evolve with training phase
   - Preserve estimator complementarity while enhancing discrimination

---

## Recommendation: Stop parameter-tuning repairs

Instead, pursue:
- **Adaptive threshold learning:** Train a small classifier to predict grokking from (H_spec, Corr_Rate, r_eff) time series
- **Multi-timescale features:** Combine short-window and long-window statistics
- **Causal intervention analysis:** Identify which estimator components causally predict grokking vs spurious correlations

**Files:**
- Repair A: `grokking/results/v0_5_repairs/` (diagnostics + tradeoff)
- Repair B: `grokking/results/v0_5_repairs_repairB/` (diagnostics + tradeoff)
- Repair C: `grokking/results/v0_5_repairC/` (diagnostics + tradeoff)
- Comparison: `docs/benchmarks/gmb_v0_5_repairs_comparison.md`
- Repair C analysis: `docs/benchmarks/gmb_v0_5_repairC_results.md`

