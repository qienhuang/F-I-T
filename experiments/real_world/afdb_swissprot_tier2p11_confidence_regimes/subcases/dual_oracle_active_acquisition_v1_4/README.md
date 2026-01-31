# Subcase v1.4 — Dual‑Oracle Active Acquisition (Policy Cards with Embedded Plots)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_4`  
**Pack version:** `v1.4_repo_ready`  
**Lineage:** v1.3 (policy cards + CI checks) → **v1.4 (policy cards + embedded plots + FPR‑sweep stats)**

This pack strengthens the *monitorability* teaching goal: cards should not be purely textual.
They should ship compact evidence plots that make **FPR floors**, **allocation dynamics**, and **cap‑based learning** visible at a glance.

---

## 0) What is new in v1.4

### 0.1 Embedded plots per policy card

New outputs under:

- `out/<run_id>/policy_cards/assets/`

For each policy, v1.4 generates 3 PNGs:

1) `*_learning.png`  
   - PAE and MSA holdout  **TPR@primary cap**  vs queried labels (budget proxy)

2) `*_allocation.png`  
   - PAE fraction of queries per round (allocation dynamics)

3) `*_tpr_vs_fpr.png`  
   - holdout TPR as a function of the preregistered FPR targets (the “coverage‑vs‑FPR” micro‑sweep)

The corresponding policy card links / embeds these images.

### 0.2 FPR‑sweep stats recorded (per round, per oracle)

The run now stores, for each round:

- `tpr_by_fpr_target_holdout`
- `fpr_by_fpr_target_holdout`

so the “coverage‑vs‑FPR” plot can be derived from artifacts, not recomputed ad hoc.

### 0.3 Assets manifest

New artifact:

- `out/<run_id>/policy_cards/assets_manifest.json`

It lists all generated asset files and their SHA256 hashes for auditability and cache correctness.

---

## 1) Quickstart (real data)

```bash
pip install -r requirements.txt
python -m src.run --prereg PREREG.yaml
```

---

## 2) Quickstart (smoke + CI‑style check)

```bash
bash scripts/ci_check.sh
```

---

## 3) Artifact contract (v1.4)

Everything from v1.3, plus:

- `policy_cards/assets/` (**NEW**)
- `policy_cards/assets_manifest.json` (**NEW**)
