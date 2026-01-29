# Regime Detection Report

**Case ID:** nyc_tlc_tier2p11
**Generated:** 2026-01-28 22:20:32
**Proposition:** P11
**Detection Method:** `robust_zscore_peak`

---

## 1. Coherence Gate

> **Status: OK_PER_WINDOW** - Coherence passes within preregistered date windows.
> 
> Interpretation rule: interpret signatures within each window; pooled level shifts can break pooled coherence.

### Coherence Test Results

- `C_congestion` vs `C_price_pressure`: rho = 0.543 (n=1826) **[FAIL]**

### Windowed Coherence (Diagnostic)

| Window | Status | Pair | rho | n | Pass |
|--------|--------|------|-----|---|------|
| pre_covid (2019-01-01..2020-02-29) | OK | `C_congestion` vs `C_price_pressure` | 0.928 | 425 | PASS |
| post_covid (2020-03-01..2023-12-31) | OK | `C_congestion` vs `C_price_pressure` | 0.601 | 1401 | PASS |

---

## 2. Detection Parameters

| Parameter | Value |
|-----------|-------|
| Method | `robust_zscore_peak` |
| zscore_threshold | 2.5 |
| min_peak_distance | 7 |
| rolling_window | 21 |
| window_size | 14 |
| shift_threshold | None |

---

## 3. Top 5 Change Points (by magnitude)

| Rank | Date | Score | dR/dt Value | Direction |
|------|------|-------|-------------|-----------|
| 1 | 2021-10-26 | +7.620 | 0.019056 | positive |
| 2 | 2020-01-20 | +7.596 | 0.027230 | positive |
| 3 | 2020-11-26 | +7.586 | 0.064998 | positive |
| 4 | 2020-02-24 | -6.874 | -0.026941 | negative |
| 5 | 2020-02-17 | +6.586 | 0.040845 | positive |

---

## 4. All Change Points (chronological)

**Total detected:** 102

