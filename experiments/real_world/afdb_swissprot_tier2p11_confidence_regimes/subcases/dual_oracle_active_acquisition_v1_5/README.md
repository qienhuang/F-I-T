# Subcase v1.5 — Dual‑Oracle Active Acquisition (Policy Cards with FPR‑Floor Plots)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_5`  
**Pack version:** `v1.5_repo_ready`  
**Lineage:** v1.4 (embedded plots + FPR sweep) → **v1.5 (explicit FPR‑floor plot per policy)**

v1.5 makes the *monitorability* lesson concrete:

- AUC and ranking metrics are not sufficient.
- A usable alarm requires either:
  - meeting a low‑FPR cap, and
  - avoiding an **FPR floor** at the preregistered TPR-min.

---

## 0) What is new in v1.5

### 0.1 New evidence plot: FPR‑floor vs round

New per-policy PNG:

- `out/<run_id>/policy_cards/assets/*_fpr_floor.png`

It plots (holdout):

- PAE `fpr_floor_at_tpr_min` and MSA `fpr_floor_at_tpr_min`
- the primary cap line

This makes “floor resolved / not resolved” visually auditable.

### 0.2 Policy cards embed 4 plots

Each card now embeds:

1) `*_learning.png`
2) `*_allocation.png`
3) `*_tpr_vs_fpr.png`
4) `*_fpr_floor.png` (**NEW**)

### 0.3 Assets manifest updated

`assets_manifest.json` now includes the new plot and its SHA256.

---

## 1) Quickstart (real data)

```bash
pip install -r requirements.txt
python -m src.run --prereg PREREG.yaml
```

---

## 2) Smoke + CI-style check

```bash
bash scripts/ci_check.sh
```
