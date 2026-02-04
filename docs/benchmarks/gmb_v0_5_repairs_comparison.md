**GMB v0.5 Repair A vs Repair B -- Side-by-side comparison**

**Setup:** Both repairs ran eval seeds 140-143 (4 seeds total).

**Tradeoff table (coverage vs FPR):**

| FPR Target | Repair A Threshold | Repair A Coverage | Repair B Threshold | Repair B Coverage | Notes |
|------------|-------------------|-------------------|-------------------|-------------------|-------|
| 0.01       | 4.76              | 0% (0/4)         | 1.90              | 0% (0/4)         | Identical operating point |
| 0.05       | 0.16              | 50% (2/4)        | 0.065             | 50% (2/4)        | Identical operating point |
| 0.10       | 0.085             | 50% (2/4)        | 0.034             | 50% (2/4)        | Identical operating point |
| 0.20       | 0.047             | 50% (2/4)        | 0.019             | 50% (2/4)        | Identical operating point |

**Per-run diagnostics (ROC AUC and Average Precision):**

Both repairs produce **identical** ROC AUC and Average Precision values for each seed:

| Seed    | ROC AUC | Average Precision |
|---------|---------|-------------------|
| seed_140| 0.4285  | 0.0576           |
| seed_141| 0.5221  | 0.0668           |
| seed_142| 0.3544  | 0.0534           |
| seed_143| 0.6059  | 0.1022           |

**Why are operating points identical?**

Both repairs modify the decision rule parameters (theta_corr, w_corr, eps_hspec) which scale or shift the score values but **do not change the rank ordering** of examples. As a result:
- ROC AUC (ranking-based metric) is unchanged
- Coverage at matched FPR targets is identical (same examples selected)
- Only the numeric threshold values differ (rescaling effect)

**Conclusion:** Repairs A and B are **monotonic transformations** of the baseline score. To improve detector performance, we need a **non-monotonic repair** that changes example ranking (e.g., reweighting features, mixing estimators, or learned calibration).

**Recommendation:** Do NOT expand to 40 seeds for these repairs. Focus on designing a non-monotonic repair candidate first.

