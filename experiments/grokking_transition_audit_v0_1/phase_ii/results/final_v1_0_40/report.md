# Phase-II v1.0 Final 40-Seed Attractor Stability Report

## Verdict: **ATTRACTOR_SUPPORTED** (2/2 metrics required)

## Setup
- Seeds: 40 (140–179)
- Grokked: step_300000 checkpoints (40 seeds)
- Pre-grok: step_5000 checkpoints (40 seeds)
- Design: within-seed matched (same seeds, different checkpoint)
- Primary matrix: `embed.weight`
- Perturbations: Gaussian + rank-1, scales 0.5/1/2/5% of ||W||_F
- Recovery horizon: 2000 steps

## Metrics (primary matrix, aggregated over all perturb conditions)

| Metric | Grokked | Pre-grok | Effect | Min required | Pass |
|---|---:|---:|---:|---:|:---:|
| t50 (steps) | 0 | 0 | nanx | ≥1.5x | fail |
| t90 (steps) | 0 | 2000 | nanx | ≥1.5x | fail |
| AUC [0,2000] | 0.916 | 0.514 | Δ=+0.402 | ≥0.10 | PASS |
| Unrecov@2000 (%) | 11.2% | 100.0% | Δ=+88.8pp | ≥20pp | PASS |

## Files
- `D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\results\final_v1_0_40\per_seed_metrics.csv`
- `D:\FIT Lab\github\F-I-T\experiments\grokking_transition_audit_v0_1\phase_ii\results\final_v1_0_40\summary.json`
