# Phase-II v1.0 Attractor Stability Report

## Verdict: **ATTRACTOR_SUPPORTED** (3/2 metrics required)

## Setup
- Grokked: step_300000 (10 seeds)
- Pre-grok: step_5000 (10 seeds)
- Design: within-seed matched (same 10 seeds, different checkpoint)
- Primary matrix: `embed.weight`
- Perturbations: Gaussian + rank-1, scales 0.5/1/2/5% of ||W||_F
- Recovery horizon: 2000 steps

## Metrics (primary matrix, all scales/perturb types aggregated)

| Metric | Grokked | Pre-grok | Effect | Min required | Pass |
|---|---:|---:|---:|---:|:---:|
| t50 (steps) | 0 | 0 | 1.0x | >=1.5x | fail |
| t90 (steps) | 0 | 2000 | 2000000000001.0x | >=1.5x | PASS |
| AUC [0,2000] | 0.918 | 0.508 | delta=0.410 | >=0.10 | PASS |
| Unrecov@2000 (%) | 10.0% | 100.0% | delta=90.0pp | >=20pp | PASS |

## Files
- `D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\results\main_v1_0\per_seed_metrics.csv`
- `D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\results\main_v1_0\summary.json`
