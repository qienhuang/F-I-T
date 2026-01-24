# Subcase v0.3 — Dual‑Oracle Active Boundary Acquisition (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v0_3`  
**Pack version:** `v0.3_repo_ready`  
**Design pattern:** non‑LLM specialists + **two oracle budgets** + decision trace  
**Primary training target:** monitorability at **low FPR** under explicit budgets  
**Secondary training target:** EST boundary discipline for *multi‑channel boundary switches*

---

## 0) Scope & claims notice

This is a FIT/EST **protocol case** about measurement channels, boundary switches, and acquisition policies — not biology.

We treat:

- PAE summary metrics as an **oracle channel** (available only under B1/B2),
- MSA depth metrics as another **oracle channel** (available only under B2),
- and we ask whether B0‑deployable proxy alarms can be learned **efficiently under budget**.

No causal claims about folding or evolution are made.

---

## 1) What is new in v0.3 (why you want this)

v0.2 had one oracle (PAE). v0.3 introduces **two independent boundary switches**:

- **B0 → B1**: query PAE (expensive)
- **B0 → B2**: query MSA (expensive)

The acquisition policy must decide:

1) **which oracle** to query (PAE vs MSA), and
2) **which accession** to query, under separate budgets.

All decisions are logged as an auditable artifact:

- `out/<run_id>/decision_trace.csv`

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



Both thresholds are preregistered.

---

## 3) What the system learns (two alarms)

We train two independent small classifiers:

- **PAE alarm**: predict `E_pae_high_uncertainty` from B0 features
- **MSA alarm**: predict `E_msa_sparse` from B0 features

Both are evaluated with the same discipline:

- do not report only AUC;
- report whether the alarm is **usable under low FPR caps**;
- explicitly detect if an **FPR floor** makes an alarm unusable.

---

## 4) Offline oracle simulation

This subcase uses a parent‑run `metrics_per_protein.parquet` that already contains both oracle metrics.
We treat it as an **offline oracle store**:

- an item is “unlabeled” for an oracle until queried,
- querying reveals the stored event label and consumes budget.

For measurement convenience, holdout labels are treated as “free for evaluation” and this is declared in prereg.

---

## 5) Policies compared

Policies are preregistered in `PREREG.yaml`.

Typical choices:

- `fixed_split`: fixed per‑round query counts for PAE and MSA
- `adaptive_uncertainty`: allocate queries based on uncertainty mass per oracle
- `adaptive_need_based`: allocate queries to whichever oracle’s alarm is not yet usable at low FPR

All tie‑breaks are deterministic (stable hash), so the decision trace is reproducible.

---

## 6) Event definitions (weak phase‑like jumps)

Define coverage jump events separately:

- `E_covjump_pae`: discrete jump in TPR at primary FPR cap for the PAE alarm
- `E_covjump_msa`: same for MSA alarm

This is “phase‑like” only in the weak protocol sense: a regime shift in a measured statistic under locked rules.

---

## 7) Inputs

This subcase consumes one parent artifact:

- `metrics_per_protein.parquet` (or `.csv` fallback)

Required columns:

- `accession`
- B0 features listed above
- `C2_pae_offdiag` (PAE oracle store)
- `msa_depth` (MSA oracle store)

If either oracle is missing for some entries, you can choose `universe_mode`:

- `intersection` (default): only entries that have both oracles
- `union`: allow per‑oracle availability (more realistic, more complex)

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
