# Subcase v0.1 — PAE Proxy Alarm (Non‑LLM Specialist Model)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `pae_proxy_alarm_v0_1`  
**Pack version:** `v0.1`  
**Primary training target:** **Monitorability gate** (low‑FPR alarm usability)  
**Secondary training target:** **EST boundary discipline** (train‑boundary vs deploy‑boundary)

---

## 0) Scope & claims notice

This is a FIT/EST engineering case about **measurement channels and alarm usability**, not biology.

- We treat AFDB confidence outputs as a **measurement system**, not ground truth.
- We train a **small, non‑LLM model** to predict a PAE‑defined target event using only B0‑available features (pLDDT‑derived).
- The objective is to decide **which entries deserve expensive oracle queries** (PAE/MSA), under an explicit false‑positive budget.

No causal claims about folding are made.

---

## 1) Why this subcase exists (the design pattern)

This subcase operationalizes the “non‑LLM specialist model” pattern:

> Use a light model as a **proxy alarm** that maps cheap signals → probability of an expensive oracle event, then operate at **low FPR** to control budget.

In AFDB terms:

- **Cheap signals (B0):** coordinate + pLDDT‑derived metrics.
- **Expensive oracle channel (B1):** PAE.
- **Decision:** “Flag this accession for PAE/MSA retrieval / deeper analysis” vs “Skip”.

---

## 2) Boundary contract (EST discipline)

We explicitly separate **two boundaries**:

### 2.1 Train boundary  $ \mathcal{B}_{train} $

In scope:
- pLDDT‑derived features (cheap)
- PAE‑derived label (oracle truth channel for training)

This requires input metrics produced under **parent boundary** `B1_COORD_PLUS_PAE`.

### 2.2 Deploy boundary  $ \mathcal{B}_{deploy} $

In scope:
- pLDDT‑derived features only

PAE is **not available** at inference time; the model must not depend on it.

**Rule:** Any attempt to use `C2_pae_offdiag` (or any PAE field) as a feature is a boundary violation.

---

## 3) Target event (what the alarm predicts)

Define a binary target event:

- `E_high_global_uncertainty` occurs when


$$
\texttt{C2\_pae\_offdiag} \ge \tau_{pae}.
$$



`C2_pae_offdiag` is the per‑protein off‑diagonal PAE summary computed in the parent case.

`tau_pae` is a preregistered threshold in `PREREG.yaml` (default 10.0).

---

## 4) Estimator tuple (alarm view)

We treat this as a monitorability/operations problem:


$$
\mathcal{E}_{alarm} = (S_t,\ \mathcal{B},\ \{\hat{F}, \hat{C}, \hat{I}\},\ W).
$$



Where:

- `S_t`: the current labeled subset (B1) + model parameters + remaining query budget
- `\mathcal{B}`: the train/deploy boundary split + feature whitelist + label definition
- `\hat{F}`: budget / query pressure (e.g., expected flagged volume)
- `\hat{C}`: false‑positive constraint (target FPR)
- `\hat{I}`: useful coverage at low FPR (TPR / recall at target FPR)
- `W`: split seed, threshold selection rule, evaluation windows

---

## 5) What you must report (monitorability gate)

For each target false‑positive rate (FPR) in `monitorability.fpr_targets`:

- choose a threshold on the **validation** split to satisfy  $ \text{FPR} \le \text{target} $
- report on the **test** split:
  - achieved FPR
  - coverage / recall (TPR)
  - precision
  - flagged volume per 10k items
  - whether the alarm is **usable** (TPR > 0) at that FPR

If TPR is 0 at the target FPR, the alarm is operationally unusable at that operating point, even if AUC is high.

---

## 6) Inputs

This subcase consumes **one file** produced by the parent case:

- `metrics_per_protein.parquet` (or `.csv` fallback)

Required columns:

- `accession`
- `length`
- `I1_hi_conf_frac`
- `I2_mean_plddt`
- `I3_plddt_entropy`
- `C1_low_conf_frac`
- `C2_pae_offdiag` (label channel)

---

## 7) Quickstart

### 7.1 Install dependencies (local)

```bash
pip install -r requirements.txt
```

### 7.2 Edit prereg

Open `PREREG.yaml` and set:

- `data.input_metrics_path` to your parent run file, e.g.  
  `../../out/<B1_RUN_ID>/metrics_per_protein.parquet`

### 7.3 Run

From this subcase directory:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs are written under `out/<run_id>/`.

---

## 8) Required outputs (artifact contract)

A run is “complete” only if these exist:

- `out/<run_id>/PREREG.locked.yaml`
- `out/<run_id>/dataset_snapshot.json`
- `out/<run_id>/boundary_snapshot.json`
- `out/<run_id>/model.joblib`
- `out/<run_id>/eval_report.md`
- `out/<run_id>/tradeoff_onepage.pdf`
- `out/<run_id>/run_manifest.json`

---

## 9) One‑page trade‑off figure

See `ONE_PAGE_TRADEOFF.md` for the exact 4‑panel figure definition.
