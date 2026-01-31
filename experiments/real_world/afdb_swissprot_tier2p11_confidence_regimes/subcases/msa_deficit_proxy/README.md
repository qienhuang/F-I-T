# Subcase v0.1 — MSA Depth/Deficit Proxy Estimator (Non‑LLM Specialist Model)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `msa_deficit_proxy_v0_1`  
**Pack version:** `v0.1_repo_ready`  
**Primary training target:** build a **B0‑deployable estimator** for an otherwise B2‑only channel  
**Secondary training target:** monitorability discipline (low‑FPR usability) + EST boundary discipline

---

## 0) Scope & claims notice

This is a FIT/EST engineering case about **measurement channels and boundary‑safe proxy estimators**, not biology.

- We treat MSA depth as an **oracle measurement channel** (available only when `.a3m` exists).
- We train a small, non‑LLM model that maps **B0‑available features** (pLDDT‑derived + length) to an estimate of:


$$
\widehat{C3} \approx C3 := -\log(1 + \texttt{msa\_depth})
$$



- The goal is to make a *deployable* proxy channel  $ \widehat{C3} $  available under a coord‑only boundary.

No causal claims about evolution or folding are made.

---

## 1) Why this subcase exists (Task B)

Many AFDB entries may lack MSA artifacts in a local boundary, or you may choose not to retrieve them due to cost.

This subcase teaches how to:

1) treat MSA as an **expensive / optional oracle channel**,  
2) learn a proxy estimator under a strict boundary, and  
3) evaluate whether the proxy is usable both as:
   - a **regression estimator** of  $ C3 $ , and
   - an **alarm score** for a sparse‑MSA event at low FPR.

---

## 2) Boundary contract (EST discipline)

### 2.1 Train boundary  $ \mathcal{B}_{train} $

In scope:
- features (deployable): pLDDT‑derived + length only (B0‑safe)
- labels (oracle): `msa_depth` or `C3_msa_deficit` from a parent run that had MSA available (B2)

Out of scope:
- any use of MSA artifacts as features
- any use of PAE as features
- any post‑hoc feature additions after seeing results

### 2.2 Deploy boundary  $ \mathcal{B}_{deploy} $

In scope:
- B0‑safe features only

Out of scope:
- MSA access (no `.a3m`), no PAE

**Rule:** The model must be deployable without MSA.

---

## 3) Inputs

This subcase consumes **one file** from the parent case (a B2 run is required):

- `metrics_per_protein.parquet` (or `.csv` fallback)

Required columns:

- `accession`
- `length`
- `I1_hi_conf_frac`
- `I2_mean_plddt`
- `I3_plddt_entropy`
- `C1_low_conf_frac`
- `msa_depth` (oracle label store)
- `C3_msa_deficit` (oracle label store; optional if you prefer to derive from `msa_depth`)

---

## 4) Primary estimator target (regression)

We predict:

- primary target  $ y := C3\_msa\_deficit $  if present, else
-  $ y := -\log(1 + \texttt{msa\_depth}) $

Report on the **test** split:

- MAE / RMSE
- Spearman correlation (rank stability)
-  $ R^2 $ 

---

## 5) Secondary task: monitorability at low FPR (optional but recommended)

Define an event:

- `E_msa_sparse`:  `msa_depth <= tau_msa_depth`  (preregistered)

Treat the regression prediction  $ \widehat{C3} $  as a **score** and ask:

- Can we threshold the score to achieve FPR ≤ {1%, 5%}
- What TPR/coverage is achievable there
- Is there an FPR floor (degenerate score overlap)

This directly matches the monitorability discipline used across your cases.

---

## 6) Quickstart

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:

- set `data.input_metrics_path` to your parent B2 run, e.g.  
  `../../out/<B2_RUN_ID>/metrics_per_protein.parquet`

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.

---

## 7) Required outputs (artifact contract)

A run is “complete” only if these exist:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `model.joblib`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 8) One‑page trade‑off figure

See `ONE_PAGE_TRADEOFF.md` for the exact 4‑panel definition.
