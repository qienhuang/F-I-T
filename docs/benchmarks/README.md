# Benchmarks (specs + templates)

This folder contains **benchmark specifications** (not full toolkits) that standardize:

- what counts as an event (evaluability)
- how positives/negatives are labeled (windows, horizons, safe gaps)
- what outcomes must be reported (especially operational alarm metrics like achieved FPR and FPR floors)
- preregistration templates and machine-readable result schemas

If you want runnable engines, start from `tools/README.md`.

## Index

- **GMB v0.4 - Grokking Monitorability Benchmark**: [docs/benchmarks/gmb_v0_4/README.md](gmb_v0_4/README.md)
  - Companion note (why AUC can mislead under low-FPR): [docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md](gmb_v0_4/monitorability_boundary_toy_theorem.md)
  - v0.5 repairs (notes + comparisons):
    - **Unified summary (all repairs A/B/C):** [gmb_repairs_unified_summary.md](gmb_repairs_unified_summary.md) *
    - Repair A/B comparison: [gmb_v0_5_repairs_comparison.md](gmb_v0_5_repairs_comparison.md)
    - Repair C analysis: [gmb_v0_5_repairC_results.md](gmb_v0_5_repairC_results.md)
    - Diagnostic note: [gmb_v0_5_repairs_note.md](gmb_v0_5_repairs_note.md)

- **Li^2 scaling-law cross-M spot check (v4)**: [docs/benchmarks/li2_scaling_law_cross_m_v4/README.md](li2_scaling_law_cross_m_v4/README.md)

- **Li^2 scaling-law cross-M spot check (v5)**: [docs/benchmarks/li2_scaling_law_cross_m_v5/README.md](li2_scaling_law_cross_m_v5/README.md)
  - **Cross-M r_crit benchmark (paper-ready, five-point \(M199 pilot\) with visualization):** [li2_cross_m_summary.md](li2_cross_m_summary.md) *
  - Visualization: [li2_rcrit_vs_M_benchmark.png](li2_rcrit_vs_M_benchmark.png) / [.pdf](li2_rcrit_vs_M_benchmark.pdf)

- **AlphaFold DB confidence regimes (AFDB Tier-2/P11)**: [experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes/README.md](../../experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes/README.md)
  - B1 (`coords+PAE`, N~1000): `COHERENT`
  - B2 (`coords+PAE+MSA`, N~1000): `ESTIMATOR_UNSTABLE` due to persistent MSA/PAE event-bin disagreement (structural, not noise)

- **Execution queue (current CPU/GPU run order)**: [EXECUTION_CHECKLIST_2026-02-12.md](EXECUTION_CHECKLIST_2026-02-12.md)

