# FRED Recession Cycles (Tier-2) - Economic Regime Switching Demo

## Scope & Claims Notice

This artifact illustrates how the FIT framework can be *applied* to economic cycle regime switching using public FRED data that explicitly incorporates Markov-switching models.

It does **not** constitute:
- proof of FIT,
- validation of universal claims,
- or generalization beyond the stated scope.

---

This folder is a **Tier-2** real-world demonstration for FIT: use FRED recession probability and leading indicators to test **regime switching** between expansion/contraction states under EST discipline.

## Why this case is ideal for FIT

1. **Phase transition is model-native**: FRED's recession probability series (RECPROUSM156N) is explicitly derived from a dynamic factor Markov-switching model (Chauvet & Piger). The "phase transition" is literally baked into the data generation process.

2. **Constraints are macroeconomic**: Credit conditions, labor market tightness, and policy rates form observable constraint layers.

3. **Academic pedigree**: Hamilton (1989) regime-switching model is foundational; NBER recession dating is the gold standard for cycle identification.

## FIT Tuple Mapping

| FIT Component | Economic Interpretation | FRED Proxy |
|---------------|------------------------|------------|
| I_hat (Information) | Economic uncertainty / confidence | Leading indicators, consumer sentiment |
| C_hat (Constraint) | Credit / labor / policy constraints | Credit spreads, unemployment claims, fed funds |
| F_hat (Force) | Shocks driving transitions | Oil prices, policy changes |

## Data Sources (FRED)

### Primary Series

| Series ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| RECPROUSM156N | Smoothed Recession Probabilities | Monthly | Markov-switching model output (0-100%) |
| USREC | NBER Recession Indicator | Monthly | Binary (0/1) official recession dating |
| USSLIND | Leading Index for US | Monthly | Conference Board Leading Economic Index |
| ICSA | Initial Jobless Claims | Weekly | Labor market constraint proxy |
| FEDFUNDS | Federal Funds Rate | Monthly | Monetary policy constraint |
| UMCSENT | Consumer Sentiment | Monthly | Information/confidence proxy |

### Supplementary Series

| Series ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| UNRATE | Unemployment Rate | Monthly | Labor market state |
| INDPRO | Industrial Production | Monthly | Real activity measure |
| T10Y2Y | 10Y-2Y Treasury Spread | Daily | Yield curve (recession predictor) |

## Preregistered Hypothesis

**H1**: Constraint estimators (credit spread, claims, fed funds) should show elevated coherence during regime transitions (expansion → contraction or vice versa).

**H2**: The leading index and recession probability should be negatively coherent (leading index drops as recession probability rises).

**Coherence gate**: If constraint family coherence < 0.3 during NBER-dated recessions, mark `ESTIMATOR_UNSTABLE`.

## Known Recession Periods (NBER)

| Start | End | Duration | Event |
|-------|-----|----------|-------|
| 2001-03 | 2001-11 | 8 months | Dot-com recession |
| 2007-12 | 2009-06 | 18 months | Great Recession |
| 2020-02 | 2020-04 | 2 months | COVID recession |

## How to Download Data

### Using pandas-datareader

```python
import pandas_datareader as pdr
from datetime import datetime

start = datetime(1990, 1, 1)
end = datetime(2024, 12, 31)

# Primary series
rec_prob = pdr.DataReader('RECPROUSM156N', 'fred', start, end)
usrec = pdr.DataReader('USREC', 'fred', start, end)
leading = pdr.DataReader('USSLIND', 'fred', start, end)
claims = pdr.DataReader('ICSA', 'fred', start, end)
fedfunds = pdr.DataReader('FEDFUNDS', 'fred', start, end)
sentiment = pdr.DataReader('UMCSENT', 'fred', start, end)
```

## Artifacts

- Results summary: `RESULTS.md` (to be generated)
- Pre-registration: `prereg.yaml`
- Scripts: `scripts/compute_recession_metrics.py`
- Raw data: `data/raw/*.csv`

## References

- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357-384.
- Chauvet, M., & Piger, J. (2008). A comparison of the real-time performance of business cycle dating methods. *Journal of Business & Economic Statistics*, 26(1), 42-49.
- FRED Recession Probabilities documentation: https://fred.stlouisfed.org/series/RECPROUSM156N
