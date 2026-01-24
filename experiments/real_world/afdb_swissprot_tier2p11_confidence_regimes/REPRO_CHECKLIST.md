# REPRO_CHECKLIST - AFDB Swiss-Prot Tier2P11 Confidence Regimes

This checklist is written to be runnable under boundary modes:
- `B0_COORD_ONLY`
- `B1_COORD_PLUS_PAE`
- `B2_COORD_PLUS_PAE_PLUS_MSA`

---

## 1) Lock prereg

- Copy `EST_PREREG.yaml` into `out/<run_id>/EST_PREREG.locked.yaml`.
- Record the SHA256 of the locked prereg in `run_manifest.json`.

If you change boundary elements after seeing plots, treat it as a new run.

---

## 2) Place artifacts according to boundary

Required (all modes):
- `data/coords/` - AFDB coordinate files (`.cif` or `.pdb`)

If `B1` or `B2`:
- `data/pae/` - PAE JSON files named `<accession>.json` (or parsable accession inside JSON path)

If `B2`:
- `data/msa/` - MSA files named `<accession>.a3m`

---

## Optional smoke test (no downloads)

This repo includes a tiny synthetic fixture under `fixtures/` to verify the pipeline:

```bash
python -m src.run --prereg EST_PREREG.fixture_B0.yaml --run_id fixture_b0
python -m src.run --prereg EST_PREREG.fixture_B1.yaml --run_id fixture_b1
```

---

## 3) Run

From this case directory:

```bash
python -m src.run --prereg EST_PREREG.yaml
```

---

## 4) Verify outputs

In `out/<run_id>/` confirm:

- `accessions_selected.txt` and `accessions_selected.sha256`
- `metrics_per_protein.parquet`
- `metrics_per_bin.parquet`
- `regime_report.md`
- `tradeoff_onepage.pdf`
- `boundary_snapshot.json`
- `run_manifest.json`

---

## 5) Interpretation rule

If `regime_report.md` says `ESTIMATOR_UNSTABLE`, do not interpret the event location.
