# Subcase v1.0 — Dual‑Oracle Active Acquisition with Regime Diagnostics (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_0`  
**Pack version:** `v1.0_repo_ready`  
**Lineage:** v0.7 (joint‑gap allocation) → v0.8 (candidate pool basis uK vs rK) → v0.9 (alpha + K caps + FPR floors) → **v1.0 (regime timeline + floor‑resolution events)**

This subcase exists to train FIT readers on **EST boundary discipline** and on the difference between:

- “a model has good ranking metrics,” vs
- “an alarm is **operationally usable** under a low‑FPR cap,” vs
- “the alarm is **structurally blocked** by an **FPR floor**.”

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

## 1) What is new in v1.0

### 1.1 Regime timeline (per round, per alarm)

Each round, each alarm is assigned a **regime label** under the primary cap:

- `UNTRAINED` — not enough labels (or single‑class); not eligible for alarm operation
- `FPR_FLOOR` — trained, but even the best threshold at  $ \text{TPR} \ge \text{tpr_min} $  cannot get  $ \text{FPR} \le \text{cap} $
- `UNUSABLE` — trained, no floor, but still fails the operating point (TPR too low or FPR too high)
- `USABLE` — meets the operating point at the cap

The output `regime_timeline.csv` is designed for audit and teaching.

### 1.2 Floor‑resolution events (phase‑like markers)

We add explicit events:

- `E_floor_resolved_pae`: first round where PAE floor no longer blocks the cap
- `E_floor_resolved_msa`: first round where MSA floor no longer blocks the cap

These are “phase‑like” only in the weak sense: discrete regime markers under a locked protocol.

---

## 2) Policy spec grammar (preregistered & auditable)

A policy spec is:

`<allocation_policy>__<ranking_policy>[__a<alpha>][__K<Kcap>]`

Examples:

- `adaptive_joint_gap__composite_batch_ff_uK__a0.7__K5000`
- `adaptive_joint_gap__composite_batch_ff_rK__a1.0__K1000`

---

## 3) Outputs (artifact contract)

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`  (includes `alpha_used`, `K_used`, `candidate_pool_basis_used`)
- `allocation_trace.csv`
- `round_metrics.json`
- `regime_timeline.csv`  (**NEW**)
- `regime_summary.json`  (**NEW**)
- `event_summary.json`   (now includes floor‑resolution events)
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
