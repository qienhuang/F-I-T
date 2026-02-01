# Li² scaling-law cross‑M spot check (v5)

This benchmark note links a small cross‑M slice of the Li² scaling-law replication runs into the `docs/benchmarks/` index.

It is **not** a standalone benchmark engine. The runnable code lives in:

- `experiments/li2_scaling_law/`

## What is included

Multi-seed cross‑M runs (GPU) using the same protocol boundary and ratio grid:

- `M=71` (results root: `experiments/li2_scaling_law/results/beta_multiseed_v5/M71/`)
- `M=97` (results root: `experiments/li2_scaling_law/results/beta_multiseed_v4/M97/`)
- `M=127` (results root: `experiments/li2_scaling_law/results/beta_multiseed_v4/M127/`)
- `M=159` (results root: `experiments/li2_scaling_law/results/beta_multiseed_v5/M159/`)

Per‑M artifacts include:

- probability-based `r_crit` estimate (from multi-seed grok probability crossing)
- beta transition report (`beta_analysis/`)
- grok-speed fit (delay-based) (`grok_speed/`)
- PT‑MSS plots (`pt_mss_plots/`)

## Cross‑M summary (operational; scope‑limited)

`r_crit` is estimated from a probability crossing (`p(grok)=0.5`) on the fixed ratio grid.

| M | log(M)/M | r_crit (p=0.5) | c = r_crit / (log(M)/M) | beta (exp) | fit_valid |
|---:|---:|---:|---:|---:|:---:|
| 71  | 0.0600 | 0.415 | 6.91 | 29.59 | ✅ |
| 97  | 0.0472 | 0.385 | 8.16 | 45.11 | ✅ |
| 127 | 0.0381 | 0.350 | 9.18 | 41.34 | ✅ |
| 159 | 0.0319 | **< 0.34** | **< 10.65** | — | ❌ (grid does not straddle boundary) |

Notes:

- For `M=159`, the lowest tested ratio (`r=0.34`) already yields `p(grok)=1.0`. This makes `r_crit` and beta **non-estimable** on this grid. The correct output is an inequality (`r_crit < 0.34`), not a forced fit.
- `beta` is an **operational slope** under the candidate exponential form on the selected points; treat as descriptive unless replicated across more `M` values and sensitivity-checked.

## Reproduce (GPU)

From `experiments/li2_scaling_law/`:

```powershell
pwsh ./run_cross_m_3090.ps1 -Ms "71,97,127,159" -Seeds "42,123,456" -Ratios "0.34,0.36,0.38,0.40,0.42,0.44,0.46,0.48" -OutputRoot "results/beta_multiseed_v5"
```

## Interpretation constraints (EST-style)

- This note is evidence that the pipeline can produce **auditable** `r_crit` and beta under a fixed boundary and fixed estimator family.
- Do not interpret the absolute values as “the scaling law constant” until:
  - more `M` values are included, and
  - sensitivity to the ratio grid / training schedule is documented.

