# REPRO_CHECKLIST — Dual‑Oracle + Candidate‑Pool Ablation (v0.8)

---

## 1) Preconditions

You must have a parent case run whose `metrics_per_protein.parquet` includes:

- B0 feature columns
- `C2_pae_offdiag` (PAE oracle store; may be missing for some accessions)
- `msa_depth` (MSA oracle store; may be missing for some accessions)

---

## 2) Lock prereg

Edit `PREREG.yaml` only for:

- `data.input_metrics_path`
- optionally thresholds: `boundary.thresholds.tau_pae`, `boundary.thresholds.tau_msa_depth`
- optionally budgets: `acquisition.oracle_budgets.*`

Run will copy prereg to:

- `out/<run_id>/PREREG.locked.yaml`

---

## 3) Run

From this subcase directory:

```bash
python -m src.run --prereg PREREG.yaml
```

---

## 4) Verify artifacts

In `out/<run_id>/` verify:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 5) Boundary discipline checks (must pass)

- Feature whitelist contains no oracle fields (`C2_pae_offdiag`, `msa_depth`)
- `allocation_trace.csv` contains per (policy, round):
  - `q_pae`, `q_msa`, `gap_pae`, `gap_msa`
  - `tpr_val_*`, `fpr_val_*` (policy diagnostics)
- Holdout metrics are not used for acquisition decisions:
  - allocation decisions are based on val diagnostics only
- no repeated (accession, oracle_type) queries
- For candidate pool ablation:
  - `decision_trace.csv` includes `candidate_pool_basis_used` for composite policies:
    - `uncertainty` for `*_uK`
    - `random_hash` for `*_rK`
