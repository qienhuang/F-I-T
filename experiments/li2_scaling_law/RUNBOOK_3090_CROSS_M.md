# Li2 scaling-law: 3090 cross-M runbook (resumable)

This runbook is designed for a single GPU (e.g., RTX 3090) on Windows.

Goal: extend the Li2 scaling-law evidence from a single M (e.g., M=97) to a small **cross-M** slice (e.g., M=127),
with **resumable** outputs and paper-ready artifacts.

## Preconditions

From `experiments/li2_scaling_law/`:

```powershell
python -c "import torch; print('cuda_available=', torch.cuda.is_available()); print('device=', (torch.cuda.get_device_name(0) if torch.cuda.is_available() else None))"
```

If `cuda_available` is `False`, install a CUDA-enabled PyTorch build first (do not proceed on CPU for these runs).

## Recommended design (cross-M, minimal but robust)

- Seeds: `42,123,456` (3 seeds for probability-based `r_crit`)
- Ratios (starter grid): `0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48`
  - This grid brackets the M=97 boundary (`r_crit ~ 0.39`) and provides enough above-boundary points for beta fits.
- Outputs:
  - `results/beta_multiseed_v4/M97/` (optional refresh; should be mostly SKIP if already done)
  - `results/beta_multiseed_v4/M127/` (new)

## One-command runner (preferred)

```powershell
pwsh ./run_cross_m_3090.ps1 -Ms "97,127" -Seeds "42,123,456" -Ratios "0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48" -OutputRoot "results/beta_multiseed_v4"
```

## Manual runner (if you prefer explicit commands)

```powershell
# M=97 (mostly SKIP if already present)
python run_fit_validation.py --M 97 --ratios "0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48" --seeds "42,123,456" --output_dir "results/beta_multiseed_v4/M97"

# M=127 (new)
python run_fit_validation.py --M 127 --ratios "0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48" --seeds "42,123,456" --output_dir "results/beta_multiseed_v4/M127"
```

## What to report (paper-ready minimum)

For each M:

- `beta_analysis/beta_transition_report.md`
- `grok_speed/grok_speed_fit_delay.json` (+ `.png`)
- `pt_mss_plots/*.png` (at least 2 representative plots)

Across Ms:

- A short table: `M, r_crit, beta, N_points, fit_valid`
- A "scope note" if any M fails `r_crit` estimation (this is still a valid result).

