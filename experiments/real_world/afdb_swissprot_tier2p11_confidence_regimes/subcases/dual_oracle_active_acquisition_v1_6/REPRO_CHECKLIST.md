# REPRO_CHECKLIST — Dual‑Oracle + Δ‑Lag + Leakage Audit (v1.6)

---

## 1) Preconditions

You must have a parent case run whose `metrics_per_protein.parquet` includes:

- B0 feature columns
- `C2_pae_offdiag` (PAE oracle store; may be missing for some accessions)
- `msa_depth` (MSA oracle store; may be missing for some accessions)

---

## 2) Lock prereg

Edit `PREREG.yaml` only for:

- `data.input_metrics_path`
- optionally thresholds: `boundary.thresholds.tau_pae`, `boundary.thresholds.tau_msa_depth`
- optionally budgets: `acquisition.oracle_budgets.*`
- optionally which policies to run: `acquisition.policy_specs`

Run will copy prereg to:

- `out/<run_id>/PREREG.locked.yaml`

---

## 3) Run

From this subcase directory:

```bash
python -m src.run --prereg PREREG.yaml
```

---

## 4) Verify artifacts

In `out/<run_id>/` verify:

- `PREREG.locked.yaml`
- `dataset_snapshot.json`
- `boundary_snapshot.json`
- `decision_trace.csv`
- `allocation_trace.csv`
- `round_metrics.json`
- `regime_timeline.csv`
- `regime_summary.json`
- `leakage_audit.json` (**NEW**)
- `event_summary.json`
- `eval_report.md`
- `tradeoff_onepage.pdf`
- `run_manifest.json`

---

## 5) Boundary discipline checks (must pass)

- Feature whitelist contains no oracle fields (`C2_pae_offdiag`, `msa_depth`)
- Holdout labels are **reporting only**; acquisition decisions are based on labeled‑val diagnostics
- No repeated (accession, oracle_type) queries

---

## 6) Leakage audit (must pass)

Open `leakage_audit.json` and verify:

- `holdout_overlap_with_queries == 0` (for both PAE and MSA)
- `duplicate_queries == 0`
- `oracle_feature_leakage == false`

If any fail, treat the run as invalid.

---

## 7) Regime diagnostics checks (must pass)

From `regime_timeline.csv`:

- `UNTRAINED` must occur early (before `min_labeled_to_train`)
- If `FPR_FLOOR` exists at cap, it must be reflected in `fpr_floor_at_tpr_min` > cap in `round_metrics.json`
- `E_floor_resolved_*` must match the first round where the floor no longer blocks the cap
- `E_enter_usable_*` must be ≥ corresponding `E_floor_resolved_*` (or flag)

---

## 8) Δ‑lag checks (must pass)

From `event_summary.json`:

- `delta_lag` must be ≥ 0 (otherwise flag)
- policies with smaller `delta_lag` are “faster stabilization” under the locked cap (within this protocol)

---

## 9) Alpha/K audit checks (must pass)

From `decision_trace.csv`:

- composite policies include:
  - `alpha_used` ∈ {0.0, 0.7, 1.0}
  - `K_used` ∈ {1000, 5000, 20000}
  - `candidate_pool_basis_used` matches `*_uK` vs `*_rK`

---

## 10) Monitorability hardness (FPR floors)

In `round_metrics.json`, for each alarm & split:

- if `fpr_floor_at_tpr_min > cap`, the alarm is **structurally unusable** at that cap

This is separate from AUC; do not collapse them.


---

## Added in v1.6 — joint coverage jump checks

- Confirm `event_summary.json` includes `E_covjump_joint` for each policy.
- Confirm `policy_cards/assets/` includes a `*_joint_cov.png` file for each policy.
- Confirm the marker round in the plot matches the `event_summary.json` value.
- Confirm `policy_table.csv` includes:
  - `final_cov_joint_at_cap`
  - `r_covjump_joint`

