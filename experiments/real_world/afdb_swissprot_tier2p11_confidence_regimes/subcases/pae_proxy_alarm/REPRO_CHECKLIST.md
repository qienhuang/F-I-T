# REPRO_CHECKLIST — PAE Proxy Alarm (v0.1)

This checklist assumes you already ran the parent case under boundary `B1_COORD_PLUS_PAE`
and have a `metrics_per_protein.parquet` containing the PAE label channel.

---

## 1) Lock prereg

1) Edit `PREREG.yaml` only for:
   - `data.input_metrics_path`
   - `boundary.tau_pae` (if you choose a different event threshold)
2) Run the pipeline; it will copy prereg to:
   - `out/<run_id>/PREREG.locked.yaml`
3) Treat any later changes as a new run.

---

## 2) Run

From this subcase directory:

```bash
python -m src.run --prereg PREREG.yaml
```

---

## 3) Verify artifacts

In `out/<run_id>/` verify:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `model.joblib`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

A run missing any of these is **NOT** repo‑ready.

---

## 4) Boundary discipline check

Open `boundary_snapshot.json` and confirm:

- feature whitelist contains **no** PAE or MSA fields
- label field is `C2_pae_offdiag`
- train/deploy boundary split is declared
