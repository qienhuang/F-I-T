# Benchmarks (specs + templates)

This folder contains **benchmark specifications** (not full toolkits) that standardize:

- what counts as an event (evaluability)
- how positives/negatives are labeled (windows, horizons, safe gaps)
- what outcomes must be reported (especially operational alarm metrics like achieved FPR and FPR floors)
- preregistration templates and machine-readable result schemas

If you want runnable engines, start from `tools/README.md`.

## Index

- **GMB v0.4 — Grokking Monitorability Benchmark**: `docs/benchmarks/gmb_v0_4/README.md`
  - Companion note (why AUC can mislead under low-FPR): `docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md`

- **Li² scaling-law cross‑M spot check (v4)**: `docs/benchmarks/li2_scaling_law_cross_m_v4/README.md`

- **Li² scaling-law cross‑M spot check (v5)**: `docs/benchmarks/li2_scaling_law_cross_m_v5/README.md`
