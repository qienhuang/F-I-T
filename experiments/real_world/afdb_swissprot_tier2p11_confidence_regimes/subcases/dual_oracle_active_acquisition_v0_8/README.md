# Subcase v0.8 — Dual‑Oracle Active Acquisition with Candidate‑Pool Ablations (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v0_8`  
**Pack version:** `v0.8_repo_ready`

This subcase continues v0.7 and adds a clean, preregistered ablation:

- **same** selection algorithm (batch diversity via farthest‑first),
- **same** composite scoring (uncertainty + novelty),
- **different candidate‑pool basis** used to form the top‑K pool:

1) **uK:** candidate pool = top‑K by uncertainty  
2) **rK:** candidate pool = K selected by stable hash (“random‑K”)

This isolates whether gains are due to:
- “picking uncertain samples” vs
- “diverse batches” (and whether uncertainty‑topK is necessary).

---

## 0) Scope & claims notice

This is a FIT/EST **protocol** case about:

- boundary discipline,
- dual oracle channels,
- active boundary acquisition,
- monitorability under low‑FPR constraints,
- and preregistered policy comparisons.

No biological claims.

---

## 1) Boundary contract (EST discipline)

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

### Oracle channels (label stores)

PAE event:



$$
E_{pae}: \ C2\_pae\_offdiag \ge \tau_{pae}
$$



MSA event:



$$
E_{msa}: \ msa\_depth \le \tau_{msa}
$$



MSA proxy channel:



$$
C3 := -\log(1 + \texttt{msa\_depth}), \quad \widehat{C3} \text{ learned from B0 features}
$$



---

## 2) What is new in v0.8

### 2.1 Candidate pool ablation for batch diversity

Ranking policies:

- `composite_batch_ff_uK`  
  - candidate pool basis: **uncertainty** (top‑K by uncertainty)
- `composite_batch_ff_rK`  
  - candidate pool basis: **random_hash** (stable “random‑K”)
- `uncertainty`  
  - baseline: pick most uncertain samples (no novelty term)
- `random_hash`  
  - baseline: stable random pick

All policies keep:
- the same feature boundary,
- the same K cap (preregistered),
- and the same farthest‑first **within‑batch** novelty update.

### 2.2 Primary event reporting (phase‑like protocol)

v0.8 treats the following as explicit, preregistered **events**:

1) `E_joint_usable(policy)` — earliest round where **both** alarms are usable on holdout at the primary cap.  
2) `E_covjump_pae(policy)` — earliest round where PAE TPR@cap increases by `delta_tpr` within `W_jump` rounds.  
3) `E_covjump_msa(policy)` — same for MSA.

These events are **protocol‑level** (learning dynamics), not domain claims.

---

## 3) Outputs (artifact contract)

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
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

- set `data.input_metrics_path` to your parent run file

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.
