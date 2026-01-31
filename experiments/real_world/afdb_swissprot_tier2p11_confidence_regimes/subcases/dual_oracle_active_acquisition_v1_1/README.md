# Subcase v1.1 — Dual‑Oracle Active Acquisition with Δ‑Lag + Leakage Audit (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_1`  
**Pack version:** `v1.1_repo_ready`  
**Lineage:** v0.9 (alpha/K/FPR floors) → v1.0 (regime timeline + floor resolution) → **v1.1 (Δ‑lag metric + leakage audit + enter/exit events)**

This subcase is designed as a FIT/EST training instrument, not a biology claim.

It teaches:

1) **Monitorability at low FPR caps** (including FPR floors).  
2) **Boundary discipline**: oracle fields are *never* used as features.  
3) **Phase‑like event reporting**: regime markers must be preregistered and auditable.  
4) **The Δ‑lag question**: after floors resolve, how long until joint usability

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

## 1) What is new in v1.1

### 1.1 Δ‑lag metric (floor‑clear → joint‑usable)

Define:



$$
r_{floor} := \max(r^{pae}_{floor\_resolved},\ r^{msa}_{floor\_resolved})
$$



and:



$$
\Delta := r^{joint}_{usable} - r_{floor}.
$$



Interpretation:

- small  $ \Delta $  means “once floors clear, joint usability arrives quickly”
- large  $ \Delta $  means “floors clear, but models still need many rounds to become usable”
- negative  $ \Delta $  should not happen; it triggers an audit warning

This is a deliberately **operational** measure of “regime stabilization time” under a locked cap.

### 1.2 Leakage audit artifact (holdout isolation proof)

New output:

- `leakage_audit.json`

It verifies:

- holdout IDs never appear in any acquisition/label query trace
- no duplicate (accession, oracle_type) queries
- feature whitelist excludes oracle fields

### 1.3 Secondary regime events (enter/exit markers)

We add phase‑like markers:

- `E_enter_usable_pae`, `E_enter_usable_msa`
- `E_exit_floor_pae`, `E_exit_floor_msa`

These are derived from the regime timeline (holdout) and are reported alongside `E_floor_resolved_*` and `E_joint_usable`.

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
- `regime_timeline.csv`
- `regime_summary.json`
- `leakage_audit.json`  (**NEW**)
- `event_summary.json`  (now includes Δ + enter/exit events)
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
