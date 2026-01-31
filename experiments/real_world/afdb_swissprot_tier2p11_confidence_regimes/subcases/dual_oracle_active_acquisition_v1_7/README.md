# Subcase v1.7 — Dual‑Oracle Active Acquisition (Cost‑Aware + Joint Coverage Jump + Jump‑Type)

**Parent case:** `afdb_swissprot_tier2p11_confidence_regimes`  
**Subcase ID:** `dual_oracle_active_acquisition_v1_7`  
**Pack version:** `v1.7_repo_ready`  
**Lineage:** v1.5 (policy cards + FPR-floor) → v1.6 (joint coverage jump) → **v1.7 (cost-aware metrics + jump_type)**

This subcase is a FIT/EST training instrument:

- It enforces **boundary discipline** across `B0 → B1 (PAE) → B2 (MSA)` acquisition.
- It enforces **monitorability discipline** (low‑FPR caps + explicit **FPR floors**).
- It adds a preregistered **phase-like observable**: a discrete **joint coverage jump** under a locked protocol.
- It upgrades “budget” from a vague notion to an explicit **oracle cost accounting**.

---

## 0) What is new in v1.7

### 0.1 Cost-aware accounting (oracle costs)

New prereg fields:

- `acquisition.oracle_costs.pae_unit_cost`
- `acquisition.oracle_costs.msa_unit_cost`

New artifact:

- `cost_summary.json` (per-policy cost curves + cost-to-event markers)

Visual changes:

- one-page tradeoff learning curves now use **cumulative cost** on the x-axis (not just label counts).

### 0.2 Jump-type classification (`availability_driven` vs `learning_driven`)

We preregister a classification rule for `E_covjump_joint`:

- Let `r_joint` be the first round where **joint usable@cap** holds.
- Let `r_jump` be the first round where **joint coverage jump** holds.
- Define `jump_delay = r_jump - r_joint`.

Then:

- `availability_driven` iff `jump_delay <= event.availability_delay_max_rounds` (default 0)
- else `learning_driven`

This prevents post-hoc storytelling: the “jump” must be visibly co-timed with (or lag behind) usability.

### 0.3 Policy cards now include cost and jump-type summaries

Each policy card includes:

- event markers (`r_joint_usable`, `r_covjump_joint`, `delta_lag`, `jump_type`)
- cost markers (`cost_to_joint_usable`, `cost_to_covjump_joint`, `total_cost_final`)
- evidence plots (including joint coverage vs **cost**)

---

## 1) Quickstart (real data)

1) Install deps:

```bash
pip install -r requirements.txt
```

2) Edit `PREREG.yaml`:

- set `data.input_metrics_path` to your parent case metrics file (parquet/csv)

3) Run:

```bash
python -m src.run --prereg PREREG.yaml
```

Outputs go to `out/<run_id>/`.

---

## 2) Quickstart (smoke test + CI-style gate)

From this directory:

```bash
bash scripts/ci_check.sh
```

It will:

1) generate `data/synthetic_metrics.csv`  
2) run the case with `PREREG_SMOKE.yaml` to `out_smoke/SMOKE/`  
3) validate required artifacts + audits

---

## 3) Artifact contract (v1.7)

A complete run produces:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `holdout_snapshot.json`
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
- `regime_timeline.csv`
- `regime_summary.json`
- `policy_table.csv`
- `cost_summary.json` (**NEW**)
- `policy_cards_index.md`
- `policy_cards/` (markdown cards)
- `policy_cards/assets_manifest.json`
- `leakage_audit.json`
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`
