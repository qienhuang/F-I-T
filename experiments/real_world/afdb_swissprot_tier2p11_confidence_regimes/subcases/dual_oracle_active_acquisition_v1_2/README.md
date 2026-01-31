# Subcase v1.2 — Dual‑Oracle Active Acquisition (Δ‑Lag + Policy Table + Holdout Snapshot + Leakage Audit)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_2`  
**Pack version:** `v1.2_repo_ready`  
**Lineage:** v1.0 (regimes) → v1.1 (Δ + leakage audit) → **v1.2 (policy_table + holdout_snapshot + smoke test)**

This is a FIT/EST training instrument: it forces **boundary discipline** and **monitorability discipline** under low FPR caps for two oracle channels (PAE + MSA).

---

## 0) What is new in v1.2

### 0.1 `policy_table.csv` (human/LLM‑friendly summary)

New artifact:

- `out/<run_id>/policy_table.csv`

One row per policy:

- event markers: floor‑resolved, enter‑usable, joint‑usable
- Δ‑lag:  $ \Delta = r\_{joint} - \max(r^{pae}\_{floor}, r^{msa}\_{floor}) $
- final holdout operating‑point stats: TPR@cap, FPR_floor@TPRmin
- proxy quality: MAE(  $ \widehat{C3} $  )
- leakage audit pass/fail

### 0.2 `holdout_snapshot.json` (audit hash of holdout IDs)

New artifact:

- `out/<run_id>/holdout_snapshot.json`

It contains:

- holdout counts
- SHA256 of the sorted holdout ID lists
- a few examples only (not the full list)

This gives you a stable audit handle without shipping huge ID lists.

### 0.3 Smoke test protocol (no parent run required)

Files:

- `PREREG_SMOKE.yaml`
- `scripts/make_synthetic_metrics.py`
- `scripts/smoke_test.sh`

Use these to validate the subcase runs end‑to‑end on synthetic data.

---

## 1) Quickstart (real data)

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:

- set `data.input_metrics_path` to your parent run file (parquet or csv)

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.

---

## 2) Quickstart (smoke test)

From this directory:

```bash
bash scripts/smoke_test.sh
```

It will:

1) generate `data/synthetic_metrics.csv`  
2) run `python -m src.run --prereg PREREG_SMOKE.yaml --run_id SMOKE`  
3) print the output directory path

---

## 3) Artifact contract

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `holdout_snapshot.json` (**NEW**)
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
- `regime_timeline.csv`
- `regime_summary.json`
- `policy_table.csv` (**NEW**)
- `leakage_audit.json`
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`
