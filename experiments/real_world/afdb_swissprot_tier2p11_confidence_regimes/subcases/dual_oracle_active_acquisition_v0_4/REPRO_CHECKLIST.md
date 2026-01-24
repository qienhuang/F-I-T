# REPRO_CHECKLIST — Dual‑Oracle Active Acquisition + Joint Gate (v0.4)

---

## 1) Preconditions

You must have a parent case run whose `metrics_per_protein.parquet` includes:

- B0 feature columns
- `C2_pae_offdiag` (PAE oracle store)
- `msa_depth` (MSA oracle store)

---

## 2) Lock prereg

Edit `PREREG.yaml` only for:

- `data.input_metrics_path`
- optionally thresholds: `boundary.thresholds.tau_pae`, `boundary.thresholds.tau_msa_depth`
- optionally budgets: `acquisition.oracle_budgets.*`

Run will copy prereg to:

- `out/<run_id>/PREREG.locked.yaml`

If you change any other field after seeing results, treat it as a new study.

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
- `round_metrics.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 5) Boundary discipline checks (must pass)

- Feature whitelist contains no oracle fields (`C2_pae_offdiag`, `msa_depth`)
- `decision_trace.csv` records **oracle_type** for every query
- Queried label counts match prereg budgets (or stop because pool exhausted)
- No repeated queries for the same (accession, oracle_type) pair
