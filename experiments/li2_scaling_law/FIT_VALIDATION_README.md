# FIT Validation Protocol for Li2 Scaling Law

This document describes the minimal reproducible protocol for validating the FIT framework's accuracy on Li2 grokking experiments.

## Quick Start

```bash
# Validate a new M value (full pipeline)
python run_fit_validation.py --M 71 --ratios 0.38,0.40,0.42,0.44,0.46,0.48,0.50,0.52

# Re-analyze existing results
python run_fit_validation.py --M 71 --ratios 0.38,0.42,0.46,0.50 --skip_training --results_dir results/beta_multiseed_v2
```

## GPU runbook (cross-M, single card)

If you have a single consumer GPU (e.g., RTX 3090), the easiest paper-ready extension is a small **cross-M** slice
using the unified runner, keeping the same protocol and adding new M values.

Runbook: `RUNBOOK_3090_CROSS_M.md`

```powershell
pwsh ./run_cross_m_3090.ps1 -Ms "97,127" -Seeds "42,123,456" -Ratios "0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48" -OutputRoot "results/beta_multiseed_v4"
```

Tips:
- Ensure there is at least 1 ratio below the boundary (0% grok) and multiple above the boundary (100% grok) so `r_crit` is estimable.
- By default, fits use only fully reliable points (`min_prob=1.0`) and require 3+ points above `r_crit`. You can override via flags below.

## Protocol Overview

Given `(M, ratios, seeds)`, the protocol produces:

| Output | Description | File |
|--------|-------------|------|
| r_crit | Critical training ratio (p(grok)=0.5) | `beta_analysis/beta_transition_analysis.json` |
| beta_epoch | Exponential fit on grok_epoch | `beta_analysis/beta_transition_analysis.json` |
| beta_delay | Exponential fit on grok_delay | `grok_speed/grok_speed_fit_delay.json` |
| PT-MSS plots | Multi-signal phase alignment | `pt_mss_plots/*.png` |

## Unified entry point

`run_fit_validation.py` is the one-command protocol runner. It orchestrates:
- training (`train.py`)
- beta analysis (`analyze_beta_transition.py`)
- grok speed analysis (`analyze_grok_speed.py --use_delay`)
- PT-MSS phase plots (`pt_mss_phase_plot.py`)

### Tuning knobs (CLI flags)

`run_fit_validation.py` forwards these knobs to the analysis scripts:
- `--beta_min_prob`, `--beta_min_points`
- `--speed_min_prob`, `--speed_min_points`
- `--speed_max_delta_r` (cap to near-boundary points; useful when far-above-boundary runs show early generalization)
- `--phase_plots`

## Component Scripts

### 1) `train.py`

Runs a single grokking experiment.

```bash
python train.py --M 71 --ratio 0.44 --seed 42 --hidden_dim 2048 \
  --activation quadratic --lr 0.001 --weight_decay 0.001 \
  --epochs 25000 --output_dir results/my_experiment
```

Output: `M71_ratio0.440_seed42.json` with `grok_happened`, `grok_epoch`, and `history`.

### 2) `analyze_beta_transition.py`

Analyzes beta (grok speed sensitivity) across M values.

```bash
python analyze_beta_transition.py --results_dir results/beta_multiseed_v2 \
  --output_dir results/analysis --min_prob 1.0 --min_points 3
```

Key outputs:
- `beta_transition_report.md` - human-readable summary
- `beta_transition_analysis.json` - machine-readable data
- `beta_transition_analysis.png` - visualization

### 3) `analyze_grok_speed.py`

Fits exponential/power-law models to time-to-grok vs `(r - r_crit)`.

```bash
python analyze_grok_speed.py --results_dir results/beta_multiseed_v2 \
  --output_dir results/analysis --use_delay
```

`--use_delay` uses `grok_delay = grok_epoch - mem_epoch` instead of raw `grok_epoch`.

### 4) `pt_mss_phase_plot.py`

Generates multi-signal phase alignment plots (acc, loss, `gf_norm`, alignment proxy).

```bash
python pt_mss_phase_plot.py --inputs "results/*.json" --out_dir results/plots --write_md
```

## Recommended Experiment Design

### For `r_crit` estimation
- Include at least 1 ratio below the expected boundary (should have 0% grok rate)
- Include at least 1 ratio at/near the boundary (should have ~50% grok rate)
- Include 3+ ratios above the boundary (should have 100% grok rate)

### For beta estimation
- Use `min_prob=1.0` to only include ratios with 100% grok rate
- Need at least 3 points above `r_crit` for a valid fit
- 5-7 points recommended for robust estimation

### Multi-seed validation
- Default seeds: `42,123,456`
- Use 3+ seeds per ratio for robustness
- Report median grok_epoch across seeds (plus spread if needed)

## Current Results (as of 2026-01)

| M | r_crit | beta | R^2 | N_points |
|---|--------|------|-----|----------|
| 30 | 0.515 | 16.2 | 0.80 | 8 |
| 45 | 0.466 | 39.7 | 0.97 | 7 |
| 71 | 0.415 | 38.6 | 0.94 | 5 |

Key finding: beta shows regime structure (low at M=30; high at M=45 and M=71) under this fixed configuration.

## Directory Structure

```
li2_scaling_law/
  train.py
  analyze_beta_transition.py
  analyze_grok_speed.py
  pt_mss_phase_plot.py
  run_fit_validation.py
  FIT_VALIDATION_README.md
  results/
    beta_multiseed_v2/
      M30_ratio*.json
      M45_ratio*.json
      M71_ratio*.json
      analysis_final_v2/
      analysis_delay_final/
      pt_mss_plots/
```

## Interpretation Guidelines

1. `r_crit` is estimated from probability crossing, not a single 0/1 run.
2. `beta` is an operational slope, not a physical constant.
3. High `R^2_log` (>0.95) suggests the local log-linear fit is a good description over the sampled band; lower values often indicate noise or mixed dynamics.
4. PT-MSS plots are the multi-signal audit layer; they should show coherent timing relationships across signals.

## Troubleshooting

- "r_crit could not be estimated": ensure you have both below-boundary (0% grok) and above-boundary (100% grok) ratios.
- Low R^2 for beta fit: may indicate noise, near-critical slowing contamination, or insufficient points above r_crit.
- Non-monotonic `T_grok`: can be real near the boundary; check `grok_delay` and PT-MSS plots for interpretation.
