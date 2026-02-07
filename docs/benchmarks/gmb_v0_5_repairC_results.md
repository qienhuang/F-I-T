**GMB v0.5 Repair C — Non-monotonic reordering results**

**Setup:** Repair C uses extreme weight imbalance (w_hspec=10, w_corr=0.5) plus high eps_hspec=0.01 and low theta_corr=0.2 to make H_spec dominate and create non-monotonic reordering relative to baseline. Ran 8 eval seeds (140-147).

**Key question:** Does reordering improve coverage@low-FPR compared to baseline and monotonic repairs A/B?

---

**Tradeoff comparison (coverage vs FPR):**

| FPR Target | Baseline (A/B, 4 seeds) Coverage | Repair C (8 seeds) Coverage | Change | Notes |
|------------|----------------------------------|----------------------------|--------|-------|
| 0.01       | 0% (0/4)                        | 0% (0/8)                  | No change | Still too conservative |
| 0.05       | 50% (2/4)                       | 25% (2/8)                 | **WORSE** | Coverage dropped by half |
| 0.10       | 50% (2/4)                       | 25% (2/8)                 | **WORSE** | Coverage dropped by half |
| 0.20       | 50% (2/4)                       | 37.5% (3/8)               | **WORSE** | Coverage dropped ~25% |

**Per-run ROC AUC comparison (first 4 seeds only, for fair comparison):**

| Seed    | Baseline (A/B) ROC AUC | Repair C ROC AUC | Change |
|---------|----------------------|-----------------|--------|
| seed_140| 0.4285               | 0.4538          | +0.025 |
| seed_141| 0.5221               | 0.5092          | -0.013 |
| seed_142| 0.3544               | 0.2163          | **-0.138** |
| seed_143| 0.6059               | 0.6046          | -0.001 |
| **Mean**| **0.4777**           | **0.4460**      | **-0.032** |

---

**Conclusion:**

Repair C's H_spec-dominant reordering **degrades performance** compared to baseline:
- Coverage@0.05 and @0.10 dropped from 50% to 25% (worse by half)
- Mean ROC AUC decreased by ~0.03 (6.7% relative drop)
- seed_142 shows severe degradation (-0.138 AUC)

**Why did reordering fail?**
- Over-weighting H_spec (spectral entropy) suppresses examples where correction rate would have been a strong signal
- High eps_hspec=0.01 filters out too many low-entropy checkpoints, reducing sensitivity
- The two estimators (H_spec and Corr_Rate) appear to provide complementary information; extreme imbalance loses this complementarity

**Recommendation:** Do NOT pursue this repair direction. Instead:
1. Try **additive non-linearity** (e.g., ReLU(H_spec - threshold) + w_corr * Corr) to create soft gating
2. Consider **learned weights** per checkpoint based on training dynamics
3. Investigate **time-varying thresholds** that adapt as training progresses

Repair C demonstrates that arbitrary reordering is insufficient; we need principled non-monotonic transformations guided by estimator complementarity.

