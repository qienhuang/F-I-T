# Subcase v0.9 — Dual‑Oracle Active Acquisition with Alpha/K Ablations (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v0_9`  
**Pack version:** `v0.9_repo_ready`  
**Lineage:** v0.7 (joint‑gap allocation) → v0.8 (candidate‑pool uK vs rK) → **v0.9 (alpha + K caps + explicit FPR floors)**

This subcase is designed to train FIT readers on **EST boundary discipline** and on **how to audit “phase‑like” protocol improvements** using:

- dual oracle channels (PAE + MSA),
- budgeted active acquisition,
- low‑FPR monitorability gates (not just AUC),
- preregistered event reporting (`covjump`, `joint usable`),
- and explicit **FPR floor** measurements.

No biological claims.

---

## 0) Boundary contract (EST discipline)

### Deploy boundary  $ \mathcal{B}_{deploy} $

Allowed features (B0‑safe only):

- `length`
- `I1_hi_conf_frac`
- `I2_mean_plddt`
- `I3_plddt_entropy`
- `C1_low_conf_frac`

Forbidden as features:

- `C2_pae_offdiag` (PAE oracle store)
- `msa_depth` (MSA oracle store)

### Oracle channels

PAE event:



$$
E_{pae}: \ C2\_pae\_offdiag \ge \tau_{pae}
$$



MSA event:



$$
E_{msa}: \ msa\_depth \le \tau_{msa}
$$



Proxy channel (estimable constraint):



$$
C3 := -\log(1 + \texttt{msa\_depth}), \quad \widehat{C3} \text{ learned from B0 features}
$$



---

## 1) What is new in v0.9

### 1.1 Alpha ablation (uncertainty vs novelty)

Composite score used in batch selection:



$$
\text{score} = \alpha \cdot U_{norm} + (1-\alpha)\cdot N_{norm}
$$



where:
-  $ U_{norm} $  is normalized uncertainty (closest to 0.5 probability),
-  $ N_{norm} $  is normalized novelty (min distance to labeled set in z‑space),
- and farthest‑first updates novelty within the batch.

We compare:
-  $ \alpha = 0.0 $  (pure novelty),
-  $ \alpha = 0.7 $  (default),
-  $ \alpha = 1.0 $  (pure uncertainty).

### 1.2 Candidate pool cap ablation (K)

We compare candidate pool sizes:
- `K=1000`
- `K=5000`
- `K=20000`

This tests whether “more candidates” is necessary for covjump/joint usability, or whether a small pool is enough.

### 1.3 Explicit FPR floors (protocol hardness)

For each alarm and split (val/holdout), we compute:

- `fpr_floor_at_tpr_min` = minimal achievable FPR among thresholds with TPR ≥ `tpr_min_for_usable`.

If `fpr_floor_at_tpr_min > cap`, then the alarm is **structurally unusable** at that cap (an “FPR floor” failure mode).

---

## 2) Policy spec grammar (preregistered & auditable)

A policy spec is:

`<allocation_policy>__<ranking_policy>[__a<alpha>][__K<Kcap>]`

Examples:

- `adaptive_joint_gap__composite_batch_ff_uK__a0.7__K5000`
- `adaptive_joint_gap__composite_batch_ff_rK__a1.0__K1000`
- `adaptive_joint_gap__uncertainty`
- `random_hash__random_hash`

Ranking bases:

- `composite_batch_ff_uK`  → candidate pool basis = uncertainty‑topK
- `composite_batch_ff_rK`  → candidate pool basis = stable random‑K (hash)
- `uncertainty`            → pick most uncertain (no novelty)
- `random_hash`            → stable random pick

---

## 3) Outputs (artifact contract)

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`  (includes `alpha_used`, `K_used`, `candidate_pool_basis_used`)
- `allocation_trace.csv`
- `round_metrics.json`  (includes `fpr_floor_at_tpr_min` for val & holdout)
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 4) Quickstart

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:

- set `data.input_metrics_path` to your parent run file (parquet or csv)

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.
