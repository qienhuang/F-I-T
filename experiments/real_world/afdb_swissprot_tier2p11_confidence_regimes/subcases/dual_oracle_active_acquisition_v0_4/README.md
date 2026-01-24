# Subcase v0.4 — Dual‑Oracle Active Boundary Acquisition with Joint Gate (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v0_4`  
**Pack version:** `v0.4_repo_ready`  
**Design pattern:** non‑LLM specialists + **two oracle budgets** + proxy channel + decision trace  
**Primary training target:** **joint usability** at low FPR (two alarms must both be usable)  
**Secondary training target:** MSA as an estimable channel  $ \widehat{C3} $  (proxy constraint channel)

---

## 0) Scope & claims notice

This is a FIT/EST **protocol case** about measurement channels, boundary switches, and acquisition policies — not biology.

We treat:

- PAE summary metrics as an **oracle channel** (available only under B1/B2),
- MSA depth metrics as another **oracle channel** (available only under B2),
- and we ask whether B0‑deployable proxy alarms and proxy channels can be learned **efficiently under budget**.

No causal claims about folding or evolution are made.

---

## 1) What is new vs v0.3

v0.3: two oracles, two alarms, two budgets.  
v0.4 adds two upgrades:

1) **MSA regression proxy channel** (not only an event alarm)  
   We learn:


$$
\widehat{C3} \approx C3 := -\log(1 + \texttt{msa\_depth})
$$



2) **Joint gate**: “usable” means **both alarms** operate at a low‑FPR cap.  
   This matches the monitorability discipline: indicators that cannot operate at low FPR are not operational alarms even if AUC is high.

---

## 2) Boundary contract (EST discipline)

### 2.1 Deploy boundary  $ \mathcal{B}_{deploy} $

Allowed features (B0‑safe):

- `length`
- `I1_hi_conf_frac`
- `I2_mean_plddt`
- `I3_plddt_entropy`
- `C1_low_conf_frac`

Forbidden:

- any PAE/MSA columns as features

### 2.2 Oracle channels (label stores)

PAE oracle label store:

- numeric: `C2_pae_offdiag`
- event: `E_pae_high_uncertainty` occurs when



$$
C2\_pae\_offdiag \ge \tau_{pae}
$$



MSA oracle label store:

- numeric: `msa_depth`
- event: `E_msa_sparse` occurs when



$$
msa\_depth \le \tau_{msa}
$$



MSA proxy channel target:



$$
C3 := -\log(1 + \texttt{msa\_depth})
$$



Both thresholds are preregistered.

---

## 3) Models learned (three specialists)

1) **PAE alarm classifier**: B0 →  $ \widehat{P}(E_{pae}) $  
2) **MSA alarm classifier**: B0 →  $ \widehat{P}(E_{msa}) $  
3) **MSA proxy regressor**: B0 →  $ \widehat{C3} $  

All models are **small**, non‑LLM, and boundary‑safe.

---

## 4) Offline oracle simulation (same as v0.3)

We consume a parent‑run `metrics_per_protein.parquet` that already contains both oracle metrics.
We treat it as an **offline oracle store**:

- an item is “unlabeled” for an oracle until queried,
- querying reveals the stored value/label and consumes budget.

Holdout labels are treated as “free for measurement” and this is declared in prereg.

---

## 5) Policies compared

Policies are preregistered in `PREREG.yaml`. Example set included:

- `fixed_split`
- `adaptive_uncertainty`
- `adaptive_need_based_joint`
- `random_hash`

Each policy decides:
1) how many queries go to PAE vs MSA (allocation), and  
2) which accession to query within each oracle (ranking).

All tie‑breaks are deterministic (stable hash), so the decision trace is reproducible.

---

## 6) Events

We keep two “coverage jump” events (weak, protocol sense):

- `E_covjump_pae`
- `E_covjump_msa`

And we add a joint milestone:

- `E_joint_usable`: first round where both alarms are usable at the primary FPR cap.

---

## 7) Inputs

Consumes one parent artifact:

- `metrics_per_protein.parquet` (or `.csv` fallback)

Required columns:

- `accession`
- B0 features listed above
- `C2_pae_offdiag` (PAE oracle store)
- `msa_depth` (MSA oracle store)

---

## 8) Quickstart

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:

- set `data.input_metrics_path` to your parent run file

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.

---

## 9) Required outputs (artifact contract)

A run is “complete” only if these exist:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `round_metrics.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 10) One‑page trade‑off figure

See `ONE_PAGE_TRADEOFF.md` for the exact 4‑panel definition.
