# REPRO_CHECKLIST — Active Acquisition (PAE Proxy Alarm v0.2)

---

## 1) Preconditions

You must have a parent case run with:

- `metrics_per_protein.parquet` (or `.csv`)  
- containing `C2_pae_offdiag` (PAE label store)

---

## 2) Lock prereg

1) Edit `PREREG.yaml` only for:
   - `data.input_metrics_path`
   - optionally `boundary.tau_pae`
2) Run; it will copy to:
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

## 5) Boundary discipline checks

- Feature whitelist must not include `C2_pae_offdiag`
- Label field must be `C2_pae_offdiag`
- `decision_trace.csv` must show which items were queried and when
