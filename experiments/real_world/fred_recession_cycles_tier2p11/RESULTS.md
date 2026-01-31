# FRED Recession Cycles (Tier-2) - Results Summary (EST-gated)

This file summarizes the repo-safe Tier-2 results for FRED recession cycle data under EST discipline.

Key rule: **interpretation is gated by coherence**. Positive results are preserved when coherence passes.

## One-sentence result

The coherence gate **passes** because the leading index and recession probability show the expected strong negative correlation (rho = -0.626), confirming that the information estimators are coherent under the preregistered hypothesis. This case demonstrates that FRED's Markov-switching recession probability forms a valid regime indicator for FIT analysis.

## Key Finding: H2 Hypothesis Confirmed

| Hypothesis | Expected | Actual | Status |
|------------|----------|--------|--------|
| **H2**: L_idx vs P_rec | rho < -0.4 | rho = **-0.626** | **PASS** |

The leading economic index and recession probability are **strongly negatively correlated**, confirming:
- As the leading index drops, recession probability rises
- The Markov-switching model output aligns with leading indicator dynamics
- This estimator pair forms a coherent family for regime analysis

## Boundary (what is in scope)

- Dataset: FRED Economic Data
- Time: 1990-01-01 to 2024-12-31 (840 months / 35 years)
- Series: RECPROUSM156N, USREC, USSLIND, ICSA, FEDFUNDS, T10Y2Y, UMCSENT

## Result Table (coherence outcomes)

### Coherence Gate

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| H2: L_idx vs P_rec | -0.626 | < -0.4 | **PASS** |
| I_sent vs L_idx | 0.418 | >= 0.3 | **PASS** |
| **Overall** | - | H2 PASS | **OK_TO_INTERPRET** |

### Recession Periods Detected (NBER)

| Period | Start | End | Duration |
|--------|-------|-----|----------|
| 1990-91 Recession | 1990-08 | 1991-04 | 8 months |
| Dot-com Recession | 2001-04 | 2001-12 | 8 months |
| Great Recession | 2008-01 | 2009-07 | 18 months |
| COVID Recession | 2020-03 | 2020-05 | 2 months |

## Why This Case Works (vs. FRED Volatility)

| Aspect | FRED Volatility | FRED Recession |
|--------|-----------------|----------------|
| Coherence gate | FAIL | **PASS** |
| Key issue | Crisis-dependent behavior | Consistent across cycles |
| Regime indicator | Proposed (VIX) | **Native (Markov-switching)** |
| Interpretation | Not permitted | **Permitted** |

The recession case succeeds because:
1. **Regime is model-native**: FRED recession probability is explicitly derived from a Markov-switching model
2. **Theoretical alignment**: Leading indicators are designed to predict recession probability
3. **Consistent behavior**: The L_idx vs P_rec relationship is stable across different recession types

## Interpretation Rules (EST-compliant)

Because the coherence gate **passes**:

1. **Regime transitions are interpretable** under the L_idx / P_rec estimator pair
2. The Markov-switching recession probability is a valid regime indicator for FIT
3. Further analysis (e.g., transition dynamics, constraint behavior during regimes) is permitted

## Archived Artifacts

- `outputs/run001/metrics_monthly.csv` - Monthly time series
- `outputs/run001/coherence_report.json` - Machine-readable coherence results
- `outputs/run001/recession_events.json` - NBER recession periods
- `outputs/run001/run_diagnostics.md` - Human-readable summary

## Reproduce (local)

```bash
cd experiments/real_world/fred_recession_cycles_tier2p11

# Download data
python scripts/download_recession_data.py --start 1990-01-01 --end 2024-12-31 --outdir data/raw

# Run analysis
python scripts/compute_recession_metrics.py --datadir data/raw --outdir outputs/run001 --start 1990-01-01 --end 2024-12-31
```

## Comparison to Other Cases

| Case | Coherence Gate | Key Finding |
|------|----------------|-------------|
| TLC Yellow | PASS (windowed) | Stable; late-2022 localized failure |
| TLC Green | FAIL | Constraint-family mismatch |
| NYC 311 | PASS | H1 inconclusive (boundary artifact) |
| FRED Volatility | FAIL | Crisis-dependent constraint behavior |
| **FRED Recession** | **PASS** | **H2 confirmed (L_idx vs P_rec = -0.626)** |

## References

- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357-384.
- Chauvet, M., & Piger, J. (2008). A comparison of the real-time performance of business cycle dating methods. *Journal of Business & Economic Statistics*, 26(1), 42-49.
