# Results (scRNA Commitment, Tier-2 / P11-style, EST-gated)

This file summarizes **completed, auditable runs** under `outputs_runs/`.

Interpretation rules:

- `OK_PER_WINDOW` means the preregistered estimator pair passes the coherence gate **within the chosen windowing**.
- `ESTIMATOR_UNSTABLE` means the coherence gate fails (including **sign mismatch** against `expected_sign`).
- For Tier-2 reporting, prefer axes with explicit semantics (see “Axis strength” below).

## Summary table (current portfolio)

| Run ID | Dataset | Axis | Mixing label | Estimators (C1 vs C2) | expected_sign | n_windows | rho | p | Verdict | Evidence |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| `pancreas_endocrinogenesis_day15` | `file:data/raw/pancreas_endocrinogenesis_day15.h5ad` | `pseudotime` | `obs:clusters` | `C_dim_collapse` vs `C_mixing` | `+1` | 17 | -0.154 | 0.554 | `ESTIMATOR_UNSTABLE` | `outputs_runs/evidence_pancreas_day15.zip` |
| `pancreas_endocrinogenesis_day15_purity` | `file:data/raw/pancreas_endocrinogenesis_day15.h5ad` | `pseudotime` | `obs:clusters` | `C_dim_collapse` vs `C_label_purity` | `+1` | 17 | 0.353 | 0.165 | `OK_PER_WINDOW` | `outputs_runs/evidence_pancreas_day15_purity.zip` |
| `gastrulation_e75_purity` | `file:data/raw/gastrulation_e75.h5ad` | `obs:stage` | `obs:celltype` | `C_dim_collapse` vs `C_label_purity` | `+1` | 17 | 0.581 | 0.0145 | `OK_PER_WINDOW` | `evidence_gastrulation_e75_purity.zip` |
| `gastrulation_e75_mixing` | `file:data/raw/gastrulation_e75.h5ad` | `obs:stage` | `obs:celltype` | `C_dim_collapse` vs `C_mixing` | `+1` | 17 | 0.306 | 0.232 | `OK_PER_WINDOW` | `evidence_gastrulation_e75_mixing.zip` |
| `gastrulation_e75_purity_mixing` | `file:data/raw/gastrulation_e75.h5ad` | `obs:stage` | `obs:celltype` | `C_label_purity` vs `C_mixing` | `+1` | 17 | 0.502 | 0.0398 | `OK_PER_WINDOW` | `evidence_gastrulation_e75_purity_mixing.zip` |
| `moignard15_exporder_leidenfixed_purity` | `file:data/raw/moignard15_exporder_leiden_fixed.h5ad` | `obs:exp_order` | `obs:leiden_fixed` | `C_dim_collapse` vs `C_label_purity` | `+1` | 3 | -1.000 | 0.0 | `ESTIMATOR_UNSTABLE` | `outputs_runs/evidence_moignard15_exporder_leidenfixed_purity.zip` |
| `nestorowa16_zenodo_purity` | `file:data/raw/nestorowa16_hsc_2016.h5ad` | `obsm:X_pca:0` | `obs:cell_types_broad_cleaned` | `C_dim_collapse` vs `C_label_purity` | `+1` | 17 | 0.447 | 0.0719 | `OK_PER_WINDOW` | `outputs_runs/evidence_nestorowa16_zenodo_purity.zip` |
| `dentategyrus_age_purity` | `file:data/raw/dentategyrus_10X43_1.h5ad` | `obs:age(days)` | `obs:clusters` | `C_dim_collapse` vs `C_label_purity` | `+1` | 3 | 0.500 | 0.667 | `OK_PER_WINDOW` | `outputs_runs/evidence_dentategyrus_age_purity.zip` |

Notes:

- The coherence threshold in these runs is `rho >= 0.2` with `expected_sign = +1` (see each run's `PREREG.locked.yaml` and `coherence_report.json`).
- The **strongest "explicit-axis" anchor** in this portfolio is `gastrulation_e75_purity` (windowing axis = `obs:stage`).
- **Same-boundary contrast** (gastrulation): Under the same axis (`obs:stage`) and boundary, `C_mixing` achieves marginal pass (rho=0.306, p=0.232, not significant) while `C_label_purity` is stronger and significant (rho=0.581, p=0.0145). This demonstrates that estimator family selection affects coherence strength, not just pass/fail.

## Estimator Family Grid (gastrulation_e75)

**Fixed boundary**: `obs:stage` × `obs:celltype` (window_q=0.20, stride_q=0.05, min_cells=500)

This grid tests all 3 pairs from 3 estimators under identical windowing:

| Pair | C1 | C2 | ρ | p-value | Verdict |
|------|----|----|---|---------|---------|
| 1 | C_dim_collapse | C_label_purity | **0.581** | 0.0145 | PASS (significant) |
| 2 | C_dim_collapse | C_mixing | 0.306 | 0.232 | PASS (marginal) |
| 3 | C_label_purity | C_mixing | **0.502** | 0.0398 | PASS (significant) |

**Findings**:

1. **All pairs PASS** the coherence gate (threshold ρ ≥ 0.20), confirming the gastrulation dataset is suitable for FIT analysis under this boundary.
2. **Pair 1** (dim_collapse × label_purity) shows strongest coherence (ρ=0.58), significant at p<0.05.
3. **Pair 3** (label_purity × mixing) is the second-strongest (ρ=0.50), also significant.
4. **Pair 2** (dim_collapse × mixing) passes but is weakest (ρ=0.31) and not statistically significant.
5. **Interpretation**: When both C_label_purity and C_mixing are available, prefer C_label_purity for tighter coherence. The fact that all three pairs pass suggests robust estimator family coverage for this biological system.

## Axis strength (for Tier-2 claims)

Windowing axes are not equally “hard”:

1. **Strong**: `obs:stage` / `obs:day` / `obs:timepoint` (externally meaningful experimental axis)
2. **Medium**: `obs:age` (meaningful, but often sparse / coarse)
3. **Weak (coordinate-only)**: `obsm:*` axes (explicit coordinates, but not “time” without extra semantics)
4. **Weakest**: `pseudotime` (inferred; useful for exploration and internal consistency checks)

Rule of thumb: if a finding only exists under `pseudotime`, treat it as **suggestive** rather than a Tier-2 anchor.

## Where artifacts live (per run)

Each run directory under `outputs_runs/<run_id>/` contains:

- `PREREG.locked.yaml`
- `metrics_log.parquet`
- `coherence_report.json`
- `regime_report.md`
- `tradeoff_onepage.png` and `tradeoff_onepage.pdf`
- `fail_windows.md`

Evidence bundles (ZIP) are in `outputs_runs/evidence_*.zip`.

## Reproduction (single run)

```bash
python run_pipeline.py --prereg EST_PREREG_gastrulation_e75_purity.yaml
python package_evidence.py --main_dir outputs_runs/gastrulation_e75_purity --out evidence_gastrulation_e75_purity.zip
```
