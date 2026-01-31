# Subcase v1.6 — Dual‑Oracle Active Acquisition (Policy Cards with FPR‑Floor Plots)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_6`  
**Pack version:** `v1.6_repo_ready`  
**Lineage:** v1.5 (policy cards + FPR-floor plots) → **v1.6 (joint coverage jump / E_jump)**

v1.6 keeps the *monitorability* discipline concrete and adds a **phase-like joint coverage jump** event:

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

## 0) What is new in v1.6

### 0.1 Joint coverage scalar `cov_joint(r)` (phase-like coverage)

We add a **joint coverage** statistic on holdout at the primary FPR cap:

- $$ \mathrm{cov}_{\mathrm{joint}}(r) = \min(\mathrm{TPR}_{\mathrm{PAE}}(r),\ \mathrm{TPR}_{\mathrm{MSA}}(r)) \cdot \mathbf{1}[\text{PAE usable at cap} \land \text{MSA usable at cap}] $$

This makes “coverage” **regime-aware**: if either oracle channel is not usable under the cap, joint coverage is defined as 0 (not “unknown”).

### 0.2 Phase-like event: `E_covjump_joint`

We preregister a **coverage jump** event on the joint statistic:

- `E_covjump_joint`: the first round where  `cov_joint`  increases by at least `delta_cov_joint`  within a window of `W_jump_rounds`.

This is the closest analogue (in this AFDB setting) to the **E_jump** language in the Case 05 pitch: a discrete regime shift under a locked boundary and a locked operating point. fileciteturn2file1

### 0.3 Policy cards now include a `joint coverage` plot

Each policy card includes a joint coverage timeline plot with the `E_covjump_joint` marker, so readers can see whether the run exhibits a clean “jump” or only gradual changes.




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
