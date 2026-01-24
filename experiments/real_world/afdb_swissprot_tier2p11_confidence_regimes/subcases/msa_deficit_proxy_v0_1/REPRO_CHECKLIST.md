# REPRO_CHECKLIST — MSA Deficit Proxy (v0.1)

---

## 1) Preconditions

You must have a parent case **B2** run with:

- `metrics_per_protein.parquet` (or `.csv`)  
- containing `msa_depth` (and ideally `C3_msa_deficit`)

---

## 2) Lock prereg

1) Edit `PREREG.yaml` only for:
   - `data.input_metrics_path`
   - optionally `boundary.event.tau_msa_depth`
2) Run; it will copy to:
   - `out/<run_id>/PREREG.locked.yaml`

If you change anything else after seeing results, treat it as a new study.

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
- `model.joblib`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 5) Boundary discipline checks

- Feature whitelist contains no MSA or PAE fields
- Labels are from MSA channel only (`msa_depth` / `C3_msa_deficit`)
