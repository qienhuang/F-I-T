# Subcase v0.5 — Dual‑Oracle Active Boundary Acquisition (Composite Ranking + Joint Minimax)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v0_5`  
**Pack version:** `v0.5_repo_ready`  
**Design pattern:** non‑LLM specialists + two oracle budgets + decision trace + composite acquisition scores  
**Primary training target:** **joint usability** at low FPR (both alarms must be usable)  
**New in v0.5:** **composite uncertainty+novelty ranking** inside each oracle + **joint minimax allocation** across oracles

---

## 0) Scope & claims notice

This is a FIT/EST **protocol case** about measurement channels, boundary switches, and acquisition policies — not biology.

We treat:

- PAE summary metrics as an **oracle channel** (queried under B1),
- MSA depth metrics as another **oracle channel** (queried under B2),
- and we ask whether B0‑deployable proxy alarms and proxy channels can be learned **efficiently under explicit budgets**.

No causal claims about folding or evolution are made.

---

## 1) What v0.5 adds (why this is worth learning)

v0.4 established:

- two oracle budgets (PAE and MSA),
- two alarms (PAE event and MSA sparse‑event),
- and one proxy channel  $ \widehat{C3} $  for MSA.

v0.5 turns “active acquisition” into a **designable object** by adding:

1) **Composite within‑oracle ranking** (uncertainty + novelty):



$$
\texttt{score}(x) = \alpha \cdot \texttt{unc}(x) + (1-\alpha)\cdot \texttt{nov}(x)
$$



Where:

-  $ \texttt{unc}(x) = 0.5 - | \hat{p}(x) - 0.5 | $  (most uncertain first)  
-  $ \texttt{nov}(x) $  is feature‑space novelty (distance to labeled set in a fixed B0 feature space)

2) **Joint minimax allocation across oracles**:

- allocate the next batch budget to the oracle that is currently the bottleneck for the **joint gate**.

This is the simplest “non‑LLM specialist + FIT discipline” upgrade: you are not building a bigger model; you are building a **better measurement‑budget policy**.

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



---

## 3) Models learned (still non‑LLM)

1) PAE alarm classifier: B0 →  $ \widehat{P}(E_{pae}) $  
2) MSA alarm classifier: B0 →  $ \widehat{P}(E_{msa}) $  
3) MSA proxy regressor: B0 →  $ \widehat{C3} $  

All models are small and boundary‑safe.

---

## 4) Policy grammar (new)

Each policy is written as:

- `<allocation_policy>__<ranking_policy>`

Examples:

- `fixed_split__uncertainty`
- `adaptive_joint_minimax__composite`
- `random_hash__random_hash`

This makes “allocation vs ranking” separable and comparable.

---

## 5) One‑page trade‑off figure (v0.5)

See `ONE_PAGE_TRADEOFF.md`.

We keep a single page with 4 panels:

- (A) PAE learning curve (TPR@cap vs PAE budget)
- (B) MSA learning curve (TPR@cap vs MSA budget)
- (C) allocation over time (fraction PAE per round)
- (D) joint gate frontier (joint_usable_round vs final MAE of  $ \widehat{C3} $ )

---

## 6) Inputs

Consumes one parent artifact:

- `metrics_per_protein.parquet` (or `.csv` fallback)

Required columns:

- `accession`
- B0 features listed above
- `C2_pae_offdiag`
- `msa_depth`

---

## 7) Quickstart

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

## 8) Required outputs (artifact contract)

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `round_metrics.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`