| Date | Score | dR/dt Value | Direction |
|------|-------|-------------|-----------|
| 2019-01-21 | +5.183 | 0.025243 | positive |
| 2019-01-28 | -3.187 | -0.020765 | negative |
| 2019-02-18 | +3.026 | 0.026575 | positive |
| 2019-02-25 | -3.917 | -0.026718 | negative |
| 2019-03-04 | +3.149 | 0.019005 | positive |
| 2019-03-11 | -3.048 | -0.020367 | negative |
| 2019-05-13 | -2.525 | -0.015467 | negative |
| 2019-05-27 | +5.053 | 0.051976 | positive |
| 2019-06-03 | -4.073 | -0.045067 | negative |
| 2019-07-04 | +5.996 | 0.050092 | positive |
| 2019-07-11 | -4.142 | -0.054901 | negative |
| 2019-09-02 | +3.938 | 0.027117 | positive |
| 2019-09-09 | -4.398 | -0.040775 | negative |
| 2019-09-30 | +2.564 | 0.027983 | positive |
| 2019-10-14 | +2.792 | 0.019996 | positive |
| 2019-11-28 | +2.663 | 0.037758 | positive |
| 2019-12-05 | -2.593 | -0.040981 | negative |
| 2019-12-25 | +4.883 | 0.047456 | positive |
| 2020-01-08 | -3.267 | -0.029573 | negative |
| 2020-01-20 | +7.596 | 0.027230 | positive |
| 2020-01-27 | -4.618 | -0.021205 | negative |
| 2020-02-10 | -2.882 | -0.016931 | negative |
| 2020-02-17 | +6.586 | 0.040845 | positive |
| 2020-02-24 | -6.874 | -0.026941 | negative |
| 2020-03-06 | -2.521 | -0.009954 | negative |
| 2020-03-28 | -3.071 | -0.033642 | negative |
| 2020-05-07 | +3.408 | 0.039703 | positive |
| 2020-06-01 | -2.872 | -0.042897 | negative |
| 2020-07-11 | -3.560 | -0.029266 | negative |
| 2020-07-18 | +3.544 | 0.022913 | positive |
| 2020-09-07 | +2.927 | 0.021697 | positive |
| 2020-09-14 | -2.868 | -0.030824 | negative |
| 2020-09-28 | +4.177 | 0.018867 | positive |
| 2020-10-05 | -4.265 | -0.021614 | negative |
| 2020-11-11 | -3.899 | -0.020437 | negative |
| 2020-11-26 | +7.586 | 0.064998 | positive |
| 2020-12-03 | -4.317 | -0.061176 | negative |
| 2020-12-17 | +2.729 | 0.025746 | positive |
| 2020-12-25 | +5.610 | 0.069273 | positive |
| 2021-01-08 | -3.885 | -0.044112 | negative |
| 2021-01-18 | +2.692 | 0.018308 | positive |
| 2021-01-25 | -2.874 | -0.026954 | negative |
| 2021-02-02 | +3.826 | 0.023946 | positive |
| 2021-02-25 | -4.081 | -0.025139 | negative |
| 2021-05-01 | +6.241 | 0.013925 | positive |
| 2021-05-12 | +4.571 | 0.011517 | positive |
| 2021-05-20 | -2.512 | -0.018304 | negative |
| 2021-05-31 | +5.572 | 0.040675 | positive |
| 2021-06-07 | -5.105 | -0.045129 | negative |
| 2021-07-05 | +3.203 | 0.043759 | positive |
| 2021-07-27 | -2.971 | -0.009227 | negative |
| 2021-08-12 | -2.760 | -0.009225 | negative |
| 2021-08-22 | +2.614 | 0.023832 | positive |
| 2021-08-29 | -3.885 | -0.034635 | negative |
| 2021-09-13 | -3.592 | -0.054886 | negative |
| 2021-09-23 | -3.533 | -0.035235 | negative |
| 2021-10-11 | +3.956 | 0.024185 | positive |
| 2021-10-18 | -4.057 | -0.018817 | negative |
| 2021-10-26 | +7.620 | 0.019056 | positive |
| 2021-11-02 | -2.512 | -0.010252 | negative |
| 2021-11-25 | +4.151 | 0.049027 | positive |
| 2021-12-02 | -4.122 | -0.050262 | negative |
| 2021-12-25 | +5.004 | 0.051700 | positive |
| 2022-01-01 | -2.758 | -0.015470 | negative |
| 2022-01-17 | +2.996 | 0.032574 | positive |
| 2022-01-24 | -3.241 | -0.041797 | negative |
| 2022-02-21 | +5.794 | 0.037870 | positive |
| 2022-02-28 | -3.946 | -0.032844 | negative |
| 2022-05-04 | +2.555 | 0.007800 | positive |
| 2022-05-30 | +4.097 | 0.046966 | positive |
| 2022-06-06 | -3.647 | -0.040639 | negative |
| 2022-07-11 | -3.417 | -0.032122 | negative |
| 2022-07-29 | -2.634 | -0.006837 | negative |
| 2022-08-16 | +3.608 | 0.012325 | positive |
| 2022-09-05 | +3.459 | 0.038104 | positive |
| 2022-09-12 | -4.637 | -0.058463 | negative |
| 2022-09-25 | -4.110 | -0.038752 | negative |
| 2022-10-03 | -2.528 | -0.033433 | negative |
| 2022-10-10 | +5.354 | 0.037179 | positive |
| 2022-10-17 | -3.759 | -0.020217 | negative |
| 2022-11-24 | +5.050 | 0.053677 | positive |
| 2022-12-01 | -4.711 | -0.054329 | negative |
| 2022-12-24 | +6.250 | 0.029154 | positive |
| 2023-01-02 | +3.423 | 0.034604 | positive |
| 2023-01-09 | -2.967 | -0.030840 | negative |
| 2023-02-20 | +3.494 | 0.038339 | positive |
| 2023-02-27 | -3.179 | -0.035299 | negative |
| 2023-03-07 | -3.084 | -0.018472 | negative |
| 2023-04-06 | +2.863 | 0.019043 | positive |
| 2023-06-19 | +2.965 | 0.020491 | positive |
| 2023-07-04 | +2.952 | 0.045337 | positive |
| 2023-07-11 | -3.232 | -0.047069 | negative |
| 2023-08-17 | +2.506 | 0.011666 | positive |
| 2023-09-04 | +3.495 | 0.031825 | positive |
| 2023-09-11 | -4.696 | -0.065120 | negative |
| 2023-09-24 | +4.065 | 0.062647 | positive |
| 2023-10-01 | -2.554 | -0.047540 | negative |
| 2023-10-09 | +2.865 | 0.022650 | positive |
| 2023-10-16 | -3.710 | -0.020082 | negative |
| 2023-11-23 | +3.143 | 0.044935 | positive |
| 2023-11-30 | -2.933 | -0.050352 | negative |
| 2023-12-25 | +5.562 | 0.044399 | positive |

---

## 5. Interpretation

**Due to coherence failure, no interpretation is permitted.**

Recommended actions:
- Review estimator definitions
- Check data quality
- Consider alternative constraint proxies

---

## 6. Failure Labels (EST Reference)

| Label | Meaning |
|-------|---------|
| `ESTIMATOR_UNSTABLE` | Coherence gate failed; change points not interpretable |
| `OK_PER_WINDOW` | Coherence passes within preregistered windows; interpret within-window only (current) |
| `OK_PER_YEAR` | Coherence passes within yearly windows; interpret within-year only |
| `SCOPE_LIMITED` | Data boundary restricts generalization |
| `DATA_MISSING` | Insufficient data for reliable estimation |
| `SCHEMA_DRIFT` | Data schema changed; requires new preregistration |
