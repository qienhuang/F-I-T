# Subcase v1.8 — Dual‑Oracle Active Acquisition (Cost‑Aware + Joint Coverage Jump + Frontier/Envelope)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_8`  
**Pack version:** `v1.8_repo_ready`  
**Lineage:** v1.6 (joint cov jump) → v1.7 (cost-aware + jump_type) → **v1.8 (frontier + post‑hoc envelope reference + sensitivity grid)**

This subcase is a FIT/EST training instrument:

- **Boundary discipline:** explicit boundary switches across `B0 → B1 (PAE) → B2 (MSA)` acquisition.
- **Monitorability discipline:** low‑FPR cap operation + explicit **FPR floors** (degenerate alarms are rejected).
- **Phase-like observable:** a discrete **joint coverage jump** `E_covjump_joint` under a locked protocol.
- **Cost discipline:** budgets are explicit **oracle costs**, not vague “labels”.
- **Decision trace discipline:** selection and acquisition decisions are logged as first‑class artifacts.

---

## 0) What is new in v1.8

### 0.1 Frontier one‑pager (Pareto surfaces)

New artifacts:

- `frontier_onepage.pdf`
- `frontier_table.csv`

The frontier one‑pager is a policy comparison surface built from:

- `cost_to_joint_usable`, `cost_to_covjump_joint`
- `final_cov_joint_at_cap`
- and Pareto flags.

### 0.2 Post‑hoc envelope reference (not deployable)

We compute a **post‑hoc envelope** across policies:

- for each cost level, take the best `cov_joint` achieved by any policy at or below that cost,
- and draw this as a dashed reference in `frontier_onepage.pdf`.

This is explicitly **not deployable**: it is a hindsight upper bound used to calibrate “how much headroom remains” inside the preregistered policy family.

### 0.3 Jump‑type sensitivity grid (preregistered)

New prereg field:

- `event.availability_delay_grid: [0, 1, 2]` (default)

New artifact:

- `jump_type_sensitivity.json`

This reports how `jump_type` changes under different preregistered delay thresholds.

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

## 3) Artifact contract (v1.8)

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
- `frontier_onepage.pdf` (**NEW**)
- `frontier_table.csv` (**NEW**)
- `jump_type_sensitivity.json` (**NEW**)
- `policy_cards_index.md`
- `policy_cards/` (markdown cards)
- `policy_cards/assets_manifest.json`
- `leakage_audit.json`
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`
