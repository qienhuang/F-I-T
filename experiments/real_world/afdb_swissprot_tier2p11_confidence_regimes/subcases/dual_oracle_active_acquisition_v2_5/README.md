# Subcase v2.0 — Dual‑Oracle Active Acquisition (Robust Baseline Band + CI‑Gated Frontier)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v2_0`  
**Pack version:** `v2.0_repo_ready`  
**Date locked:** 2026‑01‑25

v2.0 is a *hardening* release: we do not change boundary definitions, estimator semantics, or event rules.
We change **how we justify claims** by introducing a **multi‑seed random baseline band** and a **CI‑gated margin test**.

---

## What’s new in v2.0

### 1) Baseline band (multi‑seed random family)
We run the preregistered baseline family policy:

- `random_hash__random_hash`

over a preregistered seed grid:

- `robustness.baseline.seeds`

and aggregate a cost‑aligned band (default: q10–q90).

Artifact:

- `baseline_band.json`

### 2) Robust frontier vs baseline band (margin + CI)
For each policy, compute:

- `baseline_band_upper_at_final_cost`
- `margin_vs_baseline_upper`
- bootstrap CI of the margin (preregistered)

Artifact:

- `frontier_robust_table.csv`

### 3) Claims gate (machine‑checkable wording constraint)
Artifact:

- `claims_gate_report.json`

Rule:

- allow “outperforms random” only if `dominance_margin_ci_low > 0`

---

## How to run

### A) Baseline grid

```bash
python scripts/run_baseline_grid.py --prereg PREREG.yaml --out_root out_baseline
```

### B) One main run (policy family)

```bash
python -m src.run --prereg PREREG.yaml --run_id MAIN
```

### C) Aggregate band + robust frontier + gate

```bash
python scripts/aggregate_v2_0.py --main_run out/MAIN --baseline_root out_baseline
```

---

## Smoke test

```bash
bash scripts/ci_check.sh
```

## v2.1 addition

- `scripts/generate_claims.py` generates `Claims.md` and `claims_templates.json` from the CI-gated robust table.
## v2.2 addition — policy multi-seed robustness (band + phase-event distribution)

v2.2 extends v2.0/v2.1 by adding a **policy multi-seed grid**:

- baseline band: random family over preregistered baseline seeds
- policy band: policy family over preregistered policy seeds

New scripts:

- `scripts/run_policy_grid.py` (policy seeds → `POLICY_*` runs)
- `scripts/aggregate_v2_2.py` (writes into the representative main run directory)

New artifacts written to `out/<MAIN>/`:

- `policy_band.json`
- `frontier_policy_robust_table.csv`
- `policy_grid_manifest.json`
- `jump_robustness.json` (aggregated across policy seeds)

Claims are generated from `frontier_policy_robust_table.csv` (preferred if present).

## v2.3 addition — bilevel bootstrap robustness (baseline × policy)

v2.3 upgrades the robustness story from **policy-seed only** to **bilevel uncertainty**:

- We resample **baseline seeds** (random family) and **policy seeds** (policy family) together.
- In each bootstrap replicate we recompute the **baseline upper quantile** at each policy-seed cost, then compute the **mean margin** over resampled policy seeds.
- Claims gating uses the bilevel CI:

> allow “outperforms random” only if `bilevel_margin_ci_low > 0`

New artifacts written into `out/<MAIN>/` by `scripts/aggregate_v2_3.py`:

- `frontier_bilevel_robust_table.csv`
- `bilevel_bootstrap_summary.json`

Notes:

- `frontier_policy_robust_table.csv` is still written for continuity, but **v2.3 claims use the bilevel table**.
- `scripts/generate_claims.py` prefers bilevel > policy-seed > baseline-only.

## v2.4 addition — tail-robust operational advantage gate (bilevel bootstrap quantile margin)

v2.4 strengthens the “outperforms random” gate from **mean-margin robustness** to an **operational tail margin**:

- In each bilevel bootstrap replicate, we compute the margin vector across policy-seed outcomes:
  `margin_i = cov_joint_at_cap_i − baseline_upper_q(cost_i)`
- We then compute:
  - **mean margin** (secondary statistic)
  - **tail-q margin** (primary statistic): `quantile_q(margin)` with `q = 0.10`

Claims gate:

> allow “outperforms random” only if `bilevel_tail_margin_ci_low > 0`.

This makes the claim resilient to “rare bad runs”, and is closer to **monitorability-grade operational reliability** than a mean-only gate.

Artifacts:

- `frontier_bilevel_robust_table.csv` now includes both mean and tail CI columns.
- `claims_gate_report.json` uses `mode=bilevel_bootstrap_tail`.

## v2.5 addition — tail-quantile sweep + min-over-q operational gate (bilevel bootstrap)

v2.5 strengthens v2.4 by removing dependence on a *single* tail quantile.

Instead of gating on one chosen tail quantile (e.g., q=0.10), we preregister a **tail quantile sweep**:

- `tail_quantiles = {0.05, 0.10, 0.20}` (default; see PREREG)

In each bilevel bootstrap replicate we compute:

- `mean_margin = mean(margins)`
- `tail_margin_q = quantile_q(margins)` for each `q` in `tail_quantiles`
- `tail_min_margin = min_q tail_margin_q`  (worst-case across preregistered quantiles)

Claims gate:

> allow “outperforms random” only if `bilevel_tail_min_margin_ci_low > 0`.

This makes the “advantage” claim robust to:
- rare bad policy runs (tail sensitivity), and
- the analyst’s choice of which tail quantile to report (quantile sweep discipline).

Artifacts:

- `frontier_bilevel_robust_table.csv` includes:
  - per-q tail CI columns: `bilevel_tail_q05_*`, `bilevel_tail_q10_*`, `bilevel_tail_q20_*`
  - min-over-q CI columns: `bilevel_tail_min_*` (used for gating)
- `bilevel_bootstrap_summary.json` records the `tail_quantiles` sweep used.
