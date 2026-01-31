# FRED Equity Volatility - Run Diagnostics

## Run Config
- Data directory: `../data/raw`
- Output directory: `../outputs/run001`
- Boundary: 2005-01-01 to 2024-12-31
- Days loaded: 5352

## Coherence Gate
- **Status: ESTIMATOR_UNSTABLE**
- Threshold: rho >= 0.4

### Pooled Coherence
- Constraint family (C_ted vs C_hy): rho = 0.170, n = 4569
- Information family (V_emv vs V_vix): rho = 0.362, n = 1439

### Validation Periods
| Period | rho | n | Status |
|--------|-----|---|--------|
| GFC | -0.142 | 158 | FAIL |
| COVID | 0.837 | 89 | PASS |

## Regime Detection
- High volatility days (VIX > 75th pct): 1294
- Sustained high volatility days (21+ consecutive): 405

## Interpretation
Coherence gate FAILED. Do NOT interpret regime transitions as FIT-consistent.
