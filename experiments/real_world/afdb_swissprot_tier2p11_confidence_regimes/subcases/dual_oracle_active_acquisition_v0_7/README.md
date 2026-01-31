# Subcase v0.7 — Dual‑Oracle Active Acquisition with Joint‑Gap Allocation (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v0_7`  
**Pack version:** `v0.7_repo_ready`

This subcase continues v0.6, with one key discipline upgrade:

- **Policy decisions use only labeled train/val diagnostics (no holdout leakage)**,
- while holdout is reserved for **reporting** and the official `joint_usable_round`.

And one strategy upgrade:

- **`adaptive_joint_gap`** allocation uses a *continuous gap score* to push the slower alarm toward usability
  (instead of a binary “usable / not usable” rule).

---

## 0) Scope & claims notice

This is a FIT/EST **protocol** case about:

- boundary discipline,
- oracle channels,
- active boundary acquisition,
- and monitorability under low‑FPR constraints.

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

## 2) What is new in v0.7

### 2.1 No holdout leakage in acquisition policy

- Threshold selection still uses labeled **val**.
- Allocation policy uses labeled **val** operating‑point metrics only.
- Holdout metrics are computed each round **for reporting only**.

This makes comparisons across policies cleaner: your “test set” is not steering your sampler.

### 2.2 Joint‑gap allocation (continuous bottleneck targeting)

Define a usability target:

- FPR ≤ cap
- TPR ≥ `tpr_min_for_usable`

On the labeled validation split, compute:

- `tpr_val`, `fpr_val` at the selected threshold under the cap.

Define a gap score per oracle:



$$
g := w_{tpr} \cdot \max(0, \ tpr_{min} - tpr_{val}) \ + \ w_{fpr} \cdot \max(0, \ fpr_{val} - cap)
$$



Then allocate the next round budget proportionally to gaps:

- if  $ g_{pae} + g_{msa} > 0 $ , allocate by gap ratio;
- else fall back to uncertainty‑mass allocation.

The allocation trace is logged to `allocation_trace.csv`.

---

## 3) Policies compared

Policies are preregistered as:

- `<allocation_policy>__<ranking_policy>`

Allocation policies:

- `fixed_split`
- `adaptive_uncertainty`
- `adaptive_joint_minimax` (binary usable check, based on labeled val)
- `adaptive_joint_gap` (new, continuous)
- `random_hash`

Ranking policies:

- `uncertainty`
- `composite_batch_ff` (batch diversity; farthest‑first in B0 feature space)
- `random_hash`

---

## 4) Outputs (artifact contract)

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 5) Quickstart

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
