# Subcase v0.6 — Dual‑Oracle Active Acquisition with Batch Diversity (PAE + MSA)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v0_6`  
**Pack version:** `v0.6_repo_ready`

This subcase is the “make it harder” continuation of v0.4/v0.5:

- keeps **two oracle budgets** (PAE + MSA),
- keeps **joint low‑FPR usability** as the operational gate,
- keeps **MSA as an estimable channel**  $ \widehat{C3} $ ,
- and upgrades within‑oracle selection from “static novelty” to **batch‑aware diversity**.

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



The oracle values exist in the parent artifact, but are treated as **unobserved until queried**.

---

## 2) What is new in v0.6

v0.5 introduced policy grammar: `<allocation>__<ranking>` and composite ranking.  
v0.6 upgrades ranking to a batch‑aware mode:

### Batch farthest‑first (diversity) within a candidate pool

Within each oracle at each round:

1) form a candidate pool of size `K` (preregistered) using an admissible basis (by default: highest uncertainty),  
2) compute novelty as min distance in B0 feature space to the current labeled set,  
3) select a batch greedily with **farthest‑first updates** (each chosen point becomes a new “repeller” for the remaining candidates).

This turns “diversity” into a reproducible, auditable algorithm rather than a narrative claim.

All selected points record:

- uncertainty,
- novelty,
- normalized components,
- composite score,
in `decision_trace.csv`.

---

## 3) Policies compared

Policies are preregistered in `PREREG.yaml` as:

- `<allocation_policy>__<ranking_policy>`

Allocation policies:

- `fixed_split`
- `adaptive_uncertainty`
- `adaptive_joint_minimax`
- `random_hash`

Ranking policies:

- `uncertainty`
- `composite_batch_ff`  (new in v0.6)
- `random_hash`

---

## 4) One‑page trade‑off figure

See `ONE_PAGE_TRADEOFF.md`.

The one‑pager visualizes:

- PAE learning curve (TPR@cap vs PAE budget)
- MSA learning curve (TPR@cap vs MSA budget)
- allocation over time (frac PAE per round)
- joint gate frontier (joint_usable_round vs final MAE of  $ \widehat{C3} $ )

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

---

## 6) Required outputs (artifact contract)

A run is complete only if these exist:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `round_metrics.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`
