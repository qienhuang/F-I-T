# Li² scaling-law cross‑M spot check (v4)

This benchmark entry links a small cross‑M slice of the Li² scaling-law replication runs into the `docs/benchmarks/` index.

This is **not** a standalone benchmark engine. The runnable code lives in:

- `experiments/li2_scaling_law/`

## What is included

Multi-seed cross‑M runs (GPU) for:

- `M=97`
- `M=127`

Artifacts (per M) include:

- probability-based `r_crit` estimate (from multi-seed grok probability crossing)
- beta transition report (`beta_analysis/`)
- grok-speed fit (delay-based) (`grok_speed/`)
- phase plots (`pt_mss_plots/`)

## Where to look

- Runbook: `experiments/li2_scaling_law/RUNBOOK_3090_CROSS_M.md`
- Results root: `experiments/li2_scaling_law/results/beta_multiseed_v4/`
- Cross‑M summary note: `experiments/li2_scaling_law/results/beta_multiseed_v4/_cross_m_summary.md`

## Reproduce

From `experiments/li2_scaling_law/`:

```powershell
pwsh ./run_cross_m_3090.ps1 -Ms "97,127" -Seeds "42,123,456" -Ratios "0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48" -OutputRoot "results/beta_multiseed_v4"
```
