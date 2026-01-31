# Subcase v1.9 — Dual‑Oracle Active Acquisition (Cost‑Aware + Jump + Frontier/Envelope + Baseline + Card Sensitivity)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_9`  
**Pack version:** `v1.9_repo_ready`  
**Lineage:** v1.7 (cost-aware + jump_type) → v1.8 (frontier + post‑hoc envelope + sensitivity grid) → **v1.9 (baseline envelope + jump-type layering + sensitivity in policy cards)**

This subcase is a FIT/EST training instrument:

- **Boundary discipline:** explicit boundary switches across `B0 → B1 (PAE) → B2 (MSA)` acquisition.
- **Monitorability discipline:** low‑FPR cap operation + explicit **FPR floors** (degenerate alarms are rejected).
- **Phase-like observable:** a discrete **joint coverage jump** `E_covjump_joint` under a locked protocol.
- **Cost discipline:** budgets are explicit **oracle costs**, not vague “labels”.
- **Decision trace discipline:** selection and acquisition decisions are logged as first‑class artifacts.

---

## 0) What is new in v1.9

### 0.1 Frontier is now layered by `jump_type`

`frontier_onepage.pdf` now encodes `jump_type` directly (marker shapes):

- `availability_driven`
- `learning_driven`
- `none`

This makes the frontier a **regime-comparison surface**, not just a scatter plot.

### 0.2 Baseline envelope (random-policy family) vs post‑hoc envelope (policy family)

In Panel A we now plot two dashed references:

- **baseline envelope:** computed only from policies whose `allocation_policy == random` OR policy name contains `random`
- **post‑hoc envelope:** computed across the full preregistered policy family

This separation makes “strategy headroom” vs “boundary headroom” legible.

### 0.3 Frontier table now includes headroom/gain scalars

`frontier_table.csv` now includes (per policy):

- `envelope_cov_at_final_cost`
- `baseline_env_cov_at_final_cost`
- `headroom_to_envelope_at_final_cost`
- `gain_over_baseline_env_at_final_cost`

These are deliberately simple: they are not “theory”; they are audit-friendly deltas.

### 0.4 Policy cards embed jump-type sensitivity grid

Each policy card now includes a small table:

- `jump_type_by_delay` for `event.availability_delay_grid` (preregistered)

This prevents post‑hoc threshold storytelling during writeups.

---

## 1) Quickstart (real data)

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:

- set `data.input_metrics_path` to your parent case metrics file (parquet/csv)

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.

---

## 2) Quickstart (smoke test + CI-style gate)

From this directory:

```bash
bash scripts/ci_check.sh
```

It will:

1) generate `data/synthetic_metrics.csv`  
2) run the case with `PREREG_SMOKE.yaml` to `out_smoke/SMOKE/`  
3) validate required artifacts + audits

---

## 3) Artifact contract (v1.9)

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `holdout_snapshot.json`
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
- `regime_timeline.csv`
- `regime_summary.json`
- `policy_table.csv`
- `cost_summary.json`
- `frontier_onepage.pdf`
- `frontier_table.csv` (**updated columns**)
- `jump_type_sensitivity.json`
- `policy_cards_index.md`
- `policy_cards/` (markdown cards)
- `policy_cards/assets_manifest.json`
- `leakage_audit.json`
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`
