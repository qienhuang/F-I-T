# FRED Recession Cycles - Run Diagnostics

## Run Config
- Data directory: `../data/raw`
- Output directory: `../outputs/run001`
- Boundary: 1990-01-01 to 2024-12-31
- Months loaded: 840

## Coherence Gate
- **Status: OK_TO_INTERPRET**

### H2: Leading Index vs Recession Probability
- Expected: rho < -0.4 (negative correlation)
- Actual: rho = -0.626
- Status: **PASS**

### Pooled Coherence
| Pair | rho | n | Status |
|------|-----|---|--------|
| L_idx_vs_P_rec | -0.626 | 362 | PASS |
| C_claims_vs_C_ff | N/A | 0 | INSUFFICIENT_DATA |
| I_sent_vs_L_idx | 0.418 | 362 | PASS |
| C_yield_curve_vs_P_rec | N/A | 0 | INSUFFICIENT_DATA |

### Recession Period Coherence (C_claims vs C_ff)
| Period | rho | n | Status |
|--------|-----|---|--------|
| Recession_1990 | N/A | 0 | INSUFFICIENT_DATA |
| Recession_2001 | N/A | 0 | INSUFFICIENT_DATA |
| Recession_2008 | N/A | 0 | INSUFFICIENT_DATA |
| Recession_2020 | N/A | 0 | INSUFFICIENT_DATA |

## Recession Periods Detected
| Start | End |
|-------|-----|
| 1990-08-01 | 1991-04-01 |
| 2001-04-01 | 2001-12-01 |
| 2008-01-01 | 2009-07-01 |
| 2020-03-01 | 2020-05-01 |

## Interpretation
Coherence gate PASSED. Proceed with regime analysis.
