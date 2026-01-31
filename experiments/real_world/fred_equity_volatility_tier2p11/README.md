# FRED Equity Market Volatility (Tier-2) - Regime Switching Demo

## Scope & Claims Notice

This artifact illustrates how the FIT framework can be *applied* to financial market regime switching under a specific estimator choice and public FRED data.

It does **not** constitute:
- proof of FIT,
- validation of universal claims,
- or generalization beyond the stated scope.

Any observed behavior is conditional on the chosen estimators, the dataset boundary, and the preregistered configuration. This artifact should be interpreted as an *example of use*, not as theoretical evidence.

---

This folder is a **Tier-2** real-world demonstration for FIT: use public FRED financial volatility data to test a **narrow, preregistered** claim about **regime switching** between high/low volatility states under explicit constraint estimators.

## Why this case is suitable for FIT

1. **Phase transition is explicit**: High-volatility vs low-volatility regimes are a classic "multi-stable / Markov-switching" object in finance literature.

2. **Constraints are observable**: Trading mechanisms, policy interventions, margin requirements, and market microstructure form a constraint layer that can be operationalized as EST estimator families.

3. **Academic acceptance**: Regime-switching models (Hamilton, 1989) are well-established; FRED explicitly uses dynamic factor Markov-switching models for recession probability.

## FIT Tuple Mapping

| FIT Component | Financial Interpretation | FRED Proxy |
|---------------|-------------------------|------------|
| I_hat (Information) | Information availability / uncertainty | EMVFINCRISES (volatility), VIX, news intensity |
| C_hat (Constraint) | Risk constraints / liquidity | Bid-ask spread, trading volume, margin requirements |
| F_hat (Force) | Risk preference shifts | Policy announcements, credit spreads |

## Data Sources (FRED)

### Primary Series

| Series ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| EMVFINCRISES | Equity Market Volatility: Financial Crises | Daily | News-based volatility tracker for financial crisis mentions |
| VIXCLS | CBOE Volatility Index | Daily | Market-implied volatility (VIX) |
| TEDRATE | TED Spread | Daily | 3-month LIBOR minus 3-month T-Bill (credit risk proxy) |
| BAMLH0A0HYM2 | ICE BofA US High Yield Option-Adjusted Spread | Daily | Credit spread (constraint proxy) |

### Secondary Series (Recession Context)

| Series ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| USREC | NBER Recession Indicator | Monthly | Binary recession indicator |
| RECPROUSM156N | Smoothed Recession Probabilities | Monthly | Dynamic factor Markov-switching model output |

## Preregistered Hypothesis

**H1**: During high-volatility regimes (EMVFINCRISES > threshold), constraint estimators (credit spread, TED rate) should co-move positively (coherence PASS), reflecting coordinated tightening of risk constraints.

**Coherence gate**: If Spearman correlation between C_hat estimators < 0.4 during high-volatility windows, mark `ESTIMATOR_UNSTABLE` and do not interpret regime transitions as FIT-consistent.

## How to Download Data

### Option 1: FRED API (requires API key)

```python
import pandas_datareader as pdr
from datetime import datetime

start = datetime(2000, 1, 1)
end = datetime(2024, 12, 31)

# Primary volatility series
emv = pdr.DataReader('EMVFINCRISES', 'fred', start, end)
vix = pdr.DataReader('VIXCLS', 'fred', start, end)
ted = pdr.DataReader('TEDRATE', 'fred', start, end)
spread = pdr.DataReader('BAMLH0A0HYM2', 'fred', start, end)
```

### Option 2: Manual Download

1. Go to https://fred.stlouisfed.org/series/EMVFINCRISES
2. Click "Download" -> CSV
3. Place in `data/raw/EMVFINCRISES.csv`

Repeat for other series.

## Artifacts

- Results summary: `RESULTS.md` (to be generated after runs)
- Pre-registration: `prereg.yaml`
- Scripts: `scripts/compute_volatility_metrics.py`
- Raw data: `data/raw/*.csv`

## Known Regime Events (for validation)

| Period | Event | Expected Regime |
|--------|-------|-----------------|
| 2008-09 to 2009-03 | Global Financial Crisis | HIGH |
| 2010-05 | Flash Crash | HIGH (transient) |
| 2011-08 | US Debt Ceiling / Euro Crisis | HIGH |
| 2015-08 | China Devaluation | HIGH (transient) |
| 2020-03 | COVID-19 | HIGH |
| 2022-Q1 | Ukraine / Rate Hikes | ELEVATED |

## References

- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357-384.
- Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. *Quarterly Journal of Economics*, 131(4), 1593-1636.
- FRED Equity Market Volatility documentation: https://fred.stlouisfed.org/series/EMVFINCRISES
