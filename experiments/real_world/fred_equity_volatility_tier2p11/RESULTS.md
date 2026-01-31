# FRED Equity Volatility (Tier-2) - Results Summary (EST-gated)

This file summarizes the repo-safe Tier-2 results for FRED financial volatility data under EST discipline.
It is a pointer-rich results page: quick conclusion first, then auditable artifacts.

Key rule: **interpretation is gated by coherence**. Negative results are preserved as first-class outcomes.

## One-sentence result

The coherence gate **fails** because the proposed constraint family (TED spread vs high-yield spread) exhibits **inconsistent behavior across different crisis types**: negative correlation during GFC (-0.142) but strong positive correlation during COVID (0.837). This demonstrates that the constraint estimators do NOT form a coherent family across crisis regimes.

## Key Finding: Crisis-Dependent Constraint Behavior

This is a **genuine negative result** that demonstrates the value of EST discipline:

| Crisis | Period | C_ted vs C_hy | Interpretation |
|--------|--------|---------------|----------------|
| **GFC** | 2008-09 to 2009-03 | rho = **-0.142** | TED and HY spread moved in **opposite** directions |
| **COVID** | 2020-03 to 2020-06 | rho = **+0.837** | TED and HY spread tightened **together** |

**Why this matters**: The constraint family (credit risk proxies) does NOT generalize across crisis types:
- **GFC** was a credit/liquidity crisis where interbank stress (TED) and corporate credit risk (HY) had different dynamics
- **COVID** was an exogenous shock where all credit constraints tightened simultaneously

## Boundary (what is in scope)

- Dataset: FRED Economic Data
- Time: 2005-01-01 to 2024-12-31 (5,352 days)
- Series: EMVFINCRISES, VIXCLS, TEDRATE, BAMLH0A0HYM2

## Result Table (coherence outcomes)

### Coherence Gate

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Pooled (C_ted vs C_hy) | 0.170 | >= 0.4 | **FAIL** |
| Pooled (V_emv vs V_vix) | 0.362 | >= 0.4 | **FAIL** |
| GFC validation | -0.142 | >= 0.4 | **FAIL** |
| COVID validation | 0.837 | >= 0.4 | PASS |
| **Overall** | - | All validation PASS | **ESTIMATOR_UNSTABLE** |

### Regime Detection

| Metric | Value |
|--------|-------|
| High volatility days (VIX > 75th pct) | 1,294 (24%) |
| Sustained high volatility (21+ days) | 405 (8%) |

## Interpretation Rules (EST-compliant)

Because the coherence gate **fails**:

1. **Do NOT interpret regime transitions as FIT-consistent** under this estimator family
2. The proposed C_hat family (TED spread, HY spread) is **not suitable** for cross-crisis regime analysis
3. This is a measurement/estimator problem, not a theory failure

## Implications for FIT Applications

This negative result suggests two paths forward:

### Path A: Crisis-Specific Analysis
- Run separate coherence gates for each crisis type
- Accept that "constraint family" may be crisis-regime-dependent

### Path B: Alternative Estimator Family
- Replace TED spread (discontinued post-LIBOR transition)
- Consider: VIX term structure, credit default swap spreads, repo rates

## Archived Artifacts

- `outputs/run001/metrics_daily.csv` - Daily time series
- `outputs/run001/coherence_report.json` - Machine-readable coherence results
- `outputs/run001/regime_events.json` - Regime detection counts
- `outputs/run001/run_diagnostics.md` - Human-readable summary

## Reproduce (local)

```bash
cd experiments/real_world/fred_equity_volatility_tier2p11

# Download data
python scripts/download_fred_data.py --start 2000-01-01 --end 2024-12-31 --outdir data/raw

# Run analysis
python scripts/compute_volatility_metrics.py --datadir data/raw --outdir outputs/run001 --start 2005-01-01 --end 2024-12-31
```

## Comparison to Other Cases

| Case | Coherence Gate | Key Finding |
|------|----------------|-------------|
| TLC Yellow | PASS (windowed) | Stable; late-2022 localized failure |
| TLC Green | FAIL | Constraint-family mismatch |
| NYC 311 | PASS | H1 inconclusive (boundary artifact) |
| **FRED Volatility** | **FAIL** | **Crisis-dependent constraint behavior** |
